<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/open-gpu-doc · page 2 GPU Hardware Architecture · fetched 2026-10-26 -->

# GPU Hardware Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [manuals/ampere/ga100/dev_ctxsw.ref.txt](manuals/ampere/ga100/dev_ctxsw.ref.txt)
- [manuals/ampere/ga100/dev_nv_xve3g_fn0.ref.txt](manuals/ampere/ga100/dev_nv_xve3g_fn0.ref.txt)
- [manuals/ampere/ga100/dev_nv_xve3g_fn1.ref.txt](manuals/ampere/ga100/dev_nv_xve3g_fn1.ref.txt)
- [manuals/ampere/ga100/index.html](manuals/ampere/ga100/index.html)
- [manuals/ampere/ga100/pri_mme.ref.txt](manuals/ampere/ga100/pri_mme.ref.txt)
- [manuals/turing/tu104/dev_pmgr.ref.txt](manuals/turing/tu104/dev_pmgr.ref.txt)
- [manuals/turing/tu104/index.html](manuals/turing/tu104/index.html)

</details>



This document covers the hardware specifications, register definitions, and low-level programming interfaces for NVIDIA GPU architectures. It provides comprehensive documentation of hardware blocks, register maps, and system interfaces across multiple GPU generations including Turing, Ampere, Volta, and others.

For higher-level programming interfaces and hardware classes, see [Programming Interfaces](#3). For specific implementation details of command processing and memory management, see [System Components](#4).

## Architecture Overview

The NVIDIA GPU hardware architecture consists of multiple specialized processing units, each with dedicated register interfaces and control mechanisms. The architecture is organized around core processing engines, display subsystems, memory management units, and system control blocks.

```mermaid
graph TB
    subgraph "GPU Hardware Architecture"
        subgraph "Core Processing"
            CTXSW["NV_CTXSW<br/>Context Switching<br/>State Management"]
            PGRAPH["PGRAPH<br/>3D Graphics Engine<br/>Rendering Pipeline"]
            MME["NV_PGRAPH_PRI_MME<br/>Macro Method Engine<br/>Command Processing"]
        end
        
        subgraph "Display & Output"
            PDISP["NV_PDISP<br/>Display Processor<br/>Output Management"]
            HDACODEC["NV_HDACODEC<br/>Audio Codec<br/>HDMI Audio"]
        end
        
        subgraph "Memory & I/O"
            MMU["NV_MMU<br/>Memory Management<br/>Virtual Memory"]
            PBDMA["PBDMA<br/>Pushbuffer DMA<br/>Command Processing"]
            XVE["NV_XVE<br/>PCIe Interface<br/>Host Communication"]
        end
        
        subgraph "System Control"
            PMGR["NV_PMGR<br/>Power Manager<br/>Power States & GPIO"]
            PTIMER["PTIMER<br/>Timer Unit<br/>System Timing"]
        end
    end
    
    XVE --> PBDMA
    PBDMA --> PGRAPH
    CTXSW --> PGRAPH
    CTXSW --> PDISP
    MMU --> PGRAPH
    PMGR --> XVE
```

**Sources:** [manuals/turing/tu104/index.html:1-37](), [manuals/ampere/ga100/index.html:1-24]()

## GPU Generation Coverage

The documentation spans multiple GPU architecture generations, each with specific hardware capabilities and register interfaces:

| Architecture | Chip Examples | Key Features | Documentation Coverage |
|--------------|---------------|--------------|----------------------|
| **Turing** | TU104, TU102 | RT Cores, Enhanced Context Switching | Complete register definitions |
| **Ampere** | GA100, GA102 | Enhanced AI, Advanced Compute | Core system blocks |
| **Volta** | GV100 | Tensor Cores, Display Processing | Context switching focus |
| **Pascal** | GP100-GP108 | Enhanced Memory, Basic Features | Limited coverage |

```mermaid
graph LR
    subgraph "Architecture Evolution"
        VOLTA["Volta<br/>GV100<br/>• Tensor Cores<br/>• Basic Display"]
        TURING["Turing<br/>TU104/TU102<br/>• RT Cores<br/>• Enhanced CTXSW"]
        AMPERE["Ampere<br/>GA100/GA102<br/>• Enhanced AI<br/>• Advanced Compute"]
    end
    
    subgraph "Register Documentation"
        VOLTA_REGS["dev_ctxsw.ref.txt<br/>Context Switch Regs"]
        TURING_REGS["35+ .ref.txt files<br/>Complete Coverage"]
        AMPERE_REGS["Core system blocks<br/>CTXSW, XVE, MME"]
    end
    
    VOLTA --> VOLTA_REGS
    TURING --> TURING_REGS
    AMPERE --> AMPERE_REGS
```

**Sources:** [manuals/turing/tu104/index.html:1-37](), [manuals/ampere/ga100/index.html:1-24]()

## Context Switching Hardware

The `NV_CTXSW` block manages GPU context switching and preemption across different workload types. It provides hardware-level state management for graphics, compute, and display contexts.

### Context Switch Image Structure

```mermaid
graph TB
    subgraph "NV_CTXSW Memory Layout"
        HEADER["CTXSW_HEADER<br/>512 bytes<br/>0x00000000"]
        FECS["FECS_HEADER<br/>512 bytes<br/>0x00000200"]
        GPCCS["GPCCS_HEADER[8]<br/>512 bytes each<br/>0x00000400+"]
        
        subgraph "Main Image Fields"
            POOL_PTR["MAIN_IMAGE_POOL_PTR<br/>0x00000000"]
            SIZE["MAIN_IMAGE_SIZE<br/>0x00000004"]
            GPCS["MAIN_IMAGE_NUM_GPCS<br/>0x00000008"]
            CTL["MAIN_IMAGE_CTL<br/>0x0000000C"]
        end
        
        subgraph "Preemption Control"
            GFXP_OPTS["GRAPHICS_PREEMPTION_OPTIONS<br/>0x00000080"]
            COMP_OPTS["COMPUTE_PREEMPTION_OPTIONS<br/>0x00000084"]
        end
    end
    
    HEADER --> POOL_PTR
    FECS --> SIZE
    GPCCS --> CTL
```

### Preemption Types

The context switching hardware supports multiple preemption granularities:

| Preemption Type | Graphics Control | Compute Control | Use Case |
|-----------------|------------------|-----------------|----------|
| **WFI** | `CONTROL_WFI` (0x0) | `CONTROL_WFI` (0x0) | Wait for idle |
| **GFXP** | `CONTROL_GFXP` (0x1) | N/A | Graphics preemption |
| **CTA** | N/A | `CONTROL_CTA` (0x1) | Cooperative thread array |
| **CILP** | N/A | `CONTROL_CILP` (0x2) | Compute instruction level |

**Sources:** [manuals/ampere/ga100/dev_ctxsw.ref.txt:98-106]()

## Power Management and System Control

The `NV_PMGR` block handles power management, GPIO control, and system-level interrupts. It provides interfaces for power state transitions and peripheral control.

### GPIO and Interrupt Control

```mermaid
graph TB
    subgraph "NV_PMGR Register Map"
        GPIO_LIST["RM_INTR_GPIO_LIST_1<br/>0x0000DC00<br/>GPIO Rising/Falling Edge"]
        GPIO_EN["RM_INTR_EN_GPIO_LIST_1<br/>0x0000DC08<br/>GPIO Interrupt Enable"]
        I2C_INTR["RM_INTR_I2C<br/>0x0000DC20<br/>I2C Controller Events"]
        AUX_INTR["RM_INTR_AUX<br/>0x0000DC60<br/>AUX Channel Events"]
    end
    
    subgraph "GPIO Bit Fields"
        GPIO0_RISING["GPIO0_RISING[0:0]"]
        GPIO0_FALLING["GPIO0_FALLING[16:16]"]
        GPIO_ARRAY["GPIO_RISING/FALLING(i)<br/>i = 0 to 15"]
    end
    
    GPIO_LIST --> GPIO0_RISING
    GPIO_LIST --> GPIO0_FALLING
    GPIO_EN --> GPIO_ARRAY
```

**Sources:** [manuals/turing/tu104/dev_pmgr.ref.txt:33-203]()

## PCIe Interface Hardware

The `NV_XVE` block implements the PCIe interface and provides host communication capabilities. It includes standard PCIe configuration space and NVIDIA-specific extensions.

### PCIe Configuration Space

The PCIe interface supports multiple device IDs across GPU generations:

```mermaid
graph TB
    subgraph "NV_XVE Configuration"
        ID_REG["XVE_ID<br/>0x00000000<br/>Vendor/Device ID"]
        DEV_CTRL["DEV_CTRL<br/>0x00000004<br/>Command/Status"]
        BARS["BAR0-BAR3<br/>0x00000010-0x00000024<br/>Base Address Registers"]
        
        subgraph "Device IDs"
            TU104["TU104: 0x1E80-0x1EFF"]
            GA100["GA100: 0x2080-0x20FF"]
            GA102["GA102: 0x2200-0x227F"]
        end
        
        subgraph "Power Management"
            PWR_MGMT_0["PWR_MGMT_0<br/>0x00000060"]
            PWR_MGMT_1["PWR_MGMT_1<br/>0x00000064"]
        end
    end
    
    ID_REG --> TU104
    ID_REG --> GA100
    ID_REG --> GA102
```

**Sources:** [manuals/ampere/ga100/dev_nv_xve3g_fn0.ref.txt:24-139]()

## Macro Method Engine (MME)

The `NV_PGRAPH_PRI_MME` provides hardware acceleration for repetitive GPU operations through programmable macro execution.

### MME Register Interface

```mermaid
graph TB
    subgraph "MME Control Registers"
        SHADOW_INDEX["PRI_MME_SHADOW_RAM_INDEX<br/>0x00404488<br/>RAM Access Control"]
        SHADOW_DATA["PRI_MME_SHADOW_RAM_DATA<br/>0x0040448C<br/>RAM Data Interface"]
        HWW_ESR["PRI_MME_HWW_ESR<br/>0x00404490<br/>Hardware Watchdog"]
    end
    
    subgraph "Shadow RAM Fields"
        NVCLASS["NVCLASS[15:0]<br/>Hardware Class"]
        METHOD_ADDR["METHOD_ADDR[27:16]<br/>Method Address"]
        FEPIPE["FEPIPE[29:29]<br/>Frontend Pipe Select"]
        READ_WRITE["READ[30] / WRITE[31]<br/>Operation Type"]
    end
    
    subgraph "Error Conditions"
        MISSING_DATA["MISSING_MACRO_DATA[0:0]"]
        EXTRA_DATA["EXTRA_MACRO_DATA[1:1]"]
        ILLEGAL_OP["ILLEGAL_OPCODE[2:2]"]
        MAX_INSTR["MAX_INSTR_LIMIT[4:4]"]
    end
    
    SHADOW_INDEX --> NVCLASS
    SHADOW_INDEX --> METHOD_ADDR
    HWW_ESR --> MISSING_DATA
    HWW_ESR --> ILLEGAL_OP
```

**Sources:** [manuals/ampere/ga100/pri_mme.ref.txt:22-87]()

## Register Definition Format

All hardware registers follow a standardized format with 5-field access codes:

| Field | Values | Description |
|-------|--------|-------------|
| **Read** | `R`, `C`, `-` | Read capability and constant values |
| **Write** | `W`, `-` | Write capability |
| **Internal State** | `I`, `E`, `B`, `C`, `V`, `X` | Reset behavior and initialization |
| **Declaration/Size** | `1`, `2`, `4`, `8`, `V`, `U`, `S`, `F` | Data type and size |
| **Define Indicator** | `R`, `F`, `V`, `D`, `A` | Register, field, value, device, array |

Example register definition:
```
#define NV_CTXSW_MAIN_IMAGE_CTL                        0x0000000C /* RW-4R */
#define NV_CTXSW_MAIN_IMAGE_CTL_TYPE                          5:0 /* RWXVF */
#define NV_CTXSW_MAIN_IMAGE_CTL_TYPE_OPENGL                   0x8 /* RW--V */
```

**Sources:** [manuals/ampere/ga100/dev_ctxsw.ref.txt:272-343]()

---

