<!-- source: DeepWiki mcp.deepwiki.com · repo Mellanox/gpu_direct_rdma_access · page 3 Core RDMA Engine · fetched 2026-11-11 -->

# Core RDMA Engine

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [gpu_direct_rdma_access.c](gpu_direct_rdma_access.c)
- [gpu_direct_rdma_access.h](gpu_direct_rdma_access.h)

</details>



## Purpose and Scope

The Core RDMA Engine provides the fundamental RDMA (Remote Direct Memory Access) functionality that enables GPU Direct memory operations using Mellanox Dynamic Connect Queue Pairs. This subsystem abstracts the complexities of InfiniBand/RoCE hardware management, memory registration, and task execution to provide a high-level API for direct memory transfers between distributed systems.

For information about the public API interfaces, see [RDMA Interface Definition](#3.1). For internal implementation details, see [RDMA Implementation Details](#3.2). For memory management abstractions used by this engine, see [Memory Management Subsystem](#4).

## Architecture Overview

The Core RDMA Engine implements a sophisticated architecture centered around Mellanox's Dynamic Connect (DC) transport, which provides scalable one-to-many connectivity without per-connection state overhead.

```mermaid
graph TB
    subgraph "RDMA Device Management"
        rdma_open_device_client["rdma_open_device_client()<br/>DCT QP + SRQ"]
        rdma_open_device_server["rdma_open_device_server()<br/>DCI QP"]
        rdma_reset_device["rdma_reset_device()<br/>Error Recovery"]
        rdma_close_device["rdma_close_device()<br/>Cleanup"]
    end
    
    subgraph "Memory Registration"
        rdma_buffer_reg["rdma_buffer_reg()<br/>MR Creation"]
        rdma_buffer_dereg["rdma_buffer_dereg()<br/>MR Cleanup"]
        rdma_buffer_get_desc_str["rdma_buffer_get_desc_str()<br/>Serialization"]
    end
    
    subgraph "Task Execution Engine"
        rdma_submit_task["rdma_submit_task()<br/>Public Interface"]
        rdma_exec_task["rdma_exec_task()<br/>Internal Execution"]
        rdma_poll_completions["rdma_poll_completions()<br/>Event Processing"]
    end
    
    subgraph "Address Resolution"
        ah_hash["ah_hash<br/>khash_t(kh_ib_ah)"]
        rdma_create_ah_cached["rdma_create_ah_cached()<br/>Cached AH Creation"]
    end
    
    subgraph "Hardware Abstraction"
        struct_rdma_device["struct rdma_device<br/>Device State"]
        mlx5dv_qp_ex["mlx5dv_qp_ex<br/>Hardware Acceleration"]
        ibv_qp_ex["ibv_qp_ex<br/>Extended Queue Pair"]
    end
    
    rdma_submit_task --> rdma_exec_task
    rdma_exec_task --> rdma_create_ah_cached
    rdma_create_ah_cached --> ah_hash
    rdma_exec_task --> mlx5dv_qp_ex
    mlx5dv_qp_ex --> ibv_qp_ex
    rdma_open_device_client --> struct_rdma_device
    rdma_open_device_server --> struct_rdma_device
    rdma_buffer_reg --> struct_rdma_device
```

**Sources:** [gpu_direct_rdma_access.h:90-91](), [gpu_direct_rdma_access.c:526-711](), [gpu_direct_rdma_access.c:714-885]()

## Device Management

The RDMA engine supports two distinct device roles: client (target) and server (initiator), each with different Queue Pair configurations optimized for their respective functions.

### Client Device Initialization

Client devices use Dynamic Connect Target (DCT) Queue Pairs with Shared Receive Queues (SRQ) for scalable reception of RDMA operations:

```mermaid
graph LR
    rdma_open_device_client["rdma_open_device_client()"] --> open_ib_device_by_addr["open_ib_device_by_addr()"]
    open_ib_device_by_addr --> ibv_alloc_pd["ibv_alloc_pd()"]
    ibv_alloc_pd --> ibv_create_cq["ibv_create_cq()"]
    ibv_create_cq --> ibv_create_srq["ibv_create_srq()"]
    ibv_create_srq --> mlx5dv_create_qp["mlx5dv_create_qp()<br/>DCT"]
    mlx5dv_create_qp --> modify_target_qp_to_rtr["modify_target_qp_to_rtr()"]
```

**Sources:** [gpu_direct_rdma_access.c:526-711](), [gpu_direct_rdma_access.c:586-596](), [gpu_direct_rdma_access.c:618-630]()

### Server Device Initialization

Server devices use Dynamic Connect Initiator (DCI) Queue Pairs with extended capabilities for issuing RDMA operations:

```mermaid
graph LR
    rdma_open_device_server["rdma_open_device_server()"] --> open_ib_device_by_addr["open_ib_device_by_addr()"]
    open_ib_device_by_addr --> ibv_alloc_pd["ibv_alloc_pd()"]
    ibv_alloc_pd --> ibv_create_cq["ibv_create_cq()"]
    ibv_create_cq --> mlx5dv_create_qp["mlx5dv_create_qp()<br/>DCI"]
    mlx5dv_create_qp --> ibv_qp_to_qp_ex["ibv_qp_to_qp_ex()"]
    ibv_qp_to_qp_ex --> mlx5dv_qp_ex_from_ibv_qp_ex["mlx5dv_qp_ex_from_ibv_qp_ex()"]
    mlx5dv_qp_ex_from_ibv_qp_ex --> modify_source_qp_rst2rts["modify_source_qp_rst2rts()"]
```

**Sources:** [gpu_direct_rdma_access.c:714-885](), [gpu_direct_rdma_access.c:796-827](), [gpu_direct_rdma_access.c:818-823]()

## Memory Registration Subsystem

The memory registration subsystem provides abstraction over InfiniBand Memory Regions (MRs) and serialization for network communication.

| Function | Purpose | Key Parameters |
|----------|---------|----------------|
| `rdma_buffer_reg()` | Register memory with RDMA device | `rdma_dev`, `addr`, `length` |
| `rdma_buffer_dereg()` | Unregister and cleanup | `rdma_buff` |
| `rdma_buffer_get_desc_str()` | Serialize buffer info | `rdma_buff`, `desc_str`, `desc_length` |

The `struct rdma_buffer` encapsulates both buffer metadata and RDMA-specific information:

```mermaid
graph TB
    subgraph "struct rdma_buffer"
        buf_addr["void *buf_addr<br/>Buffer Address"]
        buf_size["size_t buf_size<br/>Buffer Size"]
        mr["struct ibv_mr *mr<br/>Memory Region"]
        rkey["uint32_t rkey<br/>Remote Key"]
        rdma_dev["struct rdma_device *rdma_dev<br/>Associated Device"]
    end
```

**Sources:** [gpu_direct_rdma_access.c:1155-1192](), [gpu_direct_rdma_access.c:1195-1212](), [gpu_direct_rdma_access.c:145-154]()

## Task Execution Engine

The task execution engine processes RDMA read/write operations through a multi-stage pipeline that handles address resolution, work request construction, and hardware interaction.

### Task Submission Flow

```mermaid
graph TB
    rdma_submit_task["rdma_submit_task()<br/>Public API"] --> parse_desc["Parse remote_buf_desc_str<br/>Extract addr, size, rkey, lid, dctn"]
    parse_desc --> buff_validation["buff_size_validation()<br/>Validate SGE list"]
    buff_validation --> rdma_create_ah_cached["rdma_create_ah_cached()<br/>Address Handle Resolution"]
    rdma_create_ah_cached --> rdma_exec_task["rdma_exec_task()<br/>Hardware Execution"]
    
    subgraph "rdma_exec_task() Implementation"
        ibv_wr_start["ibv_wr_start()<br/>Begin Work Request"]
        ibv_wr_rdma_rw["ibv_wr_rdma_read/write()<br/>Set Operation Type"]
        ibv_wr_set_sge["ibv_wr_set_sge_list()<br/>Configure SGE"]
        mlx5dv_wr_set_dc_addr["mlx5dv_wr_set_dc_addr()<br/>Set DC Address"]
        ibv_wr_complete["ibv_wr_complete()<br/>Ring Doorbell"]
    end
    
    rdma_exec_task --> ibv_wr_start
    ibv_wr_start --> ibv_wr_rdma_rw
    ibv_wr_rdma_rw --> ibv_wr_set_sge
    ibv_wr_set_sge --> mlx5dv_wr_set_dc_addr
    mlx5dv_wr_set_dc_addr --> ibv_wr_complete
```

**Sources:** [gpu_direct_rdma_access.c:1342-1419](), [gpu_direct_rdma_access.c:890-1006](), [gpu_direct_rdma_access.c:904-905]()

### Completion Processing

The completion processing system handles both standard and extended (latency measurement) completion events:

```mermaid
graph LR
    rdma_poll_completions["rdma_poll_completions()"] --> poll_mode{PRINT_LATENCY?}
    poll_mode -->|Yes| ibv_start_poll["ibv_start_poll()<br/>Extended CQ"]
    poll_mode -->|No| ibv_poll_cq["ibv_poll_cq()<br/>Standard CQ"]
    ibv_start_poll --> process_extended["Process with Timestamps"]
    ibv_poll_cq --> process_standard["Process Standard Events"]
    process_extended --> app_wr_id_lookup["app_wr_id[] Lookup"]
    process_standard --> app_wr_id_lookup
    app_wr_id_lookup --> update_qp_available["Update qp_available_wr"]
```

**Sources:** [gpu_direct_rdma_access.c:1422-1548](), [gpu_direct_rdma_access.c:1440-1522](), [gpu_direct_rdma_access.c:1524-1546]()

## Address Resolution Caching

The address resolution system uses a hash table to cache Address Handles (AHs), eliminating the overhead of repeated AH creation for the same destinations.

### Hash Table Implementation

The system employs `khash.h` with custom hash and equality functions for `struct ibv_ah_attr`:

| Component | Function | Purpose |
|-----------|----------|---------|
| `kh_ib_ah_hash_func()` | Hash calculation | XOR of GID and LID values |
| `kh_ib_ah_hash_equal()` | Equality comparison | `memcmp()` of attributes |
| `rdma_create_ah_cached()` | Cache management | Lookup or create AH |

**Sources:** [gpu_direct_rdma_access.c:178-194](), [gpu_direct_rdma_access.c:1264-1305](), [gpu_direct_rdma_access.c:76]()

## Core Data Structures

### struct rdma_device

The central device structure maintains all RDMA resources and state:

| Field Group | Key Members | Purpose |
|-------------|-------------|---------|
| **Context** | `context`, `pd`, `cq` | Basic InfiniBand resources |
| **Queue Pairs** | `qp`, `qpex`, `mqpex`, `srq` | Extended queue pair interfaces |
| **Address Info** | `ib_port`, `gid`, `lid`, `mtu` | Network addressing |
| **Work Management** | `app_wr_id[]`, `qp_available_wr` | Outstanding operation tracking |
| **Address Cache** | `ah_hash` | Cached address handles |

**Sources:** [gpu_direct_rdma_access.c:97-143](), [gpu_direct_rdma_access.c:109-112](), [gpu_direct_rdma_access.c:128]()

### struct rdma_task_attr

The task attribute structure defines RDMA operation parameters:

```mermaid
graph TB
    subgraph "struct rdma_task_attr"
        remote_desc["char *remote_buf_desc_str<br/>Remote Buffer Description"]
        remote_offset["size_t remote_buf_offset<br/>Offset in Remote Buffer"]
        local_buf["struct rdma_buffer *local_buf_rdma<br/>Local Memory Region"]
        iovec["struct iovec *local_buf_iovec<br/>Scatter-Gather List"]
        iovcnt["int local_buf_iovcnt<br/>SGE Count"]
        flags["uint32_t flags<br/>Operation Flags"]
        wr_id["uint64_t wr_id<br/>Work Request ID"]
    end
```

**Sources:** [gpu_direct_rdma_access.h:69-78](), [gpu_direct_rdma_access.h:65-67](), [gpu_direct_rdma_access.c:156-169]()

---

