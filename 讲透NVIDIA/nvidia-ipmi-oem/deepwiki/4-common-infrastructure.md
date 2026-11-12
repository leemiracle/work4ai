<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-ipmi-oem · page 4 Common Infrastructure · fetched 2026-10-26 -->

# Common Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.clang-format](.clang-format)
- [src/oemcommands.cpp](src/oemcommands.cpp)
- [src/sensorcommands.cpp](src/sensorcommands.cpp)
- [src/storagecommands.cpp](src/storagecommands.cpp)

</details>



This document covers the shared components and services that provide foundational functionality across all NVIDIA platform implementations. The common infrastructure layer abstracts core IPMI operations, storage management, and sensor handling to ensure consistent behavior regardless of the specific platform (Bluefield, Grace, etc.).

For platform-specific implementations that build upon this infrastructure, see [Platform Implementations](#3). For low-level hardware integration details, see [Hardware Integration](#5).

## Overview

The common infrastructure consists of three primary subsystems that work together to provide a unified IPMI management interface:

```mermaid
graph TB
    subgraph "Common Infrastructure Layer"
        subgraph "Core IPMI Services"
            OEM[OEM Commands<br/>oemcommands.cpp]
            Storage[Storage Commands<br/>storagecommands.cpp]
            Sensor[Sensor Commands<br/>sensorcommands.cpp]
        end
        
        subgraph "Shared Resources"
            DBusInt[D-Bus Integration]
            HWAbstraction[Hardware Abstraction]
            ConfigMgmt[Configuration Management]
        end
    end
    
    subgraph "External Dependencies"
        OpenBMC[OpenBMC D-Bus Services]
        Hardware[Physical Hardware]
        Network[Network Services]
    end
    
    OEM --> DBusInt
    Storage --> DBusInt
    Sensor --> DBusInt
    
    DBusInt --> OpenBMC
    HWAbstraction --> Hardware
    ConfigMgmt --> Network
    
    style OEM fill:#f9f9f9
    style Storage fill:#f9f9f9
    style Sensor fill:#f9f9f9
```

Sources: [src/oemcommands.cpp:1-1500](), [src/storagecommands.cpp:1-1000](), [src/sensorcommands.cpp:1-1700]()

## Core Service Architecture

The common infrastructure implements a layered service architecture where IPMI commands are processed through standardized interfaces:

```mermaid
graph LR
    subgraph "IPMI Command Processing Flow"
        Client[IPMI Client] --> Registry[ipmi::registerHandler]
        Registry --> Validation[Channel & Privilege<br/>Validation]
        Validation --> Dispatcher[Command Dispatcher]
        
        subgraph "Common Command Handlers"
            Dispatcher --> OEMHandlers[OEM Command Handlers<br/>ipmiSystemFactoryReset<br/>ipmiGetDNSConfig<br/>ipmiSetNTPConfig]
            Dispatcher --> StorageHandlers[Storage Command Handlers<br/>ipmiStorageReadFruData<br/>ipmiStorageWriteFruData<br/>ipmiStorageGetFruInvAreaInfo]
            Dispatcher --> SensorHandlers[Sensor Command Handlers<br/>ipmiSenGetSensorReading<br/>ipmiSenSetSensorThresholds<br/>ipmiSenGetSensorEventStatus]
        end
        
        subgraph "D-Bus Service Layer"
            OEMHandlers --> NetworkSvc[Network Services<br/>DNS, NTP, Hostname]
            StorageHandlers --> FRUSvc[FRU Device Service<br/>xyz.openbmc_project.FruDevice]
            SensorHandlers --> SensorSvc[Sensor Services<br/>xyz.openbmc_project.Sensor]
        end
    end
```

Sources: [src/oemcommands.cpp:201-330](), [src/storagecommands.cpp:979-997](), [src/sensorcommands.cpp:104-105]()

## Configuration Management

The common infrastructure provides centralized configuration management through D-Bus property manipulation and persistent storage:

| Configuration Area | Service | Key Properties | Implementation |
|-------------------|---------|----------------|----------------|
| Network Settings | `xyz.openbmc_project.Network` | `StaticNameServers`, `StaticNTPServers` | [src/oemcommands.cpp:428-748]() |
| System Event Logging | `xyz.openbmc_project.Logging.Settings` | `SelPolicy` | [src/oemcommands.cpp:751-841]() |
| Time Synchronization | `xyz.openbmc_project.Time.Synchronization` | `TimeSyncMethod` | [src/oemcommands.cpp:517-748]() |
| Vendor Field Mode | `xyz.openbmc_project.Software.BMC.VendorFieldModeService` | `VendorFieldModeStatus` | [src/oemcommands.cpp:843-931]() |
| Serial Redirect | `xyz.openbmc_project.Common.SerialRedirectMode` | `SerialRedirectModeStatus` | [src/oemcommands.cpp:933-1022]() |

Sources: [src/oemcommands.cpp:52-200]()

## Hardware Abstraction Layer

The common infrastructure provides standardized hardware access patterns through I2C transactions and GPIO control:

```mermaid
graph TB
    subgraph "Hardware Abstraction"
        I2CLayer[I2C Transaction Layer<br/>i2cTransaction]
        GPIOLayer[GPIO Control Layer<br/>CheckGWPfru]
        ServiceLayer[Service Integration Layer<br/>D-Bus Method Calls]
    end
    
    subgraph "Hardware Components"
        PSU[PSU Devices<br/>6x Power Supplies]
        Sensors[Temperature Sensors<br/>Multiple Zones]
        FRU[FRU Devices<br/>Field Replaceable Units]
        WriteProtect[Write Protection<br/>GPIO Controls]
    end
    
    subgraph "Access Methods"
        DirectI2C[Direct I2C Access<br/>Bus + Slave Address]
        ServiceAccess[Service-Based Access<br/>D-Bus Interfaces]
        GPIOAccess[GPIO-Based Control<br/>sysfs Interface]
    end
    
    I2CLayer --> DirectI2C
    ServiceLayer --> ServiceAccess
    GPIOLayer --> GPIOAccess
    
    DirectI2C --> PSU
    ServiceAccess --> Sensors
    ServiceAccess --> FRU
    GPIOAccess --> WriteProtect
```

Sources: [src/oemcommands.cpp:340-384](), [src/storagecommands.cpp:289-566]()

## Data Structure Management

The common infrastructure maintains several key data structures for efficient operation:

### FRU Management Data Structures

```mermaid
graph LR
    subgraph "FRU Device Management"
        DeviceHashes[deviceHashes<br/>flat_map&lt;uint8_t, pair&lt;uint16_t, uint8_t&gt;&gt;]
        FruCache[fruCache<br/>vector&lt;uint8_t&gt;]
        FruCacheTemp[fruCacheTemp<br/>vector&lt;uint8_t&gt;]
        ManagedFrus[frus<br/>ManagedObjectType]
    end
    
    subgraph "Cache Operations"
        DeviceHashes --> HashLookup[Device ID → Bus/Address]
        FruCache --> ReadOps[FRU Read Operations]
        FruCacheTemp --> WriteOps[FRU Write Operations]
        ManagedFrus --> Discovery[Device Discovery]
    end
    
    subgraph "Persistence"
        WriteOps --> TimerBased[Timer-Based Writes<br/>writeTimer]
        TimerBased --> PhysicalWrite[Physical FRU Update]
    end
```

Sources: [src/storagecommands.cpp:95-217]()

### Sensor Data Repository

```mermaid
graph TB
    subgraph "Sensor Data Management"
        SensorTree[sensorTree<br/>SensorSubTree]
        SensorDataRecords[sensorDataRecords<br/>SDRObjectType]
        SensorCache[SensorCache<br/>flat_map&lt;string, ManagedObjectType&gt;]
    end
    
    subgraph "SDR Generation Process"
        SensorTree --> RecordGen[SDR Record Generation<br/>getSensorDataRecords]
        RecordGen --> FullRecord[SensorDataFullRecord<br/>Type 01 Records]
        RecordGen --> FruRecord[SensorDataFruRecord<br/>Type 11 Records]
        RecordGen --> Type12[Type12Record<br/>Management Controller Records]
    end
    
    subgraph "Record Storage"
        FullRecord --> SensorDataRecords
        FruRecord --> SensorDataRecords
        Type12 --> SensorDataRecords
    end
```

Sources: [src/sensorcommands.cpp:63-84](), [src/sensorcommands.cpp:1136-1432]()

## Service Registration

The common infrastructure uses constructor-based registration to ensure all IPMI command handlers are properly registered during module initialization:

| Registration Function | Purpose | Command Handlers |
|----------------------|---------|------------------|
| `registerNvOemFunctions()` | OEM command registration | Factory reset, DNS/NTP config, SEL policy, vendor modes |
| `registerStorageFunctions()` | Storage command registration | FRU read/write, inventory info |
| `registerSensorFunctions()` | Sensor command registration | Sensor readings, thresholds, event status |

Sources: [src/oemcommands.cpp:201](), [src/storagecommands.cpp:113](), [src/sensorcommands.cpp:104]()

---

