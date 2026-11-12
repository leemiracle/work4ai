<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/open-gpu-doc · extra page Display Core Interface · fetched 2026-10-26 -->

# Display Core Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [classes/display/cl907d.h](classes/display/cl907d.h)
- [classes/display/cl917d.h](classes/display/cl917d.h)
- [classes/display/cl927d.h](classes/display/cl927d.h)
- [classes/display/cl947d.h](classes/display/cl947d.h)
- [classes/display/cl957d.h](classes/display/cl957d.h)
- [classes/display/cl977d.h](classes/display/cl977d.h)
- [classes/display/cl987d.h](classes/display/cl987d.h)
- [classes/display/clc37d.h](classes/display/clc37d.h)

</details>



The Display Core Interface provides the primary DMA-based communication channel between software and the GPU's display engine hardware. This interface handles command submission, hardware capability discovery, completion notifications, and synchronization across different display components like windows, cursors, and output resources.

For information about specific display control channels (window, cursor, immediate), see [Display Control Channels](#3.2.4). For display hardware capabilities and InfoFrame control, see [Display Capabilities and InfoFrame Control](#3.2.2).

## Core Channel Classes

The Display Core Interface is implemented through hardware classes that vary by GPU generation. Each generation provides a DMA channel class with a unique identifier for core display operations.

```mermaid
graph TB
    subgraph "GPU Generation Classes"
        NV907D["NV907D_CORE_CHANNEL_DMA<br/>0x0000907D<br/>Tesla/Fermi"]
        NV917D["NV917D_CORE_CHANNEL_DMA<br/>0x0000917D<br/>Kepler"]
        NV927D["NV927D_CORE_CHANNEL_DMA<br/>0x0000927D<br/>Maxwell"]
        NV947D["NV947D_CORE_CHANNEL_DMA<br/>0x0000947D<br/>Pascal"]
        NV957D["NV957D_CORE_CHANNEL_DMA<br/>0x0000957D<br/>Volta"]
        NV977D["NV977D_CORE_CHANNEL_DMA<br/>0x0000977D<br/>Turing"]
        NV987D["NV987D_CORE_CHANNEL_DMA<br/>0x0000987D<br/>Ampere"]
        NVC37D["NVC37D_CORE_CHANNEL_DMA<br/>0x0000C37D<br/>Ada/Hopper"]
    end
    
    subgraph "Common Interface"
        NOTIFIER["CORE_NOTIFIER_3<br/>Completion & Capabilities"]
        DMA_OPS["DMA Operations<br/>Command Submission"]
        SYNC["Synchronization<br/>Lock Pins & Interlocks"]
    end
    
    NV907D --> NOTIFIER
    NV917D --> NOTIFIER
    NV927D --> NOTIFIER
    NV947D --> NOTIFIER
    NV957D --> NOTIFIER
    NV977D --> NOTIFIER
    NV987D --> NOTIFIER
    NVC37D --> NOTIFIER
    
    NVC37D --> DMA_OPS
    NVC37D --> SYNC
```

Sources: [classes/display/cl907d.h:32-32](), [classes/display/cl917d.h:33-33](), [classes/display/cl927d.h:33-33](), [classes/display/cl947d.h:33-33](), [classes/display/cl957d.h:33-33](), [classes/display/cl977d.h:33-33](), [classes/display/cl987d.h:33-33](), [classes/display/clc37d.h:33-33]()

## DMA Command Interface

The core display channel uses a push buffer DMA mechanism for command submission. Commands are structured with specific opcodes and can target different display subsystems.

```mermaid
graph LR
    subgraph "Command Structure"
        CMD["DMA Command"]
        OPCODE["DMA_OPCODE[31:29]<br/>METHOD/JUMP/NONINC_METHOD<br/>SET_SUBDEVICE_MASK"]
        COUNT["METHOD_COUNT[27:18]"]
        OFFSET["METHOD_OFFSET[13:2]"]
        DATA["DMA_DATA[31:0]"]
    end
    
    subgraph "Queue Management"
        PUT["PUT[9:0]<br/>Write Pointer"]
        GET["GET[9:0]<br/>Read Pointer"]
        UPDATE["UPDATE Method<br/>Command Submission"]
    end
    
    subgraph "Command Types"
        FLIP["Flip Operations<br/>FLIP_LOCK_PIN"]
        NOTIFY["Notifications<br/>SET_NOTIFIER_CONTROL"]
        INTERLOCK["Interlocks<br/>SET_INTERLOCK_FLAGS"]
    end
    
    CMD --> OPCODE
    CMD --> COUNT
    CMD --> OFFSET
    CMD --> DATA
    
    PUT --> UPDATE
    GET --> UPDATE
    
    UPDATE --> FLIP
    UPDATE --> NOTIFY
    UPDATE --> INTERLOCK
```

Sources: [classes/display/clc37d.h:59-70](), [classes/display/clc37d.h:77-95](), [classes/display/clc37d.h:127-136]()

## Notification System

The notification system provides completion tracking and hardware capability reporting through a structured notifier interface. Each core channel maintains a notifier structure in memory that software can poll or receive interrupts for.

### Notifier Structure

| Offset | Field | Purpose |
|--------|-------|---------|
| 0x00 | `COMPLETION_0` | Operation completion status and timestamp |
| 0x04-0x0C | Reserved | Additional completion data |
| 0x10+ | `CAPABILITIES_4+` | Hardware capability flags |
| 0x30+ | `CAP_DAC*` | DAC output capabilities |
| 0x50+ | `CAP_SOR*` | Serial Output Resource capabilities |

```mermaid
graph TB
    subgraph "Notifier Memory Layout"
        COMP["COMPLETION_0<br/>DONE[0:0]<br/>TIMESTAMP[29:16]"]
        CAP4["CAPABILITIES_4<br/>VM_USABLE4ISO[1:1]<br/>FOS_FETCH_X4AA[20:20]<br/>FLIP_LOCK_PIN*USABLE[31:30]"]
        CAP5["CAPABILITIES_5<br/>LOCK_PIN*USAGE[31:0]<br/>SCAN_LOCK/FLIP_LOCK/STEREO"]
        CAPS_DAC["CAP_DAC0-3<br/>RGB_USABLE[0:0]<br/>TV_USABLE[1:1]<br/>CRT_CLK_MAX[7:0]"]
        CAPS_SOR["CAP_SOR0-5<br/>LVDS18/LVDS24[1:0]<br/>TMDS_A/TMDS_B[9:8]<br/>DP_A/DP_B[25:24]"]
    end
    
    subgraph "Software Interface"
        POLL["Polling Interface<br/>Check DONE flags"]
        INT["Interrupt Interface<br/>AWAKEN mode"]
        CAPS["Capability Discovery<br/>Read hardware limits"]
    end
    
    COMP --> POLL
    COMP --> INT
    CAP4 --> CAPS
    CAP5 --> CAPS
    CAPS_DAC --> CAPS
    CAPS_SOR --> CAPS
```

Sources: [classes/display/cl917d.h:35-49](), [classes/display/cl917d.h:49-69](), [classes/display/cl917d.h:163-218](), [classes/display/cl917d.h:219-390]()

## Hardware Capability Discovery

The notification system exposes detailed hardware capabilities that software can query to determine available display features and limits.

### DAC Capabilities

The Digital-to-Analog Converter capabilities indicate supported output modes and frequency limits:

- `RGB_USABLE`: Standard RGB output support
- `TV_USABLE`: Television/composite output support  
- `SCART_USABLE`: SCART connector support
- `CRT_CLK_MAX`: Maximum pixel clock for CRT outputs

### SOR Capabilities

Serial Output Resource capabilities cover digital display interfaces:

- **LVDS**: Single/dual channel 18-bit and 24-bit LVDS support
- **TMDS**: Single/dual link TMDS for DVI/HDMI (channels A/B)
- **DisplayPort**: DisplayPort A/B channel support with interlace capability
- **Clock Limits**: Maximum pixel clocks for each interface type

```mermaid
graph LR
    subgraph "Capability Types"
        DAC_CAPS["DAC Capabilities<br/>RGB/TV/SCART<br/>CRT_CLK_MAX"]
        SOR_CAPS["SOR Capabilities<br/>LVDS/TMDS/DP<br/>Clock Limits"]
        LOCK_CAPS["Lock Pin Capabilities<br/>SCAN_LOCK<br/>FLIP_LOCK<br/>STEREO"]
        MEM_CAPS["Memory Capabilities<br/>VM_USABLE4ISO<br/>NVM_USABLE4ISO"]
    end
    
    subgraph "Discovery Flow"
        READ_NOTIFIER["Read Notifier<br/>Wait for DONE=TRUE"]
        PARSE_CAPS["Parse Capability Bits<br/>Extract Supported Features"]
        CONFIG_HW["Configure Hardware<br/>Based on Capabilities"]
    end
    
    DAC_CAPS --> READ_NOTIFIER
    SOR_CAPS --> READ_NOTIFIER
    LOCK_CAPS --> READ_NOTIFIER
    MEM_CAPS --> READ_NOTIFIER
    
    READ_NOTIFIER --> PARSE_CAPS
    PARSE_CAPS --> CONFIG_HW
```

Sources: [classes/display/cl917d.h:163-218](), [classes/display/cl917d.h:219-304](), [classes/display/cl917d.h:49-69](), [classes/display/cl917d.h:70-151]()

## Synchronization and Interlocking

The Display Core Interface provides sophisticated synchronization mechanisms to coordinate operations across multiple display components.

### Lock Pin Management

Lock pins provide hardware-level synchronization for display timing:

| Lock Pin Type | Usage | Description |
|---------------|-------|-------------|
| `SCAN_LOCK` | Vertical synchronization | Locks to display scanout timing |
| `FLIP_LOCK` | Page flip synchronization | Coordinates buffer flips across heads |
| `STEREO` | Stereoscopic display | Synchronizes left/right eye timing |

### Interlock Mechanisms

The system supports interlocking between different display subsystems:

```mermaid
graph TB
    subgraph "Core Channel Coordination"
        CORE["Core Channel<br/>NVC37D_UPDATE"]
        FLIP_PINS["Flip Lock Pins<br/>LOCK_PIN_0 to LOCK_PIN_F<br/>INTERNAL_FLIP_LOCK_*"]
        SCAN_PINS["Scan Lock Pins<br/>INTERNAL_SCAN_LOCK_*"]
    end
    
    subgraph "Interlock Targets"
        CURSORS["Cursor Channels<br/>INTERLOCK_WITH_CURSOR0-7"]
        WINDOWS["Window Channels<br/>INTERLOCK_WITH_WINDOW0-31"]
        CORE_LOCK["Core Interlock<br/>INTERLOCK_WITH_CORE"]
    end
    
    subgraph "Synchronization Flow"
        SET_INTERLOCK["SET_INTERLOCK_FLAGS<br/>Configure Dependencies"]
        UPDATE_CMD["UPDATE Command<br/>FLIP_LOCK_PIN selection"]
        HW_SYNC["Hardware Synchronization<br/>Atomic Updates"]
    end
    
    CORE --> FLIP_PINS
    CORE --> SCAN_PINS
    
    FLIP_PINS --> SET_INTERLOCK
    SCAN_PINS --> SET_INTERLOCK
    
    SET_INTERLOCK --> CURSORS
    SET_INTERLOCK --> WINDOWS
    SET_INTERLOCK --> CORE_LOCK
    
    SET_INTERLOCK --> UPDATE_CMD
    UPDATE_CMD --> HW_SYNC
```

Sources: [classes/display/clc37d.h:93-126](), [classes/display/clc37d.h:154-182](), [classes/display/clc37d.h:186-277](), [classes/display/cl917d.h:70-151]()

---

