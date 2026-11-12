<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/jetson-rdma-picoevb · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [kernel-module/picoevb-rdma.c](kernel-module/picoevb-rdma.c)

</details>



## Purpose and Scope

This document provides an introduction to the **jetson-rdma-picoevb** system, a hardware-based demonstration of NVIDIA GPUDirect RDMA technology. The system enables PCIe devices to directly access GPU memory, allowing zero-copy data transfer between CUDA-capable GPUs and FPGA hardware without CPU involvement.

This overview covers the system's purpose, architecture, major components, and supported hardware platforms. For detailed setup instructions, see [Getting Started](#2). For in-depth architectural concepts, see [System Architecture](#3). For component-specific documentation, see [Kernel Module](#4), [Client Applications](#5), and [FPGA Development](#6).

**Sources:** [README.md:1-15]()

## System Purpose

The jetson-rdma-picoevb system demonstrates **GPUDirect RDMA** (Remote Direct Memory Access), a technology that allows PCIe devices to read from and write to GPU memory directly without staging data through system memory or requiring CPU involvement. This enables:

- **Zero-copy data transfer** between GPU and PCIe devices
- **Reduced CPU overhead** by eliminating memory copy operations
- **Lower latency** by avoiding round-trips through system memory
- **Higher bandwidth utilization** through direct PCIe-to-GPU paths

The system uses FPGA boards as the PCIe device that performs DMA operations against CUDA-allocated memory. This serves as a reference implementation for developers building production systems that require high-performance GPU-to-hardware communication.

**Platform Support:**
- NVIDIA Jetson AGX Xavier (ARM64 with integrated GPU)
- NVIDIA Drive AGX Xavier (ARM64 with integrated GPU)
- x86 Linux PCs with Quadro or Tesla GPUs (discrete GPU)

**Sources:** [README.md:1-10](), [kernel-module/picoevb-rdma.c:26-32]()

## High-Level Architecture

```mermaid
graph TB
    subgraph UserSpace["User Space"]
        direction TB
        TESTS["Performance Tests<br/>rdma-cuda-c2h-perf<br/>rdma-cuda-h2c-perf<br/>rdma-malloc-c2h-perf<br/>rdma-malloc-h2c-perf"]
        FUNC["Functional Tests<br/>rdma-cuda<br/>rdma-malloc"]
        UTIL["Utilities<br/>set-leds"]
    end
    
    subgraph KernelSpace["Kernel Space"]
        direction TB
        CDEV["/dev/picoevb<br/>Character Device"]
        DRIVER["picoevb-rdma.ko<br/>PCI Driver Module"]
        IOCTL["picoevb-rdma-ioctl.h<br/>IOCTL Commands:<br/>PICOEVB_IOC_PIN_CUDA<br/>PICOEVB_IOC_H2C_DMA<br/>PICOEVB_IOC_C2H_DMA<br/>PICOEVB_IOC_H2C2H_DMA"]
    end
    
    subgraph Hardware["Hardware"]
        direction LR
        FPGA["FPGA Device<br/>PicoEVB or HTG-K800<br/>Xilinx DMA Engine<br/>Internal RAM Buffer"]
        GPU["NVIDIA GPU<br/>CUDA Memory"]
    end
    
    TESTS -->|"ioctl()"| CDEV
    FUNC -->|"ioctl()"| CDEV
    UTIL -->|"ioctl()"| CDEV
    
    CDEV --> IOCTL
    IOCTL --> DRIVER
    
    DRIVER -->|"nvidia_p2p_get_pages()<br/>nvidia_p2p_dma_map_pages()"| GPU
    DRIVER -->|"DMA descriptors<br/>xlnx_dma_desc"| FPGA
    
    FPGA <-.->|"GPUDirect RDMA<br/>PCIe DMA"| GPU
```

**Sources:** [kernel-module/picoevb-rdma.c:37-72](), [kernel-module/picoevb-rdma-ioctl.h](), [README.md:12-15]()

## Major Components

The system consists of three primary software layers and two hardware components:

### Software Components

| Component | File/Module | Purpose |
|-----------|-------------|---------|
| **Kernel Module** | `picoevb-rdma.ko` | PCI driver that manages FPGA device, orchestrates DMA operations, and integrates with NVIDIA P2P API for GPU memory access |
| **IOCTL Interface** | `picoevb-rdma-ioctl.h` | Defines user-kernel API including data structures (`picoevb_rdma_pin_cuda`, `picoevb_rdma_h2c_dma`, etc.) and command codes |
| **Client Applications** | `rdma-cuda.cu`, `rdma-malloc.c`, performance tests, utilities | User-space applications for testing data integrity and measuring transfer performance |

### Hardware Components

| Component | Specification | Role |
|-----------|--------------|------|
| **FPGA Board** | PicoEVB (64KB RAM, M.2) or HTG-K800 (2GB RAM, PCIe x16) | Acts as PCIe device performing DMA; contains Xilinx DMA engine and internal RAM buffer |
| **GPU** | NVIDIA Jetson/Drive iGPU or Quadro/Tesla dGPU | Target for CUDA memory allocations; supports P2P peer-to-peer access |

**Sources:** [kernel-module/picoevb-rdma.c:51-71](), [README.md:22-82](), [kernel-module/picoevb-rdma-ioctl.h]()

## Data Transfer Patterns

The system implements three DMA transfer patterns, all using the FPGA's internal RAM as an intermediate buffer:

```mermaid
graph LR
    subgraph HostMem["Host System Memory"]
        MALLOC["malloc() buffer<br/>Regular host memory"]
        CUDA_HOST["cudaHostAlloc() buffer<br/>Pinned host memory"]
        CUDA_DEV["cudaMalloc() buffer<br/>GPU device memory"]
    end
    
    subgraph KernelOps["Kernel Module Operations"]
        H2C["pevb_dma_h2c_multi()<br/>Host-to-Card DMA<br/>PICOEVB_IOC_H2C_DMA"]
        C2H["pevb_dma_c2h_multi()<br/>Card-to-Host DMA<br/>PICOEVB_IOC_C2H_DMA"]
        H2C2H["pevb_dma_h2c2h_multi()<br/>Host-Card-Host DMA<br/>PICOEVB_IOC_H2C2H_DMA"]
    end
    
    subgraph FPGA["FPGA Hardware"]
        RAM["Internal RAM<br/>64KB PicoEVB<br/>2GB HTG-K800"]
    end
    
    MALLOC -->|"get_user_pages()<br/>dma_map_sg()"| H2C
    MALLOC -->|"get_user_pages()<br/>dma_map_sg()"| C2H
    
    CUDA_HOST -->|"nvidia_p2p_get_pages()<br/>nvidia_p2p_dma_map_pages()"| H2C
    CUDA_DEV -->|"nvidia_p2p_get_pages()<br/>nvidia_p2p_dma_map_pages()"| C2H
    
    H2C -->|"writes"| RAM
    RAM -->|"reads"| C2H
    
    H2C2H -->|"H2C then C2H<br/>via RAM buffer"| RAM
```

### Transfer Pattern Details

| Pattern | IOCTL Command | Function | Description |
|---------|---------------|----------|-------------|
| **H2C** | `PICOEVB_IOC_H2C_DMA` | `pevb_dma_h2c_multi()` | Host-to-Card: Transfers data from system memory to FPGA RAM |
| **C2H** | `PICOEVB_IOC_C2H_DMA` | `pevb_dma_c2h_multi()` | Card-to-Host: Transfers data from FPGA RAM to system memory |
| **H2C2H** | `PICOEVB_IOC_H2C2H_DMA` | `pevb_dma_h2c2h_multi()` | Host-Card-Host: Copies data from one system memory location to another via FPGA RAM |

The H2C2H pattern is used for functional validation tests as it exercises both read and write paths in a single operation. The FPGA RAM size determines the maximum chunk size for each DMA operation: 64KB for PicoEVB, 2GB for HTG-K800.

**Sources:** [kernel-module/picoevb-rdma.c:679-908](), [kernel-module/picoevb-rdma-ioctl.h](), [README.md:352-359]()

## Kernel Module Architecture

```mermaid
graph TB
    subgraph FileOps["File Operations pevb_fops"]
        OPEN["pevb_fops_open()"]
        RELEASE["pevb_fops_release()"]
        IOCTL["pevb_fops_unlocked_ioctl()"]
    end
    
    subgraph IOCTLHandlers["IOCTL Handler Functions"]
        LED["pevb_ioctl_led()"]
        PIN["pevb_ioctl_pin_cuda()"]
        UNPIN["pevb_ioctl_unpin_cuda()"]
        H2C_DMA["pevb_ioctl_h2c_dma()"]
        C2H_DMA["pevb_ioctl_c2h_dma()"]
        H2C2H_DMA["pevb_ioctl_h2c2h_dma()"]
        INFO["pevb_ioctl_card_info()"]
    end
    
    subgraph MemMgmt["Memory Management"]
        CUDA_GET["pevb_get_userbuf_cuda()"]
        PAGES_GET["pevb_get_userbuf_pages()"]
        CUDA_PUT["pevb_put_userbuf_cuda()"]
        PAGES_PUT["pevb_put_userbuf_pages()"]
    end
    
    subgraph DMAOps["DMA Operations"]
        DMA_H2C_MULTI["pevb_dma_h2c_multi()"]
        DMA_C2H_MULTI["pevb_dma_c2h_multi()"]
        DMA_H2C2H_MULTI["pevb_dma_h2c2h_multi()"]
        DMA_H2C_SINGLE["pevb_dma_h2c_single()"]
        DMA_C2H_SINGLE["pevb_dma_c2h_single()"]
        DMA_CORE["pevb_dma()"]
    end
    
    subgraph HWInterface["Hardware Interface"]
        WRITEL["pevb_writel()"]
        READL["pevb_readl()"]
        IRQ["pevb_irq_handler()"]
    end
    
    subgraph PCIDriver["PCI Driver pevb_driver"]
        PROBE["pevb_probe()"]
        REMOVE["pevb_remove()"]
    end
    
    subgraph NVP2P["NVIDIA P2P API"]
        GET_PAGES["nvidia_p2p_get_pages()"]
        PUT_PAGES["nvidia_p2p_put_pages()"]
        DMA_MAP["nvidia_p2p_dma_map_pages()"]
        DMA_UNMAP["nvidia_p2p_dma_unmap_pages()"]
    end
    
    IOCTL --> LED
    IOCTL --> PIN
    IOCTL --> UNPIN
    IOCTL --> H2C_DMA
    IOCTL --> C2H_DMA
    IOCTL --> H2C2H_DMA
    IOCTL --> INFO
    
    PIN --> GET_PAGES
    UNPIN --> PUT_PAGES
    
    H2C_DMA --> CUDA_GET
    H2C_DMA --> PAGES_GET
    H2C_DMA --> DMA_H2C_MULTI
    
    C2H_DMA --> CUDA_GET
    C2H_DMA --> PAGES_GET
    C2H_DMA --> DMA_C2H_MULTI
    
    H2C2H_DMA --> CUDA_GET
    H2C2H_DMA --> PAGES_GET
    H2C2H_DMA --> DMA_H2C2H_MULTI
    
    CUDA_GET --> DMA_MAP
    CUDA_PUT --> DMA_UNMAP
    
    DMA_H2C_MULTI --> DMA_H2C_SINGLE
    DMA_C2H_MULTI --> DMA_C2H_SINGLE
    DMA_H2C2H_MULTI --> DMA_H2C_SINGLE
    DMA_H2C2H_MULTI --> DMA_C2H_SINGLE
    
    DMA_H2C_SINGLE --> DMA_CORE
    DMA_C2H_SINGLE --> DMA_CORE
    
    DMA_CORE --> WRITEL
    DMA_CORE --> READL
    DMA_CORE --> IRQ
    
    PROBE -->|"creates"| OPEN
```

The kernel module `picoevb-rdma.ko` is implemented as a PCI driver registered via `pevb_driver`. Upon device probe, it creates a character device at `/dev/picoevb` and sets up the `pevb_fops` file operations structure. The module handles IOCTL commands to pin CUDA memory (via `nvidia_p2p_get_pages()`), map it for DMA (via `nvidia_p2p_dma_map_pages()`), and execute DMA transfers using Xilinx DMA engine registers.

**Sources:** [kernel-module/picoevb-rdma.c:137-1312](), [kernel-module/picoevb-rdma.c:1131-1136](), [kernel-module/picoevb-rdma.c:1273-1279]()

## Supported Hardware

### FPGA Boards

| Board | Form Factor | FPGA | RAM Size | Programming | Vivado Version |
|-------|-------------|------|----------|-------------|----------------|
| **PicoEVB** | M.2 (requires adapter for Jetson/PC) | Xilinx Artix-7 | 64 KB | USB via xvcd | 2018.3 |
| **HTG-K800** | PCIe x16 card | Xilinx XCKU-60 Kintex UltraScale | 2 GB | JTAG via Xilinx Platform Cable | 2018.1 |

### Host Platforms

| Platform | Architecture | GPU Type | Memory Allocation | Build Script |
|----------|--------------|----------|-------------------|--------------|
| **Jetson AGX Xavier** | ARM64 | Integrated GPU (iGPU) | `cudaHostAlloc()` - unified memory | `build-for-jetson-drive-igpu-native.sh` |
| **Drive AGX Xavier** | ARM64 | Integrated GPU (iGPU) | `cudaHostAlloc()` - unified memory | `build-for-jetson-drive-igpu-native.sh` |
| **x86 Linux PC** | x86_64 | Discrete GPU (dGPU) - Quadro/Tesla | `cudaMalloc()` - device memory | `build-for-pc-native.sh` |

The key architectural difference between platforms is the GPU memory model:
- **Integrated GPUs (iGPU):** Use unified memory accessible by both CPU and GPU; applications use `cudaHostAlloc()` to allocate pinned host memory
- **Discrete GPUs (dGPU):** Use separate device memory; applications use `cudaMalloc()` to allocate GPU memory, controlled by `NV_BUILD_DGPU` compile flag

**Sources:** [README.md:22-92](), [kernel-module/picoevb-rdma.c:42-49](), [kernel-module/picoevb-rdma.c:1248-1256]()

## Client Application Suite

The system includes several user-space applications for testing and benchmarking:

```mermaid
graph TB
    subgraph FunctionalTests["Functional Tests"]
        RDMA_CUDA["rdma-cuda<br/>Tests CUDA memory transfers<br/>H2C2H pattern with validation"]
        RDMA_MALLOC["rdma-malloc<br/>Tests host memory transfers<br/>H2C2H pattern with validation"]
    end
    
    subgraph PerfTests["Performance Tests"]
        CUDA_H2C["rdma-cuda-h2c-perf<br/>Measures H2C bandwidth<br/>CUDA memory"]
        CUDA_C2H["rdma-cuda-c2h-perf<br/>Measures C2H bandwidth<br/>CUDA memory"]
        MALLOC_H2C["rdma-malloc-h2c-perf<br/>Measures H2C bandwidth<br/>Host memory"]
        MALLOC_C2H["rdma-malloc-c2h-perf<br/>Measures C2H bandwidth<br/>Host memory"]
    end
    
    subgraph Utils["Utilities"]
        SET_LEDS["set-leds<br/>Controls FPGA GPIOs<br/>Hardware validation"]
    end
    
    subgraph SharedInterface["Common Interface"]
        IOCTL_H["picoevb-rdma-ioctl.h<br/>Defines data structures:<br/>picoevb_rdma_pin_cuda<br/>picoevb_rdma_h2c_dma<br/>picoevb_rdma_c2h_dma<br/>picoevb_rdma_h2c2h_dma"]
    end
    
    RDMA_CUDA --> IOCTL_H
    RDMA_MALLOC --> IOCTL_H
    CUDA_H2C --> IOCTL_H
    CUDA_C2H --> IOCTL_H
    MALLOC_H2C --> IOCTL_H
    MALLOC_C2H --> IOCTL_H
    SET_LEDS --> IOCTL_H
```

**Application Descriptions:**

- **rdma-cuda / rdma-malloc:** Functional tests that perform H2C2H transfers to validate data integrity. They fill source memory with a pattern, execute the transfer, and verify the destination matches.

- **rdma-cuda-*-perf / rdma-malloc-*-perf:** Performance benchmarks that measure unidirectional H2C or C2H bandwidth. They report transfer time and throughput in MB/s.

- **set-leds:** Hardware control utility that sets GPIO values controlling LEDs on the PicoEVB board for basic hardware validation.

All applications communicate with the kernel module through `ioctl()` calls on `/dev/picoevb`, using data structures defined in `picoevb-rdma-ioctl.h`.

**Sources:** [README.md:325-383](), [client-applications/]()

## Memory Management Model

The kernel module handles two distinct memory types through a unified interface (`pevb_userbuf`):

```mermaid
graph TB
    subgraph UserMem["User Space Memory"]
        MALLOC_BUF["malloc() buffer<br/>Regular heap memory"]
        CUDA_BUF["CUDA buffer<br/>cudaHostAlloc() or cudaMalloc()"]
    end
    
    subgraph KernelPin["Kernel Memory Pinning"]
        GET_USER["get_user_pages()<br/>Pin regular pages"]
        DMA_MAP_SG["dma_map_sg()<br/>Create IOMMU mappings"]
        NV_GET["nvidia_p2p_get_pages()<br/>Pin GPU pages"]
        NV_DMA_MAP["nvidia_p2p_dma_map_pages()<br/>Create P2P mappings"]
    end
    
    subgraph Struct["struct pevb_userbuf"]
        UBUF_DMAS["dmas array<br/>DMA address/length pairs"]
        UBUF_PAGES["priv.pages<br/>struct page** pages<br/>struct sg_table* sgt"]
        UBUF_CUDA["priv.cuda<br/>pevb_cuda_surface* cusurf<br/>nvidia_p2p_dma_mapping* map"]
    end
    
    MALLOC_BUF --> GET_USER
    GET_USER --> DMA_MAP_SG
    DMA_MAP_SG --> UBUF_PAGES
    
    CUDA_BUF --> NV_GET
    NV_GET --> NV_DMA_MAP
    NV_DMA_MAP --> UBUF_CUDA
    
    UBUF_PAGES --> UBUF_DMAS
    UBUF_CUDA --> UBUF_DMAS
```

**Memory Handling Functions:**

| Memory Type | Pin Function | Unpin Function | Key Operations |
|-------------|--------------|----------------|----------------|
| **Regular (malloc)** | `pevb_get_userbuf_pages()` | `pevb_put_userbuf_pages()` | `get_user_pages()`, `sg_alloc_table_from_pages()`, `dma_map_sg()` |
| **CUDA (GPU)** | `pevb_get_userbuf_cuda()` | `pevb_put_userbuf_cuda()` | `nvidia_p2p_get_pages()`, `nvidia_p2p_dma_map_pages()` |

Both paths populate a `pevb_userbuf` structure containing an array of DMA address/length pairs (`pevb_userbuf_dma`), which are then used to construct Xilinx DMA descriptors (`xlnx_dma_desc`). The module handles transfer chunking when memory is not contiguous or when FPGA RAM size limits apply.

**Sources:** [kernel-module/picoevb-rdma.c:90-117](), [kernel-module/picoevb-rdma.c:356-527](), [kernel-module/picoevb-rdma.h]()

## Next Steps

- **To set up the system:** See [Getting Started](#2) for hardware setup, software installation, and quick start instructions
- **To understand DMA operations:** See [System Architecture](#3) for RDMA fundamentals and data flow details
- **To develop with the kernel module:** See [Kernel Module](#4) for API reference and implementation details
- **To build and run tests:** See [Client Applications](#5) and [Building and Deployment](#7)
- **To modify FPGA bitstreams:** See [FPGA Development](#6) for Vivado project structure and synthesis procedures

**Sources:** [README.md:1-384]()

---

