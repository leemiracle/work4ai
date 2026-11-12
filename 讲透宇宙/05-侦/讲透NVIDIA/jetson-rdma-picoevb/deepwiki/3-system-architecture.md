<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/jetson-rdma-picoevb · page 3 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [kernel-module/picoevb-rdma.c](kernel-module/picoevb-rdma.c)
- [rdma-flow.svg](rdma-flow.svg)

</details>



This page provides a comprehensive overview of the jetson-rdma-picoevb system architecture, focusing on the interactions between user space applications, the kernel module, and hardware components. For detailed information about specific aspects, see:
- RDMA concepts and GPUDirect technology: [RDMA Fundamentals](#3.1)
- H2C, C2H, and H2C2H transfer mechanisms: [Data Transfer Patterns](#3.2)
- Memory pinning and mapping strategies: [Memory Management](#3.3)
- Kernel module implementation details: [Kernel Module](#4)
- Application programming interfaces: [Client Applications](#5)

## Three-Tier System Architecture

The system is organized into three distinct layers, each with well-defined responsibilities and interfaces.

```mermaid
graph TB
    subgraph UserSpace["User Space"]
        direction TB
        Apps["Applications<br/>rdma-cuda<br/>rdma-malloc<br/>rdma-*-perf<br/>set-leds"]
        LibC["Standard C Library"]
    end
    
    subgraph KernelSpace["Kernel Space"]
        direction TB
        CharDev["/dev/picoevb<br/>Character Device"]
        FileOps["struct file_operations<br/>pevb_fops"]
        IOCTLHandlers["IOCTL Handlers<br/>pevb_ioctl_*"]
        
        DMAOps["DMA Operations<br/>pevb_dma_h2c_multi()<br/>pevb_dma_c2h_multi()<br/>pevb_dma_h2c2h_multi()"]
        
        MemMgmt["Memory Management<br/>pevb_get_userbuf_pages()<br/>pevb_get_userbuf_cuda()"]
        
        P2PAPI["NVIDIA P2P API<br/>nvidia_p2p_get_pages()<br/>nvidia_p2p_dma_map_pages()"]
        
        PCIDriver["PCI Driver<br/>pevb_driver<br/>pevb_probe()<br/>pevb_remove()"]
        
        IRQHandler["Interrupt Handler<br/>pevb_irq_handler()"]
    end
    
    subgraph Hardware["Hardware Layer"]
        direction TB
        PCIeIF["PCIe Interface"]
        BARGPIO["BAR 0: GPIO Registers"]
        BARDMA["BAR 1: DMA Registers"]
        XilinxDMA["Xilinx DMA Engine<br/>H2C Channel<br/>C2H Channel"]
        FPGARAM["FPGA RAM<br/>64KB or 2GB"]
        GPU["NVIDIA GPU<br/>Device Memory"]
    end
    
    Apps -->|"open()<br/>ioctl()<br/>close()"| LibC
    LibC -->|"syscalls"| CharDev
    CharDev --> FileOps
    FileOps -->|"pevb_fops_unlocked_ioctl()"| IOCTLHandlers
    
    IOCTLHandlers --> DMAOps
    IOCTLHandlers --> MemMgmt
    
    MemMgmt -->|"CUDA memory"| P2PAPI
    MemMgmt -->|"host memory<br/>get_user_pages()<br/>dma_map_sg()"| DMAOps
    
    P2PAPI -->|"pin & map"| GPU
    
    DMAOps -->|"program descriptors"| XilinxDMA
    
    PCIDriver -->|"pcim_iomap_regions()"| BARGPIO
    PCIDriver -->|"pcim_iomap_regions()"| BARDMA
    PCIDriver -->|"request_irq()"| IRQHandler
    
    IRQHandler -->|"read status"| BARDMA
    
    XilinxDMA -->|"DMA transactions"| PCIeIF
    XilinxDMA -->|"access"| FPGARAM
    
    PCIeIF --> GPU
    
    BARDMA --> XilinxDMA
    BARGPIO -->|"LED control"| Hardware
    
    style CharDev fill:#f9f9f9
    style FileOps fill:#f9f9f9
    style PCIDriver fill:#f9f9f9
```

**Sources:** [kernel-module/picoevb-rdma.c:1-1312]()

### User Space Layer

Applications interact with the kernel module exclusively through the character device `/dev/picoevb`. The character device is created during module initialization [kernel-module/picoevb-rdma.c:1188-1189]() and provides a file-based interface accessible via standard system calls.

| Component | Code Symbol | Purpose |
|-----------|-------------|---------|
| Character device node | `/dev/picoevb` | Entry point for user-space communication |
| Device class | `pevb_class` | Manages device node creation [kernel-module/picoevb-rdma.c:119]() |
| Character device | `struct cdev pevb->cdev` | Kernel representation [kernel-module/picoevb-rdma.c:63]() |
| Device number | `dev_t pevb->devt` | Major/minor number allocation [kernel-module/picoevb-rdma.c:62]() |

**Sources:** [kernel-module/picoevb-rdma.c:119](), [kernel-module/picoevb-rdma.c:56-71](), [kernel-module/picoevb-rdma.c:1175-1193]()

### Kernel Space Layer

The kernel module `picoevb-rdma.ko` implements a PCI device driver that manages DMA operations and integrates with NVIDIA's P2P API.

#### Core Data Structures

```mermaid
graph LR
    subgraph PerDevice["Per-Device State"]
        pevb["struct pevb<br/>Main device context"]
        pdev["struct pci_dev *pdev<br/>PCI device"]
        iomap["void __iomem **iomap<br/>BAR mappings"]
        descs["void *descs_ptr<br/>DMA descriptors"]
        sem["struct semaphore sem<br/>Transfer serialization"]
        cmpl["struct completion dma_xfer_cmpl<br/>DMA completion signal"]
    end
    
    subgraph PerFileDescriptor["Per-File-Descriptor State"]
        pevb_file["struct pevb_file<br/>File private data"]
        lock["struct mutex lock<br/>Protects surfaces"]
        cuda_surfaces["struct idr cuda_surfaces<br/>Pinned CUDA buffers"]
    end
    
    subgraph PerBuffer["Per-Buffer State"]
        userbuf["struct pevb_userbuf<br/>Buffer DMA mapping"]
        dmas["struct pevb_userbuf_dma *dmas<br/>Scatter-gather list"]
        pages_or_cuda["union: pages or cuda<br/>Backend-specific state"]
    end
    
    pevb --> pdev
    pevb --> iomap
    pevb --> descs
    pevb --> sem
    pevb --> cmpl
    
    pevb_file --> lock
    pevb_file --> cuda_surfaces
    
    userbuf --> dmas
    userbuf --> pages_or_cuda
```

**Sources:** [kernel-module/picoevb-rdma.c:56-71](), [kernel-module/picoevb-rdma.c:73-77](), [kernel-module/picoevb-rdma.c:95-117]()

#### File Operations

The `pevb_fops` structure defines the character device interface:

```mermaid
graph TD
    open["pevb_fops_open()"]
    release["pevb_fops_release()"]
    ioctl["pevb_fops_unlocked_ioctl()"]
    
    open -->|"allocate"| pevb_file["struct pevb_file"]
    open -->|"initialize"| idr["idr_init(&cuda_surfaces)"]
    
    release -->|"iterate"| cuda_surfs["cuda_surfaces IDR"]
    release -->|"for each surface"| put_pages["nvidia_p2p_put_pages()"]
    release -->|"free"| pevb_file2["struct pevb_file"]
    
    ioctl -->|"PICOEVB_IOC_LED"| led["pevb_ioctl_led()"]
    ioctl -->|"PICOEVB_IOC_PIN_CUDA"| pin["pevb_ioctl_pin_cuda()"]
    ioctl -->|"PICOEVB_IOC_UNPIN_CUDA"| unpin["pevb_ioctl_unpin_cuda()"]
    ioctl -->|"PICOEVB_IOC_H2C_DMA"| h2c["pevb_ioctl_h2c_dma()"]
    ioctl -->|"PICOEVB_IOC_C2H_DMA"| c2h["pevb_ioctl_c2h_dma()"]
    ioctl -->|"PICOEVB_IOC_H2C2H_DMA"| h2c2h["pevb_ioctl_h2c2h_dma()"]
    ioctl -->|"PICOEVB_IOC_CARD_INFO"| info["pevb_ioctl_card_info()"]
```

**Sources:** [kernel-module/picoevb-rdma.c:1131-1136](), [kernel-module/picoevb-rdma.c:137-153](), [kernel-module/picoevb-rdma.c:176-217](), [kernel-module/picoevb-rdma.c:1104-1129]()

### Hardware Layer

The hardware layer consists of two primary components accessed via PCIe Base Address Registers (BARs):

| BAR | Symbol | Offset | Purpose |
|-----|--------|--------|---------|
| 0 | `BAR_GPIO` | `pevb->iomap[0]` | GPIO and LED control registers |
| 1 | `BAR_DMA` | `pevb->iomap[1]` | Xilinx DMA engine registers |

The Xilinx DMA engine provides separate H2C (Host-to-Card) and C2H (Card-to-Host) channels, each with its own control, status, and descriptor registers. Register definitions are located in [kernel-module/picoevb-rdma.h]().

**Sources:** [kernel-module/picoevb-rdma.c:39-40](), [kernel-module/picoevb-rdma.c:1201-1207]()

## IOCTL Command Processing Flow

The kernel module processes seven distinct IOCTL commands, each implementing a specific operation.

```mermaid
graph TB
    UserApp["User Application<br/>ioctl(fd, cmd, &params)"]
    
    Dispatch["pevb_fops_unlocked_ioctl()<br/>Command dispatch"]
    
    LED["PICOEVB_IOC_LED<br/>pevb_ioctl_led()"]
    PIN["PICOEVB_IOC_PIN_CUDA<br/>pevb_ioctl_pin_cuda()"]
    UNPIN["PICOEVB_IOC_UNPIN_CUDA<br/>pevb_ioctl_unpin_cuda()"]
    H2C["PICOEVB_IOC_H2C_DMA<br/>pevb_ioctl_h2c_dma()"]
    C2H["PICOEVB_IOC_C2H_DMA<br/>pevb_ioctl_c2h_dma()"]
    H2C2H["PICOEVB_IOC_H2C2H_DMA<br/>pevb_ioctl_h2c2h_dma()"]
    INFO["PICOEVB_IOC_CARD_INFO<br/>pevb_ioctl_card_info()"]
    
    UserApp --> Dispatch
    
    Dispatch --> LED
    Dispatch --> PIN
    Dispatch --> UNPIN
    Dispatch --> H2C
    Dispatch --> C2H
    Dispatch --> H2C2H
    Dispatch --> INFO
    
    LED -->|"pevb_writel()"| GPIORegs["BAR_GPIO + 0x00"]
    
    PIN -->|"nvidia_p2p_get_pages()"| P2PPin["Pin GPU memory"]
    PIN -->|"idr_alloc()"| StoreHandle["Store in cuda_surfaces"]
    
    UNPIN -->|"idr_find() + idr_remove()"| FindHandle["Lookup handle"]
    UNPIN -->|"nvidia_p2p_put_pages()"| P2PUnpin["Unpin GPU memory"]
    
    H2C -->|"pevb_get_userbuf_*()"| MapSrc["Map source buffer"]
    H2C -->|"pevb_dma_h2c_multi()"| TransferH2C["Execute H2C transfer"]
    
    C2H -->|"pevb_get_userbuf_*()"| MapDst["Map destination buffer"]
    C2H -->|"pevb_dma_c2h_multi()"| TransferC2H["Execute C2H transfer"]
    
    H2C2H -->|"pevb_get_userbuf_*()"| MapBoth["Map src & dst buffers"]
    H2C2H -->|"pevb_dma_h2c2h_multi()"| TransferH2C2H["Execute H2C2H transfer"]
    
    INFO -->|"copy_to_user()"| ReturnInfo["Return fpga_ram_size"]
```

**Sources:** [kernel-module/picoevb-rdma.c:1104-1129](), [kernel-module/picoevb-rdma-ioctl.h]()

### Memory Buffer Acquisition

Before DMA operations, the kernel must map user-space buffers into DMA-accessible addresses. The `pevb_get_userbuf_*` functions handle two distinct memory types:

```mermaid
graph TD
    CheckCUDA{"flags &<br/>*_IS_CUDA?"}
    
    GetUserPages["pevb_get_userbuf_pages()<br/>Regular host memory"]
    GetCUDA["pevb_get_userbuf_cuda()<br/>CUDA-managed memory"]
    
    GUP["get_user_pages()<br/>Pin user pages"]
    SGAlloc["sg_alloc_table_from_pages()<br/>Build scatter-gather table"]
    DMAMapSG["dma_map_sg()<br/>Map for DMA"]
    
    IDRFind["idr_find(&cuda_surfaces)<br/>Lookup pinned surface"]
    P2PDMAMap["nvidia_p2p_dma_map_pages()<br/>Map GPU memory for DMA"]
    
    BuildDMAList["pevb_userbuf_add_dma_chunk()<br/>Build DMA address list"]
    
    CheckCUDA -->|"No"| GetUserPages
    CheckCUDA -->|"Yes"| GetCUDA
    
    GetUserPages --> GUP
    GUP --> SGAlloc
    SGAlloc --> DMAMapSG
    DMAMapSG --> BuildDMAList
    
    GetCUDA --> IDRFind
    IDRFind --> P2PDMAMap
    P2PDMAMap --> BuildDMAList
    
    BuildDMAList --> Return["struct pevb_userbuf<br/>with dmas[] array"]
```

**Sources:** [kernel-module/picoevb-rdma.c:417-485](), [kernel-module/picoevb-rdma.c:356-414](), [kernel-module/picoevb-rdma.c:334-353]()

## DMA Transfer Execution

DMA transfers are orchestrated through the Xilinx DMA engine, which operates on descriptor-based scatter-gather DMA.

```mermaid
graph TB
    MultiFunc["pevb_dma_*_multi()<br/>High-level transfer function"]
    
    Chunk["Chunking Loop<br/>Split into DMA-sized pieces"]
    
    SingleFunc["pevb_dma_h2c_single() or<br/>pevb_dma_c2h_single()"]
    
    BuildDesc["Build DMA Descriptor<br/>struct xlnx_dma_desc"]
    
    ProgramRegs["Program DMA Registers<br/>pevb_dma()"]
    
    DescAddr["Write descriptor address<br/>H2C_SGDMA_DESC_LOW/HIGH_ADDR"]
    ClearStatus["Clear pending status<br/>H2C_STATUS_RD_CLR"]
    EnableIRQ["Enable interrupts<br/>H2C_INT_EN, IRQ_CH_INT_EN_W1S"]
    StartDMA["Start DMA engine<br/>H2C_CTRL with RUN bit"]
    
    WaitComplete["wait_for_completion_interruptible()<br/>Wait for dma_xfer_cmpl"]
    
    IRQ["pevb_irq_handler()<br/>Interrupt fires"]
    ReadStatus["Read H2C_STATUS_RD_CLR or<br/>C2H_STATUS_RD_CLR"]
    CompleteSignal["complete(&dma_xfer_cmpl)"]
    
    Cleanup["Disable IRQs<br/>Cancel operation<br/>Read perf counters"]
    
    MultiFunc -->|"down_interruptible(&sem)"| Chunk
    Chunk -->|"foreach DMA chunk"| SingleFunc
    SingleFunc --> BuildDesc
    BuildDesc --> ProgramRegs
    
    ProgramRegs --> DescAddr
    DescAddr --> ClearStatus
    ClearStatus --> EnableIRQ
    EnableIRQ --> StartDMA
    StartDMA -->|"wmb()"| WaitComplete
    
    WaitComplete -.->|"interrupted by"| IRQ
    IRQ --> ReadStatus
    ReadStatus --> CompleteSignal
    CompleteSignal -.->|"wakes"| WaitComplete
    
    WaitComplete --> Cleanup
    Cleanup -->|"up(&sem)"| Return["Return to caller"]
```

**Sources:** [kernel-module/picoevb-rdma.c:790-848](), [kernel-module/picoevb-rdma.c:850-908](), [kernel-module/picoevb-rdma.c:679-702](), [kernel-module/picoevb-rdma.c:704-727](), [kernel-module/picoevb-rdma.c:570-677](), [kernel-module/picoevb-rdma.c:529-568]()

### DMA Descriptor Structure

Each DMA operation is described by a `struct xlnx_dma_desc` programmed into coherent memory:

| Field | Type | Purpose |
|-------|------|---------|
| `control` | `u32` | Control flags: MAGIC, EOP, COMPLETED, STOP |
| `len` | `u32` | Transfer length in bytes |
| `src_adr` / `src_adr_hi` | `u64` | Source address (PCIe or FPGA RAM) |
| `dst_adr` / `dst_adr_hi` | `u64` | Destination address (PCIe or FPGA RAM) |
| `nxt_adr` / `nxt_adr_hi` | `u64` | Next descriptor (unused, always 0) |

The descriptor is allocated once during probe via `dmam_alloc_coherent()` [kernel-module/picoevb-rdma.c:1167-1173]() and reused for all transfers.

**Sources:** [kernel-module/picoevb-rdma.h](), [kernel-module/picoevb-rdma.c:688-699](), [kernel-module/picoevb-rdma.c:713-724]()

## CUDA P2P Integration

For CUDA memory transfers, the kernel module uses NVIDIA's P2P API to pin and map GPU memory for DMA access.

```mermaid
graph LR
    subgraph UserSpace["User Space"]
        CUDAAlloc["cudaMalloc() or<br/>cudaHostAlloc()"]
        IOCTLPin["ioctl(PICOEVB_IOC_PIN_CUDA)<br/>va, size"]
    end
    
    subgraph KernelSpace["Kernel Module"]
        PinHandler["pevb_ioctl_pin_cuda()"]
        AllocSurf["kzalloc(pevb_cuda_surface)"]
        GetPages["nvidia_p2p_get_pages()"]
        IDRAlloc["idr_alloc(&cuda_surfaces)"]
        ReturnHandle["Return handle to user"]
    end
    
    subgraph NVP2P["NVIDIA P2P Driver"]
        PinImpl["Pin GPU pages<br/>struct nvidia_p2p_page_table"]
        Callback["Register callback<br/>pevb_p2p_free_callback"]
    end
    
    subgraph DMATime["During DMA Transfer"]
        IDRFind["idr_find(handle)"]
        DMAMap["nvidia_p2p_dma_map_pages()"]
        BuildDMAList["Build dmas[] array from<br/>map->hw_address[] or<br/>map->dma_addresses[]"]
    end
    
    CUDAAlloc --> IOCTLPin
    IOCTLPin --> PinHandler
    PinHandler --> AllocSurf
    AllocSurf --> GetPages
    GetPages --> PinImpl
    PinImpl --> Callback
    GetPages --> IDRAlloc
    IDRAlloc --> ReturnHandle
    
    ReturnHandle -.->|"store handle"| UserSpace
    
    DMATime --> IDRFind
    IDRFind --> DMAMap
    DMAMap --> BuildDMAList
```

**Sources:** [kernel-module/picoevb-rdma.c:228-295](), [kernel-module/picoevb-rdma.c:356-414](), [kernel-module/picoevb-rdma.c:156-173]()

### Platform-Specific Differences

The P2P API has different signatures and behaviors on iGPU (integrated GPU) vs. dGPU (discrete GPU) platforms, controlled by the `NV_BUILD_DGPU` compile-time flag:

| Aspect | iGPU (`linux/nv-p2p.h`) | dGPU (`nv-p2p.h`) |
|--------|--------------------------|-------------------|
| Header include | `#include <linux/nv-p2p.h>` [kernel-module/picoevb-rdma.c:30]() | `#include <nv-p2p.h>` [kernel-module/picoevb-rdma.c:28]() |
| Page size | 4KB (`GPU_PAGE_SHIFT = 12`) [kernel-module/picoevb-rdma.c:45]() | 64KB (`GPU_PAGE_SHIFT = 16`) [kernel-module/picoevb-rdma.c:43]() |
| `nvidia_p2p_get_pages()` signature | No PID/TID args [kernel-module/picoevb-rdma.c:254]() | Requires PID/TID (0, 0) [kernel-module/picoevb-rdma.c:250-254]() |
| `nvidia_p2p_dma_map_pages()` signature | Takes `struct device*` and direction [kernel-module/picoevb-rdma.c:382-383]() | Takes `struct pci_dev*` [kernel-module/picoevb-rdma.c:379-380]() |
| DMA address array | `map->hw_address[]` [kernel-module/picoevb-rdma.c:400]() | `map->dma_addresses[]` [kernel-module/picoevb-rdma.c:397]() |
| Callback behavior | Callback frees `cusurf` [kernel-module/picoevb-rdma.c:206-209]() | Must manually call callback [kernel-module/picoevb-rdma.c:204]() |

**Sources:** [kernel-module/picoevb-rdma.c:26-32](), [kernel-module/picoevb-rdma.c:42-49](), [kernel-module/picoevb-rdma.c:250-254](), [kernel-module/picoevb-rdma.c:379-411]()

## PCI Driver Initialization

The kernel module registers as a PCI driver and binds to specific vendor/device IDs.

```mermaid
graph TB
    ModInit["pevb_init()<br/>module_init"]
    ClassCreate["class_create('picoevb')"]
    PCIReg["pci_register_driver(&pevb_driver)"]
    
    Probe["pevb_probe()<br/>Called for matching device"]
    
    AllocPevb["devm_kzalloc(struct pevb)"]
    AllocDescs["dmam_alloc_coherent()<br/>DMA descriptor memory"]
    AllocChrdev["alloc_chrdev_region()"]
    CdevInit["cdev_init(&pevb->cdev)"]
    CdevAdd["cdev_add()"]
    DevCreate["device_create(pevb_class)"]
    
    EnablePCI["pcim_enable_device()"]
    MapBARs["pcim_iomap_regions()<br/>BAR_GPIO | BAR_DMA"]
    SetMaster["pci_set_master()<br/>pci_set_dma_mask(64-bit)"]
    ReqIRQ["request_irq(pevb_irq_handler)"]
    
    Remove["pevb_remove()<br/>Called at device removal"]
    FreeIRQ["free_irq()"]
    ClearMaster["pci_clear_master()"]
    DevDestroy["device_destroy()"]
    CdevDel["cdev_del()"]
    UnregChrdev["unregister_chrdev_region()"]
    
    ModInit --> ClassCreate
    ClassCreate --> PCIReg
    
    PCIReg -.->|"device found"| Probe
    
    Probe --> AllocPevb
    AllocPevb --> AllocDescs
    AllocDescs --> AllocChrdev
    AllocChrdev --> CdevInit
    CdevInit --> CdevAdd
    CdevAdd --> DevCreate
    DevCreate --> EnablePCI
    EnablePCI --> MapBARs
    MapBARs --> SetMaster
    SetMaster --> ReqIRQ
    
    ReqIRQ -.->|"device ready"| UserSpace["User space can open /dev/picoevb"]
    
    UserSpace -.->|"rmmod or device removal"| Remove
    
    Remove --> FreeIRQ
    FreeIRQ --> ClearMaster
    ClearMaster --> DevDestroy
    DevDestroy --> CdevDel
    CdevDel --> UnregChrdev
```

**Sources:** [kernel-module/picoevb-rdma.c:1281-1294](), [kernel-module/picoevb-rdma.c:1138-1230](), [kernel-module/picoevb-rdma.c:1232-1242]()

### Device Identification

The module supports two FPGA boards distinguished by PCI subsystem device ID:

```c
static const struct pci_device_id pevb_pci_ids[] = {
    PCI_ENTRY(0x0001, picoevb),     // 64KB FPGA RAM
    PCI_ENTRY(0x0002, htg_k800),    // 2GB FPGA RAM
    { },
};
```

Driver data specifies board-specific parameters:

| Board | Subsystem Device ID | `num_h2c_chans` | `fpga_ram_size` |
|-------|---------------------|-----------------|-----------------|
| PicoEVB | `0x0001` | 1 | `SZ_64K` (65536 bytes) |
| HTG-K800 | `0x0002` | 1 | `SZ_2G` (2147483648 bytes) |

**Sources:** [kernel-module/picoevb-rdma.c:1266-1271](), [kernel-module/picoevb-rdma.c:1248-1256]()

## System Resource Management

### Synchronization Primitives

The kernel module uses multiple synchronization mechanisms:

| Primitive | Symbol | Purpose | Scope |
|-----------|--------|---------|-------|
| Semaphore | `pevb->sem` | Serializes DMA operations [kernel-module/picoevb-rdma.c:65]() | Per-device |
| Completion | `pevb->dma_xfer_cmpl` | Waits for DMA completion [kernel-module/picoevb-rdma.c:68]() | Per-device |
| Mutex | `pevb_file->lock` | Protects CUDA surface IDR [kernel-module/picoevb-rdma.c:75]() | Per-file-descriptor |

The semaphore ensures only one DMA operation executes at a time, preventing concurrent access to shared hardware resources [kernel-module/picoevb-rdma.c:739](), [kernel-module/picoevb-rdma.c:800](), [kernel-module/picoevb-rdma.c:860]().

**Sources:** [kernel-module/picoevb-rdma.c:56-77](), [kernel-module/picoevb-rdma.c:1164]()

### Memory Allocation

| Resource | Allocation Function | Lifetime | Purpose |
|----------|---------------------|----------|---------|
| `struct pevb` | `devm_kzalloc()` [kernel-module/picoevb-rdma.c:1143]() | Device lifetime | Main device context |
| DMA descriptors | `dmam_alloc_coherent()` [kernel-module/picoevb-rdma.c:1167-1168]() | Device lifetime | Hardware-accessible descriptors |
| `struct pevb_file` | `kzalloc()` [kernel-module/picoevb-rdma.c:142]() | File descriptor lifetime | Per-open state |
| `struct pevb_cuda_surface` | `kzalloc()` [kernel-module/picoevb-rdma.c:239]() | Until unpinned or file close | Pinned CUDA buffer tracking |
| `struct pevb_userbuf.dmas` | `kmalloc_array()` [kernel-module/picoevb-rdma.c:388](), [kernel-module/picoevb-rdma.c:475]() | DMA operation duration | Scatter-gather DMA address list |

The use of managed allocation functions (`devm_*`, `dmam_*`) ensures automatic cleanup on device removal.

**Sources:** [kernel-module/picoevb-rdma.c:1143-1173](), [kernel-module/picoevb-rdma.c:142-144](), [kernel-module/picoevb-rdma.c:239-241]()

## Interrupt-Driven Completion

DMA transfers complete asynchronously via hardware interrupts.

```mermaid
sequenceDiagram
    participant User as User Application
    participant IOCTL as IOCTL Handler
    participant DMA as pevb_dma()
    participant HW as Xilinx DMA Engine
    participant IRQ as pevb_irq_handler()
    
    User->>IOCTL: ioctl(H2C_DMA/C2H_DMA)
    IOCTL->>DMA: pevb_dma_*_multi()
    DMA->>DMA: down_interruptible(&sem)
    DMA->>DMA: Build DMA descriptor
    DMA->>DMA: reinit_completion()
    DMA->>HW: Write descriptor address
    DMA->>HW: Enable channel IRQ
    DMA->>HW: Write H2C_CTRL with RUN bit
    DMA->>DMA: wait_for_completion_interruptible()
    
    Note over DMA: Thread blocks
    
    HW->>HW: Execute DMA transfer
    HW->>IRQ: Assert interrupt
    
    IRQ->>HW: Read H2C_STATUS_RD_CLR
    IRQ->>IRQ: Set h2c_error or c2h_error
    IRQ->>DMA: complete(&dma_xfer_cmpl)
    
    Note over DMA: Thread wakes
    
    DMA->>DMA: Check error flags
    DMA->>HW: Disable channel IRQ
    DMA->>HW: Cancel operation
    DMA->>HW: Read perf counters
    DMA->>DMA: up(&sem)
    DMA-->>IOCTL: Return status
    IOCTL-->>User: Return to user space
```

**Sources:** [kernel-module/picoevb-rdma.c:570-677](), [kernel-module/picoevb-rdma.c:529-568](), [kernel-module/picoevb-rdma.c:589](), [kernel-module/picoevb-rdma.c:636]()

### Error Detection

The interrupt handler checks status register bits for error conditions:

```c
const u32 bad_status =
    (XLNX_DMA_H2C_STATUS_DESC_ERR_MASK << XLNX_DMA_H2C_STATUS_DESC_ERR_SHIFT) |
    (XLNX_DMA_H2C_STATUS_WRITE_ERR_MASK << XLNX_DMA_H2C_STATUS_WRITE_ERR_SHIFT) |
    (XLNX_DMA_H2C_STATUS_READ_ERR_MASK << XLNX_DMA_H2C_STATUS_READ_ERR_SHIFT) |
    XLNX_DMA_H2C_STATUS_IDLE_STOPPED |
    XLNX_DMA_H2C_STATUS_INVALID_LEN |
    XLNX_DMA_H2C_STATUS_MAGIC_STOPPED |
    XLNX_DMA_H2C_STATUS_ALIGN_MISMATCH;
```

Any of these bits being set indicates a transfer failure, causing the DMA operation to return `-EIO` [kernel-module/picoevb-rdma.c:640-644]().

**Sources:** [kernel-module/picoevb-rdma.c:534-544](), [kernel-module/picoevb-rdma.c:552](), [kernel-module/picoevb-rdma.c:562]()

---

