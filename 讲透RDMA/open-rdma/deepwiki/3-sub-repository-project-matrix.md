<!-- source: DeepWiki mcp.deepwiki.com · repo open-rdma/open-rdma · page 3 Sub-Repository Project Matrix · fetched 2026-11-11 -->

# Sub-Repository Project Matrix

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README_CN.md](README_CN.md)

</details>



The Open-RDMA project is organized as a modular ecosystem comprising six distinct sub-repositories. This matrix ensures that hardware design, software drivers, and verification tooling can evolve independently while maintaining a unified full-stack architecture for AI-optimized RDMA networking [README.md:133-135]().

## Core Repositories

The core of the project consists of the hardware RTL and the software driver stack. These repositories define the primary data path and control plane of the RDMA implementation.

| Repository | Primary Language | Role |
| :--- | :--- | :--- |
| **open-rdma-rtl** | Bluespec SystemVerilog | RoCE v2 Protocol Engine, DMA, and PCIe Interface [README.md:124, 139-143]() |
| **open-rdma-driver** | C (Kernel) / Rust (User) | Kernel-bypass data path, QP/CQ management, and IB subsystem integration [README.md:125-126, 148-152]() |

### [open-rdma-rtl — Hardware RTL Repository](#3.1)
This repository contains the hardware description logic for the RDMA NIC. It implements the RoCE v2 protocol over Ethernet and handles high-speed data movement between the network and host memory.
*   **Target:** FPGA (Altera R-Tile/T-Tile) and ASIC [README.md:13, 91]().
*   **Key Technology:** Bluespec SystemVerilog (BSV) for high-level hardware synthesis [README.md:124]().
*   **For details, see [open-rdma-rtl — Hardware RTL Repository](#3.1).**

### [open-rdma-driver — Driver Repository](#3.2)
The driver repository provides the software interface required to interact with the hardware. It is split into a C-based Linux kernel driver for hardware lifecycle management and a Rust-based user-space driver for high-performance, kernel-bypass operations [README.md:152]().
*   **Key Technology:** C for kernel stability, Rust for memory-safe user-space performance [README.md:125-126]().
*   **For details, see [open-rdma-driver — Driver Repository](#3.2).**

---

## Tooling and Verification Repositories

Open-RDMA relies on a suite of specialized tools to maintain a "beginner-friendly" and "AI-first" development workflow [README.md:96-97, 111-112]().

### [Tooling and Verification Repositories](#3.3)
This group includes environment setup, IDE support, and advanced simulation models:
*   **open-rdma-dev-env:** A Docker-based environment providing pre-installed toolchains (Bluespec, Rust, Python, Cocotb) to eliminate setup friction [README.md:157-161, 212-222]().
*   **bluespec-lsp:** A Language Server Protocol implementation for BSV to improve the developer experience in modern IDEs [README.md:168-172]().
*   **UCAgent (Fork):** An AI-agent-driven verification framework that automates test bench generation using LLMs [README.md:177-181]().
*   **cocotbext-pcie (Fork):** PCIe behavioral models used in simulation, specifically extended by the project to support Altera R-Tile [README.md:185-189]().

**For details, see [Tooling and Verification Repositories](#3.3).**

---

## System Integration Diagram

The following diagram illustrates how these sub-repositories map to the system layers and their respective code entities.

### Repository-to-Layer Mapping
```mermaid
graph TD
    subgraph "User Space"
        [User_App] --> [open-rdma-driver/user-space]
        [open-rdma-driver/user-space] -- "Rust / IB Verbs" --> [RDMA_Hardware]
    end

    subgraph "Kernel Space"
        [open-rdma-driver/kernel-space] -- "C / PCIe Ops" --> [RDMA_Hardware]
    end

    subgraph "Hardware (open-rdma-rtl)"
        [RDMA_Hardware] -- "BSV / RoCE v2" --> [Network]
    end

    subgraph "Verification & Tooling"
        [UCAgent] -. "Generates" .-> [Cocotb_Tests]
        [cocotbext-pcie] -. "Simulates" .-> [PCIe_R-Tile]
        [open-rdma-dev-env] -- "Packages" --> [All_Tools]
    end
```
**Sources:** [README.md:76-78, 120-130, 133-193]()

### Code Entity Interaction
This diagram bridges the conceptual sub-repositories to specific implementation languages and roles defined in the codebase.

```mermaid
graph LR
    subgraph "open-rdma-driver"
        [kernel_c_driver] -- "Interrupts/MMIO" --> [Hardware_Registers]
        [user_rust_driver] -- "Doorbell/DMA" --> [Hardware_Data_Path]
    end

    subgraph "open-rdma-rtl"
        [BSV_RoCE_Engine] -- "AXI/PCIe" --> [Hardware_Registers]
        [BSV_RoCE_Engine] -- "MAC/PHY" --> [Ethernet]
    end

    subgraph "Verification"
        [Python_Cocotb] -- "Simulates" --> [BSV_RoCE_Engine]
        [AI_UCAgent] -- "Orchestrates" --> [Python_Cocotb]
    end
```
**Sources:** [README.md:83, 124-128, 177-189]()

---

## Project Matrix Summary

| Sub-Repository | Role in Ecosystem | Primary Technology |
| :--- | :--- | :--- |
| `open-rdma-rtl` | Hardware logic and protocol implementation | Bluespec SystemVerilog |
| `open-rdma-driver` | Software interface (Kernel & User space) | C, Rust |
| `open-rdma-dev-env` | Containerized development environment | Docker, Shell |
| `bluespec-lsp` | IDE support for hardware development | Rust (LSP) |
| `UCAgent` | AI-assisted RTL verification | Python, LLM Agents |
| `cocotbext-pcie` | PCIe simulation infrastructure | Python, Cocotb |

**Sources:** [README.md:133-193]()

---

