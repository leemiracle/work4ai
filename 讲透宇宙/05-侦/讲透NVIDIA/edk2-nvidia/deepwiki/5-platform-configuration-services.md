<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/edk2-nvidia · page 5 Platform Configuration Services · fetched 2026-10-26 -->

# Platform Configuration Services

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Silicon/NVIDIA/Drivers/AndroidBootDxe/AndroidBootDxe.c](Silicon/NVIDIA/Drivers/AndroidBootDxe/AndroidBootDxe.c)
- [Silicon/NVIDIA/Drivers/AndroidBootDxe/AndroidBootDxe.h](Silicon/NVIDIA/Drivers/AndroidBootDxe/AndroidBootDxe.h)
- [Silicon/NVIDIA/Drivers/AndroidBootDxe/AndroidBootDxe.inf](Silicon/NVIDIA/Drivers/AndroidBootDxe/AndroidBootDxe.inf)
- [Silicon/NVIDIA/Drivers/AndroidBootDxe/UnitTest/AndroidBootDxeUnitTest.inf](Silicon/NVIDIA/Drivers/AndroidBootDxe/UnitTest/AndroidBootDxeUnitTest.inf)
- [Silicon/NVIDIA/Drivers/AndroidBootDxe/UnitTest/BootImgHeaderUnitTests.c](Silicon/NVIDIA/Drivers/AndroidBootDxe/UnitTest/BootImgHeaderUnitTests.c)
- [Silicon/NVIDIA/Drivers/NvidiaConfigDxe/NvidiaConfigDxe.c](Silicon/NVIDIA/Drivers/NvidiaConfigDxe/NvidiaConfigDxe.c)
- [Silicon/NVIDIA/Drivers/NvidiaConfigDxe/NvidiaConfigDxe.inf](Silicon/NVIDIA/Drivers/NvidiaConfigDxe/NvidiaConfigDxe.inf)
- [Silicon/NVIDIA/Drivers/NvidiaConfigDxe/NvidiaConfigHii.h](Silicon/NVIDIA/Drivers/NvidiaConfigDxe/NvidiaConfigHii.h)
- [Silicon/NVIDIA/Drivers/NvidiaConfigDxe/NvidiaConfigHii.uni](Silicon/NVIDIA/Drivers/NvidiaConfigDxe/NvidiaConfigHii.uni)
- [Silicon/NVIDIA/Drivers/NvidiaConfigDxe/NvidiaConfigHii.vfr](Silicon/NVIDIA/Drivers/NvidiaConfigDxe/NvidiaConfigHii.vfr)
- [Silicon/NVIDIA/Drivers/NvidiaConfigDxe/NvidiaConfigHiiMap.uni](Silicon/NVIDIA/Drivers/NvidiaConfigDxe/NvidiaConfigHiiMap.uni)
- [Silicon/NVIDIA/Drivers/TegraPlatformBootManager/TegraPlatformBootManagerDxe.c](Silicon/NVIDIA/Drivers/TegraPlatformBootManager/TegraPlatformBootManagerDxe.c)
- [Silicon/NVIDIA/Drivers/TegraPlatformBootManager/TegraPlatformBootManagerDxe.inf](Silicon/NVIDIA/Drivers/TegraPlatformBootManager/TegraPlatformBootManagerDxe.inf)
- [Silicon/NVIDIA/Include/AndroidBootImgHeader.h](Silicon/NVIDIA/Include/AndroidBootImgHeader.h)
- [Silicon/NVIDIA/Include/NVIDIAConfiguration.h](Silicon/NVIDIA/Include/NVIDIAConfiguration.h)
- [Silicon/NVIDIA/Include/Protocol/KernelArgsProtocol.h](Silicon/NVIDIA/Include/Protocol/KernelArgsProtocol.h)
- [Silicon/NVIDIA/Include/Server/TH500/TH500MB1Configuration.h](Silicon/NVIDIA/Include/Server/TH500/TH500MB1Configuration.h)
- [Silicon/NVIDIA/Library/PlatformBootManagerLib/PlatformBm.c](Silicon/NVIDIA/Library/PlatformBootManagerLib/PlatformBm.c)
- [Silicon/NVIDIA/Library/PlatformBootManagerLib/PlatformBm.h](Silicon/NVIDIA/Library/PlatformBootManagerLib/PlatformBm.h)
- [Silicon/NVIDIA/Library/PlatformBootManagerLib/PlatformBootManagerLib.inf](Silicon/NVIDIA/Library/PlatformBootManagerLib/PlatformBootManagerLib.inf)
- [Silicon/NVIDIA/NVIDIA.dec](Silicon/NVIDIA/NVIDIA.dec)

</details>



## Purpose and Scope

Platform Configuration Services provide user-facing interfaces for configuring NVIDIA Tegra UEFI firmware behavior. This includes the BIOS Setup menu (HII interface), UEFI variable storage and management, boot option control, and kernel command-line argument processing. The configuration system supports multiple platform variants (Jetson embedded platforms, TH500 server platforms, TegraVirt virtualization) and integrates with Redfish for remote management on server platforms.

For detailed information on specific subsystems:
- BIOS Setup and HII Interface implementation: see [5.1](#5.1)
- UEFI Variable Management architecture: see [5.2](#5.2)
- Boot Manager and Boot Options: see [5.3](#5.3)
- Boot path architecture including Android boot: see [Diagram 4](#) in the Overview
- Hardware driver configuration: see [6](#6)

## Configuration System Architecture

The platform configuration system consists of three main layers:

```mermaid
graph TB
    subgraph "User Interface Layer"
        HII["HII Forms<br/>NvidiaConfigDxe<br/>Forms: PCIe, Boot, TH500, L4T, Debug"]
        REDFISH["Redfish Interface<br/>x-UEFI-redfish-Bios.v1_2_0<br/>Remote management"]
    end
    
    subgraph "Configuration Management Layer"
        CONFIG_DXE["NvidiaConfigDxe Driver<br/>NVIDIA_CONFIG_FORMSET_GUID<br/>EFI_HII_CONFIG_ACCESS_PROTOCOL"]
        BOOT_MGR["TegraPlatformBootManagerDxe<br/>PLATFORM_BOOT_MANAGER_PROTOCOL<br/>Boot option filtering"]
        KERNEL_ARGS["Kernel Args Management<br/>NVIDIA_KERNEL_ARGS_PROTOCOL<br/>UpdateKernelArgs()"]
        
        CONFIG_DXE -->|"Processes user input"| BOOT_MGR
        CONFIG_DXE -->|"Updates"| KERNEL_ARGS
    end
    
    subgraph "Storage Layer"
        NVRAM["UEFI Variables<br/>gNVIDIAPublicVariableGuid<br/>gNVIDIATokenSpaceGuid"]
        MB1_CONFIG["TH500 MB1 Configuration<br/>TH500_MB1_CONFIGURATION<br/>TEGRABL_EARLY_BOOT_VARS"]
        PCD["Platform Configuration Database<br/>PCDs<br/>Build-time defaults"]
        
        CONFIG_DXE -->|"SetVariable()"| NVRAM
        CONFIG_DXE -->|"MM Communication"| MB1_CONFIG
        BOOT_MGR -->|"GetVariable()"| NVRAM
    end
    
    subgraph "Platform Services"
        ANDROID["AndroidBootDxe<br/>ANDROID_BOOT_PRIVATE_DATA<br/>LoadFile protocol"]
        PLATFORM_LIB["PlatformBootManagerLib<br/>Platform-specific boot logic<br/>Device enumeration"]
    end
    
    HII -->|"User changes"| CONFIG_DXE
    REDFISH -->|"REST API"| CONFIG_DXE
    
    BOOT_MGR --> ANDROID
    BOOT_MGR --> PLATFORM_LIB
    KERNEL_ARGS --> ANDROID
    
    NVRAM -.->|"Persistent storage"| PLATFORM_LIB
    
    style CONFIG_DXE fill:#f9f9f9,stroke:#333,stroke-width:2px
    style BOOT_MGR fill:#f9f9f9,stroke:#333,stroke-width:2px
    style NVRAM fill:#e8e8e8,stroke:#333,stroke-width:2px
```

**Configuration System Architecture**

The system is organized into three distinct layers:

1. **User Interface Layer**: Provides HII forms (BIOS Setup menu) and Redfish REST API for remote management
2. **Configuration Management Layer**: Processes configuration changes and manages boot behavior
3. **Storage Layer**: Persists configuration data in UEFI variables, MB1 configuration structures, and PCDs

Sources: [Silicon/NVIDIA/Drivers/NvidiaConfigDxe/NvidiaConfigDxe.c:1-100](), [Silicon/NVIDIA/Drivers/TegraPlatformBootManager/TegraPlatformBootManagerDxe.c:1-50](), [Silicon/NVIDIA/Drivers/NvidiaConfigDxe/NvidiaConfigHii.h:1-82]()

## Configuration Categories

The BIOS Setup interface organizes configuration options into multiple categories:

| Form ID | Category | Purpose | Key Variables |
|---------|----------|---------|---------------|
| `NVIDIA_CONFIG_FORM_ID` (0x0001) | Main Configuration | Entry point, serial port config, quick boot | `SerialPortConfig`, `QuickBootEnabled` |
| `PCIE_CONFIGURATION_FORM_ID` (0x0002) | PCIe Configuration | PCIe enablement, ACPI table control | `EnablePcieInOS`, `PCIeResourceConfig` |
| `BOOT_CONFIGURATION_FORM_ID` (0x0003) | Boot Configuration | Boot hierarchy, IPMI network boot, UEFI shell | `NewDeviceHierarchy`, `IpmiNetworkBootMode` |
| `L4T_CONFIGURATION_FORM_ID` (0x0004) | L4T Configuration | Linux for Tegra boot modes | `L4TDefaultBootMode`, `BoardRecoveryBoot` |
| `TH500_CONFIGURATION_FORM_ID` (0x0005) | SoC Configuration | TH500 server-specific settings | Socket configs, UPHY, MPAM |
| `DEBUG_CONFIGURATION_FORM_ID` (0x0032) | Debug Configuration | Debug output, UART baud rate | `UefiDebugLogLevel`, `UartBaudRate` |
| `MEMORY_TEST_FORM_ID` (0x0034) | Memory Test | Memory testing configuration | `MemoryTestControl` |
| `BMC_CONFIGURATION_FORM_ID` (0x003B) | BMC Configuration | Baseboard Management Controller | BMC credentials, factory reset |

Each form ID corresponds to a specific VFR form definition and set of configuration variables.

Sources: [Silicon/NVIDIA/Drivers/NvidiaConfigDxe/NvidiaConfigHii.h:23-81](), [Silicon/NVIDIA/Drivers/NvidiaConfigDxe/NvidiaConfigHii.vfr:152-200]()

## Configuration Data Flow

```mermaid
graph LR
    subgraph "User Input"
        USER["User<br/>BIOS Setup Menu"]
        REDFISH_CLIENT["Redfish Client<br/>Remote Management"]
    end
    
    subgraph "HII Processing"
        CALLBACK["RouteConfig()<br/>ExtractConfig()<br/>Callback()"]
        VALIDATION["Validate Input<br/>Check ranges<br/>Platform constraints"]
    end
    
    subgraph "Variable Update"
        SET_VAR["SetVariable()<br/>OS_CONFIG_VAR_ATTRIBUTES<br/>UEFI_CONFIG_VAR_ATTRIBUTES"]
        MM_COMM["MM Communication<br/>Update MB1 config<br/>gEfiMmCommunication2ProtocolGuid"]
    end
    
    subgraph "Platform Action"
        RESET["System Reset<br/>RESET_REQUIRED flag<br/>Apply changes"]
        RUNTIME["Runtime Update<br/>No reset needed<br/>Immediate effect"]
    end
    
    USER --> CALLBACK
    REDFISH_CLIENT --> CALLBACK
    
    CALLBACK --> VALIDATION
    VALIDATION -->|"Valid"| SET_VAR
    VALIDATION -->|"Invalid"| USER
    
    SET_VAR -->|"TH500 MB1 config"| MM_COMM
    SET_VAR -->|"NVRAM variables"| RUNTIME
    
    MM_COMM --> RESET
    
    style CALLBACK fill:#f9f9f9,stroke:#333,stroke-width:2px
    style SET_VAR fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Configuration Data Flow**

The configuration data flows from user input through HII processing to variable storage and platform actions:

1. **User Input**: Changes from BIOS Setup menu or Redfish API
2. **HII Processing**: `RouteConfig()` and `Callback()` functions in `NvidiaConfigDxe` validate and process changes
3. **Variable Update**: Variables are stored with appropriate attributes (`EFI_VARIABLE_NON_VOLATILE`, `EFI_VARIABLE_RUNTIME_ACCESS`)
4. **Platform Action**: Some changes require system reset, others take effect immediately

Sources: [Silicon/NVIDIA/Drivers/NvidiaConfigDxe/NvidiaConfigDxe.c:800-1200](), [Silicon/NVIDIA/Include/NVIDIAConfiguration.h:1-100]()

## UEFI Variable Organization

Configuration data is stored in UEFI variables organized by GUID namespace:

```mermaid
graph TB
    subgraph "gNVIDIAPublicVariableGuid"
        PUBLIC["Public Variables<br/>0x781e084c-a330-417c-b678-38e696380cb9"]
        
        QUICK_BOOT["QuickBootEnabled<br/>NVIDIA_QUICK_BOOT_ENABLED<br/>Enable/disable full enumeration"]
        NEW_DEV["NewDeviceHierarchy<br/>NVIDIA_NEW_DEVICE_HIERARCHY<br/>Top or bottom of boot order"]
        KERNEL_CMD["KernelCommandLine<br/>NVIDIA_KERNEL_COMMAND_LINE<br/>Append to kernel args"]
        OS_STATUS_A["RootfsStatusSlotA<br/>NVIDIA_OS_STATUS_A<br/>Chain A boot status"]
        OS_STATUS_B["RootfsStatusSlotB<br/>NVIDIA_OS_STATUS_B<br/>Chain B boot status"]
        L4T_BOOT["L4TDefaultBootMode<br/>NVIDIA_L4T_BOOT_MODE<br/>Grub/Direct/BootImg/Recovery"]
        
        PUBLIC --> QUICK_BOOT
        PUBLIC --> NEW_DEV
        PUBLIC --> KERNEL_CMD
        PUBLIC --> OS_STATUS_A
        PUBLIC --> OS_STATUS_B
        PUBLIC --> L4T_BOOT
    end
    
    subgraph "gNVIDIATokenSpaceGuid"
        TOKEN["Token Space Variables<br/>0xed3374ef-767b-42fa-af70-db520a392822"]
        
        PCIE_EN["EnablePcieInOS<br/>NvidiaPcieEnableVariable<br/>PCIe ACPI exposure"]
        SERIAL["SerialPortConfig<br/>NVIDIA_SERIAL_PORT_CONFIG<br/>SPCR/DBG2/Disabled"]
        REDFISH["RedfishHostInterface<br/>NVIDIA_REDFISH_HOST_INTERFACE_ENABLED<br/>Enable Redfish"]
        
        TOKEN --> PCIE_EN
        TOKEN --> SERIAL
        TOKEN --> REDFISH
    end
    
    subgraph "Variable Attributes"
        PERSISTENT["Non-Volatile<br/>EFI_VARIABLE_NON_VOLATILE<br/>Survives reset"]
        BOOTSERVICE["Boot Service Access<br/>EFI_VARIABLE_BOOTSERVICE_ACCESS<br/>DXE phase only"]
        RUNTIME["Runtime Access<br/>EFI_VARIABLE_RUNTIME_ACCESS<br/>OS can access"]
    end
    
    QUICK_BOOT -.->|"Attributes"| PERSISTENT
    QUICK_BOOT -.->|"Attributes"| BOOTSERVICE
    
    OS_STATUS_A -.->|"Attributes"| PERSISTENT
    OS_STATUS_A -.->|"Attributes"| BOOTSERVICE
    OS_STATUS_A -.->|"Attributes"| RUNTIME
    
    style PUBLIC fill:#e8e8e8,stroke:#333,stroke-width:2px
    style TOKEN fill:#e8e8e8,stroke:#333,stroke-width:2px
```

**UEFI Variable Organization**

Variables are organized by GUID namespace with appropriate access attributes:

- **gNVIDIAPublicVariableGuid**: User-facing configuration (boot mode, kernel args, OS status)
- **gNVIDIATokenSpaceGuid**: Platform-specific settings (PCIe, serial port, Redfish)

Variable attributes control persistence and access:
- **Non-Volatile**: Survives resets and power cycles
- **Boot Service Access**: Accessible during DXE phase
- **Runtime Access**: OS can read/write after ExitBootServices

Sources: [Silicon/NVIDIA/NVIDIA.dec:36-37](), [Silicon/NVIDIA/Drivers/NvidiaConfigDxe/NvidiaConfigHii.vfr:28-146](), [Silicon/NVIDIA/Drivers/NvidiaConfigDxe/NvidiaConfigDxe.c:59-60]()

## Boot Manager Integration

The boot manager integrates configuration services with boot option processing:

```mermaid
graph TB
    subgraph "Boot Manager Protocol"
        BM_PROTO["PLATFORM_BOOT_MANAGER_PROTOCOL<br/>TegraPlatformBootManagerDxe"]
        FILTER["FilterBootOptions()<br/>IsValidLoadOption()<br/>Boot option filtering"]
        KERNEL_UPDATE["UpdateKernelArgs()<br/>Aggregate kernel cmdline<br/>From multiple sources"]
    end
    
    subgraph "Boot Option Sources"
        NVRAM_OPTS["NVRAM Boot Options<br/>BootXXXX variables<br/>Auto-enumerated devices"]
        ACTIVE_PART["Active Partition<br/>GetActivePartitionName()<br/>A/B slot selection"]
        RECOVERY["Recovery Mode<br/>MISC_CMD_TYPE_RECOVERY<br/>From misc partition"]
    end
    
    subgraph "Kernel Args Aggregation"
        PLATFORM_ARGS["Platform Args<br/>NVIDIA_PLATFORM_KERNEL_ARGS_PROTOCOL<br/>Platform-specific defaults"]
        USER_ARGS["User Args<br/>KernelCommandLine variable<br/>User append string"]
        DTB_ARGS["DTB Args<br/>chosen/bootargs<br/>From device tree"]
        BOOTIMG_ARGS["Boot.img Args<br/>ANDROID_BOOTIMG_KERNEL_ARGS<br/>From Android boot image"]
        
        FINAL_ARGS["Final Kernel Args<br/>Concatenated string<br/>Passed to LoadFile protocol"]
        
        PLATFORM_ARGS --> FINAL_ARGS
        USER_ARGS --> FINAL_ARGS
        DTB_ARGS --> FINAL_ARGS
        BOOTIMG_ARGS --> FINAL_ARGS
    end
    
    subgraph "LoadFile Protocol"
        ANDROID_BOOT["AndroidBootDxe<br/>ANDROID_BOOT_PRIVATE_DATA<br/>gEfiLoadFileProtocolGuid"]
        KERNEL_ARGS_PROTO["NVIDIA_KERNEL_ARGS_PROTOCOL<br/>UpdateKernelArgs()<br/>gNVIDIALoadfileKernelArgsProtocol"]
        
        ANDROID_BOOT -->|"Implements"| KERNEL_ARGS_PROTO
    end
    
    BM_PROTO --> FILTER
    BM_PROTO --> KERNEL_UPDATE
    
    NVRAM_OPTS --> FILTER
    ACTIVE_PART --> FILTER
    RECOVERY --> FILTER
    
    FILTER -->|"Valid options"| ANDROID_BOOT
    
    KERNEL_UPDATE --> PLATFORM_ARGS
    KERNEL_UPDATE --> USER_ARGS
    
    FINAL_ARGS --> KERNEL_ARGS_PROTO
    
    style BM_PROTO fill:#f9f9f9,stroke:#333,stroke-width:2px
    style FINAL_ARGS fill:#f9f9f9,stroke:#333,stroke-width:2px
    style ANDROID_BOOT fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Boot Manager Integration**

The boot manager coordinates multiple configuration sources:

1. **Boot Option Filtering**: `IsValidLoadOption()` filters boot options based on device type (eMMC, UFS, PCIe NIC) and configuration
2. **Active Partition Selection**: Determines which partition (A/B slot) to boot based on `GetActivePartitionName()`
3. **Kernel Args Aggregation**: Combines args from platform defaults, user configuration, DTB, and boot.img
4. **LoadFile Protocol**: `AndroidBootDxe` implements `NVIDIA_KERNEL_ARGS_PROTOCOL` to provide final kernel command line

Sources: [Silicon/NVIDIA/Drivers/TegraPlatformBootManager/TegraPlatformBootManagerDxe.c:70-150](), [Silicon/NVIDIA/Drivers/AndroidBootDxe/AndroidBootDxe.c:108-165](), [Silicon/NVIDIA/Library/PlatformBootManagerLib/PlatformBm.c:1-100]()

## TH500 Server Configuration

TH500 server platforms have additional configuration stored in MB1 early boot variables:

```mermaid
graph TB
    subgraph "TH500_MB1_CONFIGURATION Structure"
        HEADER["TEGRABL_EARLY_BOOT_VARS_HEADER<br/>MajorVersion, MinorVersion<br/>0.22"]
        
        FEATURES["TEGRABL_FEATURE_DATA<br/>64-bit feature flags<br/>EgmEnable, SpreadSpecEnable, etc."]
        
        HV_MEM["Hypervisor Memory<br/>HvRsvdMemSize<br/>HvMinEgmSize<br/>HvVirtUefiSize"]
        
        UPHY["TEGRABL_MB1BCT_UPHY_CONFIG<br/>UphyConfig[4][6]<br/>Per-socket UPHY lane config"]
        
        PCIE["TEGRABL_MB1BCT_PCIE_CONFIG<br/>PcieConfig[4][10]<br/>MaxSpeed, MaxWidth, ASPM"]
        
        CORES["Active Cores<br/>ActiveCores[4]<br/>Per-socket core count"]
        
        MPAM["TEGRABL_MPAM_PARTID_CONFIG<br/>MpamConfig[5]<br/>MPAM partition IDs"]
    end
    
    subgraph "MM Communication"
        MM_COMM["MM Communication<br/>gEfiMmCommunication2ProtocolGuid"]
        MM_HANDLER["MM Handler<br/>gNVIDIAMmMb1RecordGuid<br/>Update MB1 record"]
    end
    
    subgraph "NvidiaConfigDxe Updates"
        SOCKET_FORMS["Socket Config Forms<br/>TH500_SOCKET0_CONFIGURATION_FORM_ID<br/>UPHY, PCIe settings"]
        MPAM_FORMS["MPAM Config Forms<br/>TH500_MPAM_CONFIGURATION_FORM_ID<br/>MPAM40-44 partitions"]
        FEATURE_TOGGLES["Feature Toggles<br/>EGM, TPM, GPU SMMU bypass<br/>Channel sparing, ECC algorithm"]
    end
    
    SOCKET_FORMS --> UPHY
    SOCKET_FORMS --> PCIE
    MPAM_FORMS --> MPAM
    FEATURE_TOGGLES --> FEATURES
    FEATURE_TOGGLES --> HV_MEM
    FEATURE_TOGGLES --> CORES
    
    UPHY --> MM_COMM
    PCIE --> MM_COMM
    MPAM --> MM_COMM
    FEATURES --> MM_COMM
    
    MM_COMM --> MM_HANDLER
    
    style FEATURES fill:#f9f9f9,stroke:#333,stroke-width:2px
    style MM_COMM fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**TH500 Server Configuration**

TH500 platforms store extensive configuration in the `TH500_MB1_CONFIGURATION` structure:

- **Feature Flags**: EGM, spread spectrum, TPM, GPU SMMU bypass, UART baud rate, ECC algorithm
- **UPHY Configuration**: PCIe lane bifurcation for 4 sockets × 6 UPHY blocks
- **PCIe Configuration**: Speed, width, ASPM settings for 4 sockets × 10 controllers
- **MPAM Configuration**: Memory partitioning and allocation for 5 partition IDs
- **Core Configuration**: Active core count per socket for power/performance tuning

Configuration updates are sent to MM (Management Mode) via `gEfiMmCommunication2ProtocolGuid` and handled by the MM MB1 record handler.

Sources: [Silicon/NVIDIA/Include/Server/TH500/TH500MB1Configuration.h:9-150](), [Silicon/NVIDIA/Drivers/NvidiaConfigDxe/NvidiaConfigDxe.c:2000-2500](), [Silicon/NVIDIA/Drivers/NvidiaConfigDxe/NvidiaConfigHii.h:27-80]()

## Key Code Components

| Component | File Path | Primary Functions |
|-----------|-----------|-------------------|
| **NvidiaConfigDxe** | [Silicon/NVIDIA/Drivers/NvidiaConfigDxe/NvidiaConfigDxe.c]() | `NvidiaConfigDxeInitialize()`, `RouteConfig()`, `Callback()` |
| **HII Forms** | [Silicon/NVIDIA/Drivers/NvidiaConfigDxe/NvidiaConfigHii.vfr]() | VFR form definitions for all configuration categories |
| **TegraPlatformBootManager** | [Silicon/NVIDIA/Drivers/TegraPlatformBootManager/TegraPlatformBootManagerDxe.c]() | `PlatformBootManagerEntryPoint()`, `FilterBootOptions()`, `IsValidLoadOption()` |
| **AndroidBootDxe** | [Silicon/NVIDIA/Drivers/AndroidBootDxe/AndroidBootDxe.c]() | `AndroidBootDxeDriverEntryPoint()`, `UpdateKernelArgs()`, `AndroidBootLoadFile()` |
| **PlatformBootManagerLib** | [Silicon/NVIDIA/Library/PlatformBootManagerLib/PlatformBm.c]() | `PlatformBootManagerBeforeConsole()`, `PlatformBootManagerAfterConsole()` |
| **Configuration Headers** | [Silicon/NVIDIA/Include/NVIDIAConfiguration.h]() | Configuration data structure definitions |
| **TH500 MB1 Config** | [Silicon/NVIDIA/Include/Server/TH500/TH500MB1Configuration.h]() | `TH500_MB1_CONFIGURATION`, `TEGRABL_FEATURE_DATA` |

Sources: All file paths listed in the table

## Configuration Variable Attributes

Variable attributes control persistence, access, and security:

```c
// Non-volatile variables that persist across resets
#define OS_CONFIG_VAR_ATTRIBUTES (EFI_VARIABLE_BOOTSERVICE_ACCESS | \
                                  EFI_VARIABLE_NON_VOLATILE | \
                                  EFI_VARIABLE_RUNTIME_ACCESS)

// Volatile variables that reset to defaults
#define UEFI_CONFIG_VAR_ATTRIBUTES (EFI_VARIABLE_BOOTSERVICE_ACCESS | \
                                    EFI_VARIABLE_RUNTIME_ACCESS)
```

Common attribute combinations:
- **Boot Service + Non-Volatile**: Configuration that persists but OS cannot modify
- **Boot Service + Non-Volatile + Runtime**: Configuration accessible to OS at runtime
- **Boot Service only**: Volatile configuration for current boot

Sources: [Silicon/NVIDIA/Drivers/NvidiaConfigDxe/NvidiaConfigDxe.c:59-60]()

---

