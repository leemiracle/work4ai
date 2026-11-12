<!-- source: DeepWiki mcp.deepwiki.com · repo termux/termux-tasker · page 2 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE.md](LICENSE.md)
- [README.md](README.md)
- [app/src/main/AndroidManifest.xml](app/src/main/AndroidManifest.xml)
- [fastlane/metadata/android/en-US/changelogs/6.txt](fastlane/metadata/android/en-US/changelogs/6.txt)
- [fastlane/metadata/android/en-US/changelogs/7.txt](fastlane/metadata/android/en-US/changelogs/7.txt)

</details>



This document describes the high-level system architecture of the Termux:Tasker plugin, including how it integrates with plugin host applications (Tasker, Locale) and the Termux ecosystem to enable command execution capabilities. For details on specific user interface components, see [User Interface](#3). For implementation details of security mechanisms, see [Security Model](#5.2).

## System Overview

Termux:Tasker is an Android plugin application that acts as a bridge between automation apps (plugin hosts) and the Termux terminal environment. The architecture follows the standard Android plugin model using intent-based communication while implementing additional security layers and command execution orchestration.

```mermaid
graph TB
    subgraph "Plugin Host Layer"
        Tasker["Tasker App"]
        Locale["Locale Compatible Apps"]
    end
    
    subgraph "Termux:Tasker Plugin"
        App["TermuxTaskerApplication"]
        EditActivity["EditConfigurationActivity"]
        FireReceiver["FireReceiver"]
        ResultsService["PluginResultsService"]
        MainActivity["TermuxTaskerMainActivity"]
    end
    
    subgraph "Termux Ecosystem" 
        TermuxApp["Termux App"]
        TermuxService["TERMUX_SERVICE"]
        TaskerDir["~/.termux/tasker/"]
    end
    
    subgraph "Android Framework"
        Intents["Intent System"]
        Permissions["Permission System"] 
        SharedUser["Shared User ID"]
    end
    
    Tasker -->|"EDIT_SETTING Intent"| EditActivity
    Locale -->|"EDIT_SETTING Intent"| EditActivity
    Tasker -->|"FIRE_SETTING Intent"| FireReceiver
    Locale -->|"FIRE_SETTING Intent"| FireReceiver
    
    FireReceiver -->|"Execution Intent"| TermuxService
    TermuxService -->|"PendingIntent Results"| ResultsService
    ResultsService -->|"Plugin Variables"| Tasker
    ResultsService -->|"Plugin Variables"| Locale
    
    TermuxService -->|"Command Execution"| TermuxApp
    TermuxService -->|"Script Access"| TaskerDir
    
    App --> Permissions
    App --> SharedUser
    EditActivity --> Intents
    FireReceiver --> Intents
```

**Architecture Overview**
Sources: [app/src/main/AndroidManifest.xml:1-85](), [README.md:1-394]()

## Plugin Integration Model

The plugin implements the standard Locale/Tasker plugin API using two primary intent actions for configuration and execution phases.

```mermaid
sequenceDiagram
    participant Host as "Plugin Host App"
    participant Edit as "EditConfigurationActivity"
    participant Bundle as "PluginBundleManager"
    participant Fire as "FireReceiver"
    participant Results as "PluginResultsService"
    participant Termux as "TERMUX_SERVICE"
    
    Note over Host,Termux: Configuration Phase
    Host->>+Edit: "EDIT_SETTING Intent"
    Edit->>+Bundle: "generateBundle(config)"
    Bundle-->>-Edit: "Configuration Bundle"
    Edit-->>-Host: "Bundle + Human Readable Blurb"
    
    Note over Host,Termux: Execution Phase  
    Host->>+Fire: "FIRE_SETTING Intent + Bundle"
    Fire->>+Bundle: "parseBundle(bundle)"
    Bundle-->>-Fire: "Validated Parameters"
    Fire->>+Termux: "Command Execution Intent"
    Termux->>+Results: "Results via PendingIntent"
    Results->>-Host: "Plugin Variables (%stdout, %stderr, %result)"
```

**Plugin Integration Sequence**
Sources: [app/src/main/AndroidManifest.xml:39-51](), [app/src/main/AndroidManifest.xml:69-78]()

### Intent Actions and Permissions

The plugin registers for two standard intent actions defined by the Locale plugin specification:

- **EDIT_SETTING**: `com.twofortyfouram.locale.intent.action.EDIT_SETTING` handled by `EditConfigurationActivity`
- **FIRE_SETTING**: `com.twofortyfouram.locale.intent.action.FIRE_SETTING` handled by `FireReceiver`

The `FireReceiver` requires the `com.termux.permission.RUN_COMMAND` permission to prevent unauthorized command execution.

Sources: [app/src/main/AndroidManifest.xml:49](), [app/src/main/AndroidManifest.xml:76](), [app/src/main/AndroidManifest.xml:73]()

## Core Application Components

The plugin application consists of standard Android components organized around the plugin lifecycle and command execution flow.

```mermaid
graph TB
    subgraph "Application Layer"
        TermuxTaskerApp["TermuxTaskerApplication<br/>Application Class"]
    end
    
    subgraph "Activity Components"
        EditConfig["EditConfigurationActivity<br/>Plugin Configuration UI"]
        MainAct["TermuxTaskerMainActivity<br/>Launcher Activity"]
        TextIO["TextIOActivity<br/>Shared Component"]
    end
    
    subgraph "Service Components" 
        ResultsSvc["PluginResultsService<br/>Result Handler"]
    end
    
    subgraph "Receiver Components"
        FireRcv["FireReceiver<br/>Command Trigger<br/>:background process"]
    end
    
    subgraph "Utility Classes"
        BundleMgr["PluginBundleManager<br/>Data Serialization"]
        PluginUtils["PluginUtils<br/>Core Logic"]
    end
    
    TermuxTaskerApp --> EditConfig
    TermuxTaskerApp --> MainAct
    TermuxTaskerApp --> ResultsSvc
    TermuxTaskerApp --> FireRcv
    
    EditConfig --> BundleMgr
    FireRcv --> BundleMgr
    FireRcv --> PluginUtils
    PluginUtils --> ResultsSvc
    
    MainAct -.->|"Launcher Alias"| EditConfig
    ResultsSvc -.->|"Shared Component"| TextIO
```

**Core Component Architecture**
Sources: [app/src/main/AndroidManifest.xml:8](), [app/src/main/AndroidManifest.xml:40](), [app/src/main/AndroidManifest.xml:16](), [app/src/main/AndroidManifest.xml:70](), [app/src/main/AndroidManifest.xml:82]()

### Component Responsibilities

| Component | Process | Exported | Purpose |
|-----------|---------|----------|---------|
| `TermuxTaskerApplication` | Main | N/A | Application lifecycle management |
| `EditConfigurationActivity` | Main | Yes | Plugin configuration interface |
| `TermuxTaskerMainActivity` | Main | Yes | Main launcher activity |
| `FireReceiver` | `:background` | Yes | Command execution trigger |
| `PluginResultsService` | Main | No | Result processing and delivery |

The `FireReceiver` runs in a separate `:background` process to handle command execution without blocking the main UI thread.

Sources: [app/src/main/AndroidManifest.xml:72](), [app/src/main/AndroidManifest.xml:41](), [app/src/main/AndroidManifest.xml:17](), [app/src/main/AndroidManifest.xml:83]()

## Security and Permission Model

The plugin implements a multi-layered security model to control command execution and file system access.

```mermaid
graph TD
    subgraph "Permission Layer"
        RunCmd["com.termux.permission.RUN_COMMAND<br/>Required by plugin host"]
        SharedUID["Shared User ID<br/>${TERMUX_PACKAGE_NAME}"]
    end
    
    subgraph "File System Security"
        TaskerDir["~/.termux/tasker/<br/>Default execution directory"]
        ExternalApps["allow-external-apps property<br/>~/.termux/termux.properties"]
        PathValidation["Path validation and<br/>security policy checks"]
    end
    
    subgraph "Execution Controls"
        PermissionCheck["File permission validation"]
        PolicyEnforcement["External app policy enforcement"]
        ArgumentValidation["Command argument sanitization"]
    end
    
    RunCmd --> TaskerDir
    SharedUID --> TaskerDir
    ExternalApps --> PathValidation
    TaskerDir --> PermissionCheck
    PathValidation --> PolicyEnforcement
    PolicyEnforcement --> ArgumentValidation
```

**Security Architecture**
Sources: [app/src/main/AndroidManifest.xml:4](), [app/src/main/AndroidManifest.xml:73](), [README.md:66-87]()

### Permission Requirements

1. **RUN_COMMAND Permission**: Plugin host apps must be granted `com.termux.permission.RUN_COMMAND` to execute any commands
2. **Shared User ID**: Both Termux and Termux:Tasker share the same user ID (`${TERMUX_PACKAGE_NAME}`) for file system access
3. **External Apps Policy**: Commands outside `~/.termux/tasker/` require `allow-external-apps=true` in termux properties

Sources: [README.md:67-72](), [README.md:84-87]()

## Data Flow and Bundle Management

Plugin configuration and execution data flows through a centralized bundle management system that handles serialization, validation, and security policy enforcement.

```mermaid
graph LR
    subgraph "Configuration Input"
        UserInput["User Configuration<br/>EditConfigurationActivity"]
        ConfigFields["Executable, Arguments<br/>Working Directory, Stdin<br/>Session Action, Log Level"]
    end
    
    subgraph "Bundle Processing"
        BundleGen["generateBundle()<br/>PluginBundleManager"]
        BundleValidation["parseBundle()<br/>Validation & Security"]
        BlurbGen["generateBlurb()<br/>Human-readable summary"]
    end
    
    subgraph "Command Execution"
        ArgTokenizer["ArgumentTokenizer<br/>Argument parsing"]
        PathResolver["Path resolution<br/>$PREFIX, ~/ expansion"]
        SecurityCheck["Security policy<br/>validation"]
    end
    
    subgraph "Result Processing"
        PluginVars["Plugin Variables<br/>%stdout, %stderr, %result<br/>%err, %errmsg"]
        HostResponse["Host app response<br/>TaskerPlugin API"]
    end
    
    UserInput --> ConfigFields
    ConfigFields --> BundleGen
    BundleGen --> BundleValidation
    BundleGen --> BlurbGen
    BundleValidation --> ArgTokenizer
    ArgTokenizer --> PathResolver
    PathResolver --> SecurityCheck
    SecurityCheck --> PluginVars
    PluginVars --> HostResponse
```

**Data Flow Architecture**
Sources: [README.md:132-217](), [README.md:222-255]()

### Bundle Structure and Variables

The plugin uses Android Bundle objects to serialize configuration data between the host app and plugin components. Key configuration parameters include:

- **Executable**: Script path or command (supports `$PREFIX/`, `~/` prefixes)
- **Arguments**: Command arguments processed by `ArgumentTokenizer`
- **Working Directory**: Command execution directory
- **Stdin**: Script content for dynamic execution
- **Session Action**: Terminal session behavior control
- **Log Level**: Custom logging configuration

Result data is returned to the host app through plugin variables with automatic truncation handling for large outputs.

Sources: [README.md:138-217](), [README.md:226-255]()

---

