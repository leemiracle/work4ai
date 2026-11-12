<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-ipmi-oem · page 8 Utility Components · fetched 2026-10-26 -->

# Utility Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [include/biosversionutils.hpp](include/biosversionutils.hpp)
- [include/sdrutils.hpp](include/sdrutils.hpp)

</details>



This page documents the supporting utility components that provide essential data management, sensor integration, and version tracking capabilities for the NVIDIA IPMI OEM commands library. These utilities serve as the foundational layer for sensor data record (SDR) management and BIOS version tracking across all platform implementations.

For information about platform-specific command implementations, see [Platform Implementations](#3). For details about sensor command processing, see [Sensor Management](#4.2).

## SDR Utilities

The SDR utilities provide a comprehensive framework for managing sensor data records, sensor numbering, and integration with the OpenBMC sensor infrastructure. These utilities bridge the gap between D-Bus sensor services and IPMI sensor access patterns.

### Sensor Data Management Architecture

```mermaid
graph TB
    subgraph "IPMI Sensor Access"
        SensorNum["Sensor Number<br/>(uint16_t)"]
        SensorPath["D-Bus Path<br/>(/xyz/openbmc_project/sensors/*)"]
        SensorType["Sensor Type<br/>(IPMI Type Codes)"]
    end
    
    subgraph "SDR Utility Components"
        SensorSubTree["SensorSubTree<br/>boost::flat_map"]
        SensorNumMap["SensorNumMap<br/>boost::bimap"]
        TypeMapping["Type Mapping<br/>sensorTypes"]
    end
    
    subgraph "D-Bus Integration"
        ObjectMapper["ObjectMapper<br/>xyz.openbmc_project.ObjectMapper"]
        EntityManager["EntityManager<br/>xyz.openbmc_project.EntityManager"]
        SensorServices["Sensor Services<br/>Value, Threshold interfaces"]
    end
    
    subgraph "Utility Functions"
        getSensorSubtree["getSensorSubtree()"]
        getSensorNumMap["getSensorNumMap()"]
        getSensorTypeFromPath["getSensorTypeFromPath()"]
        getSensorNumberFromPath["getSensorNumberFromPath()"]
        getPathFromSensorNumber["getPathFromSensorNumber()"]
        updateIpmiFromAssociation["updateIpmiFromAssociation()"]
    end
    
    ObjectMapper --> getSensorSubtree
    getSensorSubtree --> SensorSubTree
    SensorSubTree --> getSensorNumMap
    getSensorNumMap --> SensorNumMap
    
    SensorPath --> getSensorTypeFromPath
    getSensorTypeFromPath --> TypeMapping
    TypeMapping --> SensorType
    
    SensorPath --> getSensorNumberFromPath
    getSensorNumberFromPath --> SensorNumMap
    SensorNumMap --> SensorNum
    
    SensorNum --> getPathFromSensorNumber
    getPathFromSensorNumber --> SensorNumMap
    
    EntityManager --> updateIpmiFromAssociation
    updateIpmiFromAssociation --> SensorServices
```

Sources: [include/sdrutils.hpp:61-184](), [include/sdrutils.hpp:322-547]()

### Sensor Number Allocation Strategy

The system implements a sophisticated sensor numbering scheme that maps IPMI sensor numbers to D-Bus sensor paths using LUN-based allocation:

| LUN | Range | Purpose |
|-----|-------|---------|
| 0 | 0x00-0xFE | Primary sensors (255 max) |
| 1 | 0x100-0x1FE | Extended sensors (255 max) |
| 2 | - | Reserved (skipped) |
| 3 | 0x300-0x3FE | Additional sensors (255 max) |

```mermaid
graph LR
    subgraph "Sensor Numbering Constants"
        maxSensorsPerLUN["maxSensorsPerLUN<br/>255"]
        maxIPMISensors["maxIPMISensors<br/>765 total"]
        lun1Sensor0["lun1Sensor0<br/>0x100"]
        lun3Sensor0["lun3Sensor0<br/>0x300"]
        invalidSensorNumber["invalidSensorNumber<br/>0xFFFF"]
    end
    
    subgraph "Allocation Logic"
        StartLUN0["LUN 0: 0x00"]
        CheckLUN0["Index < 255?"]
        MoveLUN1["LUN 1: 0x100"]
        CheckLUN1["Index < 510?"]
        MoveLUN3["LUN 3: 0x300"]
        CheckLUN3["Index < 765?"]
        ThrowError["throw out_of_range"]
    end
    
    StartLUN0 --> CheckLUN0
    CheckLUN0 -->|Yes| StartLUN0
    CheckLUN0 -->|No| MoveLUN1
    MoveLUN1 --> CheckLUN1
    CheckLUN1 -->|Yes| MoveLUN1
    CheckLUN1 -->|No| MoveLUN3
    MoveLUN3 --> CheckLUN3
    CheckLUN3 -->|Yes| MoveLUN3
    CheckLUN3 -->|No| ThrowError
```

Sources: [include/sdrutils.hpp:68-73](), [include/sdrutils.hpp:158-180]()

### Sensor Type Classification

The utilities provide mapping between D-Bus sensor types and IPMI sensor type codes:

```mermaid
graph TD
    subgraph "D-Bus Sensor Types"
        DBusTemperature["temperature"]
        DBusVoltage["voltage"]
        DBusCurrent["current"]
        DBusFanTach["fan_tach"]
        DBusFanPwm["fan_pwm"]
        DBusPower["power"]
    end
    
    subgraph "SensorTypeCodes Enum"
        IPMITemperature["SensorTypeCodes::temperature<br/>0x1"]
        IPMIVoltage["SensorTypeCodes::voltage<br/>0x2"]
        IPMICurrent["SensorTypeCodes::current<br/>0x3"]
        IPMIFan["SensorTypeCodes::fan<br/>0x4"]
        IPMIOther["SensorTypeCodes::other<br/>0xB"]
        IPMISystemFW["SensorTypeCodes::system_firmware_progress<br/>0xF"]
    end
    
    subgraph "Special Cases"
        BiosPath["SYS_FW_BIOS_PATH<br/>/xyz/openbmc_project/sensors/system_firmware_progress/BIOS"]
        BiosSensorNum["BIOS_SENSOR_NUM<br/>0x06"]
    end
    
    DBusTemperature --> IPMITemperature
    DBusVoltage --> IPMIVoltage
    DBusCurrent --> IPMICurrent
    DBusFanTach --> IPMIFan
    DBusFanPwm --> IPMIFan
    DBusPower --> IPMIOther
    BiosPath --> IPMISystemFW
    BiosPath --> BiosSensorNum
```

Sources: [include/sdrutils.hpp:208-230](), [include/sdrutils.hpp:251-266](), [include/sdrutils.hpp:219-222]()

## BIOS Version Management Utilities

The BIOS version management utilities provide persistent storage and tracking of BIOS slot information, supporting dual-slot BIOS configurations common in enterprise systems.

### BIOS Version Information Architecture

```mermaid
graph TB
    subgraph "BiosVersionInformation Singleton"
        SlotInfo["slotInfo<br/>array<BiosSlotInformation, 2>"]
        LastBootSlot["lastBootSlot<br/>uint8_t"]
        ConfigFlags["configFlags<br/>array<bool, 2>"]
    end
    
    subgraph "BiosSlotInformation Structure"
        MajorVersion["majorVersion<br/>uint8_t"]
        MinorVersion["minorVersion<br/>uint8_t"]
        UpdateDate["date<br/>ISO 8601 string"]
    end
    
    subgraph "Persistent Storage"
        JsonFile["storageFilePath<br/>/var/ipmi-bios-info.json"]
        LoadFunction["loadInfoFromFile()"]
        SaveFunction["saveInfoToFile()"]
    end
    
    subgraph "Core Operations"
        UpdateSlot["updateBiosSlot()"]
        GetSlotInfo["getBiosSlotInformation()"]
        GetLastBoot["getLastBootSlot()"]
        ConfigFlagOps["getConfigFlag() / setConfigFlag()"]
    end
    
    SlotInfo --> MajorVersion
    SlotInfo --> MinorVersion
    SlotInfo --> UpdateDate
    
    SlotInfo --> JsonFile
    LastBootSlot --> JsonFile
    ConfigFlags --> JsonFile
    
    JsonFile --> LoadFunction
    JsonFile --> SaveFunction
    
    LoadFunction --> SlotInfo
    SaveFunction --> SlotInfo
    
    UpdateSlot --> SaveFunction
    ConfigFlagOps --> SaveFunction
```

Sources: [include/biosversionutils.hpp:46-171]()

### BIOS Slot Update Workflow

The system tracks BIOS version changes and boot slot usage with automatic persistence:

```mermaid
sequenceDiagram
    participant Client as "IPMI Client"
    participant BVI as "BiosVersionInformation"
    participant Storage as "JSON Storage"
    participant TimeLib as "boost::posix_time"
    
    Client->>BVI: updateBiosSlot(slot, major, minor)
    BVI->>BVI: Check slot < nSlots (2)
    
    alt Slot changed
        BVI->>BVI: lastBootSlot = slot
        Note over BVI: save = true
    end
    
    alt Version changed
        BVI->>BVI: slotInfo[slot].majorVersion = major
        BVI->>BVI: slotInfo[slot].minorVersion = minor
        BVI->>TimeLib: Get current UTC time
        TimeLib-->>BVI: ISO 8601 timestamp
        BVI->>BVI: slotInfo[slot].date = timestamp
        Note over BVI: save = true
    end
    
    alt save == true
        BVI->>Storage: saveInfoToFile()
        Storage-->>BVI: JSON written to /var/ipmi-bios-info.json
    end
    
    BVI-->>Client: Update complete
```

Sources: [include/biosversionutils.hpp:105-131](), [include/biosversionutils.hpp:74-83]()

## Entity Manager Integration

The SDR utilities provide sophisticated integration with OpenBMC's Entity Manager for sensor configuration and IPMI entity association:

```mermaid
graph TD
    subgraph "Association Discovery"
        SensorPath["Sensor D-Bus Path"]
        AssociationDefs["Association.Definitions<br/>interface"]
        AssociationRecords["Associations property<br/>vector<tuple<forward,reverse,endpoint>>"]
    end
    
    subgraph "Entity Manager Lookup"
        ChassisEndpoint["Chassis Endpoint<br/>(forward=chassis, reverse=all_sensors)"]
        EntityManagerProps["EntityManager Properties<br/>xyz.openbmc_project.EntityManager"]
        IPMIDecorator["Inventory.Decorator.Ipmi<br/>interface"]
    end
    
    subgraph "Configuration Interface Detection"
        ConfigurationInterfaces["Configuration Interfaces"]
        FanConfigs["AspeedFan / I2CFan / NuvotonFan"]
        GenericConfig["xyz.openbmc_project.Configuration.*"]
    end
    
    subgraph "IPMI Entity Information"
        EntityId["EntityId<br/>uint8_t"]
        EntityInstance["EntityInstance<br/>uint8_t"]
    end
    
    SensorPath --> AssociationDefs
    AssociationDefs --> AssociationRecords
    AssociationRecords --> ChassisEndpoint
    ChassisEndpoint --> EntityManagerProps
    EntityManagerProps --> IPMIDecorator
    IPMIDecorator --> EntityId
    IPMIDecorator --> EntityInstance
    
    ChassisEndpoint --> ConfigurationInterfaces
    ConfigurationInterfaces --> FanConfigs
    ConfigurationInterfaces --> GenericConfig
    FanConfigs --> EntityId
    GenericConfig --> EntityId
```

Sources: [include/sdrutils.hpp:417-545](), [include/sdrutils.hpp:380-413](), [include/sdrutils.hpp:353-378]()

## Data Structure Relationships

The utility components use several key data structures that provide efficient access patterns for sensor management:

| Data Structure | Type | Purpose | Key Features |
|----------------|------|---------|--------------|
| `SensorSubTree` | `boost::container::flat_map` | Sensor hierarchy mapping | Version-aware string comparison |
| `SensorNumMap` | `boost::bimap<int, std::string>` | Bidirectional sensor number mapping | O(log n) lookups both directions |
| `BiosSlotInformation` | Struct with JSON serialization | BIOS version tracking | nlohmann::json integration |
| `BiosVersionInformation` | Singleton pattern | Persistent BIOS state | Automatic file I/O |

Sources: [include/sdrutils.hpp:53-66](), [include/biosversionutils.hpp:35-43](), [include/biosversionutils.hpp:46-171]()