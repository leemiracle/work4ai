<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvbmc-docs · page 5 Platform Protocols · fetched 2026-10-26 -->

# Platform Protocols

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [designs/pldm-stack.md](designs/pldm-stack.md)
- [nvidia/FW-Update/fw_update_platform_guide.md](nvidia/FW-Update/fw_update_platform_guide.md)
- [nvidia/Host-Interfaces/redfish-host-interface.md](nvidia/Host-Interfaces/redfish-host-interface.md)
- [nvidia/MCTP/mctp.md](nvidia/MCTP/mctp.md)
- [nvidia/Telemetry/PLDM T2 Telemetry.md](nvidia/Telemetry/PLDM T2 Telemetry.md)

</details>



Platform Protocols provides advanced communication protocols that enable OpenBMC to manage and interact with various devices in the platform. This document covers the implementation and integration of industry-standard protocols including PLDM (Platform Level Data Model), MCTP (Management Component Transport Protocol), and SPDM (Security Protocol and Data Model).

For information about external management interfaces like REST and Redfish APIs, see [Management Interfaces](#4). For core OpenBMC architecture and D-Bus communication, see [Core Architecture](#3).

## Protocol Stack Overview

Platform Protocols operates as a middleware layer between OpenBMC's core services and hardware devices, providing standardized communication mechanisms for device discovery, monitoring, control, and security.

### Protocol Architecture

```mermaid
graph TB
    subgraph "Application Layer"
        PLDM_Apps["PLDM Applications<br/>pldmd, sensor monitoring"]
        NSM["NVIDIA NSM<br/>nsmd"]
        FWUpdate["Firmware Update<br/>PLDM UA"]
    end
    
    subgraph "Protocol Layer"
        PLDM["PLDM Protocol<br/>Types 0,2,5"]
        SPDM["SPDM Protocol<br/>Device Attestation"]
        VDM["Vendor Defined Messages<br/>NVIDIA VDM"]
    end
    
    subgraph "Transport Layer"
        MCTP["MCTP Protocol<br/>mctp-demux-daemon"]
        MCTPCtrl["MCTP Control<br/>mctp-ctrl"]
    end
    
    subgraph "Physical Bindings"
        PCIe["PCIe VDM"]
        I2C["I2C/SMBus"]
        USB["USB"]
        SPI["SPI"]
    end
    
    subgraph "OpenBMC Core"
        DBus["D-Bus Communication"]
        bmcweb["bmcweb Web Server"]
        EntityMgr["Entity Manager"]
    end
    
    PLDM_Apps --> PLDM
    NSM --> VDM
    FWUpdate --> PLDM
    
    PLDM --> MCTP
    SPDM --> MCTP
    VDM --> MCTP
    
    MCTP --> PCIe
    MCTP --> I2C
    MCTP --> USB
    MCTP --> SPI
    
    MCTPCtrl --> DBus
    PLDM_Apps --> DBus
    DBus --> bmcweb
    DBus --> EntityMgr
```

Sources: [designs/pldm-stack.md:25-70](), [nvidia/MCTP/mctp.md:48-76]()

## PLDM Implementation

PLDM serves as the primary application-layer protocol for platform management, providing standardized mechanisms for sensor monitoring, firmware updates, and device control.

### PLDM Service Architecture

```mermaid
graph TB
    subgraph "PLDM Daemon Components"
        pldmd["pldmd"]
        TerminusManager["TerminusManager<br/>terminus_manager.cpp"]
        PlatformManager["PlatformManager<br/>platform_manager.cpp"]
        SensorManager["SensorManager<br/>sensor_manager.cpp"]
        EventManager["EventManager<br/>event_manager.cpp"]
    end
    
    subgraph "PLDM Libraries"
        libpldm["libpldm<br/>encode/decode"]
        ProviderLibs["Provider Libraries<br/>platform specific handlers"]
    end
    
    subgraph "PLDM Types"
        Type0["Type 0: Base"]
        Type2["Type 2: Platform M&C"]
        Type5["Type 5: Firmware Update"]
    end
    
    subgraph "D-Bus Interfaces"
        SensorValue["xyz.openbmc_project.Sensor.Value"]
        SoftwareVersion["xyz.openbmc_project.Software.Version"]
        MCTPEndpoint["xyz.openbmc_project.MCTP.Endpoint"]
    end
    
    pldmd --> TerminusManager
    pldmd --> PlatformManager
    pldmd --> SensorManager
    pldmd --> EventManager
    
    TerminusManager --> libpldm
    PlatformManager --> libpldm
    SensorManager --> libpldm
    EventManager --> libpldm
    
    pldmd --> ProviderLibs
    
    Type0 --> libpldm
    Type2 --> libpldm
    Type5 --> libpldm
    
    SensorManager --> SensorValue
    EventManager --> SoftwareVersion
    TerminusManager --> MCTPEndpoint
```

Sources: [designs/pldm-stack.md:130-180](), [nvidia/Telemetry/PLDM T2 Telemetry.md:240-249]()

### PLDM Request/Response Flow

The PLDM daemon implements both requester and responder functionality, handling device discovery, initialization, and ongoing communication.

| Component | File Location | Responsibility |
|-----------|---------------|----------------|
| Terminus Discovery | [platform-mc/terminus_manager.cpp]() | EID enumeration, TID assignment |
| PDR Repository | [platform-mc/platform_manager.cpp]() | PDR retrieval and parsing |
| Sensor Polling | [platform-mc/sensor_manager.cpp]() | Periodic sensor reading updates |
| Event Handling | [platform-mc/event_manager.cpp]() | Asynchronous event processing |

Sources: [designs/pldm-stack.md:251-354](), [nvidia/Telemetry/PLDM T2 Telemetry.md:251-332]()

## MCTP Transport Layer

MCTP provides the transport foundation for all platform protocols, enabling communication across multiple physical interfaces with a unified addressing scheme.

### MCTP Service Architecture

```mermaid
graph TB
    subgraph "MCTP Services"
        DemuxDaemon["mctp-demux-daemon<br/>mctp-demux-daemon.c"]
        CtrlDaemon["mctp-ctrl<br/>mctp-ctrl.c"]
    end
    
    subgraph "MCTP Bindings"
        astpcie["astpcie.c<br/>PCIe VDM binding"]
        smbus["smbus.c<br/>I2C/SMBus binding"]
        usb["usb.c<br/>USB binding"]
        astspi["astspi.c<br/>SPI binding"]
    end
    
    subgraph "Discovery & Control"
        Discovery["mctp-discovery.c<br/>Endpoint discovery"]
        Encode["mctp-encode.c<br/>Message encoding"]
        DBusIntf["mctp-sdbus.c<br/>D-Bus interface"]
    end
    
    subgraph "Applications"
        pldmd_client["pldmd<br/>PLDM client"]
        nsmd_client["nsmd<br/>NSM client"]
        vdm_util["mctp-vdm-util<br/>VDM utility"]
    end
    
    DemuxDaemon --> astpcie
    DemuxDaemon --> smbus
    DemuxDaemon --> usb
    DemuxDaemon --> astspi
    
    CtrlDaemon --> Discovery
    CtrlDaemon --> Encode
    CtrlDaemon --> DBusIntf
    
    pldmd_client --> DemuxDaemon
    nsmd_client --> DemuxDaemon
    vdm_util --> DemuxDaemon
    
    CtrlDaemon --> DBusIntf
```

Sources: [nvidia/MCTP/mctp.md:78-127](), [nvidia/MCTP/mctp.md:130-271]()

### MCTP Endpoint Discovery

MCTP control daemon manages endpoint discovery and EID assignment using either bridged or direct-attached configurations.

| Configuration Type | Description | Supported Bindings |
|-------------------|-------------|-------------------|
| Bridged Network | Endpoints behind FPGA bridge | PCIe VDM, USB |
| Direct Attached | Point-to-point connections | SPI, SMBus |
| Multi-endpoint | Multiple devices on bus | SMBus with JSON config |

Sources: [nvidia/MCTP/mctp.md:111-127](), [nvidia/MCTP/mctp.md:645-709]()

## SPDM Security Protocol

SPDM provides device authentication and secure communication capabilities, enabling trusted platform management.

### SPDM Integration

SPDM operates over MCTP transport to establish secure sessions with devices supporting attestation and measurement protocols.

```mermaid
graph LR
    subgraph "SPDM Flow"
        GetVersion["GET_VERSION"]
        GetCapabilities["GET_CAPABILITIES"]
        NegotiateAlgorithms["NEGOTIATE_ALGORITHMS"]
        GetDigests["GET_DIGESTS"]
        GetCertificate["GET_CERTIFICATE"]
        Challenge["CHALLENGE"]
        GetMeasurements["GET_MEASUREMENTS"]
    end
    
    subgraph "Security Features"
        Authentication["Device Authentication"]
        Attestation["Platform Attestation"]
        Measurements["Device Measurements"]
        SecureSession["Secure Sessions"]
    end
    
    GetVersion --> GetCapabilities
    GetCapabilities --> NegotiateAlgorithms
    NegotiateAlgorithms --> GetDigests
    GetDigests --> GetCertificate
    GetCertificate --> Challenge
    Challenge --> GetMeasurements
    
    Challenge --> Authentication
    GetMeasurements --> Attestation
    GetMeasurements --> Measurements
    NegotiateAlgorithms --> SecureSession
```

Sources: [nvidia/FW-Update/fw_update_platform_guide.md:42-48]()

## Protocol Integration with OpenBMC

Platform Protocols integrates with OpenBMC's core architecture through standardized D-Bus interfaces and service interactions.

### D-Bus Interface Mapping

```mermaid
graph TB
    subgraph "Platform Protocol Services"
        MCTPCtrl["mctp-ctrl"]
        pldmd["pldmd"]
        nsmd["nsmd"]
    end
    
    subgraph "D-Bus Interfaces"
        MCTPEndpoint["xyz.openbmc_project.MCTP.Endpoint<br/>/xyz/openbmc_project/mctp/1/8"]
        SensorValue["xyz.openbmc_project.Sensor.Value<br/>/xyz/openbmc_project/sensors/temperature/CPU0_Temp"]
        SoftwareVersion["xyz.openbmc_project.Software.Version<br/>/xyz/openbmc_project/software/ComponentName"]
        InventoryItem["xyz.openbmc_project.Inventory.Item<br/>/xyz/openbmc_project/inventory/system/chassis/GPU0"]
    end
    
    subgraph "Consumer Services"
        bmcweb["bmcweb"]
        EntityManager["Entity Manager"]
        ObjectMapper["Object Mapper"]
    end
    
    MCTPCtrl --> MCTPEndpoint
    pldmd --> SensorValue
    pldmd --> SoftwareVersion
    nsmd --> InventoryItem
    
    MCTPEndpoint --> ObjectMapper
    SensorValue --> bmcweb
    SoftwareVersion --> bmcweb
    InventoryItem --> EntityManager
```

Sources: [designs/pldm-stack.md:383-416](), [nvidia/Telemetry/PLDM T2 Telemetry.md:475-599]()

### Service Dependencies

| Service | Dependencies | Provides |
|---------|-------------|----------|
| `mctp-demux-daemon` | Kernel drivers, udev rules | UNIX socket for MCTP communication |
| `mctp-ctrl` | `mctp-demux-daemon` | D-Bus endpoint discovery interface |
| `pldmd` | `mctp-ctrl`, `mctp-demux-daemon` | Sensor and firmware management D-Bus objects |
| `nsmd` | `mctp-ctrl`, `mctp-demux-daemon` | GPU telemetry and inventory D-Bus objects |

Sources: [nvidia/MCTP/mctp.md:273-388](), [designs/pldm-stack.md:72-115]()

## Platform Enablement

Platform Protocols requires specific configuration for transport bindings, protocol options, and device-specific settings.

### Build Configuration

Key build-time options control protocol feature enablement:

| Component | Configuration Option | Description |
|-----------|---------------------|-------------|
| PLDM | `pldm-type2=enabled` | Enable PLDM Type 2 platform monitoring |
| PLDM | `libpldmresponder=enabled` | Enable PLDM responder for async events |
| MCTP | `enable-usb=enabled` | Enable USB transport binding |
| MCTP | `mctp-batch-tx=enabled` | Enable USB packet batching |

Sources: [nvidia/Telemetry/PLDM T2 Telemetry.md:564-604](), [nvidia/MCTP/mctp.md:403-423]()

### Device Configuration

Platform-specific JSON configuration files define device mappings and protocol parameters:

```json
{
  "PrioritySensorNameSpaces": [
    "/xyz/openbmc_project/sensors/temperature/",
    "/xyz/openbmc_project/sensors/power/",
    "/xyz/openbmc_project/sensors/energy/"
  ]
}
```

Sources: [nvidia/Telemetry/PLDM T2 Telemetry.md:607-623](), [nvidia/FW-Update/fw_update_platform_guide.md:171-377]()

Platform Protocols enables standardized device communication while providing flexibility for platform-specific requirements through modular transport bindings and configurable protocol stacks.

---

