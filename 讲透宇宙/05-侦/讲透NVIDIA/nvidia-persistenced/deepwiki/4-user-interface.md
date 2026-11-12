<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-persistenced · page 4 User Interface · fetched 2026-10-26 -->

# User Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [nvidia-persistenced.1.m4](nvidia-persistenced.1.m4)
- [option-table.h](option-table.h)
- [options.c](options.c)

</details>



This page documents the user interface provided by nvidia-persistenced, covering how users and administrators interact with the daemon through command-line options, help systems, and integration with external management tools. For detailed information about specific command-line options, see [Command Line Options](#4.1). For information about how documentation is generated from option definitions, see [Documentation Generation](#4.2).

## Overview

The nvidia-persistenced daemon provides a command-line interface primarily intended for system administrators and init scripts. End users typically do not interact with the daemon directly, but instead use NVIDIA management utilities like `nvidia-smi` that communicate with the daemon automatically through its RPC interface (documented in [RPC Communication System](#2.2)).

```mermaid
graph TD
    subgraph "User Interaction Layer"
        CLI[Command Line Interface]
        HELP[Help System]
        VERSION[Version Information]
    end
    
    subgraph "External Management Tools"
        NVIDIA_SMI[nvidia-smi]
        INIT_SCRIPTS[Init Scripts]
        SYSTEMD[systemd Services]
    end
    
    subgraph "Internal Processing"
        OPTION_PARSER[Option Parser]
        CONFIG[Configuration Setup]
        DAEMON_START[Daemon Startup]
    end
    
    subgraph "Documentation System"
        MAN_PAGE[Man Page]
        HELP_TEXT[Built-in Help]
        OPTION_DOCS[Option Documentation]
    end
    
    CLI --> OPTION_PARSER
    HELP --> HELP_TEXT
    VERSION --> VERSION
    
    NVIDIA_SMI --> DAEMON_START
    INIT_SCRIPTS --> CLI
    SYSTEMD --> CLI
    
    OPTION_PARSER --> CONFIG
    CONFIG --> DAEMON_START
    
    OPTION_DOCS --> MAN_PAGE
    OPTION_DOCS --> HELP_TEXT
```

Sources: [option-table.h:36-120](), [options.c:112-193](), [nvidia-persistenced.1.m4:1-105]()

## Command-Line Interface Architecture

The command-line interface is built around the `nvgetopt` library, which provides a standardized way to define and parse options. The interface follows a table-driven approach where all options are defined in a central location and processed systematically.

```mermaid
graph TD
    subgraph "Option Definition Layer"
        OPTION_TABLE["__options[]<br/>option-table.h"]
        NVGETOPT_OPTION[NVGetoptOption Structure]
        OPTION_ENUMS[Option Constants]
    end
    
    subgraph "Parsing Layer"
        NVGETOPT_FUNC[nvgetopt Function]
        PARSE_OPTIONS[parse_options Function]
        OPTION_VALIDATION[Option Validation]
    end
    
    subgraph "Configuration Layer"
        NVPD_OPTIONS[NvPdOptions Structure]
        DEFAULTS[setup_option_defaults]
        UID_GID_LOOKUP[User/Group Resolution]
    end
    
    subgraph "Output Layer"
        HELP_OUTPUT[print_help]
        VERSION_OUTPUT[print_version]
        ERROR_HANDLING[Error Messages]
    end
    
    OPTION_TABLE --> NVGETOPT_OPTION
    OPTION_ENUMS --> OPTION_TABLE
    
    NVGETOPT_OPTION --> NVGETOPT_FUNC
    NVGETOPT_FUNC --> PARSE_OPTIONS
    PARSE_OPTIONS --> OPTION_VALIDATION
    
    OPTION_VALIDATION --> NVPD_OPTIONS
    DEFAULTS --> NVPD_OPTIONS
    OPTION_VALIDATION --> UID_GID_LOOKUP
    
    PARSE_OPTIONS --> HELP_OUTPUT
    PARSE_OPTIONS --> VERSION_OUTPUT
    PARSE_OPTIONS --> ERROR_HANDLING
```

Sources: [option-table.h:30-120](), [options.c:98-193]()

## Option Processing Flow

The daemon processes command-line options through a systematic workflow that handles validation, user/group resolution, and configuration setup:

```mermaid
flowchart TD
    START[Program Start] --> SETUP_DEFAULTS[setup_option_defaults]
    SETUP_DEFAULTS --> PARSE_LOOP[nvgetopt Loop]
    
    PARSE_LOOP --> VERSION_CHECK{"-v --version"}
    VERSION_CHECK -->|Yes| PRINT_VERSION[print_version]
    PRINT_VERSION --> EXIT_SUCCESS[Exit Success]
    
    VERSION_CHECK -->|No| HELP_CHECK{"-h --help"}
    HELP_CHECK -->|Yes| PRINT_HELP[print_help]
    PRINT_HELP --> EXIT_SUCCESS
    
    HELP_CHECK -->|No| VERBOSE_CHECK{"-V --verbose"}
    VERBOSE_CHECK -->|Yes| SET_VERBOSE[Set verbose flag]
    
    VERBOSE_CHECK -->|No| USER_CHECK{"-u --user"}
    USER_CHECK -->|Yes| USER_LOOKUP[getpwnam lookup]
    USER_LOOKUP --> USER_VALID{Valid user?}
    USER_VALID -->|No| ERROR_EXIT[Error and Exit]
    USER_VALID -->|Yes| SET_UID_GID[Set UID/GID]
    
    USER_CHECK -->|No| GROUP_CHECK{"-g --group"}
    GROUP_CHECK -->|Yes| GROUP_LOOKUP[getgrnam lookup]
    GROUP_LOOKUP --> GROUP_VALID{Valid group?}
    GROUP_VALID -->|No| ERROR_EXIT
    GROUP_VALID -->|Yes| SET_GID[Set GID Override]
    
    GROUP_CHECK -->|No| PERSIST_CHECK{Persistence Options}
    PERSIST_CHECK --> SET_PERSIST_MODE[Set Persistence Modes]
    
    SET_VERBOSE --> PARSE_LOOP
    SET_UID_GID --> PARSE_LOOP
    SET_GID --> PARSE_LOOP
    SET_PERSIST_MODE --> PARSE_LOOP
    
    PARSE_LOOP --> DONE{Options Done?}
    DONE -->|No| PARSE_LOOP
    DONE -->|Yes| CONTINUE[Continue to Daemon Start]
```

Sources: [options.c:112-193](), [options.c:98-106]()

## Help and Documentation System

The daemon provides multiple levels of documentation through integrated help systems and generated documentation:

| Component | Function | Source | Description |
|-----------|----------|---------|-------------|
| Built-in Help | `print_help()` | [options.c:77-92]() | Interactive command-line help |
| Version Info | `print_version()` | [options.c:49-61]() | Version and copyright information |
| Help Callback | `print_help_callback()` | [options.c:66-71]() | Formatted option descriptions |
| Man Page | nvidia-persistenced.1.m4 | [nvidia-persistenced.1.m4:1-105]() | System manual page |

```mermaid
graph TD
    subgraph "Documentation Sources"
        OPTION_TABLE_DESC["Option Descriptions<br/>option-table.h"]
        VERSION_INFO[Version Information]
        COPYRIGHT[Copyright Text]
    end
    
    subgraph "Generation Process"
        HELP_FORMATTER[print_help_callback]
        NVGETOPT_HELP[nvgetopt_print_help]
        M4_PROCESSING[m4 Preprocessing]
    end
    
    subgraph "Output Formats"
        CONSOLE_HELP[Console Help Output]
        MAN_PAGE_OUT[Manual Page]
        EMBEDDED_DOCS[Embedded Documentation]
    end
    
    OPTION_TABLE_DESC --> HELP_FORMATTER
    OPTION_TABLE_DESC --> M4_PROCESSING
    VERSION_INFO --> CONSOLE_HELP
    COPYRIGHT --> CONSOLE_HELP
    
    HELP_FORMATTER --> NVGETOPT_HELP
    NVGETOPT_HELP --> CONSOLE_HELP
    M4_PROCESSING --> MAN_PAGE_OUT
    
    CONSOLE_HELP --> EMBEDDED_DOCS
    MAN_PAGE_OUT --> EMBEDDED_DOCS
```

Sources: [options.c:49-92](), [nvidia-persistenced.1.m4:15-51]()

## Integration with System Management

The daemon's user interface is designed to integrate seamlessly with various system management approaches:

```mermaid
graph TD
    subgraph "System Integration Points"
        SYSTEMD_SERVICE[systemd Service Files]
        SYSV_SCRIPTS[SysV Init Scripts]
        UPSTART_CONF[Upstart Configuration]
        MANUAL_START[Manual Execution]
    end
    
    subgraph "Common Usage Patterns"
        ROOT_START[Start as Root + Drop Privileges]
        USER_START[Start as Specific User]
        DEFAULT_CONFIG[Default Configuration]
        CUSTOM_CONFIG[Custom Configuration]
    end
    
    subgraph "Runtime Considerations"
        RUNTIME_DIR["/var/run/nvidia-persistenced"]
        DEVICE_PERMS[Device File Permissions]
        NVIDIA_MODPROBE[nvidia-modprobe Integration]
    end
    
    SYSTEMD_SERVICE --> ROOT_START
    SYSTEMD_SERVICE --> USER_START
    SYSV_SCRIPTS --> ROOT_START
    UPSTART_CONF --> DEFAULT_CONFIG
    MANUAL_START --> CUSTOM_CONFIG
    
    ROOT_START --> RUNTIME_DIR
    USER_START --> DEVICE_PERMS
    DEFAULT_CONFIG --> NVIDIA_MODPROBE
    CUSTOM_CONFIG --> RUNTIME_DIR
```

Sources: [nvidia-persistenced.1.m4:34-75](), [options.c:62-85]()

## Configuration Options Overview

The daemon accepts several categories of configuration options that control its behavior:

| Category | Options | Purpose |
|----------|---------|---------|
| **Identity** | `--user`, `--group` | Process identity and privilege management |
| **Behavior** | `--verbose` | Logging and output control |
| **Persistence** | `--persistence-mode`, `--uvm-persistence-mode` | GPU persistence state control |
| **System** | `--nvidia-cfg-path` | Library and system integration paths |
| **Information** | `--help`, `--version` | Documentation and version reporting |

The option definitions use several key constants and enumerations:

```mermaid
graph TD
    subgraph "Option Categories"
        BASIC_OPTS[Basic Options<br/>help, version, verbose]
        IDENTITY_OPTS[Identity Options<br/>user, group]
        PERSIST_OPTS[Persistence Options<br/>persistence-mode, uvm-persistence-mode]
        SYSTEM_OPTS[System Options<br/>nvidia-cfg-path]
    end
    
    subgraph "Implementation Constants"
        ENUM_CONSTANTS["enum Constants<br/>PERSISTENCE_MODE_OPTION<br/>UVM_PERSISTENCE_MODE_OPTION<br/>NVIDIA_CFG_PATH_OPTION"]
        NVGETOPT_FLAGS["NVGetopt Flags<br/>NVGETOPT_HELP_ALWAYS<br/>NVGETOPT_IS_BOOLEAN<br/>NVGETOPT_STRING_ARGUMENT"]
    end
    
    subgraph "Data Structures"
        NVGETOPT_OPTION[NVGetoptOption Array]
        NVPD_OPTIONS[NvPdOptions Structure]
    end
    
    BASIC_OPTS --> ENUM_CONSTANTS
    IDENTITY_OPTS --> ENUM_CONSTANTS
    PERSIST_OPTS --> ENUM_CONSTANTS
    SYSTEM_OPTS --> ENUM_CONSTANTS
    
    ENUM_CONSTANTS --> NVGETOPT_OPTION
    NVGETOPT_FLAGS --> NVGETOPT_OPTION
    NVGETOPT_OPTION --> NVPD_OPTIONS
```

Sources: [option-table.h:30-120](), [options.c:98-106]()

---

