<!-- source: DeepWiki mcp.deepwiki.com · repo termux/termux-exec-package · page 3 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Makefile](Makefile)
- [app/main/tests/termux-exec-tests.in](app/main/tests/termux-exec-tests.in)
- [site/pages/en/projects/docs/technical/index.md](site/pages/en/projects/docs/technical/index.md)
- [site/pages/en/projects/docs/usage/index.md](site/pages/en/projects/docs/usage/index.md)

</details>



This document provides a comprehensive overview of the architectural design and components of the termux-exec package. It explains how the system intercepts execution requests, handles Android's restrictions, and ensures proper program execution within the Termux environment. For installation instructions, see [Installation and Setup](#2), and for detailed execution interception mechanisms, see [Execution Interception Mechanism](#3.2).

## Core System Overview

The termux-exec package is designed to solve two critical issues in the Termux environment:

1. **Android's W^X Restrictions**: On Android 10 and higher with targetSdkVersion ≥ 29, execution of files in app data directories is restricted
2. **Path Differences**: Standard Linux versus Termux path differences (e.g., `/bin/sh` vs. `$TERMUX__PREFIX/bin/sh`)

The system achieves this through an LD_PRELOAD library that intercepts execution requests and applies the necessary modifications before actual execution.

```mermaid
graph TD
    A["Application"] -->|"exec() family call"| B["LD_PRELOAD Mechanism"]
    B -->|"Intercepts"| C["ExecIntercept Module"]
    C -->|"ELF Binary"| D{"System Restrictions Check"}
    C -->|"Script File"| E["Shebang Processing"]
    D -->|"Android 10+, targetSdk ≥ 29"| F["System Linker Execution"]
    D -->|"Otherwise"| G["Direct Execution"]
    E -->|"Path translation"| H["Modified Path Execution"]
    F --> I["execve() system call"]
    G --> I
    H --> I
```

Sources: [lib/termux-exec_nos_c/tre/src/termux/api/termux_exec/service/ld_preload/direct/exec/ExecIntercept.c](), [lib/termux-exec_nos_c/tre/src/termux/api/termux_exec/service/ld_preload/TermuxExecLDPreload.c]()

## Library Variants Architecture

The system provides two primary library variants that serve different execution scenarios:

```mermaid
graph TD
    A["termux-exec-package"] --> B["libtermux-exec_nos_c_tre.so/a"]
    A --> C["libtermux-exec-direct-ld-preload.so"]
    A --> D["libtermux-exec-linker-ld-preload.so"]
    
    C -->|"Primary on Android < 10"| E["libtermux-exec-ld-preload.so"]
    D -->|"Primary on Android ≥ 10"| E
    E -->|"Backward compatibility"| F["libtermux-exec.so (symlink)"]
    
    B --> G["Core Intercept Components"]
    G --> H["ExecIntercept"]
    G --> I["ExecVariantsIntercept"]
    
    C --> J["TermuxExecDirectLDPreloadEntryPoint"]
    D --> K["TermuxExecLinkerLDPreloadEntryPoint"]
    
    J --> G
    K --> G
```

Sources: [Makefile:394-420](), [Makefile:422-438]()

### Component Relationships

The following diagram shows the relationship between source files and functional components:

```mermaid
graph LR
    A["libtermux-exec-direct-ld-preload.so"] --> B["TermuxExecDirectLDPreloadEntryPoint.c"]
    C["libtermux-exec-linker-ld-preload.so"] --> D["TermuxExecLinkerLDPreloadEntryPoint.c"]
    
    B --> E["libtermux-exec_nos_c_tre"]
    D --> E
    
    E --> F["ExecIntercept.c"]
    E --> G["ExecVariantsIntercept.c"]
    E --> H["TermuxExecLDPreload.c"]
    E --> I["TermuxExecProcess.c"]
    E --> J["TermuxExecShellEnvironment.c"]
```

Sources: [Makefile:194-200](), [Makefile:386-402](), [Makefile:422-438]()

## Execution Interception Process

The core functionality of the package is the interception and processing of execution requests. This is implemented as an LD_PRELOAD library that hooks into the exec() family of functions.

```mermaid
sequenceDiagram
    participant App as Application
    participant LD as LD_PRELOAD Library
    participant ExecVar as ExecVariantsIntercept
    participant ExecInt as ExecIntercept
    participant Sys as System (execve)
    
    App->>ExecVar: execl()/execlp()/execle()/etc.
    ExecVar->>ExecInt: execveIntercept()
    
    Note over ExecInt: Check if file is a script
    
    alt Is Script File
        ExecInt->>ExecInt: Read first bytes
        ExecInt->>ExecInt: Parse shebang line
        ExecInt->>ExecInt: Replace /bin/ or /usr/bin/ with TERMUX__PREFIX/bin/
    end
    
    Note over ExecInt: Check if system_linker_exec is needed
    
    alt Android ≥10 & App Data File
        ExecInt->>ExecInt: Check TERMUX_EXEC__SYSTEM_LINKER_EXEC__MODE
        alt system_linker_exec enabled
            ExecInt->>ExecInt: Set TERMUX_EXEC__PROC_SELF_EXE
            ExecInt->>ExecInt: Prepare args for /system/bin/linker64
        end
    end
    
    ExecInt->>Sys: Call real execve() with modified arguments
    Sys->>App: Execution result
```

Sources: [lib/termux-exec_nos_c/tre/src/termux/api/termux_exec/service/ld_preload/direct/exec/ExecIntercept.c](), [lib/termux-exec_nos_c/tre/src/termux/api/termux_exec/service/ld_preload/direct/exec/ExecVariantsIntercept.c]()

## System Linker Execution Mechanism

On Android 10+ with targetSdkVersion ≥ 29, direct execution of files in app data directories is restricted (W^X policy). The termux-exec package implements a bypass using the system linker:

```mermaid
graph TD
    A["ExecIntercept"] --> B{"Needs system_linker_exec?"}
    B -->|"Yes"| C["Replace direct execution with system linker"]
    B -->|"No"| D["Direct execution"]
    
    C --> E["Prepend /system/bin/linker64"]
    C --> F["Set TERMUX_EXEC__PROC_SELF_EXE"]
    
    E --> G["execve(/system/bin/linker64, ...)"]
    F --> G
    D --> H["execve(original_path, ...)"]
    
    subgraph "Execution Transformation"
        I["Original: execve(/data/data/com.termux/files/usr/bin/ls, ...)"] --> J["Transformed: execve(/system/bin/linker64, /data/data/com.termux/files/usr/bin/ls, ...)"]
    end
```

Sources: [lib/termux-exec_nos_c/tre/src/termux/api/termux_exec/service/ld_preload/TermuxExecLDPreload.c:2137-2247](), [lib/termux-exec_nos_c/tre/src/termux/api/termux_exec/service/ld_preload/direct/exec/ExecIntercept.c:216-259]()

## Build System Architecture

The build system is orchestrated by the Makefile, which creates different library variants and installs them appropriately:

```mermaid
graph TD
    A["make all"] --> B["pre-build"]
    A --> C["build-libtermux-exec_nos_c_tre"]
    A --> D["build-libtermux-exec-direct-ld-preload"]
    A --> E["build-libtermux-exec-linker-ld-preload"]
    A --> F["build-termux-exec-main-app"]
    
    C --> G["Compile .c to .o files"]
    G --> H["Create libtermux-exec_nos_c_tre.so"]
    G --> I["Create libtermux-exec_nos_c_tre.a"]
    
    D --> J["Create libtermux-exec-direct-ld-preload.so"]
    E --> K["Create libtermux-exec-linker-ld-preload.so"]
    
    J --> L["Copy as libtermux-exec-ld-preload.so"]
    L --> M["Create libtermux-exec.so symlink"]
    
    F --> N["Install scripts"]
    F --> O["Install tests"]
```

Sources: [Makefile:251-264](), [Makefile:289-316](), [Makefile:386-420](), [Makefile:422-438](), [Makefile:271-287]()

## Environment Variables and Configuration

The system's behavior is controlled by several environment variables:

| Environment Variable | Purpose | Default | Options |
|---------------------|---------|---------|---------|
| TERMUX_EXEC__SYSTEM_LINKER_EXEC__MODE | Controls system linker execution | enable | disable, enable, force |
| TERMUX_EXEC__EXECVE_CALL__INTERCEPT | Controls whether execve() is intercepted | enable | disable, enable |
| TERMUX__PREFIX | Path to Termux installation | /data/data/com.termux/files/usr | Any valid path |
| TERMUX_EXEC__LOG_LEVEL | Controls logging verbosity | 1 | 0 (OFF) to 5 (VVVERBOSE) |
| TERMUX_EXEC__PROC_SELF_EXE | Set by system when using system_linker_exec | - | Path to actual executable |

Sources: [site/pages/en/projects/docs/usage/index.md:158-241]()

## Testing Architecture

The package includes a comprehensive testing framework to verify functionality across different execution scenarios:

```mermaid
graph TD
    A["termux-exec-tests"] --> B["libtermux-exec_nos_c_tre_tests"]
    B --> C["Unit Tests"]
    B --> D["Runtime Tests"]
    
    C --> E["ExecIntercept Tests"]
    C --> F["Path Translation Tests"]
    
    D --> G["Binary Execution Tests"]
    D --> H["Script Execution Tests"]
    D --> I["System Linker Execution Tests"]
    
    subgraph "Test Environment Setup"
        J["Setup Test Variables"] --> K["Detect Android Version"]
        K --> L["Choose LD_PRELOAD Library"]
        L --> M["Prepare Test Files"]
    end
```

Sources: [app/main/tests/termux-exec-tests.in:220-261](), [app/main/tests/termux-exec-tests.in:140-215]()

## Installation Flow

```mermaid
flowchart TD
    A["Package Installation"] --> B["termux-exec-ld-preload-lib setup"]
    B --> C["termux-exec-system-linker-exec is-enabled"]
    C --> D{"Result?"}
    D -->|"Enabled"| E["Use libtermux-exec-linker-ld-preload.so"]
    D -->|"Disabled"| F["Use libtermux-exec-direct-ld-preload.so"]
    E --> G["Copy to libtermux-exec-ld-preload.so"]
    F --> G
    G --> H["Create libtermux-exec.so symlink"]
    H --> I["Add to LD_PRELOAD in login script"]
```

Sources: [site/pages/en/projects/docs/technical/index.md:15-16]()

## System Structures

The core library `libtermux-exec_nos_c_tre` consists of several key components:

| Component | Purpose | Source Files |
|-----------|---------|--------------|
| ExecIntercept | Main execution interception logic | lib/termux-exec_nos_c/tre/src/termux/api/termux_exec/service/ld_preload/direct/exec/ExecIntercept.c |
| ExecVariantsIntercept | Handles different exec variants (execl, execlp, etc.) | lib/termux-exec_nos_c/tre/src/termux/api/termux_exec/service/ld_preload/direct/exec/ExecVariantsIntercept.c |
| TermuxExecLDPreload | Provides core LD_PRELOAD functionality | lib/termux-exec_nos_c/tre/src/termux/api/termux_exec/service/ld_preload/TermuxExecLDPreload.c |
| TermuxExecProcess | Process-related utilities | lib/termux-exec_nos_c/tre/src/termux/os/process/termux_exec/TermuxExecProcess.c |
| TermuxExecShellEnvironment | Shell environment handling | lib/termux-exec_nos_c/tre/src/termux/shell/command/environment/termux_exec/TermuxExecShellEnvironment.c |

Sources: [Makefile:194-200]()

## Decision Tree for Execution Method

```mermaid
flowchart TD
    A["execve() intercepted"] --> B{"File type?"}
    B -->|"Script"| C["Process shebang line"]
    B -->|"ELF Binary"| D{"Android Version?"}
    
    C --> E["Replace /bin/ and /usr/bin/ paths"]
    E --> F["Process resulting file"]
    
    D -->|"< 10"| G["Direct Execution"]
    D -->|"≥ 10"| H{"targetSdkVersion?"}
    
    H -->|"< 29"| G
    H -->|"≥ 29"| I{"TERMUX_EXEC__SYSTEM_LINKER_EXEC__MODE?"}
    
    I -->|"disable"| G
    I -->|"enable"| J{"File Location?"}
    I -->|"force"| K["System Linker Execution"]
    
    J -->|"App Data Dir"| K
    J -->|"System Dir"| G
    
    K --> L["Set TERMUX_EXEC__PROC_SELF_EXE"]
    K --> M["Prepend /system/bin/linker64"]
    K --> N["Call real execve()"]
    
    G --> N
```

Sources: [lib/termux-exec_nos_c/tre/src/termux/api/termux_exec/service/ld_preload/TermuxExecLDPreload.c:2137-2247](), [lib/termux-exec_nos_c/tre/src/termux/api/termux_exec/service/ld_preload/direct/exec/ExecIntercept.c:216-259](), [site/pages/en/projects/docs/usage/index.md:222-256]()

## System Files and Their Roles

The following table provides an overview of the key files in the system and their roles:

| File Path | Role |
|-----------|------|
| libtermux-exec-ld-preload.so | Primary LD_PRELOAD library (copy of one of the variants) |
| libtermux-exec-direct-ld-preload.so | Direct execution variant (for Android < 10) |
| libtermux-exec-linker-ld-preload.so | System linker execution variant (for Android ≥ 10) |
| libtermux-exec.so | Backward compatibility symlink |
| libtermux-exec_nos_c_tre.so | Core library implementing execution logic |
| termux-exec-ld-preload-lib | Script to configure the primary LD_PRELOAD library |
| termux-exec-system-linker-exec | Script to check if system_linker_exec is needed |

Sources: [Makefile:386-420](), [Makefile:422-438](), [Makefile:289-316](), [site/pages/en/projects/docs/technical/index.md:11-20]()

## Integration with Termux Environment

The termux-exec package integrates with the broader Termux environment through several mechanisms:

```mermaid
flowchart TD
    A["Termux App"] --> B["Environment Setup"]
    B --> C["Export TERMUX__PREFIX"]
    B --> D["Export TERMUX_APP__DATA_DIR"]
    
    E["termux-tools package"] --> F["login script"]
    F --> G["Export LD_PRELOAD=libtermux-exec-ld-preload.so"]
    
    H["termux-exec-package"] --> I["postinst script"]
    I --> J["termux-exec-ld-preload-lib setup"]
    J --> K["Select appropriate library variant"]
    
    L["User Process"] --> M["Process Creation"]
    M --> N["LD_PRELOAD hooks exec() calls"]
    N --> O["termux-exec logic applied"]
    O --> P["Successful execution in Termux"]
```

Sources: [site/pages/en/projects/docs/technical/index.md:15-16](), [site/pages/en/projects/docs/usage/index.md:47-116]()

---

