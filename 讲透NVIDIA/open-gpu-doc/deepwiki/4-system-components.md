<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/open-gpu-doc · page 4 System Components · fetched 2026-10-26 -->

# System Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [manuals/turing/tu104/dev_ce.ref.txt](manuals/turing/tu104/dev_ce.ref.txt)
- [manuals/turing/tu104/dev_ctrl.ref.txt](manuals/turing/tu104/dev_ctrl.ref.txt)
- [manuals/turing/tu104/dev_master.ref.txt](manuals/turing/tu104/dev_master.ref.txt)
- [manuals/turing/tu104/dev_mmu.ref.txt](manuals/turing/tu104/dev_mmu.ref.txt)
- [manuals/turing/tu104/dev_pbdma.ref.txt](manuals/turing/tu104/dev_pbdma.ref.txt)
- [manuals/turing/tu104/pri_cwd.ref.txt](manuals/turing/tu104/pri_cwd.ref.txt)
- [manuals/turing/tu104/pri_eng.ref.txt](manuals/turing/tu104/pri_eng.ref.txt)
- [manuals/turing/tu104/pri_fe.ref.txt](manuals/turing/tu104/pri_fe.ref.txt)
- [manuals/turing/tu104/pri_memfmt.ref.txt](manuals/turing/tu104/pri_memfmt.ref.txt)
- [manuals/turing/tu104/pri_mme.ref.txt](manuals/turing/tu104/pri_mme.ref.txt)
- [manuals/volta/gv100/dev_mmu.ref.txt](manuals/volta/gv100/dev_mmu.ref.txt)

</details>



This document covers the core system infrastructure components that provide fundamental services for GPU operation, including command processing, memory management, data movement, and system control. These components form the foundation that enables higher-level GPU subsystems to function.

For information about specific programming interfaces and hardware classes, see [Programming Interfaces](#3). For context switching mechanisms and preemption, see [Context Switching](#4.2). For command submission and processing details, see [Command Processing](#4.1).

## Overview

The GPU system infrastructure consists of several interconnected hardware units that manage fundamental operations:

- **Command Processing**: PBDMA units fetch and process pushbuffer commands
- **Memory Management**: MMU provides virtual memory translation and protection
- **Data Movement**: Copy engines handle bulk data transfers and memory operations
- **System Control**: PMC and CTRL units manage interrupts, resets, and device coordination
- **Graphics Support**: Specialized units like MME, FE, and CWD support graphics workloads

## System Infrastructure Architecture

```mermaid
graph TB
    subgraph "System Control Layer"
        PMC["PMC<br/>Master Control<br/>NV_PMC"]
        CTRL["CTRL<br/>Interrupt Controller<br/>NV_CTRL"]
    end
    
    subgraph "Command Processing"
        PBDMA["PBDMA Units<br/>NV_PPBDMA<br/>Pushbuffer DMA"]
        GPFIFO["GP FIFO<br/>Command Buffers"]
        UDMA["UDMA<br/>Host Methods<br/>NV_UDMA"]
    end
    
    subgraph "Memory Management"
        MMU["MMU<br/>Memory Management<br/>NV_MMU"]
        PTE["Page Tables<br/>NV_MMU_VER2_PTE"]
        PDE["Page Directories<br/>NV_MMU_VER2_PDE"]
    end
    
    subgraph "Data Movement"
        CE["Copy Engines<br/>NV_CE"]
        LCE["Logical CE<br/>NV_CE_LCE"]
        PCE["Physical CE<br/>NV_CE_PCE"]
    end
    
    subgraph "Graphics Engine Support"
        FE["Front End<br/>NV_PGRAPH_PRI_FE"]
        MME["Macro Method Engine<br/>NV_PGRAPH_PRI_MME"]
        CWD["Compute Work Distribution<br/>NV_PGRAPH_PRI_CWD"]
        MEMFMT["Memory Format<br/>NV_PGRAPH_PRI_MEMFMT"]
    end
    
    PMC --> PBDMA
    PMC --> CE
    PMC --> MMU
    CTRL --> PMC
    
    PBDMA --> GPFIFO
    PBDMA --> UDMA
    PBDMA --> MMU
    
    CE --> LCE
    CE --> PCE
    CE --> MMU
    
    FE --> MME
    FE --> CWD
    FE --> MEMFMT
    
    PBDMA --> FE
```

Sources: [manuals/turing/tu104/dev_master.ref.txt:22-329](), [manuals/turing/tu104/dev_pbdma.ref.txt:53-54](), [manuals/turing/tu104/dev_ce.ref.txt:22-245](), [manuals/turing/tu104/dev_ctrl.ref.txt:22-194]()

## Command Processing Infrastructure

The command processing infrastructure centers around PBDMA (Push Buffer DMA) units that fetch and execute commands from memory-resident pushbuffers.

### PBDMA Architecture

```mermaid
graph TB
    subgraph "GP Entry Processing"
        GPBASE["GP_BASE<br/>NV_PPBDMA_GP_BASE"]
        GPGET["GP_GET<br/>NV_PPBDMA_GP_GET"]
        GPPUT["GP_PUT<br/>NV_PPBDMA_GP_PUT"]
        GPFETCH["GP_FETCH<br/>NV_PPBDMA_GP_FETCH"]
    end
    
    subgraph "GP Entry Format"
        GPENTRY0["GP_ENTRY0<br/>Address/Operand<br/>NV_PPBDMA_GP_ENTRY0"]
        GPENTRY1["GP_ENTRY1<br/>Length/Opcode<br/>NV_PPBDMA_GP_ENTRY1"]
    end
    
    subgraph "Method Processing"
        UDMA_SPACE["UDMA Address Space<br/>NV_UDMA<br/>0x000000FF:0x00000000"]
        HOST_METHODS["Host Methods<br/>Executed by PBDMA"]
        ENGINE_METHODS["Engine Methods<br/>Sent to Engines"]
    end
    
    GPBASE --> GPENTRY0
    GPBASE --> GPENTRY1
    GPGET --> GPENTRY0
    GPPUT --> GPENTRY0
    GPFETCH --> GPENTRY0
    
    GPENTRY0 --> UDMA_SPACE
    GPENTRY1 --> UDMA_SPACE
    
    UDMA_SPACE --> HOST_METHODS
    UDMA_SPACE --> ENGINE_METHODS
```

The PBDMA units operate on GP (General Purpose) entries stored in circular buffers. Each GP entry can either specify a pushbuffer segment to execute or contain control operations.

**Key PBDMA Components:**
- `NV_PPBDMA_GP_BASE`: Base address and size of GP entry circular buffer
- `NV_PPBDMA_GP_GET`: Next GP entry to process  
- `NV_PPBDMA_GP_PUT`: Next GP entry to write
- `NV_PPBDMA_GP_FETCH`: Next GP entry to fetch from memory

Sources: [manuals/turing/tu104/dev_pbdma.ref.txt:272-328](), [manuals/turing/tu104/dev_pbdma.ref.txt:374-427](), [manuals/turing/tu104/dev_pbdma.ref.txt:228-254]()

### GP Entry Format

GP entries use a two-word format that can specify either pushbuffer segments or control operations:

| Field | Purpose |
|-------|---------|
| `NV_PPBDMA_GP_ENTRY0_GET` | Pushbuffer segment start address (bits 31:2) |
| `NV_PPBDMA_GP_ENTRY0_FETCH` | Conditional/unconditional fetch control |
| `NV_PPBDMA_GP_ENTRY1_LENGTH` | Pushbuffer segment length or 0 for control |
| `NV_PPBDMA_GP_ENTRY1_OPCODE` | Control operation when LENGTH=0 |
| `NV_PPBDMA_GP_ENTRY1_SYNC` | Synchronization requirements |

**Control Opcodes:**
- `OPCODE_NOP`: No operation
- `OPCODE_GP_CRC`: Verify GP entry CRC
- `OPCODE_PB_CRC`: Verify pushbuffer CRC

Sources: [manuals/turing/tu104/dev_pbdma.ref.txt:230-254]()

## Memory Management

The Memory Management Unit (MMU) provides virtual memory translation using a hierarchical page table structure.

### MMU Page Table Hierarchy

```mermaid
graph TB
    subgraph "Virtual Address Translation"
        VADDR["Virtual Address<br/>40-bit"]
        PDE_ADDR["Page Directory<br/>NV_MMU_VER2_PDE"]
        PTE_ADDR["Page Table Entry<br/>NV_MMU_VER2_PTE"]
        PHYS_ADDR["Physical Address"]
    end
    
    subgraph "Page Table Entry"
        PTE_VALID["VALID<br/>Bit 0"]
        PTE_APERTURE["APERTURE<br/>Bits 2:1"]
        PTE_KIND["KIND<br/>Bits 63:56"]
        PTE_ADDRESS["ADDRESS<br/>Physical Page"]
    end
    
    subgraph "Memory Kinds"
        KIND_GENERIC["GENERIC_MEMORY<br/>0x06"]
        KIND_COMPRESSED["COMPRESSIBLE<br/>0x08"]
        KIND_DEPTH["Z16/Z24S8<br/>Depth formats"]
        KIND_INVALID["INVALID<br/>0x07"]
    end
    
    VADDR --> PDE_ADDR
    PDE_ADDR --> PTE_ADDR
    PTE_ADDR --> PHYS_ADDR
    
    PTE_ADDR --> PTE_VALID
    PTE_ADDR --> PTE_APERTURE
    PTE_ADDR --> PTE_KIND
    PTE_ADDR --> PTE_ADDRESS
    
    PTE_KIND --> KIND_GENERIC
    PTE_KIND --> KIND_COMPRESSED
    PTE_KIND --> KIND_DEPTH
    PTE_KIND --> KIND_INVALID
```

**Aperture Types:**
- `VIDEO_MEMORY`: Local GPU memory
- `SYSTEM_COHERENT_MEMORY`: Coherent system memory
- `SYSTEM_NON_COHERENT_MEMORY`: Non-coherent system memory
- `PEER_MEMORY`: Peer GPU memory

Sources: [manuals/turing/tu104/dev_mmu.ref.txt:104-149](), [manuals/turing/tu104/dev_mmu.ref.txt:22-148](), [manuals/volta/gv100/dev_mmu.ref.txt:268-337]()

### Memory Kinds

The MMU supports different memory kinds that specify surface formats and compression:

| Kind | Value | Purpose |
|------|-------|---------|
| `NV_MMU_PTE_KIND_GENERIC_MEMORY` | 0x06 | General memory surfaces |
| `NV_MMU_PTE_KIND_GENERIC_MEMORY_COMPRESSIBLE` | 0x08 | Compressible generic memory |
| `NV_MMU_PTE_KIND_Z16` | 0x01 | 16-bit depth buffer |
| `NV_MMU_PTE_KIND_S8Z24` | 0x03 | 8-bit stencil + 24-bit depth |
| `NV_MMU_PTE_KIND_INVALID` | 0x07 | Invalid/unmapped memory |

Sources: [manuals/turing/tu104/dev_mmu.ref.txt:22-36](), [manuals/volta/gv100/dev_mmu.ref.txt:22-267]()

## Data Movement Infrastructure

Copy engines handle bulk data transfers and memory operations between different memory spaces.

### Copy Engine Architecture

```mermaid
graph TB
    subgraph "Copy Engine Hierarchy"
        CE_TOP["NV_CE<br/>Copy Engine Top"]
        PCE_MAP["PCE_MAP<br/>Physical CE Mapping"]
        LCE_CONFIG["LCE Config<br/>Logical CE Assignment"]
    end
    
    subgraph "Logical Copy Engines"
        LCE0["LCE 0<br/>NV_CE_LCE_STATUS(0)"]
        LCE1["LCE 1<br/>NV_CE_LCE_STATUS(1)"]
        LCE2["LCE 2<br/>NV_CE_LCE_STATUS(2)"]
        LCE3["LCE 3<br/>NV_CE_LCE_STATUS(3)"]
        LCE4["LCE 4<br/>NV_CE_LCE_STATUS(4)"]
    end
    
    subgraph "Physical Copy Engines"
        PCE0["PCE 0<br/>NV_CE_PCE_PIPESTATUS(0)"]
        PCE1["PCE 1<br/>NV_CE_PCE_PIPESTATUS(1)"]
        PCE2["PCE 2<br/>NV_CE_PCE_PIPESTATUS(2)"]
        PCE3["PCE 3<br/>NV_CE_PCE_PIPESTATUS(3)"]
    end
    
    subgraph "Pipeline Stages"
        GSTRIP["GSTRIP<br/>Data Striping"]
        RALIGN["RALIGN<br/>Read Alignment"]
        SWIZ["SWIZ<br/>Swizzling"]
        WALIGN["WALIGN<br/>Write Alignment"]
    end
    
    CE_TOP --> PCE_MAP
    CE_TOP --> LCE_CONFIG
    
    LCE_CONFIG --> LCE0
    LCE_CONFIG --> LCE1
    LCE_CONFIG --> LCE2
    LCE_CONFIG --> LCE3
    LCE_CONFIG --> LCE4
    
    PCE_MAP --> PCE0
    PCE_MAP --> PCE1
    PCE_MAP --> PCE2
    PCE_MAP --> PCE3
    
    PCE0 --> GSTRIP
    GSTRIP --> RALIGN
    RALIGN --> SWIZ
    SWIZ --> WALIGN
```

**Copy Engine Configuration:**
- `NV_CE_PCE2LCE_CONFIG`: Maps physical CEs to logical CEs
- `NV_CE_GRCE_CONFIG`: Graphics copy engine sharing configuration
- `NV_CE_LCE_STATUS`: Logical CE activity status
- `NV_CE_PCE_PIPESTATUS`: Physical CE pipeline status

Sources: [manuals/turing/tu104/dev_ce.ref.txt:22-45](), [manuals/turing/tu104/dev_ce.ref.txt:102-244]()

### Copy Engine Error Handling

Copy engines provide comprehensive error detection and reporting:

| Error Type | Register Field | Purpose |
|------------|----------------|---------|
| Launch Error | `NV_CE_LCE_LAUNCHERR_REPORT` | Invalid copy parameters |
| Method Buffer Fault | `NV_CE_LCE_INTR_STATUS_MTHD_BUFFER_FAULT` | Method access violations |
| Invalid Configuration | `NV_CE_LCE_INTR_STATUS_INVALID_CONFIG` | CE setup errors |
| CRC Failure | `NV_CE_LCE_INTR_STATUS_FBUF_CRC_FAIL` | Data integrity errors |

Sources: [manuals/turing/tu104/dev_ce.ref.txt:184-201](), [manuals/turing/tu104/dev_ce.ref.txt:139-168]()

## System Control and Interrupts

The PMC (Master Control) and CTRL units manage system-wide control, interrupts, and device coordination.

### PMC Master Control

```mermaid
graph TB
    subgraph "PMC Boot and ID"
        BOOT0["PMC_BOOT_0<br/>Chip ID and Revision"]
        BOOT1["PMC_BOOT_1<br/>Virtualization Status"]
        BOOT42["PMC_BOOT_42<br/>Extended Chip Info"]
    end
    
    subgraph "Device Enable Control"
        ENABLE["PMC_ENABLE<br/>Device Enable Register"]
        PFIFO_EN["PFIFO Enable"]
        PDISP_EN["PDISP Enable"]
        PERFMON_EN["PERFMON Enable"]
    end
    
    subgraph "Interrupt Management"
        INTR["PMC_INTR<br/>Interrupt Status"]
        INTR_EN["PMC_INTR_EN<br/>Interrupt Enable"]
        INTR_MODE["PMC_INTR_MODE<br/>Level/Edge Mode"]
    end
    
    subgraph "Interrupt Sources"
        PFIFO_INT["PFIFO Interrupt"]
        HUB_INT["HUB Interrupt"]
        PDISP_INT["PDISP Interrupt"]
        THERMAL_INT["Thermal Interrupt"]
        PMU_INT["PMU Interrupt"]
    end
    
    BOOT0 --> ENABLE
    ENABLE --> PFIFO_EN
    ENABLE --> PDISP_EN
    ENABLE --> PERFMON_EN
    
    INTR --> INTR_EN
    INTR --> INTR_MODE
    
    INTR --> PFIFO_INT
    INTR --> HUB_INT
    INTR --> PDISP_INT
    INTR --> THERMAL_INT
    INTR --> PMU_INT
```

**PMC Architecture Identification:**
- `NV_PMC_BOOT_0_ARCHITECTURE`: GPU architecture (Turing = 0x15)
- `NV_PMC_BOOT_42_CHIP_ID`: Specific chip identification
- `NV_PMC_BOOT_1_VGPU`: Virtual GPU status

Sources: [manuals/turing/tu104/dev_master.ref.txt:23-196](), [manuals/turing/tu104/dev_master.ref.txt:303-329]()

### CTRL Interrupt Controller

The CTRL unit provides advanced interrupt management with CPU notification and doorbell mechanisms:

**Key CTRL Features:**
- `NV_CTRL_CPU_INTR_TOP`: Top-level interrupt aggregation
- `NV_CTRL_CPU_INTR_LEAF`: Leaf-level interrupt status  
- `NV_CTRL_DOORBELL`: Host-to-GPU notification mechanism
- `NV_CTRL_VIRTUAL_INTR_LEAF`: Virtual interrupt management

Sources: [manuals/turing/tu104/dev_ctrl.ref.txt:23-118]()

## Graphics Engine Support Components

Several specialized units support graphics workload processing and method execution.

### Graphics Pipeline Support

```mermaid
graph TB
    subgraph "Front End Processing"
        FE["Front End<br/>NV_PGRAPH_PRI_FE"]
        SETOBJ["SetObject State<br/>NV_PGRAPH_PRI_FE_SETOBJ_STATE"]
        DECODE["Decode State<br/>NV_PGRAPH_PRI_FE_DECODE_STATE"]
        SEMAPHORE["Semaphore State<br/>NV_PGRAPH_PRI_FE_SEMAPHORE_STATE"]
    end
    
    subgraph "Macro Method Engine"
        MME["MME<br/>NV_PGRAPH_PRI_MME"]
        SHADOW_RAM["Shadow RAM<br/>NV_PGRAPH_PRI_MME_SHADOW_RAM"]
        MME_ESR["MME Error Status<br/>NV_PGRAPH_PRI_MME_HWW_ESR"]
    end
    
    subgraph "Compute Work Distribution"
        CWD["CWD<br/>NV_PGRAPH_PRI_CWD"]
        PARTITION["Partition Control<br/>NV_PGRAPH_PRI_CWD_PARTITION_CTL"]
        GPC_TPC["GPC/TPC Mapping<br/>NV_PGRAPH_PRI_CWD_GPC_TPC_ID"]
    end
    
    subgraph "Memory Format"
        MEMFMT["MEMFMT<br/>NV_PGRAPH_PRI_MEMFMT"]
        MEMFMT_ESR["MEMFMT Error Status<br/>NV_PGRAPH_PRI_MEMFMT_HWW_ESR"]
    end
    
    FE --> SETOBJ
    FE --> DECODE  
    FE --> SEMAPHORE
    
    MME --> SHADOW_RAM
    MME --> MME_ESR
    
    CWD --> PARTITION
    CWD --> GPC_TPC
    
    MEMFMT --> MEMFMT_ESR
```

**Component Functions:**
- **Front End (FE)**: Method decoding and subchannel management
- **MME**: Macro method execution and expansion
- **CWD**: Compute workload distribution to SMs
- **MEMFMT**: Memory format and inline data handling

Sources: [manuals/turing/tu104/pri_fe.ref.txt:22-285](), [manuals/turing/tu104/pri_mme.ref.txt:22-112](), [manuals/turing/tu104/pri_cwd.ref.txt:22-134](), [manuals/turing/tu104/pri_memfmt.ref.txt:22-40]()

---

