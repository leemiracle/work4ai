<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/gpu-admin-tools · page 7 Configuration and Control · fetched 2026-10-26 -->

# Configuration and Control

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [gpu/prc.py](gpu/prc.py)
- [utils/bitfield.py](utils/bitfield.py)

</details>



The Configuration and Control system provides low-level infrastructure for managing GPU hardware settings, register manipulation, and hardware feature control. This system encompasses PRC (Product Reconfiguration) knobs for runtime feature control, register definitions for hardware access, and bitfield utilities for structured data manipulation.

For device identification and properties, see [Device Management](#5). For GPU unit-specific configuration, see [GPU Units and Subsystems](#6). For system-level integration, see [System Integration](#8).

## System Overview

The Configuration and Control system forms the foundation for hardware-level GPU management, providing three core capabilities:

```mermaid
graph TB
    subgraph "Configuration and Control System"
        PrcKnobs["`PrcKnob Enum
        gpu/prc.py`"]
        RegDefs["`Register Definitions
        Architecture-specific`"]
        Bitfield["`Bitfield Class
        utils/bitfield.py`"]
    end
    
    subgraph "GPU Management Layer"
        GpuClass["`Gpu Class
        nvidia_gpu_tools.py`"]
        FalconMgmt["`Falcon Management
        Various falcon classes`"]
        UnitSystem["`GPU Unit System
        gpu/units/`"]
    end
    
    subgraph "Hardware Layer"
        GPUHardware["`GPU Hardware
        Registers and Configuration`"]
        FalconProcs["`Falcon Processors
        PMU, GSP, SEC, FSP`"]
        Subsystems["`GPU Subsystems
        NVLink, C2C, Thermal`"]
    end
    
    PrcKnobs --> GpuClass
    RegDefs --> GpuClass
    Bitfield --> GpuClass
    
    PrcKnobs --> FalconMgmt
    RegDefs --> FalconMgmt
    Bitfield --> FalconMgmt
    
    RegDefs --> UnitSystem
    Bitfield --> UnitSystem
    
    GpuClass --> GPUHardware
    FalconMgmt --> FalconProcs
    UnitSystem --> Subsystems
```

**Sources:** [gpu/prc.py:26-113](), [utils/bitfield.py:37-108]()

## PRC Knobs System

The PRC (Product Reconfiguration) knobs system provides runtime control over GPU hardware features through the `PrcKnob` enum. These knobs control critical security, connectivity, and operational modes.

### Core PRC Knob Categories

| Knob Category | Knob IDs | Purpose |
|---------------|----------|---------|
| **Confidential Computing** | `PRC_KNOB_ID_CCD_ALLOW_INB` (5)<br/>`PRC_KNOB_ID_CCD` (6)<br/>`PRC_KNOB_ID_CCM_ALLOW_INB` (7)<br/>`PRC_KNOB_ID_CCM` (8) | Enable/disable confidential computing modes |
| **BAR0 Security** | `PRC_KNOB_ID_BAR0_DECOUPLER_ALLOW_INB` (9)<br/>`PRC_KNOB_ID_BAR0_DECOUPLER` (10) | Control BAR0 access decoupling |
| **PCIe Configuration** | `PRC_KNOB_ID_PPCIE_ALLOW_INB` (44)<br/>`PRC_KNOB_ID_PPCIE` (45) | Control PCIe P2P modes |
| **Reset Control** | `PRC_KNOB_ID_FORCE_RESET_COUPLING_ALLOW_INB` (35)<br/>`PRC_KNOB_ID_FORCE_RESET_COUPLING` (36) | Manage reset coupling behavior |
| **Certificate Authority** | `PRC_KNOB_ID_CECA_ALLOW_INB` (46)<br/>`PRC_KNOB_ID_CECA` (47) | Control certificate authority features |

### PRC Knob Interface

The `PrcKnob` enum provides a standardized interface for knob identification and management:

```mermaid
graph LR
    PrcKnobEnum["`PrcKnob Enum`"]
    KnobValues["`Knob ID Values
    1-47 defined`"]
    StringConversion["`str_from_knob_id()
    Converts ID to readable string`"]
    
    PrcKnobEnum --> KnobValues
    PrcKnobEnum --> StringConversion
    
    subgraph "Knob Types"
        Security["`Security Knobs
        CCD, CCM, BAR0_DECOUPLER`"]
        Connectivity["`Connectivity Knobs
        PPCIE, CECA`"]
        SystemControl["`System Control
        FORCE_RESET_COUPLING`"]
        Reserved["`Reserved Knobs
        IDs 1-4, 11-34, 37-43`"]
    end
    
    KnobValues --> Security
    KnobValues --> Connectivity
    KnobValues --> SystemControl
    KnobValues --> Reserved
```

The `str_from_knob_id()` method at [gpu/prc.py:114-123]() provides human-readable knob identification by combining enum names with numeric values in both decimal and hexadecimal formats.

**Sources:** [gpu/prc.py:26-47](), [gpu/prc.py:90-113](), [gpu/prc.py:114-123]()

## Bitfield Utilities

The `Bitfield` class provides structured access to hardware register bitfields, enabling safe manipulation of register contents through field-based operations rather than raw bit manipulation.

### Bitfield Class Architecture

```mermaid
graph TB
    BitfieldClass["`Bitfield Class
    utils/bitfield.py`"]
    
    subgraph "Core Methods"
        FieldGet["`__getitem__()
        Extract field values`"]
        FieldSet["`__setitem__()
        Set field values`"]
        GetMask["`__field_get_mask()
        Calculate field masks`"]
        GetShift["`__field_get_shift()
        Calculate bit shifts`"]
    end
    
    subgraph "Utility Methods"
        Values["`values()
        Return all field values`"]
        NonZero["`non_zero()
        Return non-zero fields`"]
        StrRepr["`__str__()
        String representation`"]
    end
    
    subgraph "Platform Support"
        LinuxFFS["`libc.ffs()
        Linux find-first-set`"]
        FallbackFFS["`Native ffs()
        Cross-platform fallback`"]
    end
    
    BitfieldClass --> FieldGet
    BitfieldClass --> FieldSet
    BitfieldClass --> GetMask
    BitfieldClass --> GetShift
    
    BitfieldClass --> Values
    BitfieldClass --> NonZero
    BitfieldClass --> StrRepr
    
    GetShift --> LinuxFFS
    GetShift --> FallbackFFS
```

### Field Definition System

Bitfield classes define their fields through a `fields` class attribute, supporting both single-bit and multi-bit field definitions:

- **Single-bit fields**: Defined as integer mask values
- **Multi-bit fields**: Defined as tuples `(high_bit, low_bit)` for bit ranges

The bitfield system automatically handles mask calculation and bit shifting through the internal methods at [utils/bitfield.py:47-63]().

### Platform Optimization

The bitfield system includes platform-specific optimizations for the find-first-set operation:

- **Linux**: Uses `libc.ffs()` for optimal performance [utils/bitfield.py:27-32]()
- **Other platforms**: Falls back to native Python implementation [utils/bitfield.py:34-35]()

**Sources:** [utils/bitfield.py:37-46](), [utils/bitfield.py:47-77](), [utils/bitfield.py:88-107](), [utils/bitfield.py:24-35]()

## Integration with GPU Management

The Configuration and Control system integrates with the broader GPU management infrastructure through multiple pathways:

```mermaid
graph TB
    subgraph "CLI Operations"
        PerGPU["`per_gpu.py
        GPU-specific operations`"]
        PerDevice["`per_device.py
        Device-level operations`"]
    end
    
    subgraph "Configuration and Control"
        PrcKnobs["`PrcKnob Enum
        Feature control knobs`"]
        Bitfields["`Bitfield Class
        Register field access`"]
        RegDefs["`Register Definitions
        Hardware register maps`"]
    end
    
    subgraph "GPU Core"
        GpuClass["`Gpu Class
        Primary GPU interface`"]
        FalconSystem["`Falcon Management
        Embedded controllers`"]
    end
    
    subgraph "Hardware Access"
        BAR0["`BAR0 Access
        Memory-mapped registers`"]
        ConfigSpace["`PCI Config Space
        Configuration registers`"]
        FalconRegs["`Falcon Registers
        Controller-specific regs`"]
    end
    
    PerGPU --> PrcKnobs
    PerDevice --> PrcKnobs
    
    GpuClass --> PrcKnobs
    GpuClass --> Bitfields
    GpuClass --> RegDefs
    
    FalconSystem --> Bitfields
    FalconSystem --> RegDefs
    
    PrcKnobs --> BAR0
    Bitfields --> BAR0
    RegDefs --> BAR0
    
    Bitfields --> ConfigSpace
    RegDefs --> ConfigSpace
    
    FalconSystem --> FalconRegs
```

The configuration system serves as the interface layer between high-level GPU management operations and low-level hardware access, providing:

- **Type-safe configuration**: PRC knobs ensure valid feature control operations
- **Structured register access**: Bitfield utilities prevent register corruption
- **Cross-architecture support**: Register definitions abstract hardware differences
- **Debugging support**: Comprehensive field inspection and string representation

**Sources:** [gpu/prc.py:114-123](), [utils/bitfield.py:79-107]()

---

