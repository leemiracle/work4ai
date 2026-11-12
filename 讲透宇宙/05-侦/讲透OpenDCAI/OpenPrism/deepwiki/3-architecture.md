<!-- source: DeepWiki mcp.deepwiki.com · repo OpenDCAI/OpenPrism · page 3 Architecture · fetched 2026-11-02 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [apps/frontend/src/api/client.ts](apps/frontend/src/api/client.ts)

</details>



This document provides a comprehensive technical overview of OpenPrism's system architecture, including its three-tier design, component relationships, data flow patterns, and key design decisions. For installation and configuration details, see [Getting Started](#2). For specific feature implementations, see [Features](#6). For development workflows, see [Development Guide](#7).

## Purpose and Scope

This page documents the structural organization of the OpenPrism codebase, describing how the frontend React application communicates with the Fastify backend server, how services are layered and integrated, and how external dependencies (LLM providers, LaTeX engines, Python environment) are orchestrated. The focus is on architectural patterns, component boundaries, and the relationships between major subsystems rather than implementation details of individual features.

---

## System Overview

OpenPrism implements a **three-tier architecture** with clear separation between presentation, business logic, and data persistence layers.

```mermaid
graph TB
    subgraph Browser["Client Browser"]
        React["React Application<br/>(apps/frontend)<br/>Port 5173 dev"]
        LocalStorage["localStorage<br/>User preferences & LLM config"]
    end
    
    subgraph Server["Backend Server"]
        Fastify["Fastify Server<br/>(apps/backend)<br/>Port 8787"]
        
        subgraph CoreServices["Core Services"]
            ProjectSvc["ProjectService<br/>Project CRUD"]
            TemplateSvc["TemplateService<br/>Template operations"]
            CompileSvc["CompileService<br/>LaTeX execution"]
        end
        
        subgraph AIServices["AI Services"]
            AgentSvc["AgentService<br/>LLM orchestration"]
            PlotSvc["PlotService<br/>Chart generation"]
            VisionSvc["VisionService<br/>Image OCR"]
        end
        
        subgraph Integration["Integration Services"]
            ArxivSvc["ArxivService<br/>Paper import"]
            SearchSvc["SearchService<br/>Web/academic search"]
        end
    end
    
    subgraph External["External Dependencies"]
        LLM["LLM Provider<br/>OpenAI-compatible"]
        LaTeX["LaTeX Engines<br/>pdflatex/xelatex/tectonic"]
        Python["Python<br/>matplotlib/seaborn"]
    end
    
    subgraph Storage["File System Storage"]
        DataDir["OPENPRISM_DATA_DIR<br/>./data (default)"]
        Projects["projects/<br/>User LaTeX files"]
        Templates["templates/<br/>Built-in templates"]
    end
    
    React -->|"REST API<br/>/api/*"| Fastify
    React <-->|"Read/Write"| LocalStorage
    
    Fastify --> CoreServices
    Fastify --> AIServices
    Fastify --> Integration
    
    ProjectSvc <-->|"fs operations"| Projects
    TemplateSvc <-->|"Read"| Templates
    CompileSvc -->|"spawn"| LaTeX
    
    AgentSvc -->|"HTTP POST"| LLM
    VisionSvc -->|"HTTP POST"| LLM
    PlotSvc -->|"spawn"| Python
    PlotSvc -->|"Code generation"| LLM
    
    DataDir --> Projects
    DataDir --> Templates
```

**Architecture Characteristics:**

| Layer | Technology | Responsibility |
|-------|-----------|---------------|
| Frontend | React + Vite + CodeMirror 6 | UI rendering, editor state, user interactions |
| Backend | Fastify + Node.js | API routing, business logic, external integrations |
| Storage | File system (local) | Project files, templates, generated assets |
| External | OpenAI-compatible LLM, LaTeX, Python | Compute-intensive operations |

The system follows a **local-first philosophy**: all user data persists in a configurable directory (`OPENPRISM_DATA_DIR`), and the LLM configuration can be overridden per-user via browser localStorage or per-request via API parameters.

**Sources:** [README.md:63-117](), [apps/frontend/src/api/client.ts:1-368]()

---

## Component Interaction Patterns

### Request Flow: Project Compilation

This diagram shows how a typical compilation request flows through the system, mapping natural language concepts to actual code entities.

```mermaid
sequenceDiagram
    participant User
    participant EditorPage as "EditorPage.tsx<br/>React Component"
    participant APIClient as "client.ts<br/>compileProject()"
    participant FastifyRoute as "/api/compile<br/>Route Handler"
    participant CompileSvc as "CompileService<br/>services/compile.js"
    participant LaTeXEngine as "pdflatex/xelatex/tectonic<br/>child_process.spawn()"
    participant FileSystem as "DATA_DIR/projects/{id}"
    
    User->>EditorPage: Click "Compile PDF"
    EditorPage->>APIClient: compileProject({projectId, mainFile, engine})
    APIClient->>FastifyRoute: POST /api/compile
    FastifyRoute->>CompileSvc: compileProject(payload)
    CompileSvc->>FileSystem: Write temp files
    CompileSvc->>LaTeXEngine: spawn(engine, [args])
    LaTeXEngine-->>CompileSvc: stdout/stderr
    CompileSvc->>CompileSvc: parseLog(log)
    CompileSvc->>FileSystem: Read output.pdf
    CompileSvc-->>FastifyRoute: {pdf: base64, log: string}
    FastifyRoute-->>APIClient: JSON response
    APIClient-->>EditorPage: {ok, pdf, log}
    EditorPage->>EditorPage: createObjectURL(pdf)
    EditorPage->>User: Display PDF in right panel
```

**Key Code Entities:**

- **Frontend:** `EditorPage` component manages compilation triggers [apps/frontend/src/app/EditorPage.tsx]()
- **API Client:** `compileProject()` function handles HTTP communication [apps/frontend/src/api/client.ts:219-231]()
- **Backend Route:** `/api/compile` route registered in [apps/backend/src/routes/compile.js]()
- **Service Layer:** `CompileService` orchestrates LaTeX engine execution [apps/backend/src/services/compile.js]()

**Sources:** [apps/frontend/src/api/client.ts:219-231](), [apps/backend/src/routes/compile.js](), Diagram 1 and Diagram 5 from high-level overview

---

## Frontend Architecture

The frontend is a **single-page application (SPA)** built with React, using Vite as the build tool and development server.

### Routing Structure

```mermaid
graph LR
    Router["react-router-dom<br/>BrowserRouter"]
    
    Router --> Landing["/<br/>LandingPage.tsx"]
    Router --> Projects["/projects<br/>ProjectPage.tsx"]
    Router --> Editor["/editor/:projectId<br/>EditorPage.tsx"]
    
    Landing --> I18n["i18next<br/>Internationalization"]
    Projects --> I18n
    Editor --> I18n
    
    Editor --> Sidebar["Sidebar<br/>7 tab modes"]
    Editor --> CodeMirror["CodeMirror 6<br/>LaTeX editor"]
    Editor --> RightPanel["Right Panel<br/>6 view modes"]
```

**Route Definitions:**

| Path | Component | Purpose |
|------|-----------|---------|
| `/` | `LandingPage.tsx` | Marketing page with feature carousel |
| `/projects` | `ProjectPage.tsx` | Project list management UI |
| `/editor/:projectId` | `EditorPage.tsx` | Main workspace with three-panel layout |

**Sources:** [apps/frontend/src/app/LandingPage.tsx](), [apps/frontend/src/app/ProjectPage.tsx](), [apps/frontend/src/app/EditorPage.tsx]()

### EditorPage Architecture

The `EditorPage` component is the most complex frontend component, implementing a three-panel workspace.

```mermaid
graph TB
    EditorPage["EditorPage Component<br/>(apps/frontend/src/app/EditorPage.tsx)"]
    
    subgraph LeftPanel["Left Sidebar (7 tabs)"]
        FilesTab["Files Tab<br/>File tree + outline"]
        AgentTab["Agent Tab<br/>Chat/Agent/Tools modes"]
        VisionTab["Vision Tab<br/>Image → LaTeX"]
        ArxivTab["arXiv Tab<br/>Paper search"]
        WebTab["Web Tab<br/>Web search"]
        PlotTab["Plot Tab<br/>Table → Chart"]
        ReviewTab["Review Tab<br/>Quality checks"]
    end
    
    subgraph CenterPanel["Center Editor"]
        CMEditor["CodeMirror EditorView<br/>LaTeX editing"]
        CMState["EditorState<br/>Document + extensions"]
        CMExtensions["Extensions:<br/>- LaTeX language<br/>- Fold service<br/>- Autocompletion<br/>- Ghost text"]
    end
    
    subgraph RightPanel["Right Panel (6 views)"]
        PDFView["PDF Preview<br/>PDF.js rendering"]
        DiffView["Diff Viewer<br/>Split diff display"]
        LogView["Compile Log<br/>Error highlighting"]
        TOCView["Table of Contents<br/>Section navigation"]
        FiguresView["Figures Gallery<br/>Asset preview"]
        ReviewView["Review Report<br/>Markdown display"]
    end
    
    EditorPage --> LeftPanel
    EditorPage --> CenterPanel
    EditorPage --> RightPanel
    
    EditorPage --> AppState["React State:<br/>- currentProject<br/>- fileTree<br/>- compileLog<br/>- pdfBlob"]
    EditorPage --> APIClient["API Client<br/>client.ts"]
```

**State Management:**

The `EditorPage` manages multiple state concerns:

1. **Project State:** Current project metadata, file tree structure [apps/frontend/src/app/EditorPage.tsx]()
2. **Editor State:** CodeMirror's internal `EditorState` object for document and cursor position
3. **UI State:** Active sidebar tab, right panel mode, modal visibility
4. **Persistent State:** LLM configuration and preferences stored in `localStorage`

**Sources:** [apps/frontend/src/app/EditorPage.tsx](), Diagram 2 from high-level overview

### CodeMirror Integration

OpenPrism uses **CodeMirror 6** for the LaTeX editor, with custom extensions for LaTeX-specific functionality.

```mermaid
graph TB
    EditorView["EditorView<br/>Main editor instance"]
    
    EditorView --> EditorState["EditorState"]
    
    EditorState --> Doc["Text.of(lines)<br/>Document content"]
    EditorState --> Extensions["Extensions Array"]
    
    Extensions --> BasicSetup["basicSetup<br/>Standard features"]
    Extensions --> LaTeXLang["LaTeX Language<br/>Syntax highlighting"]
    Extensions --> FoldSvc["Fold Service<br/>Code folding"]
    Extensions --> Completion["Autocompletion<br/>LaTeX commands"]
    Extensions --> GhostText["Ghost Text Field<br/>AI suggestions"]
    Extensions --> KeyBindings["Custom Keybindings<br/>Ctrl+S, Ctrl+Space"]
    
    GhostText --> GhostState["StateField<br/>suggestion: string"]
    GhostText --> GhostWidget["WidgetType<br/>Gray overlay text"]
```

**Key Extensions:**

| Extension | Purpose | Location |
|-----------|---------|----------|
| LaTeX Language | Syntax highlighting and parsing | [apps/frontend/src/latex/latex-lang.ts]() |
| Fold Service | Section/environment folding | [apps/frontend/src/latex/fold.ts]() |
| Completion Source | LaTeX command autocompletion | [apps/frontend/src/latex/completion.ts]() |
| Ghost Text Field | Display AI inline suggestions | [apps/frontend/src/latex/ghost-text.ts]() |

**Sources:** [apps/frontend/src/app/EditorPage.tsx](), [apps/frontend/src/latex/]()

---

## Backend Architecture

The backend is a **Fastify server** organized into route handlers, service layers, and utility modules.

### Route Organization

```mermaid
graph TB
    FastifyApp["Fastify App<br/>(apps/backend/src/index.js)"]
    
    FastifyApp --> HealthRoute["/api/health<br/>Health check + system info"]
    FastifyApp --> TemplateRoute["/api/templates<br/>Template listing"]
    FastifyApp --> ProjectRoute["/api/projects/*<br/>Project operations"]
    FastifyApp --> CompileRoute["/api/compile<br/>LaTeX compilation"]
    FastifyApp --> AgentRoute["/api/agent/run<br/>AI agent execution"]
    FastifyApp --> PlotRoute["/api/plot/from-table<br/>Chart generation"]
    FastifyApp --> VisionRoute["/api/vision/latex<br/>Image OCR"]
    FastifyApp --> ArxivRoute["/api/arxiv/*<br/>arXiv integration"]
    FastifyApp --> LLMRoute["/api/llm<br/>Direct LLM calls"]
    
    ProjectRoute --> ProjectService["ProjectService<br/>services/project.js"]
    CompileRoute --> CompileService["CompileService<br/>services/compile.js"]
    AgentRoute --> LLMService["LLMService<br/>services/llm.js"]
    PlotRoute --> PlotService["PlotService<br/>services/plot.js"]
    VisionRoute --> LLMService
    ArxivRoute --> ArxivService["ArxivService<br/>services/arxiv.js"]
```

**API Endpoints:**

| Endpoint | Method | Purpose | Handler File |
|----------|--------|---------|--------------|
| `/api/projects` | GET | List all projects | [apps/backend/src/routes/projects.js]() |
| `/api/projects` | POST | Create new project | [apps/backend/src/routes/projects.js]() |
| `/api/projects/:id/file` | GET, PUT | Read/write file | [apps/backend/src/routes/projects.js]() |
| `/api/projects/:id/tree` | GET | Get file tree | [apps/backend/src/routes/projects.js]() |
| `/api/compile` | POST | Compile LaTeX | [apps/backend/src/routes/compile.js]() |
| `/api/agent/run` | POST | Execute AI agent | [apps/backend/src/routes/agent.js]() |
| `/api/plot/from-table` | POST | Generate chart | [apps/backend/src/routes/plot.js]() |
| `/api/vision/latex` | POST | Image to LaTeX | [apps/backend/src/routes/vision.js]() |
| `/api/arxiv/search` | POST | Search arXiv | [apps/backend/src/routes/arxiv.js]() |

**Sources:** [apps/backend/src/index.js](), [apps/backend/src/routes/]()

### Service Layer Design

The service layer encapsulates business logic and external integrations, following a **dependency injection pattern** where configuration is passed as parameters.

```mermaid
graph TB
    subgraph Services["Service Layer<br/>(apps/backend/src/services)"]
        LLMSvc["LLMService<br/>llm.js"]
        ProjectSvc["ProjectService<br/>project.js"]
        TemplateSvc["TemplateService<br/>template.js"]
        CompileSvc["CompileService<br/>compile.js"]
        PlotSvc["PlotService<br/>plot.js"]
        ArxivSvc["ArxivService<br/>arxiv.js"]
    end
    
    subgraph Utils["Utility Layer<br/>(apps/backend/src/utils)"]
        FSUtils["fs-utils.js<br/>Safe file operations"]
        PathUtils["path-utils.js<br/>Path sanitization"]
        TexUtils["tex-utils.js<br/>LaTeX parsing"]
        I18nUtils["i18n-utils.js<br/>Localization"]
    end
    
    subgraph Config["Configuration"]
        EnvVars[".env file<br/>OPENPRISM_*"]
        Constants["constants.js<br/>Defaults"]
    end
    
    LLMSvc --> EnvVars
    ProjectSvc --> FSUtils
    ProjectSvc --> PathUtils
    CompileSvc --> TexUtils
    CompileSvc --> FSUtils
    TemplateSvc --> FSUtils
    
    ProjectSvc --> Constants
    LLMSvc --> Constants
```

**Service Responsibilities:**

| Service | File | Key Methods | Purpose |
|---------|------|-------------|---------|
| `LLMService` | `llm.js` | `callLLM()`, `resolveLLMConfig()` | Abstract LLM provider, handle OpenAI-compatible API calls |
| `ProjectService` | `project.js` | `createProject()`, `getFileTree()` | Project lifecycle, file operations |
| `TemplateService` | `template.js` | `listTemplates()`, `applyTemplate()` | Template discovery, project initialization |
| `CompileService` | `compile.js` | `compileProject()`, `detectEngine()` | LaTeX compilation, error parsing |
| `PlotService` | `plot.js` | `generatePlot()`, `executePython()` | Python-based chart generation |
| `ArxivService` | `arxiv.js` | `searchPapers()`, `downloadPaper()` | arXiv API integration |

**Sources:** [apps/backend/src/services/](), Diagram 3 from high-level overview

### Configuration Resolution

OpenPrism implements a **multi-layer configuration system** with the following precedence (highest to lowest):

```mermaid
graph TB
    Request["API Request"]
    
    Request --> RuntimeOverride{"Runtime Override<br/>in request body?"}
    RuntimeOverride -->|Yes| UseRuntime["Use request.body.llmConfig"]
    RuntimeOverride -->|No| CheckFrontend{"Frontend Config<br/>in localStorage?"}
    
    CheckFrontend -->|Yes| UseFrontend["Use localStorage config<br/>(sent in request)"]
    CheckFrontend -->|No| CheckEnv{"Backend .env<br/>variables set?"}
    
    CheckEnv -->|Yes| UseEnv["Use process.env.OPENPRISM_*"]
    CheckEnv -->|No| UseDefaults["Use hardcoded defaults"]
    
    UseRuntime --> FinalConfig["Final LLM Config"]
    UseFrontend --> FinalConfig
    UseEnv --> FinalConfig
    UseDefaults --> FinalConfig
```

**Configuration Variables:**

| Variable | Environment | localStorage Key | Default |
|----------|-------------|------------------|---------|
| LLM Endpoint | `OPENPRISM_LLM_ENDPOINT` | `openprism-llm-endpoint` | `https://api.openai.com/v1/chat/completions` |
| API Key | `OPENPRISM_LLM_API_KEY` | `openprism-llm-api-key` | None (required) |
| Model | `OPENPRISM_LLM_MODEL` | `openprism-llm-model` | `gpt-4o-mini` |
| Data Directory | `OPENPRISM_DATA_DIR` | N/A | `./data` |
| Port | `PORT` | N/A | `8787` |

**Sources:** [README.md:332-349](), [apps/frontend/src/api/client.ts:21-25](), Diagram 6 from high-level overview

---

## Data Storage Architecture

OpenPrism uses a **file-system-based storage model** with no database. All data persists in a configurable directory (`OPENPRISM_DATA_DIR`).

### Directory Structure

```
OPENPRISM_DATA_DIR/
├── projects/
│   ├── {projectId}/
│   │   ├── project.json          # Metadata
│   │   ├── .openprism/           # System files
│   │   │   └── fileOrder.json    # Custom file ordering
│   │   ├── main.tex              # LaTeX files
│   │   ├── references.bib
│   │   └── figures/
│   │       └── chart1.png
│   └── {projectId}/
│       └── ...
└── templates/
    ├── acl2023/
    ├── cvpr2024/
    └── neurips2023/
```

### Project Metadata Schema

The `project.json` file stores project-level metadata:

```typescript
interface ProjectMeta {
  id: string;              // Unique identifier (UUID)
  name: string;            // Display name
  createdAt: string;       // ISO 8601 timestamp
  updatedAt: string;       // ISO 8601 timestamp
  tags: string[];          // User-defined tags
  archived: boolean;       // Archive status
  trashed: boolean;        // Soft delete flag
  trashedAt: string | null; // Trash timestamp
}
```

**Sources:** [apps/frontend/src/api/client.ts:1-10](), [README.md:397-413]()

### File Order Management

Custom file ordering in the file tree is stored in `.openprism/fileOrder.json`:

```typescript
interface FileOrderMap {
  [folder: string]: string[];  // folder path -> ordered file names
}
```

Example:
```json
{
  "": ["main.tex", "abstract.tex", "introduction.tex"],
  "sections": ["related-work.tex", "methodology.tex", "results.tex"]
}
```

**Sources:** [apps/frontend/src/api/client.ts:17-19](), [apps/backend/src/routes/projects.js]()

### Template System

Templates are stored in the `templates/` directory and discovered at runtime. Each template contains:

- `manifest.json`: Metadata (name, description, mainFile, category)
- LaTeX source files (`.tex`, `.bib`, `.sty`, `.cls`)
- Optional assets (images, bibliography files)

```typescript
interface TemplateMeta {
  id: string;              // Directory name
  label: string;           // Display name (Chinese)
  mainFile: string;        // Entry point (e.g., "main.tex")
  category: string;        // Category ID
  description: string;     // Description (Chinese)
  descriptionEn: string;   // Description (English)
  tags: string[];          // Search tags
  author: string;          // Template author
  featured: boolean;       // Featured flag
}
```

**Sources:** [apps/frontend/src/api/client.ts:27-37](), [apps/backend/src/services/template.js]()

---

## API Design Patterns

### RESTful Conventions

The API follows REST principles with standard HTTP methods:

| Operation | Method | Pattern | Example |
|-----------|--------|---------|---------|
| List | GET | `/api/{resource}` | `GET /api/projects` |
| Create | POST | `/api/{resource}` | `POST /api/projects` |
| Read | GET | `/api/{resource}/{id}` | `GET /api/projects/abc123/file?path=main.tex` |
| Update | PUT/PATCH | `/api/{resource}/{id}` | `PUT /api/projects/abc123/file` |
| Delete | DELETE | `/api/{resource}/{id}` | `DELETE /api/projects/abc123` |

**Sources:** [apps/backend/src/routes/projects.js]()

### Request/Response Patterns

All API responses follow a consistent structure:

**Success Response:**
```json
{
  "ok": true,
  "data": { ... },
  "metadata": { ... }
}
```

**Error Response:**
```json
{
  "ok": false,
  "error": "Human-readable error message"
}
```

**Example: Agent Execution Response**
```typescript
interface AgentResponse {
  ok: boolean;
  reply: string;          // Conversational response
  suggestion: string;     // Inline suggestion (autocomplete)
  patches?: {             // Structured file changes
    path: string;
    diff: string;         // Unified diff format
    content: string;      // Full new content
  }[];
}
```

**Sources:** [apps/frontend/src/api/client.ts:200-217](), [apps/backend/src/routes/agent.js]()

### Server-Sent Events (SSE)

Long-running operations use **Server-Sent Events** for progress streaming:

```mermaid
sequenceDiagram
    participant Client as "Frontend<br/>importArxivSSE()"
    participant Server as "/api/projects/import-arxiv-sse"
    participant ArxivAPI as "arxiv.org"
    
    Client->>Server: GET with EventSource
    Server->>ArxivAPI: Download .tar.gz
    loop Progress Updates
        Server-->>Client: event: progress<br/>data: {phase, percent}
    end
    ArxivAPI-->>Server: Complete
    Server->>Server: Extract + create project
    Server-->>Client: event: done<br/>data: {project}
    Client->>Client: Navigate to editor
```

**SSE Events:**

| Event Type | Data Schema | Purpose |
|------------|-------------|---------|
| `progress` | `{phase: string, percent: number}` | Progress updates |
| `done` | `{ok: true, project: ProjectMeta}` | Success |
| `error` | `{ok: false, error: string}` | Failure |

**Sources:** [apps/frontend/src/api/client.ts:306-337](), [apps/backend/src/routes/projects.js]()

### API Client Abstraction

The frontend uses a centralized API client with type-safe wrappers:

```typescript
// apps/frontend/src/api/client.ts

// Internal request helper
async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const lang = getLangHeader();
  const res = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'x-lang': lang,
      ...(options?.headers || {})
    }
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// Public API functions
export function listProjects() {
  return request<{ projects: ProjectMeta[] }>('/api/projects');
}

export function createProject(payload: { name: string; template?: string }) {
  return request<ProjectMeta>('/api/projects', {
    method: 'POST',
    body: JSON.stringify(payload)
  });
}
```

**Benefits:**

- Type safety with TypeScript interfaces
- Centralized error handling
- Automatic language header injection
- Consistent response parsing

**Sources:** [apps/frontend/src/api/client.ts:53-88]()

---

## AI Agent Execution Architecture

The AI agent system supports multiple execution modes with different capabilities and guarantees.

### Execution Modes

```mermaid
graph TB
    AgentAPI["/api/agent/run"]
    
    AgentAPI --> ModeSwitch{"mode parameter"}
    
    ModeSwitch -->|"direct"| DirectMode["Direct Mode<br/>Single LLM call"]
    ModeSwitch -->|"tools"| ToolsMode["Tools Mode<br/>Multi-turn with tools"]
    
    DirectMode --> SingleCall["callLLM()<br/>messages array"]
    SingleCall --> DirectResponse["Return response<br/>{reply, suggestion}"]
    
    ToolsMode --> InitCall["Initial callLLM()<br/>with tools definition"]
    InitCall --> ToolCheck{"Tool calls<br/>requested?"}
    ToolCheck -->|Yes| ExecuteTools["Execute tool functions<br/>readFile(), writeFile()"]
    ExecuteTools --> FollowupCall["callLLM() with results"]
    FollowupCall --> ToolCheck
    ToolCheck -->|No| ToolsResponse["Return response<br/>{reply, patches}"]
```

**Mode Comparison:**

| Mode | Turns | Tool Access | Use Case | Output |
|------|-------|-------------|----------|--------|
| `direct` | 1 | No | Chat Q&A, autocomplete, polish | `reply` or `suggestion` |
| `tools` | 1+ | Yes | Multi-file edits, complex refactoring | `reply` + `patches[]` |

**Sources:** [apps/backend/src/routes/agent.js](), [apps/backend/src/services/llm.js](), Diagram 4 from high-level overview

### Context Building

Before executing an agent task, the frontend builds comprehensive context:

```typescript
interface AgentPayload {
  task: string;              // Task type: 'polish', 'rewrite', etc.
  prompt: string;            // User instruction
  selection: string;         // Selected text
  content: string;           // Full file content
  mode: 'direct' | 'tools';
  projectId?: string;        // For file operations
  activePath?: string;       // Current file
  compileLog?: string;       // Recent errors
  llmConfig?: Partial<LLMConfig>;
  interaction?: 'chat' | 'agent';
  history?: { role: string; content: string }[];
}
```

**Context Sources:**

1. **Selection Context:** User-highlighted text
2. **File Context:** Full content of active file
3. **Project Context:** File tree and related files (in tools mode)
4. **Compilation Context:** Recent compile errors for diagnosis
5. **Conversation History:** Previous chat messages

**Sources:** [apps/frontend/src/api/client.ts:200-217](), [apps/backend/src/routes/agent.js]()

### Tool Definitions

In `tools` mode, the LLM has access to file operation tools:

```typescript
const tools = [
  {
    type: 'function',
    function: {
      name: 'readFile',
      description: 'Read content of a file in the project',
      parameters: {
        type: 'object',
        properties: {
          path: { type: 'string', description: 'File path relative to project root' }
        },
        required: ['path']
      }
    }
  },
  {
    type: 'function',
    function: {
      name: 'writeFile',
      description: 'Write content to a file in the project',
      parameters: {
        type: 'object',
        properties: {
          path: { type: 'string', description: 'File path' },
          content: { type: 'string', description: 'New file content' }
        },
        required: ['path', 'content']
      }
    }
  }
];
```

The agent service executes these tools by performing actual file operations on the project directory.

**Sources:** [apps/backend/src/routes/agent.js]()

---

## Deployment Architecture

### Development Mode

In development, frontend and backend run as separate processes:

```mermaid
graph LR
    Dev["npm run dev"]
    
    Dev --> Frontend["Frontend Process<br/>npm run dev:frontend"]
    Dev --> Backend["Backend Process<br/>npm run dev:backend"]
    
    Frontend --> Vite["Vite Dev Server<br/>localhost:5173"]
    Backend --> Fastify["Fastify Server<br/>localhost:8787"]
    
    Vite -->|"Proxy /api/*"| Fastify
```

**Configuration:**

- Frontend Vite proxy configuration routes `/api/*` to backend port
- Hot Module Replacement (HMR) enabled for frontend
- Backend auto-restart on file changes via nodemon

**Sources:** [README.md:262-279](), [package.json scripts]()

### Production Mode

In production, a single Fastify server serves both static assets and API:

```mermaid
graph TB
    Build["npm run build"]
    
    Build --> BuildFrontend["Build Frontend<br/>npm run build:frontend"]
    Build --> BuildBackend["Build Backend<br/>npm run build:backend"]
    
    BuildFrontend --> StaticAssets["Static Assets<br/>apps/frontend/dist/"]
    BuildBackend --> ServerBundle["Server Bundle<br/>apps/backend/dist/"]
    
    Start["npm start"]
    Start --> FastifyServer["Unified Fastify Server"]
    
    FastifyServer --> ServeStatic["Serve Static<br/>@fastify/static"]
    FastifyServer --> APIRoutes["API Routes<br/>/api/*"]
    
    ServeStatic --> StaticAssets
    APIRoutes --> ServerBundle
```

**Unified Server Benefits:**

- Single port (8787 by default)
- Simplified deployment
- No CORS configuration needed
- Easier process management with PM2

**PM2 Configuration:**

```bash
pm2 start npm --name "openprism" -- start
pm2 save
pm2 startup
```

**Sources:** [README.md:280-328](), [apps/backend/src/index.js](), Diagram 6 from high-level overview

---

## Cross-Cutting Concerns

### Error Handling

The system implements consistent error handling across all layers:

**Frontend:**
- API client throws errors with descriptive messages
- Components catch errors and display user-friendly notifications
- Compilation errors parsed and displayed with file/line navigation

**Backend:**
- Route handlers catch exceptions and return `{ok: false, error: string}`
- Service layer throws descriptive errors
- External process failures captured and logged

**Sources:** [apps/frontend/src/api/client.ts:62-77](), [apps/backend/src/routes/]()

### Internationalization

Both frontend and backend support Chinese and English:

**Frontend:**
- i18next library with language detection
- Translation files: `locales/zh-CN.json`, `locales/en-US.json`
- Language switcher in top navigation
- Language stored in localStorage

**Backend:**
- Language header (`x-lang`) read from requests
- i18n utility provides localized error messages
- Template descriptions localized

**Language Header Flow:**

```mermaid
graph LR
    LocalStorage["localStorage<br/>'openprism-lang'"]
    APIClient["API Client<br/>getLangHeader()"]
    Request["HTTP Request<br/>x-lang: zh-CN"]
    Backend["Backend<br/>req.headers['x-lang']"]
    I18nUtil["i18n-utils.js<br/>t(key, lang)"]
    
    LocalStorage --> APIClient
    APIClient --> Request
    Request --> Backend
    Backend --> I18nUtil
```

**Sources:** [apps/frontend/src/api/client.ts:54-60](), [apps/backend/src/utils/i18n-utils.js](), [README.md:98]()

### Security Considerations

**Path Traversal Prevention:**
- `path-utils.js` sanitizes all file paths
- Paths validated to be within project directory
- Symbolic links rejected

**API Authentication:**
- Currently no authentication (local-first design)
- LLM API keys stored client-side in localStorage
- Backend only proxies LLM requests

**Sandboxing:**
- LaTeX compilation runs in temporary directories
- Python plotting executes in isolated process
- No arbitrary code execution from user input (except LaTeX itself)

**Sources:** [apps/backend/src/utils/path-utils.js](), [apps/backend/src/services/compile.js](), [apps/backend/src/services/plot.js]()

---

This architecture document provides a comprehensive technical overview of OpenPrism's system design. For implementation details of specific features, see the [Features](#6) section. For development workflows and contribution guidelines, see the [Development Guide](#7).

---

