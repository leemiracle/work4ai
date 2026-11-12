<!-- source: DeepWiki mcp.deepwiki.com · repo openucx/ucx · page 1 Overview · fetched 2026-11-11 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/tools/info/tl_info.c](src/tools/info/tl_info.c)
- [src/ucp/api/ucp.h](src/ucp/api/ucp.h)
- [src/ucp/api/ucp_compat.h](src/ucp/api/ucp_compat.h)
- [src/ucp/api/ucp_def.h](src/ucp/api/ucp_def.h)
- [src/ucp/core/ucp_context.c](src/ucp/core/ucp_context.c)
- [src/ucp/core/ucp_context.h](src/ucp/core/ucp_context.h)
- [src/ucp/core/ucp_ep.c](src/ucp/core/ucp_ep.c)
- [src/ucp/core/ucp_ep.h](src/ucp/core/ucp_ep.h)
- [src/ucp/core/ucp_ep.inl](src/ucp/core/ucp_ep.inl)
- [src/ucp/core/ucp_worker.c](src/ucp/core/ucp_worker.c)
- [src/ucp/core/ucp_worker.h](src/ucp/core/ucp_worker.h)
- [src/ucp/wireup/select.c](src/ucp/wireup/select.c)
- [src/ucp/wireup/wireup.c](src/ucp/wireup/wireup.c)
- [src/ucp/wireup/wireup.h](src/ucp/wireup/wireup.h)
- [src/ucp/wireup/wireup_cm.c](src/ucp/wireup/wireup_cm.c)
- [src/ucp/wireup/wireup_cm.h](src/ucp/wireup/wireup_cm.h)
- [src/ucp/wireup/wireup_ep.c](src/ucp/wireup/wireup_ep.c)
- [src/ucp/wireup/wireup_ep.h](src/ucp/wireup/wireup_ep.h)
- [src/uct/api/tl.h](src/uct/api/tl.h)
- [src/uct/api/uct.h](src/uct/api/uct.h)
- [src/uct/api/uct_def.h](src/uct/api/uct_def.h)
- [src/uct/api/v2/uct_v2.h](src/uct/api/v2/uct_v2.h)
- [src/uct/base/uct_iface.c](src/uct/base/uct_iface.c)
- [src/uct/base/uct_iface.h](src/uct/base/uct_iface.h)
- [src/uct/cuda/gdr_copy/gdr_copy_iface.c](src/uct/cuda/gdr_copy/gdr_copy_iface.c)
- [test/gtest/ucp/test_ucp_ep.cc](test/gtest/ucp/test_ucp_ep.cc)

</details>



UCX (Unified Communication X) is a communication framework designed for high-performance computing (HPC) and data-intensive applications. It provides a layered architecture that abstracts diverse network hardware through a unified API, enabling applications to achieve optimal performance across different interconnect technologies without modification.

This page introduces UCX's fundamental architecture, design principles, and core abstractions. For detailed information about specific layers, see: UCP layer ([2](#2)), UCT layer ([3](#3)), Memory Management ([4](#4)), and Testing ([5](#5)).

## Three-Layer Architecture

UCX employs a three-layer design that separates protocol semantics from transport mechanisms:

```mermaid
graph TB
    subgraph APP["Application Layer"]
        USER["User Application<br/>(MPI, SHMEM, PGAS)"]
    end
    
    subgraph UCP["UCP Layer: Unified Communication Protocol"]
        UCP_API["ucp_context_h<br/>ucp_worker_h<br/>ucp_ep_h"]
        PROTOCOLS["Tag Matching<br/>RMA Operations<br/>Active Messages<br/>Streams"]
    end
    
    subgraph UCT["UCT Layer: Unified Communication Transport"]
        UCT_API["uct_md_h<br/>uct_iface_h<br/>uct_ep_h"]
        ABSTRACT["Transport Abstraction"]
    end
    
    subgraph TRANSPORT["Transport Implementations"]
        IB["InfiniBand<br/>RC, UD, DC"]
        TCP["TCP Sockets"]
        SHM["Shared Memory"]
    end
    
    USER --> UCP_API
    UCP_API --> PROTOCOLS
    PROTOCOLS --> UCT_API
    UCT_API --> ABSTRACT
    ABSTRACT --> IB
    ABSTRACT --> TCP
    ABSTRACT --> SHM
    
    style UCP fill:#f9f9f9,stroke:#333,stroke-width:2px
    style UCT fill:#f9f9f9,stroke:#333,stroke-width:2px
    style TRANSPORT fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Sources:** [src/ucp/api/ucp.h:1-100](), [src/uct/api/uct.h:1-100]()

### UCP Layer (Unified Communication Protocol)

UCP provides high-level communication semantics that applications use directly. It implements protocol logic for various communication patterns.

| Feature | API Function Prefix | Description |
|---------|-------------------|-------------|
| Tagged Messages | `ucp_tag_*` | Message matching by software tags |
| RMA | `ucp_put_*`, `ucp_get_*` | Remote Memory Access operations |
| Active Messages | `ucp_am_*` | User-defined message handlers |
| Streams | `ucp_stream_*` | Ordered, connection-oriented data transfer |
| Atomics | `ucp_atomic_*` | Atomic memory operations |

The UCP layer manages:
- **Contexts** (`ucp_context_h`): Global configuration and resource management
- **Workers** (`ucp_worker_h`): Progress engine and event handling per thread
- **Endpoints** (`ucp_ep_h`): Point-to-point connections to remote peers
- **Requests** (`ucp_request_t`): Asynchronous operation tracking

**Sources:** [src/ucp/api/ucp.h:25-100](), [src/ucp/core/ucp_context.h:1-50](), [src/ucp/core/ucp_worker.h:1-50](), [src/ucp/core/ucp_ep.h:1-100]()

### UCT Layer (Unified Communication Transport)

UCT provides a uniform interface over diverse network hardware. It exposes low-level transport capabilities while hiding hardware-specific details.

```mermaid
graph LR
    subgraph UCT_ABSTRACTIONS["UCT Abstractions"]
        MD["uct_md_h<br/>Memory Domain"]
        IFACE["uct_iface_h<br/>Interface"]
        EP["uct_ep_h<br/>Endpoint"]
    end
    
    subgraph OPERATIONS["UCT Operations"]
        AM["Active Messages<br/>uct_ep_am_short/bcopy/zcopy"]
        PUT["Put Operations<br/>uct_ep_put_short/bcopy/zcopy"]
        GET["Get Operations<br/>uct_ep_get_bcopy/zcopy"]
        ATOMIC["Atomic Operations<br/>uct_ep_atomic*"]
    end
    
    MD --> IFACE
    IFACE --> EP
    EP --> AM
    EP --> PUT
    EP --> GET
    EP --> ATOMIC
```

**UCT Components:**

- **Memory Domain** (`uct_md_h`): Manages memory registration and protection
- **Interface** (`uct_iface_h`): Represents a communication channel on a device
- **Endpoint** (`uct_ep_h`): Connection to a specific remote interface

UCT operations come in three flavors:
- **Short**: Inline data in protocol headers (lowest latency)
- **Bcopy**: Buffer copy to pre-registered memory (medium messages)
- **Zcopy**: Zero-copy using registered memory (large messages)

**Sources:** [src/uct/api/uct.h:50-300](), [src/uct/api/uct_def.h:1-100](), [src/uct/base/uct_iface.h:1-100]()

### Transport Layer

The transport layer implements UCT interfaces for specific hardware:

| Transport | Type | Description | Capabilities |
|-----------|------|-------------|--------------|
| RC (Reliable Connection) | InfiniBand | Hardware-reliable, connection-oriented | High bandwidth, hardware reliability |
| UD (Unreliable Datagram) | InfiniBand | Software reliability over UD QPs | Scalability, connectionless |
| DC (Dynamic Connection) | InfiniBand | Scalable connections via DCI pool | Scalable connections, hardware reliability |
| TCP | Network | Socket-based communication | Universal connectivity |
| SHM | Memory | Intra-node shared memory | Lowest latency for same-node |

Each transport is implemented as a separate component that registers with UCT during initialization.

**Sources:** [src/uct/api/uct.h:300-350](), [src/ucp/wireup/select.c:1-100]()

## Core Abstractions and Workflow

### Initialization and Resource Management

```mermaid
graph TD
    START["Application Start"] --> CONFIG["ucp_config_read"]
    CONFIG --> INIT["ucp_init<br/>(ucp_params_t)"]
    INIT --> CONTEXT["ucp_context_h<br/>created"]
    
    CONTEXT --> WORKER["ucp_worker_create<br/>(ucp_worker_params_t)"]
    WORKER --> WORKER_H["ucp_worker_h<br/>created"]
    
    WORKER_H --> EP_CREATE["ucp_ep_create<br/>(ucp_ep_params_t)"]
    EP_CREATE --> EP_H["ucp_ep_h<br/>ready for communication"]
    
    EP_H --> COMM["Communication Operations<br/>ucp_tag_send_nbx<br/>ucp_put_nbx<br/>etc."]
    
    COMM --> PROGRESS["ucp_worker_progress<br/>(drive operations)"]
    
    style CONTEXT fill:#f9f9f9,stroke:#333,stroke-width:2px
    style WORKER_H fill:#f9f9f9,stroke:#333,stroke-width:2px
    style EP_H fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Initialization Sequence:**

1. **Configuration**: `ucp_config_read()` loads settings from environment variables and configuration files [src/ucp/api/ucp.h:600-650]()
2. **Context Creation**: `ucp_init()` creates a `ucp_context_h` with specified features (TAG, RMA, AMO, etc.) [src/ucp/core/ucp_context.c:1-100]()
3. **Worker Creation**: `ucp_worker_create()` establishes a per-thread progress engine [src/ucp/core/ucp_worker.c:1-100]()
4. **Endpoint Creation**: `ucp_ep_create()` connects to a remote worker [src/ucp/core/ucp_ep.c:1-100]()

**Sources:** [src/ucp/api/ucp.h:1-700](), [src/ucp/core/ucp_context.c:1-200](), [src/ucp/core/ucp_worker.c:1-200](), [src/ucp/core/ucp_ep.c:1-200]()

### Connection Establishment (Wireup)

UCX uses a sophisticated wireup protocol to select optimal transports and establish connections:

```mermaid
graph TB
    subgraph CLIENT["Client Side"]
        C_ADDR["Pack Worker Address<br/>ucp_address_pack"]
        C_CREATE["ucp_ep_create<br/>remote address"]
        C_SELECT["Transport Selection<br/>ucp_wireup_select_lanes"]
        C_WIREUP["Wireup Protocol<br/>CONN_REQ message"]
    end
    
    subgraph SERVER["Server Side"]
        S_RECV["Receive CONN_REQ"]
        S_SELECT["Transport Selection<br/>match client capabilities"]
        S_REPLY["Send CONN_REP<br/>with selected transports"]
    end
    
    subgraph FINALIZE["Connection Ready"]
        ACK["Client sends CONN_ACK"]
        CONNECTED["Both endpoints<br/>UCP_EP_FLAG_LOCAL_CONNECTED<br/>UCP_EP_FLAG_REMOTE_CONNECTED"]
    end
    
    C_ADDR --> C_CREATE
    C_CREATE --> C_SELECT
    C_SELECT --> C_WIREUP
    C_WIREUP --> S_RECV
    S_RECV --> S_SELECT
    S_SELECT --> S_REPLY
    S_REPLY --> ACK
    ACK --> CONNECTED
```

The wireup process:
1. Client packs its worker address containing available transports [src/ucp/wireup/address.c:1-100]()
2. Transport selection algorithm chooses optimal lanes based on bandwidth, latency, and capabilities [src/ucp/wireup/select.c:1-500]()
3. Three-way handshake (REQ/REP/ACK) exchanges connection information [src/ucp/wireup/wireup.c:1-300]()
4. Temporary wireup endpoints proxy operations until connection completes [src/ucp/wireup/wireup_ep.c:1-200]()

**Sources:** [src/ucp/wireup/wireup.c:1-300](), [src/ucp/wireup/select.c:1-500](), [src/ucp/wireup/wireup_ep.c:1-200](), [src/ucp/wireup/address.c:1-200]()

## Communication Models

### Multi-Lane Communication

UCX uses multiple parallel lanes for different operation types to maximize performance:

```mermaid
graph LR
    subgraph UCP_EP["ucp_ep_h"]
        CONFIG["ucp_ep_config_t"]
    end
    
    subgraph LANES["Lane Configuration"]
        AM_LANE["AM Lane<br/>key.am_lane"]
        TAG_LANE["Tag Lane<br/>key.tag_lane"]
        RMA_LANES["RMA Lanes<br/>key.rma_lanes[n]"]
        WIREUP_LANE["Wireup Lane<br/>key.wireup_msg_lane"]
        CM_LANE["CM Lane<br/>key.cm_lane"]
    end
    
    subgraph UCT_EPS["UCT Endpoints"]
        UCT_EP0["uct_ep_h[0]"]
        UCT_EP1["uct_ep_h[1]"]
        UCT_EP2["uct_ep_h[2]"]
    end
    
    CONFIG --> AM_LANE
    CONFIG --> TAG_LANE
    CONFIG --> RMA_LANES
    CONFIG --> WIREUP_LANE
    CONFIG --> CM_LANE
    
    AM_LANE --> UCT_EP0
    TAG_LANE --> UCT_EP1
    RMA_LANES --> UCT_EP2
    WIREUP_LANE --> UCT_EP0
    CM_LANE --> UCT_EP1
```

Each endpoint (`ucp_ep_h`) maintains:
- **Lane array**: Up to `UCP_MAX_LANES` (16) UCT endpoints [src/ucp/core/ucp_ep.h:200-250]()
- **Lane types**: Specialized for different operations (AM, RMA, TAG, wireup, CM, keepalive) [src/ucp/proto/lane_type.h:1-100]()
- **Multi-rail**: Multiple lanes can use different devices in parallel for bandwidth aggregation [src/ucp/wireup/select.c:500-700]()

**Sources:** [src/ucp/core/ucp_ep.h:200-250](), [src/ucp/wireup/select.c:500-1000]()

### Request Management and Asynchronous Operations

All communication operations in UCP are non-blocking and return a request handle:

| Return Value | Meaning | Action |
|--------------|---------|--------|
| `NULL` | Completed immediately | No further action needed |
| `UCS_PTR_IS_PTR(req)` | In progress | Test/wait for completion |
| `UCS_PTR_IS_ERR(req)` | Failed | Extract error with `UCS_PTR_STATUS()` |

Requests are allocated from memory pools and tracked through completion:
- **Request structure**: `ucp_request_t` contains operation state [src/ucp/core/ucp_request.h:1-100]()
- **Protocol selection**: Chooses short/bcopy/zcopy/rendezvous based on message size [src/ucp/core/ucp_ep.c:600-800]()
- **Completion**: Via callbacks, polling (`ucp_request_test`), or waiting (`ucp_request_wait`) [src/ucp/api/ucp.h:1500-1600]()

**Sources:** [src/ucp/core/ucp_request.h:1-200](), [src/ucp/api/ucp.h:1500-1700]()

## Design Principles

### Hardware Abstraction

UCX abstracts hardware diversity through:
- **Runtime selection**: Transport and protocol selection at runtime based on available hardware
- **Capability queries**: UCT exposes fine-grained capabilities (`UCT_IFACE_FLAG_*`) [src/uct/api/uct.h:360-450]()
- **Zero-copy**: Direct hardware access for registered memory avoids copies
- **Multi-path**: Automatic use of multiple network paths when available

**Sources:** [src/uct/api/uct.h:300-500](), [src/ucp/wireup/select.c:1-200]()

### Performance Optimization

```mermaid
graph TD
    subgraph MESSAGE_SIZE["Message Size"]
        SMALL["Small<br/>(< bcopy_thresh)"]
        MEDIUM["Medium<br/>(< zcopy_thresh)"]
        LARGE["Large<br/>(< rndv_thresh)"]
        HUGE["Huge<br/>(>= rndv_thresh)"]
    end
    
    subgraph PROTOCOL["Protocol Selection"]
        SHORT["Short Protocol<br/>Inline in header"]
        BCOPY["Bcopy Protocol<br/>Copy to bounce buffer"]
        ZCOPY["Zcopy Protocol<br/>Zero-copy registered memory"]
        RNDV["Rendezvous Protocol<br/>RTS/RTR/DATA/ATP"]
    end
    
    SMALL --> SHORT
    MEDIUM --> BCOPY
    LARGE --> ZCOPY
    HUGE --> RNDV
    
    SHORT --> LOW_LAT["Lowest Latency"]
    BCOPY --> MED_LAT["Medium Latency"]
    ZCOPY --> HIGH_BW["High Bandwidth"]
    RNDV --> MAX_BW["Maximum Bandwidth<br/>Multi-lane"]
```

UCX optimizes performance through:
- **Protocol thresholds**: Configurable via `UCX_*_THRESH` environment variables [src/ucp/core/ucp_context.c:150-400]()
- **Memory registration caching**: Reduces registration overhead [src/ucp/core/ucp_rkey.c:1-200]()
- **Progress engine**: Efficient polling with adaptive progress [src/ucp/core/ucp_worker.c:500-800]()
- **Multi-rail**: Parallel data transfer across multiple lanes [src/ucp/wireup/select.c:800-1200]()

**Sources:** [src/ucp/core/ucp_context.c:150-400](), [src/ucp/wireup/select.c:800-1500]()

## Use Cases

UCX serves as the foundation for:

- **MPI Implementations**: OpenMPI, MPICH use UCX for point-to-point and collective operations
- **PGAS Languages**: UPC, Chapel, OpenSHMEM leverage UCX for remote memory access
- **Deep Learning**: TensorFlow, PyTorch use UCX for distributed training communication
- **Storage Systems**: Parallel file systems use UCX for high-performance data movement
- **HPC Applications**: Direct use of UCX API for custom communication patterns

The layered design allows each use case to operate at the appropriate abstraction level:
- MPI/PGAS frameworks use UCP for high-level semantics
- Performance-critical custom protocols may use UCT directly
- Transport developers implement UCT interfaces for new hardware

**Sources:** [src/ucp/api/ucp.h:25-100](), [src/uct/api/uct.h:1-100]()

## Key Files and Entry Points

| Component | Key Files | Entry Points |
|-----------|-----------|--------------|
| UCP API | [src/ucp/api/ucp.h]() | `ucp_init`, `ucp_worker_create`, `ucp_ep_create` |
| UCP Core | [src/ucp/core/ucp_context.c](), [src/ucp/core/ucp_worker.c](), [src/ucp/core/ucp_ep.c]() | Context/worker/endpoint implementation |
| UCT API | [src/uct/api/uct.h]() | `uct_md_open`, `uct_iface_open`, `uct_ep_create` |
| UCT Base | [src/uct/base/uct_iface.c]() | Common UCT infrastructure |
| Wireup | [src/ucp/wireup/wireup.c](), [src/ucp/wireup/select.c]() | Connection establishment and transport selection |
| Transports | `src/uct/{ib,tcp,sm}/` | Transport-specific implementations |

**Sources:** [src/ucp/api/ucp.h:1-100](), [src/uct/api/uct.h:1-100](), [src/ucp/core/](), [src/uct/base/](), [src/ucp/wireup/]()

---

