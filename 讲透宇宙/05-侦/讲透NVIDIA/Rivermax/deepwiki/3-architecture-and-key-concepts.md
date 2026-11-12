<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/Rivermax · page 3 Architecture and Key Concepts · fetched 2026-10-26 -->

# Architecture and Key Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [resources/Rivermax_SDK.jpg](resources/Rivermax_SDK.jpg)

</details>



This page provides a technical overview of the NVIDIA Rivermax system architecture. Rivermax is designed as a layered system that bridges high-performance hardware capabilities—specifically NVIDIA ConnectX Network Interface Cards (NICs)—with sophisticated software abstractions for professional media and data streaming.

The architecture focuses on three primary pillars:
1.  **Hardware Acceleration**: Leveraging NIC offloads for timing and packet pacing.
2.  **Kernel Bypass**: Moving data directly between the application and the hardware to minimize latency and CPU overhead.
3.  **Standard Compliance**: Implementing professional media-over-IP standards like SMPTE ST 2110 and ST 2022-7.

### System Hierarchy

The following diagram illustrates the relationship between the application layer, the Rivermax SDK, and the underlying hardware components.

**Rivermax Layered Architecture**
```mermaid
graph TD
    subgraph "Application Space"
        [Application] --> [Rivermax_Dev_Kit]
        [Application] --> [Rivermax_API]
    end

    subgraph "Rivermax SDK"
        [Rivermax_API] --> [Data_Path_Manager]
        [Data_Path_Manager] --> [Memory_Management]
        [Data_Path_Manager] --> [Packet_Pacing_Engine]
    end

    subgraph "Kernel Space"
        [Rivermax_Driver]
    end

    subgraph "Hardware Layer"
        [Memory_Management] -- "GPUDirect / RDMA" --> [ConnectX_NIC]
        [Packet_Pacing_Engine] -- "Hardware Offload" --> [ConnectX_NIC]
        [ConnectX_NIC] --> [Physical_Network]
    end

    style [Rivermax_API] stroke-width:2px
    style [ConnectX_NIC] stroke-width:2px
```
**Sources:** [README.md:13-17](), [README.md:24-28](), [resources/Rivermax_SDK.jpg:1-5]()

---

### SDK Architecture and Data Path

The Rivermax SDK architecture is optimized for high-throughput, jitter-sensitive media traffic. At its core, it utilizes a kernel-bypass mechanism that allows the application to interact directly with the NIC's transmit and receive queues. This bypass is critical for achieving the deterministic performance required by broadcast standards.

Key components of the data path include:
*   **Hardware Packet Pacing**: Offloading the timing of RTP packet transmission to the ConnectX NIC to ensure compliance with SMPTE ST 2110-21 traffic shaping.
*   **Memory Management**: Support for pinned host memory and GPUDirect, enabling direct data transfer between the NIC and GPU memory without intermediate CPU copies.
*   **Flow Control**: Efficient handling of media "essences" (video, audio, and metadata) as discrete data streams.

For details, see [SDK Architecture and Data Path](#3.1).

**Sources:** [README.md:13-15](), [resources/Rivermax_SDK.jpg:1-10]()

---

### Media Streaming Standards

Rivermax is built to satisfy the rigorous requirements of the professional broadcast industry. The architecture natively supports the SMPTE ST 2110 suite, which defines the transport of uncompressed digital media over IP networks.

The system architecture incorporates:
*   **SMPTE ST 2110**: Separation of video (-20), audio (-30), and ancillary data (-40) into individual streams.
*   **SMPTE ST 2022-7**: Seamless Protection Switching, providing network redundancy by sending identical streams over two different network paths.
*   **PTP (IEEE 1588)**: Precision Time Protocol support to ensure all devices on the network are synchronized to a common clock, essential for lip-sync and multi-camera alignment.

For details, see [Media Streaming Standards](#3.2).

**Sources:** [README.md:13-16](), [README.md:34-35]()

---

### Component Interaction Map

This diagram bridges the conceptual architecture with the repository structure provided in this hub.

**Code Entity and Repository Mapping**
```mermaid
graph LR
    subgraph "rivermax-dev-kit Repository"
        [rtx_io_node] -- "High-level Abstraction" --> [rmx_api]
    end

    subgraph "rivermax-examples Repository"
        [simple_publisher_demo] -- "Direct Call" --> [rmx_api]
        [simple_receiver_demo] -- "Direct Call" --> [rmx_api]
    end

    subgraph "rivermax-utils Repository"
        [tuning_scripts] -- "Optimizes" --> [OS_Kernel]
        [validation_tools] -- "Checks" --> [ConnectX_NIC]
    end

    subgraph "Rivermax SDK (Binary)"
        [rmx_api]
    end
```
**Sources:** [README.md:24-28](), [README.md:40-41]()

---

