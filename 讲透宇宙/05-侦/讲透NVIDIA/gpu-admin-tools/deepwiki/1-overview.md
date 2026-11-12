<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/gpu-admin-tools · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [nvidia_gpu_tools.py](nvidia_gpu_tools.py)

</details>



## Purpose and Scope

The `nvidia-gpu-admin-tools` repository provides a privileged Python-based administration utility for NVIDIA GPU and NVSwitch devices. The system enables low-level configuration, debugging, and security management operations including Confidential Computing mode control, NVLink management, and comprehensive device state inspection. This toolkit operates at the hardware abstraction layer, providing direct access to GPU registers, embedded controllers (Falcons), and communication protocols.

For information about specific CLI operations, see [Command Line Interface](#3). For details about communication protocols and RPC systems, see [Communication Systems](#4). For device-specific hardware management, see [GPU Units and Subsystems](#6).

## System Architecture

The system follows a layered architecture with the core `nvidia_gpu_tools.py` module serving as the foundation for all GPU management operations:

```mermaid
graph TB
    subgraph "User Interface Layer"
        CLI["main.py<br/>CLI Entry Point"]
        PerGPU["per_gpu.py<br/>GPU Operations"]
        PerDevice["per_device.py<br/>Device Operations"]
        PerNVSwitch["per_gpu_nvswitch.py<br/>NVSwitch Operations"]
    end
    
    subgraph "Core Management Layer"
        GPUTools["nvidia_gpu_tools.py<br/>Core GPU Management"]
        GPUClass["Gpu Class"]
        NVSwitchClass["NvSwitch Class"]
        BrokenGPUClass["BrokenGpu Class"]
        NvidiaDevice["NvidiaDevice Base"]
    end
    
    subgraph "Device Abstraction"
        DeviceMap["GPU_MAP & NVSWITCH_MAP<br/>Device Identification"]
        Properties["GpuProperties<br/>Device Characteristics"]
        FalconMgmt["GpuFalcon<br/>Embedded Controller Management"]
    end
    
    subgraph "Communication Layer"
        FspRPC["FspRpc<br/>Firmware RPC Protocol"]
        MemPorts["GpuMemPort & GpuImemPort<br/>Memory Access"]
        BitfieldUtils["GpuBitfield<br/>Register Manipulation"]
    end
    
    CLI --> GPUTools
    PerGPU --> GPUTools
    PerDevice --> GPUTools
    PerNVSwitch --> GPUTools
    
    GPUTools --> GPUClass
    GPUTools --> NVSwitchClass
    GPUTools --> BrokenGPUClass
    GPUTools --> NvidiaDevice
    
    GPUClass --> DeviceMap
    GPUClass --> Properties
    GPUClass --> FalconMgmt
    
    FalconMgmt --> FspRPC
    FalconMgmt --> MemPorts
    NvidiaDevice --> BitfieldUtils
```

**Sources:** [nvidia_gpu_tools.py:1-50](), [nvidia_gpu_tools.py:100-913](), [README.md:1-25]()

## Core Device Management System

The central management system is built around the `NvidiaDevice` base class and its specialized implementations for different device types and states:

```mermaid
graph TB
    subgraph "Device Hierarchy"
        NvidiaDevice["NvidiaDevice<br/>Base PCI Device"]
        Gpu["Gpu Class<br/>Functional GPU"]
        NvSwitch["NvSwitch Class<br/>Switch Device"]
        BrokenGpu["BrokenGpu Class<br/>Failed/Unresponsive Device"]
    end
    
    subgraph "Device State Management"
        SanityCheck["sanity_check()<br/>Device Health Validation"]
        ResetPre["reset_pre()<br/>Pre-Reset Configuration"]
        ResetPost["reset_post()<br/>Post-Reset Validation"]
        ResetSBR["reset_with_sbr()<br/>Secondary Bus Reset"]
        ResetFLR["reset_with_flr()<br/>Function Level Reset"]
    end
    
    subgraph "Device Discovery"
        GPUMap["GPU_MAP<br/>Device ID to Properties"]
        NVSwitchMap["NVSWITCH_MAP<br/>Switch Device Mapping"]
        DeviceInit["Device Initialization<br/>Power & BAR Configuration"]
    end
    
    NvidiaDevice --> Gpu
    NvidiaDevice --> NvSwitch
    NvidiaDevice --> BrokenGpu
    
    Gpu --> SanityCheck
    Gpu --> ResetPre
    Gpu --> ResetPost
    Gpu --> ResetSBR
    Gpu --> ResetFLR
    
    Gpu --> GPUMap
    NvSwitch --> NVSwitchMap
    NvidiaDevice --> DeviceInit
```

The `GPU_MAP` and `NVSWITCH_MAP` dictionaries provide comprehensive device identification and capability mapping for supported hardware generations from Kepler through Blackwell architectures.

**Sources:** [nvidia_gpu_tools.py:1008-1055](), [nvidia_gpu_tools.py:100-913](), [nvidia_gpu_tools.py:965-1002]()

## Embedded Controller (Falcon) Management

The system provides extensive management of GPU embedded controllers through a hierarchical falcon class system:

```mermaid
graph TB
    subgraph "Falcon Base Infrastructure"
        GpuFalcon["GpuFalcon<br/>Base Falcon Controller"]
        MemPort["GpuMemPort<br/>Memory Access Interface"]
        ImemPort["GpuImemPort<br/>Instruction Memory Port"]
    end
    
    subgraph "Falcon Implementations"
        PMU["PmuFalcon<br/>Power Management Unit"]
        GSP["GspFalcon<br/>GPU System Processor"]
        SEC["SecFalcon<br/>Security Engine"]
        FSP["FspFalcon<br/>Firmware Service Processor"]
        NVDEC["NvDecFalcon<br/>Video Decoder"]
    end
    
    subgraph "Memory Spaces"
        IMEM["Instruction Memory<br/>Falcon Code Storage"]
        DMEM["Data Memory<br/>Falcon Data Storage"]
        EMEM["Extended Memory<br/>Additional Storage"]
    end
    
    GpuFalcon --> PMU
    GpuFalcon --> GSP
    GpuFalcon --> SEC
    GpuFalcon --> FSP
    GpuFalcon --> NVDEC
    
    GpuFalcon --> MemPort
    GpuFalcon --> ImemPort
    
    MemPort --> DMEM
    MemPort --> EMEM
    ImemPort --> IMEM
```

Each falcon provides specific functionality: `PmuFalcon` manages power states, `GspFalcon` handles system-level operations, `SecFalcon` manages security features, and `FspFalcon` provides firmware services and RPC communication.

**Sources:** [nvidia_gpu_tools.py:2037-2494](), [nvidia_gpu_tools.py:2495-2543](), [nvidia_gpu_tools.py:1930-2036]()

## Configuration and Security Management

The system implements comprehensive configuration management through PRC (Product Reconfiguration) knobs and security features:

```mermaid
graph TB
    subgraph "Configuration Knobs"
        CCMode["Confidential Computing<br/>CC Mode Control"]
        PPCIeMode["Protected PCIe<br/>PPCIe Mode Control"]
        ECCControl["ECC Memory<br/>Error Correction Control"]
        MIGMode["Multi-Instance GPU<br/>MIG Mode Control"]
    end
    
    subgraph "Security Features"
        CCSettings["query_cc_mode()<br/>set_cc_mode()"]
        PPCIeSettings["query_ppcie_mode()<br/>set_ppcie_mode()"]
        BarFirewall["BAR0 Firewall<br/>Access Control"]
        ResetCoupling["Reset Coupling<br/>Fundamental Reset Control"]
    end
    
    subgraph "Configuration Methods"
        KnobsQuery["knobs_query()<br/>State Reading"]
        KnobsSet["knobs_set()<br/>Configuration Application"]
        KnobsReset["knobs_reset_to_defaults()<br/>Factory Reset"]
        FspRpcKnobs["fsp_rpc.prc_knob_read/write()<br/>Low-level Access"]
    end
    
    CCMode --> CCSettings
    PPCIeMode --> PPCIeSettings
    ECCControl --> KnobsSet
    MIGMode --> KnobsSet
    
    CCSettings --> KnobsQuery
    PPCIeSettings --> KnobsQuery
    KnobsQuery --> FspRpcKnobs
    KnobsSet --> FspRpcKnobs
    KnobsReset --> FspRpcKnobs
```

The configuration system supports three CC modes: `"off"` (default operation), `"on"` (full security features), and `"devtools"` (security with debugging enabled).

**Sources:** [nvidia_gpu_tools.py:1662-1800](), [nvidia_gpu_tools.py:1821-1851](), [README.md:5-23]()

## NVLink Management System

The system provides comprehensive NVLink management capabilities for multi-GPU communication:

```mermaid
graph TB
    subgraph "NVLink Discovery"
        EnabledLinks["nvlink_enabled_links<br/>Active Link Detection"]
        EnabledGroups["nvlink_enabled_groups<br/>Group Organization"]
        QueryLinks["_nvlink_query_enabled_links()<br/>Link Enumeration"]
    end
    
    subgraph "Link State Management"
        LinkStates["nvlink_get_link_states()<br/>State Querying"]
        DLStates["nvlink_dl_get_link_states()<br/>Data Link States"]
        HSLinks["nvlink_get_links_in_hs()<br/>High-Speed Detection"]
    end
    
    subgraph "Debug and Monitoring"
        NVLinkDebug["nvlink_debug()<br/>Comprehensive Debug"]
        NportDebug["nvlink_debug_nport()<br/>Network Port Debug"]
        MinionDebug["nvlink_debug_minion_basic_state()<br/>Minion Controller Debug"]
        TLCDebug["nvlink_debug_nvltlc_basic_state()<br/>Transport Layer Debug"]
    end
    
    QueryLinks --> EnabledLinks
    QueryLinks --> EnabledGroups
    
    EnabledLinks --> LinkStates
    EnabledLinks --> DLStates
    LinkStates --> HSLinks
    
    LinkStates --> NVLinkDebug
    NVLinkDebug --> NportDebug
    NVLinkDebug --> MinionDebug
    NVLinkDebug --> TLCDebug
```

The NVLink system supports architecture-specific implementations with different protocols for Hopper (`nvlink_debug_h100()`) versus Blackwell (`nvlink_debug_b100()`) generations.

**Sources:** [nvidia_gpu_tools.py:1323-1346](), [nvidia_gpu_tools.py:1548-1656](), [nvidia_gpu_tools.py:1261-1322]()

---

