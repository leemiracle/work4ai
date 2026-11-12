<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/G-Assist · page 4 Python Bindings (rise module) · fetched 2026-10-26 -->

# Python Bindings (rise module)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [api/bindings/python/README.md](api/bindings/python/README.md)
- [api/bindings/python/python_binding.vcxproj.user](api/bindings/python/python_binding.vcxproj.user)
- [api/bindings/python/rise-gui-example.png](api/bindings/python/rise-gui-example.png)
- [api/bindings/python/rise-gui.py](api/bindings/python/rise-gui.py)
- [api/bindings/python/rise/rise.py](api/bindings/python/rise/rise.py)
- [api/bindings/python/setup.py](api/bindings/python/setup.py)
- [plugins/examples/twitch/README.md](plugins/examples/twitch/README.md)

</details>



## Purpose and Scope

The `rise` Python module provides a high-level Python interface to G-Assist's RISE (Runtime Inference System Engine) backend. It abstracts the complexity of asynchronous C++ callbacks and native API calls into a simple, synchronous Python API that enables developers to integrate G-Assist capabilities into Python applications.

This page covers the `rise` module's architecture, core components, and usage patterns. For detailed API documentation of individual functions, see [API Reference](#4.1). For information on developing plugins that extend G-Assist functionality, see [Plugin Development Guide](#5).

**Sources**: [api/bindings/python/README.md:1-11](), [api/bindings/python/rise/rise.py:1-20]()

---

## Architecture Overview

The rise module implements a four-layer architecture that bridges Python applications to G-Assist's native C++ core:

```mermaid
graph TB
    subgraph "Application Layer"
        PyApp["Python Applications<br/>(Custom Scripts)"]
        InteractiveChat["Interactive Chat Script"]
        RiseGUI["rise-gui.py<br/>(Flask + Electron GUI)"]
    end
    
    subgraph "Python Bindings Layer: rise Module"
        RegisterClient["register_rise_client()<br/>Initializes connection,<br/>waits for READY signal"]
        SendCommand["send_rise_command()<br/>Sends commands,<br/>polls response_done"]
        Callback["base_function_callback()<br/>Handles async callbacks:<br/>TEXT, GRAPH, PROGRESS, READY"]
        GlobalState["Global State Variables:<br/>response, chart,<br/>response_done, ready,<br/>progress_bar"]
    end
    
    subgraph "CTypes Interop Layer"
        Structures["C Structure Definitions:<br/>NV_RISE_CALLBACK_DATA_V1<br/>NV_REQUEST_RISE_SETTINGS_V1<br/>NV_RISE_CALLBACK_SETTINGS_V1"]
        DLL["python_binding.dll<br/>Functions:<br/>register_rise_callback()<br/>request_rise()"]
    end
    
    subgraph "G-Assist Native Core"
        NVAPI["NVAPI Functions<br/>(GPU info, performance)"]
        RISEBackend["RISE Backend<br/>(Runtime Inference System)"]
    end
    
    PyApp --> RegisterClient
    PyApp --> SendCommand
    InteractiveChat --> RegisterClient
    InteractiveChat --> SendCommand
    RiseGUI --> RegisterClient
    RiseGUI --> SendCommand
    
    RegisterClient --> DLL
    SendCommand --> DLL
    DLL --> Callback
    Callback --> GlobalState
    SendCommand --> GlobalState
    
    DLL --> Structures
    DLL --> NVAPI
    DLL --> RISEBackend
    
    style RegisterClient fill:#f9f9f9
    style SendCommand fill:#f9f9f9
    style Callback fill:#f9f9f9
    style DLL fill:#e8e8e8
```

**Synchronous API via Polling**: The module converts asynchronous C++ callbacks into synchronous Python calls by using global state variables that are updated by `base_function_callback()` and polled by `send_rise_command()`. This design simplifies Python application development by eliminating the need for async/await patterns or threading concerns.

**Sources**: [api/bindings/python/rise/rise.py:1-288](), [api/bindings/python/README.md:1-11]()

---

## Module Structure

### File Organization

The rise module is organized as a Python package:

```
api/bindings/python/
├── rise/
│   ├── __init__.py
│   ├── rise.py                    # Core module implementation
│   └── python_binding.dll         # Native DLL for C++ interop
├── rise-gui.py                    # GUI application example
├── setup.py                       # Package installation config
└── requirements.txt               # Python dependencies
```

**Sources**: [api/bindings/python/setup.py:1-21](), [api/bindings/python/README.md:44-49]()

---

## Core API Functions

### Registration and Initialization

```mermaid
sequenceDiagram
    participant App as "Python Application"
    participant Module as "rise Module"
    participant DLL as "python_binding.dll"
    participant Core as "G-Assist Core"
    
    App->>Module: rise.register_rise_client()
    Module->>Module: Create NV_RISE_CALLBACK_SETTINGS_V1
    Module->>Module: Set callback = base_function_callback
    Module->>DLL: register_rise_callback(settings)
    DLL->>Core: Initialize RISE connection
    Core->>DLL: Callback: READY signal
    DLL->>Module: base_function_callback(READY)
    Module->>Module: Set ready = True
    Module-->>App: Returns (connection ready)
```

The `register_rise_client()` function initializes the connection to G-Assist's RISE backend:

1. **Callback Setup**: Creates `NV_RISE_CALLBACK_SETTINGS_V1` structure and assigns `base_function_callback` as the callback handler
2. **DLL Registration**: Calls `nvapi.register_rise_callback()` with the callback settings
3. **Ready Wait**: Polls the global `ready` flag until RISE signals readiness via a `NV_RISE_CONTENT_TYPE_READY` callback
4. **Version Encoding**: Uses bitwise OR to encode version: `ctypes.sizeof(structure) | (1 << 16)`

**Implementation**: [api/bindings/python/rise/rise.py:179-205]()

**Sources**: [api/bindings/python/rise/rise.py:179-205](), [api/bindings/python/README.md:52-67]()

---

### Command Execution

```mermaid
sequenceDiagram
    participant App as "Python Application"
    participant Module as "rise Module"
    participant DLL as "python_binding.dll"
    participant Core as "G-Assist Core"
    
    App->>Module: rise.send_rise_command("What is my GPU?")
    Module->>Module: Create command JSON:<br/>{"prompt": "...", "context_assist": {}}
    Module->>Module: Create NV_REQUEST_RISE_SETTINGS_V1
    Module->>Module: Set response_done = False
    Module->>DLL: request_rise(settings)
    DLL->>Core: Forward command
    
    Core->>DLL: Callback: TEXT content (chunk 1)
    DLL->>Module: base_function_callback(TEXT, completed=0)
    Module->>Module: Append to global response
    
    Core->>DLL: Callback: TEXT content (chunk N)
    DLL->>Module: base_function_callback(TEXT, completed=1)
    Module->>Module: Append to response<br/>Set response_done = True
    
    Module->>Module: Poll: response_done == True
    Module->>Module: Copy response, reset state
    Module-->>App: Return {"completed_response": "...", "completed_chart": "..."}
```

The `send_rise_command()` function sends commands to RISE and returns responses synchronously:

1. **Command Formatting**: Wraps the prompt in a JSON object with optional `adapter` and `system_prompt` fields
2. **Request Creation**: Populates `NV_REQUEST_RISE_SETTINGS_V1` with UTF-8 encoded JSON and content type `NV_RISE_CONTENT_TYPE_TEXT`
3. **Async Execution**: Calls `nvapi.request_rise()` which returns immediately; actual processing is asynchronous
4. **Response Polling**: Blocks in a `while not response_done` loop, sleeping 1 second between checks
5. **State Reset**: Copies accumulated `response` and `chart` data, resets global state for next command

**Implementation**: [api/bindings/python/rise/rise.py:207-261]()

**Optional Parameters**:
- `adapter`: Specifies a custom adapter for the request [api/bindings/python/rise/rise.py:231-232]()
- `system_prompt`: Sets official adapter system prompt in `context_assist` [api/bindings/python/rise/rise.py:234-235]()

**Sources**: [api/bindings/python/rise/rise.py:207-261](), [README.md:36-49]()

---

## Callback System

### Content Type Enumeration

The `NV_RISE_CONTENT_TYPE` enum defines message types exchanged between RISE and the Python module:

| Content Type | Value | Purpose |
|-------------|-------|---------|
| `NV_RISE_CONTENT_TYPE_TEXT` | 1 | Standard text responses from RISE |
| `NV_RISE_CONTENT_TYPE_GRAPH` | 2 | Chart or graph data (JSON format) |
| `NV_RISE_CONTENT_TYPE_CUSTOM_BEHAVIOR` | 3 | Custom behavior triggers |
| `NV_RISE_CONTENT_TYPE_INSTALLING` | 5 | Installation status updates |
| `NV_RISE_CONTENT_TYPE_PROGRESS_UPDATE` | 6 | Progress percentage or messages |
| `NV_RISE_CONTENT_TYPE_READY` | 7 | RISE system ready signal |
| `NV_RISE_CONTENT_TYPE_DOWNLOAD_REQUEST` | 8 | Initiates download/installation |

**Implementation**: [api/bindings/python/rise/rise.py:42-63]()

**Sources**: [api/bindings/python/rise/rise.py:42-63]()

---

### Callback Handler Flow

```mermaid
flowchart TD
    Start["base_function_callback(data_ptr)"] --> Extract["Extract data from<br/>NV_RISE_CALLBACK_DATA_V1"]
    Extract --> CheckType{"Check<br/>contentType"}
    
    CheckType -->|"READY"| Ready["Check completed flag"]
    Ready --> ReadySet["Set global ready = True<br/>Print 'RISE is ready'<br/>Close progress_bar"]
    
    CheckType -->|"TEXT"| Text["Decode content as UTF-8<br/>Append to global response"]
    Text --> TextDone{"completed == 1?"}
    TextDone -->|"Yes"| SetDone["Set response_done = True"]
    TextDone -->|"No"| End
    
    CheckType -->|"GRAPH"| Graph["Decode content as UTF-8<br/>Append to global chart"]
    Graph --> GraphDone{"completed == 1?"}
    GraphDone -->|"Yes"| SetDone
    GraphDone -->|"No"| End
    
    CheckType -->|"DOWNLOAD_REQUEST"| Download["Call intiate_rise_install()<br/>Create progress_bar with tqdm"]
    
    CheckType -->|"PROGRESS_UPDATE"| Progress["Decode content"]
    Progress --> IsDigit{"Content is digit?"}
    IsDigit -->|"Yes"| UpdateBar["Update progress_bar.n<br/>Refresh display"]
    IsDigit -->|"No"| CloseBar["Close progress_bar<br/>Print message"]
    
    SetDone --> End["Return"]
    ReadySet --> End
    Download --> End
    UpdateBar --> End
    CloseBar --> End
    End --> Done["Callback Complete"]
```

**Callback Mechanism**: The `base_function_callback()` function is invoked asynchronously by the native DLL whenever RISE sends data. It updates global state variables that are polled by synchronous functions like `send_rise_command()`.

**Implementation**: [api/bindings/python/rise/rise.py:102-154]()

**Sources**: [api/bindings/python/rise/rise.py:102-154]()

---

### Global State Management

The module maintains several global variables for inter-function communication:

| Variable | Type | Purpose | Updated By | Read By |
|----------|------|---------|------------|---------|
| `nvapi` | `ctypes.CDLL` | Handle to python_binding.dll | Module load | All API calls |
| `callback_settings` | `NV_RISE_CALLBACK_SETTINGS_V1` | Callback configuration | `register_rise_client()` | DLL |
| `response` | `str` | Accumulated text response | `base_function_callback()` | `send_rise_command()` |
| `chart` | `str` | Accumulated graph data | `base_function_callback()` | `send_rise_command()` |
| `response_done` | `bool` | Response completion flag | `base_function_callback()` | `send_rise_command()` |
| `ready` | `bool` | RISE readiness flag | `base_function_callback()` | `register_rise_client()` |
| `progress_bar` | `tqdm` or `None` | Progress visualization | `base_function_callback()` | `base_function_callback()` |

**Declarations**: [api/bindings/python/rise/rise.py:32-39]()

**Thread Safety**: The module is **not thread-safe**. The global state design assumes single-threaded, sequential command execution. Concurrent calls to `send_rise_command()` will result in race conditions.

**Sources**: [api/bindings/python/rise/rise.py:32-39]()

---

## Native Interop Layer

### CTypes Structure Definitions

The module defines C-compatible structures for communication with `python_binding.dll`:

```mermaid
classDiagram
    class NV_CLIENT_CALLBACK_SETTINGS_SUPER_V1 {
        +pCallbackParam: c_void_p
        +rsvd: uint8[64]
    }
    
    class NV_RISE_CALLBACK_DATA_V1 {
        +super: NV_CLIENT_CALLBACK_SETTINGS_SUPER_V1
        +contentType: c_int
        +content: char[4096]
        +completed: c_int
    }
    
    class NV_REQUEST_RISE_SETTINGS_V1 {
        +version: c_int
        +contentType: c_int
        +content: char[4096]
        +completed: uint8
        +reserved: uint8[32]
    }
    
    class NV_RISE_CALLBACK_SETTINGS_V1 {
        +version: c_int
        +super: NV_CLIENT_CALLBACK_SETTINGS_SUPER_V1
        +callback: NV_RISE_CALLBACK_V1
        +reserved: uint8[32]
    }
    
    NV_RISE_CALLBACK_DATA_V1 *-- NV_CLIENT_CALLBACK_SETTINGS_SUPER_V1
    NV_RISE_CALLBACK_SETTINGS_V1 *-- NV_CLIENT_CALLBACK_SETTINGS_SUPER_V1
```

**Key Structures**:

1. **`NV_RISE_CALLBACK_DATA_V1`**: Carries callback data from DLL to Python
   - `contentType`: Message type from `NV_RISE_CONTENT_TYPE` enum
   - `content`: Up to 4096 bytes of UTF-8 encoded data
   - `completed`: Flag indicating final chunk of multi-part message
   - **Implementation**: [api/bindings/python/rise/rise.py:72-77]()

2. **`NV_REQUEST_RISE_SETTINGS_V1`**: Carries command data from Python to DLL
   - `version`: Encoded structure size and version number
   - `contentType`: Request type (typically `TEXT`)
   - `content`: JSON-encoded command
   - **Implementation**: [api/bindings/python/rise/rise.py:80-86]()

3. **`NV_RISE_CALLBACK_SETTINGS_V1`**: Callback registration configuration
   - `callback`: Function pointer to `base_function_callback`
   - **Implementation**: [api/bindings/python/rise/rise.py:94-99]()

**Callback Function Type**: Defined as `NV_RISE_CALLBACK_V1 = ctypes.CFUNCTYPE(None, ctypes.POINTER(NV_RISE_CALLBACK_DATA_V1))` [api/bindings/python/rise/rise.py:90-91]()

**Sources**: [api/bindings/python/rise/rise.py:66-99]()

---

### DLL Loading and Function Signatures

```mermaid
flowchart LR
    LoadPath["Determine DLL path:<br/>SCRIPT_DIR/python_binding.dll"]
    LoadDLL["ctypes.CDLL(LIB_PATH)"]
    CheckError{"OSError?"}
    VCError["Check for VC++ Runtime error"]
    PrintHelp["Print download URL:<br/>https://aka.ms/vs/17/release/<br/>vc_redist.x64.exe"]
    Exit["sys.exit(1)"]
    Config["Configure function signatures:<br/>register_rise_callback<br/>request_rise"]
    
    LoadPath --> LoadDLL
    LoadDLL --> CheckError
    CheckError -->|"Yes"| VCError
    VCError --> PrintHelp
    PrintHelp --> Exit
    CheckError -->|"No"| Config
```

**DLL Loading**: The module locates `python_binding.dll` relative to the rise.py script location and loads it using `ctypes.CDLL` [api/bindings/python/rise/rise.py:157-169]()

**Function Signatures**:
```python
nvapi.register_rise_callback.argtypes = [ctypes.POINTER(NV_RISE_CALLBACK_SETTINGS_V1)]
nvapi.register_rise_callback.restype = ctypes.c_int

nvapi.request_rise.argtypes = [ctypes.POINTER(NV_REQUEST_RISE_SETTINGS_V1)]
nvapi.request_rise.restype = ctypes.c_int
```

Both functions return integer status codes; 0 indicates success [api/bindings/python/rise/rise.py:171-174]()

**Error Handling**: The module detects missing Visual C++ Runtime dependencies and provides user-friendly error messages with download links [api/bindings/python/rise/rise.py:161-168]()

**Sources**: [api/bindings/python/rise/rise.py:157-174](), [api/bindings/python/README.md:20-42]()

---

## Usage Patterns

### Basic Command Execution

**Minimal Example**:
```python
from rise import rise

# Initialize connection
rise.register_rise_client()

# Send command and get response
response = rise.send_rise_command("What is my GPU?")
print(response['completed_response'])
```

**Example Output**:
```
RISE is ready
Your GPU is an NVIDIA GeForce RTX 5090 with a Driver version of 572.83.
```

**Sources**: [README.md:36-49](), [api/bindings/python/README.md:52-67]()

---

### Interactive Chat Application

The repository includes an interactive chat example with visual feedback:

```mermaid
flowchart TD
    Init["rise.register_rise_client()"]
    Loop["while True"]
    GetInput["user_prompt = input()"]
    StartThread["Start thinking_bubble thread"]
    SendCmd["response = rise.send_rise_command(user_prompt)"]
    StopThread["stop_event.set()<br/>thinking_thread.join()"]
    PrintResp["print response with color"]
    
    Init --> Loop
    Loop --> GetInput
    GetInput --> StartThread
    StartThread --> SendCmd
    SendCmd --> StopThread
    StopThread --> PrintResp
    PrintResp --> Loop
```

**Key Features**:
- **Threaded Animation**: Uses `threading.Thread` to display animated "thinking dots" while waiting for response
- **Colored Output**: Uses `colorama` library for color-coded user/assistant messages
- **Event Synchronization**: Employs `threading.Event` to cleanly stop animation thread

**Implementation**: [api/bindings/python/README.md:69-107]()

**Sources**: [api/bindings/python/README.md:69-107]()

---

### Advanced: Using Adapters and System Prompts

The `send_rise_command()` function supports optional parameters for customization:

```python
response = rise.send_rise_command(
    command="Analyze this data",
    adapter="custom_adapter_name",
    system_prompt="You are a data analysis assistant."
)
```

**Parameters**:
- `adapter`: Routes the command to a specific adapter/plugin [api/bindings/python/rise/rise.py:231-232]()
- `system_prompt`: Sets the system-level prompt for the official adapter [api/bindings/python/rise/rise.py:234-235]()

**JSON Command Structure**:
```json
{
    "prompt": "Analyze this data",
    "adapter": "custom_adapter_name",
    "context_assist": {
        "officialAdapterSystemPrompt": "You are a data analysis assistant."
    }
}
```

**Sources**: [api/bindings/python/rise/rise.py:207-241]()

---

## Installation and Dependencies

### Package Installation

The rise module is distributed as a Python package using setuptools:

**Installation Command**:
```bash
cd api/bindings/python
pip install .
```

**Package Configuration**: [api/bindings/python/setup.py:1-21]()

**Package Metadata**:
- **Name**: `gassist`
- **Version**: `0.0.1`
- **Binary Inclusion**: Includes `python_binding.dll` via `package_data`
- **Dependencies**: `tqdm`, `flask`, `flask-cors`, `colorama`

**Sources**: [api/bindings/python/setup.py:1-21](), [api/bindings/python/README.md:44-49]()

---

### System Requirements

**Prerequisites**:
1. **Python**: Version 3.x [api/bindings/python/README.md:12-15]()
2. **G-Assist Core Services**: Must be installed and running on the system
3. **Visual C++ Runtime**: Required for DLL loading
   - Option 1: Visual Studio Community with "Desktop development with C++" workload
   - Option 2: Standalone VC++ Redistributable (x64) from Microsoft

**Visual C++ Runtime Error Handling**:
The module automatically detects missing runtime components and provides installation guidance [api/bindings/python/rise/rise.py:161-168]()

**Sources**: [api/bindings/python/README.md:11-42]()

---

## Application Examples

### GUI Application (rise-gui.py)

A web-based chat interface built with Flask and Electron that demonstrates rise module integration. For detailed documentation, see [GUI Application (rise-gui.py)](#4.3).

**Architecture**:
- **Backend**: Flask server with `/api/send-message` endpoint
- **Frontend**: React UI with dark theme and NVIDIA branding
- **Desktop Integration**: Optional Electron wrapper for native desktop experience

**Key Implementation**: [api/bindings/python/rise-gui.py:1-50]()

**Sources**: [api/bindings/python/rise-gui.py:1-1456](), [api/bindings/python/README.md:109-138]()

---

## Relationship to Other Components

### Integration with Plugin System

The rise module operates at a different layer than the plugin system:

```mermaid
graph TB
    subgraph "Python Applications using rise module"
        PyApp["Custom Python Apps"]
        GUI["rise-gui.py"]
    end
    
    subgraph "G-Assist Core"
        SAM["System Assist Module"]
        Launcher["Plugin Launcher"]
    end
    
    subgraph "Plugin Ecosystem"
        Spotify["Spotify Plugin"]
        Gemini["Gemini Plugin"]
        Weather["Weather Plugin"]
    end
    
    PyApp -->|"rise.send_rise_command()"| SAM
    GUI -->|"rise.send_rise_command()"| SAM
    SAM -->|"Orchestrates"| Launcher
    Launcher -->|"Windows Named Pipes"| Spotify & Gemini & Weather
```

**Complementary Roles**:
- **Rise Module**: Enables Python applications to send commands to G-Assist and receive responses
- **Plugins**: Extend G-Assist functionality by implementing specific commands (e.g., Spotify control, weather queries)

**Communication Flow**: Python apps use rise module → G-Assist Core interprets command → Plugin Launcher invokes appropriate plugin → Response flows back through rise module

**Sources**: [README.md:108-134](), [api/bindings/python/README.md:1-11]()

---

## Error Handling and Troubleshooting

### Common Issues

**DLL Loading Failures**:
```
❌ Missing Visual C++ Redistributable (x64)
Download and install it from:
https://aka.ms/vs/17/release/vc_redist.x64.exe
```
**Solution**: Install Visual C++ Runtime or Visual Studio with C++ workload [api/bindings/python/rise/rise.py:161-168]()

**Registration Failures**:
```python
ret = nvapi.register_rise_callback(ctypes.byref(callback_settings))
if ret != 0:
    print('Registration Failed')
```
**Cause**: G-Assist core services not running or incompatible version [api/bindings/python/rise/rise.py:196-198]()

**Command Send Failures**:
```python
ret = nvapi.request_rise(content)
if ret != 0:
    print(f'Send RISE command failed with {ret}')
    return None
```
**Cause**: RISE backend not ready or malformed command JSON [api/bindings/python/rise/rise.py:243-246]()

**Sources**: [api/bindings/python/rise/rise.py:161-168](), [api/bindings/python/rise/rise.py:196-198](), [api/bindings/python/rise/rise.py:243-246]()

---

## Performance Considerations

### Polling Overhead

The synchronous API implementation uses polling with 1-second intervals:

```python
while not response_done:
    time.sleep(1)
```

**Implications**:
- **Minimum Latency**: Commands take at least 1 second to complete (even if RISE responds instantly)
- **CPU Usage**: Minimal due to sleep intervals
- **Responsiveness**: Suitable for interactive applications but not real-time systems

**Location**: [api/bindings/python/rise/rise.py:248-249]()

### State Reset Pattern

After each command, global state is copied and reset:

```python
response_done = False
completed_response = response
completed_chart = chart
response = ''
chart = ''
```

**Purpose**: Prevents data leakage between sequential commands [api/bindings/python/rise/rise.py:251-255]()

**Sources**: [api/bindings/python/rise/rise.py:248-256]()

---

## Related Documentation

- **[API Reference](#4.1)**: Detailed function signatures, parameters, and return values
- **[Content Types and Callbacks](#4.2)**: Deep dive into callback mechanism and content type handling
- **[GUI Application (rise-gui.py)](#4.3)**: Complete documentation of the sample GUI application
- **[Native Bindings (python_binding.dll)](#4.4)**: Technical details of the C++ DLL interface
- **[Plugin Development Guide](#5)**: Creating custom G-Assist plugins
- **[Communication Protocol](#3.3)**: Windows Named Pipes protocol used by plugins

**Sources**: Table of Contents structure

---

