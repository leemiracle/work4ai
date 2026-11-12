<!-- source: DeepWiki mcp.deepwiki.com · repo OpenDCAI/OpenPrism · page 1 Overview · fetched 2026-11-02 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README_ZH.md](README_ZH.md)

</details>



## Purpose and Scope

This document provides a comprehensive overview of the OpenPrism system architecture, its core components, and design principles. OpenPrism is a local-first LaTeX workspace integrated with AI capabilities for academic writing. This page covers the system's high-level organization, technology stack, and component relationships.

For detailed information about specific subsystems:
- Installation and environment setup: see [Installation](#2.1)
- Frontend application structure and UI components: see [Frontend Architecture](#3.2)
- Backend services and API design: see [Backend Architecture](#3.3)
- Individual feature implementations: see [Features](#6)
- Development workflows and contribution guidelines: see [Development Guide](#7)

**Sources**: [README.md:1-65]()

---

## What is OpenPrism

OpenPrism is a **local-first LaTeX + AI workspace** designed for academic writing. It combines traditional LaTeX editing capabilities with modern AI-powered assistance while maintaining complete data sovereignty through local deployment. The system runs entirely on user-controlled infrastructure, with no mandatory cloud dependencies.

**Key Characteristics**:
- **Local-First Architecture**: All project data stored in configurable local filesystem directory
- **AI-Augmented Editing**: Three AI interaction modes (Chat, Agent, Tools) with OpenAI-compatible LLM integration
- **Full-Featured LaTeX Environment**: Supports multiple compilation engines (TexLive, Tectonic) with automatic fallback
- **Academic-Focused**: Built-in templates for major conferences (ACL, CVPR, NeurIPS, ICML), paper search integration, and citation management

**Sources**: [README.md:65-117]()

---

## System Architecture

### Three-Tier Architecture

OpenPrism implements a classic three-tier architecture with clear separation between presentation, application logic, and data persistence layers.

```mermaid
graph TB
    subgraph "Presentation Layer"
        Browser["Browser<br/>(Chrome/Firefox/Safari)"]
        ReactApp["React Application<br/>apps/frontend/src/app/"]
        UI["User Interface Components"]
    end
    
    subgraph "Application Layer"
        Fastify["Fastify Server<br/>apps/backend/src/index.js"]
        Routes["Route Handlers<br/>apps/backend/src/routes/"]
        Services["Service Layer<br/>apps/backend/src/services/"]
        Utils["Utilities<br/>apps/backend/src/utils/"]
    end
    
    subgraph "Data Layer"
        FileSystem["Local Filesystem"]
        DataDir["OPENPRISM_DATA_DIR<br/>./data/ (default)"]
        Projects["projects/<br/>Project directories"]
        Templates["templates/<br/>Template cache"]
    end
    
    subgraph "External Integration"
        LLMProvider["LLM Provider<br/>(OpenAI-compatible API)"]
        LaTeX["LaTeX Engines<br/>(pdflatex/xelatex/lualatex/tectonic)"]
        Python["Python Environment<br/>(matplotlib/pandas)"]
        ArxivAPI["arXiv.org API"]
    end
    
    Browser --> ReactApp
    ReactApp --> UI
    ReactApp -->|"HTTP REST API<br/>Port 5173 (dev) / 8787 (prod)"| Fastify
    
    Fastify --> Routes
    Routes --> Services
    Services --> Utils
    
    Services -->|"File I/O"| DataDir
    DataDir --> Projects
    DataDir --> Templates
    
    Services -->|"Process spawn"| LaTeX
    Services -->|"HTTP requests"| LLMProvider
    Services -->|"Process spawn"| Python
    Services -->|"HTTP requests"| ArxivAPI
```

**Sources**: [README.md:427-442]()

---

### Deployment Modes

OpenPrism supports two distinct deployment configurations with different process topologies.

```mermaid
graph TB
    subgraph "Development Mode (npm run dev)"
        DevFE["Vite Dev Server<br/>localhost:5173<br/>Hot Module Replacement"]
        DevBE["Fastify Server<br/>localhost:8787<br/>Auto-reload enabled"]
        DevFE -->|"CORS-enabled API calls"| DevBE
    end
    
    subgraph "Production Mode (npm start)"
        ProdServer["Unified Fastify Server<br/>localhost:8787"]
        StaticAssets["Built Frontend Assets<br/>apps/frontend/dist/"]
        APIRoutes["API Endpoints<br/>/api/*"]
        
        ProdServer --> StaticAssets
        ProdServer --> APIRoutes
    end
    
    subgraph "Process Management (Recommended)"
        PM2["PM2 Process Manager"]
        PM2 -->|"Manages"| ProdServer
    end
```

**Configuration Commands**:

| Mode | Command | Frontend Port | Backend Port |
|------|---------|---------------|--------------|
| Development | `npm run dev` | 5173 | 8787 |
| Production | `npm start` | - | 8787 (unified) |

**Sources**: [README.md:260-328](), [package.json scripts]()

---

## Core Components

### Frontend Application Structure

The frontend is a React single-page application built with Vite, organized into distinct functional modules.

```mermaid
graph TB
    subgraph "apps/frontend/src/"
        MainEntry["main.tsx<br/>Application entry point"]
        
        subgraph "app/"
            AppComponent["App.tsx<br/>Root component + routing"]
            LandingPage["LandingPage.tsx<br/>Marketing page"]
            ProjectPage["ProjectPage.tsx<br/>Project list management"]
            EditorPage["EditorPage.tsx<br/>Main workspace"]
        end
        
        subgraph "api/"
            APIClient["client.ts<br/>Centralized HTTP client"]
            ProjectAPI["Project operations"]
            FileAPI["File operations"]
            AgentAPI["AI agent calls"]
            CompileAPI["Compilation requests"]
        end
        
        subgraph "latex/"
            CMEditor["CodeMirrorEditor.tsx<br/>Editor wrapper"]
            LaTeXLang["latex-lang.ts<br/>Language definition"]
            FoldService["fold-service.ts<br/>Code folding"]
            CompletionSource["completion-source.ts<br/>Autocomplete"]
            GhostTextField["GhostTextField.tsx<br/>AI suggestions"]
        end
        
        subgraph "components/"
            SidebarTabs["Sidebar components<br/>(Agent/Files/Vision/etc)"]
            RightPanel["Right panel views<br/>(PDF/Diff/Log/etc)"]
            UIComponents["Reusable UI components"]
        end
        
        subgraph "locales/"
            i18nEn["en/translation.json"]
            i18nZh["zh/translation.json"]
        end
    end
    
    MainEntry --> AppComponent
    AppComponent --> LandingPage
    AppComponent --> ProjectPage
    AppComponent --> EditorPage
    
    EditorPage --> CMEditor
    EditorPage --> SidebarTabs
    EditorPage --> RightPanel
    EditorPage --> APIClient
    
    CMEditor --> LaTeXLang
    CMEditor --> FoldService
    CMEditor --> CompletionSource
    CMEditor --> GhostTextField
    
    AppComponent --> i18nEn
    AppComponent --> i18nZh
```

**Key Files**:

| Component | File Path | Responsibility |
|-----------|-----------|----------------|
| Application Root | `apps/frontend/src/app/App.tsx` | Routing, global state, layout |
| Editor Workspace | `apps/frontend/src/app/EditorPage.tsx` | Three-panel layout, editor state management |
| API Client | `apps/frontend/src/api/client.ts` | HTTP communication with backend |
| CodeMirror Integration | `apps/frontend/src/latex/CodeMirrorEditor.tsx` | LaTeX editor instantiation |
| Language Support | `apps/frontend/src/latex/latex-lang.ts` | LaTeX syntax highlighting |

**Sources**: [README.md:427-442]()

---

### Backend Service Architecture

The backend is a Fastify-based Node.js server with modular route handlers and service layers.

```mermaid
graph TB
    subgraph "apps/backend/src/"
        IndexJS["index.js<br/>Server initialization<br/>Route registration"]
        
        subgraph "routes/"
            HealthRoute["health.js<br/>GET /api/health<br/>GET /api/templates"]
            ProjectRoutes["projects.js<br/>/api/projects/*<br/>CRUD + import"]
            CompileRoute["compile.js<br/>POST /api/compile"]
            AgentRoute["agent.js<br/>POST /api/agent/run"]
            PlotRoute["plot.js<br/>POST /api/plot/from-table"]
            VisionRoute["vision.js<br/>POST /api/vision/latex"]
            ArxivRoute["arxiv.js<br/>/api/arxiv/*<br/>Search + download"]
            SearchRoute["search.js<br/>POST /api/search"]
        end
        
        subgraph "services/"
            ProjectService["projectService.js<br/>Project lifecycle"]
            TemplateService["templateService.js<br/>Template management"]
            LLMService["llmService.js<br/>OpenAI API abstraction"]
            PlotService["plotService.js<br/>Python plot generation"]
            ArxivService["arxivService.js<br/>Paper download"]
            CompileService["compileService.js<br/>LaTeX execution"]
        end
        
        subgraph "utils/"
            FSUtils["fsUtils.js<br/>Safe file operations"]
            PathUtils["pathUtils.js<br/>Path sanitization"]
            TexUtils["texUtils.js<br/>LaTeX parsing"]
            I18nUtils["i18nUtils.js<br/>Backend localization"]
        end
        
        subgraph "config/"
            EnvConfig[".env file<br/>Environment variables"]
            Constants["constants.js<br/>System defaults"]
        end
    end
    
    IndexJS --> HealthRoute
    IndexJS --> ProjectRoutes
    IndexJS --> CompileRoute
    IndexJS --> AgentRoute
    IndexJS --> PlotRoute
    IndexJS --> VisionRoute
    IndexJS --> ArxivRoute
    IndexJS --> SearchRoute
    
    HealthRoute --> TemplateService
    ProjectRoutes --> ProjectService
    ProjectRoutes --> TemplateService
    CompileRoute --> CompileService
    AgentRoute --> LLMService
    PlotRoute --> PlotService
    PlotRoute --> LLMService
    VisionRoute --> LLMService
    ArxivRoute --> ArxivService
    
    ProjectService --> FSUtils
    ProjectService --> PathUtils
    TemplateService --> FSUtils
    CompileService --> TexUtils
    
    LLMService --> EnvConfig
    ProjectService --> Constants
```

**API Endpoints**:

| Endpoint | Method | Route Handler | Purpose |
|----------|--------|---------------|---------|
| `/api/health` | GET | `routes/health.js` | Server health check |
| `/api/templates` | GET | `routes/health.js` | List available templates |
| `/api/projects` | GET | `routes/projects.js` | List user projects |
| `/api/projects/:id` | GET/PUT/DELETE | `routes/projects.js` | Project operations |
| `/api/projects/:id/files` | GET/PUT | `routes/projects.js` | File operations |
| `/api/compile` | POST | `routes/compile.js` | LaTeX compilation |
| `/api/agent/run` | POST | `routes/agent.js` | AI agent execution |
| `/api/plot/from-table` | POST | `routes/plot.js` | Generate plot from table |
| `/api/vision/latex` | POST | `routes/vision.js` | Image to LaTeX OCR |
| `/api/arxiv/search` | GET | `routes/arxiv.js` | Search arXiv papers |

**Sources**: [README.md:427-442]()

---

## Technology Stack

### Core Dependencies

The system is built on modern JavaScript ecosystem tools with minimal external dependencies for core functionality.

**Frontend**:
| Technology | Version Requirement | Purpose |
|------------|---------------------|---------|
| React | Latest | UI framework |
| Vite | Latest | Build tool and dev server |
| CodeMirror 6 | Latest | Code editor core |
| PDF.js | Latest | PDF rendering in browser |
| i18next | Latest | Internationalization |
| react-router-dom | Latest | Client-side routing |

**Backend**:
| Technology | Version Requirement | Purpose |
|------------|---------------------|---------|
| Node.js | >= 18.0.0 | Runtime environment |
| Fastify | Latest | HTTP server framework |
| axios | Latest | HTTP client for external APIs |

**External Dependencies** (Runtime):
| Dependency | Installation Method | Purpose |
|------------|---------------------|---------|
| TexLive or Tectonic | System package manager | LaTeX compilation |
| Python 3.x | System package manager | Optional: plot generation |

**Sources**: [README.md:224-258](), [apps/frontend/package.json](), [apps/backend/package.json]()

---

## Data Storage Model

### Filesystem Organization

OpenPrism uses a directory-based storage model with a configurable root path.

```mermaid
graph TB
    subgraph "OPENPRISM_DATA_DIR (default: ./data)"
        DataRoot["Data Root Directory"]
        
        subgraph "projects/"
            ProjectList["Project directories<br/>(one per project)"]
            Project1["project-uuid-1/"]
            Project2["project-uuid-2/"]
            
            subgraph "project-uuid-1/"
                ProjectMeta["project.json<br/>Project metadata"]
                MainTex["main.tex<br/>LaTeX source"]
                RefBib["references.bib<br/>Bibliography"]
                Figures["figures/<br/>Images and assets"]
                OtherFiles["*.tex, *.sty, *.cls<br/>Additional LaTeX files"]
            end
        end
        
        subgraph "templates/"
            TemplateCache["Cached template files<br/>(copied from templates/ repo dir)"]
            ACLTemplate["ACL2023/"]
            CVPRTemplate["CVPR2024/"]
            NeurIPSTemplate["NeurIPS2023/"]
        end
    end
    
    DataRoot --> ProjectList
    DataRoot --> TemplateCache
    ProjectList --> Project1
    ProjectList --> Project2
    Project1 --> ProjectMeta
    Project1 --> MainTex
    Project1 --> RefBib
    Project1 --> Figures
    Project1 --> OtherFiles
```

**Project Metadata Schema** (`project.json`):
```json
{
  "id": "uuid-string",
  "name": "Project Name",
  "createdAt": "ISO-8601-timestamp",
  "updatedAt": "ISO-8601-timestamp",
  "mainFile": "main.tex",
  "template": "ACL2023",
  "tags": ["tag1", "tag2"]
}
```

**Storage Configuration**:
- Environment variable: `OPENPRISM_DATA_DIR`
- Default value: `./data` (relative to project root)
- Example custom path: `/var/openprism/data`

**Sources**: [README.md:395-413]()

---

## Configuration System

### Multi-Layer Configuration

OpenPrism implements a hierarchical configuration system with clear precedence rules.

```mermaid
graph TB
    subgraph "Configuration Sources (Precedence Order)"
        Runtime["1. Runtime Overrides<br/>(Per-request parameters)"]
        Frontend["2. Frontend localStorage<br/>(User preferences)"]
        Backend["3. Backend .env<br/>(System defaults)"]
        Hardcoded["4. Hardcoded Defaults<br/>(Fallback values)"]
    end
    
    subgraph "Backend Configuration (.env)"
        LLMEndpoint["OPENPRISM_LLM_ENDPOINT<br/>Default: none"]
        LLMKey["OPENPRISM_LLM_API_KEY<br/>Default: none"]
        LLMModel["OPENPRISM_LLM_MODEL<br/>Default: gpt-4o-mini"]
        DataDir["OPENPRISM_DATA_DIR<br/>Default: ./data"]
        Port["PORT<br/>Default: 8787"]
        PythonPath["OPENPRISM_PYTHON<br/>Default: python3"]
    end
    
    subgraph "Frontend Configuration (localStorage)"
        UIEndpoint["llmEndpoint<br/>User-specific endpoint"]
        UIKey["llmApiKey<br/>User-specific key"]
        UIModel["llmModel<br/>User-specific model"]
        CompileEngine["compileEngine<br/>auto/pdflatex/xelatex/etc"]
        TexPath["texLiveResourcePath<br/>Custom TeX installation"]
        Language["language<br/>en/zh"]
    end
    
    Runtime -->|"Highest priority"| LLMService["LLM Service Resolution"]
    Frontend -->|"User overrides"| LLMService
    Backend -->|"System defaults"| LLMService
    Hardcoded -->|"Fallback"| LLMService
```

**Environment Variables**:
| Variable | Purpose | Example Value |
|----------|---------|---------------|
| `OPENPRISM_LLM_ENDPOINT` | OpenAI-compatible API endpoint | `https://api.openai.com/v1/chat/completions` |
| `OPENPRISM_LLM_API_KEY` | API authentication key | `sk-...` |
| `OPENPRISM_LLM_MODEL` | Default model name | `gpt-4o-mini` |
| `OPENPRISM_DATA_DIR` | Project storage root | `./data` |
| `PORT` | Backend server port | `8787` |
| `OPENPRISM_PYTHON` | Python executable path | `python3` |

**Sources**: [README.md:332-402]()

---

## Key Design Principles

### Local-First Architecture

**Data Sovereignty**: All user data persists in the local filesystem with no mandatory cloud synchronization. The `OPENPRISM_DATA_DIR` directory contains complete project state, enabling easy backup, version control integration, and migration.

**Privacy-Preserving AI**: LLM integration is abstracted through the `llmService.js` module, allowing users to:
- Use self-hosted LLM endpoints
- Configure per-request in frontend without backend restart
- Operate entirely offline (compilation, editing) when AI features are not needed

**Sources**: [README.md:65]()

---

### Modular Service Design

**Separation of Concerns**: Backend services are isolated in dedicated modules:
- `projectService.js`: Project lifecycle (create, read, update, delete)
- `compileService.js`: LaTeX compilation pipeline (engine selection, execution, error parsing)
- `llmService.js`: LLM provider abstraction (API calls, response parsing)
- `plotService.js`: Python-based visualization (code generation, execution, asset management)

This isolation enables:
- Independent testing of each service
- Easy extension with new AI capabilities
- Safe error handling (e.g., LaTeX compilation failures don't crash the server)

**Sources**: [apps/backend/src/services/]()

---

### OpenAI-Compatible LLM Integration

**Provider Agnostic**: The system uses the OpenAI Chat Completions API format as the standardized interface, supporting:
- OpenAI official endpoint: `https://api.openai.com/v1`
- Azure OpenAI: Custom deployment URLs
- Third-party providers: Any OpenAI-compatible service
- Self-hosted models: Local inference servers (e.g., vLLM, Ollama with OpenAI compatibility layer)

**Configuration Flexibility**: Users can override LLM settings at three levels:
1. System-wide defaults in `.env`
2. Per-user settings in browser `localStorage`
3. Per-request overrides in API calls

**Sources**: [README.md:352-380]()

---

### Multi-Engine LaTeX Support

**Automatic Fallback**: The compilation service (`compileService.js`) attempts multiple LaTeX engines in sequence:
1. User-specified engine (if configured)
2. `pdflatex` (standard)
3. `xelatex` (Unicode support)
4. `lualatex` (Lua scripting)
5. `tectonic` (lightweight fallback)

This ensures maximum compatibility across different system configurations without requiring manual engine selection.

**Sources**: [README.md:381-393]()

---

## System Initialization Flow

The following diagram shows the complete startup sequence from server launch to ready state.

```mermaid
sequenceDiagram
    participant User
    participant Fastify as "Fastify Server<br/>(index.js)"
    participant Routes as "Route Handlers<br/>(routes/*)"
    participant Services as "Service Layer<br/>(services/*)"
    participant FS as "File System"
    participant ENV as "Environment<br/>(.env)"
    
    User->>Fastify: npm start
    Fastify->>ENV: Load environment variables
    ENV-->>Fastify: Configuration loaded
    
    Fastify->>FS: Check OPENPRISM_DATA_DIR
    alt Directory exists
        FS-->>Fastify: Directory accessible
    else Directory missing
        Fastify->>FS: Create directory structure
        FS-->>Fastify: Directories created
    end
    
    Fastify->>Routes: Register route handlers
    Routes->>Services: Initialize services
    Services-->>Routes: Services ready
    Routes-->>Fastify: Routes registered
    
    Fastify->>Fastify: Start HTTP server on PORT
    Fastify-->>User: Server listening on http://localhost:8787
    
    Note over User,Fastify: Server ready to accept requests
    
    User->>Fastify: Browser loads http://localhost:8787
    Fastify->>Fastify: Serve static frontend assets
    Fastify-->>User: Return index.html + JS bundles
    
    User->>User: React app initializes
    User->>Fastify: GET /api/health
    Fastify->>Routes: Health check route
    Routes-->>User: {"status": "ok"}
    
    User->>Fastify: GET /api/projects
    Fastify->>Routes: Projects route
    Routes->>Services: projectService.listProjects()
    Services->>FS: Read OPENPRISM_DATA_DIR/projects/
    FS-->>Services: Project list
    Services-->>Routes: Project metadata array
    Routes-->>User: [{"id": "...", "name": "..."}]
```

**Sources**: [apps/backend/src/index.js](), [apps/frontend/src/main.tsx]()

---

