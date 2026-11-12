<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/pyxis · page 3 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [args.c](args.c)
- [config.c](config.c)
- [enroot.c](enroot.c)
- [pyxis_slurmd.c](pyxis_slurmd.c)
- [pyxis_slurmstepd.c](pyxis_slurmstepd.c)

</details>



This document provides a high-level architectural overview of Pyxis, describing how the major components interact with Slurm and with each other to provide container execution capabilities. For details on specific components, see [Component Overview](#3.2) and [SPANK Plugin Integration](#3.1).

## System Overview

Pyxis is implemented as a Slurm SPANK (Simple Plugin Architecture for Node job control) plugin that intercepts job execution to provide containerized environments. The plugin consists of two main execution contexts:

1. **slurmstepd context** - Runs within the `slurmstepd` daemon process on compute nodes, managing container lifecycle for job tasks
2. **slurmd context** - Runs within the `slurmd` daemon for post-job cleanup operations

The plugin delegates actual container operations to the Enroot container runtime, acting as a bridge between Slurm's job management and Enroot's container capabilities.

```mermaid
graph TB
    subgraph "Slurm Core"
        srun["srun<br/>User Command"]
        slurmd["slurmd<br/>Node Daemon"]
        slurmstepd["slurmstepd<br/>Step Daemon"]
    end
    
    subgraph "Pyxis Plugin (spank_pyxis.so)"
        stepd_comp["pyxis_slurmstepd.c<br/>Container Lifecycle"]
        slurmd_comp["pyxis_slurmd.c<br/>Job Cleanup"]
        config_comp["config.c<br/>Configuration"]
        args_comp["args.c<br/>Arguments"]
    end
    
    subgraph "Container Runtime"
        enroot_wrapper["enroot.c<br/>Process Wrapper"]
        enroot_bin["enroot binary"]
        importers["Image Importers"]
    end
    
    subgraph "External Resources"
        registries["Container Registries"]
        filesystem["Shared Filesystem"]
    end
    
    srun --> slurmstepd
    slurmd --> slurmd_comp
    slurmstepd --> stepd_comp
    
    stepd_comp --> config_comp
    stepd_comp --> args_comp
    stepd_comp --> enroot_wrapper
    slurmd_comp --> enroot_wrapper
    
    enroot_wrapper --> enroot_bin
    enroot_bin --> importers
    importers --> registries
    importers --> filesystem
    
    style stepd_comp fill:#f9f9f9,stroke:#333,stroke-width:2px
    style enroot_wrapper fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Sources:** [pyxis_slurmstepd.c:1-50](), [pyxis_slurmd.c:1-20](), [enroot.c:1-17]()

## Architectural Layers

Pyxis is organized into distinct functional layers that separate concerns and enable maintainability:

| Layer | Components | Responsibilities |
|-------|------------|------------------|
| **Integration Layer** | [pyxis_slurmstepd.c](), [pyxis_slurmd.c]() | SPANK hook implementations, lifecycle orchestration, Slurm API interactions |
| **Configuration Layer** | [config.c](), [args.c]() | Plugin configuration parsing, command-line argument processing, environment variable handling |
| **Container Abstraction Layer** | [enroot.c]() | Process management for enroot commands, I/O redirection, UID/GID handling |
| **Utility Layer** | [common.c](), [common.h]() | Shared utility functions, memory management, string operations, file I/O |
| **External Integration** | [importer.c](), [caching_importer.sh](), [simple_importer.sh]() | Container image import strategies, registry interactions |

This layered architecture allows the plugin to adapt to changes in either Slurm or Enroot with minimal impact on other components.

**Sources:** [pyxis_slurmstepd.c:27-35](), [config.c:1-99](), [args.c:1-42](), [enroot.c:1-177]()

## Plugin Lifecycle and Hook Points

The plugin implements several SPANK hooks that Slurm invokes at specific points in the job lifecycle. The following diagram shows the hook execution order and the primary responsibilities of each:

```mermaid
sequenceDiagram
    participant Slurm
    participant pyxis_init as "pyxis_slurmstepd_init()"
    participant post_opt as "pyxis_slurmstepd_post_opt()"
    participant user_init as "slurm_spank_user_init()"
    participant task_init as "slurm_spank_task_init()"
    participant task_exit as "slurm_spank_task_exit()"
    participant job_epilog as "slurm_spank_job_epilog()"
    
    Note over Slurm: Plugin Loading Phase
    Slurm->>pyxis_init: Parse plugin config
    pyxis_init-->>Slurm: Register SPANK options
    
    Note over Slurm: Option Processing Phase
    Slurm->>post_opt: Check arguments/environment
    post_opt-->>Slurm: Create runtime directory
    
    Note over Slurm: Job Initialization Phase
    Slurm->>user_init: Per-job initialization
    user_init->>user_init: Initialize shared memory
    user_init->>user_init: Determine container strategy
    user_init-->>Slurm: Setup complete
    
    Note over Slurm: Task Execution Phase (per task)
    Slurm->>task_init: Task startup
    task_init->>task_init: Import/create container
    task_init->>task_init: Start container (SIGSTOP)
    task_init->>task_init: Acquire namespace FDs
    task_init->>task_init: setns() to join namespaces
    task_init-->>Slurm: Task ready in container
    
    Note over Slurm: Task Completion Phase
    Slurm->>task_exit: Task finished
    task_exit->>task_exit: Export container (optional)
    task_exit->>task_exit: Cleanup resources
    task_exit-->>Slurm: Cleanup complete
    
    Note over Slurm: Job Cleanup Phase (slurmd)
    Slurm->>job_epilog: Job complete
    job_epilog->>job_epilog: Remove job containers
    job_epilog-->>Slurm: Cleanup complete
```

**Sources:** [pyxis_slurmstepd.c:116-133](), [pyxis_slurmstepd.c:265-286](), [pyxis_slurmstepd.c:1036-1184](), [pyxis_slurmstepd.c:1308-1407](), [pyxis_slurmstepd.c:1409-1508](), [pyxis_slurmd.c:127-176]()

## Core Data Structures

The plugin maintains state through several key data structures that coordinate between different lifecycle phases:

```mermaid
classDiagram
    class plugin_context {
        +bool enabled
        +int log_fd
        +plugin_config config
        +plugin_args* args
        +job_info job
        +container container
        +int user_init_rv
        +shared_memory* shm
    }
    
    class plugin_config {
        +char runtime_path[PATH_MAX]
        +bool execute_entrypoint
        +container_scope scope
        +bool sbatch_support
        +bool use_enroot_load
        +char importer_path[PATH_MAX]
    }
    
    class plugin_args {
        +char* image
        +char** mounts
        +size_t mounts_len
        +char* workdir
        +char* container_name
        +char* container_name_flags
        +char* container_save
        +int mount_home
        +int remap_root
        +int entrypoint
        +int writable
        +char** env_vars
        +size_t env_vars_len
    }
    
    class job_info {
        +uid_t uid
        +gid_t gid
        +bool privileged
        +uint32_t jobid
        +uint32_t stepid
        +uint32_t local_task_count
        +uint32_t total_task_count
        +char** environ
        +char cwd[PATH_MAX]
    }
    
    class container {
        +char* name
        +char* squashfs_path
        +char* save_path
        +bool reuse_rootfs
        +bool reuse_ns
        +bool temporary_rootfs
        +bool use_enroot_import
        +bool use_enroot_load
        +bool use_importer
        +int userns_fd
        +int mntns_fd
        +int cgroupns_fd
        +int cwd_fd
    }
    
    class shared_memory {
        +pthread_mutex_t mutex
        +atomic_uint init_tasks
        +atomic_uint started_tasks
        +atomic_uint completed_tasks
        +pid_t pid
        +pid_t ns_pid
    }
    
    plugin_context --> plugin_config
    plugin_context --> plugin_args
    plugin_context --> job_info
    plugin_context --> container
    plugin_context --> shared_memory
```

### Structure Responsibilities

| Structure | Defined In | Purpose |
|-----------|-----------|---------|
| `plugin_context` | [pyxis_slurmstepd.c:74-83]() | Global state container for the entire plugin; single static instance shared across all hooks |
| `plugin_config` | [config.h]() | System-level configuration parsed from plugstack.conf; initialized once at plugin load |
| `plugin_args` | [args.h](), [args.c:13-28]() | User-provided arguments from command-line or environment variables; registered as SPANK options |
| `job_info` | [pyxis_slurmstepd.c:53-63]() | Job metadata retrieved from Slurm via SPANK API; includes UID, GID, job IDs, and environment |
| `container` | [pyxis_slurmstepd.c:37-51]() | Container-specific state including name, paths, flags, and namespace file descriptors |
| `shared_memory` | [pyxis_slurmstepd.c:65-72]() | Shared state between multiple tasks in the same job; coordinates single container creation |

**Sources:** [pyxis_slurmstepd.c:37-83](), [pyxis_slurmstepd.c:90-109](), [config.h](), [args.h](), [args.c:13-28]()

## Component Interaction Patterns

### Container Creation Strategy

The plugin determines the appropriate container creation strategy based on user input and configuration. This decision tree is implemented in `slurm_spank_user_init()`:

```mermaid
graph TD
    start["User Input"] --> check_name{"container_name<br/>specified?"}
    
    check_name -->|Yes| check_exists{"Container<br/>exists?"}
    check_name -->|No| new_container["Create temporary container<br/>pyxis_JOBID.STEPID"]
    
    check_exists -->|Running| reuse_ns["Reuse namespaces<br/>reuse_ns = true<br/>reuse_rootfs = true"]
    check_exists -->|Stopped| reuse_rootfs["Reuse filesystem<br/>reuse_rootfs = true"]
    check_exists -->|No| check_image{"image<br/>specified?"}
    
    check_image -->|Yes| determine_import["Determine import method"]
    check_image -->|No| error["Error: container not found"]
    
    new_container --> determine_import
    reuse_rootfs --> determine_import
    
    determine_import --> has_importer{"importer_path<br/>configured?"}
    
    has_importer -->|Yes| use_ext["use_importer = true"]
    has_importer -->|No| check_dockerd{"Image starts with<br/>dockerd://?"}
    
    check_dockerd -->|Yes| use_import["use_enroot_import = true"]
    check_dockerd -->|No| check_load_setting{"use_enroot_load<br/>config?"}
    
    check_load_setting -->|Yes| use_load["use_enroot_load = true"]
    check_load_setting -->|No| use_import
    
    use_ext --> create["enroot_container_create()"]
    use_import --> create
    use_load --> create
    reuse_ns --> skip_create["Skip container creation"]
```

**Sources:** [pyxis_slurmstepd.c:1128-1155]()

### Multi-Task Synchronization

When a job has multiple tasks on a single node, only one task should create and start the container, while all tasks join the same container namespaces. This is coordinated through shared memory:

```mermaid
sequenceDiagram
    participant Task1 as "Task 1 (First)"
    participant Task2 as "Task 2"
    participant TaskN as "Task N (Last)"
    participant SHM as "shared_memory"
    participant Container as "enroot container"
    
    Note over Task1,TaskN: All tasks call enroot_start_once()
    
    Task1->>SHM: pthread_mutex_lock(&shm->mutex)
    Task1->>SHM: shm->init_tasks++
    Task1->>Task1: Check: shm->init_tasks == 1?
    Task1->>Container: enroot_container_create()
    Task1->>Container: enroot_container_start()
    Note over Container: Container sends SIGSTOP to self
    Task1->>SHM: shm->pid = container_pid
    Task1->>SHM: shm->ns_pid = container_pid
    Task1->>SHM: pthread_mutex_unlock()
    
    Task2->>SHM: pthread_mutex_lock(&shm->mutex)
    Task2->>SHM: shm->init_tasks++
    Task2->>Task2: Check: shm->init_tasks == 1?
    Note over Task2: Not first task, skip creation
    Task2->>SHM: Read shm->ns_pid
    Task2->>SHM: pthread_mutex_unlock()
    
    TaskN->>SHM: pthread_mutex_lock(&shm->mutex)
    TaskN->>SHM: shm->init_tasks++
    TaskN->>TaskN: Check: shm->init_tasks == 1?
    TaskN->>SHM: Read shm->ns_pid
    TaskN->>SHM: pthread_mutex_unlock()
    
    Note over Task1,TaskN: All tasks acquire namespace FDs from shm->ns_pid
    
    Task1->>Task1: setns(userns_fd, CLONE_NEWUSER)
    Task1->>Task1: setns(mntns_fd, CLONE_NEWNS)
    Task2->>Task2: setns(userns_fd, CLONE_NEWUSER)
    Task2->>Task2: setns(mntns_fd, CLONE_NEWNS)
    TaskN->>TaskN: setns(userns_fd, CLONE_NEWUSER)
    TaskN->>TaskN: setns(mntns_fd, CLONE_NEWNS)
    
    Note over TaskN: Last task to join stops container
    TaskN->>SHM: atomic_fetch_add(&shm->started_tasks, 1)
    TaskN->>TaskN: Check: started_tasks == local_task_count?
    TaskN->>Container: kill(shm->pid, SIGCONT)
```

**Sources:** [pyxis_slurmstepd.c:1249-1285](), [pyxis_slurmstepd.c:1287-1306](), [pyxis_slurmstepd.c:972-1012](), [pyxis_slurmstepd.c:1324-1407]()

## Enroot Integration Architecture

The plugin communicates with Enroot through process execution wrappers. The `enroot.c` module provides a clean abstraction for invoking enroot commands with appropriate credentials and I/O handling:

```mermaid
graph TB
    subgraph "Plugin Code"
        caller["enroot_container_create()<br/>enroot_container_start()"]
    end
    
    subgraph "enroot.c Wrappers"
        exec_ctx["enroot_exec_ctx()<br/>Context-aware wrapper"]
        exec_wait["enroot_exec_wait()<br/>uid, gid, log_fd, callback, argv"]
        exec["enroot_exec()<br/>Fork and execute"]
        output["enroot_exec_output()<br/>Execute and capture output"]
    end
    
    subgraph "Child Process"
        setup["Setup I/O:<br/>stdin → /dev/null<br/>stdout/stderr → log_fd"]
        creds["Set credentials:<br/>setregid(gid)<br/>setreuid(uid)"]
        callback_fn["Execute callback:<br/>enroot_set_env()"]
        execvpe["execvpe('enroot', argv, environ)"]
    end
    
    subgraph "Enroot Runtime"
        enroot_cmd["enroot import<br/>enroot create<br/>enroot start<br/>enroot list<br/>enroot remove"]
    end
    
    caller --> exec_ctx
    exec_ctx --> exec_wait
    exec_wait --> exec
    exec --> setup
    setup --> creds
    creds --> callback_fn
    callback_fn --> execvpe
    execvpe --> enroot_cmd
    
    caller --> output
    output --> exec_wait
```

### Key Wrapper Functions

| Function | Purpose | Usage Pattern |
|----------|---------|---------------|
| `enroot_exec_ctx()` | Fork and execute enroot command using plugin context | Called from [pyxis_slurmstepd.c:436-439]() with context UID/GID |
| `enroot_exec_wait_ctx()` | Execute and wait for completion | Used for `enroot import`, `enroot create`, `enroot start` |
| `enroot_exec_output_ctx()` | Execute and capture stdout | Used for `enroot list` to query container state |
| `enroot_set_env()` | Callback to prepare environment before exec | Clears unwanted variables, sets ENROOT_* configuration |

**Sources:** [enroot.c:18-176](), [pyxis_slurmstepd.c:436-455](), [pyxis_slurmstepd.c:389-434]()

## Configuration Flow

Configuration data flows from multiple sources and is resolved with specific precedence rules:

```mermaid
graph LR
    subgraph "Configuration Sources"
        plugstack["plugstack.conf<br/>runtime_path=<br/>container_scope=<br/>execute_entrypoint="]
        cli["Command-line<br/>--container-image<br/>--container-mounts<br/>--container-workdir"]
        env["Environment Variables<br/>PYXIS_CONTAINER_IMAGE<br/>PYXIS_CONTAINER_MOUNTS"]
    end
    
    subgraph "Parser Layer"
        config_parse["pyxis_config_parse()<br/>Parse plugin config"]
        args_register["pyxis_args_register()<br/>Register SPANK options"]
        args_check_env["pyxis_args_check_environment_variables()<br/>Fallback to env vars"]
    end
    
    subgraph "Data Structures"
        plugin_config_struct["plugin_config<br/>System settings"]
        plugin_args_struct["plugin_args<br/>User arguments"]
    end
    
    subgraph "Usage"
        user_init_hook["slurm_spank_user_init()<br/>Make decisions"]
        task_init_hook["slurm_spank_task_init()<br/>Execute container"]
    end
    
    plugstack --> config_parse
    config_parse --> plugin_config_struct
    
    cli --> args_register
    args_register --> plugin_args_struct
    
    env --> args_check_env
    args_check_env --> plugin_args_struct
    
    plugin_config_struct --> user_init_hook
    plugin_args_struct --> user_init_hook
    
    user_init_hook --> task_init_hook
```

**Precedence Rules:**
1. Command-line arguments override environment variables (enforced in [args.c:166-237]())
2. User-provided settings (`plugin_args`) override system defaults (`plugin_config`)
3. For tri-state options (`mount_home`, `remap_root`, `entrypoint`, `writable`), value `-1` means "use enroot default"

**Sources:** [config.c:23-98](), [args.c:42-151](), [args.c:166-237](), [args.c:615-628](), [pyxis_slurmstepd.c:116-133](), [pyxis_slurmstepd.c:265-286]()

## Namespace Acquisition Pattern

The plugin joins container namespaces using a synchronized startup mechanism. This is one of the most critical architectural patterns in the system:

```mermaid
sequenceDiagram
    participant Plugin as "slurm_spank_task_init()"
    participant Container as "Container Process"
    participant Kernel as "/proc/{pid}/ns/*"
    
    Note over Plugin,Container: Container started with special command
    Plugin->>Container: enroot start ... "sh -c 'kill -STOP $$; exit 0'"
    Container->>Container: Shell starts in namespaces
    Container->>Container: Sends SIGSTOP to self
    Note over Container: Process stopped but still alive
    
    Plugin->>Plugin: waitpid(pid, &status, WUNTRACED)
    Note over Plugin: Wait returns when child stops
    
    Plugin->>Plugin: Check WIFSTOPPED(status)
    
    Plugin->>Kernel: open("/proc/{pid}/ns/user", O_RDONLY)
    Kernel-->>Plugin: userns_fd
    
    Plugin->>Kernel: open("/proc/{pid}/ns/mnt", O_RDONLY)
    Kernel-->>Plugin: mntns_fd
    
    Plugin->>Kernel: open("/proc/{pid}/ns/cgroup", O_RDONLY)
    Kernel-->>Plugin: cgroupns_fd
    
    Plugin->>Kernel: open("/proc/{pid}/cwd", O_RDONLY)
    Kernel-->>Plugin: cwd_fd
    
    Note over Plugin: All namespace FDs acquired
    
    Plugin->>Plugin: Store FDs in container structure
    
    Note over Plugin: Join the namespaces
    Plugin->>Kernel: setns(userns_fd, CLONE_NEWUSER)
    Plugin->>Kernel: setns(cgroupns_fd, CLONE_NEWCGROUP)
    Plugin->>Kernel: setns(mntns_fd, CLONE_NEWNS)
    Plugin->>Kernel: fchdir(cwd_fd)
    
    Note over Plugin: Last task sends SIGCONT
    Plugin->>Container: kill(pid, SIGCONT)
    Container->>Container: Resume and exit
```

This pattern allows the plugin to:
1. Ensure the container has completed `unshare()` and `pivot_root()` 
2. Acquire file descriptors to all required namespaces while they're stable
3. Join those namespaces from the plugin's process context (which becomes the task process)
4. Resume the container process to allow it to exit cleanly

**Sources:** [pyxis_slurmstepd.c:893-954](), [pyxis_slurmstepd.c:740-799](), [pyxis_slurmstepd.c:1332-1391](), [pyxis_slurmstepd.c:956-970]()

## Job Cleanup Architecture

After job completion, the `slurm_spank_job_epilog()` hook in the slurmd context removes any temporary containers. The cleanup behavior depends on the `container_scope` configuration:

| Scope | Container Name Pattern | Cleanup Behavior |
|-------|------------------------|------------------|
| `SCOPE_GLOBAL` | `pyxis_JOBID.STEPID` | Per-step containers removed after step completion |
| `SCOPE_JOB` | `pyxis_JOBID_...` | All job containers removed in epilog |

The cleanup process identifies containers by parsing output from `enroot list` and matching the name pattern:

```mermaid
graph TD
    epilog["slurm_spank_job_epilog()"] --> check_scope{"container_scope<br/>== SCOPE_JOB?"}
    check_scope -->|No| skip["Skip cleanup"]
    check_scope -->|Yes| list["enroot_exec_output()<br/>enroot list"]
    
    list --> parse["Parse container names"]
    parse --> match["Match pattern:<br/>pyxis_JOBID_*"]
    match --> found{"Match found?"}
    
    found -->|Yes| remove["enroot_exec_wait()<br/>enroot remove -f"]
    found -->|No| done["Done"]
    remove --> parse
```

**Sources:** [pyxis_slurmd.c:127-176](), [pyxis_slurmd.c:52-93](), [config.h]()

---

