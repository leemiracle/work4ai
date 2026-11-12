<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-ipmi-oem · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [CMakeLists.txt](CMakeLists.txt)
- [README.md](README.md)
- [src/BF/chassiscommands.cpp](src/BF/chassiscommands.cpp)

</details>



This document provides an overview of the NVIDIA IPMI OEM Commands library, a platform-specific extension to the OpenBMC IPMI implementation that enables hardware management and control for NVIDIA server platforms including Bluefield DPUs and Grace systems.

## Purpose and Scope

The NVIDIA IPMI OEM Commands library (`znvipmioemcmds`) extends the standard IPMI command set with platform-specific OEM commands tailored for NVIDIA hardware platforms. The library integrates with the OpenBMC ecosystem, providing out-of-band management capabilities for system monitoring, power control, thermal management, and hardware configuration across different NVIDIA platform variants.

The library serves as an IPMI provider that registers custom command handlers with the OpenBMC `libipmid` framework, enabling remote management through standard IPMI interfaces while exposing NVIDIA-specific functionality. For detailed information about specific platform implementations, see [Bluefield Platform](#3.1) and [Grace Platform](#3.2). For architecture details, see [System Architecture](#2).

## Library Architecture

The library is structured around a platform-differentiated architecture that provides common infrastructure while enabling platform-specific customizations:

### IPMI Command Registration and Processing Flow

```mermaid
graph TD
    IPMI_Client["IPMI Client<br/>(ipmitool, etc.)"]
    libipmid["libipmid Framework<br/>(OpenBMC IPMI Daemon)"]
    
    subgraph "znvipmioemcmds Library"
        Registration["Command Registration<br/>ipmi::registerHandler()"]
        
        subgraph "Platform-Specific Handlers"
            BF_Handlers["Bluefield Handlers<br/>src/BF/oemcommands.cpp"]
            Grace_Handlers["Grace Handlers<br/>Grace/src/ghoemcommands.cpp"]
            BF2_Handlers["BF2 Handlers<br/>src/BF/BF2/oemcommands.cpp"]
            Spectre_Handlers["Spectre Handlers<br/>src/BF/spectre/oemcommands.cpp"]
        end
        
        Common_Handlers["Common Handlers<br/>src/oemcommands.cpp"]
        Storage_Handlers["Storage Handlers<br/>src/storagecommands.cpp"]
        Sensor_Handlers["Sensor Handlers<br/>src/sensorcommands.cpp"]
        
        subgraph "Hardware Interface Layer"
            DBus_Services["D-Bus Service Calls<br/>OpenBMC Services"]
            I2C_GPIO["I2C/GPIO Control<br/>Direct Hardware Access"]
        end
    end
    
    IPMI_Client --> libipmid
    libipmid --> Registration
    Registration --> BF_Handlers
    Registration --> Grace_Handlers
    Registration --> BF2_Handlers
    Registration --> Spectre_Handlers
    Registration --> Common_Handlers
    Registration --> Storage_Handlers
    Registration --> Sensor_Handlers
    
    BF_Handlers --> DBus_Services
    Grace_Handlers --> DBus_Services
    Common_Handlers --> DBus_Services
    Storage_Handlers --> DBus_Services
    Sensor_Handlers --> DBus_Services
    
    BF_Handlers --> I2C_GPIO
    Grace_Handlers --> I2C_GPIO
```

*Sources: [CMakeLists.txt:114-189](), [src/BF/chassiscommands.cpp:76-151]()*

### Platform Differentiation Strategy

The library implements a graduated feature support model where different platforms receive different levels of OEM command functionality:

```mermaid
graph TB
    subgraph "Build-Time Platform Selection"
        CMake_Flags["CMake Configuration Flags<br/>CMakeLists.txt"]
        
        subgraph "Platform Build Targets"
            GH_Flag["GH-oem-commands<br/>Grace Platform"]
            BF2_Flag["BF2-OEM-COMMANDS<br/>Limited BF2 Support"]
            BF3_Flag["BF3-OEM-COMMANDS<br/>Enhanced BF3 Support"]
            Spectre_Flag["SPECTRE-OEM-COMMANDS<br/>Disabled Commands"]
        end
    end
    
    subgraph "Generated Library Variants"
        subgraph "Full Featured (Bluefield)"
            BF_OEM["ipmiOemNvNicMode()<br/>ipmiOemSetNvBootstrapAccount()<br/>ipmiOemSetNvPowerCapValue()"]
            BF_Network["ipmiOemSetNvDhcp()<br/>ipmiOemSetNvHostName()<br/>ipmiOemSetNvRshimNetwork()"]
            BF_Power["ipmiOemNvPowerCapCmd()<br/>ipmiOemNvGetPsuPresent()"]
        end
        
        subgraph "GPU Focused (Grace)"
            Grace_GPU["ipmiOemGpuSmbpbiPassThru()<br/>ipmiOemSetNvLivefish()"]
            Grace_Redfish["ipmiOemGetRedfishServiceUuid()<br/>ipmiOemSetHostName()"]
            Grace_BIOS["ipmiOemGetBiosPassword()<br/>ipmiOemSetBiosPassword()"]
        end
        
        subgraph "Limited (BF2/Spectre)"
            BF2_Limited["Most Commands Return<br/>ccResponseError"]
            Spectre_Disabled["All OEM Commands Return<br/>ccInvalidCommand"]
        end
    end
    
    CMake_Flags --> GH_Flag
    CMake_Flags --> BF2_Flag
    CMake_Flags --> BF3_Flag
    CMake_Flags --> Spectre_Flag
    
    GH_Flag --> Grace_GPU
    GH_Flag --> Grace_Redfish
    GH_Flag --> Grace_BIOS
    
    BF3_Flag --> BF_OEM
    BF3_Flag --> BF_Network
    BF3_Flag --> BF_Power
    
    BF2_Flag --> BF2_Limited
    Spectre_Flag --> Spectre_Disabled
```

*Sources: [CMakeLists.txt:120-150](), [CMakeLists.txt:185-189]()*

## Core Functional Areas

The library provides management capabilities across several key functional domains:

| Functional Area | Primary Platforms | Key Commands | Integration Method |
|-----------------|-------------------|--------------|-------------------|
| Network Management | Bluefield, Grace | `ipmiOemSetNvDhcp`, `ipmiOemSetNvHostName` | D-Bus services |
| Power Management | Bluefield | `ipmiOemNvPowerCapCmd`, `ipmiOemGetPowerSupplyInfo` | D-Bus + I2C |
| Thermal Control | All platforms | `ipmiOemNvSetFanPwm`, `ipmiOemNvGetFanPwm` | D-Bus fan services |
| Hardware Status | All platforms | `ipmiOemNvGetPsuPresent`, `ipmiOemNvGetLedStatus` | I2C + GPIO |
| User Management | Bluefield | `ipmiOemSetNvBootstrapAccount` | D-Bus user services |
| GPU Management | Grace | `ipmiOemGpuSmbpbiPassThru` | Direct I2C passthrough |
| Storage/FRU | All platforms | FRU read/write, SDR management | IPMI storage layer |

*Sources: [CMakeLists.txt:114-117](), [src/BF/chassiscommands.cpp:1-16]()*

## Integration with OpenBMC

The library leverages the OpenBMC D-Bus architecture for most system interactions, providing a clean separation between IPMI protocol handling and actual system management:

```mermaid
graph LR
    subgraph "IPMI Layer"
        OEM_Commands["OEM Command Handlers<br/>znvipmioemcmds"]
    end
    
    subgraph "D-Bus Service Layer"
        Network_Mgr["xyz.openbmc_project.Network"]
        Power_Mgr["xyz.openbmc_project.Control.Power"]
        User_Mgr["xyz.openbmc_project.User.Manager"]
        Fan_Mgr["xyz.openbmc_project.Control.FanPwm"]
        LED_Mgr["xyz.openbmc_project.LED.Controller"]
        Host_State["xyz.openbmc_project.State.Host"]
        Redfish_Svc["xyz.openbmc_project.RedfishService"]
    end
    
    subgraph "Hardware Layer"
        I2C_Buses["I2C Bus Controllers<br/>PSU, FPGA, Switch Access"]
        GPIO_Control["GPIO Controllers<br/>LED, Reset, Write Protection"]
        System_Services["System Services<br/>Network, Users, Logging"]
    end
    
    OEM_Commands --> Network_Mgr
    OEM_Commands --> Power_Mgr
    OEM_Commands --> User_Mgr
    OEM_Commands --> Fan_Mgr
    OEM_Commands --> LED_Mgr
    OEM_Commands --> Host_State
    OEM_Commands --> Redfish_Svc
    
    Network_Mgr --> System_Services
    Power_Mgr --> I2C_Buses
    Fan_Mgr --> I2C_Buses
    LED_Mgr --> GPIO_Control
    Host_State --> System_Services
```

*Sources: [src/BF/chassiscommands.cpp:40-74](), [CMakeLists.txt:96-99]()*

## Build System and Configuration

The library uses CMake with extensive conditional compilation to support multiple platform variants from a single codebase. Key configuration options include:

- **Platform Selection**: `GH-oem-commands`, `BF2-OEM-COMMANDS`, `BF3-OEM-COMMANDS`, `SPECTRE-OEM-COMMANDS`
- **Feature Toggles**: `disable-smbpbi-passthru`, `custom-pwm-fan`, `cpu-diag-enable`
- **Hardware Configuration**: `WP-GPIO`, `chassis-write-protect`, `gb200-fan-enable`

The build system generates the `znvipmioemcmds` shared library that integrates with the OpenBMC `libipmid` framework as a provider plugin.

*Sources: [CMakeLists.txt:1-236](), [README.md:1-2]()*

This overview establishes the foundation for understanding the NVIDIA IPMI OEM Commands library's role in providing platform-specific hardware management capabilities within the OpenBMC ecosystem. For detailed implementation specifics, refer to the relevant platform and functional area documentation sections.

---

