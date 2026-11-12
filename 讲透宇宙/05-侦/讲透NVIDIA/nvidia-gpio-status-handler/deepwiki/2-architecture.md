<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-gpio-status-handler · page 2 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.clang-format](.clang-format)
- [gpio_json_config.cpp](gpio_json_config.cpp)
- [gpio_json_config.hpp](gpio_json_config.hpp)
- [gpio_status_handler.cpp](gpio_status_handler.cpp)
- [meson.build](meson.build)
- [meson_options.txt](meson_options.txt)

</details>



This document describes the technical design and internal structure of the `nvidia-gpio-status-handler` daemon. It provides an overview of the system's layered architecture, component interactions, and execution model. For detailed information about individual components, see [System Components](#2.1). For D-Bus interface specifications, see [D-Bus Service](#2.2). For threading and monitoring implementation, see [GPIO Monitoring Implementation](#2.3).

## Architectural Overview

The `nvidia-gpio-status-handler` is designed as a single-process, multi-threaded daemon that bridges Linux GPIO hardware with the OpenBMC D-Bus ecosystem. The architecture follows a layered model with clear separation between configuration, hardware abstraction, monitoring logic, and external interfaces.

```mermaid
graph TB
    subgraph "External Interfaces Layer"
        JSON["JSON Configuration File<br/>(validated by GpioJsonConfig)"]
        DBUS_IF["D-Bus Interface<br/>xyz.openbmc_project.GpioStatus"]
        HW["Linux GPIO Hardware<br/>/dev/gpiochipN"]
    end
    
    subgraph "Application Layer"
        MAIN["main() Entry Point<br/>gpio_status_handler.cpp"]
    end
    
    subgraph "Core Components"
        CONFIG["GpioJsonConfig<br/>Configuration Parser"]
        CHIPS["GpioChips<br/>Chip Management"]
        LINES["GpioLines<br/>Line Request/Management"]
        MONITOR["syncAlertGpioPin()<br/>Per-Pin Monitoring Threads"]
        DBUSOBJ["createDbusObject()<br/>D-Bus Interface Setup"]
    end
    
    subgraph "Dependency Layer"
        LIBGPIOD["libgpiod<br/>gpiod_line_* functions"]
        SDBUSPLUS["sdbusplus<br/>asio::dbus_interface"]
        PLOG["phosphor-logging<br/>structured logging"]
    end
    
    JSON --> CONFIG
    CONFIG --> MAIN
    MAIN --> CHIPS
    MAIN --> LINES
    MAIN --> DBUSOBJ
    MAIN --> MONITOR
    
    CHIPS --> LIBGPIOD
    LINES --> LIBGPIOD
    MONITOR --> LIBGPIOD
    DBUSOBJ --> SDBUSPLUS
    MONITOR --> SDBUSPLUS
    
    LIBGPIOD --> HW
    SDBUSPLUS --> DBUS_IF
    
    CONFIG --> PLOG
    CHIPS --> PLOG
    LINES --> PLOG
    MONITOR --> PLOG
    
    style MAIN fill:#e8e8e8
    style CONFIG fill:#e8e8e8
    style CHIPS fill:#e8e8e8
    style LINES fill:#e8e8e8
    style MONITOR fill:#e8e8e8
    style DBUSOBJ fill:#e8e8e8
```

**Layered Architecture:**

| Layer | Components | Purpose |
|-------|-----------|---------|
| **External Interfaces** | JSON config, D-Bus service, GPIO hardware | System boundaries - input configuration, output status, hardware access |
| **Application** | `main()` function | Orchestration, initialization, error handling |
| **Core Components** | `GpioJsonConfig`, `GpioChips`, `GpioLines`, monitoring threads | Business logic, GPIO abstraction, state synchronization |
| **Dependencies** | `libgpiod`, `sdbusplus`, `phosphor-logging` | External library abstractions |

**Sources:** [gpio_status_handler.cpp:506-582](), [meson.build:94-105]()

## Component Initialization Flow

The daemon follows a strict initialization sequence to ensure all resources are properly configured before monitoring begins.

```mermaid
sequenceDiagram
    participant MAIN as "main()"
    participant CONFIG as "GpioJsonConfig"
    participant DBUS as "createDbusObject()"
    participant CHIPS as "GpioChips"
    participant LINES as "GpioLines"
    participant THREADS as "startThreads()"
    participant IO as "io.run()<br/>(D-Bus event loop)"
    
    MAIN->>CONFIG: GpioJsonConfig(fileName)
    CONFIG->>CONFIG: Parse and validate JSON schema
    CONFIG-->>MAIN: Validated configuration
    
    MAIN->>DBUS: createDbusObject(io, gpioConfig)
    DBUS->>DBUS: Register D-Bus service name<br/>xyz.openbmc_project.GpioStatusHandler
    DBUS->>DBUS: Create interface with properties<br/>for each GPIO pin
    DBUS-->>MAIN: dbus_interface shared_ptr
    
    MAIN->>CHIPS: GpioChips(gpioConfig)
    CHIPS->>CHIPS: Open /dev/gpiochipN devices<br/>referenced in config
    CHIPS-->>MAIN: Chip handles
    
    MAIN->>LINES: GpioLines(gpioChips, gpioConfig)
    LINES->>LINES: Request GPIO lines<br/>gpiod_chip_get_line()
    LINES-->>MAIN: Line handles map
    
    MAIN->>THREADS: startThreads(threads, dbusInterface, lineMap, config)
    THREADS->>THREADS: Spawn thread per GPIO<br/>syncAlertGpioPin()
    THREADS-->>MAIN: Thread vector
    
    MAIN->>IO: io.run()
    Note over IO: D-Bus server blocks here<br/>Threads run in parallel
    
    IO-->>MAIN: Service stopped
    MAIN->>THREADS: finishThreads(threads)
    THREADS->>THREADS: Join all threads
```

**Initialization Steps:**

1. **Configuration Loading** ([gpio_status_handler.cpp:514]()): `GpioJsonConfig` parses JSON and validates schema
2. **D-Bus Setup** ([gpio_status_handler.cpp:516-517]()): `createDbusObject()` registers service and creates properties
3. **Chip Opening** ([gpio_status_handler.cpp:519]()): `GpioChips` opens `/dev/gpiochipN` devices
4. **Line Requesting** ([gpio_status_handler.cpp:521]()): `GpioLines` requests individual GPIO lines
5. **Thread Spawning** ([gpio_status_handler.cpp:524-525]()): `startThreads()` creates monitoring threads
6. **Event Loop** ([gpio_status_handler.cpp:534]()): `io.run()` blocks on D-Bus event loop

**Sources:** [gpio_status_handler.cpp:506-552](), [gpio_status_handler.cpp:354-379](), [gpio_status_handler.cpp:289-342]()

## Execution Model

The daemon operates with a single-threaded D-Bus event loop and multiple GPIO monitoring threads. Each GPIO pin gets a dedicated thread that polls for state changes and updates the corresponding D-Bus property.

```mermaid
graph TB
    subgraph "Main Thread"
        MAIN_INIT["Initialization<br/>main()"]
        DBUS_LOOP["D-Bus Event Loop<br/>io.run()"]
        MAIN_CLEANUP["Cleanup<br/>finishThreads()"]
        
        MAIN_INIT --> DBUS_LOOP
        DBUS_LOOP --> MAIN_CLEANUP
    end
    
    subgraph "GPIO Monitoring Threads"
        T1["Thread 1<br/>syncAlertGpioPin()<br/>GPIO Pin A"]
        T2["Thread 2<br/>syncAlertGpioPin()<br/>GPIO Pin B"]
        TN["Thread N<br/>syncAlertGpioPin()<br/>GPIO Pin N"]
    end
    
    subgraph "Shared Resources"
        DBUS_IFACE["D-Bus Interface<br/>(thread-safe via mutex)"]
        GLOBAL_FLAG["runThreads<br/>(volatile bool)"]
    end
    
    MAIN_INIT -.->|"spawn"| T1
    MAIN_INIT -.->|"spawn"| T2
    MAIN_INIT -.->|"spawn"| TN
    
    T1 -->|"setDBusProperty()<br/>(mutex locked)"| DBUS_IFACE
    T2 -->|"setDBusProperty()<br/>(mutex locked)"| DBUS_IFACE
    TN -->|"setDBusProperty()<br/>(mutex locked)"| DBUS_IFACE
    
    DBUS_IFACE -->|"PropertiesChanged signal"| DBUS_LOOP
    
    T1 -.->|"check"| GLOBAL_FLAG
    T2 -.->|"check"| GLOBAL_FLAG
    TN -.->|"check"| GLOBAL_FLAG
    
    MAIN_CLEANUP -.->|"set false"| GLOBAL_FLAG
    MAIN_CLEANUP -.->|"join()"| T1
    MAIN_CLEANUP -.->|"join()"| T2
    MAIN_CLEANUP -.->|"join()"| TN
```

**Thread Safety:**

- **Shared D-Bus Interface**: Protected by `setDBusPropMutex` ([gpio_status_handler.cpp:39](), [gpio_status_handler.cpp:59]())
- **Global Run Flag**: Volatile `runThreads` variable for coordinated shutdown ([gpio_status_handler.cpp:38]())
- **Exception Handling**: Thread exceptions stored in `lastThreadException` ([gpio_status_handler.cpp:40](), [gpio_status_handler.cpp:80]())

**Sources:** [gpio_status_handler.cpp:37-41](), [gpio_status_handler.cpp:53-93](), [gpio_status_handler.cpp:264-277]()

## GPIO Monitoring Loop

Each monitoring thread runs the `syncAlertGpioPin()` function, which implements a hybrid polling and event-driven model. The loop waits for GPIO events with a timeout, then reads the pin state and updates the D-Bus property.

```mermaid
stateDiagram-v2
    [*] --> Initialize
    Initialize: "Calculate readPeriodTicks<br/>from read_period_sec"
    
    Initialize --> WaitEvent
    
    WaitEvent: "gpiod_line_event_wait(line, timeout)<br/>timeout = 100ms (lineEventWaitTimeoutNs)"
    
    WaitEvent --> CheckResult: "waitResult"
    
    state CheckResult <<choice>>
    CheckResult --> EventDetected: "waitResult > 0"
    CheckResult --> Timeout: "waitResult == 0"
    CheckResult --> Error: "waitResult < 0"
    
    EventDetected --> ReadValue: "Event occurred"
    Timeout --> CheckTicks: "Check period elapsed"
    
    state CheckTicks <<choice>>
    CheckTicks --> ReadValue: "ticks == 0<br/>(period complete)"
    CheckTicks --> IncrementTicks: "ticks > 0"
    
    IncrementTicks --> WaitEvent: "ticks = (ticks + 1) % readPeriodTicks"
    
    ReadValue: "lineGetResult = getGpioValue(line, pinName)<br/>OR EINJ mode file read"
    
    ReadValue --> UpdateDbus
    UpdateDbus: "setDBusProperty(dbusInterface, pinName, value)<br/>Mutex-protected operation"
    
    UpdateDbus --> CheckGlobal
    
    state CheckGlobal <<choice>>
    CheckGlobal --> WaitEvent: "runThreads && no errors"
    CheckGlobal --> StopService: "!runThreads || error"
    
    Error --> StopService
    StopService --> [*]
```

**Key Variables:**

- `lineEventWaitTimeoutNs` = 100ms: Maximum wait time per iteration ([gpio_status_handler.cpp:35]())
- `readPeriodTicks`: Number of timeout periods per full polling cycle ([gpio_status_handler.cpp:311-313]())
- `ticks`: Counter tracking progress through polling period ([gpio_status_handler.cpp:189](), [gpio_status_handler.cpp:247]())

**Sources:** [gpio_status_handler.cpp:177-255](), [gpio_status_handler.cpp:95-115]()

## Configuration Schema Validation

The `GpioJsonConfig` class ([gpio_json_config.hpp:33]()) enforces strict validation on the JSON configuration file. All configuration errors are detected at startup before any hardware access occurs.

```mermaid
flowchart TD
    START["GpioJsonConfig(fileName)"]
    
    START --> OPEN["Open file<br/>std::ifstream"]
    OPEN --> PARSE["Parse JSON<br/>nlohmann::json"]
    
    PARSE --> VALIDATE_ROOT["isJsonConfigFormatGood()<br/>Check root is object"]
    VALIDATE_ROOT --> VALIDATE_EMPTY["isJsonObjectNonEmpty()<br/>Check at least one pin"]
    
    VALIDATE_EMPTY --> LOOP_START{"For each pin entry"}
    
    LOOP_START --> VALIDATE_NAME["isGpioNameGood()<br/>Alphanumeric + underscore"]
    VALIDATE_NAME --> VALIDATE_OBJ["isPinDescriptionGood()<br/>Check pin config"]
    
    VALIDATE_OBJ --> CHECK_CHIP["configKeyGpioChip:<br/>unsigned int"]
    VALIDATE_OBJ --> CHECK_PIN["configKeyGpioPin:<br/>unsigned int"]
    VALIDATE_OBJ --> CHECK_INIT["configKeyInitialPinVal:<br/>boolean"]
    VALIDATE_OBJ --> CHECK_PERIOD["configKeyReadPeriod:<br/>positive number"]
    
    CHECK_CHIP --> NEXT_PIN
    CHECK_PIN --> NEXT_PIN
    CHECK_INIT --> NEXT_PIN
    CHECK_PERIOD --> NEXT_PIN
    
    NEXT_PIN --> LOOP_START
    LOOP_START --> SUCCESS["Store config<br/>Return object"]
    
    VALIDATE_ROOT -->|"Invalid"| THROW["throw GpioConfigError"]
    VALIDATE_EMPTY -->|"Invalid"| THROW
    VALIDATE_NAME -->|"Invalid"| THROW
    VALIDATE_OBJ -->|"Invalid"| THROW
    
    THROW --> END[["Constructor fails"]]
    SUCCESS --> END
```

**Validation Rules:**

| Field | Type | Constraints | Constant |
|-------|------|-------------|----------|
| Pin name (key) | `string` | Non-empty, alphanumeric + `_` | - |
| `gpio_chip` | `unsigned int` | Valid chip number | `configKeyGpioChip` ([gpio_json_config.cpp:22]()) |
| `gpio_pin` | `unsigned int` | Valid pin offset | `configKeyGpioPin` ([gpio_json_config.cpp:23]()) |
| `initial` | `boolean` | Initial D-Bus property value | `configKeyInitialPinVal` ([gpio_json_config.cpp:24]()) |
| `read_period_sec` | `number` | Positive value (seconds) | `configKeyReadPeriod` ([gpio_json_config.cpp:25]()) |

**Sources:** [gpio_json_config.cpp:201-212](), [gpio_json_config.cpp:152-163](), [gpio_json_config.cpp:165-189](), [gpio_json_config.hpp:8-72]()

## D-Bus Service Registration

The daemon registers a single D-Bus service with one interface containing boolean properties for each configured GPIO pin. All properties are read-only from the client perspective.

```mermaid
graph LR
    subgraph "D-Bus System Bus"
        SERVICE["Service Name:<br/>xyz.openbmc_project.GpioStatusHandler"]
    end
    
    subgraph "Object Hierarchy"
        OBJ["Object Path:<br/>/xyz/openbmc_project/GpioStatusHandler"]
    end
    
    subgraph "Interface"
        IFACE["Interface:<br/>xyz.openbmc_project.GpioStatus"]
        
        PROP1["Property: PIN_NAME_1<br/>Type: boolean<br/>Access: read-only"]
        PROP2["Property: PIN_NAME_2<br/>Type: boolean<br/>Access: read-only"]
        PROPN["Property: PIN_NAME_N<br/>Type: boolean<br/>Access: read-only"]
    end
    
    SERVICE --> OBJ
    OBJ --> IFACE
    IFACE --> PROP1
    IFACE --> PROP2
    IFACE --> PROPN
```

**Constants:**

- `dbusServiceName`: `"xyz.openbmc_project.GpioStatusHandler"` ([gpio_status_handler.cpp:26]())
- `dbusObjectPath`: `"/xyz/openbmc_project/GpioStatusHandler"` ([gpio_status_handler.cpp:25]())
- `dbusInterfaceName`: `"xyz.openbmc_project.GpioStatus"` ([gpio_status_handler.cpp:27]())

Properties are created dynamically from the configuration via `register_property()` ([gpio_status_handler.cpp:373-375]()) with initial values from the `configKeyInitialPinVal` field.

**Sources:** [gpio_status_handler.cpp:25-27](), [gpio_status_handler.cpp:354-379]()

## Build Configuration Impact

The build system provides compile-time options that significantly affect the architecture's behavior. These options enable different deployment modes without code changes.

| Option | Effect on Architecture | Macro Defined |
|--------|------------------------|---------------|
| `debug_log=0-4` | Sets default log verbosity | `DEF_DBG_LEVEL` ([meson.build:34]()) |
| `sandbox_mode=enabled` | Enables x86-64 development builds | `SANDBOX_MODE` ([meson.build:39]()) |
| `log_elapsed_time=enabled` | Adds performance instrumentation | `LOG_ELAPSED_TIME` ([meson.build:43]()) |

**Conditional Compilation:**

- `ENABLE_GSH_LOGS`: Activated when `debug_log > 0`, controls logging calls ([gpio_status_handler.cpp:45-47]())
- `SANDBOX_MODE`: Allows host system development without BMC hardware
- EINJ mode: Always available, activated by creating `/tmp/devices/gpio/` files ([gpio_status_handler.cpp:103-111]())

**Sources:** [meson.build:31-44](), [meson_options.txt:1-21]()

## Dependency Graph

The executable depends on several external libraries, each serving a specific architectural role.

```mermaid
graph TB
    EXE["gpio-status-handlerd<br/>Executable"]
    
    SRC1["gpio_status_handler.cpp"]
    SRC2["gpio_chips.cpp"]
    SRC3["gpio_lines.cpp"]
    SRC4["gpio_json_config.cpp"]
    SRC5["gpio_utils.cpp"]
    
    DEP1["sdbusplus<br/>D-Bus async I/O<br/>(dependency: 'sdbusplus')"]
    DEP2["libgpiod<br/>GPIO character device API<br/>(dependency: 'libgpiod')"]
    DEP3["phosphor-logging<br/>Structured logging<br/>(dependency: 'phosphor-logging')"]
    DEP4["threads<br/>POSIX threads<br/>(dependency: 'threads')"]
    
    SRC1 --> EXE
    SRC2 --> EXE
    SRC3 --> EXE
    SRC4 --> EXE
    SRC5 --> EXE
    
    DEP1 --> EXE
    DEP2 --> EXE
    DEP3 --> EXE
    DEP4 --> EXE
    
    DEP1 -.->|"fallback: subproject"| SUB1["sdbusplus subproject"]
    DEP3 -.->|"fallback: subproject"| SUB2["phosphor-logging subproject"]
```

**Dependency Resolution:**

All dependencies support Meson subproject fallback ([meson.build:64-87]()), allowing the build system to fetch and build them locally if not found on the system.

**Sources:** [meson.build:62-105]()

---

