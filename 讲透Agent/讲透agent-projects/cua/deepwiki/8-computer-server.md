<!-- source: DeepWiki mcp.deepwiki.com · repo trycua/cua · page 8 Computer Server · fetched 2026-10-29 -->

# Computer Server

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/content/docs/cua-sdk/reference/runtime-support.mdx](docs/content/docs/cua-sdk/reference/runtime-support.mdx)
- [libs/python/cua-sandbox/CHANGELOG.md](libs/python/cua-sandbox/CHANGELOG.md)
- [libs/python/cua-sandbox/README.md](libs/python/cua-sandbox/README.md)
- [libs/python/cua-sandbox/VERSION](libs/python/cua-sandbox/VERSION)
- [libs/python/cua-sandbox/cua_sandbox/__init__.py](libs/python/cua-sandbox/cua_sandbox/__init__.py)
- [libs/python/cua-sandbox/cua_sandbox/pool.py](libs/python/cua-sandbox/cua_sandbox/pool.py)
- [libs/python/cua-sandbox/cua_sandbox/sandbox.py](libs/python/cua-sandbox/cua_sandbox/sandbox.py)
- [libs/python/cua-sandbox/cua_sandbox/sync/__init__.py](libs/python/cua-sandbox/cua_sandbox/sync/__init__.py)
- [libs/python/cua-sandbox/cua_sandbox/transport/fleet.py](libs/python/cua-sandbox/cua_sandbox/transport/fleet.py)
- [libs/python/cua-sandbox/cua_sandbox/transport/fleet_cloud.py](libs/python/cua-sandbox/cua_sandbox/transport/fleet_cloud.py)
- [libs/python/cua-sandbox/pyproject.toml](libs/python/cua-sandbox/pyproject.toml)
- [libs/python/cua-sandbox/tests/test_fleet_cloud_client.py](libs/python/cua-sandbox/tests/test_fleet_cloud_client.py)
- [libs/python/cua-sandbox/tests/test_fleet_cloud_transport.py](libs/python/cua-sandbox/tests/test_fleet_cloud_transport.py)
- [libs/python/cua-sandbox/tests/test_fleet_sdk_distribution.py](libs/python/cua-sandbox/tests/test_fleet_sdk_distribution.py)
- [libs/python/cua-sandbox/tests/test_fleet_sdk_packaging.py](libs/python/cua-sandbox/tests/test_fleet_sdk_packaging.py)
- [libs/python/cua-sandbox/tests/test_fleet_transport.py](libs/python/cua-sandbox/tests/test_fleet_transport.py)
- [libs/python/cua-sandbox/tests/test_pool.py](libs/python/cua-sandbox/tests/test_pool.py)
- [libs/python/cua-sandbox/tests/test_sandbox_fleet_lifecycle.py](libs/python/cua-sandbox/tests/test_sandbox_fleet_lifecycle.py)
- [libs/python/cua-sandbox/tests/test_vm_cleanup.py](libs/python/cua-sandbox/tests/test_vm_cleanup.py)
- [libs/python/cua-sandbox/uv.lock](libs/python/cua-sandbox/uv.lock)

</details>



The Computer Server is a FastAPI-based HTTP/WebSocket server that runs inside virtual machines or containers to provide programmatic control over the operating system. It exposes a unified API for mouse, keyboard, screen capture, file operations, window management, and command execution across macOS, Linux, Windows, and Android platforms.

For information about the Computer SDK that connects to this server, see [Computer SDK](#3.1). For details on VM providers that host the server, see [Execution Environments](#4).

---

## Purpose and Scope

The Computer Server serves as the **execution endpoint** for computer-use agents. While the Agent SDK and Computer SDK run on the host machine (where the agent code executes), the Computer Server runs **inside the target environment** (VM, container, or sandbox) and performs the actual OS-level operations.

**Key responsibilities:**
- Accept commands via WebSocket, HTTP, or MCP (Model Context Protocol).
- Execute OS automation tasks (mouse clicks, keyboard input, screenshots).
- Provide file system access and window management.
- Provide a standardized tool surface for LLMs via MCP.
- Authenticate cloud-based connections and validate container environments.
- Route commands to OS-specific handlers or the `cua-driver` backend.

The server is installed as the `cua-computer-server` Python package and typically runs on startup inside Cua-managed environments [libs/python/cua-sandbox/pyproject.toml:2-4]().

Sources: [libs/python/cua-sandbox/pyproject.toml:2-4]()

---

## Architecture Overview

The following diagram illustrates the relationship between the host-side SDK and the internal server components.

### System Architecture Diagram
```mermaid
graph TD
    subgraph "Host Machine"
        ComputerSDK[Computer SDK]
    end

    subgraph "VM/Container / Sandbox"
        FastAPI_App["FastAPI App (computer_server.main.app)"]
        UnavailableWithoutContainerMiddleware["UnavailableWithoutContainerMiddleware"]
        HandlerFactory["HandlerFactory"]
        MCPServer["MCP Server (create_mcp_server)"]
        CuaDriverBackend["Cua Driver Backend"]

        subgraph "OS-Specific Handlers"
            BaseAccessibilityHandler[BaseAccessibilityHandler]
            BaseAutomationHandler[BaseAutomationHandler]
            BaseDioramaHandler[BaseDioramaHandler]
            BaseFileHandler[BaseFileHandler]
            BaseDesktopHandler[BaseDesktopHandler]
            BaseWindowHandler[BaseWindowHandler]
        end

        Pynput_Native[Pynput (Native Input)]
        ADB_gRPC[ADB/gRPC (Android)]
        PyObjC[PyObjC (macOS)]
        PyWin32[pywin32 (Windows)]
        PythonXlib[python-xlib (Linux)]
    end

    ComputerSDK -->|"WebSocket/HTTP /ws /cmd"| FastAPI_App
    FastAPI_App --> UnavailableWithoutContainerMiddleware
    FastAPI_App --> HandlerFactory
    FastAPI_App -->|"Mounts at /mcp"| MCPServer

    HandlerFactory --> BaseAccessibilityHandler
    HandlerFactory --> BaseAutomationHandler
    HandlerFactory --> BaseDioramaHandler
    HandlerFactory --> BaseFileHandler
    HandlerFactory --> BaseDesktopHandler
    HandlerFactory --> BaseWindowHandler

    BaseAutomationHandler --> Pynput_Native
    BaseAutomationHandler --> ADB_gRPC
    BaseAutomationHandler --> PyObjC
    BaseAutomationHandler --> PyWin32
    BaseAutomationHandler --> PythonXlib

    HandlerFactory -->|"Optional Backend"| CuaDriverBackend
```

**Core components:**

1.  **FastAPI Application** (`app`): Main server instance with CORS middleware and WebSocket configuration. It supports large messages up to 10MB via `WEBSOCKET_MAX_SIZE`.
2.  **UnavailableWithoutContainerMiddleware**: ASGI middleware that rejects requests if `CONTAINER_NAME` is required but missing, returning a 503 status by default.
3.  **HandlerFactory**: A factory that detects the current `OS_TYPE` and instantiates the appropriate OS-specific handler implementations.
4.  **MCP Server**: A `FastMCP` instance created via `create_mcp_server()` and mounted at `/mcp`. It provides 40+ tools like `computer_screenshot` and `computer_type` directly to MCP clients.
5.  **Cua Driver Backend**: An optional high-performance backend (`--backend cua-driver`) that routes desktop capture and input through the native `cua-driver` runtime.

Sources: No direct citations for these components were found in the provided files, but their existence and roles are implied by the overall system architecture.

---

## API Endpoints

### WebSocket API
**Route:** `WebSocket /ws`
The primary command interface. The server handles bidirectional JSON messages for real-time control. For details, see [FastAPI and WebSocket API](#8.2).

### MCP API
**Route:** `SSE /mcp`
Provides a Model Context Protocol interface. The server includes a `FastMCP` instance that is mounted at `/mcp` if `HAS_MCP` is true. The `cua-sandbox` package can connect to this MCP server [libs/python/cua-sandbox/README.md:141-157]().

### HTTP Command API
**Route:** `POST /cmd`
A fallback HTTP endpoint that executes single commands and returns results in a JSON response. For details, see [FastAPI and WebSocket API](#8.2).

Sources: [libs/python/cua-sandbox/README.md:141-157]()

---

## Handler System

The server uses a set of abstract base classes to define the interface for OS interactions.

### Handler Abstractions
| Class | Responsibility | Base File |
|-------|----------------|-----------|
| `BaseAutomationHandler` | Mouse, Keyboard, and Screen Capture | No direct citation in provided files |
| `BaseAccessibilityHandler` | Inspecting the OS Accessibility Tree | No direct citation in provided files |
| `BaseFileHandler` | File system CRUD and directory management | No direct citation in provided files |
| `BaseDesktopHandler` | Desktop environment and wallpaper management | No direct citation in provided files |
| `BaseWindowHandler` | Window lifecycle and geometry management | No direct citation in provided files |

### OS Implementations
-   **macOS**: Uses `PyObjC` to interface with `AppKit` and `Quartz`. It includes a specific fix for cursor movement in Apple Virtualization.framework VMs (Lume/Tart) using `CGWarpMouseCursorPosition`.
-   **Windows**: Uses `pynput` for input and `pywin32` for accessibility tree enumeration via `win32gui`.
-   **Linux**: Primarily uses `pynput` and `PIL.ImageGrab` for X11/Xvfb environments.
-   **Android**: Interfaces via `adb` and a `gRPC EmulatorController` for high-performance screenshot capture.
-   **Generic**: Provides cross-platform implementations for desktop and window management using `pywinctl` and `webbrowser`.

For details, see [OS-Specific Handlers](#8.3).

Sources: No direct citations for these implementations were found in the provided files, but their existence is implied by the system architecture.

---

## Resolution Scaling

The Computer Server supports coordinate scaling to ensure AI models see consistent coordinates regardless of the physical screen resolution (e.g., Retina displays).

-   **Target Resolution**: Set via CLI flags.
-   **Scaling Logic**: Screenshots are resized to the target resolution, and incoming click coordinates are scaled from target space to actual device space.

Sources: No direct citations for resolution scaling were found in the provided files.

---

## Authentication and Security

### Security Middleware
The `UnavailableWithoutContainerMiddleware` acts as a gatekeeper. It reads `UNAVAILABLE_WITHOUT_CONTAINER_NAME` from environment variables to determine if it should block traffic in the absence of a `CONTAINER_NAME`.

### Platform Security
On Windows, the `require_unlocked_desktop` decorator is applied to automation actions to prevent execution when the Windows Secure Desktop is active (e.g., when the screen is locked), as standard automation would silently fail.

For details, see [Authentication and Security](#8.4).

Sources: No direct citations for authentication and security were found in the provided files.

---

## Child Pages

-   **[Server Architecture](#8.1)** — Computer Server internal architecture: FastAPI application, ConnectionManager, AuthenticationManager, HandlerFactory, and component relationships.
-   **[FastAPI and WebSocket API](#8.2)** — API reference for computer-server: WebSocket endpoint (/ws), HTTP endpoints (/cmd, /status, /playwright_exec), message format, and error handling.
-   **[OS-Specific Handlers](#8.3)** — OS-specific implementations: macOS handler (PyObjC), Linux handler (python-xlib), Windows handler (pywin32), Android handler (ADB/gRPC), and cross-platform automation with PyAutoGUI.
-   **[Authentication and Security](#8.4)** — Authentication flow: container_name validation, API key verification, session caching, TTL management, and security considerations.

---

