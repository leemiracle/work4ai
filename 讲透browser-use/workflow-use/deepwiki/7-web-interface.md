<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/workflow-use · page 7 Web Interface · fetched 2026-10-30 -->

# Web Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [workflows/.gitignore](workflows/.gitignore)
- [workflows/backend/api.py](workflows/backend/api.py)
- [workflows/backend/routers.py](workflows/backend/routers.py)
- [workflows/backend/service.py](workflows/backend/service.py)
- [workflows/backend/views.py](workflows/backend/views.py)
- [workflows/workflow_use/storage/__init__.py](workflows/workflow_use/storage/__init__.py)
- [workflows/workflow_use/workflow/prompts.py](workflows/workflow_use/workflow/prompts.py)
- [workflows/workflow_use/workflow/tests/test_extract.py](workflows/workflow_use/workflow/tests/test_extract.py)

</details>



The web interface is a browser-based GUI for workflow management, execution, and monitoring. It consists of two components:

1. **Backend**: FastAPI server ([workflows/backend/api.py:7-19]()) exposing REST endpoints at `http://127.0.0.1:8000`
2. **Frontend**: React/Vite development server ([ui/]()) serving the UI at `http://localhost:5173`

The system provides workflow visualization, execution with real-time log streaming, step editing, and metadata management. All workflow operations are performed through REST API calls, with background task execution for long-running workflows.

For detailed backend API endpoint documentation, see [Backend API](#7.1). For frontend component architecture, see [Frontend Architecture](#7.2).
</thinking>

Sources: [README.md:179-224](), [workflows/backend/api.py:1-25]()
</thinking>

## Launching the GUI

The easiest way to start the web interface is using the built-in CLI command:

```bash
cd workflows
python cli.py launch-gui
```

This command automatically:
- Starts the FastAPI backend server on `http://127.0.0.1:8000`
- Starts the frontend development server on `http://localhost:5173`
- Opens the GUI in the default browser
- Captures server logs to `./tmp/logs` directory

Press `Ctrl+C` to stop both servers. The GUI remains accessible at `http://localhost:5173` while the servers are running.

Sources: [README.md:179-198]()

## Main Features

The web interface provides the following capabilities through REST API endpoints:

| Feature | Endpoint | Method | Description |
|---------|----------|--------|-------------|
| **Workflow List** | `/api/workflows` | GET | List all valid workflow files from `./tmp` directory |
| **Workflow Retrieval** | `/api/workflows/{name}` | GET | Load workflow content (YAML converted to JSON) |
| **Workflow Execution** | `/api/workflows/execute` | POST | Start background workflow execution with `WorkflowExecuteRequest` |
| **Step Editing** | `/api/workflows/update` | POST | Update individual step data via `WorkflowUpdateRequest` |
| **Metadata Editing** | `/api/workflows/update-metadata` | POST | Update workflow name, description, version via `WorkflowMetadataUpdateRequest` |
| **Log Streaming** | `/api/workflows/logs/{task_id}` | GET | Retrieve incremental logs from `./tmp/logs/backend.log` |
| **Status Polling** | `/api/workflows/tasks/{task_id}/status` | GET | Get current task status and results |
| **Execution Control** | `/api/workflows/tasks/{task_id}/cancel` | POST | Cancel running workflow execution |

All request/response models are defined in [workflows/backend/views.py:1-69]() using Pydantic for type validation.

Sources: [workflows/backend/routers.py:19-120](), [workflows/backend/views.py:1-69]()

## System Architecture

The web interface implements a three-tier client-server architecture: a React frontend for user interaction, a FastAPI backend for workflow management, and the core workflow execution engine.

### High-Level Architecture Diagram

```mermaid
graph TB
    subgraph "User Layer"
        Browser["Web Browser<br/>localhost:5173"]
    end
    
    subgraph "Frontend Layer (ui/)"
        ViteServer["Vite Dev Server<br/>Port 5173"]
        ReactApp["React Application<br/>Workflow UI Components"]
        ViteServer --> ReactApp
    end
    
    subgraph "Backend Layer (backend/)"
        FastAPI["FastAPI app<br/>api.py:7<br/>Port 8000"]
        APIRouter["APIRouter<br/>routers.py:19<br/>/api/workflows prefix"]
        WorkflowService["WorkflowService<br/>service.py:35"]
        
        FastAPI --> APIRouter
        APIRouter --> WorkflowService
    end
    
    subgraph "Execution Layer (workflow_use/)"
        WorkflowClass["Workflow<br/>workflow/service.py"]
        WorkflowController["WorkflowController<br/>controller/service.py"]
        BrowserInstance["Browser<br/>browser-use"]
        LLMInstance["ChatBrowserUse<br/>model='bu-latest'"]
        
        WorkflowService --> WorkflowClass
        WorkflowService --> WorkflowController
        WorkflowService --> BrowserInstance
        WorkflowService --> LLMInstance
    end
    
    subgraph "Storage Layer"
        TmpDir["./tmp/<br/>*.workflow.json/yaml"]
        LogDir["./tmp/logs/<br/>backend.log"]
        
        WorkflowService --> TmpDir
        WorkflowService --> LogDir
    end
    
    Browser --> ViteServer
    ReactApp --> FastAPI
```

The architecture separates concerns into four layers: presentation (React/Vite), API routing (FastAPI/APIRouter), service logic (WorkflowService), and workflow execution (Workflow class). `WorkflowService` manages three dictionaries (`active_tasks`, `workflow_tasks`, `cancel_events`) for tracking background task execution state.

Sources: [workflows/backend/api.py:1-25](), [workflows/backend/routers.py:19-120](), [workflows/backend/service.py:35-53]()

### Communication Flow

```mermaid
sequenceDiagram
    participant User
    participant React["React Frontend"]
    participant execute_workflow["routers.py:51<br/>execute_workflow()"]
    participant Service["service.py:164<br/>run_workflow_in_background()"]
    participant WorkflowRun["Workflow.run()"]
    
    User->>React: "Select workflow & input parameters"
    React->>execute_workflow: "POST /api/workflows/execute<br/>WorkflowExecuteRequest"
    execute_workflow->>execute_workflow: "Generate UUID task_id"
    execute_workflow->>execute_workflow: "asyncio.create_task()"
    execute_workflow->>React: "WorkflowExecuteResponse<br/>{task_id, log_position}"
    React->>User: "Show execution started"
    
    Service->>Service: "active_tasks[task_id] = TaskInfo(status='running')"
    Service->>WorkflowRun: "workflow.run(inputs, close_browser_at_end=True)"
    
    loop "Real-time updates"
        React->>execute_workflow: "GET /api/workflows/logs/{task_id}?position=N"
        execute_workflow->>Service: "_read_logs_from_position(position)"
        Service->>Service: "Read from ./tmp/logs/backend.log"
        Service->>execute_workflow: "new_logs, new_position"
        execute_workflow->>React: "WorkflowLogsResponse<br/>{logs, position, status}"
        React->>User: "Display logs & status"
    end
    
    WorkflowRun->>Service: "Return WorkflowResult"
    Service->>Service: "active_tasks[task_id].status = 'completed'"
    React->>execute_workflow: "GET /api/workflows/logs/{task_id}"
    execute_workflow->>React: "status: 'completed', result: [...]"
    React->>User: "Show final results"
```

The frontend polls `/api/workflows/logs/{task_id}` to retrieve incremental logs. The `position` parameter enables efficient log retrieval by seeking to the last read position in `backend.log` and only returning new entries.

Sources: [workflows/backend/routers.py:51-87](), [workflows/backend/routers.py:89-101](), [workflows/backend/service.py:164-220](), [workflows/backend/service.py:63-83]()

## Core Components

The web interface consists of three primary components that work together to provide workflow management capabilities:

### Backend Component Structure

```mermaid
graph LR
    subgraph "backend/ Module"
        API["api.py:7<br/>FastAPI()<br/>CORSMiddleware"]
        Routers["routers.py:19<br/>APIRouter<br/>prefix='/api/workflows'"]
        Service["service.py:35<br/>WorkflowService<br/>__init__()"]
        Views["views.py<br/>Pydantic Models"]
        
        API --> Routers
        Routers --> Service
        Routers --> Views
        Service --> Views
    end
    
    subgraph "workflow_use/ Integration"
        WorkflowLoad["Workflow.load_from_file()"]
        WorkflowRun["Workflow.run()"]
        WorkflowController["WorkflowController"]
        
        Service --> WorkflowLoad
        WorkflowLoad --> WorkflowRun
        Service --> WorkflowController
    end
    
    subgraph "External Dependencies"
        Browser["browser_use.browser.Browser"]
        ChatBrowserUse["browser_use.llm.ChatBrowserUse"]
        
        Service --> Browser
        Service --> ChatBrowserUse
    end
```

| Component | File Path | Key Responsibilities |
|-----------|-----------|---------------------|
| **FastAPI app** | [workflows/backend/api.py:7-19]() | App initialization, CORS middleware (`allow_origins=['http://localhost:5173']`), router registration |
| **APIRouter** | [workflows/backend/routers.py:19-120]() | 8 REST endpoints for workflow CRUD, execution, log streaming, task management |
| **WorkflowService** | [workflows/backend/service.py:35-53]() | Singleton instances (`llm_instance`, `browser_instance`, `controller_instance`), task tracking dictionaries |
| **Pydantic Models** | [workflows/backend/views.py:1-69]() | `WorkflowExecuteRequest`, `WorkflowLogsResponse`, `TaskInfo`, request/response validation |

Sources: [workflows/backend/api.py:1-25](), [workflows/backend/routers.py:1-120](), [workflows/backend/service.py:35-53](), [workflows/backend/views.py:1-69]()

### Task Management Architecture

```mermaid
graph TB
    subgraph "WorkflowService State (service.py:38-53)"
        ActiveTasks["self.active_tasks<br/>Dict[str, TaskInfo]<br/>status, workflow, result, error"]
        WorkflowTasks["self.workflow_tasks<br/>Dict[str, asyncio.Task]<br/>Task references for cancellation"]
        CancelEvents["self.cancel_events<br/>Dict[str, asyncio.Event]<br/>Cancellation signals"]
    end
    
    subgraph "Task Lifecycle (routers.py:51-87)"
        Create["execute_workflow()<br/>task_id = str(uuid.uuid4())"]
        CreateEvent["cancel_event = asyncio.Event()"]
        CreateTask["asyncio.create_task(run_workflow_in_background())"]
        AddCallback["task.add_done_callback(cleanup)"]
        
        Create --> CreateEvent
        CreateEvent --> CreateTask
        CreateTask --> AddCallback
    end
    
    subgraph "Background Execution (service.py:164-230)"
        SetRunning["active_tasks[task_id] = TaskInfo(status='running')"]
        LoadWF["Workflow.load_from_file(path, llm, browser, controller)"]
        RunWF["workflow.run(inputs, close_browser_at_end=True, cancel_event)"]
        FormatResults["Format step_results as list of dicts"]
        SetComplete["active_tasks[task_id].status = 'completed'"]
        
        AddCallback --> SetRunning
        SetRunning --> LoadWF
        LoadWF --> RunWF
        RunWF --> FormatResults
        FormatResults --> SetComplete
    end
    
    Create --> ActiveTasks
    Create --> WorkflowTasks
    CreateEvent --> CancelEvents
    SetRunning --> ActiveTasks
    SetComplete --> ActiveTasks
```

`WorkflowService` maintains three dictionaries initialized in `__init__()`:
- `active_tasks`: `Dict[str, TaskInfo]` - stores execution status (`'running'`/`'completed'`/`'failed'`/`'cancelled'`), results, and errors
- `workflow_tasks`: `Dict[str, asyncio.Task]` - holds task references for cancellation via `task.cancel()`
- `cancel_events`: `Dict[str, asyncio.Event]` - provides graceful shutdown signals checked during `workflow.run()`

Each workflow execution receives a UUID task ID for tracking throughout its lifecycle. Cleanup callbacks automatically remove entries from `workflow_tasks` and `cancel_events` upon task completion.

Sources: [workflows/backend/service.py:38-53](), [workflows/backend/routers.py:64-77](), [workflows/backend/service.py:164-230]()

## File Storage and Workflow Management

The web interface works with workflows stored in the file system, specifically in the `./tmp` directory. Workflows must have the `.workflow.json`, `.workflow.yaml`, or `.workflow.yml` extension to be recognized by the system.

### Storage Structure

```mermaid
graph TB
    subgraph "File System Layout"
        TmpDir["self.tmp_dir = Path('./tmp')<br/>service.py:40"]
        WorkflowFiles["*.workflow.json<br/>*.workflow.yaml<br/>*.workflow.yml"]
        LogsDir["self.log_dir = tmp_dir / 'logs'<br/>service.py:41"]
        BackendLog["backend.log<br/>Timestamped execution logs"]
        
        TmpDir --> WorkflowFiles
        TmpDir --> LogsDir
        LogsDir --> BackendLog
    end
    
    subgraph "WorkflowService Operations (service.py:89-162)"
        List["list_workflows():89<br/>Filter *.workflow.json/yaml/yml"]
        Get["get_workflow(name):99<br/>yaml.safe_load() -> JSON"]
        Update["update_workflow(request):120<br/>Modify steps[node_id]"]
        UpdateMeta["update_workflow_metadata(request):142<br/>Update name/description/version"]
        
        WorkflowFiles --> List
        WorkflowFiles --> Get
        WorkflowFiles --> Update
        WorkflowFiles --> UpdateMeta
    end
    
    subgraph "Log Operations (service.py:55-87)"
        Position["_log_file_position():55<br/>Return file size"]
        Read["_read_logs_from_position(pos):63<br/>Seek + read new lines"]
        Write["_write_log(file, msg):85<br/>Async append"]
        
        BackendLog --> Position
        BackendLog --> Read
        BackendLog --> Write
    end
```

`WorkflowService.__init__()` creates two directories:
- `self.tmp_dir = Path('./tmp')` - stores workflow files
- `self.log_dir = self.tmp_dir / 'logs'` - stores `backend.log`

`list_workflows()` filters files by checking:
1. `f.is_file()` - is a file, not directory
2. `not f.name.startswith('temp_recording')` - excludes temporary recording files
3. `f.name.endswith(('.workflow.json', '.workflow.yaml', '.workflow.yml'))` - valid workflow extension

`get_workflow(name)` uses `yaml.safe_load()` to parse both JSON and YAML files, then returns `json.dumps()` output for frontend compatibility.

Sources: [workflows/backend/service.py:40-42](), [workflows/backend/service.py:89-118](), [workflows/backend/service.py:55-87]()

### Workflow File Format Support

| Format | Extension | Loading | Saving | Frontend Display |
|--------|-----------|---------|--------|------------------|
| JSON | `.workflow.json` | ✓ Direct | ✓ Direct | ✓ Native |
| YAML | `.workflow.yaml`, `.workflow.yml` | ✓ Converted | ✓ Preserved | ✓ Converted to JSON |

The system uses `yaml.safe_load()` to parse both JSON and YAML files, providing format flexibility while maintaining JSON compatibility for the frontend. When updating workflows, the original format is preserved.

Sources: [workflows/backend/service.py:89-118](), [workflows/backend/service.py:120-162]()

## Workflow Execution Flow

Workflow execution in the web interface follows an asynchronous pattern with background task management and real-time status updates.

### Execution Lifecycle

```mermaid
graph TD
    subgraph "1. Request Validation (routers.py:51-62)"
        APICall["POST /api/workflows/execute<br/>request: WorkflowExecuteRequest"]
        ValidateName["if not workflow_name:<br/>HTTPException(400)"]
        ValidateFile["if not workflow_path.exists():<br/>HTTPException(404)"]
        
        APICall --> ValidateName
        ValidateName --> ValidateFile
    end
    
    subgraph "2. Task Creation (routers.py:64-77)"
        CreateTaskID["task_id = str(uuid.uuid4())"]
        CreateEvent["cancel_event = asyncio.Event()<br/>cancel_events[task_id] = cancel_event"]
        GetLogPos["log_pos = await _log_file_position()"]
        CreateBGTask["task = asyncio.create_task(<br/>  run_workflow_in_background(task_id, request, cancel_event))"]
        StoreTask["workflow_tasks[task_id] = task"]
        
        ValidateFile --> CreateTaskID
        CreateTaskID --> CreateEvent
        CreateEvent --> GetLogPos
        GetLogPos --> CreateBGTask
        CreateBGTask --> StoreTask
    end
    
    subgraph "3. Background Execution (service.py:164-220)"
        SetRunning["active_tasks[task_id] = TaskInfo(status='running')"]
        LogStart["Write '[timestamp] Starting workflow' to backend.log"]
        CheckCancel1{"if cancel_event.is_set():<br/>return"}
        LoadWF["workflow_obj = Workflow.load_from_file(<br/>  path, llm=llm_instance, browser=browser_instance)"]
        CheckCancel2{"if cancel_event.is_set():<br/>return"}
        RunWF["result = await workflow_obj.run(<br/>  inputs, close_browser_at_end=True, cancel_event)"]
        
        StoreTask --> SetRunning
        SetRunning --> LogStart
        LogStart --> CheckCancel1
        CheckCancel1 -->|No| LoadWF
        LoadWF --> CheckCancel2
        CheckCancel2 -->|No| RunWF
    end
    
    subgraph "4. Result Processing (service.py:207-220)"
        CheckCancel3{"if cancel_event.is_set():<br/>status='cancelled'"}
        FormatResult["formatted_result = [<br/>  {'step_id': i, 'extracted_content': s.extracted_content}<br/>  for i, s in enumerate(result.step_results)]"]
        SetComplete["active_tasks[task_id].status = 'completed'<br/>active_tasks[task_id].result = formatted_result"]
        LogComplete["Write '[timestamp] Workflow completed' to backend.log"]
        
        RunWF --> CheckCancel3
        CheckCancel3 -->|No| FormatResult
        FormatResult --> SetComplete
        SetComplete --> LogComplete
    end
    
    subgraph "5. Error Handling (service.py:222-229)"
        CatchCancelled["except asyncio.CancelledError:<br/>status = 'cancelled'"]
        CatchError["except Exception as exc:<br/>status = 'failed'<br/>error = str(exc)"]
    end
    
    RunWF -.->|Exception| CatchError
    CheckCancel1 -->|Yes| CatchCancelled
    CheckCancel2 -->|Yes| CatchCancelled
    CheckCancel3 -->|Yes| CatchCancelled
```

The execution flow has five stages:

1. **Request Validation**: Check `workflow_name` is provided and workflow file exists at `tmp_dir / workflow_name`
2. **Task Creation**: Generate UUID, create `asyncio.Event` for cancellation, get initial log position, create background task
3. **Background Execution**: Set status to `'running'`, log start event, check cancellation signals, load workflow, execute `workflow.run()`
4. **Result Processing**: Check cancellation, format `step_results` as list of dicts with `step_id` and `extracted_content`, update status to `'completed'`
5. **Error Handling**: Catch `asyncio.CancelledError` for forced cancellation, catch general exceptions for failed status

Cancellation signals are checked at three points before and during workflow execution to enable graceful shutdown.

Sources: [workflows/backend/routers.py:51-87](), [workflows/backend/service.py:164-230]()

### Cancellation Mechanism

```mermaid
graph TB
    subgraph "1. Cancellation Request (routers.py:113-119)"
        UserAction["User clicks 'Cancel' button"]
        CancelAPI["POST /api/workflows/tasks/{task_id}/cancel"]
        RouterCall["await cancel_workflow(task_id)"]
    end
    
    subgraph "2. Service Validation (service.py:244-266)"
        GetTaskInfo["task_info = active_tasks.get(task_id)"]
        CheckExists{"task_info<br/>exists?"}
        CheckRunning{"task_info.status<br/>== 'running'?"}
        
        RouterCall --> GetTaskInfo
        GetTaskInfo --> CheckExists
        CheckExists -->|Yes| CheckRunning
        CheckExists -->|No| ReturnNotFound["WorkflowCancelResponse(success=False, message='Task not found')"]
        CheckRunning -->|No| ReturnBadStatus["WorkflowCancelResponse(success=False, message='Task is already {status}')"]
    end
    
    subgraph "3. Signal Propagation (service.py:251-264)"
        GetRefs["task = workflow_tasks.get(task_id)<br/>cancel_event = cancel_events.get(task_id)"]
        SetEvent["if cancel_event:<br/>  cancel_event.set()"]
        CancelTask["if task and not task.done():<br/>  task.cancel()"]
        LogCancel["Write '[timestamp] Workflow execution cancelled by user'"]
        SetCancelling["active_tasks[task_id].status = 'cancelling'"]
        
        CheckRunning -->|Yes| GetRefs
        GetRefs --> SetEvent
        SetEvent --> CancelTask
        CancelTask --> LogCancel
        LogCancel --> SetCancelling
        SetCancelling --> ReturnSuccess["WorkflowCancelResponse(success=True)"]
    end
    
    subgraph "4. Workflow Response (service.py:179-204)"
        CheckSignal1["if cancel_event.is_set():<br/>  status = 'cancelled'<br/>  return"]
        CheckSignal2["if cancel_event.is_set():<br/>  status = 'cancelled'<br/>  return"]
        CheckSignal3["if cancel_event.is_set():<br/>  status = 'cancelled'<br/>  return"]
        CatchCancelError["except asyncio.CancelledError:<br/>  status = 'cancelled'<br/>  raise"]
    end
    
    SetEvent -.->|"Checked in workflow loop"| CheckSignal1
    SetEvent -.->|"Checked before load"| CheckSignal2
    SetEvent -.->|"Checked after run"| CheckSignal3
    CancelTask -.->|"Forces immediate stop"| CatchCancelError
```

The cancellation mechanism uses a two-pronged approach:

1. **Graceful Cancellation**: `cancel_event.set()` signals the workflow to stop gracefully. The event is checked at three points:
   - Before loading the workflow ([service.py:179-182]())
   - Before executing `workflow.run()` ([service.py:195-198]())
   - After execution completes ([service.py:202-205]())

2. **Forced Cancellation**: `task.cancel()` raises `asyncio.CancelledError` if the workflow hasn't responded to the event signal. This ensures workflows stop promptly even if stuck in long operations.

The status transitions are: `'running'` → `'cancelling'` (cancellation requested) → `'cancelled'` (workflow stopped). Both cancellation methods update `active_tasks[task_id].status` and log the cancellation event with timestamp to `backend.log`.

Sources: [workflows/backend/service.py:244-266](), [workflows/backend/routers.py:113-119](), [workflows/backend/service.py:179-198](), [workflows/backend/service.py:222-225]()

## Log Management System

The backend implements a file-based logging system with position tracking for efficient incremental log retrieval, enabling real-time log streaming to the frontend without re-reading the entire file.

### Log Position Tracking

```mermaid
graph TB
    subgraph "Initial Position (service.py:55-61)"
        CheckExists["log_file = log_dir / 'backend.log'<br/>if not log_file.exists():"]
        CreateFile["async with aiofiles.open(log_file, 'w'):<br/>  await f.write('')"]
        ReturnZero["return 0"]
        ReturnSize["return log_file.stat().st_size"]
        
        CheckExists -->|File missing| CreateFile
        CreateFile --> ReturnZero
        CheckExists -->|File exists| ReturnSize
    end
    
    subgraph "Incremental Read (service.py:63-83)"
        ReadCall["_read_logs_from_position(position: int)"]
        CheckSize["current_size = log_file.stat().st_size<br/>if position >= current_size:<br/>  return [], position"]
        SeekPos["async with aiofiles.open(log_file, 'r'):<br/>  await f.seek(position)"]
        ReadAll["all_logs = await f.readlines()"]
        FilterLogs["new_logs = [line for line in all_logs<br/>  if not line.strip().startswith(('INFO:', 'WARNING:', 'DEBUG:', 'ERROR:'))]"]
        ReturnData["return new_logs, current_size"]
        
        ReadCall --> CheckSize
        CheckSize -->|position < size| SeekPos
        SeekPos --> ReadAll
        ReadAll --> FilterLogs
        FilterLogs --> ReturnData
    end
    
    subgraph "API Endpoint (routers.py:89-101)"
        GetLogsAPI["GET /api/workflows/logs/{task_id}?position=N"]
        CallRead["logs, new_pos = await _read_logs_from_position(position)"]
        GetStatus["task_info = active_tasks.get(task_id)<br/>status = task_info.status if task_info else 'unknown'"]
        BuildResponse["WorkflowLogsResponse(<br/>  logs=logs, position=new_pos, log_position=new_pos,<br/>  status=status, result=task_info.result, error=task_info.error)"]
        
        GetLogsAPI --> CallRead
        CallRead --> GetStatus
        GetStatus --> BuildResponse
    end
    
    ReturnZero -.->|"Initial position"| GetLogsAPI
    ReturnSize -.->|"Initial position"| GetLogsAPI
    ReturnData -.->|"Subsequent reads"| CallRead
```

The position tracking mechanism works as follows:

1. **Initialization** (`_log_file_position()`): Returns current file size in bytes. Creates empty `backend.log` if missing.

2. **Incremental Read** (`_read_logs_from_position(position)`):
   - If `position >= current_size`: returns empty list (no new logs)
   - Otherwise: seeks to `position`, reads all remaining lines, filters out lines starting with `'INFO:'`, `'WARNING:'`, `'DEBUG:'`, `'ERROR:'`
   - Returns `(new_logs, current_size)` tuple

3. **Client Polling**: Frontend calls `GET /api/workflows/logs/{task_id}?position=N` repeatedly, incrementing `N` with each response

This approach avoids re-reading the entire log file on each poll, reducing I/O overhead for long-running workflows.

Sources: [workflows/backend/service.py:55-83](), [workflows/backend/routers.py:89-101]()

### Log Writing with Timestamps

All workflow execution events are logged to `./tmp/logs/backend.log` with timestamps using the format `[YYYY-MM-DD HH:MM:SS]`. The `_write_log()` method appends log entries asynchronously using `aiofiles` for non-blocking I/O.

| Log Event | Example Format |
|-----------|----------------|
| Workflow start | `[2024-01-15 10:30:45] Starting workflow 'example.workflow.json'` |
| Input parameters | `[2024-01-15 10:30:45] Input parameters: {"key": "value"}` |
| Step completion | `[2024-01-15 10:30:50] Completed step 0: {"data": "result"}` |
| Workflow completion | `[2024-01-15 10:31:00] Workflow completed successfully with 5 steps` |
| Error | `[2024-01-15 10:30:55] Error: Element not found` |
| Cancellation | `[2024-01-15 10:30:58] Workflow execution cancelled by user` |

Sources: [workflows/backend/service.py:85-87](), [workflows/backend/service.py:174-220]()

## Integration with Workflow Engine

The web interface integrates with the core workflow execution system through the `Workflow.load_from_file()` method and shared browser/LLM instances.

### Service Initialization and Workflow Integration

```mermaid
graph TB
    subgraph "WorkflowService.__init__() - service.py:38-53"
        CreateDirs["self.tmp_dir = Path('./tmp')<br/>self.log_dir = tmp_dir / 'logs'<br/>log_dir.mkdir(exist_ok=True, parents=True)"]
        InitLLM["self.llm_instance = ChatBrowserUse(model='bu-latest')"]
        InitBrowser["self.browser_instance = Browser()"]
        InitController["self.controller_instance = WorkflowController()"]
        InitTracking["self.active_tasks: Dict[str, TaskInfo] = {}<br/>self.workflow_tasks: Dict[str, asyncio.Task] = {}<br/>self.cancel_events: Dict[str, asyncio.Event] = {}"]
        
        CreateDirs --> InitLLM
        InitLLM --> InitBrowser
        InitBrowser --> InitController
        InitController --> InitTracking
    end
    
    subgraph "Workflow Loading - service.py:185-191"
        LoadPath["workflow_path = tmp_dir / workflow_name"]
        LoadCall["self.workflow_obj = Workflow.load_from_file(<br/>  str(workflow_path),<br/>  llm=self.llm_instance,<br/>  browser=self.browser_instance,<br/>  controller=self.controller_instance)"]
        CatchLoadError["except Exception as e:<br/>  print(f'Error loading workflow: {e}')<br/>  return"]
        
        LoadPath --> LoadCall
        LoadCall --> CatchLoadError
    end
    
    subgraph "Workflow Execution - service.py:200"
        RunCall["result = await self.workflow_obj.run(<br/>  inputs,<br/>  close_browser_at_end=True,<br/>  cancel_event=cancel_event)"]
        CheckResult["if cancel_event.is_set():<br/>  active_tasks[task_id].status = 'cancelled'<br/>  return"]
        FormatSteps["formatted_result = [{<br/>  'step_id': i,<br/>  'extracted_content': s.extracted_content,<br/>  'status': 'completed'<br/>} for i, s in enumerate(result.step_results)]"]
        
        LoadCall --> RunCall
        RunCall --> CheckResult
        CheckResult -->|Not cancelled| FormatSteps
    end
    
    subgraph "Resource Sharing"
        SharedLLM["Single ChatBrowserUse instance<br/>for all workflow executions"]
        SharedBrowser["Single Browser instance<br/>for all workflow executions"]
        SharedController["Single WorkflowController instance<br/>for all workflow executions"]
        
        InitLLM --> SharedLLM
        InitBrowser --> SharedBrowser
        InitController --> SharedController
    end
```

`WorkflowService.__init__()` creates singleton instances of core dependencies:

| Instance | Type | Purpose |
|----------|------|---------|
| `self.llm_instance` | `ChatBrowserUse(model='bu-latest')` | LLM for workflow execution and extraction |
| `self.browser_instance` | `Browser()` | Browser automation via browser-use package |
| `self.controller_instance` | `WorkflowController()` | Controller for workflow actions |

These instances are passed to `Workflow.load_from_file()` during workflow loading ([service.py:185-191]()), enabling resource sharing across multiple concurrent workflow executions. Each workflow receives its own `cancel_event` for independent cancellation control.

The `workflow.run()` method ([service.py:200]()) accepts three key parameters:
- `inputs`: `Dict[str, Any]` - workflow input parameters
- `close_browser_at_end=True`: closes browser after execution
- `cancel_event`: `asyncio.Event` - for graceful cancellation

Results are formatted as a list of dicts with `step_id`, `extracted_content`, and `status` fields for frontend consumption.

Sources: [workflows/backend/service.py:38-53](), [workflows/backend/service.py:185-191](), [workflows/backend/service.py:200-220]()

## CORS Configuration and Security

The FastAPI application includes CORS middleware configured specifically for local development with the React frontend.

```mermaid
graph LR
    subgraph "FastAPI Application"
        APP["FastAPI(title='Workflow Execution Service')"]
        MIDDLEWARE["CORSMiddleware"]
        ROUTER["workflows router"]
        
        APP --> MIDDLEWARE
        APP --> ROUTER
    end
    
    subgraph "CORS Configuration"
        ORIGINS["allow_origins: ['http://localhost:5173']"]
        CREDENTIALS["allow_credentials: True"]
        METHODS["allow_methods: ['*']"]
        HEADERS["allow_headers: ['*']"]
        
        MIDDLEWARE --> ORIGINS
        MIDDLEWARE --> CREDENTIALS  
        MIDDLEWARE --> METHODS
        MIDDLEWARE --> HEADERS
    end
    
    subgraph "Network Binding"
        HOST["host: '127.0.0.1'"]
        PORT["port: 8000"]
        LOGLEVEL["log_level: 'info'"]
        
        APP --> HOST
        APP --> PORT
        APP --> LOGLEVEL
    end
```

Sources: [workflows/backend/api.py:7-24]()

---

