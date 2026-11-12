<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-installer · page 4 User Interface System · fetched 2026-10-26 -->

# User Interface System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Makefile](Makefile)
- [ncurses-ui.c](ncurses-ui.c)
- [nvidia-installer-ui.h](nvidia-installer-ui.h)
- [stream-ui.c](stream-ui.c)
- [user-interface.c](user-interface.c)
- [user-interface.h](user-interface.h)

</details>



## Purpose and Scope

The User Interface System provides a unified abstraction layer for displaying information and collecting user input during NVIDIA driver installation. The system supports multiple UI implementations including a built-in console interface and dynamically-loaded ncurses-based graphical text interfaces, allowing the installer to adapt to different terminal environments while maintaining a consistent API for the installation engine.

For information about the overall installation workflow that drives this UI system, see [Installation Process](#3). For build system details on how UI libraries are embedded and generated, see [Build System](#5).

## Architecture Overview

The UI system implements a dispatch table pattern that allows runtime selection between different user interface implementations while providing a uniform API to the installation engine.

### UI Dispatch Table Architecture

```mermaid
graph TB
    subgraph "Installation Engine"
        InstallCore["install-from-cwd.c<br/>Installation Logic"]
    end
    
    subgraph "UI Abstraction Layer"
        UICore["user-interface.c<br/>ui_init(), ui_message(), etc."]
        GlobalUI["__ui<br/>Global InstallerUI pointer"]
    end
    
    subgraph "UI Implementations"
        StreamDispatch["stream_ui_dispatch_table<br/>Built-in fallback UI"]
        NcursesDispatch["ui_dispatch_table<br/>ncurses-ui.so"]
        Ncurses6Dispatch["ui_dispatch_table<br/>ncurses6-ui.so"]
        NcursesW6Dispatch["ui_dispatch_table<br/>ncursesw6-ui.so"]
    end
    
    subgraph "UI Implementation Functions"
        StreamFuncs["stream_detect()<br/>stream_init()<br/>stream_message()"]
        NcursesFuncs["nv_ncurses_detect()<br/>nv_ncurses_init()<br/>nv_ncurses_message()"]
    end
    
    InstallCore --> UICore
    UICore --> GlobalUI
    GlobalUI --> StreamDispatch
    GlobalUI --> NcursesDispatch
    GlobalUI --> Ncurses6Dispatch
    GlobalUI --> NcursesW6Dispatch
    
    StreamDispatch --> StreamFuncs
    NcursesDispatch --> NcursesFuncs
    Ncurses6Dispatch --> NcursesFuncs
    NcursesW6Dispatch --> NcursesFuncs
```

**Sources:** [user-interface.c:39-65](), [nvidia-installer-ui.h:39-176](), [stream-ui.c:59-75](), [ncurses-ui.c:245-261]()

The `InstallerUI` structure defines the complete interface that each UI implementation must provide:

| Function Pointer | Purpose | Example Usage |
|------------------|---------|---------------|
| `detect()` | Check if UI can be used | Terminal size validation |
| `init()` | Initialize UI resources | Setup ncurses, colors |
| `message()` | Display messages | Error/warning dialogs |
| `get_input()` | Collect user input | Configuration prompts |
| `yes_no()` | Binary choice prompts | Confirmation dialogs |
| `status_begin/update/end()` | Progress indication | Installation progress |
| `approve_command_list()` | Expert mode approval | Show planned operations |

**Sources:** [nvidia-installer-ui.h:39-176]()

## UI Implementation Selection

The system attempts to load UI implementations in priority order, falling back to simpler interfaces if advanced ones fail to initialize.

### UI Selection Flow

```mermaid
flowchart TD
    Start["ui_init() called"] --> UserSpecified{"User specified --ui option?"}
    
    UserSpecified -->|Yes| FindSpecified["Find specified UI in ui_list[]"]
    UserSpecified -->|No| StartFirst["Start with first UI in list"]
    
    FindSpecified --> ExtractUI["extract_user_interface()"]
    StartFirst --> ExtractUI
    
    ExtractUI --> ExtractSuccess{"Extraction successful?"}
    ExtractSuccess -->|No| NextUI["Try next UI in list"]
    ExtractSuccess -->|Yes| DLOpen["dlopen() the .so file"]
    
    DLOpen --> DLOpenSuccess{"dlopen() successful?"}
    DLOpenSuccess -->|No| NextUI
    DLOpenSuccess -->|Yes| GetSymbol["dlsym() ui_dispatch_table"]
    
    GetSymbol --> DetectUI["Call ui->detect()"]
    DetectUI --> DetectSuccess{"detect() returns TRUE?"}
    DetectSuccess -->|No| NextUI
    DetectSuccess -->|Yes| InitUI["Call ui->init()"]
    
    InitUI --> StreamFallback["Use stream_ui_dispatch_table"]
    NextUI --> MoreUIs{"More UIs to try?"}
    MoreUIs -->|Yes| ExtractUI
    MoreUIs -->|No| StreamFallback
    
    StreamFallback --> SetupSignals["Setup signal handlers"]
    SetupSignals --> ProcessDeferred["Process deferred messages"]
    ProcessDeferred --> Success["UI initialization complete"]
```

**Sources:** [user-interface.c:116-238]()

The UI selection process follows this priority order defined in `ui_list[]`:

1. **ncurses6** - Modern ncurses v6 implementation
2. **ncurses** - Standard ncurses implementation  
3. **ncursesw6** - Wide character ncurses v6 implementation
4. **stream** - Built-in console fallback (always available)

**Sources:** [user-interface.c:120-140]()

## UI Library Embedding System

Advanced UI implementations are embedded as binary data within the main installer executable to ensure single-file distribution without external dependencies.

### Embedded Library Architecture

```mermaid
graph LR
    subgraph "Build Process"
        NcursesSO["ncurses-ui.so<br/>Shared library"]
        BinaryData["Binary data arrays<br/>_binary_*_start/_end"]
        HeaderGen["Header generation<br/>.so.h files"]
    end
    
    subgraph "Runtime Extraction"
        TempFile["Temporary file<br/>mkstemp()"]
        MMapWrite["mmap() + memcpy()"]
        DLOpen["dlopen() extracted file"]
    end
    
    subgraph "UI Attributes"
        UIAttr["user_interface_attribute_t<br/>name, data_array, size"]
    end
    
    NcursesSO --> BinaryData
    BinaryData --> HeaderGen
    HeaderGen --> UIAttr
    UIAttr --> TempFile
    TempFile --> MMapWrite
    MMapWrite --> DLOpen
```

**Sources:** [user-interface.c:67-75](), [user-interface.c:683-754](), [Makefile:229-233]()

The extraction process in `extract_user_interface()`:

1. **Create temporary file** using `mkstemp()` in `op->tmpdir`
2. **Set file size** with `lseek()` and single byte write
3. **Memory map file** using `mmap()` with `PROT_READ | PROT_WRITE`
4. **Copy binary data** with `memcpy()` from embedded array
5. **Unmap and close** file, ready for `dlopen()`

**Sources:** [user-interface.c:683-754]()

## Message Handling System

The UI system includes a sophisticated message deferral mechanism to handle messages that arrive before UI initialization is complete.

### Message Deferral Flow

```mermaid
flowchart TD
    MessageCall["ui_message() called"] --> UIReady{"__ui != NULL?"}
    
    UIReady -->|Yes| DirectDisplay["do_print_message()"]
    UIReady -->|No| DeferMessage["defer_message()"]
    
    DeferMessage --> StoreMessage["Store in op->ui_deferred_messages[]"]
    StoreMessage --> PrintStderr["Print to stdout/stderr immediately"]
    
    DirectDisplay --> LogMessage["log_printf()"]
    
    subgraph "UI Initialization"
        UIInit["ui_init() completes"] --> ProcessDeferred["Process deferred messages"]
        ProcessDeferred --> ReplayMessages["Replay messages to UI"]
        ReplayMessages --> FreeDeferred["Free deferred message storage"]
    end
    
    PrintStderr --> UIInit
    LogMessage --> Continue["Continue execution"]
    FreeDeferred --> Continue
```

**Sources:** [user-interface.c:290-318](), [user-interface.c:216-233]()

The message level hierarchy determines how messages are displayed:

| Level | Constant | Stream Output | UI Behavior |
|-------|----------|---------------|-------------|
| Log | `NV_MSG_LEVEL_LOG` | None during status | Background logging only |
| Message | `NV_MSG_LEVEL_MESSAGE` | stdout | Standard info display |
| Warning | `NV_MSG_LEVEL_WARNING` | stderr | Warning indicators |
| Error | `NV_MSG_LEVEL_ERROR` | stderr | Error dialog/emphasis |

**Sources:** [nvidia-installer-ui.h:29-32](), [user-interface.c:290-318]()

## Stream UI Implementation

The stream UI provides a robust console-based interface that serves as the system's fallback implementation and is always compiled into the main binary.

### Stream UI Components

```mermaid
graph TB
    subgraph "Stream UI Functions"
        StreamDetect["stream_detect()<br/>Always returns TRUE"]
        StreamInit["stream_init()<br/>Welcome message + SIGWINCH"]
        StreamMessage["stream_message()<br/>stdout/stderr output"]
        StreamInput["stream_get_input()<br/>readline from stdin"]
        StreamYN["stream_yes_no()<br/>Y/N prompts"]
        StreamChoice["stream_multiple_choice()<br/>Numbered options"]
        StreamStatus["stream_status_*()<br/>ASCII progress bars"]
    end
    
    subgraph "Progress Bar System"
        StatusData["Data struct<br/>percent tracking"]
        ProgressBar["print_status_bar()<br/>30-char ASCII bar"]
        Indeterminate["Sliding hash pattern"]
    end
    
    StreamStatus --> StatusData
    StatusData --> ProgressBar
    ProgressBar --> Indeterminate
```

**Sources:** [stream-ui.c:39-75](), [stream-ui.c:95-147]()

### Stream UI Progress Bar Implementation

The stream UI renders progress using a 30-character ASCII bar with percentage display:

```
Installing kernel modules: 

  [##########                    ]  33%
```

The progress bar implementation in `print_status_bar()`:
- **Normal progress**: `#` characters fill left-to-right based on percentage
- **Indeterminate mode**: Single `#` character slides across the bar
- **Status management**: Carriage return (`\r`) for updates, newline on completion

**Sources:** [stream-ui.c:95-147]()

## NCurses UI Implementation

The ncurses UI provides a sophisticated terminal-based interface with windows, colors, and interactive elements.

### NCurses UI Architecture

```mermaid
graph TB
    subgraph "NCurses Data Structures"
        DataStruct["DataStruct<br/>UI state management"]
        RegionStruct["RegionStruct<br/>Window-like regions"]
        PagerStruct["PagerStruct<br/>Scrollable text display"]
    end
    
    subgraph "Screen Layout"
        Header["Header region<br/>Title display"]
        Message["Message region<br/>Dynamic content"]
        Footer["Footer region<br/>Status/branding"]
    end
    
    subgraph "Interactive Elements"
        Buttons["Button drawing<br/>nv_ncurses_draw_button()"]
        Input["Text input<br/>nv_ncurses_get_input()"]
        Pager["Text pager<br/>Less-like navigation"]
        Progress["Progress bars<br/>Visual progress display"]
    end
    
    DataStruct --> RegionStruct
    RegionStruct --> Header
    RegionStruct --> Message
    RegionStruct --> Footer
    
    Message --> Buttons
    Message --> Input
    Message --> Pager
    Message --> Progress
```

**Sources:** [ncurses-ui.c:74-96](), [ncurses-ui.c:44-50](), [ncurses-ui.c:59-65]()

### NCurses Color and Display System

The ncurses UI supports both color and monochrome terminals with fallback display modes:

| Element | Color Mode | No-Color Mode |
|---------|------------|---------------|
| Header | Green on Black | Reverse video |
| Footer | Reverse video | Reverse video |
| Messages | White on Blue | Normal |
| Buttons | White on Red | Reverse (if highlighted) |
| Input | Green on Black | Reverse video |

**Sources:** [ncurses-ui.c:108-125](), [ncurses-ui.c:333-338]()

The ncurses initialization sequence:
1. **Terminal detection** - Check minimum size requirements (40x10)
2. **Color initialization** - Setup color pairs if supported
3. **Screen setup** - Clear, disable echo, enable cbreak mode
4. **Region creation** - Initialize header, footer regions
5. **Signal handling** - Setup resize handlers

**Sources:** [ncurses-ui.c:281-374]()

## Status and Progress System

Both UI implementations provide progress indication through a common interface supporting determinate and indeterminate progress modes.

### Progress System Flow

```mermaid
sequenceDiagram
    participant Engine as "Installation Engine"
    participant UI as "UI Abstraction"
    participant Impl as "UI Implementation"
    
    Engine->>UI: ui_status_begin(title, msg)
    UI->>Impl: status_begin(title, msg)
    Impl->>Impl: Setup progress display
    
    loop Progress Updates
        Engine->>UI: ui_status_update(percent, msg)
        UI->>Impl: status_update(percent, msg)
        Impl->>Impl: Update progress bar
    end
    
    opt Indeterminate Operation
        Engine->>UI: ui_indeterminate_begin(msg)
        UI->>UI: Start worker thread
        loop Worker Thread
            UI->>Impl: update_indeterminate(msg)
            Impl->>Impl: Animate indeterminate display
        end
        Engine->>UI: ui_indeterminate_end()
        UI->>UI: Stop worker thread
    end
    
    Engine->>UI: ui_status_end(msg)
    UI->>Impl: status_end(msg)
    Impl->>Impl: Complete progress display
```

**Sources:** [user-interface.c:538-642](), [user-interface.c:575-626]()

### Indeterminate Progress Implementation

The indeterminate progress system uses a separate worker thread to animate progress indicators when completion time is unknown:

```c
// Indeterminate worker thread function
static void *indeterminate_worker(void *p) {
    while (indeterminate_get(id) == INDETERMINATE_ACTIVE) {
        __ui->update_indeterminate(op, msg);
    }
    return NULL;
}
```

**Sources:** [user-interface.c:580-593]()

## Signal Handling and Cleanup

The UI system includes comprehensive signal handling to ensure clean shutdown and proper terminal restoration.

### UI Signal Management

```mermaid
graph TB
    subgraph "Signal Setup"
        SignalReg["signal() registration<br/>SIGHUP, SIGINT, SIGTERM, etc."]
        Handler["ui_signal_handler()"]
    end
    
    subgraph "Cleanup Process"
        UIClose["ui_close(NULL)"]
        TermRestore["Terminal restoration"]
        ErrorMsg["Write error to stderr"]
        Exit["exit(128 + signal)"]
    end
    
    SignalReg --> Handler
    Handler --> UIClose
    UIClose --> TermRestore
    TermRestore --> ErrorMsg
    ErrorMsg --> Exit
```

**Sources:** [user-interface.c:205-215](), [user-interface.c:763-821]()

The signal handler performs cleanup without relying on potentially corrupted state:
- **UI cleanup** - Call `ui_close(NULL)` to restore terminal
- **Safe output** - Use `write(2, ...)` instead of `fprintf()` for reentrancy
- **Signal identification** - Map signal numbers to names for error reporting
- **Exit code** - Use standard `128 + signal_number` exit convention

**Sources:** [user-interface.c:763-821]()

## Build System Integration

The UI system integrates closely with the build system to support multiple ncurses variants and embed UI libraries as binary data.

### UI Library Build Process

```mermaid
graph TB
    subgraph "Source Files"
        NcursesC["ncurses-ui.c"]
        ConfigH["config.h<br/>Feature detection"]
    end
    
    subgraph "Variant Builds"
        NcursesSO["ncurses-ui.so<br/>Standard ncurses"]
        Ncurses6SO["ncurses6-ui.so<br/>ncurses v6"]
        NcursesW6SO["ncursesw6-ui.so<br/>Wide char v6"]
    end
    
    subgraph "Binary Embedding"
        ReadOnlyObj["read-only object files<br/>Binary data arrays"]
        HeaderGen["Binary data headers<br/>.so.h files"]
    end
    
    subgraph "Main Binary"
        UserInterfaceO["user-interface.o<br/>Depends on UI headers"]
        NvidiaInstaller["nvidia-installer<br/>Final executable"]
    end
    
    NcursesC --> NcursesSO
    NcursesC --> Ncurses6SO
    NcursesC --> NcursesW6SO
    ConfigH --> NcursesSO
    ConfigH --> Ncurses6SO
    ConfigH --> NcursesW6SO
    
    NcursesSO --> ReadOnlyObj
    Ncurses6SO --> ReadOnlyObj
    NcursesW6SO --> ReadOnlyObj
    
    ReadOnlyObj --> HeaderGen
    HeaderGen --> UserInterfaceO
    UserInterfaceO --> NvidiaInstaller
```

**Sources:** [Makefile:61-77](), [Makefile:201-211](), [Makefile:229-233]()

The build system handles UI library variants through feature detection:
- **Feature flags** - `BUILD_NCURSES6`, `BUILD_NCURSESW6` control which variants are built
- **Compiler flags** - `NV_INSTALLER_NCURSES6`, `NV_INSTALLER_NCURSESW6` enable conditional compilation
- **Dependency tracking** - `user-interface.o` depends on generated UI headers
- **Binary embedding** - UI shared libraries converted to object files with binary data

**Sources:** [Makefile:45-46](), [Makefile:117-118](), [Makefile:69-73]()

---

