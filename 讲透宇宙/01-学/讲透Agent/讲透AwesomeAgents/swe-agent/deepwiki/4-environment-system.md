<!-- source: DeepWiki mcp.deepwiki.com · repo SWE-agent/SWE-agent · page 4 Environment System · fetched 2026-10-26 -->

# Environment System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [pyproject.toml](pyproject.toml)
- [sweagent/environment/swe_env.py](sweagent/environment/swe_env.py)
- [tests/conftest.py](tests/conftest.py)
- [tests/test_env.py](tests/test_env.py)
- [tests/test_run.py](tests/test_run.py)

</details>



The Environment System provides a containerized execution environment for SWE-agent where language model agents can safely interact with codebases and execute commands. This system abstracts Docker containers and runtime management through the SWE-ReX backend, providing file operations, command execution, and repository management capabilities.

For information about agent tool usage within environments, see [Tool System](#6). For details about running agents and orchestration, see [Execution and Run System](#5).

## Core Architecture

The Environment System is built around two primary classes: `EnvironmentConfig` for configuration management and `SWEEnv` for runtime operations. The system integrates with SWE-ReX to provide containerized execution environments.

```mermaid
graph TB
    subgraph "Configuration Layer"
        EnvironmentConfig["EnvironmentConfig<br/>(sweagent.environment.swe_env)"]
        DeploymentConfig["DeploymentConfig<br/>(swerex.deployment.config)"]
        RepoConfig["RepoConfig<br/>(sweagent.environment.repo)"]
    end
    
    subgraph "Runtime Layer"
        SWEEnv["SWEEnv<br/>(sweagent.environment.swe_env)"]
        AbstractDeployment["AbstractDeployment<br/>(swerex.deployment.abstract)"]
        Runtime["Runtime<br/>(swerex.runtime)"]
    end
    
    subgraph "Container Infrastructure"
        DockerContainer["Docker Container"]
        BashSession["Bash Session"]
        FileSystem["Container File System"]
    end
    
    subgraph "Hook System"
        CombinedEnvHooks["CombinedEnvHooks"]
        EnvHook["EnvHook"]
    end
    
    EnvironmentConfig --> SWEEnv
    DeploymentConfig --> AbstractDeployment
    RepoConfig --> SWEEnv
    
    SWEEnv --> AbstractDeployment
    SWEEnv --> CombinedEnvHooks
    CombinedEnvHooks --> EnvHook
    
    AbstractDeployment --> Runtime
    Runtime --> DockerContainer
    Runtime --> BashSession
    Runtime --> FileSystem
    
    style SWEEnv fill:#ffcccc
    style EnvironmentConfig fill:#ccffcc
```

**Core Environment Architecture**

Sources: [sweagent/environment/swe_env.py:1-277](), [pyproject.toml:60-60]()

## Environment Configuration

The `EnvironmentConfig` class defines the environment setup parameters including deployment options, repository configuration, and startup commands.

| Configuration Field | Type | Purpose |
|---------------------|------|---------|
| `deployment` | `DeploymentConfig` | Container deployment settings (Docker image, Python setup) |
| `repo` | `RepoConfig \| None` | Repository to clone/mount in the environment |
| `post_startup_commands` | `list[str]` | Commands executed after environment initialization |
| `post_startup_command_timeout` | `int` | Timeout for startup commands (default: 500s) |
| `name` | `str` | Environment identifier (default: "main") |

```mermaid
graph LR
    subgraph "Configuration Sources"
        YAMLConfig["YAML Configuration Files"]
        CLIArgs["CLI Arguments"]
        Defaults["Default Values"]
    end
    
    subgraph "Environment Configuration"
        EnvironmentConfig_Model["EnvironmentConfig<br/>model_config = forbid"]
        DeploymentConfig_Field["deployment: DeploymentConfig"]
        RepoConfig_Field["repo: RepoConfig | None"]
        PostStartup["post_startup_commands: list[str]"]
        Timeout["post_startup_command_timeout: int"]
    end
    
    subgraph "Runtime Instantiation"
        from_config["SWEEnv.from_config()"]
        get_deployment["get_deployment()"]
        SWEEnv_Instance["SWEEnv Instance"]
    end
    
    YAMLConfig --> EnvironmentConfig_Model
    CLIArgs --> EnvironmentConfig_Model
    Defaults --> EnvironmentConfig_Model
    
    EnvironmentConfig_Model --> DeploymentConfig_Field
    EnvironmentConfig_Model --> RepoConfig_Field
    EnvironmentConfig_Model --> PostStartup
    EnvironmentConfig_Model --> Timeout
    
    EnvironmentConfig_Model --> from_config
    DeploymentConfig_Field --> get_deployment
    from_config --> SWEEnv_Instance
```

**Environment Configuration Flow**

Sources: [sweagent/environment/swe_env.py:24-49](), [sweagent/environment/swe_env.py:84-98]()

## SWE-ReX Runtime Integration

The `SWEEnv` class integrates with SWE-ReX to provide containerized execution through the `AbstractDeployment` interface. This abstraction supports different deployment types including Docker containers and dummy environments for testing.

```mermaid
sequenceDiagram
    participant Client as "SWEEnv Client"
    participant SWEEnv as "SWEEnv"
    participant Deployment as "AbstractDeployment"
    participant Runtime as "SWE-ReX Runtime"
    participant Container as "Docker Container"
    
    Client->>SWEEnv: "start()"
    SWEEnv->>SWEEnv: "_init_deployment()"
    SWEEnv->>Deployment: "start()"
    Deployment->>Container: "Create/Start Container"
    SWEEnv->>Runtime: "create_session(CreateBashSessionRequest)"
    Runtime->>Container: "Initialize Bash Session"
    SWEEnv->>SWEEnv: "set_env_variables()"
    SWEEnv->>SWEEnv: "reset()"
    SWEEnv->>SWEEnv: "_copy_repo()"
    SWEEnv->>SWEEnv: "_reset_repository()"
    
    loop "Agent Operations"
        Client->>SWEEnv: "communicate(command)"
        SWEEnv->>Runtime: "run_in_session(BashAction)"
        Runtime->>Container: "Execute Command"
        Container-->>Runtime: "Command Output"
        Runtime-->>SWEEnv: "BashAction Result"
        SWEEnv-->>Client: "Command Output"
    end
    
    Client->>SWEEnv: "close()"
    SWEEnv->>Deployment: "stop()"
    Deployment->>Container: "Stop Container"
```

**SWE-ReX Integration Sequence**

Sources: [sweagent/environment/swe_env.py:109-114](), [sweagent/environment/swe_env.py:176-190](), [sweagent/environment/swe_env.py:168-172]()

## Command Execution and Communication

The `communicate` method provides the primary interface for executing commands in the containerized environment. It supports timeout handling, exit code checking, and error management.

```mermaid
graph TD
    subgraph "Command Execution Interface"
        communicate["communicate(input, timeout, check, error_msg)"]
        BashAction_Creation["BashAction(command, timeout, check)"]
        run_in_session["runtime.run_in_session()"]
        Output_Processing["Process Output & Exit Code"]
    end
    
    subgraph "Check Modes"
        ignore_mode["check='ignore'<br/>No exit code validation"]
        warn_mode["check='warn'<br/>Log error on failure"]
        raise_mode["check='raise'<br/>Raise RuntimeError on failure"]
    end
    
    subgraph "File Operations"
        read_file["read_file(path, encoding, errors)"]
        write_file["write_file(path, content)"]
        ReadFileRequest["ReadFileRequest"]
        WriteFileRequest["WriteFileRequest"]
    end
    
    subgraph "Environment Management"
        set_env_variables["set_env_variables(env_variables)"]
        execute_command["execute_command(command, shell, check)"]
        interrupt_session["interrupt_session()"]
    end
    
    communicate --> BashAction_Creation
    BashAction_Creation --> run_in_session
    run_in_session --> Output_Processing
    
    Output_Processing --> ignore_mode
    Output_Processing --> warn_mode
    Output_Processing --> raise_mode
    
    read_file --> ReadFileRequest
    write_file --> WriteFileRequest
    
    style communicate fill:#ffeeee
    style read_file fill:#eeffee
    style write_file fill:#eeffee
```

**Command Execution and File Operations**

Sources: [sweagent/environment/swe_env.py:196-232](), [sweagent/environment/swe_env.py:234-254](), [sweagent/environment/swe_env.py:256-276]()

## Repository Management

The environment system handles repository setup, including cloning, copying, and resetting to specific commits. Repository operations are coordinated through the `Repo` protocol and `RepoConfig` classes.

```mermaid
graph TB
    subgraph "Repository Lifecycle"
        start_env["Environment Start"]
        copy_repo["_copy_repo()"]
        check_existing["Check if repo exists<br/>ls command"]
        repo_copy["repo.copy(deployment)"]
        reset_repo["_reset_repository()"]
        reset_commands["repo.get_reset_commands()"]
    end
    
    subgraph "Repository Operations"
        cd_repo["cd /{repo.repo_name}"]
        export_root["export ROOT=$(pwd -P)"]
        git_reset["Git reset operations"]
        cleanup["Repository cleanup"]
    end
    
    subgraph "Reset Scenarios"
        hard_reset["hard_reset()<br/>Complete restart"]
        soft_reset["reset()<br/>Clean state only"]
        close_start["close() → start()"]
    end
    
    start_env --> copy_repo
    copy_repo --> check_existing
    check_existing --> repo_copy
    repo_copy --> reset_repo
    reset_repo --> cd_repo
    cd_repo --> export_root
    export_root --> reset_commands
    reset_commands --> git_reset
    
    hard_reset --> close_start
    soft_reset --> copy_repo
    
    style copy_repo fill:#ffffcc
    style reset_repo fill:#ccffff
```

**Repository Management Flow**

Sources: [sweagent/environment/swe_env.py:116-127](), [sweagent/environment/swe_env.py:149-166](), [sweagent/environment/swe_env.py:128-133]()

## Hook System Integration

The environment supports an extensible hook system through `EnvHook` classes that can inject custom functionality at various lifecycle stages. Hooks are managed by the `CombinedEnvHooks` coordinator.

| Hook Method | Trigger Point | Purpose |
|------------|---------------|---------|
| `on_init` | Environment initialization | Setup hook state |
| `on_start_deployment` | Before deployment start | Pre-deployment setup |
| `on_copy_repo_started` | Before repository copy | Repository setup hooks |
| `on_environment_startup` | After environment reset | Post-initialization logic |
| `on_close` | Environment shutdown | Cleanup operations |

```mermaid
graph LR
    subgraph "Hook Registration"
        add_hook["add_hook(hook: EnvHook)"]
        hook_on_init["hook.on_init(env=self)"]
        combined_add["_chook.add_hook(hook)"]
    end
    
    subgraph "Hook Triggers"
        start_deployment["_chook.on_start_deployment()"]
        copy_repo_hook["_chook.on_copy_repo_started(repo)"]
        startup_hook["_chook.on_environment_startup()"]
        close_hook["_chook.on_close()"]
    end
    
    subgraph "Hook Implementation"
        EnvHook_Abstract["EnvHook (Abstract)"]
        Custom_Hook_1["Custom Hook Implementation"]
        Custom_Hook_2["Another Hook Implementation"]
        CombinedEnvHooks_Coordinator["CombinedEnvHooks<br/>(_chook)"]
    end
    
    add_hook --> hook_on_init
    hook_on_init --> combined_add
    
    EnvHook_Abstract --> Custom_Hook_1
    EnvHook_Abstract --> Custom_Hook_2
    Custom_Hook_1 --> CombinedEnvHooks_Coordinator
    Custom_Hook_2 --> CombinedEnvHooks_Coordinator
    
    CombinedEnvHooks_Coordinator --> start_deployment
    CombinedEnvHooks_Coordinator --> copy_repo_hook
    CombinedEnvHooks_Coordinator --> startup_hook
    CombinedEnvHooks_Coordinator --> close_hook
```

**Environment Hook System**

Sources: [sweagent/environment/swe_env.py:100-107](), [sweagent/environment/swe_env.py:19-19](), [sweagent/environment/swe_env.py:80-82]()

## Environment Lifecycle Management

The environment follows a structured lifecycle from initialization through operation to cleanup, with support for both soft resets and complete restarts.

```mermaid
stateDiagram-v2
    [*] --> Uninitialized
    
    Uninitialized --> Initializing : from_config()
    Initializing --> Configured : Configuration loaded
    
    Configured --> Starting : start()
    Starting --> DeploymentInit : _init_deployment()
    DeploymentInit --> SessionCreated : create_session()
    SessionCreated --> EnvSetup : set_env_variables()
    EnvSetup --> Ready : reset()
    
    Ready --> Operating : Agent commands
    Operating --> Operating : communicate()
    Operating --> Operating : read_file()
    Operating --> Operating : write_file()
    
    Operating --> Resetting : reset()
    Resetting --> Ready : Repository reset
    
    Operating --> HardReset : hard_reset()
    HardReset --> Closed : close()
    Closed --> Starting : start()
    
    Ready --> Closed : close()
    Operating --> Closed : close()
    Closed --> [*]
    
    Ready --> InterruptedSession : interrupt_session()
    Operating --> InterruptedSession : interrupt_session()
    InterruptedSession --> Ready : Session restored
```

**Environment State Lifecycle**

Sources: [sweagent/environment/swe_env.py:109-114](), [sweagent/environment/swe_env.py:135-147](), [sweagent/environment/swe_env.py:168-172]()

---

