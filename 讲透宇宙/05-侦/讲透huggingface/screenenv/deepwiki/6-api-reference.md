<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/screenenv · page 6 API Reference · fetched 2026-10-26 -->

# API Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/screenenv/mcp_remote_server.py](src/screenenv/mcp_remote_server.py)
- [src/screenenv/sandbox.py](src/screenenv/sandbox.py)

</details>



This document provides a comprehensive technical reference for all ScreenEnv APIs, classes, and methods. It covers the complete public interface for interacting with desktop environments programmatically and through AI agents.

For practical usage examples and step-by-step guides, see [User Guides](#4). For implementation details about the underlying architecture, see [Architecture](#2).

## API Architecture Overview

ScreenEnv provides multiple API layers designed for different access patterns and use cases. The system is built around a common base class with specialized implementations for different interaction modes.

### Core API Classes

```mermaid
classDiagram
    class RemoteScreenEnv {
        +os_type: Literal
        +provider_type: Literal
        +resolution: tuple
        +session_password: str
        +base_url: str
        +start()
        +close()
        +get_provider_id()
    }
    
    class Sandbox {
        +execute_command(command: str) CommandResponse
        +left_click(x: int, y: int)
        +right_click(x: int, y: int)
        +write(text: str)
        +press(key: str)
        +screenshot() bytes
        +open(file_or_url: str)
        +launch(application: str)
        +upload_file_to_remote(local_path: str, remote_path: str)
        +download_file_from_remote(remote_path: str, local_dest: str)
        +get_playwright_browser() Browser
    }
    
    class MCPRemoteServer {
        +mcp_server_json: dict
        +base_url: str
    }
    
    RemoteScreenEnv <|-- Sandbox
    RemoteScreenEnv <|-- MCPRemoteServer
    
    note for Sandbox "Direct programming interface\nfor Python applications"
    note for MCPRemoteServer "AI agent interface\nvia MCP protocol"
```

**Sources:** [src/screenenv/sandbox.py:42-654](), [src/screenenv/mcp_remote_server.py:9-52]()

### API Access Patterns

```mermaid
graph TB
    subgraph "Python_Programming_Access"
        PythonApp["Python Applications"]
        DirectCode["Direct Code Integration"]
        TestAutomation["Test Automation"]
    end
    
    subgraph "AI_Agent_Access"
        MCPClients["MCP Clients"]
        LLMSystems["LLM Systems"]
        AIAgents["AI Agents"]
    end
    
    subgraph "Core_API_Classes"
        SandboxAPI["Sandbox Class"]
        MCPServerAPI["MCPRemoteServer Class"]
    end
    
    subgraph "Remote_Environment_Layer"
        RemoteScreenEnvBase["RemoteScreenEnv Base Class"]
        DockerProvider["DockerProvider"]
        StreamServer["StreamServer"]
    end
    
    subgraph "Desktop_Environment"
        Container["Docker Container"]
        DesktopSession["Desktop Session"]
        Applications["Applications"]
    end
    
    PythonApp --> SandboxAPI
    DirectCode --> SandboxAPI
    TestAutomation --> SandboxAPI
    
    MCPClients --> MCPServerAPI
    LLMSystems --> MCPServerAPI
    AIAgents --> MCPServerAPI
    
    SandboxAPI --> RemoteScreenEnvBase
    MCPServerAPI --> RemoteScreenEnvBase
    
    RemoteScreenEnvBase --> DockerProvider
    RemoteScreenEnvBase --> StreamServer
    
    DockerProvider --> Container
    Container --> DesktopSession
    DesktopSession --> Applications
```

**Sources:** [src/screenenv/sandbox.py:42-90](), [src/screenenv/mcp_remote_server.py:9-44]()

## Primary API Classes

### Sandbox Class

The `Sandbox` class provides direct programmatic access to desktop environments with comprehensive mouse, keyboard, and application control capabilities.

| Category | Key Methods | Description |
|----------|-------------|-------------|
| **Mouse Control** | `left_click()`, `right_click()`, `double_click()`, `move_mouse()`, `drag()` | Complete mouse interaction capabilities |
| **Keyboard Control** | `write()`, `press()`, `key_combinations` | Text input and keyboard shortcuts |
| **Application Management** | `launch()`, `open()`, `get_application_windows()`, `activate_window()` | Launch and manage desktop applications |
| **File Operations** | `upload_file_to_remote()`, `download_file_from_remote()`, `directory_tree()` | File system operations |
| **Screen Capture** | `screenshot()`, `desktop_screenshot()`, `playwright_screenshot()` | Screenshot capabilities |
| **Command Execution** | `execute_command()`, `execute_python_command()` | Terminal and Python command execution |
| **Browser Integration** | `get_playwright_browser()`, `_chrome_open_tabs_setup()` | Web browser automation |

**Sources:** [src/screenenv/sandbox.py:42-654]()

### MCPRemoteServer Class

The `MCPRemoteServer` class provides AI-compatible access through the Model Context Protocol, enabling seamless integration with AI agents and language models.

| Feature | Implementation | Description |
|---------|----------------|-------------|
| **MCP Protocol** | `mcp_server_json` configuration | Standardized AI agent interface |
| **Transport** | `streamable-http` | HTTP-based communication protocol |
| **Base URL** | `base_url` property | Server endpoint for MCP clients |
| **Environment Management** | Inherited from `RemoteScreenEnv` | Same environment capabilities as Sandbox |

**Sources:** [src/screenenv/mcp_remote_server.py:9-52]()

## API Method Categories

### Environment Management

```mermaid
graph LR
    subgraph "Environment_Lifecycle"
        Init["__init__()"]
        Start["start()"]
        Close["close()"]
    end
    
    subgraph "Environment_Info"
        GetProviderID["get_provider_id()"]
        Platform["platform()"]
        ScreenSize["get_screen_size()"]
        DesktopPath["desktop_path()"]
    end
    
    subgraph "Session_Management"
        SessionPassword["session_password"]
        BaseURL["base_url"]
        ServerURL["server_url"]
    end
    
    Init --> Start
    Start --> GetProviderID
    GetProviderID --> Platform
    Platform --> ScreenSize
    ScreenSize --> DesktopPath
    Close --> Init
    
    SessionPassword --> Start
    BaseURL --> Start
    ServerURL --> Start
```

**Sources:** [src/screenenv/sandbox.py:55-90](), [src/screenenv/mcp_remote_server.py:10-44]()

### Input/Output Operations

```mermaid
graph TB
    subgraph "Mouse_Operations"
        LeftClick["left_click(x, y)"]
        RightClick["right_click(x, y)"]
        DoubleClick["double_click(x, y)"]
        MoveMouse["move_mouse(x, y)"]
        Drag["drag(fr, to)"]
        Scroll["scroll(direction, amount)"]
    end
    
    subgraph "Keyboard_Operations"
        Write["write(text, delay_in_ms)"]
        Press["press(key)"]
        KeyCombinations["press([key1, key2])"]
    end
    
    subgraph "Screen_Operations"
        Screenshot["screenshot()"]
        DesktopScreenshot["desktop_screenshot()"]
        PlaywrightScreenshot["playwright_screenshot()"]
        GetCursorPosition["get_cursor_position()"]
    end
    
    subgraph "File_Operations"
        UploadFile["upload_file_to_remote()"]
        DownloadFile["download_file_from_remote()"]
        DownloadURL["download_url_file_to_remote()"]
        DirectoryTree["directory_tree()"]
    end
    
    LeftClick --> GetCursorPosition
    Write --> Press
    Screenshot --> DesktopScreenshot
    UploadFile --> DownloadFile
```

**Sources:** [src/screenenv/sandbox.py:537-646]()

## Response Models and Data Types

The API uses strongly-typed response models for all operations:

| Response Type | Purpose | Key Fields |
|---------------|---------|------------|
| `CommandResponse` | Terminal command results | `status`, `output`, `error`, `returncode` |
| `ScreenSizeResponse` | Screen dimensions | `width`, `height` |
| `WindowInfoResponse` | Window information | `window_id`, `window_name` |
| `RecordingResponse` | Video recording metadata | `path`, `size`, `format` |
| `AccessibilityTreeResponse` | UI element tree | `tree_data` |
| `DirectoryTreeResponse` | File system structure | `tree_structure` |

**Sources:** [src/screenenv/sandbox.py:21-35]()

## Error Handling and Retry Logic

The API implements comprehensive error handling with automatic retry mechanisms:

```mermaid
graph TD
    subgraph "Request_Flow"
        MakeRequest["_make_request()"]
        RetryDecorator["@retry(times=10, interval=5.0)"]
        HTTPRequest["requests.request()"]
        StatusCheck["status_code >= 400"]
        ErrorHandling["Exception with details"]
    end
    
    subgraph "Retry_Configuration"
        RetryTimes["retry_times: int = 10"]
        RetryInterval["retry_interval: int = 5"]
        TimeoutConfig["timeout: int = 120"]
    end
    
    RetryDecorator --> MakeRequest
    MakeRequest --> HTTPRequest
    HTTPRequest --> StatusCheck
    StatusCheck --> ErrorHandling
    
    RetryTimes --> RetryDecorator
    RetryInterval --> RetryDecorator
    TimeoutConfig --> HTTPRequest
```

**Sources:** [src/screenenv/sandbox.py:115-153]()

## Detailed API References

For comprehensive method documentation and examples:

- **[Sandbox API](#6.1)** - Complete reference for direct programming interface
- **[MCP Server API](#6.2)** - Model Context Protocol integration reference  
- **[Provider System API](#6.3)** - Remote environment provider interface reference

Each sub-section provides detailed parameter specifications, return types, usage examples, and implementation notes for their respective API components.

---

