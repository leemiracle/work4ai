<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-ipmi-oem · page 2 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CMakeLists.txt](CMakeLists.txt)
- [Grace/src/ghoemcommands.cpp](Grace/src/ghoemcommands.cpp)
- [src/BF/chassiscommands.cpp](src/BF/chassiscommands.cpp)
- [src/BF/oemcommands.cpp](src/BF/oemcommands.cpp)
- [src/BF/spectre/oemcommands.cpp](src/BF/spectre/oemcommands.cpp)
- [src/oemcommands.cpp](src/oemcommands.cpp)

</details>



This document describes the high-level system architecture of the NVIDIA IPMI OEM Commands library (`znvipmioemcmds`). It covers the platform differentiation strategy, command processing pipeline, hardware abstraction mechanisms, and build system organization that enable unified IPMI management across different NVIDIA hardware platforms.

For platform-specific implementation details, see [Bluefield Platform](#3.1), [Grace Platform](#3.2), and [Platform Variants](#3.3). For hardware integration specifics, see [Hardware Integration](#5).

## Architectural Overview

The NVIDIA IPMI OEM Commands library implements a platform-centric architecture that provides unified IPMI management interfaces while supporting graduated feature sets across different NVIDIA hardware platforms. The system is built around three core architectural principles: platform abstraction, shared infrastructure, and conditional compilation.

```mermaid
graph TB
    subgraph "IPMI Command Layer"
        NetFnOem["ipmi::nvidia::netFnOemGlobal"]
        NetFnNV["ipmi::nvidia::netFnOemNV"] 
        NetGroupExt["ipmi::nvidia::netGroupExt"]
    end
    
    subgraph "Platform Dispatcher Layer"
        PlatformRegistry["registerNvOemPlatformFunctions()"]
        CommonRegistry["registerNvOemFunctions()"]
        SpectreRegistry["registerNvOemPlatformFunctionsSpectre()"]
    end
    
    subgraph "Implementation Layer"
        BFImpl["src/BF/oemcommands.cpp"]
        GraceImpl["Grace/src/ghoemcommands.cpp"]
        CommonImpl["src/oemcommands.cpp"]
        SpectreImpl["src/BF/spectre/oemcommands.cpp"]
    end
    
    subgraph "Hardware Abstraction"
        DBusIntf["sdbusplus::asio::connection"]
        I2CIntf["i2cTransaction()"]
        SystemdIntf["systemd unit control"]
    end
    
    NetFnOem --> PlatformRegistry
    NetFnNV --> CommonRegistry  
    NetGroupExt --> PlatformRegistry
    
    PlatformRegistry --> BFImpl
    PlatformRegistry --> GraceImpl
    CommonRegistry --> CommonImpl
    SpectreRegistry --> SpectreImpl
    
    BFImpl --> DBusIntf
    BFImpl --> I2CIntf
    GraceImpl --> DBusIntf
    GraceImpl --> I2CIntf
    CommonImpl --> DBusIntf
    
    DBusIntf --> SystemdIntf
```

**Sources:** [src/BF/oemcommands.cpp:229](), [Grace/src/ghoemcommands.cpp:132](), [src/oemcommands.cpp:201](), [src/BF/spectre/oemcommands.cpp:52]()

## Platform Differentiation Strategy

The system implements a graduated feature support model where different NVIDIA platforms expose different subsets of OEM commands based on their hardware capabilities and intended use cases.

### Platform Support Matrix

| Platform | Implementation File | Feature Level | Constructor Priority |
|----------|-------------------|---------------|---------------------|
| Bluefield | `src/BF/oemcommands.cpp` | Full Featured | 102 |
| Grace | `Grace/src/ghoemcommands.cpp` | GPU Focused | Default |
| BF2 | `src/BF/BF2/oemcommands.cpp` | Limited | N/A |
| Spectre | `src/BF/spectre/oemcommands.cpp` | Disabled | 103 |

```mermaid
graph TD
    subgraph "Feature Enablement Strategy"
        FullFeature["`registerNvOemPlatformFunctions()
        Constructor Priority: 102
        Full Command Set`"]
        GpuFocused["`registerNvOemFunctions()
        GPU Management Focus
        SMBPBI Passthrough`"]
        Limited["`BF2 Platform
        Most Commands Return
        ccResponseError`"]
        Disabled["`registerNvOemPlatformFunctionsSpectre()
        Constructor Priority: 103
        All Commands Return
        ccInvalidCommand`"]
    end
    
    subgraph "Command Registration Patterns"
        BFPattern["`ipmi::registerHandler()
        Full Command Implementation`"]
        GracePattern["`ipmi::registerHandler()
        GPU-Centric Commands`"]
        SpectrePattern["`ipmi::ipmicmdRejectNoParamSpectre()
        Rejection Handlers`"]
    end
    
    FullFeature --> BFPattern
    GpuFocused --> GracePattern
    Limited --> BFPattern
    Disabled --> SpectrePattern
```

**Sources:** [src/BF/oemcommands.cpp:229](), [Grace/src/ghoemcommands.cpp:132](), [src/BF/spectre/oemcommands.cpp:112](), [CMakeLists.txt:185-189]()

## Command Processing Pipeline

The IPMI command processing follows a structured pipeline that routes commands through platform-specific handlers while maintaining common infrastructure for shared functionality.

```mermaid
graph LR
    subgraph "IPMI Entry Points"
        ipmiHandler["`ipmi::registerHandler()
        ipmi::registerGroupHandler()`"]
    end
    
    subgraph "Command Routing"
        NetFnRouter["`Network Function Router
        netFnOemGlobal: 0x3E
        netFnOemNV: 0x30
        netGroupExt: Group Extension`"]
    end
    
    subgraph "Platform Handlers"
        BFHandlers["`Bluefield Handlers
        Power Management
        Network Services
        Bootstrap Accounts`"]
        GraceHandlers["`Grace Handlers
        GPU SMBPBI
        LED Control
        Fan Management`"]
        CommonHandlers["`Common Handlers
        DNS/NTP Config
        SEL Policy
        Factory Reset`"]
    end
    
    subgraph "Hardware Interface"
        DBusCall["`getSdBus()
        D-Bus Method Calls`"]
        I2CCall["`i2cTransaction()
        Hardware Communication`"]
        SystemdCall["`systemd Unit Control
        Service Management`"]
    end
    
    ipmiHandler --> NetFnRouter
    NetFnRouter --> BFHandlers
    NetFnRouter --> GraceHandlers  
    NetFnRouter --> CommonHandlers
    
    BFHandlers --> DBusCall
    GraceHandlers --> DBusCall
    CommonHandlers --> DBusCall
    
    BFHandlers --> I2CCall
    GraceHandlers --> I2CCall
    
    BFHandlers --> SystemdCall
    CommonHandlers --> SystemdCall
```

**Sources:** [src/BF/oemcommands.cpp:2150-2250](), [Grace/src/ghoemcommands.cpp:1850-1950](), [src/oemcommands.cpp:3400-3500]()

## Hardware Abstraction Layer

The system provides a unified hardware abstraction layer that enables platform-agnostic access to various hardware subsystems through standardized interfaces.

### D-Bus Service Integration

```mermaid
graph TB
    subgraph "IPMI Command Layer"
        OEMCommands["`OEM Command Handlers
        Platform-Specific Logic`"]
    end
    
    subgraph "D-Bus Abstraction"
        GetSdBus["`getSdBus()
        Connection Management`"]
        GetService["`ipmi::getService()
        Service Discovery`"]
        GetDbusProperty["`ipmi::getDbusProperty()
        Property Access`"]
        SetDbusProperty["`ipmi::setDbusProperty()
        Property Modification`"]
    end
    
    subgraph "OpenBMC Services"
        NetworkSvc["`xyz.openbmc_project.Network
        DNS/NTP Configuration`"]
        PowerSvc["`com.Nvidia.Powermanager
        Power Capping Control`"]
        StateSvc["`xyz.openbmc_project.State.Host
        System State Management`"]
        UserSvc["`xyz.openbmc_project.User.Manager
        Account Management`"]
        LoggingSvc["`xyz.openbmc_project.Logging.Settings
        SEL Policy Control`"]
    end
    
    OEMCommands --> GetSdBus
    GetSdBus --> GetService
    GetSdBus --> GetDbusProperty
    GetSdBus --> SetDbusProperty
    
    GetService --> NetworkSvc
    GetDbusProperty --> PowerSvc
    SetDbusProperty --> StateSvc
    GetService --> UserSvc
    GetDbusProperty --> LoggingSvc
```

**Sources:** [src/oemcommands.cpp:52-55](), [src/BF/oemcommands.cpp:68-89](), [Grace/src/ghoemcommands.cpp:89-93]()

### I2C Hardware Communication

The system provides direct hardware access through a standardized I2C transaction interface that abstracts low-level hardware communication details.

```mermaid
graph TD
    subgraph "I2C Abstraction Layer"
        I2CTransaction["`i2cTransaction()
        Bus: uint8_t
        SlaveAddr: uint8_t
        WriteData: vector<uint8_t>
        ReadData: vector<uint8_t>`"]
    end
    
    subgraph "Hardware Targets"
        PSUDevices["`PSU Communication
        nvidia::psuBus[]
        nvidia::psuAddr[]`"]
        FPGADevices["`FPGA Control
        nvidia::fpgaMidI2cBus
        nvidia::fpgaI2cAddress`"]
        SwitchDevices["`Ethernet Switches
        nvidia::ethSwitchI2cBusBF3
        nvidia::ethSwitchI2caddressBF3`"]
    end
    
    subgraph "Linux I2C Interface"
        I2CDev["`/dev/i2c-{bus}
        Linux I2C Device Files`"]
        I2CWriteRead["`ipmi::i2cWriteRead()
        IPMID I2C Helper`"]
    end
    
    I2CTransaction --> PSUDevices
    I2CTransaction --> FPGADevices
    I2CTransaction --> SwitchDevices
    
    I2CTransaction --> I2CDev
    I2CDev --> I2CWriteRead
```

**Sources:** [src/oemcommands.cpp:340-361](), [src/BF/oemcommands.cpp:372-393](), [Grace/src/ghoemcommands.cpp:328-349]()

## Build System Architecture

The build system implements a flexible configuration mechanism that enables conditional compilation of platform-specific features and commands through CMake options and preprocessor definitions.

### Conditional Compilation Strategy

```mermaid
graph TB
    subgraph "CMake Configuration"
        CMakeOptions["`CMake Build Options
        GH-oem-commands
        BF3-OEM-COMMANDS
        SPECTRE-OEM-COMMANDS
        cpu-diag-enable`"]
    end
    
    subgraph "Library Selection Logic"
        FlagLibSources["`flag_library_sources
        Platform-Specific Sources`"]
        CommonLibSources["`common_library_sources
        Shared Infrastructure`"]
    end
    
    subgraph "Compilation Targets"
        GraceTarget["`Grace Platform
        Grace/src/ghoemcommands.cpp
        Grace/src/sbmr-bootprogress.cpp`"]
        BFTarget["`Bluefield Platform
        src/BF/oemcommands.cpp
        src/BF/chassiscommands.cpp`"]
        SpectreTarget["`Spectre Platform
        src/BF/spectre/oemcommands.cpp
        Command Rejection Layer`"]
        CommonTarget["`Common Infrastructure
        src/oemcommands.cpp
        src/storagecommands.cpp
        src/sensorcommands.cpp`"]
    end
    
    subgraph "Output Library"
        ZnvIpmiOemCmds["`libznvipmioemcmds.so
        IPMI Provider Library`"]
    end
    
    CMakeOptions --> FlagLibSources
    CMakeOptions --> CommonLibSources
    
    FlagLibSources --> GraceTarget
    FlagLibSources --> BFTarget
    FlagLibSources --> SpectreTarget
    CommonLibSources --> CommonTarget
    
    GraceTarget --> ZnvIpmiOemCmds
    BFTarget --> ZnvIpmiOemCmds
    SpectreTarget --> ZnvIpmiOemCmds
    CommonTarget --> ZnvIpmiOemCmds
```

**Sources:** [CMakeLists.txt:120-150](), [CMakeLists.txt:185-189](), [CMakeLists.txt:195-197]()

### Feature Enablement Matrix

| CMake Option | Preprocessor Define | Affected Files | Purpose |
|--------------|-------------------|----------------|---------|
| `GH-oem-commands` | N/A | `Grace/src/ghoemcommands.cpp` | Enable Grace platform support |
| `BF3-OEM-COMMANDS` | `BF3_OEM_COMMANDS` | `src/BF/oemcommands.cpp` | Enable BF3 platform features |
| `SPECTRE-OEM-COMMANDS` | N/A | `src/BF/spectre/oemcommands.cpp` | Enable Spectre rejection handlers |
| `cpu-diag-enable` | `CPU_DIAG_ENABLE` | `Grace/src/ghoemcommands.cpp` | Enable CPU diagnostic commands |
| `gb200nvl-oem-commands` | `GB200NVL_OEM_COMMANDS` | Multiple files | Enable GB200NVL specific features |

**Sources:** [CMakeLists.txt:22-24](), [CMakeLists.txt:126-148](), [CMakeLists.txt:178-183]()

---

