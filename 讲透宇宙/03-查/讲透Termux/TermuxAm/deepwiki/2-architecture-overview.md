<!-- source: DeepWiki mcp.deepwiki.com · repo termux/TermuxAm · page 2 Architecture Overview · fetched 2026-10-26 -->

# Architecture Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [am-libexec-packaged](am-libexec-packaged)
- [app/src/main/java/com/termux/termuxam/Am.java](app/src/main/java/com/termux/termuxam/Am.java)
- [app/src/main/java/com/termux/termuxam/BaseCommand.java](app/src/main/java/com/termux/termuxam/BaseCommand.java)
- [app/src/main/java/com/termux/termuxam/IActivityManager.java](app/src/main/java/com/termux/termuxam/IActivityManager.java)

</details>



This page provides a comprehensive overview of the TermuxAm system architecture, covering the main components and their interactions to deliver Android Activity Manager functionality to terminal applications.

TermuxAm is designed as a command-line utility that replicates the functionality of Android's `/system/bin/am` command, which was restricted starting in Android Oreo. The system uses reflection and hidden API access to interact with Android's internal `IActivityManager` service, providing activities starting, service management, and broadcast capabilities to applications running in terminal environments like Termux.

For details about specific entry points and execution paths, see [Entry Points and Execution](#3). For information about the build system configuration that enables hidden API access, see [Build System and Configuration](#5).

## System Architecture Overview

The TermuxAm system follows a layered architecture with clear separation between entry points, application logic, Android integration, and compatibility handling.

**System Architecture with Code Entities**
```mermaid
graph TB
    subgraph "Entry Layer"
        ALP["am-libexec-packaged<br/>Shell Script"]
        AAI["am-apk-installed<br/>Shell Script"]
    end
    
    subgraph "Application Layer"
        AM["Am.java<br/>extends BaseCommand"]
        BC["BaseCommand<br/>Abstract Command Framework"]
        SC["ShellCommand<br/>Argument Parser"]
    end
    
    subgraph "Integration Layer"
        IAM["IActivityManager<br/>Reflection Wrapper"]
        CVRM["CrossVersionReflectedMethod<br/>Version Compatibility"]
        IC["IntentCmd<br/>Intent Parser"]
    end
    
    subgraph "Compatibility Layer"
        FC["FakeContext<br/>Context Management"]
        WA["Workarounds<br/>Device-Specific Fixes"]
        PU["PermissionUtils<br/>Permission Validation"]
    end
    
    subgraph "Android Framework"
        AMS["ActivityManagerService<br/>(Hidden API)"]
        APPPROCESS["/system/bin/app_process<br/>Native Entry Point"]
    end
    
    ALP --> APPPROCESS
    AAI --> APPPROCESS
    APPPROCESS --> AM
    AM --> BC
    BC --> SC
    AM --> IAM
    AM --> IC
    IAM --> CVRM
    AM --> FC
    AM --> WA
    AM --> PU
    IAM --> AMS
    
    classDef entry fill:#f9f9f9
    classDef app fill:#e1f5fe
    classDef integration fill:#f3e5f5
    classDef compat fill:#fff3e0
    classDef android fill:#ffebee
    
    class ALP,AAI entry
    class AM,BC,SC app
    class IAM,CVRM,IC integration
    class FC,WA,PU compat
    class AMS,APPPROCESS android
```

Sources: [am-libexec-packaged:1-31](), [app/src/main/java/com/termux/termuxam/Am.java:40-41](), [app/src/main/java/com/termux/termuxam/BaseCommand.java:25-27](), [app/src/main/java/com/termux/termuxam/IActivityManager.java:19-21]()

## Core Application Architecture

The application layer implements the command-line interface and business logic for processing Android Activity Manager commands.

**Application Layer Components**
```mermaid
graph TD
    subgraph "Command Processing Pipeline"
        MAIN["Am.main()<br/>Entry Point"]
        RUN["BaseCommand.run()<br/>Command Runner"]
        ONRUN["Am.onRun()<br/>Command Dispatcher"]
    end
    
    subgraph "Command Handlers"
        RS["runStart()<br/>Activity Management"]
        RSS["runStartService()<br/>Service Management"]
        RSV["runStopService()<br/>Service Stopping"]
        SB["sendBroadcast()<br/>Intent Broadcasting"]
        RU["runToUri()<br/>URI Conversion"]
        GCU["runGetCurrentUser()<br/>User Query"]
    end
    
    subgraph "Intent Processing"
        MI["makeIntent()<br/>Intent Factory"]
        IC["IntentCmd.parseCommandArgs()<br/>Argument Parser"]
        COH["CommandOptionHandler<br/>Option Processing"]
    end
    
    subgraph "User Management"
        PAU["parseUserArg()<br/>User ID Parser"]
        GCUI["getCurrentUserId()<br/>System User Query"]
        GUI["getUserId()<br/>UID Conversion"]
    end
    
    MAIN --> RUN
    RUN --> ONRUN
    ONRUN --> RS
    ONRUN --> RSS
    ONRUN --> RSV
    ONRUN --> SB
    ONRUN --> RU
    ONRUN --> GCU
    
    RS --> MI
    RSS --> MI
    RSV --> MI
    SB --> MI
    RU --> MI
    
    MI --> IC
    IC --> COH
    
    RS --> PAU
    RSS --> PAU
    RSV --> PAU
    SB --> PAU
    GCU --> GCUI
    PAU --> GUI
    PAU --> GCUI
```

Sources: [app/src/main/java/com/termux/termuxam/Am.java:119-124](), [app/src/main/java/com/termux/termuxam/BaseCommand.java:37-56](), [app/src/main/java/com/termux/termuxam/Am.java:416-524](), [app/src/main/java/com/termux/termuxam/Am.java:606-676]()

## Android System Integration Architecture

The integration layer handles the complex task of accessing Android's hidden APIs through reflection while maintaining compatibility across Android versions.

**Android Integration and Reflection Architecture**
```mermaid
graph TB
    subgraph "IActivityManager Wrapper"
        IAM_INIT["IActivityManager()<br/>Constructor"]
        GET_SERVICE["ActivityManager.getService()<br/>Modern API"]
        GET_DEFAULT["ActivityManagerNative.getDefault()<br/>Legacy API"]
    end
    
    subgraph "Reflected Method Management"
        CVRM_CLASS["CrossVersionReflectedMethod<br/>Method Wrapper"]
        GET_START["getStartActivityAsUserMethod()"]
        GET_SERVICE_METHOD["getStartServiceMethod()"]
        GET_STOP["getStopServiceMethod()"]
        GET_PROVIDER["getGetProviderMimeTypeMethod()"]
        GET_INTENT["getGetIntentSenderMethod()"]
    end
    
    subgraph "Method Invocation"
        START_ACTIVITY["startActivityAsUser()<br/>Activity Launcher"]
        START_SERVICE["startService()<br/>Service Starter"]
        STOP_SERVICE["stopService()<br/>Service Stopper"]
        BROADCAST["broadcastIntent()<br/>Intent Broadcaster"]
        GET_MIME["getProviderMimeType()<br/>MIME Type Resolver"]
    end
    
    subgraph "Android Framework APIs"
        AMS_START["ActivityManagerService.startActivityAsUser()"]
        AMS_SERVICE["ActivityManagerService.startService()"]
        AMS_BROADCAST["PendingIntent Mechanism"]
        CONTENT_RESOLVER["ContentResolver.getType()"]
    end
    
    IAM_INIT --> GET_SERVICE
    IAM_INIT --> GET_DEFAULT
    
    GET_SERVICE --> CVRM_CLASS
    GET_DEFAULT --> CVRM_CLASS
    
    CVRM_CLASS --> GET_START
    CVRM_CLASS --> GET_SERVICE_METHOD
    CVRM_CLASS --> GET_STOP
    CVRM_CLASS --> GET_PROVIDER
    CVRM_CLASS --> GET_INTENT
    
    GET_START --> START_ACTIVITY
    GET_SERVICE_METHOD --> START_SERVICE
    GET_STOP --> STOP_SERVICE
    GET_INTENT --> BROADCAST
    GET_PROVIDER --> GET_MIME
    
    START_ACTIVITY --> AMS_START
    START_SERVICE --> AMS_SERVICE
    STOP_SERVICE --> AMS_SERVICE
    BROADCAST --> AMS_BROADCAST
    GET_MIME --> CONTENT_RESOLVER
```

Sources: [app/src/main/java/com/termux/termuxam/IActivityManager.java:31-61](), [app/src/main/java/com/termux/termuxam/IActivityManager.java:63-242](), [app/src/main/java/com/termux/termuxam/IActivityManager.java:246-346]()

## Compatibility and Workaround System

The system includes extensive compatibility handling to work across different Android versions and manufacturer variations.

**Compatibility Architecture**
```mermaid
graph LR
    subgraph "Version Detection"
        VER_CHECK["Build.VERSION.SDK_INT<br/>Version Checks"]
        TIRAMISU["Android 14+ Detection"]
        S_VERSION["Android 12 Detection"]
    end
    
    subgraph "Compatibility Solutions"
        CHMOD_FIX["chmod 0400<br/>Writable DEX Fix"]
        WORKAROUNDS["Workarounds.apply()<br/>Device Fixes"]
        TARGET_SDK["targetSdkVersion 27<br/>Legacy Permissions"]
        HIDDEN_API["HiddenApiBypass<br/>Reflection Access"]
    end
    
    subgraph "Runtime Adaptations"
        METHOD_VARIANTS["tryMethodVariantInexact()<br/>Method Discovery"]
        PERMISSION_CHECK["PermissionUtils.validate*<br/>Permission Validation"]
        FAKE_CONTEXT["FakeContext.PACKAGE_NAME<br/>Context Spoofing"]
    end
    
    VER_CHECK --> TIRAMISU
    VER_CHECK --> S_VERSION
    
    TIRAMISU --> CHMOD_FIX
    S_VERSION --> WORKAROUNDS
    VER_CHECK --> TARGET_SDK
    VER_CHECK --> HIDDEN_API
    
    HIDDEN_API --> METHOD_VARIANTS
    VER_CHECK --> PERMISSION_CHECK
    TARGET_SDK --> FAKE_CONTEXT
```

Sources: [am-libexec-packaged:10-26](), [app/src/main/java/com/termux/termuxam/IActivityManager.java:247-248](), [app/src/main/java/com/termux/termuxam/IActivityManager.java:315-326]()

## Command Execution Flow

The following diagram shows how commands flow through the system from user input to Android framework interaction.

**End-to-End Command Processing Flow**
```mermaid
sequenceDiagram
    participant User
    participant Script as "am-libexec-packaged"
    participant AppProcess as "app_process"
    participant AmMain as "Am.main()"
    participant OnRun as "Am.onRun()"
    participant MakeIntent as "makeIntent()"
    participant IAM as "IActivityManager"
    participant AMS as "ActivityManagerService"
    
    User->>Script: "./am start com.example/.MainActivity"
    Script->>Script: chmod 0400 am.apk (Android 14+)
    Script->>AppProcess: exec app_process Am
    AppProcess->>AmMain: Load and execute
    AmMain->>OnRun: Command dispatch
    OnRun->>OnRun: Parse "start" command
    OnRun->>MakeIntent: Create Intent object
    MakeIntent->>MakeIntent: Parse intent arguments
    MakeIntent-->>OnRun: Return Intent
    OnRun->>IAM: startActivityAsUser()
    IAM->>IAM: Apply workarounds if needed
    IAM->>AMS: Reflect to hidden API
    AMS-->>IAM: Return result code
    IAM-->>OnRun: Return result
    OnRun-->>User: Print result and exit
```

Sources: [am-libexec-packaged:28-30](), [app/src/main/java/com/termux/termuxam/Am.java:119-124](), [app/src/main/java/com/termux/termuxam/Am.java:735-933](), [app/src/main/java/com/termux/termuxam/IActivityManager.java:246-258]()

## Key Architectural Patterns

### Reflection-Based API Access
The system heavily relies on Java reflection to access Android's hidden `IActivityManager` interface. The `CrossVersionReflectedMethod` class provides version-agnostic method discovery and invocation, allowing the same code to work across different Android versions where method signatures may vary.

### Command Pattern Implementation
The `BaseCommand` class implements a command pattern where each am subcommand (`start`, `startservice`, `broadcast`, etc.) is handled by a specific method in the `Am` class. The `onRun()` method acts as a dispatcher based on the first command argument.

### Compatibility Layer Strategy
Rather than creating version-specific code branches, the system uses a layered approach with:
- Build-time configuration (`targetSdkVersion 27`)
- Runtime workarounds (`Workarounds.apply()`)
- Permission validation (`PermissionUtils`)
- Context manipulation (`FakeContext`)

### Intent Processing Pipeline
All commands that involve Android Intents follow a common pipeline through `makeIntent()`, which parses command-line arguments into `Intent` objects using the `IntentCmd.parseCommandArgs()` method with custom option handlers.

Sources: [app/src/main/java/com/termux/termuxam/BaseCommand.java:25-108](), [app/src/main/java/com/termux/termuxam/Am.java:606-676](), [app/src/main/java/com/termux/termuxam/IActivityManager.java:63-242]()

---

