<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/screenenv · page 2 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [src/screenenv/__init__.py](src/screenenv/__init__.py)

</details>



This document describes the high-level architecture of ScreenEnv, explaining how the core components work together to provide desktop automation capabilities. It covers the system's layered design, component relationships, and the different access patterns available to users.

For implementation details of specific components, see [Core Components](#2.1) and [Remote Environment Providers](#2.2). For practical usage guidance, see [User Guides](#4).

## System Overview

ScreenEnv follows a layered architecture that separates concerns between user interfaces, core automation logic, remote environment management, and the containerized desktop environment. The system provides multiple access patterns to accommodate different use cases, from direct Python programming to AI-driven automation through the Model Context Protocol (MCP).

### High-Level Architecture

```mermaid
graph TB
    subgraph "User Interface Layer"
        PythonApp["Python Applications"]
        AISystem["AI/LLM Systems"]
        DemoScripts["Demo Scripts"]
    end
    
    subgraph "Core API Layer"
        Sandbox["Sandbox Class"]
        MCPRemoteServer["MCPRemoteServer Class"]
        DesktopAgentBase["DesktopAgentBase Class"]
    end
    
    subgraph "Environment Management Layer"
        RemoteScreenEnv["RemoteScreenEnv Class"]
        DockerProvider["DockerProvider"]
        StreamServer["StreamServer (VNC/noVNC)"]
    end
    
    subgraph "Container Runtime"
        DockerContainer["Docker Container"]
        UbuntuDesktop["Ubuntu 22.04 + XFCE4"]
        Applications["Chrome, LibreOffice, Terminal"]
        PlaywrightRuntime["Playwright Runtime"]
    end
    
    subgraph "External Dependencies"
        DockerDaemon["Docker Daemon"]
        OpenAIAPI["OpenAI API"]
        HuggingFaceHub["HuggingFace Hub"]
    end
    
    PythonApp --> Sandbox
    AISystem --> MCPRemoteServer
    DemoScripts --> Sandbox
    DemoScripts --> MCPRemoteServer
    DemoScripts --> DesktopAgentBase
    
    Sandbox --> RemoteScreenEnv
    MCPRemoteServer --> RemoteScreenEnv
    DesktopAgentBase --> Sandbox
    
    RemoteScreenEnv --> DockerProvider
    RemoteScreenEnv --> StreamServer
    
    DockerProvider --> DockerContainer
    DockerContainer --> UbuntuDesktop
    UbuntuDesktop --> Applications
    UbuntuDesktop --> PlaywrightRuntime
    
    DockerProvider --> DockerDaemon
    DesktopAgentBase --> OpenAIAPI
    DesktopAgentBase --> HuggingFaceHub
```

Sources: [README.md:1-426](), [src/screenenv/__init__.py:1-16]()

## Core Component Relationships

The system is built around three primary components that provide different levels of abstraction and access patterns for desktop automation.

### Component Interaction Flow

```mermaid
graph LR
    subgraph "Direct Programming"
        DirectUser["Python Developer"]
        SandboxAPI["Sandbox API"]
    end
    
    subgraph "AI Integration"
        AIAgent["AI Agent"]
        MCPServer["MCPRemoteServer"]
        MCPTools["30+ MCP Tools"]
    end
    
    subgraph "Core Environment"
        RemoteScreenEnv["RemoteScreenEnv"]
        DockerProvider["DockerProvider"]
        ContainerEnv["Container Environment"]
    end
    
    subgraph "Automation Capabilities"
        MouseControl["Mouse Control"]
        KeyboardInput["Keyboard Input"]
        WindowManagement["Window Management"]
        FileOperations["File Operations"]
        ScreenCapture["Screen Capture"]
        CommandExecution["Command Execution"]
    end
    
    DirectUser --> SandboxAPI
    AIAgent --> MCPServer
    MCPServer --> MCPTools
    
    SandboxAPI --> RemoteScreenEnv
    MCPTools --> RemoteScreenEnv
    
    RemoteScreenEnv --> DockerProvider
    DockerProvider --> ContainerEnv
    
    ContainerEnv --> MouseControl
    ContainerEnv --> KeyboardInput
    ContainerEnv --> WindowManagement
    ContainerEnv --> FileOperations
    ContainerEnv --> ScreenCapture
    ContainerEnv --> CommandExecution
```

Sources: [README.md:47-71](), [README.md:91-147](), [src/screenenv/__init__.py:1-16]()

### Component Responsibilities

| Component | Primary Responsibility | Key Methods/Features |
|-----------|----------------------|---------------------|
| `Sandbox` | Direct programmatic control | `left_click()`, `write()`, `launch()`, `screenshot()` |
| `MCPRemoteServer` | AI agent integration via MCP protocol | 30+ MCP tools, HTTP transport, tool calling |
| `DesktopAgentBase` | High-level AI automation framework | Agent orchestration, LLM integration |
| `RemoteScreenEnv` | Environment lifecycle management | Container orchestration, resource management |
| `DockerProvider` | Container backend implementation | Docker container management, networking |

Sources: [README.md:234-331](), [README.md:149-188]()

## Data Flow Architecture

The system processes automation requests through a structured flow from high-level commands to low-level system interactions.

### Request Processing Flow

```mermaid
flowchart TD
    subgraph "Input Processing"
        UserInput["User Input"]
        AIInstruction["AI Instruction"]
        TaskParser["Task Parser"]
        ActionPlanner["Action Planner"]
    end
    
    subgraph "Core Execution"
        SandboxExecutor["Sandbox Executor"]
        MCPToolExecutor["MCP Tool Executor"]
        CommandGenerator["Command Generator"]
    end
    
    subgraph "System Interaction"
        X11Display["X11 Display"]
        FileSystem["File System"]
        NetworkStack["Network Stack"]
        ProcessManager["Process Manager"]
    end
    
    subgraph "Output Generation"
        ScreenCapture["Screen Capture"]
        CommandOutput["Command Output"]
        FileArtifacts["File Artifacts"]
        ExecutionLogs["Execution Logs"]
    end
    
    UserInput --> TaskParser
    AIInstruction --> TaskParser
    TaskParser --> ActionPlanner
    ActionPlanner --> SandboxExecutor
    ActionPlanner --> MCPToolExecutor
    
    SandboxExecutor --> CommandGenerator
    MCPToolExecutor --> CommandGenerator
    
    CommandGenerator --> X11Display
    CommandGenerator --> FileSystem
    CommandGenerator --> NetworkStack
    CommandGenerator --> ProcessManager
    
    X11Display --> ScreenCapture
    ProcessManager --> CommandOutput
    FileSystem --> FileArtifacts
    CommandGenerator --> ExecutionLogs
```

Sources: [README.md:234-331](), [README.md:149-188]()

## Access Patterns

ScreenEnv supports three primary access patterns, each optimized for different use cases and user types.

### Access Pattern Comparison

```mermaid
graph TB
    subgraph "Direct Programming Pattern"
        DevUser["Developer"]
        PythonScript["Python Script"]
        SandboxClass["Sandbox Class"]
        DirectAPI["Direct API Calls"]
    end
    
    subgraph "AI Integration Pattern"
        AIClient["AI Client"]
        MCPProtocol["MCP Protocol"]
        MCPRemoteServerClass["MCPRemoteServer Class"]
        MCPToolsAPI["MCP Tools API"]
    end
    
    subgraph "Agent Framework Pattern"
        AgentDeveloper["Agent Developer"]
        DesktopAgentBaseClass["DesktopAgentBase Class"]
        LLMIntegration["LLM Integration"]
        HighLevelAPI["High-Level API"]
    end
    
    subgraph "Shared Infrastructure"
        RemoteScreenEnvClass["RemoteScreenEnv Class"]
        DockerProviderImpl["DockerProvider Implementation"]
        ContainerRuntime["Container Runtime"]
    end
    
    DevUser --> PythonScript
    PythonScript --> SandboxClass
    SandboxClass --> DirectAPI
    
    AIClient --> MCPProtocol
    MCPProtocol --> MCPRemoteServerClass
    MCPRemoteServerClass --> MCPToolsAPI
    
    AgentDeveloper --> DesktopAgentBaseClass
    DesktopAgentBaseClass --> LLMIntegration
    LLMIntegration --> HighLevelAPI
    
    DirectAPI --> RemoteScreenEnvClass
    MCPToolsAPI --> RemoteScreenEnvClass
    HighLevelAPI --> RemoteScreenEnvClass
    
    RemoteScreenEnvClass --> DockerProviderImpl
    DockerProviderImpl --> ContainerRuntime
```

Sources: [README.md:47-71](), [README.md:91-147](), [src/screenenv/__init__.py:1-16]()

## Technology Stack Integration

The system integrates multiple technologies to provide comprehensive desktop automation capabilities.

### Technology Dependencies

```mermaid
graph TB
    subgraph "Application Layer"
        FastAPIServer["FastAPI Server"]
        MCPHTTPTransport["MCP HTTP Transport"]
        PydanticModels["Pydantic Models"]
    end
    
    subgraph "Automation Layer"
        PlaywrightEngine["Playwright Engine"]
        X11Protocol["X11 Protocol"]
        VNCProtocol["VNC Protocol"]
        DockerAPI["Docker API"]
    end
    
    subgraph "Container Layer"
        UbuntuBase["Ubuntu 22.04 Base"]
        XFCE4Desktop["XFCE4 Desktop"]
        ChromeBrowser["Chrome Browser"]
        LibreOfficesuite["LibreOffice Suite"]
        PythonRuntime["Python Runtime"]
    end
    
    subgraph "Infrastructure Layer"
        DockerDaemonProcess["Docker Daemon Process"]
        NetworkBridge["Network Bridge"]
        VolumeStorage["Volume Storage"]
        ProcessIsolation["Process Isolation"]
    end
    
    FastAPIServer --> MCPHTTPTransport
    MCPHTTPTransport --> PydanticModels
    
    PlaywrightEngine --> X11Protocol
    X11Protocol --> VNCProtocol
    VNCProtocol --> DockerAPI
    
    UbuntuBase --> XFCE4Desktop
    XFCE4Desktop --> ChromeBrowser
    XFCE4Desktop --> LibreOfficesuit
    XFCE4Desktop --> PythonRuntime
    
    DockerAPI --> DockerDaemonProcess
    DockerDaemonProcess --> NetworkBridge
    DockerDaemonProcess --> VolumeStorage
    DockerDaemonProcess --> ProcessIsolation
```

Sources: [README.md:410-426]()

## Environment Lifecycle Management

The system manages the complete lifecycle of desktop environments, from creation to cleanup, with automatic resource management and error handling.

### Environment State Management

```mermaid
stateDiagram-v2
    [*] --> Initializing
    Initializing --> ContainerCreating : create_container()
    ContainerCreating --> ServiceStarting : start_services()
    ServiceStarting --> Ready : environment_ready()
    Ready --> Executing : execute_command()
    Executing --> Ready : command_complete()
    Ready --> Capturing : take_screenshot()
    Capturing --> Ready : capture_complete()
    Ready --> Terminating : close()
    Terminating --> Cleanup : cleanup_resources()
    Cleanup --> [*]
    
    ContainerCreating --> Error : creation_failed()
    ServiceStarting --> Error : service_failed()
    Executing --> Error : execution_failed()
    Error --> Cleanup : cleanup_on_error()
```

Sources: [README.md:208-232](), [README.md:47-71]()

---

