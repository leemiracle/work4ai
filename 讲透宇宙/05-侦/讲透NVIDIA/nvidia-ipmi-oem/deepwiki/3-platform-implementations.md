<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-ipmi-oem · page 3 Platform Implementations · fetched 2026-10-26 -->

# Platform Implementations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Grace/src/ghoemcommands.cpp](Grace/src/ghoemcommands.cpp)
- [include/oemcommandsBF.hpp](include/oemcommandsBF.hpp)
- [src/BF/BF2/oemcommands.cpp](src/BF/BF2/oemcommands.cpp)
- [src/BF/oemcommands.cpp](src/BF/oemcommands.cpp)
- [src/BF/spectre/oemcommands.cpp](src/BF/spectre/oemcommands.cpp)

</details>



This document covers the platform-specific implementations within the NVIDIA IPMI OEM Commands library, detailing how different NVIDIA hardware platforms are supported through a graduated feature model. For information about the overall system architecture and command processing flow, see [System Architecture](#2). For details about common infrastructure shared across platforms, see [Common Infrastructure](#4).

## Platform Differentiation Strategy

The codebase implements a platform-centric design that provides different levels of OEM command support based on the target hardware platform. This graduated support model allows the same codebase to serve multiple NVIDIA platforms while optimizing functionality for each platform's specific capabilities and requirements.

## Platform Support Levels

```mermaid
graph TD
    subgraph "Platform Support Hierarchy"
        BF["Bluefield Platform<br/>src/BF/oemcommands.cpp<br/>Full Feature Set"]
        Grace["Grace Platform<br/>Grace/src/ghoemcommands.cpp<br/>GPU-Focused Features"]
        BF2["BF2 Platform<br/>src/BF/BF2/oemcommands.cpp<br/>Limited Support"]
        Spectre["Spectre Platform<br/>src/BF/spectre/oemcommands.cpp<br/>Disabled Commands"]
    end
    
    subgraph "Feature Categories"
        LiveFish["Live Fish Mode<br/>ipmiEnterLiveFish<br/>ipmiExitLiveFish"]
        NIC["NIC Management<br/>SmartNIC Mode<br/>Host Access Control"]
        Power["Power Management<br/>Power Capping<br/>Capacity Control"]
        GPU["GPU Management<br/>SMBPBI Passthrough<br/>Device Control"]
        Bootstrap["Bootstrap Accounts<br/>User Management<br/>UEFI Integration"]
        TorSwitch["TorSwitch Control<br/>Port Mode Management<br/>Reset Control"]
    end
    
    BF --> LiveFish
    BF --> NIC
    BF --> Power
    BF --> Bootstrap
    BF --> TorSwitch
    
    Grace --> GPU
    Grace --> Power
    Grace --> Bootstrap
    
    BF2 -.-> |"Returns ccResponseError"| LiveFish
    BF2 -.-> |"Returns ccResponseError"| NIC
    BF2 -.-> |"Returns ccResponseError"| Power
    
    Spectre -.-> |"Returns ccInvalidCommand"| LiveFish
    Spectre -.-> |"Returns ccInvalidCommand"| NIC
    Spectre -.-> |"Returns ccInvalidCommand"| Power
```

**Sources:** [src/BF/oemcommands.cpp:1-100](), [Grace/src/ghoemcommands.cpp:1-100](), [src/BF/BF2/oemcommands.cpp:66-110](), [src/BF/spectre/oemcommands.cpp:58-110]()

## Platform Command Implementation Matrix

```mermaid
graph LR
    subgraph "Command Registration Pattern"
        Reg["ipmi::registerHandler<br/>ipmi::registerGroupHandler"]
        NetFn["Network Function<br/>netFnOemGlobal<br/>netFnOemNV<br/>netGroupExt"]
        Cmd["Command Codes<br/>cmdEnterLiveFish<br/>cmdPowerCapEnabledGet<br/>cmdSMBPBIPassthrough"]
        Handler["Platform Handlers<br/>Platform-specific functions"]
    end
    
    subgraph "Bluefield Handlers"
        BF_Enter["ipmiEnterLiveFish"]
        BF_Power["ipmicmdPowerCapEnabledGet"]
        BF_NIC["ipmicmdNicGetSmartnicMode"]
        BF_Bootstrap["ipmiGetBootStrapAccount"]
    end
    
    subgraph "Grace Handlers"
        Grace_GPU["ipmiSMBPBIPassthroughCmd"]
        Grace_Fan["ipmiSetFanZonePWMDuty"]
        Grace_LED["ipmiOemGetSSDLed"]
        Grace_SEL["ipmiGetSELPolicy"]
    end
    
    subgraph "BF2 Handlers"
        BF2_Reject["ipmicmdEnterLiveFishBF2<br/>nicManagerBF2NA<br/>ipmicmdPowerCapGet"]
    end
    
    subgraph "Spectre Handlers"
        Spectre_Reject["ipmicmdRejectNoParamSpectre<br/>ipmicmdRejectOneParamSpectre<br/>ipmicmdRejectTwoParamSpectre"]
    end
    
    Reg --> NetFn
    NetFn --> Cmd
    Cmd --> Handler
    
    Handler --> BF_Enter
    Handler --> BF_Power
    Handler --> BF_NIC
    Handler --> BF_Bootstrap
    
    Handler --> Grace_GPU
    Handler --> Grace_Fan
    Handler --> Grace_LED
    Handler --> Grace_SEL
    
    Handler --> BF2_Reject
    Handler --> Spectre_Reject
```

**Sources:** [src/BF/oemcommands.cpp:2800-3000](), [Grace/src/ghoemcommands.cpp:1800-2000](), [src/BF/BF2/oemcommands.cpp:111-206](), [src/BF/spectre/oemcommands.cpp:112-298]()

## Platform-Specific Feature Sets

### Bluefield Platform

The Bluefield platform provides the most comprehensive OEM command support, implementing full DPU (Data Processing Unit) management capabilities.

**Key Features:**
- **Live Fish Mode**: `ipmiEnterLiveFish` and `ipmiExitLiveFish` functions for firmware recovery
- **NIC Management**: SmartNIC mode control, host access privileges, external host privileges
- **Power Capping**: Complete power management with min/max capacity and percentage controls  
- **Bootstrap Accounts**: UEFI boot account management with `NvBluefieldUefi0` and `NvBluefieldUefi1` accounts
- **TorSwitch Control**: Ethernet switch port mode management
- **DPU Reset Control**: Multiple reset options including SOC hard reset and ARM soft reset
- **Network Reprovisioning**: Golden image update capabilities

**Sources:** [src/BF/oemcommands.cpp:323-570](), [src/BF/oemcommands.cpp:924-1050](), [src/BF/oemcommands.cpp:1400-1600]()

### Grace Platform  

The Grace platform focuses on GPU and system management with specialized hardware control capabilities.

**Key Features:**
- **GPU Management**: SMBPBI passthrough commands via `ipmiSMBPBIPassthroughCmd` and `ipmiSMBPBIPassthroughExtendedCmd`
- **Fan Control**: PWM duty cycle control through `ipmiSetFanZonePWMDuty` and zone management
- **LED Control**: SSD LED management with `ipmiOemGetSSDLed` and `ipmiOemSetSSDLed`
- **SEL Policy**: System Event Log policy management with linear/circular modes
- **BIOS Integration**: Redfish hostname retrieval and USB device description
- **I2C Communication**: Direct I2C master read/write operations via `ipmiI2CMasterReadWrite`

**Sources:** [Grace/src/ghoemcommands.cpp:167-275](), [Grace/src/ghoemcommands.cpp:463-605](), [Grace/src/ghoemcommands.cpp:714-834]()

### Platform Variants

#### BF2 Platform (Limited Support)

The BF2 platform provides minimal OEM command support, with most commands returning error responses.

**Command Rejection Pattern:**
```cpp
ipmi::RspType<uint8_t> ipmicmdEnterLiveFishBF2()
{
    phosphor::logging::log<phosphor::logging::level::ERR>(
        "Enter LiveFish command is unsupported in Bluefield 2");
    return ipmi::response(ipmi::ccResponseError);
}
```

**Sources:** [src/BF/BF2/oemcommands.cpp:66-100](), [src/BF/BF2/oemcommands.cpp:80-107]()

#### Spectre Platform (Disabled Commands)

The Spectre platform completely disables OEM command functionality, returning `ccInvalidCommand` for all requests.

**Universal Rejection Pattern:**
```cpp
ipmi::RspType<uint8_t> ipmicmdRejectNoParamSpectre()
{
    phosphor::logging::log<phosphor::logging::level::ERR>(
        "Command is unsupported on Spectre");
    return ipmi::response(ipmi::ccInvalidCommand);
}
```

**Sources:** [src/BF/spectre/oemcommands.cpp:58-110]()

## Constructor-Based Registration

Each platform uses constructor functions with different priorities to ensure proper initialization order:

| Platform | Constructor Function | Priority |
|----------|---------------------|----------|
| Common | `registerNvOemCommonFunctions()` | 101 |
| Bluefield | `registerNvOemPlatformFunctions()` | 102 |
| BF2 | `registerNvOemPlatformFunctionsBF2()` | 103 |
| Spectre | `registerNvOemPlatformFunctionsSpectre()` | 103 |
| Grace | `registerNvOemFunctions()` | default |

**Sources:** [src/BF/oemcommands.cpp:229](), [src/BF/BF2/oemcommands.cpp:52](), [src/BF/spectre/oemcommands.cpp:52](), [Grace/src/ghoemcommands.cpp:132]()

## Hardware Abstraction Layer

```mermaid
graph TD
    subgraph "Platform Hardware Interfaces"
        BF_HW["Bluefield Hardware<br/>DPU Control<br/>Ethernet Switch<br/>RShim Service"]
        Grace_HW["Grace Hardware<br/>GPU SMBPBI<br/>Fan Controllers<br/>FPGA MID"]
        
        I2C_Layer["I2C Transaction Layer<br/>i2cTransaction()<br/>i2cWriteRead()"]
        GPIO_Layer["GPIO Control<br/>devmem commands<br/>Register manipulation"]
        Service_Layer["System Service Layer<br/>D-Bus Integration<br/>Systemd Control"]
    end
    
    subgraph "Platform Addresses"
        BF_Addr["BF2: ethSwitchI2cBusBF2=0xe<br/>ethSwitchI2caddressBF2=0x5f<br/>cecI2cAddressBF2=0x55"]
        BF3_Addr["BF3: ethSwitchI2cBusBF3=10<br/>ethSwitchI2caddressBF3=0x5f<br/>cecI2cAddressBF3=0x52"]
        Grace_Addr["Grace: fpgaMidI2cBus<br/>fpgaI2cAddress<br/>fanZoneCtrlName0-4"]
    end
    
    BF_HW --> I2C_Layer
    BF_HW --> GPIO_Layer
    BF_HW --> Service_Layer
    
    Grace_HW --> I2C_Layer
    Grace_HW --> Service_Layer
    
    I2C_Layer --> BF_Addr
    I2C_Layer --> BF3_Addr
    I2C_Layer --> Grace_Addr
```

**Sources:** [include/oemcommandsBF.hpp:26-34](), [Grace/src/ghoemcommands.cpp:328-349](), [src/BF/oemcommands.cpp:372-393]()

---

