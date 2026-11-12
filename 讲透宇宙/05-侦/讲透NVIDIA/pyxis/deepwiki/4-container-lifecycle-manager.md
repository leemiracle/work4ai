<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/pyxis · page 4 Container Lifecycle Manager · fetched 2026-10-26 -->

# Container Lifecycle Manager

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [pyxis_slurmstepd.c](pyxis_slurmstepd.c)

</details>



## Purpose and Scope

The Container Lifecycle Manager is the core orchestration component of Pyxis, implemented in `pyxis_slurmstepd.c`. This module manages the complete lifecycle of containerized job execution within Slurm's `slurmstepd` daemon, from initial configuration parsing through container creation, namespace management, task execution, and final cleanup.

This page provides an architectural overview of the lifecycle manager and its coordination mechanisms. For specific implementation details, see:
- [Initialization & Setup](#4.1) - configuration parsing and runtime directory setup
- [Container Creation](#4.2) - image import and container creation strategies
- [Namespace Management](#4.3) - Linux namespace acquisition and multi-task coordination
- [Environment & Execution](#4.4) - environment variable handling and task execution
- [Cleanup & Teardown](#4.5) - container export and resource cleanup

For information about the configuration system used by this module, see [Configuration System](#5). For argument parsing, see [Argument Parsing](#6).

**Sources:** [pyxis_slurmstepd.c:1-1546]()

## Core Architecture

The Container Lifecycle Manager operates as a SPANK plugin within Slurm's `slurmstepd` daemon. It maintains a global `plugin_context` structure that tracks the state of container operations across multiple SPANK hook invocations.

### Key Data Structures

The lifecycle manager uses four primary data structures to manage container state:

| Structure | Purpose | Key Fields | Scope |
|-----------|---------|------------|-------|
| `plugin_context` | Global plugin state | `config`, `args`, `job`, `container`, `shm` | Per-job-step, singleton |
| `plugin_config` | Plugin configuration | `runtime_path`, `container_scope`, `importer_path` | Parsed at init |
| `plugin_args` | User arguments | `image`, `mounts`, `workdir`, `entrypoint` | From CLI/env vars |
| `job_info` | Job metadata | `uid`, `gid`, `jobid`, `stepid`, `task_count` | From SPANK API |
| `container` | Container state | `name`, `squashfs_path`, namespace FDs, flags | Runtime state |
| `shared_memory` | Multi-task sync | `mutex`, `init_tasks`, `started_tasks`, `pid` | Shared across tasks |

**Sources:** [pyxis_slurmstepd.c:37-109]()

### Plugin Context Structure

```mermaid
graph TB
    subgraph "plugin_context (singleton)"
        ENABLED["enabled: bool"]
        CONFIG["config: plugin_config"]
        ARGS["args: plugin_args*"]
        JOB["job: job_info"]
        CONTAINER["container: struct container"]
        SHM["shm: shared_memory*"]
        LOG_FD["log_fd: int"]
    end
    
    subgraph "plugin_config"
        RUNTIME_PATH["runtime_path: char[]"]
        SCOPE["container_scope: enum"]
        IMPORTER["importer_path: char[]"]
        ENROOT_LOAD["use_enroot_load: bool"]
    end
    
    subgraph "plugin_args"
        IMAGE["image: char*"]
        MOUNTS["mounts: char**"]
        WORKDIR["workdir: char*"]
        CONTAINER_NAME["container_name: char*"]
    end
    
    subgraph "job_info"
        UID["uid: uid_t"]
        GID["gid: gid_t"]
        JOBID["jobid: uint32_t"]
        STEPID["stepid: uint32_t"]
        TASK_COUNT["local_task_count: uint32_t"]
    end
    
    subgraph "container"
        CTR_NAME["name: char*"]
        SQFS_PATH["squashfs_path: char*"]
        USERNS_FD["userns_fd: int"]
        MNTNS_FD["mntns_fd: int"]
        REUSE_FLAGS["reuse_rootfs, reuse_ns: bool"]
    end
    
    CONFIG --> ENABLED
    ARGS --> ENABLED
    JOB --> ENABLED
    CONTAINER --> ENABLED
    SHM --> ENABLED
    LOG_FD --> ENABLED
```

**Sources:** [pyxis_slurmstepd.c:74-109]()

## SPANK Hook Functions

The lifecycle manager implements six SPANK hook functions that are invoked by Slurm at specific points in the job lifecycle:

| Hook Function | When Called | Primary Responsibilities |
|---------------|-------------|--------------------------|
| `pyxis_slurmstepd_init()` | Plugin load | Parse configuration, register arguments |
| `pyxis_slurmstepd_post_opt()` | After CLI parsing | Check environment variables, create runtime directories |
| `slurm_spank_user_init()` | Before task init | Set up shared memory, determine container strategy, handle batch scripts |
| `slurm_spank_task_init()` | Per-task init | Create/start container, acquire namespaces, join namespaces |
| `slurm_spank_task_exit()` | Per-task exit | Export container (last task), cleanup temporary containers |
| `pyxis_slurmstepd_exit()` | Plugin unload | Free resources, destroy shared memory |

**Sources:** [pyxis_slurmstepd.c:116-133](), [pyxis_slurmstepd.c:265-286](), [pyxis_slurmstepd.c:1036-1184](), [pyxis_slurmstepd.c:1308-1409](), [pyxis_slurmstepd.c:1491-1511](), [pyxis_slurmstepd.c:1513-1545]()

### SPANK Hook Invocation Flow

```mermaid
sequenceDiagram
    participant Slurm as "slurmstepd daemon"
    participant Init as "pyxis_slurmstepd_init"
    participant PostOpt as "pyxis_slurmstepd_post_opt"
    participant UserInit as "slurm_spank_user_init"
    participant TaskInit as "slurm_spank_task_init (per-task)"
    participant TaskExit as "slurm_spank_task_exit (per-task)"
    participant Exit as "pyxis_slurmstepd_exit"
    
    Slurm->>Init: Plugin load
    Init->>Init: "pyxis_config_parse()"
    Init->>Init: "pyxis_args_register()"
    Init-->>Slurm: Return 0
    
    Slurm->>PostOpt: After argument parsing
    PostOpt->>PostOpt: "pyxis_args_check_environment_variables()"
    PostOpt->>PostOpt: "job_get_info()"
    PostOpt->>PostOpt: "enroot_create_user_runtime_dir()"
    PostOpt-->>Slurm: Return 0
    
    Slurm->>UserInit: Before tasks spawn (once)
    UserInit->>UserInit: "shm_init()"
    UserInit->>UserInit: "Determine container strategy"
    UserInit->>UserInit: "Setup container name"
    UserInit-->>Slurm: Return 0
    
    loop For each task
        Slurm->>TaskInit: Task initialization
        TaskInit->>TaskInit: "enroot_start_once()"
        TaskInit->>TaskInit: "container_get_namespaces()"
        TaskInit->>TaskInit: "setns() calls"
        TaskInit->>TaskInit: "chdir()"
        TaskInit-->>Slurm: Return 0
        
        Note over Slurm,TaskInit: Task executes in container
        
        Slurm->>TaskExit: Task completion
        TaskExit->>TaskExit: "enroot_export() (last task)"
        TaskExit->>TaskExit: "enroot_cleanup() (last task)"
        TaskExit-->>Slurm: Return 0
    end
    
    Slurm->>Exit: Plugin unload
    Exit->>Exit: "Free all resources"
    Exit->>Exit: "shm_destroy()"
    Exit->>Exit: "pyxis_args_free()"
    Exit-->>Slurm: Return 0
```

**Sources:** [pyxis_slurmstepd.c:116-133](), [pyxis_slurmstepd.c:265-286](), [pyxis_slurmstepd.c:1036-1184](), [pyxis_slurmstepd.c:1308-1409](), [pyxis_slurmstepd.c:1491-1511](), [pyxis_slurmstepd.c:1513-1545]()

## Container Lifecycle Phases

The container lifecycle consists of five distinct phases, each handled by specific functions within the lifecycle manager:

### Lifecycle Phase Diagram

```mermaid
stateDiagram-v2
    [*] --> Configuration: "pyxis_slurmstepd_init()"
    Configuration --> RuntimeSetup: "pyxis_slurmstepd_post_opt()"
    RuntimeSetup --> StrategyDetermination: "slurm_spank_user_init()"
    
    state StrategyDetermination {
        [*] --> CheckContainerName
        CheckContainerName --> ReuseNamespaces: "container exists, running"
        CheckContainerName --> ReuseFilesystem: "container exists, stopped"
        CheckContainerName --> CreateNew: "container doesn't exist"
        CheckContainerName --> CreateNew: "no --container-name"
        
        ReuseNamespaces --> [*]: "reuse_ns = true"
        ReuseFilesystem --> [*]: "reuse_rootfs = true"
        CreateNew --> ImageResolution
        ImageResolution --> [*]: "Set import strategy"
    }
    
    StrategyDetermination --> ContainerCreation: "slurm_spank_task_init() (first task)"
    
    state ContainerCreation {
        [*] --> ImportImage: "if !reuse_rootfs"
        ImportImage --> CreateFilesystem: "enroot_container_create()"
        CreateFilesystem --> StartContainer
        [*] --> StartContainer: "if reuse_rootfs"
        StartContainer --> AcquireNamespaces: "enroot_container_start()"
        AcquireNamespaces --> [*]: "container_get_namespaces()"
    }
    
    ContainerCreation --> NamespaceJoining: "slurm_spank_task_init() (all tasks)"
    
    state NamespaceJoining {
        [*] --> JoinUserNS: "setns(userns_fd)"
        JoinUserNS --> JoinCgroupNS: "setns(cgroupns_fd)"
        JoinCgroupNS --> JoinMountNS: "setns(mntns_fd)"
        JoinMountNS --> ChangeDir: "chdir(workdir or cwd_fd)"
        ChangeDir --> SetSeccomp: "seccomp_set_filter()"
        SetSeccomp --> [*]
    }
    
    NamespaceJoining --> TaskExecution: "All tasks joined"
    TaskExecution --> Cleanup: "slurm_spank_task_exit() (last task)"
    
    state Cleanup {
        [*] --> Export: "if container_save != NULL"
        Export --> RemoveContainer: "if temporary_rootfs"
        [*] --> RemoveContainer: "if no export"
        RemoveContainer --> [*]: "enroot_cleanup()"
    }
    
    Cleanup --> [*]: "pyxis_slurmstepd_exit()"
```

**Sources:** [pyxis_slurmstepd.c:116-1545]()

## Multi-Task Coordination

When a Slurm job spawns multiple tasks on a single node, all tasks must share the same container. The lifecycle manager uses POSIX shared memory with a mutex to coordinate container creation and ensure only one task creates/starts the container.

### Shared Memory Structure

The `shared_memory` structure provides process-shared synchronization:

```c
struct shared_memory {
    pthread_mutex_t mutex;        // Process-shared, robust mutex
    atomic_uint init_tasks;       // Count of tasks in initialization
    atomic_uint started_tasks;    // Count of tasks that joined namespaces
    atomic_uint completed_tasks;  // Count of tasks that exited
    pid_t pid;                    // Container process PID
    pid_t ns_pid;                 // PID to get namespaces from
};
```

**Sources:** [pyxis_slurmstepd.c:65-72]()

### Multi-Task Synchronization Flow

```mermaid
sequenceDiagram
    participant T1 as "Task 1"
    participant T2 as "Task 2"
    participant TN as "Task N"
    participant SHM as "shared_memory"
    participant Container as "Container Process"
    
    Note over T1,TN: "slurm_spank_task_init() called for each task"
    
    T1->>SHM: "pthread_mutex_lock(&shm->mutex)"
    T1->>SHM: "shm->init_tasks += 1 (now 1)"
    
    rect rgb(240, 240, 240)
        Note over T1: "First task creates container"
        T1->>T1: "enroot_container_create()"
        T1->>Container: "enroot_container_start()"
        Container-->>Container: "kill -STOP $$"
        T1->>T1: "waitpid(pid, WUNTRACED)"
        T1->>SHM: "shm->pid = container_pid"
        T1->>SHM: "shm->ns_pid = container_pid"
        T1->>Container: "container_get_namespaces()"
    end
    
    T1->>SHM: "pthread_mutex_unlock(&shm->mutex)"
    
    T2->>SHM: "pthread_mutex_lock(&shm->mutex)"
    T2->>SHM: "shm->init_tasks += 1 (now 2)"
    T2->>T2: "Skip creation, use shm->ns_pid"
    T2->>SHM: "pthread_mutex_unlock(&shm->mutex)"
    
    TN->>SHM: "pthread_mutex_lock(&shm->mutex)"
    TN->>SHM: "shm->init_tasks += 1 (now N)"
    TN->>TN: "Skip creation, use shm->ns_pid"
    TN->>SHM: "pthread_mutex_unlock(&shm->mutex)"
    
    par All tasks join namespaces
        T1->>T1: "setns(userns_fd, mntns_fd, cgroupns_fd)"
        T2->>T2: "setns(userns_fd, mntns_fd, cgroupns_fd)"
        TN->>TN: "setns(userns_fd, mntns_fd, cgroupns_fd)"
    end
    
    T1->>SHM: "atomic_fetch_add(&shm->started_tasks, 1)"
    T2->>SHM: "atomic_fetch_add(&shm->started_tasks, 1)"
    TN->>SHM: "atomic_fetch_add(&shm->started_tasks, 1) == N-1"
    
    rect rgb(240, 240, 240)
        Note over TN: "Last task to start resumes container"
        TN->>Container: "kill(pid, SIGCONT)"
        TN->>SHM: "shm->pid = -1"
    end
    
    Note over T1,TN: "Tasks execute in container..."
    
    Note over T1,TN: "slurm_spank_task_exit() called for each task"
    
    T1->>SHM: "atomic_fetch_add(&shm->completed_tasks, 1)"
    T2->>SHM: "atomic_fetch_add(&shm->completed_tasks, 1)"
    TN->>SHM: "atomic_fetch_add(&shm->completed_tasks, 1) == N-1"
    
    rect rgb(240, 240, 240)
        Note over TN: "Last task to exit does cleanup"
        TN->>TN: "enroot_export()"
        TN->>TN: "enroot_cleanup()"
    end
```

**Sources:** [pyxis_slurmstepd.c:972-1012](), [pyxis_slurmstepd.c:1249-1285](), [pyxis_slurmstepd.c:1287-1306](), [pyxis_slurmstepd.c:1499-1508]()

### Coordination Functions

| Function | Purpose | Critical Section |
|----------|---------|------------------|
| `shm_init()` | Create shared memory mapping | Initialize process-shared mutex with `PTHREAD_PROCESS_SHARED` and `PTHREAD_MUTEX_ROBUST` |
| `enroot_start_once()` | Ensure single container creation | Mutex-protected, first task creates/starts, others wait and reuse |
| `enroot_stop_once()` | Resume container after all tasks ready | Atomic counter, last task sends `SIGCONT` |
| `enroot_export()` / `enroot_cleanup()` | Single cleanup execution | Atomic counter in `slurm_spank_task_exit()`, last task performs cleanup |
| `shm_destroy()` | Clean up shared memory | Destroy mutex and unmap memory |

**Sources:** [pyxis_slurmstepd.c:972-1012](), [pyxis_slurmstepd.c:1249-1306](), [pyxis_slurmstepd.c:1440-1489](), [pyxis_slurmstepd.c:1014-1034]()

## Container Strategy Selection

The lifecycle manager supports three container strategies, determined in `slurm_spank_user_init()`:

### Strategy Decision Tree

```mermaid
graph TB
    Start["slurm_spank_user_init()"]
    Start --> CheckName{"--container-name<br/>specified?"}
    
    CheckName -->|"Yes"| GetContainer["enroot_container_get(name, &pid)"]
    CheckName -->|"No"| AutoName["Generate name:<br/>pyxis_jobid.stepid"]
    
    GetContainer --> CheckPID{"Container<br/>status?"}
    CheckPID -->|"pid > 0 (running)"| CheckFlags1{"container_name_flags<br/>= 'exec'?"}
    CheckPID -->|"pid == 0 (stopped)"| CheckFlags2{"container_name_flags<br/>= 'no_exec'?"}
    CheckPID -->|"pid < 0 (not exist)"| CheckFlags3{"Has --container-image?"}
    
    CheckFlags1 -->|"Yes or not set"| ReuseNS["Strategy: REUSE_NS<br/>reuse_ns = true<br/>reuse_rootfs = true<br/>shm->ns_pid = pid"]
    CheckFlags1 -->|"No (error)"| Error1["Error: exec flag<br/>but not running"]
    
    CheckFlags2 -->|"Yes"| ReuseFS["Strategy: REUSE_FS<br/>reuse_rootfs = true<br/>temporary_rootfs = false"]
    CheckFlags2 -->|"No"| ReuseFS
    
    CheckFlags3 -->|"Yes"| CreateNamed["Strategy: CREATE<br/>temporary_rootfs = false<br/>Proceed to image import"]
    CheckFlags3 -->|"No"| Error2["Error: container<br/>doesn't exist,<br/>no image"]
    
    AutoName --> CreateTemp["Strategy: CREATE<br/>temporary_rootfs = true<br/>Proceed to image import"]
    
    ReuseNS --> SkipImport["Skip image import<br/>Skip container creation<br/>Skip container start"]
    ReuseFS --> SkipCreate["Skip image import<br/>Skip container creation"]
    CreateNamed --> ImagePath["Determine image<br/>import path"]
    CreateTemp --> ImagePath
    
    ImagePath --> CheckImagePath{"Image path<br/>starts with<br/>'./' or '/'?"}
    CheckImagePath -->|"Yes"| LocalPath["Use local squashfs:<br/>squashfs_path = image"]
    CheckImagePath -->|"No"| CheckImporter{"Importer<br/>configured?"}
    
    CheckImporter -->|"Yes"| UseImporter["use_importer = true"]
    CheckImporter -->|"No"| CheckDockerd{"Image starts<br/>with 'dockerd://'?"}
    
    CheckDockerd -->|"Yes"| UseImport["use_enroot_import = true"]
    CheckDockerd -->|"No"| CheckLoadConfig{"config.use_enroot_load<br/>= true?"}
    
    CheckLoadConfig -->|"Yes"| UseLoad["use_enroot_load = true"]
    CheckLoadConfig -->|"No"| UseImport
    
    LocalPath --> Done["Ready for task_init"]
    UseImporter --> Done
    UseLoad --> Done
    UseImport --> Done
    SkipImport --> Done
    SkipCreate --> Done
```

**Sources:** [pyxis_slurmstepd.c:1078-1167]()

## Integration with Other Components

The Container Lifecycle Manager coordinates with multiple other Pyxis components:

### Component Dependencies

```mermaid
graph LR
    subgraph "pyxis_slurmstepd.c (117.69)"
        LIFECYCLE["Container Lifecycle Manager"]
        SPANK_HOOKS["SPANK Hook Functions"]
        SHM["Shared Memory<br/>Coordination"]
        NS_MGMT["Namespace<br/>Management"]
    end
    
    subgraph "config.c (17.50)"
        CONFIG_PARSE["pyxis_config_parse()"]
        PLUGIN_CONFIG["plugin_config structure"]
    end
    
    subgraph "args.c (25.62)"
        ARGS_REGISTER["pyxis_args_register()"]
        ARGS_CHECK_ENV["pyxis_args_check_environment_variables()"]
        ARGS_ENABLED["pyxis_args_enabled()"]
        PLUGIN_ARGS["plugin_args structure"]
    end
    
    subgraph "enroot.c (12.58)"
        ENROOT_EXEC["enroot_exec()"]
        ENROOT_EXEC_WAIT["enroot_exec_wait()"]
        ENROOT_EXEC_OUTPUT["enroot_exec_output()"]
    end
    
    subgraph "importer.c/h"
        IMPORTER_GET["importer_exec_get()"]
        IMPORTER_RELEASE["importer_exec_release()"]
    end
    
    subgraph "common.c (8.53)"
        XASPRINTF["xasprintf()"]
        GET_LINE["get_line_from_file()"]
        MEMFD_CREATE["pyxis_memfd_create()"]
        ARRAY_CONTAINS["array_contains()"]
    end
    
    subgraph "Slurm SPANK API"
        SPANK_GET_ITEM["spank_get_item()"]
        SPANK_GETENV["spank_getenv()"]
        SPANK_SETENV["spank_setenv()"]
    end
    
    SPANK_HOOKS --> CONFIG_PARSE
    CONFIG_PARSE --> PLUGIN_CONFIG
    PLUGIN_CONFIG --> LIFECYCLE
    
    SPANK_HOOKS --> ARGS_REGISTER
    SPANK_HOOKS --> ARGS_CHECK_ENV
    SPANK_HOOKS --> ARGS_ENABLED
    ARGS_REGISTER --> PLUGIN_ARGS
    ARGS_CHECK_ENV --> PLUGIN_ARGS
    ARGS_ENABLED --> PLUGIN_ARGS
    PLUGIN_ARGS --> LIFECYCLE
    
    LIFECYCLE --> ENROOT_EXEC
    LIFECYCLE --> ENROOT_EXEC_WAIT
    LIFECYCLE --> ENROOT_EXEC_OUTPUT
    
    LIFECYCLE --> IMPORTER_GET
    LIFECYCLE --> IMPORTER_RELEASE
    
    LIFECYCLE --> XASPRINTF
    LIFECYCLE --> GET_LINE
    LIFECYCLE --> MEMFD_CREATE
    LIFECYCLE --> ARRAY_CONTAINS
    
    SPANK_HOOKS --> SPANK_GET_ITEM
    SPANK_HOOKS --> SPANK_GETENV
    SPANK_HOOKS --> SPANK_SETENV
```

**Sources:** [pyxis_slurmstepd.c:28-35]()

### Key Integration Points

| Component | Functions Used | Purpose |
|-----------|----------------|---------|
| **config.c** | `pyxis_config_parse()` | Parse plugin configuration from plugstack.conf |
| **args.c** | `pyxis_args_register()`, `pyxis_args_check_environment_variables()`, `pyxis_args_enabled()` | Register CLI options, check environment fallbacks, validate arguments |
| **enroot.c** | `enroot_exec()`, `enroot_exec_wait()`, `enroot_exec_output()` | Execute enroot commands with proper UID/GID and I/O handling |
| **importer.c** | `importer_exec_get()`, `importer_exec_release()` | Use external importer for image caching |
| **common.c** | `xasprintf()`, `get_line_from_file()`, `pyxis_memfd_create()`, `array_contains()` | Utility functions for string formatting, file I/O, logging |
| **SPANK API** | `spank_get_item()`, `spank_getenv()`, `spank_setenv()` | Query job information, manage environment variables |

**Sources:** [pyxis_slurmstepd.c:116-133](), [pyxis_slurmstepd.c:265-286](), [pyxis_slurmstepd.c:436-449](), [pyxis_slurmstepd.c:692-698](), [pyxis_slurmstepd.c:1469-1476]()

## Container Process Synchronization

The lifecycle manager uses a sophisticated synchronization technique to acquire container namespace file descriptors. The container is started with a shell command that stops itself using `SIGSTOP`, allowing the plugin to acquire namespace handles before the container continues execution.

### SIGSTOP Synchronization Mechanism

```mermaid
sequenceDiagram
    participant Plugin as "pyxis_slurmstepd"
    participant Fork as "fork()"
    participant Enroot as "enroot start"
    participant Shell as "sh -c 'kill -STOP $$'"
    participant Kernel as "Linux Kernel"
    
    Plugin->>Fork: "enroot_exec_ctx()"
    Fork->>Enroot: "exec enroot start ... sh -c 'kill -STOP $$; exit 0'"
    Enroot->>Enroot: "unshare() namespaces"
    Enroot->>Enroot: "pivot_root()"
    Enroot->>Shell: "exec sh -c ..."
    Shell->>Shell: "kill -STOP $$"
    Shell->>Kernel: "SIGSTOP to self"
    
    Note over Shell,Kernel: "Container process stopped"
    
    Plugin->>Plugin: "waitpid(pid, &status, WUNTRACED)"
    Plugin->>Plugin: "Check WIFSTOPPED(status)"
    
    rect rgb(240, 240, 240)
        Note over Plugin: "Container is stopped,<br/>namespaces are stable"
        Plugin->>Plugin: "open(/proc/pid/ns/user)"
        Plugin->>Plugin: "open(/proc/pid/ns/mnt)"
        Plugin->>Plugin: "open(/proc/pid/ns/cgroup)"
        Plugin->>Plugin: "open(/proc/pid/cwd)"
    end
    
    Plugin->>Plugin: "Store FDs in context.container"
    
    Note over Plugin: "Wait for all tasks<br/>to acquire FDs..."
    
    Plugin->>Shell: "kill(pid, SIGCONT)"
    Shell->>Shell: "Resume execution"
    Shell->>Shell: "exit 0"
```

**Sources:** [pyxis_slurmstepd.c:893-954](), [pyxis_slurmstepd.c:909-942](), [pyxis_slurmstepd.c:956-970]()

### Container Start Implementation

The `enroot_container_start()` function creates a temporary configuration file and starts the container with the synchronization shell command:

**Key Steps:**
1. Create temporary enroot configuration with mounts and hooks via `enroot_create_start_config()`
2. Start container: `enroot start --conf <file> <name> sh -c "kill -STOP $$ ; exit 0"`
3. Wait for container to stop with `waitpid(pid, &status, WUNTRACED)`
4. Verify `WIFSTOPPED(status)` is true
5. Acquire namespace file descriptors via `container_get_namespaces()`
6. Return container PID to caller

**Sources:** [pyxis_slurmstepd.c:893-954](), [pyxis_slurmstepd.c:801-891](), [pyxis_slurmstepd.c:740-781]()

## Environment Management

The lifecycle manager carefully manages environment variables to ensure proper isolation between Slurm's environment and the container's environment, while selectively importing required variables.

### Environment Variable Flow

```mermaid
graph TB
    subgraph "Slurm Job Environment"
        SLURM_ENV["Job environment<br/>(S_JOB_ENV from SPANK)"]
    end
    
    subgraph "Environment Filtering"
        CLEAR["slurm_clear_env()<br/>Clear slurmstepd env"]
        DENY["enroot_deny_env[]<br/>Blocked variables"]
        IMPORT["enroot_import_job_env()<br/>Import allowed vars"]
    end
    
    subgraph "Enroot Process Environment"
        ENROOT_ENV["Enroot command environment"]
        PYXIS_VARS["PYXIS_* variables"]
        ENROOT_CONFIG["ENROOT_* config"]
        ENROOT_OPTS["ENROOT_* options"]
    end
    
    subgraph "Container Process"
        CONTAINER_ENV["/proc/PID/environ"]
    end
    
    subgraph "Task Environment (SPANK)"
        TASK_ENV["Task environment<br/>after spank_import_container_env()"]
        CONTAINER_DENY["container_deny_env[]<br/>(LANG, LC_ALL, etc)"]
    end
    
    SLURM_ENV --> CLEAR
    CLEAR --> IMPORT
    SLURM_ENV --> DENY
    DENY -.blocks.-> IMPORT
    
    IMPORT --> ENROOT_ENV
    PYXIS_VARS --> ENROOT_ENV
    ENROOT_CONFIG --> ENROOT_ENV
    ENROOT_OPTS --> ENROOT_ENV
    
    ENROOT_ENV --> CONTAINER_ENV
    
    CONTAINER_ENV --> TASK_ENV
    CONTAINER_DENY -.removes.-> TASK_ENV
```

**Sources:** [pyxis_slurmstepd.c:300-434](), [pyxis_slurmstepd.c:590-641]()

### Denied Environment Variables

Two lists control environment variable filtering:

**Denied from Enroot** (`enroot_deny_env[]`):
- `PATH`, `LD_LIBRARY_PATH`, `LD_PRELOAD` - prevent host contamination
- `SLURM_PROCID`, `SLURM_LOCALID`, `SLURM_TASK_PID` - task-specific, set later
- `PMIX_RANK`, `PMI_FD` - PMI coordination, set later
- `ENROOT_*` - all enroot configuration variables

**Denied from Container** (`container_deny_env[]`):
- `LANG`, `LANGUAGE`, `LC_ALL` - locale variables (unless in `--container-env`)

**Sources:** [pyxis_slurmstepd.c:334-359](), [pyxis_slurmstepd.c:583-588]()

## Error Handling and Robustness

The lifecycle manager implements several robustness features:

### Mutex Robustness

The shared memory mutex uses `PTHREAD_MUTEX_ROBUST`, allowing recovery if a task crashes while holding the lock:

```c
// In shm_init()
pthread_mutexattr_setrobust(&mutex_attr, PTHREAD_MUTEX_ROBUST);

// In enroot_start_once()
if (pthread_mutex_lock(&shm->mutex) == EOWNERDEAD) {
    pthread_mutex_consistent(&shm->mutex);
    shm->pid = -1;
    shm->ns_pid = -1;
    goto fail;  // Treat as failure, retry
}
```

**Sources:** [pyxis_slurmstepd.c:992-994](), [pyxis_slurmstepd.c:1254-1259]()

### User Init Error Propagation

Due to a Slurm limitation ([bug #7573](https://bugs.schedmd.com/show_bug.cgi?id=7573)), errors from `slurm_spank_user_init()` are not propagated to `srun`. The lifecycle manager works around this by storing the error code and returning it in `slurm_spank_task_init()`:

**Sources:** [pyxis_slurmstepd.c:1171-1183](), [pyxis_slurmstepd.c:1316-1317]()

### Partial Initialization Cleanup

If container startup fails partway through, the lifecycle manager tracks what resources were allocated and cleans them up appropriately:

| Resource | Cleanup Function | When Cleaned |
|----------|------------------|--------------|
| Temporary squashfs | `unlink()` in `enroot_cleanup()` | If `use_enroot_import` is true |
| Importer resources | `importer_exec_release()` | If `use_importer` is true |
| Container filesystem | `enroot remove -f` | If `temporary_rootfs` is true |
| Shared memory | `shm_destroy()` | In `pyxis_slurmstepd_exit()` |
| Namespace FDs | `xclose()` | In `pyxis_slurmstepd_exit()` |

**Sources:** [pyxis_slurmstepd.c:1460-1489](), [pyxis_slurmstepd.c:1513-1545]()

---

