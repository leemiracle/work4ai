<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/OpenSMA · page 6 System Services · fetched 2026-10-26 -->

# System Services

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [corepdk/modules/pldm-fd/src/platforms/x86/pdk-pldm-plat.adb](corepdk/modules/pldm-fd/src/platforms/x86/pdk-pldm-plat.adb)

</details>



This document covers the core system services that provide fundamental runtime support for the OpenSMA system. These services include bootloader functionality, watchdog management, event logging, telemetry, power management, and inter-process communication.

For information about specific hardware drivers, see [Hardware Drivers](#5). For details about security protocols that run on these system services, see [Security Protocols](#3).

## System Services Architecture

System services form the foundation layer that supports all higher-level protocols and applications. They provide essential capabilities like secure boot, fault recovery, persistent storage, and inter-task communication.

### System Services Overview

```mermaid
graph TB
    subgraph "Application Layer"
        SPDM["SPDM Task"]
        PLDM["PLDM Task"]
        MCTP["MCTP Task"]
        USB["USB Task"]
    end
    
    subgraph "System Services Layer"
        BOOTLOADER["nv::bootloader::Driver<br/>Dual-Image Boot Management"]
        WATCHDOG["nv::watchdog::Boot<br/>nv::watchdog::Runtime<br/>Fault Detection & Recovery"]
        LOGGER["nv::logger::Logger<br/>nv::logger::Task<br/>Event Logging"]
        FLASH["nv::flash::Flash<br/>nv::flash::Task<br/>Storage Operations"]
        TELEMETRY["nv::telemetry::Task<br/>Data Collection"]
        IPC["nv::ipc::task::Task<br/>Inter-Core Communication"]
    end
    
    subgraph "Hardware Layer"
        FLASHHW["Flash Memory<br/>CFPA/CMPA Areas"]
        WATCHDOGHW["Code Watchdog<br/>CDOG0/CDOG1"]
        UART["UART Console"]
        MULTICORE["Multi-Core Hardware<br/>MCMGR"]
        SENSORS["Voltage/Temp Sensors"]
    end
    
    SPDM --> BOOTLOADER
    PLDM --> FLASH
    MCTP --> IPC
    USB --> LOGGER
    TELEMETRY --> SENSORS
    
    BOOTLOADER --> WATCHDOG
    BOOTLOADER --> FLASH
    LOGGER --> FLASH
    WATCHDOG --> FLASHHW
    FLASH --> FLASHHW
    LOGGER --> UART
    IPC --> MULTICORE
    
    BOOTLOADER --> WATCHDOGHW
    WATCHDOG --> WATCHDOGHW
```

**Sources:** [src/nv/bootloader.h:28-93](), [src/nv/logger/task.cpp:31-58](), [src/nv/flash/task.cpp:31-47](), [src/nv/ipc/ipc_task.cpp:28-64]()

### Service Initialization Flow

The system services follow a carefully orchestrated initialization sequence to ensure proper dependency management and fault tolerance.

```mermaid
sequenceDiagram
    participant Boot as "Bootloader"
    participant WDT as "Watchdog"
    participant Flash as "Flash Task"
    participant Logger as "Logger Task"
    participant IPC as "IPC Task"
    
    Boot->>Boot: "boot_init()"
    Boot->>WDT: "start_watchdog()"
    Boot->>Flash: "Task::make()"
    Boot->>Logger: "Task::make()"
    Boot->>IPC: "Task::make()"
    
    Flash->>Flash: "init()"
    Flash->>Boot: "set_task_booted(Flash)"
    
    Logger->>Logger: "init()"
    Logger->>Boot: "set_task_booted(Logger)"
    
    IPC->>IPC: "set_up_core_communication()"
    IPC->>Boot: "set_task_booted(IPC)"
    
    Boot->>Boot: "on_timer() - check all booted"
    Boot->>WDT: "disable()"
    Boot->>Boot: "Runtime services active"
```

**Sources:** [src/sys/mcxn556/sys/bootloader/bootloader.cpp:157-343](), [src/nv/flash/task.cpp:186-194](), [src/nv/logger/task.cpp:316-363]()

## Bootloader and Watchdog

The `nv::bootloader::Driver` class provides secure dual-image boot functionality with fault recovery capabilities. It manages image authentication via a firmware parser and handles automatic failover if a boot fails. The watchdog system provides two-tier fault detection: boot-time watchdog (`nv::watchdog::Boot`) monitors initial system startup, while runtime watchdog monitors ongoing task health.

For details, see [Bootloader and Watchdog](#6.1).

### Key Bootloader Components

| Component | Function | Implementation |
|-----------|----------|----------------|
| `current_boot_index()` | Determine active boot slot | [src/sys/mcxn556/sys/bootloader/bootloader.cpp:50-60]() |
| `boot_init()` | Initialize boot process | [src/sys/mcxn556/sys/bootloader/bootloader.cpp:157-343]() |
| `run_on_index()` | Switch to specific image | [src/sys/mcxn556/sys/bootloader/bootloader.cpp:37-48]() |
| `check_boot_reason()` | Analyze reset causes | [src/sys/mcxn556/sys/bootloader/bootloader.cpp:70-142]() |

**Sources:** [src/nv/bootloader.h:52-91](), [src/sys/mcxn556/sys/bootloader/bootloader.cpp:1-683]()

## Logging System

The logging system (`nv::logger::Logger` and `nv::logger::Task`) provides comprehensive event logging with flash persistence and UART console output capabilities. It includes specialized handling for diagnostic faults and ISR-safe logging.

For details, see [Logging System](#6.2).

### Log Storage Organization

The logging system uses a circular buffer in flash memory with metadata for tracking head/tail pointers.

```mermaid
graph LR
    subgraph "Flash Memory Layout"
        META["LogMetadata<br/>0x0000-0x1000<br/>LogPtr Entries"]
        ENTRIES["LogEntries<br/>0x1000-0xD000<br/>Circular Buffer"]
        FAULT["FaultEntries<br/>0xE000-0xF000<br/>Fatal Error Logs"]
    end
    
    subgraph "LogPtr Structure"
        HEAD["head: uint16_t<br/>Current Read Position"]
        TAIL["tail: uint16_t<br/>Next Write Position"]
        HEADCHK["head_checksum: uint16_t<br/>~head"]
        TAILCHK["tail_checksum: uint16_t<br/>~tail"]
    end
    
    META --> HEAD
    META --> TAIL
    META --> HEADCHK  
    META --> TAILCHK
    ENTRIES --> META
    FAULT --> ENTRIES
```

**Sources:** [src/nv/logger/common.h:300-320](), [src/nv/logger/log.cpp:263-302](), [src/nv/logger/common.h:30-33]()

## Telemetry and Power Management

The telemetry and power management subsystems handle the collection of sensor data and the control of system power states. This includes voltage and temperature monitoring (`nv::volt_mon`), SoC power smoothing, and GPU power controller management. The `nv::telemetry` module provides a centralized cache for this data to be queried by management protocols like PLDM.

For details, see [Telemetry and Power Management](#6.3).

### Telemetry Entity Mapping

```mermaid
graph LR
    subgraph "Code Entity Space"
        TM_TASK["nv::telemetry::Task"]
        VM_DRV["nv::volt_mon::Driver"]
        SOC_PS["nv::soc_pwr_smoothing::Manager"]
        GPU_PC["nv::gpu_pwr_controller::Controller"]
    end

    subgraph "Natural Language Space"
        SENSORS["Voltage/Temperature Sensors"]
        PWR_SMOOTH["Power Smoothing Logic"]
        GPU_PWR["GPU Power Control"]
    end

    TM_TASK -- "Collects from" --> VM_DRV
    VM_DRV -- "Monitors" --> SENSORS
    SOC_PS -- "Implements" --> PWR_SMOOTH
    GPU_PC -- "Manages" --> GPU_PWR
```

**Sources:** [src/nv/telemetry/task.cpp:45-80](), [src/nv/volt_mon/volt_mon.cpp:20-55](), [src/nv/soc_pwr_smoothing/soc_pwr_smoothing.cpp:15-40]()

## Inter-Process Communication (IPC)

The IPC system enables communication between multiple CPU cores (Core0 and Core1) using shared memory and stream buffers. It is managed by the `nv::ipc::task::Task` and utilizes hardware mailboxes (C2C) for signaling.

### IPC Code Mapping

```mermaid
graph TB
    subgraph "nv::ipc::task::Task"
        Q_PROC["process_queue()"]
        E_PROC["process_events()"]
    end

    subgraph "sys::mcxn556::sys::ipc"
        MBOX["C2C_Mailbox"]
        ISR["IPC_IRQ_Handler"]
    end

    Q_PROC -- "Uses" --> MBOX
    ISR -- "Triggers" --> E_PROC
```

**Sources:** [src/nv/ipc/ipc_task.cpp:66-110](), [src/nv/ipc/ipc_task.cpp:177-210](), [src/sys/mcxn556/sys/ipc/ipc.cpp:50-95]()

## Service Integration Summary

The system services are tightly integrated to provide comprehensive system management:

- **Bootloader-Watchdog Integration**: Boot watchdog monitors system startup and triggers image failover on boot failures.
- **Logging-Flash Integration**: Event logging uses flash services for persistent storage with circular buffer management.
- **Telemetry-Management Integration**: Telemetry data is cached and formatted for delivery via PLDM/MCTP.
- **IPC-Task Integration**: Multi-core communication enables distributed processing across CPU cores.

**Sources:** [src/sys/mcxn556/sys/bootloader/bootloader.cpp:400-535](), [src/nv/logger/task.cpp:316-504](), [src/nv/flash/task.cpp:186-293](), [src/nv/ipc/ipc_task.cpp:112-156]()

---

