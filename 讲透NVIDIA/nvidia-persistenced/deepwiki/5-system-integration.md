<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-persistenced · page 5 System Integration · fetched 2026-10-26 -->

# System Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [dist-files.mk](dist-files.mk)
- [init/README](init/README)
- [init/install.sh](init/install.sh)
- [nvidia-syslog-utils.c](nvidia-syslog-utils.c)
- [nvidia-syslog-utils.h](nvidia-syslog-utils.h)

</details>



This document covers the deployment, installation, and runtime integration of nvidia-persistenced with various operating system components. It explains how the daemon integrates with different init systems, manages system logging, handles user permissions, and maintains compatibility across platforms.

For information about command-line configuration options, see [Command Line Options](#4.1). For developer-oriented system interfaces, see [Developer Reference](#6).

## Init System Integration

The nvidia-persistenced daemon supports integration with three major init systems commonly found in Linux distributions: systemd, SysV, and Upstart. The system automatically detects the available init system and installs the appropriate service configuration.

### Supported Init Systems

```mermaid
graph TD
    INSTALLER["install.sh"] --> DETECT["Init System Detection"]
    
    DETECT --> SYSTEMD_CHECK["systemctl found?"]
    DETECT --> UPSTART_CHECK["initctl found?"] 
    DETECT --> SYSV_CHECK["chkconfig found?"]
    
    SYSTEMD_CHECK -->|Yes| SYSTEMD_INSTALL["Install systemd service"]
    UPSTART_CHECK -->|Yes| UPSTART_INSTALL["Install Upstart service"]
    SYSV_CHECK -->|Yes| SYSV_INSTALL["Install SysV script"]
    
    SYSTEMD_INSTALL --> SYSTEMD_PATHS["/usr/lib/systemd/system<br/>/etc/systemd/system"]
    UPSTART_INSTALL --> UPSTART_PATHS["/etc/init"]
    SYSV_INSTALL --> SYSV_PATHS["/etc/init.d<br/>/etc/rc.d/init.d<br/>/etc/rc.d"]
    
    SYSTEMD_PATHS --> SERVICE_FILE["nvidia-persistenced.service"]
    UPSTART_PATHS --> CONF_FILE["nvidia-persistenced.conf"]
    SYSV_PATHS --> SCRIPT_FILE["nvidia-persistenced"]
```

The installation script checks for init systems in a specific priority order: systemd first, then Upstart, then SysV. This ordering reflects the modern migration path of most Linux distributions.

**Sources:** [init/install.sh:34-39](), [init/install.sh:705-752]()

### Installation Process

The installation process involves template processing, user creation, and service registration:

```mermaid
sequenceDiagram
    participant USER as "Administrator"
    participant INSTALLER as "install.sh"
    participant SYSTEM as "System Commands"
    participant INIT as "Init System"
    
    USER->>INSTALLER: "Run installation"
    INSTALLER->>INSTALLER: "Parse command line options"
    INSTALLER->>INSTALLER: "checkCommon()"
    
    INSTALLER->>INSTALLER: "createSysVScript()"
    INSTALLER->>INSTALLER: "createSystemdService()" 
    INSTALLER->>INSTALLER: "createUpstartService()"
    
    INSTALLER->>SYSTEM: "useradd nvidia-persistenced"
    INSTALLER->>INSTALLER: "installCommon()"
    
    alt systemd detected
        INSTALLER->>INIT: "systemctl reenable"
        INSTALLER->>INIT: "systemctl start"
    else upstart detected  
        INSTALLER->>INIT: "initctl start"
    else sysv detected
        INSTALLER->>INIT: "chkconfig --level 2345 on"
        INSTALLER->>INIT: "service start"
    end
    
    INSTALLER->>USER: "Installation complete"
```

The template files use the `__USER__` placeholder which gets replaced during installation:

| Init System | Template File | Final File | Installation Path |
|-------------|---------------|------------|-------------------|
| systemd | `nvidia-persistenced.service.template` | `nvidia-persistenced.service` | `/usr/lib/systemd/system` |
| Upstart | `nvidia-persistenced.conf.template` | `nvidia-persistenced.conf` | `/etc/init` |
| SysV | `nvidia-persistenced.template` | `nvidia-persistenced` | `/etc/init.d` |

**Sources:** [init/install.sh:292-305](), [init/install.sh:407-420](), [init/install.sh:522-535](), [dist-files.mk:44-48]()

### Service Management

Each init system provides different commands for managing the service lifecycle:

```mermaid
graph LR
    subgraph "Service Operations"
        START["Start Service"]
        STOP["Stop Service"] 
        ENABLE["Enable at Boot"]
        DISABLE["Disable at Boot"]
        STATUS["Check Status"]
    end
    
    subgraph "systemd Commands"
        SYSTEMCTL_START["systemctl start nvidia-persistenced"]
        SYSTEMCTL_STOP["systemctl stop nvidia-persistenced"]
        SYSTEMCTL_ENABLE["systemctl enable nvidia-persistenced"]
        SYSTEMCTL_DISABLE["systemctl disable nvidia-persistenced"]
        SYSTEMCTL_STATUS["systemctl status nvidia-persistenced"]
    end
    
    subgraph "SysV Commands"
        SERVICE_START["service nvidia-persistenced start"]
        SERVICE_STOP["service nvidia-persistenced stop"]
        CHKCONFIG_ON["chkconfig nvidia-persistenced on"]
        CHKCONFIG_OFF["chkconfig nvidia-persistenced off"]
        SERVICE_STATUS["service nvidia-persistenced status"]
    end
    
    subgraph "Upstart Commands"
        INITCTL_START["initctl start nvidia-persistenced"]
        INITCTL_STOP["initctl stop nvidia-persistenced"]
        INITCTL_ENABLE["nvidia-persistenced enabled by default"]
        INITCTL_DISABLE["remove conf file to disable"]
        INITCTL_STATUS["initctl status nvidia-persistenced"]
    end
    
    START --> SYSTEMCTL_START
    START --> SERVICE_START
    START --> INITCTL_START
    
    STOP --> SYSTEMCTL_STOP
    STOP --> SERVICE_STOP
    STOP --> INITCTL_STOP
    
    ENABLE --> SYSTEMCTL_ENABLE
    ENABLE --> CHKCONFIG_ON
    ENABLE --> INITCTL_ENABLE
```

The installer handles running daemon detection through the `isNvpdRunning()` function which checks for the PID file at `/var/run/nvidia-persistenced/nvidia-persistenced.pid`.

**Sources:** [init/install.sh:164-182](), [init/install.sh:350-379](), [init/install.sh:464-494](), [init/install.sh:577-604]()

## System Logging Integration

The nvidia-persistenced daemon integrates with the system logging infrastructure through syslog. The logging system provides both general logging and device-specific logging capabilities.

```mermaid
graph TD
    subgraph "Logging Functions"
        SYSLOG_DEVICE["syslog_device()"]
        SYSLOG_DEVICE_VERBOSE["SYSLOG_DEVICE_VERBOSE()"]
        SYSLOG_VERBOSE["SYSLOG_VERBOSE()"]
    end
    
    subgraph "Log Filtering"
        VERBOSE_FLAG["verbose global variable"]
        LOG_MASK["log_mask global variable"]
    end
    
    subgraph "System Integration"
        SYSLOG_CALL["syslog() system call"]
        SYSLOG_DAEMON["System syslog daemon"]
        LOG_FILES["System log files"]
    end
    
    subgraph "Message Formation"
        DEVICE_INFO["NvCfgPciDevice info"]
        FORMAT_STR["Format string"]
        FINAL_MSG["Final message"]
    end
    
    SYSLOG_DEVICE --> DEVICE_INFO
    SYSLOG_DEVICE --> FORMAT_STR
    DEVICE_INFO --> FINAL_MSG
    FORMAT_STR --> FINAL_MSG
    
    SYSLOG_DEVICE_VERBOSE --> VERBOSE_FLAG
    SYSLOG_VERBOSE --> VERBOSE_FLAG
    
    SYSLOG_DEVICE --> LOG_MASK
    LOG_MASK --> SYSLOG_CALL
    
    FINAL_MSG --> SYSLOG_CALL
    SYSLOG_CALL --> SYSLOG_DAEMON
    SYSLOG_DAEMON --> LOG_FILES
```

The `syslog_device()` function formats device-specific messages with PCI device information in the format `device 0000:01:00.0 - message`. The logging system respects both verbosity settings and log priority masks.

**Sources:** [nvidia-syslog-utils.c:38-70](), [nvidia-syslog-utils.h:39-50]()

## User and Permission Management

The installation process creates a dedicated system user for running the nvidia-persistenced daemon, following security best practices by avoiding root execution when possible.

```mermaid
graph TD
    subgraph "User Creation Process"
        CHECK_USER["id nvidia-persistenced"]
        USER_EXISTS{"User exists?"}
        CREATE_USER["useradd command"]
        VERIFY_GROUP["Verify primary group"]
    end
    
    subgraph "User Configuration"
        USERNAME["nvidia-persistenced"]
        GROUP["nvidia-persistenced"]
        SHELL["/sbin/nologin"]
        HOMEDIR["/"]
        COMMENT["NVIDIA Persistence Daemon"]
        SYSTEM_USER["-r flag (system user)"]
    end
    
    subgraph "Permission Requirements"
        DEVICE_ACCESS["GPU device access"]
        PID_FILE_DIR["/var/run/nvidia-persistenced/"]
        LOG_ACCESS["Syslog access"]
    end
    
    CHECK_USER --> USER_EXISTS
    USER_EXISTS -->|No| CREATE_USER
    USER_EXISTS -->|Yes| VERIFY_GROUP
    
    CREATE_USER --> USERNAME
    CREATE_USER --> GROUP
    CREATE_USER --> SHELL
    CREATE_USER --> HOMEDIR
    CREATE_USER --> COMMENT
    CREATE_USER --> SYSTEM_USER
    
    USERNAME --> DEVICE_ACCESS
    USERNAME --> PID_FILE_DIR
    USERNAME --> LOG_ACCESS
```

The installation script supports custom user and group names through command-line options:

| Option | Purpose | Default Value |
|--------|---------|---------------|
| `-u <USER>` | Specify username | `nvidia-persistenced` |
| `-g <GROUP>` | Specify group name | Same as username |
| `-d` | Skip user deletion during uninstall | N/A |

**Sources:** [init/install.sh:243-267](), [init/install.sh:53-63](), [init/install.sh:635-687]()

## Platform Compatibility

The system integration components ensure compatibility across different Linux distributions and architectures through standardized detection and fallback mechanisms.

```mermaid
graph TD
    subgraph "Detection Tools"
        WHICH_SED["which sed"]
        WHICH_USERADD["which useradd"]
        WHICH_USERDEL["which userdel"]
        WHICH_ID["which id"]
    end
    
    subgraph "Init System Detection"
        WHICH_SYSTEMCTL["which systemctl"]
        WHICH_INITCTL["which initctl"]
        WHICH_CHKCONFIG["which chkconfig"]
    end
    
    subgraph "Path Detection"
        SYSTEMD_PATHS["Multiple systemd paths"]
        UPSTART_PATHS["Standard Upstart path"]
        SYSV_PATHS["Multiple SysV paths"]
    end
    
    subgraph "Compatibility Functions"
        CHECK_COMMON["checkCommon()"]
        CHECK_SYSTEMD["checkSystemd()"]
        CHECK_UPSTART["checkUpstart()"]
        CHECK_SYSV["checkSysV()"]
    end
    
    WHICH_SED --> CHECK_COMMON
    WHICH_USERADD --> CHECK_COMMON
    WHICH_USERDEL --> CHECK_COMMON
    WHICH_ID --> CHECK_COMMON
    
    WHICH_SYSTEMCTL --> CHECK_SYSTEMD
    WHICH_INITCTL --> CHECK_UPSTART
    WHICH_CHKCONFIG --> CHECK_SYSV
    
    SYSTEMD_PATHS --> CHECK_SYSTEMD
    UPSTART_PATHS --> CHECK_UPSTART
    SYSV_PATHS --> CHECK_SYSV
```

The system performs comprehensive compatibility checking before attempting installation, ensuring that all required tools and directories are available.

**Sources:** [init/install.sh:184-236](), [init/install.sh:314-342](), [init/install.sh:429-456](), [init/install.sh:544-569]()

## Configuration Management

The daemon configuration is managed through a combination of command-line arguments, template file processing, and runtime directory management.

```mermaid
graph LR
    subgraph "Template Processing"
        TEMPLATE_FILES["*.template files"]
        SED_REPLACEMENT["sed -e 's/__USER__/actual_user/g'"]
        FINAL_CONFIG["Final config files"]
    end
    
    subgraph "Runtime Environment"
        RUNTIME_DIR["/var/run/nvidia-persistenced/"]
        PID_FILE["nvidia-persistenced.pid"]
        SOCKET_FILE["RPC socket"]
    end
    
    subgraph "Command Line Options"
        USER_OPT["--user"]
        GROUP_OPT["--group"]
        VERBOSE_OPT["--verbose"]
        PERSISTENCE_OPT["--persistence-mode"]
    end
    
    TEMPLATE_FILES --> SED_REPLACEMENT
    SED_REPLACEMENT --> FINAL_CONFIG
    
    FINAL_CONFIG --> USER_OPT
    FINAL_CONFIG --> GROUP_OPT
    
    USER_OPT --> RUNTIME_DIR
    GROUP_OPT --> RUNTIME_DIR
    RUNTIME_DIR --> PID_FILE
    RUNTIME_DIR --> SOCKET_FILE
```

The installation process creates platform-specific configuration files from templates by replacing the `__USER__` placeholder with the actual username. This approach allows the same template to work across different deployment scenarios while maintaining proper user isolation.

**Sources:** [init/install.sh:292-305](), [init/install.sh:407-420](), [init/install.sh:522-535](), [dist-files.mk:44-48]()

---

