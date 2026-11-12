<!-- source: DeepWiki mcp.deepwiki.com · repo giselles-ai/giselle · page 6 Applications and User Interfaces · fetched 2026-10-26 -->

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

