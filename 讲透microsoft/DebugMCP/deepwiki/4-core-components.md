<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/DebugMCP · page 4 Core Components · fetched 2026-10-26 -->

# Core Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [AGENTS.md](AGENTS.md)
- [docs/architecture/debugMCPServer.md](docs/architecture/debugMCPServer.md)
- [src/index.ts](src/index.ts)
- [tsconfig.json](tsconfig.json)

</details>



This document provides detailed documentation of the major components that make up the DebugMCP system. Each component has a specific responsibility in the layered architecture that bridges MCP protocol communication with VS Code's Debug Adapter Protocol (DAP).

For information about the overall architecture and how these components work together, see [Architecture Overview](#3). For detailed information about individual components, see the subsections: [DebugMCP Server](#4.1), [Debugging Handler](#4.2), [Debugging Executor](#4.3), [Debug Configuration Manager](#4.4), and [Agent Configuration Manager](#4.5).

## Component Overview

The DebugMCP system consists of six core components organized into three architectural layers:

| Component | Layer | Primary Responsibility | File Location |
|-----------|-------|----------------------|---------------|
| `DebugMCPServer` | Protocol Layer | MCP server implementation, tool/resource registration, FastMCP integration | [src/debugMCPServer.ts]() |
| `DebuggingHandler` | Orchestration Layer | Command orchestration, state change detection, workflow management | [src/debuggingHandler.ts]() |
| `DebuggingExecutor` | Execution Layer | VS Code Debug API interface, DAP request execution | [src/debuggingExecutor.ts]() |
| `DebugConfigurationManager` | Configuration Layer | Debug configuration management, language detection | [src/utils/debugConfigurationManager.ts]() |
| `AgentConfigurationManager` | Configuration Layer | AI agent auto-configuration and setup | [src/utils/agentConfigurationManager.ts]() |
| `DebugState` | State Management | Debug session state model and tracking | [src/debugState.ts]() |

Sources: [src/debugMCPServer.ts:1-376](), [src/debuggingHandler.ts:1-617](), [AGENTS.md:13-22](), [src/index.ts:4-11]()

## Layered Architecture

```mermaid
graph TB
    subgraph "Protocol Layer"
        DMS["DebugMCPServer<br/>(src/debugMCPServer.ts)"]
        FMCP["FastMCP<br/>(external library)"]
        TOOLS["13 MCP Tools<br/>start_debugging, step_over, etc"]
        RESOURCES["MCP Resources<br/>debug_instructions.md, troubleshooting/*.md"]
    end
    
    subgraph "Orchestration Layer"
        DH["DebuggingHandler<br/>(src/debuggingHandler.ts)"]
        IHANDLER["IDebuggingHandler<br/>interface"]
    end
    
    subgraph "Execution Layer"
        DE["DebuggingExecutor<br/>(src/debuggingExecutor.ts)"]
        IEXEC["IDebuggingExecutor<br/>interface"]
    end
    
    subgraph "Configuration Layer"
        DCM["DebugConfigurationManager<br/>(src/utils/debugConfigurationManager.ts)"]
        ACM["AgentConfigurationManager<br/>(src/utils/agentConfigurationManager.ts)"]
        IDCM["IDebugConfigurationManager<br/>interface"]
    end
    
    subgraph "State Management"
        DS["DebugState<br/>(src/debugState.ts)"]
    end
    
    subgraph "VS Code Infrastructure"
        VSCODE["vscode.debug API<br/>(VS Code Extension API)"]
        DAP["Debug Adapter Protocol<br/>(DAP)"]
    end
    
    DMS -->|"uses"| FMCP
    DMS -->|"registers"| TOOLS
    DMS -->|"loads"| RESOURCES
    DMS -->|"creates"| DH
    
    DH -->|"implements"| IHANDLER
    DH -->|"creates"| DE
    DH -->|"creates"| DCM
    DH -->|"reads/updates"| DS
    
    DE -->|"implements"| IEXEC
    DE -->|"uses"| DCM
    DE -->|"updates"| DS
    DE -->|"calls"| VSCODE
    
    DCM -->|"implements"| IDCM
    
    VSCODE -->|"communicates via"| DAP
    
    TOOLS -.->|"delegates to"| IHANDLER
```

This diagram maps the natural language component names to their actual code entities (classes, interfaces, and files). The three-layer separation ensures clear boundaries: the Protocol Layer handles MCP communication, the Orchestration Layer manages workflows and state changes, and the Execution Layer directly interfaces with VS Code's debugging infrastructure.

Sources: [src/debugMCPServer.ts:35-47](), [src/debuggingHandler.ts:12-31](), [AGENTS.md:9-11]()

## Component Dependencies

```mermaid
graph LR
    subgraph "Entry Point"
        EXT["extension.ts<br/>activate()"]
    end
    
    subgraph "Main Components"
        DMS["DebugMCPServer<br/>constructor(port, timeout)"]
        DH["DebuggingHandler<br/>constructor(executor, configMgr, timeout)"]
        DE["DebuggingExecutor<br/>constructor()"]
        DCM["ConfigurationManager<br/>constructor()"]
        ACM["AgentConfigurationManager<br/>constructor()"]
    end
    
    subgraph "External Dependencies"
        FASTMCP["fastmcp<br/>FastMCP class"]
        VSCODE["vscode<br/>Extension API"]
        ZOD["zod<br/>Schema validation"]
    end
    
    EXT -->|"creates"| DMS
    EXT -->|"creates"| ACM
    
    DMS -->|"new DebuggingExecutor()"| DE
    DMS -->|"new ConfigurationManager()"| DCM
    DMS -->|"new DebuggingHandler(executor, configMgr, timeout)"| DH
    
    DMS -->|"dynamic import"| FASTMCP
    DMS -->|"z.object() validation"| ZOD
    
    DH -->|"depends on"| DE
    DH -->|"depends on"| DCM
    
    DE -->|"calls"| VSCODE
    DCM -->|"calls"| VSCODE
    ACM -->|"calls"| VSCODE
```

The dependency graph shows how components are constructed through dependency injection. `DebugMCPServer` acts as a factory that creates the executor and configuration manager, then injects them into `DebuggingHandler`. This pattern promotes testability and loose coupling.

Sources: [src/debugMCPServer.ts:41-47](), [src/index.ts:4-11](), [AGENTS.md:62-66]()

## Component Initialization Flow

```mermaid
sequenceDiagram
    participant EXT as "extension.ts<br/>activate()"
    participant DMS as "DebugMCPServer"
    participant FMCP as "FastMCP"
    participant DH as "DebuggingHandler"
    participant DE as "DebuggingExecutor"
    participant DCM as "ConfigurationManager"
    
    EXT->>DMS: new DebugMCPServer(port, timeout)
    
    Note over DMS: Constructor creates components
    DMS->>DE: new DebuggingExecutor()
    DMS->>DCM: new ConfigurationManager()
    DMS->>DH: new DebuggingHandler(executor, configMgr, timeout)
    
    EXT->>DMS: initialize()
    DMS->>FMCP: dynamic import('fastmcp')
    FMCP-->>DMS: FastMCP class
    
    DMS->>FMCP: new FastMCP({name, version, ping})
    DMS->>DMS: setupTools()
    
    Note over DMS: Register 13 tools
    loop For each tool
        DMS->>FMCP: addTool({name, description, parameters, execute})
    end
    
    DMS->>DMS: setupResources()
    
    Note over DMS: Register documentation resources
    loop For each resource
        DMS->>FMCP: addResource({uri, name, description, load})
    end
    
    EXT->>DMS: start()
    DMS->>FMCP: start({transportType: 'httpStream', port, endpoint: '/sse'})
    FMCP-->>DMS: Server started
    
    Note over DMS,FMCP: Server ready to accept MCP connections
```

This sequence diagram shows the exact initialization flow from extension activation through component creation to server startup. The `DebugMCPServer` constructor [src/debugMCPServer.ts:41-47]() performs dependency injection, creating the executor and configuration manager before passing them to the handler.

Sources: [src/debugMCPServer.ts:41-71](), [docs/architecture/debugMCPServer.md:50-56]()

## Tool Registration and Delegation

```mermaid
graph TB
    subgraph "MCP Tool Layer"
        T1["start_debugging<br/>tool"]
        T2["stop_debugging<br/>tool"]
        T3["step_over<br/>tool"]
        T4["add_breakpoint<br/>tool"]
        T5["get_variables_values<br/>tool"]
        T6["evaluate_expression<br/>tool"]
        TOTHER["...7 more tools"]
    end
    
    subgraph "Handler Methods"
        H1["handleStartDebugging()<br/>line 47-85"]
        H2["handleStopDebugging()<br/>line 90-103"]
        H3["handleStepOver()<br/>line 126-145"]
        H4["handleAddBreakpoint()<br/>line 244-280"]
        H5["handleGetVariables()<br/>line 343-388"]
        H6["handleEvaluateExpression()<br/>line 393-422"]
        HOTHER["...7 more handlers"]
    end
    
    subgraph "Executor Methods"
        E1["startDebugging()<br/>vscode.debug.startDebugging"]
        E2["stopDebugging()<br/>vscode.debug.stopDebugging"]
        E3["stepOver()<br/>session.customRequest('next')"]
        E4["addBreakpoint()<br/>vscode.debug.addBreakpoints"]
        E5["getVariables()<br/>session.customRequest('scopes')<br/>session.customRequest('variables')"]
        E6["evaluateExpression()<br/>session.customRequest('evaluate')"]
        EOTHER["...more executor methods"]
    end
    
    T1 -->|"execute: async (args)"| H1
    T2 -->|"execute: async ()"| H2
    T3 -->|"execute: async ()"| H3
    T4 -->|"execute: async (args)"| H4
    T5 -->|"execute: async (args)"| H5
    T6 -->|"execute: async (args)"| H6
    TOTHER --> HOTHER
    
    H1 --> E1
    H2 --> E2
    H3 --> E3
    H4 --> E4
    H5 --> E5
    H6 --> E6
    HOTHER --> EOTHER
    
    E1 -.->|"DAP Protocol"| VSCODE["VS Code Debug API"]
    E2 -.-> VSCODE
    E3 -.-> VSCODE
    E4 -.-> VSCODE
    E5 -.-> VSCODE
    E6 -.-> VSCODE
    EOTHER -.-> VSCODE
```

The tool registration happens in `setupTools()` [src/debugMCPServer.ts:76-220](). Each tool's `execute` callback delegates directly to a corresponding handler method, which orchestrates the operation and calls the executor. This three-tier delegation ensures separation of concerns: protocol parsing (tools), workflow orchestration (handlers), and API execution (executor).

Sources: [src/debugMCPServer.ts:76-220](), [src/debuggingHandler.ts:12-26](), [docs/architecture/debugMCPServer.md:58-71]()

## Request Processing Flow

```mermaid
sequenceDiagram
    participant AI as "AI Agent"
    participant TOOL as "MCP Tool<br/>(start_debugging)"
    participant DH as "DebuggingHandler<br/>handleStartDebugging()"
    participant DCM as "ConfigurationManager<br/>getDebugConfig()"
    participant DE as "DebuggingExecutor<br/>startDebugging()"
    participant VS as "vscode.debug API"
    participant DS as "DebugState"
    
    AI->>TOOL: POST /sse with tool call
    TOOL->>DH: execute(args: {fileFullPath, workingDirectory, testName})
    
    DH->>DCM: promptForConfiguration(workingDirectory)
    DCM-->>DH: selectedConfigName
    
    DH->>DCM: getDebugConfig(workingDirectory, fileFullPath, configName, testName)
    Note over DCM: Check launch.json or generate default
    DCM-->>DH: DebugConfiguration
    
    DH->>DE: startDebugging(workingDirectory, debugConfig)
    DE->>VS: vscode.debug.startDebugging(folder, config)
    VS-->>DE: boolean (started)
    
    Note over DH: Wait for session activation
    DH->>DH: waitForActiveDebugSession()
    
    loop Exponential backoff polling
        DH->>DE: hasActiveSession()
        DE->>VS: vscode.debug.activeDebugSession
        VS-->>DE: session | undefined
        DE-->>DH: boolean
        Note over DH: Sleep with exponential backoff
    end
    
    Note over DH: Session active, get state
    DH->>DE: getCurrentDebugState(numNextLines)
    DE->>VS: activeDebugSession.customRequest('stackTrace')
    VS-->>DE: stack frames
    DE->>DS: new DebugState(...)
    DS-->>DE: state
    DE-->>DH: DebugState
    
    DH->>DH: formatDebugState(state)
    DH-->>TOOL: formatted string response
    TOOL-->>AI: Tool result
```

This detailed sequence shows the complete request processing flow for `start_debugging`. Key aspects:
- Configuration resolution happens before debugging starts [src/debuggingHandler.ts:55-63]()
- Exponential backoff with jitter waits for session activation [src/debuggingHandler.ts:476-500]()
- State capture happens immediately after session becomes active [src/debuggingHandler.ts:77]()
- Formatted state is returned to the AI agent [src/debuggingHandler.ts:78]()

Sources: [src/debuggingHandler.ts:47-85](), [src/debuggingHandler.ts:476-500](), [docs/architecture/debugMCPServer.md:43-48]()

## State Change Detection

```mermaid
graph TB
    subgraph "Step Command Flow"
        CMD["step_over/step_into/step_out<br/>handler method"]
        BEFORE["getCurrentDebugState()<br/>capture before state"]
        EXEC["executor.stepOver/Into/Out()<br/>session.customRequest('next'/'stepIn'/'stepOut')"]
        WAIT["waitForStateChange(beforeState)<br/>exponential backoff polling"]
        AFTER["getCurrentDebugState()<br/>capture after state"]
        CHECK["hasStateChanged(before, after)<br/>compare states"]
        FORMAT["formatDebugState(afterState)<br/>return formatted result"]
    end
    
    subgraph "State Comparison Checks"
        C1["sessionActive changed?"]
        C2["fileFullPath changed?"]
        C3["currentLine changed?"]
        C4["frameName changed?"]
        C5["frameId changed?"]
    end
    
    CMD --> BEFORE
    BEFORE --> EXEC
    EXEC --> WAIT
    
    WAIT --> AFTER
    AFTER --> CHECK
    
    CHECK --> C1
    C1 -->|"yes"| FORMAT
    C1 -->|"no"| C2
    C2 -->|"yes"| FORMAT
    C2 -->|"no"| C3
    C3 -->|"yes"| FORMAT
    C3 -->|"no"| C4
    C4 -->|"yes"| FORMAT
    C4 -->|"no"| C5
    C5 -->|"yes or timeout"| FORMAT
    
    FORMAT --> RETURN["Return to AI agent"]
```

State change detection [src/debuggingHandler.ts:505-536]() ensures that step commands don't return until the debugger state has actually changed. The `hasStateChanged()` method [src/debuggingHandler.ts:541-584]() compares multiple attributes: session status, file path, line number, frame name, and frame ID. This prevents race conditions where the VS Code API returns before the debugger has actually moved.

Sources: [src/debuggingHandler.ts:505-584](), [src/debuggingHandler.ts:126-145](), [AGENTS.md:58]()

## Resource Loading

```mermaid
graph LR
    subgraph "MCP Resources"
        R1["debugmcp://docs/debug_instructions<br/>uri"]
        R2["debugmcp://docs/troubleshooting/python<br/>uri"]
        R3["debugmcp://docs/troubleshooting/javascript<br/>uri"]
        R4["debugmcp://docs/troubleshooting/java<br/>uri"]
        R5["debugmcp://docs/troubleshooting/csharp<br/>uri"]
    end
    
    subgraph "Resource Loader"
        LOAD["loadMarkdownFile(relativePath)<br/>line 268-285"]
    end
    
    subgraph "File System"
        F1["docs/agent-resources/debug_instructions.md"]
        F2["docs/agent-resources/troubleshooting/python.md"]
        F3["docs/agent-resources/troubleshooting/javascript.md"]
        F4["docs/agent-resources/troubleshooting/java.md"]
        F5["docs/agent-resources/troubleshooting/csharp.md"]
    end
    
    R1 -->|"load callback"| LOAD
    R2 -->|"load callback"| LOAD
    R3 -->|"load callback"| LOAD
    R4 -->|"load callback"| LOAD
    R5 -->|"load callback"| LOAD
    
    LOAD -->|"fs.promises.readFile()"| F1
    LOAD -->|"fs.promises.readFile()"| F2
    LOAD -->|"fs.promises.readFile()"| F3
    LOAD -->|"fs.promises.readFile()"| F4
    LOAD -->|"fs.promises.readFile()"| F5
```

MCP resources provide AI agents with documentation about how to use the debugging tools effectively. The `setupResources()` method [src/debugMCPServer.ts:225-263]() registers resources with lazy-loading callbacks. When an agent requests a resource, `loadMarkdownFile()` [src/debugMCPServer.ts:268-285]() reads the content from the `docs/agent-resources/` directory.

Sources: [src/debugMCPServer.ts:225-285](), [AGENTS.md:86-93](), [docs/architecture/debugMCPServer.md:73-79]()

## Configuration Management

```mermaid
graph TB
    subgraph "Configuration Types"
        LAUNCH["launch.json<br/>(user-defined configs)"]
        DEFAULT["Default Configs<br/>(language-specific)"]
        TEST["Test Configs<br/>(framework-specific)"]
    end
    
    subgraph "ConfigurationManager Methods"
        PROMPT["promptForConfiguration()<br/>Get user selection"]
        GET["getDebugConfig()<br/>Resolve configuration"]
        DETECT["detectLanguageFromFilePath()<br/>File extension mapping"]
        CREATE_DEFAULT["createDefaultDebugConfig()<br/>Language-specific defaults"]
        CREATE_TEST["createTestDebugConfig()<br/>Test framework configs"]
    end
    
    subgraph "Language Detection"
        PY[".py → python"]
        JS[".js, .ts → javascript/typescript"]
        JAVA[".java → java"]
        CS[".cs → csharp"]
        CPP[".cpp, .c → cpp"]
        GO[".go → go"]
        RUST[".rs → rust"]
        PHP[".php → php"]
        RUBY[".rb → ruby"]
    end
    
    PROMPT --> GET
    GET --> LAUNCH
    GET --> DETECT
    
    DETECT --> PY
    DETECT --> JS
    DETECT --> JAVA
    DETECT --> CS
    DETECT --> CPP
    DETECT --> GO
    DETECT --> RUST
    DETECT --> PHP
    DETECT --> RUBY
    
    PY --> CREATE_DEFAULT
    JS --> CREATE_DEFAULT
    JAVA --> CREATE_DEFAULT
    CS --> CREATE_DEFAULT
    CPP --> CREATE_DEFAULT
    GO --> CREATE_DEFAULT
    RUST --> CREATE_DEFAULT
    PHP --> CREATE_DEFAULT
    RUBY --> CREATE_DEFAULT
    
    PY --> CREATE_TEST
    JS --> CREATE_TEST
    JAVA --> CREATE_TEST
    CS --> CREATE_TEST
    
    CREATE_DEFAULT --> DEFAULT
    CREATE_TEST --> TEST
```

The `DebugConfigurationManager` provides a hierarchical configuration system. It first checks for user-defined configurations in `launch.json`, then falls back to language-specific defaults. Language detection uses file extensions, and each language has tailored debug configurations including test framework support (unittest for Python, Jest/Mocha for JavaScript, JUnit for Java, dotnet test for C#).

Sources: [src/utils/debugConfigurationManager.ts](), [AGENTS.md:21](), [src/index.ts:6]()

## Component Communication Patterns

The components implement three key communication patterns:

### 1. Dependency Injection Pattern
Components are constructed with their dependencies injected via constructor parameters:
- `DebuggingHandler(executor, configManager, timeout)` [src/debuggingHandler.ts:36-42]()
- Promotes testability by allowing mock implementations
- Ensures loose coupling between layers

### 2. Interface-Based Contracts
Each layer defines interfaces to formalize contracts:
- `IDebuggingHandler` [src/debuggingHandler.ts:12-26]()
- `IDebuggingExecutor` [src/index.ts:5]()
- `IDebugConfigurationManager` [src/debuggingHandler.ts:4]()
- Allows implementation swapping without affecting consumers

### 3. Exponential Backoff Polling
Asynchronous operations use exponential backoff with jitter:
- `waitForActiveDebugSession()` [src/debuggingHandler.ts:476-500]()
- `waitForStateChange()` [src/debuggingHandler.ts:505-536]()
- Balances responsiveness with resource usage

Sources: [src/debuggingHandler.ts:36-42](), [src/debuggingHandler.ts:476-536](), [AGENTS.md:58]()

## Error Handling Strategy

All components implement consistent error handling:

| Layer | Error Handling Approach | Example |
|-------|------------------------|---------|
| Protocol Layer | Catch and format errors for MCP response | Tool `execute` callbacks wrap handler calls |
| Orchestration Layer | Throw descriptive errors with context | `throw new Error(\`Error starting debug session: ${error}\`)` [src/debuggingHandler.ts:83]() |
| Execution Layer | Validate preconditions, throw on invalid state | Check `hasActiveSession()` before operations |

Errors propagate up the stack with added context at each layer, providing AI agents with actionable error messages.

Sources: [src/debuggingHandler.ts:82-84](), [src/debuggingHandler.ts:128-130](), [AGENTS.md:56]()

## Next Steps

For detailed information about each component:
- [DebugMCP Server](#4.1) - MCP protocol implementation, tool/resource registration
- [Debugging Handler](#4.2) - Operation orchestration and state management  
- [Debugging Executor](#4.3) - VS Code API interface and DAP communication
- [Debug Configuration Manager](#4.4) - Configuration resolution and language detection
- [Agent Configuration Manager](#4.5) - AI agent auto-configuration

For understanding how these components work together in practice, see [Request Flow](#3.3) and [Debugging Operations](#5).

---

