<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/screenenv · page 4 User Guides · fetched 2026-10-26 -->

# User Guides

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [src/screenenv/sandbox.py](src/screenenv/sandbox.py)

</details>



This page provides comprehensive guides for using ScreenEnv in different scenarios, covering both direct programming interfaces and AI agent integration patterns. ScreenEnv offers two primary access methods: direct control through the `Sandbox` class for programmatic automation, and standardized AI integration through the Model Context Protocol (MCP) server.

For detailed installation and basic setup instructions, see [Getting Started](#3). For complete API documentation, see [API Reference](#6).

## Usage Patterns Overview

ScreenEnv supports multiple usage patterns depending on your automation needs and integration requirements:

**Usage Pattern Decision Flow**

```mermaid
flowchart TD
    Start["User needs desktop automation"]
    
    PythonDev{"Direct Python<br/>programming?"}
    AIDriven{"AI/LLM<br/>integration?"}
    
    SandboxPath["Sandbox Class<br/>Direct Programming"]
    MCPPath["MCP Server<br/>AI Integration"]
    
    SandboxAPI["sandbox.execute_command()<br/>sandbox.left_click()<br/>sandbox.screenshot()"]
    MCPTools["MCP Tools:<br/>execute_command<br/>left_click<br/>screenshot"]
    
    DirectDemo["examples/sandbox_demo.py"]
    MCPDemo["examples/mcp_server_demo.py"]
    DesktopAgent["examples/desktop_agent.py"]
    
    Start --> PythonDev
    Start --> AIDriven
    
    PythonDev -->|Yes| SandboxPath
    AIDriven -->|Yes| MCPPath
    
    SandboxPath --> SandboxAPI
    MCPPath --> MCPTools
    
    SandboxAPI --> DirectDemo
    MCPTools --> MCPDemo
    MCPTools --> DesktopAgent
    
    classDef userNeed fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef interface fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef implementation fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef examples fill:#ffebee,stroke:#c62828,stroke-width:2px
    
    class Start userNeed
    class PythonDev,AIDriven decision
    class SandboxPath,MCPPath interface
    class SandboxAPI,MCPTools implementation
    class DirectDemo,MCPDemo,DesktopAgent examples
```

Sources: [README.md:47-147](), [examples/sandbox_demo.py:1-50](), [examples/mcp_server_demo.py:1-50]()

## Core Classes and Entry Points

The following diagram maps user automation needs to specific ScreenEnv classes and their key methods:

**Code Entity Mapping**

```mermaid
flowchart LR
    subgraph "User Requirements"
        MouseControl["Mouse Control"]
        KeyboardInput["Keyboard Input"]
        AppManagement["Application Management"]
        FileOps["File Operations"]
        ScreenCapture["Screen Capture"]
        WebAutomation["Web Automation"]
        CommandExecution["Command Execution"]
        AIIntegration["AI Integration"]
    end
    
    subgraph "Core Classes"
        SandboxClass["Sandbox<br/>(src/screenenv/sandbox.py)"]
        MCPServer["MCPRemoteServer<br/>(src/screenenv/mcp_server.py)"]
        RemoteScreenEnv["RemoteScreenEnv<br/>(src/screenenv/remote_screen_env.py)"]
    end
    
    subgraph "Key Methods"
        MouseMethods["left_click()<br/>right_click()<br/>move_mouse()<br/>drag()"]
        KeyboardMethods["write()<br/>press()"]
        AppMethods["launch()<br/>activate_window()<br/>close_window()"]
        FileMethods["upload_file_to_remote()<br/>download_file_from_remote()"]
        ScreenMethods["screenshot()<br/>desktop_screenshot()"]
        WebMethods["open()<br/>playwright_screenshot()"]
        CommandMethods["execute_command()"]
        MCPTools["30+ MCP Tools<br/>via call_tool()"]
    end
    
    MouseControl --> SandboxClass
    KeyboardInput --> SandboxClass
    AppManagement --> SandboxClass
    FileOps --> SandboxClass
    ScreenCapture --> SandboxClass
    WebAutomation --> SandboxClass
    CommandExecution --> SandboxClass
    AIIntegration --> MCPServer
    
    SandboxClass --> MouseMethods
    SandboxClass --> KeyboardMethods
    SandboxClass --> AppMethods
    SandboxClass --> FileMethods
    SandboxClass --> ScreenMethods
    SandboxClass --> WebMethods
    SandboxClass --> CommandMethods
    
    MCPServer --> MCPTools
    
    SandboxClass -.-> RemoteScreenEnv
    MCPServer -.-> RemoteScreenEnv
    
    classDef userReq fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef coreClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef methods fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    
    class MouseControl,KeyboardInput,AppManagement,FileOps,ScreenCapture,WebAutomation,CommandExecution,AIIntegration userReq
    class SandboxClass,MCPServer,RemoteScreenEnv coreClass
    class MouseMethods,KeyboardMethods,AppMethods,FileMethods,ScreenMethods,WebMethods,CommandMethods,MCPTools methods
```

Sources: [src/screenenv/sandbox.py:42-654](), [src/screenenv/mcp_server.py:1-50](), [README.md:149-187]()

## Workflow Comparison

| Aspect | Direct Programming | AI Integration |
|--------|-------------------|----------------|
| **Entry Point** | `Sandbox()` class | `MCPRemoteServer()` class |
| **Access Pattern** | Direct method calls | MCP protocol tools |
| **Best For** | Custom automation scripts | AI-driven automation |
| **Code Location** | [src/screenenv/sandbox.py:42-654]() | [src/screenenv/mcp_server.py:1-50]() |
| **Example Usage** | `sandbox.left_click(100, 200)` | `call_tool("left_click", {"x": 100, "y": 200})` |
| **Integration** | Python applications | AI agents, LLMs |
| **Available Operations** | All `Sandbox` methods | 30+ standardized MCP tools |

## Quick Start Reference

### Direct Programming Pattern

```python
from screenenv import Sandbox

# Initialize sandbox
sandbox = Sandbox(headless=True)

# Basic operations
sandbox.launch("xfce4-terminal")
sandbox.write("echo 'Hello World'")
sandbox.press("Enter")
screenshot = sandbox.screenshot()

# Cleanup
sandbox.close()
```

### AI Integration Pattern

```python
from screenenv import MCPRemoteServer

# Start MCP server
server = MCPRemoteServer()
print(f"MCP Server URL: {server.server_url}")

# Use with MCP clients
# (See detailed examples in AI Agent Integration guide)
```

Sources: [README.md:49-71](), [README.md:91-99]()

## Configuration Options

Both `Sandbox` and `MCPRemoteServer` support identical configuration parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `headless` | bool | `True` | Run without VNC viewer |
| `resolution` | tuple | `(1920, 1080)` | Screen resolution |
| `ram_size` | str | `"4G"` | Container RAM allocation |
| `cpu_cores` | str | `"4"` | Container CPU cores |
| `timeout` | int | `1000` | Operation timeout in seconds |

Sources: [src/screenenv/sandbox.py:55-90](), [README.md:192-206]()

## Navigation to Detailed Guides

- **For step-by-step direct programming instructions**: See [Direct Programming Interface](#4.1)
- **For AI agent integration and MCP usage**: See [AI Agent Integration](#4.2)
- **For practical examples and demonstrations**: See [Examples and Demos](#5)

Each sub-guide provides comprehensive coverage of its respective usage pattern, including detailed code examples, best practices, and troubleshooting information.

Sources: [README.md:1-426](), [src/screenenv/sandbox.py:1-730]()

---

