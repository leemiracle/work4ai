<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-power-manager · page 3 CPLD Management Subsystem · fetched 2026-10-26 -->

# CPLD Management Subsystem

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [nvidia-cpld/meson.build](nvidia-cpld/meson.build)
- [nvidia-cpld/src/cpld.hpp](nvidia-cpld/src/cpld.hpp)

</details>



## Purpose and Scope

The CPLD Management Subsystem provides comprehensive management of Complex Programmable Logic Device (CPLD) components in NVIDIA systems. This subsystem encompasses two primary functions:

1. **Runtime Monitoring** - A persistent D-Bus service that exposes CPLD inventory, version information, and operational status
2. **Firmware Updates** - Command-line utilities for flashing CPLD firmware images

This page provides an overview of the CPLD management architecture and the relationships between its components. For detailed documentation of specific components, see:
- [CPLD D-Bus Service](#3.1) - Runtime monitoring service implementation
- [CPLD Firmware Update Utilities](#3.2) - Firmware update tools and flows

The subsystem integrates with OpenBMC's standard D-Bus interfaces and follows the dual-hierarchy pattern where CPLDs appear in both the inventory tree (`/xyz/openbmc_project/inventory`) and software tree (`/xyz/openbmc_project/software`).

---

## CPLD Management Architecture

The CPLD Management Subsystem is organized into two independent but complementary components that share hardware access but operate at different layers of the system:

```mermaid
graph TB
    subgraph "Runtime Service Layer"
        CPLD_SERVICE["nvidia-cpld<br/>D-Bus Service<br/>(Always Running)"]
        CPLD_CLASS["Cpld class<br/>nvidia-cpld/src/cpld.hpp"]
        CPLD_MANAGER["CPLDManager<br/>Service Orchestrator"]
    end
    
    subgraph "Firmware Update Layer"
        CPLD_UPDATE["cpldupdate<br/>CLI Utility<br/>(On-Demand)"]
        
        subgraph "Conditional Compilation"
            GENERIC_PATH["Generic Path<br/>libcpld"]
            DRAGON_PATH["DragonCpld Path<br/>dragonCpld.cpp"]
        end
    end
    
    subgraph "Hardware Access Layer"
        SHELL_INTF["PSShellIntf<br/>cpldi2ccmd.sh"]
        I2C_BUS["I2C Bus<br/>/dev/i2c-*"]
        CPLD_HW["CPLD Devices<br/>Physical Hardware"]
    end
    
    subgraph "D-Bus Infrastructure"
        DBUS_SYSTEM["D-Bus System Bus<br/>com.Nvidia.Cpld"]
        INV_PATH["/xyz/openbmc_project/inventory/system/board/<br/>motherboard/CPLDxx"]
        SW_PATH["/xyz/openbmc_project/software/<br/>platform_fw_CPLDxx"]
    end
    
    CPLD_SERVICE --> CPLD_CLASS
    CPLD_SERVICE --> CPLD_MANAGER
    CPLD_CLASS --> DBUS_SYSTEM
    DBUS_SYSTEM --> INV_PATH
    DBUS_SYSTEM --> SW_PATH
    
    CPLD_CLASS -.queries status.-> SHELL_INTF
    
    CPLD_UPDATE --> GENERIC_PATH
    CPLD_UPDATE --> DRAGON_PATH
    GENERIC_PATH --> I2C_BUS
    DRAGON_PATH --> I2C_BUS
    
    SHELL_INTF --> I2C_BUS
    I2C_BUS --> CPLD_HW
    
    style CPLD_SERVICE fill:#ffe1f5
    style CPLD_UPDATE fill:#ffa07a
    style DBUS_SYSTEM fill:#e8f5e9
```

**Architecture Overview**: The D-Bus service (`nvidia-cpld`) operates continuously, exposing CPLD information through standard OpenBMC interfaces. The update utility (`cpldupdate`) runs on-demand for firmware maintenance. Both components access CPLD hardware via I2C, but through different abstraction layers: the service uses shell script wrappers (`cpldi2ccmd.sh`) for status queries, while the update utility uses direct I2C access through either generic libraries or platform-specific C++ classes.

**Sources**: [nvidia-cpld/src/cpld.hpp](), [nvidia-cpld/meson.build](), [cpld_utility/meson.build]()

---

## D-Bus Service Component

The `nvidia-cpld` service is implemented as a systemd service that publishes CPLD information to the D-Bus system bus using the bus name `com.Nvidia.Cpld`. The core implementation consists of:

| Component | File | Purpose |
|-----------|------|---------|
| `Cpld` class | [nvidia-cpld/src/cpld.hpp:126-267]() | Represents individual CPLD devices with full D-Bus interface implementation |
| `CPLDManager` | [nvidia-cpld/src/cpld_manager.hpp]() | Service orchestrator that creates and manages `Cpld` instances from JSON configuration |
| `Util` base class | [nvidia-cpld/src/cpld_util.hpp]() | Hardware abstraction providing I2C communication via shell interface |
| JSON configuration | `/usr/share/nvidia-power-manager/cpld_config.json` | Defines CPLD inventory: bus addresses, names, associations |

### D-Bus Interfaces Implemented

Each `Cpld` object implements the following OpenBMC D-Bus interfaces through multiple inheritance:

| Interface | Purpose | Key Properties |
|-----------|---------|----------------|
| `xyz.openbmc_project.State.Decorator.OperationalStatus` | Operational state tracking | `functional`, `state` (Enabled/Disabled) |
| `xyz.openbmc_project.Inventory.Item` | Basic inventory properties | `present`, `prettyName` |
| `xyz.openbmc_project.Inventory.Item.Chassis` | Chassis classification | `type` (Module) |
| `xyz.openbmc_project.Inventory.Decorator.Asset` | Asset identification | `manufacturer`, `model`, `partNumber`, `serialNumber` |
| `xyz.openbmc_project.Inventory.Decorator.Location` | Physical location metadata | `locationType` |
| `xyz.openbmc_project.Association.Definitions` | Relationship definitions | `associations` (parent-child links) |

The interface inheritance is defined via the `CpldInherit` type alias at [nvidia-cpld/src/cpld.hpp:39-46]().

### D-Bus Object Hierarchy

```mermaid
graph TB
    subgraph "Inventory Tree"
        INV_BASE["/xyz/openbmc_project/inventory/system/board"]
        INV_MB["motherboard"]
        CPLD0["CPLDxx<br/>(Cpld object)"]
        CPLD1["CPLDyy<br/>(Cpld object)"]
        
        INV_BASE --> INV_MB
        INV_MB --> CPLD0
        INV_MB --> CPLD1
    end
    
    subgraph "Software Tree"
        SW_BASE["/xyz/openbmc_project/software"]
        SW_CPLD0["platform_fw_CPLDxx<br/>(VersionInterface)"]
        SW_CPLD1["platform_fw_CPLDyy<br/>(VersionInterface)"]
        SW_ASSET0["(SoftwareAsset)"]
        SW_ASSET1["(SoftwareAsset)"]
        SW_ASSOC0["(Association)"]
        SW_ASSOC1["(Association)"]
        
        SW_BASE --> SW_CPLD0
        SW_BASE --> SW_CPLD1
        SW_CPLD0 -.implements.- SW_ASSET0
        SW_CPLD0 -.implements.- SW_ASSOC0
        SW_CPLD1 -.implements.- SW_ASSET1
        SW_CPLD1 -.implements.- SW_ASSOC1
    end
    
    subgraph "Associations"
        CPLD0 -.parent_chassis.-> INV_MB
        CPLD0 -.software_version.-> SW_CPLD0
        SW_CPLD0 -.updateable.-> SW_BASE
        SW_CPLD0 -.activation.-> INV_MB
    end
    
    style CPLD0 fill:#ffe1f5
    style CPLD1 fill:#ffe1f5
    style SW_CPLD0 fill:#fff4e1
    style SW_CPLD1 fill:#fff4e1
```

**Object Structure**: Each CPLD device creates objects in both the inventory tree (physical representation) and software tree (firmware representation). The inventory object path follows the pattern `/xyz/openbmc_project/inventory/system/board/motherboard/{PLATFORM_PREFIX}CPLD{N}`. The software object path inserts a firmware prefix into the name: `/xyz/openbmc_project/software/{PLATFORM_PREFIX}{PLATFORM_FW_PREFIX}CPLD{N}`. Associations bidirectionally link these representations.

The construction logic is implemented in:
- Inventory object creation: [nvidia-cpld/src/cpld.hpp:136-184]()
- Software version registration: [nvidia-cpld/src/cpld.hpp:209-219]()
- Association setup: [nvidia-cpld/src/cpld.hpp:186-208]()
- Asset object creation: [nvidia-cpld/src/cpld.hpp:243-253]()

**Sources**: [nvidia-cpld/src/cpld.hpp:39-267](), [nvidia-cpld/meson.build:10-16]()

---

## Firmware Update Component

The `cpldupdate` utility provides command-line firmware update capabilities for CPLD devices. The utility supports two distinct implementation paths selected at compile time:

| Implementation | Meson Option | Source Files | Platform Support |
|----------------|--------------|--------------|------------------|
| **Generic Path** | `dragon_chassis_cpld=disabled` | `libcpld` C library | Standard I2C-based platforms |
| **Dragon Chassis Path** | `dragon_chassis_cpld=enabled` | [cpld_utility/dragonCpld.cpp]() | Dragon chassis with arbitration |

### Implementation Selection

The build system uses conditional compilation to select the appropriate implementation:

```mermaid
graph LR
    MESON["meson_options.txt<br/>dragon_chassis_cpld"]
    BUILD["cpld_utility/meson.build"]
    
    subgraph "Compilation Paths"
        GENERIC["Generic Build<br/>+ libcpld<br/>+ libi2c"]
        DRAGON["Dragon Build<br/>+ dragonCpld.cpp<br/>+ dragonChassisBase.cpp<br/>+ libgpiodcxx"]
    end
    
    MESON -->|disabled| BUILD
    MESON -->|enabled| BUILD
    BUILD -->|option disabled| GENERIC
    BUILD -->|option enabled| DRAGON
    
    GENERIC --> BINARY["cpldupdate binary"]
    DRAGON --> BINARY
```

**Build Configuration**: The Meson build system evaluates the `dragon_chassis_cpld` option and includes different source files and dependencies accordingly. When Dragon support is enabled, the build adds C++ source files (`dragonCpld.cpp`, `dragonChassisBase.cpp`) and the `libgpiodcxx` dependency for GPIO control. The generic path uses simpler C libraries for direct I2C access.

### Update Utility Capabilities

Both implementation paths support the following update workflow:

1. **Image Validation** - Verify firmware image format and checksums
2. **Hardware Detection** - Identify CPLD device via I2C bus scanning
3. **Pre-Update State** - Query current firmware version
4. **Firmware Programming** - Erase and program CPLD flash memory
5. **Post-Update Verification** - Verify new firmware version

The Dragon Chassis implementation adds:
- **I2C Arbitration** - Coordinate bus access with kernel driver via sysfs
- **GPIO Refresh Signaling** - Trigger CPLD refresh using libgpiod
- **PEC (Packet Error Code)** - Enhanced I2C data integrity checking
- **Retry Logic** - Robust error handling with exponential backoff

Command-line interface example:
```bash
# Generic platform update
cpldupdate --dev <i2c_bus> --image <firmware.bin> --config <device_config.json>

# Dragon chassis update (same interface, different implementation)
cpldupdate --dev <i2c_bus> --image <firmware.bin> --config <device_config.json>
```

**Sources**: [cpld_utility/meson.build](), [cpld_utility/dragonCpld.cpp](), [cpld_utility/dragonChassisBase.cpp]()

---

## Integration with OpenBMC

The CPLD Management Subsystem follows OpenBMC architectural patterns for seamless integration with other BMC services and management interfaces:

### Service Registration

The D-Bus service is registered as a systemd unit that integrates with the BMC boot sequence:

| Configuration | Value | Location |
|---------------|-------|----------|
| **D-Bus Bus Name** | `com.Nvidia.Cpld` | [nvidia-cpld/meson.build:10]() |
| **Service Unit** | `nvidia-cpld.service` | [nvidia-cpld/services/]() |
| **Configuration Path** | `/usr/share/nvidia-power-manager/cpld_config.json` | [nvidia-cpld/meson.build:6-8]() |
| **Shell Interface** | `cpldi2ccmd.sh` | [nvidia-cpld/meson.build:24-28]() |

### Inventory Integration

CPLD objects appear in the OpenBMC inventory system with full asset management support:

- **Inventory Path Pattern**: `/xyz/openbmc_project/inventory/system/board/motherboard/{PLATFORM_PREFIX}CPLD{N}`
- **Chassis Type**: `xyz.openbmc_project.Inventory.Item.Chassis.ChassisType.Module` ([nvidia-cpld/src/cpld.hpp:163-168]())
- **Asset Properties**: Retrieved via `Util` class methods calling shell interface
  - `manufacturer()` - Manufacturer identification
  - `model()` - Model name
  - `partNumber()` - Retrieved via `getPartNumber()` ([nvidia-cpld/src/cpld.hpp:150]())
  - `serialNumber()` - Retrieved via `getSerialNumber()` ([nvidia-cpld/src/cpld.hpp:152]())

### Software Version Tracking

CPLD firmware versions are published to the OpenBMC software management tree:

- **Software Path Pattern**: `/xyz/openbmc_project/software/{PLATFORM_PREFIX}{PLATFORM_FW_PREFIX}CPLD{N}`
- **Version Interface**: `xyz.openbmc_project.Software.Version` ([nvidia-cpld/src/cpld.hpp:51-52]())
- **Version Purpose**: `xyz.openbmc_project.Software.Version.VersionPurpose.Other` ([nvidia-cpld/src/cpld.hpp:98](), [263-264]())
- **Version Retrieval**: Implemented via `getVersion()` method ([nvidia-cpld/src/cpld.hpp:216]())

### Association Model

The subsystem implements bidirectional associations linking inventory objects to software versions:

```mermaid
graph LR
    INV_CPLD["Inventory Object<br/>/inventory/.../CPLDxx"]
    SW_CPLD["Software Object<br/>/software/...fw_CPLDxx"]
    CHASSIS["Chassis Object<br/>/inventory/.../motherboard"]
    SW_BASE["Software Base<br/>/xyz/openbmc_project/software"]
    
    INV_CPLD -->|"software_version"| SW_CPLD
    SW_CPLD -->|"updateable"| INV_CPLD
    
    INV_CPLD -->|"parent_chassis"| CHASSIS
    CHASSIS -->|"inventory"| INV_CPLD
    
    SW_CPLD -->|"updateable"| SW_BASE
    SW_BASE -->|"software_version"| SW_CPLD
    
    SW_CPLD -->|"activation"| CHASSIS
    CHASSIS -->|"inventory"| SW_CPLD
```

**Association Configuration**: The `Cpld` class creates multiple association types during initialization. The `createAssociation()` method ([nvidia-cpld/src/cpld.hpp:231-238]()) establishes parent-chassis relationships. The `registerAssociationInterface()` method ([nvidia-cpld/src/cpld.hpp:186-208]()) creates bidirectional links between inventory and software objects using forward association `"software_version"` and reverse association `"updateable"` (defined at [nvidia-cpld/src/cpld.hpp:261-262]()).

**Sources**: [nvidia-cpld/src/cpld.hpp:126-267](), [nvidia-cpld/meson.build:10-16]()

---

## Data Flow and Component Interaction

The following diagram illustrates how data flows through the CPLD Management Subsystem during typical operations:

```mermaid
sequenceDiagram
    participant BMC as BMC Boot Sequence
    participant SVC as nvidia-cpld Service
    participant MGR as CPLDManager
    participant CPLD as Cpld Objects
    participant SHELL as cpldi2ccmd.sh
    participant HW as CPLD Hardware
    participant DBUS as D-Bus System Bus
    participant CLIENT as D-Bus Clients
    
    Note over BMC,SVC: Service Initialization
    BMC->>SVC: systemd starts service
    SVC->>MGR: Create CPLDManager
    MGR->>MGR: Load cpld_config.json
    
    loop For each CPLD in config
        MGR->>CPLD: Create Cpld(bus, addr, name, ...)
        CPLD->>SHELL: getVersion()
        SHELL->>HW: I2C read version register
        HW-->>SHELL: Version data
        SHELL-->>CPLD: Version string
        
        CPLD->>SHELL: getPartNumber()
        SHELL->>HW: I2C read part number
        HW-->>SHELL: Part number
        SHELL-->>CPLD: Part number string
        
        CPLD->>SHELL: getSerialNumber()
        SHELL->>HW: I2C read serial
        HW-->>SHELL: Serial data
        SHELL-->>CPLD: Serial string
        
        CPLD->>DBUS: Register inventory object
        CPLD->>DBUS: Register software version object
        CPLD->>DBUS: Register associations
    end
    
    DBUS-->>CLIENT: InterfacesAdded signals
    
    Note over CLIENT,HW: Runtime Monitoring
    CLIENT->>DBUS: GetProperty(Asset.partNumber)
    DBUS->>CPLD: Property getter
    CPLD-->>DBUS: Cached value
    DBUS-->>CLIENT: Property value
    
    Note over CLIENT,HW: Firmware Update (Separate Process)
    CLIENT->>HW: cpldupdate --dev X --image Y
    Note over HW: Update bypasses D-Bus service<br/>Uses direct I2C access
```

**Initialization Flow**: During boot, the `nvidia-cpld` service reads the JSON configuration file to determine which CPLDs exist in the system. For each configured CPLD, it creates a `Cpld` object that immediately queries hardware via the shell interface to retrieve asset information and firmware versions. These values are cached in D-Bus properties for efficient runtime access. The service then registers all objects and interfaces on the D-Bus system bus, triggering `InterfacesAdded` signals that notify other BMC services of the new inventory items.

**Runtime vs. Update**: During normal operation, D-Bus clients query CPLD information through standard OpenBMC interfaces without direct hardware access. Firmware updates occur through a separate process (`cpldupdate` utility) that accesses hardware directly via I2C, completely independent of the D-Bus service. After an update completes, the D-Bus service must be restarted or the system rebooted to refresh the cached version information.

**Sources**: [nvidia-cpld/src/cpld.hpp:126-184](), [nvidia-cpld/src/cpld_util.hpp](), [nvidia-cpld/src/main.cpp]()

---

