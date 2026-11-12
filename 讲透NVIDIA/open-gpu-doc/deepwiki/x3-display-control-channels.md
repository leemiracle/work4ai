<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/open-gpu-doc · extra page Display Control Channels · fetched 2026-10-26 -->

# Display Control Channels

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [classes/display/cl907dcrcnotif.h](classes/display/cl907dcrcnotif.h)
- [classes/display/cl917c.h](classes/display/cl917c.h)
- [classes/display/cl917dcrcnotif.h](classes/display/cl917dcrcnotif.h)
- [classes/display/cl917e.h](classes/display/cl917e.h)
- [classes/display/cl927c.h](classes/display/cl927c.h)
- [classes/display/cl927dcrcnotif.h](classes/display/cl927dcrcnotif.h)
- [classes/display/clc37a.h](classes/display/clc37a.h)
- [classes/display/clc37b.h](classes/display/clc37b.h)
- [classes/display/clc37dcrcnotif.h](classes/display/clc37dcrcnotif.h)
- [classes/display/clc67a.h](classes/display/clc67a.h)
- [classes/display/clc67b.h](classes/display/clc67b.h)
- [classes/display/clc67d.h](classes/display/clc67d.h)
- [classes/display/clc67e.h](classes/display/clc67e.h)

</details>



This document covers the display control channel interfaces that provide software control over GPU display hardware subsystems. These channels offer both DMA-based and PIO-based programming interfaces for managing display output, window composition, and cursor positioning across different GPU generations.

For information about display capabilities and InfoFrame signaling, see [Display Capabilities and InfoFrame Control](#3.2.2). For details about the core display channel DMA interface, see [Display Core Interface](#3.2.3).

## Channel Types and Interface Mechanisms

The display subsystem provides multiple specialized control channels, each designed for specific display functions. These channels use either DMA (Direct Memory Access) or PIO (Programmed Input/Output) mechanisms for hardware communication.

```mermaid
graph TB
    subgraph "Display Control Architecture"
        subgraph "Core Display Control"
            CORE["NVC67D_CORE_CHANNEL_DMA<br/>Core Display Channel<br/>0xC67D"]
        end
        
        subgraph "Window/Overlay Control"
            WINDOW_DMA["NVC67E_WINDOW_CHANNEL_DMA<br/>Window Channel<br/>0xC67E"]
            WINDOW_IMM["NVC67B_WINDOW_IMM_CHANNEL_DMA<br/>Window Immediate<br/>0xC67B"]
        end
        
        subgraph "Cursor Control"
            CURSOR_PIO["NVC67A_CURSOR_IMM_CHANNEL_PIO<br/>Cursor Immediate<br/>0xC67A"]
        end
        
        subgraph "Interface Types"
            DMA_IF["DMA Interface<br/>Command Buffer Processing"]
            PIO_IF["PIO Interface<br/>Direct Register Access"]
        end
    end
    
    CORE --> DMA_IF
    WINDOW_DMA --> DMA_IF
    WINDOW_IMM --> DMA_IF
    CURSOR_PIO --> PIO_IF
```

**Sources:** [classes/display/clc67d.h:32](), [classes/display/clc67e.h:32](), [classes/display/clc67b.h:32](), [classes/display/clc67a.h:31]()

### Channel Interface Summary

| Channel Type | Class ID | Interface | Primary Function |
|--------------|----------|-----------|------------------|
| Core Display | `NVC67D_CORE_CHANNEL_DMA` | DMA | Display controller coordination, output routing |
| Window Channel | `NVC67E_WINDOW_CHANNEL_DMA` | DMA | Surface composition, scaling, format conversion |
| Window Immediate | `NVC67B_WINDOW_IMM_CHANNEL_DMA` | DMA | Fast window position updates |
| Cursor Immediate | `NVC67A_CURSOR_IMM_CHANNEL_PIO` | PIO | Cursor positioning and control |

**Sources:** [classes/display/clc67d.h:32](), [classes/display/clc67e.h:32](), [classes/display/clc67b.h:32](), [classes/display/clc67a.h:31]()

## DMA Command Processing

DMA-based channels use a common command format for method calls, providing efficient batch processing of display operations through command buffers.

```mermaid
graph LR
    subgraph "DMA Command Structure"
        CMD["DMA Command<br/>32-bit Word"]
        OPCODE["OPCODE[31:29]<br/>Command Type"]
        METHOD_OFFSET["METHOD_OFFSET[13:2]<br/>Register Address"]
        METHOD_COUNT["METHOD_COUNT[27:18]<br/>Data Count"]
        DATA["DATA[31:0]<br/>Method Data"]
    end
    
    CMD --> OPCODE
    CMD --> METHOD_OFFSET
    CMD --> METHOD_COUNT
    CMD --> DATA
    
    subgraph "Opcode Types"
        OP_METHOD["METHOD (0x0)<br/>Single Method Call"]
        OP_NONINC["NONINC_METHOD (0x2)<br/>Multiple Data to Same Method"]
        OP_JUMP["JUMP (0x1)<br/>Command Buffer Jump"]
        OP_SUBMASK["SET_SUBDEVICE_MASK (0x3)<br/>Multi-GPU Targeting"]
    end
    
    OPCODE --> OP_METHOD
    OPCODE --> OP_NONINC
    OPCODE --> OP_JUMP
    OPCODE --> OP_SUBMASK
```

**Sources:** [classes/display/clc67d.h:58-69](), [classes/display/clc67e.h:35-46]()

### Common DMA Methods

All DMA channels implement standard command buffer control methods:

| Method | Offset | Purpose |
|--------|--------|---------|
| `PUT` | `0x000` | Command buffer write pointer |
| `GET` | `0x004` | Command buffer read pointer |
| `UPDATE` | `0x200` | Channel update and synchronization |

**Sources:** [classes/display/clc67d.h:76-80](), [classes/display/clc67e.h:49-53]()

## Core Display Channel

The `NVC67D_CORE_CHANNEL_DMA` provides centralized control over display output routing, head management, and cross-channel synchronization.

### Core Channel Responsibilities

```mermaid
graph TB
    subgraph "Core Display Functions"
        CORE_CTRL["Core Channel Control<br/>NVC67D_CORE_CHANNEL_DMA"]
        
        subgraph "Output Management"
            SOR_CTRL["SOR Control<br/>NVC67D_SOR_SET_CONTROL"]
            DSI_CTRL["DSI Control<br/>NVC67D_DSI_SET_CONTROL"]
            BLANK_CTRL["Blanking Control<br/>NVC67D_SET_GET_BLANKING_CTRL"]
        end
        
        subgraph "Window Coordination"
            WIN_CTRL["Window Control<br/>NVC67D_WINDOW_SET_CONTROL"]
            WIN_INTERLOCK["Window Interlocks<br/>NVC67D_SET_WINDOW_INTERLOCK_FLAGS"]
        end
        
        subgraph "Synchronization"
            FLIP_LOCK["Flip Lock Control<br/>NVC67D_SET_CONTROL"]
            SCAN_LINE["Scan Line Status<br/>NVC67D_GET_RG_SCAN_LINE"]
        end
    end
    
    CORE_CTRL --> SOR_CTRL
    CORE_CTRL --> DSI_CTRL
    CORE_CTRL --> BLANK_CTRL
    CORE_CTRL --> WIN_CTRL
    CORE_CTRL --> WIN_INTERLOCK
    CORE_CTRL --> FLIP_LOCK
    CORE_CTRL --> SCAN_LINE
```

**Sources:** [classes/display/clc67d.h:299-349](), [classes/display/clc67d.h:351-363](), [classes/display/clc67d.h:185-285]()

### Serial Output Resource (SOR) Control

The core channel manages SOR units that handle different display protocols:

```mermaid
graph LR
    subgraph "SOR Protocol Support"
        SOR["SOR Control<br/>NVC67D_SOR_SET_CONTROL"]
        
        subgraph "Supported Protocols"
            LVDS["LVDS_CUSTOM<br/>0x0"]
            TMDS_A["SINGLE_TMDS_A<br/>0x1"]
            TMDS_B["SINGLE_TMDS_B<br/>0x2"]
            DUAL_TMDS["DUAL_TMDS<br/>0x5"]
            DP_A["DP_A<br/>0x8"]
            DP_B["DP_B<br/>0x9"]
            HDMI_FRL["HDMI_FRL<br/>0xC"]
        end
        
        subgraph "Head Assignment"
            HEAD_MASK["OWNER_MASK[7:0]<br/>Multi-head Support"]
        end
    end
    
    SOR --> LVDS
    SOR --> TMDS_A
    SOR --> TMDS_B
    SOR --> DUAL_TMDS
    SOR --> DP_A
    SOR --> DP_B
    SOR --> HDMI_FRL
    SOR --> HEAD_MASK
```

**Sources:** [classes/display/clc67d.h:299-331]()

## Window Control Channels

Window channels manage overlay surfaces, providing composition, scaling, and format conversion capabilities. Two types of window channels are available: full-featured DMA channels and immediate update channels.

### Window Channel DMA

The `NVC67E_WINDOW_CHANNEL_DMA` provides comprehensive surface management:

| Function Category | Key Methods | Purpose |
|------------------|-------------|---------|
| Surface Configuration | `SET_SIZE`, `SET_STORAGE`, `SET_PARAMS` | Surface dimensions and format |
| Memory Management | `SET_CONTEXT_DMA_ISO`, `SET_OFFSET` | Surface memory binding |
| Scaling | `SET_SIZE_IN`, `SET_SIZE_OUT`, `SET_CONTROL_INPUT_SCALER` | Input/output scaling |
| Composition | `SET_COMPOSITION_CONTROL`, `SET_COMPOSITION_FACTOR_SELECT` | Alpha blending control |
| Color Processing | `SET_KEY_ALPHA`, `SET_KEY_RED_CR` | Color keying |

**Sources:** [classes/display/clc67e.h:126-128](), [classes/display/clc67e.h:175-176](), [classes/display/clc67e.h:186-191](), [classes/display/clc67e.h:202-266]()

### Window Immediate Channel

The `NVC67B_WINDOW_IMM_CHANNEL_DMA` provides fast position updates for time-critical operations:

```mermaid
graph TB
    subgraph "Window Immediate Interface"
        IMM_CHAN["NVC67B_WINDOW_IMM_CHANNEL_DMA<br/>Fast Position Updates"]
        
        subgraph "Available Methods"
            UPDATE_IMM["UPDATE<br/>Channel synchronization"]
            POINT_OUT["SET_POINT_OUT<br/>Window position"]
            INTERLOCK_WIN["UPDATE_INTERLOCK_WITH_WINDOW<br/>Cross-window sync"]
        end
        
        subgraph "Position Control"
            X_COORD["X[15:0]<br/>Horizontal position"]
            Y_COORD["Y[31:16]<br/>Vertical position"]
        end
    end
    
    IMM_CHAN --> UPDATE_IMM
    IMM_CHAN --> POINT_OUT
    IMM_CHAN --> INTERLOCK_WIN
    POINT_OUT --> X_COORD
    POINT_OUT --> Y_COORD
```

**Sources:** [classes/display/clc67b.h:53-63]()

## Cursor Control Channel

The `NVC67A_CURSOR_IMM_CHANNEL_PIO` provides real-time cursor positioning through direct register access, optimized for minimal latency.

### Cursor PIO Interface

```mermaid
graph TB
    subgraph "Cursor PIO Control Structure"
        PIO_STRUCT["NVC67ADispCursorImmControlPio<br/>Volatile Register Structure"]
        
        subgraph "Control Methods"
            FREE_REG["Free[0x008]<br/>Available command space"]
            UPDATE_REG["Update[0x200]<br/>Cursor update trigger"]
            INTERLOCK_REG["SetInterlockFlags[0x204]<br/>Synchronization control"]
            HOTSPOT_REG["SetCursorHotSpotPointOut[0x208-0x20F]<br/>Cursor hotspot position"]
            WIN_INTERLOCK_REG["SetWindowInterlockFlags[0x210]<br/>Window synchronization"]
        end
        
        subgraph "Flip Lock Support"
            FLIP_PINS["FLIP_LOCK_PIN[8:4]<br/>External sync pins"]
            INTERNAL_LOCKS["INTERNAL_FLIP_LOCK<br/>Internal sync signals"]
            SCAN_LOCKS["INTERNAL_SCAN_LOCK<br/>Scan-based sync"]
        end
    end
    
    PIO_STRUCT --> FREE_REG
    PIO_STRUCT --> UPDATE_REG
    PIO_STRUCT --> INTERLOCK_REG
    PIO_STRUCT --> HOTSPOT_REG
    PIO_STRUCT --> WIN_INTERLOCK_REG
    UPDATE_REG --> FLIP_PINS
    UPDATE_REG --> INTERNAL_LOCKS
    UPDATE_REG --> SCAN_LOCKS
```

**Sources:** [classes/display/clc67a.h:33-42](), [classes/display/clc67a.h:46-79]()

### Cursor Position Control

The cursor hotspot defines the active point of the cursor relative to its surface:

| Register | Bit Fields | Function |
|----------|------------|----------|
| `SET_CURSOR_HOT_SPOT_POINT_OUT[0]` | `X[15:0]`, `Y[31:16]` | Primary hotspot position |
| `SET_CURSOR_HOT_SPOT_POINT_OUT[1]` | `X[15:0]`, `Y[31:16]` | Secondary hotspot position |

**Sources:** [classes/display/clc67a.h:108-110]()

## Channel Synchronization and Interlocks

Display channels implement sophisticated synchronization mechanisms to ensure tear-free updates and coordinate between multiple display elements.

### Interlock Mechanisms

```mermaid
graph TB
    subgraph "Display Channel Interlocks"
        subgraph "Core Channel Interlocks"
            CORE_WIN["Core ↔ Window<br/>NVC67D_SET_WINDOW_INTERLOCK_FLAGS"]
            CORE_CURSOR["Core ↔ Cursor<br/>NVC67D_SET_INTERLOCK_FLAGS"]
            CORE_CORE["Core ↔ Core<br/>INTERLOCK_WITH_CORE"]
        end
        
        subgraph "Window Channel Interlocks"
            WIN_CORE["Window ↔ Core<br/>NVC67E_SET_INTERLOCK_FLAGS"]
            WIN_CURSOR["Window ↔ Cursor<br/>INTERLOCK_WITH_CURSOR"]
            WIN_WIN["Window ↔ Window<br/>SET_WINDOW_INTERLOCK_FLAGS"]
        end
        
        subgraph "Cursor Channel Interlocks"
            CURSOR_CORE["Cursor ↔ Core<br/>NVC67A_SET_INTERLOCK_FLAGS"]
            CURSOR_WIN["Cursor ↔ Window<br/>SET_WINDOW_INTERLOCK_FLAGS"]
            CURSOR_CURSOR["Cursor ↔ Cursor<br/>INTERLOCK_WITH_CURSOR"]
        end
        
        subgraph "Flip Lock Coordination"
            EXT_PINS["External Pins<br/>LOCK_PIN_0 through LOCK_PIN_F"]
            INT_FLIP["Internal Flip Locks<br/>INTERNAL_FLIP_LOCK_0-3"]
            SCAN_LOCK["Scan Locks<br/>INTERNAL_SCAN_LOCK_0-7"]
        end
    end
    
    CORE_WIN -.-> WIN_CORE
    CORE_CURSOR -.-> CURSOR_CORE
    WIN_CURSOR -.-> CURSOR_WIN
```

**Sources:** [classes/display/clc67d.h:153-285](), [classes/display/clc67e.h:324-455](), [classes/display/clc67a.h:80-207]()

### Notification and Semaphore Support

DMA channels support completion notifications and semaphore-based synchronization:

| Mechanism | Window Channel | Core Channel | Purpose |
|-----------|----------------|--------------|---------|
| Context DMA Notifier | `SET_CONTEXT_DMA_NOTIFIER` | `SET_CONTEXT_DMA_NOTIFIER` | Completion notification |
| Semaphore Acquire | `SET_SEMAPHORE_ACQUIRE` | N/A | Pre-execution sync |
| Semaphore Release | `SET_SEMAPHORE_RELEASE` | N/A | Post-execution sync |
| Semaphore Control | `SET_SEMAPHORE_CONTROL` | N/A | Sync configuration |

**Sources:** [classes/display/clc67e.h:113-118](), [classes/display/clc67e.h:291-305](), [classes/display/clc67d.h:126-135]()

## GPU Generation Variations

Different GPU generations implement variations of these channel interfaces while maintaining backward compatibility:

| Generation | Core Channel | Window Channel | Cursor Channel | Notable Changes |
|------------|--------------|----------------|----------------|-----------------|
| Volta (C37x) | `NVC37D` | `NVC37E` | `NVC37A` | Basic interlock support |
| Turing (C67x) | `NVC67D` | `NVC67E` | `NVC67A` | Enhanced flip lock mechanisms |
| Ampere (917x, 927x) | `NV917D`, `NV927D` | `NV917E` | N/A | Advanced color processing |

**Sources:** [classes/display/clc37a.h:32](), [classes/display/cl917c.h:33](), [classes/display/cl927c.h:33]()

---

