<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/jetson-rdma-picoevb · page 4 Kernel Module · fetched 2026-10-26 -->

# Kernel Module

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [kernel-module/picoevb-rdma.c](kernel-module/picoevb-rdma.c)

</details>



This document provides comprehensive documentation of the `picoevb-rdma` kernel module, the core component that enables GPUDirect RDMA functionality between FPGA devices and NVIDIA GPUs. The module implements a PCI device driver that manages DMA operations, integrates with NVIDIA's P2P API for GPU memory access, and exposes an IOCTL-based interface to user-space applications.

For details about the user-space applications that interact with this module, see [Client Applications](#5). For information about building and deploying the module, see [Building the Kernel Module](#7.2).

## Module Purpose and Architecture

The `picoevb-rdma` kernel module serves three critical roles:

1. **PCI Device Driver**: Manages PicoEVB and HTG-K800 FPGA cards as PCI devices, handling device initialization, BAR mappings, and interrupt registration
2. **DMA Orchestrator**: Coordinates data transfers between host memory, GPU memory, and FPGA RAM using the Xilinx DMA engine
3. **CUDA P2P Bridge**: Integrates with NVIDIA's P2P API to pin and map GPU memory for direct DMA access

The module creates a character device `/dev/picoevb` that user-space applications use to initiate DMA operations and control hardware features.

**Sources**: [kernel-module/picoevb-rdma.c:1-1312]()

## Core Data Structures

### Module Architecture Overview

```mermaid
graph TB
    subgraph "User Space"
        APP["Application"]
        IOCTL["ioctl() system calls"]
    end
    
    subgraph "Kernel Module: picoevb-rdma.c"
        FOPS["file_operations<br/>pevb_fops"]
        IOCTL_DISPATCH["pevb_fops_unlocked_ioctl()"]
        
        subgraph "IOCTL Handlers"
            LED["pevb_ioctl_led()"]
            PIN["pevb_ioctl_pin_cuda()"]
            UNPIN["pevb_ioctl_unpin_cuda()"]
            H2C["pevb_ioctl_h2c_dma()"]
            C2H["pevb_ioctl_c2h_dma()"]
            H2C2H["pevb_ioctl_h2c2h_dma()"]
            CARDINFO["pevb_ioctl_card_info()"]
        end
        
        subgraph "DMA Engine"
            DMA_H2C["pevb_dma_h2c_multi()"]
            DMA_C2H["pevb_dma_c2h_multi()"]
            DMA_H2C2H["pevb_dma_h2c2h_multi()"]
            DMA_CORE["pevb_dma()"]
        end
        
        subgraph "Memory Management"
            PAGES["pevb_get_userbuf_pages()"]
            CUDA["pevb_get_userbuf_cuda()"]
            P2P_MAP["nvidia_p2p_dma_map_pages()"]
        end
        
        IRQ["pevb_irq_handler()"]
    end
    
    subgraph "Hardware"
        FPGA_DMA["Xilinx DMA Engine"]
        FPGA_RAM["FPGA RAM"]
        GPU_MEM["GPU Memory"]
    end
    
    APP --> IOCTL
    IOCTL --> FOPS
    FOPS --> IOCTL_DISPATCH
    
    IOCTL_DISPATCH --> LED
    IOCTL_DISPATCH --> PIN
    IOCTL_DISPATCH --> UNPIN
    IOCTL_DISPATCH --> H2C
    IOCTL_DISPATCH --> C2H
    IOCTL_DISPATCH --> H2C2H
    IOCTL_DISPATCH --> CARDINFO
    
    H2C --> PAGES
    H2C --> CUDA
    C2H --> PAGES
    C2H --> CUDA
    H2C2H --> PAGES
    H2C2H --> CUDA
    
    CUDA --> P2P_MAP
    
    H2C --> DMA_H2C
    C2H --> DMA_C2H
    H2C2H --> DMA_H2C2H
    
    DMA_H2C --> DMA_CORE
    DMA_C2H --> DMA_CORE
    DMA_H2C2H --> DMA_CORE
    
    DMA_CORE --> FPGA_DMA
    FPGA_DMA --> IRQ
    
    P2P_MAP --> GPU_MEM
    DMA_CORE --> FPGA_RAM
```

**Sources**: [kernel-module/picoevb-rdma.c:1104-1129](), [kernel-module/picoevb-rdma.c:1131-1136]()

### Primary Data Structures

The module defines several key structures that maintain device state and track operations:

| Structure | Purpose | Location |
|-----------|---------|----------|
| `struct pevb` | Per-device state for FPGA card | [kernel-module/picoevb-rdma.c:56-71]() |
| `struct pevb_file` | Per-file-descriptor state | [kernel-module/picoevb-rdma.c:73-77]() |
| `struct pevb_cuda_surface` | Tracks pinned CUDA memory | [kernel-module/picoevb-rdma.c:80-87]() |
| `struct pevb_userbuf` | Unified user buffer representation | [kernel-module/picoevb-rdma.c:95-117]() |
| `struct pevb_userbuf_dma` | DMA segment descriptor | [kernel-module/picoevb-rdma.c:90-93]() |
| `struct pevb_drvdata` | Board-specific parameters | [kernel-module/picoevb-rdma.c:51-54]() |

#### struct pevb - Device Instance

```mermaid
graph LR
    subgraph "struct pevb"
        PDEV["pci_dev *pdev"]
        DRVDATA["pevb_drvdata *drvdata"]
        DEVNODE["device *devnode"]
        CDEV["cdev cdev"]
        IOMAP["void __iomem **iomap"]
        SEM["semaphore sem"]
        DESCS["void *descs_ptr"]
        DESCS_DMA["dma_addr_t descs_dma_addr"]
        CMPL["completion dma_xfer_cmpl"]
        ERRORS["bool h2c_error, c2h_error"]
    end
    
    PDEV -.->|"PCI device handle"| PCI["PCI Subsystem"]
    DRVDATA -.->|"fpga_ram_size<br/>num_h2c_chans"| BOARD["Board Config"]
    IOMAP -.->|"BAR_GPIO, BAR_DMA"| BARS["Memory-Mapped BARs"]
    SEM -.->|"serializes DMA ops"| SYNC["Synchronization"]
    DESCS -.->|"DMA descriptor memory"| DMA["DMA Engine"]
    CMPL -.->|"signals IRQ completion"| IRQ["IRQ Handler"]
```

**Sources**: [kernel-module/picoevb-rdma.c:56-71]()

#### struct pevb_file - File Descriptor State

Each open file descriptor maintains its own state, including a list of pinned CUDA surfaces tracked via an IDR (ID Radix tree) for efficient lookup by handle.

**Sources**: [kernel-module/picoevb-rdma.c:73-77](), [kernel-module/picoevb-rdma.c:137-153]()

#### struct pevb_userbuf - Unified Buffer Abstraction

The `pevb_userbuf` structure provides a unified representation of user-space memory that abstracts over two distinct paths:

- **Pages path**: Regular `malloc()` or `cudaHostAlloc()` memory, pinned via `get_user_pages()` and mapped via `dma_map_sg()`
- **CUDA path**: `cudaMalloc()` GPU memory, pinned via `nvidia_p2p_get_pages()` and mapped via `nvidia_p2p_dma_map_pages()`

Both paths populate the `dmas` array with DMA-accessible physical address segments.

**Sources**: [kernel-module/picoevb-rdma.c:95-117]()

## Device Lifecycle

### PCI Driver Registration

The module registers as a PCI driver using the standard Linux PCI subsystem:

```mermaid
graph TB
    INIT["pevb_init()"]
    CLASS["class_create()<br/>creates 'picoevb' class"]
    REGISTER["pci_register_driver()<br/>registers pevb_driver"]
    
    PROBE["pevb_probe()<br/>called for each device"]
    ENABLE["pcim_enable_device()"]
    IOMAP["pcim_iomap_regions()<br/>maps BAR_GPIO, BAR_DMA"]
    MASTER["pci_set_master()"]
    IRQ["request_irq()<br/>pevb_irq_handler"]
    CHRDEV["alloc_chrdev_region()<br/>cdev_init(), cdev_add()"]
    DEVNODE["device_create()<br/>/dev/picoevb"]
    
    REMOVE["pevb_remove()<br/>cleanup on device removal"]
    FREE_IRQ["free_irq()"]
    CLEAR_MASTER["pci_clear_master()"]
    DESTROY_DEV["device_destroy()"]
    CDEV_DEL["cdev_del()"]
    UNREG_CHRDEV["unregister_chrdev_region()"]
    
    INIT --> CLASS
    INIT --> REGISTER
    REGISTER --> PROBE
    
    PROBE --> ENABLE
    PROBE --> IOMAP
    PROBE --> MASTER
    PROBE --> IRQ
    PROBE --> CHRDEV
    PROBE --> DEVNODE
    
    REMOVE --> FREE_IRQ
    REMOVE --> CLEAR_MASTER
    REMOVE --> DESTROY_DEV
    REMOVE --> CDEV_DEL
    REMOVE --> UNREG_CHRDEV
```

**Sources**: [kernel-module/picoevb-rdma.c:1281-1294](), [kernel-module/picoevb-rdma.c:1138-1230](), [kernel-module/picoevb-rdma.c:1232-1242]()

### Device Identification

The module supports two FPGA boards, distinguished by PCI sub-device ID:

| Board | PCI Sub-Device ID | FPGA RAM Size | H2C Channels | Driver Data |
|-------|-------------------|---------------|--------------|-------------|
| PicoEVB | 0x0001 | 64 KB | 1 | `drvdata_picoevb` |
| HTG-K800 | 0x0002 | 2 GB | 1 | `drvdata_htg_k800` |

**Sources**: [kernel-module/picoevb-rdma.c:1248-1271]()

### BAR Layout

The module maps two Base Address Registers (BARs):

- **BAR 0 (BAR_GPIO)**: GPIO and LED control registers
- **BAR 1 (BAR_DMA)**: Xilinx DMA engine registers

**Sources**: [kernel-module/picoevb-rdma.c:39-40](), [kernel-module/picoevb-rdma.c:1201-1207]()

## IOCTL Command Dispatch

User-space applications communicate with the module through IOCTL commands. The `pevb_fops_unlocked_ioctl()` function dispatches commands to specialized handlers:

```mermaid
graph TD
    IOCTL["pevb_fops_unlocked_ioctl()<br/>cmd, arg"]
    
    LED_CMD["PICOEVB_IOC_LED"]
    PIN_CMD["PICOEVB_IOC_PIN_CUDA"]
    UNPIN_CMD["PICOEVB_IOC_UNPIN_CUDA"]
    H2C_CMD["PICOEVB_IOC_H2C_DMA"]
    C2H_CMD["PICOEVB_IOC_C2H_DMA"]
    H2C2H_CMD["PICOEVB_IOC_H2C2H_DMA"]
    CARD_CMD["PICOEVB_IOC_CARD_INFO"]
    
    LED_HANDLER["pevb_ioctl_led()"]
    PIN_HANDLER["pevb_ioctl_pin_cuda()"]
    UNPIN_HANDLER["pevb_ioctl_unpin_cuda()"]
    H2C_HANDLER["pevb_ioctl_h2c_dma()"]
    C2H_HANDLER["pevb_ioctl_c2h_dma()"]
    H2C2H_HANDLER["pevb_ioctl_h2c2h_dma()"]
    CARD_HANDLER["pevb_ioctl_card_info()"]
    
    IOCTL --> LED_CMD
    IOCTL --> PIN_CMD
    IOCTL --> UNPIN_CMD
    IOCTL --> H2C_CMD
    IOCTL --> C2H_CMD
    IOCTL --> H2C2H_CMD
    IOCTL --> CARD_CMD
    
    LED_CMD --> LED_HANDLER
    PIN_CMD --> PIN_HANDLER
    UNPIN_CMD --> UNPIN_HANDLER
    H2C_CMD --> H2C_HANDLER
    C2H_CMD --> C2H_HANDLER
    H2C2H_CMD --> H2C2H_HANDLER
    CARD_CMD --> CARD_HANDLER
    
    LED_HANDLER -.->|"writes GPIO register"| GPIO["BAR_GPIO + 0"]
    PIN_HANDLER -.->|"nvidia_p2p_get_pages()"| P2P["NVIDIA P2P API"]
    H2C_HANDLER -.->|"host to card"| DMA["DMA Engine"]
    C2H_HANDLER -.->|"card to host"| DMA
    H2C2H_HANDLER -.->|"host to card to host"| DMA
```

**Sources**: [kernel-module/picoevb-rdma.c:1104-1129]()

## Memory Management

### Two-Path Memory Handling

The module handles two fundamentally different memory types through a unified abstraction:

```mermaid
graph TB
    subgraph "User Space Memory"
        MALLOC["malloc() buffer<br/>or<br/>cudaHostAlloc() buffer"]
        CUDAMALLOC["cudaMalloc() buffer<br/>GPU device memory"]
    end
    
    subgraph "Kernel Module: Memory Acquisition"
        GET_PAGES["pevb_get_userbuf_pages()"]
        GET_CUDA["pevb_get_userbuf_cuda()"]
    end
    
    subgraph "Kernel: Page Pinning"
        GUP["get_user_pages()<br/>pins pages in memory"]
        P2P_GET["nvidia_p2p_get_pages()<br/>pins GPU pages"]
    end
    
    subgraph "Kernel: DMA Mapping"
        DMA_MAP_SG["dma_map_sg()<br/>creates IOVA mapping"]
        P2P_MAP["nvidia_p2p_dma_map_pages()<br/>creates IOVA mapping"]
    end
    
    subgraph "Result: pevb_userbuf"
        UBUF["pevb_userbuf<br/>unified representation"]
        DMAS["dmas[] array<br/>physical address segments"]
    end
    
    MALLOC --> GET_PAGES
    CUDAMALLOC --> GET_CUDA
    
    GET_PAGES --> GUP
    GET_CUDA --> P2P_GET
    
    GUP --> DMA_MAP_SG
    P2P_GET --> P2P_MAP
    
    DMA_MAP_SG --> UBUF
    P2P_MAP --> UBUF
    
    UBUF --> DMAS
```

**Sources**: [kernel-module/picoevb-rdma.c:417-485](), [kernel-module/picoevb-rdma.c:356-414]()

### CUDA Memory Pinning Workflow

For CUDA memory (`cudaMalloc()` or `cudaHostAlloc()`), the module uses NVIDIA's P2P API:

1. **Pin Request**: User calls `PICOEVB_IOC_PIN_CUDA` with virtual address and size
2. **Alignment**: Module aligns VA to GPU page boundaries (4KB for iGPU, 64KB for dGPU)
3. **Get Pages**: `nvidia_p2p_get_pages()` pins the GPU memory and returns a page table
4. **Allocate Handle**: Module stores the pinned surface in IDR and returns a handle
5. **DMA Operations**: Subsequent DMA operations use the handle to reference the pinned memory
6. **Unpin**: User calls `PICOEVB_IOC_UNPIN_CUDA` or closes file descriptor to release

**Sources**: [kernel-module/picoevb-rdma.c:228-295](), [kernel-module/picoevb-rdma.c:297-331]()

### GPU Page Size Handling

The module handles different GPU page sizes based on build configuration:

| Configuration | Page Size | Page Shift | Usage |
|---------------|-----------|------------|-------|
| `NV_BUILD_DGPU` | 64 KB | 16 | Discrete GPUs (Quadro, Tesla) |
| Default (iGPU) | 4 KB | 12 | Integrated GPUs (Jetson, Drive) |

**Sources**: [kernel-module/picoevb-rdma.c:42-49]()

### Regular Memory Pinning Workflow

For regular host memory (`malloc()`), the module uses standard Linux memory management:

1. **Calculate Pages**: Determine page count from VA and length
2. **Get User Pages**: `get_user_pages()` pins pages in physical memory
3. **Build Scatter-Gather Table**: `sg_alloc_table_from_pages()` creates SG list
4. **DMA Mapping**: `dma_map_sg()` creates IOMMU/IOVA mappings
5. **Extract Segments**: Iterate through SG list to populate `dmas[]` array

**Sources**: [kernel-module/picoevb-rdma.c:417-485]()

### DMA Chunk Coalescing

The `pevb_userbuf_add_dma_chunk()` function optimizes the DMA segment list by merging adjacent physical address ranges, reducing the number of DMA operations needed:

**Sources**: [kernel-module/picoevb-rdma.c:334-353]()

## DMA Operations

### Three Transfer Patterns

The module implements three DMA patterns, each with its own use case:

```mermaid
graph LR
    subgraph "H2C: Host to Card"
        H2C_SRC["Host Memory<br/>malloc or CUDA"]
        H2C_DST["FPGA RAM<br/>64KB or 2GB"]
        H2C_SRC -->|"pevb_dma_h2c_multi()"| H2C_DST
    end
    
    subgraph "C2H: Card to Host"
        C2H_SRC["FPGA RAM<br/>64KB or 2GB"]
        C2H_DST["Host Memory<br/>malloc or CUDA"]
        C2H_SRC -->|"pevb_dma_c2h_multi()"| C2H_DST
    end
    
    subgraph "H2C2H: Host-Card-Host"
        H2C2H_SRC["Source Memory<br/>malloc or CUDA"]
        H2C2H_FPGA["FPGA RAM<br/>temporary buffer"]
        H2C2H_DST["Dest Memory<br/>malloc or CUDA"]
        H2C2H_SRC -->|"H2C"| H2C2H_FPGA
        H2C2H_FPGA -->|"C2H"| H2C2H_DST
    end
```

**Sources**: [kernel-module/picoevb-rdma.c:790-848](), [kernel-module/picoevb-rdma.c:850-908](), [kernel-module/picoevb-rdma.c:729-788]()

### DMA Transfer Chunking

All DMA functions (`pevb_dma_h2c_multi()`, `pevb_dma_c2h_multi()`, `pevb_dma_h2c2h_multi()`) iterate through user buffer segments and chunk transfers based on hardware constraints:

| Constraint | Value | Source |
|------------|-------|--------|
| Max descriptor length | Word-aligned limit | `XLNX_DMA_DESC_LEN_MAX_WORD_ALIGNED` |
| FPGA RAM size | 64KB (PicoEVB) or 2GB (HTG-K800) | `pevb->drvdata->fpga_ram_size` |
| User buffer segment | Variable | From `dmas[]` array |

The loop selects the minimum of these constraints for each chunk, ensuring no single DMA operation exceeds hardware capabilities.

**Sources**: [kernel-module/picoevb-rdma.c:762-780]()

### DMA Descriptor Format

Each DMA operation uses a single descriptor programmed into coherent DMA memory:

```mermaid
graph LR
    subgraph "struct xlnx_dma_desc"
        CONTROL["control<br/>MAGIC | EOP | COMPLETED | STOP"]
        LEN["len<br/>transfer length"]
        SRC_LOW["src_adr<br/>source address [31:0]"]
        SRC_HIGH["src_adr_hi<br/>source address [63:32]"]
        DST_LOW["dst_adr<br/>dest address [31:0]"]
        DST_HIGH["dst_adr_hi<br/>dest address [63:32]"]
        NXT_LOW["nxt_adr<br/>next descriptor [31:0]"]
        NXT_HIGH["nxt_adr_hi<br/>next descriptor [63:32]"]
    end
```

For H2C transfers:
- Source: Host/GPU physical address from `pevb_userbuf.dmas[]`
- Destination: FPGA RAM offset

For C2H transfers:
- Source: FPGA RAM offset
- Destination: Host/GPU physical address from `pevb_userbuf.dmas[]`

**Sources**: [kernel-module/picoevb-rdma.c:679-702](), [kernel-module/picoevb-rdma.c:704-727]()

### Core DMA Execution

The `pevb_dma()` function implements the low-level DMA execution sequence:

```mermaid
sequenceDiagram
    participant Caller
    participant pevb_dma
    participant Hardware
    participant IRQ as pevb_irq_handler
    
    Caller->>pevb_dma: c2h flag
    pevb_dma->>pevb_dma: reinit_completion(&dma_xfer_cmpl)
    pevb_dma->>Hardware: Write descriptor address to SGDMA registers
    pevb_dma->>Hardware: Clear status registers
    pevb_dma->>Hardware: Enable channel and top-level IRQs
    pevb_dma->>Hardware: Arm performance counters
    pevb_dma->>Hardware: wmb() + Write RUN bit to H2C_CTRL/C2H_CTRL
    pevb_dma->>pevb_dma: wait_for_completion_interruptible(&dma_xfer_cmpl)
    Hardware->>Hardware: Execute DMA transfer
    Hardware->>IRQ: Raise interrupt on completion/error
    IRQ->>IRQ: Read status register
    IRQ->>IRQ: Check for error bits
    IRQ->>IRQ: complete(&dma_xfer_cmpl)
    pevb_dma->>pevb_dma: Check error flags
    pevb_dma->>Hardware: Disable IRQs
    pevb_dma->>Hardware: Halt descriptor fetch
    pevb_dma->>Hardware: Cancel channel operation
    pevb_dma->>Hardware: Read performance counters
    pevb_dma->>Caller: Return status
```

**Sources**: [kernel-module/picoevb-rdma.c:570-677]()

## Interrupt Handling

### IRQ Handler Flow

The interrupt handler `pevb_irq_handler()` services completion interrupts from both H2C and C2H channels:

```mermaid
graph TB
    IRQ_ENTRY["pevb_irq_handler()"]
    
    H2C_STATUS["Read H2C_STATUS_RD_CLR"]
    H2C_CHECK{"Status != 0?"}
    H2C_ERROR["Check bad_status bits<br/>set pevb->h2c_error"]
    H2C_COMPLETE["complete(&dma_xfer_cmpl)"]
    
    C2H_STATUS["Read C2H_STATUS_RD_CLR"]
    C2H_CHECK{"Status != 0?"}
    C2H_ERROR["Check bad_status bits<br/>set pevb->c2h_error"]
    C2H_COMPLETE["complete(&dma_xfer_cmpl)"]
    
    RETURN["Return IRQ_HANDLED or IRQ_NONE"]
    
    IRQ_ENTRY --> H2C_STATUS
    H2C_STATUS --> H2C_CHECK
    H2C_CHECK -->|Yes| H2C_ERROR
    H2C_ERROR --> H2C_COMPLETE
    H2C_CHECK -->|No| C2H_STATUS
    
    C2H_STATUS --> C2H_CHECK
    C2H_CHECK -->|Yes| C2H_ERROR
    C2H_ERROR --> C2H_COMPLETE
    C2H_CHECK -->|No| RETURN
    
    H2C_COMPLETE --> C2H_STATUS
    C2H_COMPLETE --> RETURN
```

### Error Detection

The handler checks for error conditions in the status register:

| Error Flag | Meaning |
|------------|---------|
| `DESC_ERR` | Descriptor fetch error |
| `WRITE_ERR` | PCIe write error |
| `READ_ERR` | PCIe read error |
| `IDLE_STOPPED` | Channel stopped while idle |
| `INVALID_LEN` | Invalid transfer length |
| `MAGIC_STOPPED` | Descriptor magic mismatch |
| `ALIGN_MISMATCH` | Address alignment error |

If any error bit is set, the handler sets the corresponding error flag (`pevb->h2c_error` or `pevb->c2h_error`) which causes `pevb_dma()` to return `-EIO`.

**Sources**: [kernel-module/picoevb-rdma.c:529-568](), [kernel-module/picoevb-rdma.c:534-544]()

## Build Configuration

### Conditional CUDA Support

The module supports building without CUDA support using the `NV_BUILD_NO_CUDA` flag, which disables:
- CUDA memory pinning IOCTLs (`PICOEVB_IOC_PIN_CUDA`, `PICOEVB_IOC_UNPIN_CUDA`)
- P2P API integration
- CUDA-specific code paths in DMA handlers

**Sources**: [kernel-module/picoevb-rdma.c:26-32]()

### Platform-Specific P2P Headers

The module includes different P2P API headers based on build configuration:

| Build Flag | Header | Platform |
|------------|--------|----------|
| `NV_BUILD_DGPU` | `<nv-p2p.h>` | Discrete GPU (Quadro, Tesla) |
| Default | `<linux/nv-p2p.h>` | Integrated GPU (Jetson, Drive) |

The APIs differ slightly in function signatures (dGPU versions include additional PID/UID parameters).

**Sources**: [kernel-module/picoevb-rdma.c:27-31]()

## Synchronization Mechanisms

The module uses multiple synchronization primitives:

| Primitive | Field | Purpose |
|-----------|-------|---------|
| Semaphore | `pevb->sem` | Serializes DMA operations (only one transfer at a time) |
| Mutex | `pevb_file->lock` | Protects per-file CUDA surface IDR |
| Completion | `pevb->dma_xfer_cmpl` | Waits for IRQ-signaled DMA completion |

**Sources**: [kernel-module/picoevb-rdma.c:65](), [kernel-module/picoevb-rdma.c:68](), [kernel-module/picoevb-rdma.c:75](), [kernel-module/picoevb-rdma.c:1164]()

## DMA Coherency and Memory Barriers

Before starting a DMA operation, the module ensures all memory writes are visible to hardware:

```c
wmb();  // Write memory barrier
pevb_writel(pevb, BAR_DMA, val, reg);  // Start DMA
```

This guarantees that descriptor contents and configuration register writes complete before the DMA engine reads them.

**Sources**: [kernel-module/picoevb-rdma.c:629-634]()

## Register Access Helpers

The module provides debug-instrumented register access functions:

- `pevb_readl()`: Reads 32-bit register with debug logging
- `pevb_writel()`: Writes 32-bit register with debug logging

Both functions accept BAR index and register offset, using the `iomap` array for actual memory access.

**Sources**: [kernel-module/picoevb-rdma.c:121-135]()

## Device File Operations Summary

| Operation | Function | Description |
|-----------|----------|-------------|
| Open | `pevb_fops_open()` | Allocates `pevb_file`, initializes mutex and IDR |
| Release | `pevb_fops_release()` | Unpins all CUDA surfaces, frees `pevb_file` |
| IOCTL | `pevb_fops_unlocked_ioctl()` | Dispatches to command-specific handlers |

**Sources**: [kernel-module/picoevb-rdma.c:1131-1136]()

---

