<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-cua-sample-app · page 3 Applications · fetched 2026-10-26 -->

# Applications

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This document describes the two main applications in the openai-cua-sample-app monorepo: the operator console (`apps/demo-web`) and the runner service (`apps/runner`). These applications work together to provide a complete system for executing browser-focused computer-use scenarios using GPT-5.4.

For detailed information about the shared packages these applications depend on, see [Core Packages](#4). For information about how scenarios are executed within the runner, see [Scenarios](#6).

## System Architecture

The repository implements a client-server architecture with two distinct applications that communicate over HTTP and Server-Sent Events (SSE).

### Application Overview

```mermaid
graph TB
    subgraph DemoWeb["apps/demo-web"]
        WebUI["Next.js Application<br/>Port 3000"]
        WebUIPages["Pages:<br/>• / (scenario selection)<br/>• /runs/[id] (live view)<br/>• /replays/[id] (replay view)"]
        WebUIComponents["Components:<br/>• ScenarioSelector<br/>• RunMonitor<br/>• ReplayViewer"]
        WebUIAPI["API Client:<br/>fetch + EventSource"]
    end
    
    subgraph Runner["apps/runner"]
        RunnerServer["Fastify Server<br/>Port 4001"]
        RunnerEndpoints["HTTP Endpoints:<br/>• POST /run<br/>• GET /replay/:id<br/>• GET /runs/:id/stream"]
        RunnerWorkspace["Workspace Manager:<br/>• Creates isolated dirs<br/>• Copies labs templates<br/>• Bundles artifacts"]
        RunnerOrchestration["Orchestration:<br/>• Browser sessions<br/>• SSE streams<br/>• Replay bundles"]
    end
    
    subgraph Packages["Shared Packages"]
        ReplaySchema["replay-schema<br/>Type contracts"]
        RunnerCore["runner-core<br/>Execution logic"]
        BrowserRuntime["browser-runtime<br/>Playwright wrapper"]
        ScenarioKit["scenario-kit<br/>Manifests"]
    end
    
    WebUI --> WebUIPages
    WebUI --> WebUIComponents
    WebUIComponents --> WebUIAPI
    WebUIAPI -->|"HTTP + SSE"| RunnerServer
    
    RunnerServer --> RunnerEndpoints
    RunnerServer --> RunnerWorkspace
    RunnerServer --> RunnerOrchestration
    
    WebUI -.->|imports| ReplaySchema
    RunnerServer -.->|imports| ReplaySchema
    RunnerOrchestration --> RunnerCore
    RunnerCore --> BrowserRuntime
    RunnerCore --> ScenarioKit
```

**Sources:** [README.md:5-7](), [README.md:108-121]()

The system separates presentation concerns (`demo-web`) from execution concerns (`runner`), enabling:
- Independent development and deployment of each service
- Clear responsibility boundaries
- Type-safe communication via `replay-schema` contracts
- Flexible hosting configurations (same machine or distributed)

### Communication Patterns

The applications communicate using three distinct patterns:

| Pattern | Direction | Purpose | Endpoint |
|---------|-----------|---------|----------|
| HTTP POST | Web → Runner | Initiate scenario execution | `POST /run` |
| SSE Stream | Runner → Web | Real-time execution updates | `GET /runs/:id/stream` |
| HTTP GET | Web → Runner | Retrieve replay artifacts | `GET /replay/:id` |

```mermaid
sequenceDiagram
    participant Browser as "Browser<br/>(User)"
    participant DemoWeb as "demo-web<br/>:3000"
    participant RunnerAPI as "runner<br/>:4001"
    participant RunnerCore as "runner-core"
    
    Browser->>DemoWeb: "Visit /"
    DemoWeb-->>Browser: "Scenario selection UI"
    
    Browser->>DemoWeb: "Select scenario + Start"
    DemoWeb->>RunnerAPI: "POST /run<br/>{scenarioId, config}"
    activate RunnerAPI
    
    RunnerAPI->>RunnerAPI: "Create workspace"
    RunnerAPI-->>DemoWeb: "201 {runId, streamUrl}"
    deactivate RunnerAPI
    
    DemoWeb->>Browser: "Navigate to /runs/[id]"
    Browser->>DemoWeb: "Load run monitor"
    DemoWeb->>RunnerAPI: "EventSource /runs/:id/stream"
    activate RunnerAPI
    
    RunnerAPI->>RunnerCore: "Execute scenario"
    
    loop "Each turn"
        RunnerCore-->>RunnerAPI: "Event + screenshot"
        RunnerAPI-->>DemoWeb: "SSE: event data"
        DemoWeb-->>Browser: "Update UI"
    end
    
    RunnerCore-->>RunnerAPI: "Completion + outcome"
    RunnerAPI->>RunnerAPI: "Bundle replay artifacts"
    RunnerAPI-->>DemoWeb: "SSE: done"
    deactivate RunnerAPI
    
    DemoWeb-->>Browser: "Show results link"
    
    Browser->>DemoWeb: "Navigate to /replays/[id]"
    DemoWeb->>RunnerAPI: "GET /replay/:id"
    RunnerAPI-->>DemoWeb: "Replay bundle"
    DemoWeb-->>Browser: "Replay viewer"
```

**Sources:** [README.md:5-7](), Diagram 5 from architecture overview

## Application Services

### Service Ports and URLs

Both applications run on localhost by default with fixed ports:

| Service | Default URL | Environment Variable |
|---------|-------------|---------------------|
| `demo-web` | `http://127.0.0.1:3000` | `RUNNER_BASE_URL` (to configure runner location) |
| `runner` | `http://127.0.0.1:4001` | `HOST` and `PORT` |

**Sources:** [README.md:130-131](), [README.md:137](), [README.md:64]()

### Monorepo Structure

```mermaid
graph LR
    subgraph Root["openai-cua-sample-app/"]
        EnvFile[".env<br/>(runner config)"]
        
        subgraph AppsDir["apps/"]
            DemoWeb["demo-web/<br/>Next.js app"]
            Runner["runner/<br/>Fastify app"]
        end
        
        subgraph PackagesDir["packages/"]
            ReplaySchema["replay-schema/"]
            ScenarioKit["scenario-kit/"]
            BrowserRuntime["browser-runtime/"]
            RunnerCore["runner-core/"]
        end
        
        subgraph LabsDir["labs/"]
            KanbanLab["kanban/"]
            PaintLab["paint/"]
            BookingLab["booking/"]
        end
    end
    
    DemoWeb -->|reads| EnvFile
    Runner -->|reads| EnvFile
    
    DemoWeb -->|imports| ReplaySchema
    Runner -->|imports| ReplaySchema
    Runner -->|imports| RunnerCore
    
    RunnerCore -->|imports| BrowserRuntime
    RunnerCore -->|imports| ScenarioKit
    
    Runner -->|copies templates from| LabsDir
```

**Sources:** [README.md:106-123]()

The monorepo uses pnpm workspaces to manage dependencies between applications and packages. Both applications import the `replay-schema` package for type-safe communication contracts.

## Development Modes

The system supports three development modes:

### Full System Mode

```bash
pnpm dev
```

Starts both `demo-web` (port 3000) and `runner` (port 4001) simultaneously. This is the standard development mode.

**Sources:** [README.md:60-62]()

### Independent Services Mode

```bash
# Terminal 1: Start runner only
pnpm dev:runner

# Terminal 2: Start web only with runner URL
RUNNER_BASE_URL=http://127.0.0.1:4001 pnpm dev:web
```

Runs services in separate terminals for independent log viewing. The `RUNNER_BASE_URL` environment variable configures the web application to connect to a specific runner instance.

**Sources:** [README.md:66-73]()

### Configuration Matrix

The following environment variables control inter-service communication:

| Variable | Location | Purpose | Default |
|----------|----------|---------|---------|
| `HOST` | Runner `.env` | Runner bind address | `127.0.0.1` |
| `PORT` | Runner `.env` | Runner listen port | `4001` |
| `RUNNER_BASE_URL` | Web `.env.local` or env | Runner API endpoint | `http://127.0.0.1:4001` |

**Sources:** [README.md:130-131](), [README.md:137]()

This configuration enables flexible deployment scenarios:
- Local development: both services on localhost
- Distributed development: runner on separate host/container
- Production: services behind reverse proxy or load balancer

## Workspace Management

The runner creates isolated workspace directories for each execution:

```mermaid
graph TB
    subgraph WorkspaceLifecycle["Workspace Lifecycle"]
        Start["Run initiated:<br/>POST /run"]
        Create["Create unique workspace dir:<br/>/tmp/run-{uuid}"]
        Copy["Copy lab templates:<br/>labs/{scenario}/* → workspace/"]
        Execute["Execute scenario:<br/>Browser points to workspace"]
        Bundle["Bundle artifacts:<br/>screenshots + events + metadata"]
        Serve["Serve replay:<br/>GET /replay/{id}"]
    end
    
    Start --> Create
    Create --> Copy
    Copy --> Execute
    Execute --> Bundle
    Bundle --> Serve
    
    subgraph LabTemplates["labs/"]
        KanbanTemplate["kanban/index.html"]
        PaintTemplate["paint/index.html"]
        BookingTemplate["booking/index.html"]
    end
    
    subgraph Workspace["Workspace: /tmp/run-abc123/"]
        WorkspaceFiles["index.html<br/>(copied from lab)"]
        WorkspaceArtifacts["artifacts/<br/>• screenshots/<br/>• events.json<br/>• metadata.json"]
    end
    
    Copy -.->|"cp -r"| KanbanTemplate
    Copy -.->|"cp -r"| PaintTemplate
    Copy -.->|"cp -r"| BookingTemplate
    
    Copy --> WorkspaceFiles
    Execute --> WorkspaceArtifacts
```

**Sources:** [README.md:6](), [README.md:121]()

Each run receives:
- A unique workspace directory for isolated execution
- A copy of the appropriate lab template from `labs/{scenario}/`
- Write access for saving artifacts and screenshots
- Automatic cleanup after replay bundle creation

## Type Safety Boundary

The `replay-schema` package enforces type consistency across the HTTP boundary:

```mermaid
graph LR
    subgraph DemoWebTypes["demo-web (TypeScript)"]
        WebRequest["RunRequest type"]
        WebResponse["RunResponse type"]
        WebEvents["ReplayEvent types"]
    end
    
    subgraph ReplaySchemaPackage["packages/replay-schema"]
        SchemaRequest["RunRequest interface"]
        SchemaResponse["RunResponse interface"]
        SchemaEvents["ReplayEvent union"]
        SchemaErrors["ErrorCode enum"]
    end
    
    subgraph RunnerTypes["runner (TypeScript)"]
        RunnerRequest["RunRequest type"]
        RunnerResponse["RunResponse type"]
        RunnerEvents["ReplayEvent types"]
    end
    
    DemoWebTypes -->|imports| ReplaySchemaPackage
    RunnerTypes -->|imports| ReplaySchemaPackage
    
    WebRequest -.->|"same type"| RunnerRequest
    WebResponse -.->|"same type"| RunnerResponse
    WebEvents -.->|"same type"| RunnerEvents
```

**Sources:** [README.md:112-113](), [README.md:7]()

Both applications import from `@cua/replay-schema`, ensuring:
- Request/response contracts match exactly
- Enum values are consistent
- Event types are validated at compile time
- Refactoring safety across the HTTP boundary

For details on specific schema types, see [replay-schema](#4.4).

## Next Steps

- For detailed documentation of the operator console UI, see [Operator Console (demo-web)](#3.1)
- For detailed documentation of the runner service API and orchestration, see [Runner Service](#3.2)
- For information about the execution logic within the runner, see [runner-core and responses-loop](#4.1)

---

