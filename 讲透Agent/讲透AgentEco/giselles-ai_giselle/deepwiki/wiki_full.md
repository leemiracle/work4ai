# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/playground/giselle-engine.ts](apps/playground/giselle-engine.ts)
- [apps/playground/package.json](apps/playground/package.json)
- [apps/studio.giselles.ai/app/giselle-engine.ts](apps/studio.giselles.ai/app/giselle-engine.ts)
- [apps/studio.giselles.ai/package.json](apps/studio.giselles.ai/package.json)
- [internal-packages/workflow-designer-ui/package.json](internal-packages/workflow-designer-ui/package.json)
- [package.json](package.json)
- [packages/giselle/package.json](packages/giselle/package.json)
- [packages/giselle/src/engine/acts/run-act.ts](packages/giselle/src/engine/acts/run-act.ts)
- [packages/giselle/src/engine/generations/generate-content.ts](packages/giselle/src/engine/generations/generate-content.ts)
- [packages/giselle/src/engine/generations/generate-image.ts](packages/giselle/src/engine/generations/generate-image.ts)
- [packages/giselle/src/engine/generations/internal/use-generation-executor.ts](packages/giselle/src/engine/generations/internal/use-generation-executor.ts)
- [packages/giselle/src/engine/generations/types.ts](packages/giselle/src/engine/generations/types.ts)
- [packages/giselle/src/engine/generations/utils.ts](packages/giselle/src/engine/generations/utils.ts)
- [packages/giselle/src/engine/operations/execute-query.ts](packages/giselle/src/engine/operations/execute-query.ts)
- [packages/giselle/src/engine/telemetry/index.ts](packages/giselle/src/engine/telemetry/index.ts)
- [packages/giselle/src/engine/telemetry/types.ts](packages/giselle/src/engine/telemetry/types.ts)
- [packages/giselle/src/engine/triggers/resolve-trigger.ts](packages/giselle/src/engine/triggers/resolve-trigger.ts)
- [packages/giselle/src/engine/types.ts](packages/giselle/src/engine/types.ts)
- [packages/giselle/src/react/generations/generation-runner.tsx](packages/giselle/src/react/generations/generation-runner.tsx)
- [pnpm-lock.yaml](pnpm-lock.yaml)
- [pnpm-workspace.yaml](pnpm-workspace.yaml)

</details>



## Purpose and Scope

This documentation covers the **Giselle AI platform**, an AI workflow orchestration system that enables users to design, execute, and manage complex AI workflows through a visual interface. The platform provides:

- **Visual workflow design** using a node-based canvas interface
- **Multi-provider LLM integration** (OpenAI, Anthropic, Google, Fal-AI)
- **RAG (Retrieval-Augmented Generation)** capabilities with document and code vector stores
- **Tool execution** for GitHub operations, web search, and database queries
- **Background job processing** for long-running AI operations
- **Real-time streaming** of generation results

This page provides a high-level overview of the entire system architecture, monorepo organization, and how the major components interact. For detailed information about specific subsystems:

- Workflow design and visual editing: see [Workflow Designer UI](#4)
- AI execution pipeline: see [Core Engine and SDK](#2)
- Document processing and RAG: see [Data Processing Systems](#3)
- Production application features: see [Studio Application](#5.1)

## System Architecture

The Giselle platform follows a **layered monorepo architecture** with clear separation between applications, UI components, and engine packages.

```mermaid
graph TB
    subgraph Apps["apps/*"]
        Studio["studio.giselles.ai<br/>Next.js 15 App<br/>/api/giselle/* routes"]
        Playground["playground<br/>Dev Environment<br/>giselleEngine"]
        UIShowcase["ui.giselles.ai<br/>Component Showcase"]
    end
    
    subgraph InternalPkg["internal-packages/*"]
        WorkflowUI["@giselle-internal/workflow-designer-ui<br/>ReactFlow canvas<br/>useEditorStore"]
        UILib["@giselle-internal/ui<br/>Radix components<br/>@theme CSS vars"]
    end
    
    subgraph Packages["packages/* (@giselles-ai/*)"]
        Giselle["giselle<br/>NextGiselleEngine<br/>generateContent()<br/>executeQuery()"]
        Protocol["protocol<br/>Generation types<br/>NodeId, ActId schemas"]
        LangModel["language-model<br/>languageModels array<br/>ModelTier enum"]
        NodeReg["node-registry<br/>Node type definitions"]
        ActionReg["action-registry<br/>Action schemas"]
        TriggerReg["trigger-registry<br/>Trigger schemas"]
        RAG["rag<br/>QueryService<br/>EmbeddingMetrics"]
        GitHubTool["github-tool<br/>githubTools()<br/>octokit()"]
        WebSearch["web-search<br/>Content extraction"]
        DocPreproc["document-preprocessor<br/>extractTextFromPdf()"]
        Langfuse["langfuse<br/>traceGeneration()<br/>traceEmbedding()"]
        SupabaseDriver["supabase-driver<br/>supabaseStorageDriver()<br/>supabaseVaultDriver()"]
        TextEditor["text-editor<br/>Tiptap editor"]
    end
    
    subgraph External["External Services"]
        AISDKProviders["@ai-sdk/openai<br/>@ai-sdk/anthropic<br/>@ai-sdk/google<br/>@ai-sdk/fal"]
        TriggerDev["@trigger.dev/sdk<br/>jobs.trigger()"]
        Supabase["@supabase/supabase-js<br/>PostgreSQL + pgvector"]
        GitHub["@octokit/core<br/>GitHub GraphQL API"]
        Vercel["@vercel/edge-config<br/>Feature flags"]
    end
    
    Studio --> WorkflowUI
    Studio --> Giselle
    Studio --> Protocol
    Studio --> RAG
    Studio --> GitHubTool
    
    Playground --> WorkflowUI
    Playground --> Giselle
    
    WorkflowUI --> Giselle
    WorkflowUI --> Protocol
    WorkflowUI --> NodeReg
    WorkflowUI --> ActionReg
    WorkflowUI --> TriggerReg
    WorkflowUI --> UILib
    
    Giselle --> Protocol
    Giselle --> LangModel
    Giselle --> NodeReg
    Giselle --> ActionReg
    Giselle --> TriggerReg
    Giselle --> GitHubTool
    Giselle --> WebSearch
    
    NodeReg --> Protocol
    ActionReg --> Protocol
    TriggerReg --> Protocol
    
    RAG --> Protocol
    RAG --> DocPreproc
    RAG --> SupabaseDriver
    
    GitHubTool --> RAG
    
    Giselle --> TriggerDev
    Giselle --> AISDKProviders
    GitHubTool --> GitHub
    SupabaseDriver --> Supabase
    Langfuse -.-> Giselle
    
    Studio --> Vercel
    Studio --> TriggerDev
```

**Figure 1: High-Level System Architecture with Code Entities**

Sources: [pnpm-lock.yaml:242-1162](), [pnpm-workspace.yaml:1-6](), [apps/studio.giselles.ai/giselle-engine.ts:1-535](), [packages/giselle/src/engine/types.ts:1-228]()

The architecture consists of three primary layers:

1. **Application Layer** (`apps/*`): Next.js applications with API routes and UI
2. **Internal Packages** (`internal-packages/*`): Private UI component libraries
3. **Engine Packages** (`packages/*`): Core engine modules with `@giselles-ai/*` namespace

## Monorepo Organization

The codebase uses **pnpm workspaces** with a shared dependency catalog to maintain version consistency across 70+ dependencies.

### Workspace Structure

| Workspace Type | Path | Purpose | Example Packages |
|---------------|------|---------|------------------|
| Apps | `apps/*` | User-facing applications | `studio.giselles.ai`, `playground`, `ui.giselles.ai` |
| Internal Packages | `internal-packages/*` | Private UI libraries | `@giselle-internal/ui`, `@giselle-internal/workflow-designer-ui` |
| Engine Packages | `packages/*` | Core engine modules with `@giselles-ai/*` namespace | `giselle`, `protocol`, `language-model`, `rag`, `node-registry` |
| Tools | `tools/*` | Build utilities | `tsconfig` |

Sources: [pnpm-workspace.yaml:1-6](), [pnpm-lock.yaml:242-264]()

### Dependency Management

```mermaid
graph LR
    subgraph Catalog["Shared Catalog (pnpm-workspace.yaml)"]
        CatalogAI["ai: 5.0.51"]
        CatalogNext["next: 15.5.2"]
        CatalogReact["react: 19.1.1"]
        CatalogTailwind["tailwindcss: 4.1.10"]
        CatalogTS["typescript: 5.7.3"]
    end
    
    subgraph StudioDeps["studio.giselles.ai Dependencies"]
        StudioAI["ai: catalog:"]
        StudioNext["next: catalog:"]
        StudioWS["@giselle-sdk/giselle: workspace:*"]
    end
    
    subgraph PlaygroundDeps["playground Dependencies"]
        PlayAI["next: catalog:"]
        PlayWS["@giselle-internal/workflow-designer-ui: workspace:*"]
    end
    
    CatalogAI --> StudioAI
    CatalogNext --> StudioNext
    CatalogNext --> PlayAI
    
    style Catalog fill:#f9f9f9
    style StudioDeps fill:#e3f2fd
    style PlaygroundDeps fill:#fff3e0
```

**Figure 2: Dependency Catalog and Workspace Protocol**

The catalog enforces consistent versions across packages using the `catalog:` specifier, while workspace packages use `workspace:*` protocol for internal dependencies.

Sources: [pnpm-workspace.yaml:7-105](), [apps/studio.giselles.ai/package.json:21-101](), [apps/playground/package.json:18-36]()

## Key Applications

### studio.giselles.ai

The **production application** deployed to Vercel, providing the full Giselle platform experience.

**Engine Configuration:**

The application creates a `NextGiselleEngine` instance at [apps/studio.giselles.ai/giselle-engine.ts:196-396]():

```typescript
export const giselleEngine = NextGiselleEngine({
  basePath: "/api/giselle",
  storage,                          // supabaseStorageDriver
  llmProviders: ["openai", "anthropic", "google"],
  vault,                           // supabaseVaultDriver
  vectorStoreQueryServices: {
    github: gitHubQueryService,
    githubIssue: gitHubIssueQueryService,
    githubPullRequest: gitHubPullRequestQueryService,
    document: getDocumentVectorStoreQueryService()
  },
  callbacks: {
    generationComplete: async (args) => { ... },
    generationFailed: async (args) => { ... },
    embeddingComplete: async (args) => { ... }
  },
  aiGateway: { httpReferer, xTitle }
})
```

**Runtime Environment Detection:**

The system detects execution context via `getRuntimeEnv()` at [apps/studio.giselles.ai/giselle-engine.ts:180-185]():
- `"trigger.dev"`: Inside Trigger.dev job
- `"vercel"`: Vercel deployment
- `"local"`: Development environment
- `"unknown"`: Fallback

**Content Generation Processor:**

Based on environment, generation work is delegated at [apps/studio.giselles.ai/giselle-engine.ts:189-194]():
- **Self-processing**: Local and development environments execute directly
- **Trigger.dev**: Production uses `jobs.trigger<typeof generateContentJob>("generate-content", ...)` for background processing

**Key Features:**
- **Trigger.dev integration** via `@trigger.dev/sdk` ([apps/studio.giselles.ai/package.json:66]())
- **Sentry monitoring** via `@sentry/nextjs` ([apps/studio.giselles.ai/package.json:62]())
- **OpenTelemetry** via `@vercel/otel` ([apps/studio.giselles.ai/package.json:69]())
- **PDF processing** via `@embedpdf/pdfium` ([apps/studio.giselles.ai/package.json:27]())
- **Feature flags** via `@vercel/edge-config` ([apps/studio.giselles.ai/package.json:67]())

Sources: [apps/studio.giselles.ai/giselle-engine.ts:1-535](), [apps/studio.giselles.ai/package.json:1-133]()

### playground

The **development application** with simplified configuration for rapid iteration.

**Engine Configuration:**

Creates a `NextGiselleEngine` instance at [apps/playground/giselle-engine.ts:122-141]():

```typescript
export const giselleEngine = NextGiselleEngine({
  basePath: "/api/giselle",
  storage,  // fsStorageDriver or supabaseStorageDriver based on VERCEL env
  llmProviders,  // Dynamically detected from env vars
  integrationConfigs,
  vault: nodeVaultDriver({ secret: process.env.VAULT_SECRET }),
  callbacks: {
    generationComplete: async (args) => {
      await traceGeneration(args);
    }
  }
})
```

**Differences from Studio:**
- Uses `fsStorageDriver()` locally instead of only Supabase ([apps/playground/giselle-engine.ts:22-24]())
- Uses `nodeVaultDriver()` with in-memory encryption ([apps/playground/giselle-engine.ts:137-139]())
- Dynamic LLM provider detection based on available API keys ([apps/playground/giselle-engine.ts:26-39]())
- No Trigger.dev background job processing
- No Sentry error tracking
- Simplified observability (Langfuse only)

Sources: [apps/playground/giselle-engine.ts:1-141](), [apps/playground/package.json:1-42]()

### ui.giselles.ai

A **component showcase application** for viewing and testing UI components in isolation.

Sources: [apps/ui.giselles.ai/package.json:1-27]()

## Core Engine Packages

The engine ecosystem is organized around specific concerns with the `@giselles-ai/*` namespace:

```mermaid
graph TB
    subgraph Foundation["Foundation Layer"]
        Protocol["@giselles-ai/protocol<br/>Generation, Act, Node types<br/>GenerationId, NodeId, WorkspaceId<br/>Zod schemas"]
        LangModel["@giselles-ai/language-model<br/>languageModels: LanguageModel[]<br/>Capability enum<br/>hasTierAccess()"]
    end
    
    subgraph Registry["Registry Layer"]
        NodeReg["@giselles-ai/node-registry<br/>Node type definitions<br/>isTextGenerationNode()<br/>isQueryNode()"]
        ActionReg["@giselles-ai/action-registry<br/>Action type schemas"]
        TriggerReg["@giselles-ai/trigger-registry<br/>githubEvents map<br/>Trigger schemas"]
    end
    
    subgraph CoreEngine["Core Engine"]
        Giselle["@giselles-ai/giselle<br/>NextGiselleEngine<br/>generateContent()<br/>generateImage()<br/>executeQuery()<br/>runAct()"]
    end
    
    subgraph Integrations["Integration Layer"]
        RAG["@giselles-ai/rag<br/>QueryService interface<br/>EmbeddingMetrics<br/>search() method"]
        GitHubTool["@giselles-ai/github-tool<br/>githubTools()<br/>octokit()<br/>GitHubAuth types"]
        WebSearch["@giselles-ai/web-search<br/>Content extraction"]
        DocPreproc["@giselles-ai/document-preprocessor<br/>extractTextFromPdf()"]
    end
    
    subgraph Infrastructure["Infrastructure Layer"]
        SupabaseDriver["@giselles-ai/supabase-driver<br/>supabaseStorageDriver()<br/>supabaseVaultDriver()<br/>GiselleStorage interface"]
        Langfuse["@giselles-ai/langfuse<br/>traceGeneration()<br/>traceEmbedding()"]
        TextEditor["@giselles-ai/text-editor<br/>Tiptap editor setup"]
        Utils["@giselles-ai/utils<br/>Utility functions"]
    end
    
    Giselle --> Protocol
    Giselle --> LangModel
    Giselle --> NodeReg
    Giselle --> ActionReg
    Giselle --> TriggerReg
    Giselle --> GitHubTool
    Giselle --> WebSearch
    
    NodeReg --> Protocol
    NodeReg --> LangModel
    ActionReg --> Protocol
    TriggerReg --> Protocol
    
    RAG --> Protocol
    RAG --> DocPreproc
    RAG --> SupabaseDriver
    
    GitHubTool --> RAG
    
    Langfuse --> Protocol
    Langfuse --> LangModel
```

**Figure 3: Engine Package Dependencies with Code Entities**

### @giselles-ai/giselle

The **core orchestration engine** that coordinates all AI operations.

**Key Functions:**
- `NextGiselleEngine()`: Factory function creating engine instance with `GiselleEngineConfig` ([packages/giselle/src/engine/types.ts:194-227]())
- `generateContent()`: Text generation with streaming and tool support ([packages/giselle/src/engine/generations/generate-content.ts:62-447]())
- `generateImage()`: Image generation via Fal-AI, DALL-E, Imagen ([packages/giselle/src/engine/generations/generate-image.ts:32-366]())
- `executeQuery()`: Vector store query with RAG ([packages/giselle/src/engine/operations/execute-query.ts:40-542]())
- `runAct()`: Workflow execution orchestration ([packages/giselle/src/engine/acts/run-act.ts:123-201]())
- `useGenerationExecutor()`: React hook for generation lifecycle ([packages/giselle/src/engine/generations/internal/use-generation-executor.ts:59-452]())

**Key Types:**
- `GiselleEngineContext`: Main context type with storage, vault, callbacks ([packages/giselle/src/engine/types.ts:90-127]())
- `GenerationMetadata`: Custom metadata for tracing ([packages/giselle/src/engine/generations/types.ts:8-10]())

Sources: [packages/giselle/package.json:1-80](), [packages/giselle/src/engine/types.ts:1-228](), [packages/giselle/src/engine/generations/generate-content.ts:1-519]()

### @giselles-ai/protocol

The **type system** defining all data structures with Zod validation.

**Key Types:**
- `Generation`, `QueuedGeneration`, `RunningGeneration`, `CompletedGeneration`: Generation lifecycle states
- `Act`, `Sequence`: Workflow execution tracking
- `NodeId`, `GenerationId`, `ActId`, `WorkspaceId`: ID types with Zod schemas
- `GenerationContext`: Context for generation execution
- `OperationNode`: Union type for all node types

**Key Type Guards:**
- `isTextGenerationNode()`, `isImageGenerationNode()`, `isQueryNode()`: Runtime type checking

Sources: [pnpm-lock.yaml:1084-1120](), [packages/giselle/src/engine/types.ts:1-228]()

### @giselles-ai/language-model

Provides **provider-agnostic abstractions** for language models.

**Key Exports:**
- `languageModels`: Array of `LanguageModel` definitions with capabilities and tiers
- `Capability`: Enum for model capabilities (Reasoning, OptionalSearchGrounding, etc.)
- `hasCapability()`: Check if model supports a capability
- `hasTierAccess()`: Check user tier access to model

Sources: [packages/giselle/src/engine/generations/generate-content.ts:8-11](), [pnpm-lock.yaml:1043-1058]()

### @giselles-ai/node-registry

Defines **node type schemas** and utility functions.

**Key Exports:**
- Node type definitions for all workflow nodes
- Type guard functions (`isClonedFileDataPayload()`, etc.)
- Node content schemas

Sources: [pnpm-lock.yaml:1059-1083](), [internal-packages/workflow-designer-ui/package.json:17-24]()

### @giselles-ai/action-registry & @giselles-ai/trigger-registry

Define **action and trigger schemas** for workflow integrations.

**trigger-registry Key Exports:**
- `githubEvents`: Map of GitHub event IDs to event definitions

Sources: [pnpm-lock.yaml:828-843](), [packages/giselle/src/engine/triggers/resolve-trigger.ts:9]()

### @giselles-ai/rag

Implements the **vector store system** for RAG operations.

**Key Types:**
- `QueryService<TContext, TMetadata>`: Interface for vector store queries with `search()` method
- `EmbeddingMetrics`: Metrics tracking for embeddings
- `QueryContext`: Union type for GitHub and Document query contexts

**Key Functionality:**
- Document chunking
- Embedding generation via AI SDK
- PostgreSQL + pgvector integration
- Similarity search

Sources: [packages/giselle/src/engine/types.ts:19,162-193](), [packages/giselle/src/engine/operations/execute-query.ts:21](), [pnpm-lock.yaml:1121-1162]()

## Technology Stack

### Frontend Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| Next.js | 15.5.2 | React framework with App Router |
| React | 19.1.1 | UI library |
| Tailwind CSS | 4.1.10 | Styling with @theme blocks |
| XyFlow | 12.8.3 | Canvas-based workflow editor |
| Radix UI | 1.1.2 | Accessible UI primitives |
| Zustand | 5.0.8 | State management |
| Motion | 12.3.1 | Animation library |

Sources: [pnpm-workspace.yaml:7-105](), [pnpm-lock.yaml:138-254]()

### Backend Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| Vercel AI SDK | 5.0.51 | Unified LLM interface |
| Supabase | 2.50.5 | Database & storage |
| PostgreSQL + pgvector | 0.2.1 | Vector similarity search |
| Drizzle ORM | 0.44.2 | Type-safe database queries |
| Trigger.dev | 4.0.4 | Background job orchestration |
| unstorage | 1.14.4 | Key-value storage abstraction |

Sources: [pnpm-workspace.yaml:7-105](), [pnpm-lock.yaml:138-254]()

### LLM Provider Integration

```mermaid
graph LR
    subgraph GenerateContent["generateContent() function"]
        BuildMsg["buildMessageObject()<br/>Construct ModelMessage[]"]
        StreamCall["streamText()<br/>AI SDK call with tools"]
        ModelGen["generationModel()<br/>Select provider model"]
    end
    
    subgraph Providers["AI SDK Provider Packages"]
        Gateway["createGateway()<br/>@ai-sdk/gateway"]
        Anthropic["anthropic()<br/>@ai-sdk/anthropic: 2.0.17"]
        OpenAI["openai()<br/>@ai-sdk/openai: 2.0.30"]
        Google["google()<br/>@ai-sdk/google: 2.0.14"]
        Fal["fal()<br/>@ai-sdk/fal: 1.0.13"]
    end
    
    subgraph ProviderOpts["Provider Options"]
        AnthropicOpts["AnthropicProviderOptions<br/>thinking.type"]
        OpenAIOpts["OpenAIResponsesProviderOptions<br/>reasoningEffort"]
    end
    
    BuildMsg --> StreamCall
    StreamCall --> ModelGen
    ModelGen --> Gateway
    
    Gateway --> Anthropic
    Gateway --> OpenAI
    Gateway --> Google
    Gateway --> Fal
    
    AnthropicOpts --> StreamCall
    OpenAIOpts --> StreamCall
```

**Figure 4: LLM Provider Integration Code Flow**

The `generateContent()` function at [packages/giselle/src/engine/generations/generate-content.ts:62-447]() orchestrates the generation:

1. **Message Building**: `buildMessageObject()` constructs `ModelMessage[]` from node configuration and context ([packages/giselle/src/engine/generations/utils.ts:36-302]())
2. **Provider Selection**: `generationModel()` selects the provider via AI Gateway ([packages/giselle/src/engine/generations/generate-content.ts:489-518]())
3. **Provider Options**: `getProviderOptions()` configures provider-specific settings like `thinking.type` for Anthropic or `reasoningEffort` for OpenAI ([packages/giselle/src/engine/generations/generate-content.ts:449-487]())
4. **Streaming**: `streamText()` from AI SDK handles streaming with tool support ([packages/giselle/src/engine/generations/generate-content.ts:256-288]())

Sources: [packages/giselle/src/engine/generations/generate-content.ts:1-519](), [packages/giselle/src/engine/generations/utils.ts:36-302](), [pnpm-workspace.yaml:8-12](), [packages/giselle/package.json:56-61]()

### Build Toolchain

| Tool | Version | Purpose |
|------|---------|---------|
| pnpm | 10.16.0 | Package manager with workspaces |
| Turbo | 2.4.2 | Monorepo build orchestration |
| tsup | 8.3.5 | TypeScript package bundler |
| Biome | 2.0.6 | Linting and formatting |
| TypeScript | 5.7.3 | Type safety |
| Vitest | 3.2.4 | Unit testing |
| Playwright | 1.53.0 | E2E testing |

Sources: [package.json:264-282](), [pnpm-workspace.yaml:8-28](), [knip.ts:1-120]()

## Deployment and Infrastructure

### Hosting

- **Application Hosting**: Vercel (studio.giselles.ai, playground, ui.giselles.ai)
- **Background Jobs**: Trigger.dev v4 with Node.js 22.x runtime
- **Database**: Supabase PostgreSQL with Drizzle ORM
- **Blob Storage**: Supabase Storage (S3-compatible via `@aws-sdk/client-s3`)
- **Vector Store**: PostgreSQL with pgvector extension (`pgvector: 0.2.1`)

**Background Job Configuration:**

Trigger.dev jobs are configured at [apps/studio.giselles.ai/trigger.config.ts]() with two main jobs:
- `generate-content`: Executes `generateContent()` asynchronously
- `run-act-job`: Executes full workflow `runAct()` asynchronously

Job triggering occurs at [apps/studio.giselles.ai/giselle-engine.ts:426-534]() via:
```typescript
await jobs.trigger<typeof generateContentJob>("generate-content", {
  generationId: generation.id,
  requestId,
  userId,
  team: { id, subscriptionId, plan }
})
```

Sources: [apps/studio.giselles.ai/package.json:66](), [apps/studio.giselles.ai/giselle-engine.ts:19,426-534](), [pnpm-lock.yaml:175-176,178-179]()

### Configuration Management

```mermaid
graph TB
    subgraph Dev["Development Environment"]
        EnvLocal[".env.local<br/>API keys & secrets"]
        LocalFlags["Local environment variables<br/>Feature flags"]
    end
    
    subgraph Prod["Production Environment"]
        EdgeConfig["Vercel Edge Config<br/>Dynamic feature flags"]
        VercelEnv["Vercel Environment Variables<br/>VERCEL_ENV"]
    end
    
    subgraph App["Next.js Application"]
        FlagEval["Flag Evaluation<br/>takeLocalEnv() / Edge Config query"]
        ServerComponent["Server Components<br/>Workspace Layout"]
        Providers["React Context Providers<br/>FeatureFlagContext"]
    end
    
    EnvLocal --> FlagEval
    LocalFlags --> FlagEval
    EdgeConfig --> FlagEval
    VercelEnv --> FlagEval
    
    FlagEval --> ServerComponent
    ServerComponent --> Providers
    
    style Dev fill:#e8f5e9
    style Prod fill:#e3f2fd
    style App fill:#fff3e0
```

**Figure 5: Configuration and Feature Flag System**

Sources: [apps/studio.giselles.ai/package.json:62](), Diagram 6 from high-level system diagrams

### Observability

| Service | Purpose | Integration Point |
|---------|---------|-------------------|
| Sentry | Error tracking | `@sentry/nextjs` instrumentation |
| Langfuse | LLM tracing & metrics | `langfuse-vercel` SDK |
| OpenTelemetry | Distributed tracing | `@vercel/otel` integration |
| Vercel Speed Insights | Performance monitoring | Built-in |

Sources: [apps/studio.giselles.ai/package.json:56,64,67,80](), [apps/studio.giselles.ai/instrumentation-client.ts:1-29]()

## Development Workflow

### Build Pipeline

The monorepo uses **Turbo** for orchestrating builds with caching and filtering capabilities:

```bash
# Build all packages
pnpm turbo build

# Build only SDK packages  
pnpm turbo build --filter="@giselle-sdk/*"

# Build studio app and its dependencies
pnpm turbo build --filter=studio.giselles.ai
```

Sources: [package.json:277-279](), [knip.ts:85-116]()

### Code Quality Gates

1. **Biome**: Linting and formatting ([package.json:265-267]())
2. **Knip**: Unused code detection ([package.json:274-276]())
3. **Type Checking**: TypeScript strict mode ([apps/studio.giselles.ai/tsconfig.json:7]())
4. **Unit Tests**: Vitest with happy-dom ([pnpm-workspace.yaml:95]())
5. **E2E Tests**: Playwright ([apps/studio.giselles.ai/package.json:107,116]())

Sources: [package.json:264-282](), [knip.ts:1-120](), [apps/studio.giselles.ai/tsconfig.json:1-38]()

### Release Process

**Changesets** manages versioning and publishing for SDK packages:

```bash
# Create a changeset
pnpm changeset

# Version packages (creates release PR)
pnpm changeset version

# Publish to npm
pnpm changeset publish
```

Sources: [package.json:268-270](), Diagram 7 from high-level system diagrams

## Summary

The Giselle platform is a comprehensive AI workflow orchestration system built on modern web technologies. Its **layered monorepo architecture** separates concerns between user-facing applications, internal UI components, and a robust SDK ecosystem. The system leverages **Next.js 15 with React 19** for the frontend, integrates with **multiple LLM providers** through the Vercel AI SDK, and uses **PostgreSQL with pgvector** for RAG capabilities. **Trigger.dev** handles background job processing while **Supabase** provides database and storage infrastructure. The entire stack is deployed to **Vercel** with comprehensive observability through Sentry, Langfuse, and OpenTelemetry.

Sources: All diagrams and sections above

---

# Page: Project Structure and Organization

# Project Structure and Organization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/playground/package.json](apps/playground/package.json)
- [apps/studio.giselles.ai/package.json](apps/studio.giselles.ai/package.json)
- [internal-packages/workflow-designer-ui/package.json](internal-packages/workflow-designer-ui/package.json)
- [package.json](package.json)
- [packages/giselle/package.json](packages/giselle/package.json)
- [pnpm-lock.yaml](pnpm-lock.yaml)
- [pnpm-workspace.yaml](pnpm-workspace.yaml)

</details>



## Purpose and Scope

This document describes the physical organization of the Giselle AI monorepo, including the directory structure, package boundaries, and how different components are distributed across the filesystem. It covers the `apps/`, `packages/`, `internal-packages/`, and `tools/` directories, the pnpm workspace configuration, and the dependency relationships between packages. For information about the build system and task orchestration, see [Build System and Dependencies](#1.2). For development workflows and tooling, see [Development Workflow](#1.3).

## Monorepo Overview

The Giselle AI project is organized as a pnpm monorepo with Turbo for task orchestration. The workspace is defined in [pnpm-workspace.yaml:1-6]() and contains four primary directory categories:

```mermaid
graph TB
    Root["Root<br/>(pnpm workspace)"]
    
    Apps["apps/<br/>(Deployable applications)"]
    Packages["packages/<br/>(Giselle SDK modules)"]
    InternalPkgs["internal-packages/<br/>(Shared UI components)"]
    Tools["tools/<br/>(Build configurations)"]
    
    Studio["studio.giselles.ai<br/>(Production app)"]
    Playground["playground<br/>(Dev environment)"]
    
    GisellePkg["@giselle-sdk/giselle<br/>(Core engine)"]
    DataType["@giselle-sdk/data-type<br/>(Type definitions)"]
    LangModel["@giselle-sdk/language-model<br/>(LLM abstractions)"]
    RAG["@giselle-sdk/rag<br/>(Vector operations)"]
    Flow["@giselle-sdk/flow<br/>(Workflow primitives)"]
    DocPreproc["@giselle-sdk/document-preprocessor<br/>(PDF extraction)"]
    GitHubTool["@giselle-sdk/github-tool<br/>(GitHub integration)"]
    Langfuse["@giselle-sdk/langfuse<br/>(Observability)"]
    Supabase["@giselle-sdk/supabase-driver<br/>(Storage driver)"]
    VectorAdapters["@giselle-sdk/vector-store-adapters<br/>(Store implementations)"]
    TextEditor["@giselle-sdk/text-editor<br/>(Tiptap wrapper)"]
    TextEditorUtils["@giselle-sdk/text-editor-utils<br/>(Editor utilities)"]
    WebSearch["@giselle-sdk/web-search<br/>(Search integration)"]
    Utils["@giselle-sdk/utils<br/>(Shared utilities)"]
    
    UI["@giselle-internal/ui<br/>(Component library)"]
    WDUI["@giselle-internal/workflow-designer-ui<br/>(Editor components)"]
    
    TSConfig["@giselle/giselle-sdk-tsconfig<br/>(Shared TypeScript config)"]
    
    Root --> Apps
    Root --> Packages
    Root --> InternalPkgs
    Root --> Tools
    
    Apps --> Studio
    Apps --> Playground
    
    Packages --> GisellePkg
    Packages --> DataType
    Packages --> LangModel
    Packages --> RAG
    Packages --> Flow
    Packages --> DocPreproc
    Packages --> GitHubTool
    Packages --> Langfuse
    Packages --> Supabase
    Packages --> VectorAdapters
    Packages --> TextEditor
    Packages --> TextEditorUtils
    Packages --> WebSearch
    Packages --> Utils
    
    InternalPkgs --> UI
    InternalPkgs --> WDUI
    
    Tools --> TSConfig
```

**Sources:** [pnpm-workspace.yaml:1-6](), [pnpm-lock.yaml:255-1656]()

### Directory Layout

The repository follows a clear separation of concerns:

| Directory | Purpose | Visibility | Example Package |
|-----------|---------|------------|-----------------|
| `apps/` | Deployable Next.js applications | Private (not published) | `studio.giselles.ai` |
| `packages/` | Reusable SDK modules with `@giselle-sdk/*` scope | Public/Internal | `@giselle-sdk/giselle` |
| `internal-packages/` | Shared UI components with `@giselle-internal/*` scope | Internal only | `@giselle-internal/ui` |
| `tools/` | Build configurations and tooling with `@giselle/*` scope | Internal only | `@giselle/giselle-sdk-tsconfig` |
| `scripts/` | Utility scripts and codemods | Not packages | `report-colors.mjs` |

**Sources:** [pnpm-workspace.yaml:1-6](), [package.json:1-47]()

## Apps Directory

The `apps/` directory contains three Next.js 15 applications that consume the SDK packages:

### studio.giselles.ai

The production application deployed at studio.giselles.ai. This is the primary user-facing application that provides:

- Visual workflow designer interface
- Stage system for workflow execution
- Team and subscription management
- Vector store configuration
- GitHub integration

**Key characteristics:**
- Next.js 15 with App Router and Server Actions
- React 19
- Drizzle ORM for database access (`drizzle-orm`)
- Supabase for authentication and storage (`@supabase/supabase-js`, `@supabase/ssr`)
- Full SDK integration (`@giselle-sdk/giselle`, `@giselle-sdk/rag`, `@giselle-sdk/github-tool`, etc.)
- Production observability (`@sentry/nextjs`, `langfuse-vercel`, `@vercel/otel`)
- Trigger.dev integration (`@trigger.dev/sdk`)
- Turbopack for development builds (`next dev --turbopack`)

**Configuration files:**
- [apps/studio.giselles.ai/next.config.ts:1-164]() - Next.js configuration with Sentry integration
- [apps/studio.giselles.ai/trigger.config.ts:1-28]() - Trigger.dev job configuration
- [apps/studio.giselles.ai/tsconfig.json:1-39]() - TypeScript configuration with path aliases

**Sources:** [apps/studio.giselles.ai/package.json:1-127](), [apps/studio.giselles.ai/next.config.ts:1-164](), [apps/studio.giselles.ai/trigger.config.ts:1-28]()

### playground

A simplified development environment for testing SDK features locally without the full production stack.

**Key characteristics:**
- Minimal dependencies (only core SDK packages)
- Simplified feature flag configuration
- Local-only storage (filesystem via `unstorage`)
- Faster iteration cycle with Turbopack
- Excludes production services (Sentry, Langfuse, Trigger.dev)

**Package dependencies:**
```json
{
  "@giselle-sdk/giselle": "workspace:*",
  "@giselle-sdk/data-type": "workspace:*",
  "@giselle-internal/ui": "workspace:^",
  "@giselle-internal/workflow-designer-ui": "workspace:*",
  "@giselle-sdk/langfuse": "workspace:^",
  "@giselle-sdk/supabase-driver": "workspace:^"
}
```

**Configuration files:**
- [apps/playground/next.config.ts:1-17]() - Minimal Next.js configuration

**Sources:** [apps/playground/package.json:1-48](), [apps/playground/next.config.ts:1-17]()

### ui.giselles.ai

A component showcase application for the `@giselle-internal/ui` package, serving as a living style guide and development environment for UI components.

**Key characteristics:**
- Next.js 15 with Turbopack
- Displays component examples and documentation
- Minimal dependencies (only `@giselle-internal/ui` and core React)
- Used for visual testing and component development

**Package dependencies:**
```json
{
  "@giselle-internal/ui": "workspace:*",
  "clsx": "catalog:",
  "lucide-react": "catalog:",
  "next": "catalog:",
  "react": "catalog:",
  "react-dom": "catalog:"
}
```

**Sources:** [apps/ui.giselles.ai/package.json:1-27](), [pnpm-lock.yaml:661-703]()

## Packages Directory (Giselle SDK)

The `packages/` directory contains the modular Giselle SDK. All packages use the `@giselle-sdk/*` scope and are organized by functional domain.

### Core Engine Packages

#### @giselle-sdk/giselle

The primary engine export that orchestrates AI operations. This is the main entry point that most applications consume.

**Key exports:**
- `NextGiselleEngine` factory for Next.js integration
- `useGenerationExecutor` for generation lifecycle management
- HTTP routers (`createJsonRouters`, `createFormDataRouters`)
- Generation functions (`generateText`, `generateContent`, `generateImage`)
- Storage interfaces (`GiselleStorage`)
- `batchWriter` utility for buffered writes

**Dependencies:**
- `@giselle-sdk/flow` - Workflow primitives (`workspace:^`)
- `@giselle-sdk/language-model` - LLM abstractions (`workspace:^`)
- `@giselle-sdk/github-tool` - GitHub integration (`workspace:^`)
- `@giselle-sdk/text-editor-utils` - Text processing (`workspace:^`)
- `@giselle-sdk/web-search` - Search capabilities (`workspace:^`)
- `@ai-sdk/anthropic`, `@ai-sdk/fal`, `@ai-sdk/google`, `@ai-sdk/openai`, `@ai-sdk/perplexity` - LLM providers (`catalog:`)
- `ai` - Vercel AI SDK 5.0.51 (`catalog:`)
- `openai` - Direct OpenAI integration (`catalog:`)
- `unstorage` - Storage abstraction (`catalog:`)
- `pg` - PostgreSQL client (`catalog:`)
- `swr` - React data fetching (`catalog:`)

**Key utilities:**
- [packages/giselle/src/utils/batch.ts:1-123]() - `batchWriter` for buffered operations

**Sources:** [pnpm-lock.yaml:919-1018](), [packages/giselle/src/utils/batch.ts:1-123]()

#### @giselle-sdk/data-type

Type definitions and Zod schemas for the entire system. This package provides the shared type system used across all SDK packages.

**Key exports:**
- Node type definitions (text generation, image generation, query, action)
- Workspace schemas
- Generation result types
- Validation schemas

**Dependencies:**
- `@giselle-sdk/flow` - Flow type definitions
- `@giselle-sdk/language-model` - Model type definitions
- `zod` - Runtime validation

**Sources:** [packages/data-type/package.json (inferred from pnpm-lock.yaml:804-827)]()

#### @giselle-sdk/language-model

LLM provider abstractions that enable model-agnostic code.

**Key exports:**
- Model ID type definitions
- Provider mapping
- Model capability definitions
- Tier-based model filtering

**Dependencies:**
- `zod` - Schema validation

**Sources:** [packages/language-model/package.json (inferred from pnpm-lock.yaml:1050-1064)]()

### Data Processing Packages

#### @giselle-sdk/rag

Vector search and RAG (Retrieval-Augmented Generation) operations.

**Key exports:**
- Embedding generation
- Vector similarity search
- Chunking strategies
- Query services

**Dependencies:**
- `@giselle-sdk/data-type` - Type definitions
- `@ai-sdk/google` - Google embeddings
- `@ai-sdk/openai` - OpenAI embeddings
- `ai` - Embedding utilities
- `openai` - Direct OpenAI integration
- `pg` - PostgreSQL client
- `pgvector` - Vector operations

**Sources:** [packages/rag/package.json (inferred from pnpm-lock.yaml:1066-1110)]()

#### @giselle-sdk/document-preprocessor

PDF and document processing utilities.

**Key exports:**
- PDF text extraction
- Image rendering from PDFs
- Text normalization

**Dependencies:**
- `@embedpdf/pdfium` - PDFium WASM bindings
- `pngjs` - PNG manipulation

**Sources:** [packages/document-preprocessor/package.json (inferred from pnpm-lock.yaml:829-855)]()

### Integration Packages

#### @giselle-sdk/github-tool

GitHub API integration for workflow tools and vector store ingestion.

**Key exports:**
- GitHub tool definitions
- Repository indexing
- Webhook handling
- GraphQL client setup

**Dependencies:**
- `@giselle-sdk/rag` - Vector operations
- `@octokit/auth-app` - GitHub App authentication
- `@octokit/core` - GitHub API client
- `@octokit/webhooks` - Webhook verification
- `@urql/core` - GraphQL client
- `gql.tada` - Type-safe GraphQL
- `tar` - Tarball extraction

**Sources:** [packages/github-tool/package.json (inferred from pnpm-lock.yaml:970-1020)]()

#### @giselle-sdk/web-search

Web search integration for action nodes.

**Dependencies:** (minimal, inferred to be a lightweight wrapper)

**Sources:** (Referenced in @giselle-sdk/giselle dependencies)

### Storage and Observability Packages

#### @giselle-sdk/supabase-driver

Storage driver implementation for Supabase and S3-compatible services.

**Key exports:**
- `SupabaseStorage` implementation
- S3 adapter
- Storage interface compliance

**Dependencies:**
- `@giselle-sdk/giselle` - Storage interface
- `@aws-sdk/client-s3` - S3 operations
- `@supabase/supabase-js` - Supabase client
- `zod` - Configuration validation

**Sources:** [packages/supabase-driver/package.json (inferred from pnpm-lock.yaml:1112-1132)]()

#### @giselle-sdk/langfuse

Langfuse observability integration with callback system.

**Key exports:**
- Generation callbacks
- Embedding callbacks
- Metadata enrichment
- Trace context management

**Dependencies:**
- `@giselle-sdk/giselle` - Engine callbacks
- `@giselle-sdk/data-type` - Type definitions
- `@giselle-sdk/language-model` - Model metadata
- `@giselle-sdk/rag` - Embedding callbacks
- `langfuse` - Langfuse SDK

**Sources:** [packages/langfuse/package.json (inferred from pnpm-lock.yaml:1022-1048)]()

#### @giselle-sdk/vector-store-adapters

Vector store implementations for different sources.

**Key exports:**
- GitHub repository vector store
- Document vector store
- Pull request embeddings store

**Dependencies:**
- Implements vector store interfaces from `@giselle-sdk/rag`

**Sources:** [apps/studio.giselles.ai/package.json:33]()

### UI and Editor Packages

#### @giselle-sdk/text-editor

Tiptap-based text editor wrapper used in node configuration.

**Key exports:**
- Configured Tiptap editor
- Placeholder extensions
- Editor state management

**Dependencies:**
- `@giselle-sdk/data-type` - Type definitions
- `@giselle-sdk/giselle` - Engine integration
- `@giselle-sdk/text-editor-utils` - Utilities
- `@tiptap/react` - React integration
- `@tiptap/extension-placeholder` - Placeholder support
- `clsx` - Conditional classes
- `lucide-react` - Icons

**Sources:** [packages/text-editor/package.json (inferred from pnpm-lock.yaml:1134-1196)]()

#### @giselle-sdk/text-editor-utils

Shared utilities for text editor functionality.

**Key exports:**
- Text transformation utilities
- Content serialization
- Editor helpers

**Sources:** (Referenced in multiple packages)

### Supporting Packages

#### @giselle-sdk/flow

Workflow and trigger primitive definitions.

**Key exports:**
- Flow trigger schemas
- Workflow step definitions
- Trigger condition types

**Dependencies:**
- `zod` - Schema validation

**Sources:** [packages/flow/package.json (inferred from pnpm-lock.yaml:857-868)]()

#### @giselle-sdk/utils

Shared utilities used across SDK packages.

**Key exports:**
- Common helper functions
- Type utilities

**Sources:** (Referenced in @giselle-sdk/giselle and @giselle-sdk/data-type)

## Internal Packages Directory

The `internal-packages/` directory contains shared UI components used by applications but not intended for external distribution.

### @giselle-internal/ui

Base component library providing design system primitives.

**Key exports:**
- Button, Input, Dialog components
- Radix UI wrappers
- Tailwind-based styling
- Icon components

**Dependencies:**
- `clsx` - Conditional classes
- `lucide-react` - Icon library
- `radix-ui` - Unstyled primitives
- `react` / `react-dom` - React runtime

**Sources:** [internal-packages/ui/package.json (inferred from pnpm-lock.yaml:658-690)]()

### @giselle-internal/workflow-designer-ui

Workflow designer-specific components built on ReactFlow.

**Key exports:**
- `Editor` component
- `NodeComponent` implementations
- Properties panels
- Toolbar components
- Generation result displays

**Dependencies:**
- `@giselle-internal/ui` - Base components
- `@giselle-sdk/giselle` - Engine integration
- `@giselle-sdk/data-type` - Type definitions
- `@giselle-sdk/flow` - Flow definitions
- `@giselle-sdk/language-model` - Model types
- `@giselle-sdk/text-editor` - Text editing
- `@xyflow/react` - ReactFlow canvas
- `zustand` - State management
- `swr` - Data fetching
- `react-markdown` - Markdown rendering
- `motion` - Animations

**Sources:** [internal-packages/workflow-designer-ui/package.json (inferred from pnpm-lock.yaml:692-802)]()

## Tools Directory

The `tools/` directory contains shared build configurations and tooling.

### @giselle/giselle-sdk-tsconfig

Shared TypeScript configuration for SDK packages.

**Usage:**
```json
{
  "extends": "@giselle/giselle-sdk-tsconfig"
}
```

Referenced by all SDK packages for consistent TypeScript compilation settings.

**Sources:** (Referenced throughout pnpm-lock.yaml in devDependencies)

## Package Dependency Graph

```mermaid
graph TB
    subgraph "Applications"
        Studio["studio.giselles.ai"]
        Playground["playground"]
    end
    
    subgraph "Core Engine"
        Giselle["@giselle-sdk/giselle"]
        DataType["@giselle-sdk/data-type"]
        LangModel["@giselle-sdk/language-model"]
    end
    
    subgraph "Domain Logic"
        Flow["@giselle-sdk/flow"]
        RAG["@giselle-sdk/rag"]
        GitHubTool["@giselle-sdk/github-tool"]
        WebSearch["@giselle-sdk/web-search"]
        DocPreproc["@giselle-sdk/document-preprocessor"]
    end
    
    subgraph "Infrastructure"
        Supabase["@giselle-sdk/supabase-driver"]
        Langfuse["@giselle-sdk/langfuse"]
        VectorAdapters["@giselle-sdk/vector-store-adapters"]
    end
    
    subgraph "UI Components"
        UI["@giselle-internal/ui"]
        WDUI["@giselle-internal/workflow-designer-ui"]
        TextEditor["@giselle-sdk/text-editor"]
        TextEditorUtils["@giselle-sdk/text-editor-utils"]
    end
    
    subgraph "External Dependencies"
        AISDK["ai (Vercel AI SDK)"]
        NextJS["next"]
        OpenAI["openai"]
        Unstorage["unstorage"]
        Octokit["@octokit/*"]
        Zustand["zustand"]
        ReactFlow["@xyflow/react"]
    end
    
    Studio --> Giselle
    Studio --> DataType
    Studio --> RAG
    Studio --> GitHubTool
    Studio --> Langfuse
    Studio --> Supabase
    Studio --> VectorAdapters
    Studio --> UI
    Studio --> WDUI
    Studio --> DocPreproc
    
    Playground --> Giselle
    Playground --> DataType
    Playground --> UI
    Playground --> WDUI
    Playground --> Supabase
    
    Giselle --> DataType
    Giselle --> LangModel
    Giselle --> Flow
    Giselle --> GitHubTool
    Giselle --> TextEditorUtils
    Giselle --> WebSearch
    Giselle --> AISDK
    Giselle --> OpenAI
    Giselle --> Unstorage
    Giselle --> NextJS
    
    DataType --> Flow
    DataType --> LangModel
    
    RAG --> DataType
    RAG --> AISDK
    RAG --> OpenAI
    
    GitHubTool --> RAG
    GitHubTool --> Octokit
    
    Langfuse --> Giselle
    Langfuse --> DataType
    Langfuse --> LangModel
    Langfuse --> RAG
    
    Supabase --> Giselle
    
    WDUI --> UI
    WDUI --> Giselle
    WDUI --> DataType
    WDUI --> Flow
    WDUI --> LangModel
    WDUI --> TextEditor
    WDUI --> ReactFlow
    WDUI --> Zustand
    
    TextEditor --> DataType
    TextEditor --> Giselle
    TextEditor --> TextEditorUtils
    
    VectorAdapters -.implements.-> RAG
```

**Sources:** [pnpm-lock.yaml:255-1656]()

## Workspace Protocol and Dependency Management

The monorepo uses pnpm's workspace protocol for internal dependencies, enabling rapid development without publishing:

### Workspace Dependency Syntax

| Syntax | Meaning | Example | Usage |
|--------|---------|---------|-------|
| `workspace:*` | Match any version in workspace | `"@giselle-sdk/giselle": "workspace:*"` | Used for packages that must always use the local version |
| `workspace:^` | Match with semver caret | `"@giselle-internal/ui": "workspace:^"` | Used for packages that could theoretically use published versions |

### Catalog System

The workspace uses pnpm's catalog feature to centralize external dependency versions. Defined in [pnpm-workspace.yaml:7-105]() and referenced in individual packages with the `catalog:` protocol:

```json
{
  "dependencies": {
    "next": "catalog:",
    "react": "catalog:",
    "zod": "catalog:"
  }
}
```

**Common cataloged dependencies (from pnpm-workspace.yaml catalog):**
- `next`: `15.5.2`
- `react`: `19.1.1`
- `react-dom`: `19.1.1`
- `typescript`: `5.7.3`
- `zod`: `3.25.76`
- `ai`: `5.0.51`
- `@xyflow/react`: `12.8.3`
- `tailwindcss`: `4.1.10`
- `@tailwindcss/postcss`: `4.1.10`
- `@ai-sdk/anthropic`: `2.0.17`
- `@ai-sdk/openai`: `2.0.30`
- `@ai-sdk/google`: `2.0.14`
- `@supabase/supabase-js`: `2.50.5`
- `@trigger.dev/sdk`: `4.0.4`
- `langfuse`: `3.38.4`

**Sources:** [pnpm-workspace.yaml:7-105](), [pnpm-lock.yaml:7-254]()

### Package Manager Configuration

The workspace enforces strict package manager and Node.js version constraints:

**Package manager:**
- pnpm version: `10.16.0` (specified in [apps/studio.giselles.ai/package.json:20]())
- Lockfile version: `9.0` with `autoInstallPeers: true` ([pnpm-lock.yaml:1-5]())

**Node.js version:**
- Required: `22.x` ([apps/studio.giselles.ai/package.json:5-6]())

**Dependency overrides:**
```yaml
pnpm:
  overrides:
    vite: "7.1.3"
    cookie: "1.0.2"
    "@electric-sql/client": "1.0.10"
```

These overrides ensure consistent versions across the dependency tree, particularly important for:
- `vite`: Build tool version consistency
- `cookie`: Security updates
- `@electric-sql/client`: Version compatibility

**Sources:** [apps/studio.giselles.ai/package.json:4-6,20](), [pnpm-lock.yaml:1-5,256-260]()

### Package Manager Configuration

The workspace enforces Node.js version constraints and uses specific overrides:

```yaml
# pnpm-workspace.yaml
packageManager: "pnpm@10.16.0"

engines:
  node: ">=22"

pnpm:
  overrides:
    vite: "7.1.3"
    cookie: "1.0.2"
    "@electric-sql/client": "1.0.10"
```

**Sources:** [package.json:36-46](), [pnpm-lock.yaml:250-253]()

## Scripts and Utilities

The `scripts/` directory contains non-package utilities:

### report-colors.mjs

A ripgrep-based utility for auditing color usage across the codebase.

**Usage:**
```bash
node scripts/report-colors.mjs
node scripts/report-colors.mjs --out .reports/report-colors.json
```

**Scans for:**
- Tailwind utility classes (`text-*`, `bg-*`, `border-*`, etc.)
- Hex colors (`#fff`, `#ffffff`, etc.)
- CSS functions (`rgba()`, `hsla()`, `oklch()`)
- CSS variables (`--color-*`, `--brand-*`, etc.)
- SVG attributes (`fill=`, `stroke=`)

**Sources:** [scripts/report-colors.mjs:1-337](), [package.json:21-22]()

### Codemods

Code transformation utilities for automated refactoring:

- `replace-text-black-600-20.mjs` - Consolidates `text-black-600/20` usages
- `replace-text-white-900-to-inverse.mjs` - Updates color class patterns

**Usage:**
```bash
# Preview changes
pnpm codemod:text-black-600-20

# Apply changes
pnpm codemod:text-black-600-20:apply
```

**Sources:** [package.json:23-26]()

## Build Configuration and TypeScript Setup

### Build Output Locations

Each package type produces build artifacts in different locations:

| Package Type | Build Output | Build Command | Example |
|--------------|--------------|---------------|---------|
| Next.js apps | `.next/` directory | `next build --turbopack` | [apps/studio.giselles.ai/package.json:11]() |
| SDK packages | `dist/` directory | `tsup` | SDK packages use tsup for bundling |
| Internal packages | Not built separately | Consumed as TypeScript source | Used directly via path aliases |

### TypeScript Configuration

**Studio app configuration:**
- Base config: [apps/studio.giselles.ai/tsconfig.json:1-39]()
- Module resolution: `bundler`
- JSX: `preserve` (handled by Next.js)
- Path aliases:
  - `@/*` maps to app root
  - `@giselles-ai/*` maps to `./packages/*`
  - `@giselles-ai/icons/*` maps to workflow-designer-ui icons

**SDK packages configuration:**
- Shared config: `@giselle/giselle-sdk-tsconfig` (referenced in devDependencies)
- Target: `ES2017`
- Module system: ESM

### PostCSS Configuration

All applications use Tailwind CSS v4 with the PostCSS plugin:

```javascript
// apps/studio.giselles.ai/postcss.config.mjs
const config = {
  plugins: {
    "@tailwindcss/postcss": {},
  },
};
```

**Sources:** [apps/studio.giselles.ai/package.json:9-11](), [apps/studio.giselles.ai/tsconfig.json:1-39](), [apps/studio.giselles.ai/postcss.config.mjs:1-9]()

### Server External Packages

Both Next.js apps configure `serverExternalPackages` to prevent bundling of certain Node.js-specific dependencies:

**Studio app externals:**
```typescript
export const serverExternalPackages = [
  "@embedpdf/pdfium",
  "@opentelemetry/sdk-node",
  "pino",
  "pino-pretty",
  "unstorage",
  "happy-dom",
  "@supabase/supabase-js",
  "@supabase/realtime-js",
];
```

**Playground app externals:**
```typescript
serverExternalPackages: [
  "unstorage",
  "happy-dom",
  "@supabase/supabase-js",
  "@supabase/realtime-js",
]
```

These packages are excluded from webpack bundling to avoid compatibility issues with native modules and Node.js-specific APIs.

**Sources:** [apps/studio.giselles.ai/next.config.ts:13-22](), [apps/playground/next.config.ts:5-10](), [knip.ts:10-83]()

## Summary

The Giselle AI monorepo structure provides clear separation between:

1. **Applications** (`apps/`) - Deployable Next.js applications consuming the SDK
2. **Public SDK** (`packages/@giselle-sdk/*`) - Modular, reusable packages organized by domain
3. **Internal UI** (`internal-packages/@giselle-internal/*`) - Shared components not for external distribution
4. **Build tooling** (`tools/@giselle/*`) - Shared configurations

This architecture enables:
- Independent versioning of SDK modules
- Shared UI components across applications
- Clear dependency boundaries
- Efficient build caching with Turbo
- Type-safe workspace dependencies with pnpm

The workspace protocol and catalog system ensure version consistency while allowing rapid local development without publishing packages to npm.

**Sources:** [pnpm-workspace.yaml:1-102](), [package.json:1-47](), [pnpm-lock.yaml:1-1656]()

---

# Page: Package Architecture and Dependencies

# Package Architecture and Dependencies

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/playground/package.json](apps/playground/package.json)
- [apps/studio.giselles.ai/package.json](apps/studio.giselles.ai/package.json)
- [internal-packages/workflow-designer-ui/package.json](internal-packages/workflow-designer-ui/package.json)
- [package.json](package.json)
- [packages/giselle/package.json](packages/giselle/package.json)
- [pnpm-lock.yaml](pnpm-lock.yaml)
- [pnpm-workspace.yaml](pnpm-workspace.yaml)

</details>



## Overview and Scope

This document details the package architecture of the Giselle AI platform, covering the dependency graph, the catalog-based dependency management system, and the organization of packages into logical layers. The platform is structured as a pnpm monorepo with workspace-scoped packages that follow a layered dependency architecture.

For information about the monorepo's build system and development workflow, see [Build System and Development Workflow](#1.3). For details about how the core engine orchestrates these packages, see [Core Engine and SDK](#2).

## Monorepo Structure

The Giselle AI platform uses a pnpm workspace monorepo with the following directory structure:

| Directory | Purpose | Package Naming |
|-----------|---------|----------------|
| `apps/` | User-facing applications | Domain-based (e.g., `studio.giselles.ai`) |
| `internal-packages/` | Private shared UI and workflow components | `@giselle-internal/*` scope |
| `packages/` | Public-scoped SDK and integration packages | `@giselles-ai/*` scope |
| `tools/` | Build tools and shared configurations | `@giselles-ai/*` scope |

The workspace configuration defines package locations and sets a minimum release age for dependencies:

[pnpm-workspace.yaml:1-6]()

**Sources:** [pnpm-workspace.yaml:1-6]()

## Dependency Catalog System

The monorepo uses pnpm's catalog feature to manage dependency versions centrally. This ensures consistent versions across all packages and simplifies version updates.

### Catalog Definition

The catalog is defined in `pnpm-workspace.yaml` and contains version specifications for all shared dependencies:

```yaml
catalog:
  '@ai-sdk/anthropic': 2.0.17
  '@ai-sdk/openai': 2.0.30
  react: 19.1.1
  next: 15.5.2
  # ... 95+ more entries
```

[pnpm-workspace.yaml:7-101]()

### Catalog Usage

Packages reference catalog entries using the `catalog:` protocol:

```json
{
  "dependencies": {
    "react": "catalog:",
    "@ai-sdk/openai": "catalog:",
    "next": "catalog:"
  }
}
```

This resolves to the version specified in the catalog. For example, `"react": "catalog:"` resolves to `19.1.1`.

### Catalog Benefits

1. **Single Source of Truth**: All version specifications exist in one location
2. **Atomic Updates**: Updating a dependency version updates all consumers
3. **Consistency Guarantees**: Prevents version mismatches across packages
4. **Simplified Maintenance**: No need to update versions in multiple `package.json` files

**Sources:** [pnpm-workspace.yaml:7-101](), [apps/studio.giselles.ai/package.json:25-106](), [packages/giselle/package.json:55-75]()

## Package Layers and Dependencies

The package architecture follows a layered dependency model where lower layers provide abstractions consumed by higher layers. Dependencies flow upward through the layers, with no circular dependencies.

### Layer Overview

```mermaid
graph TB
    Applications["Applications Layer<br/>(studio.giselles.ai, playground)"]
    Internal["Internal Packages Layer<br/>(@giselle-internal/*)"]
    Engine["Core Engine Layer<br/>(@giselles-ai/giselle)"]
    Integration["Integration Layer<br/>(rag, github-tool, etc.)"]
    Registry["Registry Layer<br/>(node-registry, etc.)"]
    Protocol["Protocol Layer<br/>(@giselles-ai/protocol)"]
    LangModel["Language Model Layer<br/>(@giselles-ai/language-model)"]
    Utils["Utility Layer<br/>(utils, telemetry, etc.)"]
    
    Applications --> Internal
    Applications --> Engine
    Internal --> Registry
    Internal --> Engine
    Engine --> Integration
    Engine --> Registry
    Integration --> Protocol
    Integration --> LangModel
    Registry --> Protocol
    Registry --> LangModel
    Registry --> Utils
```

**Sources:** [pnpm-lock.yaml:242-964]()

## Protocol Layer

### @giselles-ai/protocol

The foundational package defining shared TypeScript types and schemas used throughout the platform.

**Key Responsibilities:**
- Workflow graph data structures (nodes, edges, ports)
- Generation and Act execution types
- Vector store and RAG types
- Tool and model configuration schemas
- GitHub integration types

**Dependencies:**
```json
{
  "@ai-sdk/provider": "catalog:",
  "@giselles-ai/action-registry": "workspace:*",
  "@giselles-ai/language-model": "workspace:^",
  "@giselles-ai/trigger-registry": "workspace:*",
  "@octokit/webhooks": "catalog:",
  "ai": "catalog:",
  "zod": "catalog:"
}
```

[packages/protocol/package.json]() (not shown in files but referenced in dependencies)

**Sources:** [pnpm-lock.yaml:1084-1119](), [packages/giselle/package.json:44]()

### @giselles-ai/language-model

Provides model abstraction types and validation schemas.

**Dependencies:**
```json
{
  "zod": "catalog:"
}
```

[pnpm-lock.yaml:1043-1057]()

**Sources:** [pnpm-lock.yaml:1043-1057]()

## Registry Layer

Registry packages define pluggable components that extend workflow capabilities.

### @giselles-ai/action-registry

Defines action types for GitHub and other integrations.

**Dependencies:**
```json
{
  "@giselles-ai/utils": "workspace:*"
}
```

[pnpm-lock.yaml:828-842]()

### @giselles-ai/trigger-registry

Defines trigger types for workflow initiation (GitHub events, manual triggers, etc.).

**Dependencies:** Minimal (utility only)

### @giselles-ai/node-registry

Defines node types for the workflow graph (TextGeneration, ImageGeneration, Query, etc.).

**Dependencies:**
```json
{
  "@giselles-ai/action-registry": "workspace:*",
  "@giselles-ai/language-model": "workspace:*",
  "@giselles-ai/protocol": "workspace:*",
  "@giselles-ai/text-editor-utils": "workspace:*",
  "@giselles-ai/trigger-registry": "workspace:*"
}
```

[pnpm-lock.yaml:1059-1082]()

**Sources:** [pnpm-lock.yaml:828-842](), [pnpm-lock.yaml:1059-1082]()

## Core Engine Layer

### @giselles-ai/giselle

The main orchestration engine responsible for workflow execution, generation lifecycle management, and AI provider integration.

**Key Responsibilities:**
- Generation pipeline execution (text, image, query)
- Act runner for multi-step workflows
- AI provider abstraction and routing
- Storage and vault integration
- Tool orchestration

**Core Dependencies:**

| Package | Purpose |
|---------|---------|
| `@ai-sdk/anthropic`, `@ai-sdk/openai`, `@ai-sdk/google`, `@ai-sdk/fal` | AI provider integrations via Vercel AI SDK |
| `@ai-sdk/gateway` | AI Gateway for provider routing |
| `ai` (Vercel AI SDK) | Core AI streaming and generation abstractions |
| `@giselles-ai/protocol` | Type definitions |
| `@giselles-ai/action-registry`, `@giselles-ai/trigger-registry`, `@giselles-ai/node-registry` | Registry packages |
| `@giselles-ai/github-tool`, `@giselles-ai/web-search` | Tool integrations |
| `@giselles-ai/language-model` | Model abstractions |
| `openai` | OpenAI API client |
| `pg` | PostgreSQL client for database queries |

[packages/giselle/package.json:55-75]()

**Exports Structure:**

The package provides multiple entry points for different contexts:

```json
{
  ".": "./dist/index.js",
  "./next": "./next/dist/index.js",
  "./react": "./react/dist/index.js",
  "./client": "./client/dist/index.js"
}
```

[packages/giselle/package.json:16-41]()

**Sources:** [packages/giselle/package.json:1-80](), [pnpm-lock.yaml:872-964]()

## Integration Layer

Integration packages provide specialized functionality for external services and data processing.

### @giselles-ai/rag

Vector search and retrieval-augmented generation capabilities.

**Dependencies:**
```json
{
  "@ai-sdk/gateway": "catalog:",
  "@ai-sdk/google": "catalog:",
  "@ai-sdk/openai": "catalog:",
  "@giselles-ai/protocol": "workspace:*",
  "ai": "catalog:",
  "openai": "catalog:",
  "pg": "catalog:",
  "pgvector": "catalog:",
  "zod": "catalog:"
}
```

[pnpm-lock.yaml:1121-1162]()

### @giselles-ai/github-tool

GitHub integration including repository indexing, GraphQL API access, and webhook handling.

**Dependencies:**
```json
{
  "@giselles-ai/rag": "workspace:*",
  "@octokit/auth-app": "catalog:",
  "@octokit/core": "catalog:",
  "@octokit/request-error": "catalog:",
  "@octokit/webhooks": "catalog:",
  "@urql/core": "catalog:",
  "ai": "catalog:",
  "gql.tada": "catalog:",
  "tar": "catalog:",
  "urql": "catalog:",
  "zod": "catalog:"
}
```

[pnpm-lock.yaml:966-1016]()

### @giselles-ai/web-search

Web search tool integration for querying external search engines.

**Dependencies:** Minimal, focused on search API integration.

### @giselles-ai/document-preprocessor

Document processing pipeline for PDF text extraction and image rendering.

**Dependencies:**
```json
{
  "@embedpdf/pdfium": "catalog:",
  "pngjs": "catalog:"
}
```

[pnpm-lock.yaml:844-870]()

### @giselles-ai/supabase-driver

Storage driver implementation for Supabase backend.

**Dependencies:** Supabase client libraries and authentication.

**Sources:** [pnpm-lock.yaml:844-1162]()

## Utility Layer

### @giselles-ai/text-editor

Tiptap-based rich text editor component.

**Dependencies:**
```json
{
  "@tiptap/core": "catalog:",
  "@tiptap/extension-code-block-lowlight": "catalog:",
  "@tiptap/extension-mention": "catalog:",
  "@tiptap/extension-placeholder": "catalog:",
  "@tiptap/html": "catalog:",
  "@tiptap/react": "catalog:",
  "@tiptap/starter-kit": "catalog:",
  "@tiptap/suggestion": "catalog:"
}
```

### @giselles-ai/text-editor-utils

Utilities for text editor content manipulation and serialization.

### @giselles-ai/langfuse

LLM observability integration with Langfuse.

**Dependencies:**
```json
{
  "@giselles-ai/language-model": "workspace:^",
  "@giselles-ai/protocol": "workspace:^",
  "@giselles-ai/rag": "workspace:^",
  "langfuse": "catalog:"
}
```

[pnpm-lock.yaml:1018-1041]()

### @giselles-ai/telemetry

OpenTelemetry integration for distributed tracing.

### @giselles-ai/utils

Shared utility functions and helpers.

**Sources:** [pnpm-lock.yaml:1018-1041](), [pnpm-workspace.yaml:35-43]()

## Internal Packages Layer

### @giselle-internal/ui

Shared UI component library with design system primitives.

**Key Components:**
- Theme system with CSS variables
- Radix UI component wrappers
- Text editor integration
- Protocol type integration

**Dependencies:**
```json
{
  "@giselles-ai/protocol": "workspace:^",
  "@giselles-ai/text-editor": "workspace:^",
  "clsx": "catalog:",
  "lucide-react": "catalog:",
  "next": "catalog:",
  "radix-ui": "catalog:",
  "react": "catalog:",
  "react-dom": "catalog:"
}
```

[pnpm-lock.yaml:673-714]()

### @giselle-internal/workflow-designer-ui

Visual workflow editor components built on ReactFlow.

**Key Components:**
- Node rendering system
- Properties panels for node configuration
- Toolbar and node creation flow
- Generation execution and results display

**Dependencies:**
```json
{
  "@giselle-internal/ui": "workspace:^",
  "@giselles-ai/action-registry": "workspace:*",
  "@giselles-ai/giselle": "workspace:*",
  "@giselles-ai/language-model": "workspace:^",
  "@giselles-ai/node-registry": "workspace:*",
  "@giselles-ai/protocol": "workspace:*",
  "@giselles-ai/text-editor": "workspace:^",
  "@giselles-ai/text-editor-utils": "workspace:^",
  "@giselles-ai/trigger-registry": "workspace:*",
  "@xyflow/react": "catalog:",
  "clsx": "catalog:",
  "fast-levenshtein": "catalog:",
  "lucide-react": "catalog:",
  "marked": "catalog:",
  "motion": "catalog:",
  "next": "catalog:",
  "radix-ui": "catalog:",
  "react": "catalog:",
  "react-dom": "catalog:",
  "react-markdown": "catalog:",
  "react-resizable-panels": "catalog:",
  "swr": "catalog:",
  "zod": "catalog:",
  "zustand": "catalog:"
}
```

[internal-packages/workflow-designer-ui/package.json:15-41]()

**Sources:** [pnpm-lock.yaml:673-826](), [internal-packages/workflow-designer-ui/package.json:1-58]()

## Applications Layer

### studio.giselles.ai

The primary production application providing workflow design, execution, and management.

**Key Features:**
- Workflow designer integration
- Stage system for production execution
- Vector store management
- GitHub integration
- User authentication and team management
- Database schema via Drizzle ORM

**Dependencies Summary:**

| Category | Key Packages |
|----------|--------------|
| Internal | `@giselle-internal/ui`, `@giselle-internal/workflow-designer-ui` |
| Engine | `@giselles-ai/giselle`, `@giselles-ai/protocol`, `@giselles-ai/node-registry` |
| Integrations | `@giselles-ai/github-tool`, `@giselles-ai/rag`, `@giselles-ai/document-preprocessor` |
| Framework | `next`, `react`, `react-dom` |
| Database | `drizzle-orm`, `@vercel/postgres`, `pg` |
| Auth | `@supabase/supabase-js`, `@supabase/ssr`, `@supabase/auth-js` |
| AI | `ai`, `openai`, `langfuse-vercel` |
| Infrastructure | `@trigger.dev/sdk`, `@vercel/edge-config`, `@vercel/functions`, `@vercel/otel` |
| Observability | `@sentry/nextjs`, `@opentelemetry/*` packages |
| Payments | `stripe` |
| Email | `@react-email/components`, `nodemailer` |

[apps/studio.giselles.ai/package.json:25-106]()

### playground

Simplified development and testing application with reduced feature set.

**Dependencies:**
```json
{
  "@giselle-internal/ui": "workspace:^",
  "@giselle-internal/workflow-designer-ui": "workspace:*",
  "@giselles-ai/protocol": "workspace:*",
  "@giselles-ai/giselle": "workspace:*",
  "@giselles-ai/langfuse": "workspace:^",
  "@giselles-ai/supabase-driver": "workspace:^",
  "clsx": "catalog:",
  "lucide-react": "catalog:",
  "next": "catalog:",
  "react": "catalog:",
  "react-dom": "catalog:"
}
```

[apps/playground/package.json:19-30]()

**Sources:** [apps/studio.giselles.ai/package.json:1-132](), [apps/playground/package.json:1-42]()

## Key External Dependencies

The platform relies on several critical external dependencies managed through the catalog.

### AI and Language Models

```mermaid
graph LR
    Platform["Giselle Platform"]
    VercelAI["ai (Vercel AI SDK)<br/>v5.0.51"]
    Anthropic["@ai-sdk/anthropic<br/>v2.0.17"]
    OpenAI["@ai-sdk/openai<br/>v2.0.30"]
    Google["@ai-sdk/google<br/>v2.0.14"]
    Fal["@ai-sdk/fal<br/>v1.0.13"]
    Gateway["@ai-sdk/gateway<br/>v1.0.23"]
    OpenAIClient["openai<br/>v5.11.0"]
    
    Platform --> VercelAI
    Platform --> Gateway
    Gateway --> Anthropic
    Gateway --> OpenAI
    Gateway --> Google
    Gateway --> Fal
    Platform --> OpenAIClient
```

| Package | Version | Purpose |
|---------|---------|---------|
| `ai` | 5.0.51 | Core Vercel AI SDK for streaming and generation abstractions |
| `@ai-sdk/gateway` | 1.0.23 | AI Gateway for provider routing and fallback |
| `@ai-sdk/anthropic` | 2.0.17 | Claude model integration |
| `@ai-sdk/openai` | 2.0.30 | GPT model integration |
| `@ai-sdk/google` | 2.0.14 | Gemini model integration |
| `@ai-sdk/fal` | 1.0.13 | Fal.ai image generation |
| `openai` | 5.11.0 | Direct OpenAI API client for embeddings |

**Sources:** [pnpm-workspace.yaml:8-23](), [pnpm-lock.yaml:123-125]()

### React and UI Framework

```mermaid
graph LR
    Apps["Applications"]
    Next["next<br/>v15.5.2"]
    React["react<br/>v19.1.1"]
    ReactDOM["react-dom<br/>v19.1.1"]
    ReactFlow["@xyflow/react<br/>v12.9.0"]
    RadixUI["radix-ui<br/>v1.4.3"]
    Motion["motion<br/>v12.23.24"]
    
    Apps --> Next
    Next --> React
    Next --> ReactDOM
    Apps --> ReactFlow
    Apps --> RadixUI
    Apps --> Motion
    ReactFlow --> React
    RadixUI --> React
    Motion --> React
```

| Package | Version | Purpose |
|---------|---------|---------|
| `next` | 15.5.2 | React framework with App Router |
| `react` | 19.1.1 | Core React library |
| `react-dom` | 19.1.1 | React DOM renderer |
| `@xyflow/react` | 12.9.0 | Node-based graph editor for workflow canvas |
| `radix-ui` | 1.4.3 | Accessible UI primitives (meta-package) |
| `motion` | 12.23.24 | Animation library (Framer Motion successor) |
| `lucide-react` | 0.473.0 | Icon library |

**Sources:** [pnpm-workspace.yaml:58-92]()

### Database and Vector Store

| Package | Version | Purpose |
|---------|---------|---------|
| `pg` | 8.14.1 | PostgreSQL client |
| `pgvector` | 0.2.1 | PostgreSQL vector extension types |
| `drizzle-orm` | 0.44.2 | TypeScript ORM |
| `@vercel/postgres` | 0.9.0 | Vercel-optimized PostgreSQL client |

**Sources:** [pnpm-workspace.yaml:80-81](), [apps/studio.giselles.ai/package.json:76]()

### Authentication and Storage

| Package | Version | Purpose |
|---------|---------|---------|
| `@supabase/supabase-js` | 2.50.5 | Supabase client SDK |
| `@supabase/ssr` | 0.6.1 | Server-side rendering support |
| `@supabase/auth-js` | 2.70.0 | Authentication library |

**Sources:** [pnpm-workspace.yaml:30-32]()

### GitHub Integration

| Package | Version | Purpose |
|---------|---------|---------|
| `@octokit/core` | 7.0.2 | Core GitHub API client |
| `@octokit/auth-app` | 8.0.1 | GitHub App authentication |
| `@octokit/webhooks` | 14.0.2 | Webhook event handling |
| `@urql/core` | 5.1.1 | GraphQL client for GitHub API |
| `gql.tada` | 1.8.10 | Type-safe GraphQL queries |

**Sources:** [pnpm-workspace.yaml:23-28](), [pnpm-workspace.yaml:55](), [pnpm-workspace.yaml:63]()

### Observability

| Package | Version | Purpose |
|---------|---------|---------|
| `langfuse` | 3.38.4 | LLM observability and tracing |
| `@sentry/nextjs` | 9.30.0 | Error tracking and performance monitoring |
| `@opentelemetry/*` | Various | OpenTelemetry instrumentation |
| `@vercel/otel` | 1.10.0 | Vercel OpenTelemetry integration |
| `pino` | 9.9.0 | Structured logging |

**Sources:** [pnpm-workspace.yaml:69-82](), [apps/studio.giselles.ai/package.json:45-51]()

### Infrastructure

| Package | Version | Purpose |
|---------|---------|---------|
| `@trigger.dev/sdk` | 4.0.5 | Background job processing |
| `@vercel/edge-config` | 1.4.0 | Edge configuration and feature flags |
| `@vercel/functions` | 2.2.11 | Vercel serverless functions utilities |

**Sources:** [pnpm-workspace.yaml:44](), [pnpm-workspace.yaml:56-57]()

## Complete Dependency Graph

The following diagram shows the complete dependency relationships between all workspace packages:

```mermaid
graph TB
    Studio["studio.giselles.ai"]
    Playground["playground"]
    
    WorkflowUI["@giselle-internal/workflow-designer-ui"]
    InternalUI["@giselle-internal/ui"]
    
    Giselle["@giselles-ai/giselle"]
    Protocol["@giselles-ai/protocol"]
    LangModel["@giselles-ai/language-model"]
    
    NodeReg["@giselles-ai/node-registry"]
    ActionReg["@giselles-ai/action-registry"]
    TriggerReg["@giselles-ai/trigger-registry"]
    
    RAG["@giselles-ai/rag"]
    GitHubTool["@giselles-ai/github-tool"]
    WebSearch["@giselles-ai/web-search"]
    DocPreproc["@giselles-ai/document-preprocessor"]
    SupabaseDriver["@giselles-ai/supabase-driver"]
    
    TextEditor["@giselles-ai/text-editor"]
    TextEditorUtils["@giselles-ai/text-editor-utils"]
    Langfuse["@giselles-ai/langfuse"]
    Telemetry["@giselles-ai/telemetry"]
    Utils["@giselles-ai/utils"]
    
    Studio --> WorkflowUI
    Studio --> InternalUI
    Studio --> Giselle
    Studio --> Protocol
    Studio --> NodeReg
    Studio --> GitHubTool
    Studio --> RAG
    Studio --> DocPreproc
    Studio --> Langfuse
    Studio --> LangModel
    Studio --> SupabaseDriver
    Studio --> Utils
    
    Playground --> WorkflowUI
    Playground --> InternalUI
    Playground --> Giselle
    Playground --> Protocol
    Playground --> Langfuse
    Playground --> SupabaseDriver
    
    WorkflowUI --> InternalUI
    WorkflowUI --> Giselle
    WorkflowUI --> Protocol
    WorkflowUI --> NodeReg
    WorkflowUI --> ActionReg
    WorkflowUI --> TriggerReg
    WorkflowUI --> LangModel
    WorkflowUI --> TextEditor
    WorkflowUI --> TextEditorUtils
    
    InternalUI --> Protocol
    InternalUI --> TextEditor
    
    Giselle --> Protocol
    Giselle --> LangModel
    Giselle --> NodeReg
    Giselle --> ActionReg
    Giselle --> TriggerReg
    Giselle --> GitHubTool
    Giselle --> WebSearch
    Giselle --> TextEditorUtils
    
    NodeReg --> Protocol
    NodeReg --> LangModel
    NodeReg --> ActionReg
    NodeReg --> TriggerReg
    NodeReg --> TextEditorUtils
    
    Protocol --> ActionReg
    Protocol --> TriggerReg
    Protocol --> LangModel
    
    ActionReg --> Utils
    
    RAG --> Protocol
    
    GitHubTool --> RAG
    
    Langfuse --> Protocol
    Langfuse --> LangModel
    Langfuse --> RAG
```

**Dependency Flow Rules:**

1. **No Circular Dependencies**: The graph is acyclic (DAG)
2. **Layer Ordering**: Dependencies only flow from higher to lower layers
3. **Protocol Foundation**: Most packages depend on `@giselles-ai/protocol` for shared types
4. **Engine Independence**: The `@giselles-ai/giselle` engine has no dependencies on application or internal packages
5. **Workspace References**: All internal package references use `workspace:*` or `workspace:^` protocol

**Sources:** [pnpm-lock.yaml:242-1162](), [apps/studio.giselles.ai/package.json:25-39](), [apps/playground/package.json:19-30](), [internal-packages/workflow-designer-ui/package.json:15-41](), [packages/giselle/package.json:55-75]()

## Package Version Management

### Workspace Protocol

Internal packages use the `workspace:` protocol to reference other workspace packages:

```json
{
  "dependencies": {
    "@giselles-ai/protocol": "workspace:*",
    "@giselles-ai/giselle": "workspace:^"
  }
}
```

- `workspace:*` - Exact version match, always uses current workspace version
- `workspace:^` - Compatible version range, allows minor/patch updates

### Overrides

The root `package.json` defines global overrides to ensure specific versions:

```json
{
  "pnpm": {
    "overrides": {
      "@electric-sql/client": "1.0.10",
      "@types/react": "19.1.10",
      "@types/react-dom": "19.1.7",
      "cookie": "1.0.2",
      "vite": "7.1.3"
    }
  }
}
```

[package.json:46-53]()

These overrides resolve version conflicts and ensure critical packages use specific versions across the entire dependency tree.

**Sources:** [package.json:46-54](), [pnpm-lock.yaml:235-240]()

---

# Page: Build System and Development Workflow

# Build System and Dependencies

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/playground/package.json](apps/playground/package.json)
- [apps/studio.giselles.ai/package.json](apps/studio.giselles.ai/package.json)
- [docs/packages-license.md](docs/packages-license.md)
- [internal-packages/workflow-designer-ui/package.json](internal-packages/workflow-designer-ui/package.json)
- [package.json](package.json)
- [packages/document-preprocessor/README.md](packages/document-preprocessor/README.md)
- [packages/document-preprocessor/package.json](packages/document-preprocessor/package.json)
- [packages/document-preprocessor/src/global.d.ts](packages/document-preprocessor/src/global.d.ts)
- [packages/document-preprocessor/src/index.ts](packages/document-preprocessor/src/index.ts)
- [packages/document-preprocessor/src/pdf.ts](packages/document-preprocessor/src/pdf.ts)
- [packages/document-preprocessor/src/text.test.ts](packages/document-preprocessor/src/text.test.ts)
- [packages/document-preprocessor/src/text.ts](packages/document-preprocessor/src/text.ts)
- [packages/document-preprocessor/src/types.ts](packages/document-preprocessor/src/types.ts)
- [packages/document-preprocessor/tsconfig.json](packages/document-preprocessor/tsconfig.json)
- [packages/document-preprocessor/tsup.config.ts](packages/document-preprocessor/tsup.config.ts)
- [packages/document-preprocessor/turbo.json](packages/document-preprocessor/turbo.json)
- [packages/document-preprocessor/vitest.config.mts](packages/document-preprocessor/vitest.config.mts)
- [packages/giselle/package.json](packages/giselle/package.json)
- [pnpm-lock.yaml](pnpm-lock.yaml)
- [pnpm-workspace.yaml](pnpm-workspace.yaml)

</details>



## Purpose and Scope

This document describes the build system architecture, dependency management strategy, and package organization in the Giselle AI monorepo. It covers the pnpm workspace configuration, Turbo build orchestration, version catalog management, and key external dependencies. For information about the monorepo's directory structure and organization, see [Project Structure and Organization](#1.1). For development workflows and tooling, see [Development Workflow](#1.3).

## Package Management with pnpm

The project uses **pnpm** as its package manager with workspace support enabled. The workspace configuration defines the monorepo structure and dependency management behavior.

### Workspace Configuration

The workspace is configured in [pnpm-workspace.yaml:1-7]() with four primary workspace patterns:

```yaml
packages:
  - apps/*
  - internal-packages/*
  - packages/*
  - tools/*
minimumReleaseAge: 1440
```

The `minimumReleaseAge: 1440` setting enforces a 24-hour minimum age (in minutes) for package releases before they can be installed, reducing the risk of using untested versions.

### Lockfile Structure

The lockfile [pnpm-lock.yaml:1-6]() uses lockfile version 9.0 with specific settings:

```yaml
lockfileVersion: '9.0'

settings:
  autoInstallPeers: true
  excludeLinksFromLockfile: false
```

The `autoInstallPeers: true` setting automatically installs peer dependencies, while `excludeLinksFromLockfile: false` includes workspace links in the lockfile for deterministic builds.

### Package Manager Version

The project requires **pnpm@10.16.0** as specified in [package.json:36]():

```json
"packageManager": "pnpm@10.16.0"
```

This exact version is enforced through the `packageManager` field, ensuring consistency across development environments.

**Sources:** [pnpm-workspace.yaml:1-7](), [pnpm-lock.yaml:1-6](), [package.json:36]()

## Dependency Catalog System

The project uses pnpm's catalog feature to centralize version management across the monorepo. All shared dependency versions are defined once and referenced throughout the workspace.

### Catalog Definition

The catalog is defined in [pnpm-workspace.yaml:7-102]() and contains 100+ pinned versions. Key categories include:

| Category | Example Dependencies | Purpose |
|----------|---------------------|---------|
| Core Framework | `next: 15.5.2`, `react: 19.1.1` | Next.js and React ecosystem |
| Build Tools | `typescript: 5.7.3`, `tsup: 8.3.5` | TypeScript compilation and bundling |
| AI Integration | `ai: 5.0.44`, `openai: 5.11.0` | LLM provider SDKs |
| Database | `pg: 8.14.1`, `pgvector: 0.2.1` | PostgreSQL and vector extensions |
| Testing | `vitest: 3.2.4`, `playwright: 1.53.0` | Unit and E2E testing frameworks |
| Code Quality | `@biomejs/biome: 2.0.6` | Formatting and linting |
| UI Components | `@xyflow/react: 12.8.3`, `lucide-react: 0.473.0` | Visual workflow and icons |

### Catalog Usage Pattern

Dependencies reference catalog versions using the `catalog:` specifier. For example, in [apps/studio.giselles.ai/package.json:84-92]():

```json
"next": "catalog:",
"react": "catalog:",
"react-dom": "catalog:",
"pg": "catalog:",
"openai": "catalog:"
```

This pattern ensures all workspace packages use the same versions for shared dependencies, preventing version conflicts and duplicate installations.

### Catalog in Lockfile

The lockfile mirrors the catalog structure in [pnpm-lock.yaml:7-248](), creating a single source of truth for resolved versions. When a catalog entry is updated, all packages referencing it are automatically updated during the next install.

**Sources:** [pnpm-workspace.yaml:7-102](), [pnpm-lock.yaml:7-248](), [apps/studio.giselles.ai/package.json:84-92]()

## Turbo Build Orchestration

The project uses **Turbo** (version 2.4.2) for task orchestration, caching, and parallel execution across the monorepo.

### Turbo Configuration

Turbo configuration is defined in `turbo.json` (not shown in provided files) and orchestrates tasks like:

- `build` - Build all packages and applications
- `dev` - Start development servers
- `test` - Run test suites
- `check-types` - TypeScript type checking

### Build Scripts

The root [package.json:5-26]() defines several build-related scripts:

```json
"build": "turbo build",
"build-sdk": "turbo build --filter '@giselle-sdk/*'",
"build-data-type": "turbo build --filter '@giselle-sdk/data-type'",
"check-types": "turbo check-types",
"dev": "turbo dev --filter playground",
"dev:studio.giselles.ai": "NODE_NO_WARNINGS=1 turbo dev --filter studio.giselles.ai"
```

### Task Filtering

Turbo's `--filter` flag enables selective execution:

- `--filter '@giselle-sdk/*'` - Run tasks only for SDK packages matching the glob pattern
- `--filter playground` - Run tasks only for the playground app
- `--filter studio.giselles.ai` - Run tasks only for the production Studio app

This filtering reduces build times during development by avoiding unnecessary rebuilds.

### Turbo Caching

Turbo caches task outputs locally (`.turbo` directory) and optionally remotely. This enables:

1. **Incremental builds** - Skip rebuilding unchanged packages
2. **Parallel execution** - Build independent packages concurrently
3. **Task dependencies** - Automatically build dependencies before dependents

**Sources:** [package.json:5-26]()

## Workspace Dependency Graph

The following diagram shows how workspace packages depend on each other and external dependencies:

```mermaid
graph TB
    subgraph "External Dependencies"
        AI_SDK["ai@5.0.44"]
        Next["next@15.5.2"]
        React["react@19.1.1"]
        OpenAI["openai@5.11.0"]
        Anthropic["@ai-sdk/anthropic@2.0.17"]
        Google["@ai-sdk/google@2.0.14"]
        Supabase["@supabase/supabase-js@2.50.5"]
        PG["pg@8.14.1"]
        Drizzle["drizzle-orm@0.44.2"]
        XYFlow["@xyflow/react@12.8.3"]
    end
    
    subgraph "SDK Packages (packages/)"
        Giselle["@giselle-sdk/giselle"]
        DataType["@giselle-sdk/data-type"]
        LangModel["@giselle-sdk/language-model"]
        RAG["@giselle-sdk/rag"]
        Flow["@giselle-sdk/flow"]
        DocPreproc["@giselle-sdk/document-preprocessor"]
        GitHub["@giselle-sdk/github-tool"]
        Langfuse["@giselle-sdk/langfuse"]
        SupabaseDriver["@giselle-sdk/supabase-driver"]
        VectorAdapters["@giselle-sdk/vector-store-adapters"]
        TextEditor["@giselle-sdk/text-editor"]
        TextEditorUtils["@giselle-sdk/text-editor-utils"]
        WebSearch["@giselle-sdk/web-search"]
    end
    
    subgraph "Internal Packages (internal-packages/)"
        UI["@giselle-internal/ui"]
        WDUI["@giselle-internal/workflow-designer-ui"]
    end
    
    subgraph "Applications (apps/)"
        Studio["studio.giselles.ai"]
        Playground["playground"]
    end
    
    %% SDK Internal Dependencies
    Giselle --> DataType
    Giselle --> LangModel
    Giselle --> Flow
    Giselle --> GitHub
    Giselle --> TextEditorUtils
    Giselle --> WebSearch
    
    DataType --> Flow
    DataType --> LangModel
    
    RAG --> DataType
    
    GitHub --> RAG
    
    Langfuse --> DataType
    Langfuse --> Giselle
    Langfuse --> LangModel
    Langfuse --> RAG
    
    TextEditor --> DataType
    TextEditor --> Giselle
    TextEditor --> TextEditorUtils
    
    %% UI Package Dependencies
    WDUI --> UI
    WDUI --> DataType
    WDUI --> Flow
    WDUI --> Giselle
    WDUI --> LangModel
    WDUI --> TextEditor
    WDUI --> TextEditorUtils
    
    %% Application Dependencies
    Studio --> Giselle
    Studio --> DataType
    Studio --> DocPreproc
    Studio --> GitHub
    Studio --> Langfuse
    Studio --> LangModel
    Studio --> RAG
    Studio --> SupabaseDriver
    Studio --> VectorAdapters
    Studio --> UI
    Studio --> WDUI
    
    Playground --> Giselle
    Playground --> DataType
    Playground --> Langfuse
    Playground --> SupabaseDriver
    Playground --> UI
    Playground --> WDUI
    
    %% External Dependencies
    Giselle --> AI_SDK
    Giselle --> OpenAI
    Giselle --> Anthropic
    Giselle --> Google
    Giselle --> PG
    Giselle --> Next
    
    RAG --> AI_SDK
    RAG --> OpenAI
    RAG --> PG
    
    Studio --> Next
    Studio --> React
    Studio --> Drizzle
    Studio --> Supabase
    
    WDUI --> XYFlow
    WDUI --> Next
    WDUI --> React
    
    Playground --> Next
    Playground --> React
```

**Sources:** [apps/studio.giselles.ai/package.json:21-102](), [apps/playground/package.json:18-35](), [pnpm-lock.yaml:255-1110]()

## Key External Dependencies

The project integrates several critical external dependencies that form the foundation of its functionality.

### AI and LLM Integration

The **Vercel AI SDK** (`ai@5.0.44`) provides the core abstraction layer for LLM interactions. Provider-specific integrations include:

| Package | Version | Purpose |
|---------|---------|---------|
| `@ai-sdk/anthropic` | 2.0.17 | Claude models integration |
| `@ai-sdk/openai` | 2.0.30 | OpenAI models integration |
| `@ai-sdk/google` | 2.0.14 | Google Gemini integration |
| `@ai-sdk/google-vertex` | 3.0.27 | Google Vertex AI integration |
| `@ai-sdk/perplexity` | 2.0.9 | Perplexity API integration |
| `@ai-sdk/fal` | 1.0.13 | Fal.ai image generation |

These are defined in the catalog [pnpm-workspace.yaml:34-41]() and used throughout the SDK packages.

The **OpenAI SDK** (`openai@5.11.0`) is used directly for advanced features like embeddings generation and fine-tuning that require lower-level API access.

### Next.js and React Ecosystem

The application layer uses **Next.js 15.5.2** with **React 19.1.1**, representing cutting-edge versions:

- **Next.js 15.5.2** - Server Components, Server Actions, App Router, Turbopack
- **React 19.1.1** - New hooks, improved performance, concurrent rendering
- **@next/env** - Environment variable loading
- **@next/third-parties** - Third-party script optimization

These versions are specified in [pnpm-workspace.yaml:14-16]() and [pnpm-workspace.yaml:25-26]().

### Database and Storage

Database access is handled through multiple layers:

```mermaid
graph LR
    App["Application Code"]
    Drizzle["drizzle-orm@0.44.2"]
    VercelPG["@vercel/postgres@0.9.0"]
    PG["pg@8.14.1"]
    Pgvector["pgvector@0.2.1"]
    PostgreSQL[("PostgreSQL Database")]
    
    App --> Drizzle
    Drizzle --> VercelPG
    Drizzle --> PG
    App --> PG
    PG --> Pgvector
    Pgvector --> PostgreSQL
    VercelPG --> PostgreSQL
```

- **drizzle-orm@0.44.2** - Type-safe ORM for schema definition and queries
- **@vercel/postgres@0.9.0** - Serverless PostgreSQL connection pooling
- **pg@8.14.1** - Core PostgreSQL client driver
- **pgvector@0.2.1** - Vector similarity search extension

Storage services include:

- **@vercel/blob@0.27.3** - Blob storage for files and images
- **@aws-sdk/client-s3@3.842.0** - S3-compatible object storage
- **unstorage@1.14.4** - Universal storage abstraction layer
- **@supabase/supabase-js@2.50.5** - Supabase client for auth and storage

### UI and Visualization

Workflow visualization uses **@xyflow/react@12.8.3** (formerly ReactFlow), defined in [pnpm-workspace.yaml:32]():

```
"@xyflow/react": 12.8.3
```

UI component libraries include:

- **Radix UI** - Accessible component primitives (dialogs, dropdowns, tooltips)
- **lucide-react@0.473.0** - Icon library
- **motion@12.3.1** - Animation library (Framer Motion)
- **Tiptap 2.11.5** - Rich text editor framework

### Observability and Monitoring

Observability is integrated through multiple systems:

- **langfuse@3.38.4** / **langfuse-vercel@3.37.0** - LLM tracing and analytics
- **@sentry/nextjs@9.30.0** - Error tracking and performance monitoring
- **OpenTelemetry** - Distributed tracing infrastructure:
  - `@opentelemetry/api@1.9.0`
  - `@opentelemetry/sdk-node@0.51.1`
  - `@opentelemetry/sdk-trace-base@1.30.1`
- **@vercel/otel@1.10.0** - Vercel's OpenTelemetry integration

These packages are specified in [apps/studio.giselles.ai/package.json:39-65]().

### Background Processing

Asynchronous task processing uses **@trigger.dev/sdk@4.0.4**, defined in [pnpm-workspace.yaml:102]():

```
"@trigger.dev/sdk": 4.0.4
```

This handles long-running operations like document ingestion, GitHub repository indexing, and resumable generation tasks.

**Sources:** [pnpm-workspace.yaml:14-102](), [apps/studio.giselles.ai/package.json:21-102](), [pnpm-lock.yaml:7-248]()

## Build Scripts and Commands

### Root-Level Scripts

The root [package.json:5-26]() defines workspace-wide commands:

| Script | Command | Purpose |
|--------|---------|---------|
| `build` | `turbo build` | Build all workspace packages |
| `build-sdk` | `turbo build --filter '@giselle-sdk/*'` | Build only SDK packages |
| `build-data-type` | `turbo build --filter '@giselle-sdk/data-type'` | Build data-type package only |
| `check-types` | `turbo check-types` | TypeScript type checking |
| `format` | `biome check --write .` | Format code with Biome |
| `clean` | `turbo clean` | Remove build artifacts |
| `dev` | `turbo dev --filter playground` | Start playground dev server |
| `dev:studio.giselles.ai` | `NODE_NO_WARNINGS=1 turbo dev --filter studio.giselles.ai` | Start Studio dev server |
| `test` | `turbo test` | Run all test suites |
| `tidy` | `knip --no-config-hints` | Find unused dependencies |
| `changeset` | `changeset` | Create changeset for versioning |
| `version` | `changeset version` | Bump versions based on changesets |

### Application-Level Scripts

The Studio application [apps/studio.giselles.ai/package.json:8-18]() defines:

```json
"dev": "next dev --turbopack",
"dev-debug": "LOGLEVEL=debug pnpm run dev",
"build": "next build",
"build:analyze": "ANALYZE=true next build",
"start": "next start",
"test": "vitest run",
"test:e2e": "playwright test",
"check-types": "tsc --noEmit"
```

Notable patterns:

- **--turbopack flag** - Uses Next.js 15's Turbopack bundler for faster development
- **LOGLEVEL=debug** - Enables debug logging for troubleshooting
- **ANALYZE=true** - Generates bundle analysis reports via `@next/bundle-analyzer`

### Utility Scripts

The project includes custom utility scripts in [package.json:21-26]():

```json
"report:colors": "node scripts/report-colors.mjs",
"report:colors:out": "node scripts/report-colors.mjs --out .reports/report-colors.json",
"codemod:text-black-600-20": "node scripts/codemods/replace-text-black-600-20.mjs",
"codemod:text-black-600-20:apply": "node scripts/codemods/replace-text-black-600-20.mjs --apply"
```

The color report script [scripts/report-colors.mjs:1-337]() uses `ripgrep` to analyze color usage across the codebase, generating reports on:

- Tailwind utility classes (`text-*`, `bg-*`, `border-*`, etc.)
- Hex color literals
- CSS functional notations (`rgba()`, `oklch()`, etc.)
- CSS custom properties (`--color-*`, `--brand-*`, etc.)

This enables systematic refactoring of the design system.

**Sources:** [package.json:5-26](), [apps/studio.giselles.ai/package.json:8-18](), [scripts/report-colors.mjs:1-337]()

## Version Constraints and Overrides

### Node.js Version Requirements

The project requires **Node.js 22.x**, enforced in multiple locations:

- Root [package.json:37-39](): `"node": ">=22"`
- Studio [apps/studio.giselles.ai/package.json:4-6](): `"node": "22.x"`
- Playground [apps/playground/package.json:4-6](): `"node": "22.x"`

The root allows `>=22` for flexibility, while applications pin to `22.x` for production consistency.

### Dependency Overrides

The root [package.json:40-46]() defines critical version overrides:

```json
"pnpm": {
  "overrides": {
    "vite": "7.1.3",
    "cookie": "1.0.2",
    "@electric-sql/client": "1.0.10"
  }
}
```

These overrides force specific versions across the entire dependency tree:

- **vite@7.1.3** - Latest Vite version for improved performance and compatibility
- **cookie@1.0.2** - Security patch for cookie parsing vulnerabilities
- **@electric-sql/client@1.0.10** - Stable version of Electric SQL client

Overrides in [pnpm-lock.yaml:250-253]() mirror this configuration:

```yaml
overrides:
  vite: 7.1.3
  cookie: 1.0.2
  '@electric-sql/client': 1.0.10
```

### TypeScript Version

TypeScript is pinned to **5.7.3** throughout the workspace via the catalog [pnpm-workspace.yaml:9]():

```
typescript: 5.7.3
```

This version provides the latest language features while maintaining stability across all packages.

**Sources:** [package.json:37-46](), [apps/studio.giselles.ai/package.json:4-6](), [pnpm-lock.yaml:250-253](), [pnpm-workspace.yaml:9]()

## Dependency Resolution Flow

The following diagram illustrates how dependencies are resolved and installed in the workspace:

```mermaid
graph TB
    Developer["Developer runs<br/>pnpm install"]
    
    subgraph "Workspace Configuration"
        WSConfig["pnpm-workspace.yaml<br/>- Package patterns<br/>- Catalog definitions"]
        RootPkg["package.json (root)<br/>- Overrides<br/>- Node engine"]
        AppPkgs["Application package.json<br/>- catalog: references<br/>- workspace: links"]
    end
    
    subgraph "Resolution Process"
        ReadCatalog["Read catalog entries<br/>from pnpm-workspace.yaml"]
        ResolveRefs["Resolve 'catalog:' specifiers<br/>to pinned versions"]
        ApplyOverrides["Apply pnpm.overrides<br/>from root package.json"]
        ResolveWorkspace["Resolve 'workspace:*' links<br/>to local packages"]
        FetchPackages["Fetch from registry<br/>(registry.npmjs.org)"]
    end
    
    subgraph "Installation"
        Lockfile["Generate/update<br/>pnpm-lock.yaml"]
        LinkLocal["Symlink workspace packages<br/>in node_modules"]
        InstallDeps["Install external deps<br/>to virtual store"]
    end
    
    Result["Installed dependencies<br/>- Local symlinks<br/>- Content-addressed store"]
    
    Developer --> WSConfig
    Developer --> RootPkg
    Developer --> AppPkgs
    
    WSConfig --> ReadCatalog
    AppPkgs --> ResolveRefs
    ReadCatalog --> ResolveRefs
    
    ResolveRefs --> ApplyOverrides
    RootPkg --> ApplyOverrides
    
    ApplyOverrides --> ResolveWorkspace
    AppPkgs --> ResolveWorkspace
    
    ResolveWorkspace --> FetchPackages
    FetchPackages --> Lockfile
    
    Lockfile --> LinkLocal
    Lockfile --> InstallDeps
    
    LinkLocal --> Result
    InstallDeps --> Result
```

**Sources:** [pnpm-workspace.yaml:1-102](), [package.json:40-46](), [pnpm-lock.yaml:1-253]()

## Development Tools

### Code Quality with Biome

**Biome** (version 2.0.6) replaces ESLint and Prettier, providing unified formatting and linting. It's configured via `biome.json` (not shown) and invoked through:

```bash
pnpm format  # Format entire workspace
```

Biome is specified in the catalog [pnpm-workspace.yaml:8]():

```
"@biomejs/biome": 2.0.6
```

### Dependency Analysis with Knip

**Knip** (version 5.61.3) detects unused dependencies, exports, and files. The [package.json:17]() script:

```json
"tidy": "knip --no-config-hints"
```

This runs as part of CI/CD to prevent accumulation of dead code.

### Bundle Analysis

The Studio application includes [apps/studio.giselles.ai/package.json:106]() `@next/bundle-analyzer@15.3.4` for analyzing production bundles:

```bash
pnpm build:analyze  # Generate bundle report
```

This identifies large dependencies and optimization opportunities.

**Sources:** [pnpm-workspace.yaml:8](), [package.json:17,32](), [apps/studio.giselles.ai/package.json:106]()

## Build Output Structure

The following table describes build outputs for different package types:

| Package Type | Build Tool | Output Directory | Entry Points |
|--------------|-----------|------------------|--------------|
| SDK Packages | `tsup` | `dist/` | ESM + CJS bundles |
| Applications | `next build` | `.next/` | Server and client bundles |
| Internal Packages | `tsc` or `tsup` | `dist/` | ESM bundles |
| Tools | `tsc` | `dist/` | ESM bundles |

SDK packages use **tsup@8.3.5** (specified in [pnpm-workspace.yaml:12]()) to generate dual ESM/CJS bundles for maximum compatibility. This is typically configured with:

```typescript
// tsup.config.ts
export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm', 'cjs'],
  dts: true,
  clean: true,
});
```

Applications use Next.js's built-in build system with **Turbopack** in development and optimized production bundles.

**Sources:** [pnpm-workspace.yaml:12](), [apps/studio.giselles.ai/package.json:9,11]()

---

# Page: Core Engine and SDK

# Core Engine and SDK

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/playground/giselle-engine.ts](apps/playground/giselle-engine.ts)
- [apps/studio.giselles.ai/app/giselle-engine.ts](apps/studio.giselles.ai/app/giselle-engine.ts)
- [packages/giselle/src/engine/acts/run-act.ts](packages/giselle/src/engine/acts/run-act.ts)
- [packages/giselle/src/engine/generations/generate-content.ts](packages/giselle/src/engine/generations/generate-content.ts)
- [packages/giselle/src/engine/generations/generate-image.ts](packages/giselle/src/engine/generations/generate-image.ts)
- [packages/giselle/src/engine/generations/internal/use-generation-executor.ts](packages/giselle/src/engine/generations/internal/use-generation-executor.ts)
- [packages/giselle/src/engine/generations/types.ts](packages/giselle/src/engine/generations/types.ts)
- [packages/giselle/src/engine/generations/utils.ts](packages/giselle/src/engine/generations/utils.ts)
- [packages/giselle/src/engine/operations/execute-query.ts](packages/giselle/src/engine/operations/execute-query.ts)
- [packages/giselle/src/engine/telemetry/index.ts](packages/giselle/src/engine/telemetry/index.ts)
- [packages/giselle/src/engine/telemetry/types.ts](packages/giselle/src/engine/telemetry/types.ts)
- [packages/giselle/src/engine/triggers/resolve-trigger.ts](packages/giselle/src/engine/triggers/resolve-trigger.ts)
- [packages/giselle/src/engine/types.ts](packages/giselle/src/engine/types.ts)
- [packages/giselle/src/react/generations/generation-runner.tsx](packages/giselle/src/react/generations/generation-runner.tsx)

</details>



## Purpose and Scope

The Core Engine and SDK form the foundation of the Giselle AI platform, orchestrating AI operations through a unified interface. The `@giselle-sdk/giselle` package provides the core engine (`NextGiselleEngine`) that manages generation lifecycles, provider integrations, storage operations, and tool execution. The broader SDK ecosystem includes specialized packages for language models, RAG operations, document processing, and external integrations.

This document provides an overview of the engine architecture, SDK packages, and integration patterns. For detailed information about specific subsystems, see:
- Generation pipeline implementation: [Generation Pipeline and Lifecycle](#2.2)
- LLM provider abstractions: [Language Models and AI Providers](#2.3)
- Storage backends and data persistence: [Storage Architecture](#2.4)
- Tool preparation and execution: [Tool System and External Integrations](#2.6)

---

## Architecture Overview

The engine architecture separates concerns into distinct layers: configuration, execution, storage, and integration.

```mermaid
graph TB
    subgraph "Application Layer"
        STUDIO["studio.giselles.ai<br/>NextGiselleEngine instance"]
        PLAYGROUND["playground<br/>NextGiselleEngine instance"]
    end
    
    subgraph "Core Engine (giselle package)"
        ENGINE["NextGiselleEngine<br/>Configuration & Orchestration"]
        GEN_EXECUTOR["useGenerationExecutor<br/>Lifecycle Management"]
        
        subgraph "Generation Operations"
            GEN_TEXT["generateText"]
            GEN_CONTENT["generateContent"]
            GEN_IMAGE["generateImage"]
            EXEC_QUERY["executeQuery"]
        end
    end
    
    subgraph "Storage Layer"
        STORAGE["Storage (unstorage)<br/>Key-value operations"]
        EXP_STORAGE["GiselleStorage<br/>Blob operations"]
    end
    
    subgraph "Integration Layer"
        VAULT["Vault<br/>Secret decryption"]
        LLM_PROVIDERS["LLM Providers<br/>OpenAI, Anthropic, Google, Fal"]
        VECTOR_SERVICES["Vector Store Services<br/>GitHub, Document"]
        CALLBACKS["Callbacks<br/>Telemetry & Observability"]
    end
    
    STUDIO --> ENGINE
    PLAYGROUND --> ENGINE
    
    ENGINE --> GEN_EXECUTOR
    GEN_EXECUTOR --> GEN_TEXT
    GEN_EXECUTOR --> GEN_CONTENT
    GEN_EXECUTOR --> GEN_IMAGE
    GEN_EXECUTOR --> EXEC_QUERY
    
    GEN_TEXT --> STORAGE
    GEN_CONTENT --> EXP_STORAGE
    GEN_IMAGE --> STORAGE
    EXEC_QUERY --> STORAGE
    
    ENGINE --> VAULT
    GEN_TEXT --> LLM_PROVIDERS
    GEN_CONTENT --> LLM_PROVIDERS
    GEN_IMAGE --> LLM_PROVIDERS
    EXEC_QUERY --> VECTOR_SERVICES
    
    ENGINE --> CALLBACKS
```

**Sources:** [apps/studio.giselles.ai/app/giselle-engine.ts:218-400](), [apps/playground/giselle-engine.ts:141-160](), [packages/giselle/src/engine/types.ts:87-122]()

---

## NextGiselleEngine Configuration

The `NextGiselleEngine` function initializes the core engine with configuration for storage, integrations, callbacks, and runtime behavior.

### Configuration Interface

| Configuration Field | Type | Purpose |
|---|---|---|
| `basePath` | `string` | API route prefix (e.g., `/api/giselle`) |
| `storage` | `Storage` | Key-value storage (unstorage) |
| `experimental_storage` | `GiselleStorage` | Blob storage (S3-compatible) |
| `llmProviders` | `LanguageModelProvider[]` | Enabled LLM providers |
| `integrationConfigs` | `GiselleIntegrationConfig` | GitHub, etc. integration settings |
| `vault` | `Vault` | Secret encryption/decryption interface |
| `vectorStoreQueryServices` | `Object` | Vector store query implementations |
| `callbacks` | `Object` | Lifecycle event handlers |
| `onConsumeAgentTime` | `Function` | Usage tracking callback |
| `fetchUsageLimitsFn` | `Function` | Usage limit enforcement |
| `telemetry` | `Object` | Observability settings |
| `aiGateway` | `Object` | AI Gateway routing configuration |
| `logger` | `GiselleLogger` | Logging interface |
| `waitUntil` | `Function` | Background task deferral |

**Sources:** [packages/giselle/src/engine/types.ts:189-220]()

### Studio Configuration Example

```mermaid
graph LR
    subgraph "Storage Configuration"
        SUPABASE_STORAGE["Supabase Storage<br/>(production)"]
        FS_STORAGE["Filesystem<br/>(development)"]
    end
    
    subgraph "Engine Configuration"
        ENGINE["NextGiselleEngine"]
        CONFIG["basePath: /api/giselle<br/>llmProviders: [openai, anthropic, google, fal]"]
    end
    
    subgraph "Integration Services"
        GITHUB_CONFIG["GitHub App<br/>appId, privateKey, etc."]
        VAULT["supabaseVaultDriver<br/>Secret encryption"]
        VECTOR_SERVICES["Vector Query Services<br/>github, document"]
    end
    
    subgraph "Callbacks"
        GEN_COMPLETE["generationComplete<br/>→ traceGeneration"]
        GEN_FAILED["generationFailed<br/>→ traceGeneration"]
        EMBED_COMPLETE["embeddingComplete<br/>→ traceEmbedding"]
    end
    
    SUPABASE_STORAGE --> ENGINE
    FS_STORAGE -.-> ENGINE
    CONFIG --> ENGINE
    
    GITHUB_CONFIG --> ENGINE
    VAULT --> ENGINE
    VECTOR_SERVICES --> ENGINE
    
    ENGINE --> GEN_COMPLETE
    ENGINE --> GEN_FAILED
    ENGINE --> EMBED_COMPLETE
```

The Studio configuration instantiates storage drivers based on runtime environment, sets up GitHub App authentication, configures vector store query services, and registers callbacks for telemetry via Langfuse.

**Sources:** [apps/studio.giselles.ai/app/giselle-engine.ts:43-70](), [apps/studio.giselles.ai/app/giselle-engine.ts:218-400]()

### Runtime Environment Detection

The engine adapts behavior based on runtime context:

| Runtime | Condition | Behavior |
|---|---|---|
| `trigger.dev` | `process.env.TRIGGERDOTDEV === "1"` | Background job execution context |
| `vercel` | `process.env.VERCEL === "1"` | Vercel serverless/edge runtime |
| `local` | `process.env.NODE_ENV === "development"` | Local development environment |
| `unknown` | None of the above | Fallback runtime |

Content generation is delegated to Trigger.dev when `generateContentProcessor === "trigger.dev"`, determined by checking `USE_TRIGGER_DEV` environment variable or inferring from runtime environment.

**Sources:** [apps/studio.giselles.ai/app/giselle-engine.ts:202-217]()

---

## SDK Package Ecosystem

The SDK is organized into specialized packages under the `@giselle-sdk` namespace.

### Core SDK Packages

```mermaid
graph TB
    subgraph "Core SDK Packages"
        GISELLE["@giselle-sdk/giselle<br/>Engine, generations, operations"]
        DATA_TYPE["@giselle-sdk/data-type<br/>Type system, schemas"]
        FLOW["@giselle-sdk/flow<br/>Workflow definitions"]
    end
    
    subgraph "AI & ML Packages"
        LANG_MODEL["@giselle-sdk/language-model<br/>Model registry, capabilities"]
        RAG["@giselle-sdk/rag<br/>Vector stores, embeddings"]
        DOC_PREPROC["@giselle-sdk/document-preprocessor<br/>PDF extraction, chunking"]
    end
    
    subgraph "Integration Packages"
        GITHUB_TOOL["@giselle-sdk/github-tool<br/>GitHub tools & auth"]
        WEB_SEARCH["@giselle-sdk/web-search<br/>Web content extraction"]
    end
    
    subgraph "Infrastructure Packages"
        SUPABASE["@giselle-sdk/supabase-driver<br/>DB & storage drivers"]
        LANGFUSE["@giselle-sdk/langfuse<br/>LLM observability"]
    end
    
    GISELLE --> DATA_TYPE
    GISELLE --> LANG_MODEL
    GISELLE --> RAG
    GISELLE --> FLOW
    
    RAG --> DOC_PREPROC
    GISELLE --> GITHUB_TOOL
    GISELLE --> LANGFUSE
    GISELLE --> SUPABASE
```

**Sources:** Based on import patterns in [apps/studio.giselles.ai/app/giselle-engine.ts:1-41](), [packages/giselle/src/engine/generations/generate-text.ts:1-29]()

### Package Responsibilities

| Package | Primary Responsibilities |
|---|---|
| `@giselle-sdk/giselle` | Core engine, generation operations, lifecycle management |
| `@giselle-sdk/data-type` | Zod schemas for nodes, outputs, generations, identifiers |
| `@giselle-sdk/language-model` | Model registry, capability detection, tier-based access |
| `@giselle-sdk/rag` | Vector store interfaces, embedding generation, similarity search |
| `@giselle-sdk/github-tool` | GitHub API tools (issues, files, PRs), authentication |
| `@giselle-sdk/supabase-driver` | Storage drivers for Supabase (S3-compatible, Vault) |
| `@giselle-sdk/langfuse` | Langfuse tracing for generation and embedding operations |

---

## Generation Operations

The engine provides four primary generation operation types, each implemented as a separate function with consistent lifecycle management through `useGenerationExecutor`.

### Operation Function Signatures

```mermaid
graph LR
    subgraph "Generation Functions"
        GEN_TEXT["generateText<br/>(args)"]
        GEN_CONTENT["generateContent<br/>(args)"]
        GEN_IMAGE["generateImage<br/>(args)"]
        EXEC_QUERY["executeQuery<br/>(args)"]
    end
    
    subgraph "Common Arguments"
        CONTEXT["context: GiselleEngineContext"]
        GENERATION["generation: QueuedGeneration | RunningGeneration"]
        FLAGS["useExperimentalStorage: boolean<br/>useResumableGeneration: boolean<br/>useAiGateway: boolean"]
        METADATA["metadata?: GenerationMetadata"]
    end
    
    subgraph "Lifecycle Executor"
        EXECUTOR["useGenerationExecutor<br/>execute callback"]
    end
    
    CONTEXT --> GEN_TEXT
    CONTEXT --> GEN_CONTENT
    CONTEXT --> GEN_IMAGE
    CONTEXT --> EXEC_QUERY
    
    GENERATION --> GEN_TEXT
    GENERATION --> GEN_CONTENT
    GENERATION --> GEN_IMAGE
    GENERATION --> EXEC_QUERY
    
    GEN_TEXT --> EXECUTOR
    GEN_CONTENT --> EXECUTOR
    GEN_IMAGE --> EXECUTOR
    EXEC_QUERY --> EXECUTOR
```

**Sources:** [packages/giselle/src/engine/generations/generate-text.ts:36-42](), [packages/giselle/src/engine/generations/generate-content.ts:62-72](), [packages/giselle/src/engine/generations/generate-image.ts:34-39](), [packages/giselle/src/engine/operations/execute-query.ts:43-47]()

### Operation Implementations

| Operation | File | LLM Integration | Output Types |
|---|---|---|---|
| `generateText` | `generate-text.ts` | Vercel AI SDK `streamText` | `generated-text`, `reasoning`, `source` |
| `generateContent` | `generate-content.ts` | Vercel AI SDK `streamText` + smoothStream | `generated-text`, `reasoning`, `source` |
| `generateImage` | `generate-image.ts` | Vercel AI SDK `experimental_generateImage` | `generated-image` |
| `executeQuery` | `execute-query.ts` | Vector store query services | `query-result` |

The primary difference between `generateText` and `generateContent` is that `generateContent` includes:
1. UI message chunk streaming to storage for resumability
2. Smooth streaming transformation (`smoothStream`)
3. Abort signal support for cancellation
4. Always uses experimental storage

**Sources:** [packages/giselle/src/engine/generations/generate-text.ts:227-245](), [packages/giselle/src/engine/generations/generate-content.ts:258-292](), [packages/giselle/src/engine/generations/generate-image.ts:169-175](), [packages/giselle/src/engine/operations/execute-query.ts:80-90]()

---

## useGenerationExecutor Lifecycle

The `useGenerationExecutor` function provides consistent lifecycle management across all generation operations.

```mermaid
sequenceDiagram
    participant Op as "Operation Function"
    participant Exec as "useGenerationExecutor"
    participant UsageCheck as "checkUsageLimits"
    participant Execute as "execute callback"
    participant Finish as "finishGeneration"
    participant Callbacks as "Engine Callbacks"
    
    Op->>Exec: Call with generation & execute fn
    Exec->>Exec: Parse GenerationContext
    Exec->>Exec: Convert QueuedGeneration → RunningGeneration
    Exec->>Exec: Persist RunningGeneration
    
    Exec->>UsageCheck: Check workspace usage limits
    alt Usage limit exceeded
        UsageCheck-->>Exec: Error
        Exec->>Exec: Set generation status = "failed"
        Exec-->>Op: Throw UsageLimitError
    end
    
    Exec->>Execute: Call with utilities
    Note over Execute: fileResolver<br/>generationContentResolver<br/>imageGenerationResolver<br/>finishGeneration
    
    Execute->>Execute: Build messages & execute operation
    Execute->>Finish: Call with outputs & usage
    
    Finish->>Finish: Create CompletedGeneration
    Finish->>Finish: Process output images
    Finish->>Finish: Persist generation
    Finish->>Callbacks: handleAgentTimeConsumption
    Finish->>Callbacks: generationComplete callback
    
    Finish-->>Execute: Return completedGeneration
    Execute-->>Exec: Return result
    Exec-->>Op: Return result
```

**Sources:** [packages/giselle/src/engine/generations/internal/use-generation-executor.ts:59-411]()

### Resolver Functions

The executor provides three resolver functions to the operation's `execute` callback:

| Resolver | Purpose | Implementation |
|---|---|---|
| `fileResolver` | Retrieve file content by `FileId` | Reads from storage at `filePath()` |
| `generationContentResolver` | Resolve node output to text | Finds generation by node/act, formats output |
| `imageGenerationResolver` | Resolve node output to images | Finds generation, loads image blobs as `ImagePart[]` |

These resolvers enable operations to build message objects with content from upstream nodes in the workflow graph.

**Sources:** [packages/giselle/src/engine/generations/internal/use-generation-executor.ts:146-324]()

### finishGeneration Function

The `finishGeneration` callback provided to operations handles completion logic:

1. Sanitize usage metrics with `sanitizeGenerationUsage`
2. Create `CompletedGeneration` with outputs and usage
3. Process output file blobs (images) from storage
4. Persist completed generation
5. Call `handleAgentTimeConsumption` for usage tracking
6. Invoke `callbacks.generationComplete` for telemetry

**Sources:** [packages/giselle/src/engine/generations/internal/use-generation-executor.ts:326-398]()

---

## Integration Points

The engine integrates with external services through well-defined interfaces.

### LLM Provider Integration

The engine uses the Vercel AI SDK to abstract provider differences:

```mermaid
graph TB
    subgraph "Engine Layer"
        GEN_TEXT["generateText"]
        GEN_CONTENT["generateContent"]
    end
    
    subgraph "AI SDK Layer"
        STREAM_TEXT["streamText"]
        AI_GATEWAY["createGateway"]
        PROVIDER_SDKS["@ai-sdk/anthropic<br/>@ai-sdk/openai<br/>@ai-sdk/google-vertex<br/>@ai-sdk/perplexity<br/>@ai-sdk/fal"]
    end
    
    subgraph "Provider Endpoints"
        ANTHROPIC["Anthropic API"]
        OPENAI["OpenAI API"]
        GOOGLE["Google Vertex AI"]
        PERPLEXITY["Perplexity API"]
        FAL["Fal AI"]
    end
    
    GEN_TEXT --> STREAM_TEXT
    GEN_CONTENT --> STREAM_TEXT
    
    STREAM_TEXT --> AI_GATEWAY
    AI_GATEWAY --> PROVIDER_SDKS
    
    PROVIDER_SDKS --> ANTHROPIC
    PROVIDER_SDKS --> OPENAI
    PROVIDER_SDKS --> GOOGLE
    PROVIDER_SDKS --> PERPLEXITY
    PROVIDER_SDKS --> FAL
```

When `useAiGateway` is enabled, the engine uses the AI Gateway pattern with custom headers for request identification:

```
headers: {
  "http-referer": "https://studio.giselles.ai",
  "x-title": "Giselle"
}
```

Provider models are constructed as `gateway(${provider}/${modelId})` (e.g., `gateway("openai/gpt-4o")`).

**Sources:** [packages/giselle/src/engine/generations/generate-text.ts:360-412](), [apps/studio.giselles.ai/app/giselle-engine.ts:391-398]()

### Vector Store Integration

Vector stores are accessed through the `QueryService` interface:

```typescript
// From engine configuration
vectorStoreQueryServices: {
  github?: GitHubVectorStoreQueryService<Record<string, unknown>>;
  githubPullRequest?: GitHubVectorStoreQueryService<Record<string, unknown>>;
  document?: DocumentVectorStoreQueryService<Record<string, unknown>>;
}
```

The `executeQuery` operation uses these services to perform similarity search with embedding generation and result ranking.

**Sources:** [packages/giselle/src/engine/types.ts:103-107](), [packages/giselle/src/engine/operations/execute-query.ts:299-502]()

### Tool Integration

Tools are prepared dynamically based on node configuration:

| Tool Category | Configuration Source | Preparation |
|---|---|---|
| GitHub Tools | `operationNode.content.tools?.github` | Decrypt PAT/secret, prepare `githubTools()` |
| Postgres Tools | `operationNode.content.tools?.postgres` | Decrypt connection string, create `createPostgresTools()` |
| OpenAI Web Search | `operationNode.content.tools?.openaiWebSearch` | Prepare `openai.tools.webSearchPreview()` |
| Anthropic Web Search | `operationNode.content.tools?.anthropicWebSearch` | Prepare `anthropic.tools.webSearch_20250305()` |
| Google Search Grounding | `operationNode.content.llm.configurations.searchGrounding` | Prepare `vertex.tools.googleSearch()` |
| Google URL Context | `operationNode.content.llm.configurations.urlContext` | Prepare `vertex.tools.urlContext()` |

Tools are injected into the `streamText` call and cleaned up after generation via `cleanupFunctions`.

**Sources:** [packages/giselle/src/engine/generations/generate-text.ts:77-211](), [packages/giselle/src/engine/generations/generate-content.ts:112-245]()

---

## Process Delegation

The engine supports delegating operations to external job processors via `setGenerateContentProcess` and `setRunActProcess`.

### Generate Content Process Delegation

```mermaid
graph TD
    ENGINE["NextGiselleEngine"]
    
    subgraph "Process Configuration"
        SELF["type: 'self'<br/>Execute in-process"]
        EXTERNAL["type: 'external'<br/>Delegate to Trigger.dev"]
    end
    
    subgraph "Delegation Flow"
        CHECK_ENV["Check runtimeEnv"]
        ORIGIN["Check generation.context.origin.type"]
        
        GITHUB_APP["origin: github-app<br/>→ getWorkspaceTeam"]
        STAGE_STUDIO["origin: stage/studio<br/>→ Check runtimeEnv"]
        
        LOCAL_VERCEL["runtimeEnv: local/vercel<br/>→ fetchCurrentUser/fetchCurrentTeam"]
        TRIGGER_CTX["runtimeEnv: trigger.dev<br/>→ Parse metadata"]
        
        TRIGGER_JOB["jobs.trigger<br/>('generate-content')"]
    end
    
    ENGINE --> CHECK_ENV
    CHECK_ENV --> ORIGIN
    
    ORIGIN --> GITHUB_APP
    ORIGIN --> STAGE_STUDIO
    
    STAGE_STUDIO --> LOCAL_VERCEL
    STAGE_STUDIO --> TRIGGER_CTX
    
    GITHUB_APP --> TRIGGER_JOB
    LOCAL_VERCEL --> TRIGGER_JOB
    TRIGGER_CTX --> TRIGGER_JOB
```

The delegation logic branches based on:
1. **Generation origin type** (`github-app` vs. `stage`/`studio`)
2. **Runtime environment** (`local`/`vercel` vs. `trigger.dev`)

When delegating to Trigger.dev, the engine packages metadata including `userId`, `team`, and `requestId` for telemetry correlation.

**Sources:** [apps/studio.giselles.ai/app/giselle-engine.ts:402-493]()

### Run Act Process Delegation

Similar delegation occurs for Act execution via `setRunActProcess`:

```typescript
giselleEngine.setRunActProcess(async ({ act, generationOriginType }) => {
  // Branch by generationOriginType
  // Fetch user context
  // Trigger run-act-job
});
```

**Sources:** [apps/studio.giselles.ai/app/giselle-engine.ts:495-537]()

---

## Callbacks and Telemetry

The engine invokes callbacks at key lifecycle events for observability and usage tracking.

### Callback Types

```mermaid
graph TB
    subgraph "Generation Callbacks"
        GEN_COMPLETE["generationComplete<br/>Args: generation, inputMessages, outputFileBlobs, providerMetadata"]
        GEN_FAILED["generationFailed<br/>Args: generation, inputMessages"]
    end
    
    subgraph "Embedding Callbacks"
        EMBED_COMPLETE["embeddingComplete<br/>Args: embeddingMetrics, generation, queryContext"]
    end
    
    subgraph "Telemetry Implementations"
        TRACE_GEN["traceGeneration<br/>(Langfuse)"]
        TRACE_EMBED["traceEmbedding<br/>(Langfuse)"]
    end
    
    subgraph "Usage Tracking"
        CONSUME_TIME["onConsumeAgentTime<br/>Args: workspaceId, startedAt, endedAt, totalDurationMs"]
    end
    
    GEN_COMPLETE --> TRACE_GEN
    GEN_FAILED --> TRACE_GEN
    EMBED_COMPLETE --> TRACE_EMBED
    
    CONSUME_TIME -.-> "Database Insert"
```

**Sources:** [packages/giselle/src/engine/types.ts:57-85](), [apps/studio.giselles.ai/app/giselle-engine.ts:256-389]()

### Telemetry Context

Callbacks receive metadata for correlation:

| Field | Source | Purpose |
|---|---|---|
| `requestId` | `getRequestId()` or parsed from metadata | Trace request across services |
| `userId` | `fetchCurrentUser()` or `"github-app"` | Identify user for analytics |
| `team` | `fetchCurrentTeam()` or `getWorkspaceTeam()` | Team-level metrics |
| `sessionId` | `generation.context.origin.actId` | Group generations by Act |
| `tags` | `["plan:pro", "teamType:personal"]` | Filter traces by plan/team type |

When executing in Trigger.dev context, metadata is parsed from `GenerationMetadata` to avoid circular authentication calls.

**Sources:** [apps/studio.giselles.ai/app/giselle-engine.ts:107-200](), [apps/studio.giselles.ai/app/giselle-engine.ts:256-298]()

---

## Storage Interface Abstraction

The engine uses two storage interfaces to separate concerns:

```mermaid
graph TB
    subgraph "Storage Interfaces"
        UNSTORAGE["Storage (unstorage)<br/>Key-value operations<br/>Generations, indexes, secrets"]
        GISELLE_STORAGE["GiselleStorage<br/>Blob operations<br/>Images, UI chunks, files"]
    end
    
    subgraph "Backend Implementations"
        subgraph "Production"
            SUPABASE_KV["supabaseStorageDriver<br/>→ Supabase Storage"]
            SUPABASE_BLOB["experimental_supabaseStorageDriver<br/>→ S3-compatible API"]
        end
        
        subgraph "Development"
            FS_DRIVER["fsDriver<br/>→ ./.storage"]
            FS_STORAGE["fsStorageDriver<br/>→ ./.storage"]
        end
    end
    
    UNSTORAGE --> SUPABASE_KV
    UNSTORAGE --> FS_DRIVER
    
    GISELLE_STORAGE --> SUPABASE_BLOB
    GISELLE_STORAGE --> FS_STORAGE
```

The `useExperimentalStorage` flag controls which interface is used for generation and file operations. The migration to `GiselleStorage` enables direct S3-compatible operations for improved performance.

**Sources:** [apps/studio.giselles.ai/app/giselle-engine.ts:43-70](), [apps/playground/giselle-engine.ts:17-39]()

---

# Page: Engine Architecture and Configuration

# Engine Architecture and Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/playground/giselle-engine.ts](apps/playground/giselle-engine.ts)
- [apps/studio.giselles.ai/app/giselle-engine.ts](apps/studio.giselles.ai/app/giselle-engine.ts)
- [packages/giselle/src/engine/acts/run-act.ts](packages/giselle/src/engine/acts/run-act.ts)
- [packages/giselle/src/engine/generations/generate-content.ts](packages/giselle/src/engine/generations/generate-content.ts)
- [packages/giselle/src/engine/generations/generate-image.ts](packages/giselle/src/engine/generations/generate-image.ts)
- [packages/giselle/src/engine/generations/internal/use-generation-executor.ts](packages/giselle/src/engine/generations/internal/use-generation-executor.ts)
- [packages/giselle/src/engine/generations/types.ts](packages/giselle/src/engine/generations/types.ts)
- [packages/giselle/src/engine/generations/utils.ts](packages/giselle/src/engine/generations/utils.ts)
- [packages/giselle/src/engine/operations/execute-query.ts](packages/giselle/src/engine/operations/execute-query.ts)
- [packages/giselle/src/engine/telemetry/index.ts](packages/giselle/src/engine/telemetry/index.ts)
- [packages/giselle/src/engine/telemetry/types.ts](packages/giselle/src/engine/telemetry/types.ts)
- [packages/giselle/src/engine/triggers/resolve-trigger.ts](packages/giselle/src/engine/triggers/resolve-trigger.ts)
- [packages/giselle/src/engine/types.ts](packages/giselle/src/engine/types.ts)
- [packages/giselle/src/react/generations/generation-runner.tsx](packages/giselle/src/react/generations/generation-runner.tsx)

</details>



This page documents the architecture and configuration of the Giselle Engine, specifically focusing on the `NextGiselleEngine` initialization, runtime environment detection, and how the engine is configured across different deployment environments (Studio, Playground, local, Vercel, Trigger.dev).

For information about the generation execution pipeline and lifecycle, see [Generation Pipeline and Lifecycle](#2.2). For details about Act orchestration, see [Act Runner and Workflow Orchestration](#2.4).

## Overview

The Giselle Engine is initialized through the `NextGiselleEngine` factory function, which creates a `GiselleEngineContext` containing all runtime dependencies, configuration, and callback hooks. The engine supports flexible deployment through runtime environment detection and process delegation, allowing the same codebase to execute in multiple contexts: local development, Vercel serverless functions, and Trigger.dev background jobs.

## Engine Initialization

### NextGiselleEngine Factory

The engine is instantiated by calling `NextGiselleEngine()` with a `GiselleEngineConfig` object. This factory creates the internal `GiselleEngineContext` and returns an engine instance with methods for generation execution, workflow management, and storage operations.

```mermaid
graph TB
    subgraph "Application Layer"
        StudioApp["studio.giselles.ai/app/giselle-engine.ts"]
        PlaygroundApp["playground/giselle-engine.ts"]
    end
    
    subgraph "Engine Factory"
        Factory["NextGiselleEngine(config)"]
        Context["GiselleEngineContext"]
    end
    
    subgraph "Configuration Inputs"
        Storage["storage: GiselleStorage"]
        Vault["vault: Vault"]
        Providers["llmProviders: LanguageModelProvider[]"]
        Integrations["integrationConfigs: GiselleIntegrationConfig"]
        Callbacks["callbacks: Lifecycle hooks"]
        VectorStores["vectorStoreQueryServices"]
        Telemetry["telemetry: TelemetrySettings"]
        Gateway["aiGateway: {httpReferer, xTitle}"]
    end
    
    subgraph "Runtime Detection"
        RuntimeEnv["getRuntimeEnv()"]
        ProcessorChoice["generateContentProcessor selection"]
    end
    
    StudioApp -->|provides config| Factory
    PlaygroundApp -->|provides config| Factory
    
    Storage --> Factory
    Vault --> Factory
    Providers --> Factory
    Integrations --> Factory
    Callbacks --> Factory
    VectorStores --> Factory
    Telemetry --> Factory
    Gateway --> Factory
    
    Factory -->|creates| Context
    
    RuntimeEnv -->|determines| ProcessorChoice
    ProcessorChoice -->|configures| Context
    
    Context -->|used by| GenerateContent["generateContent()"]
    Context -->|used by| RunAct["runAct()"]
    Context -->|used by| ExecuteQuery["executeQuery()"]
```

**Sources:**
- [apps/studio.giselles.ai/app/giselle-engine.ts:196-396]()
- [apps/playground/giselle-engine.ts:122-140]()
- [packages/giselle/src/engine/types.ts:194-227]()

### GiselleEngineContext Structure

The `GiselleEngineContext` is the central dependency container passed to all engine operations. It contains configured instances of storage, vault, providers, and callbacks.

| Property | Type | Purpose |
|----------|------|---------|
| `storage` | `GiselleStorage` | Abstraction for file/blob storage (Supabase S3 or filesystem) |
| `vault` | `Vault` | Secure credential storage (Supabase pgsodium or in-memory) |
| `llmProviders` | `LanguageModelProvider[]` | Enabled AI providers (openai, anthropic, google) |
| `integrationConfigs` | `GiselleIntegrationConfig` | GitHub App credentials and configuration |
| `vectorStoreQueryServices` | Object | RAG query services for GitHub and document vector stores |
| `callbacks` | Object | Lifecycle hooks (generationComplete, generationFailed, etc.) |
| `aiGateway` | Object | AI Gateway headers for request routing |
| `telemetry` | Object | Observability settings (isEnabled, waitForFlushFn) |
| `logger` | `GiselleLogger` | Structured logging instance |
| `waitUntil` | `WaitUntil` | Async task scheduling for serverless environments |
| `generateContentProcess` | `GenerateContentProcess` | Self or external (Trigger.dev) execution |
| `runActProcess` | `RunActProcess` | Self or external (Trigger.dev) execution |

**Sources:**
- [packages/giselle/src/engine/types.ts:90-127]()

## Runtime Environment Detection

### getRuntimeEnv Function

The engine detects its runtime environment to adapt behavior for different deployment contexts:

```mermaid
graph TD
    Start["getRuntimeEnv()"]
    
    CheckTrigger{"process.env.TRIGGERDOTDEV === '1'"}
    CheckVercel{"process.env.VERCEL === '1'"}
    CheckDev{"process.env.NODE_ENV === 'development'"}
    
    ReturnTrigger["return 'trigger.dev'"]
    ReturnVercel["return 'vercel'"]
    ReturnLocal["return 'local'"]
    ReturnUnknown["return 'unknown'"]
    
    Start --> CheckTrigger
    CheckTrigger -->|Yes| ReturnTrigger
    CheckTrigger -->|No| CheckVercel
    CheckVercel -->|Yes| ReturnVercel
    CheckVercel -->|No| CheckDev
    CheckDev -->|Yes| ReturnLocal
    CheckDev -->|No| ReturnUnknown
```

The detected environment influences:
1. **Processor selection** - Whether to use Trigger.dev for async processing
2. **Telemetry context** - How to retrieve user/team information for tracing
3. **Callback behavior** - Different authentication flows based on context

**Sources:**
- [apps/studio.giselles.ai/app/giselle-engine.ts:180-187]()

### Processor Selection Logic

```mermaid
graph TB
    Start["Select generateContentProcessor"]
    
    EnvCheck{"USE_TRIGGER_DEV === '1' OR<br/>runtimeEnv === 'trigger.dev' OR<br/>(runtimeEnv === 'vercel' AND NODE_ENV !== 'development')"}
    
    UseTrigger["generateContentProcessor = 'trigger.dev'<br/>(delegate to jobs.trigger)"]
    UseSelf["generateContentProcessor = 'self'<br/>(execute in-process)"]
    
    SetProcess["giselleEngine.setGenerateContentProcess()"]
    SetActProcess["giselleEngine.setRunActProcess()"]
    
    Start --> EnvCheck
    EnvCheck -->|Yes| UseTrigger
    EnvCheck -->|No| UseSelf
    
    UseTrigger --> SetProcess
    UseTrigger --> SetActProcess
    
    UseSelf --> Skip["No setters called,<br/>uses default in-process execution"]
```

In Studio production (Vercel), content generation and Act execution are delegated to Trigger.dev jobs to avoid serverless timeout limits. In Playground and local development, execution happens in-process.

**Sources:**
- [apps/studio.giselles.ai/app/giselle-engine.ts:189-194]()
- [apps/studio.giselles.ai/app/giselle-engine.ts:426-534]()

## Configuration Components

### Storage Driver Configuration

The engine supports two storage drivers:

**Studio (Production):**
```typescript
const storage = experimental_supabaseStorageDriver({
  endpoint: process.env.SUPABASE_STORAGE_URL,
  region: process.env.SUPABASE_STORAGE_REGION,
  accessKeyId: process.env.SUPABASE_STORAGE_ACCESS_KEY_ID,
  secretAccessKey: process.env.SUPABASE_STORAGE_SECRET_ACCESS_KEY,
  bucket: "app",
});
```

**Playground:**
```typescript
const storage = isVercelEnvironment
  ? experimental_supabaseStorageDriver({ /* ... */ })
  : fsStorageDriver({ root: "./.storage" });
```

The storage abstraction is used for:
- Generation state persistence
- Generated images and file artifacts
- Node generation indexes
- Act execution state

**Sources:**
- [apps/studio.giselles.ai/app/giselle-engine.ts:40-46]()
- [apps/playground/giselle-engine.ts:14-24]()

### Vault Driver Configuration

The vault securely stores encrypted credentials:

**Studio:**
```typescript
const vault = supabaseVaultDriver({
  url: process.env.SUPABASE_URL,
  serviceKey: process.env.SUPABASE_SERVICE_KEY,
});
```

**Playground:**
```typescript
const vault = nodeVaultDriver({
  secret: process.env.VAULT_SECRET,
});
```

The vault is queried when:
- Resolving GitHub PAT tokens for tool execution
- Decrypting PostgreSQL connection strings for database tools
- Accessing stored secrets referenced by `secretId`

**Sources:**
- [apps/studio.giselles.ai/app/giselle-engine.ts:48-51]()
- [apps/playground/giselle-engine.ts:137-139]()
- [packages/giselle/src/engine/generations/generate-content.ts:118-134]()

### LLM Provider Configuration

Providers are conditionally enabled based on environment variables:

```mermaid
graph LR
    subgraph "Studio Configuration"
        StudioProviders["llmProviders: ['openai', 'anthropic', 'google']<br/>(hardcoded)"]
    end
    
    subgraph "Playground Configuration"
        CheckOpenAI{"OPENAI_API_KEY<br/>present?"}
        CheckAnthropic{"ANTHROPIC_API_KEY<br/>present?"}
        CheckGoogle{"GOOGLE_GENERATIVE_AI_API_KEY<br/>present?"}
        
        AddOpenAI["Add 'openai'"]
        AddAnthropic["Add 'anthropic'"]
        AddGoogle["Add 'google'"]
        
        PlaygroundProviders["llmProviders: LanguageModelProvider[]"]
        
        CheckOpenAI -->|Yes| AddOpenAI
        CheckAnthropic -->|Yes| AddAnthropic
        CheckGoogle -->|Yes| AddGoogle
        
        AddOpenAI --> PlaygroundProviders
        AddAnthropic --> PlaygroundProviders
        AddGoogle --> PlaygroundProviders
    end
```

Studio always includes all three providers. Playground conditionally includes providers based on available API keys.

**Sources:**
- [apps/studio.giselles.ai/app/giselle-engine.ts:199]()
- [apps/playground/giselle-engine.ts:26-39]()

### AI Gateway Configuration

Studio configures AI Gateway headers for request routing through a gateway proxy:

```typescript
aiGateway: {
  httpReferer: process.env.VERCEL_ENV === "preview"
    ? `https://${process.env.VERCEL_URL}`
    : "https://studio.giselles.ai",
  xTitle: process.env.VERCEL_ENV === "preview" ? "Giselle(preview)" : "Giselle",
}
```

These headers are passed to the Vercel AI SDK's `createGateway()` to identify requests and apply usage limits or routing rules.

**Sources:**
- [apps/studio.giselles.ai/app/giselle-engine.ts:387-394]()
- [packages/giselle/src/engine/generations/generate-content.ts:489-503]()

### Integration Configuration

GitHub App credentials are configured for trigger/action integration:

```typescript
integrationConfigs: {
  github: {
    auth: { /* legacy auth */ },
    authV2: {
      appId: process.env.GITHUB_APP_ID,
      privateKey: process.env.GITHUB_APP_PRIVATE_KEY,
      clientId: process.env.GITHUB_APP_CLIENT_ID,
      clientSecret: process.env.GITHUB_APP_CLIENT_SECRET,
      webhookSecret: process.env.GITHUB_APP_WEBHOOK_SECRET,
    },
  },
}
```

The `authV2` configuration is used by the GitHub trigger resolver and action executor.

**Sources:**
- [apps/studio.giselles.ai/app/giselle-engine.ts:70-84]()
- [apps/studio.giselles.ai/app/giselle-engine.ts:207-226]()
- [packages/giselle/src/engine/types.ts:133-146]()

## Callback System

### Lifecycle Callbacks

The engine provides hooks for observing generation lifecycle events:

```mermaid
graph TB
    subgraph "Callback Hooks"
        AppCreate["appCreate(app)"]
        AppDelete["appDelete(appId)"]
        GenComplete["generationComplete(generation, inputMessages, outputFileBlobs)"]
        GenFailed["generationFailed(generation, inputMessages)"]
        EmbedComplete["embeddingComplete(embeddingMetrics, generation, queryContext)"]
    end
    
    subgraph "Studio Implementation"
        TraceGen["traceGenerationForTeam()<br/>→ Langfuse"]
        TraceEmbed["traceEmbeddingForTeam()<br/>→ Langfuse"]
        DBInsert["db.insert(apps)"]
        DBDelete["db.delete(apps)"]
    end
    
    AppCreate -->|creates DB record| DBInsert
    AppDelete -->|removes DB record| DBDelete
    GenComplete -->|traces LLM usage| TraceGen
    GenFailed -->|traces errors| TraceGen
    EmbedComplete -->|traces embedding calls| TraceEmbed
```

**Callback Execution Context:**

The callbacks execute with different authentication contexts based on `generation.context.origin.type`:

| Origin Type | User Context | Team Context | Request ID |
|-------------|--------------|--------------|------------|
| `"github-app"` | `"github-app"` | Fetched via `getWorkspaceTeam()` | From `getRequestId()` |
| `"studio"` or `"stage"` (Vercel) | `fetchCurrentUser()` | `fetchCurrentTeam()` | From `getRequestId()` |
| `"studio"` or `"stage"` (Trigger.dev) | From `metadata.userId` | From `metadata.team` | From `metadata.requestId` |

This branching logic ensures callbacks can identify the user/team even when running in background jobs where session context is unavailable.

**Sources:**
- [apps/studio.giselles.ai/app/giselle-engine.ts:234-385]()
- [apps/studio.giselles.ai/app/giselle-engine.ts:88-178]()
- [packages/giselle/src/engine/types.ts:111-118]()

### Telemetry Configuration

Telemetry settings control observability integration:

```typescript
telemetry: {
  isEnabled: true,
  waitForFlushFn: waitForLangfuseFlush,
}
```

The `waitForFlushFn` ensures telemetry data is flushed before serverless functions terminate. Studio uses Langfuse for LLM tracing; Playground uses a minimal implementation.

**Sources:**
- [apps/studio.giselles.ai/app/giselle-engine.ts:201-204]()
- [packages/giselle/src/engine/types.ts:99-103]()

## Process Delegation

### Content Generation Process

When Trigger.dev is enabled, the engine delegates content generation to a background job:

```mermaid
sequenceDiagram
    participant Engine as "GiselleEngine"
    participant Setter as "setGenerateContentProcess()"
    participant Handler as "Process Handler"
    participant Trigger as "jobs.trigger()"
    participant Job as "generate-content-job"
    participant Generate as "generateContent()"
    
    Engine->>Setter: Configure external process
    Note over Engine: generateContentProcess = "external"
    
    Engine->>Handler: generation created
    Handler->>Handler: Determine origin type<br/>(github-app/stage/studio)
    
    alt GitHub App Origin
        Handler->>Handler: Fetch team via getWorkspaceTeam()
        Handler->>Trigger: Trigger job with userId="github-app"
    else Studio/Stage Origin + Vercel Runtime
        Handler->>Handler: fetchCurrentUser() + fetchCurrentTeam()
        Handler->>Trigger: Trigger job with userId, team
    else Studio/Stage Origin + Trigger.dev Runtime
        Handler->>Handler: Parse metadata (user/team from metadata)
        Handler->>Trigger: Trigger job with parsed metadata
    end
    
    Trigger->>Job: Execute in background
    Job->>Generate: generateContent(context, generation, metadata)
```

This delegation prevents serverless timeout issues by moving long-running AI generation to a durable background job.

**Sources:**
- [apps/studio.giselles.ai/app/giselle-engine.ts:426-489]()
- [packages/giselle/src/engine/types.ts:33-40]()

### Act Execution Process

Similarly, Act execution can be delegated:

```typescript
giselleEngine.setRunActProcess(async ({ act, generationOriginType }) => {
  const requestId = getRequestId();
  switch (generationOriginType) {
    case "github-app": {
      const team = await getWorkspaceTeam(act.workspaceId);
      await jobs.trigger<typeof runActJob>("run-act-job", {
        actId: act.id,
        requestId,
        userId: "github-app",
        team: { id: team.id, subscriptionId: team.activeSubscriptionId, plan: team.plan },
      });
      break;
    }
    case "stage":
    case "studio": {
      const [currentUser, currentTeam] = await Promise.all([
        fetchCurrentUser(),
        fetchCurrentTeam(),
      ]);
      await jobs.trigger<typeof runActJob>("run-act-job", { /* ... */ });
      break;
    }
  }
});
```

**Sources:**
- [apps/studio.giselles.ai/app/giselle-engine.ts:491-533]()
- [packages/giselle/src/engine/types.ts:42-54]()

## Vector Store Query Services

The engine connects to vector store query services for RAG functionality:

```mermaid
graph TB
    subgraph "Engine Context"
        VectorServices["vectorStoreQueryServices"]
    end
    
    subgraph "Service Implementations"
        GitHubService["gitHubQueryService<br/>(GitHub blob embeddings)"]
        IssueService["gitHubIssueQueryService<br/>(GitHub issue embeddings)"]
        PRService["gitHubPullRequestQueryService<br/>(GitHub PR embeddings)"]
        DocService["getDocumentVectorStoreQueryService()<br/>(Document embeddings)"]
    end
    
    subgraph "Query Execution"
        ExecuteQuery["executeQuery(generation)"]
        QueryNode["Query Node in workflow"]
        VectorStoreNode["VectorStore Node"]
    end
    
    VectorServices --> GitHubService
    VectorServices --> IssueService
    VectorServices --> PRService
    VectorServices --> DocService
    
    QueryNode --> ExecuteQuery
    VectorStoreNode --> ExecuteQuery
    ExecuteQuery --> VectorServices
```

These services are injected at engine initialization and used by `executeQuery()` to perform semantic search against configured vector stores.

**Sources:**
- [apps/studio.giselles.ai/app/giselle-engine.ts:228-233]()
- [packages/giselle/src/engine/operations/execute-query.ts:290-541]()
- [packages/giselle/src/engine/types.ts:105-110]()

## Configuration Differences: Studio vs Playground

| Aspect | Studio | Playground |
|--------|--------|------------|
| Storage | Supabase S3 | Filesystem (local) or Supabase S3 (Vercel) |
| Vault | Supabase pgsodium | In-memory with VAULT_SECRET |
| LLM Providers | Always all 3 (openai, anthropic, google) | Conditional on API key presence |
| Process Delegation | Trigger.dev in production | Always in-process |
| Callbacks | Full Langfuse tracing + DB persistence | Basic tracing only |
| Vector Store Services | All 4 services configured | None configured |
| GitHub Integration | Full GitHub App auth | Optional (if env vars present) |
| AI Gateway | Configured with referer/title | Not configured |
| Telemetry | Enabled with flush function | Enabled without flush |

**Sources:**
- [apps/studio.giselles.ai/app/giselle-engine.ts:40-396]()
- [apps/playground/giselle-engine.ts:1-141]()

## Sample App Workspace IDs

Both Studio and Playground support a `SAMPLE_APP_WORKSPACE_IDS` environment variable:

```typescript
let sampleAppWorkspaceIds: WorkspaceId[] | undefined;
if (process.env.SAMPLE_APP_WORKSPACE_IDS) {
  const workspaceIdStrings = process.env.SAMPLE_APP_WORKSPACE_IDS.split(",")
    .map((id) => id.trim())
    .filter((id) => id.length > 0);
  const parsedWorkspaceIds: WorkspaceId[] = [];
  for (const workspaceIdString of workspaceIdStrings) {
    const parseResult = WorkspaceId.safeParse(workspaceIdString);
    if (parseResult.success) {
      parsedWorkspaceIds.push(parseResult.data);
    }
  }
  if (parsedWorkspaceIds.length > 0) {
    sampleAppWorkspaceIds = parsedWorkspaceIds;
  }
}
```

These workspace IDs are likely used to identify example or template workspaces that are treated specially by the system.

**Sources:**
- [apps/studio.giselles.ai/app/giselle-engine.ts:53-68]()
- [apps/playground/giselle-engine.ts:105-120]()

---

# Page: Generation Pipeline and Lifecycle

# Generation Pipeline and Lifecycle

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/playground/giselle-engine.ts](apps/playground/giselle-engine.ts)
- [apps/studio.giselles.ai/app/giselle-engine.ts](apps/studio.giselles.ai/app/giselle-engine.ts)
- [packages/giselle/src/engine/acts/run-act.ts](packages/giselle/src/engine/acts/run-act.ts)
- [packages/giselle/src/engine/generations/generate-content.ts](packages/giselle/src/engine/generations/generate-content.ts)
- [packages/giselle/src/engine/generations/generate-image.ts](packages/giselle/src/engine/generations/generate-image.ts)
- [packages/giselle/src/engine/generations/internal/use-generation-executor.ts](packages/giselle/src/engine/generations/internal/use-generation-executor.ts)
- [packages/giselle/src/engine/generations/types.ts](packages/giselle/src/engine/generations/types.ts)
- [packages/giselle/src/engine/generations/utils.ts](packages/giselle/src/engine/generations/utils.ts)
- [packages/giselle/src/engine/operations/execute-query.ts](packages/giselle/src/engine/operations/execute-query.ts)
- [packages/giselle/src/engine/telemetry/index.ts](packages/giselle/src/engine/telemetry/index.ts)
- [packages/giselle/src/engine/telemetry/types.ts](packages/giselle/src/engine/telemetry/types.ts)
- [packages/giselle/src/engine/triggers/resolve-trigger.ts](packages/giselle/src/engine/triggers/resolve-trigger.ts)
- [packages/giselle/src/engine/types.ts](packages/giselle/src/engine/types.ts)
- [packages/giselle/src/react/generations/generation-runner.tsx](packages/giselle/src/react/generations/generation-runner.tsx)

</details>



## Purpose and Scope

This document explains the generation execution pipeline, covering how AI operations progress through their lifecycle from creation to completion or failure. It details the `useGenerationExecutor` orchestrator, streaming operations, cancellation mechanisms, and the distinction between local and delegated execution.

For information about language model integration and provider configuration, see [Language Models and AI Providers](#2.3). For storage mechanisms used to persist generation data, see [Storage Architecture](#2.4). For the workflow orchestration that triggers generations, see [Giselle Engine Architecture](#2.1).

---

## Generation Lifecycle States

A generation progresses through distinct states from initiation to completion:

```mermaid
stateDiagram-v2
    [*] --> created: User initiates generation
    created --> queued: Validation passes
    queued --> running: Execution begins
    running --> completed: Success
    running --> failed: Error occurs
    running --> cancelled: User cancels
    completed --> [*]
    failed --> [*]
    cancelled --> [*]
    
    note right of created
        Status shown in UI
        Not yet queued
    end note
    
    note right of queued
        QueuedGeneration type
        Ready for execution
    end note
    
    note right of running
        RunningGeneration type
        startedAt timestamp set
        messages array initialized
    end note
    
    note right of completed
        CompletedGeneration type
        outputs populated
        usage metrics recorded
    end note
    
    note right of failed
        FailedGeneration type
        error details stored
    end note
```

**Sources:**
- [packages/giselle/src/engine/generations/internal/use-generation-executor.ts:84-95]()
- [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:196-241]()

### Generation Type Definitions

| State | Type | Key Properties | Storage Path |
|-------|------|----------------|--------------|
| `created` | Initial UI state | No formal type | Display only |
| `queued` | `QueuedGeneration` | `status: "queued"`, `context`, `createdAt` | `generations/{id}/generation.json` |
| `running` | `RunningGeneration` | `status: "running"`, `startedAt`, `messages: []` | Same path, updated |
| `completed` | `CompletedGeneration` | `status: "completed"`, `completedAt`, `outputs`, `usage` | Same path, finalized |
| `failed` | `FailedGeneration` | `status: "failed"`, `failedAt`, `error` | Same path, with error |
| `cancelled` | Part of running flow | Detected via storage check | Same path |

**Sources:**
- [packages/giselle/src/engine/generations/internal/use-generation-executor.ts:24-25]()
- [packages/giselle/src/concepts/generation/output.ts:1-107]()

---

## useGenerationExecutor Architecture

The `useGenerationExecutor` function orchestrates the entire generation lifecycle, providing a consistent execution environment across all generation types.

```mermaid
graph TB
    Input["useGenerationExecutor<br/>args: {context, generation, execute}"]
    
    subgraph "Initialization"
        ParseContext["Parse GenerationContext<br/>from generation.context"]
        CreateRunning["Create RunningGeneration<br/>(if QueuedGeneration)<br/>status: 'running'<br/>startedAt: Date.now()"]
        PersistRunning["Persist to storage<br/>via setGeneration()"]
    end
    
    subgraph "Pre-Execution Checks"
        ExtractWorkspace["Extract workspaceId<br/>from origin.workspaceId"]
        CheckLimits["checkUsageLimits()<br/>fetchUsageLimitsFn"]
        LimitError["Throw UsageLimitError<br/>Set failed state"]
    end
    
    subgraph "Resolver Setup"
        FileResolver["fileResolver(fileId)<br/>→ DataContent<br/>from storage paths"]
        TextResolver["generationContentResolver<br/>(nodeId, outputId)<br/>→ string"]
        ImageResolver["imageGenerationResolver<br/>(nodeId, outputId)<br/>→ ImagePart[]"]
        FinishGen["finishGeneration()<br/>callback builder"]
    end
    
    subgraph "User Execute Function"
        UserExecute["execute({<br/>  runningGeneration,<br/>  generationContext,<br/>  fileResolver,<br/>  ...resolvers,<br/>  finishGeneration<br/>})"]
        GenLogic["Generation-specific logic<br/>(text/image/query)"]
        CallFinish["Call finishGeneration({<br/>  outputs,<br/>  usage,<br/>  inputMessages<br/>})"]
    end
    
    subgraph "Completion Flow"
        Sanitize["sanitizeGenerationUsage(usage)"]
        CreateCompleted["Create CompletedGeneration<br/>status: 'completed'<br/>completedAt: Date.now()"]
        ProcessImages["Process image outputs<br/>getGeneratedImage()"]
        Persist["Persist completed state"]
        ConsumeTime["handleAgentTimeConsumption()"]
        Callback["callbacks.generationComplete()"]
    end
    
    Input --> ParseContext
    ParseContext --> CreateRunning
    CreateRunning --> PersistRunning
    PersistRunning --> ExtractWorkspace
    ExtractWorkspace --> CheckLimits
    CheckLimits -->|Pass| FileResolver
    CheckLimits -->|Fail| LimitError
    
    FileResolver --> TextResolver
    TextResolver --> ImageResolver
    ImageResolver --> FinishGen
    FinishGen --> UserExecute
    
    UserExecute --> GenLogic
    GenLogic --> CallFinish
    
    CallFinish --> Sanitize
    Sanitize --> CreateCompleted
    CreateCompleted --> ProcessImages
    ProcessImages --> Persist
    Persist --> ConsumeTime
    ConsumeTime --> Callback
    Callback --> Output["Return result"]
```

**Sources:**
- [packages/giselle/src/engine/generations/internal/use-generation-executor.ts:59-411]()

### Key Responsibilities

**1. State Transition Management**

The executor transitions a generation from `queued` to `running`, then to either `completed` or `failed`:

```typescript
// Transition queued → running
const runningGeneration: RunningGeneration = isQueuedGeneration(args.generation)
  ? {
      ...args.generation,
      status: "running",
      messages: [],
      startedAt: Date.now(),
    }
  : args.generation;
```

**Sources:**
- [packages/giselle/src/engine/generations/internal/use-generation-executor.ts:86-95]()

**2. Usage Limit Validation**

Before execution begins, usage limits are checked:

```typescript
const usageLimitStatus = await checkUsageLimits({
  workspaceId,
  generation: args.generation,
  fetchUsageLimitsFn: args.context.fetchUsageLimitsFn,
});

if (usageLimitStatus.type === "error") {
  const failedGeneration: Generation = {
    ...runningGeneration,
    status: "failed",
    failedAt: Date.now(),
    error: {
      name: usageLimitStatus.error,
      message: usageLimitStatus.error,
      dump: usageLimitStatus,
    },
  } as const;
  await setGeneration(failedGeneration);
  throw new UsageLimitError(usageLimitStatus.error);
}
```

**Sources:**
- [packages/giselle/src/engine/generations/internal/use-generation-executor.ts:123-145]()

**3. Content Resolution**

Three resolver functions enable accessing previous generation outputs and files:

| Resolver | Purpose | Returns |
|----------|---------|---------|
| `fileResolver` | Retrieve file content | `DataContent` (Uint8Array) |
| `generationContentResolver` | Get text output from previous nodes | `string \| undefined` |
| `imageGenerationResolver` | Get image output from previous nodes | `ImagePart[] \| undefined` |

**Sources:**
- [packages/giselle/src/engine/generations/internal/use-generation-executor.ts:146-324]()

**4. Completion Finalization**

The `finishGeneration` callback handles completion state:

```typescript
async function finishGeneration({
  outputs,
  usage,
  inputMessages,
  generateMessages,
  providerMetadata,
}: FinishGenerationArgs) {
  const sanitizedUsage = sanitizeGenerationUsage(usage);
  const completedGeneration = {
    ...runningGeneration,
    status: "completed",
    completedAt: Date.now(),
    outputs,
    usage: sanitizedUsage,
    messages: generateMessages ?? [],
  } satisfies CompletedGeneration;

  // Process image outputs into outputFileBlobs
  const outputFileBlobs: OutputFileBlob[] = [];
  for (const output of outputs) {
    if (output.type !== "generated-image") continue;
    // ... image blob processing
  }

  await Promise.all([
    setGeneration(completedGeneration),
    handleAgentTimeConsumption({ workspaceId, generation: completedGeneration, ... }),
    args.context.callbacks?.generationComplete?.({
      generation: completedGeneration,
      inputMessages,
      outputFileBlobs,
      providerMetadata,
      generationMetadata: args.metadata,
    }),
  ]);
  
  return { completedGeneration, outputFileBlobs };
}
```

**Sources:**
- [packages/giselle/src/engine/generations/internal/use-generation-executor.ts:326-398]()

---

## Generation Type Implementations

Different generation types use `useGenerationExecutor` with type-specific execution logic.

### Text Generation Flow

Text generation with streaming is implemented in `generateContent`:

```mermaid
sequenceDiagram
    participant Client
    participant generateContent
    participant Executor as useGenerationExecutor
    participant AISDk as streamText (AI SDK)
    participant Storage
    
    Client->>generateContent: generation: RunningGeneration
    generateContent->>Executor: useGenerationExecutor({execute})
    Executor->>Executor: Check usage limits<br/>checkUsageLimits()
    Executor->>generateContent: Execute callback
    
    generateContent->>generateContent: buildMessageObject()<br/>Resolve {{nodeId:outputId}} refs
    generateContent->>generateContent: Prepare PreparedToolSet<br/>githubTools, createPostgresTools
    generateContent->>generateContent: getProviderOptions()<br/>Anthropic/OpenAI configs
    
    generateContent->>AISDk: streamText({<br/>  model: generationModel(),<br/>  messages, tools,<br/>  onChunk, onError, onFinish<br/>})
    AISDk-->>generateContent: toUIMessageStream()
    
    loop Streaming chunks
        AISDk->>generateContent: UI message chunk
        generateContent->>Storage: batchWriter.add(chunk)<br/>→ ui-message-chunks
        generateContent->>Client: Stream chunk
    end
    
    AISDk->>generateContent: onFinish({ messages })
    generateContent->>generateContent: Extract outputs:<br/>text, reasoningText, sources
    generateContent->>Executor: finishGeneration({<br/>  outputs, usage, inputMessages<br/>})
    Executor->>Storage: setGeneration(CompletedGeneration)
    Executor->>Client: Generation complete
```

**Sources:**
- [packages/giselle/src/engine/generations/generate-content.ts:62-447]()

The text generation implementation in `generateContent`:

1. **Message Building**: `buildMessageObject()` constructs `ModelMessage[]` by resolving `{{nd-X:otp-Y}}` template patterns with source node outputs
2. **Tool Preparation**: Creates `PreparedToolSet` with:
   - `githubTools()` from `@giselles-ai/github-tool` 
   - `createPostgresTools()` for database queries
   - `openai.tools.webSearch()` or `anthropic.tools.webSearch_20250305()`
   - `google.tools.googleSearch()` and `google.tools.urlContext()`
3. **Provider Options**: `getProviderOptions()` configures provider-specific settings:
   - Anthropic: `thinking.budgetTokens`
   - OpenAI: `textVerbosity`, `reasoningEffort`, `reasoningSummary`
4. **Streaming**: Uses `streamText().toUIMessageStream()` with `smoothStream({ delayInMs: 1000 })` transform
5. **Output Extraction**: Awaits `streamTextResult.text`, `streamTextResult.reasoningText`, `streamTextResult.sources`

**Sources:**
- [packages/giselle/src/engine/generations/generate-content.ts:103-244]()
- [packages/giselle/src/engine/generations/generate-content.ts:256-288]()
- [packages/giselle/src/engine/generations/generate-content.ts:289-411]()
- [packages/giselle/src/engine/generations/generate-content.ts:449-487]()

### Chunk Persistence and Resumability

The `generateContent` function persists streaming chunks for resumability:

```mermaid
graph TB
    Start["generateContent()"]
    UseExec["useGenerationExecutor"]
    
    subgraph "Execution Setup"
        Build["buildMessageObject()"]
        PrepTools["Prepare PreparedToolSet"]
        CreateAbort["abortController = new AbortController()"]
        StreamSetup["streamText({<br/>  abortSignal: abortController.signal,<br/>  onChunk, onError, onFinish,<br/>  experimental_transform: smoothStream<br/>})"]
    end
    
    subgraph "UI Message Streaming"
        UIStream["streamTextResult.toUIMessageStream({<br/>  onFinish: async ({ messages })<br/>})"]
        Writer["batchWriter({<br/>  process: setBlob(ui-message-chunks),<br/>  preserveItems: true<br/>})"]
        ChunkLoop["for await (chunk of uiMessageStream)"]
        AddChunk["writer.add(chunk)<br/>uiMessageChunks.push(chunk)"]
        ProcessBatch["Batch writes to<br/>generationUiMessageChunksPath()"]
    end
    
    subgraph "Completion Handling"
        OnFinish["onFinish callback"]
        ExtractText["await streamTextResult.text"]
        ExtractReasoning["await streamTextResult.reasoningText"]
        ExtractSources["await streamTextResult.sources"]
        FinishGen["finishGeneration({ outputs })"]
    end
    
    Start --> UseExec
    UseExec --> Build
    Build --> PrepTools
    PrepTools --> CreateAbort
    CreateAbort --> StreamSetup
    StreamSetup --> UIStream
    UIStream --> Writer
    Writer --> ChunkLoop
    ChunkLoop --> AddChunk
    AddChunk --> ProcessBatch
    ProcessBatch --> ChunkLoop
    ChunkLoop -->|Stream ends| OnFinish
    OnFinish --> ExtractText
    ExtractText --> ExtractReasoning
    ExtractReasoning --> ExtractSources
    ExtractSources --> FinishGen
```

**Key Implementation Details:**

1. **Smooth Streaming**: `experimental_transform: smoothStream({ delayInMs: 1000, chunking: "line" })` controls output rate
2. **Chunk Persistence**: `batchWriter` accumulates chunks and writes newline-delimited JSON to `generations/{id}/ui-message-chunks`
3. **Cancellation Checking**: `onChunk` callback polls `getGeneration()` to detect `status === "cancelled"`, then calls `abortController.abort()`
4. **Abort Signal**: `AbortController.signal` propagates cancellation to AI SDK's `streamText()`
5. **Error Handling**: `onError` callback stores error in `generationError` variable for later processing

**Sources:**
- [packages/giselle/src/engine/generations/generate-content.ts:256-288]()
- [packages/giselle/src/engine/generations/generate-content.ts:289-412]()
- [packages/giselle/src/engine/generations/generate-content.ts:414-438]()
- [packages/giselle/src/utils/batch-writer.ts:1-100]() (inferred)

### Image Generation Flow

Image generation follows a simpler, non-streaming pattern:

```mermaid
sequenceDiagram
    participant generateImage
    participant Executor
    participant Provider as Provider SDK
    participant Storage
    
    generateImage->>Executor: useGenerationExecutor
    Executor->>generateImage: Execute callback
    
    generateImage->>generateImage: Build messages
    
    alt Fal Provider
        generateImage->>Provider: generateImage(fal.image(modelId))
    else OpenAI Provider
        generateImage->>Provider: generateImage(openai.image("gpt-image-1"))
    else Google Provider
        generateImage->>Provider: generateText(google(modelId))
    end
    
    Provider-->>generateImage: { images: [...] }
    
    loop For each image
        generateImage->>generateImage: detectImageType(uint8Array)
        generateImage->>Storage: setGeneratedImage({<br/>  generation,<br/>  generatedImage,<br/>  filename<br/>})
    end
    
    generateImage->>Executor: finishGeneration({ outputs })
    Executor->>Storage: Persist CompletedGeneration
```

**Sources:**
- [packages/giselle/src/engine/generations/generate-image.ts:34-135]()
- [packages/giselle/src/engine/generations/generate-image.ts:137-221]()
- [packages/giselle/src/engine/generations/generate-image.ts:223-308]()
- [packages/giselle/src/engine/generations/generate-image.ts:310-380]()

### Query Execution Flow

Query nodes execute vector store searches:

```mermaid
graph TB
    Start["executeQuery()"]
    UseExec["useGenerationExecutor"]
    
    subgraph "Query Resolution"
        ResolveQuery["resolveQuery()<br/>Replace {{nd-X:otp-Y}} templates<br/>with source node outputs"]
        ExtractNodes["Extract connected<br/>VectorStoreNodes"]
    end
    
    subgraph "Vector Store Search"
        LoopStores["For each vector store node"]
        CheckProvider{Provider?}
        GitHubSearch["gitHubQueryService.search()"]
        DocSearch["documentQueryService.search()"]
        EmbedCallback["embeddingComplete callback<br/>(track usage)"]
    end
    
    subgraph "Result Assembly"
        BuildOutput["Build QueryResultOutput<br/>with records + metadata"]
        Finish["finishGeneration({ outputs })"]
    end
    
    Start --> UseExec
    UseExec --> ResolveQuery
    ResolveQuery --> ExtractNodes
    ExtractNodes --> LoopStores
    LoopStores --> CheckProvider
    CheckProvider -->|GitHub| GitHubSearch
    CheckProvider -->|Document| DocSearch
    GitHubSearch --> EmbedCallback
    DocSearch --> EmbedCallback
    EmbedCallback --> BuildOutput
    BuildOutput --> Finish
```

**Sources:**
- [packages/giselle/src/engine/operations/execute-query.ts:43-126]()
- [packages/giselle/src/engine/operations/execute-query.ts:299-502]()

---

## Streaming Operations

### UI Message Stream Structure

Text generation streams data as UI messages to the client:

```typescript
type UIMessageStreamChunk = 
  | { type: "text-delta", text: string }
  | { type: "tool-call", toolName: string, args: unknown }
  | { type: "tool-result", toolName: string, result: unknown }
  | { type: "finish", ... }
```

**Streaming Pipeline:**

```mermaid
graph LR
    AIModel["AI Model<br/>(OpenAI/Anthropic/Google)"]
    StreamText["streamText()<br/>AI SDK"]
    ToUI["toUIMessageStream()"]
    BatchWriter["batchWriter"]
    Storage["Storage<br/>ui-message-chunks"]
    Client["Client UI"]
    
    AIModel -->|Raw chunks| StreamText
    StreamText -->|Smooth stream| ToUI
    ToUI -->|UI chunks| BatchWriter
    ToUI -->|UI chunks| Client
    BatchWriter -->|Persisted batches| Storage
```

**Sources:**
- [packages/giselle/src/engine/generations/generate-content.ts:258-292]()
- [packages/giselle/src/engine/generations/generate-content.ts:418-442]()

### Batch Writing for Resumability

The `batchWriter` accumulates chunks and writes them in batches:

```typescript
const writer = batchWriter<StreamItem<typeof uiMessageStream>>({
  process: (batch) => {
    return context.experimental_storage.setBlob(
      generationUiMessageChunksPath(generation.id),
      new TextEncoder().encode(
        batch.map((chunk) => JSON.stringify(chunk)).join("\n")
      )
    );
  },
  preserveItems: true,
  logger,
});

for await (const chunk of uiMessageStream) {
  writer.add(chunk);
  uiMessageChunks.push(chunk);
}
await writer.close();
```

**Sources:**
- [packages/giselle/src/engine/generations/generate-content.ts:418-442]()

---

## Cancellation Support

### Cancellation Detection

Generations can be cancelled during execution through two mechanisms:

**1. OnChunk Polling (generateContent)**

```typescript
streamText({
  // ...
  onChunk: async () => {
    const currentGeneration = await getGeneration({
      storage: context.storage,
      experimental_storage: context.experimental_storage,
      useExperimentalStorage: true,
      generationId: generation.id,
    });
    if (currentGeneration?.status === "cancelled") {
      logger.debug(`${generation.id} will abort`);
      abortController.abort();
    }
  },
  onAbort: () => {
    logger.debug({ generationId: generation.id }, "streamText onAbort");
  },
  // ...
});
```

**Sources:**
- [packages/giselle/src/engine/generations/generate-content.ts:265-276]()

**2. AbortSignal Propagation**

The executor propagates `AbortSignal` to generation functions:

```mermaid
graph TB
    Client["Client calls<br/>stopCurrentGeneration()"]
    UpdateStorage["Update storage:<br/>generation.status = 'cancelled'"]
    OnChunk["onChunk callback:<br/>getGeneration() polls storage"]
    CheckStatus{"status === 'cancelled'?"}
    Abort["abortController.abort()"]
    OnAbort["onAbort callback triggered"]
    SDKCheck["AI SDK receives signal:<br/>abortSignal.aborted === true"]
    Stop["streamText() stops:<br/>throws AbortError"]
    
    Client --> UpdateStorage
    UpdateStorage --> OnChunk
    OnChunk --> CheckStatus
    CheckStatus -->|Yes| Abort
    CheckStatus -->|No| OnChunk
    Abort --> OnAbort
    Abort --> SDKCheck
    SDKCheck --> Stop
```

**Code Entity Flow:**

1. UI calls `stopCurrentGeneration()` which updates generation status via `setGeneration()`
2. `onChunk` callback in `streamText()` polls storage: `await getGeneration({ storage, generationId })`
3. If `currentGeneration?.status === "cancelled"`, calls `abortController.abort()`
4. `onAbort` callback logs: `logger.debug({ generationId }, "streamText onAbort")`
5. AI SDK receives `abortSignal.aborted === true` and stops streaming

**Sources:**
- [packages/giselle/src/engine/generations/generate-content.ts:264-276]()
- [packages/giselle/src/engine/generations/internal/use-generation-executor.ts:62]()
- [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:207-216]()

### UI Cancellation Flow

In the workflow designer UI, users can cancel running generations:

```typescript
{(currentGeneration?.status === "queued" || currentGeneration?.status === "running") && (
  <button
    type="button"
    onClick={(e) => {
      e.stopPropagation();
      stopCurrentGeneration();
    }}
  >
    <SquareIcon className="w-2 h-2" />
  </button>
)}
```

**Sources:**
- [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:206-225]()

---

## Process Delegation: Self vs Trigger.dev

The engine supports two execution modes for content generation:

```mermaid
graph TB
    GiselleEngine["GiselleEngine"]
    CheckProcessor{generateContentProcessor}
    
    subgraph "Self Execution"
        SelfRoute["Process: 'self'"]
        LocalExec["Execute locally<br/>in same request"]
    end
    
    subgraph "Trigger.dev Delegation"
        TriggerRoute["Process: 'trigger.dev'"]
        TriggerJob["jobs.trigger(<br/>'generate-content',<br/>{ generationId, userId, team }<br/>)"]
        JobContext["Trigger.dev job context"]
        JobExec["generateContent()<br/>in worker"]
    end
    
    GiselleEngine --> CheckProcessor
    CheckProcessor -->|"'self'"| SelfRoute
    CheckProcessor -->|"'trigger.dev'"| TriggerRoute
    
    SelfRoute --> LocalExec
    TriggerRoute --> TriggerJob
    TriggerJob --> JobContext
    JobContext --> JobExec
```

### Delegation Configuration

The choice between self-execution and delegation is determined at engine initialization:

```typescript
const generateContentProcessor =
  process.env.USE_TRIGGER_DEV === "1" ||
  runtimeEnv === "trigger.dev" ||
  (runtimeEnv === "vercel" && process.env.NODE_ENV !== "development")
    ? "trigger.dev"
    : "self";
```

**Decision Logic:**

| Condition | Processor | Reason |
|-----------|-----------|--------|
| `USE_TRIGGER_DEV=1` | `trigger.dev` | Explicitly enabled |
| Runtime is Trigger.dev | `trigger.dev` | Already in worker context |
| Production Vercel | `trigger.dev` | Long-running operations need background jobs |
| Development (local/Vercel) | `self` | Immediate feedback for debugging |

**Sources:**
- [apps/studio.giselles.ai/app/giselle-engine.ts:211-216]()

### Trigger.dev Process Configuration

When delegated, the engine provides a process function:

```typescript
giselleEngine.setGenerateContentProcess(async ({ generation, metadata }) => {
  const requestId = getRequestId();
  
  switch (generation.context.origin.type) {
    case "github-app": {
      const team = await getWorkspaceTeam(generation.context.origin.workspaceId);
      await jobs.trigger<typeof generateContentJob>("generate-content", {
        generationId: generation.id,
        requestId,
        userId: "github-app",
        team: { id: team.id, type: team.type, subscriptionId: team.activeSubscriptionId },
      });
      break;
    }
    case "stage":
    case "studio": {
      // Fetch user/team based on runtime environment
      // Trigger job with user context
      break;
    }
  }
});
```

The job receives `GenerationMetadata` containing user and team context to avoid circular authentication calls:

```typescript
type GenerationMetadata = {
  userId: string;
  requestId: string;
  team: { id: string; type: string; subscriptionId: string | null };
};
```

**Sources:**
- [apps/studio.giselles.ai/app/giselle-engine.ts:430-493]()
- [packages/giselle/src/engine/generations/generate-content.ts:62-77]()

---

## Storage Paths and Persistence

### Generation Storage Paths

| Path Pattern | Purpose | Format | Function |
|--------------|---------|--------|----------|
| `generations/{id}/generation.json` | Main generation state | JSON with `Generation` type | `generationPath()` |
| `generations/byNode/{nodeId}.json` | Node → Generation index | Array of `NodeGenerationIndex` | `nodeGenerationIndexPath()` |
| `generations/byAct/{actId}.json` | Act → Generation index | Array of `{id, nodeId, createdAt}` | `actGenerationIndexPath()` |
| `generations/{id}/ui-message-chunks` | Streaming chunks (resumable) | Newline-delimited JSON | `generationUiMessageChunksPath()` |
| `generations/{id}/generated-images/{filename}` | Image outputs | Binary blob (uint8Array) | `generatedImagePath()` |

**Sources:**
- [packages/giselle/src/engine/generations/utils.ts:316-318]()
- [packages/giselle/src/engine/generations/utils.ts:335-337]()
- [packages/giselle/src/engine/path.ts:1-20]() (inferred from usage)
- [packages/giselle/src/engine/generations/utils.ts:612-614]()

### Storage Backend

The engine uses `GiselleStorage` interface for all generation persistence:

```mermaid
graph TB
    Generation["Generation Operation"]
    
    subgraph "GiselleStorage Interface"
        Interface["context.storage"]
        GetBlob["getBlob(path): Promise<Uint8Array>"]
        SetBlob["setBlob(path, data): Promise<void>"]
        GetJson["getJson({path, schema}): Promise<T>"]
        Exists["exists(path): Promise<boolean>"]
    end
    
    subgraph "Storage Driver"
        Driver["supabaseStorageDriver"]
        S3Ops["S3-compatible operations<br/>endpoint, accessKeyId, secretAccessKey"]
        Bucket["bucket: 'app'"]
    end
    
    Generation --> Interface
    Interface --> GetBlob
    Interface --> SetBlob
    Interface --> GetJson
    Interface --> Exists
    
    GetBlob --> Driver
    SetBlob --> Driver
    GetJson --> Driver
    Exists --> Driver
    
    Driver --> S3Ops
    S3Ops --> Bucket
```

**Implementation in Studio:**

```typescript
const storage = experimental_supabaseStorageDriver({
  endpoint: process.env.SUPABASE_STORAGE_URL ?? "",
  region: process.env.SUPABASE_STORAGE_REGION ?? "",
  accessKeyId: process.env.SUPABASE_STORAGE_ACCESS_KEY_ID ?? "",
  secretAccessKey: process.env.SUPABASE_STORAGE_SECRET_ACCESS_KEY ?? "",
  bucket: "app",
});
```

**Sources:**
- [apps/studio.giselles.ai/app/giselle-engine.ts:40-46]()
- [packages/giselle/src/engine/storage/types.ts:1-20]() (inferred)

---

## Callbacks and Telemetry

### Lifecycle Callbacks

The engine invokes callbacks at key lifecycle events:

```mermaid
sequenceDiagram
    participant Gen as Generation
    participant Callbacks
    participant Langfuse
    participant Analytics
    
    Note over Gen: Generation completes
    Gen->>Callbacks: generationComplete({<br/>  generation,<br/>  inputMessages,<br/>  outputFileBlobs,<br/>  providerMetadata<br/>})
    
    Callbacks->>Langfuse: traceGeneration({<br/>  generation,<br/>  inputMessages,<br/>  userId, tags, metadata<br/>})
    
    Callbacks->>Analytics: Track usage metrics
    
    Note over Gen: Generation fails
    Gen->>Callbacks: generationFailed({<br/>  generation,<br/>  inputMessages<br/>})
    
    Callbacks->>Langfuse: traceGeneration (with error)
    
    Note over Gen: Embedding query completes
    Gen->>Callbacks: embeddingComplete({<br/>  embeddingMetrics,<br/>  generation,<br/>  queryContext<br/>})
    
    Callbacks->>Langfuse: traceEmbedding({<br/>  metrics, userId,<br/>  metadata<br/>})
```

**Sources:**
- [apps/studio.giselles.ai/app/giselle-engine.ts:256-298]()
- [apps/studio.giselles.ai/app/giselle-engine.ts:299-328]()
- [apps/studio.giselles.ai/app/giselle-engine.ts:329-389]()

### Callback Timing

Callbacks are invoked during `finishGeneration`:

```typescript
await Promise.all([
  setGeneration(completedGeneration),
  handleAgentTimeConsumption({ workspaceId, generation: completedGeneration, ... }),
  (async () => {
    const result = await args.context.callbacks?.generationComplete?.({
      generation: completedGeneration,
      inputMessages,
      outputFileBlobs,
      providerMetadata,
      generationMetadata: args.metadata,
    });
    return result;
  })(),
]);
```

This ensures storage persistence, usage tracking, and telemetry occur concurrently.

**Sources:**
- [packages/giselle/src/engine/generations/internal/use-generation-executor.ts:372-390]()

---

## Summary: Key Components

| Component | File Path | Responsibility |
|-----------|-----------|----------------|
| `useGenerationExecutor` | `packages/giselle/src/engine/generations/internal/use-generation-executor.ts` | Lifecycle orchestration, state transitions, resolver setup |
| `generateText` | `packages/giselle/src/engine/generations/generate-text.ts` | Text generation via `streamText()` |
| `generateContent` | `packages/giselle/src/engine/generations/generate-content.ts` | Content generation with resumable streaming |
| `generateImage` | `packages/giselle/src/engine/generations/generate-image.ts` | Image generation (Fal, OpenAI, Google) |
| `executeQuery` | `packages/giselle/src/engine/operations/execute-query.ts` | Vector store query execution |
| `setGenerateContentProcess` | `apps/studio.giselles.ai/app/giselle-engine.ts` | Trigger.dev delegation configuration |
| UI Status Display | `internal-packages/workflow-designer-ui/src/editor/node/node.tsx` | Visual lifecycle state feedback |

**Sources:**
- [packages/giselle/src/engine/generations/internal/use-generation-executor.ts:1-412]()
- [packages/giselle/src/engine/generations/generate-text.ts:1-467]()
- [packages/giselle/src/engine/generations/generate-content.ts:1-523]()
- [packages/giselle/src/engine/generations/generate-image.ts:1-381]()
- [packages/giselle/src/engine/operations/execute-query.ts:1-503]()
- [apps/studio.giselles.ai/app/giselle-engine.ts:430-538]()
- [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:196-241]()

---

# Page: Language Models and AI Provider Integration

# Language Models and AI Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/playground/giselle-engine.ts](apps/playground/giselle-engine.ts)
- [apps/playground/package.json](apps/playground/package.json)
- [apps/studio.giselles.ai/app/giselle-engine.ts](apps/studio.giselles.ai/app/giselle-engine.ts)
- [apps/studio.giselles.ai/package.json](apps/studio.giselles.ai/package.json)
- [internal-packages/workflow-designer-ui/package.json](internal-packages/workflow-designer-ui/package.json)
- [package.json](package.json)
- [packages/giselle/package.json](packages/giselle/package.json)
- [packages/giselle/src/engine/acts/run-act.ts](packages/giselle/src/engine/acts/run-act.ts)
- [packages/giselle/src/engine/generations/generate-content.ts](packages/giselle/src/engine/generations/generate-content.ts)
- [packages/giselle/src/engine/generations/generate-image.ts](packages/giselle/src/engine/generations/generate-image.ts)
- [packages/giselle/src/engine/generations/internal/use-generation-executor.ts](packages/giselle/src/engine/generations/internal/use-generation-executor.ts)
- [packages/giselle/src/engine/generations/types.ts](packages/giselle/src/engine/generations/types.ts)
- [packages/giselle/src/engine/generations/utils.ts](packages/giselle/src/engine/generations/utils.ts)
- [packages/giselle/src/engine/operations/execute-query.ts](packages/giselle/src/engine/operations/execute-query.ts)
- [packages/giselle/src/engine/telemetry/index.ts](packages/giselle/src/engine/telemetry/index.ts)
- [packages/giselle/src/engine/telemetry/types.ts](packages/giselle/src/engine/telemetry/types.ts)
- [packages/giselle/src/engine/triggers/resolve-trigger.ts](packages/giselle/src/engine/triggers/resolve-trigger.ts)
- [packages/giselle/src/engine/types.ts](packages/giselle/src/engine/types.ts)
- [packages/giselle/src/react/generations/generation-runner.tsx](packages/giselle/src/react/generations/generation-runner.tsx)
- [pnpm-lock.yaml](pnpm-lock.yaml)
- [pnpm-workspace.yaml](pnpm-workspace.yaml)

</details>



## Purpose and Scope

This document describes the language model integration architecture in the Giselle platform, covering how multiple LLM providers (OpenAI, Anthropic, Google, Perplexity) are abstracted and integrated through the Vercel AI SDK. It details model selection, provider-specific configurations, tier-based access control, and the generation pipeline that powers text and image generation workflows.

For information about the generation lifecycle and execution flow, see [Generation Pipeline and State Management](#2.2). For storage of generation artifacts, see [Storage Architecture](#2.4).

## Provider Architecture

The Giselle Engine supports multiple LLM providers through a unified abstraction layer, with provider availability determined at engine initialization.

### Provider Registration

```mermaid
graph TB
    Config["GiselleEngineConfig<br/>{llmProviders: LanguageModelProvider[]}"]
    Context["GiselleEngineContext<br/>llmProviders: array"]
    
    subgraph "Provider Types"
        OpenAI["'openai'"]
        Anthropic["'anthropic'"]
        Google["'google'"]
        Perplexity["'perplexity'"]
        Fal["'fal'"]
    end
    
    subgraph "API Key Requirements"
        OpenAIKey["OPENAI_API_KEY"]
        AnthropicKey["ANTHROPIC_API_KEY"]
        GoogleKey["GOOGLE_GENERATIVE_AI_API_KEY"]
        FalKey["FAL_API_KEY"]
    end
    
    Config --> Context
    Context --> OpenAI
    Context --> Anthropic
    Context --> Google
    Context --> Perplexity
    Context --> Fal
    
    OpenAIKey -.required for.-> OpenAI
    AnthropicKey -.required for.-> Anthropic
    GoogleKey -.required for.-> Google
    FalKey -.required for.-> Fal
    
    WorkflowDesigner["WorkflowDesignerStore<br/>llmProviders filter"]
    Context --> WorkflowDesigner
```

**Sources:** 
- [apps/studio.giselles.ai/app/giselle-engine.ts:271]()
- [apps/playground/giselle-engine.ts:41-54]()
- [packages/giselle/src/engine/types.ts:67-101]()

The `llmProviders` array in `GiselleEngineContext` controls which providers are available throughout the application. In the studio app, all supported providers are enabled, while the playground conditionally enables providers based on available API keys.

### Provider SDK Mapping

```mermaid
graph LR
    subgraph "AI SDK Packages"
        AISDK_OpenAI["@ai-sdk/openai<br/>v2.0.30"]
        AISDK_Anthropic["@ai-sdk/anthropic<br/>v2.0.17"]
        AISDK_Google["@ai-sdk/google<br/>v2.0.14"]
        AISDK_GoogleVertex["@ai-sdk/google-vertex<br/>v3.0.27"]
        AISDK_Perplexity["@ai-sdk/perplexity<br/>v2.0.9"]
        AISDK_Fal["@ai-sdk/fal<br/>v1.0.13"]
        AISDK_Provider["@ai-sdk/provider<br/>v2.0.0"]
        AISDK_Gateway["@ai-sdk/gateway<br/>v1.0.23"]
    end
    
    subgraph "Core Integration"
        AI["ai<br/>v5.0.44<br/>Vercel AI SDK"]
    end
    
    subgraph "Generation Functions"
        GenerateText["generateText()<br/>packages/giselle/src/engine/generations/generate-text.ts"]
        GenerateImage["generateImage()<br/>packages/giselle/src/engine/generations/generate-image.ts"]
        GenerateContent["generateContent()<br/>packages/giselle/src/engine/generations/generate-content.ts"]
    end
    
    AISDK_Provider --> AI
    AISDK_OpenAI --> GenerateText
    AISDK_Anthropic --> GenerateText
    AISDK_GoogleVertex --> GenerateText
    AISDK_Perplexity --> GenerateText
    AISDK_Gateway --> GenerateText
    
    AISDK_OpenAI --> GenerateImage
    AISDK_Google --> GenerateImage
    AISDK_Fal --> GenerateImage
    
    AI --> GenerateText
    AI --> GenerateImage
    AI --> GenerateContent
```

**Sources:**
- [pnpm-lock.yaml:9-41]()
- [packages/giselle/src/engine/generations/generate-text.ts:1-6]()
- [packages/giselle/src/engine/generations/generate-image.ts:1-6]()

## AI SDK Integration

Giselle uses the Vercel AI SDK (`ai` package v5.0.44) as the primary abstraction for interacting with language models. The SDK provides unified interfaces for streaming, tool calling, and multi-modal generation.

### Core Functions

| Function | Purpose | Return Type | Primary Use Case |
|----------|---------|-------------|------------------|
| `streamText()` | Stream text generation with tool support | `UIMessageStream` | Real-time text generation in Studio |
| `generateText()` | Non-streaming text generation | `GenerateTextResult` | Tool execution, batch processing |
| `experimental_generateImage()` | Generate images | `GenerateImageResult` | Image generation nodes |
| `createUIMessageStreamResponse()` | Convert stream to HTTP response | `Response` | HTTP API endpoints |

**Sources:**
- [packages/giselle/src/engine/generations/generate-text.ts:19]()
- [packages/giselle/src/http/router.ts:81-98]()

### Model Instantiation Pattern

```mermaid
graph TB
    Request["Generation Request<br/>QueuedGeneration"]
    
    subgraph "Model Selection"
        LMData["TextGenerationLanguageModelData<br/>{provider, id, configurations}"]
        Gateway["aiGateway flag check"]
        
        DirectPath["Direct Provider SDK"]
        GatewayPath["AI Gateway"]
    end
    
    subgraph "Direct Provider Instantiation"
        OpenAIDirect["openai.responses(modelId)"]
        AnthropicDirect["anthropic(modelId)"]
        GoogleDirect["vertex(modelId)"]
        PerplexityDirect["perplexity(modelId)"]
    end
    
    subgraph "Gateway Instantiation"
        GatewayCreate["createGateway({headers})"]
        GatewayModel["gateway('provider/modelId')"]
    end
    
    subgraph "Stream Configuration"
        StreamText["streamText({<br/>  model,<br/>  providerOptions,<br/>  messages,<br/>  tools<br/>})"]
    end
    
    Request --> LMData
    LMData --> Gateway
    
    Gateway -->|false| DirectPath
    Gateway -->|true| GatewayPath
    
    DirectPath --> OpenAIDirect
    DirectPath --> AnthropicDirect
    DirectPath --> GoogleDirect
    DirectPath --> PerplexityDirect
    
    GatewayPath --> GatewayCreate
    GatewayCreate --> GatewayModel
    
    OpenAIDirect --> StreamText
    AnthropicDirect --> StreamText
    GoogleDirect --> StreamText
    PerplexityDirect --> StreamText
    GatewayModel --> StreamText
```

**Sources:**
- [packages/giselle/src/engine/generations/generate-text.ts:348-400]()
- [packages/giselle/src/engine/generations/generate-content.ts:228-231]()

The `generationModel()` function handles provider-specific model instantiation. When the `aiGateway` flag is enabled, requests are routed through the AI Gateway using the format `"provider/modelId"`, otherwise direct provider SDKs are used.

## Model Selection System

### Model Registry

The `@giselle-sdk/language-model` package maintains a centralized registry of available models with their capabilities and tier restrictions.

```mermaid
graph TB
    subgraph "Model Definition Structure"
        Base["LanguageModelBase<br/>{id, provider, capabilities, tier, configurations}"]
        
        subgraph "Capability Flags (Bitwise)"
            TextGen["Capability.TextGeneration"]
            ImageGen["Capability.ImageGeneration"]
            ImageInput["Capability.ImageFileInput"]
            PDFInput["Capability.PdfFileInput"]
            Reasoning["Capability.Reasoning"]
            SearchGround["Capability.OptionalSearchGrounding"]
        end
        
        subgraph "Access Tiers"
            Free["Tier.free"]
            Pro["Tier.pro"]
        end
    end
    
    subgraph "Provider-Specific Models"
        OpenAIModels["openai.ts<br/>gpt-5, gpt-4o, dalle-3, etc."]
        AnthropicModels["anthropic.ts<br/>claude-3-opus, sonnet, haiku"]
        GoogleModels["google.ts<br/>gemini-2.5-pro, flash"]
        PerplexityModels["perplexity.ts<br/>sonar-reasoning, sonar-pro"]
    end
    
    Registry["languageModels: LanguageModel[]<br/>packages/language-model/src/index.ts"]
    
    Base --> TextGen
    Base --> ImageGen
    Base --> Free
    Base --> Pro
    
    OpenAIModels --> Registry
    AnthropicModels --> Registry
    GoogleModels --> Registry
    PerplexityModels --> Registry
    
    UI["Toolbar Component<br/>Model Selection UI"]
    Registry --> UI
```

**Sources:**
- [packages/language-model/src/base.ts]() (referenced in imports)
- [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:27-29]()

### UI Model Filtering

The toolbar component implements sophisticated filtering based on user tier, provider availability, search query, and capability category.

```mermaid
graph TB
    AllModels["languageModels array"]
    
    subgraph "Filter Pipeline"
        ProviderFilter["Filter by llmProviders<br/>only show enabled providers"]
        SearchFilter["filterModelsBySearch(model, query)<br/>match id or provider"]
        CategoryFilter["filterModelsByCategory(model, category)<br/>Text | Image | All"]
        TierFilter["Check user tier<br/>free users see subset"]
    end
    
    subgraph "UI State"
        SearchQuery["searchQuery: string"]
        SelectedCategory["selectedCategory: 'All' | 'Text' | 'Image'"]
        UserTier["userTier from usageLimits"]
    end
    
    subgraph "Display Groups"
        Recommended["Recommended Models<br/>tier-specific defaults"]
        AllFiltered["All Matching Models"]
    end
    
    AllModels --> ProviderFilter
    ProviderFilter --> SearchFilter
    SearchFilter --> CategoryFilter
    CategoryFilter --> TierFilter
    
    SearchQuery --> SearchFilter
    SelectedCategory --> CategoryFilter
    UserTier --> TierFilter
    UserTier --> Recommended
    
    TierFilter --> AllFiltered
    TierFilter --> Recommended
    
    ProOverlay["Pro Plan Overlay<br/>isProModelForFreeUser()"]
    UserTier --> ProOverlay
```

**Sources:**
- [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:92-127]()
- [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/model-components.tsx]() (referenced in imports)

The filtering logic automatically adjusts the category selector based on search results, selecting "Text" if only text models match, "Image" if only image models match, or "All" if both are present.

## Provider-Specific Features

### Reasoning Configuration

Anthropic's Claude models and OpenAI's o1/o3 models support extended reasoning capabilities with provider-specific configuration.

```mermaid
graph LR
    subgraph "Anthropic Reasoning"
        AnthropicCheck["hasCapability(model, Capability.Reasoning)<br/>AND configurations.reasoningText = true"]
        AnthropicOptions["AnthropicProviderOptions<br/>{thinking: {type: 'enabled', budgetTokens: 4096}}"]
    end
    
    subgraph "OpenAI Reasoning"
        OpenAICheck["hasCapability(model, Capability.Reasoning)"]
        OpenAIOptions["OpenAIResponsesProviderOptions<br/>{textVerbosity, reasoningSummary: 'auto', reasoningEffort}"]
    end
    
    GetProviderOptions["getProviderOptions()<br/>generate-text.ts:402-454"]
    
    AnthropicCheck --> AnthropicOptions
    OpenAICheck --> OpenAIOptions
    
    AnthropicOptions --> GetProviderOptions
    OpenAIOptions --> GetProviderOptions
    
    StreamText["streamText({providerOptions})"]
    GetProviderOptions --> StreamText
```

**Sources:**
- [packages/giselle/src/engine/generations/generate-text.ts:402-454]()
- [packages/giselle/src/engine/generations/generate-content.ts:226]()

Anthropic reasoning uses a fixed budget of 4096 tokens based on Zed's configuration. OpenAI reasoning supports configurable `textVerbosity` and `reasoningEffort` from the model configuration.

### Search Grounding

Multiple providers support search grounding through different tool integrations.

| Provider | Tool Name | Configuration | Capability Check |
|----------|-----------|---------------|------------------|
| OpenAI | `web_search_preview` | `openai.tools.webSearchPreview(config)` | `Capability.OptionalSearchGrounding` |
| Google | `google_search` | `google.tools.googleSearch({})` | `Capability.OptionalSearchGrounding` + `configurations.searchGrounding` |
| Anthropic | `web_search` | `anthropic.tools.webSearch_20250305(config)` | Provider-specific tool |
| Perplexity | Built-in | `search_domain_filter` in provider options | Provider-level configuration |

**Sources:**
- [packages/giselle/src/engine/generations/generate-text.ts:156-198]()
- [packages/giselle/src/engine/generations/generate-content.ts:182-224]()

Search grounding tools are conditionally added to the tool set based on model capabilities and user configuration. Perplexity's search is configured through provider options rather than as a separate tool.

### Tool Execution Limits

OpenAI's newer models (gpt-5, gpt-5-mini, gpt-5-nano) have tool step limits disabled to allow unrestricted agentic behavior.

```typescript
const shouldDisableToolStepLimit =
  operationNode.content.llm.provider === "openai" &&
  ["gpt-5", "gpt-5-mini", "gpt-5-nano"].includes(operationNode.content.llm.id);

const streamTextResult = streamText({
  ...(shouldDisableToolStepLimit
    ? {}
    : { stopWhen: stepCountIs(preparedToolCount + 1) }),
});
```

**Sources:**
- [packages/giselle/src/engine/generations/generate-text.ts:209-224]()

## Tier-Based Access Control

### Model Tier System

Models are classified into `free` and `pro` tiers in the language model registry. The UI enforces these restrictions at the toolbar level.

```mermaid
graph TB
    subgraph "Tier Definition"
        ModelDef["LanguageModel<br/>{tier: 'free' | 'pro'}"]
    end
    
    subgraph "User Context"
        UsageLimits["UsageLimits<br/>{featureTier: Tier}"]
        UserTier["userTier = usageLimits?.featureTier ?? Tier.enum.free"]
    end
    
    subgraph "Tier Checks"
        IsProModel["isProModelForFreeUser(model, userTier)<br/>model.tier === 'pro' && userTier === 'free'"]
        ProOverlay["Pro Plan Overlay Display<br/>'This model is available on Pro plan'"]
    end
    
    subgraph "Recommended Models"
        FreeRec["Free User Recommendations<br/>gpt-5-nano, claude-haiku, gemini-flash-lite"]
        ProRec["Pro User Recommendations<br/>gpt-5, claude-opus, gemini-pro"]
    end
    
    ModelDef --> IsProModel
    UsageLimits --> UserTier
    UserTier --> IsProModel
    
    IsProModel -->|true| ProOverlay
    
    UserTier -->|free| FreeRec
    UserTier -->|pro| ProRec
```

**Sources:**
- [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:130-163]()
- [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/model-components.tsx]() (referenced)

### Recommended Models by Tier

The toolbar displays tier-specific recommended models, ensuring free users see accessible options while pro users see premium models.

**Free Tier Recommendations:**
- OpenAI: `gpt-5-nano`
- Anthropic: `claude-3-5-haiku-20241022`
- Google: `gemini-2.5-flash-lite-preview-06-17`

**Pro Tier Recommendations:**
- OpenAI: `gpt-5`
- Anthropic: `claude-3-opus-20240229`, `claude-3-sonnet-20240229`
- Google: `gemini-2.5-pro-exp-03-25`, `gemini-1.5-pro-latest`, `gemini-1.0-pro`

**Sources:**
- [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:133-163]()

## Usage Calculation System

### Usage Calculator Interface

The `UsageCalculator` interface defines how to calculate usage metrics for different models. Each calculator returns usage data with optional cost information.

```mermaid
graph TB
    Interface["UsageCalculator interface<br/>{calculateUsage(params): UsageResult}"]
    
    subgraph "Usage Result"
        Output["output: number<br/>Primary usage metric"]
        OutputCost["outputCost?: number<br/>Optional cost for output"]
        TotalCost["totalCost?: number<br/>Optional total cost"]
        Unit["unit: 'TOKENS' | 'IMAGES'<br/>Measurement unit"]
    end
    
    subgraph "Image Generation Calculators"
        Pixel["PixelBasedUsageCalculator<br/>Flux models"]
        Count["ImageCountBasedUsageCalculator<br/>Stable Diffusion"]
        OpenAICalc["OpenAIImageGenerationUsageCalculator<br/>gpt-image-1"]
    end
    
    Factory["createUsageCalculator(modelId)<br/>usage-factory.ts"]
    
    Interface --> Output
    Interface --> OutputCost
    Interface --> TotalCost
    Interface --> Unit
    
    Pixel --> Factory
    Count --> Factory
    OpenAICalc --> Factory
```

**Sources:**
- [packages/language-model/src/fal.ts:143-160]()
- [packages/language-model/src/openai-image.ts:92-108]()
- [packages/language-model/src/usage-factory.ts:1-21]()

### Fal Image Generation Usage

Fal models use two different usage calculation strategies depending on the model.

#### Pixel-Based Calculation

Used by Flux models (`flux/schnell`, `flux-pro/v1.1`):

```typescript
class PixelBasedUsageCalculator {
  calculateUsage({ width, height, n }: FalImageGenerationParams) {
    const totalPixels = width * height * n;
    return {
      output: Math.ceil(totalPixels / 1_000_000) * 1_000_000,  // Round up to millions
      unit: "IMAGES" as const,
    };
  }
}
```

**Sources:**
- [packages/language-model/src/fal.ts:143-151]()

#### Image Count-Based Calculation

Used by Stable Diffusion models:

```typescript
class ImageCountBasedUsageCalculator {
  calculateUsage({ n }: { width: number; height: number; n: number }) {
    return {
      output: n,  // Simple count of images
      unit: "IMAGES" as const,
    };
  }
}
```

**Sources:**
- [packages/language-model/src/fal.ts:153-160]()

### OpenAI Image Generation Usage

OpenAI's `gpt-image-1` uses a cost-based calculator with a pricing table by size and quality.

```typescript
class OpenAIImageGenerationUsageCalculator {
  calculateUsage({ width, height, quality }: OpenAIImageGenerationParams) {
    const totalPixels = width * height;
    const price = openAICostTable[quality][getSizeKey(width, height)];
    
    return {
      output: totalPixels,
      outputCost: price ?? 0,
      totalCost: price ?? 0,
      unit: "IMAGES" as const,
    };
  }
}
```

**Pricing Table (USD per image):**

| Quality | 1024x1024 | 1536x1024 | 1024x1536 |
|---------|-----------|-----------|-----------|
| low     | $0.011    | $0.016    | $0.016    |
| medium  | $0.042    | $0.063    | $0.063    |
| high    | $0.167    | $0.250    | $0.250    |
| auto    | $0.042    | $0.063    | $0.063    |

**Note:** The `auto` quality uses medium pricing as a conservative estimate since the actual quality chosen by OpenAI cannot be determined in advance.

**Sources:**
- [packages/language-model/src/openai-image.ts:59-108]()

### Usage Calculator Factory

The `createUsageCalculator()` factory function returns the appropriate calculator instance for a given model ID.

```typescript
const usageCalculatorMap: Record<string, UsageCalculator> = {
  "fal-ai/stable-diffusion-v3-medium": new ImageCountBasedUsageCalculator(),
  "fal-ai/flux/schnell": new PixelBasedUsageCalculator(),
  "fal-ai/flux-pro/v1.1": new PixelBasedUsageCalculator(),
  "gpt-image-1": new OpenAIImageGenerationUsageCalculator(),
};

export function createUsageCalculator(modelId: string): UsageCalculator {
  if (usageCalculatorMap[modelId]) {
    return usageCalculatorMap[modelId];
  }
  throw new Error(`Unknown model: ${modelId}`);
}
```

**Sources:**
- [packages/language-model/src/usage-factory.ts:8-20]()

## Model Provider Utilities

### Image Generation Model Provider Detection

The `getImageGenerationModelProvider()` function extracts the model family from a Fal model ID for provider-specific handling.

```typescript
function getImageGenerationModelProvider(
  provider: string,
): ImageGenerationModelProvider | undefined {
  // Extract model family from model ID
  // E.g., "fal-ai/flux/schnell" -> "flux"
  // E.g., "fal-ai/stable-diffusion-v3-medium" -> "stable-diffusion"
  
  const parts = provider.split("/");
  if (parts.length < 2) return undefined;
  
  if (parts[1] === "flux" || parts[1] === "flux-pro") return "flux";
  if (parts[1].startsWith("recraft")) return "recraft";
  if (parts[1] === "ideogram") return "ideogram";
  if (parts[1].startsWith("stable-diffusion")) return "stable-diffusion";
  
  return undefined;
}
```

**Model Families:**
- `flux` - Flux models (schnell, pro variants)
- `recraft` - Recraft models
- `ideogram` - Ideogram models
- `stable-diffusion` - Stable Diffusion variants

**Sources:**
- [packages/language-model/src/fal.ts:110-135]()
- [packages/language-model/src/fal.test.ts:4-48]()

## AI Gateway Configuration

The AI Gateway provides unified rate limiting, monitoring, and cost tracking across all providers when enabled.

### Gateway Setup

```mermaid
graph TB
    subgraph "Configuration"
        Flag["aiGateway feature flag"]
        Config["aiGateway config<br/>{httpReferer, xTitle}"]
    end
    
    subgraph "Environment Detection"
        VercelEnv["process.env.VERCEL_ENV"]
        PreviewURL["https://${VERCEL_URL}"]
        ProdURL["https://studio.giselles.ai"]
    end
    
    subgraph "Gateway Initialization"
        CreateGateway["createGateway({<br/>  headers: {<br/>    'http-referer': referer,<br/>    'x-title': title<br/>  }<br/>})"]
    end
    
    subgraph "Model Format"
        GatewayModel["gateway('provider/modelId')<br/>e.g., 'openai/gpt-4o'<br/>'anthropic/claude-3-5-sonnet-20240620'"]
    end
    
    Flag --> Config
    VercelEnv --> PreviewURL
    VercelEnv --> ProdURL
    
    Config --> CreateGateway
    ProdURL --> CreateGateway
    PreviewURL --> CreateGateway
    
    CreateGateway --> GatewayModel
```

**Sources:**
- [apps/studio.giselles.ai/app/giselle-engine.ts:352-359]()
- [packages/giselle/src/engine/generations/generate-text.ts:354-378]()

The gateway is configured with environment-specific HTTP referer headers to identify traffic origin (preview vs production). The model specifier format follows the pattern `"provider/modelId"` for gateway routing.

### Gateway vs Direct Provider

```typescript
function generationModel(languageModel, useAiGateway, gatewayOptions) {
  if (useAiGateway) {
    const gateway = createGateway(gatewayOptions ? {
      headers: {
        "http-referer": gatewayOptions.httpReferer,
        "x-title": gatewayOptions.xTitle,
      }
    } : undefined);
    
    return gateway(`${llmProvider}/${languageModel.id}`);
  }
  
  // Direct provider SDKs
  switch (llmProvider) {
    case "anthropic": return anthropic(languageModel.id);
    case "openai": return openai.responses(languageModel.id);
    case "google": return vertex(languageModel.id);
    case "perplexity": return perplexity(languageModel.id);
  }
}
```

**Sources:**
- [packages/giselle/src/engine/generations/generate-text.ts:348-400]()

## Generation Pipeline Integration

### Text Generation Flow

```mermaid
graph TB
    Queue["QueuedGeneration<br/>{context, status: 'queued'}"]
    
    UseExecutor["useGenerationExecutor()<br/>packages/giselle/src/engine/generations/internal/use-generation-executor.ts"]
    
    subgraph "Execution Context Setup"
        Running["RunningGeneration<br/>{status: 'running', startedAt}"]
        UsageLimitCheck["checkUsageLimits()<br/>fetchUsageLimitsFn"]
        MessageBuild["buildMessageObject()<br/>resolve file/text/image inputs"]
        ToolPrep["Prepare tools<br/>GitHub, Postgres, Web Search"]
    end
    
    subgraph "Model & Provider Setup"
        ModelSelect["generationModel(llm, useAiGateway, gatewayOptions)"]
        ProviderOpts["getProviderOptions(llm)<br/>reasoning, search, etc."]
    end
    
    subgraph "Streaming Execution"
        StreamText["streamText({model, providerOptions, messages, tools})"]
        UIStream["toUIMessageStream({sendReasoning: true})"]
    end
    
    subgraph "Completion"
        OnFinish["onFinish callback<br/>extract text, reasoning, sources"]
        Complete["CompletedGeneration<br/>{status: 'completed', outputs, usage}"]
        Callbacks["generationComplete callback<br/>Langfuse tracing"]
    end
    
    Queue --> UseExecutor
    UseExecutor --> Running
    Running --> UsageLimitCheck
    UsageLimitCheck --> MessageBuild
    MessageBuild --> ToolPrep
    
    ToolPrep --> ModelSelect
    ToolPrep --> ProviderOpts
    
    ModelSelect --> StreamText
    ProviderOpts --> StreamText
    
    StreamText --> UIStream
    UIStream --> OnFinish
    OnFinish --> Complete
    Complete --> Callbacks
```

**Sources:**
- [packages/giselle/src/engine/generations/generate-text.ts:37-346]()
- [packages/giselle/src/engine/generations/internal/use-generation-executor.ts:54-395]()

### Image Generation Flow

Image generation follows a similar pattern but uses `experimental_generateImage()` from the AI SDK with provider-specific implementations.

| Provider | SDK Function | Models |
|----------|--------------|--------|
| OpenAI | `openai.image(modelId)` | `dall-e-3`, `dall-e-2` |
| Google | `google.image(modelId)` | `gemini-2.5-flash-image-preview` |
| Fal | `fal.image(modelId)` | Multiple image models |

**Sources:**
- [packages/giselle/src/engine/generations/generate-image.ts:1-350]()
- [packages/language-model/src/google-image.ts:1-41]()

### Batch Generation (Trigger.dev)

For long-running text generation in production (non-studio contexts), the system delegates to Trigger.dev using `generateContent()`.

```mermaid
graph TB
    Check["generateContentProcessor check<br/>VERCEL=1 && NODE_ENV !== 'development'"]
    
    subgraph "Trigger.dev Delegation"
        SetProcess["giselleEngine.setGenerateContentProcess()"]
        TriggerTask["tasks.trigger('generate-content', {generationId, userId, team})"]
    end
    
    subgraph "Task Execution"
        TaskRun["generateContentTask<br/>apps/studio.giselles.ai/trigger/generate-content-task.ts"]
        GetGen["getGeneration(generationId)"]
        GenContent["giselleEngine.generateContent({generation, logger})"]
    end
    
    subgraph "Content Generation"
        UseExec["useGenerationExecutor()<br/>with useResumableGeneration: true"]
        BatchWrite["batchWriter()<br/>chunk streaming to storage"]
        Complete["finishGeneration()<br/>trace + callbacks"]
    end
    
    Check -->|trigger.dev| SetProcess
    SetProcess --> TriggerTask
    TriggerTask --> TaskRun
    
    TaskRun --> GetGen
    GetGen --> GenContent
    GenContent --> UseExec
    UseExec --> BatchWrite
    BatchWrite --> Complete
```

**Sources:**
- [apps/studio.giselles.ai/app/giselle-engine.ts:234-410]()
- [apps/studio.giselles.ai/trigger/generate-content-task.ts:1-100]()
- [packages/giselle/src/engine/generations/generate-content.ts:60-393]()

The `generateContent()` function uses a `batchWriter` to efficiently stream UI message chunks to storage in batches, enabling resumable generation and better handling of long-running tasks.

## Configuration Workflow

### Engine Initialization

```mermaid
sequenceDiagram
    participant App as Application<br/>(studio/playground)
    participant Config as GiselleEngineConfig
    participant Engine as NextGiselleEngine
    participant Context as GiselleEngineContext
    
    App->>Config: Define llmProviders array
    App->>Config: Set aiGateway config
    App->>Config: Set telemetry callbacks
    
    App->>Engine: NextGiselleEngine(config)
    Engine->>Context: Create context with providers
    
    Engine->>App: Return engine instance
    
    Note over App: Engine available via<br/>giselleEngine export
```

**Sources:**
- [apps/studio.giselles.ai/app/giselle-engine.ts:267-362]()
- [apps/playground/giselle-engine.ts:141-160]()

### Workspace Provider Integration

The `WorkspaceProvider` component passes feature flags and configuration to React components, enabling conditional behavior based on enabled features.

```mermaid
graph TB
    Layout["Layout Component<br/>workspaces/[workspaceId]/layout.tsx"]
    
    subgraph "Feature Flags"
        AIGateway["aiGatewayFlag()"]
        ExpStorage["experimental_storageFlag()"]
        Resumable["resumableGenerationFlag()"]
    end
    
    subgraph "WorkspaceProvider Props"
        FFContext["featureFlag: {aiGateway, experimental_storage, resumableGeneration}"]
        TelemetryContext["telemetry: {metadata: {isProPlan, teamType, userId}}"]
        UsageLimitsContext["usageLimits: UsageLimits"]
    end
    
    subgraph "Consumer Components"
        Toolbar["Toolbar<br/>Model filtering by tier"]
        GenRunner["GenerationRunner<br/>Select generate vs generateContent"]
        Editor["Editor<br/>Feature-gated UI elements"]
    end
    
    Layout --> AIGateway
    Layout --> ExpStorage
    Layout --> Resumable
    
    AIGateway --> FFContext
    ExpStorage --> FFContext
    Resumable --> FFContext
    
    FFContext --> Toolbar
    FFContext --> GenRunner
    FFContext --> Editor
    
    TelemetryContext --> GenRunner
    UsageLimitsContext --> Toolbar
```

**Sources:**
- [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:29-145]()
- [packages/giselle/src/react/workspace/provider.tsx:25-67]()
- [apps/playground/app/workspaces/[workspaceId]/layout.tsx:4-20]()

The playground app uses hardcoded feature flags for simplicity, while the studio app dynamically loads flags from Vercel Edge Config based on the environment.

---

# Page: Act Runner and Workflow Orchestration

# Act Runner and Workflow Orchestration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/playground/.gitignore](apps/playground/.gitignore)
- [apps/playground/giselle-engine.ts](apps/playground/giselle-engine.ts)
- [apps/studio.giselles.ai/app/(main)/workspaces/actions.ts](apps/studio.giselles.ai/app/(main)/workspaces/actions.ts)
- [apps/studio.giselles.ai/app/api/workspaces/route.ts](apps/studio.giselles.ai/app/api/workspaces/route.ts)
- [apps/studio.giselles.ai/app/giselle-engine.ts](apps/studio.giselles.ai/app/giselle-engine.ts)
- [apps/studio.giselles.ai/app/stage/(top)/actions.ts](apps/studio.giselles.ai/app/stage/(top)/actions.ts)
- [apps/studio.giselles.ai/app/stage/(top)/circular-carousel.module.css](apps/studio.giselles.ai/app/stage/(top)/circular-carousel.module.css)
- [apps/studio.giselles.ai/app/stage/(top)/circular-carousel.tsx](apps/studio.giselles.ai/app/stage/(top)/circular-carousel.tsx)
- [apps/studio.giselles.ai/app/stage/(top)/form-input-renderer.tsx](apps/studio.giselles.ai/app/stage/(top)/form-input-renderer.tsx)
- [apps/studio.giselles.ai/app/stage/(top)/form.tsx](apps/studio.giselles.ai/app/stage/(top)/form.tsx)
- [apps/studio.giselles.ai/app/stage/(top)/helpers.ts](apps/studio.giselles.ai/app/stage/(top)/helpers.ts)
- [apps/studio.giselles.ai/app/stage/(top)/page.tsx](apps/studio.giselles.ai/app/stage/(top)/page.tsx)
- [apps/studio.giselles.ai/app/stage/(top)/resizable-layout.tsx](apps/studio.giselles.ai/app/stage/(top)/resizable-layout.tsx)
- [apps/studio.giselles.ai/app/stage/(top)/services.ts](apps/studio.giselles.ai/app/stage/(top)/services.ts)
- [apps/studio.giselles.ai/app/stage/(top)/settings-dialog.tsx](apps/studio.giselles.ai/app/stage/(top)/settings-dialog.tsx)
- [apps/studio.giselles.ai/app/stage/(top)/team-card.tsx](apps/studio.giselles.ai/app/stage/(top)/team-card.tsx)
- [apps/studio.giselles.ai/app/stage/(top)/types.ts](apps/studio.giselles.ai/app/stage/(top)/types.ts)
- [apps/studio.giselles.ai/app/stage/acts/[actId]/actions.ts](apps/studio.giselles.ai/app/stage/acts/[actId]/actions.ts)
- [apps/studio.giselles.ai/app/stage/acts/[actId]/lib/data.ts](apps/studio.giselles.ai/app/stage/acts/[actId]/lib/data.ts)
- [apps/studio.giselles.ai/app/stage/acts/[actId]/lib/utils.ts](apps/studio.giselles.ai/app/stage/acts/[actId]/lib/utils.ts)
- [apps/studio.giselles.ai/app/stage/acts/components/filterable-acts-list.tsx](apps/studio.giselles.ai/app/stage/acts/components/filterable-acts-list.tsx)
- [apps/studio.giselles.ai/app/stage/acts/page.tsx](apps/studio.giselles.ai/app/stage/acts/page.tsx)
- [apps/studio.giselles.ai/app/stage/acts/types/index.ts](apps/studio.giselles.ai/app/stage/acts/types/index.ts)
- [apps/studio.giselles.ai/app/stage/layout.tsx](apps/studio.giselles.ai/app/stage/layout.tsx)
- [apps/studio.giselles.ai/app/stage/showcase/[appId]/actions.ts](apps/studio.giselles.ai/app/stage/showcase/[appId]/actions.ts)
- [apps/studio.giselles.ai/app/stage/showcase/[appId]/page.tsx](apps/studio.giselles.ai/app/stage/showcase/[appId]/page.tsx)
- [packages/giselle/src/engine/acts/run-act.ts](packages/giselle/src/engine/acts/run-act.ts)
- [packages/giselle/src/engine/generations/generate-content.ts](packages/giselle/src/engine/generations/generate-content.ts)
- [packages/giselle/src/engine/generations/generate-image.ts](packages/giselle/src/engine/generations/generate-image.ts)
- [packages/giselle/src/engine/generations/internal/use-generation-executor.ts](packages/giselle/src/engine/generations/internal/use-generation-executor.ts)
- [packages/giselle/src/engine/generations/types.ts](packages/giselle/src/engine/generations/types.ts)
- [packages/giselle/src/engine/generations/utils.ts](packages/giselle/src/engine/generations/utils.ts)
- [packages/giselle/src/engine/operations/execute-query.ts](packages/giselle/src/engine/operations/execute-query.ts)
- [packages/giselle/src/engine/telemetry/index.ts](packages/giselle/src/engine/telemetry/index.ts)
- [packages/giselle/src/engine/telemetry/types.ts](packages/giselle/src/engine/telemetry/types.ts)
- [packages/giselle/src/engine/triggers/resolve-trigger.ts](packages/giselle/src/engine/triggers/resolve-trigger.ts)
- [packages/giselle/src/engine/types.ts](packages/giselle/src/engine/types.ts)
- [packages/giselle/src/react/generations/generation-runner.tsx](packages/giselle/src/react/generations/generation-runner.tsx)

</details>



## Purpose and Scope

This document explains how Acts orchestrate multi-step AI workflows in the Giselle Engine. An Act represents a single execution instance of a workflow, managing the sequential and parallel execution of nodes (steps) through sequences, handling state updates via patch queues, and providing lifecycle callbacks for monitoring progress. This page covers the core orchestration logic, while generation-specific execution is detailed in [Generation Pipeline and Lifecycle](#2.2) and engine configuration in [Engine Architecture and Configuration](#2.1).

## Act Concept and Data Model

An Act is the runtime representation of a workflow execution. It contains sequences (ordered groups of steps), each step corresponding to a node generation in the workflow graph.

```mermaid
graph TB
    Act["Act<br/>(Workflow Execution Instance)"]
    Act --> |"contains"| Sequences["Sequences[]<br/>(Ordered Execution Groups)"]
    Sequences --> |"contains"| Steps["Steps[]<br/>(Node Executions)"]
    Steps --> |"references"| Generation["Generation<br/>(Node Output)"]
    
    Act --> |"has"| Status["status<br/>created/inProgress/completed/failed/cancelled"]
    Act --> |"belongs to"| Workspace["workspaceId"]
    Act --> |"triggered by"| Node["nodeId<br/>(Trigger/AppEntry Node)"]
    
    Steps --> |"has"| StepStatus["status<br/>created/running/completed/failed/cancelled"]
    Steps --> |"produces"| GenerationId["generationId"]
```

**Sources:** [packages/giselle/src/engine/acts/run-act.ts:1-25]()

### Act Status Lifecycle

| Status | Description |
|--------|-------------|
| `created` | Act initialized but not started |
| `inProgress` | Act currently executing |
| `completed` | All sequences completed successfully |
| `failed` | At least one step failed |
| `cancelled` | Execution cancelled by user |

**Sources:** [apps/studio.giselles.ai/app/stage/acts/types/index.ts:1-7]()

## Act Creation and Initialization

Acts are created through the `giselleEngine.createAct()` method and started with `giselleEngine.startAct()`. The Stage system provides the primary interface for this workflow.

### Creation Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant Stage as "Stage UI<br/>/stage"
    participant Action as "performStageAction"
    participant Engine as "giselleEngine"
    participant DB as "Database"
    participant Runner as "Act Runner"
    
    User->>Stage: "Select app & fill inputs"
    Stage->>Action: "performStageAction(payloads)"
    
    Action->>Engine: "createAct({workspaceId, nodeId, inputs})"
    Engine->>Engine: "Build sequences from workflow graph"
    Engine->>DB: "Store act metadata"
    Engine-->>Action: "Return act object"
    
    Action->>DB: "Insert act record with team/user"
    Action->>Engine: "startAct({actId})"
    
    alt Self Execution
        Engine->>Runner: "runAct() directly"
    else Trigger.dev
        Engine->>Runner: "jobs.trigger('run-act-job')"
    end
    
    Runner->>Runner: "Execute sequences"
```

**Sources:** [apps/studio.giselles.ai/app/stage/(top)/actions.ts:9-51](), [apps/studio.giselles.ai/app/stage/(top)/page.tsx:1-169]()

### Act Creation Implementation

The `createAct` method builds the execution plan:

```typescript
// From giselleEngine
const { act } = await giselleEngine.createAct({
  workspaceId: trigger.workspaceId,
  nodeId: trigger.nodeId,
  inputs: [
    {
      type: "parameters",
      items: parameterItems
    }
  ],
  generationOriginType: "stage" // or "github-app"
});
```

**Key Components:**
- `workspaceId`: The workflow to execute
- `nodeId`: Entry point node (trigger or appEntry)
- `inputs`: Input data (parameters, webhook events)
- `generationOriginType`: Execution context (`"stage"`, `"studio"`, `"github-app"`)

**Sources:** [apps/studio.giselles.ai/app/stage/(top)/actions.ts:14-24]()

### Starting Act Execution

After creation, the act must be explicitly started:

```typescript
await giselleEngine.startAct({
  actId: act.id,
  generationOriginType: "stage"
});
```

This triggers either direct execution or delegates to Trigger.dev based on configuration.

**Sources:** [apps/studio.giselles.ai/app/stage/(top)/actions.ts:41-44]()

## Execution Architecture

### Processor Selection

The engine supports two execution strategies configured at initialization:

**Self Execution** - Direct invocation within the same process:
```typescript
// Default for local development
const runtimeEnv = getRuntimeEnv(); // "local"
const generateContentProcessor = "self";
```

**External Execution** - Delegated to Trigger.dev for production:
```typescript
// Configured for production
if (process.env.USE_TRIGGER_DEV === "1" || runtimeEnv === "vercel") {
  generateContentProcessor = "trigger.dev";
}
```

**Sources:** [apps/studio.giselles.ai/app/giselle-engine.ts:180-194]()

### Act Runner Process Configuration

```mermaid
graph LR
    StartAct["giselleEngine.startAct()"]
    
    StartAct --> CheckProcessor{"Processor Type?"}
    
    CheckProcessor --> |"self"| DirectRun["runAct()<br/>immediate execution"]
    CheckProcessor --> |"trigger.dev"| TriggerJob["jobs.trigger()<br/>run-act-job"]
    
    DirectRun --> RunActLogic["Run Act Logic"]
    TriggerJob --> TriggerWorker["Trigger.dev Worker"]
    TriggerWorker --> RunActLogic
    
    RunActLogic --> ExecuteSequences["executeAct()"]
```

**Sources:** [apps/studio.giselles.ai/app/giselle-engine.ts:491-533](), [packages/giselle/src/engine/types.ts:42-54]()

### setRunActProcess Configuration

When Trigger.dev is enabled, the engine configures external processing:

```typescript
giselleEngine.setRunActProcess(async ({ act, generationOriginType }) => {
  const requestId = getRequestId();
  
  switch (generationOriginType) {
    case "github-app": {
      const team = await getWorkspaceTeam(act.workspaceId);
      await jobs.trigger<typeof runActJob>("run-act-job", {
        actId: act.id,
        requestId,
        userId: "github-app",
        team: {
          id: team.id,
          subscriptionId: team.activeSubscriptionId,
          plan: team.plan
        }
      });
      break;
    }
    case "stage":
    case "studio": {
      const [currentUser, currentTeam] = await Promise.all([
        fetchCurrentUser(),
        fetchCurrentTeam()
      ]);
      await jobs.trigger<typeof runActJob>("run-act-job", {
        actId: act.id,
        requestId,
        userId: currentUser.id,
        team: { /* team data */ }
      });
      break;
    }
  }
});
```

**Sources:** [apps/studio.giselles.ai/app/giselle-engine.ts:491-533]()

## Sequence and Step Execution

An Act's execution is organized into sequences, with each sequence containing multiple steps that execute in order or in parallel.

### Execution Flow

```mermaid
graph TB
    Start["runAct()"]
    Start --> LoadAct["getAct({actId})"]
    LoadAct --> CreateQueue["createPatchQueue()"]
    CreateQueue --> ExecuteAct["executeAct()"]
    
    ExecuteAct --> ForEachSeq["For each Sequence"]
    ForEachSeq --> SeqStart["onSequenceStart()"]
    SeqStart --> ForEachStep["For each Step"]
    
    ForEachStep --> LoadGen["getGeneration(generationId)"]
    LoadGen --> CheckStatus{"Generation<br/>status?"}
    
    CheckStatus --> |"created"| QueueGen["Create QueuedGeneration"]
    CheckStatus --> |"other"| SkipStep["Skip Step"]
    
    QueueGen --> ExecuteStep["executeStep()"]
    
    ExecuteStep --> CheckType{"Node Type?"}
    CheckType --> |"textGeneration"| TextGen["startContentGeneration()"]
    CheckType --> |"imageGeneration"| ImageGen["generateImage()"]
    CheckType --> |"action"| Action["executeAction()"]
    CheckType --> |"trigger"| Trigger["resolveTrigger()"]
    CheckType --> |"query"| Query["executeQuery()"]
    
    TextGen --> WaitComplete["waitUntilGenerationFinishes()"]
    ImageGen --> OnComplete["onCompleted callback"]
    Action --> OnComplete
    Trigger --> OnComplete
    Query --> OnComplete
    WaitComplete --> OnComplete
    
    OnComplete --> NextStep{"More Steps?"}
    NextStep --> |"yes"| ForEachStep
    NextStep --> |"no"| SeqComplete["onSequenceComplete()"]
    
    SeqComplete --> NextSeq{"More Sequences?"}
    NextSeq --> |"yes"| ForEachSeq
    NextSeq --> |"no"| ActComplete["onActComplete()"]
    
    ActComplete --> FlushQueue["patchQueue.flush()"]
    FlushQueue --> Cleanup["patchQueue.cleanup()"]
    Cleanup --> Done["Done"]
    
    ExecuteStep -.->|"on error"| SeqError["onSequenceError()"]
    SeqError --> NextSeq
```

**Sources:** [packages/giselle/src/engine/acts/run-act.ts:123-200]()

### executeStep Implementation

The `executeStep` function routes to the appropriate operation handler based on node type:

```typescript
async function executeStep(args: {
  context: GiselleEngineContext;
  generation: QueuedGeneration;
  callbacks?: {
    onCompleted?: () => void | Promise<void>;
    onFailed?: (generation: Generation) => void | Promise<void>;
  };
  logger?: GiselleLogger;
  metadata?: GenerationMetadata;
}) {
  try {
    switch (args.generation.context.operationNode.content.type) {
      case "action":
        await executeAction(args);
        break;
      case "imageGeneration":
        await generateImage({ ...args });
        break;
      case "textGeneration": {
        await startContentGeneration(args);
        const finishedGeneration = await waitUntilGenerationFinishes({
          context: args.context,
          generationId: args.generation.id
        });
        if (isFailedGeneration(finishedGeneration)) {
          await args.callbacks?.onFailed?.(finishedGeneration);
        }
        if (isCompletedGeneration(finishedGeneration)) {
          await args.callbacks?.onCompleted?.();
        }
        break;
      }
      case "trigger":
        await resolveTrigger({ context: args.context, generation: args.generation });
        break;
      case "query":
        await executeQuery(args);
        break;
      case "appEntry":
        break; // No execution needed
      default:
        throw new Error(`Unhandled step type`);
    }
    await args.callbacks?.onCompleted?.();
  } catch (_e) {
    await args.callbacks?.onFailed?.(args.generation);
  }
}
```

**Sources:** [packages/giselle/src/engine/acts/run-act.ts:59-113]()

### waitUntilGenerationFinishes

For text generation (which may be processed asynchronously), the runner polls until completion:

```typescript
async function waitUntilGenerationFinishes(args: {
  context: GiselleEngineContext;
  generationId: GenerationId;
}) {
  while (true) {
    const generation = await getGeneration({
      context: args.context,
      generationId: args.generationId
    });
    
    if (!generation) {
      throw new Error(`Generation(id: ${args.generationId}) is not found`);
    }
    
    if (
      generation.status === "completed" ||
      generation.status === "failed" ||
      generation.status === "cancelled"
    ) {
      return generation;
    }
    
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }
}
```

**Sources:** [packages/giselle/src/engine/acts/run-act.ts:26-50]()

## Patch Queue Management

The patch queue system manages concurrent state updates during Act execution, ensuring consistency when multiple steps modify the Act state simultaneously.

### Patch Queue Concept

```mermaid
graph LR
    Step1["Step 1<br/>Execution"]
    Step2["Step 2<br/>Execution"]
    Step3["Step 3<br/>Execution"]
    
    Step1 --> |"queue patch"| PatchQueue["Patch Queue<br/>(Buffer)"]
    Step2 --> |"queue patch"| PatchQueue
    Step3 --> |"queue patch"| PatchQueue
    
    PatchQueue --> |"applyPatches()"| ActState["Act State<br/>(Storage)"]
    
    ActComplete["onActComplete()"] --> Flush["patchQueue.flush()"]
    Flush --> ActState
    Flush --> Cleanup["patchQueue.cleanup()"]
```

**Sources:** [packages/giselle/src/engine/acts/run-act.ts:131-133]()

### Patch Queue Lifecycle

1. **Creation** - A patch queue is created at the start of `runAct()`:
```typescript
const patchQueue = createPatchQueue(args.context);
const applyPatches = patchQueue.createApplyPatches();
```

2. **Usage** - The `applyPatches` function is passed to `executeAct()` which queues updates during step execution

3. **Flushing** - On act completion, all pending patches are applied:
```typescript
await executeAct({
  act,
  applyPatches,
  // ... other args
  onActComplete: async () => {
    await patchQueue.flush();
  }
});
```

4. **Cleanup** - Resources are released after execution:
```typescript
patchQueue.cleanup();
```

**Sources:** [packages/giselle/src/engine/acts/run-act.ts:123-200]()

## Lifecycle Callbacks

The Act runner provides callback hooks for monitoring and reacting to execution events.

### Callback Types

```typescript
export interface RunActCallbacks {
  sequenceStart?: (args: { sequence: Sequence }) => void | Promise<void>;
  sequenceFail?: (args: { sequence: Sequence }) => void | Promise<void>;
  sequenceComplete?: (args: { sequence: Sequence }) => void | Promise<void>;
  sequenceSkip?: (args: { sequence: Sequence }) => void | Promise<void>;
}
```

**Sources:** [packages/giselle/src/engine/acts/run-act.ts:52-57]()

### Callback Invocation Flow

```mermaid
sequenceDiagram
    participant Runner as "Act Runner"
    participant ExecuteAct as "executeAct()"
    participant Callbacks as "RunActCallbacks"
    participant External as "External System<br/>(e.g., Progress Tracking)"
    
    Runner->>ExecuteAct: "Start execution"
    
    loop For each sequence
        ExecuteAct->>Callbacks: "sequenceStart({sequence})"
        Callbacks->>External: "Update progress UI"
        
        alt Sequence succeeds
            ExecuteAct->>Callbacks: "sequenceComplete({sequence})"
            Callbacks->>External: "Mark sequence done"
        else Sequence fails
            ExecuteAct->>Callbacks: "sequenceFail({sequence})"
            Callbacks->>External: "Show error state"
        else Sequence skipped
            ExecuteAct->>Callbacks: "sequenceSkip({sequence})"
            Callbacks->>External: "Skip notification"
        end
    end
    
    ExecuteAct->>Runner: "Execution complete"
```

**Sources:** [packages/giselle/src/engine/acts/run-act.ts:159-186]()

### Callback Implementation Example

In the `runAct` function, callbacks are wired to logging and external handlers:

```typescript
await executeAct({
  act,
  applyPatches,
  startGeneration: async (generationId, callbacks) => { /* ... */ },
  onSequenceStart: async (sequence) => {
    args.context.logger.debug({ sequence }, `Starting sequence ${sequence.id}`);
    await args.callbacks?.sequenceStart?.({ sequence });
  },
  onSequenceError: async (sequence) => {
    args.context.logger.error({ sequence }, `Sequence ${sequence.id} failed`);
    await args.callbacks?.sequenceFail?.({ sequence });
  },
  onSequenceComplete: async (sequence) => {
    args.context.logger.debug({ sequence }, `Sequence ${sequence.id} completed`);
    await args.callbacks?.sequenceComplete?.({ sequence });
  },
  onSequenceSkip: async (sequence) => {
    args.context.logger.debug({ sequence }, `Skipping sequence ${sequence.id}`);
    await args.callbacks?.sequenceSkip?.({ sequence });
  },
  onActComplete: async () => {
    await patchQueue.flush();
  }
});
```

**Sources:** [packages/giselle/src/engine/acts/run-act.ts:159-189]()

## Generation Execution within Acts

Acts coordinate generation execution by maintaining generation indexes and providing context resolution.

### Act-Scoped Generation Lookup

When a step needs data from a previous generation within the same Act, it uses act-scoped lookup:

```mermaid
graph TB
    Step["Current Step<br/>Needs Input"]
    Step --> CheckActId{"Has actId?"}
    
    CheckActId --> |"yes"| ActIndex["Load Act Generation Index"]
    CheckActId --> |"no"| NodeIndex["Load Node Generation Index"]
    
    ActIndex --> FindInAct["Find generation by<br/>nodeId in act context"]
    NodeIndex --> FindLatest["Find latest generation<br/>for nodeId"]
    
    FindInAct --> LoadGen["getGeneration(generationId)"]
    FindLatest --> LoadGen
    
    LoadGen --> UseOutput["Use generation output<br/>as step input"]
```

**Sources:** [packages/giselle/src/engine/generations/internal/use-generation-executor.ts:180-234]()

### Generation Index Paths

The system maintains two index types:

**Node Generation Index** (`/generations/byNode/{nodeId}.json`):
- Lists all generations for a node across all Acts
- Used in studio/playground without Act context

**Act Generation Index** (referenced in code but path varies):
- Lists generations specific to an Act
- Used during Act execution for step-to-step data flow

**Sources:** [packages/giselle/src/engine/generations/internal/use-generation-executor.ts:211-233]()

### Generation Context Resolution

The `useGenerationExecutor` provides resolvers for accessing previous generation outputs:

```typescript
async function generationContentResolver(nodeId: NodeId, outputId: OutputId) {
  const generation = await findGeneration(nodeId);
  if (generation === undefined || !isCompletedGeneration(generation)) {
    return undefined;
  }
  
  const generationOutput = generation.outputs.find(
    (o) => o.outputId === outputId
  );
  
  if (generationOutput === undefined) {
    return undefined;
  }
  
  return formatGenerationOutput(generationOutput);
}
```

**Sources:** [packages/giselle/src/engine/generations/internal/use-generation-executor.ts:245-277]()

## Stage System Integration

The Stage system provides a production interface for Act execution, separate from the workflow designer.

### Stage Components

```mermaid
graph TB
    User["End User"]
    
    User --> StagePage["/stage<br/>Stage Page"]
    StagePage --> FormContainer["FormContainer<br/>App Selection"]
    FormContainer --> FormInputRenderer["FormInputRenderer<br/>Dynamic Inputs"]
    
    FormInputRenderer --> PerformAction["performStageAction"]
    PerformAction --> CreateAct["giselleEngine.createAct()"]
    PerformAction --> InsertDB["db.insert(acts)"]
    PerformAction --> StartAct["giselleEngine.startAct()"]
    
    StartAct --> ActRunner["Act Runner"]
    
    StagePage --> ActsList["Acts List<br/>Recent Executions"]
    ActsList --> ActDetail["/stage/acts/[actId]<br/>Act Detail View"]
```

**Sources:** [apps/studio.giselles.ai/app/stage/(top)/page.tsx:25-169](), [apps/studio.giselles.ai/app/stage/(top)/form.tsx:46-390]()

### Stage Act Creation Flow

The Stage system workflow:

1. **App Selection** - User selects a published application (FlowTrigger) from their team
2. **Input Collection** - Dynamic form renders based on trigger parameters
3. **Validation** - Client-side validation using `parseFormInputs()`
4. **Act Creation** - Server action calls `performStageAction()`
5. **Database Recording** - Act metadata stored with team/user associations
6. **Execution Start** - Act begins processing via configured runner

**Sources:** [apps/studio.giselles.ai/app/stage/(top)/page.tsx:14-45](), [apps/studio.giselles.ai/app/stage/(top)/actions.ts:9-51]()

### Stage Act Tracking

Acts created through Stage are tracked in the database:

```typescript
await db.insert(actsSchema).values({
  teamDbId: team.dbId,
  directorDbId: user.dbId,
  sdkActId: act.id,
  sdkFlowTriggerId: payloads.trigger.id,
  sdkWorkspaceId: payloads.trigger.workspaceId
});
```

This enables:
- **History Views** - `/stage/acts` lists all user's acts
- **Progress Tracking** - Real-time status updates via polling
- **Detail Views** - `/stage/acts/[actId]` shows execution details
- **Team Analytics** - Act usage statistics per team

**Sources:** [apps/studio.giselles.ai/app/stage/(top)/actions.ts:32-39](), [apps/studio.giselles.ai/app/stage/acts/page.tsx:14-147]()

## Act Status Monitoring

### Status Navigation Links

The Stage system creates smart navigation links based on Act status:

```typescript
let link = `/stage/acts/${tmpAct.id}`;
let targetStep = null;

switch (tmpAct.status) {
  case "created":
  case "inProgress":
    targetStep = findStepByStatus("running") ?? getFirstStep();
    break;
  case "completed":
    targetStep = getLastStep();
    break;
  case "cancelled":
    targetStep = findStepByStatus("cancelled");
    break;
  case "failed":
    targetStep = findStepByStatus("failed");
    break;
}

if (targetStep) {
  link += `/${targetStep.id}`;
}
```

This directs users to the most relevant step:
- In-progress Acts → currently running step
- Completed Acts → final step with results
- Failed Acts → step that failed
- Cancelled Acts → step where cancellation occurred

**Sources:** [apps/studio.giselles.ai/app/stage/(top)/services.ts:68-93]()

### Act List Filtering

The Acts page provides comprehensive filtering:

| Filter Type | Description |
|-------------|-------------|
| `is:open` | Non-archived acts (all current acts) |
| `is:archived` | Archived acts (future feature) |
| Status filters | Filter by created/inProgress/completed/failed/cancelled |
| Free text | Search by workspace or team name |

**Sources:** [apps/studio.giselles.ai/app/stage/acts/components/filterable-acts-list.tsx:31-83]()

## Integration with Generation Pipeline

Acts delegate individual node execution to the generation system while maintaining orchestration control.

### Act-Generation Relationship

```mermaid
graph TB
    Act["Act<br/>(Orchestrator)"]
    
    Act --> Seq1["Sequence 1"]
    Act --> Seq2["Sequence 2"]
    
    Seq1 --> Step1["Step 1"]
    Seq1 --> Step2["Step 2"]
    Seq2 --> Step3["Step 3"]
    
    Step1 --> Gen1["Generation 1<br/>status: completed"]
    Step2 --> Gen2["Generation 2<br/>status: running"]
    Step3 --> Gen3["Generation 3<br/>status: created"]
    
    Gen1 --> |"provides output to"| Step2
    Gen2 --> |"provides output to"| Step3
    
    Gen1 --> Storage["Storage<br/>/generations/{id}/"]
    Gen2 --> Storage
    Gen3 --> Storage
```

**Sources:** [packages/giselle/src/engine/acts/run-act.ts:136-158]()

### Generation Metadata in Acts

When Acts execute with external processors (Trigger.dev), generation metadata is passed through:

```typescript
export interface GenerationMetadata {
  [key: string]: string | number | GenerationMetadata | null | undefined;
}

// Example usage in Act execution
await executeStep({
  context: args.context,
  generation: queuedGeneration,
  callbacks,
  metadata: args.metadata // Passed from Act to Generation
});
```

This metadata includes:
- `requestId` - For request tracing
- `userId` - User who initiated the Act
- `team` - Team context (id, subscriptionId, plan)

**Sources:** [packages/giselle/src/engine/acts/run-act.ts:152-157](), [packages/giselle/src/engine/generations/types.ts:8-10]()

## Error Handling and Recovery

### Error Propagation

```mermaid
graph TB
    ExecuteStep["executeStep()"]
    ExecuteStep --> TryCatch{"try/catch"}
    
    TryCatch --> |"success"| OnCompleted["callbacks.onCompleted()"]
    TryCatch --> |"error"| OnFailed["callbacks.onFailed(generation)"]
    
    OnFailed --> SequenceError["onSequenceError(sequence)"]
    SequenceError --> UpdateActStatus["Update Act status to 'failed'"]
    SequenceError --> ContinueOrStop{"Continue<br/>execution?"}
    
    ContinueOrStop --> |"continue"| NextSequence["Execute next sequence"]
    ContinueOrStop --> |"stop"| ActFailed["Act status: 'failed'"]
```

**Sources:** [packages/giselle/src/engine/acts/run-act.ts:59-113](), [packages/giselle/src/engine/acts/run-act.ts:166-172]()

### Execution Error Handling

The `runAct` function wraps execution in error handling:

```typescript
let executionError: Error | null = null;
try {
  await executeAct({
    // ... execution config
  });
} catch (error) {
  executionError = error as Error;
}

patchQueue.cleanup();
if (executionError !== null) {
  console.error("Execution failed:", executionError);
  throw executionError;
}
```

**Sources:** [packages/giselle/src/engine/acts/run-act.ts:134-199]()

## Summary

The Act Runner system provides:

1. **Orchestration** - Coordinates multi-step workflow execution through sequences
2. **State Management** - Patch queue ensures consistent concurrent updates
3. **Lifecycle Tracking** - Callbacks enable external progress monitoring
4. **Flexible Execution** - Supports both direct and external (Trigger.dev) processing
5. **Integration** - Seamlessly connects with generation pipeline and Stage UI
6. **Error Handling** - Graceful failure recovery and status propagation

The system serves as the backbone for workflow execution, bridging user-facing Stage interfaces with the low-level generation execution engine.

---

# Page: Storage and Vault Systems

# Storage and Vault Systems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/playground/giselle-engine.ts](apps/playground/giselle-engine.ts)
- [apps/studio.giselles.ai/app/giselle-engine.ts](apps/studio.giselles.ai/app/giselle-engine.ts)
- [packages/giselle/src/engine/acts/run-act.ts](packages/giselle/src/engine/acts/run-act.ts)
- [packages/giselle/src/engine/generations/generate-content.ts](packages/giselle/src/engine/generations/generate-content.ts)
- [packages/giselle/src/engine/generations/generate-image.ts](packages/giselle/src/engine/generations/generate-image.ts)
- [packages/giselle/src/engine/generations/internal/use-generation-executor.ts](packages/giselle/src/engine/generations/internal/use-generation-executor.ts)
- [packages/giselle/src/engine/generations/types.ts](packages/giselle/src/engine/generations/types.ts)
- [packages/giselle/src/engine/generations/utils.ts](packages/giselle/src/engine/generations/utils.ts)
- [packages/giselle/src/engine/operations/execute-query.ts](packages/giselle/src/engine/operations/execute-query.ts)
- [packages/giselle/src/engine/telemetry/index.ts](packages/giselle/src/engine/telemetry/index.ts)
- [packages/giselle/src/engine/telemetry/types.ts](packages/giselle/src/engine/telemetry/types.ts)
- [packages/giselle/src/engine/triggers/resolve-trigger.ts](packages/giselle/src/engine/triggers/resolve-trigger.ts)
- [packages/giselle/src/engine/types.ts](packages/giselle/src/engine/types.ts)
- [packages/giselle/src/react/generations/generation-runner.tsx](packages/giselle/src/react/generations/generation-runner.tsx)

</details>



This document describes the storage abstraction layer and secret management (vault) system used throughout the Giselle Engine. The storage system provides a unified interface for persisting generation data, files, and indexes across different backend implementations (Supabase S3, local filesystem). The vault system provides secure secret storage and decryption for tool credentials, API keys, and database connection strings.

For information about how storage is used during generation execution, see [Generation Pipeline and Lifecycle](#2.2). For database schema and persistent data models, see [Database Schema and Data Model](#2.6).

---

## Storage System Architecture

The storage system uses an abstraction layer (`GiselleStorage`) that allows the engine to operate with different storage backends without changing application code. The system supports both cloud storage (Supabase S3-compatible) and local filesystem storage.

### Storage Abstraction Interface

The `GiselleStorage` interface defines the contract for all storage operations:

```mermaid
classDiagram
    class GiselleStorage {
        <<interface>>
        +exists(path: string) Promise~boolean~
        +getBlob(path: string) Promise~Uint8Array~
        +setBlob(path: string, blob: Uint8Array) Promise~void~
        +getJson(path, schema) Promise~T~
        +setJson(path, data) Promise~void~
    }
    
    class supabaseStorageDriver {
        +endpoint: string
        +region: string
        +accessKeyId: string
        +secretAccessKey: string
        +bucket: string
        --
        +exists()
        +getBlob()
        +setBlob()
        +getJson()
        +setJson()
    }
    
    class fsStorageDriver {
        +root: string
        --
        +exists()
        +getBlob()
        +setBlob()
        +getJson()
        +setJson()
    }
    
    GiselleStorage <|.. supabaseStorageDriver : implements
    GiselleStorage <|.. fsStorageDriver : implements
```

**Sources:** [packages/giselle/src/engine/types.ts:23](), [packages/giselle/src/engine/storage.ts]() (inferred), [packages/supabase-driver/src/index.ts]() (inferred)

### Storage Driver Implementations

#### Supabase Storage Driver

The `supabaseStorageDriver` provides S3-compatible object storage through Supabase:

| Configuration Field | Type | Description |
|-------------------|------|-------------|
| `endpoint` | `string` | Supabase storage endpoint URL |
| `region` | `string` | Storage region identifier |
| `accessKeyId` | `string` | S3-compatible access key |
| `secretAccessKey` | `string` | S3-compatible secret key |
| `bucket` | `string` | Storage bucket name (typically "app") |

The driver is initialized in the Studio application:

**Sources:** [apps/studio.giselles.ai/app/giselle-engine.ts:40-46]()

#### Filesystem Storage Driver

The `fsStorageDriver` provides local filesystem storage for development:

| Configuration Field | Type | Description |
|-------------------|------|-------------|
| `root` | `string` | Root directory path for storage (e.g., "./.storage") |

The playground application conditionally selects the storage driver based on environment:

**Sources:** [apps/playground/giselle-engine.ts:14-24]()

### Storage Path Organization

The storage system uses a hierarchical path structure to organize different types of data:

```mermaid
graph TB
    Root["Storage Root"]
    
    Generations["generations/"]
    ByNode["byNode/"]
    ByAct["byAct/"]
    GenId["<generationId>/"]
    
    GenJson["generation.json"]
    UiChunks["ui-message-chunks.json"]
    GenImages["generated-images/"]
    
    Files["files/"]
    FileOrg["<workspaceId>/<fileId>"]
    
    Acts["acts/"]
    ActId["<actId>/"]
    ActJson["act.json"]
    ActIdx["act-generation-index.json"]
    
    Triggers["triggers/"]
    TriggerId["<triggerId>/"]
    TriggerJson["trigger.json"]
    
    Root --> Generations
    Root --> Files
    Root --> Acts
    Root --> Triggers
    
    Generations --> ByNode
    Generations --> ByAct
    Generations --> GenId
    
    ByNode --> NodeIndex["<nodeId>.json"]
    ByAct --> ActIndex["<actId>.json"]
    
    GenId --> GenJson
    GenId --> UiChunks
    GenId --> GenImages
    GenImages --> ImageFile["<imageId>.png/jpeg/webp"]
    
    Files --> FileOrg
    
    Acts --> ActId
    ActId --> ActJson
    ActId --> ActIdx
    
    Triggers --> TriggerId
    TriggerId --> TriggerJson
```

**Key Path Functions:**

| Function | Path Pattern | Usage |
|----------|-------------|-------|
| `generationPath` | `generations/{generationId}/generation.json` | Store/retrieve generation metadata |
| `generationUiMessageChunksPath` | `generations/{generationId}/ui-message-chunks.json` | Store streaming UI messages |
| `generatedImagePath` | `generations/{generationId}/generated-images/{filename}` | Store generated images |
| `filePath` | `files/{workspaceId}/{fileId}` | Store uploaded files |
| `nodeGenerationIndexPath` | `generations/byNode/{nodeId}.json` | Index generations by node |
| `actGenerationIndexPath` | `generations/byAct/{actId}.json` | Index generations by act |

**Sources:** [packages/giselle/src/engine/path.ts]() (inferred), [packages/giselle/src/engine/generations/utils.ts:316-318,335-337,612-614](), [packages/giselle/src/engine/files/utils.ts]() (inferred)

---

## Vault System Architecture

The vault system provides secure storage and retrieval of sensitive credentials. It uses encryption at rest and supports multiple backend implementations.

### Vault Abstraction Interface

```mermaid
classDiagram
    class Vault {
        <<interface>>
        +encrypt(plaintext: string) Promise~string~
        +decrypt(ciphertext: string) Promise~string~
    }
    
    class supabaseVaultDriver {
        +url: string
        +serviceKey: string
        --
        Uses pgsodium encryption
        Stores secrets in database
        --
        +encrypt()
        +decrypt()
    }
    
    class nodeVaultDriver {
        +secret: string
        --
        In-memory encryption
        Uses AES-256-GCM
        --
        +encrypt()
        +decrypt()
    }
    
    Vault <|.. supabaseVaultDriver : implements
    Vault <|.. nodeVaultDriver : implements
```

**Sources:** [packages/giselle/src/engine/vault.ts]() (inferred), [packages/supabase-driver/src/vault.ts]() (inferred), [apps/playground/lib/vault-driver.ts]()

### Vault Driver Implementations

#### Supabase Vault Driver

The `supabaseVaultDriver` uses PostgreSQL's pgsodium extension for encryption at rest:

| Configuration Field | Type | Description |
|-------------------|------|-------------|
| `url` | `string` | Supabase project URL |
| `serviceKey` | `string` | Supabase service role key |

The driver stores encrypted secrets in the database with column-level encryption provided by pgsodium.

**Sources:** [apps/studio.giselles.ai/app/giselle-engine.ts:48-51](), [packages/supabase-driver/src/vault.ts]() (inferred)

#### Node Vault Driver

The `nodeVaultDriver` provides in-memory encryption for development environments:

| Configuration Field | Type | Description |
|-------------------|------|-------------|
| `secret` | `string` | Encryption key from `VAULT_SECRET` environment variable |

This driver uses AES-256-GCM encryption and is suitable for local development where database-backed encryption is not available.

**Sources:** [apps/playground/giselle-engine.ts:137-139](), [apps/playground/lib/vault-driver.ts]()

### Vault Integration in Engine Context

The vault is provided to the engine through `GiselleEngineContext`:

```mermaid
graph LR
    EngineInit["NextGiselleEngine initialization"]
    EngineContext["GiselleEngineContext"]
    Vault["Vault instance"]
    
    EngineInit -->|creates| EngineContext
    EngineContext -->|contains| Vault
    
    GenerateContent["generateContent"]
    ExecuteQuery["executeQuery"]
    Tools["Tool execution"]
    
    Vault -->|used by| GenerateContent
    Vault -->|used by| ExecuteQuery
    Vault -->|used by| Tools
```

**Sources:** [packages/giselle/src/engine/types.ts:90-127](), [apps/studio.giselles.ai/app/giselle-engine.ts:196-227]()

---

## Storage Usage Patterns

### Generation Data Storage Flow

The storage system is used throughout the generation lifecycle to persist state and results:

```mermaid
sequenceDiagram
    participant Executor as "useGenerationExecutor"
    participant Storage as "GiselleStorage"
    participant Gen as "Generation Data"
    
    Note over Executor,Storage: Generation Start
    Executor->>Storage: setJson(generationPath, runningGeneration)
    
    Note over Executor,Storage: Streaming Content
    loop For each chunk
        Executor->>Storage: setBlob(uiMessageChunksPath, chunks)
    end
    
    Note over Executor,Storage: Image Generation
    alt Has generated images
        Executor->>Storage: setBlob(generatedImagePath, imageBytes)
    end
    
    Note over Executor,Storage: Completion
    Executor->>Storage: setJson(generationPath, completedGeneration)
    Executor->>Storage: setJson(nodeGenerationIndexPath, index)
    
    Note over Executor,Gen: Later Retrieval
    Gen->>Storage: getJson(generationPath)
    Storage-->>Gen: Generation data
    Gen->>Storage: getBlob(generatedImagePath)
    Storage-->>Gen: Image bytes
```

**Key storage operations during generation:**

1. **Generation metadata**: Stored as JSON at `generations/{generationId}/generation.json`
2. **UI message chunks**: Streamed chunks stored at `generations/{generationId}/ui-message-chunks.json`
3. **Generated images**: Binary blobs stored at `generations/{generationId}/generated-images/{filename}`
4. **Indexes**: Generation lookups by node ID and act ID

**Sources:** [packages/giselle/src/engine/generations/internal/use-generation-executor.ts:96-101,328-398](), [packages/giselle/src/engine/generations/generate-content.ts:414-427](), [packages/giselle/src/engine/generations/generate-image.ts:188-196]()

### File Resolution and Retrieval

The `fileResolver` function provides file data retrieval during generation execution:

```mermaid
graph TB
    FileRef["File Reference in Node"]
    FileId["fileId"]
    ClonedCheck{"Is cloned file?"}
    FileIdMap["fileIdMap"]
    OriginalId["originalFileIdForCopy"]
    ActualId["actualFileId"]
    
    FilePath["filePath(origin, actualFileId)"]
    Storage["storage.getBlob(path)"]
    FileData["Uint8Array file data"]
    
    FileRef --> FileId
    FileId --> ClonedCheck
    ClonedCheck -->|Yes| FileIdMap
    ClonedCheck -->|No| ActualId
    FileIdMap --> OriginalId
    OriginalId --> ActualId
    ActualId --> FilePath
    FilePath --> Storage
    Storage --> FileData
```

**File ID mapping for duplicated nodes:**

When nodes are duplicated, cloned file references point to the original file's storage location. The `fileIdMap` is built during generation execution to map cloned file IDs to their original storage IDs.

**Sources:** [packages/giselle/src/engine/generations/internal/use-generation-executor.ts:144-179](), [packages/giselle/src/engine/files/utils.ts]() (inferred)

### Generated Image Storage

Generated images from text-to-image models are stored as binary blobs:

| Operation | Path | Data Type | Content |
|-----------|------|-----------|---------|
| Write | `generations/{genId}/generated-images/{imageId}.{ext}` | `Uint8Array` | PNG, JPEG, or WebP image bytes |
| Read | Same path | `Uint8Array` | Raw image data for display |

**Image type detection:** The system detects image format by examining header bytes (magic numbers) to determine the correct file extension.

**Sources:** [packages/giselle/src/engine/generations/utils.ts:612-637,640-685](), [packages/giselle/src/engine/generations/generate-image.ts:179-196,263-280,330-357]()

### Generation Index Storage

The system maintains indexes for efficient generation lookup:

```mermaid
graph LR
    subgraph "By Node Index"
        NodeIdx["generations/byNode/{nodeId}.json"]
        NodeGenList["Array of generation IDs"]
        NodeIdx --> NodeGenList
    end
    
    subgraph "By Act Index"
        ActIdx["generations/byAct/{actId}.json"]
        ActGenList["Array of generation IDs + node IDs"]
        ActIdx --> ActGenList
    end
    
    LookupByNode["getNodeGenerationIndexes"]
    LookupByAct["getActGenerationIndexes"]
    
    LookupByNode --> NodeIdx
    LookupByAct --> ActIdx
```

**Index structures:**

- **Node index**: `NodeGenerationIndex[]` - chronological list of all generations for a node
- **Act index**: `ActGenerationIndex[]` - list of generations executed within an act, with node association

**Sources:** [packages/giselle/src/engine/generations/utils.ts:335-350](), [packages/giselle/src/engine/generations/internal/get-act-generation-indexes.ts]() (inferred)

---

## Vault Usage Patterns

### Secret Decryption for Tools

The vault is used to decrypt credentials when tools are executed during generation:

```mermaid
sequenceDiagram
    participant Gen as "generateContent"
    participant Node as "TextGenerationNode"
    participant Vault as "Vault"
    participant Tool as "Tool (GitHub/Postgres)"
    
    Note over Gen,Node: Tool Configuration
    Gen->>Node: Read tool configuration
    
    alt GitHub Tool
        Node->>Node: Check auth.type (pat/secret)
        alt auth.type === "pat"
            Node->>Vault: decrypt(auth.token)
        else auth.type === "secret"
            Node->>Vault: decryptSecret(secretId)
        end
        Vault-->>Node: decrypted PAT
        Node->>Tool: githubTools(octokit(PAT))
    end
    
    alt Postgres Tool
        Node->>Vault: decryptSecret(secretId)
        Vault-->>Node: connection string
        Node->>Tool: createPostgresTools(connectionString)
    end
    
    Tool-->>Gen: toolSet prepared
```

**Credential types stored in vault:**

| Tool | Credential Type | Storage Format |
|------|----------------|----------------|
| GitHub | Personal Access Token | Encrypted string |
| Postgres | Connection string | Encrypted string (contains host, user, password, database) |
| Custom integrations | API keys | Encrypted string |

**Sources:** [packages/giselle/src/engine/generations/generate-content.ts:117-186](), [packages/giselle/src/engine/secrets.ts]() (inferred)

### GitHub Authentication Decryption

Two authentication patterns use vault decryption:

**Pattern 1: Direct PAT decryption**
```typescript
// Tool configuration with direct token reference
const decryptToken = await context.vault?.decrypt(githubTool.auth.token);
```

**Pattern 2: Secret ID lookup**
```typescript
// Tool configuration with secret ID
const decryptToken = await decryptSecret({
    context,
    secretId: githubTool.auth.secretId,
});
```

Both patterns result in a decrypted personal access token used to initialize the GitHub Octokit client.

**Sources:** [packages/giselle/src/engine/generations/generate-content.ts:119-134]()

### Database Connection Decryption

PostgreSQL tool configuration requires decryption of connection strings:

```mermaid
graph TB
    ToolConfig["Postgres Tool Config"]
    SecretId["secretId"]
    DecryptFn["decryptSecret(context, secretId)"]
    Vault["Vault.decrypt()"]
    ConnStr["Connection String"]
    PgClient["PostgreSQL Client"]
    
    ToolConfig --> SecretId
    SecretId --> DecryptFn
    DecryptFn --> Vault
    Vault --> ConnStr
    ConnStr --> PgClient
    
    ConnStrFormat["postgres://user:password@host:port/database"]
    ConnStr -.example.-> ConnStrFormat
```

**Connection string format:** The decrypted string contains all necessary connection parameters in standard PostgreSQL URI format.

**Sources:** [packages/giselle/src/engine/generations/generate-content.ts:154-186]()

---

## Runtime Environment Selection

The storage and vault drivers are selected based on the runtime environment:

### Environment Detection

```mermaid
graph TB
    Init["Engine Initialization"]
    EnvCheck{"Check Environment"}
    
    Init --> EnvCheck
    
    EnvCheck -->|process.env.VERCEL === "1"| Vercel["Vercel Environment"]
    EnvCheck -->|process.env.NODE_ENV === "development"| Local["Local Environment"]
    EnvCheck -->|Other| Production["Production Environment"]
    
    Vercel --> SupabaseStorage["supabaseStorageDriver"]
    Vercel --> SupabaseVault["supabaseVaultDriver"]
    
    Local --> FSStorage["fsStorageDriver"]
    Local --> NodeVault["nodeVaultDriver"]
    
    Production --> SupabaseStorage
    Production --> SupabaseVault
```

**Environment-specific configuration:**

| Environment | Storage Driver | Vault Driver | Configuration Source |
|------------|----------------|--------------|---------------------|
| **Production (Studio)** | `supabaseStorageDriver` | `supabaseVaultDriver` | Environment variables (`SUPABASE_*`) |
| **Development (Local)** | `fsStorageDriver` | `nodeVaultDriver` | Local config (`./.storage`, `VAULT_SECRET`) |
| **Vercel Preview** | `supabaseStorageDriver` | `supabaseVaultDriver` | Environment variables |
| **Playground (Vercel)** | `supabaseStorageDriver` | `nodeVaultDriver` | Mixed configuration |
| **Playground (Local)** | `fsStorageDriver` | `nodeVaultDriver` | Local config |

**Sources:** [apps/studio.giselles.ai/app/giselle-engine.ts:40-51,180-187](), [apps/playground/giselle-engine.ts:12-24,137-139]()

### Driver Configuration Examples

**Studio production configuration:**
```typescript
const storage = experimental_supabaseStorageDriver({
    endpoint: process.env.SUPABASE_STORAGE_URL,
    region: process.env.SUPABASE_STORAGE_REGION,
    accessKeyId: process.env.SUPABASE_STORAGE_ACCESS_KEY_ID,
    secretAccessKey: process.env.SUPABASE_STORAGE_SECRET_ACCESS_KEY,
    bucket: "app",
});

const vault = supabaseVaultDriver({
    url: process.env.SUPABASE_URL,
    serviceKey: process.env.SUPABASE_SERVICE_KEY,
});
```

**Playground local configuration:**
```typescript
const storage = fsStorageDriver({
    root: "./.storage",
});

const vault = nodeVaultDriver({
    secret: process.env.VAULT_SECRET,
});
```

**Sources:** [apps/studio.giselles.ai/app/giselle-engine.ts:40-51](), [apps/playground/giselle-engine.ts:14-24,137-139]()

---

## Storage Access Patterns

### Batch Writing for Streaming Data

The storage system uses batched writes for efficient streaming data persistence:

```mermaid
graph LR
    Stream["UI Message Stream"]
    BatchWriter["batchWriter"]
    Queue["In-memory Queue"]
    Flush["Batch Flush"]
    Storage["storage.setBlob()"]
    
    Stream -->|chunks| BatchWriter
    BatchWriter --> Queue
    Queue -->|on batch size/timeout| Flush
    Flush --> Storage
```

The `batchWriter` utility collects streaming chunks in memory and periodically flushes them to storage, reducing I/O operations.

**Sources:** [packages/giselle/src/engine/generations/generate-content.ts:414-438](), [packages/giselle/src/utils/index.ts]() (inferred)

### Generation Retrieval Pattern

```mermaid
graph TB
    Request["Get Generation"]
    Path["generationPath(generationId)"]
    Storage["storage.getJson(path, schema)"]
    Validate["Zod validation"]
    Context["Parse GenerationContext"]
    Result["Generation object"]
    
    Request --> Path
    Path --> Storage
    Storage --> Validate
    Validate --> Context
    Context --> Result
```

All generation data is validated against Zod schemas when retrieved from storage, ensuring type safety and data integrity.

**Sources:** [packages/giselle/src/engine/generations/utils.ts:320-333]()

---

# Page: Database Schema and Data Model

# Database Schema and Data Model

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/playground/.gitignore](apps/playground/.gitignore)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/configure-sources-dialog.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/configure-sources-dialog.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/data.ts](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/data.ts)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/diagnostic-modal.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/diagnostic-modal.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-embedding-profiles.ts](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-embedding-profiles.ts)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-store-create-dialog.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-store-create-dialog.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-vector-store-list.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-vector-store-list.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/page.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/page.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/layout.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/layout.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/navigation-layout.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/navigation-layout.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/page.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/page.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-list.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-list.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-registration-dialog.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-registration-dialog.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/sidebar-menu.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/sidebar-menu.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/types.ts](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/types.ts)
- [apps/studio.giselles.ai/app/(main)/workspaces/actions.ts](apps/studio.giselles.ai/app/(main)/workspaces/actions.ts)
- [apps/studio.giselles.ai/app/api/workspaces/route.ts](apps/studio.giselles.ai/app/api/workspaces/route.ts)
- [apps/studio.giselles.ai/app/stage/(top)/actions.ts](apps/studio.giselles.ai/app/stage/(top)/actions.ts)
- [apps/studio.giselles.ai/app/stage/(top)/circular-carousel.module.css](apps/studio.giselles.ai/app/stage/(top)/circular-carousel.module.css)
- [apps/studio.giselles.ai/app/stage/(top)/circular-carousel.tsx](apps/studio.giselles.ai/app/stage/(top)/circular-carousel.tsx)
- [apps/studio.giselles.ai/app/stage/(top)/form-input-renderer.tsx](apps/studio.giselles.ai/app/stage/(top)/form-input-renderer.tsx)
- [apps/studio.giselles.ai/app/stage/(top)/form.tsx](apps/studio.giselles.ai/app/stage/(top)/form.tsx)
- [apps/studio.giselles.ai/app/stage/(top)/helpers.ts](apps/studio.giselles.ai/app/stage/(top)/helpers.ts)
- [apps/studio.giselles.ai/app/stage/(top)/page.tsx](apps/studio.giselles.ai/app/stage/(top)/page.tsx)
- [apps/studio.giselles.ai/app/stage/(top)/resizable-layout.tsx](apps/studio.giselles.ai/app/stage/(top)/resizable-layout.tsx)
- [apps/studio.giselles.ai/app/stage/(top)/services.ts](apps/studio.giselles.ai/app/stage/(top)/services.ts)
- [apps/studio.giselles.ai/app/stage/(top)/settings-dialog.tsx](apps/studio.giselles.ai/app/stage/(top)/settings-dialog.tsx)
- [apps/studio.giselles.ai/app/stage/(top)/team-card.tsx](apps/studio.giselles.ai/app/stage/(top)/team-card.tsx)
- [apps/studio.giselles.ai/app/stage/(top)/types.ts](apps/studio.giselles.ai/app/stage/(top)/types.ts)
- [apps/studio.giselles.ai/app/stage/acts/[actId]/actions.ts](apps/studio.giselles.ai/app/stage/acts/[actId]/actions.ts)
- [apps/studio.giselles.ai/app/stage/acts/[actId]/lib/data.ts](apps/studio.giselles.ai/app/stage/acts/[actId]/lib/data.ts)
- [apps/studio.giselles.ai/app/stage/acts/[actId]/lib/utils.ts](apps/studio.giselles.ai/app/stage/acts/[actId]/lib/utils.ts)
- [apps/studio.giselles.ai/app/stage/acts/components/filterable-acts-list.tsx](apps/studio.giselles.ai/app/stage/acts/components/filterable-acts-list.tsx)
- [apps/studio.giselles.ai/app/stage/acts/page.tsx](apps/studio.giselles.ai/app/stage/acts/page.tsx)
- [apps/studio.giselles.ai/app/stage/acts/types/index.ts](apps/studio.giselles.ai/app/stage/acts/types/index.ts)
- [apps/studio.giselles.ai/app/stage/layout.tsx](apps/studio.giselles.ai/app/stage/layout.tsx)
- [apps/studio.giselles.ai/app/stage/showcase/[appId]/actions.ts](apps/studio.giselles.ai/app/stage/showcase/[appId]/actions.ts)
- [apps/studio.giselles.ai/app/stage/showcase/[appId]/page.tsx](apps/studio.giselles.ai/app/stage/showcase/[appId]/page.tsx)
- [internal-packages/ui/components/form-field.tsx](internal-packages/ui/components/form-field.tsx)
- [internal-packages/ui/components/section-header.tsx](internal-packages/ui/components/section-header.tsx)
- [internal-packages/ui/components/status-indicator.tsx](internal-packages/ui/components/status-indicator.tsx)

</details>



## Purpose and Scope

This document describes the database schema and data model used throughout the Giselle AI platform. It covers the core tables for team management, workflow execution, and vector store systems, as well as the relationships between these entities. The schema supports multi-tenant operations, workflow execution tracking, and RAG capabilities through vector embeddings.

For information about how the engine interacts with this data model, see [Engine Architecture and Configuration](#2.1). For vector store management interfaces, see [Vector Store Management](#3.2). For workflow execution lifecycle, see [Act Runner and Workflow Orchestration](#2.4).

## Database Technology Stack

The Giselle platform uses the following database technologies:

| Technology | Purpose |
|------------|---------|
| PostgreSQL | Primary relational database |
| pgvector | Vector similarity search extension |
| Drizzle ORM | Type-safe database client and query builder |
| Supabase | Database hosting, authentication, and storage |
| pgsodium | Encryption for sensitive data (vault) |

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:1-55]()

## Core Entity Relationship Diagram

```mermaid
erDiagram
    teams ||--o{ workspaces : "owns"
    teams ||--o{ acts : "owns"
    teams ||--o{ flowTriggers : "has"
    teams ||--o{ githubRepositoryIndex : "has"
    teams ||--o{ documentVectorStores : "has"
    teams ||--o{ agents : "owns"
    
    users ||--o{ supabaseUserMappings : "maps_to"
    users ||--o{ acts : "directs"
    
    workspaces ||--o{ flowTriggers : "contains"
    workspaces ||--o{ acts : "executes_in"
    
    flowTriggers ||--o{ acts : "triggers"
    
    githubRepositoryIndex ||--o{ githubRepositoryContentStatus : "has"
    githubRepositoryIndex ||--o{ githubRepositoryEmbeddingProfiles : "has"
    
    documentVectorStores ||--o{ documentVectorStoreSources : "contains"
    documentVectorStores ||--o{ documentEmbeddingProfiles : "uses"
    
    githubRepositoryContentStatus }o--|| githubRepositoryEmbeddingProfiles : "per_profile"
    
    agents ||--o{ agentActivities : "tracks"
```

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:107-251](), [apps/studio.giselles.ai/app/stage/(top)/services.ts:1-135](), [apps/studio.giselles.ai/app/stage/showcase/[appId]/page.tsx:1-210]()

## Team and User Management Schema

### Teams Table

The `teams` table represents organizations or workspaces within the platform. Each team has:

| Column | Type | Purpose |
|--------|------|---------|
| `dbId` | integer | Internal database ID (primary key) |
| `id` | string | External team identifier (`tm_*`) |
| `name` | string | Team display name |
| `plan` | enum | Subscription plan (free, pro, team, enterprise, internal) |
| `avatarUrl` | string | Team avatar image URL |

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:161-166](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-list.tsx:184-194]()

### Users and Authentication

```mermaid
erDiagram
    users ||--|| supabaseUserMappings : "maps_to"
    users {
        int dbId PK
        string id "user_*"
        timestamp createdAt
        timestamp updatedAt
    }
    supabaseUserMappings {
        int userDbId FK
        string supabaseUserId
    }
```

The `supabaseUserMappings` table bridges Supabase authentication with internal user records, enabling OAuth-based authentication while maintaining internal user identities.

Sources: [apps/studio.giselles.ai/app/stage/showcase/[appId]/page.tsx:88-96]()

## Workflow and Execution Schema

### Flow Triggers Table

The `flowTriggers` table stores published workflow entry points:

| Column | Type | Purpose |
|--------|------|---------|
| `dbId` | integer | Internal database ID |
| `teamDbId` | integer | Owning team (FK) |
| `sdkWorkspaceId` | string | Associated workspace ID |
| `sdkFlowTriggerId` | string | SDK trigger identifier |
| `updatedAt` | timestamp | Last update time |

Flow triggers represent configured trigger nodes in workspaces that can be invoked to start workflow executions. The system filters triggers by team and supports various filter types (all, latest, history, favorites).

Sources: [apps/studio.giselles.ai/app/stage/(top)/services.ts:137-233](), [apps/studio.giselles.ai/app/stage/(top)/page.tsx:41-55]()

### Acts Table (Execution Tracking)

The `acts` table tracks individual workflow executions:

| Column | Type | Purpose |
|--------|------|---------|
| `dbId` | integer | Internal database ID |
| `teamDbId` | integer | Team context (FK) |
| `directorDbId` | integer | User who initiated (FK) |
| `sdkActId` | string | Engine act identifier |
| `sdkFlowTriggerId` | string | Trigger that started this act |
| `sdkWorkspaceId` | string | Workspace being executed |
| `createdAt` | timestamp | Execution start time |

Each act represents a single workflow execution initiated either from the Stage interface or via GitHub triggers. The table maintains the relationship between the user-facing database layer and the engine's internal act representation.

Sources: [apps/studio.giselles.ai/app/stage/(top)/actions.ts:1-51](), [apps/studio.giselles.ai/app/stage/acts/page.tsx:4-147]()

### Act Status and Navigation

```mermaid
graph TB
    ActRecord["acts table record"] -->|"sdkActId"| EngineAct["Engine Act object"]
    EngineAct -->|"contains"| Sequences["sequences[]"]
    Sequences -->|"contains"| Steps["steps[]"]
    Steps -->|"has"| Status["status: created|running|completed|failed|cancelled"]
    
    ActRecord -->|"teamDbId"| Team["teams.dbId"]
    ActRecord -->|"directorDbId"| User["users.dbId"]
    ActRecord -->|"sdkWorkspaceId"| Workspace["Workspace object"]
    
    Navigation["Navigation link"] -->|"computed from"| Status
    Navigation -->|"points to"| StepId["specific step ID"]
```

The system computes navigation links to acts by examining the step statuses within sequences and routing to the appropriate step based on execution state.

Sources: [apps/studio.giselles.ai/app/stage/acts/page.tsx:15-115](), [apps/studio.giselles.ai/app/stage/(top)/services.ts:13-104]()

### Agents Table

The `agents` table stores AI agent configurations:

| Column | Type | Purpose |
|--------|------|---------|
| `dbId` | integer | Internal database ID |
| `id` | string | Agent identifier |
| `teamDbId` | integer | Owning team (FK) |
| `name` | string | Agent display name |
| `description` | string | Agent description |
| `creatorDbId` | integer | Creating user (FK) |
| `workspaceId` | string | Associated workspace |
| `updatedAt` | timestamp | Last update time |

The `agentActivities` table tracks usage metrics for agents:

| Column | Type | Purpose |
|--------|------|---------|
| `agentDbId` | integer | Agent reference (FK) |
| `userDbId` | integer | User who used agent (FK) |
| `activityAt` | timestamp | Activity timestamp |

Sources: [apps/studio.giselles.ai/app/stage/showcase/[appId]/page.tsx:98-133]()

## Vector Store Schema

### GitHub Vector Store System

The GitHub vector store system uses three interconnected tables to manage repository indexing with multiple embedding profiles and content types:

```mermaid
erDiagram
    githubRepositoryIndex ||--o{ githubRepositoryContentStatus : "tracks"
    githubRepositoryIndex ||--o{ githubRepositoryEmbeddingProfiles : "uses"
    githubRepositoryContentStatus }o--|| githubRepositoryEmbeddingProfiles : "per_profile_per_content"
    
    githubRepositoryIndex {
        int dbId PK
        string id "gthbi_*"
        int teamDbId FK
        string owner
        string repo
        int installationId
    }
    
    githubRepositoryEmbeddingProfiles {
        int repositoryIndexDbId FK
        int embeddingProfileId
        timestamp createdAt
    }
    
    githubRepositoryContentStatus {
        int repositoryIndexDbId FK
        int embeddingProfileId FK
        string contentType "blob|issue|pull_request"
        boolean enabled
        string status "idle|running|completed|failed"
        string errorCode
        timestamp retryAfter
        timestamp lastSyncedAt
        jsonb metadata
    }
```

#### GitHub Repository Index Table

The `githubRepositoryIndex` table is the primary record for registered repositories:

| Column | Type | Purpose |
|--------|------|---------|
| `id` | string | External identifier (`gthbi_*`) |
| `owner` | string | GitHub repository owner |
| `repo` | string | GitHub repository name |
| `teamDbId` | integer | Owning team (FK) |
| `installationId` | integer | GitHub App installation ID |

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:203-212]()

#### Content Status Granularity

The `githubRepositoryContentStatus` table provides fine-grained tracking for each combination of:
- Repository
- Embedding profile (OpenAI Small, OpenAI Large, Google, Cohere)
- Content type (blob/code, issue, pull_request)

This design enables:
1. **Per-profile ingestion tracking**: Each embedding model can have different ingestion states for the same content
2. **Per-content-type control**: Code, issues, and PRs can be enabled/disabled independently
3. **Granular retry logic**: Failed ingestions can be retried after exponential backoff per content type

| Column | Type | Purpose |
|--------|------|---------|
| `repositoryIndexDbId` | integer | Repository reference (FK) |
| `embeddingProfileId` | integer | Embedding profile (1=OpenAI Small, 2=OpenAI Large, 3=Google, 4=Cohere) |
| `contentType` | enum | Content category (blob, issue, pull_request) |
| `enabled` | boolean | Whether ingestion is active |
| `status` | enum | Current state (idle, running, completed, failed) |
| `errorCode` | string | Error identifier if failed |
| `retryAfter` | timestamp | When retry is allowed after failure |
| `lastSyncedAt` | timestamp | Last successful sync |
| `metadata` | jsonb | Type-specific metadata (commit SHA, issue number, PR number) |

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:25-27](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:222-232]()

#### Embedding Profile Management

The `githubRepositoryEmbeddingProfiles` table establishes which embedding models are active for a repository:

```mermaid
graph LR
    Repo["Repository Index"] -->|"has multiple"| Profile1["Embedding Profile 1<br/>OpenAI Small"]
    Repo -->|"has multiple"| Profile2["Embedding Profile 2<br/>OpenAI Large"]
    Repo -->|"has multiple"| Profile3["Embedding Profile 3<br/>Google"]
    
    Profile1 -->|"generates statuses for"| Code1["blob status"]
    Profile1 -->|"generates statuses for"| Issue1["issue status"]
    Profile1 -->|"generates statuses for"| PR1["pull_request status"]
    
    Profile2 -->|"generates statuses for"| Code2["blob status"]
    Profile2 -->|"generates statuses for"| Issue2["issue status"]
    Profile2 -->|"generates statuses for"| PR2["pull_request status"]
```

When profiles are added or removed, the system synchronizes content statuses automatically. The compound primary key `(repositoryIndexDbId, embeddingProfileId)` ensures each profile is registered once per repository.

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:214-221](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-registration-dialog.tsx:47-58]()

### Document Vector Store System

The document vector store system manages uploaded documents with similar multi-profile architecture:

```mermaid
erDiagram
    documentVectorStores ||--o{ documentVectorStoreSources : "contains"
    documentVectorStores ||--o{ documentEmbeddingProfiles : "uses"
    
    documentVectorStores {
        int dbId PK
        string id "dvs_*"
        int teamDbId FK
        string name
        timestamp createdAt
        timestamp updatedAt
    }
    
    documentVectorStoreSources {
        int dbId PK
        string id
        int documentVectorStoreDbId FK
        string fileName
        string storageBucket
        string storageKey
        string ingestStatus "idle|running|completed|failed"
        string ingestErrorCode
        timestamp createdAt
    }
    
    documentEmbeddingProfiles {
        int documentVectorStoreDbId FK
        int embeddingProfileId
        timestamp createdAt
    }
```

#### Document Vector Stores Table

| Column | Type | Purpose |
|--------|------|---------|
| `id` | string | External identifier (`dvs_*`) |
| `teamDbId` | integer | Owning team (FK) |
| `name` | string | User-defined store name |

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:659-666]()

#### Document Sources Table

The `documentVectorStoreSources` table tracks individual uploaded files:

| Column | Type | Purpose |
|--------|------|---------|
| `id` | string | Source identifier |
| `documentVectorStoreDbId` | integer | Parent store (FK) |
| `fileName` | string | Original file name |
| `storageBucket` | string | Supabase storage bucket |
| `storageKey` | string | Storage path/key |
| `ingestStatus` | enum | Processing state |
| `ingestErrorCode` | string | Error identifier if failed |

Files are stored in Supabase storage under the path pattern `vector-stores/{dvs_id}/{file}` and referenced by the `storageKey` column.

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:803-812](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx:286-295]()

#### Document Embedding Profiles

Similar to GitHub stores, document stores support multiple embedding profiles simultaneously. The `documentEmbeddingProfiles` table uses a compound key `(documentVectorStoreDbId, embeddingProfileId)` to prevent duplicates.

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:668-683]()

## Status Tracking and State Machines

### Content Status State Machine

The vector store ingestion system uses a state machine for tracking processing status:

```mermaid
stateDiagram-v2
    [*] --> idle: Initial state
    idle --> running: Manual ingest or scheduled sync
    running --> completed: Success
    running --> failed: Error occurs
    failed --> idle: After retry period expires
    completed --> idle: Re-ingest triggered
    running --> running: Progress updates (stale after 15min)
```

**Status values:**
- `idle`: Ready for ingestion, not currently processing
- `running`: Actively ingesting content
- `completed`: Successfully ingested and indexed
- `failed`: Error occurred, retry after backoff period

The system considers a `running` status "stale" if `updatedAt` is older than 15 minutes, allowing forced re-ingestion.

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:928-973]()

### Ingestability Logic

The system determines whether a repository can be manually ingested based on content status:

```mermaid
graph TD
    Start["Check ingestability"] --> HasBlob{"Has blob<br/>content status?"}
    HasBlob -->|No| Reject1["Cannot ingest:<br/>Missing blob status"]
    HasBlob -->|Yes| CheckEnabled["For each enabled content type"]
    
    CheckEnabled --> IsIdle{"Status is idle<br/>or completed?"}
    IsIdle -->|Yes| Allow["Can ingest"]
    IsIdle -->|No| IsStale{"Status is running<br/>but stale >15min?"}
    IsStale -->|Yes| Allow
    IsStale -->|No| IsFailed{"Status is failed<br/>and retryAfter expired?"}
    IsFailed -->|Yes| Allow
    IsFailed -->|No| Reject2["Cannot ingest:<br/>Blocked by content type"]
    
    Reject2 --> End["Return reason"]
    Reject1 --> End
    Allow --> End
```

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:103-114](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:929-973]()

### Error Handling and Retry

When ingestion fails, the system:
1. Sets `status = 'failed'`
2. Records `errorCode` (e.g., `DOCUMENT_NOT_FOUND`, `DOCUMENT_FETCH_ERROR`, `DOCUMENT_RATE_LIMITED`, `DOCUMENT_TOO_LARGE`)
3. Sets `retryAfter` timestamp for exponential backoff
4. Prevents manual ingestion until retry period expires

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/types.ts:1-6](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:363-373]()

## Data Access Patterns

### Multi-Tenancy Enforcement

All vector store queries enforce team isolation through foreign key constraints and query filters:

```typescript
// Example: Team-scoped repository query
await db
  .select()
  .from(githubRepositoryIndex)
  .where(
    and(
      eq(githubRepositoryIndex.teamDbId, team.dbId),
      eq(githubRepositoryIndex.id, indexId)
    )
  )
```

This pattern appears consistently across all team-owned resources (acts, vector stores, agents).

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:287-296]()

### Quota Enforcement with Row Locking

Vector store creation enforces quotas using row-level locking to prevent race conditions:

```mermaid
sequenceDiagram
    participant Client
    participant Transaction
    participant TeamsTable
    participant IndexTable
    
    Client->>Transaction: Begin transaction
    Transaction->>TeamsTable: SELECT ... FOR UPDATE<br/>(lock team row)
    Transaction->>IndexTable: SELECT COUNT(*) ... FOR UPDATE<br/>(lock existing indexes)
    Transaction->>Transaction: Check count < quota.maxStores
    alt Quota available
        Transaction->>IndexTable: INSERT new index
        Transaction->>Client: Commit
    else Quota exceeded
        Transaction->>Client: Rollback with error
    end
```

The `FOR UPDATE` lock on the team row serializes quota checks, preventing concurrent insertions from exceeding limits.

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:159-201](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:643-657]()

### Compound Status Queries

Retrieving repository data with all content statuses requires joining multiple tables:

```typescript
// Fetch repository with all content statuses
const records = await db
  .select({
    repositoryIndex: githubRepositoryIndex,
    contentStatus: githubRepositoryContentStatus
  })
  .from(githubRepositoryIndex)
  .leftJoin(
    githubRepositoryContentStatus,
    eq(githubRepositoryContentStatus.repositoryIndexDbId, githubRepositoryIndex.dbId)
  )
  .where(eq(githubRepositoryIndex.teamDbId, team.dbId))
```

The result is then grouped by repository to produce the `RepositoryWithStatuses` structure used throughout the UI.

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/data.ts:13-56]()

### Cascading Deletes

When deleting vector stores, the system:
1. Deletes embedding profiles (cascade via FK)
2. Deletes content statuses (cascade via FK)
3. Deletes document sources (explicit deletion)
4. Schedules async storage cleanup (uses Next.js `after()`)

```mermaid
graph TD
    DeleteStore["Delete documentVectorStores"] --> DeleteProfiles["CASCADE DELETE<br/>documentEmbeddingProfiles"]
    DeleteStore --> DeleteSources["DELETE<br/>documentVectorStoreSources"]
    DeleteSources --> QueueCleanup["Queue async cleanup<br/>with after()"]
    QueueCleanup --> CleanupStorage["Delete files from<br/>Supabase storage"]
```

The storage cleanup happens asynchronously to avoid blocking the database transaction.

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:778-891]()

## Embedding Profile Configuration

### Supported Embedding Models

The platform supports multiple embedding profiles identified by numeric IDs:

| ID | Name | Provider | Dimensions | Notes |
|----|------|----------|------------|-------|
| 1 | OpenAI Small | OpenAI | 1536 | Default, text-embedding-3-small |
| 2 | OpenAI Large | OpenAI | 3072 | text-embedding-3-large |
| 3 | Google | Google | 768 | text-embedding-004 |
| 4 | Cohere | Cohere | 1024 | Legacy, not selectable in UI |

The `DEFAULT_EMBEDDING_PROFILE_ID` is `1` (OpenAI Small).

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-registration-dialog.tsx:16-17](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx:336-355]()

### Profile Selection UI

Users can select multiple profiles when registering repositories or creating document stores. The UI enforces that at least one profile must remain selected to prevent invalid configurations.

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-registration-dialog.tsx:378-433]()

## Storage Integration

### Supabase Storage Structure

Document files are stored in Supabase storage with the following structure:

```
bucket: {storageBucket}
├── vector-stores/
│   ├── {dvs_id}/
│   │   ├── {file1}
│   │   ├── {file2}
│   │   └── ...
```

The `documentVectorStoreSources.storageKey` contains the full path: `vector-stores/{dvs_id}/{filename}`.

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:55-56](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:844-857]()

### Storage Cleanup on Deletion

When a document vector store is deleted, the system:
1. Collects all storage keys from `documentVectorStoreSources`
2. Deletes database records in a transaction
3. Asynchronously removes files from storage buckets
4. Groups deletions by bucket to minimize API calls

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:842-880]()

## pgvector Integration

While not explicitly shown in the provided files, the database uses the pgvector extension for storing and querying vector embeddings. The embeddings are generated during ingestion and stored in vector columns, enabling similarity search for RAG queries.

The schema supports multiple embedding profiles per content, allowing the same document or code to be indexed with different embedding models simultaneously. This enables experimentation with different models and fallback options.

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:1-55]()

---

# Page: Tool System and External Integrations

# Tool System and External Integrations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/playground/giselle-engine.ts](apps/playground/giselle-engine.ts)
- [apps/studio.giselles.ai/app/giselle-engine.ts](apps/studio.giselles.ai/app/giselle-engine.ts)
- [packages/giselle/src/engine/acts/run-act.ts](packages/giselle/src/engine/acts/run-act.ts)
- [packages/giselle/src/engine/generations/generate-content.ts](packages/giselle/src/engine/generations/generate-content.ts)
- [packages/giselle/src/engine/generations/generate-image.ts](packages/giselle/src/engine/generations/generate-image.ts)
- [packages/giselle/src/engine/generations/internal/use-generation-executor.ts](packages/giselle/src/engine/generations/internal/use-generation-executor.ts)
- [packages/giselle/src/engine/generations/types.ts](packages/giselle/src/engine/generations/types.ts)
- [packages/giselle/src/engine/generations/utils.ts](packages/giselle/src/engine/generations/utils.ts)
- [packages/giselle/src/engine/operations/execute-query.ts](packages/giselle/src/engine/operations/execute-query.ts)
- [packages/giselle/src/engine/telemetry/index.ts](packages/giselle/src/engine/telemetry/index.ts)
- [packages/giselle/src/engine/telemetry/types.ts](packages/giselle/src/engine/telemetry/types.ts)
- [packages/giselle/src/engine/triggers/resolve-trigger.ts](packages/giselle/src/engine/triggers/resolve-trigger.ts)
- [packages/giselle/src/engine/types.ts](packages/giselle/src/engine/types.ts)
- [packages/giselle/src/react/generations/generation-runner.tsx](packages/giselle/src/react/generations/generation-runner.tsx)

</details>



This document describes the tool system that enables LLM operations to interact with external services and data sources. Tools are dynamically prepared and injected into text generation calls based on node configuration, allowing AI models to access GitHub repositories, execute database queries, and perform web searches.

For information about vector stores and RAG query execution, see [RAG Implementation and Query Execution](#3.3). For LLM provider configuration and model selection, see [Language Models and AI Providers](#2.3).

## Purpose and Architecture

The tool system provides a plugin-like mechanism for extending LLM capabilities with external integrations. Tools are prepared at generation time by examining the operation node's configuration, authenticating with external services, and building a tool set that is passed to the AI SDK's `streamText()` function.

The system supports three categories of tools:
- **GitHub tools**: Repository file access, issue management, pull request operations
- **Postgres tools**: Database query execution
- **Web search tools**: Provider-specific search and grounding capabilities

### Tool Lifecycle Overview

```mermaid
graph TB
    subgraph "Node Configuration"
        NodeConfig["TextGenerationNode.content.tools"]
        GitHubConfig["tools.github"]
        PostgresConfig["tools.postgres"]
        SearchConfig["tools.openaiWebSearch<br/>tools.anthropicWebSearch<br/>llm.configurations.searchGrounding"]
    end
    
    subgraph "Tool Preparation Phase"
        PrepareTools["useGenerationExecutor"]
        AuthCheck["Authenticate with Vault/Secret"]
        BuildToolSet["Build PreparedToolSet"]
        CleanupReg["Register cleanup functions"]
    end
    
    subgraph "Tool Execution Phase"
        StreamText["streamText()"]
        ToolCall["LLM invokes tool"]
        ToolExec["Tool execution"]
        ToolResult["Return result to LLM"]
    end
    
    subgraph "Cleanup Phase"
        OnFinish["streamText onFinish"]
        RunCleanup["Execute cleanupFunctions"]
        CloseConn["Close DB connections"]
    end
    
    NodeConfig --> PrepareTools
    GitHubConfig --> AuthCheck
    PostgresConfig --> AuthCheck
    SearchConfig --> BuildToolSet
    
    AuthCheck --> BuildToolSet
    BuildToolSet --> CleanupReg
    CleanupReg --> StreamText
    
    StreamText --> ToolCall
    ToolCall --> ToolExec
    ToolExec --> ToolResult
    ToolResult --> StreamText
    
    StreamText --> OnFinish
    OnFinish --> RunCleanup
    RunCleanup --> CloseConn
```

**Sources:**
- [packages/giselle/src/engine/generations/generate-text.ts:76-153]()
- [packages/giselle/src/engine/generations/generate-content.ts:112-188]()
- [packages/giselle/src/engine/generations/internal/use-generation-executor.ts:59-411]()

## PreparedToolSet Data Structure

The `PreparedToolSet` type encapsulates both the tools themselves and their lifecycle management:

```typescript
interface PreparedToolSet {
  toolSet: Record<string, CoreTool>;
  cleanupFunctions: (() => Promise<void>)[];
}
```

This structure is built incrementally as each tool type is evaluated and conditionally added to the set.

**Sources:**
- [packages/giselle/src/engine/generations/types.ts]()

## GitHub Tools Integration

GitHub tools enable LLM operations to interact with repositories, issues, and pull requests. The integration supports two authentication strategies: Personal Access Token (PAT) and encrypted secrets.

### GitHub Tool Configuration

```mermaid
graph LR
    subgraph "Node Configuration"
        GitHubToolConfig["operationNode.content.tools.github"]
        AuthType["auth.type: 'pat' | 'secret'"]
        ToolList["tools: string[]"]
    end
    
    subgraph "Authentication Resolution"
        PATAuth["PAT: vault.decrypt(token)"]
        SecretAuth["Secret: decryptSecret(secretId)"]
    end
    
    subgraph "Tool Instantiation"
        OctokitClient["octokit({ strategy: 'personal-access-token' })"]
        GitHubTools["githubTools(octokit)"]
        ToolSelection["Filter tools from githubTools"]
    end
    
    GitHubToolConfig --> AuthType
    AuthType -->|"type === 'pat'"| PATAuth
    AuthType -->|"type === 'secret'"| SecretAuth
    
    PATAuth --> OctokitClient
    SecretAuth --> OctokitClient
    OctokitClient --> GitHubTools
    GitHubTools --> ToolSelection
```

### Tool Preparation Logic

The GitHub tool preparation follows this pattern in both `generate-text.ts` and `generate-content.ts`:

| Step | Action | Code Location |
|------|--------|---------------|
| 1. Check configuration | Verify `operationNode.content.tools?.github` exists | Line 82 |
| 2. Resolve authentication | Decrypt PAT or retrieve secret | Lines 84-101 |
| 3. Create Octokit client | Initialize with `personal-access-token` strategy | Lines 102-106 |
| 4. Get all GitHub tools | Call `githubTools(octokit)` | Lines 102-107 |
| 5. Filter selected tools | Add only configured tools to `preparedToolSet` | Lines 108-118 |

### Authentication Flow

```mermaid
sequenceDiagram
    participant Gen as "generateText/generateContent"
    participant Vault as "Vault"
    participant Decrypt as "decryptSecret"
    participant Storage as "GiselleStorage"
    
    Gen->>Gen: Check githubTool.auth.type
    
    alt auth.type === "pat"
        Gen->>Vault: decrypt(githubTool.auth.token)
        Vault-->>Gen: decryptedToken
    else auth.type === "secret"
        Gen->>Decrypt: decryptSecret({ secretId })
        Decrypt->>Storage: getJson(secretPath)
        Storage-->>Decrypt: Secret
        Decrypt->>Vault: decrypt(secret.value)
        Vault-->>Decrypt: decryptedValue
        Decrypt-->>Gen: decryptedToken
    end
    
    Gen->>Gen: octokit({ personalAccessToken: decryptedToken })
```

### Available GitHub Tools

The `@giselle-sdk/github-tool` package provides tools that are selectively enabled based on node configuration. The exact tools available depend on the package implementation, but the system allows specifying which tools to include via the `tools` array in the configuration.

**Sources:**
- [packages/giselle/src/engine/generations/generate-text.ts:82-119]()
- [packages/giselle/src/engine/generations/generate-content.ts:117-153]()
- [packages/giselle/src/engine/secrets/decrypt-secret.ts:1-36]()

## Postgres Tools Integration

Postgres tools enable SQL query execution during LLM operations. The tool requires an encrypted connection string stored as a secret.

### Postgres Tool Preparation

```mermaid
graph TB
    subgraph "Configuration Check"
        PostgresConfig["operationNode.content.tools?.postgres"]
        SecretId["postgresToolData.secretId"]
    end
    
    subgraph "Secret Retrieval"
        DecryptSecret["decryptSecret({ secretId })"]
        ConnectionString["connectionString"]
    end
    
    subgraph "Tool Creation"
        CreateTools["createPostgresTools(connectionString)"]
        ToolSet["postgresTool.toolSet"]
        Cleanup["postgresTool.cleanup"]
    end
    
    subgraph "Tool Registration"
        SelectTools["Filter configured tools"]
        AddToSet["Add to preparedToolSet.toolSet"]
        RegisterCleanup["Add to preparedToolSet.cleanupFunctions"]
    end
    
    PostgresConfig --> SecretId
    SecretId --> DecryptSecret
    DecryptSecret --> ConnectionString
    ConnectionString --> CreateTools
    CreateTools --> ToolSet
    CreateTools --> Cleanup
    
    ToolSet --> SelectTools
    SelectTools --> AddToSet
    Cleanup --> RegisterCleanup
```

### Implementation Details

The Postgres tool integration differs from GitHub tools in that it requires explicit cleanup. The `createPostgresTools()` function returns both a tool set and a cleanup function:

| Property | Purpose | Registration |
|----------|---------|-------------|
| `postgresTool.toolSet` | Contains executable tools | Added to `preparedToolSet.toolSet` |
| `postgresTool.cleanup` | Closes database connections | Added to `preparedToolSet.cleanupFunctions` |

The cleanup function is invoked in the `streamText` `onFinish` callback, ensuring database connections are properly closed even if generation completes or fails.

**Sources:**
- [packages/giselle/src/engine/generations/generate-text.ts:121-153]()
- [packages/giselle/src/engine/generations/generate-content.ts:155-188]()
- [packages/giselle/src/engine/generations/tools/postgres.ts]()

## Web Search Tools Integration

Web search tools are provider-specific and enable LLMs to access real-time information. Each provider has different tool APIs and configuration requirements.

### Provider Tool Mapping

```mermaid
graph TB
    subgraph "OpenAI Provider"
        OpenAIConfig["provider === 'openai'"]
        OpenAIWebSearch["tools?.openaiWebSearch"]
        OpenAIPreview["openai.tools.webSearchPreview()"]
        OpenAIStandard["openai.tools.webSearch()"]
        OptionalGrounding1["hasCapability(model, OptionalSearchGrounding)"]
    end
    
    subgraph "Anthropic Provider"
        AnthropicConfig["provider === 'anthropic'"]
        AnthropicWebSearch["tools?.anthropicWebSearch"]
        AnthropicTool["anthropic.tools.webSearch_20250305()"]
    end
    
    subgraph "Google Provider"
        GoogleConfig["provider === 'google'"]
        SearchGrounding["llm.configurations.searchGrounding"]
        UrlContext["llm.configurations.urlContext"]
        GoogleSearch["vertex.tools.googleSearch() or google.tools.googleSearch()"]
        GoogleUrl["vertex.tools.urlContext() or google.tools.urlContext()"]
        OptionalGrounding2["hasCapability(model, OptionalSearchGrounding)"]
        UrlCapability["hasCapability(model, UrlContext)"]
    end
    
    OpenAIConfig --> OpenAIWebSearch
    OpenAIWebSearch --> OptionalGrounding1
    OptionalGrounding1 -->|"generate-text.ts"| OpenAIPreview
    OptionalGrounding1 -->|"generate-content.ts"| OpenAIStandard
    
    AnthropicConfig --> AnthropicWebSearch
    AnthropicWebSearch --> AnthropicTool
    
    GoogleConfig --> SearchGrounding
    GoogleConfig --> UrlContext
    SearchGrounding --> OptionalGrounding2
    OptionalGrounding2 --> GoogleSearch
    UrlContext --> UrlCapability
    UrlCapability --> GoogleUrl
```

### OpenAI Web Search Tools

OpenAI offers two web search tool variants:

| Tool Name | File | Usage Context | Configuration Source |
|-----------|------|---------------|---------------------|
| `web_search_preview` | `generate-text.ts` | Older streaming approach | `operationNode.content.tools.openaiWebSearch` |
| `web_search` | `generate-content.ts` | Newer content generation | `operationNode.content.tools.openaiWebSearch` |

Both require the model to have `Capability.OptionalSearchGrounding` and are configured with parameters from the node's tool configuration.

**Sources:**
- [packages/giselle/src/engine/generations/generate-text.ts:155-169]()
- [packages/giselle/src/engine/generations/generate-content.ts:190-204]()

### Google Search and URL Context Tools

Google Vertex AI provides two distinct tools:

1. **Google Search** (`google_search`): Real-time web search grounding
   - Enabled when `llm.configurations.searchGrounding === true`
   - Requires `Capability.OptionalSearchGrounding`
   - Uses `vertex.tools.googleSearch({})` in `generate-text.ts`
   - Uses `google.tools.googleSearch({})` in `generate-content.ts`

2. **URL Context** (`url_context`): Fetch and process content from URLs
   - Enabled when `llm.configurations.urlContext === true`
   - Requires `Capability.UrlContext`
   - Uses `vertex.tools.urlContext({})` in `generate-text.ts`
   - Uses `google.tools.urlContext({})` in `generate-content.ts`

**Sources:**
- [packages/giselle/src/engine/generations/generate-text.ts:170-195]()
- [packages/giselle/src/engine/generations/generate-content.ts:205-230]()

### Anthropic Web Search Tool

Anthropic's web search integration is simpler:

- Tool name: `web_search`
- API: `anthropic.tools.webSearch_20250305()`
- Configuration: `operationNode.content.tools.anthropicWebSearch`
- No capability check required

**Sources:**
- [packages/giselle/src/engine/generations/generate-text.ts:197-210]()
- [packages/giselle/src/engine/generations/generate-content.ts:232-245]()

## Tool Injection into LLM Calls

Once tools are prepared, they are injected into the `streamText()` call via the `tools` parameter. The system also manages step count limits for tool usage.

### Tool Step Limiting

```mermaid
graph LR
    subgraph "Step Limit Configuration"
        Provider["operationNode.content.llm.provider"]
        ModelId["operationNode.content.llm.id"]
        ToolCount["Object.keys(preparedToolSet.toolSet).length"]
    end
    
    subgraph "Step Limit Decision"
        IsOpenAI{{"provider === 'openai'"}}
        IsGPT5{{"model in ['gpt-5', 'gpt-5-mini', 'gpt-5-nano']"}}
        DisableLimit["shouldDisableToolStepLimit = true"]
        EnableLimit["stopWhen: stepCountIs(toolCount + 1)"]
    end
    
    Provider --> IsOpenAI
    ModelId --> IsGPT5
    IsOpenAI -->|Yes| IsGPT5
    IsGPT5 -->|Yes| DisableLimit
    IsGPT5 -->|No| EnableLimit
    IsOpenAI -->|No| EnableLimit
    ToolCount --> EnableLimit
```

The step limit logic prevents infinite tool calling loops:

- **Default behavior**: Limit tool calls to `toolCount + 1` steps using `stepCountIs()`
- **GPT-5 exception**: Models like `gpt-5`, `gpt-5-mini`, and `gpt-5-nano` have no step limit
- In `generate-content.ts`, the step limit always applies: `stopWhen: stepCountIs(Object.keys(preparedToolSet.toolSet).length + 1)`

### streamText Integration

The prepared tool set is passed to `streamText()` along with other parameters:

```typescript
const streamTextResult = streamText({
  model,
  providerOptions,
  messages,
  tools: preparedToolSet.toolSet,  // Injected here
  stopWhen: stepCountIs(preparedToolCount + 1),
  onError: ({ error }) => { /* ... */ },
  onFinish: () => { /* cleanup */ }
});
```

**Sources:**
- [packages/giselle/src/engine/generations/generate-text.ts:221-245]()
- [packages/giselle/src/engine/generations/generate-content.ts:258-292]()

## Tool Cleanup and Resource Management

Tools that manage persistent connections (like database clients) must be properly cleaned up after generation completes or fails.

### Cleanup Execution Flow

```mermaid
sequenceDiagram
    participant StreamText as "streamText()"
    participant OnFinish as "onFinish callback"
    participant Cleanup as "preparedToolSet.cleanupFunctions"
    participant Tools as "Individual tool cleanup"
    
    StreamText->>StreamText: Generation completes
    StreamText->>OnFinish: Trigger onFinish
    
    OnFinish->>OnFinish: Log completion time
    OnFinish->>Cleanup: Promise.all(cleanupFunctions.map(...))
    
    loop For each cleanup function
        Cleanup->>Tools: Execute cleanup()
        Tools-->>Cleanup: Connection closed
    end
    
    Cleanup-->>OnFinish: All cleanup complete
    OnFinish->>OnFinish: Log cleanup time
    OnFinish->>OnFinish: Handle generation completion
```

The cleanup phase occurs in the `streamText` `onFinish` callback:

1. **Tool cleanup**: Execute all registered cleanup functions in parallel
2. **Error handling**: Process any generation errors
3. **Output processing**: Extract text, reasoning, and sources
4. **Completion**: Call `finishGeneration()` to persist results

**Sources:**
- [packages/giselle/src/engine/generations/generate-text.ts:248-260]()
- [packages/giselle/src/engine/generations/generate-content.ts:296-307]()

## Integration Configuration

The Giselle Engine requires integration configuration at initialization time to enable external tool access.

### GitHub Integration Configuration

```mermaid
graph TB
    subgraph "Environment Variables"
        AppId["GITHUB_APP_ID"]
        PrivateKey["GITHUB_APP_PRIVATE_KEY"]
        ClientId["GITHUB_APP_CLIENT_ID"]
        ClientSecret["GITHUB_APP_CLIENT_SECRET"]
        WebhookSecret["GITHUB_APP_WEBHOOK_SECRET"]
    end
    
    subgraph "Engine Configuration"
        IntegrationConfigs["integrationConfigs.github"]
        AuthV2["authV2 configuration"]
        LegacyAuth["auth configuration"]
    end
    
    subgraph "Runtime Usage"
        GenerateText["generateText()"]
        GitHubTools["GitHub tool preparation"]
    end
    
    AppId --> AuthV2
    PrivateKey --> AuthV2
    ClientId --> AuthV2
    ClientSecret --> AuthV2
    WebhookSecret --> AuthV2
    
    AuthV2 --> IntegrationConfigs
    LegacyAuth --> IntegrationConfigs
    
    IntegrationConfigs --> GenerateText
    GenerateText --> GitHubTools
```

The `NextGiselleEngine()` configuration includes:

| Configuration Key | Purpose | Required Fields |
|-------------------|---------|-----------------|
| `integrationConfigs.github.authV2` | GitHub App authentication | `appId`, `privateKey`, `clientId`, `clientSecret`, `webhookSecret` |
| `integrationConfigs.github.auth` | Legacy authentication | `strategy`, `appId`, `privateKey`, `resolver` |

**Sources:**
- [apps/studio.giselles.ai/app/giselle-engine.ts:89-248]()
- [apps/playground/giselle-engine.ts:62-93]()
- [packages/giselle/src/engine/types.ts:124-141]()

## Tool Security and Secrets Management

All tool authentication credentials are handled through the vault system to ensure secure storage and transmission.

### Secret Resolution Pattern

```mermaid
graph TB
    subgraph "Secret Storage"
        SecretId["SecretId"]
        SecretPath["secrets/{workspaceId}/{secretId}.json"]
        EncryptedValue["secret.value (encrypted)"]
    end
    
    subgraph "Retrieval Layer"
        DecryptFn["decryptSecret()"]
        Storage["experimental_storage.getJson()"]
    end
    
    subgraph "Vault Layer"
        VaultDecrypt["vault.decrypt()"]
        DecryptedValue["Plaintext credential"]
    end
    
    subgraph "Tool Usage"
        GitHubAuth["GitHub PAT"]
        PostgresConn["Postgres connection string"]
    end
    
    SecretId --> DecryptFn
    DecryptFn --> Storage
    Storage --> SecretPath
    SecretPath --> EncryptedValue
    EncryptedValue --> VaultDecrypt
    VaultDecrypt --> DecryptedValue
    
    DecryptedValue --> GitHubAuth
    DecryptedValue --> PostgresConn
```

The `decryptSecret()` function provides a unified interface for retrieving and decrypting secrets:

1. Load secret from storage using `secretPath(secretId)`
2. Parse with `Secret` schema
3. Decrypt value using `vault.decrypt(secret.value)`
4. Return plaintext credential

**Sources:**
- [packages/giselle/src/engine/secrets/decrypt-secret.ts:1-36]()
- [packages/giselle/src/engine/secrets/paths.ts]()

---

# Page: Knowledge and Context Systems

# Knowledge and Context Systems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/configure-sources-dialog.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/configure-sources-dialog.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/data.ts](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/data.ts)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/diagnostic-modal.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/diagnostic-modal.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-embedding-profiles.ts](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-embedding-profiles.ts)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-store-create-dialog.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-store-create-dialog.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-vector-store-list.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-vector-store-list.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/page.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/page.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/layout.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/layout.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/navigation-layout.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/navigation-layout.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/page.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/page.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-list.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-list.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-registration-dialog.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-registration-dialog.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/sidebar-menu.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/sidebar-menu.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/types.ts](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/types.ts)
- [internal-packages/ui/components/form-field.tsx](internal-packages/ui/components/form-field.tsx)
- [internal-packages/ui/components/section-header.tsx](internal-packages/ui/components/section-header.tsx)
- [internal-packages/ui/components/status-indicator.tsx](internal-packages/ui/components/status-indicator.tsx)

</details>



The Knowledge and Context Systems provide retrieval-augmented generation (RAG) capabilities to the Giselle platform. These systems process documents (PDFs, text files, Markdown), manage vector stores (GitHub repositories and uploaded documents), generate embeddings using multiple providers, and execute semantic similarity searches to provide relevant context for AI generations.

The system consists of three primary components:
1. **Document Processing Pipeline** ([3.1](#31-document-processing-pipeline)): Extracts text and images from binary documents using the `@giselles-ai/document-preprocessor` package
2. **Vector Store Management** ([3.2](#32-vector-store-management)): Configures and manages GitHub and Document vector stores through the team settings UI
3. **RAG System and Query Execution** ([3.3](#33-rag-system-and-query-execution)): Chunks documents, generates embeddings, and performs similarity searches using PostgreSQL with pgvector

For information about how the Giselle Engine integrates vector stores into generation workflows, see page 2. For database schema details, see page 2.6.

## 3.1 Document Processing Pipeline

The document preprocessing system transforms raw binary files (PDFs, plain text, Markdown) into normalized text and image data suitable for embedding and indexing. The core functionality is implemented in the `@giselles-ai/document-preprocessor` package, which provides a unified API for extracting text and rendering images from various document formats.

### Architecture and Core Components

```mermaid
graph TB
    subgraph "Document Preprocessor Package"
        extractText["extractText()<br/>packages/document-preprocessor/src/text.ts"]
        extractPdfText["extractPdfText()<br/>packages/document-preprocessor/src/pdf.ts"]
        renderPdfPageImages["renderPdfPageImages()<br/>packages/document-preprocessor/src/pdf.ts"]
        
        subgraph "Internal Utilities"
            withPdfDocument["withPdfDocument()<br/>internal/pdfium.ts"]
            normalizeExtractedText["normalizeExtractedText()<br/>internal/text-normalizer.ts"]
            toUint8Array["toUint8Array()<br/>internal/binary.ts"]
            assertNotAborted["assertNotAborted()<br/>internal/abort.ts"]
        end
    end
    
    subgraph "External Dependencies"
        embedpdf["@embedpdf/pdfium<br/>PDFium WASM bindings"]
        pngjs["pngjs<br/>PNG encoding library"]
    end
    
    subgraph "Input Types"
        BinaryDataInput["BinaryDataInput<br/>Buffer | Uint8Array | ArrayBuffer"]
    end
    
    subgraph "Output Types"
        TextExtractionResult["TextExtractionResult<br/>{ text: string }"]
        PdfTextExtractionResult["PdfTextExtractionResult<br/>{ totalPages, pages[] }"]
        PdfImageRenderResult["PdfImageRenderResult<br/>{ totalPages, pages[] }"]
    end
    
    BinaryDataInput --> extractText
    BinaryDataInput --> extractPdfText
    BinaryDataInput --> renderPdfPageImages
    
    extractText --> toUint8Array
    extractText --> assertNotAborted
    extractText --> TextExtractionResult
    
    extractPdfText --> withPdfDocument
    extractPdfText --> normalizeExtractedText
    extractPdfText --> assertNotAborted
    extractPdfText --> PdfTextExtractionResult
    
    renderPdfPageImages --> withPdfDocument
    renderPdfPageImages --> pngjs
    renderPdfPageImages --> assertNotAborted
    renderPdfPageImages --> PdfImageRenderResult
    
    withPdfDocument --> embedpdf
```

**Sources:** [packages/document-preprocessor/src/index.ts:1-13](), [packages/document-preprocessor/src/pdf.ts:1-138](), [packages/document-preprocessor/src/text.ts:1-37](), [packages/document-preprocessor/src/types.ts:1-53]()

### Processing Functions

| Function | Input | Options | Output | Use Case |
|----------|-------|---------|--------|----------|
| `extractText()` | Buffer, Uint8Array, ArrayBuffer | `encoding`, `signal` | `{ text: string }` | Plain text and Markdown files |
| `extractPdfText()` | Binary PDF data | `password`, `maxPages`, `signal` | `{ totalPages, pages: PdfTextPage[] }` | Extract text content from PDFs |
| `renderPdfPageImages()` | Binary PDF data | `password`, `targetDpi`, `maxPages`, `renderFormFields`, `signal` | `{ totalPages, pages: PdfImagePage[] }` | Render PDF pages as PNG images |

**Sources:** [packages/document-preprocessor/src/pdf.ts:21-54](), [packages/document-preprocessor/src/pdf.ts:56-99](), [packages/document-preprocessor/src/text.ts:13-36]()

### PDF Processing Implementation

The PDF processing pipeline uses the PDFium library through `@embedpdf/pdfium` bindings. The `withPdfDocument()` helper manages the PDFium document lifecycle:

```mermaid
sequenceDiagram
    participant Client
    participant extractPdfText
    participant withPdfDocument
    participant PDFiumDocument
    participant PDFiumPage
    participant normalizeExtractedText
    
    Client->>extractPdfText: Binary data + options
    extractPdfText->>withPdfDocument: bytes, { password, signal }
    withPdfDocument->>PDFiumDocument: Load document
    
    loop For each page (up to maxPages)
        extractPdfText->>extractPdfText: assertNotAborted(signal)
        extractPdfText->>PDFiumDocument: loadPage(index)
        PDFiumDocument->>PDFiumPage: Create page
        extractPdfText->>PDFiumPage: getText()
        PDFiumPage-->>extractPdfText: rawText
        extractPdfText->>normalizeExtractedText: rawText
        normalizeExtractedText-->>extractPdfText: normalized text
        extractPdfText->>PDFiumPage: close()
    end
    
    withPdfDocument->>PDFiumDocument: Close document
    extractPdfText-->>Client: { totalPages, pages }
```

**Sources:** [packages/document-preprocessor/src/pdf.ts:21-54](), [packages/document-preprocessor/README.md:36-50]()

### Text Normalization

The `normalizeExtractedText()` function in [packages/document-preprocessor/src/internal/text-normalizer.ts]() performs the following transformations on extracted PDF text:

1. Repairs hyphenated line breaks (e.g., "exam-\nple" → "example")
2. Normalizes whitespace (multiple spaces/newlines → single space)
3. Removes trailing/leading whitespace
4. Preserves intentional paragraph breaks

**Sources:** [packages/document-preprocessor/README.md:9]()

### Image Rendering Pipeline

For PDFs that require visual processing, `renderPdfPageImages()` converts each page to a PNG buffer:

```mermaid
graph LR
    PDFPage["PDF Page"] --> render["page.render()<br/>scale, renderFormFields"]
    render --> RGBA["RGBA pixel data<br/>Uint8Array"]
    RGBA --> encodeRgbaToPng["encodeRgbaToPng()<br/>width, height"]
    encodeRgbaToPng --> PNG["PNG.pack()"]
    PNG --> chunks["Buffer chunks"]
    chunks --> concat["Buffer.concat()"]
    concat --> Uint8Array["Uint8Array<br/>(PNG data)"]
```

The rendering process:
1. Calculates scale factor from target DPI (default 144 DPI)
2. Renders page to RGBA pixel buffer using PDFium
3. Encodes RGBA data to PNG using `pngjs` library
4. Returns page number, dimensions, and PNG buffer

**Sources:** [packages/document-preprocessor/src/pdf.ts:56-99](), [packages/document-preprocessor/src/pdf.ts:101-130]()

### Abort Signal Support

All extraction functions accept an `AbortSignal` for cancellation:

```typescript
// From pdf.ts
for (let index = 0; index < limit; index += 1) {
    assertNotAborted(signal);  // Throws if aborted
    const page = document.loadPage(index);
    // ... process page
}
```

The `assertNotAborted()` helper throws immediately if the signal has been aborted, enabling responsive cancellation of long-running document processing operations.

**Sources:** [packages/document-preprocessor/src/pdf.ts:37](), [packages/document-preprocessor/README.md:72-79]()

### Security Considerations

From [packages/document-preprocessor/README.md:149-154]():

- **PDFium sandboxing**: PDFium engine executes in a sandboxed environment to mitigate malicious PDF risks
- **Password-protected PDFs**: Handle encrypted PDFs cautiously; not all encryption schemes are fully supported
- **Resource limits**: Enforce file size and processing time limits to prevent DoS attacks

The package supports password-protected PDFs through the `password` option in `PdfTextExtractionOptions` and `PdfImageRenderOptions`.

**Sources:** [packages/document-preprocessor/README.md:149-154](), [packages/document-preprocessor/src/types.ts:14-18](), [packages/document-preprocessor/src/types.ts:32-38]()

## 3.2 Vector Store Management

The vector store system manages two types of repositories: GitHub repositories (code, issues, and pull requests) and document uploads (PDFs and text files). Both use configurable embedding profiles and share a common architecture built on PostgreSQL with the pgvector extension. The management UI is located at `/settings/team/vector-stores` in the Studio application.

### Vector Store Types and Database Schema

```mermaid
graph TB
    subgraph "UI_Components"
        VectorStoresPage["/settings/team/vector-stores/page.tsx<br/>Main vector stores page"]
        RepositoryList["RepositoryList component<br/>repository-list.tsx"]
        DocumentVectorStoreList["DocumentVectorStoreList component<br/>document-vector-store-list.tsx"]
        RepositoryItem["RepositoryItem component<br/>repository-item.tsx"]
        DocumentVectorStoreItem["DocumentVectorStoreItem component<br/>document-vector-store-item.tsx"]
    end
    
    subgraph "Database_Tables"
        githubRepositoryIndex["githubRepositoryIndex<br/>id, owner, repo, teamDbId, installationId"]
        githubRepositoryEmbeddingProfiles["githubRepositoryEmbeddingProfiles<br/>repositoryIndexDbId, embeddingProfileId"]
        githubRepositoryContentStatus["githubRepositoryContentStatus<br/>contentType, status, errorCode, retryAfter, metadata"]
        
        documentVectorStores["documentVectorStores<br/>id, teamDbId, name"]
        documentEmbeddingProfiles["documentEmbeddingProfiles<br/>documentVectorStoreDbId, embeddingProfileId"]
        documentVectorStoreSources["documentVectorStoreSources<br/>id, fileName, storageKey, ingestStatus"]
    end
    
    subgraph "Actions"
        registerRepositoryIndex["registerRepositoryIndex()<br/>actions.ts:107"]
        updateRepositoryIndex["updateRepositoryIndex()<br/>actions.ts:257"]
        triggerManualIngest["triggerManualIngest()<br/>actions.ts:554"]
        createDocumentVectorStore["createDocumentVectorStore()<br/>actions.ts:616"]
        updateDocumentVectorStore["updateDocumentVectorStore()<br/>actions.ts:702"]
    end
    
    VectorStoresPage --> RepositoryList
    VectorStoresPage --> DocumentVectorStoreList
    RepositoryList --> RepositoryItem
    DocumentVectorStoreList --> DocumentVectorStoreItem
    
    RepositoryItem --> registerRepositoryIndex
    RepositoryItem --> updateRepositoryIndex
    RepositoryItem --> triggerManualIngest
    
    DocumentVectorStoreItem --> createDocumentVectorStore
    DocumentVectorStoreItem --> updateDocumentVectorStore
    
    registerRepositoryIndex --> githubRepositoryIndex
    registerRepositoryIndex --> githubRepositoryEmbeddingProfiles
    registerRepositoryIndex --> githubRepositoryContentStatus
    
    createDocumentVectorStore --> documentVectorStores
    createDocumentVectorStore --> documentEmbeddingProfiles
    createDocumentVectorStore --> documentVectorStoreSources
```

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/page.tsx:1-80](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:1-892](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:1-565]()

### GitHub Repository Vector Store

GitHub repositories are indexed with three content types: `blob` (code files), `issue` (issue titles, descriptions, and comments), and `pull_request` (merged PR content and discussions). Each content type can be enabled/disabled independently through the `ConfigureSourcesDialog` component, though `blob` is mandatory and cannot be disabled.

#### Repository Index Structure

| Field | Type | Description |
|-------|------|-------------|
| `id` | `GitHubRepositoryIndexId` | `gthbi_` prefixed CUID |
| `owner` | `string` | GitHub repository owner |
| `repo` | `string` | Repository name |
| `teamDbId` | `number` | Team association |
| `installationId` | `number` | GitHub App installation ID |

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:166-177]()

#### Content Status Tracking

Each combination of repository + embedding profile + content type has a status record in `githubRepositoryContentStatus`. The `EmbeddingModelCard` component in `repository-item.tsx` displays status for each embedding profile and content type.

**Content Status Lifecycle**

```mermaid
stateDiagram-v2
    [*] --> idle: Initial state
    idle --> running: triggerManualIngest()
    running --> completed: Ingestion succeeds
    running --> failed: Error occurs
    failed --> idle: Retry allowed (retryAfter passed)
    completed --> running: Re-ingest triggered
    
    state failed {
        [*] --> errorCode: Set error code
        errorCode --> retryAfter: Calculate retry timestamp
    }
    
    state completed {
        [*] --> metadata: Store sync metadata
        note right of metadata
            blob: lastIngestedCommitSha
            issue: lastIngestedIssueNumber
            pull_request: lastIngestedPrNumber
        end note
    }
```

The status is displayed in the UI through the `StatusIndicator` and `StatusBadge` components. Each content type section shows:
- **Code**: Status, last sync time, and commit SHA (lines 283-374 in repository-item.tsx)
- **Issues**: Status, last sync time, and issue number (lines 376-468)
- **Pull Requests**: Status, last sync time, and PR number (lines 470-560)

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:240-565](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/types.ts:1-6]()

#### Registration and Configuration Flow

The `RepositoryRegistrationDialog` component (repository-registration-dialog.tsx) provides the UI for registering new GitHub repositories. Users select:
1. Owner/Organization (from GitHub App installations)
2. Repository name (filtered by selected owner)
3. Content types to ingest (Code, Issues, Pull Requests)
4. Embedding models (at least one required)

**Registration Flow**

```mermaid
sequenceDiagram
    participant User
    participant RepositoryRegistrationDialog as "RepositoryRegistrationDialog<br/>repository-registration-dialog.tsx:41"
    participant registerRepositoryIndex as "registerRepositoryIndex()<br/>actions.ts:107"
    participant validateGitHubAccess as "validateGitHubAccess()<br/>actions.ts:62"
    participant GitHub as "GitHub API"
    participant Database as "db.transaction()"
    participant getInstallationsWithRepos as "getInstallationsWithRepos()<br/>data.ts:58"
    
    User->>RepositoryRegistrationDialog: Open dialog
    RepositoryRegistrationDialog->>getInstallationsWithRepos: Load installations + repos
    getInstallationsWithRepos-->>RepositoryRegistrationDialog: InstallationWithRepos[]
    
    User->>RepositoryRegistrationDialog: Select owner, repo, content types, profiles
    RepositoryRegistrationDialog->>registerRepositoryIndex: registerRepositoryIndex(owner, repo, installationId, contentTypes, embeddingProfileIds)
    
    registerRepositoryIndex->>validateGitHubAccess: validateGitHubAccess(installationId, owner, repo)
    validateGitHubAccess->>GitHub: GET /repos/{owner}/{repo}
    
    alt Repository accessible
        GitHub-->>validateGitHubAccess: 200 OK
        validateGitHubAccess-->>registerRepositoryIndex: { success: true }
        
        registerRepositoryIndex->>Database: Start transaction
        registerRepositoryIndex->>Database: Lock team row (for quota check)
        registerRepositoryIndex->>Database: Check existing repos count < quota.maxStores
        registerRepositoryIndex->>Database: INSERT githubRepositoryIndex
        registerRepositoryIndex->>Database: INSERT githubRepositoryEmbeddingProfiles (for each profile)
        registerRepositoryIndex->>Database: INSERT githubRepositoryContentStatus (profile × contentType)
        Database-->>registerRepositoryIndex: Commit
        
        registerRepositoryIndex->>registerRepositoryIndex: revalidatePath('/settings/team/vector-stores')
        registerRepositoryIndex-->>RepositoryRegistrationDialog: { success: true }
        RepositoryRegistrationDialog-->>User: Close dialog, refresh list
    else Repository not accessible
        GitHub-->>validateGitHubAccess: 404/403
        validateGitHubAccess-->>registerRepositoryIndex: { success: false, error }
        registerRepositoryIndex-->>RepositoryRegistrationDialog: { success: false, error }
        RepositoryRegistrationDialog-->>User: Display error
    end
```

The registration process enforces quota limits by locking the team row during the transaction (lines 161-166 in actions.ts) and checking existing repository count before insertion (lines 188-201).

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:62-251](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-registration-dialog.tsx:41-477](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/data.ts:58-104]()

### Document Vector Store

Document vector stores allow teams to upload PDF and text files for RAG operations. Each store has a name and one or more embedding profiles. The UI is located at `/settings/team/vector-stores/document` and uses the `DocumentVectorStoreList` and `DocumentVectorStoreItem` components.

#### Document Vector Store Structure

| Field | Type | Description |
|-------|------|-------------|
| `id` | `DocumentVectorStoreId` | `dvs_` prefixed CUID (e.g., `dvs_clx9k2...`) |
| `teamDbId` | `number` | Foreign key to teams table |
| `name` | `string` | User-defined name displayed in UI |
| `createdAt` | `Date` | Creation timestamp |

The `createDocumentVectorStore()` action (actions.ts:616-700) creates the store and associated embedding profiles in a single transaction with quota enforcement.

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:616-700](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/page.tsx:1-48]()

#### Document Source Management

Each uploaded file creates a `documentVectorStoreSources` record:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Source ID (CUID) |
| `documentVectorStoreDbId` | `number` | Parent store |
| `fileName` | `string` | Original filename |
| `storageKey` | `string` | Supabase storage path |
| `ingestStatus` | `IngestStatus` | `idle`, `running`, `completed`, `failed` |
| `ingestErrorCode` | `string?` | Error code if failed |

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx:254-270]()

#### Document Upload Flow

The `DocumentVectorStoreConfigureDialog` component provides drag-and-drop and file selection UI for uploading documents. File validation occurs client-side before upload.

**File Upload and Ingestion**

```mermaid
sequenceDiagram
    participant User
    participant DocumentVectorStoreConfigureDialog as "DocumentVectorStoreConfigureDialog<br/>document-vector-store-item.tsx:327"
    participant handleFilesUpload as "handleFilesUpload()<br/>:397"
    participant API as "POST /api/vector-stores/document/{id}/documents"
    participant SupabaseStorage as "Supabase Storage<br/>DOCUMENT_VECTOR_STORE_STORAGE_PREFIX"
    participant Database as "documentVectorStoreSources table"
    participant BackgroundIngest as "Background Ingest Job<br/>(trigger.dev or async)"
    
    User->>DocumentVectorStoreConfigureDialog: Drag/drop or select files
    DocumentVectorStoreConfigureDialog->>handleFilesUpload: Validate files
    
    alt Invalid files
        handleFilesUpload->>handleFilesUpload: Check file type, size, empty
        handleFilesUpload-->>User: showErrorToast(error)
    else Valid files
        handleFilesUpload->>API: POST FormData with valid files
        
        loop For each file
            API->>SupabaseStorage: Upload to vector-stores/{storeId}/
            SupabaseStorage-->>API: storageKey
            API->>Database: INSERT documentVectorStoreSources (ingestStatus='idle')
            Database-->>API: sourceId
        end
        
        API-->>handleFilesUpload: { successes: [...], failures: [...] }
        handleFilesUpload->>DocumentVectorStoreConfigureDialog: Update documentSources state
        handleFilesUpload->>DocumentVectorStoreConfigureDialog: setUploadMessage(success message)
        DocumentVectorStoreConfigureDialog-->>User: Display upload success
        
        Note over BackgroundIngest: Triggered asynchronously on insert
        BackgroundIngest->>Database: UPDATE ingestStatus='running'
        BackgroundIngest->>SupabaseStorage: Download file via storageKey
        BackgroundIngest->>BackgroundIngest: extractPdfText() or extractText()
        BackgroundIngest->>BackgroundIngest: Generate embeddings via embedMany()
        BackgroundIngest->>Database: Store embeddings in pgvector
        BackgroundIngest->>Database: UPDATE ingestStatus='completed' or 'failed'
    end
```

**File Validation Rules** (enforced in handleFilesUpload):
- Supported types: PDF, TXT, MD (defined in `DOCUMENT_VECTOR_STORE_SUPPORTED_MIME_TYPES`)
- Max file size: `DOCUMENT_VECTOR_STORE_MAX_FILE_SIZE_BYTES` (displayed as `DOCUMENT_VECTOR_STORE_MAX_FILE_SIZE_LABEL`)
- Empty files rejected
- Validation helper: `isSupportedDocumentFile()` checks MIME type and extension

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx:327-634](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:55]()

### Embedding Profile System

Embedding profiles define which embedding model to use for a vector store. Different profiles have different dimensions and providers. The profiles are defined in `@giselles-ai/protocol` and re-exported by the vector store UI components.

#### Embedding Profile Configuration

The `EMBEDDING_PROFILES` constant in `@giselles-ai/protocol` defines four profiles:

| ID | Name | Provider | Model | Dimensions | GitHub Support | Document Support |
|----|------|----------|-------|------------|----------------|------------------|
| 1 | OpenAI Small | openai | text-embedding-3-small | 1536 | ✓ | ✓ |
| 2 | OpenAI Large | openai | text-embedding-3-large | 3072 | ✓ | ✓ |
| 3 | Google | google | text-embedding-004 | 768 | ✓ | ✓ |
| 4 | Cohere | cohere | embed-english-v3.0 | 1024 | ✗ | ✓ |

**GitHub Vector Store Profiles** (github-embedding-profiles.ts:1-13):
```typescript
import { EMBEDDING_PROFILES } from "@giselles-ai/protocol";

export const GITHUB_EMBEDDING_PROFILES = {
  1: EMBEDDING_PROFILES[1], // OpenAI Small
  2: EMBEDDING_PROFILES[2], // OpenAI Large
  3: EMBEDDING_PROFILES[3], // Google (excludes Cohere)
} as const;
```

**Document Vector Store Profiles** (document-embedding-profiles.ts:1-5):
```typescript
import { EMBEDDING_PROFILES } from "@giselles-ai/protocol";

// Surface all currently supported providers (OpenAI, Google, Cohere)
export const DOCUMENT_EMBEDDING_PROFILES = EMBEDDING_PROFILES;
```

Document Vector Stores support all four profiles, while GitHub Vector Stores exclude Cohere (profile ID 4) from the UI selection.

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/github-embedding-profiles.ts:1-13](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-embedding-profiles.ts:1-6]()

#### Profile Selection and Updates

Users can select multiple embedding profiles when registering a vector store. The system enforces:
- At least one profile must be selected
- The blob content type for GitHub repositories cannot be disabled
- Updates create/remove embedding profiles and content statuses in a transaction

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:114-145](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:216-367]()

### Manual Ingestion and Status Management

Teams can trigger manual ingestion for GitHub repositories through the "Ingest Now" option in the `RepoActionMenu` (repository-item.tsx:130-138). The system enforces ingestability rules before allowing manual triggers.

**Ingestability Check Flow**

```mermaid
flowchart TD
    User["User clicks 'Ingest Now'<br/>RepositoryItem:90"]
    HandleManualIngest["handleManualIngest()<br/>RepositoryItem:90"]
    TriggerManualIngest["triggerManualIngest(indexId)<br/>actions.ts:554"]
    FetchRepo["fetchRepositoryWithStatuses()<br/>actions.ts:896"]
    CheckIngestability["checkIngestability(contentStatuses)<br/>actions.ts:929"]
    
    User --> HandleManualIngest
    HandleManualIngest --> TriggerManualIngest
    TriggerManualIngest --> FetchRepo
    FetchRepo --> CheckIngestability
    
    CheckIngestability --> Rule1{For each enabled<br/>content status}
    
    Rule1 --> StatusCheck{Check status}
    StatusCheck -->|idle or completed| CanIngest[canIngest = true]
    StatusCheck -->|running| IsStale{Updated > 15 min ago?}
    StatusCheck -->|failed| HasRetry{retryAfter <= now?}
    
    IsStale -->|Yes| CanIngest
    IsStale -->|No| CannotIngest[canIngest = false<br/>Return error]
    
    HasRetry -->|Yes| CanIngest
    HasRetry -->|No| CannotIngest
    
    CanIngest --> CreateTrigger["createManualIngestTrigger(userId)<br/>lib/vector-stores/github"]
    CreateTrigger --> ExecuteManualIngest["executeManualIngest(repositoryData, trigger)<br/>actions.ts:978"]
    ExecuteManualIngest --> After["after(() => processRepository())<br/>Next.js after() API"]
    After --> ProcessRepository["processRepository(repositoryData, trigger)<br/>lib/vector-stores/github"]
    ProcessRepository --> UpdateStatus["Update githubRepositoryContentStatus<br/>Set status=running"]
    
    CannotIngest --> ReturnError["Return { success: false, error }"]
```

**Ingestability Rules** (checkIngestability function, actions.ts:929-973):
1. Content status must be `enabled: true`
2. Status must be one of:
   - `idle` or `completed` (ready to re-ingest)
   - `running` with `updatedAt` more than 15 minutes ago (stale, allow re-trigger)
   - `failed` with `retryAfter` timestamp in the past
3. At least one `blob` content status must exist

The manual ingest button is disabled when `canManuallyIngest` is false (repository-item.tsx:105-114).

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:554-593](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:929-985](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:90-114]()

### Diagnostic and Recovery System

When a GitHub repository becomes inaccessible (e.g., due to `DOCUMENT_NOT_FOUND` error from changed installation permissions), the `DiagnosticModal` component helps users diagnose and restore connectivity. The modal is triggered by clicking "Check ↗" next to failed content types (repository-item.tsx:320-327).

**Diagnostic Flow**

```mermaid
sequenceDiagram
    participant User
    participant DiagnosticModal as "DiagnosticModal<br/>diagnostic-modal.tsx:31"
    participant RunDiagnosis as "runDiagnosis()<br/>:44"
    participant DiagnoseAction as "diagnoseRepositoryConnection(indexId)<br/>actions.ts:424"
    participant GitHubAPI as "GitHub API"
    participant UpdateAction as "updateRepositoryInstallation(indexId, newId)<br/>actions.ts:505"
    participant Database as "db.update()"
    
    User->>DiagnosticModal: Click "Check ↗" on failed repo
    DiagnosticModal->>RunDiagnosis: open=true triggers useEffect
    RunDiagnosis->>DiagnoseAction: diagnoseRepositoryConnection(repositoryIndex.id)
    
    DiagnoseAction->>GitHubAPI: userClient.getInstallations()
    GitHubAPI-->>DiagnoseAction: installations[]
    
    loop For each installation
        DiagnoseAction->>GitHubAPI: buildAppInstallationClient(installation.id)
        DiagnoseAction->>GitHubAPI: GET /repos/{owner}/{repo}
        
        alt Repository accessible
            GitHubAPI-->>DiagnoseAction: 200 OK
            DiagnoseAction->>DiagnoseAction: Set validInstallationId
        else Repository not accessible
            GitHubAPI-->>DiagnoseAction: 404 or 403
        end
    end
    
    alt Valid installation found
        DiagnoseAction-->>DiagnosticModal: { canBeFixed: true, newInstallationId }
        DiagnosticModal-->>User: Show "Restore Connection" button
        
        User->>DiagnosticModal: Click "Restore Connection"
        DiagnosticModal->>UpdateAction: updateRepositoryInstallation(indexId, newInstallationId)
        
        UpdateAction->>Database: UPDATE githubRepositoryIndex SET installationId
        UpdateAction->>Database: UPDATE githubRepositoryContentStatus<br/>SET status='idle', errorCode=null, retryAfter=null
        UpdateAction->>UpdateAction: revalidatePath('/settings/team/vector-stores')
        UpdateAction-->>DiagnosticModal: Success
        DiagnosticModal-->>User: Close modal, refresh page
        
    else No valid installation
        DiagnoseAction-->>DiagnosticModal: { canBeFixed: false, reason, errorMessage }
        DiagnosticModal-->>User: Show "Delete Repository" button
        
        alt User deletes repo
            User->>DiagnosticModal: Click "Delete Repository"
            DiagnosticModal->>DiagnosticModal: onDelete() callback
        end
    end
```

**Diagnostic Results** (DiagnosticResult type, types.ts:32-41):
- `canBeFixed: true` with `newInstallationId`: Repository found in another installation
- `canBeFixed: false` with reason:
  - `no-installation`: No installation has access
  - `repository-not-found`: Repository not found in database
  - `diagnosis-failed`: Error during diagnosis

The recovery process resets all content statuses to `idle` and clears error codes, allowing re-ingestion under the new installation (actions.ts:534-546).

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/diagnostic-modal.tsx:23-206](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:424-549](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/types.ts:32-42]()

### Storage Layer Integration

Vector stores use two storage systems:

1. **Supabase PostgreSQL** (with pgvector extension) for embeddings and metadata
2. **Supabase Storage** for document source files

The storage prefix for document files is defined as:
```typescript
const DOCUMENT_VECTOR_STORE_STORAGE_PREFIX = "vector-stores";
```

This corresponds to a Supabase bucket where PDF and text files are stored before ingestion.

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:53](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:43-52]()

## 3.3 RAG System and Query Execution

The RAG pipeline integrates document processing, embedding generation, and similarity search to enable context-aware generation operations. This section describes how processed documents are chunked, embedded, stored, and queried. The RAG implementation is primarily located in the `@giselles-ai/rag` package and supporting libraries in `lib/vector-stores/`.

### RAG Pipeline Architecture

```mermaid
graph TB
    subgraph "Document Ingestion"
        Upload["Document Upload<br/>PDF, Text, Markdown"]
        Extract["extractPdfText() / extractText()"]
        Chunk["Chunking Strategy<br/>Paragraph/sentence-based"]
        Embed["Embedding Generation<br/>AI SDK embedMany()"]
    end
    
    subgraph "Vector Store"
        PGVector["PostgreSQL + pgvector<br/>Similarity search"]
        Metadata["Metadata Tables<br/>githubRepositoryContentStatus<br/>documentVectorStoreSources"]
    end
    
    subgraph "Query Execution"
        QueryNode["Query Node in Workflow"]
        TemplateResolution["Resolve template references<br/>{{sourceNode.text}}"]
        GenerateEmbedding["Generate query embedding"]
        SimilaritySearch["pgvector similarity search<br/><-> operator"]
        ResultRanking["Rank by cosine similarity"]
    end
    
    subgraph "Generation Context"
        ContextAssembly["Assemble context from results"]
        LLMGeneration["LLM Generation<br/>generateText/generateContent"]
    end
    
    Upload --> Extract
    Extract --> Chunk
    Chunk --> Embed
    Embed --> PGVector
    Embed --> Metadata
    
    QueryNode --> TemplateResolution
    TemplateResolution --> GenerateEmbedding
    GenerateEmbedding --> SimilaritySearch
    SimilaritySearch --> PGVector
    PGVector --> ResultRanking
    ResultRanking --> ContextAssembly
    ContextAssembly --> LLMGeneration
```

**Sources:** [packages/document-preprocessor/src/index.ts:1-13](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:1-42]()

### Chunking Strategies

After text extraction via `extractPdfText()` or `extractText()`, documents are split into chunks for embedding. The chunking implementation varies by content type and is handled by the ingestion pipeline (not directly visible in the provided vector store UI files).

**Content Type Chunking Strategies**

| Content Type | Strategy | Metadata Displayed in UI | Metadata Location in Code |
|--------------|----------|--------------------------|---------------------------|
| Code (blob) | File-based | Commit SHA (e.g., `abc1234`) | `blobStatus.metadata.lastIngestedCommitSha` (repository-item.tsx:350-356) |
| Issues | Issue-based | Issue number (e.g., `#42`) | `issueStatus.metadata.lastIngestedIssueNumber` (repository-item.tsx:444-448) |
| Pull Requests | PR-based | PR number (e.g., `#123`) | `pullRequestStatus.metadata.lastIngestedPrNumber` (repository-item.tsx:538-542) |
| PDF Documents | Page/paragraph-based | Page number, file name | `documentVectorStoreSources.fileName` (document-vector-store-item.tsx:280-295) |
| Plain Text | Paragraph-based | Source file name | `documentVectorStoreSources.fileName` |

The `metadata` field in `githubRepositoryContentStatus` stores chunk-specific information that is displayed in the UI after successful ingestion (status = `completed`).

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:346-361](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:438-452](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx:286-295]()

### Embedding Generation

Embeddings are generated using the AI SDK's `embedMany()` function with the configured embedding profile:

```typescript
// Conceptual flow (actual implementation in lib/vector-stores)
const chunks = splitDocumentIntoChunks(text);
const embeddings = await embedMany({
  model: embeddingProfile.model,
  values: chunks.map(chunk => chunk.text),
});

// Store in pgvector
for (let i = 0; i < chunks.length; i++) {
  await db.insert(embeddingTable).values({
    content: chunks[i].text,
    embedding: embeddings[i],
    embeddingProfileId: profile.id,
    metadata: chunks[i].metadata,
  });
}
```

Each embedding profile (OpenAI Small, OpenAI Large, Google, Cohere) uses a different dimension size, which affects storage requirements and query performance.

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/github-embedding-profiles.ts:1-13]()

### Query Resolution and Template References

Query nodes in workflows support template references to dynamically include content from source nodes:

```typescript
// Example query template
const queryTemplate = "Find code related to {{sourceNode.text}}";

// Resolution process
const resolvedQuery = resolveTemplateReferences(queryTemplate, sourceNodes);
// Result: "Find code related to authentication implementation"
```

The resolved query text is then embedded using the same embedding profile as the target vector store, ensuring semantic similarity search works correctly.

**Sources:** Based on workflow node query patterns in the codebase (implementation details in query execution layer not shown in provided files)

### Similarity Search with pgvector

PostgreSQL with the pgvector extension provides efficient similarity search using the cosine distance operator (`<->`):

```sql
-- Conceptual query structure
SELECT 
  content,
  metadata,
  1 - (embedding <-> $queryEmbedding) as similarity
FROM embeddings
WHERE embedding_profile_id = $profileId
  AND repository_index_db_id = $repositoryDbId  -- or document_vector_store_db_id
ORDER BY embedding <-> $queryEmbedding
LIMIT $topK;
```

The `<->` operator computes cosine distance between the query embedding and stored embeddings. Results are ranked by similarity (1 - distance), with the most similar chunks returned first.

**Sources:** Based on pgvector usage patterns (actual SQL in lib/vector-stores not shown in provided files)

### Query Execution and Context Assembly

The query execution flow integrates workflow nodes with vector stores through the Giselle Engine. While the detailed implementation is in the `@giselles-ai/rag` and engine packages (see page 2), the vector store UI surfaces key configuration:

**Vector Store Configuration for Queries**

The vector store system provides:
1. **Store Selection**: Users select which GitHub or Document vector store to query
2. **Embedding Profile**: Determines which embedding space to search within
3. **Content Type Filtering**: For GitHub stores, filter by blob/issue/pull_request
4. **Status Visibility**: UI shows which content is ready (`completed`) for querying

**Query Execution Components**

```mermaid
graph LR
    subgraph "Vector_Store_Configuration"
        RepositoryItem["RepositoryItem<br/>repository-item.tsx"]
        DocumentItem["DocumentVectorStoreItem<br/>document-vector-store-item.tsx"]
        EmbeddingProfileSelector["Embedding Profile Selection<br/>GITHUB_EMBEDDING_PROFILES"]
    end
    
    subgraph "Database_Layer"
        PGVector["PostgreSQL + pgvector<br/>Cosine similarity: <->"]
        EmbeddingTables["Embedding tables<br/>(by profile ID)"]
        MetadataTables["githubRepositoryContentStatus<br/>documentVectorStoreSources"]
    end
    
    subgraph "Query_Interface"
        RAGPackage["@giselles-ai/rag<br/>Vector similarity search"]
        QueryServices["Vector Store Query Services<br/>GitHub/Document/Issue/PR"]
    end
    
    subgraph "Workflow_Integration"
        QueryNode["Query Workflow Node<br/>Uses vector store as context"]
        TextGenNode["TextGeneration Node<br/>Receives context from query"]
    end
    
    RepositoryItem --> EmbeddingProfileSelector
    DocumentItem --> EmbeddingProfileSelector
    EmbeddingProfileSelector --> EmbeddingTables
    
    EmbeddingTables --> PGVector
    MetadataTables --> PGVector
    
    PGVector --> RAGPackage
    RAGPackage --> QueryServices
    QueryServices --> QueryNode
    QueryNode --> TextGenNode
```

**Vector Store Status and Query Readiness**

Only vector stores with `status='completed'` content are ready for queries. The UI displays:
- **Ready badge** (green): Content ingested and queryable
- **Processing badge** (blue): Ingestion in progress, not yet queryable
- **Failed badge** (red): Ingestion failed, requires diagnostic check
- **Pending badge** (yellow): Ingestion queued, waiting to start

The `StatusIndicator` and `IngestStatusBadge` components visualize query readiness (repository-item.tsx:289-293, document-vector-store-item.tsx:63-127).

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:240-320](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx:63-127]()

### Error Handling and Retry Logic

The vector store system implements automatic retry logic for failed ingestion operations:

| Error Code | Description | Retry Strategy |
|------------|-------------|----------------|
| `DOCUMENT_NOT_FOUND` | Repository/file not accessible | Manual fix via diagnostic modal |
| `DOCUMENT_FETCH_ERROR` | Transient fetch failure | Exponential backoff with `retryAfter` |
| `DOCUMENT_RATE_LIMITED` | GitHub rate limit hit | Wait until rate limit reset |
| `DOCUMENT_TOO_LARGE` | File exceeds size limit | No retry (permanent failure) |

The `retryAfter` timestamp in `githubRepositoryContentStatus` controls when a failed ingestion can be retried. Users can manually trigger ingestion once `retryAfter` has passed.

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/types.ts:1-5](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:98-107](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/error-messages.ts]()

### Integration with Workflow Nodes

Vector stores are consumed by workflow nodes through node-specific interfaces:

1. **GitHub Vector Store Node**: Queries code and PR embeddings using repository-specific profiles
2. **Document Vector Store Node**: Queries uploaded document embeddings
3. **Query Node**: Generic interface supporting both GitHub and Document stores

Node properties panels allow users to select the target vector store and configure query parameters (e.g., `topK` results, embedding profile selection).

**Sources:** Based on workflow node patterns described in the architecture diagrams (detailed implementation in workflow-designer-ui not shown in provided files)

---

# Page: Document Processing Pipeline

# Document Processing Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/packages-license.md](docs/packages-license.md)
- [packages/document-preprocessor/README.md](packages/document-preprocessor/README.md)
- [packages/document-preprocessor/package.json](packages/document-preprocessor/package.json)
- [packages/document-preprocessor/src/global.d.ts](packages/document-preprocessor/src/global.d.ts)
- [packages/document-preprocessor/src/index.ts](packages/document-preprocessor/src/index.ts)
- [packages/document-preprocessor/src/pdf.ts](packages/document-preprocessor/src/pdf.ts)
- [packages/document-preprocessor/src/text.test.ts](packages/document-preprocessor/src/text.test.ts)
- [packages/document-preprocessor/src/text.ts](packages/document-preprocessor/src/text.ts)
- [packages/document-preprocessor/src/types.ts](packages/document-preprocessor/src/types.ts)
- [packages/document-preprocessor/tsconfig.json](packages/document-preprocessor/tsconfig.json)
- [packages/document-preprocessor/tsup.config.ts](packages/document-preprocessor/tsup.config.ts)
- [packages/document-preprocessor/turbo.json](packages/document-preprocessor/turbo.json)
- [packages/document-preprocessor/vitest.config.mts](packages/document-preprocessor/vitest.config.mts)

</details>



## Purpose and Scope

The Document Processing Pipeline is implemented in the `@giselle-sdk/document-preprocessor` package and provides low-level utilities for converting raw document binaries into structured text and image outputs suitable for downstream RAG ingestion. This page documents the preprocessing layer that transforms PDFs, plain text, and Markdown files into normalized content with per-page metadata.

For information about how processed documents are indexed and stored in vector stores, see [Vector Store System](#3.2). For details on the RAG query execution and chunking strategies applied to preprocessed content, see [RAG Implementation and Query Execution](#3.3).

---

## Architecture Overview

The document-preprocessor package exposes three primary functions that operate on binary inputs and return structured results. All functions support abort signals for cancellation and implement consistent error handling patterns.

```mermaid
graph TB
    subgraph "Public API"
        extractText["extractText()<br/>packages/document-preprocessor/src/text.ts:13"]
        extractPdfText["extractPdfText()<br/>packages/document-preprocessor/src/pdf.ts:21"]
        renderPdfPageImages["renderPdfPageImages()<br/>packages/document-preprocessor/src/pdf.ts:56"]
    end
    
    subgraph "Internal Utilities"
        toUint8Array["toUint8Array<br/>src/internal/binary.js"]
        normalizeExtractedText["normalizeExtractedText<br/>src/internal/text-normalizer.js"]
        withPdfDocument["withPdfDocument<br/>src/internal/pdfium.js"]
        assertNotAborted["assertNotAborted<br/>src/internal/abort.js"]
    end
    
    subgraph "External Dependencies"
        pdfium["@embedpdf/pdfium<br/>PDFium WASM bindings"]
        pngjs["pngjs<br/>PNG encoding"]
    end
    
    extractText --> toUint8Array
    extractText --> assertNotAborted
    
    extractPdfText --> toUint8Array
    extractPdfText --> withPdfDocument
    extractPdfText --> normalizeExtractedText
    extractPdfText --> assertNotAborted
    
    renderPdfPageImages --> toUint8Array
    renderPdfPageImages --> withPdfDocument
    renderPdfPageImages --> assertNotAborted
    renderPdfPageImages --> pngjs
    
    withPdfDocument --> pdfium
```

**Sources:** [packages/document-preprocessor/src/index.ts:1-13](), [packages/document-preprocessor/src/pdf.ts:1-138](), [packages/document-preprocessor/src/text.ts:1-37](), [packages/document-preprocessor/README.md:1-154]()

---

## Public API Surface

The package exports three main functions through [packages/document-preprocessor/src/index.ts:1-13]():

| Function | Input | Output | Purpose |
|----------|-------|--------|---------|
| `extractText` | Plain text/Markdown binary | `TextExtractionResult` | UTF-8 decoding of text files |
| `extractPdfText` | PDF binary | `PdfTextExtractionResult` | Page-by-page text extraction with normalization |
| `renderPdfPageImages` | PDF binary | `PdfImageRenderResult` | PNG rendering at configurable DPI |

All functions accept `BinaryDataInput` which can be `ArrayBuffer`, `ArrayBufferView`, `Uint8Array`, or Node.js `Buffer`. This flexibility accommodates various input sources including file system reads, HTTP responses, and in-memory buffers.

**Sources:** [packages/document-preprocessor/src/types.ts:1-53](), [packages/document-preprocessor/README.md:82-127]()

---

## PDF Text Extraction

### Processing Flow

The `extractPdfText` function implements a page-by-page extraction pipeline defined in [packages/document-preprocessor/src/pdf.ts:21-54]():

```mermaid
sequenceDiagram
    participant Caller
    participant extractPdfText
    participant withPdfDocument
    participant PDFium as "@embedpdf/pdfium"
    participant normalizeExtractedText
    
    Caller->>extractPdfText: "Binary input + options"
    extractPdfText->>extractPdfText: "toUint8Array(input)"
    extractPdfText->>withPdfDocument: "bytes, {password, signal}"
    withPdfDocument->>PDFium: "document.getPageCount()"
    PDFium-->>withPdfDocument: "totalPages"
    
    loop "For each page (up to maxPages)"
        extractPdfText->>extractPdfText: "assertNotAborted(signal)"
        extractPdfText->>PDFium: "document.loadPage(index)"
        PDFium-->>extractPdfText: "page"
        extractPdfText->>PDFium: "page.getText()"
        PDFium-->>extractPdfText: "rawText"
        extractPdfText->>normalizeExtractedText: "rawText"
        normalizeExtractedText-->>extractPdfText: "normalized text"
        extractPdfText->>PDFium: "page.close()"
    end
    
    extractPdfText-->>Caller: "{totalPages, pages[]}"
```

### Configuration Options

The `PdfTextExtractionOptions` interface defined in [packages/document-preprocessor/src/types.ts:14-18]() supports:

- **password**: Optional string for encrypted PDFs
- **maxPages**: Limit extraction to first N pages (useful for preview operations)
- **signal**: `AbortSignal` for cancellation

The `calculatePageLimit` helper in [packages/document-preprocessor/src/pdf.ts:132-137]() determines the actual page range by taking the minimum of `totalPages` and `maxPages`.

### Text Normalization

Raw text extracted from PDFium undergoes normalization through the `normalizeExtractedText` function (implementation in `src/internal/text-normalizer.js`). This process:

- Repairs hyphenated words split across lines
- Normalizes whitespace sequences
- Removes spurious control characters
- Preserves paragraph structure

The normalized text is stored in the `PdfTextPage` structure with `pageNumber` (1-indexed) and `text` fields.

**Sources:** [packages/document-preprocessor/src/pdf.ts:21-54](), [packages/document-preprocessor/src/types.ts:9-23](), [packages/document-preprocessor/README.md:36-50]()

---

## PDF Image Rendering

### Rendering Pipeline

The `renderPdfPageImages` function in [packages/document-preprocessor/src/pdf.ts:56-99]() converts PDF pages to PNG images using a configurable DPI setting:

```mermaid
graph TB
    Input["BinaryDataInput"]
    toUint8Array["toUint8Array()"]
    withPdfDocument["withPdfDocument()"]
    
    subgraph "Per-Page Processing"
        assertNotAborted["assertNotAborted(signal)"]
        loadPage["document.loadPage(index)"]
        render["page.render({scale, ...})"]
        encodeRgbaToPng["encodeRgbaToPng(data, width, height)"]
        pageClose["page.close()"]
    end
    
    PdfImagePage["PdfImagePage{<br/>pageNumber,<br/>width,<br/>height,<br/>png: Uint8Array}"]
    
    Input --> toUint8Array
    toUint8Array --> withPdfDocument
    withPdfDocument --> assertNotAborted
    assertNotAborted --> loadPage
    loadPage --> render
    render --> encodeRgbaToPng
    encodeRgbaToPng --> pageClose
    pageClose --> PdfImagePage
```

### DPI Calculation

The scale factor is computed in [packages/document-preprocessor/src/pdf.ts:18-19,62-63]():

```
POINTS_PER_INCH = 72
DEFAULT_TARGET_DPI = 144
scale = max(targetDpi / POINTS_PER_INCH, 0.1)
```

A `targetDpi` of 144 produces a scale of 2.0, doubling the resolution of the base 72 DPI PDF coordinate system. The minimum scale of 0.1 prevents rendering errors from extremely small values.

### PNG Encoding

The `encodeRgbaToPng` function in [packages/document-preprocessor/src/pdf.ts:101-130]() uses the `pngjs` library to convert RGBA pixel data from PDFium into PNG format:

1. Creates a `PNG` instance with `inputHasAlpha: true` and `colorType: 6` (RGB + alpha)
2. Copies RGBA bytes into the PNG data buffer
3. Streams encoded chunks into a Buffer array via the `pack()` pipeline
4. Returns a `Uint8Array` view over the concatenated buffer without copying

The resulting PNG can be stored in blob storage or passed to image-based LLM models for multimodal RAG.

### Form Field Rendering

The `renderFormFields` option (default `true`) in [packages/document-preprocessor/src/pdf.ts:79]() controls whether interactive PDF form elements are rendered as part of the image. This is useful for capturing filled form data in document previews.

**Sources:** [packages/document-preprocessor/src/pdf.ts:56-130](), [packages/document-preprocessor/src/types.ts:25-43](), [packages/document-preprocessor/README.md:53-68]()

---

## Text and Markdown Processing

The `extractText` function in [packages/document-preprocessor/src/text.ts:13-36]() provides a simpler processing path for non-PDF documents:

```mermaid
graph LR
    BinaryInput["BinaryDataInput"]
    signalCheck["signal?.throwIfAborted()"]
    toBuffer["Convert to Buffer"]
    decode["buffer.toString(encoding)"]
    result["TextExtractionResult{text}"]
    
    BinaryInput --> signalCheck
    signalCheck --> toBuffer
    toBuffer --> decode
    decode --> result
```

### Encoding Support

The function accepts a `BufferEncoding` parameter (default `"utf-8"`) to handle various text encodings. The conversion logic in [packages/document-preprocessor/src/text.ts:21-31]() handles multiple input types:

- **Buffer**: Used directly
- **Uint8Array**: Creates Buffer view over underlying ArrayBuffer
- **ArrayBufferView**: Extracts buffer with correct offset and length
- **ArrayBuffer**: Converts to Buffer

No text normalization is applied to plain text files, preserving the exact content including whitespace and formatting.

**Sources:** [packages/document-preprocessor/src/text.ts:1-37](), [packages/document-preprocessor/src/text.test.ts:1-58](), [packages/document-preprocessor/README.md:20-32]()

---

## Internal Utilities

### Abort Signal Handling

The `assertNotAborted` utility (referenced in [packages/document-preprocessor/src/pdf.ts:4,37,74]()) checks the abort signal state at critical points in the processing pipeline. This enables responsive cancellation of long-running PDF operations, which is important for:

- User-initiated cancellation in upload flows
- Timeout enforcement for large documents
- Resource cleanup on service shutdown

All public functions accept an optional `signal` parameter in their options objects.

### Binary Data Conversion

The `toUint8Array` helper (referenced in [packages/document-preprocessor/src/pdf.ts:5,25,60]()) normalizes various binary input formats to `Uint8Array` for consistent handling by PDFium. This abstraction allows callers to pass data from different sources without pre-conversion.

### PDFium Document Lifecycle

The `withPdfDocument` wrapper (referenced in [packages/document-preprocessor/src/pdf.ts:6,28,65]()) manages PDFium document lifecycle:

1. Loads the PDF document with optional password
2. Provides the document handle to a callback function
3. Ensures proper cleanup even if the callback throws
4. Propagates abort signals to nested operations

The pattern guarantees that PDFium resources are released, preventing memory leaks in long-running processes.

**Sources:** [packages/document-preprocessor/src/pdf.ts:1-138](), [packages/document-preprocessor/README.md:70-79]()

---

## Type System

### Input Types

The `BinaryDataInput` union type in [packages/document-preprocessor/src/types.ts:3-7]() accepts:

```typescript
type BinaryDataInput =
  | ArrayBuffer
  | ArrayBufferView
  | Uint8Array
  | Buffer
```

This broad compatibility supports integration with various I/O systems including file streams, HTTP clients, and in-memory data structures.

### Result Types

The package defines three result interfaces:

| Type | Fields | Description |
|------|--------|-------------|
| `TextExtractionResult` | `text: string` | Simple text content |
| `PdfTextExtractionResult` | `totalPages: number`<br/>`pages: PdfTextPage[]` | Page-indexed text with metadata |
| `PdfImageRenderResult` | `totalPages: number`<br/>`pages: PdfImagePage[]` | Rendered images with dimensions |

The `PdfTextPage` structure in [packages/document-preprocessor/src/types.ts:9-12]() contains:
- `pageNumber`: 1-indexed page number
- `text`: Normalized text content

The `PdfImagePage` structure in [packages/document-preprocessor/src/types.ts:25-30]() contains:
- `pageNumber`: 1-indexed page number
- `width`: Image width in pixels
- `height`: Image height in pixels
- `png`: PNG-encoded image as Uint8Array

**Sources:** [packages/document-preprocessor/src/types.ts:1-53](), [packages/document-preprocessor/src/index.ts:1-13]()

---

## Security Considerations

### PDFium Sandboxing

The package uses `@embedpdf/pdfium` which runs in a sandboxed WASM environment, mitigating risks from malicious PDF files. However, as noted in [packages/document-preprocessor/README.md:150-154](), users should:

- Keep dependencies updated
- Monitor security advisories for PDFium vulnerabilities
- Enforce file size limits to prevent resource exhaustion
- Set processing timeout limits via abort signals

### Password-Protected PDFs

When processing password-protected PDFs, be aware that:

- Not all encryption schemes are supported by PDFium
- Password validation occurs during document loading
- Failed authentication throws an error that should be caught and handled gracefully
- Sensitive passwords should not be logged or stored

### Resource Limits

To prevent denial-of-service attacks, production deployments should:

- Limit maximum input file size
- Use `maxPages` option to cap processing scope
- Set abort signal timeouts for long-running operations
- Monitor memory usage during concurrent processing

**Sources:** [packages/document-preprocessor/README.md:149-154]()

---

## Integration with RAG System

### Document Upload Flow

The document-preprocessor serves as the entry point in the RAG ingestion pipeline:

```mermaid
graph LR
    Upload["Document Upload<br/>(PDF, TXT, MD)"]
    Preprocess["Document Preprocessor<br/>extractPdfText() or<br/>extractText()"]
    Chunk["Chunking Strategy<br/>(see #3.3)"]
    Embed["Embedding Generation<br/>(see #3.3)"]
    Store["Vector Store<br/>(see #3.2)"]
    
    Upload --> Preprocess
    Preprocess --> Chunk
    Chunk --> Embed
    Embed --> Store
```

### Output Format

Preprocessed documents produce structured pages that can be:

1. **Chunked** using strategies defined in the RAG implementation (semantic chunking, fixed-size windows, etc.)
2. **Embedded** via OpenAI or Google embedding models
3. **Stored** in PostgreSQL with pgvector extension

The `pageNumber` field enables provenance tracking, allowing RAG queries to cite specific page numbers in retrieved chunks.

### Image Processing for Multimodal RAG

For documents with complex visual elements:

1. Use `renderPdfPageImages` to generate PNG representations
2. Store images in Supabase Storage (see [Storage Architecture](#2.4))
3. Pass images to multimodal LLMs alongside text chunks during query time

This enables RAG over diagrams, charts, and other visual content that text extraction alone cannot capture.

**Sources:** [packages/document-preprocessor/README.md:1-154](), high-level diagrams (Diagram 5)

---

## Build Configuration

### TypeScript Configuration

The package uses `@giselles-ai/tsconfig/node-library.json` as the base configuration in [packages/document-preprocessor/tsconfig.json:2](), targeting Node.js 18+ environments.

### Build Setup

The tsup configuration in [packages/document-preprocessor/tsup.config.ts:1-11]() produces:

- **Formats**: CommonJS and ESM
- **Target**: node18
- **External dependencies**: `@embedpdf/pdfium`, `pngjs` (not bundled)
- **Outputs**: Type definitions (`.d.ts`), source maps, and compiled JavaScript

### Package Metadata

The package.json in [packages/document-preprocessor/package.json:1-32]() declares:

- **Main entry**: `dist/index.js`
- **Type definitions**: `dist/index.d.ts`
- **Keywords**: pdf, preprocessing, rag
- **License**: MIT

**Sources:** [packages/document-preprocessor/tsup.config.ts:1-11](), [packages/document-preprocessor/tsconfig.json:1-10](), [packages/document-preprocessor/package.json:1-32]()

---

# Page: Vector Store Management

# Vector Store Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/configure-sources-dialog.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/configure-sources-dialog.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/data.ts](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/data.ts)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/diagnostic-modal.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/diagnostic-modal.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-embedding-profiles.ts](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-embedding-profiles.ts)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-store-create-dialog.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-store-create-dialog.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-vector-store-list.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-vector-store-list.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/page.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/page.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/layout.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/layout.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/navigation-layout.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/navigation-layout.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/page.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/page.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-list.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-list.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-registration-dialog.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-registration-dialog.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/sidebar-menu.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/sidebar-menu.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/types.ts](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/types.ts)
- [internal-packages/ui/components/form-field.tsx](internal-packages/ui/components/form-field.tsx)
- [internal-packages/ui/components/section-header.tsx](internal-packages/ui/components/section-header.tsx)
- [internal-packages/ui/components/status-indicator.tsx](internal-packages/ui/components/status-indicator.tsx)

</details>



## Purpose and Scope

This document describes the Vector Store Management system, which provides user interfaces and backend operations for configuring and managing vector stores within teams. Vector stores enable Retrieval-Augmented Generation (RAG) by ingesting and indexing content from GitHub repositories or uploaded documents, making this content searchable through semantic similarity queries.

The system supports two types of vector stores:
1. **GitHub Vector Stores**: Index code, issues, and pull requests from GitHub repositories
2. **Document Vector Stores**: Index uploaded PDF and text documents

For information about how vector stores are queried during workflow execution, see [RAG System and Query Execution](#3.3). For details on document preprocessing and text extraction, see [Document Processing Pipeline](#3.1).

---

## System Architecture Overview

The Vector Store Management system consists of UI components for configuration, server actions for data operations, and background ingestion pipelines that process content and generate embeddings.

**Architecture Overview**

```mermaid
graph TB
    subgraph "User Interface Layer"
        GitHubUI["GitHub Vector Stores UI<br/>/settings/team/vector-stores/page.tsx"]
        DocumentUI["Document Vector Stores UI<br/>/settings/team/vector-stores/document/page.tsx"]
        RepositoryItem["RepositoryItem<br/>repository-item.tsx"]
        DocumentItem["DocumentVectorStoreItem<br/>document-vector-store-item.tsx"]
        RegistrationDialog["RepositoryRegistrationDialog"]
        ConfigureDialog["ConfigureSourcesDialog"]
        CreateDialog["DocumentVectorStoreCreateDialog"]
    end
    
    subgraph "Server Actions"
        RegisterRepo["registerRepositoryIndex"]
        UpdateRepo["updateRepositoryIndex"]
        TriggerIngest["triggerManualIngest"]
        DeleteRepo["deleteRepositoryIndex"]
        CreateDoc["createDocumentVectorStore"]
        UpdateDoc["updateDocumentVectorStore"]
        DeleteDoc["deleteDocumentVectorStore"]
    end
    
    subgraph "Database Tables"
        RepoIndex["githubRepositoryIndex"]
        ContentStatus["githubRepositoryContentStatus"]
        RepoProfiles["githubRepositoryEmbeddingProfiles"]
        DocStores["documentVectorStores"]
        DocProfiles["documentEmbeddingProfiles"]
        DocSources["documentVectorStoreSources"]
    end
    
    subgraph "Processing"
        ProcessRepo["processRepository<br/>lib/vector-stores/github"]
        IngestPipeline["Document Ingestion<br/>API Routes"]
    end
    
    GitHubUI --> RepositoryItem
    GitHubUI --> RegistrationDialog
    RepositoryItem --> ConfigureDialog
    
    DocumentUI --> DocumentItem
    DocumentUI --> CreateDialog
    DocumentItem --> ConfigureDialog
    
    RegistrationDialog --> RegisterRepo
    ConfigureDialog --> UpdateRepo
    RepositoryItem --> TriggerIngest
    RepositoryItem --> DeleteRepo
    
    CreateDialog --> CreateDoc
    DocumentItem --> UpdateDoc
    DocumentItem --> DeleteDoc
    
    RegisterRepo --> RepoIndex
    RegisterRepo --> ContentStatus
    RegisterRepo --> RepoProfiles
    UpdateRepo --> ContentStatus
    UpdateRepo --> RepoProfiles
    TriggerIngest --> ProcessRepo
    
    CreateDoc --> DocStores
    CreateDoc --> DocProfiles
    UpdateDoc --> DocStores
    UpdateDoc --> DocProfiles
    DeleteDoc --> DocSources
    
    ProcessRepo --> ContentStatus
    IngestPipeline --> DocSources
```

**Sources:**
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/page.tsx:1-80]()
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/page.tsx:1-48]()
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:1-986]()

---

## GitHub Vector Stores

### Registration and Configuration

GitHub Vector Stores are registered through the `RepositoryRegistrationDialog` component, which allows users to select repositories from their installed GitHub Apps.

**Registration Flow**

```mermaid
sequenceDiagram
    participant User
    participant RegistrationDialog
    participant registerRepositoryIndex
    participant validateGitHubAccess
    participant Database
    participant ProcessRepo
    
    User->>RegistrationDialog: Click "Register Repository"
    RegistrationDialog->>RegistrationDialog: Display owner/repo selectors
    User->>RegistrationDialog: Select owner, repository, sources, profiles
    RegistrationDialog->>registerRepositoryIndex: Submit registration
    registerRepositoryIndex->>validateGitHubAccess: Check installation access
    validateGitHubAccess-->>registerRepositoryIndex: Validation result
    
    registerRepositoryIndex->>Database: Lock team row (quota enforcement)
    registerRepositoryIndex->>Database: Check existing repository
    registerRepositoryIndex->>Database: Check quota limit
    
    alt Quota available
        registerRepositoryIndex->>Database: Insert githubRepositoryIndex
        registerRepositoryIndex->>Database: Insert githubRepositoryEmbeddingProfiles
        registerRepositoryIndex->>Database: Insert githubRepositoryContentStatus
        registerRepositoryIndex-->>RegistrationDialog: Success
        RegistrationDialog->>ProcessRepo: Trigger background ingestion
    else Quota exceeded
        registerRepositoryIndex-->>RegistrationDialog: Error: quota reached
    end
```

The registration process enforces team-based quotas and validates GitHub access before creating database records.

**Key Components:**

- **RepositoryRegistrationDialog** ([apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-registration-dialog.tsx:41-477]()): Manages the UI for selecting repositories and configuring initial settings
- **registerRepositoryIndex** ([apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:107-251]()): Server action that validates access, checks quotas, and creates database records
- **validateGitHubAccess** ([apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:62-105]()): Verifies the installation can access the repository

**Sources:**
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-registration-dialog.tsx:41-477]()
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:62-251]()

### Content Type Management

Each GitHub repository can ingest three content types: code (blob), issues, and pull requests. Code ingestion is mandatory and cannot be disabled.

**Content Type Configuration**

| Content Type | Database Value | UI Label | Mandatory | Description |
|--------------|----------------|----------|-----------|-------------|
| `blob` | `"blob"` | Code | Yes | Source code files from the repository |
| `issue` | `"issue"` | Issues | No | Issue titles, descriptions, and comments |
| `pull_request` | `"pull_request"` | Pull Requests | No | Merged PR content and discussions |

Content types are managed per embedding profile, meaning each profile can have different content types enabled. The `githubRepositoryContentStatus` table tracks the status for each combination of repository, embedding profile, and content type.

**Content Status States**

```mermaid
stateDiagram-v2
    [*] --> idle: Initial state
    idle --> running: Manual ingest triggered
    running --> completed: Ingestion successful
    running --> failed: Ingestion error
    completed --> running: Re-ingest triggered
    failed --> idle: Retry after delay
    failed --> running: Manual retry
```

The status tracking includes:
- `status`: Current state (`idle`, `running`, `completed`, `failed`)
- `enabled`: Whether this content type is active
- `errorCode`: Error type if status is `failed` (e.g., `DOCUMENT_NOT_FOUND`)
- `retryAfter`: Timestamp when retry is allowed after failure
- `lastSyncedAt`: Last successful synchronization timestamp
- `metadata`: Content-specific metadata (e.g., `lastIngestedCommitSha`, `lastIngestedIssueNumber`)

**Sources:**
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/configure-sources-dialog.tsx:40-323]()
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:240-564]()

### Embedding Profile Selection

Multiple embedding profiles can be selected for each repository, allowing the same content to be indexed with different embedding models. This supports use cases where different downstream applications require different embedding dimensions or providers.

**Available Embedding Profiles**

The `GITHUB_EMBEDDING_PROFILES` constant ([apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/github-embedding-profiles.ts]()) defines supported profiles:

| Profile ID | Name | Provider | Dimensions |
|------------|------|----------|------------|
| `1` | OpenAI Small | OpenAI | 1536 |
| `2` | OpenAI Large | OpenAI | 3072 |
| `3` | Google Gecko | Google | 768 |

Each profile is stored in the `githubRepositoryEmbeddingProfiles` table, and content statuses are tracked separately for each profile-content type combination.

**Profile Management:**
- At least one profile must be selected
- Profiles can be added or removed via the `ConfigureSourcesDialog`
- Removing a profile deletes its content statuses and associated embeddings
- Adding a new profile triggers ingestion for all enabled content types

**Sources:**
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-registration-dialog.tsx:378-432]()
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/configure-sources-dialog.tsx:186-241]()
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:257-409]()

### Repository Item Display and Status

The `RepositoryItem` component displays each registered repository with status cards for each embedding profile.

**Repository Item Structure**

```mermaid
graph LR
    RepositoryItem["RepositoryItem"]
    Header["Repository Header<br/>owner/repo + actions menu"]
    ProfileCards["Embedding Profile Cards"]
    Card1["OpenAI Small Card"]
    Card2["OpenAI Large Card"]
    Card3["Google Gecko Card"]
    
    ContentStatus1["Code: Status<br/>Issues: Status<br/>PRs: Status"]
    ContentStatus2["Code: Status<br/>Issues: Status<br/>PRs: Status"]
    ContentStatus3["Code: Status<br/>Issues: Status<br/>PRs: Status"]
    
    RepositoryItem --> Header
    RepositoryItem --> ProfileCards
    ProfileCards --> Card1
    ProfileCards --> Card2
    ProfileCards --> Card3
    
    Card1 --> ContentStatus1
    Card2 --> ContentStatus2
    Card3 --> ContentStatus3
```

Each embedding profile card shows:
- Profile name and metadata
- Status for each content type (code, issues, PRs)
- Last sync timestamp
- Ingestion metadata (commit SHA, issue number, PR number)
- Error messages with retry information

**Status Display Logic** ([apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:283-374]()):
- `enabled=false`: Shows "Disabled" badge
- `status=completed`: Shows "Enabled" badge with success styling
- `status=running` or `isIngesting`: Shows "Running" status with indicator
- `status=idle`: Shows "Idle" status
- `status=failed`: Shows "Error" status with error message and optional "Check ↗" link

**Sources:**
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:56-237]()
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:240-564]()

### Manual Ingestion

Users can trigger manual ingestion through the "Ingest Now" action in the repository menu. The system checks whether ingestion is allowed before proceeding.

**Ingestability Rules** ([apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:929-973]()):

1. At least one enabled content type must be in an ingestable state
2. A content type is ingestable if:
   - Status is `idle`, `completed`, or
   - Status is `running` but hasn't been updated in 15 minutes (stale threshold), or
   - Status is `failed` and `retryAfter` timestamp has passed
3. Repository must have a blob content status configured

**Manual Ingest Flow:**

```mermaid
sequenceDiagram
    participant User
    participant RepositoryItem
    participant triggerManualIngest
    participant checkIngestability
    participant executeManualIngest
    participant processRepository
    
    User->>RepositoryItem: Click "Ingest Now"
    RepositoryItem->>triggerManualIngest: Request ingestion
    triggerManualIngest->>checkIngestability: Validate ingestability
    
    alt Can ingest
        checkIngestability-->>triggerManualIngest: Allowed
        triggerManualIngest->>executeManualIngest: Schedule processing
        triggerManualIngest-->>RepositoryItem: Success
        RepositoryItem->>RepositoryItem: Update UI to show running
        executeManualIngest->>processRepository: Process in background
    else Cannot ingest
        checkIngestability-->>triggerManualIngest: Blocked (reason)
        triggerManualIngest-->>RepositoryItem: Error message
    end
```

The `executeManualIngest` function uses `after()` ([apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:978-985]()) to schedule background processing, allowing the UI to respond immediately while ingestion proceeds asynchronously.

**Sources:**
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:554-593]()
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:929-985]()
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:90-101]()

### Diagnostic System

When a repository encounters a `DOCUMENT_NOT_FOUND` error, users can access the diagnostic modal to troubleshoot connection issues.

**Diagnostic Flow**

```mermaid
graph TB
    Start["User clicks Check ↗"]
    OpenModal["DiagnosticModal opens"]
    RunDiag["diagnoseRepositoryConnection"]
    
    CheckInstalls["Iterate through user's<br/>GitHub App installations"]
    TryAccess["Attempt repository access<br/>with each installation"]
    
    FoundAccess{"Found valid<br/>installation?"}
    CanFix["Result: canBeFixed=true<br/>with newInstallationId"]
    CannotFix["Result: canBeFixed=false<br/>with error reason"]
    
    UserAction{"User action"}
    RestoreConn["Update installation ID<br/>in database"]
    DeleteRepo["Delete repository"]
    
    Start --> OpenModal
    OpenModal --> RunDiag
    RunDiag --> CheckInstalls
    CheckInstalls --> TryAccess
    TryAccess --> FoundAccess
    
    FoundAccess -->|Yes| CanFix
    FoundAccess -->|No| CannotFix
    
    CanFix --> UserAction
    CannotFix --> UserAction
    
    UserAction -->|Restore Connection| RestoreConn
    UserAction -->|Delete| DeleteRepo
```

**Diagnostic Actions:**
- **diagnoseRepositoryConnection** ([apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:424-503]()): Checks all user installations for repository access
- **updateRepositoryInstallation** ([apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:505-549]()): Updates the installation ID and resets content statuses

**Possible Diagnostic Results:**
- `canBeFixed=true`: A valid installation was found; shows "Restore Connection" button
- `canBeFixed=false, reason="no-installation"`: No installation has access; suggests reviewing from Integrations page
- `canBeFixed=false, reason="repository-not-found"`: Repository not found in database
- `canBeFixed=false, reason="diagnosis-failed"`: Error during diagnosis

**Sources:**
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/diagnostic-modal.tsx:23-206]()
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:424-549]()

---

## Document Vector Stores

### Creation and Configuration

Document Vector Stores are created through the `DocumentVectorStoreCreateDialog`, which requires a name and at least one embedding profile.

**Creation Flow**

```mermaid
sequenceDiagram
    participant User
    participant CreateDialog
    participant createDocumentVectorStore
    participant Database
    
    User->>CreateDialog: Click "New Vector Store"
    CreateDialog->>CreateDialog: Display creation form
    User->>CreateDialog: Enter name, select profiles
    CreateDialog->>createDocumentVectorStore: Submit creation
    
    createDocumentVectorStore->>Database: Lock team row (quota enforcement)
    createDocumentVectorStore->>Database: Check quota limit
    
    alt Quota available
        createDocumentVectorStore->>Database: Insert documentVectorStores
        createDocumentVectorStore->>Database: Insert documentEmbeddingProfiles
        createDocumentVectorStore-->>CreateDialog: Success
        CreateDialog->>User: Close dialog, refresh list
    else Quota exceeded
        createDocumentVectorStore-->>CreateDialog: Error: quota reached
        CreateDialog->>User: Display error message
    end
```

**Key Functions:**
- **createDocumentVectorStore** ([apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:616-700]()): Creates vector store with transaction-based quota enforcement
- **validateDocumentEmbeddingProfileIds** ([apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:595-614]()): Validates profile IDs are valid and unique

**Sources:**
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-store-create-dialog.tsx:30-241]()
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:595-700]()

### Document Upload and Management

Document uploads are handled through API routes at `/api/vector-stores/document/[storeId]/documents`.

**Upload Flow**

```mermaid
sequenceDiagram
    participant User
    participant ConfigureDialog
    participant UploadAPI
    participant Supabase
    participant Database
    participant Preprocessor
    
    User->>ConfigureDialog: Select/drag files
    ConfigureDialog->>ConfigureDialog: Validate file types and sizes
    
    alt Valid files
        ConfigureDialog->>UploadAPI: POST multipart/form-data
        UploadAPI->>UploadAPI: Validate store ownership
        
        loop For each file
            UploadAPI->>Supabase: Upload to storage bucket
            UploadAPI->>Database: Insert documentVectorStoreSources
            UploadAPI->>Preprocessor: Trigger ingestion
        end
        
        UploadAPI-->>ConfigureDialog: Success/partial success
        ConfigureDialog->>User: Display upload results
    else Invalid files
        ConfigureDialog->>User: Display validation errors
    end
```

**File Validation:**
- Supported types: PDF, TXT, Markdown ([apps/studio.giselles.ai/lib/vector-stores/document/constants.ts]())
- Maximum size: 10MB per file
- Empty files are rejected
- Validation occurs client-side before upload

**Document Source Tracking:**

Each uploaded document is stored in `documentVectorStoreSources` with:
- `id`: Unique source identifier
- `documentVectorStoreDbId`: Foreign key to parent store
- `fileName`: Original filename
- `storageBucket`: Supabase bucket name
- `storageKey`: Path in storage bucket
- `ingestStatus`: Current ingestion status (`idle`, `running`, `completed`, `failed`)
- `ingestErrorCode`: Error code if ingestion failed

**Sources:**
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx:397-517]()
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx:585-635]()

### Document Vector Store Configuration

The `DocumentVectorStoreConfigureDialog` provides a comprehensive interface for managing store settings, embedding profiles, and source files.

**Configuration Dialog Features:**

```mermaid
graph TB
    ConfigDialog["DocumentVectorStoreConfigureDialog"]
    
    NameSection["Name Input<br/>Update store name"]
    ProfileSection["Embedding Profile Selection<br/>Add/remove profiles"]
    UploadSection["File Upload Area<br/>Drag-and-drop support"]
    SourceList["Source Files List<br/>View and delete sources"]
    
    UpdateAction["updateDocumentVectorStore<br/>Save name + profiles"]
    UploadAction["POST /api/documents<br/>Upload files"]
    DeleteAction["DELETE /api/documents<br/>Remove sources"]
    
    ConfigDialog --> NameSection
    ConfigDialog --> ProfileSection
    ConfigDialog --> UploadSection
    ConfigDialog --> SourceList
    
    NameSection --> UpdateAction
    ProfileSection --> UpdateAction
    UploadSection --> UploadAction
    SourceList --> DeleteAction
```

**Embedding Profile Management:**

Similar to GitHub Vector Stores, Document Vector Stores support multiple embedding profiles. However, Cohere profiles are currently excluded from the selectable options ([apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx:340-344]()).

Available profiles from `DOCUMENT_EMBEDDING_PROFILES` ([apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-embedding-profiles.ts:1-6]()):
- Same as `GITHUB_EMBEDDING_PROFILES`
- Filtered to exclude Cohere provider in UI
- At least one profile must remain selected

**Update Logic** ([apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:702-776]()):
1. Validates name and profile selection
2. Acquires database lock on store row
3. Updates store name
4. Deletes all existing embedding profile associations
5. Inserts new profile associations
6. Transaction ensures consistency

**Sources:**
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx:327-867]()
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:702-776]()

### Document Deletion and Cleanup

Deleting a document vector store involves removing database records and storage files.

**Deletion Flow**

```mermaid
sequenceDiagram
    participant User
    participant DocumentItem
    participant deleteDocumentVectorStore
    participant Database
    participant After
    participant Supabase
    
    User->>DocumentItem: Click "Delete"
    DocumentItem->>deleteDocumentVectorStore: Confirm deletion
    
    deleteDocumentVectorStore->>Database: Begin transaction
    deleteDocumentVectorStore->>Database: Lock store row
    deleteDocumentVectorStore->>Database: Fetch storage sources
    deleteDocumentVectorStore->>Database: Delete documentVectorStoreSources
    deleteDocumentVectorStore->>Database: Delete documentEmbeddingProfiles
    deleteDocumentVectorStore->>Database: Delete documentVectorStores
    deleteDocumentVectorStore->>Database: Commit transaction
    
    deleteDocumentVectorStore->>After: Schedule storage cleanup
    deleteDocumentVectorStore-->>DocumentItem: Success response
    
    After->>After: Group files by bucket
    loop For each bucket
        After->>Supabase: Delete files from storage
    end
```

**Storage Cleanup Strategy** ([apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:843-880]()):

1. Database deletion completes synchronously within transaction
2. Storage cleanup is deferred using `after()` to avoid blocking
3. Files are grouped by bucket to minimize API calls
4. Both individual file keys and folder paths are deleted
5. Cleanup errors are logged but don't fail the deletion operation

This approach ensures fast response times while still cleaning up storage resources, with the understanding that storage cleanup failures are non-critical.

**Sources:**
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:778-891]()

---

## Database Schema

The Vector Store Management system uses several interconnected database tables to track configuration and status.

**Database Schema Relationships**

```mermaid
erDiagram
    teams ||--o{ githubRepositoryIndex : "owns"
    teams ||--o{ documentVectorStores : "owns"
    
    githubRepositoryIndex ||--o{ githubRepositoryContentStatus : "has"
    githubRepositoryIndex ||--o{ githubRepositoryEmbeddingProfiles : "has"
    
    documentVectorStores ||--o{ documentEmbeddingProfiles : "has"
    documentVectorStores ||--o{ documentVectorStoreSources : "has"
    
    teams {
        int dbId PK
        string id
        string plan
    }
    
    githubRepositoryIndex {
        int dbId PK
        string id
        string owner
        string repo
        int teamDbId FK
        int installationId
    }
    
    githubRepositoryContentStatus {
        int dbId PK
        int repositoryIndexDbId FK
        int embeddingProfileId
        string contentType
        boolean enabled
        string status
        string errorCode
        timestamp retryAfter
        timestamp lastSyncedAt
        json metadata
    }
    
    githubRepositoryEmbeddingProfiles {
        int repositoryIndexDbId FK
        int embeddingProfileId
        timestamp createdAt
    }
    
    documentVectorStores {
        int dbId PK
        string id
        string name
        int teamDbId FK
    }
    
    documentEmbeddingProfiles {
        int documentVectorStoreDbId FK
        int embeddingProfileId
        timestamp createdAt
    }
    
    documentVectorStoreSources {
        int dbId PK
        string id
        int documentVectorStoreDbId FK
        string fileName
        string storageBucket
        string storageKey
        string ingestStatus
        string ingestErrorCode
    }
```

**GitHub Repository Tables:**

- **githubRepositoryIndex**: Primary repository configuration
  - `id`: External identifier (format: `gthbi_*`)
  - `owner` + `repo`: Repository coordinates
  - `installationId`: GitHub App installation for access
  - `teamDbId`: Foreign key to owning team

- **githubRepositoryContentStatus**: Per-profile, per-content-type status tracking
  - Composite uniqueness: `repositoryIndexDbId` + `embeddingProfileId` + `contentType`
  - `enabled`: Whether this combination is active
  - `status`: Current state (`idle`, `running`, `completed`, `failed`)
  - `metadata`: JSON field with content-specific data (commit SHA, issue number, PR number)

- **githubRepositoryEmbeddingProfiles**: Enabled embedding profiles
  - Links repository to embedding profile IDs
  - Deleted when profile is removed from configuration

**Document Vector Store Tables:**

- **documentVectorStores**: Store definition
  - `id`: External identifier (format: `dvs_*`)
  - `name`: User-provided name
  - `teamDbId`: Foreign key to owning team

- **documentEmbeddingProfiles**: Enabled embedding profiles
  - Links store to embedding profile IDs
  - Replaced on every configuration update

- **documentVectorStoreSources**: Individual document tracking
  - `id`: Unique source identifier
  - `storageBucket` + `storageKey`: Location in Supabase Storage
  - `ingestStatus`: Processing state
  - `ingestErrorCode`: Error details if ingestion failed

**Sources:**
- Database schema referenced throughout actions.ts
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:10-23]() (imports)

---

## Server Actions and API Routes

Vector store operations are exposed through Next.js Server Actions for mutations and API routes for file operations.

**Server Actions Overview**

| Action | Purpose | File Location |
|--------|---------|---------------|
| `registerRepositoryIndex` | Register new GitHub repository | [actions.ts:107-251]() |
| `updateRepositoryIndex` | Update content types and profiles | [actions.ts:257-409]() |
| `deleteRepositoryIndex` | Remove repository registration | [actions.ts:411-422]() |
| `triggerManualIngest` | Start manual ingestion | [actions.ts:554-593]() |
| `diagnoseRepositoryConnection` | Check repository access | [actions.ts:424-503]() |
| `updateRepositoryInstallation` | Fix installation ID | [actions.ts:505-549]() |
| `createDocumentVectorStore` | Create new document store | [actions.ts:616-700]() |
| `updateDocumentVectorStore` | Update store configuration | [actions.ts:702-776]() |
| `deleteDocumentVectorStore` | Delete store and cleanup files | [actions.ts:778-891]() |

**Transaction Patterns:**

All quota-enforcing operations use pessimistic locking:
1. Begin transaction
2. Lock team row with `FOR UPDATE`
3. Check existing records (also locked)
4. Verify quota limit
5. Perform insertions if quota allows
6. Commit or rollback

Example from `registerRepositoryIndex` ([apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:159-235]()):
```typescript
await db.transaction(async (tx) => {
  // Lock team row
  await tx
    .select({ dbId: teams.dbId })
    .from(teams)
    .where(eq(teams.dbId, team.dbId))
    .limit(1)
    .for("update");
  
  // Check existing repositories count
  const existingRepositories = await tx
    .select({ dbId: githubRepositoryIndex.dbId })
    .from(githubRepositoryIndex)
    .where(eq(githubRepositoryIndex.teamDbId, team.dbId))
    .limit(quota.maxStores)
    .for("update");
  
  if (existingRepositories.length >= quota.maxStores) {
    return { success: false, error: "Quota reached" };
  }
  
  // Proceed with insertion...
});
```

**API Routes:**

Document upload and deletion use API routes due to multipart form data requirements:

- **POST** `/api/vector-stores/document/[storeId]/documents`: Upload files
  - Accepts multipart/form-data
  - Validates file types and sizes
  - Stores in Supabase Storage
  - Creates source records
  - Returns success/failure for each file (HTTP 207 Multi-Status)

- **DELETE** `/api/vector-stores/document/[storeId]/documents`: Delete source
  - Accepts JSON body with `sourceId`
  - Removes database record
  - Deletes from Supabase Storage
  - Returns success/error

These routes are referenced in the document vector store item component but implemented outside the provided file listing.

**Sources:**
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:1-986]()
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx:442-514]() (API usage)

---

## Plan-Based Quota Management

Vector store availability and limits are determined by team plan tier.

**Quota Enforcement Architecture**

```mermaid
graph TB
    TeamPlan["Team Plan<br/>free/pro/team/enterprise"]
    
    GitHubQuota["getGitHubVectorStoreQuota"]
    DocumentQuota["getDocumentVectorStoreQuota"]
    
    GitHubCheck["GitHub Vector Store Quota<br/>isAvailable + maxStores"]
    DocumentCheck["Document Vector Store Quota<br/>isAvailable + maxStores"]
    
    UIDisable["Disable 'Register' button<br/>Show tooltip with upgrade message"]
    ActionReject["Reject server action<br/>Return error message"]
    
    TeamPlan --> GitHubQuota
    TeamPlan --> DocumentQuota
    
    GitHubQuota --> GitHubCheck
    DocumentQuota --> DocumentCheck
    
    GitHubCheck --> UIDisable
    GitHubCheck --> ActionReject
    DocumentCheck --> UIDisable
    DocumentCheck --> ActionReject
```

**Quota Functions:**

- **getGitHubVectorStoreQuota** ([apps/studio.giselles.ai/services/teams/plan-features/github-vector-store.ts]()): Returns `{ isAvailable, maxStores }` based on plan
- **getDocumentVectorStoreQuota** ([apps/studio.giselles.ai/services/teams/plan-features/document-vector-store.ts]()): Returns `{ isAvailable, maxStores }` based on plan

**Quota Enforcement Points:**

1. **UI Level** ([apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/page.tsx:47-56]()):
   - Buttons disabled when `!hasAccess` or `hasReachedLimit`
   - Tooltip explains upgrade requirement
   - Usage counter displayed in list view

2. **Server Action Level**:
   - Quota check happens in transaction after locking team row
   - Rejects if quota exceeded even if UI bypass attempted
   - Consistent error messages returned

3. **Display Level**:
   - Empty state shows lock icon when `!hasAccess`
   - Usage notice shows count and remaining quota
   - Alert displayed when limit reached with upgrade link

**Example Quota Display** ([apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-list.tsx:84-151]()):
```
GitHub Vector Stores used: 3 / 5
2 GitHub Vector Stores remaining in your Pro plan.
```

When limit reached:
```
⚠ Maximum capacity reached
Delete an existing store or upgrade your plan in Team Settings to add more GitHub Vector Stores.
```

**Sources:**
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/page.tsx:19-78]()
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-list.tsx:84-151]()
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:148-156]() (GitHub quota check)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:631-639]() (Document quota check)

---

## Navigation and Layout

The Vector Store settings are organized with tab navigation and consistent layout structure.

**Layout Hierarchy**

```mermaid
graph TB
    Layout["VectorStoresLayout<br/>layout.tsx"]
    Navigation["VectorStoresNavigationLayout<br/>navigation-layout.tsx"]
    Sidebar["VectorStoresSidebarMenu<br/>sidebar-menu.tsx"]
    
    GitHubPage["GitHub Vector Stores Page<br/>page.tsx"]
    DocumentPage["Document Vector Stores Page<br/>document/page.tsx"]
    
    Layout --> Navigation
    Navigation --> Sidebar
    Navigation --> GitHubPage
    Navigation --> DocumentPage
    
    Sidebar -.Tab 1.-> GitHubPage
    Sidebar -.Tab 2.-> DocumentPage
```

**Routes:**
- `/settings/team/vector-stores` - GitHub vector stores (default)
- `/settings/team/vector-stores/document` - Document vector stores

The `TabNavigation` component ([apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/sidebar-menu.tsx:5-8]()) provides switching between these two tabs.

**Common Layout Elements:**
- Page heading: "Vector Stores" with glow effect
- Documentation link: "About Vector Stores" to external docs
- Tab navigation with "GitHub" and "Document" tabs
- Consistent spacing and background colors

**Sources:**
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/layout.tsx:1-32]()
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/navigation-layout.tsx:1-19]()
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/sidebar-menu.tsx:1-13]()

---

# Page: RAG System and Query Execution

# RAG Implementation and Query Execution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/playground/giselle-engine.ts](apps/playground/giselle-engine.ts)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/configure-sources-dialog.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/configure-sources-dialog.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/data.ts](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/data.ts)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/diagnostic-modal.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/diagnostic-modal.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-embedding-profiles.ts](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-embedding-profiles.ts)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-store-create-dialog.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-store-create-dialog.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-vector-store-list.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-vector-store-list.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/page.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/page.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/layout.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/layout.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/navigation-layout.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/navigation-layout.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/page.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/page.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-list.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-list.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-registration-dialog.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-registration-dialog.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/sidebar-menu.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/sidebar-menu.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/types.ts](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/types.ts)
- [apps/studio.giselles.ai/app/giselle-engine.ts](apps/studio.giselles.ai/app/giselle-engine.ts)
- [internal-packages/ui/components/form-field.tsx](internal-packages/ui/components/form-field.tsx)
- [internal-packages/ui/components/section-header.tsx](internal-packages/ui/components/section-header.tsx)
- [internal-packages/ui/components/status-indicator.tsx](internal-packages/ui/components/status-indicator.tsx)
- [packages/giselle/src/engine/acts/run-act.ts](packages/giselle/src/engine/acts/run-act.ts)
- [packages/giselle/src/engine/generations/generate-content.ts](packages/giselle/src/engine/generations/generate-content.ts)
- [packages/giselle/src/engine/generations/generate-image.ts](packages/giselle/src/engine/generations/generate-image.ts)
- [packages/giselle/src/engine/generations/internal/use-generation-executor.ts](packages/giselle/src/engine/generations/internal/use-generation-executor.ts)
- [packages/giselle/src/engine/generations/types.ts](packages/giselle/src/engine/generations/types.ts)
- [packages/giselle/src/engine/generations/utils.ts](packages/giselle/src/engine/generations/utils.ts)
- [packages/giselle/src/engine/operations/execute-query.ts](packages/giselle/src/engine/operations/execute-query.ts)
- [packages/giselle/src/engine/telemetry/index.ts](packages/giselle/src/engine/telemetry/index.ts)
- [packages/giselle/src/engine/telemetry/types.ts](packages/giselle/src/engine/telemetry/types.ts)
- [packages/giselle/src/engine/triggers/resolve-trigger.ts](packages/giselle/src/engine/triggers/resolve-trigger.ts)
- [packages/giselle/src/engine/types.ts](packages/giselle/src/engine/types.ts)
- [packages/giselle/src/react/generations/generation-runner.tsx](packages/giselle/src/react/generations/generation-runner.tsx)

</details>



## Purpose and Scope

This page documents the Retrieval-Augmented Generation (RAG) pipeline implementation in Giselle, specifically focusing on how vector store queries are executed and integrated into workflow generation processes. It covers query resolution, embedding-based similarity search, and result formatting for consumption by downstream nodes.

For information about the document processing and ingestion pipeline that populates vector stores, see [3.2](#3.2). For details on vector store management interfaces and registration, see [5.1.3](#5.1.3).

## RAG System Architecture

The RAG system consists of three primary components: query nodes that initiate searches, vector store services that perform similarity lookups, and the query execution engine that orchestrates the flow and formats results.

```mermaid
graph TB
    subgraph "Workflow Layer"
        QN["QueryNode<br/>(isQueryNode)"]
        VSN["VectorStoreNode<br/>(isConfiguredVectorStoreNode)"]
        TGN["TextGenerationNode"]
    end
    
    subgraph "Execution Layer"
        EQ["executeQuery<br/>packages/giselle/src/engine/operations/execute-query.ts"]
        RQ["resolveQuery<br/>(Template interpolation)"]
        QVS["queryVectorStore<br/>(Orchestrator)"]
    end
    
    subgraph "Vector Store Services"
        GHQS["gitHubQueryService<br/>(GitHub code/PR search)"]
        GHPRQS["gitHubPullRequestQueryService"]
        DVQS["DocumentVectorStoreQueryService"]
    end
    
    subgraph "Storage & Embedding"
        PGVECTOR["PostgreSQL + pgvector<br/>(Similarity search)"]
        EP["EmbeddingProfile<br/>(OpenAI, Google, Cohere)"]
    end
    
    QN -->|"query string + refs"| EQ
    VSN -->|"config"| EQ
    EQ --> RQ
    RQ -->|"resolved query"| QVS
    QVS --> GHQS
    QVS --> GHPRQS
    QVS --> DVQS
    GHQS --> PGVECTOR
    GHPRQS --> PGVECTOR
    DVQS --> PGVECTOR
    PGVECTOR -->|"results"| QVS
    QVS -->|"QueryResultOutput"| EQ
    EQ -->|"GenerationOutput"| TGN
    EP -.->|"generates embeddings"| PGVECTOR
```

**Sources:** [packages/giselle/src/engine/operations/execute-query.ts:1-450](), [apps/studio.giselles.ai/app/giselle-engine.ts:251-255](), [packages/giselle/src/engine/types.ts:162-188]()

## Query Context Types

The system supports two types of vector store queries, each with its own context structure and configuration requirements.

| Context Type | Provider | Key Fields | Embedding Profile | Use Case |
|-------------|----------|------------|-------------------|----------|
| `GitHubQueryContext` | `github` | `owner`, `repo`, `contentType` (`blob` or `pullRequest`) | `EmbeddingProfileId` (default: 1) | Search repository code or merged pull requests |
| `DocumentVectorStoreQueryContext` | `document` | `documentVectorStoreId` | `EmbeddingProfileId` (default: 1) | Search uploaded documents (PDF, text) |

**Type Definitions:**

```typescript
// GitHubQueryContext structure
{
  provider: "github",
  workspaceId: WorkspaceId,
  owner: string,
  repo: string,
  contentType: "blob" | "pullRequest",
  embeddingProfileId: EmbeddingProfileId
}

// DocumentVectorStoreQueryContext structure
{
  provider: "document",
  workspaceId: WorkspaceId,
  documentVectorStoreId: string,
  embeddingProfileId: EmbeddingProfileId
}
```

**Sources:** [packages/giselle/src/engine/types.ts:162-179](), [packages/giselle/src/engine/operations/execute-query.ts:269-279]()

## Query Execution Pipeline

The query execution process follows a staged pipeline from node initialization through result formatting.

```mermaid
sequenceDiagram
    participant WF as Workflow Designer
    participant GE as GiselleEngine
    participant EQ as executeQuery
    participant RQ as resolveQuery
    participant QVS as queryVectorStore
    participant VS as VectorStoreQueryService
    participant PG as PostgreSQL+pgvector
    
    WF->>GE: Generate with QueryNode
    GE->>EQ: useGenerationExecutor
    EQ->>EQ: Validate isQueryNode
    EQ->>RQ: resolveQuery(query, generation, storage)
    
    Note over RQ: Find template refs: {{nd-XXX:otp-XXX}}
    RQ->>RQ: generationContentResolver
    RQ->>RQ: Replace templates with content
    RQ-->>EQ: Resolved query string
    
    EQ->>EQ: Filter connected VectorStoreNodes
    EQ->>QVS: queryVectorStore(workspaceId, query, nodes)
    
    loop For each VectorStoreNode
        QVS->>QVS: Validate isConfiguredVectorStoreNode
        QVS->>VS: query(context, queryText, options)
        VS->>PG: Embedding similarity search
        PG-->>VS: Ranked results with metadata
        VS-->>QVS: QueryResult[]
    end
    
    QVS-->>EQ: Combined results
    EQ->>EQ: Format as QueryResultOutput
    EQ->>GE: finishGeneration(outputs)
    GE-->>WF: Generation completed
```

**Sources:** [packages/giselle/src/engine/operations/execute-query.ts:43-126](), [packages/giselle/src/engine/operations/execute-query.ts:299-450]()

## Query Resolution and Template Interpolation

Query nodes support dynamic query construction through template references that pull content from upstream nodes. The resolution process handles multiple node types and formats.

### Template Syntax

Query strings can contain references in the format `{{nd-{nodeId}:otp-{outputId}}}` which are replaced with actual content at execution time.

### Resolution Logic

```mermaid
graph TD
    START["Query string with templates"]
    PARSE["Extract pattern matches<br/>{{nd-XXX:otp-XXX}}"]
    LOOP["For each reference"]
    FIND["Find contextNode by nodeId"]
    CHECK["Check node.content.type"]
    
    TEXT["type: 'text'<br/>Extract text content<br/>(handle JSON)"]
    TEXTGEN["type: 'textGeneration'<br/>generationContentResolver<br/>(get completed output)"]
    ACTION["type: 'action'/'trigger'<br/>generationContentResolver<br/>(get completed output)"]
    QUERY["type: 'query'<br/>Skip (no replacement)"]
    
    REPLACE["Replace template with content"]
    CONTINUE["Continue to next reference"]
    DONE["Return resolved query"]
    
    START --> PARSE
    PARSE --> LOOP
    LOOP --> FIND
    FIND --> CHECK
    CHECK -->|text| TEXT
    CHECK -->|textGeneration| TEXTGEN
    CHECK -->|action/trigger| ACTION
    CHECK -->|query/vectorStore| QUERY
    TEXT --> REPLACE
    TEXTGEN --> REPLACE
    ACTION --> REPLACE
    QUERY --> CONTINUE
    REPLACE --> CONTINUE
    CONTINUE --> LOOP
    LOOP -->|done| DONE
```

**Key Implementation Details:**

- **JSON Content Handling:** [packages/giselle/src/engine/operations/execute-query.ts:199-201]() - If query is JSON content, converts to plain text using `jsonContentToText`
- **Pattern Matching:** [packages/giselle/src/engine/operations/execute-query.ts:204-208]() - Uses regex `/\{\{(nd-[a-zA-Z0-9]+):(otp-[a-zA-Z0-9]+)\}\}/g` to find all references
- **Generation Lookup:** [packages/giselle/src/engine/operations/execute-query.ts:136-194]() - `generationContentResolver` retrieves completed generation outputs by node and output IDs

**Sources:** [packages/giselle/src/engine/operations/execute-query.ts:128-267]()

## Vector Store Query Services

Each vector store type implements the `QueryService` interface, which provides a uniform abstraction for similarity searches across different providers.

### Service Interface

```typescript
// Generic QueryService signature
QueryService<TContext, TMetadata> = {
  query: (
    context: TContext,
    queryText: string,
    options: {
      maxResults?: number,
      similarityThreshold?: number
    }
  ) => Promise<QueryResult<TMetadata>[]>
}
```

### Configured Services

The engine is initialized with three query service implementations:

```mermaid
graph LR
    subgraph "GiselleEngine Configuration"
        ENGINE["giselleEngine<br/>apps/studio.giselles.ai/app/giselle-engine.ts:218"]
    end
    
    subgraph "Vector Store Query Services"
        GHQS["gitHubQueryService<br/>(Code blobs)"]
        GHPRQS["gitHubPullRequestQueryService<br/>(Merged PRs)"]
        DVQS["getDocumentVectorStoreQueryService<br/>(Uploaded documents)"]
    end
    
    ENGINE -->|vectorStoreQueryServices.github| GHQS
    ENGINE -->|vectorStoreQueryServices.githubPullRequest| GHPRQS
    ENGINE -->|vectorStoreQueryServices.document| DVQS
    
    GHQS -.->|"Returns GithubEmbeddingMetadata<br/>(fileSha, path)"| RESULTS
    GHPRQS -.->|"Returns PR metadata"| RESULTS
    DVQS -.->|"Returns document metadata"| RESULTS
    
    RESULTS["Query Results"]
```

**Configuration:** [apps/studio.giselles.ai/app/giselle-engine.ts:251-255]()

**Query Execution:** [packages/giselle/src/engine/operations/execute-query.ts:299-450]() dispatches to appropriate service based on `vectorStoreNode.content.source.provider`

**Sources:** [apps/studio.giselles.ai/app/giselle-engine.ts:36-40](), [packages/giselle/src/engine/types.ts:181-187]()

## Embedding Profiles and Similarity Search

Each vector store query operates within the context of a specific embedding profile that determines which embedding model was used for indexing and should be used for query embedding.

### Embedding Profile Specification

```mermaid
graph TB
    subgraph "Embedding Profile Selection"
        VSN["VectorStoreNode.content.source"]
        STATE["state.embeddingProfileId"]
        DEFAULT["DEFAULT_EMBEDDING_PROFILE_ID<br/>(value: 1)"]
    end
    
    subgraph "Query Context Assembly"
        QC["QueryContext"]
        EPID["embeddingProfileId: number"]
    end
    
    subgraph "Available Profiles"
        EP1["1: OpenAI Small<br/>(text-embedding-3-small)"]
        EP2["2: OpenAI Large<br/>(text-embedding-3-large)"]
        EP3["3: Google Gecko<br/>(text-embedding-004)"]
        EP4["4: Cohere v3<br/>(embed-english-v3.0)"]
    end
    
    VSN --> STATE
    STATE -->|if present| EPID
    STATE -->|if undefined| DEFAULT
    DEFAULT --> EPID
    EPID --> QC
    
    QC -.->|profile 1| EP1
    QC -.->|profile 2| EP2
    QC -.->|profile 3| EP3
    QC -.->|profile 4| EP4
```

**Profile Assignment:**
- [packages/giselle/src/engine/operations/execute-query.ts:334-335]() - GitHub blob queries use `state.embeddingProfileId ?? DEFAULT_EMBEDDING_PROFILE_ID`
- [packages/giselle/src/engine/operations/execute-query.ts:361-362]() - GitHub PR queries use same fallback logic
- [packages/giselle/src/engine/operations/execute-query.ts:387-388]() - Document vector store queries use same fallback logic

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `maxResults` | `number` | `DEFAULT_MAX_RESULTS` | Maximum number of results to return |
| `similarityThreshold` | `number` | `DEFAULT_SIMILARITY_THRESHOLD` | Minimum cosine similarity score (0-1) |
| `embeddingProfileId` | `EmbeddingProfileId` | `1` (OpenAI Small) | Which embedding model to use |

**Sources:** [packages/giselle/src/engine/operations/execute-query.ts:299-450](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/github-embedding-profiles.ts:1-13]()

## Integration with Workflow Nodes

Query nodes connect to vector store nodes and expose their results to downstream text generation nodes through the output system.

### Node Connection Pattern

```mermaid
graph LR
    subgraph "Source Nodes"
        TN["TextNode<br/>(Provides query template)"]
        VSN1["VectorStoreNode<br/>(GitHub repo)"]
        VSN2["VectorStoreNode<br/>(Document store)"]
    end
    
    subgraph "Query Node"
        QN["QueryNode"]
        QCFG["content.query: string<br/>content.maxResults: number<br/>content.similarityThreshold: number"]
        QOUT["output: 'result'<br/>(accessor: 'result')"]
    end
    
    subgraph "Downstream Nodes"
        TGN["TextGenerationNode<br/>(Uses {{nd-X:otp-Y}})"]
    end
    
    TN -.->|"{{nd-X:otp-Y}}<br/>(Optional template ref)"| QN
    VSN1 -->|connection| QN
    VSN2 -->|connection| QN
    QN --> QCFG
    QCFG --> QOUT
    QOUT -->|"QueryResultOutput"| TGN
```

**Connection Filtering:** [packages/giselle/src/engine/operations/execute-query.ts:72-78]() - Only vector store nodes with active connections to the query node are included in the search

**Output Definition:** [packages/giselle/src/engine/operations/execute-query.ts:91-96]() - Query results are written to the output with accessor `"result"`

**Sources:** [packages/giselle/src/engine/operations/execute-query.ts:60-108]()

## Query Result Formatting

Query results are formatted as structured `QueryResultOutput` objects that can be consumed by downstream nodes or converted to plain text.

### Result Structure

```typescript
// QueryResultOutput type
{
  type: "query-result",
  outputId: OutputId,
  content: QueryResult[]
}

// QueryResult structure (varies by provider)
{
  content: string,           // The retrieved text chunk
  similarity: number,        // Cosine similarity score (0-1)
  source: VectorStoreSource, // GitHub or Document source info
  metadata: TMetadata        // Provider-specific metadata
}
```

### Text Conversion

The `queryResultToText` function converts structured query results into a readable text format for consumption by LLMs:

```mermaid
graph TD
    QR["QueryResult[]"]
    CHECK["Check content length"]
    EMPTY["Return empty string"]
    FORMAT["Format each result"]
    
    subgraph "Result Formatting"
        HEADER["'Search Results:'"]
        LOOP["For each result (index i)"]
        BLOCK["Build text block:<br/>Result i+1<br/>Content: ...<br/>Similarity: ..."]
    end
    
    JOIN["Join with newlines"]
    RETURN["Return formatted text"]
    
    QR --> CHECK
    CHECK -->|length === 0| EMPTY
    CHECK -->|length > 0| FORMAT
    FORMAT --> HEADER
    HEADER --> LOOP
    LOOP --> BLOCK
    BLOCK --> JOIN
    JOIN --> RETURN
```

**Implementation:** [packages/giselle/src/engine/generations/utils.ts:442-461]() - Formats results as numbered blocks with content and similarity scores

**Usage in Text Generation:**
- [packages/giselle/src/engine/generations/internal/use-generation-executor.ts:243-253]() - `generationContentResolver` calls `queryResultToText` when resolving query node references
- [packages/giselle/src/engine/operations/execute-query.ts:186-187]() - Query outputs are converted to text when used as template replacements

**Sources:** [packages/giselle/src/engine/generations/utils.ts:442-461](), [packages/giselle/src/engine/operations/execute-query.ts:186-187](), [packages/giselle/src/engine/generations/internal/use-generation-executor.ts:243-253]()

## Observability and Telemetry

The RAG system includes telemetry hooks for tracking embedding usage and query performance.

### Embedding Callback

The `embeddingComplete` callback is invoked after each query execution to track embedding metrics:

```typescript
// Callback signature
embeddingComplete?: (args: {
  embeddingMetrics: EmbeddingMetrics,
  generation: RunningGeneration,
  queryContext: QueryContext,
  generationMetadata?: GenerationMetadata
}) => void | Promise<void>
```

**Invocation Points:**
- [apps/studio.giselles.ai/app/giselle-engine.ts:329-389]() - `traceEmbeddingForTeam` function traces embedding operations with plan tags and metadata
- Telemetry includes: team type, subscription status, resource provider, content type, embedding profile ID

**Metadata Captured:**

| Field | Description |
|-------|-------------|
| `generationId` | ID of the query generation |
| `teamId` | Team performing the query |
| `isProPlan` | Whether team has Pro subscription |
| `resourceProvider` | `"github"` or `"document"` |
| `embeddingProfileId` | Which embedding model was used |
| Provider-specific fields | `resourceOwner`, `resourceRepo`, `documentVectorStoreId`, etc. |

**Sources:** [apps/studio.giselles.ai/app/giselle-engine.ts:140-200](), [apps/studio.giselles.ai/app/giselle-engine.ts:329-389](), [packages/giselle/src/engine/types.ts:77-85]()

---

# Page: GitHub Integration

# GitHub Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/github-action-properties-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/github-action-properties-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/index.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/ui/github-action-configured-view.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/ui/github-action-configured-view.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/event-type-display.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/event-type-display.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/icons/index.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/icons/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/install-application.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/install-application.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/labels-input-step.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/labels-input-step.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/unauthorized.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/unauthorized.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/github-trigger-properties-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/github-trigger-properties-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/utils/trigger-configuration.ts](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/utils/trigger-configuration.ts)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/utils/use-trigger-configuration.ts](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/utils/use-trigger-configuration.ts)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/manual-trigger/manual-trigger-properties-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/manual-trigger/manual-trigger-properties-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/ui/configured-views/github-trigger-configured-view.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/ui/configured-views/github-trigger-configured-view.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/select-repository.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/select-repository.tsx)
- [packages/giselle/src/engine/github/event-handlers.test.ts](packages/giselle/src/engine/github/event-handlers.test.ts)
- [packages/giselle/src/engine/github/event-handlers.ts](packages/giselle/src/engine/github/event-handlers.ts)
- [packages/protocol/src/trigger/github.ts](packages/protocol/src/trigger/github.ts)

</details>



This document describes the GitHub integration system, which enables workflows to be triggered by GitHub events (issues, pull requests, discussions) and to perform actions on GitHub repositories. The integration uses a GitHub App for authentication and webhook delivery.

For information about the workflow execution engine that processes GitHub-triggered workflows, see [Act Runner and Workflow Orchestration](#2.4). For the vector store system that indexes GitHub repository content, see [Vector Store Management](#3.2).

## System Purpose and Scope

The GitHub integration provides bidirectional interaction between Giselle workflows and GitHub repositories:

**Inbound (Triggers)**: Workflows can be triggered by 12 different GitHub event types, including issue creation, pull request events, and comments. Events are delivered via GitHub webhooks, matched against configured triggers, and initiate workflow execution.

**Outbound (Actions)**: Workflows can perform actions on GitHub repositories, such as creating issues, posting comments, and replying to discussions. Actions execute during workflow runs and use the GitHub API.

The integration consists of three main subsystems:
- **Configuration UI**: Properties panels for setting up triggers and actions in the workflow designer
- **Event Processing Engine**: Backend handlers that process incoming webhooks and create Acts
- **Action Execution**: Runtime components that execute GitHub operations during workflow execution

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/github-trigger-properties-panel.tsx:1-849](), [packages/giselle/src/engine/github/event-handlers.ts:1-150](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/github-action-properties-panel.tsx:1-179]()

## Architecture Overview

```mermaid
graph TB
    subgraph "GitHub Platform"
        GitHubApp["GitHub App<br/>(OAuth & Webhooks)"]
        GitHubAPI["GitHub API<br/>(GraphQL & REST)"]
    end
    
    subgraph "Workflow Designer UI"
        TriggerPanel["GitHubTriggerPropertiesPanel<br/>Event Configuration"]
        ActionPanel["GitHubActionPropertiesPanel<br/>Action Configuration"]
        SelectRepo["SelectRepository<br/>Installation & Repo Picker"]
    end
    
    subgraph "Configuration Storage"
        FlowTriggers[("flow_triggers<br/>Trigger Configurations")]
        ActionNodes[("nodes<br/>Action Configurations")]
    end
    
    subgraph "Event Processing"
        WebhookEndpoint["Webhook Endpoint<br/>/api/github/webhooks"]
        ProcessEvent["processEvent<br/>Event Router"]
        EventHandlers["12 Event Handlers<br/>handleIssueOpened, etc."]
    end
    
    subgraph "Act Execution"
        CreateAct["createAndStartAct<br/>Workflow Instantiation"]
        ActRunner["Act Runner<br/>Execution Engine"]
        Callbacks["Lifecycle Callbacks<br/>Progress Updates"]
    end
    
    subgraph "Feedback Loop"
        AddReaction["addReaction<br/>GitHub Reactions"]
        CreateComment["createIssueComment<br/>createPullRequestComment"]
        UpdateComment["updateIssueComment<br/>updatePullRequestReviewComment"]
    end
    
    GitHubApp -->|"OAuth Flow"| TriggerPanel
    GitHubApp -->|"OAuth Flow"| ActionPanel
    TriggerPanel --> SelectRepo
    ActionPanel --> SelectRepo
    
    TriggerPanel -->|"configureTrigger"| FlowTriggers
    ActionPanel -->|"updateNodeData"| ActionNodes
    
    GitHubApp -->|"Webhook Delivery"| WebhookEndpoint
    WebhookEndpoint --> ProcessEvent
    ProcessEvent --> EventHandlers
    
    EventHandlers -->|"Match Trigger"| FlowTriggers
    EventHandlers --> CreateAct
    CreateAct --> ActRunner
    ActRunner --> Callbacks
    
    Callbacks --> AddReaction
    Callbacks --> CreateComment
    Callbacks --> UpdateComment
    
    CreateComment --> GitHubAPI
    UpdateComment --> GitHubAPI
    AddReaction --> GitHubAPI
    
    ActionNodes -->|"During Execution"| GitHubAPI
```

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/github-trigger-properties-panel.tsx:165-228](), [packages/giselle/src/engine/github/event-handlers.ts:477-557]()

## GitHub App Configuration

### Installation Flow

The GitHub integration requires a GitHub App to be installed on the user's account or organization. The installation process follows this sequence:

```mermaid
sequenceDiagram
    participant User
    participant UI as Properties Panel
    participant Popup as Popup Window
    participant GitHub as GitHub Platform
    participant Backend as Giselle Backend
    
    User->>UI: Click "Continue with GitHub"
    UI->>Popup: window.open(authUrl)
    Popup->>GitHub: OAuth Authorization
    GitHub->>Popup: Authorization Code
    Popup->>Backend: POST /api/github/callback
    Backend->>GitHub: Exchange Code for Token
    GitHub->>Backend: Access Token
    Backend->>Backend: Store Installation Data
    Popup->>UI: postMessage("github-app-installed")
    UI->>Backend: refresh()
    Backend->>UI: Integration State
    UI->>User: Show Repository Selection
```

The UI components handle three authentication states:

**Unauthorized State** (`status: "unauthorized"`): User has not connected GitHub account. Displays `Unauthorized` component with OAuth initiation button.

**Not Installed State** (`status: "not-installed"`): User is authenticated but hasn't installed the GitHub App. Displays `InstallGitHubApplication` component with installation link.

**Installed State** (`status: "installed"`): GitHub App is installed and ready. Displays repository selection and event/action configuration UI.

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/unauthorized.tsx:1-54](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/install-application.tsx:1-59](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/github-action-properties-panel.tsx:150-179]()

### Installation Data Structure

The integration state uses `GitHubIntegrationInstallation` objects:

```typescript
interface GitHubIntegrationInstallation {
  id: number;  // Installation ID from GitHub
  account: {
    login: string;  // Username or org name
  };
  repositories: Repository[];
}

interface Repository {
  node_id: string;    // GitHub GraphQL node ID
  name: string;
  private: boolean;
  owner: {
    login: string;
  };
}
```

The `SelectRepository` component provides a dropdown for selecting installations (organizations) and displays available repositories for the selected installation. The component manages state locally and calls `onChangeInstallation` and `onSelectRepository` callbacks when selections are made.

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/select-repository.tsx:1-253](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/github-trigger-properties-panel.tsx:125-163]()

## GitHub Triggers

### Supported Event Types

The system supports 12 GitHub event types, defined in the trigger registry. Each event maps to a specific webhook event and has associated input fields that become outputs on the trigger node:

| Event ID | Webhook Event | Description | Special Configuration |
|----------|--------------|-------------|----------------------|
| `github.issue.created` | `issues.opened` | Issue opened | None |
| `github.issue.closed` | `issues.closed` | Issue closed | None |
| `github.issue.labeled` | `issues.labeled` | Label added to issue | **Labels required** |
| `github.issue_comment.created` | `issue_comment.created` | Comment on issue | **Callsign required** |
| `github.pull_request.opened` | `pull_request.opened` | Pull request opened | None |
| `github.pull_request.ready_for_review` | `pull_request.ready_for_review` | PR ready for review | None |
| `github.pull_request.closed` | `pull_request.closed` | Pull request closed | None |
| `github.pull_request.labeled` | `pull_request.labeled` | Label added to PR | **Labels required** |
| `github.pull_request_comment.created` | `issue_comment.created` (with PR check) | Comment on PR | **Callsign required** |
| `github.pull_request_review_comment.created` | `pull_request_review_comment.created` | Review comment on PR | **Callsign required** |
| `github.discussion.created` | `discussion.created` | Discussion created | None |
| `github.discussion_comment.created` | `discussion_comment.created` | Comment on discussion | **Callsign required** |

Sources: [packages/protocol/src/trigger/github.ts:1-107](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/icons/index.tsx:266-298]()

### Trigger Configuration State Machine

The trigger configuration UI uses a multi-step state machine:

```mermaid
stateDiagram-v2
    [*] --> Unconfigured
    Unconfigured --> SelectEvent: User opens panel
    SelectEvent --> SelectRepository: Event selected
    SelectRepository --> ConfirmRepository: Repository selected
    
    ConfirmRepository --> InputCallsign: Requires callsign
    ConfirmRepository --> InputLabels: Requires labels
    ConfirmRepository --> Configured: No special config
    
    InputCallsign --> Configured: Callsign submitted
    InputLabels --> Configured: Labels submitted
    
    Configured --> Reconfiguring: User clicks "Change..."
    Reconfiguring --> SelectRepository: Repository mode
    Reconfiguring --> InputCallsign: Callsign mode
    Reconfiguring --> InputLabels: Labels mode
    Reconfiguring --> Configured: Complete
```

The state machine is implemented in the `GitHubTriggerPropertiesPanel` component with a `GitHubTriggerSetupStep` discriminated union:

```typescript
type GitHubTriggerSetupStep =
  | { state: "select-event" }
  | { state: "select-repository"; eventId: GitHubEventId }
  | { state: "input-callsign"; eventId: GitHubEventId; owner: string; repo: string; repoNodeId: string; installationId: number; callsign?: string }
  | { state: "input-labels"; eventId: GitHubEventId; owner: string; repo: string; repoNodeId: string; installationId: number; labels?: string[] }
  | { state: "confirm-repository"; eventId: GitHubEventId; installationId: number; owner: string; repo: string; repoNodeId: string }
```

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/github-trigger-properties-panel.tsx:230-273](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/github-trigger-properties-panel.tsx:297-848]()

### Callsign System

Comment-based triggers (issue comments, PR comments, review comments, discussion comments) require a **callsign** - a command prefix that must appear at the start of the comment for the trigger to fire. This prevents workflows from executing on every comment in a repository.

**Configuration UI**: The `InputCallsignStep` renders when `isTriggerRequiringCallsign(eventId)` returns true. It displays an input field with a `/` prefix placeholder and stores the callsign without the prefix.

**Parsing**: The `parseCommand` function extracts the callsign and content from comment bodies. The event handler checks if `command?.callsign` matches `conditions?.callsign` before triggering the workflow.

**Example**: If the callsign is configured as `code-review`, the workflow only triggers when comments start with `/code-review`.

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/github-trigger-properties-panel.tsx:276-285](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/github-trigger-properties-panel.tsx:735-825](), [packages/giselle/src/engine/github/event-handlers.ts:200-226]()

### Labels System

Label-based triggers (`github.issue.labeled`, `github.pull_request.labeled`) require one or more **labels** to be configured. The workflow triggers when any of the configured labels is added to an issue or pull request.

**Configuration UI**: The `LabelsInputStep` component allows users to add multiple labels with a dynamic form. Users can add/remove label inputs and submit the list.

**Matching Logic**: The event handler checks if `conditions.labels.includes(addedLabel.name)` where `addedLabel` is the label from the webhook payload.

**Example**: If labels `["bug", "urgent"]` are configured, the workflow triggers when either the "bug" label or "urgent" label is added to an issue.

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/github-trigger-properties-panel.tsx:288-295](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/labels-input-step.tsx:1-185](), [packages/giselle/src/engine/github/event-handlers.ts:353-384]()

### Trigger Configuration Flow

```mermaid
sequenceDiagram
    participant User
    participant Panel as GitHubTriggerPropertiesPanel
    participant Hook as useTriggerConfiguration
    participant Engine as GiselleEngine
    participant Store as Workflow Store
    participant DB as Database
    
    User->>Panel: Select event type
    Panel->>Panel: setState("select-repository")
    
    User->>Panel: Select repository
    Panel->>Panel: setState("confirm-repository")
    
    alt Requires Callsign
        User->>Panel: Enter callsign
        Panel->>Panel: handleCallsignSubmit
    else Requires Labels
        User->>Panel: Enter labels
        Panel->>Panel: handleLabelsSubmit
    end
    
    Panel->>Hook: configureTrigger(event, step)
    Hook->>Engine: configureTrigger({trigger})
    Engine->>DB: INSERT INTO flow_triggers
    DB-->>Engine: triggerId
    Engine-->>Hook: {triggerId}
    
    Hook->>Store: updateNodeData(node, {state: "configured"})
    Store->>Panel: Node updated
    Panel->>User: Show configured view
```

The `configureTrigger` method called by the hook creates a trigger record in the database with the configuration:

```typescript
{
  nodeId: string,
  workspaceId: string,
  enable: boolean,
  configuration: {
    provider: "github",
    repositoryNodeId: string,
    installationId: number,
    event: GitHubEventData  // Includes id, conditions
  }
}
```

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/utils/use-trigger-configuration.ts:1-87](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/github-trigger-properties-panel.tsx:343-403]()

### Configured Trigger View

Once configured, the trigger displays the `GitHubTriggerConfiguredView` component, which shows:

1. **State Toggle**: Enable/Disable switch for the trigger
2. **Event Type**: Icon and label for the configured event
3. **Repository**: Owner/repo display with "Change Repository" button
4. **Callsign** (if applicable): Display with copy button and usage instructions
5. **Labels** (if applicable): Display as colored badges with "Change Labels" button

The view provides "Change..." buttons that transition the trigger into `reconfiguring` state, allowing users to modify specific aspects without starting from scratch.

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/ui/configured-views/github-trigger-configured-view.tsx:1-321]()

## Event Processing Pipeline

### Webhook Reception and Routing

When GitHub sends a webhook to the Giselle backend, the webhook endpoint validates the signature and routes the event to `processEvent`:

```mermaid
graph LR
    Webhook["GitHub Webhook<br/>POST /api/github/webhooks"]
    Validate["Validate Signature"]
    Parse["Parse Payload"]
    ProcessEvent["processEvent<br/>Main Router"]
    
    Webhook --> Validate
    Validate --> Parse
    Parse --> ProcessEvent
```

The `processEvent` function iterates through an array of 12 event handlers, each testing whether it should handle the event:

```typescript
const eventHandlers = [
  handleIssueOpened,
  handleIssueClosed,
  handleIssueCommentCreated,
  handleIssueLabeled,
  handlePullRequestCommentCreated,
  handlePullRequestReviewCommentCreated,
  handlePullRequestOpened,
  handlePullRequestReadyForReview,
  handlePullRequestClosed,
  handlePullRequestLabeled,
  handleDiscussionCreated,
  handleDiscussionCommentCreated,
];
```

Each handler returns an `EventHandlerResult`:
- `shouldRun: boolean` - Whether this handler matched the event
- `reactionNodeId?: string` - GitHub node ID to add a reaction to

Sources: [packages/giselle/src/engine/github/event-handlers.ts:462-475](), [packages/giselle/src/engine/github/event-handlers.ts:477-510]()

### Event Handler Structure

Each event handler follows a consistent pattern:

```mermaid
flowchart TD
    Start["Event Handler<br/>(e.g., handleIssueOpened)"]
    CheckEvent["ensureWebhookEvent<br/>Verify event type"]
    CheckTrigger["Check trigger.configuration.event.id<br/>Matches expected ID?"]
    CheckPayload["Validate payload<br/>Has required fields?"]
    CheckConditions{"Has conditions?<br/>(callsign/labels)"}
    CheckMatch["Validate conditions<br/>Match?"]
    
    ReturnMatch["Return {shouldRun: true,<br/>reactionNodeId}"]
    ReturnNoMatch["Return {shouldRun: false}"]
    
    Start --> CheckEvent
    CheckEvent -->|No| ReturnNoMatch
    CheckEvent -->|Yes| CheckTrigger
    CheckTrigger -->|No| ReturnNoMatch
    CheckTrigger -->|Yes| CheckPayload
    CheckPayload -->|No| ReturnNoMatch
    CheckPayload -->|Yes| CheckConditions
    CheckConditions -->|No| ReturnMatch
    CheckConditions -->|Yes| CheckMatch
    CheckMatch -->|No| ReturnNoMatch
    CheckMatch -->|Yes| ReturnMatch
```

Example handler implementation:

```typescript
export function handleIssueCommentCreated<TEventName extends WebhookEventName>(
  args: EventHandlerArgs<TEventName>,
): EventHandlerResult {
  // Check webhook event type matches
  if (!args.deps.ensureWebhookEvent(args.event, "issue_comment.created") ||
      args.trigger.configuration.event.id !== "github.issue_comment.created") {
    return { shouldRun: false };
  }

  const comment = args.event.data.payload.comment;
  if (!comment) {
    return { shouldRun: false };
  }

  // Parse and validate callsign
  const command = args.deps.parseCommand(comment.body);
  const conditions = args.trigger.configuration.event.conditions;

  if (command?.callsign !== conditions?.callsign) {
    return { shouldRun: false };
  }

  return { shouldRun: true, reactionNodeId: comment.node_id };
}
```

Sources: [packages/giselle/src/engine/github/event-handlers.ts:200-226](), [packages/giselle/src/engine/github/event-handlers.ts:164-180]()

### Act Creation and Execution

When an event handler matches, `processEvent` creates and starts an Act:

```mermaid
sequenceDiagram
    participant Handler as Event Handler
    participant Process as processEvent
    participant Reaction as addReaction
    participant CreateAct as createAndStartAct
    participant Comment as Create/Update Comment
    
    Handler->>Process: {shouldRun: true, reactionNodeId}
    
    opt Has reaction node
        Process->>Reaction: addReaction(nodeId, "EYES")
    end
    
    Process->>CreateAct: createAndStartAct({context, workspace, inputs, callbacks})
    
    CreateAct->>Comment: actCreate callback<br/>createIssueComment("Running flow...")
    Comment-->>Process: comment {id}
    Process->>Process: Store createdComment
    
    CreateAct->>Comment: sequenceStart callback<br/>updateComment(progressTable)
    CreateAct->>Comment: sequenceComplete callback<br/>updateComment(progressTable)
    
    alt Flow completes successfully
        CreateAct->>Comment: actComplete callback<br/>updateComment("Flow completed")
    else Flow fails
        CreateAct->>Comment: actFail callback<br/>updateComment("Flow failed")
    end
```

The Act is created with inputs containing the webhook event:

```typescript
inputs: [
  {
    type: "github-webhook-event",
    webhookEvent: args.event,
  },
]
```

This makes the webhook payload available to nodes in the workflow via the trigger's outputs.

Sources: [packages/giselle/src/engine/github/event-handlers.ts:551-676](), [packages/giselle/src/engine/github/event-handlers.ts:677-804]()

### Progress Tracking

The event processing system provides real-time progress feedback by posting and updating comments on the GitHub issue/PR/discussion:

**Initial Comment**: Posted when the Act is created, showing a progress table with all sequences and steps in "pending" state.

**Progress Table Format**: HTML table showing sequences and steps with status icons:
- ⚪ Pending
- ⏳ In progress
- 🟢 Success
- ❌ Failed

**Updates**: The comment is updated whenever:
- A sequence starts (`sequenceStart` callback)
- A sequence completes (`sequenceComplete` callback)
- A sequence fails (`sequenceFail` callback)
- The Act completes (`actComplete` callback)
- The Act fails (`actFail` callback)

The progress table data structure:

```typescript
type ProgressTableRow = {
  id: string;
  status: "pending" | "in-progress" | "success" | "failed";
  updatedAt: Date | undefined;
  miniStepProgressTableRows: MiniStepProgressTableRow[];
};

type MiniStepProgressTableRow = {
  id: string;
  name: string;
  status: "pending" | "in-progress" | "success" | "failed";
  updatedAt: Date | undefined;
};
```

Sources: [packages/giselle/src/engine/github/event-handlers.ts:22-134](), [packages/giselle/src/engine/github/event-handlers.ts:548-804]()

## GitHub Actions

### Supported Action Types

GitHub actions allow workflows to interact with repositories during execution. The action registry defines available actions:

| Action ID | Description | Input Fields |
|-----------|-------------|--------------|
| `github.create.issue` | Create a new issue | title, body |
| `github.create.issueComment` | Post a comment on an issue | issue_number, body |
| `github.create.pullRequestComment` | Post a comment on a PR | pull_number, body |
| `github.reply.pullRequestReviewComment` | Reply to a review comment | comment_id, body |
| `github.get.discussion` | Fetch discussion details | discussion_number |
| `github.create.discussionComment` | Post a comment on a discussion | discussion_id, body |

Each action has an icon, label, and defined input fields that are mapped to node inputs when the action is configured.

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/github-action-properties-panel.tsx:82-102](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/ui/github-action-configured-view.tsx:65-83]()

### Action Configuration State Machine

The action configuration follows a simpler flow than triggers:

```mermaid
stateDiagram-v2
    [*] --> Unconfigured
    Unconfigured --> SelectRepository: User opens panel
    SelectRepository --> SelectAction: Repository selected
    SelectAction --> Configured: Action selected
    
    Configured --> Reconfiguring: User clicks "Change Repository"
    Reconfiguring --> SelectRepository
    Reconfiguring --> Configured: Repository changed
```

State types:

```typescript
type GitHubActionSetupStep =
  | { state: "select-repository" }
  | { state: "select-action"; owner: string; repo: string; repoNodeId: string; installationId: number }
  | { state: "configure-action"; owner: string; repo: string; repoNodeId: string; installationId: number; actionId: string }
```

When an action is selected, the component:
1. Looks up the action definition from `githubActions[actionId]`
2. Maps input fields to node inputs using `githubActionToInputFields(action)`
3. Creates inputs with `InputId.generate()` for each field
4. Updates the node with the configuration and inputs
5. Creates a single output with accessor `"action-result"`

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/github-action-properties-panel.tsx:324-458]()

### Action Configuration Flow

```mermaid
sequenceDiagram
    participant User
    participant Panel as GitHubActionPropertiesPanel
    participant Store as Workflow Store
    
    User->>Panel: Select repository
    Panel->>Panel: setState("select-action")
    
    User->>Panel: Select action type
    Panel->>Panel: handleActionSelect(actionId)
    
    Panel->>Panel: githubActionToInputFields(action)
    Panel->>Panel: Create Input[] with generated IDs
    
    Panel->>Store: updateNodeData(node, {<br/>  content: {state: "configured"},<br/>  inputs,<br/>  outputs<br/>})
    
    Store->>Panel: Node updated
    Panel->>User: Show configured view
```

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/github-action-properties-panel.tsx:368-415]()

### Configured Action View

The `GitHubActionConfiguredView` component displays:

1. **Repository Block**: Shows owner/repo with "Change Repository" button
2. **Event Type**: Icon and label for the action (reusing trigger icons)
3. **Input Parameters**: List of inputs with connection status
   - Shows connected source node and output
   - Displays "required" badge for required inputs
   - Shows "Select Source" dropdown for unconnected inputs
4. **Run Action Button**: Triggers execution (or stops if running)

The input connection system uses `useConnectedInputs` hook to resolve which outputs are connected to each input:

```typescript
type InputWithConnectedOutput = Input & {
  connectedOutput?: {
    node: Node;
    label: string;
    connectionId: ConnectionId;
  };
};
```

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/ui/github-action-configured-view.tsx:96-276](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/ui/github-action-configured-view.tsx:284-412]()

### Action Execution

During workflow execution, action nodes execute their configured GitHub operation. The execution is triggered from the properties panel via `createAndStartGenerationRunner`:

```mermaid
sequenceDiagram
    participant User
    participant Panel as ActionNodePropertiesPanel
    participant Hook as useNodeGenerations
    participant Engine as GiselleEngine
    participant GitHub as GitHub API
    
    User->>Panel: Click "Run Action"
    Panel->>Panel: Validate inputs (isValid)
    
    alt Has validation errors
        Panel->>Panel: setUiNodeState({showError: true})
        Panel->>User: Display error indicators
    else Inputs valid
        Panel->>Hook: createAndStartGenerationRunner({<br/>  operationNode,<br/>  sourceNodes,<br/>  connections<br/>})
        Hook->>Engine: Execute action with inputs
        Engine->>GitHub: API call (create issue, post comment, etc.)
        GitHub-->>Engine: Response
        Engine-->>Hook: Generation complete
        Hook->>Panel: Update UI
    end
```

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/index.tsx:12-80]()

## Data Model and Protocol

### GitHub Event Data Schema

The protocol package defines event data structures using Zod schemas:

```typescript
// Base event types (no conditions)
const GitHubIssueCreatedEventData = z.object({
  id: z.literal("github.issue.created"),
});

// Comment events (require callsign)
const GitHubEventIssueCommentCreatedData = z.object({
  id: z.literal("github.issue_comment.created"),
  conditions: z.object({
    callsign: z.string(),
  }),
});

// Label events (require labels array)
const GitHubEventIssueLabeledData = z.object({
  id: z.literal("github.issue.labeled"),
  conditions: z.object({
    labels: z.array(z.string()).min(1),
  }),
});

// Discriminated union of all event types
export const GitHubEventData = z.discriminatedUnion("id", [
  GitHubIssueCreatedEventData,
  GitHubEventIssueClosedData,
  GitHubEventIssueCommentCreatedData,
  GitHubEventIssueLabeledData,
  // ... 8 more event types
]);
```

The complete configuration structure:

```typescript
export const GitHubEventConfiguration = z.object({
  provider: z.literal("github"),
  event: GitHubEventData,
  installationId: z.number(),
  repositoryNodeId: z.string(),
});
```

Sources: [packages/protocol/src/trigger/github.ts:1-107]()

### Node State Schema

Trigger nodes maintain state in their `content.state` field:

```typescript
type TriggerNodeState =
  | { status: "unconfigured" }
  | { status: "configured"; flowTriggerId: TriggerId }
  | { status: "reconfiguring"; flowTriggerId: TriggerId }
```

Action nodes maintain state in their `content.command.state` field:

```typescript
type ActionCommandState =
  | { status: "unconfigured"; provider: "github" }
  | { status: "configured"; provider: "github"; commandId: string; repositoryNodeId: string; installationId: number }
  | { status: "reconfiguring"; provider: "github"; commandId: string }
```

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/github-trigger-properties-panel.tsx:165-198](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/github-action-properties-panel.tsx:116-146]()

### Helper Functions

The `createTriggerEvent` utility creates properly typed event configurations:

```typescript
function createTriggerEvent(args: {
  eventId: GitHubEventId;
  callsign?: string;
  labels?: string[];
}): GitHubEventData {
  switch (args.eventId) {
    case "github.issue.created":
    case "github.issue.closed":
      return { id: args.eventId };
    
    case "github.issue_comment.created":
      if (!args.callsign || args.callsign.length === 0) {
        throw new Error("Callsign is required for this trigger type");
      }
      return {
        id: args.eventId,
        conditions: { callsign: args.callsign },
      };
    
    case "github.issue.labeled":
      if (!args.labels || args.labels.length === 0) {
        throw new Error("Labels are required for this trigger type");
      }
      return {
        id: args.eventId,
        conditions: { labels: args.labels },
      };
    
    // ... other cases
  }
}
```

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/utils/trigger-configuration.ts:1-50]()

## Code Organization

### UI Components Hierarchy

```
internal-packages/workflow-designer-ui/src/editor/properties-panel/
├── action-node-properties-panel/
│   ├── index.tsx                           # Main action panel wrapper
│   ├── github-action-properties-panel.tsx  # GitHub action configuration UI
│   ├── ui/
│   │   └── github-action-configured-view.tsx  # Configured action display
│   └── lib/
│       └── use-connected-inputs.ts         # Input connection resolution
│
├── trigger-node-properties-panel/
│   ├── providers/
│   │   └── github-trigger/
│   │       ├── github-trigger-properties-panel.tsx  # Main trigger configuration
│   │       ├── components/
│   │       │   ├── event-selection-step.tsx
│   │       │   ├── event-type-display.tsx
│   │       │   ├── labels-input-step.tsx
│   │       │   ├── repository-display.tsx
│   │       │   ├── unauthorized.tsx
│   │       │   ├── install-application.tsx
│   │       │   └── icons/
│   │       │       └── index.tsx            # Event type icons
│   │       └── utils/
│   │           ├── trigger-configuration.ts  # createTriggerEvent helper
│   │           └── use-trigger-configuration.ts  # Configuration hook
│   └── ui/
│       ├── configured-views/
│       │   └── github-trigger-configured-view.tsx  # Configured trigger display
│       ├── reconfiguring-views/
│       │   └── github-trigger-reconfiguring-view.tsx
│       └── select-repository.tsx            # Shared repository picker
│
└── ui/
    ├── select-repository.tsx                # Repository selection component
    └── ...
```

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/github-action-properties-panel.tsx:1-10](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/github-trigger-properties-panel.tsx:1-48]()

### Backend Event Processing

```
packages/giselle/src/engine/github/
├── event-handlers.ts          # Event handler implementations
│   ├── handleIssueOpened()
│   ├── handleIssueClosed()
│   ├── handleIssueCommentCreated()
│   ├── handleIssueLabeled()
│   ├── handlePullRequestCommentCreated()
│   ├── handlePullRequestReviewCommentCreated()
│   ├── handlePullRequestOpened()
│   ├── handlePullRequestReadyForReview()
│   ├── handlePullRequestClosed()
│   ├── handlePullRequestLabeled()
│   ├── handleDiscussionCreated()
│   ├── handleDiscussionCommentCreated()
│   └── processEvent()          # Main event router
│
└── event-handlers.test.ts      # Comprehensive test suite
```

Sources: [packages/giselle/src/engine/github/event-handlers.ts:1-150](), [packages/giselle/src/engine/github/event-handlers.ts:462-804]()

### Protocol Definitions

```
packages/protocol/src/trigger/
└── github.ts                   # GitHub event type definitions
    ├── GitHubEventData         # Discriminated union of all events
    ├── GitHubEventConfiguration  # Trigger configuration structure
    └── Individual event schemas
```

Sources: [packages/protocol/src/trigger/github.ts:1-107]()

### Key Dependencies

The GitHub integration relies on several key dependencies:

- **Event Handler Dependencies** (`EventHandlerDependencies`): Injected functions for GitHub API operations, reaction management, comment creation/updating, and Act creation
- **GitHub Tool Package** (`@giselles-ai/github-tool`): Provides GitHub API client functions and webhook event type definitions
- **Trigger Registry** (`@giselles-ai/trigger-registry`): Defines available GitHub event types and their metadata
- **Action Registry** (`@giselles-ai/action-registry`): Defines available GitHub action types and their input fields

Sources: [packages/giselle/src/engine/github/event-handlers.ts:136-149]()

---

# Page: GitHub Triggers and Event Processing

# GitHub Triggers and Event Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/github-action-properties-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/github-action-properties-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/index.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/ui/github-action-configured-view.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/ui/github-action-configured-view.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/event-type-display.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/event-type-display.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/icons/index.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/icons/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/install-application.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/install-application.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/labels-input-step.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/labels-input-step.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/unauthorized.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/unauthorized.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/github-trigger-properties-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/github-trigger-properties-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/utils/trigger-configuration.ts](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/utils/trigger-configuration.ts)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/utils/use-trigger-configuration.ts](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/utils/use-trigger-configuration.ts)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/manual-trigger/manual-trigger-properties-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/manual-trigger/manual-trigger-properties-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/ui/configured-views/github-trigger-configured-view.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/ui/configured-views/github-trigger-configured-view.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/select-repository.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/select-repository.tsx)
- [packages/giselle/src/engine/github/event-handlers.test.ts](packages/giselle/src/engine/github/event-handlers.test.ts)
- [packages/giselle/src/engine/github/event-handlers.ts](packages/giselle/src/engine/github/event-handlers.ts)
- [packages/protocol/src/trigger/github.ts](packages/protocol/src/trigger/github.ts)

</details>



This document describes the GitHub trigger system, which enables workflows to execute automatically in response to GitHub webhook events. It covers trigger configuration through the UI, webhook event processing, event matching logic, and Act execution initiation.

For information about GitHub Actions (performing actions on GitHub repositories), see [GitHub Actions and Integration](#4.2). For the broader Act execution lifecycle, see [Act Runner and Workflow Orchestration](#2.4).

## Purpose and Scope

The GitHub trigger system enables workflows to respond to GitHub repository events such as issue creation, pull request comments, and label additions. Users configure triggers through a multi-step UI, specifying the event type, target repository, and optional conditions (callsigns for comment events, labels for labeled events). When GitHub sends webhooks to the platform, the event processing engine matches incoming events against configured triggers and initiates Act executions for matching workflows.

## Trigger Configuration States

GitHub triggers progress through several states during configuration and operation:

```mermaid
stateDiagram-v2
    [*] --> Unconfigured
    Unconfigured --> SelectEvent: User adds trigger node
    SelectEvent --> SelectRepository: Event selected
    SelectRepository --> InputCallsign: Callsign required
    SelectRepository --> InputLabels: Labels required
    SelectRepository --> Configured: No conditions required
    InputCallsign --> Configured: Callsign provided
    InputLabels --> Configured: Labels provided
    Configured --> Reconfiguring: User changes config
    Reconfiguring --> Configured: Configuration updated
    Configured --> [*]: Trigger active
```

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/github-trigger-properties-panel.tsx:230-273]()

The trigger node's `content.state.status` field tracks these states:
- `unconfigured` - Initial state when node is created
- `configured` - Trigger is configured with a `flowTriggerId`
- `reconfiguring` - User is modifying an existing configuration

## GitHub Integration Authentication States

Before configuring triggers, the GitHub integration must be authenticated and installed:

| State | Description | User Action Required |
|-------|-------------|---------------------|
| `unset` | No GitHub configuration | N/A - system error |
| `unauthorized` | User needs to authorize GitHub App | Click "Continue with GitHub" |
| `not-installed` | GitHub App not installed on any accounts | Click "Install" |
| `invalid-credential` | Credentials expired or invalid | Re-authenticate |
| `installed` | GitHub App installed, ready to configure | Proceed with trigger configuration |
| `error` | Integration error occurred | Check error message |

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/github-trigger-properties-panel.tsx:200-227]()

## Trigger Configuration Workflow

### Configuration Steps

The `GitHubTriggerPropertiesPanel` component implements a multi-step configuration wizard:

```mermaid
graph TB
    SelectEvent["SelectEventStep<br/>{state: 'select-event'}"]
    SelectRepo["SelectRepositoryStep<br/>{state: 'select-repository'<br/>eventId: GitHubEventId}"]
    ConfirmRepo["ConfirmRepositoryStep<br/>{state: 'confirm-repository'<br/>eventId, owner, repo,<br/>repoNodeId, installationId}"]
    InputCallsign["InputCallsignStep<br/>{state: 'input-callsign'<br/>eventId, owner, repo,<br/>repoNodeId, installationId,<br/>callsign?}"]
    InputLabels["InputLabelsStep<br/>{state: 'input-labels'<br/>eventId, owner, repo,<br/>repoNodeId, installationId,<br/>labels?}"]
    ConfigureTrigger["configureTrigger()<br/>Creates flow_triggers record"]
    
    SelectEvent -->|"User selects event type"| SelectRepo
    SelectRepo -->|"User selects installation"| ConfirmRepo
    ConfirmRepo -->|"isTriggerRequiringCallsign()"| InputCallsign
    ConfirmRepo -->|"isTriggerRequiringLabels()"| InputLabels
    ConfirmRepo -->|"No conditions"| ConfigureTrigger
    InputCallsign -->|"Callsign provided"| ConfigureTrigger
    InputLabels -->|"Labels provided"| ConfigureTrigger
    ConfigureTrigger -->|"Returns triggerId"| Configured["Trigger Configured"]
```

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/github-trigger-properties-panel.tsx:230-273](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/github-trigger-properties-panel.tsx:278-295]()

### Event Type Selection

The `EventSelectionStep` component displays all available GitHub events:

| Event ID | Label | Requires Callsign | Requires Labels |
|----------|-------|-------------------|-----------------|
| `github.issue.created` | Issue Created | No | No |
| `github.issue.closed` | Issue Closed | No | No |
| `github.issue.labeled` | Issue Labeled | No | Yes |
| `github.issue_comment.created` | Issue Comment Created | Yes | No |
| `github.pull_request.opened` | Pull Request Opened | No | No |
| `github.pull_request.ready_for_review` | Pull Request Ready For Review | No | No |
| `github.pull_request.closed` | Pull Request Closed | No | No |
| `github.pull_request.labeled` | Pull Request Labeled | No | Yes |
| `github.pull_request_comment.created` | Pull Request Comment Created | Yes | No |
| `github.pull_request_review_comment.created` | Pull Request Review Comment Created | Yes | No |
| `github.discussion.created` | Discussion Created | No | No |
| `github.discussion_comment.created` | Discussion Comment Created | Yes | No |

Sources: [packages/protocol/src/trigger/github.ts:1-107](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/github-trigger-properties-panel.tsx:278-295]()

### Repository Selection

The `SelectRepository` component manages GitHub App installations and repository selection:

```mermaid
graph LR
    Installations["GitHubIntegrationInstallation[]<br/>From integration context"]
    OrgDropdown["Organization Dropdown<br/>Select installation"]
    RepoList["Repository List<br/>installation.repositories[]"]
    Selected["Selected Repository<br/>{installationId, owner,<br/>repo, repoNodeId}"]
    
    Installations --> OrgDropdown
    OrgDropdown -->|"setSelectedInstallationId"| RepoList
    RepoList -->|"onSelectRepository"| Selected
```

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/select-repository.tsx:19-252]()

### Callsign Input

For comment-based triggers, the `InputCallsignStep` collects a callsign that must appear at the start of comments:

```typescript
// Callsign format: /callsign
// Example: /code-review, /check-policy
```

The system parses comments using `parseCommand()` to extract the callsign:

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/github-trigger-properties-panel.tsx:343-403](), [packages/giselle/src/engine/github/event-handlers.ts:200-226]()

### Labels Input

For label-based triggers, the `LabelsInputStep` collects an array of labels that act as OR conditions:

```typescript
// If any of the specified labels is added, the trigger fires
// Example: ["bug", "urgent", "needs-review"]
```

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/labels-input-step.tsx:1-184]()

### Trigger Storage

The `useTriggerConfiguration` hook calls `client.configureTrigger()` which creates a record in the `flow_triggers` table:

```typescript
{
  nodeId: NodeId,
  workspaceId: string,
  enable: boolean,
  configuration: {
    provider: "github",
    repositoryNodeId: string,
    installationId: number,
    event: GitHubEventData
  }
}
```

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/utils/use-trigger-configuration.ts:29-86]()

## Event Handler Architecture

### Event Processing Flow

When GitHub sends a webhook, the system processes it through multiple layers:

```mermaid
graph TB
    Webhook["GitHub Webhook<br/>WebhookEvent&lt;TEventName&gt;"]
    ProcessEvent["processEvent()<br/>Main router function"]
    TriggerQuery["Query flow_triggers<br/>WHERE provider='github'<br/>AND enable=true"]
    HandlerLoop["Loop through<br/>eventHandlers array"]
    Handler["Event Handler Function<br/>handleIssueOpened(),<br/>handleIssueCommentCreated(), etc."]
    Match["Match Result<br/>{shouldRun: boolean,<br/>reactionNodeId?: string}"]
    AddReaction["addReaction()<br/>Add 👀 emoji"]
    CreateAct["createAndStartAct()<br/>Initialize workflow execution"]
    ProgressComments["Progress Tracking<br/>Create & update GitHub comments"]
    
    Webhook --> ProcessEvent
    ProcessEvent --> TriggerQuery
    TriggerQuery --> HandlerLoop
    HandlerLoop --> Handler
    Handler --> Match
    Match -->|"shouldRun=true"| AddReaction
    Match -->|"shouldRun=false"| HandlerLoop
    AddReaction --> CreateAct
    CreateAct --> ProgressComments
```

Sources: [packages/giselle/src/engine/github/event-handlers.ts:477-821]()

### Event Handler Array

The system uses an array of handler functions that are checked in sequence:

```typescript
const eventHandlers = [
  handleIssueOpened,
  handleIssueClosed,
  handleIssueCommentCreated,
  handleIssueLabeled,
  handlePullRequestCommentCreated,
  handlePullRequestReviewCommentCreated,
  handlePullRequestOpened,
  handlePullRequestReadyForReview,
  handlePullRequestClosed,
  handlePullRequestLabeled,
  handleDiscussionCreated,
  handleDiscussionCommentCreated,
]
```

Sources: [packages/giselle/src/engine/github/event-handlers.ts:462-475]()

### Individual Event Handlers

Each handler implements the same signature and returns a match result:

```mermaid
graph TB
    Input["EventHandlerArgs<br/>{event, context, trigger,<br/>authConfig, deps}"]
    EnsureEvent["deps.ensureWebhookEvent()<br/>Type guard for event name"]
    CheckTriggerId["Check trigger.configuration<br/>.event.id matches"]
    ExtractPayload["Extract payload data<br/>(issue, comment, etc)"]
    CheckConditions["Check conditions<br/>(callsign, labels)"]
    Return["Return EventHandlerResult<br/>{shouldRun, reactionNodeId?}"]
    
    Input --> EnsureEvent
    EnsureEvent -->|"Type mismatch"| NoRun["Return {shouldRun: false}"]
    EnsureEvent -->|"Type matches"| CheckTriggerId
    CheckTriggerId -->|"ID mismatch"| NoRun
    CheckTriggerId -->|"ID matches"| ExtractPayload
    ExtractPayload -->|"Missing data"| NoRun
    ExtractPayload -->|"Has data"| CheckConditions
    CheckConditions -->|"Condition fails"| NoRun
    CheckConditions -->|"Condition passes"| Return
```

Sources: [packages/giselle/src/engine/github/event-handlers.ts:164-180](), [packages/giselle/src/engine/github/event-handlers.ts:200-226]()

### Callsign Matching

For comment-based events, handlers use `parseCommand()` to extract and match callsigns:

```typescript
// Handler extracts callsign from comment
const command = deps.parseCommand(comment.body);

// Compare with configured callsign
const conditions = trigger.configuration.event.conditions;
if (command?.callsign !== conditions?.callsign) {
  return { shouldRun: false };
}
```

Sources: [packages/giselle/src/engine/github/event-handlers.ts:200-226](), [packages/giselle/src/engine/github/event-handlers.ts:228-257]()

### Label Matching

For label-based events, handlers check if the added label is in the configured set:

```typescript
// Extract added label from event
const addedLabel = event.data.payload.label;

// Check if it's in the configured labels array
const conditions = trigger.configuration.event.conditions;
const shouldRun = conditions.labels.includes(addedLabel.name);
```

Sources: [packages/giselle/src/engine/github/event-handlers.ts:353-384](), [packages/giselle/src/engine/github/event-handlers.ts:386-417]()

## Act Execution and Progress Tracking

### Act Creation with Callbacks

When an event matches, `processEvent()` calls `deps.createAndStartAct()` with lifecycle callbacks:

```mermaid
graph TB
    CreateAct["createAndStartAct()<br/>{context, nodeId,<br/>workspace, inputs,<br/>callbacks}"]
    ActCreate["callbacks.actCreate<br/>{act}"]
    InitProgress["Initialize progressTableData<br/>from act.sequences[]"]
    CreateComment["Create GitHub comment<br/>createIssueComment() or<br/>createPullRequestComment()"]
    SeqStart["callbacks.sequenceStart<br/>{sequence}"]
    UpdateProgress["Update progressTableData<br/>Map step.status to<br/>mini-step status"]
    UpdateComment["updateIssueComment() or<br/>updatePullRequestReviewComment()"]
    SeqComplete["callbacks.sequenceComplete<br/>{sequence}"]
    ActComplete["callbacks.actComplete<br/>{act}"]
    FinalComment["Final comment update<br/>Flow completed successfully"]
    
    CreateAct --> ActCreate
    ActCreate --> InitProgress
    InitProgress --> CreateComment
    CreateComment --> SeqStart
    SeqStart --> UpdateProgress
    UpdateProgress --> UpdateComment
    UpdateComment --> SeqComplete
    SeqComplete --> ActComplete
    ActComplete --> FinalComment
```

Sources: [packages/giselle/src/engine/github/event-handlers.ts:556-749]()

### Progress Table Structure

The system builds an HTML table to display progress in GitHub comments:

```typescript
type MiniStepProgressTableRow = {
  id: string,
  name: string,
  status: "pending" | "in-progress" | "success" | "failed",
  updatedAt: Date | undefined
}

type ProgressTableRow = {
  id: string,
  status: "pending" | "in-progress" | "success" | "failed",
  updatedAt: Date | undefined,
  miniStepProgressTableRows: MiniStepProgressTableRow[]
}

type ProgressTableData = ProgressTableRow[]
```

Sources: [packages/giselle/src/engine/github/event-handlers.ts:23-38]()

The `buildProgressTable()` function converts this data to HTML:

```html
<table>
  <tbody>
    <tr><td colspan='2'><strong>Step 1</strong></td></tr>
    <tr><td>⏳</td><td><details><summary><strong>Node Name</strong></summary>Status: In progress\nUpdated: Jan 1, 2024 12:00pm</details></td></tr>
    ...
  </tbody>
</table>
```

Sources: [packages/giselle/src/engine/github/event-handlers.ts:94-134]()

### Status Icon Mapping

The system maps Act step statuses to visual indicators:

| Step Status | Mini-Step Status | Icon | Display Text |
|-------------|------------------|------|--------------|
| `created` | `pending` | ⚪ | Pending |
| `queued` | `pending` | ⚪ | Pending |
| `running` | `in-progress` | ⏳ | In progress |
| `completed` | `success` | 🟢 | Success |
| `failed` | `failed` | ❌ | Failed |
| `cancelled` | `failed` | ❌ | Failed |

Sources: [packages/giselle/src/engine/github/event-handlers.ts:67-92]()

### Comment Creation by Event Type

Different event types require different comment creation methods:

```mermaid
graph TB
    EventType["Check webhook event type<br/>ensureWebhookEvent()"]
    IssueEvent["Issue events<br/>(opened, closed, labeled)"]
    PREvent["PR events<br/>(opened, closed, labeled)"]
    ReviewComment["PR review comment"]
    Discussion["Discussion events"]
    
    IssueComment["createIssueComment()<br/>{repositoryNodeId,<br/>issueNumber, body}"]
    PRComment["createPullRequestComment()<br/>{repositoryNodeId,<br/>pullNumber, body}"]
    ReviewReply["replyPullRequestReviewComment()<br/>{repositoryNodeId, pullNumber,<br/>commentId, body}"]
    DiscussionComment["createDiscussionComment()<br/>{discussionId, body,<br/>replyToId?}"]
    
    EventType --> IssueEvent
    EventType --> PREvent
    EventType --> ReviewComment
    EventType --> Discussion
    
    IssueEvent --> IssueComment
    PREvent --> PRComment
    ReviewComment --> ReviewReply
    Discussion --> DiscussionComment
```

Sources: [packages/giselle/src/engine/github/event-handlers.ts:583-675]()

## Event Handler Dependencies

The `processEvent()` function requires an `EventHandlerDependencies` object providing testable dependencies:

```typescript
interface EventHandlerDependencies {
  addReaction: typeof addReaction;
  ensureWebhookEvent: typeof ensureWebhookEvent;
  createAndStartAct: typeof createAndStartAct;
  parseCommand: typeof parseCommand;
  createIssueComment: typeof createIssueComment;
  createPullRequestComment: typeof createPullRequestComment;
  replyPullRequestReviewComment: typeof replyPullRequestReviewComment;
  updateIssueComment: typeof updateIssueComment;
  updatePullRequestReviewComment: typeof updatePullRequestReviewComment;
  createDiscussionComment: typeof createDiscussionComment;
  updateDiscussionComment: typeof updateDiscussionComment;
  getDiscussionForCommentCreation: typeof getDiscussionForCommentCreation;
}
```

Sources: [packages/giselle/src/engine/github/event-handlers.ts:136-149]()

## Configured Trigger Display

### GitHubTriggerConfiguredView Component

Once configured, triggers display their settings in the `GitHubTriggerConfiguredView`:

```mermaid
graph TB
    View["GitHubTriggerConfiguredView"]
    Toggle["Enable/Disable Toggle<br/>enableFlowTrigger()<br/>disableFlowTrigger()"]
    EventDisplay["Event Type Display<br/>Icon + Label"]
    RepoDisplay["Repository Display<br/>owner/repo"]
    CallsignDisplay["Callsign Display<br/>(if applicable)<br/>/callsign + copy button"]
    LabelsDisplay["Labels Display<br/>(if applicable)<br/>Label badges"]
    ChangeButtons["Change Buttons<br/>beginReconfigure()"]
    
    View --> Toggle
    View --> EventDisplay
    View --> RepoDisplay
    View --> CallsignDisplay
    View --> LabelsDisplay
    View --> ChangeButtons
    
    ChangeButtons -->|"mode='repository'"| RepoReconfig["Set state to<br/>'reconfiguring'"]
    ChangeButtons -->|"mode='callsign'"| CallsignReconfig["Set state to<br/>'reconfiguring'"]
    ChangeButtons -->|"mode='labels'"| LabelsReconfig["Set state to<br/>'reconfiguring'"]
```

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/ui/configured-views/github-trigger-configured-view.tsx:70-320]()

### Reconfiguration Modes

The configured view supports reconfiguring different aspects of the trigger:

```typescript
type GitHubTriggerReconfigureMode = "repository" | "callsign" | "labels"
```

When a reconfiguration begins, the system:
1. Sets `node.content.state.status` to `"reconfiguring"`
2. Stores the `reconfigureMode` in a ref
3. Calls `client.reconfigureGitHubTrigger()` with the new configuration
4. Updates the UI back to `"configured"` status

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/github-trigger-properties-panel.tsx:50](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/ui/configured-views/github-trigger-configured-view.tsx:104-115]()

## Event Handler Testing

The event handlers are tested using mocked dependencies to verify matching logic without external dependencies:

```typescript
// Test structure
const testDeps: EventHandlerDependencies = {
  addReaction: vi.fn().mockResolvedValue(undefined),
  ensureWebhookEvent: createEnsureWebhookEventMock(),
  createAndStartAct: vi.fn().mockResolvedValue(undefined),
  parseCommand: vi.fn().mockReturnValue({ callsign: "giselle", content: "help me" }),
  // ... other mocked methods
}
```

Tests verify:
- Event type matching via `ensureWebhookEvent()`
- Trigger event ID matching
- Callsign extraction and comparison
- Label matching logic
- Reaction node ID extraction

Sources: [packages/giselle/src/engine/github/event-handlers.test.ts:54-126](), [packages/giselle/src/engine/github/event-handlers.test.ts:129-207]()

## Integration with Workflow System

### Trigger Node Output Configuration

When a trigger is configured, the system generates outputs based on the event type:

```typescript
const outputs: Output[] = githubEventToInputFields(githubEvent).map(
  (inputField) => ({
    id: OutputId.generate(),
    label: inputField.label,
    accessor: inputField.key,
  })
)
```

These outputs become available for downstream nodes to consume through connections.

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/utils/use-trigger-configuration.ts:58-64]()

### Webhook Event Input

When `createAndStartAct()` is called, the webhook event is passed as an input:

```typescript
inputs: [
  {
    type: "github-webhook-event",
    webhookEvent: event
  }
]
```

This makes the full webhook payload available to nodes in the workflow through the trigger node's outputs.

Sources: [packages/giselle/src/engine/github/event-handlers.ts:561-566]()

---

# Page: GitHub Actions and Integration

# GitHub Actions and Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/github-action-properties-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/github-action-properties-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/index.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/ui/github-action-configured-view.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/ui/github-action-configured-view.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/event-type-display.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/event-type-display.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/icons/index.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/icons/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/install-application.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/install-application.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/labels-input-step.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/labels-input-step.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/unauthorized.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/unauthorized.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/github-trigger-properties-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/github-trigger-properties-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/utils/trigger-configuration.ts](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/utils/trigger-configuration.ts)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/utils/use-trigger-configuration.ts](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/utils/use-trigger-configuration.ts)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/manual-trigger/manual-trigger-properties-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/manual-trigger/manual-trigger-properties-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/ui/configured-views/github-trigger-configured-view.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/ui/configured-views/github-trigger-configured-view.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/select-repository.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/select-repository.tsx)
- [packages/giselle/src/engine/github/event-handlers.test.ts](packages/giselle/src/engine/github/event-handlers.test.ts)
- [packages/giselle/src/engine/github/event-handlers.ts](packages/giselle/src/engine/github/event-handlers.ts)
- [packages/protocol/src/trigger/github.ts](packages/protocol/src/trigger/github.ts)

</details>



## Purpose and Scope

This document describes the GitHub action node system, which enables workflows to perform operations on GitHub repositories such as creating issues, posting comments, and managing discussions. GitHub actions are output-oriented nodes that write data to GitHub, as opposed to GitHub triggers which respond to incoming webhook events. For information about GitHub triggers (webhooks that initiate workflow execution), see [GitHub Triggers and Event Processing](#4.1).

## Action Node Architecture

### Node Type and States

GitHub action nodes are operation nodes with a `command` property that specifies GitHub as the provider. The action configuration follows a state machine pattern:

```mermaid
stateDiagram-v2
    [*] --> unconfigured
    unconfigured --> configured: User completes setup
    configured --> reconfiguring: User clicks "Change Repository"
    reconfiguring --> configured: User selects new repository
```

**Configuration State Structure**

| State | Description | UI Behavior |
|-------|-------------|-------------|
| `unconfigured` | No GitHub action configured | Shows action selection flow |
| `configured` | Action fully configured with repository and inputs | Shows parameter inputs and "Run Action" button |
| `reconfiguring` | User is changing repository settings | Shows repository selection only |

The action node structure is defined by the `ActionNode` type, where `node.content.command.provider === "github"` and `node.content.command.state` contains the configuration.

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/github-action-properties-panel.tsx:115-178](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/ui/github-action-configured-view.tsx:96-143]()

## Available GitHub Actions

### Action Registry

The system supports six GitHub action types registered in `@giselles-ai/action-registry`:

```mermaid
graph TD
    ActionRegistry["@giselles-ai/action-registry<br/>githubActions"]
    
    IssueCreate["github.create.issue<br/>Create Issue"]
    IssueComment["github.create.issueComment<br/>Create Issue Comment"]
    PRComment["github.create.pullRequestComment<br/>Create PR Comment"]
    PRReviewReply["github.reply.pullRequestReviewComment<br/>Reply to Review Comment"]
    DiscussionGet["github.get.discussion<br/>Get Discussion"]
    DiscussionComment["github.create.discussionComment<br/>Create Discussion Comment"]
    
    ActionRegistry --> IssueCreate
    ActionRegistry --> IssueComment
    ActionRegistry --> PRComment
    ActionRegistry --> PRReviewReply
    ActionRegistry --> DiscussionGet
    ActionRegistry --> DiscussionComment
```

### Action Input Fields

Each action defines input fields through `githubActionToInputFields()`, which are converted to node inputs:

| Action | Required Inputs | Description |
|--------|----------------|-------------|
| `github.create.issue` | title, body | Creates a new issue in the repository |
| `github.create.issueComment` | issue_number, body | Adds a comment to an existing issue |
| `github.create.pullRequestComment` | pull_number, body | Adds a comment to a pull request |
| `github.reply.pullRequestReviewComment` | pull_number, comment_id, body | Replies to a PR review comment |
| `github.get.discussion` | discussion_number | Retrieves discussion details |
| `github.create.discussionComment` | discussion_id, body | Adds a comment to a discussion |

When an action is selected, the system generates `Input` objects with `isRequired` flags based on the action's field definitions.

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/github-action-properties-panel.tsx:1-10](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/ui/github-action-configured-view.tsx:380-411]()

## Configuration UI Flow

### Setup State Machine

```mermaid
stateDiagram-v2
    [*] --> SelectRepositoryStep
    SelectRepositoryStep --> SelectActionStep: Repository selected
    SelectActionStep --> Configured: Action selected
    Configured --> [*]
    
    note right of SelectRepositoryStep
        User picks organization
        and repository
    end note
    
    note right of SelectActionStep
        User chooses action type
        (create issue, comment, etc)
    end note
    
    note right of Configured
        GitHubActionConfiguredView
        shows input parameters
    end note
```

### Step 1: Repository Selection

The `Installed` component in `github-action-properties-panel.tsx` manages the repository selection flow:

1. **Organization Selection**: User selects from GitHub App installations via dropdown populated from `GitHubIntegrationInstallation[]`
2. **Repository Selection**: After organization selection, available repositories are displayed as clickable cards
3. **State Transition**: Selection triggers `handleSelectRepository()` which either:
   - For new actions: moves to action selection (`select-action` state)
   - For reconfiguration: updates the repository and returns to configured state

```mermaid
sequenceDiagram
    participant User
    participant SelectRepository as SelectRepository Component
    participant Installations as GitHub Installations
    participant Node as Action Node State
    
    User->>SelectRepository: Click organization dropdown
    SelectRepository->>Installations: Query installations
    Installations-->>SelectRepository: Return organizations list
    User->>SelectRepository: Select organization
    SelectRepository->>SelectRepository: setSelectedInstallationId(id)
    SelectRepository->>Installations: Get repositories for installation
    Installations-->>SelectRepository: Return repositories[]
    SelectRepository->>User: Display repository cards
    User->>SelectRepository: Click repository
    SelectRepository->>Node: handleSelectRepository({installationId, owner, repo, repoNodeId})
    Node->>Node: Update state to select-action or configured
```

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/github-action-properties-panel.tsx:347-457](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/select-repository.tsx:19-252]()

### Step 2: Action Type Selection

After repository selection, the `select-action` step displays all available GitHub actions:

```mermaid
graph LR
    ActionList["Action Selection Grid"]
    
    subgraph "Rendered Action Buttons"
        A1["Create Issue<br/>IssueCreatedIcon"]
        A2["Create Issue Comment<br/>IssueCommentCreatedIcon"]
        A3["Create PR Comment<br/>PRCommentCreatedIcon"]
        A4["Reply Review Comment<br/>ReviewCommentIcon"]
        A5["Get Discussion<br/>DefaultActionIcon"]
        A6["Create Discussion Comment<br/>DiscussionCommentIcon"]
    end
    
    ActionList --> A1
    ActionList --> A2
    ActionList --> A3
    ActionList --> A4
    ActionList --> A5
    ActionList --> A6
    
    A1 -->|handleActionSelect| ConfiguredNode["Node with inputs/outputs"]
    A2 -->|handleActionSelect| ConfiguredNode
    A3 -->|handleActionSelect| ConfiguredNode
```

The `handleActionSelect` callback performs these operations:
1. Validates the action ID with `isGitHubActionId()`
2. Retrieves action definition from `githubActions[actionId]`
3. Generates `Input[]` array from `githubActionToInputFields()`
4. Creates a single output with accessor `"action-result"`
5. Updates node data with configured state

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/github-action-properties-panel.tsx:368-415](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/github-action-properties-panel.tsx:544-606]()

## Configured Action View

### Input Parameter Management

Once configured, `GitHubActionConfiguredView` displays a comprehensive parameter binding interface:

```mermaid
graph TB
    ConfiguredView["GitHubActionConfiguredView"]
    
    subgraph "Display Elements"
        RepoBlock["GitHubRepositoryBlock<br/>Shows owner/repo"]
        ActionType["Action Type Display<br/>Icon + Label"]
        InputParams["Input Parameters List"]
    end
    
    subgraph "Input Connection UI"
        InputRow["Input Row per Parameter"]
        ConnectedChip["Connected Output Chip<br/>Shows source node/output"]
        SelectDropdown["SelectOutputPopover<br/>Dropdown to pick source"]
        RemoveBtn["Remove Connection Button"]
    end
    
    subgraph "Actions"
        ChangeRepo["Change Repository Button"]
        RunAction["Run Action Button"]
    end
    
    ConfiguredView --> RepoBlock
    ConfiguredView --> ActionType
    ConfiguredView --> InputParams
    
    InputParams --> InputRow
    InputRow --> ConnectedChip
    InputRow --> SelectDropdown
    ConnectedChip --> RemoveBtn
    
    ConfiguredView --> ChangeRepo
    ConfiguredView --> RunAction
```

### Parameter Binding

Each required input must be connected to an output from another node. The `useConnectedInputs` hook enriches inputs with connection information:

```typescript
interface InputWithConnectedOutput {
  id: string;
  label: string;
  isRequired: boolean;
  connectedOutput?: {
    node: Node;
    label: string;
    connectionId: ConnectionId;
  };
}
```

The `SelectOutputPopover` component groups available outputs by node type:
- Text Generator nodes
- Action nodes
- Trigger nodes
- Text nodes
- File nodes
- GitHub nodes

Connection validation uses `isSupportedConnection()` to ensure type compatibility between source and target nodes.

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/ui/github-action-configured-view.tsx:96-276](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/ui/github-action-configured-view.tsx:284-412]()

### Repository Display and Reconfiguration

The repository information is fetched asynchronously using SWR:

```typescript
const { isLoading, data } = useSWR(
  { installationId, repositoryNodeId },
  ({ installationId, repositoryNodeId }) =>
    client.getGitHubRepositoryFullname({
      installationId,
      repositoryNodeId,
    })
);
```

The "Change Repository" button triggers reconfiguration by updating node state:

```typescript
updateNodeData(node, {
  content: {
    ...node.content,
    command: {
      provider: "github",
      state: {
        status: "reconfiguring",
        commandId: state.commandId,
      },
    },
  },
});
```

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/ui/github-action-configured-view.tsx:109-180]()

## Action Execution

### Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant PropertiesPanel as ActionNodePropertiesPanel
    participant Validator as useConnectedInputs
    participant Engine as GiselleEngine
    participant Runner as GenerationRunner
    participant GitHub as GitHub API
    
    User->>PropertiesPanel: Click "Run Action"
    PropertiesPanel->>Validator: Check isValid (all required inputs connected)
    
    alt Invalid inputs
        Validator-->>PropertiesPanel: isValid = false
        PropertiesPanel->>PropertiesPanel: setUiNodeState({showError: true})
        PropertiesPanel-->>User: Display error indicators
    else Valid inputs
        PropertiesPanel->>Engine: createAndStartGenerationRunner()
        Engine->>Runner: Create runner with operationNode + sourceNodes
        Runner->>Runner: Build execution context from connections
        Runner->>GitHub: Execute GitHub action via github-tool
        GitHub-->>Runner: Return action result
        Runner-->>PropertiesPanel: Update generation status
        PropertiesPanel-->>User: Display completion
    end
```

The execution is managed by `ActionNodePropertiesPanel`:

1. **Validation**: `isValid` flag from `useConnectedInputs()` checks all required inputs are connected
2. **Error Display**: If invalid, sets `showError: true` in UI state to highlight missing connections
3. **Generation Creation**: Calls `createAndStartGenerationRunner()` with:
   - `operationNode`: The action node
   - `sourceNodes`: Connected input nodes
   - `connections`: Connection data for parameter mapping
4. **Execution**: The Giselle Engine handles the actual GitHub API calls

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/index.tsx:12-80](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/index.tsx:21-60]()

### Error Handling

Required inputs without connections are visually indicated:

- Red badge with "required" text next to parameter label
- Red alert icon with "Please choose a source" message when `showError` is true
- Input row styled with `TriangleAlert` icon and error text

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/ui/github-action-configured-view.tsx:199-261]()

## GitHub App Integration

### Authentication and Installation Flow

```mermaid
stateDiagram-v2
    [*] --> CheckIntegration
    CheckIntegration --> Unset: No GitHub integration
    CheckIntegration --> Unauthorized: Not signed in
    CheckIntegration --> NotInstalled: Signed in, app not installed
    CheckIntegration --> Installed: App installed
    
    Unauthorized --> OAuth: User clicks "Continue with GitHub"
    OAuth --> Installed: Auth complete
    
    NotInstalled --> InstallFlow: User clicks "Install"
    InstallFlow --> Installed: Installation complete
    
    Installed --> ActionConfig: Show action configuration UI
    ActionConfig --> [*]
```

### Integration States

The `useIntegration()` hook provides GitHub integration status:

| Status | Condition | UI Response |
|--------|-----------|-------------|
| `unset` | No GitHub integration configured | Display "unset" message |
| `unauthorized` | User not authenticated with GitHub | Show `Unauthorized` component with OAuth button |
| `not-installed` | Authenticated but app not installed | Show `InstallGitHubApplication` component |
| `invalid-credential` | Credentials expired or invalid | Display error message |
| `installed` | Fully configured | Show action configuration UI (`Installed` component) |
| `error` | Integration error occurred | Display error message |

### OAuth and Installation Popup

Both `Unauthorized` and `InstallGitHubApplication` components use a popup window pattern:

1. Opens GitHub OAuth/installation URL in centered popup window (800x800px)
2. Listens for `postMessage` event with `type: "github-app-installed"`
3. Triggers integration refresh via `refresh()` from `useIntegration()`
4. Popup cleanup on component unmount

The popup window is managed with:
```typescript
const width = 800;
const height = 800;
const left = window.screenX + (window.outerWidth - width) / 2;
const top = window.screenY + (window.outerHeight - height) / 2;

popupRef.current = window.open(
  authUrl,
  "Configure GitHub App",
  `width=${width},height=${height},top=${top},left=${left},popup=1`
);
```

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/github-action-properties-panel.tsx:181-248](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/github-action-properties-panel.tsx:250-322]()

## GitHub Tool Integration with Event Handlers

While action nodes are configured in the UI, their execution during GitHub trigger workflows is coordinated by event handlers. When a GitHub webhook event triggers a workflow, event handlers can create comments and reactions to provide feedback:

```mermaid
graph TD
    WebhookEvent["GitHub Webhook Event"]
    EventHandler["processEvent()<br/>event-handlers.ts"]
    
    subgraph "Event Handler Functions"
        IssueHandler["handleIssueOpened<br/>handleIssueClosed"]
        CommentHandler["handleIssueCommentCreated<br/>handlePRCommentCreated"]
        PRHandler["handlePullRequestOpened<br/>handlePullRequestClosed"]
    end
    
    subgraph "GitHub Tool Operations"
        AddReaction["addReaction()<br/>EYES emoji"]
        CreateComment["createIssueComment()<br/>createPRComment()<br/>createDiscussionComment()"]
        UpdateComment["updateIssueComment()<br/>updatePullRequestReviewComment()<br/>updateDiscussionComment()"]
    end
    
    WebhookEvent --> EventHandler
    EventHandler --> IssueHandler
    EventHandler --> CommentHandler
    EventHandler --> PRHandler
    
    IssueHandler --> AddReaction
    CommentHandler --> AddReaction
    PRHandler --> AddReaction
    
    EventHandler --> CreateComment
    CreateComment --> UpdateComment
```

### Progress Reporting

Event handlers create and update GitHub comments to report workflow execution progress:

1. **Initial Comment**: Created when Act starts, contains progress table
2. **Progress Updates**: Updated as sequences/steps complete with status changes
3. **Final Comment**: Shows completion status or error information

The progress table uses emoji indicators:
- ⚪ Pending
- ⏳ In progress  
- 🟢 Success
- ❌ Failed

Sources: [packages/giselle/src/engine/github/event-handlers.ts:462-476](), [packages/giselle/src/engine/github/event-handlers.ts:556-758]()

## Code Entity Map

### Key Components and Their Locations

| Component | File Path | Purpose |
|-----------|-----------|---------|
| `GitHubActionPropertiesPanel` | [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/github-action-properties-panel.tsx:104-179]() | Main action node configuration UI |
| `GitHubActionConfiguredView` | [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/ui/github-action-configured-view.tsx:96-276]() | Displays configured action with parameter inputs |
| `ActionNodePropertiesPanel` | [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/index.tsx:12-80]() | Orchestrates action execution |
| `SelectRepository` | [internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/select-repository.tsx:19-252]() | Repository selection component |
| `processEvent` | [packages/giselle/src/engine/github/event-handlers.ts:477-758]() | Handles GitHub webhook events and creates feedback comments |
| `githubActions` | Referenced from `@giselles-ai/action-registry` | Registry of available GitHub actions |
| `githubActionToInputFields` | Referenced from `@giselles-ai/action-registry` | Converts action definitions to input fields |

### Type Definitions

| Type | Location | Description |
|------|----------|-------------|
| `ActionNode` | `@giselles-ai/protocol` | Node type with `content.command.provider === "github"` |
| `GitHubActionConfiguredState` | `@giselles-ai/protocol` | Contains `commandId`, `repositoryNodeId`, `installationId` |
| `GitHubIntegrationInstallation` | `@giselles-ai/giselle` | Installation data with account info and repositories |
| `Input` | `@giselles-ai/protocol` | Input parameter with `id`, `accessor`, `label`, `isRequired` |
| `Output` | `@giselles-ai/protocol` | Output parameter with `id`, `label`, `accessor` |

Sources: [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/github-action-properties-panel.tsx:1-22](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/ui/github-action-configured-view.tsx:1-23]()

---

# Page: Workflow Designer UI

# Workflow Designer UI

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [internal-packages/ui/components/note.tsx](internal-packages/ui/components/note.tsx)
- [internal-packages/workflow-designer-ui/src/app/globals.css](internal-packages/workflow-designer-ui/src/app/globals.css)
- [internal-packages/workflow-designer-ui/src/editor/chat/floating-chat.tsx](internal-packages/workflow-designer-ui/src/editor/chat/floating-chat.tsx)
- [internal-packages/workflow-designer-ui/src/editor/chat/index.ts](internal-packages/workflow-designer-ui/src/editor/chat/index.ts)
- [internal-packages/workflow-designer-ui/src/editor/context-menu/index.tsx](internal-packages/workflow-designer-ui/src/editor/context-menu/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/context-menu/types.ts](internal-packages/workflow-designer-ui/src/editor/context-menu/types.ts)
- [internal-packages/workflow-designer-ui/src/editor/hooks/use-keyboard-shortcuts.ts](internal-packages/workflow-designer-ui/src/editor/hooks/use-keyboard-shortcuts.ts)
- [internal-packages/workflow-designer-ui/src/editor/node/index.ts](internal-packages/workflow-designer-ui/src/editor/node/index.ts)
- [internal-packages/workflow-designer-ui/src/editor/v2/components/floating-properties-panel.tsx](internal-packages/workflow-designer-ui/src/editor/v2/components/floating-properties-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx](internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx)
- [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-footer.tsx](internal-packages/workflow-designer-ui/src/editor/v2/components/v2-footer.tsx)
- [internal-packages/workflow-designer-ui/src/editor/v2/state.ts](internal-packages/workflow-designer-ui/src/editor/v2/state.ts)
- [internal-packages/workflow-designer-ui/src/editor/v2/v2-placeholder.tsx](internal-packages/workflow-designer-ui/src/editor/v2/v2-placeholder.tsx)

</details>



## Purpose and Scope

The Workflow Designer UI is the visual interface system for creating and editing AI workflows in the Giselle platform. It provides a node-based canvas for assembling workflows, configuring AI model parameters, managing connections between components, and executing generations. The system is built on ReactFlow for the graph visualization and uses Zustand for state management.

This page covers the overall architecture, component structure, state management, and user interaction patterns of the designer interface. For detailed information about specific subsystems:
- Editor architecture and state management details: [5.1](#5.1)
- Node rendering and visual components: [5.2](#5.2)
- Properties panels for node configuration: [5.3](#5.3)
- Toolbar and node creation: [5.4](#5.4)
- Generation execution and results: [5.5](#5.5)
- Model configuration interfaces: [5.6](#5.6)

For information about the underlying workflow execution engine, see [Core Engine and SDK](#2).

## System Architecture

The Workflow Designer UI is organized as a layered component hierarchy that integrates ReactFlow for graph visualization with custom UI components for workflow-specific functionality.

### High-Level Component Architecture

```mermaid
graph TB
    V2Placeholder["V2Placeholder<br/>(Root Component)"]
    RootProvider["RootProvider<br/>(ReactFlow Provider)"]
    V2Header["V2Header<br/>(Workflow Name & Actions)"]
    V2Container["V2Container<br/>(Main Layout)"]
    V2Footer["V2Footer<br/>(Panel Controls)"]
    V2NodeCanvas["V2NodeCanvas<br/>(ReactFlow Canvas)"]
    
    LeftPanel["LeftPanel<br/>(Run History/Secrets)"]
    FloatingPropertiesPanel["FloatingPropertiesPanel<br/>(Node Configuration)"]
    PropertiesPanel["PropertiesPanel<br/>(Config Forms)"]
    
    ReactFlow["ReactFlow<br/>(@xyflow/react)"]
    Toolbar["Toolbar<br/>(Node Creation)"]
    Background["Background<br/>(Grid Pattern)"]
    ContextMenu["ContextMenu<br/>(Right-Click Actions)"]
    
    WorkflowDesignerStore["useWorkflowDesignerStore<br/>(Zustand State)"]
    
    V2Placeholder --> RootProvider
    V2Placeholder --> V2Header
    V2Placeholder --> V2Container
    V2Placeholder --> V2Footer
    
    V2Container --> LeftPanel
    V2Container --> V2NodeCanvas
    V2Container --> FloatingPropertiesPanel
    
    FloatingPropertiesPanel --> PropertiesPanel
    
    V2NodeCanvas --> ReactFlow
    ReactFlow --> Toolbar
    ReactFlow --> Background
    ReactFlow --> ContextMenu
    
    V2NodeCanvas -.reads.-> WorkflowDesignerStore
    PropertiesPanel -.reads/writes.-> WorkflowDesignerStore
    LeftPanel -.reads.-> WorkflowDesignerStore
```

**Sources:** [internal-packages/workflow-designer-ui/src/editor/v2/v2-placeholder.tsx:1-107](), [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:1-491]()

### Component Hierarchy and Data Flow

```mermaid
graph TB
    subgraph "Application Layer"
        V2Placeholder["V2Placeholder"]
    end
    
    subgraph "Layout Components"
        V2Header["V2Header"]
        V2Container["V2Container"]
        V2Footer["V2Footer"]
        LeftPanel["LeftPanel<br/>(run-history | secret)"]
    end
    
    subgraph "Canvas Layer"
        V2NodeCanvas["V2NodeCanvas"]
        ReactFlowInstance["ReactFlow<br/>(nodes, edges, handlers)"]
        FloatingNodePreview["FloatingNodePreview<br/>(during node creation)"]
    end
    
    subgraph "Interactive Elements"
        Toolbar["Toolbar<br/>(bottom-center panel)"]
        FloatingPropertiesPanel["FloatingPropertiesPanel<br/>(right side)"]
        ContextMenu["ContextMenu<br/>(on right-click)"]
    end
    
    subgraph "State Management"
        ZustandStore["useWorkflowDesignerStore<br/>(workspace.nodes, connections, ui)"]
        workspaceActions["workspaceActions<br/>(setUiNodeState, addNode, etc.)"]
    end
    
    V2Placeholder --> V2Header
    V2Placeholder --> V2Container
    V2Placeholder --> V2Footer
    
    V2Container --> LeftPanel
    V2Container --> V2NodeCanvas
    V2Container --> FloatingPropertiesPanel
    
    V2NodeCanvas --> ReactFlowInstance
    ReactFlowInstance --> Toolbar
    ReactFlowInstance --> FloatingNodePreview
    ReactFlowInstance --> ContextMenu
    
    V2NodeCanvas -.subscribes.-> ZustandStore
    V2NodeCanvas -.dispatches.-> workspaceActions
    FloatingPropertiesPanel -.subscribes.-> ZustandStore
```

**Sources:** [internal-packages/workflow-designer-ui/src/editor/v2/v2-placeholder.tsx:66-106](), [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:49-491]()

## Core Components

### V2Placeholder - Root Component

`V2Placeholder` is the top-level component that orchestrates the entire designer interface. It manages layout state, tour visibility, and read-only banner display.

| Component | Purpose |
|-----------|---------|
| `RootProvider` | Wraps the editor with ReactFlow context |
| `V2Header` | Displays workflow name and actions |
| `V2Container` | Main canvas and panels layout |
| `V2Footer` | Panel toggles and documentation link |
| `WorkspaceTour` | Interactive tour for new users |
| `FloatingChat` | AI assistant chat interface |

**Key State:**
- `layoutState.leftPanel`: Controls which left panel is visible (`"run-history"` \| `"secret"` \| `null`)
- `isTourOpen`: Controls workspace tour visibility
- `isChatOpen`: Controls floating chat visibility
- `showReadOnlyBanner`: Controls read-only mode banner

**Sources:** [internal-packages/workflow-designer-ui/src/editor/v2/v2-placeholder.tsx:16-107]()

### V2Container - Main Layout

`V2Container` implements the resizable panel layout using `react-resizable-panels`. It contains:
- Left panel (conditional) for run history or secrets
- Main canvas area with `V2NodeCanvas`
- Floating properties panel (conditional based on node selection)

```mermaid
graph LR
    subgraph "Panel Layout"
        LeftPanel["LeftPanel<br/>(Panel order=1)"]
        ResizeHandle["PanelResizeHandle<br/>(12px width)"]
        MainPanel["Main Canvas<br/>(Panel order=2)"]
    end
    
    LeftPanel --> ResizeHandle
    ResizeHandle --> MainPanel
    
    MainPanel --> V2NodeCanvas
    MainPanel --> FloatingPropertiesPanel
```

**Conditional Rendering Logic:**
- Left panel renders only if `leftPanel !== null`
- Floating properties panel renders when exactly one node is selected
- Panel visibility affects `defaultWidth` and `minWidth` based on node type

**Sources:** [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:400-490]()

### V2NodeCanvas - ReactFlow Integration

`V2NodeCanvas` is the core canvas component that wraps ReactFlow and manages all graph interactions.

**Key Responsibilities:**
1. **Node Management**: Converts workspace nodes to ReactFlow nodes with UI state
2. **Edge Management**: Converts connections to ReactFlow edges with selection state
3. **Event Handling**: Processes node clicks, drags, connections, and deletions
4. **Keyboard Shortcuts**: Integrates with keyboard shortcut system
5. **Tool Integration**: Handles node creation from toolbar

```mermaid
graph TB
    subgraph "Data Transformation"
        WorkspaceNodes["workspace.nodes<br/>(protocol nodes)"]
        WorkspaceConnections["workspace.connections<br/>(protocol connections)"]
        NodeState["workspace.ui.nodeState<br/>(position, selected, measured)"]
        
        CacheNodesRef["cacheNodesRef<br/>(Map<NodeId, RFNode>)"]
        CacheEdgesRef["cacheEdgesRef<br/>(Map<string, Edge>)"]
        
        ReactFlowNodes["nodes: RFNode[]"]
        ReactFlowEdges["edges: Edge[]"]
    end
    
    WorkspaceNodes --> CacheNodesRef
    NodeState --> CacheNodesRef
    CacheNodesRef --> ReactFlowNodes
    
    WorkspaceConnections --> CacheEdgesRef
    CacheEdgesRef --> ReactFlowEdges
    
    ReactFlowNodes --> ReactFlowComponent["ReactFlow Component"]
    ReactFlowEdges --> ReactFlowComponent
```

**Node Caching Strategy:**
The component uses `useMemo` with ref-based caching to optimize ReactFlow performance by only recreating nodes/edges when their relevant properties change ([v2-container.tsx:89-151]()).

**Sources:** [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:53-398]()

## State Management

The Workflow Designer uses Zustand for centralized state management through `useWorkflowDesignerStore`. The store maintains workspace data and UI state.

### Store Structure

```mermaid
graph TB
    subgraph "useWorkflowDesignerStore"
        workspace["workspace"]
        
        subgraph "Workspace Data"
            nodes["nodes: Node[]"]
            connections["connections: Connection[]"]
        end
        
        subgraph "UI State"
            nodeState["ui.nodeState<br/>(Record<NodeId, NodeUiState>)"]
            viewport["ui.viewport<br/>(x, y, zoom)"]
            selectedConnectionIds["ui.selectedConnectionIds<br/>(string[])"]
            currentShortcutScope["ui.currentShortcutScope<br/>(canvas | properties-panel)"]
        end
        
        subgraph "Actions"
            setUiNodeState["setUiNodeState<br/>(position, selected, measured)"]
            setUiViewport["setUiViewport"]
            addNode["addNode"]
            addConnection["addConnection"]
            deleteConnection["deleteConnection"]
            updateNodeData["updateNodeData"]
        end
    end
    
    workspace --> nodes
    workspace --> connections
    workspace --> nodeState
    workspace --> viewport
    workspace --> selectedConnectionIds
    workspace --> currentShortcutScope
```

**State Access Patterns:**
- Components use `useShallow` selector to prevent unnecessary re-renders
- Actions are imported via `workspaceActions` from the store
- Node state is tracked per-node with unique `NodeId` keys

**Sources:** [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:54-76]()

### Node State Management

Each node has associated UI state stored in `workspace.ui.nodeState[nodeId]`:

| Property | Type | Purpose |
|----------|------|---------|
| `position` | `{ x: number, y: number }` | Canvas position |
| `selected` | `boolean` | Selection state |
| `measured` | `{ width?: number, height?: number }` | Rendered dimensions |

**Update Flow:**
```mermaid
sequenceDiagram
    participant User
    participant ReactFlow
    participant onNodesChange
    participant setUiNodeState
    participant ZustandStore
    
    User->>ReactFlow: Drag node
    ReactFlow->>onNodesChange: position change event
    onNodesChange->>setUiNodeState: Update position
    setUiNodeState->>ZustandStore: Persist state
    ZustandStore-->>ReactFlow: Trigger re-render
```

**Sources:** [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:233-295]()

## User Interactions

### Node Connection Flow

When users connect nodes by dragging from one handle to another:

```mermaid
sequenceDiagram
    participant User
    participant ReactFlow
    participant handleConnect
    participant isSupportedConnection
    participant Store
    
    User->>ReactFlow: Drag from output to input
    ReactFlow->>handleConnect: Connection object
    handleConnect->>handleConnect: Find output/input nodes
    handleConnect->>isSupportedConnection: Validate connection
    
    alt Connection invalid
        isSupportedConnection-->>handleConnect: Error message
        handleConnect->>User: Show toast error
    else Connection valid
        isSupportedConnection-->>handleConnect: Can connect
        alt Action node
            handleConnect->>Store: addConnection with existing input
        else Non-action node
            handleConnect->>Store: Create new input + addConnection
        end
        Store-->>ReactFlow: Update edges
    end
```

**Validation Logic:**
- Checks if nodes can be connected using `isSupportedConnection` from `@giselles-ai/giselle/react`
- Prevents duplicate connections to the same input/output
- For action nodes, uses existing input; for other nodes, dynamically creates new input

**Sources:** [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:153-204](), [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:206-221]()

### Node Creation with Toolbar

Node creation follows a state machine pattern managed by the toolbar:

```mermaid
stateDiagram-v2
    [*] --> Idle: reset()
    Idle --> ToolSelected: selectTool()
    ToolSelected --> NodeCreated: Click on canvas
    ToolSelected --> Idle: Escape key
    NodeCreated --> Idle: reset()
    
    note right of ToolSelected
        selectedTool.action === "addNode"
        FloatingNodePreview visible
        Cursor shows preview
    end note
```

**Implementation:**
1. User selects tool from `Toolbar` component
2. `useToolbar` hook manages `selectedTool` state
3. `FloatingNodePreview` follows cursor when tool is selected
4. Canvas click event calls `addNode` with cursor position
5. Tool resets to "move" mode

**Sources:** [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:317-344]()

### Keyboard Shortcuts

The editor provides comprehensive keyboard shortcuts managed by `useKeyboardShortcuts` hook:

| Shortcut | Action | Scope |
|----------|--------|-------|
| `t` | Select trigger tool | Canvas |
| `i` | Select source category | Canvas |
| `g` | Select language model tool | Canvas |
| `r` | Select retrieval category | Canvas |
| `d` | Select action tool | Canvas |
| `Escape` | Reset to move tool | Canvas |
| `Cmd/Ctrl + C` | Copy selected nodes | Canvas |
| `Cmd/Ctrl + V` | Paste nodes | Canvas |
| `Cmd/Ctrl + D` | Duplicate nodes | Canvas |
| `Cmd/Ctrl + Enter` | Generate (in properties panel) | Properties Panel |

**Shortcut Scope System:**
- `workspace.ui.currentShortcutScope` determines which shortcuts are active
- Canvas scope: Keyboard shortcuts for tools and node manipulation
- Properties panel scope: Generation shortcuts and form interactions
- Prevents conflicts between canvas and form interactions

**Sources:** [internal-packages/workflow-designer-ui/src/editor/hooks/use-keyboard-shortcuts.ts:1-139]()

### Context Menu

Right-clicking a node opens a context menu with actions:

```mermaid
graph LR
    RightClick["Right-click node"] --> handleNodeContextMenu
    handleNodeContextMenu --> setMenu["Set menu position"]
    setMenu --> ContextMenu
    
    ContextMenu --> Duplicate["Duplicate action"]
    ContextMenu --> Delete["Delete action"]
    
    Duplicate --> duplicateNode
    Delete --> deleteNode
```

**Position Calculation:**
The context menu calculates position to avoid going off-screen by checking if cursor is within 200px of canvas edges ([v2-container.tsx:345-362]()).

**Sources:** [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:345-362](), [internal-packages/workflow-designer-ui/src/editor/context-menu/index.tsx:1-59]()

## Floating Properties Panel

The `FloatingPropertiesPanel` provides a resizable, draggable panel for node configuration. It uses a custom implementation rather than a modal to maintain canvas context.

### Panel Architecture

```mermaid
graph TB
    subgraph "Floating Properties Panel"
        DialogRoot["Dialog.Root<br/>(modal=false)"]
        DialogPortal["Dialog.Portal<br/>(container=mainRef)"]
        DialogContent["Dialog.Content"]
        
        PanelContainer["Panel Container<br/>(absolute positioning)"]
        GlassSurface["GlassSurfaceLayers<br/>(backdrop blur)"]
        ResizeHandle["ResizeHandle<br/>(horizontal)"]
        ContentArea["Content Area<br/>(PropertiesPanel)"]
    end
    
    DialogRoot --> DialogPortal
    DialogPortal --> DialogContent
    DialogContent --> PanelContainer
    
    PanelContainer --> GlassSurface
    PanelContainer --> ResizeHandle
    PanelContainer --> ContentArea
```

**Resize Implementation:**
- Uses mouse event handlers with throttling for performance
- Maintains `intermediateWidthRef` for smooth resize
- Respects `minWidth` and `maxWidth` constraints
- Position-aware (can be right or left aligned)

**Conditional Behavior:**
| Node Type | `defaultWidth` | `minWidth` | `autoHeight` |
|-----------|----------------|------------|--------------|
| `textGeneration` | 400px | 400px | false |
| `file` | default | default | true |
| `text` | default | default | true |
| `vectorStore` | default | default | true |
| `webPage` | default | default | true |
| `manualTrigger` | default | default | true |

**Sources:** [internal-packages/workflow-designer-ui/src/editor/v2/components/floating-properties-panel.tsx:1-179](), [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:409-484]()

## Footer Panel Controls

`V2Footer` provides quick access to auxiliary panels and documentation:

```mermaid
graph LR
    subgraph "Left Section"
        RunHistory["Run History<br/>(HistoryIcon)"]
        Secrets["Secrets<br/>(FileKey2Icon)"]
    end
    
    subgraph "Right Section"
        Chat["Chat<br/>(MessageCircleIcon)"]
        Docs["Documentation<br/>(ExternalLinkIcon)"]
    end
    
    RunHistory -.toggles.-> LeftPanelRunHistory["leftPanel='run-history'"]
    Secrets -.toggles.-> LeftPanelSecret["leftPanel='secret'"]
    Chat -.toggles.-> ChatOpen["isChatOpen"]
    Docs -.links to.-> DocsUrl["docs.giselles.ai"]
```

**Active State Styling:**
- Active panels shown in `#6B8FF0` (blue)
- Inactive panels shown in `text-inverse` with hover effect
- Icons are 14x14px for consistency

**Sources:** [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-footer.tsx:1-118]()

## CSS and Styling

The designer uses a custom CSS theme system with CSS variables and Tailwind utilities.

### Canvas Styling

```css
/* ReactFlow pane with glass effect */
.giselle-workflow-editor-v3 .react-flow__pane {
  border: 0.5px solid rgba(235, 235, 235, 0.15);
  box-shadow: inset 0 0 40px rgba(200, 200, 200, 0.15);
}
```

**Cursor States:**
- Default: `cursor: default` for pane and nodes
- Node creation: `cursor: crosshair` when `data-floating-node="true"`
- Dragging: `cursor: default` (overrides ReactFlow's grab cursor)

**Sources:** [internal-packages/workflow-designer-ui/src/app/globals.css:1-240]()

### Custom Animations

The system defines several keyframe animations:

| Animation | Purpose | Usage |
|-----------|---------|-------|
| `pop-pop` | Node activity indicator | Loading states with 3 phases |
| `follow-through-overlap-spin` | Spinner animation | Progress indicators |
| `slideDown` / `slideUp` | Accordion transitions | Expandable sections |
| `shimmer` | Shimmer effect | Loading placeholders |
| `fadeInUp` | Entrance animation | Floating chat panel |

**Sources:** [internal-packages/workflow-designer-ui/src/app/globals.css:51-147](), [internal-packages/workflow-designer-ui/src/app/globals.css:168-223]()

## Integration with Core Systems

### Giselle Engine Integration

The Workflow Designer UI connects to the Giselle Engine through several integration points:

```mermaid
graph TB
    subgraph "UI Layer"
        PropertiesPanel["PropertiesPanel"]
        V2NodeCanvas["V2NodeCanvas"]
        useWorkflowDesigner["useWorkflowDesigner hook"]
    end
    
    subgraph "State Layer"
        WorkflowDesignerStore["useWorkflowDesignerStore"]
    end
    
    subgraph "Engine Layer"
        GiselleEngine["@giselles-ai/giselle"]
        createAndStartGenerationRunner["createAndStartGenerationRunner"]
        startAct["startAct"]
        deleteNode["deleteNode"]
    end
    
    PropertiesPanel --> createAndStartGenerationRunner
    V2NodeCanvas --> useWorkflowDesigner
    useWorkflowDesigner --> deleteNode
    
    WorkflowDesignerStore -.provides workspace data.-> PropertiesPanel
    WorkflowDesignerStore -.provides workspace data.-> V2NodeCanvas
```

**Key Integration Methods:**
- `useWorkflowDesigner`: Hook providing `deleteNode`, `data` access
- `isSupportedConnection`: Validates node connections based on protocol rules
- `createAndStartGenerationRunner`: Initiates generation execution from properties panel

**Sources:** [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:24-29](), [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:77]()

### ReactFlow Node and Edge Types

The designer registers custom node and edge types with ReactFlow:

```javascript
// From node/index.ts and connector/index.ts
const nodeTypes = {
  giselle: NodeComponent  // Custom node renderer
};

const edgeTypes = {
  giselleConnector: ConnectorComponent  // Custom edge renderer
};
```

**Node Data Structure:**
```
RFNode {
  id: NodeId
  type: "giselle"
  position: { x, y }
  selected: boolean
  measured: { width?, height? }
  data: {}  // Empty, actual data in workspace store
}
```

**Edge Data Structure:**
```
Edge {
  id: string (connection.id)
  source: NodeId
  sourceHandle: OutputId
  target: NodeId
  targetHandle: InputId
  type: "giselleConnector"
  selected: boolean
  data: { connection }
}
```

**Sources:** [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:34-36](), [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:90-151]()

## Read-Only Mode

The designer supports a read-only mode for viewers and guests:

```mermaid
graph TB
    V2Placeholder --> CheckReadOnly{isReadOnly?}
    CheckReadOnly -->|Yes| ShowBanner["ReadOnlyBanner<br/>(dismissible)"]
    CheckReadOnly -->|No| NoBanner["No banner"]
    
    ShowBanner --> RoleCheck{userRole?}
    RoleCheck -->|viewer| ViewerMessage["'You are viewing this workflow'"]
    RoleCheck -->|guest| GuestMessage["'You are a guest'"]
    RoleCheck -->|editor/owner| OwnerMessage["'Different message'"]
```

**Access Control:**
The `V2Placeholder` component accepts `isReadOnly` and `userRole` props to control UI behavior and messaging. Note: Actual enforcement of read-only restrictions happens at the API/action layer, not just the UI.

**Sources:** [internal-packages/workflow-designer-ui/src/editor/v2/v2-placeholder.tsx:16-75]()

## Summary

The Workflow Designer UI is a sophisticated React-based visual editor built on ReactFlow. Its architecture emphasizes:

1. **Separation of Concerns**: Layout (V2Container), canvas (V2NodeCanvas), and configuration (PropertiesPanel) are distinct layers
2. **Performance**: Node/edge caching and shallow selectors minimize re-renders
3. **State Management**: Centralized Zustand store with action creators for predictable updates
4. **User Experience**: Keyboard shortcuts, context menus, floating panels, and visual feedback
5. **Extensibility**: Plugin-based node types and edge types through ReactFlow registries

The system integrates tightly with the Giselle Engine ([2](#2)) for workflow execution while maintaining a clean separation between UI concerns and business logic.

---

# Page: Editor Architecture and State Management

# Editor Architecture and State Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [internal-packages/ui/components/note.tsx](internal-packages/ui/components/note.tsx)
- [internal-packages/workflow-designer-ui/src/app/globals.css](internal-packages/workflow-designer-ui/src/app/globals.css)
- [internal-packages/workflow-designer-ui/src/editor/chat/floating-chat.tsx](internal-packages/workflow-designer-ui/src/editor/chat/floating-chat.tsx)
- [internal-packages/workflow-designer-ui/src/editor/chat/index.ts](internal-packages/workflow-designer-ui/src/editor/chat/index.ts)
- [internal-packages/workflow-designer-ui/src/editor/context-menu/index.tsx](internal-packages/workflow-designer-ui/src/editor/context-menu/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/context-menu/types.ts](internal-packages/workflow-designer-ui/src/editor/context-menu/types.ts)
- [internal-packages/workflow-designer-ui/src/editor/hooks/use-keyboard-shortcuts.ts](internal-packages/workflow-designer-ui/src/editor/hooks/use-keyboard-shortcuts.ts)
- [internal-packages/workflow-designer-ui/src/editor/node/index.ts](internal-packages/workflow-designer-ui/src/editor/node/index.ts)
- [internal-packages/workflow-designer-ui/src/editor/v2/components/floating-properties-panel.tsx](internal-packages/workflow-designer-ui/src/editor/v2/components/floating-properties-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx](internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx)
- [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-footer.tsx](internal-packages/workflow-designer-ui/src/editor/v2/components/v2-footer.tsx)
- [internal-packages/workflow-designer-ui/src/editor/v2/state.ts](internal-packages/workflow-designer-ui/src/editor/v2/state.ts)
- [internal-packages/workflow-designer-ui/src/editor/v2/v2-placeholder.tsx](internal-packages/workflow-designer-ui/src/editor/v2/v2-placeholder.tsx)

</details>



## Purpose and Scope

This document describes the architecture and state management of the Workflow Designer V2 editor, which provides a visual interface for creating and editing AI workflows. The editor is built on top of ReactFlow and uses Zustand for state management. This page covers the overall editor structure, state management patterns, component hierarchy, event handling, and keyboard shortcuts. For information about individual node rendering and visual styling, see [Node Rendering and Visual System](#5.2). For node configuration interfaces, see [Properties Panels and Node Configuration](#5.3).

## Architecture Overview

The V2 editor architecture consists of several integrated layers that work together to provide a visual workflow editing experience:

**Editor Architecture Layers**

```mermaid
graph TB
    subgraph "Presentation Layer"
        V2Placeholder["V2Placeholder<br/>Main Container"]
        V2Container["V2Container<br/>Layout Manager"]
        V2Header["V2Header<br/>Toolbar"]
        V2Footer["V2Footer<br/>Status Bar"]
    end
    
    subgraph "Canvas Layer"
        V2NodeCanvas["V2NodeCanvas<br/>ReactFlow Integration"]
        ReactFlow["ReactFlow<br/>Node Graph Library"]
        FloatingNodePreview["FloatingNodePreview<br/>Node Creation Preview"]
        Toolbar["Toolbar<br/>Node Selection"]
    end
    
    subgraph "Interaction Layer"
        ContextMenu["ContextMenu<br/>Node Actions"]
        FloatingPropertiesPanel["FloatingPropertiesPanel<br/>Node Configuration"]
        PropertiesPanel["PropertiesPanel<br/>Content"]
        LeftPanel["LeftPanel<br/>Run History/Secrets"]
    end
    
    subgraph "State Management"
        useWorkflowDesignerStore["useWorkflowDesignerStore<br/>Zustand Store"]
        workspaceActions["workspaceActions<br/>Action Creators"]
        ReactFlowState["ReactFlow Internal State<br/>Viewport, Selection"]
    end
    
    subgraph "Event System"
        useKeyboardShortcuts["useKeyboardShortcuts<br/>Keyboard Handler"]
        useToolbar["useToolbar<br/>Tool State"]
        useNodeManipulation["useNodeManipulation<br/>Node Operations"]
    end
    
    V2Placeholder --> V2Container
    V2Placeholder --> V2Header
    V2Placeholder --> V2Footer
    V2Container --> V2NodeCanvas
    V2Container --> FloatingPropertiesPanel
    
    V2NodeCanvas --> ReactFlow
    V2NodeCanvas --> FloatingNodePreview
    V2NodeCanvas --> Toolbar
    V2NodeCanvas --> ContextMenu
    
    V2NodeCanvas --> useWorkflowDesignerStore
    V2NodeCanvas --> workspaceActions
    V2NodeCanvas --> ReactFlowState
    
    V2NodeCanvas --> useKeyboardShortcuts
    V2NodeCanvas --> useToolbar
    
    FloatingPropertiesPanel --> PropertiesPanel
    V2Container --> LeftPanel
    
    useKeyboardShortcuts --> useNodeManipulation
    useKeyboardShortcuts --> useToolbar
```

Sources: [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:1-491](), [internal-packages/workflow-designer-ui/src/editor/v2/v2-placeholder.tsx:1-107](), [internal-packages/workflow-designer-ui/src/editor/hooks/use-keyboard-shortcuts.ts:1-139]()

## State Management Architecture

### Zustand Store Structure

The editor uses a centralized Zustand store accessed through `useWorkflowDesignerStore`. The store maintains workspace state including nodes, connections, and UI state:

**Store State Schema**

```mermaid
graph TB
    subgraph "workspace"
        nodes["nodes: Node[]<br/>Workflow Nodes"]
        connections["connections: Connection[]<br/>Node Connections"]
        ui["ui: UIState<br/>Editor UI State"]
    end
    
    subgraph "ui: UIState"
        nodeState["nodeState: Record<NodeId, NodeUIState><br/>Per-Node UI State"]
        viewport["viewport: Viewport<br/>Canvas Position/Zoom"]
        selectedConnectionIds["selectedConnectionIds: string[]<br/>Selected Edges"]
        currentShortcutScope["currentShortcutScope: 'canvas' | 'properties-panel'<br/>Focus Scope"]
    end
    
    subgraph "NodeUIState"
        position["position: {x, y}<br/>Node Position"]
        selected["selected: boolean<br/>Selection State"]
        measured["measured: {width?, height?}<br/>Node Dimensions"]
    end
    
    workspace --> nodes
    workspace --> connections
    workspace --> ui
    
    ui --> nodeState
    ui --> viewport
    ui --> selectedConnectionIds
    ui --> currentShortcutScope
    
    nodeState --> position
    nodeState --> selected
    nodeState --> measured
```

Sources: [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:54-62]()

### ReactFlow State Integration

The editor transforms Zustand state into ReactFlow's node and edge formats using memoized transformations with caching for performance:

**Node Transformation**

The `V2NodeCanvas` component converts workspace nodes to ReactFlow nodes [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:89-125]():

- Retrieves nodes and UI state from Zustand store
- Uses `cacheNodesRef` to prevent unnecessary re-renders by comparing previous state
- Creates `RFNode` objects with position, selection state, and measured dimensions
- Triggers `updateNodeInternals` when node structure changes

**Edge Transformation**

Connections are transformed to ReactFlow edges [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:127-151]():

- Maps connection objects to edge format with source/target handles
- Uses `cacheEdgesRef` for caching and comparison
- Includes selection state and connection metadata

### State Synchronization

State flows bidirectionally between Zustand and ReactFlow:

**Zustand → ReactFlow**

```mermaid
sequenceDiagram
    participant Store as useWorkflowDesignerStore
    participant Component as V2NodeCanvas
    participant Cache as cacheNodesRef/cacheEdgesRef
    participant RF as ReactFlow
    
    Store->>Component: "nodes, connections, nodeState"
    Component->>Cache: "Check cached values"
    alt "State changed"
        Component->>Component: "Transform to RFNode/Edge"
        Component->>RF: "Update nodes/edges"
    else "State unchanged"
        Component->>RF: "Reuse cached nodes/edges"
    end
```

**ReactFlow → Zustand**

```mermaid
sequenceDiagram
    participant RF as ReactFlow
    participant Component as V2NodeCanvas
    participant Actions as workspaceActions
    participant Store as useWorkflowDesignerStore
    
    RF->>Component: "onNodesChange/onEdgesChange"
    Component->>Component: "Process change event"
    Component->>Actions: "setUiNodeState/deleteConnection"
    Actions->>Store: "Update store state"
```

Sources: [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:233-295](), [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:297-316]()

## Component Hierarchy

The V2 editor is organized into a hierarchical component structure:

**Component Tree**

```mermaid
graph TB
    V2Placeholder["V2Placeholder<br/>internal-packages/workflow-designer-ui/src/editor/v2/v2-placeholder.tsx"]
    RootProvider["RootProvider<br/>Context Provider"]
    V2Header["V2Header<br/>Header Bar"]
    V2Container["V2Container<br/>Main Content Area"]
    V2Footer["V2Footer<br/>Footer Controls"]
    
    PanelGroup["PanelGroup<br/>Resizable Layout"]
    LeftPanel["LeftPanel<br/>Run History/Secrets"]
    V2NodeCanvas["V2NodeCanvas<br/>Canvas Content"]
    FloatingPropertiesPanel["FloatingPropertiesPanel<br/>Properties Panel"]
    
    ReactFlow_Component["ReactFlow<br/>@xyflow/react"]
    Background["Background<br/>Grid Pattern"]
    FloatingNodePreview["FloatingNodePreview<br/>Node Preview"]
    Toolbar_Panel["Toolbar<br/>XYFlowPanel"]
    ContextMenu_Component["ContextMenu<br/>Context Menu"]
    
    PropertiesPanel_Content["PropertiesPanel<br/>Panel Content"]
    
    V2Placeholder --> RootProvider
    V2Placeholder --> V2Header
    V2Placeholder --> V2Container
    V2Placeholder --> V2Footer
    V2Placeholder --> WorkspaceTour
    V2Placeholder --> FloatingChat
    
    V2Container --> PanelGroup
    PanelGroup --> LeftPanel
    PanelGroup --> V2NodeCanvas
    V2Container --> FloatingPropertiesPanel
    
    V2NodeCanvas --> ReactFlow_Component
    ReactFlow_Component --> Background
    ReactFlow_Component --> FloatingNodePreview
    ReactFlow_Component --> Toolbar_Panel
    ReactFlow_Component --> ContextMenu_Component
    
    FloatingPropertiesPanel --> PropertiesPanel_Content
```

Sources: [internal-packages/workflow-designer-ui/src/editor/v2/v2-placeholder.tsx:16-106](), [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:400-490]()

### V2Placeholder

The root component that manages top-level layout state [internal-packages/workflow-designer-ui/src/editor/v2/v2-placeholder.tsx:16-106]():

**State Management:**
- `layoutState: V2LayoutState` - Controls left panel visibility
- `isTourOpen: boolean` - Workspace tour state
- `isChatOpen: boolean` - Chat panel state
- `showReadOnlyBanner: boolean` - Read-only mode indicator

**Responsibilities:**
- Feature flag integration for layout variants
- Read-only mode handling
- Left panel toggle coordination
- Chat panel coordination

### V2Container

The main content container that orchestrates the canvas and panels [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:400-490]():

**Layout Structure:**
- Uses `react-resizable-panels` for resizable layout
- Left panel (optional): Run History or Secrets
- Main panel: Node canvas
- Floating properties panel (right): Node configuration

**Panel Selection Logic:**
```typescript
const isPropertiesPanelOpen = selectedNodes.length === 1;
const isTextGenerationPanel = isPropertiesPanelOpen && 
  selectedNodes[0]?.content.type === "textGeneration";
```

The properties panel automatically opens when a single node is selected and adapts its size based on node type.

Sources: [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:400-490]()

### V2NodeCanvas

The core canvas component that integrates ReactFlow [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:53-398]():

**Key Features:**
- Node and edge transformation from Zustand state
- Connection validation and creation
- Node selection and manipulation
- Context menu handling
- Tool-based node creation
- Keyboard event handling

**ReactFlow Configuration:**
```typescript
<ReactFlow
  className="giselle-workflow-editor-v3"
  colorMode="dark"
  nodes={nodes}
  edges={edges}
  nodeTypes={nodeTypes}
  edgeTypes={edgeTypes}
  panOnScroll={true}
  zoomOnScroll={false}
  zoomOnPinch={true}
  onConnect={handleConnect}
  isValidConnection={isValidConnection}
  onNodesChange={handleNodesChange}
  onEdgesChange={handleEdgesChange}
  onNodeClick={handleNodeClick}
  onPaneClick={handlePanelClick}
  onKeyDown={handleKeyDown}
  onNodeContextMenu={handleNodeContextMenu}
/>
```

Sources: [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:364-397]()

## Layout State Management

The editor uses a simple state type to manage layout configuration:

**Layout State Type** [internal-packages/workflow-designer-ui/src/editor/v2/state.ts:1-5]():

```typescript
export type LeftPanelValue = "run-history" | "secret";
export interface V2LayoutState {
  leftPanel: LeftPanelValue | null;
}
```

**Layout State Flow:**

```mermaid
sequenceDiagram
    participant Footer as V2Footer
    participant Placeholder as V2Placeholder
    participant Container as V2Container
    participant LeftPanel as LeftPanel
    
    Footer->>Placeholder: "onLeftPanelValueChange('run-history')"
    Placeholder->>Placeholder: "Toggle leftPanel state"
    alt "Panel opened"
        Placeholder->>Container: "leftPanel='run-history'"
        Container->>LeftPanel: "Render RunHistoryTable"
    else "Panel closed"
        Placeholder->>Container: "leftPanel=null"
        Container->>Container: "Hide left panel"
    end
```

The footer provides toggle buttons that cycle through panel states:
- Clicking an active panel closes it
- Clicking an inactive panel opens it and closes any other open panel

Sources: [internal-packages/workflow-designer-ui/src/editor/v2/state.ts:1-5](), [internal-packages/workflow-designer-ui/src/editor/v2/v2-placeholder.tsx:39-59](), [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-footer.tsx:1-118]()

## Floating Properties Panel

The `FloatingPropertiesPanel` is a resizable, non-modal dialog that displays node configuration:

**Panel Configuration** [internal-packages/workflow-designer-ui/src/editor/v2/components/floating-properties-panel.tsx:9-35]():

| Property | Type | Description |
|----------|------|-------------|
| `isOpen` | boolean | Panel visibility state |
| `defaultWidth` | number | Initial width (default: 400px) |
| `minWidth` | number | Minimum width (default: 400px) |
| `maxWidth` | number | Maximum width (default: 1200px) |
| `autoHeight` | boolean | Auto-height mode for simple panels |
| `container` | Element | Portal container for positioning |

**Resize Implementation:**

The panel uses a custom resize handle with throttled mouse move events [internal-packages/workflow-designer-ui/src/editor/v2/components/floating-properties-panel.tsx:66-101]():

1. Mouse down on resize handle captures start position
2. Mouse move calculates delta and updates width
3. Throttling (~60fps) prevents excessive re-renders
4. Mouse up cleanup removes event listeners

**Visual Layers:**

```mermaid
graph TB
    Panel["FloatingPropertiesPanel Container<br/>absolute positioning"]
    BaseFill["Base Fill Layer<br/>Semi-transparent background"]
    GlassSurface["GlassSurfaceLayers<br/>Blur and border effects"]
    ResizeHandle["ResizeHandle<br/>Left/right edge"]
    Content["Content Area<br/>PropertiesPanel"]
    
    Panel --> BaseFill
    Panel --> GlassSurface
    Panel --> ResizeHandle
    Panel --> Content
```

Sources: [internal-packages/workflow-designer-ui/src/editor/v2/components/floating-properties-panel.tsx:1-179]()

## Event Handling

### Connection Management

The editor validates and creates connections between nodes [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:153-204]():

**Connection Validation Flow:**

```mermaid
sequenceDiagram
    participant User
    participant RF as ReactFlow
    participant isValid as isValidConnection
    participant handleConnect as handleConnect
    participant Store as Zustand Store
    
    User->>RF: "Drag connection"
    RF->>isValid: "Validate connection"
    alt "Invalid"
        isValid-->>RF: "false"
        RF->>User: "Visual feedback (invalid)"
    else "Valid"
        isValid-->>RF: "true"
        RF->>User: "Visual feedback (valid)"
        User->>RF: "Drop connection"
        RF->>handleConnect: "connection object"
        handleConnect->>handleConnect: "Find nodes, check support"
        alt "Action Node"
            handleConnect->>Store: "addConnection with existing input"
        else "Non-Action Node"
            handleConnect->>Store: "updateNodeData with new input"
            handleConnect->>Store: "addConnection with new input"
        end
    end
```

**Validation Rules:**
- Source and target must have valid handles
- Self-connections are not allowed
- Duplicate connections are prevented
- Node type compatibility is checked via `isSupportedConnection`

Sources: [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:153-221]()

### Node Manipulation

Node changes flow through the `handleNodesChange` callback [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:233-295]():

**Change Types:**

| Type | Action | State Update |
|------|--------|--------------|
| `position` | Node dragged | Update `nodeState[id].position` |
| `dimensions` | Node measured | Update `nodeState[id].measured` |
| `select` | Selection changed | Update `nodeState[id].selected` |
| `remove` | Node deleted | Delete connections, clean up inputs, call `deleteNode` |

**Node Removal Flow:**

```mermaid
sequenceDiagram
    participant RF as ReactFlow
    participant Handler as handleNodesChange
    participant Store as Zustand Store
    participant Designer as useWorkflowDesigner
    
    RF->>Handler: "remove change"
    loop "For each connection"
        Handler->>Handler: "Check if outputNode matches"
        Handler->>Store: "deleteConnection(id)"
        Handler->>Handler: "Find connected node"
        alt "TextGeneration node"
            Handler->>Store: "updateNodeData (remove input)"
        end
    end
    Handler->>Designer: "deleteNode(id)"
```

Sources: [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:233-295]()

### Edge Selection

Edge selection is managed through `handleEdgesChange` [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:297-316]():

```typescript
const handleEdgesChange: OnEdgesChange = useCallback(
  (changes) => {
    for (const change of changes) {
      switch (change.type) {
        case "select":
          if (change.selected) {
            selectConnection(change.id);
          } else {
            deselectConnection(change.id);
          }
          break;
        case "remove":
          deleteConnection(change.id);
          break;
      }
    }
  },
  [selectConnection, deleteConnection, deselectConnection],
);
```

Sources: [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:297-316]()

### Canvas Interaction

The canvas click handler manages multiple interaction modes [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:317-344]():

**Canvas Click Behavior:**

```mermaid
flowchart TD
    Click["User clicks canvas"]
    CloseMenu["Close context menu"]
    DeselectAll["Deselect all nodes"]
    CheckTool{"selectedTool.action<br/>== 'addNode'?"}
    AddNode["Calculate position<br/>addNode(tool.node, position)"]
    ResetTool["reset() toolbar state"]
    SetFocus["setCurrentShortcutScope('canvas')"]
    
    Click --> CloseMenu
    CloseMenu --> DeselectAll
    DeselectAll --> CheckTool
    CheckTool -->|Yes| AddNode
    CheckTool -->|No| ResetTool
    AddNode --> ResetTool
    ResetTool --> SetFocus
```

When a tool is active (e.g., user clicked "Text Generation" in toolbar), clicking the canvas places a new node at that position.

Sources: [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:317-344]()

### Context Menu

Right-click on nodes shows a context menu [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:345-362](), [internal-packages/workflow-designer-ui/src/editor/context-menu/index.tsx:1-59]():

**Menu Position Calculation:**

The context menu position is calculated to keep it within viewport bounds:

```typescript
const handleNodeContextMenu: NodeMouseHandler = useCallback((event, node) => {
  event.preventDefault();
  const pane = reactFlowRef.current?.getBoundingClientRect();
  if (!pane) return;
  setMenu({
    id: node.id,
    top: event.clientY < pane.height - 200 ? event.clientY : undefined,
    left: event.clientX < pane.width - 200 ? event.clientX : undefined,
    right: event.clientX >= pane.width - 200 ? pane.width - event.clientX : undefined,
    bottom: event.clientY >= pane.height - 200 ? pane.height - event.clientY : undefined,
  });
}, []);
```

**Menu Actions:**
- Duplicate: Uses `useNodeManipulation().duplicate()`
- Delete: Uses `useWorkflowDesigner().deleteNode()`

Sources: [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:345-362](), [internal-packages/workflow-designer-ui/src/editor/context-menu/index.tsx:9-58]()

## Keyboard Shortcuts System

The editor implements a comprehensive keyboard shortcut system with focus scope awareness.

### Shortcut Architecture

**Keyboard Shortcut Flow:**

```mermaid
graph TB
    subgraph "Event Sources"
        ReactFlow_KB["ReactFlow onKeyDown"]
        useKeyPress_Hook["useKeyPress hooks<br/>@xyflow/react"]
    end
    
    subgraph "useKeyboardShortcuts Hook"
        ScopeCheck["Check currentShortcutScope<br/>canvas vs properties-panel"]
        ToolActions["useToolAction hooks<br/>Tool selection"]
        CopyPaste["Copy/Paste/Duplicate<br/>useNodeManipulation"]
        GenerateAction["Generate shortcut<br/>onGenerate callback"]
        BrowserPrevent["Browser shortcut prevention"]
    end
    
    subgraph "Focus Scopes"
        CanvasScope["'canvas' scope<br/>Canvas shortcuts active"]
        PropertiesScope["'properties-panel' scope<br/>Panel shortcuts active"]
    end
    
    subgraph "Actions"
        Toolbar_Actions["Toolbar actions<br/>setSelectedTool"]
        Node_Actions["Node actions<br/>copy, paste, duplicate"]
        Generate_Action["Generate action<br/>Execute generation"]
    end
    
    ReactFlow_KB --> BrowserPrevent
    useKeyPress_Hook --> ScopeCheck
    
    ScopeCheck --> ToolActions
    ScopeCheck --> CopyPaste
    ScopeCheck --> GenerateAction
    
    ToolActions --> CanvasScope
    CopyPaste --> CanvasScope
    GenerateAction --> PropertiesScope
    
    CanvasScope --> Toolbar_Actions
    CanvasScope --> Node_Actions
    PropertiesScope --> Generate_Action
```

Sources: [internal-packages/workflow-designer-ui/src/editor/hooks/use-keyboard-shortcuts.ts:1-139]()

### Shortcut Definitions

**Canvas Shortcuts** (active when `currentShortcutScope === "canvas"`):

| Key | Action | Implementation |
|-----|--------|----------------|
| `t` | Select Trigger tool | `selectTriggerTool()` |
| `i` | Select Source/Input tool | `selectSourceCategoryTool()` |
| `g` | Select Language Model tool | `selectLanguageModelTool()` |
| `r` | Select Retrieval tool | `selectRetrievalCategoryTool()` |
| `d` | Select Action tool | `selectActionTool()` |
| `Escape` | Reset to Move tool | `moveTool()` |
| `Cmd/Ctrl+C` | Copy selected nodes | `handleCopy()` |
| `Cmd/Ctrl+V` | Paste copied nodes | `handlePaste()` |
| `Cmd/Ctrl+D` | Duplicate selected nodes | `handleDuplicate()` |

**Properties Panel Shortcuts** (active when `currentShortcutScope === "properties-panel"`):

| Key | Action | Implementation |
|-----|--------|----------------|
| `Cmd/Ctrl+Enter` | Execute generation | `onGenerate()` |

Sources: [internal-packages/workflow-designer-ui/src/editor/hooks/use-keyboard-shortcuts.ts:72-112]()

### useKeyAction Hook

Custom hook for handling keyboard shortcuts with repeat prevention [internal-packages/workflow-designer-ui/src/editor/hooks/use-keyboard-shortcuts.ts:26-53]():

```typescript
function useKeyAction(
  key: string | string[],
  action: () => void,
  enabled: boolean = false,
  options: {
    inputShortcutPolicy?: InputShortcutPolicy;
    preventDefault?: boolean;
  } = { inputShortcutPolicy: "ignore" },
)
```

**Input Shortcut Policies:**
- `"ignore"`: Shortcuts disabled in input fields (default)
- `"modifierOnly"`: Shortcuts work in inputs only with modifier keys
- `"always"`: Shortcuts always active

**Repeat Prevention:**

Uses a ref to track key press state and only triggers on initial press:

```typescript
const wasPressed = useRef(false);
useEffect(() => {
  if (isPressed && !wasPressed.current && enabled) {
    action();
  }
  wasPressed.current = isPressed;
}, [isPressed, enabled, action]);
```

Sources: [internal-packages/workflow-designer-ui/src/editor/hooks/use-keyboard-shortcuts.ts:26-53]()

### Browser Shortcut Prevention

The system prevents specific browser shortcuts when canvas is focused [internal-packages/workflow-designer-ui/src/editor/hooks/use-keyboard-shortcuts.ts:18-24](), [internal-packages/workflow-designer-ui/src/editor/hooks/use-keyboard-shortcuts.ts:114-133]():

```typescript
const BROWSER_SHORTCUTS_TO_PREVENT = [
  { key: "d", modifiers: ["meta", "ctrl"] }, // Bookmark
];

const handleKeyDown = useCallback((event: React.KeyboardEvent) => {
  if (!isCanvasFocused) return;
  
  const shouldPrevent = BROWSER_SHORTCUTS_TO_PREVENT.some((shortcut) => {
    const keyMatches = event.key.toLowerCase() === shortcut.key;
    const modifierMatches = shortcut.modifiers.some((mod) => {
      if (mod === "meta") return event.metaKey;
      if (mod === "ctrl") return event.ctrlKey;
      return false;
    });
    return keyMatches && modifierMatches;
  });
  
  if (shouldPrevent) {
    event.preventDefault();
  }
}, [isCanvasFocused]);
```

This is necessary because `Cmd/Ctrl+D` is used for node duplication but would normally trigger browser bookmark functionality.

Sources: [internal-packages/workflow-designer-ui/src/editor/hooks/use-keyboard-shortcuts.ts:18-24](), [internal-packages/workflow-designer-ui/src/editor/hooks/use-keyboard-shortcuts.ts:114-133]()

## Focus and Scope Management

The editor uses a `currentShortcutScope` state to manage which shortcuts are active:

**Focus Scope Values:**
- `"canvas"`: Canvas-related shortcuts (tool selection, copy/paste)
- `"properties-panel"`: Panel-related shortcuts (generate)

**Scope Transitions:**

```mermaid
stateDiagram-v2
    [*] --> canvas: "Initial state"
    
    canvas --> canvas: "Click canvas"
    canvas --> canvas: "Click node"
    canvas --> properties_panel: "Focus input in panel"
    
    properties_panel --> canvas: "Click canvas"
    properties_panel --> canvas: "Click node"
    properties_panel --> canvas: "Escape key"
```

**Scope Setting Locations:**

| Location | Code | New Scope |
|----------|------|-----------|
| Node click | [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:228]() | `"canvas"` |
| Canvas click | [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:332]() | `"canvas"` |

This ensures that keyboard shortcuts don't interfere with text input in the properties panel while still allowing quick access to canvas operations.

Sources: [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:69](), [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:228](), [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:332](), [internal-packages/workflow-designer-ui/src/editor/hooks/use-keyboard-shortcuts.ts:83-86]()

## Complete Data Flow

**End-to-End Editor Data Flow:**

```mermaid
sequenceDiagram
    participant User
    participant V2Container as V2Container
    participant V2NodeCanvas as V2NodeCanvas
    participant Store as useWorkflowDesignerStore
    participant Actions as workspaceActions
    participant RF as ReactFlow
    participant Cache as Cache Refs
    
    Note over User,RF: "Initialization"
    V2NodeCanvas->>Store: "useShallow(s => s.workspace)"
    Store-->>V2NodeCanvas: "nodes, connections, nodeState"
    V2NodeCanvas->>Cache: "Check cache"
    V2NodeCanvas->>V2NodeCanvas: "Transform to RFNode/Edge"
    V2NodeCanvas->>RF: "render(nodes, edges)"
    
    Note over User,RF: "User Interaction"
    User->>RF: "Drag node"
    RF->>V2NodeCanvas: "onNodesChange(position)"
    V2NodeCanvas->>Actions: "setUiNodeState(id, position)"
    Actions->>Store: "Update nodeState[id].position"
    Store->>V2NodeCanvas: "Trigger re-render"
    V2NodeCanvas->>Cache: "Compare with cache"
    V2NodeCanvas->>V2NodeCanvas: "Create new RFNode"
    V2NodeCanvas->>RF: "Update nodes"
    RF->>User: "Visual feedback"
    
    Note over User,RF: "Tool-based Node Creation"
    User->>V2Container: "Click toolbar (select tool)"
    V2Container->>V2Container: "useToolbar.setSelectedTool"
    User->>RF: "Click canvas"
    RF->>V2NodeCanvas: "onPaneClick(event)"
    V2NodeCanvas->>V2NodeCanvas: "screenToFlowPosition"
    V2NodeCanvas->>Actions: "addNode(node, position)"
    Actions->>Store: "Add to workspace.nodes"
    Store->>V2NodeCanvas: "Trigger re-render"
    V2NodeCanvas->>RF: "Update nodes"
    
    Note over User,RF: "Connection Creation"
    User->>RF: "Drag from handle"
    RF->>V2NodeCanvas: "isValidConnection"
    V2NodeCanvas-->>RF: "true/false"
    User->>RF: "Drop on target"
    RF->>V2NodeCanvas: "onConnect(connection)"
    V2NodeCanvas->>V2NodeCanvas: "Validate & check node types"
    alt "Action Node"
        V2NodeCanvas->>Actions: "addConnection(existing input)"
    else "Non-Action Node"
        V2NodeCanvas->>Actions: "updateNodeData(add input)"
        V2NodeCanvas->>Actions: "addConnection(new input)"
    end
    Actions->>Store: "Update workspace.connections"
    Store->>V2NodeCanvas: "Trigger re-render"
    V2NodeCanvas->>RF: "Update edges"
```

Sources: [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:53-398]()

## Styling and Visual Presentation

The editor uses custom CSS classes and styles for visual presentation:

**Editor Class:** `giselle-workflow-editor-v3` [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:367]()

**Pane Styling** [internal-packages/workflow-designer-ui/src/app/globals.css:14-17]():
```css
.giselle-workflow-editor-v3 .react-flow__pane {
  border: 0.5px solid rgba(235, 235, 235, 0.15);
  box-shadow: inset 0 0 40px rgba(200, 200, 200, 0.15);
}
```

This creates a subtle border and inner glow effect on the canvas.

**Cursor States** [internal-packages/workflow-designer-ui/src/app/globals.css:25-40]():
- Default cursor for selection mode
- Crosshair cursor when a floating node is active
- Default cursor for node dragging (prevents grabbing cursor)

Sources: [internal-packages/workflow-designer-ui/src/app/globals.css:1-240](), [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:367]()

## Performance Optimizations

The editor implements several performance optimizations:

### Memoization and Caching

**Node Cache** [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:89-125]():
- Uses `cacheNodesRef` to store previous RFNode objects
- Compares position, selection, and dimensions before creating new objects
- Only creates new RFNode when actual changes are detected
- Reuses cached objects for unchanged nodes

**Edge Cache** [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:127-151]():
- Uses `cacheEdgesRef` for edge objects
- Compares selection state before creating new edges
- Prevents unnecessary edge re-renders

### Shallow Equality Checks

Uses `useShallow` from Zustand to prevent re-renders when nested objects haven't changed [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:54-62]():

```typescript
const data = useWorkflowDesignerStore(
  useShallow((s) => ({
    nodes: s.workspace.nodes,
    connections: s.workspace.connections,
    nodeState: s.workspace.ui.nodeState,
    viewport: s.workspace.ui.viewport,
    selectedConnectionIds: s.workspace.ui.selectedConnectionIds,
  })),
);
```

### Throttled Resize

The properties panel resize handler uses throttling to limit updates [internal-packages/workflow-designer-ui/src/editor/v2/components/floating-properties-panel.tsx:42-64]():

```typescript
const throttle = useCallback((func: (e: MouseEvent) => void, delay: number) => {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;
  let lastExecTime = 0;
  return (e: MouseEvent) => {
    const currentTime = Date.now();
    if (currentTime - lastExecTime > delay) {
      func(e);
      lastExecTime = currentTime;
    } else {
      // Delayed execution
    }
  };
}, []);

const throttledMouseMove = throttle(handleMouseMove, 16); // ~60fps
```

Sources: [internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx:89-151](), [internal-packages/workflow-designer-ui/src/editor/v2/components/floating-properties-panel.tsx:42-88]()

---

# Page: Node Rendering and Visual System

# Node Rendering and Visual System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/playground/app/globals.css](apps/playground/app/globals.css)
- [apps/playground/app/layout.tsx](apps/playground/app/layout.tsx)
- [apps/studio.giselles.ai/app/globals.css](apps/studio.giselles.ai/app/globals.css)
- [apps/studio.giselles.ai/app/layout.tsx](apps/studio.giselles.ai/app/layout.tsx)
- [apps/studio.giselles.ai/tailwind.config.ts](apps/studio.giselles.ai/tailwind.config.ts)
- [internal-packages/workflow-designer-ui/src/editor/node/node.tsx](internal-packages/workflow-designer-ui/src/editor/node/node.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/vector-store/index.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/vector-store/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/tool/floating-node/component.tsx](internal-packages/workflow-designer-ui/src/editor/tool/floating-node/component.tsx)
- [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/state.tsx](internal-packages/workflow-designer-ui/src/editor/tool/toolbar/state.tsx)
- [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx](internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx)
- [internal-packages/workflow-designer-ui/src/editor/tool/types.ts](internal-packages/workflow-designer-ui/src/editor/tool/types.ts)
- [internal-packages/workflow-designer-ui/src/icons/node/file-node.tsx](internal-packages/workflow-designer-ui/src/icons/node/file-node.tsx)
- [internal-packages/workflow-designer-ui/src/icons/node/image-generation-node.tsx](internal-packages/workflow-designer-ui/src/icons/node/image-generation-node.tsx)
- [internal-packages/workflow-designer-ui/src/icons/node/index.tsx](internal-packages/workflow-designer-ui/src/icons/node/index.tsx)
- [internal-packages/workflow-designer-ui/src/new-editor/components/node/node.tsx](internal-packages/workflow-designer-ui/src/new-editor/components/node/node.tsx)
- [internal-packages/workflow-designer-ui/src/ui/node/node-handle-dot.tsx](internal-packages/workflow-designer-ui/src/ui/node/node-handle-dot.tsx)
- [internal-packages/workflow-designer-ui/src/ui/node/node-input-label.tsx](internal-packages/workflow-designer-ui/src/ui/node/node-input-label.tsx)

</details>



This document describes the node rendering and visual system in the workflow designer, including how `NodeComponent` renders nodes on the canvas, the `NodeIcon` resolution system that determines which icon to display for each node type, the `NodeHandleDot` handle system for connection points, and the dynamic styling architecture that uses data attributes and CSS variables to apply node-specific gradients and colors.

For information about the overall editor architecture and state management, see [Editor Architecture and State Management](#5.1). For node-specific configuration panels, see [Properties Panels and Node Configuration](#5.3). For generation execution and results display, see [Generation Execution and Results Display](#5.5).

## Rendering Architecture Overview

The node rendering system provides the visual representation of workflow nodes on the canvas through a layered architecture. Each node is rendered through XyFlow's custom node system, with `CustomXyFlowNode` acting as the ReactFlow integration layer and `NodeComponent` providing the core rendering logic.

The rendering system handles:
- Integration with ReactFlow's (@xyflow/react) node rendering lifecycle
- Dynamic icon resolution based on node type and LLM provider
- Connection state tracking and visual feedback for inputs/outputs
- Visual differentiation using CSS variables and data attributes
- Generation status display with animated transitions
- Editable node names and metadata display
- Node setup state indication with dashed borders

**Sources:** [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:1-145]()

## Rendering Component Architecture

### ReactFlow Integration Layer

ReactFlow Integration and Node Rendering Pipeline

```mermaid
graph TB
    ReactFlow["@xyflow/react<br/>ReactFlow Canvas"]
    nodeTypes["nodeTypes: NodeTypes<br/>{giselle: CustomXyFlowNode}"]
    CustomXyFlowNode["CustomXyFlowNode<br/>function CustomXyFlowNode(id, selected)"]
    Store["useWorkflowDesignerStore<br/>workspace.nodes<br/>workspace.connections<br/>workspace.ui.nodeState"]
    NodeComponent["NodeComponent<br/>function NodeComponent(node, selected, highlighted)"]
    
    ReactFlow -->|"renders with"| nodeTypes
    nodeTypes -->|"maps 'giselle' to"| CustomXyFlowNode
    CustomXyFlowNode -->|"useWorkflowDesignerStore(useShallow)"| Store
    CustomXyFlowNode -->|"renders"| NodeComponent
    
    Store -->|"nodes: NodeLike[]"| CustomXyFlowNode
    Store -->|"connections: Connection[]"| CustomXyFlowNode
    Store -->|"nodeState[nodeId].highlighted"| CustomXyFlowNode
```

The `nodeTypes` export provides ReactFlow with the custom node component mapping:

```typescript
export const nodeTypes: NodeTypes = {
  giselle: CustomXyFlowNode,
};
```

All workflow nodes use the type `"giselle"`, which ReactFlow maps to `CustomXyFlowNode`. This component queries the Zustand store and delegates to `NodeComponent` for actual rendering.

**Sources:** [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:103-105](), [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:107-144]()

### CustomXyFlowNode Wrapper

The `CustomXyFlowNode` component serves as the integration layer between XyFlow and the application state:

| Responsibility | Implementation |
|---------------|----------------|
| Receive XyFlow props | `NodeProps` interface with `id` and `selected` |
| Query workspace state | `useWorkflowDesignerStore` with shallow equality |
| Compute connection state | Filter connections by node ID for inputs/outputs |
| Delegate rendering | Pass all data to `NodeComponent` |

The component uses `useShallow` from Zustand to optimize re-renders by only updating when relevant state changes.

**Sources:** [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:66-104]()

### Data Flow to NodeComponent

```mermaid
graph LR
    subgraph "CustomXyFlowNode"
        StoreQuery["useWorkflowDesignerStore<br/>useShallow"]
        ComputeConn["Compute<br/>connectedInputIds<br/>connectedOutputIds"]
    end
    
    subgraph "NodeComponent Props"
        NodeData["node: NodeLike"]
        Selected["selected: boolean"]
        Highlighted["highlighted: boolean"]
        ConnInputs["connectedInputIds: InputId[]"]
        ConnOutputs["connectedOutputIds: OutputId[]"]
        Preview["preview: boolean"]
    end
    
    StoreQuery -->|"node"| NodeData
    StoreQuery -->|"connections"| ComputeConn
    StoreQuery -->|"highlighted"| Highlighted
    ComputeConn --> ConnInputs
    ComputeConn --> ConnOutputs
    
    NodeData --> Render["NodeComponent<br/>Rendering"]
    Selected --> Render
    Highlighted --> Render
    ConnInputs --> Render
    ConnOutputs --> Render
    Preview --> Render
```

The `connectedInputIds` and `connectedOutputIds` arrays are computed by filtering the workspace connections:

```typescript
const connectedInputIds = useMemo(
  () =>
    connections
      .filter((connection) => connection.inputNode.id === id)
      .map((connection) => connection.inputId),
  [connections, id],
);
```

**Sources:** [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:75-88](), [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:95-103]()

## Node Type System

Nodes are classified into several categories based on their role in the workflow:

### Node Categories

| Category | Node Types | Characteristics |
|----------|-----------|----------------|
| **Source Nodes** | `text`, `file`, `webPage` | Provide input data; have outputs only |
| **Operation Nodes** | `textGeneration`, `imageGeneration`, `query`, `webSearch`, `audioGeneration`, `videoGeneration` | Transform data; have both inputs and outputs |
| **Integration Nodes** | `github`, `vectorStore` | Access external data sources; configuration-dependent I/O |
| **Flow Control** | `trigger`, `action` | Control workflow execution; special connection rules |

### Type Guards and Helpers

The system uses type guard functions from `@giselle-sdk/data-type`:

- `isTextGenerationNode(node)` - Check for text generation nodes
- `isImageGenerationNode(node)` - Check for image generation nodes
- `isTriggerNode(node, type?)` - Check for trigger nodes with optional type filter
- `isActionNode(node, type?)` - Check for action nodes with optional type filter
- `isVectorStoreNode(node)` - Check for vector store nodes

**Sources:** [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:1-11]()

### Node Setup Requirements

The `nodeRequiresSetup` function determines if a node needs configuration before use:

```mermaid
graph TD
    Check["nodeRequiresSetup(node)"]
    
    IsTrigger{"isTriggerNode<br/>(node, 'github')"}
    IsAction{"isActionNode<br/>(node, 'github')"}
    IsVector{"isVectorStoreNode<br/>(node)"}
    
    TriggerStatus{"node.content.state.status<br/>!== 'configured'"}
    ActionStatus{"node.content.command.state.status<br/>!== 'configured'"}
    VectorStatus{"node.content.source.state.status<br/>!== 'configured'"}
    
    Check --> IsTrigger
    IsTrigger -->|Yes| TriggerStatus
    IsTrigger -->|No| IsAction
    IsAction -->|Yes| ActionStatus
    IsAction -->|No| IsVector
    IsVector -->|Yes| VectorStatus
    IsVector -->|No| ReturnFalse["return false"]
    
    TriggerStatus -->|True| ReturnTrue["return true"]
    TriggerStatus -->|False| ReturnFalse
    ActionStatus -->|True| ReturnTrue
    ActionStatus -->|False| ReturnFalse
    VectorStatus -->|True| ReturnTrue
    VectorStatus -->|False| ReturnFalse
```

Nodes requiring setup are rendered with reduced opacity and a dashed border.

**Sources:** [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:42-60](), [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:193](), [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:245-246]()

## Handle Connection System

Handles are the connection points on nodes where edges can be attached. The system implements XyFlow's `Handle` component with custom styling and connection logic.

### Handle Types and Positions

```mermaid
graph LR
    subgraph "Left Side (Inputs)"
        Target1["Handle<br/>type='target'<br/>position=Left"]
        Target2["Handle<br/>type='target'<br/>position=Left"]
        Target3["Handle<br/>type='target'<br/>position=Left"]
    end
    
    subgraph "Node"
        NodeCore["NodeComponent<br/>Visual Content"]
    end
    
    subgraph "Right Side (Outputs)"
        Source1["Handle<br/>type='source'<br/>position=Right"]
        Source2["Handle<br/>type='source'<br/>position=Right"]
    end
    
    Target1 --> NodeCore
    Target2 --> NodeCore
    Target3 --> NodeCore
    NodeCore --> Source1
    NodeCore --> Source2
```

### Input Handle Rendering

Input handles are rendered on the left side with different logic based on node type:

#### Standard Operation Nodes

For text/image generation, query, and web search nodes with defined inputs:

```typescript
node.inputs?.map((input) => (
  <Handle
    type="target"
    isConnectable={false}
    position={Position.Left}
    id={input.id}
    className="!absolute !w-[11px] !h-[11px] !rounded-full..."
  />
))
```

**Sources:** [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:377-402]()

#### Action Nodes

Action nodes have special connection state handling with required/optional inputs:

| Connection State | Visual Treatment |
|-----------------|------------------|
| Connected | Handle filled, label shown on right (inside node) |
| Disconnected (required) | Handle unfilled, label shown on left (outside) in red |
| Disconnected (optional) | Handle unfilled, label shown on left (outside) in gray |

The handle's `isConnectable` prop is computed based on connection state:

```typescript
isConnectable={
  !connectedInputIds?.some(
    (connectedInputId) => connectedInputId === input.id,
  )
}
```

**Sources:** [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:403-444]()

#### Blank Handle for Operations

Operations without explicit inputs (but not triggers or actions) render a generic "blank handle":

```typescript
<Handle
  type="target"
  position={Position.Left}
  id="blank-handle"
  className="!absolute !w-[11px] !h-[11px] !rounded-full..."
/>
```

**Sources:** [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:445-470]()

### Output Handle Rendering

Output handles are rendered on the right side for all nodes with outputs:

```mermaid
graph TD
    RenderOutput["Render output handles"]
    
    CheckConn{"Is output ID in<br/>connectedOutputIds?"}
    
    SetConnected["data-state='connected'<br/>Handle filled<br/>Label inside node"]
    SetDisconnected["data-state='disconnected'<br/>Handle unfilled<br/>Label outside node"]
    
    RenderOutput --> CheckConn
    CheckConn -->|Yes| SetConnected
    CheckConn -->|No| SetDisconnected
```

The connection state determines styling through data attributes:

```typescript
data-state={
  connectedOutputIds?.some(
    (connectedOutputId) => connectedOutputId === output.id,
  )
    ? "connected"
    : "disconnected"
}
```

**Sources:** [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:473-538]()

## Visual Styling Architecture

The node component uses a CSS variable and data attribute-based styling system. All styling is computed through the variant object (`v`) and applied using `clsx` for conditional classes.

### Variant Object System

The `NodeComponent` computes a variant object that drives all visual styling decisions:

Visual Variant Computation Flow

```mermaid
graph TD
    ContentType["node.content.type"]
    
    ComputeV["Compute variant object (v)<br/>useMemo based on node.content.type"]
    
    TypeFlags["Type Flags<br/>v.isText, v.isFile, v.isWebPage<br/>v.isTextGeneration, v.isImageGeneration<br/>v.isGithub, v.isVectorStore<br/>v.isTrigger, v.isAction, v.isQuery"]
    
    ProviderFlags["Provider-specific Flags<br/>v.isVectorStoreGithub<br/>v.isVectorStoreDocument"]
    
    StyleFlags["Style Flags<br/>v.isFillIcon / v.isStrokeIcon<br/>v.isDarkIconText / v.isLightIconText"]
    
    ApplyStyles["Apply to Elements<br/>Root div background gradients<br/>Border overlay gradients<br/>Icon background colors<br/>Icon SVG fill/stroke<br/>Handle colors"]
    
    ContentType --> ComputeV
    ComputeV --> TypeFlags
    ComputeV --> ProviderFlags
    ComputeV --> StyleFlags
    
    TypeFlags --> ApplyStyles
    ProviderFlags --> ApplyStyles
    StyleFlags --> ApplyStyles
```

The variant object is computed once per render using `useMemo`:

```typescript
const v = useMemo(() => {
  const isText = node.content.type === "text";
  const isFile = node.content.type === "file";
  const isWebPage = node.content.type === "webPage";
  const isTextGeneration = node.content.type === "textGeneration";
  // ... more type checks
  
  const isVectorStoreGithub =
    isVectorStore &&
    isVectorStoreNode(node) &&
    node.content.source.provider === "github";
  
  const isFillIcon =
    isText || isFile || isWebPage || isGithub || isVectorStore || isAction;
  const isStrokeIcon =
    isTextGeneration || isImageGeneration || isTrigger || isQuery;
  
  const isDarkIconText = isText || isFile || isWebPage || isQuery;
  const isLightIconText =
    isTextGeneration || isImageGeneration || isGithub || isVectorStoreGithub || isTrigger || isAction;
  
  return { isText, isFile, /* ... */ isFillIcon, isStrokeIcon, isDarkIconText, isLightIconText };
}, [node]);
```

**Sources:** [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:200-255]()

### Data Attribute System

The root `div` element sets multiple data attributes that cascade to child elements:

| Data Attribute | Values | Purpose |
|---------------|--------|---------|
| `data-type` | `source`, `operation` | Node category |
| `data-content-type` | `text`, `textGeneration`, `imageGeneration`, etc. | Specific node type |
| `data-selected` | `true`, `false` | Selection state |
| `data-highlighted` | `true`, `false` | Highlight state (from store) |
| `data-preview` | `true`, `false` | Preview mode |
| `data-current-generation-status` | `created`, `queued`, `running`, `completed`, `failed` | Generation lifecycle |
| `data-vector-store-source-provider` | `github`, `githubPullRequest`, `document` | Vector store provider |

**Sources:** [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:261-270]()

### CSS Variable and Gradient System

Each node type has gradient colors defined as CSS variables in `globals.css`:

CSS Variable to Visual Element Mapping

```mermaid
graph TB
    subgraph "CSS Variables (globals.css)"
        TextVars["--color-text-node-1<br/>--color-text-node-2"]
        FileVars["--color-file-node-1<br/>--color-file-node-2"]
        GenVars["--color-generation-node-1<br/>--color-generation-node-2"]
        ImageVars["--color-image-generation-node-1<br/>--color-image-generation-node-2"]
        GitHubVars["--color-github-node-1<br/>--color-github-node-2"]
        TriggerVars["--color-trigger-node-1<br/>--color-trigger-node-2"]
        ActionVars["--color-action-node-1<br/>--color-action-node-2"]
        QueryVars["--color-query-node-1<br/>--color-query-node-2"]
    end
    
    subgraph "Tailwind Classes"
        BgGradient["bg-gradient-to-tl<br/>from-{type}-node-1<br/>to-{type}-node-2"]
        BorderGradient["bg-gradient-to-br<br/>from-{type}-node-1/40<br/>to-{type}-node-1"]
        IconBg["bg-{type}-node-1"]
        HandleBorder["!border-{type}-node-1"]
        HandleFill["!bg-{type}-node-1"]
    end
    
    subgraph "Applied Elements"
        RootDiv["Root div<br/>Node container"]
        BorderOverlay["Border overlay div<br/>Absolute positioned"]
        IconContainer["Icon container div<br/>32x32 square"]
        Handles["Handle components<br/>NodeHandleDot"]
    end
    
    TextVars --> BgGradient
    FileVars --> BgGradient
    GenVars --> BgGradient
    
    BgGradient --> RootDiv
    BorderGradient --> BorderOverlay
    IconBg --> IconContainer
    HandleBorder --> Handles
    HandleFill --> Handles
```

Example color variables from `apps/studio.giselles.ai/app/globals.css`:

```css
--color-text-node-1: var(--color-node-text-primary);
--color-text-node-2: var(--color-node-text-secondary);

--color-generation-node-1: var(--color-node-generation-primary);
--color-generation-node-2: var(--color-node-generation-secondary);

--color-image-generation-node-1: var(--color-node-image-generation-primary);
--color-image-generation-node-2: var(--color-node-image-generation-secondary);
```

The gradient classes are applied conditionally based on the variant object:

```typescript
className={clsx(
  "group relative flex flex-col rounded-[16px] py-[16px] gap-[16px] min-w-[180px]",
  "bg-gradient-to-tl transition-all backdrop-blur-[4px]",
  v.isText && "from-text-node-1/10 to-text-node-2 shadow-text-node-1",
  v.isFile && "from-file-node-1/10 to-file-node-2 shadow-file-node-1",
  v.isTextGeneration && "from-generation-node-1/10 to-generation-node-2 shadow-generation-node-1",
  v.isImageGeneration && "from-image-generation-node-1/20 to-image-generation-node-2 shadow-image-generation-node-1",
  // etc.
)}
```

**Sources:** [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:271-306](), [apps/studio.giselles.ai/app/globals.css:70-112]()

### Border Overlay System

The node uses a dual-layer approach for visual depth:

1. **Base container**: Background gradient with `bg-gradient-to-tl` and `backdrop-blur-[4px]`
2. **Border overlay**: Absolutely positioned `div` with `bg-gradient-to-br` for the border effect

Border Overlay Dual-Layer System

```mermaid
graph LR
    Base["Base Container<br/>bg-gradient-to-tl<br/>backdrop-blur-4px<br/>from-{type}-node-1/10<br/>to-{type}-node-2"]
    
    Overlay["Border Overlay<br/>absolute inset-0 z-0<br/>bg-gradient-to-br<br/>from-{type}-node-1/40<br/>to-{type}-node-1"]
    
    SetupBorder["Setup Requirement<br/>requiresSetup === true"]
    
    DashedBorder["border-black/60<br/>border-dashed<br/>[border-width:2px]"]
    
    TransparentBorder["border-transparent<br/>border-[1px]"]
    
    Base --> Overlay
    Overlay --> SetupBorder
    SetupBorder -->|"true"| DashedBorder
    SetupBorder -->|"false"| TransparentBorder
```

The border overlay changes based on setup requirements checked by `nodeRequiresSetup()`:

```typescript
className={clsx(
  "absolute z-0 rounded-[16px] inset-0 border-[1px] mask-fill bg-gradient-to-br bg-origin-border bg-clip-boarder",
  requiresSetup
    ? "border-black/60 border-dashed [border-width:2px]"
    : "border-transparent",
  v.isText && "from-text-node-1/40 to-text-node-1",
  v.isFile && "from-file-node-1/40 to-file-node-1",
  // gradient for each type
)}
```

**Sources:** [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:354-375]()

### Handle Visual Coordination System

The `NodeHandleDot` component provides consistent handle styling coordinated with node colors:

Handle Color Coordination with NodeHandleDot

```mermaid
graph TB
    ContentType["contentType prop<br/>textGeneration, imageGeneration, etc."]
    
    BorderMap["borderToneByType map<br/>Record<contentType, string>"]
    FillMap["fillToneByType map<br/>Record<contentType, string>"]
    
    BorderClass["Border Class<br/>!border-{type}-node-1"]
    FillClass["Fill Class<br/>!bg-{type}-node-1"]
    
    IsConnected{"isConnected prop"}
    
    Handle["Handle component<br/>@xyflow/react"]
    
    UnconnectedStyle["Unfilled<br/>background: var(--color-background)<br/>borderColor: var(--color-border)"]
    
    ConnectedStyle["Filled<br/>Apply border + fill classes"]
    
    ContentType --> BorderMap
    ContentType --> FillMap
    
    BorderMap --> BorderClass
    FillMap --> FillClass
    
    BorderClass --> Handle
    FillClass --> Handle
    
    Handle --> IsConnected
    IsConnected -->|"false"| UnconnectedStyle
    IsConnected -->|"true"| ConnectedStyle
```

The `NodeHandleDot` component maintains lookup maps for colors:

```typescript
const borderToneByType: Record<NodeHandleDotProps["contentType"], string> = {
  textGeneration: "!border-generation-node-1",
  imageGeneration: "!border-image-generation-node-1",
  github: "!border-github-node-1",
  // etc.
};

const fillToneByType: Record<NodeHandleDotProps["contentType"], string> = {
  textGeneration: "!bg-generation-node-1",
  imageGeneration: "!bg-image-generation-node-1",
  github: "!bg-github-node-1",
  // etc.
};
```

When rendered, connected handles show the fill color, while disconnected handles use the canvas background:

```typescript
<Handle
  style={
    !isConnected
      ? {
          background: "var(--color-background)",
          borderColor: "var(--color-border)",
        }
      : undefined
  }
  className={clsx(
    borderToneByType[safeContentType],
    isConnected ? fillToneByType[safeContentType] : "",
  )}
/>
```

**Sources:** [internal-packages/workflow-designer-ui/src/ui/node/node-handle-dot.tsx:26-102]()

## Generation Status Display

The node component integrates with the generation system to display real-time status:

### Status Badge Rendering

```mermaid
stateDiagram-v2
    [*] --> created: Generation starts
    created --> queued: Queued for execution
    queued --> running: Execution begins
    running --> completed: Success
    running --> failed: Error
    
    created --> WaitingBadge: Show "Waiting..."
    queued --> GeneratingBadge: Show "Generating..." + Stop button
    running --> GeneratingBadge: Show "Generating..." + Stop button
    completed --> CompletionBadge: Show provider label + checkmark (2s)
    CompletionBadge --> [*]: Fade out
```

The component uses `useCurrentNodeGeneration` hook to track the current generation and `useTransition` to show the completion label for 2 seconds:

```typescript
const { currentGeneration, stopCurrentGeneration } = useCurrentNodeGeneration(node.id);

useEffect(() => {
  if (currentGeneration === undefined) return;
  
  if (
    prevGenerationStatusRef.current === "running" &&
    currentGeneration.status === "completed"
  ) {
    startTransition(
      async () =>
        new Promise((resolve) => {
          setTimeout(() => resolve(), 2000);
        }),
    );
  }
}, [currentGeneration]);
```

**Sources:** [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:122-146]()

### Completion Label

The completion label shows the LLM provider for generation nodes:

```typescript
function getCompletionLabel(node: NodeLike): string {
  if (isTextGenerationNode(node) || isImageGenerationNode(node)) {
    return node.content.llm.provider;
  }
  return "Completed";
}
```

This label is displayed with a checkmark icon using Framer Motion's `AnimatePresence` for animation:

```typescript
<AnimatePresence>
  {showCompleteLabel && node.content.type !== "trigger" && (
    <motion.div
      className="absolute top-[-28px] right-0..."
      exit={{ opacity: 0 }}
    >
      <p>{getCompletionLabel(node)}</p>
      <CheckIcon className="w-4 h-4" />
    </motion.div>
  )}
</AnimatePresence>
```

**Sources:** [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:34-40](), [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:227-241]()

## Node Metadata and Editing

### Metadata Display

The node displays metadata in a small font at the top:

| Metadata Item | Display Logic |
|--------------|---------------|
| LLM Provider | Shown for text/image generation nodes |
| Node ID | Shown as 8-character substring (`node.id.substring(3, 11)`) |

When the node is selected, metadata items show tooltips:

```typescript
{selected ? (
  <Tooltip text={item.tooltip} variant="dark">
    <button type="button">{item.label}</button>
  </Tooltip>
) : (
  item.label
)}
```

**Sources:** [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:147-154](), [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:335-346]()

### Editable Node Name

The node name is rendered using the `EditableText` component with `defaultName` fallback:

```typescript
<EditableText
  className="group-data-[selected=false]:pointer-events-none..."
  text={defaultName(node)}
  onValueChange={(value) => {
    if (value === defaultName(node)) return;
    if (value.trim().length === 0) {
      updateNodeData(node.id, { name: undefined });
      return;
    }
    updateNodeData(node.id, { name: value });
  }}
  onClickToEditMode={(e) => {
    if (!selected) {
      e.preventDefault();
      return;
    }
    e.stopPropagation();
  }}
/>
```

The name is only editable when the node is selected, enforced through both pointer events and click handler logic.

**Sources:** [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:348-368]()

## Special Node Information Components

### DocumentNodeInfo Component

The `DocumentNodeInfo` component displays document-specific information for document vector store nodes (implementation not shown in provided files).

**Sources:** [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:372]()

### GitHubNodeInfo Component

The `GitHubNodeInfo` component displays GitHub-specific information for GitHub integration nodes (implementation not shown in provided files).

**Sources:** [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:373]()

### GitHubTriggerStatusBadge

For configured GitHub trigger nodes, a status badge is displayed:

```typescript
{isTriggerNode(node, "github") &&
  node.content.state.status === "configured" && (
    <div className="-mt-[6px]">
      <GitHubTriggerStatusBadge
        flowTriggerId={node.content.state.flowTriggerId}
      />
    </div>
  )}
```

**Sources:** [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:267-274]()

## Node Icon System

Each node displays an icon in a colored square at the top:

```mermaid
graph TB
    NodeIcon["NodeIcon Component"]
    NodeType["node.type + node.content.type"]
    
    IconBg["Icon Background<br/>32x32px rounded square<br/>Color based on content type"]
    IconSvg["SVG Icon<br/>16x16px<br/>Fill or stroke based on type"]
    
    NodeType -->|"determines"| IconBg
    NodeType -->|"determines"| IconSvg
    
    IconBg -->|"contains"| IconSvg
    
    NodeIcon -->|"receives"| NodeType
    NodeIcon -->|"renders"| IconBg
```

The icon background uses the node's primary color:

```typescript
className={clsx(
  "w-[32px] h-[32px] flex items-center justify-center rounded-[8px]",
  "group-data-[content-type=text]:bg-text-node-1",
  "group-data-[content-type=textGeneration]:bg-generation-node-1",
  // etc.
)}
```

The icon itself has content-specific fill/stroke styling:

```typescript
className={clsx(
  "w-[16px] h-[16px]",
  "group-data-[content-type=text]:fill-current",
  "group-data-[content-type=vectorStore]:stroke-current fill-none",
  // etc.
)}
```

**Sources:** [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:276-333]()

---

# Page: Properties Panels and Node Configuration

# Properties Panels and Node Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [internal-packages/ui/components/prompt-editor.tsx](internal-packages/ui/components/prompt-editor.tsx)
- [internal-packages/workflow-designer-ui/src/editor/index.tsx](internal-packages/workflow-designer-ui/src/editor/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/app-entry-node-properties-panel/index.ts](internal-packages/workflow-designer-ui/src/editor/properties-panel/app-entry-node-properties-panel/index.ts)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/file-node-properties-panel/file-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/file-node-properties-panel/file-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/file-node-properties-panel/index.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/file-node-properties-panel/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/generation-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/generation-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/index.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/prompt-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/prompt-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/index.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/generation-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/generation-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/index.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/query-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/query-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/generation-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/generation-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/index.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/prompt-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/prompt-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-node-properties-panel/index.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/text-node-properties-panel/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/index.ts](internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/index.ts)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/panel-spacing.ts](internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/panel-spacing.ts)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/properties-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/properties-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/resizable-section.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/resizable-section.tsx)
- [internal-packages/workflow-designer-ui/src/ui/generation-view.tsx](internal-packages/workflow-designer-ui/src/ui/generation-view.tsx)
- [internal-packages/workflow-designer-ui/src/ui/image-generation-loading.tsx](internal-packages/workflow-designer-ui/src/ui/image-generation-loading.tsx)
- [internal-packages/workflow-designer-ui/src/ui/query-result-view.tsx](internal-packages/workflow-designer-ui/src/ui/query-result-view.tsx)
- [packages/text-editor/src/react/component.tsx](packages/text-editor/src/react/component.tsx)

</details>



This document covers the properties panel system in the workflow designer that allows users to configure node behavior, select AI models, adjust parameters, and execute generations. The properties panel system provides specialized interfaces for TextGeneration, ImageGeneration, Query, File, and Text nodes, each with node-type-specific configuration options.

For information about the visual node rendering system, see page 5.2. For details about generation execution and results display, see page 5.5.

## Properties Panel Architecture

The properties panel system is built around a modular architecture that dynamically renders different configuration interfaces based on the selected node type. The main entry point is the `PropertiesPanel` component in [internal-packages/workflow-designer-ui/src/editor/properties-panel/index.tsx](), which uses type guards to determine which specialized panel to render.

### Panel Component Structure

```mermaid
graph TD
    PropertiesPanel["PropertiesPanel<br/>(index.tsx)"]
    
    subgraph "Base Components"
        PropertiesPanelRoot["PropertiesPanelRoot"]
        NodePanelHeader["NodePanelHeader"]
        PropertiesPanelContent["PropertiesPanelContent"]
    end
    
    subgraph "Node-Specific Panels"
        TextGenPanel["TextGenerationNodePropertiesPanel"]
        ImageGenPanel["ImageGenerationNodePropertiesPanel"]
        QueryPanel["QueryNodePropertiesPanel"]
        FilePanel["FileNodePropertiesPanel"]
        TextPanel["TextNodePropertiesPanel"]
        VectorStorePanel["VectorStoreNodePropertiesPanel"]
        ActionPanel["ActionNodePropertiesPanel"]
        TriggerPanel["TriggerNodePropertiesPanel"]
    end
    
    subgraph "State Hooks"
        useWorkflowDesigner["useWorkflowDesigner()"]
        useNodeGenerations["useNodeGenerations()"]
        useWorkflowDesignerStore["useWorkflowDesignerStore"]
    end
    
    PropertiesPanel --> |"isTextGenerationNode()"|TextGenPanel
    PropertiesPanel --> |"isImageGenerationNode()"|ImageGenPanel
    PropertiesPanel --> |"isQueryNode()"|QueryPanel
    PropertiesPanel --> |"isFileNode()"|FilePanel
    PropertiesPanel --> |"isTextNode()"|TextPanel
    PropertiesPanel --> |"isVectorStoreNode()"|VectorStorePanel
    PropertiesPanel --> |"isActionNode()"|ActionPanel
    PropertiesPanel --> |"isTriggerNode()"|TriggerPanel
    
    TextGenPanel --> PropertiesPanelRoot
    ImageGenPanel --> PropertiesPanelRoot
    QueryPanel --> PropertiesPanelRoot
    FilePanel --> PropertiesPanelRoot
    TextPanel --> PropertiesPanelRoot
    
    PropertiesPanelRoot --> NodePanelHeader
    PropertiesPanelRoot --> PropertiesPanelContent
    
    TextGenPanel --> useWorkflowDesigner
    TextGenPanel --> useNodeGenerations
    ImageGenPanel --> useWorkflowDesigner
    ImageGenPanel --> useNodeGenerations
    QueryPanel --> useWorkflowDesigner
    QueryPanel --> useNodeGenerations
    
    useWorkflowDesigner --> useWorkflowDesignerStore
```

Each specialized panel component follows a consistent structure:
- `NodePanelHeader` with node name, documentation link, and delete action
- `PropertiesPanelContent` containing configuration sections
- Generation/execution controls at the bottom

**Sources:** [internal-packages/workflow-designer-ui/src/editor/properties-panel/index.tsx:27-112](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/properties-panel.tsx:49-156](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/node-panel-header.tsx]()

## Text Generation Node Configuration

The `TextGenerationNodePropertiesPanel` provides configuration for LLM-based text generation nodes, supporting OpenAI, Anthropic, and Google providers. The panel is located at [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/index.tsx]().

### Component Structure

```mermaid
graph TD
    TextGenPanel["TextGenerationNodePropertiesPanel"]
    
    subgraph "Header"
        NodePanelHeader["NodePanelHeader<br/>name, docs, delete"]
        UsageLimitWarning["UsageLimitWarning"]
    end
    
    subgraph "Configuration"
        PromptPanel["PromptPanel"]
        ModelPicker["ModelPicker<br/>(openai/anthropic/google)"]
        ModelParams["Model Parameters"]
        PromptEditor["PromptEditor"]
        ToolsPanel["ToolsPanel<br/>(Advanced options)"]
    end
    
    subgraph "Model-Specific Panels"
        OpenAIPanel["OpenAIModelPanel<br/>temperature, maxTokens, tools"]
        AnthropicPanel["AnthropicModelPanel<br/>temperature, maxTokens"]
        GooglePanel["GoogleModelPanel<br/>temperature, searchGrounding"]
    end
    
    subgraph "Output Section"
        GenerationPanel["GenerationPanel"]
        GenerationView["GenerationView<br/>(markdown, reasoning)"]
        GenerateCtaButton["GenerateCtaButton<br/>(Cmd+Enter)"]
    end
    
    subgraph "Hooks & State"
        useNodeGenerations["useNodeGenerations<br/>createAndStartGenerationRunner"]
        useConnectedOutputs["useConnectedOutputs<br/>sourceNodes, connectedSources"]
        updateNodeDataContent["updateNodeDataContent"]
    end
    
    TextGenPanel --> NodePanelHeader
    TextGenPanel --> UsageLimitWarning
    TextGenPanel --> PromptPanel
    
    PromptPanel --> ModelPicker
    PromptPanel --> PromptEditor
    PromptPanel --> ToolsPanel
    
    ModelPicker --> OpenAIPanel
    ModelPicker --> AnthropicPanel
    ModelPicker --> GooglePanel
    
    TextGenPanel --> GenerationPanel
    GenerationPanel --> GenerationView
    TextGenPanel --> GenerateCtaButton
    
    TextGenPanel --> useNodeGenerations
    TextGenPanel --> useConnectedOutputs
    PromptPanel --> updateNodeDataContent
```

### Key Features

**Expandable Editors**: The prompt editor and generation output both support expansion to full-screen overlays (lines 184-285). The expanded state uses `isPromptExpanded` and `isGenerationExpanded` flags with animated transitions.

**Keyboard Shortcuts**: `useKeyboardShortcuts` hook (line 80-86) enables Cmd/Ctrl+Enter to trigger generation.

**Connected Sources**: The `useConnectedOutputs` hook (line 47-59) retrieves nodes connected to this node's inputs, making them available for insertion into the prompt via `@` mentions.

**Generation Execution**: The `generateText` callback (lines 88-117):
1. Checks usage limits via `usageLimitsReached`
2. Validates prompt is not empty using `isPromptEmpty`
3. Calls `createAndStartGenerationRunner` with operation node, source nodes, and connections
4. Passes workspace ID as origin for tracking

**Sources:** [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/index.tsx:28-290](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/prompt-panel.tsx:89-397]()

## Image Generation Node Configuration

The `ImageGenerationNodePropertiesPanel` handles configuration for AI image generation nodes, supporting Fal, OpenAI, and Google providers with provider-specific parameters. The panel is located at [internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/index.tsx]().

### Component Architecture

```mermaid
graph TD
    ImageGenPanel["ImageGenerationNodePropertiesPanel"]
    
    subgraph "Configuration"
        PromptPanel["PromptPanel"]
        ModelPicker["ModelPicker<br/>(fal/openai/google)"]
        PromptEditor["PromptEditor<br/>with image node inputs"]
    end
    
    subgraph "Model Panels"
        FalModelPanel["FalModelPanel<br/>size, numImages"]
        OpenAIImageModelPanel["OpenAIImageModelPanel<br/>size, quality"]
    end
    
    subgraph "Output"
        GenerationPanel["GenerationPanel"]
        GenerationView["GenerationView<br/>ImageCard grid"]
        GenerateCtaButton["GenerateCtaButton"]
    end
    
    subgraph "State Management"
        useConnectedSources["useConnectedSources<br/>file/text inputs"]
        createDefaultModelData["createDefaultModelData<br/>(fal|openai|google)"]
        disconnectInvalidConnections["disconnectInvalidConnections"]
    end
    
    ImageGenPanel --> PromptPanel
    PromptPanel --> ModelPicker
    PromptPanel --> PromptEditor
    
    ModelPicker --> FalModelPanel
    ModelPicker --> OpenAIImageModelPanel
    
    ImageGenPanel --> GenerationPanel
    GenerationPanel --> GenerationView
    ImageGenPanel --> GenerateCtaButton
    
    PromptPanel --> useConnectedSources
    ModelPicker --> createDefaultModelData
    ModelPicker --> disconnectInvalidConnections
```

### Provider-Specific Configuration

| Provider | Models | Configuration Parameters |
|----------|--------|-------------------------|
| `fal` | `fal-ai/flux/schnell`, `fal-ai/flux-pro` | `size`: "1024x1024" \| "1152x864" \| "1312x736" \| "512x512"<br/>`numImages`: 1-4 |
| `openai` | `dall-e-3` | `size`: "1024x1024" \| "1024x1792" \| "1792x1024"<br/>`quality`: "standard" \| "hd" |
| `google` | `imagen-3.0-generate-001` | (uses default configurations) |

### Key Implementation Details

**Model Selection**: The `ModelPicker` component (lines 133-164) displays provider groups with model options. When a model is selected, `createDefaultModelData` creates provider-specific configuration with default values.

**Connection Validation**: The `disconnectInvalidConnections` function (lines 102-123) checks if existing connections remain valid after a model change. For example, switching from OpenAI to Fal may invalidate connections if the new model doesn't support certain input types.

**Expandable Overlays**: Both prompt editor and generation panel support full-screen expansion (lines 144-243) with animated transitions and backdrop clicks to minimize.

**Image-Specific Inputs**: The prompt editor supports connecting to File nodes (category: "image") to use reference images in the generation. The `useConnectedSources` hook (line 39) filters for compatible source nodes.

**Sources:** [internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/index.tsx:27-248](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/prompt-panel.tsx:32-205](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/models/fal.tsx](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/models/openai.tsx]()

## Query Node Configuration

The `QueryNodePropertiesPanel` provides configuration for semantic search across vector stores (GitHub repositories and document stores). The panel is located at [internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/index.tsx]().

### Component Structure

```mermaid
graph TD
    QueryPanel["QueryNodePropertiesPanel"]
    
    subgraph "Configuration"
        SettingsPanel["SettingsPanel<br/>topK, scoreThreshold"]
        QueryPanel_Inner["QueryPanel<br/>TextEditor for query"]
    end
    
    subgraph "Data Source Display"
        ConnectedDatasources["Connected Vector Stores"]
        GitHubInfo["GitHub: owner/repo, contentType"]
        DocumentInfo["Document Store: name, status"]
        RemoveButton["Remove data source button"]
    end
    
    subgraph "Output"
        GenerationPanel["GenerationPanel"]
        QueryResultView["QueryResultView<br/>tabs per data source"]
    end
    
    subgraph "State Hooks"
        useConnectedSources["useConnectedSources<br/>vectorStore nodes"]
        useVectorStore["useVectorStore<br/>documentStores context"]
        useNodeGenerations["useNodeGenerations"]
    end
    
    QueryPanel --> SettingsPanel
    QueryPanel --> QueryPanel_Inner
    
    QueryPanel_Inner --> ConnectedDatasources
    ConnectedDatasources --> GitHubInfo
    ConnectedDatasources --> DocumentInfo
    ConnectedDatasources --> RemoveButton
    
    QueryPanel --> GenerationPanel
    GenerationPanel --> QueryResultView
    
    QueryPanel --> useConnectedSources
    QueryPanel_Inner --> useVectorStore
    QueryPanel --> useNodeGenerations
```

### Settings and Parameters

The `SettingsPanel` component provides:
- **topK**: Number of results to return (default: 5, range: 1-20)
- **scoreThreshold**: Minimum similarity score (default: 0.7, range: 0-1)

### Query Input

The `QueryPanel` component (lines 144-275) uses `TextEditor` to create semantic search queries. It displays connected vector store nodes with metadata:

**GitHub Sources**: Shows `owner/repo` and content type (Code or Pull Requests)
**Document Sources**: Shows document store name and ingestion status (e.g., "3/5 ready", "processing")

Each connected source has a remove button (X icon) that calls `deleteConnection` and removes the corresponding input from the node.

### Generation and Results

Query execution (lines 51-77):
1. Validates query is not empty using `isJsonContent` check
2. Calls `createAndStartGenerationRunner` with source nodes (vector stores)
3. Results displayed in `QueryResultView` with tabs for each data source
4. Each result shows chunk content, similarity score, and metadata

**Sources:** [internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/index.tsx:25-128](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/query-panel.tsx:144-275](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/settings-panel.tsx](), [internal-packages/workflow-designer-ui/src/ui/query-result-view.tsx:435-530]()

## File Node Configuration

The `FileNodePropertiesPanel` provides file upload and management for PDF, text, and image files. The panel is located at [internal-packages/workflow-designer-ui/src/editor/properties-panel/file-node-properties-panel/index.tsx]().

### Component Structure

```mermaid
graph TD
    FilePanel["FileNodePropertiesPanel"]
    
    subgraph "Configuration"
        FileTypeConfig["fileType config<br/>pdf/text/image"]
        AcceptTypes["accept MIME types"]
        MaxFileSize["maxSize: 4.5MB"]
    end
    
    subgraph "Upload UI"
        DragDropZone["Drag & Drop Zone<br/>300px height"]
        FileInput["File Input<br/>multiple=true"]
        PasteHandler["Paste Handler<br/>(images only)"]
    end
    
    subgraph "File List"
        AddedFiles["Added Files list"]
        FileListItem["FileListItem<br/>name, status, remove"]
    end
    
    subgraph "Validation"
        ValidateItems["validateItems<br/>check MIME types"]
        AssertFiles["assertFiles<br/>size + type checks"]
        ErrorHandlers["InvalidFileTypeError<br/>FileSizeExceededError"]
    end
    
    subgraph "State Hooks"
        useFileNode["useFileNode<br/>addFiles, removeFile"]
    end
    
    FilePanel --> FileTypeConfig
    FileTypeConfig --> AcceptTypes
    FileTypeConfig --> MaxFileSize
    
    FilePanel --> DragDropZone
    DragDropZone --> FileInput
    DragDropZone --> PasteHandler
    
    FilePanel --> AddedFiles
    AddedFiles --> FileListItem
    
    DragDropZone --> ValidateItems
    FileInput --> AssertFiles
    AssertFiles --> ErrorHandlers
    
    FilePanel --> useFileNode
```

### File Type Configurations

Defined in `fileType` object (lines 8-21):

| Category | Accept MIME Types | Label |
|----------|------------------|-------|
| `pdf` | `application/pdf` | PDF |
| `text` | `text/plain`, `text/markdown` | Text |
| `image` | `image/png`, `image/jpeg`, `image/gif`, `image/svg` | Image |

### Upload Methods

**Drag & Drop**: The drag zone (lines 303-390) validates file types on `dragover` and shows appropriate indicators (valid/invalid file type).

**File Input**: Standard file input with `multiple` attribute for batch uploads.

**Paste (Images Only)**: Image nodes support pasting from clipboard (lines 226-272). The paste handler extracts image items from `ClipboardEvent` and creates a `FileList` for validation.

### Validation and Error Handling

**File Size**: Hard limit of 4.5MB per file due to Vercel Serverless Functions body size limit (line 23).

**MIME Type Validation**:
- Uses regex to match MIME types against `accept` list
- Falls back to file extension for markdown files (`.md` → `text/markdown`)
- Throws `InvalidFileTypeError` with provider-specific suggestions

**Duplicate Handling**: For image nodes, `generateIncrementalUniqueName` (lines 84-104) appends numbers to duplicate filenames (e.g., "image.png" → "image 1.png").

**Sources:** [internal-packages/workflow-designer-ui/src/editor/properties-panel/file-node-properties-panel/index.tsx:23-39](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/file-node-properties-panel/file-panel.tsx:106-408]()

## Text Node Configuration

The `TextNodePropertiesPanel` provides a simple text editor for static text content. The panel is located at [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-node-properties-panel/index.tsx]().

### Component Structure

```mermaid
graph TD
    TextPanel["TextNodePropertiesPanel"]
    
    subgraph "Header"
        NodePanelHeader["NodePanelHeader<br/>name, docs, delete"]
    end
    
    subgraph "Content"
        TextEditor["TextEditor<br/>from @giselles-ai/text-editor"]
        EditorConfig["showToolbar: false<br/>placeholder: 'Write or paste text here...'"]
        EditorClassName["bg + border styling<br/>min-h: 120px"]
    end
    
    subgraph "State"
        updateNodeDataContent["updateNodeDataContent<br/>({ text })"]
        containerRef["containerRef<br/>for height calculation"]
    end
    
    TextPanel --> NodePanelHeader
    TextPanel --> TextEditor
    
    TextEditor --> EditorConfig
    TextEditor --> EditorClassName
    
    TextEditor --> updateNodeDataContent
    TextPanel --> containerRef
```

### Implementation Details

The Text node is the simplest properties panel, containing only:
1. `NodePanelHeader` with editable name and delete button (lines 16-21)
2. `TextEditor` component with minimal styling (lines 24-30)

The editor:
- Uses TipTap-based editor from `@giselles-ai/text-editor/react`
- No toolbar or advanced formatting
- Updates node content via `updateNodeDataContent` callback
- Styled with transparent background and minimal padding

This node serves as a static text source that can be connected to other nodes (e.g., text generation prompts or query inputs).

**Sources:** [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-node-properties-panel/index.tsx:8-35](), [packages/text-editor/src/react/component.tsx:129-208]()

## Model Selection and Eligibility System

The properties panels use the `ModelPicker` component to handle model selection across providers, with tier-based access control.

### Model Picker Architecture

```mermaid
graph TD
    ModelPicker["ModelPicker<br/>(ui/model-picker)"]
    
    subgraph "Input"
        Groups["groups: ModelGroup[]<br/>{ provider, label, models }"]
        CurrentProvider["currentProvider"]
        CurrentModelId["currentModelId"]
    end
    
    subgraph "Model Groups"
        OpenAIGroup["OpenAI: openaiLanguageModels"]
        AnthropicGroup["Anthropic: anthropicLanguageModels"]
        GoogleGroup["Google: googleLanguageModels"]
        FalGroup["Fal: falLanguageModels"]
    end
    
    subgraph "Tier Checking"
        hasTierAccess["hasTierAccess(model, userTier)"]
        UserTier["userTier: Tier.enum.free|pro"]
        ProTag["ProTag badge"]
        DisabledReason["disabledReason: 'Upgrade to Pro'"]
    end
    
    subgraph "Selection"
        OnSelect["onSelect(provider, modelId)"]
        CreateDefault["createDefaultModelData(provider)"]
        UpdateModelId["updateModelId(model, modelId)"]
        UpdateNode["updateNodeDataContent({ llm })"]
    end
    
    ModelPicker --> Groups
    Groups --> OpenAIGroup
    Groups --> AnthropicGroup
    Groups --> GoogleGroup
    Groups --> FalGroup
    
    OpenAIGroup --> hasTierAccess
    hasTierAccess --> UserTier
    hasTierAccess --> ProTag
    hasTierAccess --> DisabledReason
    
    ModelPicker --> OnSelect
    OnSelect --> CreateDefault
    CreateDefault --> UpdateModelId
    UpdateModelId --> UpdateNode
```

### Model Registry and Tier Access

Models are defined in `@giselles-ai/language-model` package:

**Text Generation Models**:
- `openaiLanguageModels`: GPT-4o, GPT-4o-mini, o1-preview, o1-mini
- `anthropicLanguageModels`: Claude 3.5 Sonnet, Claude 3.5 Haiku, Claude 3 Opus
- `googleLanguageModels`: Gemini 1.5 Pro, Gemini 1.5 Flash, Gemini 2.0 Flash

**Image Generation Models**:
- `falLanguageModels`: FLUX Schnell, FLUX Pro
- `openaiImageModels`: DALL-E 3
- `googleImageLanguageModels`: Imagen 3.0

Each model has a `tier` property (Tier.enum.free or Tier.enum.pro). The `hasTierAccess` function checks if the user's subscription tier allows access to the model.

### Model Group Construction

In `PromptPanel` components, `useModelGroups` hook (text generation) or inline `groups` useMemo (image generation) constructs model groups:

```typescript
const groups = [
  {
    provider: "openai",
    label: "OpenAI",
    models: openaiLanguageModels.map(m => ({
      id: m.id,
      badge: m.tier === Tier.enum.pro ? <ProTag /> : undefined,
      disabled: !hasTierAccess(m, userTier),
      disabledReason: !hasTierAccess(m, userTier) ? "Upgrade to Pro" : undefined
    }))
  },
  // ... other providers
]
```

**Sources:** [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/prompt-panel.tsx:53-87](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/prompt-panel.tsx:63-100](), [internal-packages/ui/components/model-picker.tsx](), [packages/language-model/src/index.ts]()

## Model Parameter Controls

The properties panels use specialized UI components from `@giselle-internal/ui` for parameter adjustment, with provider-specific panels for different model types.

### OpenAI Model Parameters (Text Generation)

The `OpenAIModelPanel` component provides:

| Parameter | Component | Range/Options | Default |
|-----------|-----------|---------------|---------|
| `temperature` | `Slider` | 0.0 - 2.0 | 1.0 |
| `maxTokens` | `Input` (number) | 1 - model max | 4096 |
| `topP` | `Slider` | 0.0 - 1.0 | 1.0 |
| Web Search | `Switch` | on/off | off |
| Structured Output | `Switch` | on/off | off |

When Web Search is enabled, the panel adds a "Source" output to the node for citation data.

### Anthropic Model Parameters

The `AnthropicModelPanel` provides:

| Parameter | Component | Range/Options | Default |
|-----------|-----------|---------------|---------|
| `temperature` | `Slider` | 0.0 - 1.0 | 1.0 |
| `maxTokens` | `Input` (number) | 1 - 8192 | 4096 |
| `topP` | `Slider` | 0.0 - 1.0 | N/A |
| `topK` | `Slider` | 1 - 500 | N/A |

### Google Model Parameters

The `GoogleModelPanel` provides:

| Parameter | Component | Range/Options | Default |
|-----------|-----------|---------------|---------|
| `temperature` | `Slider` | 0.0 - 2.0 | 1.0 |
| `topP` | `Slider` | 0.0 - 1.0 | N/A |
| `topK` | `Slider` | 1 - 500 | N/A |
| `maxOutputTokens` | `Input` (number) | 1 - model max | 8192 |
| Search Grounding | `Switch` | on/off | off |
| URL Context | `Switch` (feature flag) | on/off | off |

Search Grounding and URL Context are mutually exclusive. When either is enabled, a "Source" output is added to the node.

### Parameter Update Flow

```mermaid
graph TD
    ParamControl["Parameter Control<br/>(Slider/Input/Switch)"]
    
    subgraph "Value Change"
        OnValueChange["onValueChange callback"]
        NewValue["new value (number/string/boolean)"]
    end
    
    subgraph "Model Data Update"
        UpdateConfig["update configurations object"]
        MergeModel["{ ...llm, configurations: { ...config, [param]: value } }"]
        OnModelChange["onModelChange callback"]
    end
    
    subgraph "Node Update"
        UpdateNodeDataContent["updateNodeDataContent(node, { llm })"]
        WorkflowStore["workflowDesignerStore.workspace.nodes"]
    end
    
    ParamControl --> OnValueChange
    OnValueChange --> NewValue
    NewValue --> UpdateConfig
    UpdateConfig --> MergeModel
    MergeModel --> OnModelChange
    OnModelChange --> UpdateNodeDataContent
    UpdateNodeDataContent --> WorkflowStore
```

Each model panel receives `languageModel` (current config) and `onModelChange` callback. The callback merges the updated parameter into the `configurations` object and calls `updateNodeDataContent` to persist the change to the node.

**Sources:** [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/openai.tsx](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/anthropic.tsx](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/google.tsx](), [internal-packages/ui/components/slider.tsx]()

## Configuration Validation and Generation Execution

The properties panels implement comprehensive validation before allowing generation execution, including prompt validation, usage limit checks, and model eligibility verification.

### Validation and Execution Flow

```mermaid
graph TD
    subgraph "Generation Execution Pipeline"
        GenerateButton["Generate Button Click"]
        
        subgraph "Pre-execution Validation"
            UsageLimitCheck["usageLimitsReached check"]
            PromptValidation["isPromptEmpty validation"]
            ConnectedSources["useConnectedOutputs/useConnectedSources"]
        end
        
        subgraph "Generation Setup"
            CreateRunner["createAndStartGenerationRunner"]
            OperationNode["operationNode configuration"]
            SourceNodes["sourceNodes from connections"]
            Connections["filtered connections"]
        end
        
        subgraph "Generation Context"
            Origin["origin: { type: 'studio', workspaceId }"]
            GenerationContext["GenerationContext"]
            FileResolver["fileResolver"]
            ContentResolver["generationContentResolver"]
        end
        
        subgraph "AI Provider Integration"
            GenerateImage["generateImage"]
            GenerateText["generateText"]
            ProviderSpecific["Provider-specific generation"]
        end
    end
    
    GenerateButton --> UsageLimitCheck
    GenerateButton --> PromptValidation
    GenerateButton --> ConnectedSources
    
    UsageLimitCheck --> CreateRunner
    PromptValidation --> CreateRunner
    ConnectedSources --> CreateRunner
    
    CreateRunner --> OperationNode
    CreateRunner --> SourceNodes
    CreateRunner --> Connections
    
    CreateRunner --> Origin
    Origin --> GenerationContext
    GenerationContext --> FileResolver
    GenerationContext --> ContentResolver
    
    GenerationContext --> GenerateImage
    GenerationContext --> GenerateText
    GenerateImage --> ProviderSpecific
    GenerateText --> ProviderSpecific
```

The validation system prevents execution when usage limits are reached, prompts are empty, or required configurations are missing, providing appropriate user feedback through toast notifications.

**Sources:** [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/index.tsx:57-88](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/index.tsx:97-128](), [packages/giselle/src/engine/generations/generate-image.ts:34-133](), [internal-packages/workflow-designer-ui/src/editor/lib/validate-prompt:14]()

---

# Page: Toolbar and Node Creation Flow

# Toolbar and Node Creation Flow

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/playground/app/globals.css](apps/playground/app/globals.css)
- [apps/playground/app/layout.tsx](apps/playground/app/layout.tsx)
- [apps/studio.giselles.ai/app/globals.css](apps/studio.giselles.ai/app/globals.css)
- [apps/studio.giselles.ai/app/layout.tsx](apps/studio.giselles.ai/app/layout.tsx)
- [apps/studio.giselles.ai/tailwind.config.ts](apps/studio.giselles.ai/tailwind.config.ts)
- [internal-packages/workflow-designer-ui/src/editor/node/node.tsx](internal-packages/workflow-designer-ui/src/editor/node/node.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/vector-store/index.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/vector-store/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/tool/floating-node/component.tsx](internal-packages/workflow-designer-ui/src/editor/tool/floating-node/component.tsx)
- [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/state.tsx](internal-packages/workflow-designer-ui/src/editor/tool/toolbar/state.tsx)
- [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx](internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx)
- [internal-packages/workflow-designer-ui/src/editor/tool/types.ts](internal-packages/workflow-designer-ui/src/editor/tool/types.ts)
- [internal-packages/workflow-designer-ui/src/icons/node/file-node.tsx](internal-packages/workflow-designer-ui/src/icons/node/file-node.tsx)
- [internal-packages/workflow-designer-ui/src/icons/node/image-generation-node.tsx](internal-packages/workflow-designer-ui/src/icons/node/image-generation-node.tsx)
- [internal-packages/workflow-designer-ui/src/icons/node/index.tsx](internal-packages/workflow-designer-ui/src/icons/node/index.tsx)
- [internal-packages/workflow-designer-ui/src/new-editor/components/node/node.tsx](internal-packages/workflow-designer-ui/src/new-editor/components/node/node.tsx)
- [internal-packages/workflow-designer-ui/src/ui/node/node-handle-dot.tsx](internal-packages/workflow-designer-ui/src/ui/node/node-handle-dot.tsx)
- [internal-packages/workflow-designer-ui/src/ui/node/node-input-label.tsx](internal-packages/workflow-designer-ui/src/ui/node/node-input-label.tsx)

</details>



## Purpose and Scope

This document describes the toolbar component and the node creation workflow in the Workflow Designer UI. The toolbar provides the primary interface for users to add nodes to the workflow canvas through a multi-step selection process. It manages tool state, displays contextual popovers for node type selection, and handles the floating preview system that follows the mouse cursor during node placement.

For information about how nodes are rendered on the canvas after creation, see [Node Rendering and Visual System](#5.2). For details on node configuration after placement, see [Properties Panels and Node Configuration](#5.3).

## Architecture Overview

The toolbar system consists of three main components:

| Component | Purpose | Location |
|-----------|---------|----------|
| `Toolbar` | Main UI component with tool buttons and popovers | [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx]() |
| `ToolbarContext` | State management for selected tool | [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/state.tsx]() |
| `FloatingNodePreview` | Preview that follows mouse during placement | [internal-packages/workflow-designer-ui/src/editor/tool/floating-node/component.tsx]() |

The toolbar is positioned at the top of the editor and provides access to all node creation tools through a state-machine-based selection flow.

**Architecture Diagram**

```mermaid
graph TB
    User["User Action"]
    Toolbar["Toolbar Component<br/>(toolbar.tsx)"]
    Context["ToolbarContext<br/>(state.tsx)"]
    Popovers["Radix Popovers<br/>(inline in toolbar.tsx)"]
    FloatingPreview["FloatingNodePreview<br/>(floating-node/component.tsx)"]
    Canvas["ReactFlow Canvas"]
    
    User -->|"Click tool button"| Toolbar
    Toolbar -->|"setSelectedTool()"| Context
    Context -->|"selectedTool state"| Toolbar
    Toolbar -->|"open conditionally"| Popovers
    Popovers -->|"setSelectedTool(addNodeTool)"| Context
    Context -->|"tool.action === 'addNode'"| FloatingPreview
    FloatingPreview -->|"follows mouse"| User
    User -->|"click canvas"| Canvas
    Canvas -->|"reset()"| Context
```

Sources: [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:1-1302](), [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/state.tsx:1-122](), [internal-packages/workflow-designer-ui/src/editor/tool/floating-node/component.tsx:1-21]()

## Tool State Machine

The toolbar operates as a state machine where the selected tool determines both UI state and available actions. The tool state is managed by `ToolbarContext` and stored as a `Tool` union type.

**Tool Type Hierarchy**

```mermaid
graph TD
    Tool["Tool<br/>(union type)"]
    
    Tool --> MoveTool["MoveTool<br/>action: 'move'<br/>category: 'move'"]
    Tool --> SelectTools["Selection Tools<br/>category: 'edit'"]
    Tool --> AddNodeTool["AddNodeTool<br/>action: 'addNode'<br/>category: 'edit'<br/>node: Node"]
    
    SelectTools --> SelectLanguageModelTool["SelectLanguageModelTool<br/>action: 'selectLanguageModel'"]
    SelectTools --> SelectSourceCategoryTool["SelectSourceCategoryTool<br/>action: 'selectSourceCategory'"]
    SelectTools --> SelectTriggerTool["SelectTriggerTool<br/>action: 'selectTrigger'"]
    SelectTools --> SelectActionTool["SelectActionTool<br/>action: 'selectAction'"]
    SelectTools --> SelectRetrievalCategoryTool["SelectRetrievalCategoryTool<br/>action: 'selectRetrievalCategory'"]
    SelectTools --> SelectFileNodeCategoryTool["SelectFileNodeCategoryTool<br/>action: 'selectFileNodeCategory'"]
```

Sources: [internal-packages/workflow-designer-ui/src/editor/tool/types.ts:1-71]()

### Tool State Transitions

The state machine transitions follow this pattern:

1. **Initial State**: `MoveTool` (default)
2. **Selection State**: User clicks a toolbar button → one of the `Select*Tool` types
3. **Preview State**: User selects from popover → `AddNodeTool` with node data
4. **Placement**: User clicks canvas → back to `MoveTool` (via `reset()`)

**State Transition Functions**

| Function | Returns | Purpose |
|----------|---------|---------|
| `moveTool()` | `MoveTool` | Default state for canvas interaction |
| `selectLanguageModelTool()` | `SelectLanguageModelTool` | Opens model selection popover |
| `selectSourceCategoryTool()` | `SelectSourceCategoryTool` | Opens import node popover |
| `selectTriggerTool()` | `SelectTriggerTool` | Opens trigger selection popover |
| `selectActionTool()` | `SelectActionTool` | Opens action selection popover |
| `addNodeTool(node)` | `AddNodeTool` | Enters placement mode with node |

Sources: [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/state.tsx:58-113]()

## Toolbar Component Structure

The `Toolbar` component renders a horizontal bar with five main tool groups, each implemented as a `ToggleGroup.Item` from Radix UI.

**Toolbar Component Hierarchy**

```mermaid
graph TB
    Toolbar["Toolbar<br/>(toolbar.tsx:85-1302)"]
    GlassSurface["GlassSurfaceLayers<br/>(styling)"]
    ToggleGroupRoot["ToggleGroup.Root<br/>(Radix UI)"]
    
    Toolbar --> GlassSurface
    Toolbar --> ToggleGroupRoot
    
    ToggleGroupRoot --> TriggerButton["Trigger Button<br/>ZapIcon<br/>value='selectTrigger'"]
    ToggleGroupRoot --> ImportButton["Import Button<br/>FolderOpenIcon<br/>value='selectSourceCategory'"]
    ToggleGroupRoot --> GenerationButton["Generation Button<br/>SparklesIcon<br/>value='selectLanguageModel'"]
    ToggleGroupRoot --> RetrievalButton["Retrieval Button<br/>DatabaseZapIcon<br/>value='selectRetrievalCategory'"]
    ToggleGroupRoot --> ActionButton["Action Button<br/>RocketIcon<br/>value='selectAction'"]
    
    TriggerButton --> TriggerPopover["Popover: Triggers"]
    ImportButton --> ImportPopover["Popover: Import Nodes"]
    GenerationButton --> GenerationPopover["Popover: Language Models"]
    RetrievalButton --> RetrievalPopover["Popover: Query Nodes"]
    ActionButton --> ActionPopover["Popover: Actions"]
```

Sources: [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:85-246](), [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:327-431](), [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:433-846]()

### Toolbar Button Configuration

The toolbar uses CSS variables for consistent sizing and positioning:

- `--language-model-toggle-group-popover-width`: Width of the model selection popover
- `--language-model-detail-panel-width`: Width of the model details panel

Each button in the `ToggleGroup` has:
- A `value` attribute matching the tool action name
- A `data-tool` attribute for styling
- A tooltip with keyboard shortcut (via `TooltipAndHotkey`)
- Conditional popover rendering based on `selectedTool.action`

Sources: [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:207-325]()

## Node Creation Flow

The node creation process involves multiple steps from initial button click to final placement on the canvas.

**Node Creation Sequence Diagram**

```mermaid
sequenceDiagram
    participant User
    participant Toolbar
    participant Context as ToolbarContext
    participant Popover
    participant Registry as node-registry
    participant FloatingPreview
    participant Canvas as ReactFlow Canvas
    
    User->>Toolbar: Click "Import" button
    Toolbar->>Context: setSelectedTool(selectSourceCategoryTool())
    Context-->>Toolbar: selectedTool updated
    Toolbar->>Popover: Render Import popover
    
    User->>Popover: Select "Plain Text"
    Popover->>Registry: createTextNode()
    Registry-->>Popover: TextNode instance
    Popover->>Context: setSelectedTool(addNodeTool(node))
    Context-->>Toolbar: selectedTool.action === "addNode"
    Toolbar->>FloatingPreview: Render with node
    
    loop Mouse movement
        FloatingPreview->>FloatingPreview: Update position
    end
    
    User->>Canvas: Click at position
    Canvas->>Canvas: addNode(node, position)
    Canvas->>Context: reset()
    Context-->>Toolbar: selectedTool = moveTool()
    FloatingPreview->>FloatingPreview: Unmount
```

Sources: [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:327-431](), [internal-packages/workflow-designer-ui/src/editor/tool/floating-node/component.tsx:5-20]()

### Step-by-Step Flow

1. **Tool Selection**: User clicks a toolbar button (e.g., "Import")
   - `onValueChange` handler receives the tool action string
   - Calls `setSelectedTool()` with appropriate `Select*Tool` type
   - Location: [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:217-240]()

2. **Popover Display**: Toolbar conditionally renders popover
   - Checks `selectedTool?.action === "selectSourceCategory"`
   - Renders `Popover.Root` with `open={true}`
   - Location: [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:335-430]()

3. **Node Type Selection**: User selects specific node type
   - Popover's `ToggleGroup.onValueChange` handler fires
   - Calls node creation function from `@giselles-ai/node-registry`
   - Example: `createTextNode()`, `createFileNode(category)`
   - Wraps result in `addNodeTool(node)`
   - Location: [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:369-399]()

4. **Preview Mode**: Floating preview appears
   - Component conditionally renders when `tool.action === "addNode"`
   - Tracks mouse position via `useMousePosition` hook
   - Renders `NodeComponent` with `preview={true}` prop
   - Location: [internal-packages/workflow-designer-ui/src/editor/tool/floating-node/component.tsx:5-20]()

5. **Node Placement**: User clicks canvas
   - Canvas click handler receives position and current tool
   - If tool is `AddNodeTool`, adds node at clicked position
   - Calls `reset()` to return to `MoveTool` state
   - Location: [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/state.tsx:33-35]()

Sources: [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:85-431](), [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/state.tsx:26-56]()

## Floating Node Preview System

The floating preview provides visual feedback during node placement by rendering a semi-transparent node that follows the mouse cursor.

**FloatingNodePreview Implementation**

```mermaid
graph LR
    AddNodeTool["AddNodeTool<br/>(contains Node)"]
    FloatingNode["FloatingNodePreview<br/>(component.tsx)"]
    MouseHook["useMousePosition<br/>(state.tsx)"]
    NodeComp["NodeComponent<br/>(node.tsx)"]
    
    AddNodeTool -->|"node prop"| FloatingNode
    FloatingNode -->|"calls"| MouseHook
    MouseHook -->|"returns { x, y }"| FloatingNode
    FloatingNode -->|"renders with preview=true"| NodeComp
    
    FloatingNode -->|"style: transform"| Transform["translate(x, y)"]
```

Sources: [internal-packages/workflow-designer-ui/src/editor/tool/floating-node/component.tsx:1-21]()

### Preview Component Details

The `FloatingNodePreview` component:
- Accepts a `node: Node` prop
- Uses `useMousePosition()` hook to track cursor position
- Renders in a fixed-position container with `pointer-events-none`
- Applies CSS transform for positioning: `translate(${x}px, ${y}px)`
- Sets node width to `180px` (matches minimum node width)
- Passes `preview={true}` to `NodeComponent` for styling

The `preview` prop on `NodeComponent` triggers visual changes:
- Sets `opacity-50` class
- Disables rendering of input/output handles
- Location: [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:260-307]()

Sources: [internal-packages/workflow-designer-ui/src/editor/tool/floating-node/component.tsx:5-20](), [internal-packages/workflow-designer-ui/src/editor/node/node.tsx:147-638]()

## Tool Selection Popovers

Each toolbar button opens a specialized popover for selecting node subtypes. The popovers use Radix UI's `Popover` component with custom styling.

### Popover Common Structure

All popovers follow this pattern:

```tsx
{selectedTool?.action === "selectTrigger" && (
  <Popover.Root open={true}>
    <Popover.Anchor />
    <Popover.Portal>
      <Popover.Content
        className="relative rounded-[8px] px-[8px] py-[8px]"
        sideOffset={42}
      >
        <GlassSurfaceLayers />
        <ToggleGroup.Root onValueChange={...}>
          {/* Options */}
        </ToggleGroup.Root>
      </Popover.Content>
    </Popover.Portal>
  </Popover.Root>
)}
```

Sources: [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:250-324]()

### Trigger Selection Popover

The trigger popover renders available trigger types from `triggerRegistry`:

**Trigger Options**

| Value | Display Name | Icon | Function Call |
|-------|--------------|------|---------------|
| `"appEntry"` | App Entry Node | `TriggerIcon` | `createAppEntryNode()` |
| `"manual"` | Manual Trigger | `TriggerIcon` | `createTriggerNode("manual")` |
| `"github"` | GitHub Trigger | `GitHubIcon` | `createTriggerNode("github")` |

The popover iterates over `triggerRegistry.map()` to render available triggers dynamically. The "App Entry Node" option is only shown when the `stage` feature flag is enabled.

Sources: [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:250-324]()

### Import (Source Category) Popover

The import popover provides options for creating input nodes:

**Import Node Options**

| Value | Display Name | Icon | Node Type | Function Call |
|-------|--------------|------|-----------|---------------|
| `"text"` | Plain Text | `PromptIcon` | Text | `createTextNode()` |
| `"pdf"` | PDF Upload | `PdfFileIcon` | File | `createFileNode("pdf")` |
| `"image"` | Image Upload | `PictureIcon` | File | `createFileNode("image")` |
| `"textFile"` | Text Upload | `TextFileIcon` | File | `createFileNode("text")` |
| `"documentVectorStore"` | Document Vector Store | `DocumentVectorStoreIcon` | VectorStore | `createDocumentVectorStoreNode()` |
| `"githubVectorStore"` | GitHub Vector Store | `GitHubIcon` | VectorStore | `createGitHubVectorStoreNode()` |

Sources: [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:335-430]()

### Generation (Language Model) Popover

The generation popover is the most complex, featuring:
- Search functionality
- Category tabs (All, Text, Image, Video, Audio)
- Recommended models section
- Model details panel (separate popover)
- Pro plan overlay for restricted models

**Language Model Popover Features**

```mermaid
graph TB
    Popover["Language Model Popover"]
    SearchInput["Search Input<br/>(filters models)"]
    CategoryTabs["Category Tabs<br/>(All/Text/Image/Video/Audio)"]
    RecommendedSection["Recommended Models<br/>(tier-based)"]
    ModelList["Filtered Model List<br/>(scrollable)"]
    DetailsPanel["Model Details Panel<br/>(hover-triggered)"]
    
    Popover --> SearchInput
    Popover --> CategoryTabs
    Popover --> RecommendedSection
    Popover --> ModelList
    Popover --> DetailsPanel
    
    SearchInput -->|"updates searchQuery"| ModelList
    CategoryTabs -->|"updates selectedCategory"| ModelList
    ModelList -->|"onMouseEnter"| DetailsPanel
    
    DetailsPanel --> Capabilities["Capability Icons<br/>(text/image/pdf/etc)"]
    DetailsPanel --> ProOverlay["Pro Plan Overlay<br/>(free users only)"]
```

Sources: [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:441-845]()

#### Model Search and Filtering

The generation popover implements multi-stage filtering:

1. **Provider Filtering**: Only models from enabled LLM providers
   - Checks `llmProviders.includes(model.provider)`
   - Location: [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:99-111]()

2. **Search Filtering**: Text search by model ID or provider
   - Function: `filterModelsBySearch(model, searchQuery)`
   - Location: [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:113-115]()

3. **Category Filtering**: Filter by capability (text/image)
   - Function: `filterModelsByCategory(model, selectedCategory)`
   - Uses `hasCapability(model, Capability.TextGeneration)` checks
   - Location: [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:143-145]()

4. **Auto-Category Selection**: Automatically adjusts category based on search results
   - If only text models found → select "Text" category
   - If only image models found → select "Image" category
   - Location: [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:118-138]()

#### Recommended Models Section

The toolbar displays tier-appropriate recommended models:

```typescript
const isFreeUser = userTier === Tier.enum.free;
const openaiModels = getAvailableModels(
  isFreeUser ? ["gpt-5-nano"] : ["gpt-5"],
  "openai",
  llmProviders,
  availableLanguageModels,
);
// Similar for anthropic and google
```

Free tier users see: `gpt-5-nano`, `claude-haiku-4-5`, `gemini-2.5-flash-lite`
Pro tier users see: `gpt-5`, `claude-sonnet-4-5`, `gemini-2.5-pro-exp`

Sources: [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:148-182]()

#### Model Details Panel

A secondary popover displays detailed information when hovering over a model:
- Model ID and provider icon
- Capability badges (Generate Text, Generate Image, Input PDF, etc.)
- Pro plan overlay for restricted models (free users only)

The panel uses separate hover state management:
- `handleModelHover`: Sets `languageModelMouseHovered`
- `handleCapabilityPanelEnter/Leave`: Prevents unwanted hiding
- Location: [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:585-844]()

Sources: [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:585-845]()

### Action Selection Popover

The action popover renders available actions from `actionRegistry`:

```typescript
{actionRegistry.map((actionEntry) => (
  <ToggleGroup.Item
    key={actionEntry.provider}
    value={actionEntry.provider}
    data-tool
  >
    {/* Icon based on provider */}
    <p>{actionNodeDefaultName(actionEntry.provider)}</p>
  </ToggleGroup.Item>
))}
```

When a provider is selected, calls `createActionNode(provider)` and wraps in `addNodeTool()`.

Sources: [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:847-1126]()

### Query (Retrieval Category) Popover

The query popover provides options for database query nodes:

```typescript
<ToggleGroup.Item value="query" data-tool>
  <DatabaseZapIcon />
  <p>Query</p>
</ToggleGroup.Item>
```

Calls `createQueryNode()` when selected.

Sources: [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:1128-1234]()

## Keyboard Shortcuts

The toolbar supports keyboard shortcuts for quick tool access. Shortcuts are displayed in tooltips using the `TooltipAndHotkey` component:

| Shortcut | Tool | Action |
|----------|------|--------|
| `t` | Trigger | Opens trigger selection popover |
| `i` | Import | Opens source category popover |
| `g` | Generation | Opens language model popover |

The shortcuts are implemented at the application level and call `setSelectedTool()` directly with the appropriate tool state.

Sources: [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:247-249](), [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:332-334](), [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:438-440]()

## Integration with Canvas

The toolbar integrates with the ReactFlow canvas through the tool state. When `selectedTool.action === "addNode"`, the canvas click handler:

1. Retrieves the `node` from the `AddNodeTool` state
2. Calculates the canvas position from the click event
3. Calls the appropriate node addition function (via Zustand store)
4. Calls `reset()` on the toolbar context to return to `MoveTool`

The canvas also handles:
- Escape key to cancel placement (calls `reset()`)
- Right-click to cancel placement
- Cursor style changes based on tool state

This integration is typically implemented in the canvas component that consumes `useToolbar()`.

Sources: [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/state.tsx:18-56]()

## Styling and Theming

The toolbar uses a consistent glass-morphism design pattern through `GlassSurfaceLayers`:

**Styling Layers**

| Layer | Purpose | CSS Variables |
|-------|---------|---------------|
| Base Fill | Semi-transparent background | `color-mix(in srgb, var(--color-background) 50%, transparent)` |
| Border | Subtle outline | `borderStyle="solid"` |
| Blur | Backdrop blur effect | `backdrop-blur-[4px]` or `backdrop-blur-lg` |

Tool buttons use consistent spacing:
- Padding: `px-[4px]` on toolbar, `px-[8px] py-[4px]` on popover items
- Gap: `gap-[12px]` between toolbar buttons, `gap-[8px]` in popovers
- Border radius: `rounded-[12px]` for toolbar, `rounded-[8px]` for popovers

Icon sizing:
- Toolbar icons: `w-[24px] h-[24px]`
- Popover icons: `w-[20px] h-[20px]` or `size-[20px]`

Sources: [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:199-206](), [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:258-274]()

## Node Registry Integration

The toolbar relies heavily on the `@giselles-ai/node-registry` package for node creation:

**Node Creation Functions**

| Function | Package | Returns | Purpose |
|----------|---------|---------|---------|
| `createTextNode()` | `@giselles-ai/node-registry` | `TextNode` | Plain text input |
| `createFileNode(category)` | `@giselles-ai/node-registry` | `FileNode` | PDF, image, or text file |
| `createGitHubVectorStoreNode()` | `@giselles-ai/node-registry` | `VectorStoreNode` | GitHub repository index |
| `createDocumentVectorStoreNode()` | `@giselles-ai/node-registry` | `VectorStoreNode` | Document vector store |
| `createTriggerNode(provider)` | `@giselles-ai/node-registry` | `TriggerNode` | Manual or GitHub trigger |
| `createAppEntryNode()` | `@giselles-ai/node-registry` | `AppEntryNode` | Stage application entry |
| `createActionNode(provider)` | `@giselles-ai/node-registry` | `ActionNode` | Environment action |
| `createQueryNode()` | `@giselles-ai/node-registry` | `QueryNode` | Database query |
| `createWebPageNode()` | `@giselles-ai/node-registry` | `WebPageNode` | Web page import |

For generation nodes, the toolbar creates nodes using language model configuration:
- Text generation: Uses `languageModels` array from `@giselles-ai/language-model`
- Image generation: Uses model IDs like `"flux-1.1-pro"`, `"recraft-v3"`

Sources: [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:1-83]()

---

# Page: Generation Execution and Results Display

# Generation Execution and Results Display

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [internal-packages/ui/components/prompt-editor.tsx](internal-packages/ui/components/prompt-editor.tsx)
- [internal-packages/workflow-designer-ui/src/editor/index.tsx](internal-packages/workflow-designer-ui/src/editor/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/app-entry-node-properties-panel/index.ts](internal-packages/workflow-designer-ui/src/editor/properties-panel/app-entry-node-properties-panel/index.ts)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/file-node-properties-panel/file-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/file-node-properties-panel/file-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/file-node-properties-panel/index.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/file-node-properties-panel/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/generation-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/generation-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/index.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/prompt-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/prompt-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/index.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/generation-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/generation-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/index.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/query-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/query-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/generation-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/generation-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/index.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/prompt-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/prompt-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-node-properties-panel/index.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/text-node-properties-panel/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/index.ts](internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/index.ts)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/panel-spacing.ts](internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/panel-spacing.ts)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/properties-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/properties-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/resizable-section.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/resizable-section.tsx)
- [internal-packages/workflow-designer-ui/src/ui/generation-view.tsx](internal-packages/workflow-designer-ui/src/ui/generation-view.tsx)
- [internal-packages/workflow-designer-ui/src/ui/image-generation-loading.tsx](internal-packages/workflow-designer-ui/src/ui/image-generation-loading.tsx)
- [internal-packages/workflow-designer-ui/src/ui/query-result-view.tsx](internal-packages/workflow-designer-ui/src/ui/query-result-view.tsx)
- [packages/text-editor/src/react/component.tsx](packages/text-editor/src/react/component.tsx)

</details>



## Purpose and Scope

This document describes how generations are triggered from the Workflow Designer UI and how their results are displayed to users. It covers the client-side execution flow, the `useNodeGenerations` hook that manages generation lifecycle, and the display components that render text, image, and query results in real-time.

For information about the server-side generation execution and engine orchestration, see [Generation Pipeline and Lifecycle](#2.2). For details on Act execution in production, see [Stage System and Act Execution](#6.1.2).

## Generation Execution Architecture

The generation execution system follows a client-initiated, server-executed model where the UI triggers generation requests and subscribes to real-time updates.

```mermaid
graph TB
    subgraph "UI Layer"
        PropPanel["Properties Panel<br/>(TextGenerationNodePropertiesPanel)"]
        GenButton["Generate Button<br/>(GenerateCtaButton)"]
        Hook["useNodeGenerations Hook"]
    end
    
    subgraph "Generation Management"
        CreateRunner["createAndStartGenerationRunner"]
        IsGenerating["isGenerating state"]
        CurrentGen["currentGeneration state"]
        StopRunner["stopGenerationRunner"]
    end
    
    subgraph "Display Components"
        GenPanel["GenerationPanel"]
        GenView["GenerationView"]
        QueryView["QueryResultView"]
    end
    
    subgraph "Engine Integration"
        EngineAPI["GiselleEngine API"]
        Storage["Storage Layer"]
        Stream["Streaming Updates"]
    end
    
    PropPanel --> GenButton
    PropPanel --> Hook
    GenButton --> CreateRunner
    Hook --> CreateRunner
    Hook --> IsGenerating
    Hook --> CurrentGen
    Hook --> StopRunner
    
    CreateRunner --> EngineAPI
    StopRunner --> EngineAPI
    
    EngineAPI --> Stream
    Stream --> CurrentGen
    EngineAPI --> Storage
    Storage --> CurrentGen
    
    GenPanel --> CurrentGen
    GenPanel --> GenView
    GenPanel --> QueryView
    
    style Hook fill:#e1ffe1
    style CreateRunner fill:#fff4e1
    style GenView fill:#e1f5ff
```

**Sources:**
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/index.tsx:1-290]()
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/index.tsx:1-248]()

## useNodeGenerations Hook

The `useNodeGenerations` hook is the primary interface for managing generation execution from the UI. It provides methods to create, start, stop generations and track their state.

### Hook Interface

```typescript
const {
    createAndStartGenerationRunner,
    isGenerating,
    stopGenerationRunner,
    currentGeneration,
} = useNodeGenerations({
    nodeId: node.id,
    origin: { type: "studio", workspaceId: data.id },
});
```

### Hook Return Values

| Property | Type | Description |
|----------|------|-------------|
| `createAndStartGenerationRunner` | Function | Initiates a new generation with context |
| `isGenerating` | boolean | Whether a generation is currently running |
| `stopGenerationRunner` | Function | Cancels the current generation |
| `currentGeneration` | Generation \| undefined | The most recent generation object |

### Generation Context

When calling `createAndStartGenerationRunner`, the UI must provide:

```typescript
{
    origin: {
        type: "studio",
        workspaceId: data.id,
    },
    operationNode: node,           // The node being executed
    sourceNodes,                   // Connected input nodes
    connections: data.connections  // Relevant connections
}
```

**Sources:**
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/index.tsx:38-46]()
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/index.tsx:98-108]()

## Execution Flow

### Text Generation Execution

```mermaid
sequenceDiagram
    participant User
    participant PropPanel as "TextGenerationNodePropertiesPanel"
    participant Hook as "useNodeGenerations"
    participant Validate as "Validation Logic"
    participant Engine as "GiselleEngine"
    participant GenPanel as "GenerationPanel"
    participant GenView as "GenerationView"
    
    User->>PropPanel: Click Generate Button
    PropPanel->>Validate: Check isEmpty(prompt)
    alt Prompt is empty
        Validate-->>User: Show error toast
    else Prompt valid
        Validate->>Hook: createAndStartGenerationRunner(context)
        Hook->>Engine: POST /api/generation
        Engine-->>Hook: Generation created (status: created)
        Hook->>PropPanel: Update isGenerating = true
        PropPanel->>GenPanel: Render with currentGeneration
        GenPanel->>GenView: Display status
        GenView-->>User: Show "Generating..." spinner
        
        loop Streaming chunks
            Engine-->>Hook: Stream text chunks
            Hook->>GenPanel: Update currentGeneration
            GenPanel->>GenView: Re-render with new content
            GenView-->>User: Show partial results
        end
        
        Engine-->>Hook: Generation complete
        Hook->>PropPanel: Update isGenerating = false
        PropPanel->>GenPanel: Render final result
        GenPanel->>GenView: Display complete generation
        GenView-->>User: Show full result with metrics
    end
```

### Execution Steps

1. **Validation Phase** - [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/index.tsx:88-96]()
   - Check if prompt is empty using `isPromptEmpty`
   - Verify usage limits not reached
   - Show error toasts if validation fails

2. **Context Building** - [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/index.tsx:98-108]()
   - Gather operation node configuration
   - Collect connected source nodes
   - Filter relevant connections

3. **Execution Initiation** - Hook invokes `createAndStartGenerationRunner`
   - Sends request to engine
   - Receives generation ID
   - Begins streaming subscription

4. **Real-time Updates** - Generation state flows back through hook
   - `currentGeneration` updates with each chunk
   - React re-renders display components
   - User sees progressive results

**Sources:**
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/index.tsx:88-117]()
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/index.tsx:51-77]()

## Results Display System

### Generation View Component

The `GenerationView` component renders the output of text generations, handling multiple message types and streaming states.

```mermaid
graph TB
    subgraph "GenerationView"
        StatusCheck["Check generation.status"]
        Failed["FailedView<br/>Show error message"]
        Running["RunningView<br/>Show spinner"]
        Completed["CompletedView<br/>Render outputs"]
    end
    
    subgraph "Completed Rendering"
        Images["Generated Images<br/>(ImageCard grid)"]
        Messages["Assistant Messages<br/>(Text + Reasoning)"]
        Lightbox["Lightbox<br/>(Image zoom)"]
    end
    
    subgraph "Message Parts"
        TextPart["Text Part<br/>MemoizedMarkdown"]
        ReasonPart["Reasoning Part<br/>Accordion"]
        ToolPart["Tool Call Part<br/>(future)"]
    end
    
    StatusCheck --> Failed
    StatusCheck --> Running
    StatusCheck --> Completed
    
    Completed --> Images
    Completed --> Messages
    Images --> Lightbox
    
    Messages --> TextPart
    Messages --> ReasonPart
    Messages --> ToolPart
    
    style GenerationView fill:#e1ffe1
    style Completed fill:#fff4e1
```

### Status-Based Rendering

The component adapts its display based on `generation.status`:

| Status | Display Behavior |
|--------|------------------|
| `failed` | Shows error message and generation ID |
| `created`, `queued` | Shows animated spinner |
| `running` | Shows spinner (previously showed per-image placeholders) |
| `completed` | Renders full outputs and messages |
| `cancelled` | Renders partial results |

**Sources:**
- [internal-packages/workflow-designer-ui/src/ui/generation-view.tsx:85-268]()
- [internal-packages/workflow-designer-ui/src/ui/generation-view.tsx:115-143]()

### Message Part Rendering

Text generations produce messages with different part types that require specialized rendering:

#### Text Parts
Plain text content rendered with Markdown support:
```typescript
case "text":
    return (
        <div className="markdown-renderer">
            <MemoizedMarkdown content={part.text} />
        </div>
    );
```

#### Reasoning Parts
Collapsible reasoning process display using Radix UI Accordion:
- Shows shimmer animation while active (last part)
- Collapsed by default when complete
- Displays thinking process in italic text
- Includes left border for visual distinction

**Sources:**
- [internal-packages/workflow-designer-ui/src/ui/generation-view.tsx:175-248]()
- [internal-packages/workflow-designer-ui/src/ui/generation-view.tsx:180-232]()

### Image Generation Display

Image outputs are rendered in a horizontal scrollable grid with interaction capabilities:

```typescript
{generation.outputs.map((output) => {
    if (output.type !== "generated-image") return null;
    return (
        <div className="flex gap-[12px] pt-[8px] overflow-x-auto">
            {output.contents.map((content) => (
                <ImageCard
                    src={`${client.basePath}${content.pathname}`}
                    onDownload={() => { /* download logic */ }}
                    onZoom={() => setLightboxImage(pathname)}
                />
            ))}
        </div>
    );
})}
```

The `ImageCard` component provides:
- Thumbnail display with fixed height
- Download button overlay
- Zoom button for lightbox view
- Responsive hover states

**Sources:**
- [internal-packages/workflow-designer-ui/src/ui/generation-view.tsx:146-174]()
- [internal-packages/workflow-designer-ui/src/ui/generation-view.tsx:262-265]()

## Query Results Display

Query nodes produce specialized output that requires a different display component: `QueryResultView`.

### Query Result Structure

```mermaid
graph TB
    subgraph "QueryResultView"
        Check["Check generation.status"]
        TabNav["Data Source Tabs"]
        Content["Query Result Content"]
    end
    
    subgraph "Tab Navigation"
        GitHubTab["GitHub Source Tab<br/>repo/contentType"]
        DocTab["Document Source Tab<br/>store name/status"]
        TabState["activeTabIndex state"]
    end
    
    subgraph "Result Card"
        Records["Record List"]
        ChunkCard["Chunk Card<br/>content + metadata"]
        ScoreInd["Score Indicator<br/>similarity score"]
        PRContext["PR Context Display<br/>(if GitHub PR)"]
    end
    
    Check --> TabNav
    Check --> Content
    TabNav --> GitHubTab
    TabNav --> DocTab
    GitHubTab --> TabState
    DocTab --> TabState
    TabState --> Content
    
    Content --> Records
    Records --> ChunkCard
    ChunkCard --> ScoreInd
    ChunkCard --> PRContext
    
    style QueryResultView fill:#e1ffe1
    style TabNav fill:#fff4e1
    style ChunkCard fill:#e1f5ff
```

### Data Source Tabs

Each vector store source that contributed results gets its own tab:

```typescript
function DataSourceTab({
    result,
    isActive,
    onClick,
    documentStoreMap,
}) {
    const displayInfo = getDataSourceDisplayInfo(result, documentStoreMap);
    const recordCount = result.records?.length || 0;
    
    return (
        <button onClick={onClick} className={isActive ? "active" : ""}>
            <Icon /> {/* GitHubIcon or DocumentVectorStoreIcon */}
            <div>
                <span>{displayInfo.line1}</span>
                <span>{displayInfo.line2}</span>
            </div>
            <span>{recordCount}</span>
        </button>
    );
}
```

The display information is computed based on source type:
- **GitHub sources**: Shows `owner/repo` and content type (Pull Requests/Code)
- **Document stores**: Shows store name and ingestion status

**Sources:**
- [internal-packages/workflow-designer-ui/src/ui/query-result-view.tsx:279-332]()
- [internal-packages/workflow-designer-ui/src/ui/query-result-view.tsx:240-277]()

### Chunk Display

Each retrieved chunk is rendered in a card with expandable content:

```typescript
<div className="space-y-[12px]">
    {records.map((record, recordIndex) => (
        <div className="bg-surface/5 rounded-[8px] p-[12px]">
            <div className="flex items-center justify-between">
                <span>Chunk #{record.chunkIndex}</span>
                <ScoreIndicator score={record.score} />
            </div>
            
            <ContentPreview
                content={record.chunkContent}
                isExpanded={expandedRecords.has(recordIndex)}
                onToggle={() => toggleRecord(recordIndex)}
            />
            
            <PRContextDisplay metadata={record.metadata} />
            <details>Metadata</details>
        </div>
    ))}
</div>
```

#### Score Indicator

Visual representation of similarity score with color coding:
- **> 0.8**: Green (high relevance)
- **> 0.5**: Yellow (medium relevance)
- **≤ 0.5**: Gray (low relevance)

**Sources:**
- [internal-packages/workflow-designer-ui/src/ui/query-result-view.tsx:334-433]()
- [internal-packages/workflow-designer-ui/src/ui/query-result-view.tsx:31-60]()

### Pull Request Context

For GitHub PR results, additional context is displayed:

```typescript
function PRContextDisplay({ metadata, additional }) {
    const prNumber = metadata.prNumber;
    const contentType = metadata.contentType; // comment | diff | title_body
    const prContext = additional?.prContext;
    
    const [title, ...bodyParts] = prContext.split("\n\n");
    
    return (
        <div className="bg-blue-500/10 rounded-[6px] border border-blue-500/20">
            <GitPullRequestIcon />
            <span>PR #{prNumber}</span>
            <span>{contentTypeLabel}</span>
            <p>{title}</p>
            {/* Expandable body */}
        </div>
    );
}
```

**Sources:**
- [internal-packages/workflow-designer-ui/src/ui/query-result-view.tsx:105-198]()
- [internal-packages/workflow-designer-ui/src/ui/query-result-view.tsx:17-19]()

## Generation Panel Containers

Each node type has a dedicated `GenerationPanel` component that wraps the appropriate view component and provides consistent UI chrome.

### Text Generation Panel

```mermaid
graph TB
    subgraph "GenerationPanel<br/>(TextGeneration)"
        Empty["Empty State<br/>No generations yet"]
        Container["Panel Container<br/>min-h-250px"]
        Header["Panel Header<br/>status + metrics"]
        Content["Panel Content<br/>overflow-y-auto"]
        Actions["Action Buttons<br/>expand/copy"]
    end
    
    subgraph "Header Sections"
        Status["Status Text<br/>Generating.../Result/Error"]
        Model["Model Info<br/>provider + modelId"]
        Metrics["Usage Metrics<br/>time/tokens"]
    end
    
    subgraph "Action Area"
        CopyBtn["ClipboardButton<br/>copy text"]
        ExpandBtn["Expand Button<br/>full-screen view"]
    end
    
    Container --> Header
    Container --> Content
    Container --> Actions
    
    Header --> Status
    Header --> Model
    Header --> Metrics
    
    Actions --> CopyBtn
    Actions --> ExpandBtn
    Content --> GenerationView["GenerationView"]
    
    style Container fill:#e1ffe1
    style Header fill:#fff4e1
```

### Panel Header Display

The header adapts based on generation status and shows contextual information:

```typescript
// Status-based header text
{currentGeneration.status === "running" && <p>Generating...</p>}
{currentGeneration.status === "completed" && (
    <p>Result <span>from {provider} {modelId}</span></p>
)}
{currentGeneration.status === "failed" && <p>Error</p>}

// Metrics display (completed only)
{currentGeneration.status === "completed" && currentGeneration.usage && (
    <div className="flex items-center gap-[10px]">
        <span>
            <TimerIcon />
            {formatExecutionTime(startedAt, completedAt)}
        </span>
        <span>
            <ArrowUpIcon />
            {inputTokens.toLocaleString()}t
        </span>
        <span>
            <ArrowDownIcon />
            {outputTokens.toLocaleString()}t
        </span>
    </div>
)}
```

**Sources:**
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/generation-panel.tsx:118-245]()
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/generation-panel.tsx:163-222]()

### Execution Time Formatting

```typescript
function formatExecutionTime(startedAt: number, completedAt: number): string {
    const durationMs = completedAt - startedAt;
    if (durationMs < 60000) {
        return `${durationMs.toLocaleString()}ms`;
    }
    const minutes = Math.floor(durationMs / 60000);
    const seconds = Math.floor((durationMs % 60000) / 1000);
    return `${minutes}m ${seconds}s`;
}
```

**Sources:**
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/generation-panel.tsx:36-44]()

### Text Content Extraction

For clipboard functionality, text content is extracted from generation outputs:

```typescript
function getGenerationTextContent(generation: Generation): string {
    if (generation.status === "completed") {
        const textOutputs = generation.outputs
            .filter((output) => output.type === "generated-text")
            .map((output) => output.content)
            .join("\n\n");
        
        if (textOutputs) return textOutputs;
    }
    
    // Fallback to extracting from messages
    const generatedMessages = generation.messages
        ?.filter((m) => m.role === "assistant") ?? [];
    
    return generatedMessages
        .map((message) => 
            message.parts
                ?.filter((part) => part.type === "text")
                .map((part) => part.text)
                .join("\n")
        )
        .join("\n");
}
```

**Sources:**
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/generation-panel.tsx:46-76]()

## Expanded View System

Properties panels support expanding the prompt editor and generation results to full-screen overlays for better visibility.

### Expansion Architecture

```mermaid
graph TB
    subgraph "Properties Panel Layout"
        MainContent["Main Content<br/>overflow-y-auto"]
        PromptEditor["Prompt Editor<br/>with expand button"]
        GenPanel["Generation Panel<br/>with expand button"]
        PromptOverlay["Prompt Overlay<br/>isPromptExpanded"]
        GenOverlay["Generation Overlay<br/>isGenerationExpanded"]
    end
    
    subgraph "Overlay Positioning"
        CalcTop["useElementTopPx<br/>calculate origin"]
        CalcBottom["useOverlayBottom<br/>calculate bottom"]
        Transform["Transform Origin<br/>scale animation"]
    end
    
    subgraph "Overlay Controls"
        MinimizeBtn["Minimize Button<br/>bottom-right"]
        Backdrop["Backdrop Button<br/>click to close"]
        ESC["ESC Key Handler"]
    end
    
    PromptEditor --> PromptOverlay
    GenPanel --> GenOverlay
    
    PromptOverlay --> CalcTop
    PromptOverlay --> CalcBottom
    GenOverlay --> CalcTop
    GenOverlay --> CalcBottom
    
    CalcTop --> Transform
    CalcBottom --> Transform
    
    PromptOverlay --> MinimizeBtn
    PromptOverlay --> Backdrop
    PromptOverlay --> ESC
    
    GenOverlay --> MinimizeBtn
    GenOverlay --> Backdrop
    
    style PromptOverlay fill:#e1ffe1
    style GenOverlay fill:#fff4e1
```

### Overlay Implementation

Overlays are absolutely positioned dialogs that scale from the original component position:

```typescript
const [isPromptExpanded, setIsPromptExpanded] = useState(false);
const [isGenerationExpanded, setIsGenerationExpanded] = useState(false);

const generateCtaRef = useRef<HTMLDivElement | null>(null);
const promptEditorRef = useRef<HTMLDivElement | null>(null);
const generationPanelRef = useRef<HTMLDivElement | null>(null);

const overlayBottomPx = useOverlayBottom(generateCtaRef);
const promptTopPx = useElementTopPx(promptEditorRef);
const generationTopPx = useElementTopPx(generationPanelRef);

<div
    role="dialog"
    aria-modal="true"
    className={`absolute left-0 right-0 z-20 flex flex-col transition-all ${
        isPromptExpanded ? "opacity-100 scale-y-100" : "opacity-0 scale-y-0"
    }`}
    style={{
        top: 0,
        bottom: overlayBottomPx,
        transformOrigin: `center ${promptTopPx}px`,
    }}
>
    {/* Expanded content */}
</div>
```

**Sources:**
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/index.tsx:60-74]()
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/index.tsx:184-241]()

### Keyboard Navigation

The expanded views support keyboard shortcuts for better UX:

```typescript
useEffect(() => {
    const onKeydown = (e: KeyboardEvent) => {
        if (isPromptExpanded && e.key === "Escape") {
            e.stopPropagation();
            setIsPromptExpanded(false);
            setEditorVersion((v) => v + 1); // Remount editor
        }
        if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
            generateText();
        }
    };
    window.addEventListener("keydown", onKeydown, { capture: true });
    return () => window.removeEventListener("keydown", onKeydown);
}, [isPromptExpanded, generateText]);
```

**Sources:**
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/index.tsx:119-132]()

### Live Prompt Synchronization

When expanding the prompt editor, the latest prompt value is synchronized using `useLivePrompt`:

```typescript
const livePrompt = useLivePrompt(node.id);

<PromptEditor
    key={`expanded-${editorVersion}-${node.id}`}
    value={livePrompt ?? node.content.prompt}
    onValueChange={(value) => {
        updateNodeDataContent(node, { prompt: value });
    }}
    // ...
/>
```

This ensures the expanded editor always shows the current content, even if the user was typing in the collapsed view before expanding.

**Sources:**
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/index.tsx:77]()
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/index.tsx:201-217]()

## Spinner and Loading States

### Text Generation Spinner

A consistent spinner component uses animated ghost icons:

```typescript
function Spinner() {
    return (
        <div className="flex gap-[12px] text-text-muted">
            <WilliIcon className="w-[20px] h-[20px] animate-pop-pop-1" />
            <WilliIcon className="w-[20px] h-[20px] animate-pop-pop-2" />
            <WilliIcon className="w-[20px] h-[20px] animate-pop-pop-3" />
        </div>
    );
}
```

The spinner is shown when:
- Generation status is `created`, `queued`, or `running`
- There are no reasoning parts being streamed yet

**Sources:**
- [internal-packages/workflow-designer-ui/src/ui/generation-view.tsx:45-53]()
- [internal-packages/workflow-designer-ui/src/ui/generation-view.tsx:251-260]()

### Image Generation Loading

Image generation shows a more sophisticated loading state with aspect ratio preservation:

```typescript
function ImageGenerationLoading({ configuration }) {
    const aspectRatio = getAspectRatio(configuration);
    
    return (
        <div 
            className="bg-surface/10 rounded-[8px] relative overflow-hidden"
            style={{ aspectRatio, width: "auto" }}
        >
            <div className="absolute inset-0 opacity-30 animate-glare" />
            <div className="flex items-center gap-[4px] absolute top-[12px] left-[12px]">
                <p className="animate-shine">Generating...</p>
                <WilliIcon className="animate-ghost-glow" />
                <WilliIcon className="animate-ghost-glow delay-500" />
                <WilliIcon className="animate-ghost-glow delay-1000" />
            </div>
        </div>
    );
}
```

The aspect ratio is calculated based on the model and configuration:
- Fal models: Parse from size configuration (e.g., "1152x864")
- OpenAI models: Parse from WIDTHxHEIGHT format
- Google models: Default to 1:1

**Sources:**
- [internal-packages/workflow-designer-ui/src/ui/image-generation-loading.tsx:51-135]()
- [internal-packages/workflow-designer-ui/src/ui/image-generation-loading.tsx:11-49]()

## Generate CTA Button

The `GenerateCtaButton` component provides a consistent execution button across all node types:

```typescript
<GenerateCtaButton
    isGenerating={isGenerating}
    isEmpty={isPromptEmpty(node.content.prompt)}
    onClick={() => {
        if (isGenerating) stopGenerationRunner();
        else generateText();
    }}
    idleLabel="Generate"  // Optional custom label
    emptyLabel="Start Writing Your Prompt"  // Optional custom label
/>
```

### Button States

| State | Label | Action | Styling |
|-------|-------|--------|---------|
| Empty | "Start Writing Your Prompt" | No-op | Disabled appearance |
| Idle | "Generate" / custom | Trigger generation | Primary button |
| Generating | "Stop" | Cancel generation | Secondary button |

The button automatically handles:
- Visual state transitions
- Keyboard shortcuts (Cmd/Ctrl + Enter)
- Accessibility labels
- Loading indicators

**Sources:**
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/index.tsx:175-182]()
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/index.tsx:110-122]()

## Node-Specific Implementations

### Text Generation Node

Text generation panels integrate all components into a cohesive workflow:

```typescript
export function TextGenerationNodePropertiesPanel({ node }) {
    const { createAndStartGenerationRunner, isGenerating, stopGenerationRunner, currentGeneration } 
        = useNodeGenerations({ nodeId: node.id, origin: { type: "studio", workspaceId: data.id } });
    
    const generateText = useCallback(() => {
        if (usageLimitsReached) {
            error("Please upgrade your plan to continue using this feature.");
            return;
        }
        if (isPromptEmpty(node.content.prompt)) {
            error("Please fill in the prompt to run.");
            return;
        }
        
        createAndStartGenerationRunner({
            origin: { type: "studio", workspaceId: data.id },
            operationNode: node,
            sourceNodes,
            connections: data.connections.filter((c) => c.inputNode.id === node.id),
        });
    }, [/* deps */]);
    
    return (
        <PropertiesPanelRoot>
            <NodePanelHeader node={node} onChangeName={...} onDelete={...} />
            <PropertiesPanelContent>
                <TextGenerationTabContent node={node} onPromptExpand={...} />
                <GenerationPanel node={node} onClickGenerateButton={generateText} />
                <GenerateCtaButton isGenerating={isGenerating} onClick={...} />
                {/* Expanded overlays */}
            </PropertiesPanelContent>
        </PropertiesPanelRoot>
    );
}
```

**Sources:**
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/index.tsx:28-290]()

### Image Generation Node

Image generation follows a similar pattern but with model-specific configuration:

```typescript
export function ImageGenerationNodePropertiesPanel({ node }) {
    const { createAndStartGenerationRunner, isGenerating, stopGenerationRunner }
        = useNodeGenerations({ nodeId: node.id, origin: { type: "studio", workspaceId: data.id } });
    
    const generateImage = useCallback(() => {
        if (usageLimitsReached) {
            error("Please upgrade your plan to continue using this feature.");
            return;
        }
        if (isPromptEmpty(node.content.prompt)) {
            error("Please fill in the prompt to run.");
            return;
        }
        
        createAndStartGenerationRunner({
            origin: { type: "studio", workspaceId: data.id },
            operationNode: node,
            sourceNodes: connectedSources.map((cs) => cs.node),
            connections: data.connections.filter((c) => c.inputNode.id === node.id),
        });
    }, [/* deps */]);
    
    return (
        <PropertiesPanelRoot>
            <NodePanelHeader node={node} onChangeName={...} onDelete={...} />
            <PropertiesPanelContent>
                <PromptPanel node={node} onExpand={...} />
                <GenerationPanel node={node} onClickGenerateButton={generateImage} onExpand={...} />
                <GenerateCtaButton isGenerating={isGenerating} onClick={...} />
                {/* Expanded overlays */}
            </PropertiesPanelContent>
        </PropertiesPanelRoot>
    );
}
```

**Sources:**
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/index.tsx:27-248]()
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/index.tsx:63-94]()

### Query Node

Query nodes use `QueryResultView` instead of `GenerationView`:

```typescript
export function QueryNodePropertiesPanel({ node }) {
    const { createAndStartGenerationRunner, isGenerating, stopGenerationRunner }
        = useNodeGenerations({ nodeId: node.id, origin: { type: "studio", workspaceId: data.id } });
    
    const query = useMemo(() => {
        const rawQuery = node.content.query.trim();
        if (isJsonContent(rawQuery)) {
            return jsonContentToText(JSON.parse(rawQuery));
        }
        return rawQuery;
    }, [node.content.query]);
    
    const generate = useCallback(() => {
        if (query.length === 0) {
            error("Query is empty");
            return;
        }
        createAndStartGenerationRunner({
            origin: { type: "studio", workspaceId: data.id },
            operationNode: node,
            sourceNodes: connectedSources.map((cs) => cs.node),
            connections: data.connections.filter((c) => c.inputNode.id === node.id),
        });
    }, [/* deps */]);
    
    return (
        <PropertiesPanelRoot>
            <NodePanelHeader node={node} onChangeName={...} onDelete={...} />
            <PropertiesPanelContent>
                <SettingsPanel node={node} />
                <QueryPanel node={node} />
                <GenerationPanel node={node} /> {/* Uses QueryResultView */}
                <GenerateCtaButton 
                    isGenerating={isGenerating} 
                    isEmpty={query.length === 0}
                    onClick={...}
                    idleLabel="Run Query"
                    emptyLabel="Start Writing Your Query"
                />
            </PropertiesPanelContent>
        </PropertiesPanelRoot>
    );
}
```

**Sources:**
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/index.tsx:25-128]()
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/index.tsx:35-77]()

## Summary

The Generation Execution and Results Display system provides a unified interface for triggering and monitoring AI operations across different node types. Key components include:

- **useNodeGenerations hook** - Central state management for generation lifecycle
- **GenerationView** - Text/reasoning display with streaming support
- **QueryResultView** - Vector search result display with tabs and metadata
- **GenerationPanel** - Node-specific result containers with metrics
- **Expanded overlays** - Full-screen views for prompts and results
- **Loading states** - Animated spinners and image placeholders

The system maintains real-time synchronization between the engine and UI, providing immediate feedback to users as generations progress from creation through completion.

---

# Page: Model Configuration Panels

# Model Configuration Panels

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/playground/app/ui/page.tsx](apps/playground/app/ui/page.tsx)
- [apps/studio.giselles.ai/app/(auth)/components/auth-container.tsx](apps/studio.giselles.ai/app/(auth)/components/auth-container.tsx)
- [internal-packages/ui/components/button.tsx](internal-packages/ui/components/button.tsx)
- [internal-packages/ui/components/dialog.tsx](internal-packages/ui/components/dialog.tsx)
- [internal-packages/ui/components/glass-dialog.tsx](internal-packages/ui/components/glass-dialog.tsx)
- [internal-packages/ui/components/prompt-editor.tsx](internal-packages/ui/components/prompt-editor.tsx)
- [internal-packages/ui/style.css](internal-packages/ui/style.css)
- [internal-packages/ui/styles/semantic.css](internal-packages/ui/styles/semantic.css)
- [internal-packages/workflow-designer-ui/src/editor/chat/chat-panel.tsx](internal-packages/workflow-designer-ui/src/editor/chat/chat-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/index.tsx](internal-packages/workflow-designer-ui/src/editor/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/app-entry-node-properties-panel/index.ts](internal-packages/workflow-designer-ui/src/editor/properties-panel/app-entry-node-properties-panel/index.ts)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/file-node-properties-panel/file-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/file-node-properties-panel/file-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/file-node-properties-panel/index.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/file-node-properties-panel/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/generation-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/generation-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/index.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/prompt-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/prompt-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/index.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/generation-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/generation-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/index.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/query-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/query-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/generation-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/generation-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/index.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/anthropic.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/anthropic.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/google.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/google.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/openai.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/openai.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/prompt-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/prompt-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/tab-content.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/tab-content.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/tools/tool-provider/anthropic-web-search/anthropic-web-search.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/tools/tool-provider/anthropic-web-search/anthropic-web-search.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-node-properties-panel/index.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/text-node-properties-panel/index.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/index.ts](internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/index.ts)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/panel-spacing.ts](internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/panel-spacing.ts)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/properties-panel.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/properties-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/resizable-section.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/ui/resizable-section.tsx)
- [internal-packages/workflow-designer-ui/src/ui/generation-view.tsx](internal-packages/workflow-designer-ui/src/ui/generation-view.tsx)
- [internal-packages/workflow-designer-ui/src/ui/image-generation-loading.tsx](internal-packages/workflow-designer-ui/src/ui/image-generation-loading.tsx)
- [internal-packages/workflow-designer-ui/src/ui/query-result-view.tsx](internal-packages/workflow-designer-ui/src/ui/query-result-view.tsx)
- [packages/text-editor/src/react/component.tsx](packages/text-editor/src/react/component.tsx)

</details>



## Purpose and Scope

Model Configuration Panels provide UI components for configuring AI language model parameters within text generation and image generation nodes. These panels allow users to select AI models from different providers (OpenAI, Anthropic, Google, Fal) and adjust provider-specific parameters such as temperature, top-p, reasoning settings, and tool integrations.

For information about the parent properties panel system, see [Properties Panels and Node Configuration](#5.3). For generation execution triggered by these configurations, see [Generation Execution and Results Display](#5.5).

## Architecture Overview

Model configuration panels are organized by node type and AI provider. Each provider has a dedicated panel component that renders appropriate controls for that provider's model parameters.

```mermaid
graph TB
    subgraph "Node Properties Panels"
        TGPanel["TextGenerationNodePropertiesPanel"]
        IGPanel["ImageGenerationNodePropertiesPanel"]
    end
    
    subgraph "Configuration Components"
        PromptPanel["PromptPanel"]
        ImagePromptPanel["Image PromptPanel"]
        ModelPicker["ModelPicker"]
    end
    
    subgraph "Provider-Specific Panels"
        OpenAIPanel["OpenAIModelPanel"]
        AnthropicPanel["AnthropicModelPanel"]
        GooglePanel["GoogleModelPanel"]
        FalPanel["FalModelPanel"]
        OpenAIImagePanel["OpenAIImageModelPanel"]
    end
    
    subgraph "Shared Controls"
        TempSlider["TemperatureSlider"]
        TopPSlider["TopPSlider"]
        FreqSlider["FrequencyPenaltySlider"]
        PresSlider["PresencePenaltySlider"]
        Toggle["Toggle"]
        Select["Select"]
    end
    
    TGPanel --> PromptPanel
    IGPanel --> ImagePromptPanel
    PromptPanel --> ModelPicker
    ImagePromptPanel --> ModelPicker
    
    PromptPanel --> OpenAIPanel
    PromptPanel --> AnthropicPanel
    PromptPanel --> GooglePanel
    ImagePromptPanel --> FalPanel
    ImagePromptPanel --> OpenAIImagePanel
    
    OpenAIPanel --> TempSlider
    OpenAIPanel --> TopPSlider
    OpenAIPanel --> FreqSlider
    OpenAIPanel --> PresSlider
    OpenAIPanel --> Toggle
    OpenAIPanel --> Select
    
    AnthropicPanel --> TempSlider
    AnthropicPanel --> TopPSlider
    AnthropicPanel --> Toggle
    
    GooglePanel --> TempSlider
    GooglePanel --> TopPSlider
    GooglePanel --> Toggle
```

**Sources:**
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/index.tsx:1-290]()
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/prompt-panel.tsx:1-397]()
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/prompt-panel.tsx:1-205]()

## Model Picker Component

The `ModelPicker` component provides a unified interface for selecting AI models across different providers. It organizes models into provider groups and handles tier-based access control.

### Model Groups Structure

```mermaid
graph LR
    ModelPicker["ModelPicker Component"]
    
    subgraph "Provider Groups"
        OpenAIGroup["OpenAI Group"]
        AnthropicGroup["Anthropic Group"]
        GoogleGroup["Google Group"]
        FalGroup["Fal Group"]
    end
    
    subgraph "Model Metadata"
        ModelId["model.id"]
        Badge["ProTag badge"]
        Disabled["disabled flag"]
        Reason["disabledReason"]
    end
    
    subgraph "Tier Access Control"
        UserTier["usageLimits.featureTier"]
        TierCheck["hasTierAccess()"]
    end
    
    ModelPicker --> OpenAIGroup
    ModelPicker --> AnthropicGroup
    ModelPicker --> GoogleGroup
    ModelPicker --> FalGroup
    
    OpenAIGroup --> ModelId
    OpenAIGroup --> Badge
    OpenAIGroup --> Disabled
    OpenAIGroup --> Reason
    
    UserTier --> TierCheck
    TierCheck --> Disabled
```

The model picker uses the following data structure from [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/prompt-panel.tsx:53-86]():

| Field | Type | Description |
|-------|------|-------------|
| `provider` | `string` | Provider identifier (openai, anthropic, google, fal) |
| `label` | `string` | Display name for provider group |
| `models` | `Array` | Array of model objects |
| `models[].id` | `string` | Model identifier |
| `models[].badge` | `ReactNode` | Optional Pro badge for premium models |
| `models[].disabled` | `boolean` | Whether model is unavailable to user |
| `models[].disabledReason` | `string` | Explanation if disabled |

**Sources:**
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/prompt-panel.tsx:53-86]()
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/prompt-panel.tsx:63-100]()

## OpenAI Model Panel

The `OpenAIModelPanel` component handles configuration for OpenAI language models, including both standard and reasoning models.

### Configuration Flow

```mermaid
sequenceDiagram
    participant User
    participant OpenAIPanel as OpenAIModelPanel
    participant Controls as Slider/Toggle/Select
    participant Store as WorkflowDesignerStore
    participant Node as TextGenerationNode
    
    User->>OpenAIPanel: Adjust parameter
    OpenAIPanel->>Controls: Render control component
    User->>Controls: Change value
    Controls->>OpenAIPanel: onValueChange callback
    OpenAIPanel->>OpenAIPanel: Parse with OpenAILanguageModelData
    OpenAIPanel->>Store: updateNodeDataContent()
    Store->>Node: Update node.content.llm
```

### Parameter Controls by Model Type

**Standard OpenAI Models** ([internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/openai.tsx:108-136]()):

| Parameter | Control | Range | Description |
|-----------|---------|-------|-------------|
| `temperature` | `TemperatureSlider` | 0.0 - 2.0 | Randomness in responses |
| `topP` | `TopPSlider` | 0.0 - 1.0 | Nucleus sampling threshold |
| `frequencyPenalty` | `FrequencyPenaltySlider` | -2.0 - 2.0 | Penalty for repeated tokens |
| `presencePenalty` | `PresencePenaltySlider` | -2.0 - 2.0 | Penalty for topic repetition |
| `webSearch` | `Toggle` | boolean | Enable OpenAI web search tool |

**Reasoning Models** (e.g., o1, o3) ([internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/openai.tsx:44-106]()):

| Parameter | Control | Options | Description |
|-----------|---------|---------|-------------|
| `reasoningEffort` | `Select` | minimal, low, medium, high | Computational effort for reasoning |
| `textVerbosity` | `Select` | low, medium, high | Output verbosity level |

### Web Search Tool Integration

When web search is enabled ([internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/openai.tsx:137-178]()), the panel:

1. Adds `openaiWebSearch` configuration to `node.content.tools`
2. Creates a new output with `accessor: "source"` on the node
3. Manages connection cleanup when disabled

**Sources:**
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/openai.tsx:1-181]()
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/prompt-panel.tsx:119-165]()

## Anthropic Model Panel

The `AnthropicModelPanel` configures Anthropic Claude models with reasoning capabilities.

```mermaid
graph TB
    AnthropicPanel["AnthropicModelPanel"]
    
    subgraph "Standard Parameters"
        Temp["temperature: 0.0-2.0"]
        TopP["topP: 0.0-1.0"]
    end
    
    subgraph "Reasoning Configuration"
        ReasoningCheck["hasCapability(Reasoning)"]
        ReasoningToggle["reasoningText: boolean"]
    end
    
    subgraph "Data Updates"
        ParseData["AnthropicLanguageModelData.parse()"]
        UpdateNode["updateNodeDataContent()"]
    end
    
    AnthropicPanel --> Temp
    AnthropicPanel --> TopP
    AnthropicPanel --> ReasoningCheck
    
    ReasoningCheck -->|true| ReasoningToggle
    ReasoningCheck -->|false| UnsupportedMsg["Unsupported message"]
    
    Temp --> ParseData
    TopP --> ParseData
    ReasoningToggle --> ParseData
    ParseData --> UpdateNode
```

The reasoning capability check ([internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/anthropic.tsx:21-28]()) determines whether to show the reasoning toggle:

```typescript
const hasReasoningCapability = useMemo(() => {
    const languageModel = anthropicLanguageModels.find(
        (lm) => lm.id === anthropicLanguageModel.id,
    );
    return (
        !!languageModel && hasCapability(languageModel, Capability.Reasoning)
    );
}, [anthropicLanguageModel.id]);
```

**Sources:**
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/anthropic.tsx:1-79]()

## Google Model Panel

The `GoogleModelPanel` configures Google Gemini models with search grounding and URL context features.

### Mutually Exclusive Features

Search Grounding and URL Context cannot be enabled simultaneously ([internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/google.tsx:21-64]()):

```mermaid
stateDiagram-v2
    [*] --> NoFeatures
    NoFeatures --> SearchGrounding: Enable Search
    NoFeatures --> UrlContext: Enable URL
    SearchGrounding --> NoFeatures: Disable Search
    UrlContext --> NoFeatures: Disable URL
    
    note right of SearchGrounding
        searchGrounding: true
        urlContext: false
        output.accessor: "source"
    end note
    
    note right of UrlContext
        searchGrounding: false
        urlContext: true
        output.accessor: "source"
    end note
```

### Output Management

Both features require a "source" output ([internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/prompt-panel.tsx:167-209]()):

| Feature | Output Required | Cleanup on Disable |
|---------|----------------|-------------------|
| Search Grounding | Yes | Deletes connections and removes output |
| URL Context | Yes | Deletes connections and removes output |
| Both Disabled | No | Removes source output |

**Sources:**
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/google.tsx:1-101]()
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/prompt-panel.tsx:167-255]()

## Image Generation Model Panels

Image generation panels configure models for visual content creation from Fal and OpenAI providers.

### Fal Model Panel

Configures Flux models with size and guidance parameters:

```mermaid
graph LR
    FalPanel["FalModelPanel"]
    
    subgraph "Configuration"
        Size["size: Select"]
        Guidance["guidanceScale: Slider"]
        Steps["steps: Slider"]
    end
    
    subgraph "Size Options"
        S1["512x512"]
        S2["1024x1024"]
        S3["1152x864"]
        S4["1312x736"]
    end
    
    FalPanel --> Size
    FalPanel --> Guidance
    FalPanel --> Steps
    Size --> S1
    Size --> S2
    Size --> S3
    Size --> S4
```

**Sources:**
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/models/index.tsx:1-50]()

### OpenAI Image Model Panel

Configures DALL-E models with size, quality, and style parameters. The panel also handles reference image connections ([internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/prompt-panel.tsx:102-123]()):

```mermaid
graph TB
    ImagePanel["OpenAIImageModelPanel"]
    
    subgraph "Parameters"
        Size["size: Select"]
        Quality["quality: Select"]
        Style["style: Select"]
    end
    
    subgraph "Image Reference Support"
        CheckModel["Is gpt-image-1?"]
        FilterConnections["Filter incompatible"]
        UpdateInputs["Update node.inputs"]
    end
    
    ImagePanel --> Size
    ImagePanel --> Quality
    ImagePanel --> Style
    
    ImagePanel --> CheckModel
    CheckModel -->|yes| FilterConnections
    CheckModel -->|no| UpdateInputs
    FilterConnections --> UpdateInputs
```

**Sources:**
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/models/index.tsx:1-200]()
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/prompt-panel.tsx:102-123]()

## Shared Model Control Components

Reusable slider components provide consistent parameter adjustment across providers.

### Control Component Interface

Each slider component follows this pattern from [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/shared-model-controls.tsx]():

| Component | Parameter | Range | Step | Default |
|-----------|-----------|-------|------|---------|
| `TemperatureSlider` | `temperature` | 0.0 - 2.0 | 0.01 | 1.0 |
| `TopPSlider` | `topP` | 0.0 - 1.0 | 0.01 | 1.0 |
| `FrequencyPenaltySlider` | `frequencyPenalty` | -2.0 - 2.0 | 0.01 | 0.0 |
| `PresencePenaltySlider` | `presencePenalty` | -2.0 - 2.0 | 0.01 | 0.0 |

### Update Pattern

All sliders use a generic update pattern:

```mermaid
sequenceDiagram
    participant Slider
    participant onModelChange
    participant parseModelData
    participant Store
    
    Slider->>onModelChange: onChange(value)
    onModelChange->>parseModelData: Parse updated config
    parseModelData->>onModelChange: Validated ModelData
    onModelChange->>Store: updateNodeDataContent()
    Store->>Store: Update node.content.llm.configurations
```

**Sources:**
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/shared-model-controls.tsx:1-150]()

## Tool Configuration Dialogs

Advanced tool configurations are managed through dedicated dialog components.

### Anthropic Web Search Configuration

The `AnthropicWebSearchToolConfigurationDialog` ([internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/tools/tool-provider/anthropic-web-search/anthropic-web-search.tsx:30-472]()) provides:

```mermaid
graph TB
    Dialog["AnthropicWebSearchToolConfigurationDialog"]
    
    subgraph "Basic Settings"
        Enable["webSearchEnabled: Toggle"]
        MaxUses["maxUses: Slider 1-10"]
    end
    
    subgraph "Domain Filtering"
        Mode["filteringMode: Radio"]
        NoneMode["none"]
        AllowMode["allow"]
        BlockMode["block"]
        DomainInput["Domain Tags Input"]
    end
    
    subgraph "Validation"
        ValidateDomain["isValidDomain()"]
        CheckDuplicates["Check existing"]
        ShowErrors["Display errors"]
    end
    
    Dialog --> Enable
    Enable -->|true| MaxUses
    Enable -->|true| Mode
    
    Mode --> NoneMode
    Mode --> AllowMode
    Mode --> BlockMode
    
    AllowMode --> DomainInput
    BlockMode --> DomainInput
    
    DomainInput --> ValidateDomain
    ValidateDomain --> CheckDuplicates
    CheckDuplicates --> ShowErrors
```

**Domain Filtering Modes:**

| Mode | Config Field | Behavior |
|------|-------------|----------|
| `none` | `allowedDomains: undefined`<br>`blockedDomains: undefined` | Search all domains |
| `allow` | `allowedDomains: string[]` | Only search listed domains |
| `block` | `blockedDomains: string[]` | Exclude listed domains |

**Sources:**
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/tools/tool-provider/anthropic-web-search/anthropic-web-search.tsx:1-472]()

## Integration with Properties Panels

Model configuration panels are embedded within node-specific properties panels through the `PromptPanel` component.

### Text Generation Integration

```mermaid
graph TB
    TGPanel["TextGenerationNodePropertiesPanel"]
    PromptPanel["PromptPanel"]
    TabContent["TextGenerationTabContent"]
    
    subgraph "Panel Sections"
        ModelPickerSection["modelPicker: boolean"]
        ModelParamsSection["modelParameters: boolean"]
        AdvancedSection["advancedOptions: boolean"]
        PromptLabelSection["promptLabel: boolean"]
    end
    
    subgraph "Panel Slots"
        HeaderActions["headerActions: ReactNode"]
        UploadArea["uploadArea: ReactNode"]
        Footer["footer: ReactNode"]
    end
    
    TGPanel --> TabContent
    TabContent --> PromptPanel
    
    PromptPanel --> ModelPickerSection
    PromptPanel --> ModelParamsSection
    PromptPanel --> AdvancedSection
    PromptPanel --> PromptLabelSection
    
    PromptPanel --> HeaderActions
    PromptPanel --> UploadArea
    PromptPanel --> Footer
```

The `PromptPanel` component ([internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/prompt-panel.tsx:89-397]()) accepts configuration through `sections` and `slots` props:

**Sections Configuration:**
```typescript
type PromptPanelSections = {
    modelPicker?: boolean;          // Show ModelPicker
    modelParameters?: boolean;      // Show provider panels
    advancedOptions?: boolean;      // Show tools section
    promptLabel?: boolean;          // Show "Prompt" label
};
```

**Slots Configuration:**
```typescript
type PromptPanelSlots = {
    headerActions?: React.ReactNode;  // Custom header actions
    uploadArea?: React.ReactNode;     // File upload controls
    footer?: React.ReactNode;         // Custom footer content
};
```

**Sources:**
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/index.tsx:28-289]()
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/tab-content.tsx:1-32]()
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/prompt-panel.tsx:40-51]()

## State Management and Data Flow

Model configuration changes flow through the workflow designer store to update node data.

```mermaid
sequenceDiagram
    participant User
    participant Panel as ModelPanel
    participant Store as useWorkflowDesignerStore
    participant Node as Node in workspace.nodes
    participant Engine as GiselleEngine
    
    User->>Panel: Change model parameter
    Panel->>Panel: Validate with ModelData.parse()
    Panel->>Store: updateNodeDataContent(node, {llm})
    Store->>Node: Update node.content.llm
    Store->>Store: Notify subscribers
    
    Note over User,Engine: Generation Time
    
    User->>Panel: Click Generate
    Panel->>Engine: createAndStartGenerationRunner()
    Engine->>Node: Read node.content.llm
    Engine->>Engine: Configure AI SDK with parameters
```

### Update Functions

The store provides two primary update functions ([internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/prompt-panel.tsx:102-106]()):

| Function | Purpose | Usage |
|----------|---------|-------|
| `updateNodeDataContent(node, content)` | Update `node.content` fields | Model parameters, prompt, tools |
| `updateNodeData(node, data)` | Update top-level node fields | Name, inputs, outputs |

**Sources:**
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/prompt-panel.tsx:102-106]()
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/openai.tsx:61-68]()
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/anthropic.tsx:52-59]()

## Model Defaults and Initialization

Default model configurations are created through factory functions.

### Default Model Data Creation

The `createDefaultModelData` function ([internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model-defaults.tsx]()) initializes provider-specific configurations:

```mermaid
graph LR
    CreateDefault["createDefaultModelData(provider)"]
    
    subgraph "Provider Branches"
        OpenAI["openai branch"]
        Anthropic["anthropic branch"]
        Google["google branch"]
    end
    
    subgraph "Default Configs"
        OpenAIDefaults["temperature: 1.0<br/>topP: 1.0<br/>frequencyPenalty: 0<br/>presencePenalty: 0"]
        AnthropicDefaults["temperature: 1.0<br/>topP: 1.0<br/>reasoningText: false"]
        GoogleDefaults["temperature: 1.0<br/>topP: 1.0<br/>searchGrounding: false"]
    end
    
    CreateDefault --> OpenAI
    CreateDefault --> Anthropic
    CreateDefault --> Google
    
    OpenAI --> OpenAIDefaults
    Anthropic --> AnthropicDefaults
    Google --> GoogleDefaults
```

### Model Switching

When a user switches models via `ModelPicker`, the system:

1. Creates default configuration for new provider
2. Updates model ID via `updateModelId()`
3. Resets incompatible parameters
4. Clears tool configurations

From [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/prompt-panel.tsx:281-287]():

```typescript
onSelect={(provider, modelId) => {
    const next = createDefaultModelData(
        provider as "openai" | "anthropic" | "google",
    );
    const updated = updateModelId(next, modelId);
    updateNodeDataContent(node, { llm: updated, tools: {} });
}}
```

**Sources:**
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model-defaults.tsx:1-100]()
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/model-defaults.tsx:1-80]()

---

# Page: Applications and User Interfaces

# Applications and User Interfaces

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/playground/package.json](apps/playground/package.json)
- [apps/studio.giselles.ai/package.json](apps/studio.giselles.ai/package.json)
- [internal-packages/workflow-designer-ui/package.json](internal-packages/workflow-designer-ui/package.json)
- [package.json](package.json)
- [packages/giselle/package.json](packages/giselle/package.json)
- [pnpm-lock.yaml](pnpm-lock.yaml)
- [pnpm-workspace.yaml](pnpm-workspace.yaml)

</details>



This document covers the user-facing applications in the Giselle AI platform, including the Studio production application, the Playground development environment, and the UI component showcase. It explains the application architecture, routing structure, workspace context system, and key user interfaces for workflow execution (Stage) and knowledge management (Vector Stores).

For information about the Workflow Designer UI components and visual editing system, see [Workflow Designer UI](#5). For details about the underlying engine and execution system, see [Core Engine and SDK](#2).

## Overview

The Giselle AI platform provides three Next.js applications serving different purposes:

| Application | Location | Purpose | Key Dependencies |
|------------|----------|---------|------------------|
| **Studio** | `apps/studio.giselles.ai` | Production application for building and executing AI workflows | workflow-designer-ui, giselle engine, full integration suite |
| **Playground** | `apps/playground` | Development and testing environment with simplified configuration | workflow-designer-ui, giselle engine, minimal integrations |
| **UI Showcase** | `apps/ui.giselles.ai` | Component library showcase and documentation | @giselle-internal/ui only |

All applications are built with Next.js 15.5.2 and use React 19.1.1. The Studio application contains the complete feature set for production deployment, while Playground provides a minimal environment for development and testing.

**Sources:** [apps/studio.giselles.ai/package.json:1-133](), [apps/playground/package.json:1-43](), [apps/ui.giselles.ai/package.json]()

## Application Architecture

```mermaid
graph TB
    subgraph "Studio Application"
        StudioApp["Studio App<br/>apps/studio.giselles.ai"]
        StudioRoutes["Route Structure<br/>/flow, /stage, /settings"]
        WorkspaceProvider["WorkspaceProvider<br/>Central Context"]
        FeatureFlags["Feature Flag System<br/>flags.ts + Edge Config"]
    end
    
    subgraph "Playground Application"
        PlaygroundApp["Playground App<br/>apps/playground"]
        PlaygroundRoutes["Simplified Routes<br/>/flow only"]
        MinimalConfig["Minimal Configuration<br/>Local-only"]
    end
    
    subgraph "UI Showcase"
        UIApp["UI Showcase<br/>apps/ui.giselles.ai"]
        ComponentDocs["Component Documentation<br/>Visual Examples"]
    end
    
    subgraph "Shared Dependencies"
        WorkflowDesigner["@giselle-internal/workflow-designer-ui<br/>Visual Editor Components"]
        UILib["@giselle-internal/ui<br/>Shared UI Components"]
        GiselleEngine["@giselles-ai/giselle<br/>Orchestration Engine"]
    end
    
    subgraph "Studio-Specific Infrastructure"
        Database["Database Layer<br/>Drizzle ORM + Supabase"]
        Auth["Authentication<br/>@supabase/ssr"]
        Integrations["Integration Layer<br/>GitHub, RAG, Vector Stores"]
        Observability["Observability<br/>Sentry, OpenTelemetry"]
    end
    
    StudioApp --> WorkspaceProvider
    StudioApp --> FeatureFlags
    StudioApp --> StudioRoutes
    StudioApp --> WorkflowDesigner
    StudioApp --> UILib
    StudioApp --> GiselleEngine
    
    PlaygroundApp --> PlaygroundRoutes
    PlaygroundApp --> WorkflowDesigner
    PlaygroundApp --> UILib
    PlaygroundApp --> GiselleEngine
    PlaygroundApp --> MinimalConfig
    
    UIApp --> ComponentDocs
    UIApp --> UILib
    
    StudioApp --> Database
    StudioApp --> Auth
    StudioApp --> Integrations
    StudioApp --> Observability
    
    WorkspaceProvider -.provides context to.-> WorkflowDesigner
    WorkspaceProvider -.provides context to.-> StudioRoutes
```

**Sources:** [apps/studio.giselles.ai/package.json:25-106](), [apps/playground/package.json:19-31]()

## Studio Application

The Studio application (`apps/studio.giselles.ai`) is the production deployment of the Giselle AI platform. It provides a complete environment for designing workflows, managing knowledge bases, configuring integrations, and executing AI applications.

### Application Structure

```mermaid
graph TB
    subgraph "Entry Points"
        RootLayout["app/layout.tsx<br/>Root Layout"]
        AuthMiddleware["middleware.ts<br/>Auth + Route Protection"]
    end
    
    subgraph "Core Routes"
        FlowRoute["/flow/[flowId]<br/>Workflow Designer"]
        StageRoute["/stage<br/>Application Execution"]
        StageActsRoute["/stage/acts<br/>Execution History"]
        StageActDetail["/stage/acts/[actId]<br/>Act Details"]
        SettingsRoute["/settings<br/>Team Settings"]
        VectorStoresRoute["/settings/team/vector-stores<br/>Knowledge Management"]
    end
    
    subgraph "Server Actions"
        FlowActions["app/actions/flows.ts<br/>Workflow CRUD"]
        StageActions["app/actions/stage.ts<br/>Act Execution"]
        VectorStoreActions["app/actions/vector-stores.ts<br/>Knowledge Ingestion"]
        GitHubActions["app/actions/github.ts<br/>GitHub Integration"]
    end
    
    subgraph "API Routes"
        GenerationAPI["/api/generations/[id]<br/>Generation Data"]
        WebhookAPI["/api/webhooks/github<br/>GitHub Webhooks"]
        TriggerdevAPI["/api/trigger/*<br/>Trigger.dev Jobs"]
    end
    
    subgraph "Database Layer"
        DrizzleSchema["app/drizzle/*<br/>Schema Definitions"]
        SupabaseClient["app/lib/supabase/*<br/>Client Factories"]
    end
    
    RootLayout --> AuthMiddleware
    AuthMiddleware --> FlowRoute
    AuthMiddleware --> StageRoute
    AuthMiddleware --> SettingsRoute
    
    StageRoute --> StageActsRoute
    StageActsRoute --> StageActDetail
    SettingsRoute --> VectorStoresRoute
    
    FlowRoute --> FlowActions
    StageRoute --> StageActions
    VectorStoresRoute --> VectorStoreActions
    
    FlowActions --> DrizzleSchema
    StageActions --> DrizzleSchema
    VectorStoreActions --> DrizzleSchema
    
    SupabaseClient --> DrizzleSchema
    
    WebhookAPI --> GitHubActions
```

The Studio application uses Next.js App Router with server-side rendering and server actions for data mutations. All routes are protected by authentication middleware that validates Supabase sessions.

**Sources:** [apps/studio.giselles.ai/package.json:1-133]()

### Technology Stack

The Studio application leverages the following core technologies:

| Technology | Purpose | Key Packages |
|-----------|---------|--------------|
| **Framework** | Next.js with App Router, React Server Components | next@15.5.2, react@19.1.1 |
| **Authentication** | Supabase Auth with SSR support | @supabase/ssr@0.6.1, @supabase/auth-js@2.70.0 |
| **Database** | PostgreSQL with Drizzle ORM | drizzle-orm@0.44.2, @vercel/postgres@0.9.0 |
| **Styling** | Tailwind CSS v4 with custom theme system | tailwindcss@4.1.10, @tailwindcss/postcss@4.1.10 |
| **UI Components** | Radix UI primitives with custom theming | @radix-ui/* packages, @giselle-internal/ui |
| **Observability** | Sentry error tracking, OpenTelemetry tracing | @sentry/nextjs@9.30.0, @vercel/otel@1.10.0 |
| **Async Processing** | Trigger.dev for background jobs | @trigger.dev/sdk@4.0.5 |

**Sources:** [apps/studio.giselles.ai/package.json:25-106]()

### Key Dependencies

```mermaid
graph LR
    subgraph "Studio Application"
        StudioApp["studio.giselles.ai"]
    end
    
    subgraph "Internal Packages"
        WorkflowDesignerUI["@giselle-internal/workflow-designer-ui<br/>Visual workflow editor"]
        InternalUI["@giselle-internal/ui<br/>Shared components"]
    end
    
    subgraph "Engine Packages"
        Giselle["@giselles-ai/giselle<br/>Orchestration engine"]
        Protocol["@giselles-ai/protocol<br/>Type definitions"]
        NodeRegistry["@giselles-ai/node-registry<br/>Node types"]
    end
    
    subgraph "Integration Packages"
        GitHubTool["@giselles-ai/github-tool<br/>GitHub integration"]
        RAG["@giselles-ai/rag<br/>Vector search"]
        DocPreprocessor["@giselles-ai/document-preprocessor<br/>PDF processing"]
        Langfuse["@giselles-ai/langfuse<br/>LLM observability"]
    end
    
    subgraph "Infrastructure"
        Supabase["@supabase/supabase-js<br/>Database & Auth"]
        VercelEdgeConfig["@vercel/edge-config<br/>Feature flags"]
        Sentry["@sentry/nextjs<br/>Error tracking"]
        Triggerdev["@trigger.dev/sdk<br/>Background jobs"]
    end
    
    StudioApp --> WorkflowDesignerUI
    StudioApp --> InternalUI
    StudioApp --> Giselle
    StudioApp --> Protocol
    StudioApp --> NodeRegistry
    StudioApp --> GitHubTool
    StudioApp --> RAG
    StudioApp --> DocPreprocessor
    StudioApp --> Langfuse
    StudioApp --> Supabase
    StudioApp --> VercelEdgeConfig
    StudioApp --> Sentry
    StudioApp --> Triggerdev
    
    WorkflowDesignerUI --> Giselle
    WorkflowDesignerUI --> Protocol
    Giselle --> RAG
    Giselle --> GitHubTool
```

**Sources:** [apps/studio.giselles.ai/package.json:25-106]()

## Workspace Context and Feature Flags

The Studio application uses a centralized context system to provide configuration, feature flags, and integration settings throughout the application. This system enables environment-specific behavior and gradual feature rollouts.

### WorkspaceProvider Architecture

```mermaid
graph TB
    subgraph "Context Provider Tree"
        WorkspaceProvider["WorkspaceProvider<br/>app/lib/workspace-context/provider.tsx"]
        FeatureFlagContext["FeatureFlagContext<br/>Feature enablement"]
        IntegrationContext["IntegrationContext<br/>GitHub, etc."]
        UsageLimitsContext["UsageLimitsContext<br/>Plan quotas"]
        VectorStoreContext["VectorStoreContext<br/>Available stores"]
        TelemetryContext["TelemetryContext<br/>Tracing config"]
    end
    
    subgraph "Data Sources"
        Database["Database Queries<br/>Teams, Workspaces, Settings"]
        EdgeConfig["Vercel Edge Config<br/>Remote Feature Flags"]
        LocalEnv["process.env<br/>Local Environment"]
    end
    
    subgraph "Consumers"
        FlowPage["Flow Designer Page<br/>Conditional UI"]
        StagePage["Stage Page<br/>Feature-gated apps"]
        SettingsPage["Settings Pages<br/>Integration config"]
        ServerActions["Server Actions<br/>Business logic"]
    end
    
    WorkspaceProvider --> FeatureFlagContext
    WorkspaceProvider --> IntegrationContext
    WorkspaceProvider --> UsageLimitsContext
    WorkspaceProvider --> VectorStoreContext
    WorkspaceProvider --> TelemetryContext
    
    Database --> WorkspaceProvider
    EdgeConfig --> FeatureFlagContext
    LocalEnv --> FeatureFlagContext
    
    FlowPage --> WorkspaceProvider
    StagePage --> WorkspaceProvider
    SettingsPage --> WorkspaceProvider
    ServerActions --> WorkspaceProvider
```

The `WorkspaceProvider` is initialized at the root layout level and fetches workspace-specific data including team information, integration configurations, and usage quotas. It provides this data to all child components through React Context.

**Sources:** [apps/studio.giselles.ai/package.json:77-77]()

### Feature Flag System

The feature flag system uses a two-tier resolution strategy:

| Environment | Source | Priority | Use Case |
|------------|--------|----------|----------|
| **Local Development** | `process.env` variables | High | Developer overrides, local testing |
| **Production** | Vercel Edge Config | Medium | Remote flag management, gradual rollouts |
| **Default** | Flag definition file | Low | Fallback values |

```mermaid
graph TB
    subgraph "Flag Definition"
        FlagFile["flags.ts<br/>Flag Definitions & Defaults"]
        FlagSchema["Flag Schema<br/>Type-safe definitions"]
    end
    
    subgraph "Resolution Strategy"
        LocalCheck["Check process.env<br/>LOCAL_* variables"]
        EdgeCheck["Check Edge Config<br/>Remote flags"]
        DefaultCheck["Use Default Value<br/>From definition"]
    end
    
    subgraph "Usage"
        ServerSide["Server Components<br/>Direct flag access"]
        ClientSide["Client Components<br/>Via Context"]
        Middleware["Middleware<br/>Route protection"]
    end
    
    FlagFile --> FlagSchema
    FlagSchema --> LocalCheck
    LocalCheck -->|Not found| EdgeCheck
    EdgeCheck -->|Not found| DefaultCheck
    
    LocalCheck --> ServerSide
    EdgeCheck --> ServerSide
    DefaultCheck --> ServerSide
    
    ServerSide --> ClientSide
    ServerSide --> Middleware
```

Flags control features such as:
- Stage system availability (`stage`)
- GitHub integration enablement (`github`)
- Vector store features (`vectorStore`)
- Experimental node types (`experimentalNodes`)
- Telemetry and observability (`telemetry`)

**Sources:** [apps/studio.giselles.ai/package.json:66-67](), [apps/studio.giselles.ai/package.json:77-77]()

### Context Data Flow

```mermaid
sequenceDiagram
    participant Browser
    participant RootLayout as "Root Layout<br/>app/layout.tsx"
    participant AuthCheck as "Supabase Auth"
    participant WorkspaceProvider as "WorkspaceProvider"
    participant Database as "Database Queries"
    participant EdgeConfig as "Edge Config API"
    participant Page as "Page Component"
    
    Browser->>RootLayout: Request page
    RootLayout->>AuthCheck: Validate session
    AuthCheck-->>RootLayout: User authenticated
    
    RootLayout->>WorkspaceProvider: Initialize context
    WorkspaceProvider->>Database: Fetch team data
    WorkspaceProvider->>Database: Fetch workspace settings
    WorkspaceProvider->>Database: Fetch integrations
    WorkspaceProvider->>EdgeConfig: Fetch feature flags
    
    Database-->>WorkspaceProvider: Team info
    Database-->>WorkspaceProvider: Settings
    Database-->>WorkspaceProvider: Integrations
    EdgeConfig-->>WorkspaceProvider: Flag values
    
    WorkspaceProvider->>WorkspaceProvider: Merge configurations
    WorkspaceProvider-->>Page: Provide context
    Page->>Page: Render with context
    Page-->>Browser: HTML response
```

The WorkspaceProvider fetches all necessary data during server-side rendering, ensuring that page components have immediate access to configuration without additional client-side requests.

**Sources:** [apps/studio.giselles.ai/package.json:63-67]()

## Stage System and Act Execution

The Stage system provides a production-ready interface for executing published workflows (applications). It separates the execution environment from the workflow designer, allowing end-users to run applications without access to the design interface.

### Stage Interface Architecture

```mermaid
graph TB
    subgraph "Stage Routes"
        StageList["/stage<br/>Application Selection"]
        ActsList["/stage/acts<br/>Execution History"]
        ActDetail["/stage/acts/[actId]<br/>Act Details & Results"]
    end
    
    subgraph "Application Selection UI"
        CarouselView["Carousel View<br/>Featured Applications"]
        ListView["List View<br/>All Applications"]
        FilterControls["Filter Controls<br/>All/History/Latest/Favorites"]
    end
    
    subgraph "Form System"
        DynamicForm["Dynamic Form<br/>Based on Flow Triggers"]
        ParameterInputs["Parameter Inputs<br/>Text, Number, File, etc."]
        ValidationLogic["Validation<br/>Required fields, types"]
    end
    
    subgraph "Execution Flow"
        CreateAct["createAct()<br/>Server Action"]
        StartAct["startAct()<br/>Engine Execution"]
        ActTracking["Acts Table<br/>Status & Metadata"]
        GenerationResults["Generations<br/>Node Outputs"]
    end
    
    subgraph "Data Sources"
        FlowTriggers["flow_triggers Table<br/>Published Applications"]
        ActsTable["acts Table<br/>Execution Records"]
        SequencesTable["sequences Table<br/>Step Tracking"]
        GenerationsTable["generations Table<br/>Results"]
    end
    
    StageList --> CarouselView
    StageList --> ListView
    StageList --> FilterControls
    
    CarouselView --> DynamicForm
    ListView --> DynamicForm
    
    DynamicForm --> ParameterInputs
    DynamicForm --> ValidationLogic
    
    ParameterInputs --> CreateAct
    CreateAct --> StartAct
    StartAct --> ActTracking
    
    ActsList --> ActsTable
    ActDetail --> ActsTable
    ActDetail --> SequencesTable
    ActDetail --> GenerationResults
    
    FlowTriggers --> CarouselView
    FlowTriggers --> ListView
    ActsTable --> ActsList
    SequencesTable --> ActDetail
    GenerationsTable --> ActDetail
```

**Sources:** [apps/studio.giselles.ai/package.json:1-133]()

### Application Selection and Filtering

The Stage page queries the `flow_triggers` table to retrieve published applications. Applications can be filtered by type:

| Filter Type | Description | Query Logic |
|------------|-------------|-------------|
| **All** | All published applications | No filter, ordered by creation date |
| **History** | Applications user has executed | Filter by `acts.user_id = current_user` |
| **Latest** | Recently published applications | Order by `created_at DESC`, limit 10 |
| **Favorites** | User-favorited applications | Filter by `user_favorites.user_id = current_user` |

Each application displays:
- Application name and description
- Required parameters (from trigger configuration)
- Execution count (number of acts created)
- Last execution timestamp
- Thumbnail or icon

**Sources:** [apps/studio.giselles.ai/package.json:1-133]()

### Dynamic Form Generation

```mermaid
graph TB
    subgraph "Form Generation Logic"
        TriggerParams["Trigger Parameters<br/>from flow_triggers.parameters"]
        ParamSchema["Parameter Schema<br/>name, type, required, default"]
        InputFactory["Input Component Factory<br/>Map type to component"]
    end
    
    subgraph "Input Components"
        TextInput["Text Input<br/>string parameters"]
        NumberInput["Number Input<br/>number parameters"]
        FileInput["File Upload<br/>file parameters"]
        SelectInput["Select Input<br/>enum parameters"]
        TextareaInput["Textarea<br/>long text parameters"]
    end
    
    subgraph "Validation"
        RequiredCheck["Required Field Check"]
        TypeValidation["Type Validation"]
        CustomValidation["Custom Validation<br/>min/max, pattern, etc."]
    end
    
    TriggerParams --> ParamSchema
    ParamSchema --> InputFactory
    
    InputFactory --> TextInput
    InputFactory --> NumberInput
    InputFactory --> FileInput
    InputFactory --> SelectInput
    InputFactory --> TextareaInput
    
    TextInput --> RequiredCheck
    NumberInput --> RequiredCheck
    FileInput --> RequiredCheck
    
    RequiredCheck --> TypeValidation
    TypeValidation --> CustomValidation
```

The form system introspects the trigger's parameter definitions and generates appropriate input components. This allows applications to have custom input requirements without UI code changes.

**Sources:** [apps/studio.giselles.ai/package.json:1-133]()

### Act Execution Lifecycle

```mermaid
sequenceDiagram
    participant User
    participant StageUI as "Stage UI<br/>/stage"
    participant ServerAction as "performStageAction<br/>Server Action"
    participant Database as "Database<br/>acts table"
    participant Engine as "GiselleEngine<br/>startAct()"
    participant Storage as "Storage Layer<br/>Generations"
    participant ActDetail as "Act Detail Page<br/>/stage/acts/[actId]"
    
    User->>StageUI: Fill form & submit
    StageUI->>ServerAction: performStageAction(flowTriggerId, params)
    
    ServerAction->>Database: INSERT INTO acts
    Database-->>ServerAction: actId
    
    ServerAction->>Engine: startAct(actId, flowTriggerId, params)
    
    Engine->>Engine: Initialize workflow graph
    Engine->>Engine: Execute nodes
    
    loop For each node
        Engine->>Storage: Write generation results
        Storage-->>Engine: Generation saved
        Engine->>Database: UPDATE acts.status = 'running'
    end
    
    Engine->>Database: UPDATE acts.status = 'completed'
    Engine-->>ServerAction: Execution complete
    
    ServerAction-->>StageUI: Redirect to /stage/acts/[actId]
    StageUI->>ActDetail: Navigate to results
    
    ActDetail->>Database: Fetch act details
    ActDetail->>Storage: Fetch generations
    Database-->>ActDetail: Act metadata
    Storage-->>ActDetail: Generation results
    
    ActDetail-->>User: Display results
```

The act execution creates a record in the `acts` table with status `'created'`, then invokes the Giselle Engine to execute the workflow. The engine updates the act status to `'running'` during execution and `'completed'` or `'failed'` upon completion.

**Sources:** [apps/studio.giselles.ai/package.json:1-133]()

### Act Detail Page Structure

```mermaid
graph TB
    subgraph "Act Detail Page<br/>/stage/acts/[actId]"
        ActHeader["Act Header<br/>Name, Status, Timestamp"]
        SequenceList["Sequence List<br/>Execution Steps"]
        GenerationResults["Generation Results<br/>Node Outputs"]
        Metadata["Execution Metadata<br/>Duration, Parameters"]
    end
    
    subgraph "Sequence Display"
        SequenceItem["Sequence Item"]
        NodeInfo["Node Information<br/>Type, Name"]
        NodeStatus["Node Status<br/>pending/running/completed/failed"]
        NodeTiming["Timing Info<br/>Start, End, Duration"]
    end
    
    subgraph "Generation Display"
        TextGeneration["Text Generation View<br/>Markdown content"]
        ImageGeneration["Image Generation View<br/>Image preview"]
        QueryResults["Query Results View<br/>Retrieved documents"]
        ErrorDisplay["Error Display<br/>Stack trace, message"]
    end
    
    ActHeader --> SequenceList
    ActHeader --> Metadata
    
    SequenceList --> SequenceItem
    SequenceItem --> NodeInfo
    SequenceItem --> NodeStatus
    SequenceItem --> NodeTiming
    
    SequenceItem --> GenerationResults
    GenerationResults --> TextGeneration
    GenerationResults --> ImageGeneration
    GenerationResults --> QueryResults
    GenerationResults --> ErrorDisplay
```

The Act Detail page provides comprehensive visibility into the execution, showing each node's execution status, timing information, and output results. Users can inspect the entire workflow execution trace.

**Sources:** [apps/studio.giselles.ai/package.json:1-133]()

### Database Schema for Stage System

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `flow_triggers` | Published applications | `id`, `flow_id`, `name`, `description`, `parameters`, `is_published` |
| `acts` | Execution records | `id`, `flow_trigger_id`, `user_id`, `status`, `created_at`, `completed_at` |
| `sequences` | Execution step tracking | `id`, `act_id`, `node_id`, `status`, `started_at`, `completed_at` |
| `generations` | Node output results | `id`, `act_id`, `node_id`, `type`, `content`, `metadata` |
| `user_favorites` | User-favorited apps | `user_id`, `flow_trigger_id`, `created_at` |

The schema supports multi-tenancy through team/workspace associations and tracks complete execution history with timing information.

**Sources:** [apps/studio.giselles.ai/package.json:76-76]()

## Vector Store Management Interface

The Vector Store Management Interface provides users with tools to configure and manage knowledge sources for retrieval-augmented generation (RAG). It supports both GitHub repositories and uploaded documents as vector store sources.

### Vector Store Settings UI Structure

```mermaid
graph TB
    subgraph "Settings Routes"
        VectorStoreList["/settings/team/vector-stores<br/>Vector Store List"]
        GitHubRepoConfig["GitHub Repository Configuration"]
        DocumentUpload["Document Upload"]
        ProfileConfig["Embedding Profile Selection"]
    end
    
    subgraph "Repository Management"
        RepoList["Repository List<br/>Installed repos"]
        RepoCard["Repository Card<br/>Status, Ingestion Info"]
        RegisterDialog["Register Dialog<br/>Select repo & content types"]
        IngestionTrigger["Manual Ingestion Trigger<br/>Refresh content"]
    end
    
    subgraph "Document Management"
        DocList["Document List<br/>Uploaded files"]
        DocCard["Document Card<br/>Name, Size, Status"]
        UploadDialog["Upload Dialog<br/>PDF file selection"]
        DocStatus["Document Status<br/>Processing state"]
    end
    
    subgraph "Configuration Options"
        ContentTypes["Content Type Selection<br/>Code/Issues/PRs/Discussions"]
        EmbeddingProfile["Embedding Profile<br/>OpenAI/Google/Cohere"]
        QuotaDisplay["Quota Display<br/>Usage limits"]
    end
    
    VectorStoreList --> RepoList
    VectorStoreList --> DocList
    
    RepoList --> RepoCard
    RepoCard --> RegisterDialog
    RepoCard --> IngestionTrigger
    
    DocList --> DocCard
    DocCard --> UploadDialog
    
    RegisterDialog --> ContentTypes
    RegisterDialog --> EmbeddingProfile
    UploadDialog --> EmbeddingProfile
    
    VectorStoreList --> QuotaDisplay
```

**Sources:** [apps/studio.giselles.ai/package.json:30-38]()

### GitHub Repository Integration

```mermaid
graph TB
    subgraph "Repository Registration Flow"
        SelectRepo["Select Repository<br/>From GitHub installations"]
        SelectContent["Select Content Types<br/>code, issues, prs, discussions"]
        SelectProfile["Select Embedding Profile<br/>OpenAI, Google, Cohere"]
        CreateRecord["createRepositoryIndex()<br/>Server Action"]
    end
    
    subgraph "Ingestion Pipeline"
        TriggerIngestion["triggerManualIngest()<br/>Start background job"]
        FetchContent["Fetch GitHub Content<br/>via GitHub API"]
        ProcessContent["Process Content<br/>Chunking, extraction"]
        GenerateEmbeddings["Generate Embeddings<br/>via embedding service"]
        StoreVectors["Store in pgvector<br/>PostgreSQL"]
    end
    
    subgraph "Status Tracking"
        ContentStatus["vector_store_content_status<br/>Per content type"]
        StatusEnum["Status Values<br/>idle/ingesting/completed/failed"]
        LastIngestion["Last Ingestion<br/>Timestamp, commit hash"]
    end
    
    SelectRepo --> SelectContent
    SelectContent --> SelectProfile
    SelectProfile --> CreateRecord
    
    CreateRecord --> TriggerIngestion
    TriggerIngestion --> FetchContent
    FetchContent --> ProcessContent
    ProcessContent --> GenerateEmbeddings
    GenerateEmbeddings --> StoreVectors
    
    TriggerIngestion --> ContentStatus
    ProcessContent --> ContentStatus
    StoreVectors --> ContentStatus
    ContentStatus --> StatusEnum
    ContentStatus --> LastIngestion
```

The GitHub integration uses Octokit to fetch repository content and the GitHub GraphQL API for issues, pull requests, and discussions. Content is processed asynchronously using Trigger.dev jobs.

**Sources:** [apps/studio.giselles.ai/package.json:43-44](), [apps/studio.giselles.ai/package.json:32-32]()

### Document Upload and Processing

```mermaid
sequenceDiagram
    participant User
    participant UploadUI as "Upload Dialog"
    participant ServerAction as "uploadDocument()<br/>Server Action"
    participant S3Storage as "S3/Supabase Storage"
    participant TriggerJob as "Trigger.dev Job<br/>Document Processing"
    participant Preprocessor as "Document Preprocessor<br/>@giselles-ai/document-preprocessor"
    participant Embedder as "Embedding Service"
    participant Database as "PostgreSQL<br/>pgvector"
    
    User->>UploadUI: Select PDF file
    UploadUI->>ServerAction: uploadDocument(file, profileId)
    
    ServerAction->>S3Storage: Upload file
    S3Storage-->>ServerAction: File URL
    
    ServerAction->>Database: INSERT INTO documents
    Database-->>ServerAction: documentId
    
    ServerAction->>TriggerJob: Enqueue processing job
    TriggerJob->>S3Storage: Download file
    
    TriggerJob->>Preprocessor: extractTextFromPDF(file)
    Preprocessor-->>TriggerJob: Extracted text
    
    TriggerJob->>Preprocessor: normalizeText(text)
    Preprocessor-->>TriggerJob: Normalized chunks
    
    loop For each chunk
        TriggerJob->>Embedder: generateEmbedding(chunk)
        Embedder-->>TriggerJob: Embedding vector
        TriggerJob->>Database: INSERT INTO vector_store_document_chunks
    end
    
    TriggerJob->>Database: UPDATE documents.status = 'completed'
    Database-->>UploadUI: Status update via polling
    UploadUI-->>User: Processing complete
```

Document processing extracts text from PDFs using `@embedpdf/pdfium`, normalizes the text, chunks it into manageable segments, and generates embeddings using the selected profile's embedding model.

**Sources:** [apps/studio.giselles.ai/package.json:30-30](), [apps/studio.giselles.ai/package.json:26-27]()

### Vector Store Database Schema

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `vector_store_github` | GitHub repository configuration | `id`, `workspace_id`, `repo_owner`, `repo_name`, `embedding_profile_id` |
| `vector_store_content_status` | Ingestion status per content type | `vector_store_id`, `content_type`, `status`, `last_ingested_at` |
| `vector_store_github_files` | File-level vector storage | `id`, `vector_store_id`, `file_path`, `content_hash`, `embedding` (vector) |
| `vector_store_github_issues` | Issue-level vector storage | `id`, `vector_store_id`, `issue_number`, `title`, `body`, `embedding` (vector) |
| `vector_store_documents` | Uploaded document metadata | `id`, `workspace_id`, `filename`, `status`, `embedding_profile_id` |
| `vector_store_document_chunks` | Document chunk vectors | `id`, `document_id`, `chunk_index`, `content`, `embedding` (vector) |
| `embedding_profiles` | Embedding model configurations | `id`, `provider`, `model`, `dimensions` |

All embedding columns use the `vector` type from the pgvector extension, enabling efficient similarity searches.

**Sources:** [apps/studio.giselles.ai/package.json:76-76](), [apps/studio.giselles.ai/package.json:38-38]()

### Quota Management

```mermaid
graph TB
    subgraph "Usage Tracking"
        CurrentUsage["Current Usage<br/>Embeddings generated"]
        PlanLimits["Plan Limits<br/>Free/Pro/Enterprise"]
        QuotaCheck["Quota Check<br/>Before operations"]
    end
    
    subgraph "Quota Display"
        ProgressBar["Progress Bar<br/>Visual quota usage"]
        NumericDisplay["Numeric Display<br/>X / Y embeddings"]
        UpgradePrompt["Upgrade Prompt<br/>When approaching limit"]
    end
    
    subgraph "Enforcement"
        BlockRegistration["Block New Registration<br/>When at limit"]
        BlockIngestion["Block Ingestion<br/>When at limit"]
        AllowDeletion["Allow Deletion<br/>To free quota"]
    end
    
    CurrentUsage --> QuotaCheck
    PlanLimits --> QuotaCheck
    
    CurrentUsage --> ProgressBar
    PlanLimits --> NumericDisplay
    
    QuotaCheck --> UpgradePrompt
    QuotaCheck --> BlockRegistration
    QuotaCheck --> BlockIngestion
    
    AllowDeletion --> CurrentUsage
```

Quota enforcement prevents users from exceeding their plan limits. The system tracks the total number of embeddings (vectors) stored and blocks new operations when limits are reached.

**Sources:** [apps/studio.giselles.ai/package.json:1-133]()

### Content Type Configuration

When registering a GitHub repository, users can select which content types to index:

| Content Type | Source | API Used | Indexing Granularity |
|-------------|--------|----------|---------------------|
| **Code** | Repository files | REST API + tarball download | Per-file embeddings |
| **Issues** | GitHub Issues | GraphQL API | Per-issue embeddings (title + body) |
| **Pull Requests** | GitHub PRs | GraphQL API | Per-PR embeddings (title + description) |
| **Discussions** | GitHub Discussions | GraphQL API | Per-discussion embeddings |

Each content type has independent ingestion status tracking, allowing partial updates (e.g., re-ingest issues without re-processing code).

**Sources:** [apps/studio.giselles.ai/package.json:32-32](), [apps/studio.giselles.ai/package.json:43-44]()

## Playground Application

The Playground application (`apps/playground`) provides a minimal development environment for testing workflow functionality without the full production infrastructure. It serves as a rapid prototyping tool for developers.

### Key Differences from Studio

| Aspect | Studio | Playground |
|--------|--------|-----------|
| **Authentication** | Full Supabase Auth with sessions | No authentication |
| **Database** | PostgreSQL with Drizzle ORM | In-memory or file-based storage |
| **Feature Flags** | Edge Config + environment variables | Environment variables only |
| **Integrations** | GitHub, RAG, Vector Stores, all tools | Minimal integrations |
| **Observability** | Sentry, OpenTelemetry, Langfuse | Langfuse only (optional) |
| **Deployment** | Vercel production | Local development only |
| **Routes** | Multiple routes (flow, stage, settings) | Single flow route |

**Sources:** [apps/playground/package.json:1-43](), [apps/studio.giselles.ai/package.json:1-133]()

### Playground Architecture

```mermaid
graph TB
    subgraph "Playground Application"
        PlaygroundApp["Playground App<br/>apps/playground"]
        FlowRoute["Flow Route<br/>/flow/[flowId]"]
    end
    
    subgraph "Shared Components"
        WorkflowDesigner["@giselle-internal/workflow-designer-ui<br/>Complete visual editor"]
        UIComponents["@giselle-internal/ui<br/>UI primitives"]
    end
    
    subgraph "Minimal Engine Config"
        GiselleEngine["@giselles-ai/giselle<br/>Core engine only"]
        FileSystemStorage["File System Storage<br/>Local file storage"]
        SimpleVault["Simple Vault<br/>Environment-based secrets"]
    end
    
    subgraph "Optional Features"
        LangfuseTracing["Langfuse Tracing<br/>Optional observability"]
        SupabaseDriver["Supabase Driver<br/>Optional database"]
    end
    
    PlaygroundApp --> FlowRoute
    FlowRoute --> WorkflowDesigner
    FlowRoute --> UIComponents
    
    WorkflowDesigner --> GiselleEngine
    GiselleEngine --> FileSystemStorage
    GiselleEngine --> SimpleVault
    
    GiselleEngine -.optional.-> LangfuseTracing
    GiselleEngine -.optional.-> SupabaseDriver
```

**Sources:** [apps/playground/package.json:19-31]()

### Simplified Configuration

The Playground uses minimal configuration in `next.config.js`:

```typescript
// Simplified feature flag resolution
const flags = {
  stage: false,  // No Stage system
  github: false, // No GitHub integration
  vectorStore: false, // No vector stores
  telemetry: process.env.LANGFUSE_PUBLIC_KEY ? true : false
}

// Simple engine configuration
const engineConfig = {
  storage: new FileSystemStorage('./storage'),
  vault: new SimpleVault(),
  providers: [
    createOpenAI({ apiKey: process.env.OPENAI_API_KEY }),
    createAnthropic({ apiKey: process.env.ANTHROPIC_API_KEY })
  ]
}
```

This configuration allows developers to test workflow logic without setting up database infrastructure, authentication, or external integrations.

**Sources:** [apps/playground/package.json:19-31]()

### Development Workflow

```mermaid
sequenceDiagram
    participant Developer
    participant Playground as "Playground App<br/>localhost:3000"
    participant WorkflowDesigner as "Workflow Designer"
    participant Engine as "Giselle Engine"
    participant FileSystem as "File System Storage<br/>./storage"
    
    Developer->>Playground: pnpm dev
    Playground->>Playground: Start Next.js dev server
    
    Developer->>WorkflowDesigner: Design workflow
    WorkflowDesigner->>FileSystem: Save workflow graph
    
    Developer->>WorkflowDesigner: Test generation
    WorkflowDesigner->>Engine: createAndStartGenerationRunner()
    
    Engine->>Engine: Execute workflow
    Engine->>FileSystem: Write generation results
    FileSystem-->>Engine: Saved
    
    Engine-->>WorkflowDesigner: Stream results
    WorkflowDesigner-->>Developer: Display output
    
    Developer->>FileSystem: Inspect storage files
    FileSystem-->>Developer: JSON generation data
```

The Playground stores all data in local files under `./storage`, making it easy to inspect and debug workflow execution without database queries.

**Sources:** [apps/playground/package.json:10-10]()

### Use Cases

The Playground is ideal for:

1. **Rapid Prototyping**: Test new node types or workflow patterns without production setup
2. **Integration Testing**: Develop and test new integrations in isolation
3. **Documentation Examples**: Create reproducible examples for documentation
4. **Contributor Onboarding**: New contributors can explore the platform without complex setup
5. **Local Development**: Test engine changes without impacting production infrastructure

**Sources:** [apps/playground/package.json:1-43]()

## Routing and Navigation

### Studio Application Routes

```mermaid
graph TB
    subgraph "Public Routes"
        Home["/"]
        SignIn["/sign-in"]
        SignUp["/sign-up"]
    end
    
    subgraph "Protected Routes"
        Dashboard["/dashboard"]
        FlowList["/flows"]
        FlowDetail["/flow/[flowId]"]
        Stage["/stage"]
        StageActs["/stage/acts"]
        StageActDetail["/stage/acts/[actId]"]
    end
    
    subgraph "Settings Routes"
        SettingsRoot["/settings"]
        TeamSettings["/settings/team"]
        VectorStores["/settings/team/vector-stores"]
        GitHubSettings["/settings/integrations/github"]
        UsageSettings["/settings/usage"]
        BillingSettings["/settings/billing"]
    end
    
    subgraph "API Routes"
        GenerationAPI["/api/generations/[id]"]
        WebhookAPI["/api/webhooks/github"]
        TriggerAPI["/api/trigger"]
    end
    
    Home --> SignIn
    Home --> SignUp
    SignIn --> Dashboard
    SignUp --> Dashboard
    
    Dashboard --> FlowList
    FlowList --> FlowDetail
    Dashboard --> Stage
    Stage --> StageActs
    StageActs --> StageActDetail
    
    Dashboard --> SettingsRoot
    SettingsRoot --> TeamSettings
    TeamSettings --> VectorStores
    SettingsRoot --> GitHubSettings
    SettingsRoot --> UsageSettings
    SettingsRoot --> BillingSettings
    
    FlowDetail -.API call.-> GenerationAPI
    GitHubSettings -.Webhook.-> WebhookAPI
    StageActDetail -.Background job.-> TriggerAPI
```

All protected routes require authentication via Supabase Auth. The middleware validates sessions and redirects unauthenticated users to `/sign-in`.

**Sources:** [apps/studio.giselles.ai/package.json:1-133]()

### Route Protection and Middleware

```mermaid
graph TB
    subgraph "Middleware Flow"
        Request["Incoming Request"]
        Middleware["middleware.ts"]
        SessionCheck["Check Supabase Session"]
        RouteAuth["Route Authorization"]
    end
    
    subgraph "Public Routes"
        AllowPublic["Allow Access<br/>/sign-in, /sign-up, /api/webhooks"]
    end
    
    subgraph "Protected Routes"
        RequireAuth["Require Authentication<br/>All other routes"]
        RedirectLogin["Redirect to /sign-in"]
    end
    
    subgraph "Team-Scoped Routes"
        CheckTeamMembership["Check Team Membership"]
        AllowTeamMember["Allow Access"]
        ForbidNonMember["403 Forbidden"]
    end
    
    Request --> Middleware
    Middleware --> SessionCheck
    SessionCheck --> RouteAuth
    
    RouteAuth --> AllowPublic
    RouteAuth --> RequireAuth
    
    RequireAuth -->|No session| RedirectLogin
    RequireAuth -->|Has session| CheckTeamMembership
    
    CheckTeamMembership -->|Is member| AllowTeamMember
    CheckTeamMembership -->|Not member| ForbidNonMember
```

The middleware enforces both authentication (user logged in) and authorization (user has access to the requested team's resources).

**Sources:** [apps/studio.giselles.ai/package.json:63-65]()

## Build and Development Scripts

### Studio Application Scripts

| Script | Command | Purpose |
|--------|---------|---------|
| `dev` | `next dev --turbopack` | Start development server with Turbopack |
| `dev-debug` | `LOGLEVEL=debug pnpm run dev` | Development with verbose logging |
| `build` | `next build` | Production build |
| `build:analyze` | `ANALYZE=true next build` | Build with bundle analysis |
| `start` | `next start` | Start production server |
| `test` | `vitest run` | Run unit tests |
| `test:e2e` | `playwright test` | Run end-to-end tests |
| `email:dev` | `email dev --dir emails` | React Email preview server |
| `check-types` | `tsc --noEmit` | TypeScript type checking |

**Sources:** [apps/studio.giselles.ai/package.json:9-22]()

### Playground Application Scripts

| Script | Command | Purpose |
|--------|---------|---------|
| `dev` | `next dev --turbopack` | Start development server |
| `build` | `next build --turbopack` | Production build |
| `start` | `next start` | Start production server |
| `clean` | `rm -rf .next .turbo node_modules` | Clean build artifacts |
| `check-types` | `tsc --noEmit` | TypeScript type checking |

**Sources:** [apps/playground/package.json:9-17]()

### Environment Variables

Both applications require environment variables for configuration:

**Studio (Production)**:
```
# Required
DATABASE_URL=postgresql://...
NEXT_PUBLIC_SUPABASE_URL=https://...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...

# Optional
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
GOOGLE_AI_API_KEY=...
FAL_KEY=...
GITHUB_APP_ID=...
GITHUB_APP_PRIVATE_KEY=...
SENTRY_DSN=...
LANGFUSE_PUBLIC_KEY=...
VERCEL_EDGE_CONFIG=...
```

**Playground (Development)**:
```
# Minimal
OPENAI_API_KEY=...

# Optional
ANTHROPIC_API_KEY=...
LANGFUSE_PUBLIC_KEY=...
```

**Sources:** [apps/studio.giselles.ai/package.json:1-133](), [apps/playground/package.json:1-43]()

---

# Page: Studio Application

# Studio Application

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/playground/app/workspaces/[workspaceId]/layout.tsx](apps/playground/app/workspaces/[workspaceId]/layout.tsx)
- [apps/playground/package.json](apps/playground/package.json)
- [apps/studio.giselles.ai/app/deprecated/workspaces/[workspaceId]/layout.tsx](apps/studio.giselles.ai/app/deprecated/workspaces/[workspaceId]/layout.tsx)
- [apps/studio.giselles.ai/app/workspaces/[workspaceId]/data-loader.ts](apps/studio.giselles.ai/app/workspaces/[workspaceId]/data-loader.ts)
- [apps/studio.giselles.ai/flags.ts](apps/studio.giselles.ai/flags.ts)
- [apps/studio.giselles.ai/package.json](apps/studio.giselles.ai/package.json)
- [internal-packages/workflow-designer-ui/package.json](internal-packages/workflow-designer-ui/package.json)
- [package.json](package.json)
- [packages/giselle/package.json](packages/giselle/package.json)
- [packages/giselle/src/react/feature-flags/context.ts](packages/giselle/src/react/feature-flags/context.ts)
- [packages/giselle/src/react/workspace/provider.tsx](packages/giselle/src/react/workspace/provider.tsx)
- [pnpm-lock.yaml](pnpm-lock.yaml)
- [pnpm-workspace.yaml](pnpm-workspace.yaml)

</details>



The Studio Application is the production Next.js application hosted at `studio.giselles.ai` that provides the primary user interface for creating and managing AI workflows. It serves as the main entry point for end users to interact with the Giselle platform, orchestrating workspace management, workflow design, generation execution, and integration with external services.

This page covers the Studio Application's architecture, workspace initialization, context provisioning, and feature flag integration. For details about the workflow designer UI components used within Studio, see [Workflow Designer UI](#4). For the simplified development version of this application, see [Playground Application](#5.2). For information about workspace configuration details and specific features, see [Workspace Configuration and Context](#5.1.1).

## Application Architecture

The Studio Application is a Next.js 15 application organized as a workspace-centric system. Each workspace is identified by a `workspaceId` route parameter and corresponds to an agent in the database.

```mermaid
graph TB
    subgraph "Next.js Application Structure"
        APP["apps/studio.giselles.ai"]
        LAYOUT["app/workspaces/[workspaceId]/layout.tsx"]
        PAGES["Workspace Pages"]
        SETTINGS["Settings Pages"]
        API["API Routes & Server Actions"]
    end
    
    subgraph "Core Dependencies"
        ENGINE["giselleEngine<br/>(NextGiselleEngine instance)"]
        DRIZZLE["db<br/>(Drizzle ORM)"]
        FLAGS["Feature Flags<br/>(flags.ts)"]
    end
    
    subgraph "External Services"
        SUPABASE["Supabase<br/>(Database & Storage)"]
        TRIGGER["Trigger.dev<br/>(Background Jobs)"]
        SENTRY["Sentry<br/>(Error Monitoring)"]
        VERCEL["Vercel<br/>(Hosting & Edge Config)"]
    end
    
    subgraph "React Context Hierarchy"
        WS_PROVIDER["WorkspaceProvider"]
        ZUSTAND["ZustandBridgeProvider"]
        FF_CTX["FeatureFlagContext"]
        TELEM["TelemetryProvider"]
        USAGE["UsageLimitsProvider"]
        INTEG["IntegrationProvider"]
        VECTOR["VectorStoreProvider"]
    end
    
    LAYOUT --> ENGINE
    LAYOUT --> DRIZZLE
    LAYOUT --> FLAGS
    LAYOUT --> WS_PROVIDER
    
    WS_PROVIDER --> FF_CTX
    WS_PROVIDER --> TELEM
    WS_PROVIDER --> USAGE
    WS_PROVIDER --> INTEG
    WS_PROVIDER --> VECTOR
    WS_PROVIDER --> ZUSTAND
    
    ZUSTAND --> PAGES
    
    ENGINE --> TRIGGER
    ENGINE --> SENTRY
    DRIZZLE --> SUPABASE
    FLAGS --> VERCEL
    
    API --> ENGINE
    API --> DRIZZLE
```

**Sources:** [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:1-167]()

The application follows a layered architecture where:
- The workspace layout performs server-side data fetching and authorization
- Multiple React contexts provide scoped data and functionality
- Child pages consume context via hooks
- Server actions handle mutations and integration with background jobs

## Workspace Layout and Initialization

The workspace layout at [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx]() serves as the initialization layer for each workspace. It performs authentication, authorization, data fetching, and context setup before rendering child components.

```mermaid
sequenceDiagram
    participant Browser
    participant Layout as "Layout Server Component"
    participant DB as "Drizzle Database"
    participant Auth as "fetchCurrentUser"
    participant Teams as "Team Services"
    participant Engine as "giselleEngine"
    participant Flags as "Feature Flags"
    participant VectorDB as "Vector Store Queries"
    
    Browser->>Layout: Navigate to /workspaces/{workspaceId}
    Layout->>Layout: Parse & validate workspaceId
    
    Layout->>DB: query.agents.findFirst(workspaceId)
    DB-->>Layout: agent record
    
    Layout->>Auth: fetchCurrentUser()
    Auth-->>Layout: currentUser
    
    Layout->>Teams: isMemberOfTeam(userId, teamDbId)
    Teams-->>Layout: authorization result
    
    alt User not authorized
        Layout-->>Browser: notFound()
    end
    
    par Parallel Data Fetching
        Layout->>Teams: fetchWorkspaceTeam(teamDbId)
        Teams-->>Layout: workspaceTeam
        
        Layout->>Teams: getUsageLimitsForTeam(team)
        Teams-->>Layout: usageLimits
        
        Layout->>Layout: getGitHubIntegrationState(agentDbId)
        Layout-->>Layout: gitHubIntegrationState
        
        Layout->>VectorDB: getGitHubRepositoryIndexes(teamDbId)
        VectorDB-->>Layout: gitHubRepositoryIndexes
        
        Layout->>VectorDB: getDocumentVectorStores(teamDbId)
        VectorDB-->>Layout: documentVectorStores
        
        Layout->>Flags: Evaluate feature flags
        Flags-->>Layout: Feature flag values
        
        Layout->>Engine: getWorkspace(workspaceId, experimental_storage)
        Engine-->>Layout: workspace data
    end
    
    Layout->>Layout: Construct WorkspaceProvider props
    Layout-->>Browser: Render with WorkspaceProvider
```

**Sources:** [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:31-167]()

### Initialization Steps

The layout performs the following initialization sequence:

1. **Workspace ID Validation** [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:38-43]()
   - Parses the `workspaceId` parameter using the `WorkspaceId` schema
   - Returns 404 if validation fails

2. **Agent Lookup** [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:45-50]()
   - Queries the `agents` table for a record matching the workspace ID
   - Returns 404 if no agent exists

3. **Authorization Check** [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:51-60]()
   - Fetches the current user via `fetchCurrentUser()`
   - Verifies the user is a member of the agent's team
   - Returns 404 if authorization fails

4. **Parallel Data Fetching** [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:62-87]()
   - GitHub integration state
   - Workspace team information
   - Usage limits for the team
   - GitHub repository indexes
   - Document vector stores (if feature flag enabled)
   - Feature flag evaluations
   - Workspace data from the engine

5. **Context Provider Setup** [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:90-166]()
   - Constructs props for `WorkspaceProvider`
   - Wraps children with `ZustandBridgeProvider`

## Context Provider Hierarchy

The Studio Application uses a nested context provider hierarchy to make workspace data and functionality available throughout the component tree. This hierarchy is established in the workspace layout and consumed via React hooks.

```mermaid
graph TB
    subgraph "Context Provider Hierarchy"
        WP["WorkspaceProvider<br/>(packages/giselle/.../provider.tsx)"]
        
        subgraph "Nested Contexts"
            FF["FeatureFlagContext<br/>useFeatureFlag()"]
            TELEM["TelemetryProvider<br/>settings prop"]
            FT["FlowTriggerContext<br/>useFlowTrigger()"]
            UL["UsageLimitsProvider<br/>useUsageLimits()"]
            IP["IntegrationProvider<br/>useIntegration()"]
            VS["VectorStoreProvider<br/>useVectorStore()"]
            ZB["ZustandBridgeGenerationProvider<br/>timeout prop"]
        end
        
        CHILDREN["Child Components<br/>(Editor, Toolbar, Properties)"]
    end
    
    WP --> FF
    FF --> TELEM
    TELEM --> FT
    FT --> UL
    UL --> IP
    IP --> VS
    VS --> ZB
    ZB --> CHILDREN
    
    CHILDREN -.->|"useFeatureFlag()"| FF
    CHILDREN -.->|"useUsageLimits()"| UL
    CHILDREN -.->|"useIntegration()"| IP
    CHILDREN -.->|"useVectorStore()"| VS
    CHILDREN -.->|"useFlowTrigger()"| FT
```

**Sources:** [packages/giselle/src/react/workspace/provider.tsx:25-72]()

### Context Providers

| Provider | Hook | Purpose | Props Source |
|----------|------|---------|--------------|
| `FeatureFlagContext` | `useFeatureFlag()` | Feature flag access | [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:73-84]() |
| `TelemetryProvider` | N/A | Analytics metadata injection | [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:120-127]() |
| `FlowTriggerContext` | `useFlowTrigger()` | Flow trigger update callbacks | [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:138-162]() |
| `UsageLimitsProvider` | `useUsageLimits()` | Usage quotas and tier info | [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:69]() |
| `IntegrationProvider` | `useIntegration()` | External integration state | [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:94-101]() |
| `VectorStoreProvider` | `useVectorStore()` | Vector store configuration | [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:103-118]() |
| `ZustandBridgeProvider` | N/A | Bridges workspace data to Zustand | [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:164]() |

**Sources:** [packages/giselle/src/react/workspace/provider.tsx:25-72](), [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:90-166]()

### Context Consumption Example

Components throughout the application consume these contexts using dedicated hooks:

```typescript
// Example from Toolbar component
const { webSearchAction, documentVectorStore } = useFeatureFlag();
const usageLimits = useUsageLimits();
const userTier = usageLimits?.featureTier ?? Tier.enum.free;
```

**Sources:** [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:95-133]()

## Feature Flag System

The Studio Application implements an environment-aware feature flag system that supports both local development and production deployments. Feature flags control the availability of experimental features, integrations, and UI components.

```mermaid
graph LR
    subgraph "Development Environment"
        DEV_ENV["process.env.NODE_ENV === 'development'"]
        LOCAL_VAR["Local Environment Variable<br/>(e.g., STAGE_FLAG=true)"]
        TAKE_LOCAL["takeLocalEnv()<br/>helper function"]
    end
    
    subgraph "Production Environment"
        PROD_ENV["process.env.NODE_ENV !== 'development'"]
        EDGE_CONFIG["Vercel Edge Config<br/>flag__{key}"]
        EDGE_GET["@vercel/edge-config get()"]
    end
    
    subgraph "Flag Definition"
        FLAG_DEF["flag<boolean>()<br/>(flags/next)"]
        DECIDE["decide() method"]
        DEFAULT["defaultValue"]
    end
    
    subgraph "Layout Evaluation"
        LAYOUT_CALL["await stageFlag()"]
        WORKSPACE_PROVIDER["WorkspaceProvider<br/>featureFlag prop"]
    end
    
    subgraph "Component Consumption"
        USE_FLAG["useFeatureFlag() hook"]
        COMPONENT["Toolbar, Properties, etc."]
    end
    
    DEV_ENV --> TAKE_LOCAL
    LOCAL_VAR --> TAKE_LOCAL
    TAKE_LOCAL --> DECIDE
    
    PROD_ENV --> EDGE_GET
    EDGE_CONFIG --> EDGE_GET
    EDGE_GET --> DECIDE
    
    FLAG_DEF --> DECIDE
    DECIDE --> DEFAULT
    DEFAULT --> LAYOUT_CALL
    
    LAYOUT_CALL --> WORKSPACE_PROVIDER
    WORKSPACE_PROVIDER --> USE_FLAG
    USE_FLAG --> COMPONENT
```

**Sources:** [apps/studio.giselles.ai/flags.ts:1-197](), [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:11-19]()

### Feature Flag Definitions

The flag system defines the following feature flags:

| Flag | Environment Variable | Description | Default |
|------|---------------------|-------------|---------|
| `developerFlag` | `DEVELOPER_FLAG` | Enable developer mode | `false` |
| `webSearchActionFlag` | `WEB_SEARCH_ACTION_FLAG` | Enable web search action nodes | `false` |
| `layoutV3Flag` | `LAYOUT_V3_FLAG` | Enable Layout V3 | `undefined` |
| `experimental_storageFlag` | `EXPERIMENTAL_STORAGE_FLAG` | Enable experimental storage backend | `undefined` |
| `stageFlag` | `STAGE_FLAG` | Enable stage system for flow triggering | `undefined` |
| `aiGatewayFlag` | `AI_GATEWAY_FLAG` | Enable AI Gateway routing | `undefined` |
| `resumableGenerationFlag` | `RESUMABLE_GENERATION_FLAG` | Enable resumable generation | `undefined` |
| `googleUrlContextFlag` | `GOOGLE_URL_CONTEXT_FLAG` | Enable Google URL Context tool | `false` |
| `docVectorStoreFlag` | `DOC_VECTOR_STORE_FLAG` | Enable document vector store ingest | `undefined` |

**Sources:** [apps/studio.giselles.ai/flags.ts:17-196]()

### Flag Evaluation Logic

Each flag follows this evaluation pattern:

```mermaid
flowchart TD
    START["Flag Evaluation Starts"]
    CHECK_ENV{"NODE_ENV === 'development'?"}
    CHECK_LOCAL{"Local env var set<br/>and not 'false'?"}
    USE_LOCAL["Return true"]
    CHECK_PROD_ENV{"NODE_ENV !== 'development'?"}
    QUERY_EDGE["Query Vercel Edge Config<br/>flag__{key}"]
    CHECK_EDGE{"Edge Config value<br/>exists?"}
    PARSE_EDGE{"Value === true<br/>or 'true'?"}
    USE_EDGE["Return true"]
    USE_DEFAULT["Return defaultValue"]
    
    START --> CHECK_ENV
    CHECK_ENV -->|Yes| CHECK_LOCAL
    CHECK_LOCAL -->|Yes| USE_LOCAL
    CHECK_LOCAL -->|No| USE_DEFAULT
    
    CHECK_ENV -->|No| CHECK_PROD_ENV
    CHECK_PROD_ENV -->|Yes| QUERY_EDGE
    QUERY_EDGE --> CHECK_EDGE
    CHECK_EDGE -->|Yes| PARSE_EDGE
    CHECK_EDGE -->|No| USE_DEFAULT
    PARSE_EDGE -->|Yes| USE_EDGE
    PARSE_EDGE -->|No| USE_DEFAULT
```

**Sources:** [apps/studio.giselles.ai/flags.ts:4-15](), [apps/studio.giselles.ai/flags.ts:43-79]()

The `takeLocalEnv()` helper function checks if the environment is development and if the specified environment variable is set and not `"false"` [apps/studio.giselles.ai/flags.ts:4-15](). Production environments query Vercel Edge Config using the pattern `flag__{key}` [apps/studio.giselles.ai/flags.ts:49-53]().

### Flag Consumption in Components

Components access feature flags through the `useFeatureFlag()` hook:

```typescript
// From Toolbar component
const { webSearchAction, documentVectorStore } = useFeatureFlag();

// Conditionally render Document Vector Store option
{documentVectorStore && (
  <ToggleGroup.Item value="documentVectorStore" data-tool>
    <DocumentVectorStoreIcon className="w-[20px] h-[20px]" />
    <p className="text-[14px]">Document Vector Store</p>
  </ToggleGroup.Item>
)}
```

**Sources:** [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:95](), [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:370-378]()

The hook throws an error if used outside of a `FeatureFlagContext` provider [packages/giselle/src/react/feature-flags/context.ts:17-25]().

## Data Fetching Pipeline

The workspace layout orchestrates a parallel data fetching pipeline to minimize initialization latency. This pipeline fetches data from multiple sources concurrently.

```mermaid
graph TB
    subgraph "Data Sources"
        DB[(Supabase Database)]
        GITHUB_API["GitHub API"]
        ENGINE["giselleEngine"]
        FLAGS["Feature Flag System"]
    end
    
    subgraph "Fetching Functions"
        FWT["fetchWorkspaceTeam(teamDbId)"]
        GUFT["getUsageLimitsForTeam(team)"]
        GGIS["getGitHubIntegrationState(agentDbId)"]
        GGRI["getGitHubRepositoryIndexes(teamDbId)"]
        GDVS["getDocumentVectorStores(teamDbId)"]
        GW["giselleEngine.getWorkspace(workspaceId)"]
        FLAG_EVAL["Feature Flag Evaluations"]
    end
    
    subgraph "Fetched Data"
        TEAM["workspaceTeam<br/>(type, activeSubscriptionId)"]
        LIMITS["usageLimits<br/>(featureTier, quotas)"]
        GH_STATE["gitHubIntegrationState<br/>(installationId, repositories)"]
        GH_INDEXES["gitHubRepositoryIndexes<br/>(repository, embeddingProfiles)"]
        DOC_STORES["documentVectorStores<br/>(sources, embeddingProfiles)"]
        WS_DATA["workspace data<br/>(nodes, connections, flow)"]
        FF_VALUES["Feature flag boolean values"]
    end
    
    DB --> FWT
    DB --> GUFT
    DB --> GGIS
    DB --> GGRI
    DB --> GDVS
    GITHUB_API --> GGIS
    ENGINE --> GW
    FLAGS --> FLAG_EVAL
    
    FWT --> TEAM
    GUFT --> LIMITS
    GGIS --> GH_STATE
    GGRI --> GH_INDEXES
    GDVS --> DOC_STORES
    GW --> WS_DATA
    FLAG_EVAL --> FF_VALUES
```

**Sources:** [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:62-87]()

### Data Fetching Sequence

The layout performs the following data fetches in parallel:

1. **GitHub Integration State** [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:62]()
   - `getGitHubIntegrationState(agent.dbId)`
   - Returns installation ID and repository list

2. **Workspace Team** [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:64-67]()
   - `fetchWorkspaceTeam(agent.teamDbId)`
   - Returns team type, subscription info, and tier

3. **Usage Limits** [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:69]()
   - `getUsageLimitsForTeam(workspaceTeam)`
   - Calculates quotas based on team tier

4. **GitHub Repository Indexes** [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:70-72]()
   - `getGitHubRepositoryIndexes(workspaceTeam.dbId)`
   - Returns vector store indexes for GitHub repositories

5. **Feature Flags** [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:73-79]()
   - Evaluates each flag (e.g., `await webSearchActionFlag()`)
   - Returns boolean values

6. **Workspace Data** [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:80-83]()
   - `giselleEngine.getWorkspace(workspaceId, experimental_storage)`
   - Returns nodes, connections, and flow configuration

7. **Document Vector Stores** [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:84-87]()
   - `getDocumentVectorStores(workspaceTeam.dbId)` (conditional)
   - Only fetched if `docVectorStoreFlag` is enabled

## Integration Points

The Studio Application integrates with multiple external services and internal packages:

| Integration | Purpose | Configuration |
|-------------|---------|---------------|
| **Giselle Engine** | AI workflow orchestration | [apps/studio.giselles.ai/app/giselle-engine.ts]() |
| **Drizzle ORM** | Database access | [apps/studio.giselles.ai/drizzle/index.ts]() |
| **Trigger.dev** | Background job execution | Configured via `generationTimeout` [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:93]() |
| **Sentry** | Error monitoring | Integrated in engine configuration |
| **Vercel Edge Config** | Production feature flags | Queried via `@vercel/edge-config` [apps/studio.giselles.ai/flags.ts:1]() |
| **Workflow Designer UI** | Visual workflow editor | Consumed via `ZustandBridgeProvider` |

**Sources:** [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:8-29]()

### Flow Trigger Callbacks

The layout provides flow trigger update callbacks that synchronize flow trigger state with the database:

```typescript
flowTrigger={{
  callbacks: {
    flowTriggerUpdate: async (flowTrigger) => {
      "use server";
      await db
        .insert(flowTriggers)
        .values({
          teamDbId: workspaceTeam.dbId,
          sdkFlowTriggerId: flowTrigger.id,
          sdkWorkspaceId: flowTrigger.workspaceId,
          staged:
            flowTrigger.configuration.provider === "manual" &&
            flowTrigger.configuration.staged,
        })
        .onConflictDoUpdate({
          target: flowTriggers.dbId,
          set: {
            staged:
              flowTrigger.configuration.provider === "manual" &&
              flowTrigger.configuration.staged,
          },
        });
    },
  },
}}
```

**Sources:** [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:138-162]()

This callback is invoked when flow triggers are created or updated, ensuring database state remains synchronized with the SDK's flow trigger configuration.

## Comparison with Playground Application

The Playground Application [apps/playground/app/workspaces/[workspaceId]/layout.tsx]() serves as a simplified development environment compared to Studio. The key differences highlight Studio's production-focused architecture:

| Aspect | Studio | Playground |
|--------|--------|-----------|
| **Feature Flags** | Dynamic evaluation via environment variables or Edge Config | Hardcoded static values |
| **Data Fetching** | Extensive parallel fetching (team, usage, integrations, vector stores) | None (no server-side data) |
| **Authorization** | Full team membership verification | None |
| **Integration State** | GitHub integration state with refresh capability | None |
| **Vector Stores** | Full support with GitHub and document stores | None |
| **Usage Limits** | Team-based quota enforcement | None |
| **Telemetry** | Pro plan status and user metadata | None |
| **Flow Triggers** | Database synchronization callbacks | None |

**Sources:** [apps/playground/app/workspaces/[workspaceId]/layout.tsx:4-21](), [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:31-167]()

The Playground's layout is minimal:

```typescript
export default function Layout({ children }: { children: ReactNode }) {
  return (
    <WorkspaceProvider
      featureFlag={{
        webSearchAction: false,
        layoutV3: true,
        experimental_storage: true,
        stage: true,
        aiGateway: false,
        resumableGeneration: false,
        googleUrlContext: false,
        documentVectorStore: false,
      }}
    >
      {children}
    </WorkspaceProvider>
  );
}
```

This simplified architecture makes Playground suitable for rapid development and testing without the overhead of production features like authentication, authorization, and external service integration.

**Sources:** [apps/playground/app/workspaces/[workspaceId]/layout.tsx:4-21]()

---

# Page: Workspace Context and Feature Flags

# Workspace Context and Feature Flags

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/playground/app/workspaces/[workspaceId]/layout.tsx](apps/playground/app/workspaces/[workspaceId]/layout.tsx)
- [apps/studio.giselles.ai/app/deprecated/workspaces/[workspaceId]/layout.tsx](apps/studio.giselles.ai/app/deprecated/workspaces/[workspaceId]/layout.tsx)
- [apps/studio.giselles.ai/app/workspaces/[workspaceId]/data-loader.ts](apps/studio.giselles.ai/app/workspaces/[workspaceId]/data-loader.ts)
- [apps/studio.giselles.ai/flags.ts](apps/studio.giselles.ai/flags.ts)
- [packages/giselle/src/react/feature-flags/context.ts](packages/giselle/src/react/feature-flags/context.ts)
- [packages/giselle/src/react/workspace/provider.tsx](packages/giselle/src/react/workspace/provider.tsx)

</details>



## Purpose and Scope

This document explains the workspace-level context system and feature flag architecture in the Studio application. The `WorkspaceProvider` component serves as the central configuration provider, wrapping multiple React contexts that supply workspace-specific settings, integration states, usage limits, and feature flags to the entire application tree. The feature flag system provides a two-tier resolution strategy: local environment variables for development and Vercel Edge Config for production deployments.

For information about Stage-specific execution contexts, see [6.1.2](#6.1.2). For vector store configuration loaded by the workspace context, see [6.1.3](#6.1.3).

## WorkspaceProvider Architecture

### Context Hierarchy

The `WorkspaceProvider` component at [packages/giselle/src/react/workspace/provider.tsx:22-68]() acts as a composite provider that nests multiple specialized context providers in a specific hierarchy:

```mermaid
graph TB
    App["Application Root"]
    WP["WorkspaceProvider"]
    FFC["FeatureFlagContext"]
    TP["TelemetryProvider"]
    TC["TriggerContext"]
    ULP["UsageLimitsProvider"]
    IP["IntegrationProvider"]
    VSC["VectorStoreContext"]
    ZBG["ZustandBridgeGenerationProvider"]
    Children["Child Components"]
    
    App --> WP
    WP --> FFC
    FFC --> TP
    TP --> TC
    TC --> ULP
    ULP --> IP
    IP --> VSC
    VSC --> ZBG
    ZBG --> Children
    
    FFC -.provides.-> FFV["webSearchAction<br/>layoutV3<br/>stage<br/>aiGateway<br/>aiGatewayUnsupportedModels<br/>googleUrlContext"]
    TP -.provides.-> TV["telemetry settings<br/>metadata"]
    TC -.provides.-> TCV["trigger callbacks"]
    ULP -.provides.-> ULV["usage limits"]
    IP -.provides.-> IV["github integration<br/>refresh callbacks"]
    VSC -.provides.-> VSV["githubRepositoryIndexes<br/>documentStores<br/>setting paths"]
    ZBG -.provides.-> ZBGV["generation timeout<br/>generation bridge"]
```

**Sources:** [packages/giselle/src/react/workspace/provider.tsx:22-68]()

### Provider Props and Configuration

The `WorkspaceProvider` accepts configuration for each nested context:

| Prop | Type | Purpose |
|------|------|---------|
| `featureFlag` | `FeatureFlagContextValue` | Feature flag states |
| `integration` | `IntegrationProviderProps` | GitHub integration state and refresh callback |
| `usageLimits` | `UsageLimits` | Plan-based quota information |
| `telemetry` | `TelemetrySettings` | Observability configuration and metadata |
| `vectorStore` | `VectorStoreContextValue` | Vector store indexes and settings paths |
| `trigger` | `TriggerContextValue` | Trigger update callbacks |
| `generationTimeout` | `number` | Generation execution timeout in milliseconds |

**Sources:** [packages/giselle/src/react/workspace/provider.tsx:22-40]()

## Feature Flag System

### Flag Definition Structure

Feature flags are defined in [apps/studio.giselles.ai/flags.ts:1-177]() using the `flag()` function from the `flags/next` package. Each flag follows a consistent structure:

```mermaid
graph LR
    FlagDef["flag() Definition"]
    Key["key: string<br/>Unique identifier"]
    Decide["decide()<br/>Resolution logic"]
    Desc["description: string"]
    Options["options: array<br/>Allowed values"]
    Default["defaultValue: T<br/>Fallback value"]
    
    FlagDef --> Key
    FlagDef --> Decide
    FlagDef --> Desc
    FlagDef --> Options
    FlagDef --> Default
    
    Decide --> LocalCheck["takeLocalEnv()<br/>Development mode"]
    Decide --> EdgeCheck["Edge Config<br/>Production mode"]
```

**Sources:** [apps/studio.giselles.ai/flags.ts:17-177]()

### Two-Tier Resolution Strategy

The flag resolution strategy differs between development and production environments:

```mermaid
sequenceDiagram
    participant Caller as "Flag Consumer"
    participant Flag as "flag.decide()"
    participant Helper as "takeLocalEnv()"
    participant Env as "process.env"
    participant Edge as "Vercel Edge Config"
    
    Caller->>Flag: await flag()
    
    alt NODE_ENV === "development"
        Flag->>Helper: takeLocalEnv(key)
        Helper->>Env: Check process.env[key]
        alt env var undefined or "false"
            Env-->>Helper: false
        else env var truthy
            Env-->>Helper: true
        end
        Helper-->>Flag: boolean
    else Production
        Flag->>Edge: get(`flag__${key}`)
        alt Edge Config undefined
            Edge-->>Flag: defaultValue
        else Edge Config defined
            Edge-->>Flag: edgeConfig === true || "true"
        end
    end
    
    Flag-->>Caller: boolean
```

**Sources:** [apps/studio.giselles.ai/flags.ts:4-177]()

### takeLocalEnv Helper Function

The `takeLocalEnv()` helper at [apps/studio.giselles.ai/flags.ts:4-15]() implements the local environment variable resolution logic:

```typescript
function takeLocalEnv(localEnvironmentKey: string) {
	if (process.env.NODE_ENV !== "development") {
		return false;
	}
	if (
		process.env[localEnvironmentKey] === undefined ||
		process.env[localEnvironmentKey] === "false"
	) {
		return false;
	}
	return true;
}
```

This function ensures flags are only read from local environment variables in development mode. In non-development environments, it always returns `false`, forcing the flag's `decide()` method to fall back to Edge Config or default values.

**Sources:** [apps/studio.giselles.ai/flags.ts:4-15]()

### Available Feature Flags

The Studio application defines the following feature flags:

| Flag Key | Environment Variable | Default | Description |
|----------|---------------------|---------|-------------|
| `developer` | `DEVELOPER_FLAG` | `false` | Enable developer features |
| `web-search-action` | `WEB_SEARCH_ACTION_FLAG` | `false` | Enable web search action nodes |
| `layout-v3` | `LAYOUT_V3_FLAG` | `false` | Enable Layout V3 interface |
| `experimental-storage` | `EXPERIMENTAL_STORAGE_FLAG` | `true` | Enable experimental storage backend |
| `stage` | `STAGE_FLAG` | `false` | Enable Stage production execution interface |
| `ai-gateway` | `AI_GATEWAY_FLAG` | `false` | Enable AI Gateway for request routing |
| `ai-gateway-unsupported-models` | `AI_GATEWAY_UNSUPPORTED_MODELS_FLAG` | `false` | Allow unsupported models through AI Gateway |
| `google-url-context` | `GOOGLE_URL_CONTEXT_FLAG` | `false` | Enable Google URL context tool |
| `new-editor` | `NEW_EDITOR_FLAG` | `false` | Enable new editor interface |

**Sources:** [apps/studio.giselles.ai/flags.ts:17-177]()

### Flag Resolution Examples

The `layoutV3Flag` at [apps/studio.giselles.ai/flags.ts:43-60]() demonstrates the typical resolution pattern:

```typescript
export const layoutV3Flag = flag<boolean>({
	key: "layout-v3",
	async decide() {
		if (process.env.NODE_ENV === "development") {
			return takeLocalEnv("LAYOUT_V3_FLAG");
		}
		const edgeConfig = await get(`flag__${this.key}`);
		if (edgeConfig === undefined) {
			return false;
		}
		return edgeConfig === true || edgeConfig === "true";
	},
	description: "Enable Layout V3",
	options: [
		{ value: false, label: "disable" },
		{ value: true, label: "Enable" },
	],
});
```

**Sources:** [apps/studio.giselles.ai/flags.ts:43-60]()

## Feature Flag Context

### FeatureFlagContext Definition

The `FeatureFlagContext` at [packages/giselle/src/react/feature-flags/context.ts:1-24]() defines the interface for accessing feature flags in React components:

```typescript
export interface FeatureFlagContextValue {
	webSearchAction: boolean;
	layoutV3: boolean;
	stage: boolean;
	aiGateway: boolean;
	aiGatewayUnsupportedModels: boolean;
	googleUrlContext: boolean;
}
```

Components consume these flags using the `useFeatureFlag()` hook at [packages/giselle/src/react/feature-flags/context.ts:15-23]().

**Sources:** [packages/giselle/src/react/feature-flags/context.ts:1-24]()

### Context Initialization

The `WorkspaceProvider` initializes the `FeatureFlagContext` with default values at [packages/giselle/src/react/workspace/provider.tsx:42-52]():

```typescript
<FeatureFlagContext
	value={{
		webSearchAction: featureFlag?.webSearchAction ?? false,
		layoutV3: featureFlag?.layoutV3 ?? false,
		stage: featureFlag?.stage ?? false,
		aiGateway: featureFlag?.aiGateway ?? false,
		aiGatewayUnsupportedModels:
			featureFlag?.aiGatewayUnsupportedModels ?? false,
		googleUrlContext: featureFlag?.googleUrlContext ?? false,
	}}
>
```

All flags default to `false` if not provided, ensuring safe fallback behavior.

**Sources:** [packages/giselle/src/react/workspace/provider.tsx:42-52]()

## Server-Side Flag Loading

### Data Loading Pattern

The `dataLoader` function at [apps/studio.giselles.ai/app/workspaces/[workspaceId]/data-loader.ts:21-86]() evaluates all feature flags server-side before rendering:

```mermaid
graph TB
    Request["HTTP Request<br/>/workspaces/[id]"]
    DataLoader["dataLoader()"]
    
    subgraph "Flag Evaluation"
        WSA["webSearchActionFlag()"]
        LV3["layoutV3Flag()"]
        STG["stageFlag()"]
        AIG["aiGatewayFlag()"]
        AIGU["aiGatewayUnsupportedModelsFlag()"]
        GUC["googleUrlContextFlag()"]
    end
    
    subgraph "Other Data Loading"
        User["fetchCurrentUser()"]
        Team["fetchWorkspaceTeam()"]
        Limits["getUsageLimitsForTeam()"]
        GitHub["getGitHubIntegrationState()"]
        Repos["getGitHubRepositoryIndexes()"]
        Docs["getDocumentVectorStores()"]
        WD["giselleEngine.getWorkspace()"]
    end
    
    Assembly["Assemble LoaderData"]
    Layout["Layout Component"]
    WP["WorkspaceProvider"]
    
    Request --> DataLoader
    DataLoader --> WSA
    DataLoader --> LV3
    DataLoader --> STG
    DataLoader --> AIG
    DataLoader --> AIGU
    DataLoader --> GUC
    DataLoader --> User
    DataLoader --> Team
    DataLoader --> Limits
    DataLoader --> GitHub
    DataLoader --> Repos
    DataLoader --> Docs
    DataLoader --> WD
    
    WSA --> Assembly
    LV3 --> Assembly
    STG --> Assembly
    AIG --> Assembly
    AIGU --> Assembly
    GUC --> Assembly
    User --> Assembly
    Team --> Assembly
    Limits --> Assembly
    GitHub --> Assembly
    Repos --> Assembly
    Docs --> Assembly
    WD --> Assembly
    
    Assembly --> Layout
    Layout --> WP
```

**Sources:** [apps/studio.giselles.ai/app/workspaces/[workspaceId]/data-loader.ts:21-86]()

### Feature Flag Evaluation

The data loader evaluates each flag using `await`:

```typescript
const webSearchAction = await webSearchActionFlag();
const layoutV3 = await layoutV3Flag();
const stage = await stageFlag();
const aiGateway = await aiGatewayFlag();
const aiGatewayUnsupportedModels = await aiGatewayUnsupportedModelsFlag();
const googleUrlContext = await googleUrlContextFlag();
```

These evaluated values are then packaged into the `featureFlags` object at [apps/studio.giselles.ai/app/workspaces/[workspaceId]/data-loader.ts:77-84]() and returned from the loader.

**Sources:** [apps/studio.giselles.ai/app/workspaces/[workspaceId]/data-loader.ts:51-84]()

## Configuration Cascading Flow

### Complete Data Flow

The configuration flows from server-side loading through the provider hierarchy to client components:

```mermaid
sequenceDiagram
    participant Route as "Route Handler"
    participant Loader as "dataLoader()"
    participant Flags as "Flag Definitions"
    participant EdgeConfig as "Vercel Edge Config"
    participant Layout as "Layout Component"
    participant WP as "WorkspaceProvider"
    participant Child as "Child Component"
    participant Hook as "useFeatureFlag()"
    
    Route->>Loader: Load workspace data
    
    loop For each flag
        Loader->>Flags: await flagFunction()
        Flags->>Flags: Call decide()
        alt Development
            Flags->>Flags: Check process.env
        else Production
            Flags->>EdgeConfig: get(`flag__${key}`)
            EdgeConfig-->>Flags: value or undefined
        end
        Flags-->>Loader: boolean
    end
    
    Loader-->>Layout: LoaderData with featureFlags
    Layout->>WP: Pass featureFlag prop
    WP->>WP: Initialize FeatureFlagContext
    WP->>Child: Render children
    Child->>Hook: useFeatureFlag()
    Hook-->>Child: FeatureFlagContextValue
```

**Sources:** [apps/studio.giselles.ai/app/workspaces/[workspaceId]/data-loader.ts:21-86](), [packages/giselle/src/react/workspace/provider.tsx:22-68](), [apps/studio.giselles.ai/flags.ts:1-177]()

### Deprecated Layout Example

The deprecated layout at [apps/studio.giselles.ai/app/deprecated/workspaces/[workspaceId]/layout.tsx:25-153]() demonstrates the complete integration pattern:

```typescript
export default async function Layout({ params, children }) {
	// ... authentication and data loading ...
	
	const webSearchAction = await webSearchActionFlag();
	const layoutV3 = await layoutV3Flag();
	const stage = await stageFlag();
	const aiGateway = await aiGatewayFlag();
	const aiGatewayUnsupportedModels = await aiGatewayUnsupportedModelsFlag();
	const googleUrlContext = await googleUrlContextFlag();
	
	return (
		<WorkspaceProvider
			generationTimeout={3600 * 1000}
			integration={{ /* ... */ }}
			vectorStore={{ /* ... */ }}
			usageLimits={usageLimits}
			telemetry={{ /* ... */ }}
			featureFlag={{
				webSearchAction,
				layoutV3,
				stage,
				aiGateway,
				aiGatewayUnsupportedModels,
				googleUrlContext,
			}}
			trigger={{ /* ... */ }}
		>
			<ZustandBridgeProvider data={data}>
				{children}
			</ZustandBridgeProvider>
		</WorkspaceProvider>
	);
}
```

**Sources:** [apps/studio.giselles.ai/app/deprecated/workspaces/[workspaceId]/layout.tsx:25-153]()

## Application-Specific Configuration

### Playground Configuration

The Playground application at [apps/playground/app/workspaces/[workspaceId]/layout.tsx:4-19]() uses a simplified, hardcoded configuration:

```typescript
export default function Layout({ children }: { children: ReactNode }) {
	return (
		<WorkspaceProvider
			featureFlag={{
				webSearchAction: false,
				layoutV3: true,
				stage: true,
				aiGateway: false,
				aiGatewayUnsupportedModels: false,
				googleUrlContext: false,
			}}
		>
			{children}
		</WorkspaceProvider>
	);
}
```

This approach bypasses the flag evaluation system entirely, providing static configuration suitable for development and testing environments.

**Sources:** [apps/playground/app/workspaces/[workspaceId]/layout.tsx:4-19]()

### Studio vs Playground Differences

| Aspect | Studio | Playground |
|--------|--------|-----------|
| Flag resolution | Dynamic (env vars + Edge Config) | Static hardcoded values |
| Additional contexts | Integration, UsageLimits, Telemetry, VectorStore, Trigger | FeatureFlag only |
| Generation timeout | 3600 seconds (1 hour) | Default |
| Authentication | Full user/team verification | Simplified |
| Database integration | Full workspace/team data loading | Minimal |

**Sources:** [apps/studio.giselles.ai/app/deprecated/workspaces/[workspaceId]/layout.tsx:25-153](), [apps/playground/app/workspaces/[workspaceId]/layout.tsx:4-19]()

## Context Access Patterns

### Nested Context Dependencies

The `WorkspaceProvider` nesting order ensures that contexts can access outer contexts if needed:

```mermaid
graph TB
    FF["FeatureFlagContext<br/>Outermost"]
    T["TelemetryProvider<br/>Can access flags"]
    TR["TriggerContext<br/>Can access flags & telemetry"]
    UL["UsageLimitsProvider<br/>Can access all above"]
    INT["IntegrationProvider<br/>Can access all above"]
    VS["VectorStoreContext<br/>Can access all above"]
    ZBG["ZustandBridgeGenerationProvider<br/>Innermost<br/>Can access all contexts"]
    
    FF --> T
    T --> TR
    TR --> UL
    UL --> INT
    INT --> VS
    VS --> ZBG
```

This hierarchical structure enables inner contexts to conditionally adjust behavior based on feature flags or other outer context values.

**Sources:** [packages/giselle/src/react/workspace/provider.tsx:42-66]()

---

# Page: Stage System and Act Execution

# Stage System and Act Execution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/playground/.gitignore](apps/playground/.gitignore)
- [apps/studio.giselles.ai/app/(main)/workspaces/actions.ts](apps/studio.giselles.ai/app/(main)/workspaces/actions.ts)
- [apps/studio.giselles.ai/app/api/workspaces/route.ts](apps/studio.giselles.ai/app/api/workspaces/route.ts)
- [apps/studio.giselles.ai/app/stage/(top)/actions.ts](apps/studio.giselles.ai/app/stage/(top)/actions.ts)
- [apps/studio.giselles.ai/app/stage/(top)/circular-carousel.module.css](apps/studio.giselles.ai/app/stage/(top)/circular-carousel.module.css)
- [apps/studio.giselles.ai/app/stage/(top)/circular-carousel.tsx](apps/studio.giselles.ai/app/stage/(top)/circular-carousel.tsx)
- [apps/studio.giselles.ai/app/stage/(top)/form-input-renderer.tsx](apps/studio.giselles.ai/app/stage/(top)/form-input-renderer.tsx)
- [apps/studio.giselles.ai/app/stage/(top)/form.tsx](apps/studio.giselles.ai/app/stage/(top)/form.tsx)
- [apps/studio.giselles.ai/app/stage/(top)/helpers.ts](apps/studio.giselles.ai/app/stage/(top)/helpers.ts)
- [apps/studio.giselles.ai/app/stage/(top)/page.tsx](apps/studio.giselles.ai/app/stage/(top)/page.tsx)
- [apps/studio.giselles.ai/app/stage/(top)/resizable-layout.tsx](apps/studio.giselles.ai/app/stage/(top)/resizable-layout.tsx)
- [apps/studio.giselles.ai/app/stage/(top)/services.ts](apps/studio.giselles.ai/app/stage/(top)/services.ts)
- [apps/studio.giselles.ai/app/stage/(top)/settings-dialog.tsx](apps/studio.giselles.ai/app/stage/(top)/settings-dialog.tsx)
- [apps/studio.giselles.ai/app/stage/(top)/team-card.tsx](apps/studio.giselles.ai/app/stage/(top)/team-card.tsx)
- [apps/studio.giselles.ai/app/stage/(top)/types.ts](apps/studio.giselles.ai/app/stage/(top)/types.ts)
- [apps/studio.giselles.ai/app/stage/acts/[actId]/actions.ts](apps/studio.giselles.ai/app/stage/acts/[actId]/actions.ts)
- [apps/studio.giselles.ai/app/stage/acts/[actId]/lib/data.ts](apps/studio.giselles.ai/app/stage/acts/[actId]/lib/data.ts)
- [apps/studio.giselles.ai/app/stage/acts/[actId]/lib/utils.ts](apps/studio.giselles.ai/app/stage/acts/[actId]/lib/utils.ts)
- [apps/studio.giselles.ai/app/stage/acts/components/filterable-acts-list.tsx](apps/studio.giselles.ai/app/stage/acts/components/filterable-acts-list.tsx)
- [apps/studio.giselles.ai/app/stage/acts/page.tsx](apps/studio.giselles.ai/app/stage/acts/page.tsx)
- [apps/studio.giselles.ai/app/stage/acts/types/index.ts](apps/studio.giselles.ai/app/stage/acts/types/index.ts)
- [apps/studio.giselles.ai/app/stage/layout.tsx](apps/studio.giselles.ai/app/stage/layout.tsx)
- [apps/studio.giselles.ai/app/stage/showcase/[appId]/actions.ts](apps/studio.giselles.ai/app/stage/showcase/[appId]/actions.ts)
- [apps/studio.giselles.ai/app/stage/showcase/[appId]/page.tsx](apps/studio.giselles.ai/app/stage/showcase/[appId]/page.tsx)

</details>



## Purpose and Scope

The Stage system provides a production execution environment for published workflows in the Studio application. It allows end-users to execute workflows without accessing the workflow designer interface. Users select published flow triggers (applications), provide input parameters through dynamically generated forms, and initiate Act executions. The system maintains comprehensive execution history with filtering and search capabilities.

This document covers the Stage UI (`/stage` route), Act creation via `performStageAction`, and the Acts list interface (`/stage/acts`). For the underlying Act execution engine and sequence orchestration, see section 2.4. For workflow designer integration, see section 5.

**Key Routes:**
- `/stage` - Main application selection and execution interface
- `/stage/acts` - Task list with search and filtering
- `/stage/acts/[actId]` - Individual Act execution details
- `/stage/acts/[actId]/[stepId]` - Specific step view within an Act

**Sources:** [apps/studio.giselles.ai/app/stage/(top)/page.tsx:1-169](), [apps/studio.giselles.ai/app/stage/(top)/actions.ts:1-51](), [apps/studio.giselles.ai/app/stage/acts/page.tsx:1-147]()

## System Architecture

The Stage system implements a three-layer architecture separating presentation, server actions, and data access. Components communicate through Next.js server actions with database persistence and Giselle Engine integration.

**System Component Diagram**

```mermaid
graph TB
    subgraph "Client Components"
        FormContainer["FormContainer<br/>app/stage/(top)/form.tsx"]
        CircularCarousel["CircularCarousel<br/>circular-carousel.tsx"]
        FormInputRenderer["FormInputRenderer<br/>form-input-renderer.tsx"]
        FilterableActsList["FilterableActsList<br/>acts/components/filterable-acts-list.tsx"]
    end
    
    subgraph "Server Components & Actions"
        StagePage["StagePage<br/>app/stage/(top)/page.tsx"]
        ActsPage["StageActsPage<br/>acts/page.tsx"]
        performStageAction["performStageAction<br/>actions.ts"]
        fetchFlowTriggers["fetchFlowTriggers<br/>services.ts"]
        fetchEnrichedActs["fetchEnrichedActs<br/>services.ts"]
        enrichActWithNavigationData["enrichActWithNavigationData"]
    end
    
    subgraph "Data Layer"
        giselleEngine["giselleEngine<br/>NextGiselleEngine instance"]
        dbQuery["db.query.acts"]
        flowTriggersTable["db.query.flowTriggers"]
        teamsTable["db.query.teams"]
    end
    
    subgraph "Helper Functions"
        createInputsFromTrigger["createInputsFromTrigger<br/>helpers.ts:8-33"]
        parseFormInputs["parseFormInputs<br/>helpers.ts:35-80"]
        toParameterItems["toParameterItems<br/>helpers.ts:82-115"]
    end
    
    StagePage --> fetchFlowTriggers
    StagePage --> fetchEnrichedActs
    StagePage --> FormContainer
    
    FormContainer --> CircularCarousel
    FormContainer --> FormInputRenderer
    FormContainer --> createInputsFromTrigger
    FormContainer --> parseFormInputs
    FormContainer --> performStageAction
    
    ActsPage --> enrichActWithNavigationData
    ActsPage --> FilterableActsList
    
    performStageAction --> giselleEngine
    performStageAction --> dbQuery
    
    fetchFlowTriggers --> flowTriggersTable
    fetchFlowTriggers --> teamsTable
    fetchFlowTriggers --> giselleEngine
    
    fetchEnrichedActs --> dbQuery
    fetchEnrichedActs --> enrichActWithNavigationData
    
    enrichActWithNavigationData --> giselleEngine
    
    parseFormInputs --> toParameterItems
```

**Sources:** [apps/studio.giselles.ai/app/stage/(top)/page.tsx:1-169](), [apps/studio.giselles.ai/app/stage/(top)/form.tsx:1-391](), [apps/studio.giselles.ai/app/stage/(top)/actions.ts:1-51](), [apps/studio.giselles.ai/app/stage/(top)/services.ts:1-234](), [apps/studio.giselles.ai/app/stage/acts/page.tsx:1-147]()

## Flow Trigger System

Flow triggers define executable entry points for workflows. The Stage page fetches available triggers for the user's teams and displays them as selectable apps.

### FlowTrigger Data Structure

Flow triggers are fetched from the database and enriched with workspace information:

| Property | Type | Description |
|----------|------|-------------|
| `id` | `FlowTriggerId` | Unique trigger identifier |
| `workspaceId` | `string` | Associated workspace ID |
| `nodeId` | `string` | Node ID in the workflow graph |
| `workspaceName` | `string` | Display name for the app |
| `teamId` | `TeamId` | Owning team identifier |
| `configuration` | `object` | Provider-specific configuration (manual or GitHub) |

### Trigger Configuration Types

The system supports two trigger provider types:

**Manual Triggers** - User-initiated with configurable parameters:
```typescript
{
  provider: "manual",
  event: {
    parameters: [
      { id: string, name: string, type: "text" | "number" | "multiline-text", required: boolean }
    ]
  }
}
```

**GitHub Triggers** - Webhook-based with no user-configurable parameters:
```typescript
{
  provider: "github",
  event: { /* webhook configuration */ }
}
```

**Sources:** [apps/studio.giselles.ai/app/stage/(top)/page.tsx:41-41](), [apps/studio.giselles.ai/app/stage/(top)/helpers.ts:9-34](), [apps/studio.giselles.ai/app/stage/(top)/types.ts:1-38]()

## Form Container and Input Rendering

The `FormContainer` component manages team selection, app (flow trigger) selection, and parameter input through a multi-step form flow.

```mermaid
stateDiagram-v2
    [*] --> TeamSelection
    TeamSelection --> AppSelection: team selected
    AppSelection --> InputForm: app selected (manual trigger)
    AppSelection --> Submit: app selected (GitHub trigger)
    InputForm --> Validation: submit clicked
    Validation --> InputForm: validation errors
    Validation --> PerformAction: valid inputs
    PerformAction --> [*]: Act created
```

### Form State Management

The form maintains local state for:
- `teamId`: Currently selected team
- `appId`: Currently selected flow trigger ID
- `displayCategory`: Filter category (all/history/latest/favorites - UI only)
- `validationErrors`: Field-level validation error messages
- `isPending`: Submission in progress flag

**Sources:** [apps/studio.giselles.ai/app/stage/(top)/form.tsx:49-121]()

### Dynamic Input Generation

Inputs are dynamically created from the flow trigger configuration using `createInputsFromTrigger`:

**Input Creation Logic:**
1. Check trigger provider type
2. For manual triggers, map each parameter to a `FormInput` object
3. For GitHub triggers, return empty array (no user inputs)

**FormInput Structure:**
```typescript
type FormInput = {
  name: string;           // Parameter ID
  label: string;          // Display name
  type: "text" | "number" | "multiline-text";
  required: boolean;
}
```

**Sources:** [apps/studio.giselles.ai/app/stage/(top)/helpers.ts:9-34](), [apps/studio.giselles.ai/app/stage/(top)/form.tsx:176-176]()

### Input Rendering Component

The `FormInputRenderer` component renders form fields based on the input type:

| Input Type | HTML Element | Attributes |
|------------|--------------|------------|
| `text` | `<input type="text">` | Standard text input |
| `number` | `<input type="number">` | Numeric input with validation |
| `multiline-text` | `<textarea rows={4}>` | Multi-line text area |

Each field includes:
- Label with required indicator (`*`)
- ARIA attributes for accessibility (`aria-required`, `aria-invalid`, `aria-describedby`)
- Validation error display with role="alert"
- Disabled state during form submission

**Sources:** [apps/studio.giselles.ai/app/stage/(top)/form-input-renderer.tsx:1-117]()

### Form Validation and Parsing

Form validation occurs in `parseFormInputs`:

**Validation Rules:**
1. Required fields must have non-empty values
2. Number fields must parse to valid numbers (not NaN)
3. Empty optional fields are preserved as empty strings

**Parsing Flow:**
```mermaid
graph LR
    FormData["FormData<br/>from form submission"]
    Validate["parseFormInputs<br/>validation"]
    Errors["ValidationErrors<br/>object"]
    Values["FormValues<br/>object"]
    Items["ParameterItem[]<br/>for Act creation"]
    
    FormData --> Validate
    Validate --> Errors
    Validate --> Values
    Values --> ToItems["toParameterItems"]
    ToItems --> Items
```

**Sources:** [apps/studio.giselles.ai/app/stage/(top)/helpers.ts:36-81](), [apps/studio.giselles.ai/app/stage/(top)/helpers.ts:83-116](), [apps/studio.giselles.ai/app/stage/(top)/form.tsx:178-200]()

## App Selection UI

The system provides two UI modes for app selection: carousel view and list view.

### Circular Carousel View

The `CircularCarousel` component displays apps in a semi-circular arrangement with advanced interaction:

**Key Features:**
- Semicircular layout with configurable visible cards (3-7 based on screen width)
- Drag-to-navigate (horizontal swipe) and drag-to-select (vertical swipe)
- Keyboard navigation (arrow keys, Enter/Space)
- Animation states: normal → selected → animating-down → inserted
- Responsive card positioning with tilt rotation

**Card Position Calculation:**
```
x = centerX + radius * cos(angle + dragOffset * 0.008)
y = centerY - radius * sin(angle) - cardHeight
rotation = -(angle - π/2) * (180/π)
```

**Sources:** [apps/studio.giselles.ai/app/stage/(top)/circular-carousel.tsx:34-665]()

### List View

The list view displays apps in a 2-column grid with selection highlighting:
- App icon + workspace name + trigger label
- Selected app highlighted with blue border (`border-blue-500/50`)
- Click to select, displays input form in slide-up modal

**Sources:** [apps/studio.giselles.ai/app/stage/(top)/form.tsx:280-338]()

## Act Creation and Execution

The `performStageAction` server action in [app/stage/(top)/actions.ts:9-51]() orchestrates Act creation through the Giselle Engine. This function bridges the Stage UI with the core execution engine.

### Act Creation Flow with Code Entities

```mermaid
sequenceDiagram
    participant User
    participant FormContainer
    participant parseFormInputs
    participant toParameterItems
    participant performStageAction
    participant fetchCurrentUser
    participant giselleEngine.createAct
    participant db.insert
    participant giselleEngine.startAct
    participant revalidatePath
    
    User->>FormContainer: "Submit form"
    FormContainer->>parseFormInputs: "formData, inputs[]"
    parseFormInputs-->>FormContainer: "{errors, values}"
    FormContainer->>toParameterItems: "inputs[], values"
    toParameterItems-->>FormContainer: "ParameterItem[]"
    
    FormContainer->>performStageAction: "PerformStagePayloads"
    
    performStageAction->>fetchCurrentUser: "Get authenticated user"
    fetchCurrentUser-->>performStageAction: "user with dbId"
    
    performStageAction->>giselleEngine.createAct: "{workspaceId, nodeId, inputs, generationOriginType}"
    giselleEngine.createAct-->>performStageAction: "{act: {id: ActId}}"
    
    performStageAction->>db.insert: "acts.values({teamDbId, directorDbId, sdkActId, ...})"
    
    performStageAction->>giselleEngine.startAct: "{actId, generationOriginType}"
    
    performStageAction->>revalidatePath: "/stage"
    
    performStageAction-->>FormContainer: "void (success)"
```

### Server Action Implementation Details

**Function Signature:**
```typescript
async function performStageAction(
  payloads: PerformStagePayloads
): Promise<void>
```

**PerformStagePayloads Type:**
```typescript
interface PerformStagePayloads {
  teamId: TeamId;
  trigger: Trigger;  // Contains workspaceId, nodeId, configuration
  parameterItems: ParameterItem[];
}
```

**Execution Steps:**

1. **User Authentication** - `fetchCurrentUser()` returns authenticated user with `dbId`
2. **Act Creation** - `giselleEngine.createAct()` receives:
   ```typescript
   {
     workspaceId: payloads.trigger.workspaceId,
     nodeId: payloads.trigger.nodeId,
     inputs: [{
       type: "parameters",
       items: payloads.parameterItems
     }],
     generationOriginType: "stage"
   }
   ```
3. **Database Persistence** - `db.insert(actsSchema).values()` creates record:
   ```typescript
   {
     teamDbId: team.dbId,
     directorDbId: user.dbId,
     sdkActId: act.id,
     sdkFlowTriggerId: payloads.trigger.id,
     sdkWorkspaceId: payloads.trigger.workspaceId
   }
   ```
4. **Execution Initiation** - `giselleEngine.startAct({actId: act.id, generationOriginType: "stage"})`
5. **Cache Invalidation** - `revalidatePath("/stage")` refreshes UI

**Error Handling:**
- Try-catch wraps entire operation
- Console error logging
- Throws user-friendly error: `"Failed to start the flow. Please try again."`

**Sources:** [apps/studio.giselles.ai/app/stage/(top)/actions.ts:9-51](), [apps/studio.giselles.ai/app/stage/(top)/types.ts:35-43]()

### Database Schema Integration

The `acts` table links Stage UI records to Giselle Engine Act instances:

| Column | Type | Source | Purpose |
|--------|------|--------|---------|
| `teamDbId` | `integer` | `db.query.teams` | Team ownership reference |
| `directorDbId` | `integer` | `fetchCurrentUser().dbId` | User who initiated execution |
| `sdkActId` | `string` | `giselleEngine.createAct().act.id` | Giselle Engine Act ID |
| `sdkFlowTriggerId` | `TriggerId` | `payloads.trigger.id` | Originating flow trigger |
| `sdkWorkspaceId` | `WorkspaceId` | `payloads.trigger.workspaceId` | Associated workspace |
| `createdAt` | `timestamp` | Auto-generated | Act creation time |

**Key Relationships:**
- `teamDbId` → `teams.dbId` (foreign key)
- `directorDbId` → `users.dbId` (foreign key)
- `sdkActId` → Used to query `giselleEngine.getAct({actId})`
- `sdkFlowTriggerId` → Used to query `giselleEngine.getTrigger({triggerId})`

**Sources:** [apps/studio.giselles.ai/app/stage/(top)/actions.ts:33-39](), [apps/studio.giselles.ai/db/schema.ts]()

### Act Lifecycle in Stage System

```mermaid
stateDiagram-v2
    [*] --> FormSubmission: "User submits form"
    FormSubmission --> Validation: "parseFormInputs()"
    Validation --> CreateAct: "Valid inputs"
    Validation --> FormSubmission: "Validation errors"
    CreateAct --> PersistDB: "giselleEngine.createAct()"
    PersistDB --> StartExecution: "db.insert(actsSchema)"
    StartExecution --> Running: "giselleEngine.startAct()"
    Running --> Completed: "All sequences complete"
    Running --> Failed: "Error in execution"
    Running --> Cancelled: "User cancellation"
    Completed --> [*]
    Failed --> [*]
    Cancelled --> [*]
```

**Sources:** [apps/studio.giselles.ai/app/stage/(top)/actions.ts:9-51](), [apps/studio.giselles.ai/app/stage/acts/page.tsx:66-84]()

## Task List and Management

The `/stage/acts` route provides a filterable, searchable list of all Acts (tasks) created by the user.

### FilterableActsList Component

The `FilterableActsList` component implements GitHub-style search with custom filters:

**Search Query Syntax:**
- `is:open` - Show non-archived tasks (default)
- `is:archived` - Show archived tasks (not yet implemented)
- Free text - Search by workspace name or team name

**Filter Controls:**
| Filter | Type | Options |
|--------|------|---------|
| Status | Multi-select dropdown | Created, Running, Completed, Failed, Cancelled |
| Tab | Single-select | Open (default), Archived |
| Search | Text input with tags | GitHub-style query parser |

### Search Query Parsing

The `parseSearchQuery` function splits queries into structured filters:

```typescript
// Example: "is:open workspace-name" 
// → {isOpen: true, freeText: "workspace-name"}
```

**Parsing Logic:**
1. Split query by whitespace
2. Check each part for `is:open` or `is:archived`
3. Remaining parts become `freeText`
4. Apply filters with AND logic

**Sources:** [apps/studio.giselles.ai/app/stage/acts/components/filterable-acts-list.tsx:37-78]()

### Act Enrichment Process

The `enrichActWithNavigationData` function in [apps/studio.giselles.ai/app/stage/acts/page.tsx:18-116]() transforms database Act records into UI-ready objects with navigation links and display metadata.

**Function Signature:**
```typescript
async function enrichActWithNavigationData(
  act: typeof actsSchema.$inferSelect,
  teams: { dbId: number; name: string }[]
): Promise<ActWithNavigation | null>
```

**Enrichment Pipeline:**

```mermaid
graph TB
    dbAct["DB Act Record<br/>acts table"]
    getAct["giselleEngine.getAct({actId})"]
    actData["Act with sequences/steps"]
    getWorkspace["giselleEngine.getWorkspace(workspaceId)"]
    workspaceData["Workspace with nodes"]
    
    findStep["Status-based step selection"]
    extractModels["Extract LLM models from nodes"]
    buildLink["Construct link with stepId"]
    
    enriched["ActWithNavigation object"]
    
    dbAct --> getAct
    getAct --> actData
    dbAct --> getWorkspace
    getWorkspace --> workspaceData
    
    actData --> findStep
    actData --> buildLink
    workspaceData --> extractModels
    
    findStep --> buildLink
    extractModels --> enriched
    buildLink --> enriched
```

**Step Selection Logic:**

| Act Status | Target Step Selection | Function |
|------------|----------------------|----------|
| `created` / `inProgress` | First step with `status: "running"`, fallback to first step | `findStepByStatus("running") ?? getFirstStep()` |
| `completed` | Last step of last sequence | `getLastStep()` |
| `failed` | First step with `status: "failed"` | `findStepByStatus("failed")` |
| `cancelled` | First step with `status: "cancelled"` | `findStepByStatus("cancelled")` |

**Helper Functions:**

```typescript
// Find step matching specific status
const findStepByStatus = (status: string) => {
  for (const sequence of tmpAct.sequences) {
    for (const step of sequence.steps) {
      if (step.status === status) return step;
    }
  }
  return null;
};

// Get first available step
const getFirstStep = () => {
  if (tmpAct.sequences.length === 0) return null;
  const firstSequence = tmpAct.sequences[0];
  return firstSequence.steps.length > 0 ? firstSequence.steps[0] : null;
};

// Get last available step
const getLastStep = () => {
  if (tmpAct.sequences.length === 0) return null;
  const lastSequence = tmpAct.sequences[tmpAct.sequences.length - 1];
  return lastSequence.steps.length > 0 
    ? lastSequence.steps[lastSequence.steps.length - 1] 
    : null;
};
```

**LLM Model Extraction:**

Parses workspace nodes to extract text generation models:
```typescript
// Extract from workspace.nodes
for (const node of tmpWorkspace.nodes) {
  if (node.content?.type === "textGeneration" && node.content.llm) {
    const model = node.content.llm.id;
    if (typeof model === "string" && !llmModels.includes(model)) {
      llmModels.push(model);
    }
  }
}
```

**Output Structure:**
```typescript
{
  id: string;                    // Act ID
  status: StatusFilter;          // created | inProgress | completed | failed | cancelled
  createdAt: string;             // ISO timestamp
  link: string;                  // "/stage/acts/{actId}/{stepId}"
  teamName: string;              // From teams lookup
  workspaceName: string;         // From workspace.name
  llmModels?: string[];          // Array of model IDs
  inputValues?: string;          // Not implemented yet
}
```

**Error Handling:**
- Wraps entire function in try-catch
- Returns `null` for any enrichment failure (unparseable legacy data)
- Caller filters out `null` results: `tmp.filter((actOrNull): actOrNull is ActWithNavigation => actOrNull !== null)`

**Sources:** [apps/studio.giselles.ai/app/stage/acts/page.tsx:18-116](), [apps/studio.giselles.ai/app/stage/(top)/services.ts:15-104](), [apps/studio.giselles.ai/app/stage/acts/types/index.ts:8-17]()

### Task Table Display

The table presents enriched Acts with the following columns:

| Column | Content | Visibility |
|--------|---------|-----------|
| Name | Workspace name + creation timestamp + team name | Always |
| LLM Models | Badge list of models used (max 2 shown) | Desktop only |
| Input Values | Truncated input parameter display | Desktop only |
| Status | Status badge with dot variant | Always |
| Actions | Archive button or reload (for failed tasks) | Desktop only |

**Status Badge Mapping:**
```typescript
inProgress → StatusBadge status="info" (blue, animated)
completed → StatusBadge status="success" (green)
failed → StatusBadge status="error" (red)
cancelled → StatusBadge status="ignored" (gray)
```

**Sources:** [apps/studio.giselles.ai/app/stage/acts/components/filterable-acts-list.tsx:526-698](), [internal-packages/ui/components/status-badge.tsx:39-87]()

### Empty States

The component handles three empty states:

1. **No Acts Created** - Shows create button linking to `/stage`
2. **No Matching Filters** - Shows clear filters button
3. **Filtered Empty Result** - Displays search icon and suggestion to adjust filters

**Sources:** [apps/studio.giselles.ai/app/stage/acts/components/filterable-acts-list.tsx:485-524]()

## ResizableLayout Pattern

The Stage page uses a two-panel resizable layout to display the form and recent tasks simultaneously on desktop.

### Layout Implementation

```mermaid
graph LR
    subgraph "Desktop Layout"
        PanelGroup["PanelGroup<br/>direction=horizontal"]
        MainPanel["Panel<br/>defaultSize=70%<br/>minSize=50%"]
        ResizeHandle["PanelResizeHandle<br/>3px wide, cursor col-resize"]
        ActsPanel["Panel<br/>defaultSize=30%<br/>minSize=20%, maxSize=50%"]
    end
    
    subgraph "Mobile Layout"
        SinglePanel["Single flex column<br/>main content only"]
    end
    
    PanelGroup --> MainPanel
    PanelGroup --> ResizeHandle
    PanelGroup --> ActsPanel
```

**Responsive Behavior:**
- **Desktop (≥768px)**: Two-panel layout with resize handle
- **Mobile (<768px)**: Single column, acts panel hidden

**Panel Configuration:**
- Main content: 70% default, 50% minimum
- Acts content: 30% default, 20-50% range
- Resize handle: 3px width, hover highlight

**Sources:** [apps/studio.giselles.ai/app/stage/(top)/resizable-layout.tsx:1-49](), [apps/studio.giselles.ai/app/stage/(top)/page.tsx:61-167]()

## Extended Duration Configuration

Both the main Stage page and Acts list page are configured with extended server action duration:

```typescript
export const maxDuration = 800; // 800 seconds
```

This configuration enables:
- Long-running Act execution without timeout
- Support for complex workflow processing
- Fluid compute capability on Vercel

The extended duration is necessary because Acts may trigger sequences of LLM operations, file processing, and tool executions that exceed standard serverless function timeouts.

**Sources:** [apps/studio.giselles.ai/app/stage/(top)/page.tsx:23-23](), [apps/studio.giselles.ai/app/stage/acts/page.tsx:13-13]()

---

# Page: Vector Store Management Interface

# Vector Store Management Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/configure-sources-dialog.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/configure-sources-dialog.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/data.ts](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/data.ts)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/diagnostic-modal.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/diagnostic-modal.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-embedding-profiles.ts](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-embedding-profiles.ts)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-store-create-dialog.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-store-create-dialog.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-vector-store-list.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-vector-store-list.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/page.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/page.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/layout.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/layout.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/navigation-layout.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/navigation-layout.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/page.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/page.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-list.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-list.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-registration-dialog.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-registration-dialog.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/sidebar-menu.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/sidebar-menu.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/types.ts](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/types.ts)
- [internal-packages/ui/components/form-field.tsx](internal-packages/ui/components/form-field.tsx)
- [internal-packages/ui/components/section-header.tsx](internal-packages/ui/components/section-header.tsx)
- [internal-packages/ui/components/status-indicator.tsx](internal-packages/ui/components/status-indicator.tsx)

</details>



The Vector Store Management Interface provides the user-facing settings pages and dialogs for managing GitHub repository and document vector stores in the Studio application. This includes UI components for registering, configuring, and monitoring vector store ingestion status, as well as server actions for CRUD operations and diagnostic tools for troubleshooting connection issues.

For information about the underlying vector store system and RAG implementation, see [3.2](#3.2) and [3.3](#3.3). For the Stage System that uses vector stores, see [5.1.2](#5.1.2).

## Architecture Overview

The vector store management interface consists of two parallel systems: GitHub repository vector stores and document vector stores. Both share common UI patterns but manage different types of content sources.

```mermaid
graph TB
    subgraph "Page Routes"
        GitHubPage["page.tsx<br/>/settings/team/vector-stores"]
        DocumentPage["document/page.tsx<br/>/settings/team/vector-stores/document"]
    end
    
    subgraph "GitHub Repository UI Components"
        RepositoryList["RepositoryList"]
        RepositoryItem["RepositoryItem<br/>Main display card"]
        RegistrationDialog["RepositoryRegistrationDialog<br/>Add new repo"]
        ConfigureDialog["ConfigureSourcesDialog<br/>Edit settings"]
        DiagnosticModal["DiagnosticModal<br/>Fix connection issues"]
        EmbeddingModelCard["EmbeddingModelCard<br/>Status per profile"]
    end
    
    subgraph "Document Vector Store UI Components"
        DocumentList["DocumentVectorStoreList"]
        DocumentItem["DocumentVectorStoreItem<br/>Main display card"]
        CreateDialog["DocumentVectorStoreCreateDialog<br/>Add new store"]
        DocumentConfigureDialog["DocumentVectorStoreConfigureDialog<br/>Edit & upload files"]
    end
    
    subgraph "Server Actions (actions.ts)"
        RegisterRepo["registerRepositoryIndex"]
        UpdateRepo["updateRepositoryIndex"]
        DeleteRepo["deleteRepositoryIndex"]
        TriggerIngest["triggerManualIngest"]
        Diagnose["diagnoseRepositoryConnection"]
        UpdateInstallation["updateRepositoryInstallation"]
        CreateDoc["createDocumentVectorStore"]
        UpdateDoc["updateDocumentVectorStore"]
        DeleteDoc["deleteDocumentVectorStore"]
    end
    
    subgraph "Data Layer"
        DataQueries["data.ts<br/>getGitHubRepositoryIndexes<br/>getInstallationsWithRepos<br/>getDocumentVectorStores"]
        Database[("Database<br/>githubRepositoryIndex<br/>githubRepositoryContentStatus<br/>documentVectorStores<br/>documentVectorStoreSources")]
        SupabaseStorage[("Supabase Storage<br/>Document files")]
    end
    
    GitHubPage --> RepositoryList
    RepositoryList --> RepositoryItem
    RepositoryItem --> EmbeddingModelCard
    RepositoryItem --> ConfigureDialog
    RepositoryItem --> DiagnosticModal
    GitHubPage --> RegistrationDialog
    
    DocumentPage --> DocumentList
    DocumentList --> DocumentItem
    DocumentItem --> DocumentConfigureDialog
    DocumentPage --> CreateDialog
    
    RegistrationDialog --> RegisterRepo
    RepositoryItem --> DeleteRepo
    RepositoryItem --> TriggerIngest
    RepositoryItem --> UpdateRepo
    ConfigureDialog --> UpdateRepo
    DiagnosticModal --> Diagnose
    DiagnosticModal --> UpdateInstallation
    
    CreateDialog --> CreateDoc
    DocumentItem --> DeleteDoc
    DocumentItem --> UpdateDoc
    DocumentConfigureDialog --> UpdateDoc
    
    RegisterRepo --> Database
    UpdateRepo --> Database
    DeleteRepo --> Database
    TriggerIngest --> Database
    CreateDoc --> Database
    UpdateDoc --> Database
    DeleteDoc --> Database
    DeleteDoc --> SupabaseStorage
    
    DataQueries --> Database
    GitHubPage --> DataQueries
    DocumentPage --> DataQueries
```

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/page.tsx:1-74](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/page.tsx:1-46](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:1-440](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-vector-store-item.tsx:1-806](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:1-919]()

## GitHub Repository Vector Store Interface

### Main Page Component

The main entry point for GitHub repository vector stores is `page.tsx`, which handles authentication state and delegates to specialized components based on the GitHub identity status.

```mermaid
flowchart TD
    PageLoad["TeamVectorStorePage<br/>page.tsx:21"]
    
    CheckAuth["getGitHubIdentityState"]
    
    Unauthorized{"status =<br/>unauthorized or<br/>invalid-credential?"}
    AuthRequired["GitHubAuthRequiredCard"]
    
    Error{"status =<br/>error?"}
    ErrorCard["GitHubAuthErrorCard"]
    
    CheckInstallations["userClient.getInstallations"]
    NoInstall{"total_count<br/>== 0?"}
    InstallRequired["GitHubAppInstallRequiredCard"]
    
    FetchData["Promise.all:<br/>getInstallationsWithRepos<br/>getGitHubRepositoryIndexes<br/>docVectorStoreFlag"]
    
    RenderUI["VectorStoresNavigationLayout<br/>+ RepositoryList<br/>+ RepositoryRegistrationDialog"]
    
    PageLoad --> CheckAuth
    CheckAuth --> Unauthorized
    Unauthorized -->|Yes| AuthRequired
    Unauthorized -->|No| Error
    Error -->|Yes| ErrorCard
    Error -->|No| CheckInstallations
    CheckInstallations --> NoInstall
    NoInstall -->|Yes| InstallRequired
    NoInstall -->|No| FetchData
    FetchData --> RenderUI
```

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/page.tsx:21-74]()

The page component performs three authentication and access checks before rendering the main interface:

| Check | Condition | Component Rendered |
|-------|-----------|-------------------|
| GitHub Auth | `status === "unauthorized"` or `status === "invalid-credential"` | `GitHubAuthRequiredCard` |
| GitHub Error | `status === "error"` | `GitHubAuthErrorCard` |
| GitHub App Installation | `installationData.total_count === 0` | `GitHubAppInstallRequiredCard` |
| Success | All checks pass | `RepositoryList` + `RepositoryRegistrationDialog` |

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/page.tsx:24-42]()

### Repository Item Display

The `RepositoryItem` component renders each registered repository as a `GlassCard` with embedded `EmbeddingModelCard` components showing status per embedding profile.

```mermaid
graph TB
    subgraph "RepositoryItem Component"
        ItemRoot["GlassCard container<br/>repository-item.tsx:112"]
        
        Header["Repository header row"]
        OwnerRepo["AccentLink<br/>owner/repo"]
        ActionMenu["RepoActionMenu<br/>Ingest/Configure/Delete"]
        
        CardGrid["Grid of EmbeddingModelCard<br/>grid-cols-3"]
        
        DeleteDialog["GlassDialogContent<br/>Delete confirmation"]
        ConfigDialog["ConfigureSourcesDialog"]
        DiagModal["DiagnosticModal"]
    end
    
    subgraph "EmbeddingModelCard (per profile)"
        ModelHeader["Profile name<br/>GITHUB_EMBEDDING_PROFILES"]
        CodeSection["Code status<br/>blob contentType"]
        PullRequestSection["Pull Requests status<br/>pull_request contentType"]
        StatusDisplay["StatusBadge/StatusIndicator<br/>idle/running/completed/failed"]
        SyncInfo["Last sync timestamp<br/>Commit SHA / PR number"]
        ErrorInfo["Error message + retry time"]
        CheckLink["Check ↗ button<br/>Opens DiagnosticModal"]
    end
    
    ItemRoot --> Header
    Header --> OwnerRepo
    Header --> ActionMenu
    ItemRoot --> CardGrid
    CardGrid --> ModelHeader
    ModelHeader --> CodeSection
    ModelHeader --> PullRequestSection
    CodeSection --> StatusDisplay
    CodeSection --> SyncInfo
    CodeSection --> ErrorInfo
    CodeSection --> CheckLink
    PullRequestSection --> StatusDisplay
    PullRequestSection --> SyncInfo
    PullRequestSection --> ErrorInfo
    PullRequestSection --> CheckLink
    
    ActionMenu -.->|Ingest Now| TriggerAction["triggerManualIngestAction"]
    ActionMenu -.->|Configure| ConfigDialog
    ActionMenu -.->|Delete| DeleteDialog
    CheckLink -.->|Opens| DiagModal
```

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:48-207](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:210-439]()

The `RepositoryItem` component manages three dialogs via React state:

```typescript
const [showDeleteDialog, setShowDeleteDialog] = useState(false);
const [showConfigureDialog, setShowConfigureDialog] = useState(false);
const [showDiagnosticModal, setShowDiagnosticModal] = useState(false);
```

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:65-67]()

#### Content Status Display Logic

Each `EmbeddingModelCard` displays two content types (Code and Pull Requests) with conditional rendering based on status:

| Status | Enabled | Display |
|--------|---------|---------|
| `completed` | `true` | `StatusBadge` with "Enabled" label (success variant) |
| `idle` / `running` / `failed` | `true` | `StatusIndicator` with status-specific styling |
| Any | `false` | `StatusBadge` with "Disabled" label (ignored variant) |

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:250-305](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:346-397]()

When a content status has `status === "failed"` and `errorCode === "DOCUMENT_NOT_FOUND"`, a "Check ↗" button is displayed that opens the `DiagnosticModal` to troubleshoot the connection issue.

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:288-297](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:381-390]()

#### Manual Ingest Eligibility

The "Ingest Now" action is conditionally enabled based on content status eligibility checks:

```typescript
const canManuallyIngest = contentStatuses.some((cs) => {
  if (!cs.enabled) return false;
  return (
    cs.status === "idle" ||
    cs.status === "completed" ||
    (cs.status === "failed" &&
      cs.retryAfter &&
      new Date(cs.retryAfter) <= now)
  );
});
```

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:96-107]()

### Repository Registration Dialog

The `RepositoryRegistrationDialog` allows users to register new GitHub repositories for vector store ingestion.

```mermaid
graph TB
    subgraph "RepositoryRegistrationDialog Form"
        TriggerButton["GlassButton<br/>Register Repository"]
        
        FormFields["Dialog Form Fields"]
        OwnerSelect["Select: Owner/Organization<br/>From installationsWithRepos"]
        RepoSelect["Select: Repository Name<br/>Filtered by ownerId"]
        
        SourcesSection["Sources to Ingest"]
        CodeToggle["Toggle: Code<br/>blob contentType<br/>disabled=true (required)"]
        PRToggle["Toggle: Pull Requests<br/>pull_request contentType"]
        
        ProfilesSection["Embedding Models"]
        ProfileCheckboxes["Checkboxes<br/>GITHUB_EMBEDDING_PROFILES<br/>min 1 required"]
        
        Footer["GlassDialogFooter<br/>Cancel / Register"]
    end
    
    subgraph "Data Flow"
        InstallationsData["installationsWithRepos prop<br/>From getInstallationsWithRepos"]
        SelectedOwner["ownerId state"]
        SelectedRepo["repositoryId state"]
        ContentConfig["contentConfig state<br/>code, pullRequests"]
        SelectedProfiles["selectedProfiles state<br/>default: [1]"]
        
        RegisterAction["registerRepositoryIndexAction<br/>Server action"]
        ValidationResult["ActionResult<br/>success or error"]
    end
    
    TriggerButton --> FormFields
    FormFields --> OwnerSelect
    FormFields --> RepoSelect
    FormFields --> SourcesSection
    FormFields --> ProfilesSection
    SourcesSection --> CodeToggle
    SourcesSection --> PRToggle
    ProfilesSection --> ProfileCheckboxes
    FormFields --> Footer
    
    InstallationsData --> OwnerSelect
    OwnerSelect --> SelectedOwner
    SelectedOwner --> RepoSelect
    RepoSelect --> SelectedRepo
    CodeToggle --> ContentConfig
    PRToggle --> ContentConfig
    ProfileCheckboxes --> SelectedProfiles
    
    Footer --> RegisterAction
    SelectedOwner --> RegisterAction
    SelectedRepo --> RegisterAction
    ContentConfig --> RegisterAction
    SelectedProfiles --> RegisterAction
    RegisterAction --> ValidationResult
```

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-registration-dialog.tsx:1-346]()

The registration dialog enforces several validation rules:

| Validation | Implementation |
|------------|----------------|
| Owner required | `!ownerId` → `setError("Owner is required")` |
| Repository required | `!repositoryId` → `setError("Repository is required")` |
| Code always enabled | `contentConfig.code.enabled` is set to `true` and toggle is `disabled={true}` |
| At least one profile | Default `[1]` (OpenAI Small), cannot uncheck last profile |

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-registration-dialog.tsx:67-94](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-registration-dialog.tsx:213-235](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-registration-dialog.tsx:273-318]()

### Configure Sources Dialog

The `ConfigureSourcesDialog` allows users to modify content types and embedding profiles for an existing repository.

```mermaid
graph TB
    subgraph "ConfigureSourcesDialog"
        DialogRoot["Dialog.Root<br/>Controlled by open/setOpen"]
        
        HeaderSection["GlassDialogHeader<br/>Configure Vector Stores"]
        
        BodySection["GlassDialogBody"]
        SourcesConfig["Sources Section<br/>ContentTypeToggle components"]
        CodeToggle["Code toggle<br/>disabled=true"]
        PRToggle["Pull Requests toggle"]
        
        ProfilesConfig["Embedding Models Section"]
        ProfileList["Checkbox list<br/>GITHUB_EMBEDDING_PROFILES"]
        LastOneDisabled["isLastOne prevents unchecking"]
        
        ErrorDisplay["Error message display"]
        
        FooterSection["GlassDialogFooter<br/>Cancel / Save Changes"]
    end
    
    subgraph "State Management"
        ConfigState["config state<br/>code: {enabled}<br/>pullRequests: {enabled}"]
        ProfilesState["selectedProfiles state<br/>Initialized from enabledProfiles"]
        ErrorState["error state"]
        IsPending["isPending<br/>useTransition"]
    end
    
    subgraph "Data Flow"
        RepoData["repositoryData prop<br/>repositoryIndex + contentStatuses"]
        UpdateAction["updateRepositoryIndexAction<br/>Server action"]
        RevalidatePath["revalidatePath<br/>/settings/team/vector-stores"]
    end
    
    DialogRoot --> HeaderSection
    DialogRoot --> BodySection
    DialogRoot --> FooterSection
    
    BodySection --> SourcesConfig
    SourcesConfig --> CodeToggle
    SourcesConfig --> PRToggle
    BodySection --> ProfilesConfig
    ProfilesConfig --> ProfileList
    ProfileList --> LastOneDisabled
    BodySection --> ErrorDisplay
    
    RepoData --> ConfigState
    RepoData --> ProfilesState
    CodeToggle --> ConfigState
    PRToggle --> ConfigState
    ProfileList --> ProfilesState
    
    FooterSection --> UpdateAction
    ConfigState --> UpdateAction
    ProfilesState --> UpdateAction
    UpdateAction --> ErrorState
    UpdateAction --> RevalidatePath
    ErrorState --> ErrorDisplay
    UpdateAction --> IsPending
```

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/configure-sources-dialog.tsx:1-271]()

The dialog initializes state from the current repository data on open:

```typescript
const blobStatus = contentStatuses.find((cs) => cs.contentType === "blob");
const pullRequestStatus = contentStatuses.find(
  (cs) => cs.contentType === "pull_request",
);

const [config, setConfig] = useState({
  code: { enabled: blobStatus?.enabled ?? true },
  pullRequests: { enabled: pullRequestStatus?.enabled ?? false },
});
```

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/configure-sources-dialog.tsx:47-55]()

### Diagnostic Modal

The `DiagnosticModal` diagnoses and fixes repository connection issues when the `DOCUMENT_NOT_FOUND` error occurs.

```mermaid
sequenceDiagram
    participant User
    participant Modal as DiagnosticModal
    participant Diagnose as diagnoseRepositoryConnection
    participant GitHub as GitHub API
    participant Update as updateRepositoryInstallation
    participant DB as Database
    
    User->>Modal: Open modal (showDiagnostic)
    Modal->>Modal: setIsDiagnosing(true)
    Modal->>Diagnose: diagnoseRepositoryConnection(indexId)
    
    Diagnose->>DB: Fetch repositoryIndex
    Diagnose->>GitHub: Check user installations
    
    loop For each installation
        Diagnose->>GitHub: Try GET /repos/{owner}/{repo}
        alt Repository accessible
            GitHub-->>Diagnose: 200 OK
            Note over Diagnose: validInstallationId found
        else Repository not accessible
            GitHub-->>Diagnose: Error
        end
    end
    
    alt validInstallationId found
        Diagnose-->>Modal: {canBeFixed: true, newInstallationId}
        Modal->>User: Show "Connection can be restored"
        User->>Modal: Click "Restore Connection"
        Modal->>Update: updateRepositoryInstallation(indexId, newInstallationId)
        Update->>DB: UPDATE installationId
        Update->>DB: UPDATE contentStatus (status=idle, errorCode=null)
        Update->>Modal: revalidatePath
        Modal->>User: Close modal
    else No installation found
        Diagnose-->>Modal: {canBeFixed: false, reason: "no-installation"}
        Modal->>User: Show "Repository no longer accessible"
        User->>Modal: Click "Delete Repository"
        Modal->>User: Execute onDelete callback
    end
```

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/diagnostic-modal.tsx:1-171](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:384-508]()

The diagnostic process follows this decision tree:

| Condition | Result | Action |
|-----------|--------|--------|
| Repository not found in DB | `{canBeFixed: false, reason: "repository-not-found"}` | Cannot proceed |
| GitHub auth failed | `{canBeFixed: false, reason: "diagnosis-failed"}` | Cannot proceed |
| Valid installation found | `{canBeFixed: true, newInstallationId}` | Show "Restore Connection" button |
| No installation found | `{canBeFixed: false, reason: "no-installation"}` | Show "Delete Repository" button |

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:400-448]()

## Document Vector Store Interface

### Document Vector Store Item

The `DocumentVectorStoreItem` component displays a document vector store with configuration and file management capabilities.

```mermaid
graph TB
    subgraph "DocumentVectorStoreItem"
        ItemCard["GlassCard container"]
        Header["Header section"]
        StoreName["store.name display"]
        StoreId["ID: store.id"]
        ActionMenu["RepoActionMenu<br/>Configure/Delete"]
        
        DeleteConfirm["Delete confirmation dialog"]
        ConfigureDialog["DocumentVectorStoreConfigureDialog"]
    end
    
    subgraph "DocumentVectorStoreConfigureDialog"
        ConfigRoot["GlassDialogContent"]
        NameInput["Name input field"]
        ProfilesSection["Embedding Models checkboxes<br/>selectableProfiles filtered"]
        
        FilesSection["Source Files section"]
        UploadButton["Drag & drop upload button<br/>ArrowUpFromLine icon"]
        FileInput["Hidden file input<br/>accept=DOCUMENT_UPLOAD_ACCEPT"]
        FileList["Uploaded Files list<br/>documentSources state"]
        FileItem["File with IngestStatusBadge<br/>+ Delete button"]
        
        SaveButton["GlassDialogFooter<br/>Save button"]
    end
    
    subgraph "File Upload Flow"
        HandleFiles["handleFilesUpload"]
        ValidateFiles["Validate type/size/emptiness"]
        FormData["Build FormData with files"]
        UploadAPI["POST /api/vector-stores/document/{id}/documents"]
        ParseResponse["Parse DocumentUploadResponse<br/>successes + failures"]
        UpdateSources["Update documentSources state<br/>mergeDocumentSourceItems"]
        ShowToast["Display success/error toast"]
    end
    
    subgraph "File Delete Flow"
        DeleteFile["handleDeleteSource"]
        DeleteAPI["DELETE /api/vector-stores/document/{id}/documents<br/>body: {sourceId}"]
        FilterSources["Filter out deleted source"]
        RefreshRouter["router.refresh()"]
    end
    
    ItemCard --> Header
    Header --> StoreName
    Header --> StoreId
    Header --> ActionMenu
    ActionMenu --> ConfigureDialog
    ActionMenu --> DeleteConfirm
    
    ConfigureDialog --> ConfigRoot
    ConfigRoot --> NameInput
    ConfigRoot --> ProfilesSection
    ConfigRoot --> FilesSection
    FilesSection --> UploadButton
    FilesSection --> FileInput
    FilesSection --> FileList
    FileList --> FileItem
    ConfigRoot --> SaveButton
    
    UploadButton --> HandleFiles
    FileInput --> HandleFiles
    HandleFiles --> ValidateFiles
    ValidateFiles --> FormData
    FormData --> UploadAPI
    UploadAPI --> ParseResponse
    ParseResponse --> UpdateSources
    ParseResponse --> ShowToast
    UpdateSources --> RefreshRouter
    
    FileItem --> DeleteFile
    DeleteFile --> DeleteAPI
    DeleteAPI --> FilterSources
    FilterSources --> RefreshRouter
```

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-vector-store-item.tsx:123-226](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-vector-store-item.tsx:302-805]()

#### File Upload Validation

The file upload handler validates files before uploading:

| Validation | Implementation | Constant |
|------------|----------------|----------|
| Supported types | `isSupportedDocumentFile(file)` | `DOCUMENT_VECTOR_STORE_SUPPORTED_MIME_TYPES` + `DOCUMENT_VECTOR_STORE_SUPPORTED_FILE_EXTENSIONS` |
| Non-empty | `file.size === 0` | N/A |
| Size limit | `file.size > DOCUMENT_VECTOR_STORE_MAX_FILE_SIZE_BYTES` | `DOCUMENT_VECTOR_STORE_MAX_FILE_SIZE_BYTES` |

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-vector-store-item.tsx:381-398]()

#### Document Upload Response Handling

The upload response (`DocumentUploadResponse`) contains both successes and failures:

```typescript
type DocumentUploadResponse = {
  successes: Array<{
    fileName: string;
    sourceId: string;
    storageKey: string;
  }>;
  failures: Array<{
    fileName: string;
    error: string;
    code?: string;
  }>;
};
```

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-vector-store-item.tsx:241-252]()

The dialog displays appropriate messages based on the response:

- All successes: Show success message with file count
- Partial failures (207 Multi-Status): Show success message for uploaded files + error toast for first failure with count
- All failures: Show error toast only

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-vector-store-item.tsx:428-462]()

#### Ingest Status Display

Each uploaded file displays an `IngestStatusBadge` with the following status types:

| Status | Icon | Label | Color |
|--------|------|-------|-------|
| `idle` | `Clock` | "Pending" | Yellow |
| `running` | `Loader2` (animated) | "Processing" | Blue |
| `completed` | `CheckCircle2` | "Ready" | Green |
| `failed` | `AlertCircle` | "Failed" | Red (with error tooltip) |

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-vector-store-item.tsx:55-121]()

### Document Vector Store Creation Dialog

The `DocumentVectorStoreCreateDialog` allows users to create new document vector stores.

```mermaid
graph TB
    subgraph "DocumentVectorStoreCreateDialog"
        TriggerBtn["GlassButton<br/>Create Document Vector Store"]
        DialogContent["GlassDialogContent"]
        
        NameField["FormField: Name"]
        ProfilesSection["Embedding Models Section"]
        ProfileCheckboxes["Checkboxes<br/>DOCUMENT_EMBEDDING_PROFILES filtered<br/>Exclude cohere provider"]
        
        ErrorMsg["Error message display"]
        Footer["GlassDialogFooter<br/>Cancel / Create"]
    end
    
    subgraph "State Management"
        NameState["name state"]
        ProfilesState["selectedProfiles state<br/>default: defaultProfiles"]
        ErrorState["error state"]
        PendingState["isPending<br/>useTransition"]
    end
    
    subgraph "Default Profile Logic"
        SelectableProfiles["selectableProfiles<br/>filter out cohere"]
        DefaultProfiles["defaultProfiles<br/>Prefer DEFAULT_EMBEDDING_PROFILE_ID<br/>Fallback to first selectable"]
    end
    
    TriggerBtn --> DialogContent
    DialogContent --> NameField
    DialogContent --> ProfilesSection
    ProfilesSection --> ProfileCheckboxes
    DialogContent --> ErrorMsg
    DialogContent --> Footer
    
    NameField --> NameState
    ProfileCheckboxes --> ProfilesState
    SelectableProfiles --> DefaultProfiles
    DefaultProfiles --> ProfilesState
    
    Footer --> CreateAction["createDocumentVectorStore<br/>Server action"]
    NameState --> CreateAction
    ProfilesState --> CreateAction
    CreateAction --> ErrorState
    CreateAction --> PendingState
```

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-store-create-dialog.tsx]() (not shown in full but structure is similar to registration dialog)

The dialog uses `DOCUMENT_EMBEDDING_PROFILES` which excludes Cohere provider, unlike GitHub vector stores:

```typescript
const selectableProfiles = useMemo(
  () =>
    availableProfiles.filter(([, profile]) => profile.provider !== "cohere"),
  [availableProfiles],
);
```

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-vector-store-item.tsx:315-318]()

## Server Actions

The `actions.ts` file implements all server-side operations for vector store management.

### GitHub Repository Actions

```mermaid
graph TB
    subgraph "registerRepositoryIndex"
        ValidateAccess["validateGitHubAccess<br/>Check installation + repo access"]
        EnsureBlob["Ensure blob contentType enabled"]
        ValidateProfiles["Filter valid EmbeddingProfileIds"]
        CheckExisting["Query existing index for team"]
        Transaction["db.transaction"]
        InsertIndex["Insert githubRepositoryIndex"]
        InsertProfiles["Insert githubRepositoryEmbeddingProfiles"]
        InsertStatuses["Insert githubRepositoryContentStatus<br/>For each profile × contentType"]
        Revalidate["revalidatePath<br/>/settings/team/vector-stores"]
    end
    
    subgraph "updateRepositoryIndex"
        ValidateBlob["Ensure blob enabled"]
        ValidateProfiles2["Filter valid profiles"]
        FetchRepo["Fetch repository by id + teamDbId"]
        Transaction2["db.transaction"]
        CleanupOld["Delete removed profiles + statuses"]
        UpsertProfiles["Upsert new profiles<br/>onConflictDoNothing"]
        UpsertStatuses["Upsert content statuses<br/>onConflictDoUpdate preserves status"]
        Revalidate2["revalidatePath"]
    end
    
    subgraph "triggerManualIngest"
        FetchWithStatuses["fetchRepositoryWithStatuses"]
        CheckIngestability["checkIngestability<br/>Validate status + retryAfter"]
        CreateTrigger["createManualIngestTrigger"]
        ExecuteIngest["executeManualIngest<br/>after() async call"]
        ProcessRepo["processRepository<br/>From @/lib/vector-stores/github"]
        Revalidate3["revalidatePath<br/>immediate for UI update"]
    end
    
    subgraph "diagnoseRepositoryConnection"
        FetchIndex["Fetch githubRepositoryIndex"]
        CheckAuth["getGitHubIdentityState"]
        IterateInstallations["For each installation"]
        TryAccess["Try GET /repos/{owner}/{repo}"]
        ReturnResult["Return DiagnosticResult<br/>canBeFixed + newInstallationId"]
    end
    
    registerRepositoryIndex --> ValidateAccess
    ValidateAccess --> EnsureBlob
    EnsureBlob --> ValidateProfiles
    ValidateProfiles --> CheckExisting
    CheckExisting --> Transaction
    Transaction --> InsertIndex
    InsertIndex --> InsertProfiles
    InsertProfiles --> InsertStatuses
    InsertStatuses --> Revalidate
    
    updateRepositoryIndex --> ValidateBlob
    ValidateBlob --> ValidateProfiles2
    ValidateProfiles2 --> FetchRepo
    FetchRepo --> Transaction2
    Transaction2 --> CleanupOld
    CleanupOld --> UpsertProfiles
    UpsertProfiles --> UpsertStatuses
    UpsertStatuses --> Revalidate2
    
    triggerManualIngest --> FetchWithStatuses
    FetchWithStatuses --> CheckIngestability
    CheckIngestability --> CreateTrigger
    CreateTrigger --> ExecuteIngest
    ExecuteIngest --> ProcessRepo
    ExecuteIngest --> Revalidate3
    
    diagnoseRepositoryConnection --> FetchIndex
    FetchIndex --> CheckAuth
    CheckAuth --> IterateInstallations
    IterateInstallations --> TryAccess
    TryAccess --> ReturnResult
```

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:105-210](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:216-368](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:513-552](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:384-462]()

#### Ingestability Check Logic

The `checkIngestability` function validates whether a repository can be manually ingested:

```typescript
function checkIngestability(
  contentStatuses: (typeof githubRepositoryContentStatus.$inferSelect)[],
  now: Date = new Date(),
): IngestabilityCheck {
  for (const contentStatus of contentStatuses) {
    if (!contentStatus.enabled) {
      continue;
    }

    const canIngestThis =
      contentStatus.status === "idle" ||
      contentStatus.status === "completed" ||
      (contentStatus.status === "failed" &&
        contentStatus.retryAfter &&
        contentStatus.retryAfter <= now);

    if (!canIngestThis) {
      return {
        canIngest: false,
        reason: `Repository cannot be ingested at this time (${contentStatus.contentType} is blocking)`,
      };
    }
  }

  const hasBlobStatus = contentStatuses.some((cs) => cs.contentType === "blob");
  if (!hasBlobStatus) {
    return {
      canIngest: false,
      reason: "Repository does not have a blob content status",
    };
  }

  return { canIngest: true };
}
```

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:870-906]()

### Document Vector Store Actions

```mermaid
graph TB
    subgraph "createDocumentVectorStore"
        CheckFlag["docVectorStoreFlag()"]
        ValidateName["Trim name, check non-empty"]
        ValidateProfiles["validateDocumentEmbeddingProfileIds"]
        FetchTeam["fetchCurrentTeam()"]
        Transaction["db.transaction"]
        InsertStore["Insert documentVectorStores"]
        InsertProfiles["Insert documentEmbeddingProfiles"]
        Revalidate["revalidatePath<br/>/settings/team/vector-stores/document"]
    end
    
    subgraph "updateDocumentVectorStore"
        CheckFlag2["docVectorStoreFlag()"]
        ValidateName2["Validate name"]
        ValidateProfiles2["Validate profiles"]
        Transaction2["db.transaction"]
        FetchStore["Fetch store for update lock"]
        UpdateName["Update name"]
        DeleteOldProfiles["Delete old profiles"]
        InsertNewProfiles["Insert new profiles"]
        Revalidate2["revalidatePath"]
    end
    
    subgraph "deleteDocumentVectorStore"
        CheckFlag3["docVectorStoreFlag()"]
        Transaction3["db.transaction"]
        FetchStoreForDelete["Fetch store for update lock"]
        FetchSources["Fetch documentVectorStoreSources<br/>storageBucket + storageKey"]
        DeleteSources["Delete documentVectorStoreSources"]
        DeleteProfiles["Delete documentEmbeddingProfiles"]
        DeleteStore["Delete documentVectorStores"]
        AfterCleanup["after() cleanup"]
        SupabaseDelete["supabase.storage.from(bucket).remove()"]
        Revalidate3["revalidatePath"]
    end
    
    createDocumentVectorStore --> CheckFlag
    CheckFlag --> ValidateName
    ValidateName --> ValidateProfiles
    ValidateProfiles --> FetchTeam
    FetchTeam --> Transaction
    Transaction --> InsertStore
    InsertStore --> InsertProfiles
    InsertProfiles --> Revalidate
    
    updateDocumentVectorStore --> CheckFlag2
    CheckFlag2 --> ValidateName2
    ValidateName2 --> ValidateProfiles2
    ValidateProfiles2 --> Transaction2
    Transaction2 --> FetchStore
    FetchStore --> UpdateName
    UpdateName --> DeleteOldProfiles
    DeleteOldProfiles --> InsertNewProfiles
    InsertNewProfiles --> Revalidate2
    
    deleteDocumentVectorStore --> CheckFlag3
    CheckFlag3 --> Transaction3
    Transaction3 --> FetchStoreForDelete
    FetchStoreForDelete --> FetchSources
    FetchSources --> DeleteSources
    DeleteSources --> DeleteProfiles
    DeleteProfiles --> DeleteStore
    DeleteStore --> AfterCleanup
    AfterCleanup --> SupabaseDelete
    AfterCleanup --> Revalidate3
```

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:575-634](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:636-715](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:717-835]()

#### Storage Cleanup with `after()`

The `deleteDocumentVectorStore` action uses Next.js 15's `after()` API to perform potentially slow Supabase storage cleanup after the database transaction commits:

```typescript
if (storageSources.length > 0) {
  // Perform potentially slow storage cleanup after the database transaction commits.
  after(async () => {
    const storeFolder = `${DOCUMENT_VECTOR_STORE_STORAGE_PREFIX}/${documentVectorStoreId}`;
    const cleanupTargetsByBucket = new Map<string, Set<string>>();
    // ... build cleanup targets ...
    
    for (const [bucket, targets] of cleanupTargetsByBucket) {
      const { error: storageError } = await supabase.storage
        .from(bucket)
        .remove(Array.from(targets));
      // ... handle errors ...
    }
  });
}
```

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:785-823]()

This ensures the API response is not delayed by storage operations while still cleaning up files.

## Embedding Profile Configuration

Both GitHub and document vector stores use embedding profiles defined in `@giselle-sdk/data-type`, but with different filtering rules for the UI.

### GitHub Embedding Profiles

The GitHub vector store UI excludes Cohere profiles:

```typescript
// github-embedding-profiles.ts
export const GITHUB_EMBEDDING_PROFILES = Object.fromEntries(
  Object.entries(EMBEDDING_PROFILES).filter(
    ([, profile]) => profile.provider !== "cohere",
  ),
) as typeof EMBEDDING_PROFILES;
```

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/github-embedding-profiles.ts:1-13]()

Available GitHub profiles:

| Profile ID | Name | Provider | Dimensions |
|------------|------|----------|------------|
| 1 | OpenAI Small | openai | 1536 |
| 2 | OpenAI Large | openai | 3072 |
| 3 | Google Multilingual | google | 768 |

Sources: Inferred from `EMBEDDING_PROFILES` in `@giselle-sdk/data-type` with Cohere filtered out

### Document Embedding Profiles

The document vector store UI also excludes Cohere but uses the same filter logic inline:

```typescript
const selectableProfiles = useMemo(
  () =>
    availableProfiles.filter(([, profile]) => profile.provider !== "cohere"),
  [availableProfiles],
);
```

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-vector-store-item.tsx:315-318]()

The default profile selection logic prefers `DEFAULT_EMBEDDING_PROFILE_ID` (value 1) if available:

```typescript
const defaultProfiles = useMemo(() => {
  const primaryIds = selectableProfiles.map(([id]) => Number(id));
  const fallbackIds =
    primaryIds.length > 0
      ? primaryIds
      : availableProfiles.map(([id]) => Number(id));
  if (fallbackIds.includes(DEFAULT_EMBEDDING_PROFILE_ID)) {
    return [DEFAULT_EMBEDDING_PROFILE_ID];
  }
  return fallbackIds.length > 0 ? [fallbackIds[0]] : [];
}, [selectableProfiles, availableProfiles]);
```

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-vector-store-item.tsx:320-330]()

## Navigation Layout

Both GitHub and document vector store pages are wrapped in `VectorStoresNavigationLayout`, which provides tab navigation when the document vector store feature flag is enabled.

```mermaid
graph LR
    subgraph "VectorStoresNavigationLayout"
        TabsRoot["Tabs.Root"]
        TabsList["Tabs.List"]
        GitHubTab["GitHub tab"]
        DocumentTab["Document tab<br/>conditionally rendered"]
        TabsContent["Tabs.Content<br/>children prop"]
    end
    
    FeatureFlag["isEnabled prop<br/>from docVectorStoreFlag()"]
    
    FeatureFlag --> DocumentTab
    TabsRoot --> TabsList
    TabsList --> GitHubTab
    TabsList --> DocumentTab
    TabsRoot --> TabsContent
```

Sources: Inferred from [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/page.tsx:64-71](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/page.tsx:36-42]()

The document tab is only visible when `docVectorStoreFlag()` returns `true`, providing a gradual rollout mechanism for the document vector store feature.

## Data Fetching

The `data.ts` file provides query functions for fetching vector store data:

### GitHub Repository Indexes Query

```typescript
export async function getGitHubRepositoryIndexes(): Promise<
  RepositoryWithStatuses[]
> {
  const team = await fetchCurrentTeam();

  const records = await db
    .select({
      repositoryIndex: githubRepositoryIndex,
      contentStatus: githubRepositoryContentStatus,
    })
    .from(githubRepositoryIndex)
    .leftJoin(
      githubRepositoryContentStatus,
      eq(
        githubRepositoryContentStatus.repositoryIndexDbId,
        githubRepositoryIndex.dbId,
      ),
    )
    .where(eq(githubRepositoryIndex.teamDbId, team.dbId))
    .orderBy(desc(githubRepositoryIndex.dbId));

  // Group by repository
  const repositoryMap = new Map<number, RepositoryWithStatuses>();
  // ... grouping logic ...
  return Array.from(repositoryMap.values());
}
```

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/data.ts:17-60]()

This query returns `RepositoryWithStatuses[]` where each item contains:
- `repositoryIndex`: The `githubRepositoryIndex` record
- `contentStatuses`: Array of `githubRepositoryContentStatus` records for all embedding profiles

### Installations and Repositories Query

```typescript
export async function getInstallationsWithRepos(): Promise<
  InstallationWithRepos[]
> {
  const githubIdentityState = await getGitHubIdentityState();
  const userClient = githubIdentityState.gitHubUserClient;
  const installationData = await userClient.getInstallations();
  const installations = installationData.installations;

  const installationsWithRepos = await Promise.all(
    installations.map(async (installation) => {
      const repos = await userClient.getRepositories(installation.id);
      // ... transform to InstallationWithRepos format ...
      return { installation, repositories };
    }),
  );

  return installationsWithRepos;
}
```

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/data.ts:62-108]()

This fetches all GitHub App installations accessible to the authenticated user and their repositories, used to populate the registration dialog dropdowns.

### Document Vector Stores Query

The `getDocumentVectorStores()` function is defined in `@/lib/vector-stores/document/queries` and returns `DocumentVectorStoreWithProfiles[]` with:
- Document vector store metadata (id, name, teamDbId)
- Associated embedding profile IDs
- Source files with ingestion status

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/data.ts:10-11]()

## Error Handling

The interface displays user-friendly error messages for common failure scenarios:

### Document Loader Error Codes

```typescript
export type DocumentLoaderErrorCode =
  | "DOCUMENT_NOT_FOUND"
  | "DOCUMENT_FETCH_ERROR"
  | "DOCUMENT_RATE_LIMITED"
  | "DOCUMENT_TOO_LARGE";
```

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/types.ts:1-5]()

The `getErrorMessage()` helper function (referenced but not shown in provided files) maps these codes to user-friendly messages displayed in the `EmbeddingModelCard` components.

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:26](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:335-341]()

### Action Result Type

All server actions return a standardized result type:

```typescript
export type ActionResult =
  | { success: true }
  | { success: false; error: string };
```

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/types.ts:23-25]()

This allows UI components to display error messages in a consistent way using error state variables.

## UI Component Library Usage

The vector store management interface extensively uses components from the `@giselle-internal/ui` package:

| Component | Usage | File Path |
|-----------|-------|-----------|
| `GlassCard` | Container for repository/document items | `internal-packages/ui/components/glass-card.tsx` |
| `Select` | Dropdowns for owner/repository selection | `internal-packages/ui/components/select.tsx` |
| `Toggle` | Content type enable/disable switches | `internal-packages/ui/components/toggle.tsx` |
| `StatusBadge` | Enabled/Disabled/Success status indicators | `internal-packages/ui/components/status-badge.tsx` |
| `StatusIndicator` | Running/Idle/Error state visualization | `internal-packages/ui/components/status-indicator.tsx` |
| `RepoActionMenu` | Ellipsis menu with actions | `internal-packages/ui/components/repo-action-menu.tsx` |
| `AccentLink` | Repository links to GitHub | `internal-packages/ui/components/accent-link.tsx` |
| `SectionHeader` | Section titles with descriptions | `internal-packages/ui/components/section-header.tsx` |
| `FormField` | Labeled input fields | `internal-packages/ui/components/form-field.tsx` |
| `PageHeading` | Page-level heading with glow effect | `internal-packages/ui/components/page-heading.tsx` |
| `DocsLink` | Links to documentation | `internal-packages/ui/components/docs-link.tsx` |

Sources: [internal-packages/ui/package.json:10-42]()

The `GlassDialogContent`, `GlassDialogHeader`, `GlassDialogBody`, and `GlassDialogFooter` components are custom wrappers defined in the settings app:

Sources: [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:20-23](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-vector-store-item.tsx:38-42]()

---

# Page: Playground Application

# Playground Application

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/playground/package.json](apps/playground/package.json)
- [apps/studio.giselles.ai/package.json](apps/studio.giselles.ai/package.json)
- [internal-packages/workflow-designer-ui/package.json](internal-packages/workflow-designer-ui/package.json)
- [package.json](package.json)
- [packages/giselle/package.json](packages/giselle/package.json)
- [pnpm-lock.yaml](pnpm-lock.yaml)
- [pnpm-workspace.yaml](pnpm-workspace.yaml)

</details>



## Purpose and Scope

The Playground application is a minimal development and testing environment for the Giselle workflow designer and execution engine. It provides a simplified interface for developing and testing workflow features without the complexity of production infrastructure, authentication, database persistence, or external integrations. For the full production application with all features enabled, see [Studio Application](#6.1).

The Playground serves as:
- A rapid prototyping environment for workflow designer UI development
- A testing ground for Giselle engine behavior without production dependencies
- A reference implementation demonstrating minimal viable configuration
- A development tool accessible via `pnpm dev` at the repository root

**Sources:** [package.json:12](), [apps/playground/package.json:1-42]()

---

## Application Structure

### Next.js Application Configuration

The Playground is a Next.js 15 application located at [apps/playground]() with Turbopack enabled for fast development iteration. The application requires Node.js 22.x and uses pnpm as its package manager.

```mermaid
graph TB
    subgraph "apps/playground"
        App["Next.js Application<br/>(next dev --turbopack)"]
        Package["package.json"]
        Scripts["Build Scripts<br/>dev/build/start"]
    end
    
    subgraph "Core Dependencies"
        WDCore["@giselle-internal/workflow-designer-ui<br/>Visual Editor"]
        InternalUI["@giselle-internal/ui<br/>Component Library"]
        GiselleEngine["@giselles-ai/giselle<br/>Workflow Engine"]
        Protocol["@giselles-ai/protocol<br/>Type Definitions"]
    end
    
    subgraph "Support Dependencies"
        Langfuse["@giselles-ai/langfuse<br/>Telemetry"]
        SupabaseDriver["@giselles-ai/supabase-driver<br/>Storage Driver"]
    end
    
    subgraph "External Frameworks"
        Next["next (15.5.2)"]
        React["react (19.1.1)"]
        Tailwind["tailwindcss (4.1.10)"]
    end
    
    App --> WDCore
    App --> InternalUI
    App --> GiselleEngine
    App --> Protocol
    App --> Langfuse
    App --> SupabaseDriver
    
    WDCore --> Next
    WDCore --> React
    App --> Tailwind
    
    Package -.defines.-> Scripts
    Scripts -.executes.-> App
```

**Sources:** [apps/playground/package.json:1-42](), [pnpm-lock.yaml:265-324]()

### Available Scripts

| Script | Command | Purpose |
|--------|---------|---------|
| `dev` | `next dev --turbopack` | Start development server with hot reload |
| `build` | `next build --turbopack` | Create production build |
| `start` | `next start` | Run production server |
| `clean` | `rm -rf .next .turbo node_modules` | Clean build artifacts |
| `check-types` | `tsc --noEmit` | Validate TypeScript types |
| `format` | `biome check --write .` | Format code with Biome |

**Sources:** [apps/playground/package.json:9-17]()

---

## Package Dependencies

### Dependency Footprint

The Playground maintains a minimal dependency set focused on workflow design and execution, excluding production-specific features like authentication, external integrations, and observability services.

```mermaid
graph LR
    subgraph "Playground Dependencies"
        PG["playground"]
        
        subgraph "UI Layer"
            UI["@giselle-internal/ui"]
            WD["@giselle-internal/workflow-designer-ui"]
        end
        
        subgraph "Engine Layer"
            Giselle["@giselles-ai/giselle"]
            Protocol["@giselles-ai/protocol"]
        end
        
        subgraph "Infrastructure"
            Langfuse["@giselles-ai/langfuse"]
            Supabase["@giselles-ai/supabase-driver"]
        end
    end
    
    PG --> UI
    PG --> WD
    PG --> Giselle
    PG --> Protocol
    PG --> Langfuse
    PG --> Supabase
    
    WD --> UI
    WD --> Giselle
    WD --> Protocol
```

**Sources:** [apps/playground/package.json:19-30](), [pnpm-lock.yaml:265-299]()

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `@giselle-internal/ui` | workspace:^ | Shared UI component library with theme system |
| `@giselle-internal/workflow-designer-ui` | workspace:* | Complete workflow visual editor implementation |
| `@giselles-ai/protocol` | workspace:* | Type definitions for workflow structures and API contracts |
| `@giselles-ai/giselle` | workspace:* | Main orchestration engine for workflow execution |
| `@giselles-ai/langfuse` | workspace:^ | LLM observability and tracing integration |
| `@giselles-ai/supabase-driver` | workspace:^ | Storage abstraction for generation data persistence |

**Sources:** [apps/playground/package.json:19-30]()

---

## Comparison with Studio

### Dependency Differences

The key architectural difference between Playground and Studio is feature scope. The Playground includes only essential workflow design and execution capabilities, while Studio includes the full production stack.

| Feature Category | Playground | Studio |
|------------------|------------|--------|
| **Workflow Designer** | ✓ | ✓ |
| **Engine Execution** | ✓ | ✓ |
| **UI Components** | ✓ | ✓ |
| **Document Processing** | ✗ | ✓ (@giselles-ai/document-preprocessor) |
| **GitHub Integration** | ✗ | ✓ (@giselles-ai/github-tool) |
| **RAG System** | ✗ | ✓ (@giselles-ai/rag) |
| **Authentication** | ✗ | ✓ (@supabase/auth-js, @supabase/ssr) |
| **Database ORM** | ✗ | ✓ (drizzle-orm) |
| **Observability** | Basic (Langfuse) | Full (@sentry/nextjs, @vercel/otel) |
| **External Services** | ✗ | ✓ (Stripe, Trigger.dev, Email) |
| **Production Storage** | ✗ | ✓ (AWS S3, PostgreSQL) |

**Sources:** [apps/playground/package.json:19-30](), [apps/studio.giselles.ai/package.json:25-106]()

### Configuration Simplification

```mermaid
graph TB
    subgraph "Playground Configuration"
        PGConfig["Minimal Configuration"]
        PGEnv["Local Environment Variables"]
        PGFlags["Basic Feature Flags"]
        PGStorage["In-Memory/Local Storage"]
    end
    
    subgraph "Studio Configuration"
        StudioConfig["Production Configuration"]
        StudioEnv["Environment Variables<br/>+ Edge Config"]
        StudioFlags["Advanced Feature Flags<br/>+ Remote Management"]
        StudioStorage["Supabase + S3<br/>+ PostgreSQL + pgvector"]
        StudioAuth["Authentication System"]
        StudioIntegrations["External Integrations<br/>GitHub/Stripe/Email"]
    end
    
    PGConfig -.simplified.-> StudioConfig
    PGEnv -.subset of.-> StudioEnv
    PGFlags -.subset of.-> StudioFlags
    PGStorage -.minimal version of.-> StudioStorage
```

**Sources:** [apps/playground/package.json:1-42](), [apps/studio.giselles.ai/package.json:1-132]()

---

## Development Workflow

### Running the Playground

The Playground is the default development target when running `pnpm dev` from the repository root.

```bash
# From repository root - runs Playground by default
pnpm dev

# Explicit Playground target
turbo dev --filter playground

# From Playground directory
cd apps/playground
pnpm dev
```

The development server starts on the default Next.js port (typically 3000) with Turbopack hot module replacement enabled for fast iteration.

**Sources:** [package.json:12](), [apps/playground/package.json:10]()

### Development Use Cases

**Workflow Designer Development:**
- Test visual node editing without database persistence
- Validate ReactFlow canvas interactions and rendering
- Develop properties panel components in isolation
- Debug Zustand state management without production side effects

**Engine Testing:**
- Execute workflow generations with local storage
- Test AI provider integrations without production credentials
- Validate generation pipeline behavior
- Debug Act orchestration logic

**Component Development:**
- Test UI components from `@giselle-internal/ui` in context
- Validate theme system and styling
- Develop new node types and visualization

**Sources:** [apps/playground/package.json:19-30]()

---

## Architecture Integration

### Relationship to Workflow Designer UI

The Playground's primary function is hosting the Workflow Designer UI package for development and testing. It provides the Next.js runtime environment and minimal infrastructure required by the designer.

```mermaid
graph TB
    subgraph "Playground App"
        AppRoot["Next.js App Router"]
        Pages["Page Components"]
        Config["app Configuration"]
    end
    
    subgraph "@giselle-internal/workflow-designer-ui"
        Editor["V2Editor Component"]
        Canvas["Node Canvas"]
        Panels["Properties Panels"]
        Store["Zustand Store<br/>(useFlowState)"]
    end
    
    subgraph "Engine Integration"
        GiselleEngine["NextGiselleEngine"]
        Runners["Generation Runners"]
        Storage["Storage Driver"]
    end
    
    subgraph "Minimal Infrastructure"
        LocalEnv["Local Environment"]
        MemStorage["In-Memory Storage"]
        BasicFlags["Basic Feature Flags"]
    end
    
    AppRoot --> Pages
    Pages --> Editor
    Pages --> Config
    
    Editor --> Canvas
    Editor --> Panels
    Editor --> Store
    
    Canvas --> GiselleEngine
    Panels --> Runners
    
    GiselleEngine --> Storage
    Storage --> MemStorage
    
    Config --> LocalEnv
    Config --> BasicFlags
```

**Sources:** [apps/playground/package.json:19-30](), [internal-packages/workflow-designer-ui/package.json:12-41]()

### Engine Configuration

Unlike Studio, which configures the `NextGiselleEngine` with production storage drivers, database connections, and external service credentials, the Playground uses simplified configuration suitable for local development.

**Playground Engine Configuration:**
- **Storage:** Local filesystem or in-memory storage via `@giselles-ai/supabase-driver`
- **Vault:** Node-based vault with `VAULT_SECRET` environment variable (no Supabase pgsodium)
- **AI Providers:** Direct provider configuration without API gateway
- **Callbacks:** Basic logging via `@giselles-ai/langfuse` (no production telemetry)
- **Runtime Environment:** Detected as `local` rather than `vercel` or `trigger.dev`

**Sources:** [apps/playground/package.json:19-30](), [packages/giselle/package.json:55-75]()

---

## Build and Deployment

### Build Process

The Playground uses Next.js with Turbopack for both development and production builds:

```bash
# Development build (auto-rebuilding)
pnpm dev

# Production build
pnpm build

# Production server
pnpm start
```

Build configuration is managed through [next.config.js]() (if present) with Turbopack enabled for faster compilation than Webpack.

**Sources:** [apps/playground/package.json:10-13]()

### Type Generation

The Playground supports Next.js type generation for route types and configuration:

```bash
# Generate TypeScript types for Next.js routes
pnpm typegen

# Type checking without emitting files
pnpm check-types
```

**Sources:** [apps/playground/package.json:15-16]()

---

## Purpose-Built Constraints

### What Playground Excludes

The Playground intentionally omits production features to maintain simplicity and fast iteration:

**Authentication & Authorization:**
- No Supabase authentication (`@supabase/auth-js`, `@supabase/ssr`)
- No user management or team workspaces
- No access control or permissions

**Data Persistence:**
- No PostgreSQL database (`drizzle-orm`)
- No vector storage (`pgvector`)
- No persistent workflow storage

**External Integrations:**
- No GitHub integration (`@giselles-ai/github-tool`)
- No document processing (`@giselles-ai/document-preprocessor`)
- No RAG system (`@giselles-ai/rag`)
- No payment processing (Stripe)
- No email services
- No async job processing (Trigger.dev)

**Production Infrastructure:**
- No Sentry error tracking
- No Vercel-specific features (`@vercel/otel`, `@vercel/edge-config`)
- No comprehensive observability stack
- No production secret management

**Sources:** [apps/playground/package.json:19-30](), [apps/studio.giselles.ai/package.json:25-106]()

---

## Entry Point Reference

The Playground application entry point follows Next.js App Router conventions. Key files include:

- **[apps/playground/app]()**: Next.js App Router root directory
- **[apps/playground/app/layout.tsx]()**: Root layout defining global providers and styles
- **[apps/playground/app/page.tsx]()**: Default page component hosting the workflow designer
- **[apps/playground/tailwind.config.ts]()**: Tailwind CSS configuration extending theme system
- **[apps/playground/next.config.js]()**: Next.js configuration with Turbopack settings

**Sources:** [apps/playground/package.json:1-42](), [pnpm-lock.yaml:265-324]()

---

# Page: Infrastructure and Cross-Cutting Concerns

# Infrastructure and Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/playground/package.json](apps/playground/package.json)
- [apps/studio.giselles.ai/package.json](apps/studio.giselles.ai/package.json)
- [internal-packages/workflow-designer-ui/package.json](internal-packages/workflow-designer-ui/package.json)
- [package.json](package.json)
- [packages/giselle/package.json](packages/giselle/package.json)
- [pnpm-lock.yaml](pnpm-lock.yaml)
- [pnpm-workspace.yaml](pnpm-workspace.yaml)

</details>



This document covers the cross-cutting infrastructure and operational systems that support the Giselle platform. These include the build system, CI/CD pipelines, color token validation system, feature flag architecture, and deployment workflows. For specific details on feature flag implementation, see [Feature Flag System](#6.1). For theming and styling architecture, see [Theming and Styling System](#6.2). For release processes, see [Build and Release Process](#6.3). For monitoring and tracing, see [Observability and Telemetry](#6.4).

## Build System Architecture

The project uses a monorepo structure managed by pnpm workspaces with Turbo for build orchestration.

### Package Management

The root [package.json:1-53]() defines the build system configuration:

| Component | Version | Purpose |
|-----------|---------|---------|
| pnpm | 10.16.0 | Workspace and dependency management |
| Turbo | 2.4.2 | Monorepo build orchestration |
| Node.js | >=22 | Runtime requirement |
| Biome | catalog | Linting and formatting |
| Knip | ^5.61.3 | Dead code detection |
| TypeScript | catalog | Type checking |

The package manager is locked to pnpm 10.16.0 via the `packageManager` field, ensuring consistent dependency resolution across all environments.

### Build Scripts

```mermaid
graph TB
    subgraph "Build Commands"
        BUILD["pnpm build"]
        BUILD_SDK["pnpm build-sdk"]
        BUILD_DATA_TYPE["pnpm build-data-type"]
    end
    
    subgraph "Quality Commands"
        FORMAT["pnpm format"]
        CHECK_TYPES["pnpm check-types"]
        TEST["pnpm test"]
        TIDY["pnpm tidy"]
    end
    
    subgraph "Color Validation"
        REPORT_COLORS["pnpm report:colors"]
        GUARD_COLORS["pnpm guard:colors"]
        LINT_COLORS["pnpm lint:colors:code"]
        COMPAT_TOKENS["pnpm report:compat-tokens"]
    end
    
    subgraph "Development"
        DEV["pnpm dev"]
        DEV_STUDIO["pnpm dev:studio.giselles.ai"]
    end
    
    subgraph "Release"
        CHANGESET["pnpm changeset"]
        VERSION["pnpm version"]
    end
    
    BUILD --> TURBO_BUILD["turbo build"]
    BUILD_SDK --> TURBO_BUILD_SDK["turbo build --filter '@giselle-sdk/*'"]
    
    FORMAT --> BIOME["biome check --write"]
    CHECK_TYPES --> TURBO_TYPES["turbo check-types"]
    TIDY --> KNIP["knip --no-config-hints"]
    
    REPORT_COLORS --> RG_SCAN["ripgrep color scan"]
    GUARD_COLORS --> VALIDATE["validate against baseline"]
    LINT_COLORS --> TS_TSX_LINT["TS/TSX color linting"]
    COMPAT_TOKENS --> COMPAT_SCAN["compat token inventory"]
    
    DEV --> TURBO_DEV["turbo dev --filter playground"]
    DEV_STUDIO --> TURBO_DEV_STUDIO["turbo dev --filter studio.giselles.ai"]
    
    CHANGESET --> CHANGESETS_CLI["@changesets/cli"]
    VERSION --> CHANGESETS_VERSION["changesets version"]
```

**Sources:** [package.json:5-33]()

The build system provides granular filtering through Turbo, enabling selective builds of SDK packages without rebuilding the entire monorepo. The `build-sdk` command is frequently used in CI and deployment workflows.

## Continuous Integration Pipeline

The CI pipeline implements multiple quality gates that run on every push and pull request.

### CI Workflow Architecture

```mermaid
sequenceDiagram
    participant DEV as "Developer"
    participant GH as "GitHub Actions"
    participant BIOME as "Biome CI"
    participant KNIP as "Knip"
    participant TURBO as "Turbo Build"
    participant RG as "ripgrep"
    participant STYLELINT as "Stylelint"
    participant VITEST as "Vitest"
    participant ARTIFACT as "Artifact Storage"
    
    DEV->>GH: "Push / PR"
    GH->>BIOME: "biome ci ."
    BIOME-->>GH: "Lint & format check"
    
    GH->>KNIP: "pnpm knip"
    KNIP-->>GH: "Unused code check"
    
    GH->>TURBO: "pnpm build-sdk"
    TURBO-->>GH: "SDK build complete"
    
    GH->>RG: "Install ripgrep"
    RG->>RG: "pnpm report:colors"
    RG->>ARTIFACT: "Upload report-colors.json"
    
    GH->>RG: "pnpm guard:colors"
    RG-->>GH: "Baseline comparison (non-blocking)"
    
    GH->>STYLELINT: "pnpm lint:colors:code"
    STYLELINT-->>GH: "TS/TSX color lint (non-blocking)"
    
    GH->>VITEST: "pnpm test"
    VITEST-->>GH: "Test results"
```

**Sources:** [.github/workflows/ci.yml:1-50]()

### Color Validation System

The color validation system is a sophisticated multi-stage pipeline designed to enforce color token consistency during the migration from legacy color usage to Tailwind v4's token system.

```mermaid
graph TB
    subgraph "Stage 1: Detection"
        RG_SCAN["ripgrep Scan"]
        HEX_PATTERN["Detect #RGB #RGBA #RRGGBB #RRGGBBAA"]
        FUNC_PATTERN["Detect rgb/rgba/hsl/hsla/oklch"]
        TW_PATTERN["Detect text-black-* bg-black-* border-white-*"]
    end
    
    subgraph "Stage 2: Reporting"
        REPORT_JSON["report-colors.json"]
        FINDINGS_COUNT["Count findings by type"]
        ARTIFACT_UPLOAD["Upload as CI artifact"]
    end
    
    subgraph "Stage 3: Validation"
        GUARD_COLORS["guard-colors.mjs"]
        BASELINE_COMPARE["Compare against baseline"]
        WARN_REGRESSIONS["Warn on new violations"]
    end
    
    subgraph "Stage 4: Code Linting"
        LINT_COLORS["lint-colors-code.mjs"]
        CHECK_TS_TSX["Check TS/TSX files"]
        CHECK_TAILWIND["Check Tailwind classes"]
        PRINT_FINDINGS["Print human-readable report"]
    end
    
    subgraph "Stage 5: Stylelint"
        STYLELINT_CONFIG[".stylelintrc.json"]
        BLOCK_HEX["Block hex colors"]
        BLOCK_FUNC["Block rgb/rgba/hsl/hsla/oklch"]
    end
    
    RG_SCAN --> HEX_PATTERN
    RG_SCAN --> FUNC_PATTERN
    RG_SCAN --> TW_PATTERN
    
    HEX_PATTERN --> REPORT_JSON
    FUNC_PATTERN --> REPORT_JSON
    TW_PATTERN --> REPORT_JSON
    
    REPORT_JSON --> FINDINGS_COUNT
    FINDINGS_COUNT --> ARTIFACT_UPLOAD
    REPORT_JSON --> GUARD_COLORS
    
    GUARD_COLORS --> BASELINE_COMPARE
    BASELINE_COMPARE --> WARN_REGRESSIONS
    
    LINT_COLORS --> CHECK_TS_TSX
    LINT_COLORS --> CHECK_TAILWIND
    CHECK_TS_TSX --> PRINT_FINDINGS
    CHECK_TAILWIND --> PRINT_FINDINGS
    
    STYLELINT_CONFIG --> BLOCK_HEX
    STYLELINT_CONFIG --> BLOCK_FUNC
```

**Sources:** [scripts/lint-colors-code.mjs:1-134](), [.github/workflows/ci.yml:30-47](), [.stylelintrc.json:1-17]()

#### Color Detection Patterns

The `lint-colors-code.mjs` script implements three detection strategies:

1. **Hex Color Detection** [scripts/lint-colors-code.mjs:95-98]()
   - Pattern: `#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})(?![0-9a-fA-F])`
   - Matches #RGB, #RGBA, #RRGGBB, #RRGGBBAA formats
   - Negative lookahead prevents partial matches

2. **Functional Color Detection** [scripts/lint-colors-code.mjs:101]()
   - Pattern: `\b(?:rgba?|hsla?|oklch)\s*\(`
   - Matches rgb(), rgba(), hsl(), hsla(), oklch() functions

3. **Tailwind Direct Scale Detection** [scripts/lint-colors-code.mjs:107-109]()
   - Pattern: `(?:text|bg|border)-(?:black|white)\b(?:-[0-9]{1,3})?(?:\/[0-9]{1,3})?`
   - Matches direct black/white scale usage in Tailwind classes
   - Supports opacity variants (e.g., `text-black-600/20`)

#### Stylelint Configuration

The [.stylelintrc.json:1-17]() enforces CSS-level restrictions:

```json
{
  "rules": {
    "color-no-hex": [true, { "severity": "warning" }],
    "function-disallowed-list": [["rgb", "rgba", "hsl", "hsla", "oklch"], { "severity": "warning" }]
  }
}
```

This blocks hex and functional colors in CSS files, with exceptions for the token definition file [.stylelintrc.json:10]().

#### Compatibility Token Tracking

The [scripts/compat-tokens-inventory.mjs:1-57]() script tracks usage of legacy color tokens during migration:

| Token | Purpose |
|-------|---------|
| `--color-white-900` | Legacy white scale |
| `--color-black-600` | Legacy black scale |
| `--color-black-850` | Dark theme base |
| `--color-white-850` | Light theme base |

These tokens are tracked separately from the token definition file [scripts/compat-tokens-inventory.mjs:34](), enabling staged removal after semantic token migration.

**Sources:** [scripts/compat-tokens-inventory.mjs:4-56](), [docs/compat-tokens-inventory.md:1-37]()

## Release Management

The release process uses Changesets for version management and automated PR creation.

### Changeset Configuration

```mermaid
graph LR
    subgraph "Changeset Config"
        CONFIG[".changeset/config.json"]
        IGNORE["Ignore: @giselle-sdk/*, @giselle-internal/*"]
        UPDATE_INTERNAL["updateInternalDependencies: patch"]
        BASE_BRANCH["baseBranch: main"]
    end
    
    subgraph "Developer Actions"
        ADD_CHANGESET["pnpm changeset"]
        DESCRIBE_CHANGE["Describe change & affected packages"]
    end
    
    subgraph "Automation"
        RELEASE_PR["Release PR (auto-created)"]
        VERSION_BUMP["changesets version"]
        PUBLISH["changesets publish"]
    end
    
    CONFIG --> IGNORE
    CONFIG --> UPDATE_INTERNAL
    CONFIG --> BASE_BRANCH
    
    ADD_CHANGESET --> DESCRIBE_CHANGE
    DESCRIBE_CHANGE --> RELEASE_PR
    
    RELEASE_PR --> VERSION_BUMP
    VERSION_BUMP --> PUBLISH
```

**Sources:** [.changeset/config.json:1-12]()

The configuration [.changeset/config.json:10]() excludes SDK and internal packages from automatic version management, as they follow independent versioning schemes.

### Release Workflow

The [.github/workflows/release.yml:1-39]() implements the Changeset Check workflow:

1. Triggered on pull requests to `main`
2. Executes `pnpm version` via Changesets action
3. Creates release PRs with bundled changes
4. Generates GitHub releases automatically

**Sources:** [.github/workflows/release.yml:9-38]()

## Deployment Pipelines

The system has separate deployment workflows for different components.

### Trigger.dev Deployment

```mermaid
sequenceDiagram
    participant GH as "GitHub (main push)"
    participant CI as "CI Runner"
    participant PNPM as "pnpm"
    participant TURBO as "Turbo"
    participant TRIGGER as "Trigger.dev CLI"
    participant PROD as "Trigger.dev Production"
    
    GH->>CI: "Push to main"
    CI->>PNPM: "pnpm install --frozen-lockfile"
    PNPM-->>CI: "Dependencies installed"
    
    CI->>TURBO: "pnpm build-sdk"
    TURBO-->>CI: "SDK packages built"
    
    CI->>TRIGGER: "pnpm dlx trigger.dev@latest deploy"
    Note over CI,TRIGGER: "Working directory: apps/studio.giselles.ai"
    TRIGGER->>PROD: "Deploy background job workers"
    PROD-->>TRIGGER: "Deployment complete"
```

**Sources:** [.github/workflows/release-trigger-prod.yml:1-25]()

The Trigger.dev deployment [.github/workflows/release-trigger-prod.yml:20-24]() runs on every push to `main`, deploying background job workers defined in the studio application. The `TRIGGER_ACCESS_TOKEN` secret [.github/workflows/release-trigger-prod.yml:22]() authenticates the deployment.

### Vercel Deployment

Vercel deployments are configured separately and handle:
- Studio application deployment (`studio.giselles.ai`)
- Preview deployments for pull requests
- Edge function deployments

The studio build uses Turbopack via the `--turbopack` flag for faster builds.

## End-to-End Testing

The E2E testing workflow runs on a schedule and supports manual triggering.

### E2E Workflow Configuration

```mermaid
graph TB
    subgraph "Trigger Conditions"
        MANUAL["Manual: workflow_dispatch"]
        SCHEDULE["Schedule: Weekdays 9:00 & 18:00 JST"]
    end
    
    subgraph "Setup Phase"
        CHECKOUT["Checkout code"]
        INSTALL_DEPS["pnpm install"]
        DETECT_VERSION["Extract Playwright version"]
        CACHE_BROWSERS["Cache Playwright browsers"]
        INSTALL_BROWSERS["Install browsers & OS deps"]
    end
    
    subgraph "Execution Phase"
        RUN_TESTS["pnpm test:e2e"]
        INJECT_SECRETS["PLAYWRIGHT_BASE_URL<br/>PLAYWRIGHT_LOGIN_EMAIL<br/>PLAYWRIGHT_LOGIN_PASSWORD"]
    end
    
    MANUAL --> CHECKOUT
    SCHEDULE --> CHECKOUT
    
    CHECKOUT --> INSTALL_DEPS
    INSTALL_DEPS --> DETECT_VERSION
    DETECT_VERSION --> CACHE_BROWSERS
    CACHE_BROWSERS --> INSTALL_BROWSERS
    INSTALL_BROWSERS --> RUN_TESTS
    
    INJECT_SECRETS --> RUN_TESTS
```

**Sources:** [.github/workflows/e2e.yml:1-46]()

The workflow [.github/workflows/e2e.yml:9-10]() runs twice daily on weekdays and supports manual execution with custom base URLs [.github/workflows/e2e.yml:4-8](). Playwright browser caching [.github/workflows/e2e.yml:30-35]() optimizes execution time by keying on the Playwright version.

### Test Execution Environment

The E2E tests run in the studio application directory [.github/workflows/e2e.yml:41]() and require three secrets:

| Secret | Purpose |
|--------|---------|
| `PLAYWRIGHT_BASE_URL` | Target environment URL |
| `PLAYWRIGHT_LOGIN_EMAIL` | Authentication email |
| `PLAYWRIGHT_LOGIN_PASSWORD` | Authentication password |

## License Compliance

The license compliance workflow tracks third-party dependencies and their licenses.

### License Finder Integration

```mermaid
graph TB
    subgraph "Trigger Conditions"
        PUSH_MAIN["Push to main"]
        PR["Pull Request"]
    end
    
    subgraph "Change Detection"
        CACHE_KEY["Hash: workflow file, pnpm-lock, configs"]
        CACHE_HIT{"Cache hit?"}
        FILES_CHANGED["Set files_changed flag"]
    end
    
    subgraph "Execution"
        INSTALL_RUBY["Install Ruby 3.3"]
        INSTALL_LF["gem install license_finder"]
        RUN_LF["license_finder"]
        GENERATE_REPORT["Generate markdown report"]
    end
    
    subgraph "Commit Phase"
        FORK_CHECK{"Fork PR?"}
        COMMIT_REPORT["Commit docs/packages-license.md"]
        PUSH_BRANCH["Push to PR branch"]
    end
    
    PUSH_MAIN --> CACHE_KEY
    PR --> CACHE_KEY
    
    CACHE_KEY --> CACHE_HIT
    CACHE_HIT -->|"No"| FILES_CHANGED
    CACHE_HIT -->|"Yes"| SKIP["Skip execution"]
    
    FILES_CHANGED --> INSTALL_RUBY
    INSTALL_RUBY --> INSTALL_LF
    INSTALL_LF --> RUN_LF
    RUN_LF --> GENERATE_REPORT
    
    GENERATE_REPORT --> FORK_CHECK
    FORK_CHECK -->|"No"| COMMIT_REPORT
    FORK_CHECK -->|"Yes"| END["Skip commit"]
    
    COMMIT_REPORT --> PUSH_BRANCH
```

**Sources:** [.github/workflows/license.yml:1-113]()

The workflow [.github/workflows/license.yml:50-68]() uses caching to skip execution when dependency files haven't changed. For non-fork PRs, it generates and commits a license report to [.github/workflows/license.yml:25](), using a GitHub App token [.github/workflows/license.yml:32-38]() for authentication.

## Development Environment Configuration

The project provides development environment configuration for Zed editor.

### Zed Tasks Configuration

The [.zed/tasks.json:1-9]() defines a test task that integrates with Zed's symbol navigation:

```json
{
  "label": "test with symbol",
  "command": "pnpm vitest watch",
  "cwd": "$ZED_DIRNAME",
  "args": ["$ZED_FILENAME", "--testNamePattern", "$ZED_SYMBOL"],
  "tags": ["js-test", "ts-test", "tsx-test"]
}
```

This enables running specific tests by symbol name directly from the editor, with watch mode for rapid iteration.

**Sources:** [.zed/tasks.json:1-9]()

## Semantic Token Migration Strategy

The color system is undergoing a migration to semantic tokens aligned with Tailwind v4.

### Current State

The [internal-packages/ui/styles/semantic.css:1-17]() file defines the semantic token scaffold:

```css
:root {
  --color-text: var(--color-gray-50);
  --color-text-inverse: var(--color-white);
  --color-surface: var(--color-gray-950);
  --color-border: var(--color-gray-900);
  --color-border-muted: var(--color-gray-700);
  --color-focused: var(--color-info-500);
  --color-text-secondary: #505d7b;
  --color-link-muted: var(--color-text-secondary);
}
```

Note [internal-packages/ui/styles/semantic.css:1]() indicates this is not applied globally yet, representing Phase 1.5 of the migration.

### Migration Goals

Per [docs/tailwind-v4-verification.md:1-18]():

1. Confirm `@theme` primitives in token definitions
2. Ensure v3 bridge provides semantic utilities
3. Validate CI color report generation
4. Prepare isolated playground for v4 bump

The strategy involves staged removal of compatibility tokens after semantic migration, tracked through the compatibility token inventory system.

**Sources:** [internal-packages/ui/styles/semantic.css:1-17](), [docs/tailwind-v4-verification.md:1-18](), [docs/compat-tokens-inventory.md:1-37]()

## Summary

The infrastructure and operations layer provides:

- **Build orchestration** via Turbo with selective filtering
- **Multi-stage CI/CD** with Biome, Knip, and color validation
- **Color token enforcement** through ripgrep, stylelint, and compatibility tracking
- **Automated releases** via Changesets with PR automation
- **Dual deployment** to Trigger.dev (background jobs) and Vercel (web app)
- **E2E testing** with Playwright and browser caching
- **License compliance** with automated report generation
- **Semantic token migration** strategy for Tailwind v4 readiness

These systems enable safe, consistent development and deployment while maintaining code quality and visual token consistency across the monorepo.

---

# Page: Feature Flag System

# Feature Flag System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/playground/app/workspaces/[workspaceId]/layout.tsx](apps/playground/app/workspaces/[workspaceId]/layout.tsx)
- [apps/studio.giselles.ai/app/deprecated/workspaces/[workspaceId]/layout.tsx](apps/studio.giselles.ai/app/deprecated/workspaces/[workspaceId]/layout.tsx)
- [apps/studio.giselles.ai/app/workspaces/[workspaceId]/data-loader.ts](apps/studio.giselles.ai/app/workspaces/[workspaceId]/data-loader.ts)
- [apps/studio.giselles.ai/flags.ts](apps/studio.giselles.ai/flags.ts)
- [packages/giselle/src/react/feature-flags/context.ts](packages/giselle/src/react/feature-flags/context.ts)
- [packages/giselle/src/react/workspace/provider.tsx](packages/giselle/src/react/workspace/provider.tsx)

</details>



## Purpose and Scope

The Feature Flag System provides runtime control over feature availability in the Giselle AI platform. It enables conditional feature enablement based on environment (development vs production) and supports gradual rollouts via Vercel Edge Config in production. This document covers flag definition, environment-aware decision logic, distribution through React Context, and consumption patterns in UI components.

For information about how feature flags control Stage workflow execution, see [Stage System and Task Execution](#3.1.2). For usage limits and tier-based feature access, see [Language Models and AI Integration](#2.3).

---

## Architecture Overview

The feature flag system follows a server-side evaluation pattern with client-side distribution through React Context:

```mermaid
graph TB
    subgraph "Flag Definition Layer"
        FlagDef["flag() definitions<br/>flags.ts"]
        DecideLogic["decide() logic<br/>Environment-aware"]
        EdgeConfig["Vercel Edge Config<br/>Production flags"]
        EnvVars["Environment Variables<br/>Development flags"]
    end
    
    subgraph "Evaluation Layer"
        LayoutServer["Layout Component<br/>apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx"]
        FlagEval["Flag Evaluation<br/>await flagName()"]
    end
    
    subgraph "Distribution Layer"
        WorkspaceProvider["WorkspaceProvider<br/>packages/giselle/src/react/workspace/provider.tsx"]
        FeatureFlagContext["FeatureFlagContext<br/>packages/giselle/src/react/feature-flags/context.ts"]
    end
    
    subgraph "Consumption Layer"
        UseFeatureFlag["useFeatureFlag() hook"]
        Toolbar["Toolbar<br/>internal-packages/workflow-designer-ui"]
        PropsPanel["Properties Panels"]
        OtherComponents["Other UI Components"]
    end
    
    FlagDef --> DecideLogic
    DecideLogic --> EnvVars
    DecideLogic --> EdgeConfig
    
    DecideLogic --> FlagEval
    FlagEval --> LayoutServer
    
    LayoutServer --> WorkspaceProvider
    WorkspaceProvider --> FeatureFlagContext
    
    FeatureFlagContext --> UseFeatureFlag
    UseFeatureFlag --> Toolbar
    UseFeatureFlag --> PropsPanel
    UseFeatureFlag --> OtherComponents
```

**Sources:** [apps/studio.giselles.ai/flags.ts:1-196](), [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:1-146](), [packages/giselle/src/react/workspace/provider.tsx:1-72](), [packages/giselle/src/react/feature-flags/context.ts:1-25]()

---

## Flag Definition System

Feature flags are defined using the `flag()` function from the `flags/next` package. Each flag follows a consistent structure:

| Component | Type | Purpose |
|-----------|------|---------|
| `key` | `string` | Unique identifier for the flag |
| `decide()` | `async function` | Evaluation logic (environment-aware) |
| `description` | `string` | Human-readable description |
| `defaultValue` | `boolean` | Fallback value if evaluation fails |
| `options` | `array` | Available values (typically `[false, true]`) |

### Flag Definition Pattern

```mermaid
graph LR
    FlagCall["flag<boolean>()"]
    Key["key: 'flag-name'"]
    Decide["decide(): async fn"]
    Desc["description: 'Enable...'"]
    Default["defaultValue: false"]
    Options["options: [false, true]"]
    
    FlagCall --> Key
    FlagCall --> Decide
    FlagCall --> Desc
    FlagCall --> Default
    FlagCall --> Options
```

### Example Flag Definition

The `runV3Flag` demonstrates the standard pattern:

[apps/studio.giselles.ai/flags.ts:43-60]()

```typescript
export const runV3Flag = flag<boolean>({
  key: "run-v3",
  async decide() {
    if (process.env.NODE_ENV === "development") {
      return takeLocalEnv("RUN_V3_FLAG");
    }
    const edgeConfig = await get(`flag__${this.key}`);
    if (edgeConfig === undefined) {
      return false;
    }
    return edgeConfig === true || edgeConfig === "true";
  },
  description: "Enable Run v3",
  options: [
    { value: false, label: "disable" },
    { value: true, label: "Enable" },
  ],
});
```

**Sources:** [apps/studio.giselles.ai/flags.ts:43-60]()

---

## Environment-Aware Decision Logic

The `decide()` function implements environment-specific evaluation strategies:

```mermaid
flowchart TD
    Start["decide() invoked"]
    CheckEnv{"process.env.NODE_ENV<br/>=== 'development'?"}
    LocalEnv["takeLocalEnv(envKey)"]
    CheckLocalEnv{"Environment variable<br/>defined and !== 'false'?"}
    ReturnTrue["return true"]
    ReturnFalse["return false"]
    EdgeConfig["get(`flag__${this.key}`)<br/>from Vercel Edge Config"]
    CheckEdge{"edgeConfig<br/>value?"}
    ParseEdge["Parse boolean<br/>(true or 'true')"]
    
    Start --> CheckEnv
    CheckEnv -->|Yes| LocalEnv
    CheckEnv -->|No| EdgeConfig
    
    LocalEnv --> CheckLocalEnv
    CheckLocalEnv -->|Yes| ReturnTrue
    CheckLocalEnv -->|No| ReturnFalse
    
    EdgeConfig --> CheckEdge
    CheckEdge -->|undefined| ReturnFalse
    CheckEdge -->|defined| ParseEdge
    ParseEdge --> ReturnTrue
```

### Local Development Helper

The `takeLocalEnv()` function handles development environment flags:

[apps/studio.giselles.ai/flags.ts:4-15]()

```typescript
function takeLocalEnv(localEnvironmentKey: string) {
  if (process.env.NODE_ENV !== "development") {
    return false;
  }
  if (
    process.env[localEnvironmentKey] === undefined ||
    process.env[localEnvironmentKey] === "false"
  ) {
    return false;
  }
  return true;
}
```

### Development Environment Variables

| Flag | Environment Variable | Example |
|------|---------------------|---------|
| `developerFlag` | `DEVELOPER_FLAG` | `DEVELOPER_FLAG=true` |
| `webSearchActionFlag` | `WEB_SEARCH_ACTION_FLAG` | `WEB_SEARCH_ACTION_FLAG=true` |
| `runV3Flag` | `RUN_V3_FLAG` | `RUN_V3_FLAG=true` |
| `layoutV3Flag` | `LAYOUT_V3_FLAG` | `LAYOUT_V3_FLAG=true` |
| `experimental_storageFlag` | `EXPERIMENTAL_STORAGE_FLAG` | `EXPERIMENTAL_STORAGE_FLAG=true` |
| `stageFlag` | `STAGE_FLAG` | `STAGE_FLAG=true` |
| `aiGatewayFlag` | `AI_GATEWAY_FLAG` | `AI_GATEWAY_FLAG=true` |
| `resumableGenerationFlag` | `RESUMABLE_GENERATION_FLAG` | `RESUMABLE_GENERATION_FLAG=true` |
| `newEditorFlag` | `NEW_EDITOR_FLAG` | `NEW_EDITOR_FLAG=true` |
| `docVectorStoreFlag` | `DOC_VECTOR_STORE_FLAG` | `DOC_VECTOR_STORE_FLAG=true` |

### Production Vercel Edge Config

In production, flags are retrieved from Vercel Edge Config with keys prefixed by `flag__`:

[apps/studio.giselles.ai/flags.ts:49]()

```typescript
const edgeConfig = await get(`flag__${this.key}`);
```

For a flag with `key: "run-v3"`, the Edge Config key is `flag__run-v3`.

**Sources:** [apps/studio.giselles.ai/flags.ts:1-196]()

---

## Flag Distribution Pattern

Feature flags are evaluated server-side in Next.js layouts and distributed to client components via React Context:

```mermaid
sequenceDiagram
    participant Layout as "Layout (Server)"
    participant FlagModule as "flags.ts"
    participant EdgeConfig as "Vercel Edge Config"
    participant Provider as "WorkspaceProvider"
    participant Context as "FeatureFlagContext"
    participant Component as "UI Component"
    
    Layout->>FlagModule: await runV3Flag()
    FlagModule->>EdgeConfig: get('flag__run-v3')
    EdgeConfig-->>FlagModule: boolean value
    FlagModule-->>Layout: evaluated value
    
    Layout->>FlagModule: await webSearchActionFlag()
    FlagModule-->>Layout: evaluated value
    
    Note over Layout: Evaluate all flags
    
    Layout->>Provider: <WorkspaceProvider featureFlag={{...}}>
    Provider->>Context: <FeatureFlagContext value={{...}}>
    
    Component->>Context: useFeatureFlag()
    Context-->>Component: { runV3, webSearchAction, ... }
    Component->>Component: Conditional rendering
```

### Server-Side Evaluation

Flags are evaluated in the workspace layout component:

[apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:71-77]()

```typescript
const runV3 = await runV3Flag();
const webSearchAction = await webSearchActionFlag();
const layoutV3 = await layoutV3Flag();
const experimental_storage = await experimental_storageFlag();
const stage = await stageFlag();
const aiGateway = await aiGatewayFlag();
const resumableGeneration = await resumableGenerationFlag();
```

### Context Provider Initialization

Evaluated flags are passed to the `WorkspaceProvider`:

[apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:107-115]()

```typescript
<WorkspaceProvider
  featureFlag={{
    runV3,
    webSearchAction,
    layoutV3,
    experimental_storage,
    stage,
    aiGateway,
    resumableGeneration,
  }}
  {/* other props */}
>
```

### WorkspaceProvider Implementation

The `WorkspaceProvider` wraps children with `FeatureFlagContext`:

[packages/giselle/src/react/workspace/provider.tsx:44-55]()

```typescript
return (
  <FeatureFlagContext
    value={{
      runV3: featureFlag?.runV3 ?? false,
      webSearchAction: featureFlag?.webSearchAction ?? false,
      layoutV3: featureFlag?.layoutV3 ?? false,
      experimental_storage: featureFlag?.experimental_storage ?? false,
      stage: featureFlag?.stage ?? false,
      aiGateway: featureFlag?.aiGateway ?? false,
      resumableGeneration: featureFlag?.resumableGeneration ?? false,
    }}
  >
    {/* nested providers */}
  </FeatureFlagContext>
);
```

**Sources:** [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:71-115](), [packages/giselle/src/react/workspace/provider.tsx:44-72](), [packages/giselle/src/react/feature-flags/context.ts:1-25]()

---

## Flag Consumption in UI Components

UI components access feature flags through the `useFeatureFlag()` hook:

### Hook Interface

[packages/giselle/src/react/feature-flags/context.ts:3-24]()

```typescript
export interface FeatureFlagContextValue {
  runV3: boolean;
  webSearchAction: boolean;
  layoutV3: boolean;
  experimental_storage: boolean;
  stage: boolean;
  aiGateway: boolean;
  resumableGeneration: boolean;
}

export function useFeatureFlag(): FeatureFlagContextValue {
  const context = useContext(FeatureFlagContext);
  if (!context) {
    throw new Error(
      "useFeatureFlagContext must be used within a FeatureFlagProvider"
    );
  }
  return context;
}
```

### Conditional Rendering Pattern

The Toolbar component demonstrates feature-gated UI rendering:

[internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:93]()

```typescript
const { webSearchAction } = useFeatureFlag();
```

[internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:856-863]()

```typescript
{actionProviders
  .filter((actionProvider) => {
    // Filter based on feature flags
    if (actionProvider === "web-search") {
      return webSearchAction;
    }
    return true; // Show other providers by default
  })
  .map((actionProvider) => (
    // render action node button
  ))}
```

### Conditional Feature Availability

The Manual Trigger properties panel uses the `stage` flag:

[internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/manual-trigger/manual-trigger-properties-panel.tsx:39]()

```typescript
const { experimental_storage, stage } = useFeatureFlag();
```

[internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/manual-trigger/manual-trigger-properties-panel.tsx:235-251]()

```typescript
{stage && (
  <div className="mt-[8px]">
    <Toggle
      name="staged"
      checked={staged}
      onCheckedChange={setStaged}
    >
      <label className="text-[12px]" htmlFor="staged">
        Enable this trigger to run in Stage
        <span className="text-text-muted ml-[8px]">
          (This can be changed later)
        </span>
      </label>
      <div className="flex-grow mx-[12px] h-[1px] bg-element-background" />
    </Toggle>
  </div>
)}
```

**Sources:** [packages/giselle/src/react/feature-flags/context.ts:3-24](), [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:93](), [internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx:856-863](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/manual-trigger/manual-trigger-properties-panel.tsx:39-251]()

---

## Available Feature Flags

| Flag | Key | Purpose |
|------|-----|---------|
| `developerFlag` | `developer` | Enables developer-only features and debug tools |
| `webSearchActionFlag` | `web-search-action` | Enables web search action nodes in workflows |
| `runV3Flag` | `run-v3` | Enables version 3 of the workflow execution engine |
| `layoutV3Flag` | `layout-v3` | Enables version 3 of the application layout |
| `experimental_storageFlag` | `experimental-storage` | Enables experimental GiselleStorage instead of legacy storage |
| `stageFlag` | `stage` | Enables the Stage system for workflow execution and monitoring |
| `aiGatewayFlag` | `ai-gateway` | Enables AI Gateway for LLM request routing |
| `resumableGenerationFlag` | `resumable-generation` | Enables resumable generation with chunk-based writing |
| `newEditorFlag` | `new-editor` | Enables the new workflow editor implementation |
| `docVectorStoreFlag` | `doc-vector-store` | Enables document vector store ingestion (PDF text and image) |

### Flag Definitions by Category

**Workflow Execution:**
- [apps/studio.giselles.ai/flags.ts:43-60]() - `runV3Flag`
- [apps/studio.giselles.ai/flags.ts:138-155]() - `resumableGenerationFlag`

**UI/Layout:**
- [apps/studio.giselles.ai/flags.ts:62-79]() - `layoutV3Flag`
- [apps/studio.giselles.ai/flags.ts:157-174]() - `newEditorFlag`

**Storage:**
- [apps/studio.giselles.ai/flags.ts:81-98]() - `experimental_storageFlag`

**Feature Access:**
- [apps/studio.giselles.ai/flags.ts:30-41]() - `webSearchActionFlag`
- [apps/studio.giselles.ai/flags.ts:100-117]() - `stageFlag`
- [apps/studio.giselles.ai/flags.ts:178-195]() - `docVectorStoreFlag`

**Infrastructure:**
- [apps/studio.giselles.ai/flags.ts:119-136]() - `aiGatewayFlag`
- [apps/studio.giselles.ai/flags.ts:17-28]() - `developerFlag`

**Sources:** [apps/studio.giselles.ai/flags.ts:1-196]()

---

## Development vs Production Configuration

The system supports different configuration patterns for development and production environments:

```mermaid
graph TB
    subgraph "Development Environment"
        DevEnv["NODE_ENV === 'development'"]
        EnvVars["Environment Variables<br/>FEATURE_FLAG=true/false"]
        LocalCheck["takeLocalEnv() check"]
        DevResult["Immediate boolean result"]
    end
    
    subgraph "Production Environment"
        ProdEnv["NODE_ENV === 'production'"]
        EdgeConfigAPI["@vercel/edge-config<br/>get() API"]
        RemoteCheck["await get(`flag__key`)"]
        EdgeParse["Parse boolean/string"]
        ProdResult["Boolean result"]
    end
    
    subgraph "Playground Application"
        PlaygroundLayout["apps/playground/app/workspaces/[workspaceId]/layout.tsx"]
        HardcodedFlags["Hardcoded flag values"]
        PlaygroundResult["Static configuration"]
    end
    
    DevEnv --> EnvVars
    EnvVars --> LocalCheck
    LocalCheck --> DevResult
    
    ProdEnv --> EdgeConfigAPI
    EdgeConfigAPI --> RemoteCheck
    RemoteCheck --> EdgeParse
    EdgeParse --> ProdResult
    
    PlaygroundLayout --> HardcodedFlags
    HardcodedFlags --> PlaygroundResult
```

### Playground Static Configuration

The playground application uses hardcoded feature flags for simplified local development:

[apps/playground/app/workspaces/[workspaceId]/layout.tsx:5-19]()

```typescript
export default function Layout({ children }: { children: ReactNode }) {
  return (
    <WorkspaceProvider
      featureFlag={{
        runV3: true,
        webSearchAction: false,
        layoutV3: true,
        experimental_storage: true,
        stage: true,
        aiGateway: false,
        resumableGeneration: false,
      }}
    >
      {children}
    </WorkspaceProvider>
  );
}
```

### Development Configuration Example

For local development of the Studio app:

```bash
# .env.local
DEVELOPER_FLAG=true
WEB_SEARCH_ACTION_FLAG=true
RUN_V3_FLAG=true
LAYOUT_V3_FLAG=false
EXPERIMENTAL_STORAGE_FLAG=true
STAGE_FLAG=true
AI_GATEWAY_FLAG=false
RESUMABLE_GENERATION_FLAG=true
DOC_VECTOR_STORE_FLAG=true
```

### Production Edge Config Example

Production flags are managed in Vercel Edge Config with these keys:

```json
{
  "flag__developer": false,
  "flag__web-search-action": true,
  "flag__run-v3": true,
  "flag__layout-v3": false,
  "flag__experimental-storage": true,
  "flag__stage": true,
  "flag__ai-gateway": false,
  "flag__resumable-generation": false,
  "flag__doc-vector-store": false
}
```

**Sources:** [apps/studio.giselles.ai/flags.ts:4-15](), [apps/studio.giselles.ai/flags.ts:45-53](), [apps/playground/app/workspaces/[workspaceId]/layout.tsx:5-19]()

---

## Flag Lifecycle and Dependencies

```mermaid
graph TD
    subgraph "Definition Phase"
        DefineFlag["Define flag<br/>in flags.ts"]
        AddEnvVar["Add environment variable<br/>for development"]
        ConfigEdge["Configure Edge Config<br/>for production"]
    end
    
    subgraph "Type System Phase"
        UpdateContext["Update FeatureFlagContextValue<br/>interface"]
        UpdateProvider["Update WorkspaceProvider<br/>default values"]
    end
    
    subgraph "Evaluation Phase"
        EvalLayout["Add flag evaluation<br/>in layout.tsx"]
        PassProvider["Pass to WorkspaceProvider<br/>featureFlag prop"]
    end
    
    subgraph "Consumption Phase"
        UseHook["Component calls<br/>useFeatureFlag()"]
        ConditionalLogic["Implement conditional<br/>rendering/logic"]
    end
    
    DefineFlag --> AddEnvVar
    DefineFlag --> ConfigEdge
    DefineFlag --> UpdateContext
    
    UpdateContext --> UpdateProvider
    UpdateProvider --> EvalLayout
    
    EvalLayout --> PassProvider
    PassProvider --> UseHook
    UseHook --> ConditionalLogic
```

### Adding a New Feature Flag

**Step 1:** Define the flag in [apps/studio.giselles.ai/flags.ts]():

```typescript
export const myNewFlag = flag<boolean>({
  key: "my-new-feature",
  async decide() {
    if (process.env.NODE_ENV === "development") {
      return takeLocalEnv("MY_NEW_FEATURE_FLAG");
    }
    const edgeConfig = await get(`flag__${this.key}`);
    if (edgeConfig === undefined) {
      return false;
    }
    return edgeConfig === true || edgeConfig === "true";
  },
  description: "Enable my new feature",
  defaultValue: false,
  options: [
    { value: false, label: "disable" },
    { value: true, label: "Enable" },
  ],
});
```

**Step 2:** Update the `FeatureFlagContextValue` interface in [packages/giselle/src/react/feature-flags/context.ts:3-11]():

```typescript
export interface FeatureFlagContextValue {
  // ... existing flags
  myNewFeature: boolean;
}
```

**Step 3:** Update `WorkspaceProvider` default values in [packages/giselle/src/react/workspace/provider.tsx:45-54]():

```typescript
<FeatureFlagContext
  value={{
    // ... existing flags
    myNewFeature: featureFlag?.myNewFeature ?? false,
  }}
>
```

**Step 4:** Evaluate and pass the flag in [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx]():

```typescript
const myNewFeature = await myNewFlag();

// Later in JSX:
<WorkspaceProvider
  featureFlag={{
    // ... existing flags
    myNewFeature,
  }}
>
```

**Step 5:** Consume in components:

```typescript
const { myNewFeature } = useFeatureFlag();

if (myNewFeature) {
  // Render new feature
}
```

**Sources:** [apps/studio.giselles.ai/flags.ts:1-196](), [packages/giselle/src/react/feature-flags/context.ts:3-11](), [packages/giselle/src/react/workspace/provider.tsx:45-54](), [apps/studio.giselles.ai/app/workspaces/[workspaceId]/layout.tsx:71-115]()

---

# Page: UI Component Library and Theming

# UI Component Library and Theming

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/playground/app/ui/page.tsx](apps/playground/app/ui/page.tsx)
- [apps/studio.giselles.ai/app/(auth)/components/auth-container.tsx](apps/studio.giselles.ai/app/(auth)/components/auth-container.tsx)
- [internal-packages/ui/components/button.tsx](internal-packages/ui/components/button.tsx)
- [internal-packages/ui/components/dialog.tsx](internal-packages/ui/components/dialog.tsx)
- [internal-packages/ui/components/glass-dialog.tsx](internal-packages/ui/components/glass-dialog.tsx)
- [internal-packages/ui/style.css](internal-packages/ui/style.css)
- [internal-packages/ui/styles/semantic.css](internal-packages/ui/styles/semantic.css)
- [internal-packages/workflow-designer-ui/src/editor/chat/chat-panel.tsx](internal-packages/workflow-designer-ui/src/editor/chat/chat-panel.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/anthropic.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/anthropic.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/google.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/google.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/openai.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/openai.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/tab-content.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/tab-content.tsx)
- [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/tools/tool-provider/anthropic-web-search/anthropic-web-search.tsx](internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/tools/tool-provider/anthropic-web-search/anthropic-web-search.tsx)

</details>



This document covers the `@giselle-internal/ui` package, which provides a shared component library and theming system used across all applications in the Giselle platform. The package includes reusable UI components (buttons, dialogs, inputs, etc.), a CSS variable-based theming system, and support for multiple visual variants (glass, solid, outline).

For information about workspace-level context and feature flags, see [Workspace Context and Feature Flags](#6.1.1). For the workflow designer's specific UI components, see [Workflow Designer UI](#5).

## Package Structure

The UI package is located at `internal-packages/ui/` and serves as the foundational design system for the platform. It is consumed by both the Studio application and the Workflow Designer UI.

```mermaid
graph TB
    subgraph "Applications"
        Studio["studio.giselles.ai"]
        Playground["playground"]
    end
    
    subgraph "Internal Packages"
        WDCore["workflow-designer-ui"]
        UI["@giselle-internal/ui"]
    end
    
    subgraph "UI Package Exports"
        StyleCSS["style.css<br/>Theme Variables"]
        Components["Components<br/>Button, Dialog, Toggle, etc"]
        GlassSurface["GlassSurfaceLayers<br/>Glass Effect System"]
    end
    
    subgraph "Theme System"
        ThemeVars["@theme CSS Variables"]
        SemanticCSS["semantic.css<br/>Semantic Mappings"]
        TokensCSS["tokens.css<br/>Primitive Tokens"]
    end
    
    Studio --> WDCore
    Studio --> UI
    Playground --> UI
    WDCore --> UI
    
    UI --> StyleCSS
    UI --> Components
    UI --> GlassSurface
    
    StyleCSS --> ThemeVars
    StyleCSS --> SemanticCSS
    StyleCSS --> TokensCSS
```

**Sources:** [internal-packages/ui/style.css:1-5]()

## Theme System Architecture

The theming system is built on CSS custom properties defined in the `@theme` directive, providing a centralized color palette and styling tokens that cascade throughout the application.

### CSS Variable Organization

The theme is organized into several categories of variables:

| Category | Purpose | Example Variables |
|----------|---------|-------------------|
| Border | Border colors and variants | `--color-border`, `--color-border-focused`, `--color-border-selected` |
| Surface | Background colors for panels | `--color-surface-background`, `--color-elevated-surface-background` |
| Element | Interactive element states | `--color-element-hover`, `--color-element-active`, `--color-element-selected` |
| Text | Text colors and hierarchy | `--color-text`, `--color-text-muted`, `--color-text-accent` |
| Status | Semantic status colors | `--color-error`, `--color-success`, `--color-warning`, `--color-info` |
| Glass | Glass morphism effects | `--glass-button-bg`, `--shadow-glass`, `--glass-stroke-gradient` |
| Solid | Solid button styling | `--solid-button-bg`, `--solid-button-shadow` |
| Outline | Outline button styling | `--shadow-outline-button`, `--color-outline-button-bg` |

**Sources:** [internal-packages/ui/style.css:5-225]()

### Theme Variable Hierarchy

```mermaid
graph LR
    subgraph "Theme Layers"
        Primitives["Primitive Tokens<br/>tokens.css"]
        Theme["@theme Block<br/>style.css"]
        Semantic["Semantic Layer<br/>semantic.css"]
        Components["Component Styles<br/>button.tsx, dialog.tsx"]
    end
    
    Primitives --> Theme
    Theme --> Semantic
    Semantic --> Components
    Theme --> Components
```

The theme system follows a layered approach where primitive tokens are defined first, then mapped to theme variables in the `@theme` block, with an optional semantic layer for higher-level abstractions.

**Sources:** [internal-packages/ui/style.css:1-3](), [internal-packages/ui/styles/semantic.css:1-21]()

## Component Variants

The UI library supports multiple visual variants that provide different visual treatments for components. These variants are implemented consistently across components using data attributes and CSS.

### Variant System

```mermaid
graph TB
    subgraph "Button Variants"
        Subtle["subtle<br/>Hover background only"]
        Filled["filled<br/>Background + border"]
        Solid["solid<br/>Gradient background"]
        Glass["glass<br/>Frosted glass effect"]
        Outline["outline<br/>Border only"]
        Link["link<br/>No background"]
        Primary["primary<br/>Emphasized action"]
        Destructive["destructive<br/>Danger actions"]
    end
    
    subgraph "Dialog Variants"
        DefaultDialog["default<br/>Standard dialog"]
        GlassDialog["glass<br/>Glass morphism"]
        DestructiveDialog["destructive<br/>Danger confirmation"]
    end
    
    subgraph "Shared Styling"
        ThemeVars["Theme Variables"]
        GlassLayers["GlassSurfaceLayers"]
    end
    
    Glass --> GlassLayers
    GlassDialog --> GlassLayers
    
    Subtle --> ThemeVars
    Filled --> ThemeVars
    Solid --> ThemeVars
    Glass --> ThemeVars
    Outline --> ThemeVars
    DefaultDialog --> ThemeVars
    GlassDialog --> ThemeVars
```

**Sources:** [internal-packages/ui/components/button.tsx:4-12](), [internal-packages/ui/components/dialog.tsx:11-19]()

### Glass Variant Implementation

The glass variant creates a frosted glass effect using multiple layers: backdrop blur, gradient backgrounds, border highlights, and shadow effects. This variant is extensively used in auth pages and dialogs.

**Glass Styling Components:**
- Background gradient: `--glass-button-bg` and `--auth-glass-bg`
- Border gradient: `--glass-stroke-gradient` 
- Top highlight: `--glass-highlight-bg`
- Shadow: `--shadow-glass`
- Overlay: `--color-dialog-overlay` for modal backgrounds

**Sources:** [internal-packages/ui/style.css:165-225](), [internal-packages/ui/components/dialog.tsx:28-89]()

### Solid Variant Implementation

The solid variant provides a more traditional button appearance with a gradient background and stronger shadows:

```css
--solid-button-bg: linear-gradient(180deg, #202530 0%, #12151f 100%)
--color-button-solid-border: rgba(0, 0, 0, 0.7)
--solid-button-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.05),
                       0 2px 8px rgba(5, 10, 20, 0.4),
                       0 1px 2px rgba(0, 0, 0, 0.3)
```

**Sources:** [internal-packages/ui/style.css:213-218]()

### Outline Variant Implementation

The outline variant creates a subtle bordered appearance with no background fill:

```css
--shadow-outline-button: 0 1px 0 rgba(255, 255, 255, 0.05) inset,
                         0 -1px 0 rgba(0, 0, 0, 0.2) inset,
                         0 0 0 1px rgba(255, 255, 255, 0.08)
--color-outline-button-bg: var(--color-black)
```

**Sources:** [internal-packages/ui/style.css:220-224]()

## Key Components

### Button Component

The `Button` component is the primary interactive element, supporting all variants and multiple sizes.

**Component Structure:**

```mermaid
graph TB
    Button["Button Component"]
    
    subgraph "Props"
        Variant["variant: ButtonStyle"]
        Size["size: ButtonSize"]
        LeftIcon["leftIcon: ReactNode"]
        RightIcon["rightIcon: ReactNode"]
        AsChild["asChild: boolean"]
    end
    
    subgraph "Variants"
        V1["subtle"]
        V2["filled"]
        V3["solid"]
        V4["glass"]
        V5["outline"]
        V6["link"]
        V7["primary"]
        V8["destructive"]
    end
    
    subgraph "Sizes"
        S1["compact: 4px padding"]
        S2["default: 8px padding"]
        S3["large: 38px height"]
    end
    
    Button --> Variant
    Button --> Size
    Button --> LeftIcon
    Button --> RightIcon
    Button --> AsChild
    
    Variant --> V1
    Variant --> V2
    Variant --> V3
    Variant --> V4
    Variant --> V5
    Variant --> V6
    Variant --> V7
    Variant --> V8
    
    Size --> S1
    Size --> S2
    Size --> S3
```

**Implementation Details:**
- Uses `data-style` and `data-size` attributes for variant styling
- Supports icon composition with `leftIcon` and `rightIcon` props
- `asChild` prop enables Radix UI Slot composition pattern
- Glass variant includes layered background effects with hover transitions

**Sources:** [internal-packages/ui/components/button.tsx:1-100]()

### Dialog Component

The `Dialog` component system provides modal overlays with multiple variants and a composable API.

**Dialog Composition Pattern:**

```mermaid
graph TB
    subgraph "Dialog Primitives"
        DialogRoot["Dialog<br/>Radix Root"]
        DialogTrigger["DialogTrigger"]
        DialogPortal["DialogPortal"]
        DialogOverlay["DialogOverlay"]
        DialogContent["DialogContent"]
        DialogClose["DialogClose"]
    end
    
    subgraph "Content Components"
        DialogHeader["DialogHeader"]
        DialogTitle["DialogTitle"]
        DialogDescription["DialogDescription"]
        DialogBody["DialogBody<br/>Scrollable"]
        DialogFooter["DialogFooter<br/>Actions"]
    end
    
    subgraph "Styling Layers"
        GlassSurface["GlassSurfaceLayers"]
        OverlayBg["Dialog Overlay<br/>--color-dialog-overlay"]
    end
    
    DialogRoot --> DialogTrigger
    DialogRoot --> DialogPortal
    DialogPortal --> DialogOverlay
    DialogPortal --> DialogContent
    
    DialogContent --> DialogHeader
    DialogHeader --> DialogTitle
    DialogHeader --> DialogDescription
    DialogContent --> DialogBody
    DialogContent --> DialogFooter
    
    DialogContent --> GlassSurface
    DialogOverlay --> OverlayBg
```

**Variant Behavior:**
- `default`: Standard dialog with solid background and blur
- `glass`: Full glass morphism treatment using `GlassSurfaceLayers`
- `destructive`: Glass variant with red-tinted background for danger actions

**Sources:** [internal-packages/ui/components/dialog.tsx:1-144](), [internal-packages/ui/components/glass-dialog.tsx:1-36]()

### GlassSurfaceLayers Component

The `GlassSurfaceLayers` component provides a reusable system for creating layered glass effects. It's used by dialogs and auth containers.

**Layer Structure:**

```mermaid
graph TB
    Container["Relative Container"]
    
    subgraph "Layers (z-index order)"
        BaseFill["Base Fill<br/>bg-bg/18 or custom"]
        GradientBorder["Gradient Border<br/>--glass-stroke-gradient"]
        TopHighlight["Top Highlight<br/>--glass-highlight-bg"]
        AuxHairline["Auxiliary Hairline<br/>Optional"]
        BlurEffect["Backdrop Blur<br/>backdrop-blur-sm/md"]
    end
    
    Container --> BaseFill
    Container --> GradientBorder
    Container --> TopHighlight
    Container --> AuxHairline
    Container --> BlurEffect
```

**Customization Props:**
- `variant`: default or destructive tone
- `borderStyle`: solid, gradient, or none
- `borderTone`: muted or destructive color
- `withTopHighlight`: enable top edge highlight
- `withBaseFill`: enable background tint
- `baseFillClass`: custom background class
- `blurClass`: blur intensity (sm/md)
- `withAuxHairline`: additional border detail
- `radiusClass`: border radius
- `zIndexClass`: layer z-index

**Sources:** [internal-packages/ui/components/dialog.tsx:4](), [apps/studio.giselles.ai/app/(auth)/components/auth-container.tsx:30-50]()

## Usage Patterns

### Button Usage Examples

**Subtle Button (Default):**
```tsx
<Button variant="subtle" leftIcon={<Settings2Icon />}>
  Configure
</Button>
```

**Glass Button (Auth Pages):**
```tsx
<Button variant="glass" size="large">
  Sign In
</Button>
```

**Destructive Action:**
```tsx
<Button variant="destructive" rightIcon={<TrashIcon />}>
  Delete
</Button>
```

**Sources:** [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/tools/tool-provider/anthropic-web-search/anthropic-web-search.tsx:215-221]()

### Dialog Usage Examples

**Standard Dialog:**
```tsx
<Dialog>
  <DialogTrigger asChild>
    <Button>Open Dialog</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Title</DialogTitle>
      <DialogDescription>Description</DialogDescription>
    </DialogHeader>
    <DialogBody>
      {/* Scrollable content */}
    </DialogBody>
    <DialogFooter>
      <Button>Action</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

**Glass Dialog (Auth & Special Modals):**
```tsx
<Dialog>
  <DialogContent variant="glass">
    {/* Content with glass morphism effect */}
  </DialogContent>
</Dialog>
```

**Destructive Confirmation:**
```tsx
<Dialog>
  <DialogContent variant="destructive">
    <DialogTitle>Confirm Deletion</DialogTitle>
    {/* Danger action content */}
  </DialogContent>
</Dialog>
```

**Sources:** [internal-packages/ui/components/dialog.tsx:21-89](), [internal-packages/ui/components/glass-dialog.tsx:20-22]()

## Context-Specific Styling

### Auth Page Theming

Auth pages use specialized variables and utility classes for a distinct visual treatment:

**Auth-Specific Variables:**
```css
--color-auth-background: hsl(234, 91%, 5%)
--color-auth-ambient-light: hsl(218, 58%, 21%)
--color-auth-logo-watermark: hsl(207, 19%, 77%)
--shadow-stage-form: /* Complex shadow with blue glow */
```

**Auth Utility Classes:**
- `.auth-title-glow`: Text glow effect for titles
- `.auth-gradient-border`: Gradient stroke border for containers
- `.auth-corner-dot--*`: Corner accent decorations

**Sources:** [internal-packages/ui/style.css:92-108](), [internal-packages/ui/style.css:242-264](), [apps/studio.giselles.ai/app/(auth)/components/auth-container.tsx:17-61]()

### Stage System Theming

The Stage system (production execution environment) has its own color palette:

**Stage Variables:**
```css
--color-stage-background: #030610
--color-stage-form-background: #101520
--color-stage-sidebar-text: #7084ac
--color-stage-sidebar-text-hover: #f7f9fd
--color-stage-accent: #6b8ff0
--stage-radial-overlay: /* Radial gradient for canvas background */
```

**Sources:** [internal-packages/ui/style.css:79-90]()

### Editor Theming

The code editor and text editor components use specialized color tokens:

**Editor Variables:**
```css
--color-editor-foreground: #acb2be
--color-editor-background: #00020b
--color-editor-gutter-background: #282c33
--color-editor-active-line-background: #2f343e
--color-editor-line-number: #4e5a5f
```

**Sources:** [internal-packages/ui/style.css:110-124]()

### Chat Panel Theming

Chat UI components use bubble-specific styling:

**Chat Variables:**
```css
--color-chat-bubble-accent-bg: rgba(107, 143, 240, 0.2)
--color-chat-bubble-accent-border: rgba(107, 143, 240, 0.8)
--color-chat-bubble-user-bg: #4a6fd8
```

These variables create distinct visual treatments for assistant vs. user messages with appropriate contrast and readability.

**Sources:** [internal-packages/ui/style.css:153-156](), [internal-packages/workflow-designer-ui/src/editor/chat/chat-panel.tsx:170-181]()

## Color System and Accessibility

### Text Hierarchy

The theme provides multiple text color levels for establishing visual hierarchy:

```mermaid
graph LR
    subgraph "Text Color Hierarchy"
        Primary["--color-text<br/>#f7f9fd<br/>Primary text"]
        Muted["--color-text-muted<br/>#a9afbc<br/>Secondary text"]
        Placeholder["--color-text-placeholder<br/>#878a98<br/>Input placeholders"]
        Disabled["--color-text-disabled<br/>#878a98<br/>Disabled states"]
        Accent["--color-text-accent<br/>#74ade8<br/>Highlighted text"]
    end
    
    subgraph "Derived Levels"
        Text80["--color-text-80<br/>80% opacity"]
        Text60["--color-text-60<br/>60% opacity"]
    end
    
    Primary --> Muted
    Muted --> Placeholder
    Placeholder --> Disabled
    Primary --> Text80
    Text80 --> Text60
```

**Color Mix Usage:**
The theme uses CSS `color-mix()` for creating opacity variants:
```css
--color-text-80: color-mix(in srgb, var(--color-text), transparent 20%)
--color-text-60: color-mix(in srgb, var(--color-text), transparent 40%)
```

**Sources:** [internal-packages/ui/style.css:37-63]()

### Status Colors with RGB Variants

Status colors are provided in both standard and RGB formats to enable alpha transparency:

```css
--color-error: #ff3d71
--color-error-rgb: 255, 61, 113

--color-success: #39ff7f
--color-success-rgb: 57, 255, 127
```

This allows usage like `bg-[rgba(var(--color-success-rgb),0.05)]` for subtle backgrounds.

**Sources:** [internal-packages/ui/style.css:133-163](), [internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/tools/tool-provider/anthropic-web-search/anthropic-web-search.tsx:402-406]()

## Base Layer Normalization

The theme includes base layer normalization for consistent rendering across browsers and environments:

**Autofill Styling:**
```css
input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus {
  -webkit-text-fill-color: var(--color-text);
  box-shadow: 0 0 0px 1000px var(--color-editor-background) inset;
  transition: background-color 9999s ease-out 0s;
}
```

This prevents browser autofill from breaking the dark theme by applying a persistent dark background.

**Sources:** [internal-packages/ui/style.css:227-240]()

## Integration with Tailwind CSS

The UI package imports Tailwind CSS and extends it with custom theme variables through the `@theme` directive:

```css
@import "tailwindcss";
@import "./styles/tokens.css";
@import "./styles/semantic.css";

@theme {
  /* Custom CSS variables that extend Tailwind */
}
```

This approach allows:
- Standard Tailwind utility classes (e.g., `flex`, `gap-4`, `rounded-lg`)
- Custom color utilities (e.g., `text-text`, `bg-surface`, `border-border`)
- Theme variable access via `var(--color-*)` in CSS
- Arbitrary value utilities (e.g., `bg-[rgba(var(--color-success-rgb),0.05)]`)

**Sources:** [internal-packages/ui/style.css:1-5]()

---

# Page: Observability and Telemetry

# Observability and Telemetry

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/playground/giselle-engine.ts](apps/playground/giselle-engine.ts)
- [apps/playground/package.json](apps/playground/package.json)
- [apps/studio.giselles.ai/app/giselle-engine.ts](apps/studio.giselles.ai/app/giselle-engine.ts)
- [apps/studio.giselles.ai/package.json](apps/studio.giselles.ai/package.json)
- [internal-packages/workflow-designer-ui/package.json](internal-packages/workflow-designer-ui/package.json)
- [package.json](package.json)
- [packages/giselle/package.json](packages/giselle/package.json)
- [packages/giselle/src/engine/acts/run-act.ts](packages/giselle/src/engine/acts/run-act.ts)
- [packages/giselle/src/engine/generations/generate-content.ts](packages/giselle/src/engine/generations/generate-content.ts)
- [packages/giselle/src/engine/generations/generate-image.ts](packages/giselle/src/engine/generations/generate-image.ts)
- [packages/giselle/src/engine/generations/internal/use-generation-executor.ts](packages/giselle/src/engine/generations/internal/use-generation-executor.ts)
- [packages/giselle/src/engine/generations/types.ts](packages/giselle/src/engine/generations/types.ts)
- [packages/giselle/src/engine/generations/utils.ts](packages/giselle/src/engine/generations/utils.ts)
- [packages/giselle/src/engine/operations/execute-query.ts](packages/giselle/src/engine/operations/execute-query.ts)
- [packages/giselle/src/engine/telemetry/index.ts](packages/giselle/src/engine/telemetry/index.ts)
- [packages/giselle/src/engine/telemetry/types.ts](packages/giselle/src/engine/telemetry/types.ts)
- [packages/giselle/src/engine/triggers/resolve-trigger.ts](packages/giselle/src/engine/triggers/resolve-trigger.ts)
- [packages/giselle/src/engine/types.ts](packages/giselle/src/engine/types.ts)
- [packages/giselle/src/react/generations/generation-runner.tsx](packages/giselle/src/react/generations/generation-runner.tsx)
- [pnpm-lock.yaml](pnpm-lock.yaml)
- [pnpm-workspace.yaml](pnpm-workspace.yaml)

</details>



This document describes the observability and telemetry infrastructure in the Giselle AI platform, including the callback system for generation lifecycle events, Langfuse integration for LLM tracing, metadata enrichment, and error tracking mechanisms.

For information about error handling and error types, see the Error Handling section (not yet documented). For usage limit tracking and agent time consumption, see [Usage Limits and Tier Management](#2.3).

## Overview

The observability system provides comprehensive monitoring of AI operations through:
- **Callback-based event system** for generation lifecycle tracking
- **Langfuse integration** for LLM and embedding operation tracing
- **Metadata enrichment** with team, plan, and user context
- **Request correlation** via request ID tracking
- **Asynchronous telemetry** to avoid blocking generation pipelines

The system operates through callbacks registered in the `GiselleEngineContext` and executed at specific lifecycle points during generation execution.

## Callback System Architecture

### Callback Registration and Types

The engine supports four primary callback types defined in the `GiselleEngineContext`:

| Callback Type | Trigger Point | Purpose |
|---------------|---------------|---------|
| `generationComplete` | Generation completes successfully | Trace successful operations, record usage |
| `generationFailed` | Generation fails with error | Trace failures, log error details |
| `embeddingComplete` | Embedding operation completes | Trace vector query embeddings, track costs |
| `flowTriggerUpdate` | Flow trigger configuration changes | Persist trigger state changes |

```mermaid
graph TB
    subgraph "Generation Execution Pipeline"
        GenStart["Generation Start"]
        GenRunning["Running Generation"]
        GenComplete["Generation Complete"]
        GenFailed["Generation Failed"]
    end
    
    subgraph "Callback System"
        CompleteCallback["generationComplete callback"]
        FailedCallback["generationFailed callback"]
        EmbedCallback["embeddingComplete callback"]
    end
    
    subgraph "Telemetry Destinations"
        Langfuse["Langfuse Platform"]
        ErrorTracking["Error Tracking"]
        UsageMetrics["Usage Metrics"]
    end
    
    GenStart --> GenRunning
    GenRunning --> GenComplete
    GenRunning --> GenFailed
    
    GenComplete --> CompleteCallback
    GenFailed --> FailedCallback
    GenRunning --> EmbedCallback
    
    CompleteCallback --> Langfuse
    CompleteCallback --> UsageMetrics
    FailedCallback --> Langfuse
    FailedCallback --> ErrorTracking
    EmbedCallback --> Langfuse
```

**Sources:** [packages/giselle/src/engine/types.ts:40-91](), [apps/studio.giselles.ai/app/giselle-engine.ts:240-265]()

### Callback Execution Flow

Callbacks are executed asynchronously using Next.js's `after()` function to ensure they don't block generation responses. The execution follows this pattern:

```mermaid
sequenceDiagram
    participant Gen as Generation Executor
    participant CB as Callback Handler
    participant Async as after() Wrapper
    participant Trace as Tracing Service
    
    Gen->>CB: finishGeneration()
    CB->>Async: after(async callback)
    Async-->>Gen: Returns immediately
    Gen->>Gen: Continue execution
    
    Note over Async,Trace: Non-blocking execution
    Async->>CB: Execute callback
    CB->>Trace: traceGeneration()
    Trace->>Trace: Send to Langfuse
    CB->>Trace: Wait for flush
```

**Sources:** [apps/studio.giselles.ai/app/giselle-engine.ts:185-232](), [packages/giselle/src/engine/generations/internal/use-generation-executor.ts:365-374]()

## Langfuse Integration

### Generation Tracing

The `traceGeneration()` function from `@giselle-sdk/langfuse` sends comprehensive telemetry data to Langfuse for LLM operations:

```mermaid
graph LR
    subgraph "Generation Data"
        GenID["Generation ID"]
        Messages["Input/Output Messages"]
        Usage["Token Usage"]
        Metadata["Enriched Metadata"]
        Files["Output File Blobs"]
    end
    
    subgraph "traceGeneration Function"
        Prepare["Prepare Trace Payload"]
        Enrich["Add Metadata"]
        Send["Send to Langfuse"]
    end
    
    subgraph "Langfuse Platform"
        Store["Store Trace"]
        Analyze["Usage Analytics"]
        Dashboard["Observability Dashboard"]
    end
    
    GenID --> Prepare
    Messages --> Prepare
    Usage --> Prepare
    Files --> Prepare
    Prepare --> Enrich
    Metadata --> Enrich
    Enrich --> Send
    Send --> Store
    Store --> Analyze
    Analyze --> Dashboard
```

The tracing payload includes:

| Field | Source | Purpose |
|-------|--------|---------|
| `generation` | Completed/Failed generation object | Full generation state |
| `inputMessages` | ModelMessage[] | LLM input messages |
| `outputFileBlobs` | OutputFileBlob[] | Generated images/files |
| `userId` | User context or "github-app" | User attribution |
| `sessionId` | Act ID | Session grouping |
| `tags` | Plan and team type | Filtering and analytics |
| `metadata` | Enriched context | Detailed attribution |
| `providerMetadata` | Provider-specific data | Model-specific info |

**Sources:** [apps/studio.giselles.ai/app/giselle-engine.ts:108-139](), [apps/studio.giselles.ai/trigger/generate-content-task.ts:17-48]()

### Embedding Tracing

Embedding operations (vector queries) are traced separately via `traceEmbedding()`:

```mermaid
graph TB
    subgraph "Vector Query Execution"
        Query["Query Execution"]
        Embed["Generate Query Embedding"]
        Search["Vector Search"]
        Complete["Query Complete"]
    end
    
    subgraph "Embedding Callback"
        Metrics["EmbeddingMetrics"]
        Context["QueryContext"]
        Callback["embeddingComplete callback"]
    end
    
    subgraph "Trace Enrichment"
        BaseMetrics["Usage metrics<br/>model, token count"]
        ResourceInfo["Resource info<br/>owner, repo, contentType"]
        TeamInfo["Team/Plan info<br/>subscription, teamType"]
    end
    
    Query --> Embed
    Embed --> Metrics
    Embed --> Context
    Embed --> Search
    Search --> Complete
    Complete --> Callback
    
    Callback --> BaseMetrics
    Callback --> ResourceInfo
    Callback --> TeamInfo
    
    BaseMetrics --> Langfuse["traceEmbedding()"]
    ResourceInfo --> Langfuse
    TeamInfo --> Langfuse
```

**Sources:** [apps/studio.giselles.ai/app/giselle-engine.ts:141-175](), [packages/giselle/src/engine/operations/execute-query.ts:44-58](), [packages/giselle/src/engine/operations/execute-query.ts:356-368]()

## Metadata Enrichment Pipeline

### Team and Plan Context

Each trace is enriched with team and plan information for cost attribution and analytics:

```mermaid
graph TB
    subgraph "Context Resolution"
        Origin["Generation Origin"]
        ResolveUser["Resolve User"]
        ResolveTeam["Resolve Team"]
    end
    
    subgraph "Origin Types"
        Studio["studio origin<br/>fetchCurrentUser<br/>fetchCurrentTeam"]
        Stage["stage origin<br/>fetchCurrentUser<br/>fetchCurrentTeam"]
        GitHubApp["github-app origin<br/>user: 'github-app'<br/>getWorkspaceTeam"]
    end
    
    subgraph "Metadata Generation"
        PlanCheck["isProPlan check"]
        Tags["Generate tags<br/>plan:pro/free<br/>teamType:customer/internal"]
        Metadata["Build metadata object<br/>generationId<br/>isProPlan<br/>teamType<br/>userId<br/>subscriptionId<br/>providerMetadata<br/>requestId"]
    end
    
    Origin --> Studio
    Origin --> Stage
    Origin --> GitHubApp
    
    Studio --> PlanCheck
    Stage --> PlanCheck
    GitHubApp --> PlanCheck
    
    PlanCheck --> Tags
    PlanCheck --> Metadata
    Tags --> TraceCall["traceGeneration() or traceEmbedding()"]
    Metadata --> TraceCall
```

**Sources:** [apps/studio.giselles.ai/app/giselle-engine.ts:185-232](), [apps/studio.giselles.ai/app/giselle-engine.ts:108-139]()

### Request ID Tracking

Request IDs provide correlation across distributed traces and async operations:

| Context | Request ID Source | Purpose |
|---------|-------------------|---------|
| HTTP Requests | `getRequestId()` from request context | Correlate API call with generation |
| Trigger.dev Tasks | Passed as task payload | Correlate async task with originating request |
| Callback Execution | Captured at callback creation | Link trace to original request |

```mermaid
sequenceDiagram
    participant Client as Client Request
    participant API as API Handler
    participant Gen as Generation
    participant Task as Trigger.dev Task
    participant Trace as Trace Service
    
    Note over Client,API: Request ID: req_abc123
    Client->>API: POST /api/generation
    API->>API: getRequestId() → req_abc123
    API->>Gen: Create generation
    Gen->>Task: Trigger task (requestId: req_abc123)
    Task->>Task: Execute generation
    Task->>Trace: traceGeneration(requestId: req_abc123)
    
    Note over Client,Trace: All events correlated by req_abc123
```

**Sources:** [apps/studio.giselles.ai/app/giselle-engine.ts:250-251](), [apps/studio.giselles.ai/trigger/generate-content-task.ts:52-54](), [apps/studio.giselles.ai/trigger/generate-content-task.ts:84]()

## Telemetry Configuration

### Engine Configuration

Telemetry is configured at engine initialization via the `telemetry` config object:

```mermaid
graph TB
    subgraph "GiselleEngineConfig"
        TelConfig["telemetry object"]
        IsEnabled["isEnabled: boolean"]
        WaitFlush["waitForFlushFn: () => Promise<unknown>"]
        Meta["metadata?: TelemetrySettings['metadata']"]
    end
    
    subgraph "Studio Configuration"
        StudioEnabled["isEnabled: true"]
        StudioFlush["waitForFlushFn:<br/>waitForLangfuseFlush"]
        StudioCallbacks["callbacks:<br/>generationComplete<br/>generationFailed<br/>embeddingComplete"]
    end
    
    subgraph "Playground Configuration"
        PlayEnabled["isEnabled: undefined<br/>defaults to false"]
        PlayCallbacks["callbacks:<br/>generationComplete only"]
    end
    
    TelConfig --> IsEnabled
    TelConfig --> WaitFlush
    TelConfig --> Meta
    
    IsEnabled --> StudioEnabled
    WaitFlush --> StudioFlush
    IsEnabled --> PlayEnabled
```

**Studio Configuration:**
```typescript
telemetry: {
  isEnabled: true,
  waitForFlushFn: waitForLangfuseFlush,
}
```

**Playground Configuration:**
```typescript
callbacks: {
  generationComplete: async (args) => {
    try {
      await traceGeneration(args);
    } catch (error) {
      console.error("Trace generation failed:", error);
    }
  },
}
```

**Sources:** [apps/studio.giselles.ai/app/giselle-engine.ts:273-276](), [apps/playground/giselle-engine.ts:148-156](), [packages/giselle/src/engine/types.ts:77-81]()

## Execution Context Handling

### Origin-Based Context Resolution

The system handles three execution contexts with different context resolution strategies:

```mermaid
graph TB
    subgraph "Origin Type Detection"
        CheckOrigin["generation.context.origin.type"]
        StudioOrigin["studio"]
        StageOrigin["stage"]
        GitHubOrigin["github-app"]
    end
    
    subgraph "Studio/Stage Context"
        FetchUser["fetchCurrentUser()"]
        FetchTeam["fetchCurrentTeam()"]
        UserID["userId: user.id"]
        SessionID["sessionId: actId"]
    end
    
    subgraph "GitHub App Context"
        GetWorkspace["getWorkspaceTeam(workspaceId)"]
        StaticUser["userId: 'github-app'"]
        SessionIDGH["sessionId: actId"]
    end
    
    CheckOrigin --> StudioOrigin
    CheckOrigin --> StageOrigin
    CheckOrigin --> GitHubOrigin
    
    StudioOrigin --> FetchUser
    StageOrigin --> FetchUser
    FetchUser --> UserID
    FetchTeam --> UserID
    UserID --> SessionID
    
    GitHubOrigin --> GetWorkspace
    GetWorkspace --> StaticUser
    StaticUser --> SessionIDGH
    
    SessionID --> TraceCall["traceGenerationForTeam()"]
    SessionIDGH --> TraceCall
```

**Sources:** [apps/studio.giselles.ai/app/giselle-engine.ts:188-227](), [apps/studio.giselles.ai/app/giselle-engine.ts:309-348]()

### Conditional Tracing in Studio Context

Studio generation with Trigger.dev delegation has special handling to avoid duplicate traces:

```mermaid
graph TB
    GenComplete["generationComplete callback"]
    CheckProcessor{"generateContentProcessor"}
    CheckOrigin{"origin.type"}
    
    GenComplete --> CheckProcessor
    
    CheckProcessor -->|"trigger.dev"| CheckOrigin
    CheckProcessor -->|"self"| Trace["Execute tracing"]
    
    CheckOrigin -->|"studio"| Skip["Skip tracing<br/>Trigger.dev task will trace"]
    CheckOrigin -->|"stage/github-app"| Trace
    
    Trace --> TraceCall["handleGenerationTrace()"]
```

**Rationale:** Studio generations delegated to Trigger.dev are traced by the task itself to ensure proper metadata context. Act executions (stage/github-app) are traced immediately because they don't support Trigger.dev delegation yet.

**Sources:** [apps/studio.giselles.ai/app/giselle-engine.ts:240-264](), [apps/studio.giselles.ai/app/giselle-engine.ts:234-238]()

## Trigger.dev Task Telemetry

### Task-Based Tracing

Long-running generations delegated to Trigger.dev tasks perform tracing within the task execution:

```mermaid
sequenceDiagram
    participant Engine as GiselleEngine
    participant Task as generateContentTask
    participant GenContent as generateContent()
    participant Trace as traceGenerationForTeam()
    
    Engine->>Task: trigger task with:<br/>generationId, userId, team, requestId
    Task->>Task: Fetch generation
    Task->>GenContent: Execute generation
    
    alt Generation Succeeds
        GenContent-->>Task: GenerateContentResult (success)
        Task->>Trace: traceGeneration with:<br/>completedGeneration, inputMessages,<br/>outputFileBlobs, providerMetadata,<br/>requestId
    else Generation Fails
        GenContent-->>Task: GenerateContentResult (failed)
        Task->>Trace: traceGeneration with:<br/>failedGeneration, inputMessages,<br/>requestId
    end
    
    Trace->>Trace: Add plan/team tags
    Trace->>Trace: Build metadata
    Trace->>Trace: Send to Langfuse
```

The task receives pre-resolved context to avoid authentication issues in background execution:
- `userId`: Already resolved user ID
- `team`: Team object with `id`, `type`, `subscriptionId`
- `requestId`: Correlation ID from originating request

**Sources:** [apps/studio.giselles.ai/trigger/generate-content-task.ts:50-104](), [apps/studio.giselles.ai/app/giselle-engine.ts:367-409]()

## Callback Implementation Details

### Generation Complete Callback Structure

```mermaid
graph TB
    subgraph "generationComplete Args"
        GenArg["CompletedGeneration"]
        InputMsg["inputMessages: ModelMessage[]"]
        OutputBlobs["outputFileBlobs: OutputFileBlob[]"]
        ProvMeta["providerMetadata?: ProviderMetadata"]
    end
    
    subgraph "Callback Implementation"
        GetReqId["getRequestId()"]
        HandleTrace["handleGenerationTrace()"]
        AfterWrap["after() wrapper"]
    end
    
    subgraph "handleGenerationTrace"
        CheckOrigin["Check origin type"]
        ResolveContext["Resolve user/team context"]
        CallTraceFunc["traceGenerationForTeam()"]
    end
    
    GenArg --> HandleTrace
    InputMsg --> HandleTrace
    OutputBlobs --> HandleTrace
    ProvMeta --> HandleTrace
    GetReqId --> HandleTrace
    
    HandleTrace --> AfterWrap
    AfterWrap --> CheckOrigin
    CheckOrigin --> ResolveContext
    ResolveContext --> CallTraceFunc
```

**Sources:** [apps/studio.giselles.ai/app/giselle-engine.ts:240-252](), [apps/studio.giselles.ai/app/giselle-engine.ts:185-232]()

### Embedding Complete Callback Structure

```mermaid
graph TB
    subgraph "embeddingComplete Args"
        Metrics["embeddingMetrics: EmbeddingMetrics"]
        Gen["generation: RunningGeneration"]
        Context["queryContext: QueryContext"]
    end
    
    subgraph "Callback Implementation"
        AfterWrap["after() wrapper"]
        CheckOrigin["Check origin type"]
        ResolveContext["Resolve user/team context"]
    end
    
    subgraph "traceEmbeddingForTeam"
        BuildTags["Build tags:<br/>plan:pro/free<br/>teamType<br/>embedding-purpose:query"]
        BuildMeta["Build metadata:<br/>generationId, teamId<br/>resourceProvider, resourceOwner<br/>resourceRepo, resourceContentType"]
        CallTrace["traceEmbedding()"]
    end
    
    Metrics --> AfterWrap
    Gen --> AfterWrap
    Context --> AfterWrap
    
    AfterWrap --> CheckOrigin
    CheckOrigin --> ResolveContext
    ResolveContext --> BuildTags
    BuildTags --> BuildMeta
    BuildMeta --> CallTrace
```

**Sources:** [apps/studio.giselles.ai/app/giselle-engine.ts:306-349](), [apps/studio.giselles.ai/app/giselle-engine.ts:141-175]()

## Batch Writing for Streaming Data

The `generateContent()` function uses a batch writer for efficiently persisting streaming UI message chunks:

```mermaid
graph TB
    subgraph "Stream Processing"
        StreamChunk["UI Message Chunk"]
        AddToBatch["writer.add(chunk)"]
        BatchBuffer["Accumulate in buffer"]
    end
    
    subgraph "Batch Writer Configuration"
        IntervalConfig["intervalMs: 2000ms"]
        PreserveItems["preserveItems: true"]
        Logger["Optional logger"]
    end
    
    subgraph "Batch Flush Logic"
        CheckInterval["Timer tick every 2s"]
        CheckMaxItems["Check maxItems"]
        ExecuteFlush["executeFlush()"]
        WriteStorage["experimental_storage.setBlob()"]
    end
    
    StreamChunk --> AddToBatch
    AddToBatch --> BatchBuffer
    
    IntervalConfig --> CheckInterval
    CheckMaxItems --> ExecuteFlush
    CheckInterval --> ExecuteFlush
    
    BatchBuffer --> ExecuteFlush
    ExecuteFlush --> WriteStorage
    
    PreserveItems --> BatchBuffer
```

The batch writer ensures:
- **Periodic flushing** every 2 seconds to reduce write operations
- **Item preservation** (`preserveItems: true`) maintains all chunks in buffer until successfully written
- **Error recovery** restores items to buffer on write failure
- **Graceful shutdown** via `writer.close()` ensures all buffered items are flushed

**Sources:** [packages/giselle/src/engine/generations/generate-content.ts:392-416](), [packages/giselle/src/utils/batch.ts:1-123]()

## Error Tracking Integration

### Generation Failure Handling

Failed generations trigger the `generationFailed` callback with error details:

```mermaid
graph TB
    subgraph "Generation Failure"
        GenError["Generation error"]
        BuildFailed["Build FailedGeneration object"]
        ErrorInfo["error: {<br/>name, message, dump<br/>}"]
    end
    
    subgraph "Callback Execution"
        FailedCB["generationFailed callback"]
        TraceFunc["handleGenerationTrace()"]
        ResolveContext["Resolve user/team context"]
    end
    
    subgraph "Trace Data"
        FailedGen["FailedGeneration"]
        InputMsg["inputMessages"]
        NoOutputs["No outputFileBlobs"]
        RequestID["requestId"]
    end
    
    GenError --> BuildFailed
    BuildFailed --> ErrorInfo
    ErrorInfo --> FailedCB
    
    FailedCB --> TraceFunc
    TraceFunc --> ResolveContext
    
    FailedGen --> TraceLangfuse["Send to Langfuse"]
    InputMsg --> TraceLangfuse
    NoOutputs --> TraceLangfuse
    RequestID --> TraceLangfuse
```

Error information includes:
- **Error name**: Exception class or "UnknownError"
- **Error message**: Human-readable error description
- **Error dump**: Full error object for debugging
- **Context preservation**: Input messages and generation state retained

**Sources:** [packages/giselle/src/engine/generations/generate-text.ts:265-279](), [packages/giselle/src/engine/generations/generate-content.ts:298-317](), [apps/studio.giselles.ai/app/giselle-engine.ts:253-264]()

## Telemetry Flush Coordination

The `waitForFlushFn` ensures traces are fully transmitted before serverless function termination:

```mermaid
sequenceDiagram
    participant Gen as Generation Complete
    participant CB as Callback
    participant Trace as traceGeneration()
    participant Flush as waitForLangfuseFlush()
    participant Function as Serverless Function
    
    Gen->>CB: Trigger callback
    CB->>Trace: Send trace data
    Trace->>Trace: Queue for transmission
    
    Note over Function: Before function exit
    Function->>Flush: Ensure flush complete
    Flush->>Flush: Wait for queue drain
    Flush-->>Function: Flush complete
    Function->>Function: Safe to exit
```

This coordination is critical in serverless environments where premature function termination can lose telemetry data.

**Sources:** [apps/studio.giselles.ai/app/giselle-engine.ts:273-276](), [apps/studio.giselles.ai/instrumentation.node.ts]()

## Summary of Telemetry Data Flow

```mermaid
graph TB
    subgraph "Generation Lifecycle"
        Start["Generation Start"]
        Execute["Execute Operation"]
        Complete["Complete/Fail"]
    end
    
    subgraph "Callback System"
        Callbacks["Registered Callbacks"]
        AfterWrap["after() Async Wrapper"]
        ContextResolve["Context Resolution"]
    end
    
    subgraph "Trace Preparation"
        Enrich["Metadata Enrichment"]
        Tags["Tag Generation"]
        ReqID["Request ID Correlation"]
    end
    
    subgraph "Transmission"
        LangfuseTrace["Langfuse Tracing"]
        FlushWait["Wait for Flush"]
        Complete2["Telemetry Complete"]
    end
    
    Start --> Execute
    Execute --> Complete
    Complete --> Callbacks
    Callbacks --> AfterWrap
    AfterWrap --> ContextResolve
    ContextResolve --> Enrich
    Enrich --> Tags
    Tags --> ReqID
    ReqID --> LangfuseTrace
    LangfuseTrace --> FlushWait
    FlushWait --> Complete2
```

The observability system provides comprehensive tracking of all AI operations while maintaining non-blocking execution through asynchronous callbacks, ensuring production performance is not impacted by telemetry overhead.

---

# Page: Build and Deployment

# Build and Release Process

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/playground/package.json](apps/playground/package.json)
- [apps/studio.giselles.ai/package.json](apps/studio.giselles.ai/package.json)
- [docs/packages-license.md](docs/packages-license.md)
- [internal-packages/workflow-designer-ui/package.json](internal-packages/workflow-designer-ui/package.json)
- [package.json](package.json)
- [packages/document-preprocessor/README.md](packages/document-preprocessor/README.md)
- [packages/document-preprocessor/package.json](packages/document-preprocessor/package.json)
- [packages/document-preprocessor/src/global.d.ts](packages/document-preprocessor/src/global.d.ts)
- [packages/document-preprocessor/src/index.ts](packages/document-preprocessor/src/index.ts)
- [packages/document-preprocessor/src/pdf.ts](packages/document-preprocessor/src/pdf.ts)
- [packages/document-preprocessor/src/text.test.ts](packages/document-preprocessor/src/text.test.ts)
- [packages/document-preprocessor/src/text.ts](packages/document-preprocessor/src/text.ts)
- [packages/document-preprocessor/src/types.ts](packages/document-preprocessor/src/types.ts)
- [packages/document-preprocessor/tsconfig.json](packages/document-preprocessor/tsconfig.json)
- [packages/document-preprocessor/tsup.config.ts](packages/document-preprocessor/tsup.config.ts)
- [packages/document-preprocessor/turbo.json](packages/document-preprocessor/turbo.json)
- [packages/document-preprocessor/vitest.config.mts](packages/document-preprocessor/vitest.config.mts)
- [packages/giselle/package.json](packages/giselle/package.json)
- [pnpm-lock.yaml](pnpm-lock.yaml)
- [pnpm-workspace.yaml](pnpm-workspace.yaml)

</details>



This document covers the complete build pipeline, CI/CD workflows, testing processes, versioning, and deployment strategies for the Giselle platform. It includes the monorepo build orchestration, automated quality checks, release management, and license compliance processes.

For information about feature flag management and gradual rollouts, see [Feature Flag System](#4.1). For details about the overall project structure and package organization, see [Project Structure and Organization](#1.1).

## Build System Architecture

The Giselle project uses a sophisticated build system built around Turborepo for monorepo orchestration, pnpm for package management, and Node.js 22+ as the runtime requirement.

```mermaid
graph TD
    subgraph "Build Orchestration"
        TurboRepo["turbo build"]
        PnpmWorkspace["pnpm workspace"]
        PackageManager["pnpm@10.2.1"]
    end
    
    subgraph "Build Targets"
        FullBuild["turbo build<br/>All packages"]
        SDKBuild["turbo build --filter '@giselle-sdk/*'<br/>SDK packages only"]
        DataTypeBuild["turbo build --filter '@giselle-sdk/data-type'<br/>Data type package"]
        TypeCheck["turbo check-types<br/>TypeScript validation"]
    end
    
    subgraph "Quality Gates"
        BiomeCheck["biome check --write .<br/>Format & Lint"]
        KnipCheck["knip --no-config-hints<br/>Unused dependency detection"]
        TestSuite["turbo test<br/>Unit & Integration tests"]
    end
    
    subgraph "Development Tools"
        DevServer["turbo dev --filter playground<br/>Development mode"]
        StudioDev["turbo dev --filter studio.giselles.ai<br/>Production app dev"]
        CleanBuild["turbo clean<br/>Build artifact cleanup"]
    end
    
    TurboRepo --> FullBuild
    TurboRepo --> SDKBuild
    TurboRepo --> DataTypeBuild
    TurboRepo --> TypeCheck
    
    PnpmWorkspace --> TurboRepo
    PackageManager --> PnpmWorkspace
    
    FullBuild --> BiomeCheck
    FullBuild --> KnipCheck
    FullBuild --> TestSuite
    
    DevServer --> TurboRepo
    StudioDev --> TurboRepo
    CleanBuild --> TurboRepo
    
    style TurboRepo fill:#e1f5fe
    style PnpmWorkspace fill:#f3e5f5
    style BiomeCheck fill:#fff3e0
```

The build system supports incremental builds, parallel execution, and smart caching through Turborepo. The [`package.json:6-20`]() file defines the primary build scripts, with `turbo build` orchestrating the entire monorepo build process and specialized scripts for SDK-only builds.

Sources: [`package.json`](), [`knip.ts`]()

## Development Workflow and Quality Checks

The development workflow integrates multiple quality assurance tools and processes to maintain code quality and consistency across the monorepo.

```mermaid
graph TD
    subgraph "Code Quality Pipeline"
        BiomeCI["@biomejs/biome v2.0.6<br/>Format & Lint Check"]
        KnipAnalysis["knip<br/>Dependency Analysis"]
        TypeScriptCheck["TypeScript Validation<br/>Node.js 22.14.0"]
    end
    
    subgraph "Build Validation"
        SDKBuild["pnpm build-sdk<br/>SDK Package Build"]
        TestExecution["pnpm test<br/>Test Suite"]
        CacheValidation["pnpm cache validation"]
    end
    
    subgraph "Development Servers"
        PlaygroundDev["turbo dev --filter playground<br/>Development Environment"]
        StudioDev["NODE_NO_WARNINGS=1 turbo dev --filter studio.giselles.ai<br/>Production App Dev"]
        VercelDev["vercel dev<br/>Deployment Preview"]
    end
    
    subgraph "Utility Scripts"
        StripWorkspace["pnpm -F strip-workspace strip-workspace<br/>Workspace Cleanup"]
        PreVercel["pnpm i && pnpm build-sdk<br/>Pre-deployment Setup"]
        TidyCheck["pnpm tidy<br/>Alias for knip --no-config-hints"]
    end
    
    BiomeCI --> KnipAnalysis
    KnipAnalysis --> TypeScriptCheck
    TypeScriptCheck --> SDKBuild
    SDKBuild --> TestExecution
    
    PlaygroundDev --> SDKBuild
    StudioDev --> SDKBuild
    VercelDev --> PreVercel
    
    StripWorkspace --> CacheValidation
    TidyCheck --> KnipAnalysis
    
    style BiomeCI fill:#e1f5fe
    style SDKBuild fill:#f3e5f5
    style PlaygroundDev fill:#fff3e0
```

The [`knip.ts:85-117`]() configuration file defines workspace-specific rules for dependency analysis, including server external packages and framework-specific dependencies that should be ignored during unused dependency detection.

Sources: [`package.json`](), [`knip.ts`](), [`.zed/tasks.json`]()

## CI/CD Pipeline Architecture

The continuous integration and deployment pipeline consists of multiple specialized workflows that handle different aspects of the development lifecycle.

```mermaid
graph TD
    subgraph "Main CI Pipeline (.github/workflows/ci.yml)"
        Checkout["actions/checkout@v5<br/>Source code retrieval"]
        BiomeSetup["biomejs/setup-biome@v2.6.0<br/>Code formatter setup"]
        PnpmSetup["pnpm/action-setup@v4.1.0<br/>Package manager setup"]
        NodeSetup["actions/setup-node@v4.2.0<br/>Node.js 22.14.0"]
        BiomeRun["biome ci .<br/>Format & lint check"]
        KnipRun["pnpm knip<br/>Unused dependencies"]
        BuildSDK["pnpm build-sdk<br/>SDK build validation"]
        TestRun["pnpm test<br/>Test suite execution"]
    end
    
    subgraph "License Compliance (.github/workflows/license.yml)"
        LicenseCache["actions/cache@v4<br/>Dependency file caching"]
        RubySetup["ruby/setup-ruby@v1.257.0<br/>Ruby 3.3 setup"]
        LicenseFinder["gem install -N license_finder<br/>License analysis tool"]
        LicenseCheck["license_finder<br/>Compliance validation"]
        LicenseReport["license_finder report --format=markdown<br/>Generate docs/packages-license.md"]
    end
    
    subgraph "Release Management (.github/workflows/release.yml)"
        ChangesetAction["changesets/action@v1.5.3<br/>Version management"]
        ReleaseCreation["createGithubReleases: true<br/>Automated GitHub releases"]
        VersionCommand["pnpm version<br/>Package versioning"]
    end
    
    subgraph "E2E Testing (.github/workflows/e2e.yml)"
        PlaywrightCache["actions/cache@v4.2.3<br/>Browser cache management"]
        PlaywrightInstall["playwright install --with-deps<br/>Browser setup"]
        E2EExecution["pnpm test:e2e<br/>End-to-end test suite"]
    end
    
    Checkout --> BiomeSetup
    BiomeSetup --> PnpmSetup
    PnpmSetup --> NodeSetup
    NodeSetup --> BiomeRun
    BiomeRun --> KnipRun
    KnipRun --> BuildSDK
    BuildSDK --> TestRun
    
    LicenseCache --> RubySetup
    RubySetup --> LicenseFinder
    LicenseFinder --> LicenseCheck
    LicenseCheck --> LicenseReport
    
    ChangesetAction --> ReleaseCreation
    VersionCommand --> ReleaseCreation
    
    PlaywrightCache --> PlaywrightInstall
    PlaywrightInstall --> E2EExecution
    
    style Checkout fill:#e1f5fe
    style LicenseCheck fill:#f3e5f5
    style ChangesetAction fill:#fff3e0
    style E2EExecution fill:#f1f8e9
```

The CI pipeline runs on every push to main and pull request, ensuring code quality through automated checks. The [`license.yml:20-23`]() workflow uses concurrency controls to prevent overlapping executions and includes fork detection logic for secure token handling.

Sources: [`.github/workflows/ci.yml`](), [`.github/workflows/license.yml`](), [`.github/workflows/release.yml`](), [`.github/workflows/e2e.yml`]()

## Release and Versioning Process

The project implements a sophisticated release management system using Changesets for semantic versioning and automated package publishing.

### Changeset Configuration

The release process is configured through [`.changeset/config.json:1-11`](), which defines the versioning strategy, changelog generation, and package inclusion rules. The configuration excludes internal SDK packages and utilities from public releases while maintaining dependency tracking.

| Configuration Key | Value | Purpose |
|------------------|--------|---------|
| `changelog` | `@changesets/cli/changelog` | Automated changelog generation |
| `commit` | `false` | Manual commit control |
| `access` | `restricted` | Private package access |
| `baseBranch` | `main` | Primary development branch |
| `updateInternalDependencies` | `patch` | Internal dependency versioning |
| `ignore` | `["giselle-sdk", "@giselle-sdk/**", "@giselle-internal/**"]` | Excluded packages |

```mermaid
graph TD
    subgraph "Changeset Workflow"
        ChangesetCLI["@changesets/cli v2.28.1<br/>Version management"]
        ChangesetAdd["changeset<br/>Create version entry"]
        VersionUpdate["changeset version<br/>Update package versions"]
        PublishRelease["GitHub Release Creation<br/>Automated publishing"]
    end
    
    subgraph "Release Triggers"
        PRMerge["Pull Request to main<br/>Triggers release check"]
        ManualTrigger["Manual changeset creation<br/>Developer initiated"]
        ScheduledRelease["Release PR creation<br/>Automated versioning"]
    end
    
    subgraph "Version Types"
        PatchRelease["Patch (x.x.X)<br/>Bug fixes & minor updates"]
        MinorRelease["Minor (x.X.x)<br/>New features"]
        MajorRelease["Major (X.x.x)<br/>Breaking changes"]
    end
    
    subgraph "Package Categories"
        PublicPackages["Public packages<br/>Semantic versioning"]
        InternalSDK["@giselle-sdk/**<br/>Excluded from releases"]
        InternalTools["@giselle-internal/**<br/>Development utilities"]
    end
    
    ChangesetCLI --> ChangesetAdd
    ChangesetAdd --> VersionUpdate
    VersionUpdate --> PublishRelease
    
    PRMerge --> ChangesetCLI
    ManualTrigger --> ChangesetAdd
    ScheduledRelease --> VersionUpdate
    
    VersionUpdate --> PatchRelease
    VersionUpdate --> MinorRelease
    VersionUpdate --> MajorRelease
    
    PublicPackages --> VersionUpdate
    InternalSDK --> VersionUpdate
    InternalTools --> VersionUpdate
    
    style ChangesetCLI fill:#e1f5fe
    style PublishRelease fill:#f3e5f5
    style PatchRelease fill:#fff3e0
```

Sources: [`.changeset/config.json`](), [`.changeset/README.md`](), [`package.json`](), [`.github/workflows/release.yml`]()

## License Compliance System

The project maintains comprehensive license compliance through automated scanning and reporting of all dependencies.

### License Analysis Pipeline

The [`license.yml:18-112`]() workflow implements a sophisticated license compliance system that tracks dependency changes and generates compliance reports. The system uses caching to optimize performance and only runs when dependency-related files change.

```mermaid
graph TD
    subgraph "License Compliance Workflow"
        CacheCheck["Cache Check<br/>pnpm-lock.yaml & dependency files"]
        FileChangeDetection["File Change Detection<br/>license.yml, package.json, configs"]
        RubyEnvironment["Ruby 3.3 Setup<br/>License Finder runtime"]
        LicenseFinderInstall["gem install -N license_finder<br/>Analysis tool installation"]
        ComplianceCheck["license_finder<br/>Dependency license validation"]
        ReportGeneration["license_finder report --format=markdown<br/>Generate compliance report"]
    end
    
    subgraph "Compliance Tracking"
        PackageLicenseDoc["docs/packages-license.md<br/>1,107 tracked packages"]
        LicenseBreakdown["License Distribution<br/>815 MIT, 184 Apache 2.0, etc."]
        UnknownLicenses["Unknown License Tracking<br/>1 package flagged"]
        TimestampRemoval["sed -e '/^As of /d'<br/>Consistent report format"]
    end
    
    subgraph "Automated Updates"
        GitCommit["git commit -m 'Update docs/packages-license.md'<br/>Automated documentation"]
        PRUpdate["GitHub PR Update<br/>Non-fork repository only"]
        BranchPush["git push origin<br/>Updated compliance report"]
    end
    
    CacheCheck --> FileChangeDetection
    FileChangeDetection --> RubyEnvironment
    RubyEnvironment --> LicenseFinderInstall
    LicenseFinderInstall --> ComplianceCheck
    ComplianceCheck --> ReportGeneration
    ReportGeneration --> PackageLicenseDoc
    
    PackageLicenseDoc --> LicenseBreakdown
    LicenseBreakdown --> UnknownLicenses
    UnknownLicenses --> TimestampRemoval
    
    TimestampRemoval --> GitCommit
    GitCommit --> PRUpdate
    PRUpdate --> BranchPush
    
    style ComplianceCheck fill:#e1f5fe
    style PackageLicenseDoc fill:#f3e5f5
    style GitCommit fill:#fff3e0
```

The license compliance system tracks 1,107 packages across 22 different license types, with the majority being MIT (815 packages) and Apache 2.0 (184 packages) licensed. The [`docs/packages-license.md:4-23`]() file provides a comprehensive breakdown of license distribution and flagged packages requiring attention.

Sources: [`.github/workflows/license.yml`](), [`docs/packages-license.md`]()

## Testing and Quality Assurance

The testing strategy encompasses multiple layers of validation, from unit tests to end-to-end testing with Playwright.

### Testing Architecture

```mermaid
graph TD
    subgraph "E2E Testing Pipeline"
        PlaywrightVersion["Playwright Version Detection<br/>pnpm -s dlx playwright --version"]
        BrowserCache["Browser Cache Management<br/>~/.cache/ms-playwright"]
        PlaywrightInstall["playwright install --with-deps<br/>Browser & OS dependencies"]
        E2EExecution["pnpm test:e2e<br/>studio.giselles.ai workspace"]
    end
    
    subgraph "Test Configuration"
        BaseURL["PLAYWRIGHT_BASE_URL<br/>Environment-specific testing"]
        LoginCredentials["PLAYWRIGHT_LOGIN_EMAIL/PASSWORD<br/>Authentication secrets"]
        ScheduledRuns["Cron: '0 0,9 * * 1-5'<br/>Weekday automation"]
        WorkflowDispatch["workflow_dispatch<br/>Manual trigger support"]
    end
    
    subgraph "Quality Gates"
        UnitTests["turbo test<br/>Package-level testing"]
        TypeChecking["turbo check-types<br/>TypeScript validation"]
        LintChecks["biome ci .<br/>Code style validation"]
        DependencyCheck["knip<br/>Unused dependency detection"]
    end
    
    subgraph "Development Testing"
        ViTest["pnpm vitest watch<br/>Development mode testing"]
        TestWithSymbol["ZED_SYMBOL pattern matching<br/>Targeted test execution"]
        TestFileWatch["$ZED_FILENAME monitoring<br/>File-specific testing"]
    end
    
    PlaywrightVersion --> BrowserCache
    BrowserCache --> PlaywrightInstall
    PlaywrightInstall --> E2EExecution
    
    BaseURL --> E2EExecution
    LoginCredentials --> E2EExecution
    ScheduledRuns --> PlaywrightVersion
    WorkflowDispatch --> PlaywrightVersion
    
    UnitTests --> TypeChecking
    TypeChecking --> LintChecks
    LintChecks --> DependencyCheck
    
    ViTest --> TestWithSymbol
    TestWithSymbol --> TestFileWatch
    
    style E2EExecution fill:#e1f5fe
    style UnitTests fill:#f3e5f5
    style ViTest fill:#fff3e0
```

The E2E testing system runs on a schedule (weekdays at 9:00 and 18:00 JST) and supports manual triggers through `workflow_dispatch`. The [`e2e.yml:42-45`]() configuration shows environment variable handling for different testing environments and authentication.

Sources: [`.github/workflows/e2e.yml`](), [`.zed/tasks.json`](), [`package.json`]()

## Build Performance and Optimization

The build system leverages several optimization strategies to improve performance and maintainability across the monorepo.

### Caching and Performance Strategy

| Component | Caching Strategy | Performance Impact |
|-----------|------------------|-------------------|
| Playwright Browsers | `~/.cache/ms-playwright` with version-based keys | Reduces setup time from minutes to seconds |
| License Dependencies | Hash-based cache of dependency files | Skips analysis when no changes detected |
| pnpm Dependencies | Node.js cache integration | Faster package installation |
| Turbo Build Cache | Incremental build artifacts | Only rebuilds changed packages |

The [`knip.ts:10-83`]() configuration includes Next.js predefined external packages to optimize bundle analysis and prevent false positives in dependency detection. This comprehensive list covers common server-side packages that should be excluded from client-side bundling.

### Build Target Optimization

The build system provides granular control over build targets through specialized scripts:

- `build-sdk`: Targets only SDK packages for library development
- `build-data-type`: Builds only the data type package for rapid iteration
- `dev:studio.giselles.ai`: Runs the production application with Node.js warning suppression
- `strip-workspace`: Cleans workspace artifacts for deployment optimization

Sources: [`knip.ts`](), [`package.json`](), [`.github/workflows/ci.yml`](), [`.github/workflows/e2e.yml`]()