<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/open-gpu-doc · extra page Display Capabilities and InfoFrame Control · fetched 2026-10-26 -->

# Display Capabilities and InfoFrame Control

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [classes/display/cl9171.h](classes/display/cl9171.h)
- [classes/display/cl9271.h](classes/display/cl9271.h)
- [classes/display/cl9471.h](classes/display/cl9471.h)
- [classes/display/cl9571.h](classes/display/cl9571.h)
- [classes/display/clc371.h](classes/display/clc371.h)
- [classes/display/clc573.h](classes/display/clc573.h)
- [classes/display/clc57a.h](classes/display/clc57a.h)
- [classes/display/clc57b.h](classes/display/clc57b.h)
- [classes/display/clc671.h](classes/display/clc671.h)
- [classes/display/clc673.h](classes/display/clc673.h)

</details>



This document covers the display subsystem's hardware capability reporting and HDMI InfoFrame signaling interfaces. These systems enable software to query available display hardware features and control video metadata transmission over HDMI connections.

For information about core display channel operation, see [Display Core Interface](#3.2.3). For window and cursor control mechanisms, see [Display Control Channels](#3.2.4).

## Purpose and Scope

The display capabilities system provides standardized interfaces for discovering hardware features across different GPU generations, including heads, SORs (Serial Output Resources), windows, and post-composition processing units. The InfoFrame control system manages HDMI metadata packet transmission, including AVI InfoFrames, General Control Packets, and Vendor Specific InfoFrames.

## Display Capabilities Architecture

The display capabilities system uses dedicated hardware classes to report available display features and their specifications. Different GPU generations implement varying capability sets through versioned class interfaces.

```mermaid
graph TB
    subgraph "Display Capabilities Classes"
        NVC573["NVC573_DISP_CAPABILITIES<br/>Class 0xC573"]
        NVC673["NVC673_DISP_CAPABILITIES<br/>Class 0xC673"]
    end
    
    subgraph "Capability Categories"
        SYS_CAP["SYS_CAP<br/>System Capabilities"]
        IHUB_CAP["IHUB_COMMON_CAPA<br/>Input Hub Capabilities"]
        POSTCOMP_CAP["POSTCOMP_HEAD_HDR_CAPA<br/>Post-Compositor Capabilities"]
        SOR_CAP["SOR_CAP<br/>Serial Output Capabilities"]
    end
    
    subgraph "Hardware Resources"
        HEADS["Display Heads<br/>HEAD0-HEAD7"]
        SORS["Serial Outputs<br/>SOR0-SOR7"]
        WINDOWS["Display Windows<br/>WINDOW0-WINDOW31"]
        DSI["DSI Controllers<br/>DSI0-DSI3"]
    end
    
    NVC573 --> SYS_CAP
    NVC673 --> SYS_CAP
    NVC573 --> IHUB_CAP
    NVC673 --> IHUB_CAP
    NVC573 --> POSTCOMP_CAP
    NVC673 --> POSTCOMP_CAP
    NVC573 --> SOR_CAP
    NVC673 --> SOR_CAP
    
    SYS_CAP --> HEADS
    SYS_CAP --> SORS
    SYS_CAP --> WINDOWS
    SYS_CAP --> DSI
```

Sources: [classes/display/clc573.h:31-35](), [classes/display/clc673.h:31-35](), [classes/display/clc573.h:38-112](), [classes/display/clc673.h:38-110]()

### System Capabilities

The `SYS_CAP` register provides basic existence flags for display hardware components. Each bit indicates whether a specific resource is present and functional.

| Capability Type | Register Fields | Purpose |
|----------------|----------------|----------|
| Display Heads | `HEAD0_EXISTS` - `HEAD7_EXISTS` | Available display output heads |
| Serial Outputs | `SOR0_EXISTS` - `SOR7_EXISTS` | HDMI/DP/LVDS output controllers |
| Windows | `WINDOW0_EXISTS` - `WINDOW31_EXISTS` | Overlay/composition windows |
| DSI Controllers | `DSI0_EXISTS` - `DSI3_EXISTS` | MIPI DSI interface controllers |

Sources: [classes/display/clc573.h:38-112](), [classes/display/clc673.h:38-110]()

### Input Hub Capabilities

The IHUB capabilities describe memory management and processing features for display input handling.

```mermaid
graph LR
    subgraph "IHUB_COMMON_CAPA Features"
        MEMPOOL["Memory Pool<br/>Entries & Width"]
        COMPRESSION["Compression Support<br/>MEMPOOL_COMPRESSION"]
        FORMATS["Format Support<br/>PLANAR, VGA"]
        PROCESSING["Processing Features<br/>ROTATION, MSCG"]
    end
    
    subgraph "Memory Management"
        POOL_ENTRIES["MEMPOOL_ENTRIES<br/>15:0"]
        ENTRY_WIDTH["MEMPOOL_ENTRY_WIDTH<br/>32B/64B/128B/256B"]
        REQUEST_SIZE["REQUEST_SIZE_PER_LINE<br/>Non-rotation"]
    end
    
    MEMPOOL --> POOL_ENTRIES
    MEMPOOL --> ENTRY_WIDTH
    MEMPOOL --> REQUEST_SIZE
```

Sources: [classes/display/clc573.h:247-285](), [classes/display/clc673.h:212-244]()

### Post-Compositor Capabilities

Post-compositor capabilities define available processing units in the display output pipeline.

| Processing Unit | Register Field | Description |
|----------------|----------------|-------------|
| Output Color Space Converter | `OCSC0_PRESENT`, `OCSC1_PRESENT` | Color space conversion |
| Scaler | `SCLR_PRESENT` | Image scaling and filtering |
| Output Low-Pass Filter | `OLPF_PRESENT` | Anti-aliasing filter |
| Dithering | `DTH_PRESENT` | Color depth reduction |
| Overscan | `OSCAN_PRESENT` | Display area adjustment |
| Display Stream Compression | `DSC_PRESENT` | Bandwidth compression |

Sources: [classes/display/clc573.h:286-387](), [classes/display/clc673.h:263-341]()

## InfoFrame Control System

The InfoFrame control system manages HDMI metadata packet transmission through dedicated hardware classes. Different generations provide varying levels of InfoFrame support and control granularity.

```mermaid
graph TB
    subgraph "InfoFrame Control Classes"
        NV9171["NV9171_DISP_SF_USER<br/>Class 0x9171"]
        NV9271["NV9271_DISP_SF_USER<br/>Class 0x9271"]
        NV9471["NV9471_DISP_SF_USER<br/>Class 0x9471"]
        NV9571["NV9571_DISP_SF_USER<br/>Class 0x9571"]
        NVC371["NVC371_DISP_SF_USER<br/>Class 0xC371"]
        NVC671["NVC671_DISP_SF_USER<br/>Class 0xC671"]
    end
    
    subgraph "InfoFrame Types"
        AVI["AVI InfoFrame<br/>Video Parameters"]
        GENERIC["Generic InfoFrame<br/>Custom Metadata"]
        GCP["General Control Packet<br/>AV Mute Control"]
        VSI["Vendor Specific InfoFrame<br/>Proprietary Data"]
    end
    
    subgraph "Control Registers"
        CTRL["SF_HDMI_INFO_CTRL<br/>Enable/Control"]
        STATUS["SF_HDMI_INFO_STATUS<br/>Transmission Status"]
        HEADER["INFOFRAME_HEADER<br/>Packet Header"]
        SUBPACK["INFOFRAME_SUBPACK<br/>Payload Data"]
    end
    
    NV9171 --> AVI
    NV9271 --> AVI
    NV9471 --> AVI
    NV9571 --> AVI
    NVC371 --> AVI
    NVC671 --> AVI
    
    AVI --> CTRL
    GENERIC --> CTRL
    GCP --> CTRL
    VSI --> CTRL
    
    CTRL --> STATUS
    CTRL --> HEADER
    CTRL --> SUBPACK
```

Sources: [classes/display/cl9171.h:31-35](), [classes/display/cl9271.h:31-35](), [classes/display/cl9471.h:31-35](), [classes/display/cl9571.h:31-35](), [classes/display/clc371.h:31-35](), [classes/display/clc671.h:31-35]()

### InfoFrame Packet Structure

Each InfoFrame type follows a standardized packet structure with header and payload sections.

```mermaid
graph LR
    subgraph "InfoFrame Packet Layout"
        HEADER_BYTES["Header Bytes<br/>HB0, HB1, HB2"]
        SUBPACK0["Subpacket 0<br/>PB0-PB6"]
        SUBPACK1["Subpacket 1<br/>PB7-PB13"]
        SUBPACK2["Subpacket 2<br/>PB14-PB20"]
        SUBPACK3["Subpacket 3<br/>PB21-PB27"]
    end
    
    subgraph "Control Fields"
        ENABLE["ENABLE<br/>0:0"]
        OTHER["OTHER<br/>4:4"]
        SINGLE["SINGLE<br/>8:8"]
        CHKSUM_HW["CHKSUM_HW<br/>9:9"]
        HBLANK["HBLANK<br/>12:12"]
        VIDEO_FMT["VIDEO_FMT<br/>16:16"]
    end
    
    HEADER_BYTES --> SUBPACK0
    SUBPACK0 --> SUBPACK1
    SUBPACK1 --> SUBPACK2
    SUBPACK2 --> SUBPACK3
```

Sources: [classes/display/cl9171.h:98-141](), [classes/display/cl9271.h:98-141](), [classes/display/cl9471.h:98-141]()

### AVI InfoFrame Control

The AVI InfoFrame carries video format and display parameters. The control interface provides enable/disable functionality and automatic checksum generation.

| Register | Field | Description |
|----------|-------|-------------|
| `SF_HDMI_AVI_INFOFRAME_CTRL` | `ENABLE` | Enable/disable AVI InfoFrame transmission |
| | `CHKSUM_HW` | Hardware checksum generation |
| | `SINGLE` | Single transmission mode |
| `SF_HDMI_AVI_INFOFRAME_STATUS` | `SENT` | Transmission completion status |
| `SF_HDMI_AVI_INFOFRAME_HEADER` | `HB0-HB2` | InfoFrame header bytes |
| `SF_HDMI_AVI_INFOFRAME_SUBPACK0_LOW` | `PB0-PB3` | Payload bytes 0-3 |
| `SF_HDMI_AVI_INFOFRAME_SUBPACK0_HIGH` | `PB4-PB6` | Payload bytes 4-6 |

Sources: [classes/display/cl9171.h:75-141](), [classes/display/clc671.h:42-118]()

### General Control Packet (GCP)

The GCP provides AV mute control and other general signaling functions.

```mermaid
graph LR
    subgraph "GCP Control"
        GCP_CTRL["SF_HDMI_INFO_CTRL<br/>Index: GCP"]
        GCP_SUBPACK["SF_HDMI_GCP_SUBPACK"]
    end
    
    subgraph "GCP Payload"
        SB0["SB0: Control Bits<br/>SET_AVMUTE/CLR_AVMUTE"]
        SB1["SB1: Reserved"]
        SB2["SB2: Reserved"]
    end
    
    GCP_CTRL --> GCP_SUBPACK
    GCP_SUBPACK --> SB0
    GCP_SUBPACK --> SB1
    GCP_SUBPACK --> SB2
```

Sources: [classes/display/cl9171.h:222-231](), [classes/display/cl9271.h:222-231]()

### Multi-Head InfoFrame Management

Modern display classes support per-head InfoFrame control with indexed access patterns.

```mermaid
graph TB
    subgraph "Multi-Head Architecture"
        HEAD0["Display Head 0<br/>Index 0"]
        HEAD1["Display Head 1<br/>Index 1"]
        HEAD2["Display Head 2<br/>Index 2"]
        HEAD3["Display Head 3<br/>Index 3"]
    end
    
    subgraph "InfoFrame Registers"
        CTRL_BASE["SF_HDMI_INFO_CTRL(i,j)<br/>Base + (i)*1024 + (j)*64"]
        STATUS_BASE["SF_HDMI_INFO_STATUS(i,j)<br/>Base + (i)*1024 + (j)*64"]
    end
    
    subgraph "InfoFrame Types (j)"
        AVI_IDX["j=0: AVI InfoFrame"]
        GENERIC_IDX["j=1: Generic InfoFrame"]
        GCP_IDX["j=3: General Control Packet"]
        VSI_IDX["j=4: Vendor Specific InfoFrame"]
    end
    
    HEAD0 --> CTRL_BASE
    HEAD1 --> CTRL_BASE
    HEAD2 --> CTRL_BASE
    HEAD3 --> CTRL_BASE
    
    CTRL_BASE --> STATUS_BASE
    CTRL_BASE --> AVI_IDX
    CTRL_BASE --> GENERIC_IDX
    CTRL_BASE --> GCP_IDX
    CTRL_BASE --> VSI_IDX
```

Sources: [classes/display/cl9171.h:41-74](), [classes/display/cl9271.h:41-74](), [classes/display/cl9471.h:41-74]()

## Hardware Generation Mapping

Different GPU architectures implement varying levels of display capabilities and InfoFrame support.

| GPU Generation | Capabilities Class | InfoFrame Class | Key Features |
|---------------|-------------------|-----------------|--------------|
| Turing | `NVC573` | `NV9171`, `NV9271`, `NV9471`, `NV9571` | Basic capability reporting, full InfoFrame support |
| Ampere | `NVC673` | `NVC371`, `NVC671` | Enhanced capabilities, rotation support, simplified InfoFrame control |

The newer generations provide additional capability flags such as rotation support (`SUPPORT_ROTATION`) and enhanced processing features while maintaining backward compatibility for core InfoFrame functionality.

Sources: [classes/display/clc573.h:31](), [classes/display/clc673.h:31](), [classes/display/clc371.h:31](), [classes/display/clc671.h:31]()

---

