<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-tal · page 5 Data Flow · fetched 2026-10-26 -->

# Data Flow

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [lib/include/tal.hpp](lib/include/tal.hpp)
- [lib/tal.cpp](lib/tal.cpp)

</details>



This document details the end-to-end telemetry data flow through the NVIDIA Telemetry Abstraction Layer (TAL) system, tracing how data moves from producers to clients. The document covers initialization processes, data production and consumption patterns, and module-specific data handling mechanisms.

## 1. Data Flow Overview

The TAL system provides a unified interface for telemetry data collection and access by abstracting underlying telemetry mechanisms. Data flows through the system in the following sequence:

```mermaid
flowchart TD
    subgraph "Telemetry Production"
        Producer["Telemetry Producer"]
        Producer -->|"1. Call namespaceInit()"| TAInit["TelemetryAggregator::namespaceInit()"]
        Producer -->|"2. Call updateTelemetry()"| TAUpdate["TelemetryAggregator::updateTelemetry()"]
    end
    
    subgraph "TAL Core"
        TAInit -->|"3. Register modules"| Modules["Telemetry Modules"]
        TAUpdate -->|"4. Forward updates"| Modules
    end
    
    subgraph "Storage Layer"
        Modules -->|"5. Store data"| SharedMem["Shared Memory"]
        Modules -->|"5. Store data"| SMBus["SMBus Hardware"]
    end
    
    subgraph "Telemetry Consumption"
        Client["Telemetry Client"]
        Client -->|"6. Call namespaceInit()"| TAInitClient["TelemetryAggregator::namespaceInit()"]
        Client -->|"7. Call getAllMrds()"| TAGet["TelemetryAggregator::getAllMrds()"]
        TAGet -->|"8. Request data"| Modules
        Modules -->|"9. Retrieve data"| SharedMem
        Modules -->|"10. Return SensorValues"| TAGet
        TAGet -->|"11. Return SensorValues"| Client
    end
```

Sources: [lib/tal.cpp:60-78](), [lib/tal.cpp:80-97](), [lib/tal.cpp:116-136]()

## 2. Initialization Flow

Before any telemetry data can flow through the system, the TAL framework must be initialized. This initialization differs between producers and clients.

### 2.1. System Initialization Process

```mermaid
sequenceDiagram
    participant App as "Application (Producer/Client)"
    participant TA as "TelemetryAggregator"
    participant Modules as "Telemetry Modules"
    
    App->>TA: namespaceInit(ProcessType, processName)
    
    alt "TAL not initialized"
        TA->>TA: initTal()
        loop "For each module in talModulesArray"
            TA->>Modules: Create module (SharedMemModule, SmBusModule)
        end
        TA->>TA: talInit = true
        
        alt "ProcessType.Producer"
            loop "For each module"
                TA->>Modules: namespaceInit(processName)
            end
        end
    else "TAL already initialized"
        TA-->>App: return false (error)
    end
    
    TA-->>App: return status
```

The initialization process involves:

1. An application (producer or client) calls `TelemetryAggregator::namespaceInit()`
2. If TAL is not initialized, `initTal()` creates and registers all available telemetry modules
3. For producer processes, each module's `namespaceInit()` is called with the producer's process name
4. For client processes, only the basic TAL initialization is performed

Sources: [lib/tal.cpp:36-58](), [lib/tal.cpp:116-136]()

## 3. Telemetry Data Production

After initialization, telemetry producers can send data through TAL using the `updateTelemetry()` function.

### 3.1. Data Production Process

```mermaid
sequenceDiagram
    participant Producer as "Telemetry Producer"
    participant TA as "TelemetryAggregator"
    participant SM as "SharedMemModule"
    participant SMBM as "SmBusModule"
    
    Producer->>TA: updateTelemetry(devicePath, interface, propName, rawData, timestamp, rc, value, associatedEntityPath)
    
    alt "TAL initialized"
        loop "For each registered module"
            TA->>SM: updateTelemetry(...)
            TA->>SMBM: updateTelemetry(...)
        end
    else "TAL not initialized"
        TA-->>Producer: Error: "namespaceInit for tal is not invoked"
    end
```

The data production process includes:

1. A producer calls `TelemetryAggregator::updateTelemetry()` with telemetry data parameters
2. The aggregator verifies TAL is initialized
3. The aggregator forwards the update to all registered telemetry modules
4. Each module processes the data according to its implementation

Sources: [lib/tal.cpp:60-78](), [lib/include/tal.hpp:94-100]()

## 4. Telemetry Data Consumption

Telemetry clients retrieve data from the TAL system using two primary methods:

```mermaid
sequenceDiagram
    participant Client as "Telemetry Client"
    participant TA as "TelemetryAggregator"
    participant SM as "SharedMemModule"
    
    Note over Client, SM: Getting specific MRD namespace data
    Client->>TA: getAllMrds(mrdNamespace)
    
    alt "TAL initialized"
        TA->>SM: getAllMrds(mrdNamespace)
        SM-->>TA: Return vector<SensorValue>
        TA-->>Client: Return vector<SensorValue>
    else "TAL not initialized"
        TA-->>Client: Error: "namespaceInit for tal is not invoked"
    end
    
    Note over Client, SM: Discovering available namespaces
    Client->>TA: getMrdNamespaces()
    
    alt "TAL initialized"
        TA->>SM: getMrdNamespaces()
        SM-->>TA: Return vector<string>
        TA-->>Client: Return vector<string>
    else "TAL not initialized"
        TA-->>Client: Error: "namespaceInit for tal is not invoked"
    end
```

Important aspects of data consumption:

1. Currently, only data from the `SharedMemModule` is accessible to clients
2. `getAllMrds(mrdNamespace)` retrieves all sensor values for a specific namespace
3. `getMrdNamespaces()` returns all available MRD namespaces
4. Both methods require TAL to be initialized first

Sources: [lib/tal.cpp:80-97](), [lib/tal.cpp:99-114](), [lib/include/tal.hpp:111-121]()

## 5. Module-Specific Data Flow

### 5.1. Shared Memory Module Data Flow

The `SharedMemModule` handles telemetry data through shared memory, allowing efficient inter-process communication:

```mermaid
graph TD
    subgraph "Producer Side"
        Producer["Telemetry Producer"] -->|"updateTelemetry()"| TA["TelemetryAggregator"]
        TA -->|"updateTelemetry()"| SMM["SharedMemModule"]
        SMM -->|"Uses"| AS["AggregationService"]
        AS -->|"Writes data"| SHM["Shared Memory Region"]
    end
    
    subgraph "Client Side"
        Client["Telemetry Client"] -->|"getAllMrds()"| TAClient["TelemetryAggregator"]
        TAClient -->|"getAllMrds()"| SMMClient["SharedMemModule"]
        SMMClient -->|"Uses"| ASClient["AggregationService"]
        ASClient -->|"Reads data"| SHM
        ASClient -->|"Return data"| SMMClient
        SMMClient -->|"Return SensorValues"| TAClient
        TAClient -->|"Return SensorValues"| Client
    end
```

Sources: [lib/tal_shmem.hpp](), [lib/tal.cpp:80-97]()

### 5.2. SMBus Module Data Flow

The `SmBusModule` handles telemetry data through the System Management Bus:

```mermaid
graph TD
    Producer["Telemetry Producer"] -->|"updateTelemetry()"| TA["TelemetryAggregator"]
    TA -->|"updateTelemetry()"| SMBM["SmBusModule"]
    SMBM -->|"Uses"| SMTA["SMBus Telemetry API"]
    SMTA -->|"Formats data"| SMTU["SMBus Telemetry Update"]
    SMTU -->|"Writes to hardware registers"| SMBH["SMBus Hardware"]
    
    subgraph "Configuration"
        CSV["CSV Configuration Files"]
    end
    
    SMTU -->|"References"| CSV
```

Currently, the SMBus module is only used for data production, not consumption, which is why the `getAllMrds()` and `getMrdNamespaces()` methods only query the `SharedMemModule`.

Sources: [lib/tal_smbus.hpp](), [lib/tal.cpp:60-78]()

## 6. End-to-End Data Flow

The following diagram illustrates the complete end-to-end data flow through the TAL system:

```mermaid
sequenceDiagram
    participant Producer as "Telemetry Producer"
    participant Client as "Telemetry Client"
    participant TA as "TelemetryAggregator"
    participant SM as "SharedMemModule"
    participant SHM as "Shared Memory"
    participant SMBM as "SmBusModule"
    participant SMBT as "SMBus Telemetry"
    
    Note over Producer, SMBT: Initialization Phase
    Producer->>TA: namespaceInit(ProcessType.Producer, processName)
    TA->>TA: initTal()
    TA->>SM: Create SharedMemModule
    TA->>SMBM: Create SmBusModule
    TA->>SM: namespaceInit(processName)
    TA->>SMBM: namespaceInit(processName)
    
    Note over Producer, SMBT: Data Production Phase
    Producer->>TA: updateTelemetry(devicePath, interface, propName, rawData, timestamp, rc, value, associatedEntityPath)
    TA->>SM: updateTelemetry(...)
    SM->>SHM: Write data to shared memory
    TA->>SMBM: updateTelemetry(...)
    SMBM->>SMBT: Update SMBus telemetry
    
    Note over Producer, SMBT: Client Initialization
    Client->>TA: namespaceInit(ProcessType.Client, processName)
    
    Note over Producer, SMBT: Data Consumption Phase
    Client->>TA: getAllMrds(namespace)
    TA->>SM: getAllMrds(namespace)
    SM->>SHM: Read data from shared memory
    SHM-->>SM: Return data
    SM-->>TA: Return vector<SensorValue>
    TA-->>Client: Return vector<SensorValue>
    
    Client->>TA: getMrdNamespaces()
    TA->>SM: getMrdNamespaces()
    SM-->>TA: Return vector<string>
    TA-->>Client: Return vector<string>
```

Sources: [lib/tal.cpp:36-136](), [lib/include/tal.hpp:59-122]()

## 7. Code Structure Supporting Data Flow

The following class diagram illustrates how the data flow is implemented in the TAL code structure:

```mermaid
classDiagram
    class TelemetryHandler {
        <<interface>>
        +updateTelemetry(devicePath, interface, propName, rawData, timestamp, rc, value, associatedEntityPath) int
        +getAllMrds(mrdNamespace) vector~SensorValue~
        +getMrdNamespaces() vector~string~
        +namespaceInit(processName) bool
    }
    
    class TelemetryAggregator {
        +static namespaceInit(ProcessType, processName) bool
        +static updateTelemetry(devicePath, interface, propName, rawData, timestamp, rc, value, associatedEntityPath) void
        +static getAllMrds(mrdNamespace) vector~SensorValue~
        +static getMrdNamespaces() vector~string~
    }
    
    class SharedMemModule {
        +updateTelemetry(...) int
        +getAllMrds(mrdNamespace) vector~SensorValue~
        +getMrdNamespaces() vector~string~
        +namespaceInit(processName) bool
    }
    
    class SmBusModule {
        +updateTelemetry(...) int
        +getAllMrds(mrdNamespace) vector~SensorValue~
        +getMrdNamespaces() vector~string~
        +namespaceInit(processName) bool
    }
    
    TelemetryHandler <|-- SharedMemModule : implements
    TelemetryHandler <|-- SmBusModule : implements
    TelemetryAggregator --> TelemetryHandler : uses
```

Sources: [lib/include/tal.hpp:59-122](), [lib/tal_module.hpp]()

## 8. Key Data Flow Parameters

The following table summarizes the key parameters used in telemetry data flow:

| Parameter | Description | Used In |
|-----------|-------------|---------|
| `devicePath` | Path of the telemetry device/sensor | `updateTelemetry()` |
| `interface` | Phosphor D-Bus interface of telemetry object | `updateTelemetry()` |
| `propName` | Metric property name | `updateTelemetry()` |
| `rawData` | Raw binary data of the value | `updateTelemetry()` |
| `timestamp` | Timestamp when the value was collected | `updateTelemetry()` |
| `rc` | Return code (non-zero for NaN update) | `updateTelemetry()` |
| `value` | Metric value (DbusVariantType) | `updateTelemetry()` |
| `associatedEntityPath` | Optional entity path for metrics | `updateTelemetry()` |
| `mrdNamespace` | Namespace for retrieving MRDs | `getAllMrds()` |
| `processName` | Name of the process initializing TAL | `namespaceInit()` |

Sources: [lib/include/tal.hpp:77-121](), [README.md:42-100]()

---

