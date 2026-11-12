<!-- source: DeepWiki mcp.deepwiki.com · repo ruc-datalab/DeepAnalyze · page 6 API Server Architecture · fetched 2026-10-26 -->

# API Server Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [API/chat_api.py](API/chat_api.py)
- [API/config.py](API/config.py)
- [API/example/exampleOpenAI.py](API/example/exampleOpenAI.py)
- [API/example/exampleRequest.py](API/example/exampleRequest.py)
- [API/main.py](API/main.py)
- [API/models.py](API/models.py)
- [API/utils.py](API/utils.py)

</details>



## Purpose and Scope

This page provides a high-level architectural overview of the DeepAnalyze API Server, including its multi-port design, core components, and how they interact to deliver OpenAI-compatible data analysis capabilities. 

For detailed information about specific components:
- Application initialization and startup process: see [Application Setup and Entry Points](#2.1)
- Configuration parameters and settings: see [Configuration System](#2.2)
- API request/response models: see [Data Models](#2.3)
- In-memory storage implementation: see [Storage Layer](#2.4)
- Code execution and workspace management: see [Utilities and Core Functions](#2.5)

For information about individual API endpoints and their usage: see [API Endpoints](#3)

---

## Multi-Port Architecture

The API server uses a three-port architecture with clear separation of responsibilities:

**Port Configuration:**

| Port | Service | Implementation | Configuration Constant |
|------|---------|----------------|------------------------|
| **8000** | vLLM Inference Server | External process, OpenAI-compatible API | `config.API_BASE = "http://localhost:8000/v1"` |
| **8200** | FastAPI Application | `uvicorn.run(app, host=API_HOST, port=API_PORT)` | `config.API_PORT = 8200` |
| **8100** | HTTP File Server | `socketserver.ThreadingTCPServer` in daemon thread | `config.HTTP_SERVER_PORT = 8100` |

**Service Initialization and Communication:**

```mermaid
graph TB
    subgraph ExternalProcess["External vLLM Process"]
        vLLMServer["vLLM Server<br/>Port 8000<br/>OpenAI-Compatible API"]
    end
    
    subgraph MainPythonProcess["API Server Process"]
        MainThread["Main Thread<br/>uvicorn.run()"]
        HTTPThread["Daemon Thread<br/>start_http_server()"]
        
        subgraph FastAPIApp["FastAPI Application"]
            CreateApp["create_app()<br/>Returns FastAPI instance"]
            Routers["file_api.router<br/>models_api.router<br/>chat_api.router<br/>admin_api.router"]
        end
        
        subgraph HTTPServerImpl["HTTP Server Implementation"]
            ThreadingTCP["socketserver.ThreadingTCPServer"]
            SimpleHTTP["http.server.SimpleHTTPRequestHandler"]
        end
    end
    
    subgraph FileSystem["File System"]
        WorkspaceBase["WORKSPACE_BASE_DIR = 'workspace'"]
        ThreadDirs["workspace/thread-{id}/<br/>Per-conversation directories"]
        GeneratedDirs["workspace/thread-{id}/generated/<br/>Artifacts directory"]
        FilesDir["workspace/_files/<br/>Uploaded files"]
    end
    
    subgraph Clients["HTTP Clients"]
        OpenAIClient["openai.OpenAI<br/>base_url=API_BASE"]
        HTTPRequests["requests / fetch / curl"]
    end
    
    MainThread -->|"Lines 75-76"| HTTPThread
    MainThread -->|"Line 79"| CreateApp
    CreateApp -->|"Lines 45-48"| Routers
    HTTPThread --> ThreadingTCP
    ThreadingTCP --> SimpleHTTP
    
    Clients -->|"POST /v1/chat/completions"| Routers
    Routers -->|"vllm_client.chat.completions.create()"| vLLMServer
    Routers -->|"os.makedirs() / shutil.copy2()"| WorkspaceBase
    SimpleHTTP -->|"Serves from directory"| WorkspaceBase
    Clients -.->|"GET /{thread_id}/generated/{file}"| SimpleHTTP
    
    style vLLMServer fill:#f5f5f5
    style CreateApp fill:#f5f5f5
    style ThreadingTCP fill:#f5f5f5
```

**Client Initialization for vLLM Communication:**

The API server communicates with vLLM using OpenAI client instances initialized in [API/chat_api.py:36-38]():

```python
vllm_client = openai.OpenAI(base_url=API_BASE, api_key="dummy")
vllm_client_async = openai.AsyncOpenAI(base_url=API_BASE, api_key="dummy")
```

Sources: [API/main.py:62-83](), [API/config.py:1-44](), [API/chat_api.py:36-38](), [API/utils.py:494-510]()

---

## Application Structure

The FastAPI application is initialized in [API/main.py:26-59]() through the `create_app()` function, which configures middleware and registers routers.

**Application Initialization Flow:**

```mermaid
graph TB
    subgraph EntryPoint["Entry Point"]
        MainFunc["main.py::main()<br/>Lines 62-83"]
    end
    
    subgraph Initialization["Initialization Sequence"]
        PrintBanner["Print startup banner<br/>Lines 64-72"]
        StartHTTP["threading.Thread(target=start_http_server)<br/>Line 75-76"]
        CreateAppCall["app = create_app()<br/>Line 79"]
        UvicornRun["uvicorn.run(app, host, port)<br/>Line 82"]
    end
    
    subgraph CreateAppFunc["create_app() Function"]
        FastAPIInit["FastAPI(title=API_TITLE, version=API_VERSION)<br/>Line 28"]
        AddCORS["app.add_middleware(CORSMiddleware)<br/>Lines 31-37"]
        IncludeRouters["app.include_router(file_router)<br/>app.include_router(models_router)<br/>app.include_router(chat_router)<br/>app.include_router(admin_router)<br/>Lines 40-48"]
        RegisterHealth["@app.get('/health')<br/>Lines 51-57"]
    end
    
    MainFunc --> PrintBanner
    PrintBanner --> StartHTTP
    StartHTTP --> CreateAppCall
    CreateAppCall --> FastAPIInit
    FastAPIInit --> AddCORS
    AddCORS --> IncludeRouters
    IncludeRouters --> RegisterHealth
    RegisterHealth --> UvicornRun
    
    style MainFunc fill:#f5f5f5
    style CreateAppCall fill:#f5f5f5
```

**Router and Module Dependencies:**

```mermaid
graph LR
    subgraph APIRouters["API Router Modules"]
        FileAPI["file_api.py<br/>router = APIRouter(prefix='/v1/files')"]
        ModelsAPI["models_api.py<br/>router = APIRouter(prefix='/v1/models')"]
        ChatAPI["chat_api.py<br/>router = APIRouter(prefix='/v1/chat')"]
        AdminAPI["admin_api.py<br/>router = APIRouter(prefix='/v1/admin')"]
    end
    
    subgraph SharedModules["Shared Modules"]
        ConfigMod["config.py<br/>Module-level constants<br/>API_BASE, WORKSPACE_BASE_DIR, etc."]
        ModelsMod["models.py<br/>Pydantic classes<br/>FileObject, ThreadObject, ChatCompletionRequest, etc."]
        StorageMod["storage.py<br/>Storage class<br/>storage = Storage() singleton"]
        UtilsMod["utils.py<br/>Functions<br/>get_thread_workspace(), execute_code_safe_async(), etc."]
    end
    
    subgraph vLLMClient["vLLM Client Objects"]
        SyncClient["chat_api.py:37<br/>vllm_client = openai.OpenAI()"]
        AsyncClient["chat_api.py:38<br/>vllm_client_async = openai.AsyncOpenAI()"]
    end
    
    FileAPI -->|"from storage import storage"| StorageMod
    ChatAPI -->|"from storage import storage"| StorageMod
    AdminAPI -->|"from storage import storage"| StorageMod
    
    ChatAPI -->|"from utils import"| UtilsMod
    FileAPI -->|"from config import"| ConfigMod
    ChatAPI -->|"from config import"| ConfigMod
    
    FileAPI -->|"from models import"| ModelsMod
    ChatAPI -->|"from models import"| ModelsMod
    ModelsAPI -->|"from models import"| ModelsMod
    
    ChatAPI -->|"import openai"| SyncClient
    ChatAPI -->|"import openai"| AsyncClient
    
    style ConfigMod fill:#f5f5f5
    style StorageMod fill:#f5f5f5
    style UtilsMod fill:#f5f5f5
```

Sources: [API/main.py:26-83](), [API/chat_api.py:1-42](), [API/config.py:1-44](), [API/storage.py](), [API/utils.py:1-24]()

---

## Core Components

### Configuration System (config.py)

Module-level constants defined in [API/config.py:1-44]():

**Configuration Constants:**

| Constant | Value | Line | Purpose |
|----------|-------|------|---------|
| `API_BASE` | `"http://localhost:8000/v1"` | 12 | vLLM server endpoint |
| `MODEL_PATH` | `"DeepAnalyze-8B"` | 13 | Model identifier |
| `WORKSPACE_BASE_DIR` | `"workspace"` | 14 | Root directory for all workspaces |
| `HTTP_SERVER_PORT` | `8100` | 15 | File server port |
| `API_HOST` | `"0.0.0.0"` | 19 | FastAPI bind address |
| `API_PORT` | `8200` | 20 | FastAPI listen port |
| `DEFAULT_TEMPERATURE` | `0.4` | 37 | LLM sampling temperature |
| `MAX_NEW_TOKENS` | `32768` | 30 | Maximum tokens per generation |
| `STOP_TOKEN_IDS` | `[151676, 151645]` | 41 | Stop token IDs for DeepAnalyze-8B |
| `CODE_EXECUTION_TIMEOUT` | `120` | 29 | Code execution timeout (seconds) |
| `FILE_STORAGE_DIR` | `workspace/_files` | 33 | Uploaded files directory |
| `CLEANUP_TIMEOUT_HOURS` | `12` | 25 | Thread expiration time |

The `os.environ.setdefault("MPLBACKEND", "Agg")` at line 9 configures matplotlib for headless environments.

Sources: [API/config.py:1-44]()

### Data Models (models.py)

Pydantic models in [API/models.py:1-137]() provide OpenAI API compatibility:

**Key Pydantic Classes:**

```mermaid
graph TB
    subgraph FileModels["File Management Models"]
        FileObject["FileObject<br/>id, filename, bytes, purpose<br/>Lines 10-18"]
        FileDeleteResponse["FileDeleteResponse<br/>id, deleted<br/>Lines 20-25"]
    end
    
    subgraph ThreadModels["Thread Management Models"]
        ThreadObject["ThreadObject<br/>id, created_at, last_accessed_at, metadata<br/>Lines 29-38"]
        MessageObject["MessageObject<br/>id, thread_id, role, content<br/>Lines 40-52"]
    end
    
    subgraph ChatModels["Chat Completion Models"]
        ChatCompletionRequest["ChatCompletionRequest<br/>model, messages, file_ids, temperature, stream<br/>Lines 54-61"]
        ChatCompletionResponse["ChatCompletionResponse<br/>id, object, created, model, choices, generated_files<br/>Lines 76-85"]
        ChatCompletionChoice["ChatCompletionChoice<br/>index, message, finish_reason<br/>Lines 69-74"]
        ChatCompletionChunk["ChatCompletionChunk<br/>For streaming responses<br/>Lines 87-95"]
    end
    
    subgraph AdminModels["Admin Models"]
        ThreadCleanupRequest["ThreadCleanupRequest<br/>timeout_hours<br/>Lines 103-106"]
        ThreadCleanupResponse["ThreadCleanupResponse<br/>status, cleaned_threads<br/>Lines 108-114"]
        ThreadStatsResponse["ThreadStatsResponse<br/>total_threads, recent_threads, etc.<br/>Lines 116-124"]
    end
    
    subgraph OtherModels["Other Models"]
        HealthResponse["HealthResponse<br/>status, timestamp<br/>Lines 97-101"]
        ModelObject["ModelObject<br/>id, object, created, owned_by<br/>Lines 126-132"]
    end
    
    ChatCompletionResponse --> ChatCompletionChoice
    
    style FileObject fill:#f5f5f5
    style ThreadObject fill:#f5f5f5
    style ChatCompletionRequest fill:#f5f5f5
    style ChatCompletionResponse fill:#f5f5f5
```

All models inherit from `pydantic.BaseModel` and use type annotations for automatic validation.

Sources: [API/models.py:1-137]()

### Storage Layer (storage.py)

The `Storage` class provides in-memory state management. Key data structures:

**Storage Class Interface:**

```mermaid
graph TB
    subgraph StorageClass["Storage Class"]
        Init["__init__()<br/>Initializes empty dictionaries and lock"]
        
        subgraph DataStructures["Data Structures"]
            FilesDict["self.files: Dict[str, Dict]<br/>file_id -> {filepath, FileObject}"]
            ThreadsDict["self.threads: Dict[str, ThreadObject]<br/>thread_id -> ThreadObject"]
            MessagesDict["self.messages: Dict[str, List[MessageObject]]<br/>thread_id -> [MessageObject]"]
            Lock["self._lock: threading.Lock<br/>Thread-safe operations"]
        end
        
        subgraph FileMethods["File Methods"]
            CreateFile["create_file(filename, filepath, purpose, size)<br/>Returns FileObject"]
            GetFile["get_file(file_id)<br/>Returns FileObject or None"]
            DeleteFile["delete_file(file_id)<br/>Removes file metadata"]
            ListFiles["list_files(purpose=None)<br/>Returns List[FileObject]"]
        end
        
        subgraph ThreadMethods["Thread Methods"]
            CreateThread["create_thread(metadata=None)<br/>Returns ThreadObject with UUID"]
            GetThread["get_thread(thread_id)<br/>Updates last_accessed_at"]
            ListThreads["list_threads()<br/>Returns List[ThreadObject]"]
            CleanupThreads["cleanup_old_threads(timeout_hours)<br/>Deletes expired threads and workspaces"]
        end
        
        subgraph MessageMethods["Message Methods"]
            AddMessage["add_message(thread_id, role, content, file_ids)<br/>Appends to messages list"]
            GetMessages["get_messages(thread_id)<br/>Returns List[MessageObject]"]
        end
    end
    
    subgraph Singleton["Module-Level Singleton"]
        StorageInstance["storage = Storage()<br/>Global instance used by all routers"]
    end
    
    Init --> FilesDict
    Init --> ThreadsDict
    Init --> MessagesDict
    Init --> Lock
    
    FilesDict -.-> FileMethods
    ThreadsDict -.-> ThreadMethods
    MessagesDict -.-> MessageMethods
    
    StorageClass --> StorageInstance
    
    style StorageInstance fill:#f5f5f5
    style CreateThread fill:#f5f5f5
    style CreateFile fill:#f5f5f5
```

The singleton instance is created at module import and shared across all API endpoints. Thread cleanup deletes both in-memory state and corresponding filesystem directories via `shutil.rmtree()`.

Sources: [API/storage.py]() (referenced in architecture)

### Utilities Layer (utils.py)

The [API/utils.py:1-510]() module provides core functionality for workspace management, code execution, and artifact tracking.

**Key Utility Functions:**

| Function | Lines | Parameters | Returns | Purpose |
|----------|-------|------------|---------|---------|
| `get_thread_workspace()` | 26-30 | `thread_id: str` | `str` | Creates and returns `workspace/{thread_id}/` path |
| `build_download_url()` | 33-39 | `thread_id: str, rel_path: str` | `str` | Constructs URL for file server: `http://localhost:8100/{thread_id}/{rel_path}` |
| `collect_file_info()` | 71-86 | `directory: str` | `str` | Scans directory and returns JSON-formatted file list with sizes |
| `prepare_vllm_messages()` | 91-127 | `messages: List[Dict], workspace_dir: str` | `List[Dict]` | Injects file context into last user message with `# Instruction` and `# Data` headers |
| `execute_code_safe()` | 130-167 | `code_str: str, workspace_dir: str, timeout_sec: int` | `str` | Executes Python code in subprocess with timeout, returns stdout/stderr |
| `execute_code_safe_async()` | 170-219 | Same as above | `str` | Async version using `asyncio.create_subprocess_exec()` |
| `extract_code_from_segment()` | 222-229 | `segment: str` | `Optional[str]` | Extracts Python code from `<Code>...</Code>` tags, handles ```python``` fences |
| `extract_sections_from_history()` | 254-336 | `messages: List[Dict]` | `str` | Builds markdown report from tagged sections (`<Analyze>`, `<Code>`, etc.) |
| `generate_report_from_messages()` | 412-470 | `original_messages, assistant_reply, workspace_dir, thread_id, generated_files_sink` | `str` | Generates timestamped markdown report in `generated/` folder |
| `render_file_block()` | 471-492 | `artifact_paths: List[Path], workspace_dir, thread_id, generated_files_sink` | `str` | Builds file metadata list with download URLs |
| `start_http_server()` | 494-510 | None | None | Starts `socketserver.ThreadingTCPServer` on `HTTP_SERVER_PORT` |

**WorkspaceTracker Class:**

Defined at [API/utils.py:350-409](), this class monitors filesystem changes to detect generated artifacts:

```mermaid
graph TB
    subgraph WorkspaceTrackerClass["WorkspaceTracker Class"]
        InitMethod["__init__(workspace_dir, generated_dir)<br/>Lines 353-357"]
        SnapshotMethod["_snapshot() -> Dict[Path, Tuple[int, int]]<br/>Lines 359-367<br/>Walks directory tree, records (size, mtime_ns) for each file"]
        DiffCollectMethod["diff_and_collect() -> List[Path]<br/>Lines 369-409<br/>Compares before/after snapshots<br/>Copies new/modified files to generated/<br/>Returns artifact paths"]
        
        subgraph StateVars["State Variables"]
            WorkspaceDir["self.workspace_dir: Path<br/>Thread workspace directory"]
            GeneratedDir["self.generated_dir: Path<br/>workspace/{thread_id}/generated/"]
            BeforeState["self.before_state: Dict[Path, Tuple]<br/>Snapshot at initialization"]
        end
    end
    
    InitMethod --> WorkspaceDir
    InitMethod --> GeneratedDir
    InitMethod --> BeforeState
    InitMethod -->|"Calls"| SnapshotMethod
    
    DiffCollectMethod -->|"Calls"| SnapshotMethod
    DiffCollectMethod -->|"Compares with"| BeforeState
    DiffCollectMethod -->|"Uses shutil.copy2()"| GeneratedDir
    
    style DiffCollectMethod fill:#f5f5f5
    style SnapshotMethod fill:#f5f5f5
```

The tracker uses file metadata (size, mtime) to detect changes, then copies artifacts to the `generated/` subdirectory for HTTP serving.

Sources: [API/utils.py:1-510](), [API/utils.py:350-409]()

---

## Request Processing Flow

### Chat Completion Endpoint Handler

The main endpoint is defined at [API/chat_api.py:44-389]() as an async function decorated with `@router.post("/completions")`.

**Request Processing Steps:**

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI as "FastAPI<br/>app instance"
    participant ChatHandler as "chat_completions()<br/>chat_api.py:45-389"
    participant Storage as "storage.py<br/>storage singleton"
    participant Utils as "utils.py functions"
    participant vLLMAsync as "vllm_client_async<br/>openai.AsyncOpenAI()"
    participant Subprocess as "asyncio.create_subprocess_exec()"
    participant Tracker as "WorkspaceTracker instance"
    participant FileServer as "HTTP Server<br/>localhost:8100"
    
    Client->>FastAPI: "POST /v1/chat/completions<br/>{model, messages, file_ids, stream}"
    FastAPI->>ChatHandler: "Route to async handler"
    
    Note over ChatHandler: "Lines 68-87: Thread management"
    ChatHandler->>ChatHandler: "Check messages[-1] for thread_id"
    alt Existing thread_id
        ChatHandler->>Storage: "get_thread(thread_id)"
        Storage-->>ChatHandler: "ThreadObject"
    else New conversation
        ChatHandler->>Storage: "create_thread(metadata={'temporary': True})"
        Storage-->>ChatHandler: "New ThreadObject with UUID"
    end
    
    ChatHandler->>Utils: "get_thread_workspace(thread_id)"
    Utils-->>ChatHandler: "workspace_dir path"
    ChatHandler->>ChatHandler: "os.makedirs(generated_dir)"
    
    Note over ChatHandler: "Lines 90-114: File handling"
    loop For each file_id
        ChatHandler->>Storage: "get_file(file_id)"
        Storage-->>ChatHandler: "FileObject with filepath"
        ChatHandler->>ChatHandler: "shutil.copy2(src, workspace_dir)"
    end
    
    Note over ChatHandler: "Lines 117-119: Prepare messages"
    ChatHandler->>Utils: "prepare_vllm_messages(messages, workspace_dir)"
    Utils->>Utils: "collect_file_info(workspace_dir)"
    Utils-->>ChatHandler: "vllm_messages with injected context"
    
    Note over ChatHandler: "Lines 126-277: Streaming loop"
    ChatHandler->>Tracker: "WorkspaceTracker(workspace_dir, generated_dir)"
    
    loop Until finished or </Answer>
        ChatHandler->>vLLMAsync: "chat.completions.create(stream=True, extra_body={stop_token_ids, max_new_tokens})"
        
        loop For each chunk
            vLLMAsync-->>ChatHandler: "chunk.choices[0].delta.content"
            ChatHandler->>Client: "yield SSE chunk"
            
            alt Contains </Code>
                Note over ChatHandler: "Lines 196-226: Code execution"
                ChatHandler->>Utils: "extract_code_from_segment(cur_res)"
                Utils-->>ChatHandler: "code_str"
                ChatHandler->>ChatHandler: "code_str = Chinese_matplot_str + code_str"
                ChatHandler->>Utils: "execute_code_safe_async(code_str, workspace_dir)"
                Utils->>Subprocess: "sys.executable temp.py with timeout"
                Subprocess-->>Utils: "stdout + stderr"
                Utils-->>ChatHandler: "exe_output"
                
                ChatHandler->>Tracker: "diff_and_collect()"
                Tracker->>Tracker: "_snapshot() -> after_state"
                Tracker->>Tracker: "Compare with before_state"
                Tracker->>Tracker: "shutil.copy2(artifacts, generated/)"
                Tracker-->>ChatHandler: "artifact_paths: List[Path]"
                
                ChatHandler->>Utils: "render_file_block(artifacts, workspace_dir, thread_id, generated_files)"
                Utils->>Utils: "build_download_url(thread_id, rel_path)"
                Utils-->>ChatHandler: "generated_files list populated"
                
                ChatHandler->>ChatHandler: "Append execute output to vllm_messages"
            end
        end
    end
    
    Note over ChatHandler: "Lines 229-247: Report generation"
    ChatHandler->>Utils: "generate_report_from_messages(messages, assistant_reply, workspace_dir, thread_id, generated_files)"
    Utils->>Utils: "extract_sections_from_history(history_records)"
    Utils->>Utils: "save_markdown_report(md_text, base_name, export_dir)"
    Utils-->>ChatHandler: "report_block with URL"
    
    Note over ChatHandler: "Lines 250-276: Final chunk"
    ChatHandler->>Client: "yield final_chunk with thread_id and generated_files"
    ChatHandler->>Client: "yield 'data: [DONE]'"
    
    Client->>FileServer: "GET /{thread_id}/generated/plot.png"
    FileServer-->>Client: "Binary file content"
```

**Key Code References:**

- Thread resolution: [API/chat_api.py:68-87]()
- File collection and copying: [API/chat_api.py:90-114]()
- Message preparation with file context: [API/chat_api.py:117-119]()
- Streaming loop with code execution: [API/chat_api.py:126-277]()
- Code extraction: [API/utils.py:222-229]()
- Async code execution: [API/utils.py:170-219]()
- Workspace tracking: [API/utils.py:369-409]()
- Report generation: [API/utils.py:412-470]()

Sources: [API/chat_api.py:44-389](), [API/utils.py:170-219](), [API/utils.py:222-229](), [API/utils.py:369-409](), [API/utils.py:412-470]()

### Code Execution Safety Mechanisms

Code execution in [API/utils.py:170-219]() implements multiple safety layers:

**Execution Isolation:**

1. **Temporary File Creation**: `tempfile.mkstemp(suffix=".py", dir=exec_cwd)` at line 178
2. **Subprocess Isolation**: `asyncio.create_subprocess_exec(sys.executable, tmp_path)` at lines 189-195
3. **Environment Configuration**: 
   - `MPLBACKEND=Agg` for headless matplotlib (line 184)
   - `QT_QPA_PLATFORM=offscreen` for Qt applications (line 185)
   - `DISPLAY` removed to prevent X11 usage (line 186)
4. **Working Directory**: `cwd=exec_cwd` restricts file access to thread workspace (line 191)
5. **Timeout Control**: `asyncio.wait_for(process.communicate(), timeout=timeout_sec)` at lines 198-201
6. **Cleanup**: Temporary file deleted in `finally` block (lines 215-219)

Sources: [API/utils.py:170-219]()

---

## Application Lifecycle

**Startup Sequence:**

```mermaid
graph TB
    Start["start_server.py or<br/>python -m API"]
    InitModule["__init__.py::main()"]
    MainModule["main.py::main()"]
    CreateApp["main.py::create_app()"]
    HTTPThread["utils.py::start_http_server()<br/>Daemon thread"]
    UvicornRun["uvicorn.run(app)<br/>Blocking call"]
    
    Start --> InitModule
    InitModule --> MainModule
    MainModule --> HTTPThread
    MainModule --> CreateApp
    CreateApp --> UvicornRun
    
    HTTPThread -.->|"Runs concurrently"| UvicornRun
    
    style HTTPThread fill:#f9f9f9
    style UvicornRun fill:#f9f9f9
```

**Key Startup Steps (main.py):**

1. **Line 64-72**: Print startup banner with service URLs and endpoints
2. **Line 75-76**: Start HTTP file server in daemon thread via `start_http_server()`
3. **Line 79**: Create FastAPI app via `create_app()`
4. **Line 82**: Start uvicorn server with configured host and port

The daemon thread for the HTTP server ensures it terminates when the main process exits.

Sources: [API/main.py:62-83]()

---

## OpenAI Client Integration

The API server uses the official OpenAI Python library to communicate with the vLLM server, treating it as an OpenAI-compatible endpoint.

**Client Initialization:**

At [API/chat_api.py:36-38]():

```python
vllm_client = openai.OpenAI(base_url=API_BASE, api_key="dummy")
vllm_client_async = openai.AsyncOpenAI(base_url=API_BASE, api_key="dummy")
```

- `API_BASE = "http://localhost:8000/v1"` from [API/config.py:12]()
- Both synchronous and asynchronous clients initialized
- API key is "dummy" since vLLM doesn't require authentication in local deployment

**Streaming Chat Completion Call:**

At [API/chat_api.py:133-143]():

```python
response = await vllm_client_async.chat.completions.create(
    model=model,
    messages=vllm_messages,
    temperature=temperature,
    stream=True,
    extra_body={
        "add_generation_prompt": False,
        "stop_token_ids": STOP_TOKEN_IDS,  # [151676, 151645]
        "max_new_tokens": MAX_NEW_TOKENS,   # 32768
    },
)
```

The `extra_body` parameter passes vLLM-specific settings that aren't part of the standard OpenAI API.

Sources: [API/chat_api.py:36-38](), [API/chat_api.py:133-143](), [API/config.py:12]()

## CORS Configuration

Configured at [API/main.py:31-37]() to allow cross-origin requests:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Accept all origins
    allow_credentials=True,   # Allow cookies/auth headers
    allow_methods=["*"],      # All HTTP methods (GET, POST, DELETE, etc.)
    allow_headers=["*"],      # All request headers
)
```

This enables the API to be accessed from the WebUI (port 4000), Gradio apps (port 8080), or any other web-based client.

Sources: [API/main.py:31-37]()

---

## Health Check Endpoint

Defined at [API/main.py:51-57]() as a simple liveness probe:

```python
@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=int(time.time())
    )
```

**Response Model** ([API/models.py:97-101]()):
- `status: str` - Always "healthy" if server is running
- `timestamp: int` - Unix timestamp of response

This endpoint does not verify vLLM connectivity or file system health; it only confirms the FastAPI process is responsive.

Sources: [API/main.py:51-57](), [API/models.py:97-101]()

---

## Thread and Workspace Management

### Thread Lifecycle

Threads are created dynamically by the chat completion endpoint and tracked in `storage.threads: Dict[str, ThreadObject]`.

**Thread Creation Flow:**

```mermaid
graph TB
    subgraph ClientRequest["Client Request"]
        CheckThreadID["Check messages[-1]['thread_id']<br/>chat_api.py:68-70"]
    end
    
    subgraph ThreadResolution["Thread Resolution Logic"]
        HasThreadID{Has thread_id?}
        GetExisting["storage.get_thread(thread_id)<br/>chat_api.py:74"]
        CreateNew["storage.create_thread(metadata={'temporary': True})<br/>chat_api.py:83"]
    end
    
    subgraph WorkspaceSetup["Workspace Setup"]
        GetWorkspace["get_thread_workspace(thread_id)<br/>Returns 'workspace/{thread_id}/'<br/>utils.py:26-30"]
        CreateDirs["os.makedirs(workspace_dir)<br/>os.makedirs(generated_dir)<br/>chat_api.py:78-79, 85-86"]
    end
    
    subgraph FileOperations["File Operations"]
        CopyFiles["shutil.copy2(file, workspace_dir)<br/>For each file_id<br/>chat_api.py:104-114"]
    end
    
    CheckThreadID --> HasThreadID
    HasThreadID -->|Yes| GetExisting
    HasThreadID -->|No| CreateNew
    GetExisting --> GetWorkspace
    CreateNew --> GetWorkspace
    GetWorkspace --> CreateDirs
    CreateDirs --> CopyFiles
    
    style GetExisting fill:#f5f5f5
    style CreateNew fill:#f5f5f5
    style GetWorkspace fill:#f5f5f5
```

**Thread Directory Structure:**

```
workspace/
├── _files/                          # FILE_STORAGE_DIR (config.py:33)
│   └── {file_id}                    # Uploaded files by ID
└── {thread_id}/                     # Thread workspace (created by get_thread_workspace)
    ├── data.csv                     # Copied input files
    ├── analysis_script.py           # Temporary execution scripts
    └── generated/                   # Generated artifacts
        ├── plot.png                 # Matplotlib outputs
        ├── results.csv              # Data files
        └── Conversation_Report_YYYYMMDD_HHMMSS.md
```

### Thread Cleanup

The `storage.cleanup_old_threads(timeout_hours)` method removes expired threads and their workspaces:

1. Identifies threads with `last_accessed_at` older than timeout
2. Deletes thread from `storage.threads` dictionary
3. Deletes workspace directory with `shutil.rmtree(workspace_path)`
4. Returns count of cleaned threads

This is invoked by the admin API endpoint `POST /v1/admin/cleanup`.

Sources: [API/chat_api.py:68-87](), [API/utils.py:26-30](), [API/config.py:33](), [API/storage.py]() (referenced in architecture)

## Deployment Considerations

### State Management

The `Storage` class in [API/storage.py]() uses in-memory dictionaries protected by `threading.Lock`. This design has implications:

**Single-Instance Deployment:**
- ✅ Simple, no external dependencies
- ✅ Fast access, no network latency
- ⚠️ State lost on restart
- ⚠️ Memory usage grows with active threads

**Multi-Instance Deployment:**
- ❌ Each instance has separate state
- ❌ Thread IDs not shared across instances
- ❌ File uploads visible only to uploading instance
- **Solution**: Requires shared state backend (Redis, PostgreSQL) or sticky sessions

### Workspace Storage

The `WORKSPACE_BASE_DIR = "workspace"` directory must be:
- Writable by the API server process
- Shared across API instances if horizontally scaled (NFS, EFS, S3 with FUSE)
- Accessible by the HTTP file server thread

For production deployments, consider:
- Using absolute paths or environment variables for `WORKSPACE_BASE_DIR`
- Implementing workspace quota limits
- Setting up automated cleanup jobs for expired threads
- Mounting shared storage with proper permissions

Sources: [API/config.py:14](), [API/storage.py]() (referenced in architecture)

---

## Summary

The DeepAnalyze API Server architecture provides:

1. **Separation of Concerns**: Three-port design isolates API logic, file serving, and model inference
2. **OpenAI Compatibility**: Drop-in replacement for OpenAI API with file attachment extensions
3. **Modular Design**: Layered architecture with clear component boundaries
4. **Agentic Capabilities**: Code execution loop integrated into chat completions
5. **Thread Isolation**: Per-conversation workspaces prevent cross-contamination
6. **Type Safety**: Pydantic models for request/response validation

The architecture supports both simple chat interactions and complex autonomous data analysis workflows through its integration of the storage, utilities, and routing layers.

Sources: [API/main.py:1-85](), [API/__init__.py:1-11](), [API/README.md:1-389]()

---

