<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvrc · page 5 System Services · fetched 2026-10-26 -->

# System Services

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/daemon.rs](src/daemon.rs)
- [src/lockdown.rs](src/lockdown.rs)
- [src/user_group.rs](src/user_group.rs)

</details>



This page documents the management of system daemons and infrastructure services within NVRC. It covers daemon lifecycle management, user identity management, and security hardening mechanisms that support the overall GPU management system.

For information about filesystem setup and device mounting, see [Filesystem Setup](#3.1). For details about container integration services, see [Container Integration](#4.4).

## Overview

NVRC manages several critical system services that enable GPU functionality in containerized environments. The system services subsystem is responsible for:

- Managing NVIDIA daemon processes (nvidia-persistenced, nv-hostengine, dcgm-exporter)
- Creating and managing user/group identities for service isolation
- Implementing security hardening measures including module loading restrictions
- Handling process lifecycle operations (start, stop, restart)

## System Services Architecture

```mermaid
graph TB
    subgraph "NVRC Core"
        NVRC_STRUCT["NVRC Struct"]
    end
    
    subgraph "Daemon Management"
        DAEMON_RS["daemon.rs"]
        PERSISTENCED["nvidia-persistenced"]
        HOSTENGINE["nv-hostengine"] 
        DCGM_EXPORTER["dcgm-exporter"]
        NVIDIA_SMI["nvidia-smi"]
    end
    
    subgraph "Identity Management"
        USER_GROUP_RS["user_group.rs"]
        PASSWD_FILE["/etc/passwd"]
        SHADOW_FILE["/etc/shadow"]
        GROUP_FILE["/etc/group"]
    end
    
    subgraph "Security Hardening"
        LOCKDOWN_RS["lockdown.rs"]
        PANIC_HOOK["Panic Hook"]
        MODULE_DISABLE["Module Loading Disable"]
    end
    
    NVRC_STRUCT --> DAEMON_RS
    DAEMON_RS --> PERSISTENCED
    DAEMON_RS --> HOSTENGINE
    DAEMON_RS --> DCGM_EXPORTER
    DAEMON_RS --> NVIDIA_SMI
    
    NVRC_STRUCT --> USER_GROUP_RS
    USER_GROUP_RS --> PASSWD_FILE
    USER_GROUP_RS --> SHADOW_FILE
    USER_GROUP_RS --> GROUP_FILE
    
    NVRC_STRUCT --> LOCKDOWN_RS
    LOCKDOWN_RS --> PANIC_HOOK
    LOCKDOWN_RS --> MODULE_DISABLE
    
    DAEMON_RS -.-> USER_GROUP_RS
```

Sources: [src/daemon.rs:1-224](), [src/user_group.rs:1-377](), [src/lockdown.rs:1-21]()

## Daemon Lifecycle Management

NVRC implements a comprehensive daemon management system through the `daemon.rs` module. The system supports three primary actions for each managed daemon:

| Action | Purpose | Implementation |
|--------|---------|----------------|
| `Start` | Initialize daemon process | `background()` function with process tracking |
| `Stop` | Terminate daemon gracefully | `kill()` followed by `kill_processes_by_comm()` |
| `Restart` | Stop then start sequence | Combined stop and start operations |

### Managed Daemons

#### NVIDIA Persistence Daemon

The `nvidia_persistenced` daemon maintains GPU state across driver unloads. Configuration depends on system settings:

```mermaid
flowchart TD
    START["nvidia_persistenced()"]
    CHECK_UVM["Check UVM persistence mode"]
    CHECK_CC["Check GPU CC mode"]
    CREATE_DIR["Create /var/run/nvidia-persistenced"]
    SET_PERMS["Set directory permissions"]
    BUILD_ARGS["Build command arguments"]
    EXECUTE["Execute daemon"]
    
    START --> CHECK_UVM
    CHECK_UVM --> CHECK_CC
    CHECK_CC --> CREATE_DIR
    CREATE_DIR --> SET_PERMS
    SET_PERMS --> BUILD_ARGS
    BUILD_ARGS --> EXECUTE
    
    CHECK_UVM --> |"on"| UVM_ON["Add --uvm-persistence-mode"]
    CHECK_UVM --> |"off"| UVM_OFF["No UVM flag"]
    CHECK_UVM --> |"None/other"| UVM_DEFAULT["Default to on"]
    
    CHECK_CC --> |"on"| CC_ROOT["Run as root (CC mode)"]
    CHECK_CC --> |"off"| CC_USER["Run as configured user/group"]
```

Sources: [src/daemon.rs:129-178]()

#### Data Center GPU Manager Services

For systems with DCGM enabled, NVRC manages two additional services:

- **nv-hostengine**: DCGM host engine service
- **dcgm-exporter**: Metrics exporter for monitoring

Both services are conditionally started based on the `dcgm_enabled` configuration flag.

Sources: [src/daemon.rs:180-208]()

### Process Management Implementation

The daemon management system uses two execution modes:

| Mode | Function | Use Case |
|------|----------|----------|
| Foreground | `foreground()` | One-time commands (nvidia-smi) |
| Background | `background()` | Long-running daemons |

Both modes redirect stdout/stderr to the kernel message buffer via `kmsg()` for centralized logging.

Sources: [src/daemon.rs:47-78]()

## User Identity Management

The `user_group.rs` module provides user and group management capabilities for service isolation and security.

### UserGroup Structure

```mermaid
classDiagram
    class UserGroup {
        +Uid user_id
        +Gid group_id
        +String user_name
        +String group_name
        +new() UserGroup
        +root() UserGroup
        +with_ids() UserGroup
        +write_to_system_files() Result
    }
    
    class SystemFiles {
        +passwd_entry() String
        +shadow_entry() String  
        +group_entry() String
    }
    
    UserGroup --> SystemFiles : generates
```

Sources: [src/user_group.rs:14-44]()

### Random User Generation

For enhanced security, NVRC can generate random user accounts with:

- User IDs in range 1000-60000
- 8-character lowercase alphabetic usernames
- Matching group names
- Disabled password authentication

```mermaid
sequenceDiagram
    participant Caller as "System Initialization"
    participant RNG as "random_user_group()"
    participant UserGroup as "UserGroup"
    participant Files as "System Files"
    
    Caller->>RNG: "Generate random identity"
    RNG->>RNG: "Generate UID/GID (1000-60000)"
    RNG->>RNG: "Generate 8-char username"
    RNG->>UserGroup: "with_ids(uid, gid, name, name)"
    UserGroup->>Files: "write_to_system_files()"
    Files->>Files: "Update /etc/passwd"
    Files->>Files: "Update /etc/shadow"  
    Files->>Files: "Update /etc/group"
    UserGroup->>Caller: "Return UserGroup"
```

Sources: [src/user_group.rs:115-126]()

### System File Integration

The user management system writes entries to standard Unix authentication files:

| File | Format | Purpose |
|------|--------|---------|
| `/etc/passwd` | `username:x:uid:gid:username:/nonexistent:/bin/false` | User account database |
| `/etc/shadow` | `username:*:18295:0:99999:7:::` | Password policy (disabled) |
| `/etc/group` | `groupname:x:gid:` | Group membership |

Sources: [src/user_group.rs:64-76]()

## Security Hardening

The `lockdown.rs` module implements critical security measures for the NVRC system.

### Panic Handling

```mermaid
graph LR
    PANIC["System Panic"]
    HOOK["Panic Hook"]
    LOG["Log Error"]
    SYNC["sync()"]
    REBOOT["Power Off"]
    
    PANIC --> HOOK
    HOOK --> LOG
    LOG --> SYNC
    SYNC --> REBOOT
```

The panic hook ensures system stability by immediately powering off on critical failures, preventing potential security compromises or data corruption.

Sources: [src/lockdown.rs:10-16]()

### Module Loading Restriction

NVRC disables kernel module loading after initialization by writing to `/proc/sys/kernel/modules_disabled`. This prevents runtime injection of unauthorized kernel modules.

```mermaid
flowchart LR
    INIT["System Initialization"]
    WRITE["Write '1' to /proc/sys/kernel/modules_disabled"]
    LOCKED["Module Loading Disabled"]
    
    INIT --> WRITE
    WRITE --> LOCKED
```

Sources: [src/lockdown.rs:18-20]()

## Service Dependencies and Integration

The system services integrate with other NVRC subsystems through well-defined interfaces:

| Service Component | Dependency | Integration Point |
|------------------|------------|-------------------|
| Daemon Management | GPU Detection | Conditional service startup |
| User Management | Filesystem Setup | System file access |
| Security Hardening | System Initialization | Early boot integration |
| All Services | Kernel Logging | `kmsg()` for output redirection |

This architecture ensures that system services are properly sequenced during initialization and maintain appropriate isolation and security boundaries during runtime operation.

Sources: [src/daemon.rs:1-224](), [src/user_group.rs:1-377](), [src/lockdown.rs:1-21]()

---

