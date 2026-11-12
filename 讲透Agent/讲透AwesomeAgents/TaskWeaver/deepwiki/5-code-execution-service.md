<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/TaskWeaver · page 5 Code Execution Service · fetched 2026-10-26 -->

# Code Execution Service

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitattributes](.gitattributes)
- [docker/ces_container/Dockerfile](docker/ces_container/Dockerfile)
- [docker/ces_container/entrypoint.sh](docker/ces_container/entrypoint.sh)
- [project/examples/planner_examples/example-planner-echo.yaml](project/examples/planner_examples/example-planner-echo.yaml)
- [project/examples/planner_examples/example-planner-recepta.yaml](project/examples/planner_examples/example-planner-recepta.yaml)
- [scripts/build_executor.ps1](scripts/build_executor.ps1)
- [taskweaver/ces/__init__.py](taskweaver/ces/__init__.py)
- [taskweaver/ces/environment.py](taskweaver/ces/environment.py)
- [taskweaver/ces/kernel/ctx_magic.py](taskweaver/ces/kernel/ctx_magic.py)
- [taskweaver/ces/kernel/ext.py](taskweaver/ces/kernel/ext.py)
- [taskweaver/ces/kernel/launcher.py](taskweaver/ces/kernel/launcher.py)
- [taskweaver/ces/manager/sub_proc.py](taskweaver/ces/manager/sub_proc.py)
- [taskweaver/ces/runtime/executor.py](taskweaver/ces/runtime/executor.py)
- [taskweaver/ext_role/recepta/__init__.py](taskweaver/ext_role/recepta/__init__.py)
- [taskweaver/ext_role/recepta/recepta.py](taskweaver/ext_role/recepta/recepta.py)
- [taskweaver/ext_role/recepta/recepta.role.yaml](taskweaver/ext_role/recepta/recepta.role.yaml)
- [taskweaver/module/execution_service.py](taskweaver/module/execution_service.py)
- [tests/unit_tests/test_environment.py](tests/unit_tests/test_environment.py)

</details>



The Code Execution Service (CES) is TaskWeaver's isolated code execution environment that provides secure, sandboxed Python code execution capabilities. It manages IPython kernels, handles plugin loading, and maintains execution state across user sessions. The service supports both local and containerized execution modes for flexibility and security.

For information about how the Code Execution Service integrates with the broader TaskWeaver architecture, see [System Architecture](#2). For details about plugin development and management, see [Plugin System](#6).

## Architecture Overview

The Code Execution Service follows a manager-client pattern with pluggable execution environments:

```mermaid
graph TB
    subgraph "CES Factory Layer"
        Factory["code_execution_service_factory"]
    end
    
    subgraph "Management Layer"
        DeferredManager["DeferredManager"]
        SubProcessManager["SubProcessManager"]
    end
    
    subgraph "Client Layer"
        SubProcessClient["SubProcessClient"]
    end
    
    subgraph "Execution Environment"
        Environment["Environment"]
        EnvSession["EnvSession"]
        EnvExecution["EnvExecution"]
    end
    
    subgraph "Kernel Infrastructure"
        KernelSpecProvider["KernelSpecProvider"]
        TaskWeaverMultiKernelManager["TaskWeaverMultiKernelManager"]
        IPKernelApp["IPKernelApp"]
    end
    
    subgraph "Execution Modes"
        LocalMode["Local Mode<br/>Direct kernel launch"]
        ContainerMode["Container Mode<br/>Docker-based isolation"]
    end
    
    subgraph "Runtime Components"
        Executor["Executor"]
        TaskWeaverContextMagic["TaskWeaverContextMagic"]
        TaskWeaverPluginMagic["TaskWeaverPluginMagic"]
    end
    
    Factory --> DeferredManager
    DeferredManager --> SubProcessManager
    SubProcessManager --> SubProcessClient
    SubProcessClient --> Environment
    Environment --> EnvSession
    EnvSession --> EnvExecution
    
    Environment --> KernelSpecProvider
    Environment --> TaskWeaverMultiKernelManager
    TaskWeaverMultiKernelManager --> IPKernelApp
    
    Environment --> LocalMode
    Environment --> ContainerMode
    
    IPKernelApp --> Executor
    IPKernelApp --> TaskWeaverContextMagic
    IPKernelApp --> TaskWeaverPluginMagic
    
    style Environment fill:#f9f,stroke:#333,stroke-width:2px
    style Executor fill:#bbf,stroke:#333,stroke-width:2px
```

*Sources: taskweaver/ces/__init__.py, taskweaver/ces/environment.py, taskweaver/ces/manager/sub_proc.py, taskweaver/ces/kernel/launcher.py*

## Service Factory and Configuration

The CES uses a factory pattern for initialization through the `code_execution_service_factory` function:

```mermaid
graph LR
    ExecutionServiceConfig["ExecutionServiceConfig"]
    ExecutionServiceModule["ExecutionServiceModule"]
    DeferredManager["DeferredManager"]
    SubProcessManager["SubProcessManager"]
    Environment["Environment"]
    
    ExecutionServiceConfig --> ExecutionServiceModule
    ExecutionServiceModule --> DeferredManager
    DeferredManager --> SubProcessManager
    SubProcessManager --> Environment
    
    ExecutionServiceConfig -.-> ConfigOptions["env_dir<br/>kernel_mode<br/>custom_image"]
```

The configuration supports key parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `env_dir` | `{app_base_path}/env` | Directory for execution environments |
| `kernel_mode` | `"container"` | Execution mode: `"local"` or `"container"` |
| `custom_image` | `None` | Custom Docker image for container mode |

*Sources: taskweaver/module/execution_service.py:11-36, taskweaver/ces/__init__.py:8-23*

## Environment Management

### Environment Class

The `Environment` class [taskweaver/ces/environment.py:113-178]() is the core component managing kernel lifecycle and execution:

```mermaid
graph TB
    subgraph "Environment Class"
        Environment["Environment"]
        
        subgraph "Session Management"
            SessionDict["session_dict: Dict[str, EnvSession]"]
            ClientDict["client_dict: Dict[str, BlockingKernelClient]"]
        end
        
        subgraph "Execution Modes"
            LocalExecution["Local Mode<br/>TaskWeaverMultiKernelManager"]
            ContainerExecution["Container Mode<br/>Docker Client"]
        end
        
        subgraph "Session Operations"
            StartSession["start_session()"]
            StopSession["stop_session()"]
            ExecuteCode["execute_code()"]
            LoadPlugin["load_plugin()"]
        end
    end
    
    Environment --> SessionDict
    Environment --> ClientDict
    Environment --> LocalExecution
    Environment --> ContainerExecution
    Environment --> StartSession
    Environment --> StopSession
    Environment --> ExecuteCode
    Environment --> LoadPlugin
```

*Sources: taskweaver/ces/environment.py:113-178*

### Session Lifecycle

Each execution session follows a defined lifecycle managed by `EnvSession`:

```mermaid
stateDiagram-v2
    [*] --> pending: start_session()
    pending --> ready: kernel_started
    ready --> running: execute_code()
    running --> ready: execution_complete
    ready --> stopped: stop_session()
    running --> error: execution_error
    error --> stopped: stop_session()
    stopped --> [*]
```

Session state is tracked through the `EnvSession` dataclass [taskweaver/ces/environment.py:58-73]():

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | `str` | Unique session identifier |
| `kernel_status` | `Literal` | Current kernel state |
| `kernel_id` | `str` | IPython kernel identifier |
| `execution_count` | `int` | Number of executions performed |
| `session_dir` | `str` | Session workspace directory |
| `session_var` | `Dict[str, str]` | Session variables |
| `plugins` | `Dict[str, EnvPlugin]` | Loaded plugins |

*Sources: taskweaver/ces/environment.py:58-73, taskweaver/ces/environment.py:187-310*

## Execution Modes

### Local Mode

Local mode [taskweaver/ces/environment.py:200-236]() runs IPython kernels directly on the host system:

```mermaid
graph LR
    subgraph "Local Mode Components"
        TaskWeaverMultiKernelManager["TaskWeaverMultiKernelManager"]
        KernelSpecProvider["KernelSpecProvider"]
        IPKernelApp["IPKernelApp + TaskWeaver Extensions"]
    end
    
    subgraph "Environment Variables"
        EnvVars["TASKWEAVER_ENV_ID<br/>TASKWEAVER_SESSION_ID<br/>TASKWEAVER_SESSION_DIR<br/>PYTHONPATH"]
    end
    
    TaskWeaverMultiKernelManager --> KernelSpecProvider
    KernelSpecProvider --> IPKernelApp
    EnvVars --> IPKernelApp
```

*Sources: taskweaver/ces/environment.py:200-236, taskweaver/ces/environment.py:75-91*

### Container Mode

Container mode [taskweaver/ces/environment.py:237-308]() provides Docker-based isolation using the `taskweavercontainers/taskweaver-executor` image:

```mermaid
graph TB
    subgraph "Container Infrastructure"
        DockerClient["docker.from_env()"]
        DefaultImage["taskweavercontainers/taskweaver-executor:latest"]
        CustomImage["custom_image (optional)"]
    end
    
    subgraph "Container Configuration"
        Volumes["Volume Mounts<br/>/app/ces/ → session_dir/ces<br/>/app/cwd → session_dir/cwd"]
        Ports["Port Mapping<br/>12345-12349 → random host ports"]
        Environment["Container Environment<br/>TASKWEAVER_KERNEL_MODE=container<br/>TASKWEAVER_SESSION_ID<br/>TASKWEAVER_UID/GID"]
    end
    
    subgraph "Connection Management"
        ConnectionFile["Connection File<br/>conn-{session_id}-{kernel_id}.json"]
        PortsFile["ports.json<br/>Host port mappings"]
    end
    
    DockerClient --> DefaultImage
    DockerClient --> CustomImage
    DefaultImage --> Volumes
    CustomImage --> Volumes
    Volumes --> Ports
    Ports --> Environment
    Environment --> ConnectionFile
    ConnectionFile --> PortsFile
```

*Sources: taskweaver/ces/environment.py:237-308, docker/ces_container/Dockerfile, docker/ces_container/entrypoint.sh*

## Kernel Integration

### Kernel Launcher

The kernel launcher [taskweaver/ces/kernel/launcher.py]() initializes IPython kernels with TaskWeaver extensions:

```mermaid
graph TB
    subgraph "Kernel Initialization"
        Launcher["launcher.py"]
        IPKernelApp["IPKernelApp"]
        ZMQInteractiveShell["ZMQInteractiveShell"]
    end
    
    subgraph "TaskWeaver Extensions"
        ContextMagic["taskweaver.ces.kernel.ctx_magic"]
        DisplayHook["TaskWeaverZMQShellDisplayHook"]
        ConfigFile["config.py"]
    end
    
    subgraph "Environment Detection"
        KernelMode["TASKWEAVER_KERNEL_MODE"]
        LocalConfig["Direct IPKernel configuration"]
        ContainerConfig["Environment-based configuration"]
    end
    
    Launcher --> IPKernelApp
    IPKernelApp --> ZMQInteractiveShell
    IPKernelApp --> ContextMagic
    ZMQInteractiveShell --> DisplayHook
    IPKernelApp --> ConfigFile
    
    KernelMode --> LocalConfig
    KernelMode --> ContainerConfig
    LocalConfig --> IPKernelApp
    ContainerConfig --> IPKernelApp
```

*Sources: taskweaver/ces/kernel/launcher.py, taskweaver/ces/kernel/ext.py*

### Magic Commands

TaskWeaver extends IPython with custom magic commands through `TaskWeaverContextMagic` and `TaskWeaverPluginMagic`:

| Magic Command | Type | Purpose |
|---------------|------|---------|
| `%_taskweaver_session_init` | Line | Initialize TaskWeaver context |
| `%%_taskweaver_update_session_var` | Cell | Update session variables |
| `%_taskweaver_check_session_var` | Line | Display session variables |
| `%_taskweaver_exec_pre_check` | Line | Pre-execution setup |
| `%_taskweaver_exec_post_check` | Line | Post-execution cleanup |
| `%%_taskweaver_plugin_register` | Cell | Register plugin code |
| `%%_taskweaver_plugin_load` | Cell | Load plugin with configuration |
| `%_taskweaver_plugin_test` | Line | Test plugin functionality |
| `%_taskweaver_plugin_unload` | Line | Unload plugin |

*Sources: taskweaver/ces/kernel/ctx_magic.py:19-155*

## Runtime Execution

### Executor Class

The `Executor` class [taskweaver/ces/runtime/executor.py:139-236]() manages plugin lifecycle and execution context:

```mermaid
graph TB
    subgraph "Executor State"
        SessionVar["session_var: Dict[str, str]"]
        PluginRegistry["plugin_registry: Dict[str, RuntimePlugin]"]
        ExecutionCounter["cur_execution_count: int"]
        Context["ctx: ExecutorPluginContext"]
    end
    
    subgraph "Plugin Management"
        RegisterPlugin["register_plugin()"]
        ConfigPlugin["config_plugin()"]
        GetInstance["get_plugin_instance()"]
        TestPlugin["test_plugin()"]
    end
    
    subgraph "Execution Management"
        PreExecution["pre_execution()"]
        PostExecution["get_post_execution_state()"]
        LoadLib["load_lib()"]
    end
    
    SessionVar --> Context
    PluginRegistry --> RegisterPlugin
    PluginRegistry --> ConfigPlugin
    PluginRegistry --> GetInstance
    PluginRegistry --> TestPlugin
    
    ExecutionCounter --> PreExecution
    ExecutionCounter --> PostExecution
    Context --> LoadLib
```

*Sources: taskweaver/ces/runtime/executor.py:139-236*

### Code Execution Flow

The code execution process follows a structured pipeline:

```mermaid
sequenceDiagram
    participant Client as "SubProcessClient"
    participant Env as "Environment"
    participant Kernel as "IPython Kernel"
    participant Executor as "Executor"
    participant Magic as "Magic Commands"
    
    Client->>Env: execute_code(session_id, code, exec_id)
    Env->>Env: increment execution_count
    Env->>Magic: %_taskweaver_exec_pre_check
    Magic->>Executor: pre_execution(exec_idx, exec_id)
    Executor->>Executor: reset context state
    
    Note over Env: Update session variables if needed
    Env->>Magic: %%_taskweaver_update_session_var
    Magic->>Executor: update_session_var()
    
    Env->>Kernel: execute user code
    Kernel-->>Env: execution messages (stdout, stderr, results)
    
    Env->>Magic: %_taskweaver_exec_post_check
    Magic->>Executor: get_post_execution_state()
    Executor-->>Magic: artifacts, logs, output
    Magic-->>Env: execution metadata
    
    Env->>Env: parse_exec_result()
    Env-->>Client: ExecutionResult
```

*Sources: taskweaver/ces/environment.py:312-343, taskweaver/ces/kernel/ctx_magic.py:50-61*

## Container Infrastructure

### Docker Image Build

The executor container is built using a multi-stage process:

```mermaid
graph TB
    subgraph "Build Process"
        BaseImage["python:3.10-slim"]
        Requirements["requirements.txt"]
        TaskWeaverCode["taskweaver/ces<br/>taskweaver/plugin<br/>taskweaver/module"]
        Entrypoint["entrypoint.sh"]
    end
    
    subgraph "Runtime Configuration"
        PythonPath["PYTHONPATH=/app"]
        WorkDir["WORKDIR /app"]
        EntrypointExec["ENTRYPOINT ['/app/entrypoint.sh']"]
    end
    
    subgraph "User Management"
        UserCreation["useradd taskweaver"]
        Permissions["chown -R taskweaver:taskweaver /app"]
        VirtualEnv["python -m venv --system-site-packages"]
    end
    
    BaseImage --> Requirements
    Requirements --> TaskWeaverCode
    TaskWeaverCode --> Entrypoint
    Entrypoint --> PythonPath
    PythonPath --> WorkDir
    WorkDir --> EntrypointExec
    
    EntrypointExec --> UserCreation
    UserCreation --> Permissions
    Permissions --> VirtualEnv
```

*Sources: docker/ces_container/Dockerfile, docker/ces_container/entrypoint.sh, scripts/build_executor.ps1*

### Container Security

The container implements security measures through user isolation and environment configuration:

| Security Feature | Implementation | Purpose |
|------------------|----------------|---------|
| Non-root execution | `useradd -u $USER_ID taskweaver` | Prevent privilege escalation |
| Volume isolation | Bind mounts for `/app/ces` and `/app/cwd` | Limit filesystem access |
| Port isolation | Dynamic port mapping | Prevent port conflicts |
| UID/GID mapping | `TASKWEAVER_UID`/`TASKWEAVER_GID` | File permission consistency |

*Sources: docker/ces_container/entrypoint.sh:3-13, taskweaver/ces/environment.py:250-254*

## Client Interface

### SubProcessClient

The `SubProcessClient` class [taskweaver/ces/manager/sub_proc.py:9-52]() provides the primary interface to the execution service:

```mermaid
graph LR
    subgraph "SubProcessClient Interface"
        Start["start()"]
        Stop["stop()"]
        ExecuteCode["execute_code()"]
        LoadPlugin["load_plugin()"]
        TestPlugin["test_plugin()"]
        UpdateSessionVar["update_session_var()"]
    end
    
    subgraph "Environment Delegation"
        EnvStartSession["env.start_session()"]
        EnvStopSession["env.stop_session()"]
        EnvExecuteCode["env.execute_code()"]
        EnvLoadPlugin["env.load_plugin()"]
        EnvTestPlugin["env.test_plugin()"]
        EnvUpdateSessionVar["env.update_session_var()"]
    end
    
    Start --> EnvStartSession
    Stop --> EnvStopSession
    ExecuteCode --> EnvExecuteCode
    LoadPlugin --> EnvLoadPlugin
    TestPlugin --> EnvTestPlugin
    UpdateSessionVar --> EnvUpdateSessionVar
```

*Sources: taskweaver/ces/manager/sub_proc.py:9-52*

## Testing and Validation

The CES includes comprehensive testing for both local and container modes:

```mermaid
graph TB
    subgraph "Test Categories"
        LocalTests["Local Mode Tests"]
        ContainerTests["Container Mode Tests"]
        SessionVarTests["Session Variable Tests"]
    end
    
    subgraph "Test Operations"
        StartSession["start_session()"]
        ExecuteCode["execute_code()"]
        StopSession["stop_session()"]
        FileOperations["File I/O operations"]
        PluginManagement["Plugin loading/unloading"]
    end
    
    subgraph "Validation Points"
        DirectoryCreation["Session directories created"]
        ConnectionFiles["Kernel connection files"]
        PortMappings["Container port mappings"]
        CodeExecution["Code execution results"]
        SessionPersistence["Session variable persistence"]
    end
    
    LocalTests --> StartSession
    ContainerTests --> StartSession
    SessionVarTests --> StartSession
    
    StartSession --> ExecuteCode
    ExecuteCode --> StopSession
    StopSession --> FileOperations
    FileOperations --> PluginManagement
    
    PluginManagement --> DirectoryCreation
    DirectoryCreation --> ConnectionFiles
    ConnectionFiles --> PortMappings
    PortMappings --> CodeExecution
    CodeExecution --> SessionPersistence
```

*Sources: tests/unit_tests/test_environment.py:88-191*

---

