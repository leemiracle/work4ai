<!-- source: DeepWiki mcp.deepwiki.com · repo ruc-datalab/DeepAnalyze · page 5 Frontend Interfaces · fetched 2026-10-26 -->

# Frontend Interfaces

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/wechat.jpg](assets/wechat.jpg)
- [docs/DeepAnalyze_API_Key_Usage_Guide.md](docs/DeepAnalyze_API_Key_Usage_Guide.md)
- [docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md](docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md)
- [example/README.md](example/README.md)
- [quantize.py](quantize.py)
- [requirements.txt](requirements.txt)

</details>



## Purpose and Scope

This document covers the five distinct frontend interfaces provided by DeepAnalyze for user interaction. Each interface targets different use cases and user preferences while maintaining consistent functionality through shared backend services. This page provides technical details about the architecture, key components, and deployment of each frontend.

For backend API architecture details, see [API Server Architecture](#6). For usage guides and examples, see [Using DeepAnalyze](#7).

## Overview of Available Interfaces

DeepAnalyze provides a "multiple frontends, unified backend" architecture. All interfaces support streaming responses, file uploads, workspace management, and multi-turn conversations, but differ in deployment complexity and feature richness.

| Interface | Technology Stack | Target Users | Key Features | Requires Browser |
|-----------|-----------------|--------------|--------------|------------------|
| **WebUI** | React + TypeScript | Data scientists, analysts | Three-panel layout, Monaco editor, file tree, structured output | Yes |
| **CLI** | Python + Rich library | Terminal users, automation | Bilingual support, file commands, progress bars | No |
| **JupyterUI** | MCP + fastmcp | Jupyter users | Native notebook cells, markdown/code conversion | Yes (Jupyter) |
| **Gradio** | Gradio framework | Non-technical users | Simplified interface, ZIP support, easy deployment | Yes |
| **Python SDK** | Pure Python | Developers, embedding | Direct vLLM access, programmatic control, no API server | No |

**Sources:** [README.md:21-113](), [docs/DeepAnalyze_API_Key_Usage_Guide.md:1-192]()

## Frontend-Backend Architecture

```mermaid
graph TB
    subgraph "Frontend_Layer"
        WebUI["WebUI<br/>(React SPA)<br/>Port 4000"]
        CLI_EN["api_cli.py<br/>(English CLI)"]
        CLI_ZH["api_cli_ZH.py<br/>(中文 CLI)"]
        Jupyter["jupyter-mcp-server<br/>(JupyterUI)"]
        Gradio_EN["app.py<br/>(English Gradio)"]
        Gradio_ZH["app_ZH.py<br/>(中文 Gradio)"]
        SDK["DeepAnalyzeVLLM<br/>(Python SDK)"]
    end
    
    subgraph "Backend_Services"
        API["FastAPI Server<br/>localhost:8200<br/>/v1/chat/completions<br/>/v1/files"]
        FileServer["HTTP File Server<br/>localhost:8100<br/>Serves workspace files"]
        vLLM["vLLM Engine<br/>localhost:8000<br/>OpenAI-compatible API"]
    end
    
    subgraph "Storage"
        Workspace["workspace/<br/>thread-based directories<br/>generated/ subdirectories"]
    end
    
    WebUI --> API
    WebUI --> FileServer
    CLI_EN --> API
    CLI_EN --> FileServer
    CLI_ZH --> API
    CLI_ZH --> FileServer
    Jupyter --> API
    Gradio_EN --> API
    Gradio_EN --> FileServer
    Gradio_ZH --> API
    Gradio_ZH --> FileServer
    
    SDK -.Direct Connection.-> vLLM
    
    API --> vLLM
    API --> Workspace
    FileServer --> Workspace
    
    style SDK fill:#f9f,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5
```

**Key Architectural Points:**

- **Standard Path**: WebUI, CLI, Jupyter, and Gradio interfaces communicate with the FastAPI server (port 8200) for chat completions and the HTTP file server (port 8100) for downloading generated artifacts
- **Direct Path**: The Python SDK (`DeepAnalyzeVLLM`) bypasses the API server entirely and communicates directly with vLLM (port 8000), providing lower latency and full control over generation parameters
- **Shared Backend**: All standard-path frontends benefit from the same workspace isolation, file tracking, and code execution capabilities provided by the API server
- **Port Configuration**: Ports 4000 (WebUI), 8080 (Gradio), 8100 (file server), 8200 (API server), and 8000 (vLLM) are the default values and can be reconfigured

**Sources:** [README.md:56-111](), [docs/DeepAnalyze_API_Key_Usage_Guide.md:173-177]()

## Interface Comparison Matrix

```mermaid
graph LR
    subgraph "Feature_Support_Matrix"
        direction TB
        
        Features["<b>Features</b><br/>• Streaming<br/>• File Upload<br/>• Multi-turn<br/>• Workspaces<br/>• Code Exec<br/>• File Download"]
        
        WebUI_F["<b>WebUI</b><br/>✓ All features<br/>✓ Three panels<br/>✓ Monaco editor<br/>✓ File tree<br/>✓ Step navigator"]
        
        CLI_F["<b>CLI</b><br/>✓ All features<br/>✓ File commands<br/>✓ Progress bars<br/>✓ Bilingual<br/>✓ History"]
        
        Jupyter_F["<b>JupyterUI</b><br/>✓ All features<br/>✓ Cell conversion<br/>✓ Native output<br/>✓ MCP tools"]
        
        Gradio_F["<b>Gradio</b><br/>✓ All features<br/>✓ ZIP support<br/>✓ Preset prompts<br/>✓ Simplified UI"]
        
        SDK_F["<b>Python SDK</b><br/>✓ Direct vLLM<br/>✓ Full trace<br/>✗ No API server<br/>✗ No UI"]
    end
    
    Features --> WebUI_F
    Features --> CLI_F
    Features --> Jupyter_F
    Features --> Gradio_F
    Features --> SDK_F
```

**Deployment Complexity:**
- **Simplest**: Gradio (single command: `python app.py`)
- **Simple**: CLI (requires API server running: `python start_server.py` + `python api_cli.py`)
- **Moderate**: WebUI (requires npm install, API server, and React dev server)
- **Moderate**: JupyterUI (requires Jupyter Lab + MCP server configuration)
- **Advanced**: Python SDK (requires understanding of workspace management and direct vLLM interaction)

**Sources:** [README.md:56-111]()

## Common Communication Patterns

All standard-path frontends follow similar interaction patterns with the backend:

### File Upload Flow

```mermaid
sequenceDiagram
    participant Frontend as Any Frontend
    participant API as API Server :8200
    participant Storage as storage.py
    participant FS as File System
    
    Frontend->>API: POST /v1/files<br/>multipart/form-data
    API->>Storage: create_file(filename, content)
    Storage->>Storage: Generate file_id (uuid)
    Storage->>FS: Save to FILE_STORAGE_DIR
    Storage-->>API: FileObject{id, filename, size}
    API-->>Frontend: JSON response with file_id
```

**Sources:** [README.md:292-310]()

### Chat Completion Flow

```mermaid
sequenceDiagram
    participant Frontend as Any Frontend
    participant API as API Server :8200
    participant vLLM as vLLM :8000
    participant FileServer as File Server :8100
    
    Frontend->>API: POST /v1/chat/completions<br/>{messages, file_ids, thread_id}
    API->>API: prepare_vllm_messages()<br/>Inject file context
    API->>vLLM: Stream request
    
    loop Streaming Response
        vLLM-->>API: Delta chunks
        API->>API: Detect <Code> tags<br/>Execute code<br/>Track files
        API-->>Frontend: Stream chunks with<br/><Execute>, <File> tags
    end
    
    API-->>Frontend: Final chunk with thread_id
    Frontend->>FileServer: GET /thread-{id}/generated/file.png
    FileServer-->>Frontend: Generated artifact
```

**Sources:** [README.md:292-310]()

## Detailed Interface Specifications

### Connection Endpoints

All standard-path frontends use these endpoints:

| Endpoint | Port | Purpose | Used By |
|----------|------|---------|---------|
| `/v1/files` | 8200 | File upload, list, delete | All except SDK |
| `/v1/chat/completions` | 8200 | Main chat interface | All except SDK |
| `/v1/models` | 8200 | List available models | All except SDK |
| `/thread-{id}/generated/{file}` | 8100 | Download generated files | All except SDK |
| `/v1/completions` | 8000 | Direct vLLM inference | SDK only |
| `/health` | 8200 | API health check | All |

**Sources:** [README.md:292-310](), [docs/DeepAnalyze_API_Key_Usage_Guide.md:173-177]()

### Session Management

All interfaces except the Python SDK use thread-based session management:

| Concept | Description | Storage Location |
|---------|-------------|------------------|
| `thread_id` | Unique session identifier (UUID) | In-memory storage + filesystem |
| `session_id` | Legacy alternative to thread_id | Gradio interfaces |
| Workspace | Per-thread directory | `workspace/thread-{id}/` |
| Generated Files | Artifacts from code execution | `workspace/thread-{id}/generated/` |

**Sources:** [README.md:56-111]()

## Language Support

Three interfaces provide bilingual support (English and Chinese):

```mermaid
graph TB
    subgraph "English_Interfaces"
        CLI_EN["api_cli.py<br/>demo/cli/"]
        Gradio_EN["app.py<br/>demo/deepanalyze_general/"]
        WebUI_EN["WebUI<br/>demo/chat/frontend/<br/>(English default)"]
    end
    
    subgraph "Chinese_Interfaces"
        CLI_ZH["api_cli_ZH.py<br/>demo/cli/"]
        Gradio_ZH["app_ZH.py<br/>demo/deepanalyze_general/"]
    end
    
    subgraph "Language_Agnostic"
        Jupyter["JupyterUI<br/>demo/jupyter/"]
        SDK["Python SDK<br/>deepanalyze.py"]
    end
```

**Implementation Notes:**
- Language selection is at the file level (separate scripts for EN/ZH)
- WebUI supports both languages but defaults to English in the UI
- JupyterUI and SDK are language-agnostic, relying on the model's multilingual capabilities
- All interfaces can process prompts in any language the model supports

**Sources:** [README.md:96-104]()

## Startup and Deployment

### Startup Sequences by Interface

| Interface | Required Services | Startup Command(s) | Access URL |
|-----------|------------------|-------------------|------------|
| WebUI | vLLM + API + React | `vllm serve DeepAnalyze-8B`<br/>`cd demo/chat && bash start.sh` | http://localhost:4000 |
| CLI | vLLM + API | `python API/start_server.py`<br/>`python demo/cli/api_cli.py` | Terminal |
| JupyterUI | vLLM + API + Jupyter | See [demo/jupyter]() | Jupyter Lab |
| Gradio | vLLM + API (embedded) | `python demo/deepanalyze_general/app.py` | http://localhost:8080 |
| Python SDK | vLLM only | `vllm serve DeepAnalyze-8B` | Programmatic |

**Sources:** [README.md:56-111](), [docs/DeepAnalyze_API_Key_Usage_Guide.md:164-178]()

### Gradio Embedded API Pattern

Gradio applications use a unique deployment pattern where they start their own API server:

```mermaid
graph TB
    User["User Browser"]
    
    subgraph "Gradio_Application_Process"
        Gradio["gradio.Interface<br/>app.py or app_ZH.py<br/>Port 8080"]
        
        subgraph "Embedded_Services"
            API_Thread["API Server Thread<br/>uvicorn in subprocess<br/>Port 8200"]
            File_Thread["File Server Thread<br/>Port 8100"]
        end
    end
    
    vLLM["vLLM Server<br/>Port 8000"]
    
    User --> Gradio
    Gradio --> API_Thread
    Gradio --> File_Thread
    API_Thread --> vLLM
```

**Key Points:**
- Gradio scripts launch API and file servers as background threads/subprocesses
- This provides "one-command deployment" without manual service management
- The embedded servers use the same code from `API/` directory
- Health checks ensure all services are ready before exposing Gradio UI

**Sources:** [docs/DeepAnalyze_API_Key_Usage_Guide.md:171-178]()

## File Format Support

All interfaces support the same file formats through the unified API backend:

| Category | Formats | Extensions |
|----------|---------|------------|
| Structured Data | CSV, Excel, Parquet | `.csv`, `.xlsx`, `.xls`, `.parquet` |
| Semi-structured | JSON, XML, YAML | `.json`, `.xml`, `.yaml`, `.yml` |
| Unstructured | Text, Markdown, Logs | `.txt`, `.md`, `.log` |
| Code | Python, SQL, R | `.py`, `.sql`, `.r` |
| Documents | PDF | `.pdf` |
| Archives | ZIP | `.zip` (auto-extracted) |
| Images | PNG, JPG, SVG | `.png`, `.jpg`, `.jpeg`, `.svg` |

**ZIP Archive Handling:**
- All interfaces automatically extract ZIP files
- Only supported formats within the archive are processed
- Nested directories are flattened
- Original ZIP structure is not preserved in workspace

**Sources:** [docs/DeepAnalyze_API_Key_Usage_Guide.md:185-186](), [docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md:110-112]()

## Feature Comparison: Standard Frontends vs Python SDK

The Python SDK has a fundamentally different architecture:

| Feature | Standard Frontends | Python SDK |
|---------|-------------------|------------|
| **Connection** | API Server (port 8200) | Direct vLLM (port 8000) |
| **Streaming** | Server-sent events | Full response at once |
| **Code Execution** | Automatic (API handles) | Manual (user manages) |
| **File Tracking** | Automatic (WorkspaceTracker) | Manual (user manages) |
| **Workspace** | Managed by API server | User-specified directory |
| **Thread Management** | Automatic (thread_id) | Not supported |
| **Output** | Parsed sections (<Analyze>, <Code>) | Raw reasoning trace |
| **Use Case** | Interactive analysis | Batch processing, embedding |

**Sources:** [README.md:236-262]()

### Python SDK Return Format

The SDK returns a dictionary with the complete reasoning trace:

```python
{
    "reasoning": str,  # Full model output including <Analyze>, <Code>, <Execute> tags
    "answer": str,     # Extracted final answer
}
```

This raw format requires the caller to parse action tags and manage code execution manually, providing maximum control but requiring more implementation effort.

**Sources:** [README.md:260-261]()

## Next Steps

For detailed documentation on each specific interface:
- WebUI technical details: see [WebUI](#5.1)
- CLI usage and commands: see [Command Line Interface](#5.2)
- Jupyter integration: see [JupyterUI](#5.3)
- Gradio deployment: see [Gradio Apps](#5.4)
- SDK programming guide: see [Python SDK](#5.5)

For backend services that all frontends depend on:
- API endpoint specifications: see [Chat Completions API](#6.6)
- File management: see [File Management API](#6.7)
- Workspace persistence: see [Workspace and File Tracking](#6.6.2)

For practical usage examples:
- First-time setup: see [Quick Start Guide](#7.1)
- File operations: see [File Upload and Management](#7.3)
- Multi-turn workflows: see [Multi-turn Conversations](#7.4)

**Sources:** [README.md:1-403]()

---

