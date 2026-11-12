<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-monitor-eventing · page 2 Core Runtime Architecture · fetched 2026-10-26 -->

# Core Runtime Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [include/data_accessor.hpp](include/data_accessor.hpp)
- [include/device_status_handler.hpp](include/device_status_handler.hpp)
- [include/event_detection.hpp](include/event_detection.hpp)
- [include/meson.build](include/meson.build)
- [meson.build](meson.build)
- [meson_options.txt](meson_options.txt)
- [src/data_accessor.cpp](src/data_accessor.cpp)
- [src/event_detection.cpp](src/event_detection.cpp)
- [src/eventing_main.cpp](src/eventing_main.cpp)
- [src/meson.build](src/meson.build)
- [test/accessor_test.cpp](test/accessor_test.cpp)

</details>



## Purpose and Scope

This document covers the main runtime components of the nvidia-monitor-eventing system and how they work together to detect, process, and respond to hardware events in real-time. The core runtime architecture provides the foundation for continuous monitoring of NVIDIA hardware components through D-Bus signals, command-line interfaces, and hardware APIs.

For detailed information about event definitions and configuration, see [Configuration System](#3). For testing and validation workflows, see [Testing and Validation](#5). For the main service executable configuration, see [Main Service - monitor-eventingd](#4).

## Runtime Architecture Overview

The runtime architecture centers around the `EventDetection` class which orchestrates event detection, data access, and event processing through a multi-threaded, queue-based design.

**Core Runtime Architecture**

```mermaid
graph TB
    subgraph "Main Thread"
        MAIN[main] --> EVENTING_MAIN["eventing_main.cpp"]
        EVENTING_MAIN --> IO["boost::asio::io_context"]
        EVENTING_MAIN --> DBUS_CONN["sdbusplus::asio::connection"]
    end
    
    subgraph "Event Detection Engine"
        EVENT_DETECTION["EventDetection"]
        DBUS_HANDLER["dbusEventHandlerCallback"]
        EVENT_DISCOVERY["eventDiscovery"]
        PROPERTY_FILTER["PropertyFilterSet"]
    end
    
    subgraph "Queue & Threading"
        PC_QUEUE["PcQueueType queue"]
        WORKER_THREAD["workerThreadMainLoop"]
        THREADPOOL["ThreadpoolManager"]
        PUSH_QUEUE["pushToQueue"]
        POP_QUEUE["popFromQueue"]
    end
    
    subgraph "Data Access Layer"
        DATA_ACCESSOR["DataAccessor"]
        DBUS_ACCESSOR["DbusAccessor"]
        CMDLINE_ACCESSOR["CommandLine"]
        DEVICECORE_ACCESSOR["DeviceCoreAPI"]
    end
    
    subgraph "Event Processing"
        EVENTS_DETECTION["EventsDetection"]
        PROCESS_EVENT_LIST["processEventList"]
        EVENT_HANDLERS["EventHandlerManager"]
    end
    
    DBUS_CONN --> EVENT_DETECTION
    EVENT_DETECTION --> DBUS_HANDLER
    DBUS_HANDLER --> EVENT_DISCOVERY
    EVENT_DISCOVERY --> PUSH_QUEUE
    PUSH_QUEUE --> PC_QUEUE
    WORKER_THREAD --> POP_QUEUE
    POP_QUEUE --> PC_QUEUE
    POP_QUEUE --> EVENTS_DETECTION
    EVENTS_DETECTION --> DATA_ACCESSOR
    EVENTS_DETECTION --> PROCESS_EVENT_LIST
    PROCESS_EVENT_LIST --> THREADPOOL
    PROCESS_EVENT_LIST --> EVENT_HANDLERS
    DATA_ACCESSOR --> DBUS_ACCESSOR
    DATA_ACCESSOR --> CMDLINE_ACCESSOR
    DATA_ACCESSOR --> DEVICECORE_ACCESSOR
```

Sources: [src/eventing_main.cpp:302-314](), [src/event_detection.cpp:59-84](), [include/event_detection.hpp:105-180]()

## Key Runtime Components

### EventDetection Engine

The `EventDetection` class serves as the central orchestrator for the runtime system. It manages D-Bus signal subscriptions, processes incoming events, and coordinates with other subsystems.

**EventDetection Core Components**

```mermaid
graph LR
    subgraph "D-Bus Integration"
        START_EVENT_DETECTION["startEventDetection"]
        DBUS_HANDLER_CALLBACK["dbusEventHandlerCallback"]
        SUBSCRIBE_ACC["subscribeAcc"]
    end
    
    subgraph "Event Discovery"
        EVENT_DISCOVERY["eventDiscovery"]
        EVENT_TRIGGER_VIEW["eventTriggerView"]
        EVENT_ACCESSOR_VIEW["eventAccessorView"]
        EVENT_RECOVERY_VIEW["eventRecoveryView"]
    end
    
    subgraph "Event Processing"
        EVENTS_DETECTION_METHOD["EventsDetection"]
        IS_EVENT["IsEvent"]
        CHECK_ACCESSOR["CheckAccessor"]
    end
    
    START_EVENT_DETECTION --> SUBSCRIBE_ACC
    SUBSCRIBE_ACC --> DBUS_HANDLER_CALLBACK
    DBUS_HANDLER_CALLBACK --> EVENT_DISCOVERY
    EVENT_DISCOVERY --> EVENT_TRIGGER_VIEW
    EVENT_DISCOVERY --> EVENT_ACCESSOR_VIEW
    EVENT_DISCOVERY --> EVENT_RECOVERY_VIEW
    EVENT_DISCOVERY --> EVENTS_DETECTION_METHOD
    EVENTS_DETECTION_METHOD --> CHECK_ACCESSOR
    EVENTS_DETECTION_METHOD --> IS_EVENT
```

The `EventDetection` class implements several key methods:

- `startEventDetection()` - Initializes D-Bus subscriptions for all configured event triggers and accessors
- `dbusEventHandlerCallback()` - Processes incoming D-Bus PropertyChanged signals
- `eventDiscovery()` - Maps incoming signals to potential events using view containers
- `EventsDetection()` - Validates and processes candidate events

Sources: [include/event_detection.hpp:108-224](), [src/event_detection.cpp:158-181](), [src/event_detection.cpp:85-156]()

### DataAccessor System

The `DataAccessor` class provides a unified interface for accessing data from multiple sources including D-Bus properties, command-line tools, and hardware APIs.

| Accessor Type | Key Field | Usage |
|---------------|-----------|-------|
| `DBUS` | `object`, `interface`, `property` | D-Bus property access |
| `CMDLINE` | `executable`, `arguments` | Command execution |
| `DeviceCoreAPI` | `property` | Hardware API calls |
| `DEVICE` | `device_name` | Device name resolution |
| `CONSTANT` | `value` | Static values |

The `DataAccessor::read()` method routes to appropriate handlers:

- `readDbus()` - Reads D-Bus properties via `dbus::readDbusProperty()`
- `runCommandLine()` - Executes commands using `boost::process`
- `readDeviceCoreApi()` - Calls hardware APIs via `dbus::deviceGetCoreAPI()`

Sources: [include/data_accessor.hpp:83-421](), [src/data_accessor.cpp:85-110](), [src/data_accessor.cpp:112-217]()

## Threading and Queue Architecture

The runtime uses a producer-consumer pattern with separate threads for D-Bus signal handling and event processing.

**Threading Architecture**

```mermaid
graph TB
    subgraph "Main Thread"
        MAIN_LOOP["io->run()"]
        DBUS_SIGNALS["D-Bus PropertyChanged Signals"]
    end
    
    subgraph "Signal Processing"
        DBUS_CALLBACK["dbusEventHandlerCallback"]
        EVENT_DISCOVERY_MAIN["eventDiscovery"]
        PUSH_TO_QUEUE["pushToQueue"]
    end
    
    subgraph "Queue"
        PC_QUEUE_DETAIL["PcQueueType<br/>PROPERTIESCHANGED_QUEUE_SIZE=100"]
    end
    
    subgraph "Worker Thread"
        WORKER_MAIN_LOOP["workerThreadMainLoop"]
        WORKER_PROCESS["workerThreadProcessEvents"]
        POP_FROM_QUEUE["popFromQueue"]
        EVENTS_DETECTION_WORKER["EventsDetection"]
    end
    
    subgraph "Event Handler Threads"
        THREADPOOL_MGR["ThreadpoolManager"]
        RUN_EVENT_HANDLERS["RunEventHandlers"]
        THREAD_GUARD["ThreadpoolGuard"]
    end
    
    MAIN_LOOP --> DBUS_SIGNALS
    DBUS_SIGNALS --> DBUS_CALLBACK
    DBUS_CALLBACK --> EVENT_DISCOVERY_MAIN
    EVENT_DISCOVERY_MAIN --> PUSH_TO_QUEUE
    PUSH_TO_QUEUE --> PC_QUEUE_DETAIL
    WORKER_MAIN_LOOP --> WORKER_PROCESS
    WORKER_PROCESS --> POP_FROM_QUEUE
    POP_FROM_QUEUE --> PC_QUEUE_DETAIL
    POP_FROM_QUEUE --> EVENTS_DETECTION_WORKER
    EVENTS_DETECTION_WORKER --> RUN_EVENT_HANDLERS
    RUN_EVENT_HANDLERS --> THREADPOOL_MGR
    THREADPOOL_MGR --> THREAD_GUARD
```

The threading model ensures:

1. **Non-blocking signal processing** - D-Bus signals are quickly queued without blocking
2. **Configurable concurrency** - `ThreadpoolManager` limits concurrent event processing
3. **Resource management** - `ThreadpoolGuard` prevents thread pool exhaustion

Key configuration constants:
- `PROPERTIESCHANGED_QUEUE_SIZE` = 100 (queue capacity)
- `DEFAULT_RUNNING_THREAD_LIMIT` = 3 (concurrent event handlers)
- `DEFAULT_TOTAL_THREAD_LIMIT` = 4 (total thread pool size)

Sources: [src/event_detection.cpp:59-84](), [include/event_detection.hpp:45-47](), [src/eventing_main.cpp:302-314]()

## Event Processing Flow

The event processing pipeline transforms D-Bus signals into actionable events through a multi-stage process.

**Event Processing Pipeline**

```mermaid
flowchart TD
    subgraph "Signal Reception"
        PROPERTY_CHANGED["PropertyChanged Signal"]
        CREATE_ACCESSOR["Create DataAccessor<br/>from signal data"]
    end
    
    subgraph "Event Discovery"
        EVENT_DISCOVERY_FLOW["eventDiscovery()"]
        TRIGGER_VIEW_LOOKUP["eventTriggerView.equal_range()"]
        RECOVERY_VIEW_LOOKUP["eventRecoveryView.equal_range()"]
        UNIQUE_EVENTS["Filter duplicate events"]
    end
    
    subgraph "Event Validation"
        EVENTS_DETECTION_FLOW["EventsDetection()"]
        CHECK_RECOVERY["Check recovery conditions"]
        CHECK_TRIGGER["Check trigger conditions"]
        CHECK_ACCESSOR_FLOW["CheckAccessor.check()"]
    end
    
    subgraph "Event Execution"
        IS_EVENT_CHECK["IsEvent() - Leaky bucket logic"]
        PROCESS_EVENT_LIST_FLOW["processEventList()"]
        RUN_HANDLERS["RunEventHandlers()"]
    end
    
    PROPERTY_CHANGED --> CREATE_ACCESSOR
    CREATE_ACCESSOR --> EVENT_DISCOVERY_FLOW
    EVENT_DISCOVERY_FLOW --> TRIGGER_VIEW_LOOKUP
    EVENT_DISCOVERY_FLOW --> RECOVERY_VIEW_LOOKUP
    TRIGGER_VIEW_LOOKUP --> UNIQUE_EVENTS
    RECOVERY_VIEW_LOOKUP --> UNIQUE_EVENTS
    UNIQUE_EVENTS --> EVENTS_DETECTION_FLOW
    EVENTS_DETECTION_FLOW --> CHECK_RECOVERY
    EVENTS_DETECTION_FLOW --> CHECK_TRIGGER
    CHECK_RECOVERY --> CHECK_ACCESSOR_FLOW
    CHECK_TRIGGER --> CHECK_ACCESSOR_FLOW
    CHECK_ACCESSOR_FLOW --> IS_EVENT_CHECK
    IS_EVENT_CHECK --> PROCESS_EVENT_LIST_FLOW
    PROCESS_EVENT_LIST_FLOW --> RUN_HANDLERS
```

The pipeline implements sophisticated event filtering using view containers:

- `eventTriggerView` - Maps trigger accessors to events for real-time detection
- `eventAccessorView` - Maps main accessors to events for bootup validation
- `eventRecoveryView` - Maps recovery accessors to events for fault clearing

Sources: [src/event_detection.cpp:266-341](), [src/event_detection.cpp:408-567](), [src/event_detection.cpp:379-460]()

## Integration with OpenBMC Ecosystem

The runtime architecture integrates deeply with the OpenBMC ecosystem through standardized interfaces and protocols.

| Integration Point | Implementation | Purpose |
|-------------------|----------------|---------|
| **D-Bus System Bus** | `sdbusplus::asio::connection` | IPC with other BMC services |
| **phosphor-logging** | `MessageComposer` handler | Standard OpenBMC logging |
| **Device Health Properties** | `DeviceStatusHandler` | Hardware health reporting |
| **Redfish Events** | Message registry integration | REST API event exposure |

The main service daemon (`monitor-eventingd`) runs as a systemd service and registers the D-Bus service name `xyz.openbmc_project.nvidia_monitor_eventing` for integration with other BMC components.

Sources: [src/eventing_main.cpp:686-696](), [meson.build:89-98](), [include/device_status_handler.hpp:123-274]()

---

