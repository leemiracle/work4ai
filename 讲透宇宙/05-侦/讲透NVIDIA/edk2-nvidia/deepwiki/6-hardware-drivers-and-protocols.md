<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/edk2-nvidia · page 6 Hardware Drivers and Protocols · fetched 2026-10-26 -->

# Hardware Drivers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Silicon/NVIDIA/Drivers/PciGenericControllerDxe/PcieGenericControllerDxe.c](Silicon/NVIDIA/Drivers/PciGenericControllerDxe/PcieGenericControllerDxe.c)
- [Silicon/NVIDIA/Drivers/PciGenericControllerDxe/PcieGenericControllerDxe.inf](Silicon/NVIDIA/Drivers/PciGenericControllerDxe/PcieGenericControllerDxe.inf)
- [Silicon/NVIDIA/Drivers/PciGenericControllerDxe/PcieGenericControllerPrivate.h](Silicon/NVIDIA/Drivers/PciGenericControllerDxe/PcieGenericControllerPrivate.h)
- [Silicon/NVIDIA/Drivers/PcieControllerDxe/PciPlatformDxe.c](Silicon/NVIDIA/Drivers/PcieControllerDxe/PciPlatformDxe.c)
- [Silicon/NVIDIA/Drivers/PcieControllerDxe/PcieConfigDxe.c](Silicon/NVIDIA/Drivers/PcieControllerDxe/PcieConfigDxe.c)
- [Silicon/NVIDIA/Drivers/PcieControllerDxe/PcieControllerConfigGPU.c](Silicon/NVIDIA/Drivers/PcieControllerDxe/PcieControllerConfigGPU.c)
- [Silicon/NVIDIA/Drivers/PcieControllerDxe/PcieControllerConfigGPU.h](Silicon/NVIDIA/Drivers/PcieControllerDxe/PcieControllerConfigGPU.h)
- [Silicon/NVIDIA/Drivers/PcieControllerDxe/PcieControllerDxe.c](Silicon/NVIDIA/Drivers/PcieControllerDxe/PcieControllerDxe.c)
- [Silicon/NVIDIA/Drivers/PcieControllerDxe/PcieControllerDxe.inf](Silicon/NVIDIA/Drivers/PcieControllerDxe/PcieControllerDxe.inf)
- [Silicon/NVIDIA/Drivers/PcieControllerDxe/PcieControllerPrivate.h](Silicon/NVIDIA/Drivers/PcieControllerDxe/PcieControllerPrivate.h)
- [Silicon/NVIDIA/Include/AcpiPowerMeter.h](Silicon/NVIDIA/Include/AcpiPowerMeter.h)
- [Silicon/NVIDIA/Include/Protocol/BpmpIpc.h](Silicon/NVIDIA/Include/Protocol/BpmpIpc.h)
- [Silicon/NVIDIA/Include/Protocol/PciRootBridgeConfigurationIo.h](Silicon/NVIDIA/Include/Protocol/PciRootBridgeConfigurationIo.h)
- [Silicon/NVIDIA/Include/Server/TH500/TH500Definitions.h](Silicon/NVIDIA/Include/Server/TH500/TH500Definitions.h)
- [Silicon/NVIDIA/Library/DeviceDiscoveryLib/DeviceDiscoveryLibPrivate.h](Silicon/NVIDIA/Library/DeviceDiscoveryLib/DeviceDiscoveryLibPrivate.h)
- [Silicon/NVIDIA/Library/PciHostBridgeLib/PciHostBridgeLib.c](Silicon/NVIDIA/Library/PciHostBridgeLib/PciHostBridgeLib.c)
- [Silicon/NVIDIA/Library/PciHostBridgeLib/PciHostBridgeLib.inf](Silicon/NVIDIA/Library/PciHostBridgeLib/PciHostBridgeLib.inf)

</details>



This document covers the hardware-specific UEFI drivers that manage PCIe controllers, memory management units (SMMUs), display controllers, and other platform hardware in the edk2-nvidia firmware. These drivers provide the fundamental hardware abstraction layer that enables device discovery, memory translation, and graphics output for NVIDIA Tegra platforms.

For information about platform resource discovery and device tree management, see [Hardware Discovery and Device Tree](#3.3). For boot management and operating system handoff, see [Boot and Operating System Support](#5).

## Hardware Driver Architecture

The hardware drivers follow a layered architecture where device discovery drivers locate and initialize hardware components, which then expose standardized UEFI protocols for use by higher-level services.

### Driver Architecture Overview

```mermaid
graph TB
    subgraph "Hardware Abstraction Layer"
        DeviceDiscovery["DeviceDiscoveryDriverLib<br/>Hardware Detection"]
        CompatMap["Compatibility Mapping<br/>Device Tree → GUID"]
        NonDiscov["NonDiscoverableDevice<br/>Protocol"]
    end
    
    subgraph "PCIe Subsystem"
        PcieDriver["PcieControllerDxe<br/>Main Driver"]
        PciePrivate["PCIE_CONTROLLER_PRIVATE<br/>Controller State"]
        PcieProtocol["NVIDIA_PCI_ROOT_BRIDGE_CONFIGURATION_IO_PROTOCOL<br/>Config Space Access"]
        PciPlatform["PciPlatformProtocol<br/>Platform Policies"]
    end
    
    subgraph "Memory Management (SMMU)"
        SmmuDriver["SmmuV3Dxe<br/>Controller Driver"]
        SmmuPrivate["SMMU_V3_CONTROLLER_PRIVATE_DATA<br/>Controller State"]
        SmmuProtocol["NVIDIA_SMMUV3_CONTROLLER_PROTOCOL<br/>Translation Control"]
        IoMmuDriver["SmmuDriverDxe<br/>IOMMU Protocol"]
        IoMmuProtocol["EDKII_IOMMU_PROTOCOL<br/>DMA Mapping"]
    end
    
    subgraph "Display Controllers"
        DisplayDriver["NvDisplayControllerDxe<br/>Platform Driver"]
        DisplayPrivate["NV_DISPLAY_CONTROLLER_PRIVATE<br/>Controller State"]
        DisplayT234["NvDisplayControllerT234<br/>Chip-specific Logic"]
        DisplayT264["NvDisplayControllerT264<br/>Chip-specific Logic"]
        GOP["Graphics Output Protocol<br/>Display Output"]
    end
    
    DeviceDiscovery --> CompatMap
    CompatMap --> NonDiscov
    
    NonDiscov --> PcieDriver
    PcieDriver --> PciePrivate
    PciePrivate --> PcieProtocol
    PcieDriver --> PciPlatform
    
    NonDiscov --> SmmuDriver
    SmmuDriver --> SmmuPrivate
    SmmuPrivate --> SmmuProtocol
    SmmuProtocol --> IoMmuDriver
    IoMmuDriver --> IoMmuProtocol
    
    NonDiscov --> DisplayDriver
    DisplayDriver --> DisplayPrivate
    DisplayDriver --> DisplayT234
    DisplayDriver --> DisplayT264
    DisplayT234 --> GOP
    DisplayT264 --> GOP
```

Sources: [Silicon/NVIDIA/Drivers/PcieControllerDxe/PcieControllerDxe.c:61-88](), [Silicon/NVIDIA/Drivers/SmmuV3Dxe/SmmuV3Dxe.c:25-32](), [Silicon/NVIDIA/Drivers/NvDisplayControllerDxe/NvDisplayControllerDxe.c:22-33]()

### Driver Initialization Flow

```mermaid
sequenceDiagram
    participant Platform as "Platform Resource Discovery"
    participant DevDisc as "Device Discovery Framework"
    participant PCIe as "PcieControllerDxe"
    participant SMMU as "SmmuV3Dxe"
    participant Display as "NvDisplayControllerDxe"
    participant Protocols as "Protocol Installation"
    
    Platform->>DevDisc: "Populate Device Tree Nodes"
    DevDisc->>PCIe: "DeviceDiscoveryNotify(DriverBindingStart)"
    PCIe->>PCIe: "InitializeController(Private, Handle)"
    PCIe->>Protocols: "Install PCI Root Bridge Configuration IO"
    
    DevDisc->>SMMU: "DeviceDiscoveryNotify(DriverBindingStart)"
    SMMU->>SMMU: "ConfigureSmmuV3ControllerSettings(Private)"
    SMMU->>SMMU: "SetupSmmuV3Cmdq(Private)"
    SMMU->>SMMU: "SetupSmmuV3StrTable(Private)"
    SMMU->>Protocols: "Install SMMUV3_CONTROLLER_PROTOCOL"
    
    DevDisc->>Display: "DeviceDiscoveryNotify(DriverBindingStart)"
    Display->>Display: "NvDisplayControllerStart(Handle, HwEnable, HwHandoff)"
    Display->>Display: "EnableHwT234/T264(Enable=TRUE)"
    Display->>Protocols: "Install Graphics Output Protocol"
    
    Note over PCIe,Display: "All drivers signal completion via protocol installation"
```

Sources: [Silicon/NVIDIA/Drivers/PcieControllerDxe/PcieControllerDxe.c:574-723](), [Silicon/NVIDIA/Drivers/SmmuV3Dxe/SmmuV3Dxe.c:394-458](), [Silicon/NVIDIA/Drivers/NvDisplayControllerDxe/NvDisplayController.c:519-543]()

## PCIe Controllers and Interconnect

The PCIe controller driver (`PcieControllerDxe`) manages PCIe root complex controllers on NVIDIA Tegra platforms, providing configuration space access, link training, error handling, and power management.

### PCIe Controller Components

```mermaid
graph TB
    subgraph "PCIe Controller Driver Structure"
        PcieMain["PcieControllerDxe.c<br/>Main Driver Entry"]
        PciePrivate["PCIE_CONTROLLER_PRIVATE<br/>Controller Instance Data"]
        PcieConfig["PcieConfigurationAccess()<br/>Config Space R/W"]
        LinkTrain["InitializeController()<br/>Link Training"]
        ErrorHandle["PcieEnableErrorReporting()<br/>AER/DPC Setup"]
    end
    
    subgraph "Hardware Registers"
        XAL["XAL Registers<br/>Address Translation"]
        XTL["XTL Registers<br/>Transaction Layer"]
        ECAM["ECAM Base<br/>Configuration Space"]
        CapRegs["PCIe Capability<br/>Registers"]
    end
    
    subgraph "Platform Integration"
        C2CInit["C2C Initialization<br/>Chip-to-Chip Links"]
        GPUKick["GPU Kick GPIO<br/>External GPU Detection"]
        ConfigMgr["Configuration Manager<br/>ACPI Table Data"]
        BPMP["BPMP IPC<br/>Platform Services"]
    end
    
    PcieMain --> PciePrivate
    PciePrivate --> PcieConfig
    PciePrivate --> LinkTrain
    PciePrivate --> ErrorHandle
    
    PcieConfig --> ECAM
    LinkTrain --> XAL
    LinkTrain --> XTL
    ErrorHandle --> CapRegs
    
    LinkTrain --> C2CInit
    LinkTrain --> GPUKick
    PciePrivate --> ConfigMgr
    C2CInit --> BPMP
```

Sources: [Silicon/NVIDIA/Drivers/PcieControllerDxe/PcieControllerPrivate.h:50-98](), [Silicon/NVIDIA/Drivers/PcieControllerDxe/PcieControllerDxe.c:574-723]()

### PCIe Configuration Space Access

The driver implements custom configuration space access through the `NVIDIA_PCI_ROOT_BRIDGE_CONFIGURATION_IO_PROTOCOL`:

| Function | Purpose | Implementation |
|----------|---------|----------------|
| `PcieConfigurationRead` | Read config space | [Silicon/NVIDIA/Drivers/PcieControllerDxe/PcieControllerDxe.c:245-253]() |
| `PcieConfigurationWrite` | Write config space | [Silicon/NVIDIA/Drivers/PcieControllerDxe/PcieControllerDxe.c:270-278]() |
| `PcieConfigurationAccess` | Common access logic | [Silicon/NVIDIA/Drivers/PcieControllerDxe/PcieControllerDxe.c:111-228]() |

Key features:
- ECAM-based configuration access with offset calculation
- Option ROM disable for non-root bridge devices
- Bus number validation and device enumeration
- Support for 8, 16, and 32-bit access widths

Sources: [Silicon/NVIDIA/Drivers/PcieControllerDxe/PcieControllerDxe.c:111-278]()

### Link Training and Initialization

The `InitializeController` function manages the complete PCIe link bring-up sequence:

```mermaid
flowchart TD
    Start["InitializeController()"] --> XALProg["Program XAL Registers<br/>Memory/IO Address Windows"]
    XALProg --> BusSetup["Setup Bus Numbers<br/>Primary/Secondary Bus"]
    BusSetup --> CommandReg["Enable Command Register<br/>Memory/IO/Bus Master"]
    CommandReg --> FindCap["Find PCIe Capability<br/>PCIeFindCap()"]
    FindCap --> ReleasePERST["Release PERST#<br/>100ms delay"]
    ReleasePERST --> WaitLink["Wait for Link Up<br/>Poll DLL Active"]
    WaitLink --> LinkUp{"Link Status?"}
    LinkUp -->|Up| Retrain["Check Auto-train Disable<br/>RetrainLink() if needed"]
    LinkUp -->|Down| LinkDown["Log Link Down<br/>Continue anyway"]
    Retrain --> C2CCheck{"C2C Required?"}
    LinkDown --> C2CCheck
    C2CCheck -->|Yes| C2CInit["Initialize C2C<br/>Chip-to-Chip Link"]
    C2CCheck -->|No| Complete["Initialization Complete"]
    C2CInit --> Complete
```

Sources: [Silicon/NVIDIA/Drivers/PcieControllerDxe/PcieControllerDxe.c:574-723]()

### Error Reporting and Recovery

The driver configures Advanced Error Reporting (AER) and Downstream Port Containment (DPC) for robust error handling:

- **AER Configuration**: Clears error status registers, configures severity levels, enables error forwarding
- **DPC Setup**: Enables DPC triggers for fatal/non-fatal errors with interrupt generation  
- **Root Port Controls**: Configures system error signaling for correctable/uncorrectable errors
- **ECRC Support**: Enables End-to-End CRC generation and checking when supported

Sources: [Silicon/NVIDIA/Drivers/PcieControllerDxe/PcieControllerDxe.c:968-1188]()

## Memory Management and SMMU

The System Memory Management Unit (SMMU) provides I/O memory management and translation services, implementing both SMMUv3 controller management and the UEFI IOMMU protocol for DMA operations.

### SMMU Controller Architecture

```mermaid
graph TB
    subgraph "SMMUv3 Controller Driver"
        SmmuDriver["SmmuV3Dxe<br/>Controller Driver"]
        SmmuPrivate["SMMU_V3_CONTROLLER_PRIVATE_DATA<br/>Controller State"]
        SmmuFeatures["SMMU_V3_CONTROLLER_FEATURES<br/>Hardware Capabilities"]
        SmmuProtocol["NVIDIA_SMMUV3_CONTROLLER_PROTOCOL<br/>Control Interface"]
    end
    
    subgraph "Hardware Queues"
        CmdQueue["Command Queue<br/>SMMU_V3_QUEUE CmdQueue"]
        EvtQueue["Event Queue<br/>SMMU_V3_QUEUE EvtQueue"]
        StreamTable["Stream Table<br/>STE Entries"]
        PageTables["Page Tables<br/>Translation Tables"]
    end
    
    subgraph "IOMMU Protocol Layer"  
        IoMmuDriver["SmmuDriverDxe<br/>Protocol Implementation"]
        IoMmuProtocol["EDKII_IOMMU_PROTOCOL<br/>Standard Interface"]
        MapOperations["IoMmuMap/Unmap<br/>DMA Buffer Management"]
        AttributeOps["IoMmuSetAttribute<br/>Stream ID Configuration"]
    end
    
    subgraph "Client Integration"
        SmmuLib["SmmuLib<br/>Helper Functions"]
        SourceId["GetSourceIdFromPciHandle()<br/>PCI→Stream ID Mapping"]
        PciHandle["PCI Device Handles"]
    end
    
    SmmuDriver --> SmmuPrivate
    SmmuPrivate --> SmmuFeatures
    SmmuPrivate --> SmmuProtocol
    SmmuPrivate --> CmdQueue
    SmmuPrivate --> EvtQueue
    SmmuPrivate --> StreamTable
    
    SmmuProtocol --> IoMmuDriver
    IoMmuDriver --> IoMmuProtocol
    IoMmuProtocol --> MapOperations
    IoMmuProtocol --> AttributeOps
    
    AttributeOps --> SmmuLib
    SmmuLib --> SourceId
    SourceId --> PciHandle
    
    StreamTable --> PageTables
```

Sources: [Silicon/NVIDIA/Drivers/SmmuV3Dxe/SmmuV3DxePrivate.h:363-378](), [Silicon/NVIDIA/Drivers/SmmuDriverDxe/SmmuDriverDxe.c:23-29](), [Silicon/NVIDIA/Library/SmmuLib/SmmuLib.c:28-36]()

### SMMU Initialization Sequence

The SMMUv3 driver follows a structured initialization process to configure hardware features and establish translation services:

```mermaid
sequenceDiagram
    participant Driver as "SmmuV3Dxe"
    participant Hardware as "SMMU Hardware"
    participant Memory as "System Memory"
    participant Queues as "Command/Event Queues"
    
    Driver->>Hardware: "ResetSmmuV3Controller()<br/>Set Global Bypass Mode"
    Driver->>Hardware: "IdentifySmmuV3ControllerFeatures()<br/>Read IDR registers"
    Driver->>Hardware: "ConfigureSmmuV3ControllerXlatSupport()<br/>Set address size limits"
    Driver->>Hardware: "ConfigureSmmuV3ControllerQueueSizes()<br/>Determine queue capacities"
    
    Driver->>Memory: "AllocateAlignedPages()<br/>Command Queue Memory"
    Driver->>Queues: "SetupSmmuV3Cmdq()<br/>Initialize Command Queue"
    Driver->>Memory: "AllocateAlignedPages()<br/>Event Queue Memory"  
    Driver->>Queues: "SetupSmmuV3Evtq()<br/>Initialize Event Queue"
    
    Driver->>Memory: "AllocateAlignedPages()<br/>Stream Table Memory"
    Driver->>Hardware: "SetupSmmuV3StrTable()<br/>Configure Stream Table"
    Driver->>Hardware: "InvalidateStes()<br/>Clear all Stream Table Entries"
    
    Note over Driver,Hardware: "Controller ready for translation operations"
```

Sources: [Silicon/NVIDIA/Drivers/SmmuV3Dxe/SmmuV3Dxe.c:37-699]()

### Stream ID Management

The SMMU uses Stream IDs to identify DMA transactions from different devices. The `SmmuLib` provides functions to map PCI device handles to Stream IDs:

| Component | Function | Implementation |
|-----------|----------|----------------|
| **Stream ID Calculation** | `GetSourceIdFromPciHandle()` | [Silicon/NVIDIA/Library/SmmuLib/SmmuLib.c:176-318]() |
| **PCI Location Mapping** | Bus/Device/Function → RID | RID = (Bus << 8) \| (Device << 3) \| Function |
| **Root Bridge Lookup** | Segment → StreamIdBase | Search `NVIDIA_PCI_ROOT_BRIDGE_CONFIGURATION_IO_PROTOCOL` |
| **Final Stream ID** | RID + StreamIdBase | StreamId = StreamIdBase + RID |

### Translation Modes

The SMMU supports two primary translation modes:

- **SMMU_V3_BYPASS**: Direct memory access without translation
- **SMMU_V3_TRANSLATE**: Full address translation through page tables

Mode selection is based on device vendor ID matching against bypass lists stored in the device tree under `/firmware/uefi/skip-smmu-vid`.

Sources: [Silicon/NVIDIA/Library/SmmuLib/SmmuLib.c:40-169](), [Silicon/NVIDIA/Include/Protocol/SmmuV3Protocol.h:23-27]()

## Display and Graphics Controllers

The display controller driver (`NvDisplayControllerDxe`) manages display hardware initialization, clock/reset control, and graphics output protocol implementation across different NVIDIA Tegra platforms.

### Display Controller Architecture

```mermaid
graph TB
    subgraph "Display Controller Driver"
        DisplayMain["NvDisplayControllerDxe.c<br/>Platform Detection"]
        DisplayController["NvDisplayController.c<br/>Common Logic"]
        DisplayPrivate["NV_DISPLAY_CONTROLLER_PRIVATE<br/>Controller State"]
    end
    
    subgraph "Platform-Specific Implementations"
        T234Driver["NvDisplayControllerT234.c<br/>Tegra 234 Implementation"]
        T264Driver["NvDisplayControllerT264.c<br/>Tegra 264 Implementation"]
        T234Enable["EnableHwT234()<br/>T234 Hardware Control"]
        T264Enable["EnableHwT264()<br/>T264 Hardware Control"]
    end
    
    subgraph "Hardware Management"
        DisplayHw["NvDisplayHw.c<br/>Hardware Abstraction"]
        ClockMgmt["Clock Management<br/>Enable/Disable/Parent Setting"]
        ResetMgmt["Reset Management<br/>Assert/Deassert Sequences"]
        MmioRegions["MMIO Region Mapping<br/>Register Access"]
    end
    
    subgraph "Graphics Output"
        ChildGop["NvDisplayChildGop.c<br/>GOP Instance Management"]
        GopProtocol["Graphics Output Protocol<br/>Framebuffer Interface"]
        Handoff["Display Handoff<br/>SimpleFB/EFIFB"]
        FdtUpdate["Device Tree Update<br/>Framebuffer Properties"]
    end
    
    DisplayMain --> DisplayController
    DisplayController --> DisplayPrivate
    DisplayController --> T234Driver
    DisplayController --> T264Driver
    
    T234Driver --> T234Enable
    T264Driver --> T264Enable
    T234Enable --> DisplayHw
    T264Enable --> DisplayHw
    
    DisplayHw --> ClockMgmt
    DisplayHw --> ResetMgmt
    DisplayHw --> MmioRegions
    
    DisplayController --> ChildGop
    ChildGop --> GopProtocol
    ChildGop --> Handoff
    Handoff --> FdtUpdate
```

Sources: [Silicon/NVIDIA/Drivers/NvDisplayControllerDxe/NvDisplayControllerDxe.c:51-108](), [Silicon/NVIDIA/Drivers/NvDisplayControllerDxe/NvDisplayController.c:28-43]()

### Platform-Specific Hardware Control

The display driver uses function pointers to abstract chip-specific hardware operations:

```mermaid
flowchart TD
    Start["DeviceDiscoveryNotify()"] --> PlatDetect{"Platform Detection"}
    PlatDetect -->|T234| T234Start["NvDisplayControllerStartT234()"]
    PlatDetect -->|T264| T264Start["NvDisplayControllerStartT264()"]
    
    T234Start --> T234Create["CreateControllerPrivate(<br/>HwEnable=EnableHwT234,<br/>HwHandoff=HandoffHwT234)"]
    T264Start --> T264Create["CreateControllerPrivate(<br/>HwEnable=EnableHwT264,<br/>HwHandoff=HandoffHwT264)"]
    
    T234Create --> CommonFlow["Common Initialization Flow"]
    T264Create --> CommonFlow
    
    CommonFlow --> HwEnable["HwEnable(Enable=TRUE)"]
    HwEnable --> T234Impl["T234: AssertResets(FALSE)<br/>EnableClocks(TRUE)"]
    HwEnable --> T264Impl["T264: AssertResets(FALSE)<br/>EnableClocks(TRUE)<br/>SetupEmcFrequency()"]
    
    T234Impl --> ProtocolInstall["Install Graphics Output Protocol"]
    T264Impl --> ProtocolInstall
```

### T234 vs T264 Implementation Differences

| Aspect | T234 Implementation | T264 Implementation |
|--------|-------------------|-------------------|
| **Reset Signals** | `nvdisplay_reset`, `dpaux0_reset` | `dpaux0_reset` only |
| **Clock Parents** | `disp_root→disppll_clk`<br/>`nvdisplayhub_clk→sppll0_clkoutb_clk` | `disp_root→disppll_clk`<br/>`nvdisplayhub_clk→sppll0_clkoutb_clk` |  
| **Additional Clocks** | `dsi_core_clk`, `aza_bit_clk` | None |
| **Memory Bandwidth** | Not managed | BPMP BWMGR integration via `SetupEmcFrequency()` |
| **GPIO Configuration** | HDMI/DP mux control via TCA9539 | Not implemented |

Sources: [Silicon/NVIDIA/Drivers/NvDisplayControllerDxe/NvDisplayControllerT234.c:42-99](), [Silicon/NVIDIA/Drivers/NvDisplayControllerDxe/NvDisplayControllerT264.c:70-122]()

### Display Handoff Mechanisms

The display driver supports multiple handoff methods for seamless transition to the operating system:

```mermaid
graph TD
    HandoffMode{"Handoff Mode<br/>PcdSocDisplayHandoffMode"}
    HandoffMode -->|NEVER| Shutdown["NvDisplayHwShutdown()<br/>Reset display hardware"]
    HandoffMode -->|ALWAYS| CheckMethod{"Handoff Method"}
    HandoffMode -->|AUTO| CheckActive{"GOP Active?"}
    
    CheckActive -->|Yes| CheckMethod
    CheckActive -->|No| Shutdown
    
    CheckMethod -->|SIMPLEFB| UpdateFDT["NvDisplayUpdateFdtTableActiveChildGop()<br/>Add SimpleFB node to Device Tree"]
    CheckMethod -->|EFIFB| EnableEFI["NvDisplayEnableEfifbActiveChildGop()<br/>Enable EFI Framebuffer driver"]
    
    UpdateFDT --> KeepRunning["Leave display running<br/>Framebuffer preserved"]
    EnableEFI --> KeepRunning
    Shutdown --> PowerDown["Assert resets<br/>Disable clocks"]
```

The handoff process is triggered by `ReadyToBoot` and `FdtTable` events, ensuring display configuration is updated before OS boot.

Sources: [Silicon/NVIDIA/Drivers/NvDisplayControllerDxe/NvDisplayController.c:158-242](), [Silicon/NVIDIA/Drivers/NvDisplayControllerDxe/NvDisplayChildGop.c:154-271]()

---

