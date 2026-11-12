<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/gpu-admin-tools · page 2 Core Architecture · fetched 2026-10-26 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [gpu/__init__.py](gpu/__init__.py)
- [nvidia_gpu_tools.py](nvidia_gpu_tools.py)

</details>



The Core Architecture represents the foundational system that provides GPU and NVSwitch device management capabilities through the central `nvidia_gpu_tools.py` module. This system handles device identification, instantiation, communication, and control operations across multiple GPU architectures and device types.

For information about specific device operations and CLI interfaces, see [Device Operations](#3.2). For details about communication protocols and RPC systems, see [Communication Systems](#4).

## System Overview

The core architecture establishes a hierarchical device management framework built around the `NvidiaDevice` base class and specialized implementations for different device types and states. The system provides unified interfaces for hardware communication, memory management, and device control operations.

### Core Architecture Diagram

```mermaid
graph TB
    subgraph "Device Identification Layer"
        GPUMap["GPU_MAP<br/>Device Configurations"]
        NVSwitchMap["NVSWITCH_MAP<br/>Device Configurations"]
        GPUMapMultiple["GPU_MAP_MULTIPLE<br/>Multi-Product Support"]
    end
    
    subgraph "Base Device Classes"
        NvidiaDevice["NvidiaDevice<br/>Base Device Class"]
        BrokenGpu["BrokenGpu<br/>Broken Device Handler"]
        NvidiaDeviceInternal["NvidiaDeviceInternal<br/>Internal Interface"]
    end
    
    subgraph "Specialized Device Classes"
        Gpu["Gpu Class<br/>GPU Device Implementation"]
        NvSwitch["NvSwitch Class<br/>Switch Device Implementation"]
    end
    
    subgraph "Communication Infrastructure"
        GpuBitfield["GpuBitfield<br/>Register Access"]
        RawBitfield["RawBitfield<br/>Bitfield Operations"]
        FspRpc["FspRpc Integration<br/>Firmware Communication"]
    end
    
    subgraph "Memory Management"
        GpuMemPort["GpuMemPort<br/>Memory Port Base"]
        GpuImemPort["GpuImemPort<br/>Instruction Memory"]
        GpuFalcon["GpuFalcon<br/>Falcon Controller Base"]
    end
    
    GPUMap --> NvidiaDevice
    NVSwitchMap --> NvidiaDevice
    GPUMapMultiple --> NvidiaDevice
    
    NvidiaDevice --> Gpu
    NvidiaDevice --> NvSwitch
    NvidiaDeviceInternal --> NvidiaDevice
    
    BrokenGpu -.-> PciDevice
    
    Gpu --> GpuBitfield
    Gpu --> FspRpc
    
    GpuFalcon --> GpuMemPort
    GpuFalcon --> GpuImemPort
    
    GpuBitfield --> RawBitfield
```

Sources: [nvidia_gpu_tools.py:50-913](), [nvidia_gpu_tools.py:1004-1055](), [nvidia_gpu_tools.py:915-964]()

## Device Identification and Mapping

The system uses comprehensive device mapping tables to identify and configure GPU and NVSwitch devices based on their hardware characteristics.

### Device Mapping Structure

| Component | Purpose | Key Properties |
|-----------|---------|----------------|
| `GPU_MAP` | Primary GPU device configurations | Architecture, memory support, falcon configurations |
| `NVSWITCH_MAP` | NVSwitch device configurations | Link counts, falcon support, architecture |
| `GPU_MAP_MULTIPLE` | Multi-product device disambiguation | Device ID to product name mapping |

### Device Architecture Support

```mermaid
graph LR
    subgraph "GPU Architectures"
        Kepler["kepler"]
        Maxwell["maxwell"] 
        Pascal["pascal"]
        Volta["volta"]
        Turing["turing"]
        Ampere["ampere"]
        Ada["ada"]
        Hopper["hopper"]
        Blackwell["blackwell"]
    end
    
    subgraph "NVSwitch Architectures"
        Limerock["limerock<br/>LR10"]
        Laguna["laguna<br/>NVSwitch_gen3"]
    end
    
    subgraph "Device Properties"
        MemoryClear["memory_clear_supported"]
        ECCForcing["forcing_ecc_on_after_reset_supported"]
        PMUReset["pmu_reset_in_pmc"]
        NVLinkSupport["nvlink configuration"]
    end
    
    Kepler --> MemoryClear
    Maxwell --> MemoryClear
    Pascal --> ECCForcing
    Volta --> NVLinkSupport
    Ampere --> NVLinkSupport
    Hopper --> NVLinkSupport
    Blackwell --> NVLinkSupport
    
    Limerock --> Laguna
    Laguna --> NVLinkSupport
```

Sources: [nvidia_gpu_tools.py:50-78](), [nvidia_gpu_tools.py:83-913]()

## Base Device Classes

The foundation of the device management system consists of several key base classes that provide common functionality and interfaces.

### Class Hierarchy

```mermaid
graph TB
    PciDevice["PciDevice<br/>PCI Infrastructure"]
    NvidiaDeviceInternal["NvidiaDeviceInternal<br/>Internal Marker"]
    
    subgraph "Core Device Classes"
        NvidiaDevice["NvidiaDevice<br/>• Bar mapping<br/>• Power management<br/>• Reset operations<br/>• Common device ops"]
        BrokenGpu["BrokenGpu<br/>• Broken device handling<br/>• Limited functionality<br/>• Error state management"]
    end
    
    subgraph "Device States"
        WorkingGpu["Working GPU<br/>Full functionality"]
        BrokenGpuSecFault["Broken with SEC fault<br/>Security fault state"]
        BrokenGpuCfgSpace["Broken config space<br/>PCI issues"]
        UnknownDevice["Unknown Device<br/>Unsupported hardware"]
    end
    
    PciDevice --> BrokenGpu
    PciDevice --> NvidiaDevice
    NvidiaDeviceInternal --> NvidiaDevice
    
    NvidiaDevice --> WorkingGpu
    BrokenGpu --> BrokenGpuSecFault
    BrokenGpu --> BrokenGpuCfgSpace
    NvidiaDevice --> UnknownDevice
```

Sources: [nvidia_gpu_tools.py:1004-1055](), [nvidia_gpu_tools.py:965-1003]()

### NvidiaDevice Base Functionality

The `NvidiaDevice` class provides essential device management capabilities:

- **Power Management**: Automatic D0 state enforcement and power control handling
- **BAR0 Mapping**: Memory-mapped register access infrastructure  
- **Reset Operations**: FLR and SBR reset support with pre/post validation
- **Device Units**: Dynamic discovery and caching of GPU functional units
- **Falcon Management**: Embedded controller initialization and communication

Key properties initialized during device creation include form factor detection (`is_pcie`, `is_sxm`), interconnect support (`has_c2c`, `is_nvlink_supported`), and reset capabilities (`is_reset_coupling_supported`).

Sources: [nvidia_gpu_tools.py:1016-1055](), [nvidia_gpu_tools.py:1104-1176]()

## Memory and Communication Infrastructure

The core architecture provides sophisticated memory access and communication systems built around bitfield operations and direct hardware communication.

### Bitfield Access System

```mermaid
graph TB
    subgraph "Bitfield Classes"
        RawBitfield["RawBitfield<br/>• Slice-based access<br/>• Mask operations<br/>• Value manipulation"]
        GpuBitfield["GpuBitfield<br/>• Hardware register access<br/>• Automatic read/write<br/>• Deferred operations"]
    end
    
    subgraph "Register Operations"
        DirectRead["gpu.read(offset)"]
        DirectWrite["gpu.write(offset, data)"]
        BitfieldAccess["bitfield[start:end]"]
        DeferredWrite["bitfield.commit()"]
    end
    
    subgraph "Hardware Interface"
        BAR0["BAR0 Memory Space"]
        RegisterMap["GPU Register Map"]
        MMIO["Memory-Mapped I/O"]
    end
    
    RawBitfield --> GpuBitfield
    GpuBitfield --> DirectRead
    GpuBitfield --> DirectWrite
    
    DirectRead --> BAR0
    DirectWrite --> BAR0
    BitfieldAccess --> GpuBitfield
    DeferredWrite --> GpuBitfield
    
    BAR0 --> RegisterMap
    RegisterMap --> MMIO
```

Sources: [nvidia_gpu_tools.py:915-964](), [nvidia_gpu_tools.py:1257-1259]()

### Hardware Communication Methods

The core architecture provides multiple levels of hardware access:

| Method | Purpose | Usage Pattern |
|--------|---------|---------------|
| `read()/write()` | Direct register access | Immediate hardware operations |
| `read_bad_ok()` | Fault-tolerant reads | Accessing potentially offline hardware |
| `bitfield()` | Structured field access | Multi-bit register field manipulation |
| `poll_register()` | Synchronous waiting | Waiting for hardware state changes |

The system includes comprehensive register polling capabilities with timeout handling, automatic retry logic, and debug tracing support for complex hardware state monitoring operations.

Sources: [nvidia_gpu_tools.py:1080-1088](), [nvidia_gpu_tools.py:1194-1249]()

---

