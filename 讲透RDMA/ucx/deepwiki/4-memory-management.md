<!-- source: DeepWiki mcp.deepwiki.com · repo openucx/ucx · page 4 Memory Management · fetched 2026-11-11 -->

# Memory Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/ucp/core/ucp_request.c](src/ucp/core/ucp_request.c)
- [src/ucp/core/ucp_request.h](src/ucp/core/ucp_request.h)
- [src/ucp/core/ucp_request.inl](src/ucp/core/ucp_request.inl)
- [src/ucp/proto/proto_am.inl](src/ucp/proto/proto_am.inl)
- [src/ucp/stream/stream.h](src/ucp/stream/stream.h)
- [src/ucp/stream/stream_recv.c](src/ucp/stream/stream_recv.c)
- [src/ucp/stream/stream_send.c](src/ucp/stream/stream_send.c)
- [src/ucp/tag/eager_rcv.c](src/ucp/tag/eager_rcv.c)
- [src/ucp/tag/eager_snd.c](src/ucp/tag/eager_snd.c)
- [src/ucp/tag/offload.c](src/ucp/tag/offload.c)
- [src/ucp/tag/offload.h](src/ucp/tag/offload.h)
- [src/ucp/tag/tag_match.c](src/ucp/tag/tag_match.c)
- [src/ucp/tag/tag_match.h](src/ucp/tag/tag_match.h)
- [src/ucp/tag/tag_match.inl](src/ucp/tag/tag_match.inl)
- [src/ucp/tag/tag_recv.c](src/ucp/tag/tag_recv.c)
- [src/ucp/tag/tag_send.c](src/ucp/tag/tag_send.c)
- [src/uct/ib/base/ib_md.c](src/uct/ib/base/ib_md.c)
- [src/uct/ib/base/ib_md.h](src/uct/ib/base/ib_md.h)
- [src/uct/ib/configure.m4](src/uct/ib/configure.m4)
- [src/uct/ib/mlx5/dv/ib_mlx5_dv.c](src/uct/ib/mlx5/dv/ib_mlx5_dv.c)
- [src/uct/ib/mlx5/dv/ib_mlx5_ifc.h](src/uct/ib/mlx5/dv/ib_mlx5_ifc.h)
- [src/uct/ib/mlx5/dv/ib_mlx5dv_md.c](src/uct/ib/mlx5/dv/ib_mlx5dv_md.c)
- [src/uct/ib/mlx5/ib_mlx5.c](src/uct/ib/mlx5/ib_mlx5.c)
- [src/uct/ib/mlx5/ib_mlx5.h](src/uct/ib/mlx5/ib_mlx5.h)
- [src/uct/ib/mlx5/ib_mlx5.inl](src/uct/ib/mlx5/ib_mlx5.inl)

</details>



## Purpose and Scope

This document describes UCX's memory management system, which handles registration, protection, and remote access of memory regions. Memory management in UCX operates across two layers: the high-level UCP layer provides portable memory handles for applications, while the lower UCT layer implements transport-specific memory registration and key generation for hardware like InfiniBand NICs and GPUs.

For information about memory domains as UCT components, see [Memory Domains](#4.1). For details on memory types and GPU-specific handling, see [Memory Types and GPU Support](#4.3). For memory registration and remote key mechanisms, see [Memory Registration and Remote Keys](#4.2).

## Architecture Overview

Memory management in UCX spans both the UCP (Protocol) and UCT (Transport) layers, with the UCP layer providing a unified interface while UCT handles hardware-specific registration.

```mermaid
graph TB
    subgraph "Application"
        APP_BUF["Application Buffer<br/>(malloc/GPU alloc)"]
    end
    
    subgraph "UCP Memory Management"
        UCP_MEM_MAP["ucp_mem_map()<br/>Map/Register Memory"]
        UCP_MEMH["ucp_mem_h<br/>UCP Memory Handle"]
        UCP_MEMH_PACK["ucp_memh_pack()<br/>Serialize for Network"]
        UCP_RKEY["ucp_rkey_h<br/>Remote Access Key"]
    end
    
    subgraph "UCT Memory Management"
        UCT_MD["uct_md_h<br/>Memory Domain"]
        UCT_MEM_REG["uct_md_mem_reg()<br/>Hardware Registration"]
        UCT_MEMH["uct_mem_h<br/>Local Memory Handle"]
        UCT_RKEY["Packed RKEY Buffer<br/>Wire Format"]
    end
    
    subgraph "Hardware Layer"
        IB_PD["Protection Domain<br/>ibv_pd"]
        IB_MR["Memory Region<br/>ibv_mr with lkey/rkey"]
        DEVX_MKEY["DEVX MKEY<br/>Direct HW Access"]
    end
    
    APP_BUF --> UCP_MEM_MAP
    UCP_MEM_MAP --> UCP_MEMH
    UCP_MEMH --> UCP_MEMH_PACK
    UCP_MEMH_PACK --> UCP_RKEY
    
    UCP_MEM_MAP --> UCT_MD
    UCT_MD --> UCT_MEM_REG
    UCT_MEM_REG --> UCT_MEMH
    UCT_MEMH --> UCT_RKEY
    
    UCT_MEM_REG --> IB_PD
    IB_PD --> IB_MR
    IB_PD --> DEVX_MKEY
    IB_MR -.->|standard path| UCT_MEMH
    DEVX_MKEY -.->|optimized path| UCT_MEMH
```

**Sources:** [src/ucp/api/ucp.h:369-400](), [src/uct/ib/base/ib_md.h:116-126](), [src/uct/ib/base/ib_md.h:141-175]()

## UCP Memory API

The UCP layer provides application-facing memory management through handles and operations that abstract transport-specific details.

### Memory Handle Structure

```mermaid
graph LR
    subgraph "ucp_mem_h Structure"
        MEMH["ucp_mem_h<br/>Opaque Handle"]
        ADDR["address<br/>Virtual Address"]
        LEN["length<br/>Size in Bytes"]
        MEMTYPE["mem_type<br/>HOST/CUDA/ROCM"]
    end
    
    subgraph "Memory Registration Parameters"
        PARAMS["ucp_mem_map_params_t"]
        FLAGS["flags<br/>ALLOCATE/FIXED/LOCK"]
        PROT["prot<br/>LOCAL_READ/WRITE<br/>REMOTE_READ/WRITE"]
        MEMTYPE_PARAM["memory_type<br/>Explicit Type"]
    end
    
    subgraph "Memory Attributes"
        ATTRS["ucp_mem_attr_t"]
        ATTR_ADDR["address"]
        ATTR_LEN["length"]
        ATTR_TYPE["mem_type"]
    end
    
    PARAMS --> MEMH
    MEMH --> ATTRS
```

The `ucp_mem_h` handle represents a registered memory region. Applications create it using `ucp_mem_map()` and can query its properties using `ucp_mem_query()`.

Key API functions:
- `ucp_mem_map()` - Register or allocate memory [src/ucp/api/ucp.h:377-400]()
- `ucp_mem_unmap()` - Unregister memory
- `ucp_memh_pack()` - Serialize for remote access [src/ucp/api/ucp.h:1156-1215]()
- `ucp_mem_query()` - Query memory attributes

**Sources:** [src/ucp/api/ucp_def.h:155-167](), [src/ucp/api/ucp_def.h:185-207](), [src/ucp/api/ucp.h:547-582]()

### Memory Mapping Flags

| Flag | Value | Description |
|------|-------|-------------|
| `UCP_MEM_MAP_NONBLOCK` | `UCS_BIT(0)` | Complete mapping faster, populate pages lazily |
| `UCP_MEM_MAP_ALLOCATE` | `UCS_BIT(1)` | Allocate memory (not just register) |
| `UCP_MEM_MAP_FIXED` | `UCS_BIT(2)` | Use exact address provided |
| `UCP_MEM_MAP_SYMMETRIC_RKEY` | `UCS_BIT(3)` | Generate symmetric remote keys |
| `UCP_MEM_MAP_LOCK` | `UCS_BIT(4)` | Pin and populate pages immediately |

**Sources:** [src/ucp/api/ucp.h:547-582]()

### Remote Key Management

Remote keys enable memory access from remote endpoints:

```mermaid
graph TB
    subgraph "Local Node"
        LOCAL_MEMH["ucp_mem_h<br/>Local Memory Handle"]
        PACK["ucp_memh_pack()<br/>Serialize RKEY"]
        PACKED_BUF["Packed Buffer<br/>Wire Format"]
    end
    
    subgraph "Network Transfer"
        WIRE["Application sends<br/>packed buffer via<br/>control channel"]
    end
    
    subgraph "Remote Node"
        REMOTE_BUF["Received Buffer"]
        UNPACK["ucp_ep_rkey_unpack()<br/>Deserialize"]
        RKEY["ucp_rkey_h<br/>Remote Key Handle"]
        RMA_OPS["RMA Operations<br/>ucp_put/get/atomic"]
    end
    
    LOCAL_MEMH --> PACK
    PACK --> PACKED_BUF
    PACKED_BUF --> WIRE
    WIRE --> REMOTE_BUF
    REMOTE_BUF --> UNPACK
    UNPACK --> RKEY
    RKEY --> RMA_OPS
```

**Sources:** [src/ucp/api/ucp.h:1156-1215](), [src/ucp/api/ucp.h:1227-1264](), [src/ucp/api/ucp_def.h:142-152]()

## UCT Memory Domains

At the UCT layer, memory domains (`uct_md_h`) represent physical devices capable of memory registration. Each transport (IB, TCP, GPU) provides its own memory domain implementation.

### Memory Domain Structure

```mermaid
graph TB
    subgraph "uct_ib_md_t Structure"
        MD["uct_ib_md_t"]
        PD["pd<br/>ibv_pd*<br/>Protection Domain"]
        DEV["dev<br/>uct_ib_device_t<br/>IB Device Info"]
        REG_COST["reg_cost<br/>ucs_linear_func_t<br/>Registration Cost Model"]
        CONFIG["config<br/>uct_ib_md_ext_config_t"]
    end
    
    subgraph "Configuration"
        MT_REG["min_mt_reg<br/>MT Registration Threshold"]
        CHUNK["mt_reg_chunk<br/>Chunk Size"]
        ODP["odp.prefetch<br/>ODP Prefetch"]
        RETRY["reg_retry_cnt<br/>Retry Count"]
    end
    
    subgraph "Capabilities"
        CAP_FLAGS["cap_flags<br/>UCT_MD_FLAG_*"]
        REG_TYPES["reg_mem_types<br/>Supported Types"]
        NONBLOCK_TYPES["reg_nonblock_mem_types<br/>ODP Types"]
    end
    
    MD --> PD
    MD --> DEV
    MD --> REG_COST
    MD --> CONFIG
    CONFIG --> MT_REG
    CONFIG --> CHUNK
    CONFIG --> ODP
    CONFIG --> RETRY
    MD --> CAP_FLAGS
    MD --> REG_TYPES
    MD --> NONBLOCK_TYPES
```

**Sources:** [src/uct/ib/base/ib_md.h:141-175](), [src/uct/ib/base/ib_md.h:87-113](), [src/uct/ib/base/ib_md.h:188-209]()

### Memory Registration Flow

```mermaid
sequenceDiagram
    participant App as Application
    participant UCP as UCP Layer
    participant UCT as UCT MD
    participant Verbs as IB Verbs
    participant HW as Hardware

    App->>UCP: ucp_mem_map(buffer, size, params)
    UCP->>UCT: uct_md_mem_reg(address, length, flags)
    
    alt Standard Registration
        UCT->>UCT: uct_ib_reg_mr()
        UCT->>Verbs: ibv_reg_mr(pd, addr, len, access)
        Verbs->>HW: Pin pages, create MR
        HW-->>Verbs: lkey/rkey
        Verbs-->>UCT: ibv_mr*
    else DEVX Registration
        UCT->>UCT: mlx5dv_devx_obj_create(CREATE_MKEY)
        UCT->>HW: Direct DEVX command
        HW-->>UCT: MKEY
    end
    
    UCT->>UCT: Store lkey/rkey in uct_ib_mem_t
    UCT-->>UCP: uct_mem_h
    UCP-->>App: ucp_mem_h
```

**Sources:** [src/uct/ib/base/ib_md.c:469-528](), [src/uct/ib/mlx5/dv/ib_mlx5dv_md.c:136-189]()

## Memory Registration Methods

UCX supports multiple memory registration paths with different characteristics.

### Standard Verbs Registration

The standard path uses `ibv_reg_mr()` to register memory:

```mermaid
graph LR
    subgraph "uct_ib_reg_mr()"
        ADDR["address<br/>Virtual Address"]
        LEN["length<br/>Size"]
        FLAGS["access_flags<br/>LOCAL_WRITE<br/>REMOTE_READ/WRITE<br/>REMOTE_ATOMIC"]
    end
    
    subgraph "ibv_reg_mr()"
        PD["pd<br/>Protection Domain"]
        PIN["Pin Physical Pages"]
        CREATE["Create MR Entry"]
    end
    
    subgraph "Result"
        MR["ibv_mr"]
        LKEY["lkey<br/>Local Key"]
        RKEY["rkey<br/>Remote Key"]
    end
    
    ADDR --> PIN
    LEN --> PIN
    FLAGS --> CREATE
    PD --> CREATE
    PIN --> CREATE
    CREATE --> MR
    MR --> LKEY
    MR --> RKEY
```

The function `uct_ib_reg_mr()` wraps `ibv_reg_mr()` with retry logic and profiling. On success, it returns an `ibv_mr` structure containing local and remote keys.

**Sources:** [src/uct/ib/base/ib_md.c:469-528](), [src/uct/ib/base/ib_md.c:269-297]()

### Multi-Threaded Registration

For large memory regions (>= `IB_REG_MT_THRESH`), UCX uses multi-threaded registration to parallelize the work:

```mermaid
graph TB
    subgraph "Large Memory Region"
        REGION["Memory Region<br/>Size >= mt_reg_chunk"]
    end
    
    subgraph "Chunking"
        CHUNK1["Chunk 1<br/>mt_reg_chunk"]
        CHUNK2["Chunk 2<br/>mt_reg_chunk"]
        CHUNK3["Chunk 3<br/>mt_reg_chunk"]
        CHUNKN["Chunk N<br/>remaining"]
    end
    
    subgraph "Parallel Registration"
        THREAD1["Thread 1<br/>ibv_reg_mr(chunk1)"]
        THREAD2["Thread 2<br/>ibv_reg_mr(chunk2)"]
        THREAD3["Thread 3<br/>ibv_reg_mr(chunk3)"]
        THREADN["Thread N<br/>ibv_reg_mr(chunkN)"]
    end
    
    subgraph "KSM Wrapping"
        KSM["Create KSM MKEY<br/>mlx5dv_devx_obj_create"]
        KLM["KLM List<br/>Points to all MRs"]
        INDIRECT["Indirect MKEY<br/>Single rkey"]
    end
    
    REGION --> CHUNK1
    REGION --> CHUNK2
    REGION --> CHUNK3
    REGION --> CHUNKN
    
    CHUNK1 --> THREAD1
    CHUNK2 --> THREAD2
    CHUNK3 --> THREAD3
    CHUNKN --> THREADN
    
    THREAD1 --> KLM
    THREAD2 --> KLM
    THREAD3 --> KLM
    THREADN --> KLM
    
    KLM --> KSM
    KSM --> INDIRECT
```

Multi-threaded registration creates multiple `ibv_mr` structures in parallel, then wraps them with a KSM (Kernel Shared Memory) indirect MKEY that provides a single rkey for the entire region.

**Sources:** [src/uct/ib/base/ib_md.c:308-349](), [src/uct/ib/base/ib_md.c:351-467](), [src/uct/ib/mlx5/dv/ib_mlx5dv_md.c:229-282]()

### Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `IB_REG_MT_THRESH` | 4GB | Minimum size for multi-threaded registration |
| `IB_REG_MT_CHUNK` | 2GB | Size of each chunk in MT registration |
| `IB_REG_MT_BIND` | no | Bind registration threads to CPUs |
| `IB_REG_RETRY_CNT` | inf | Number of registration retry attempts |

**Sources:** [src/uct/ib/base/ib_md.c:144-169]()

## Memory Keys and RKEY Packing

Memory keys enable local and remote access to registered memory.

### Key Structure

```mermaid
graph TB
    subgraph "uct_ib_mem_t"
        MEMH["Memory Handle"]
        LKEY["lkey<br/>uint32_t<br/>Local Access Key"]
        RKEY["rkey<br/>uint32_t<br/>Remote Access Key"]
        FLAGS["flags<br/>ODP/ATOMIC/RMA/GVA"]
    end
    
    subgraph "Packed RKEY Format"
        PACKED["uint64_t packed_rkey"]
        DIRECT["Bits 0-31<br/>Direct RKEY"]
        ATOMIC["Bits 32-63<br/>Atomic RKEY or INVALID"]
    end
    
    subgraph "RKEY Resolution"
        RESOLVE["uct_ib_resolve_atomic_rkey()"]
        CHECK_ATOMIC["Check if atomic access<br/>needed"]
        OFFSET["Add atomic_mr_offset<br/>if indirect key"]
    end
    
    MEMH --> LKEY
    MEMH --> RKEY
    MEMH --> FLAGS
    
    RKEY --> PACKED
    PACKED --> DIRECT
    PACKED --> ATOMIC
    
    PACKED --> RESOLVE
    RESOLVE --> CHECK_ATOMIC
    CHECK_ATOMIC --> OFFSET
```

The packed RKEY format encodes both a direct key (for standard operations) and optionally an atomic key (for atomic operations requiring special alignment):

```c
packed_rkey = (atomic_rkey << 32) | direct_rkey
```

**Sources:** [src/uct/ib/base/ib_md.h:116-126](), [src/uct/ib/base/ib_md.h:260-278](), [src/uct/ib/base/ib_md.h:301-312]()

### RKEY Packing Function Flow

```mermaid
sequenceDiagram
    participant App as Application
    participant UCP as ucp_memh_pack()
    participant UCT_MD as uct_md_mkey_pack()
    participant IB as uct_ib_verbs_mkey_pack()
    participant Pack as uct_ib_md_pack_rkey()

    App->>UCP: Pack memory handle
    UCP->>UCT_MD: Pack local memh
    UCT_MD->>IB: mkey_pack operation
    
    alt Needs Atomic Key
        IB->>IB: Get atomic_mr_type
        IB->>IB: Determine atomic_rkey
    else Standard Key
        IB->>IB: Use direct rkey only
        IB->>IB: Set atomic_rkey = INVALID
    end
    
    IB->>Pack: Pack both keys
    Pack->>Pack: Combine into uint64_t
    Pack-->>IB: Packed buffer
    IB-->>UCT_MD: Success
    UCT_MD-->>UCP: Packed RKEY
    UCP-->>App: Serialized buffer
```

**Sources:** [src/uct/ib/base/ib_md.c:732-752](), [src/uct/ib/base/ib_md.h:272-279]()

## MLX5 DEVX Memory Management

MLX5 devices support DEVX (Direct Export Verbs) for optimized memory registration and key management.

### DEVX Memory Handle

```mermaid
graph TB
    subgraph "uct_ib_mlx5_devx_mem_t"
        BASE["super<br/>uct_ib_mem_t<br/>Base Handle"]
        ADDR["address<br/>Virtual Address"]
        MRS["mrs[]<br/>Array of MRs"]
        INDIRECT_MR["indirect_dvmr<br/>struct mlx5dv_devx_obj*"]
        INDIRECT_KEY["indirect_rkey<br/>uint32_t"]
        ATOMIC_MR["atomic_dvmr<br/>struct mlx5dv_devx_obj*"]
        ATOMIC_KEY["atomic_rkey<br/>uint32_t"]
    end
    
    subgraph "MR Types"
        DEFAULT["UCT_IB_MR_DEFAULT<br/>Standard MR"]
        STRICT["UCT_IB_MR_STRICT_ORDER<br/>Non-relaxed Order"]
    end
    
    subgraph "KSM Data"
        KSM["ksm_data<br/>For MT registration"]
        KSM_MRS["mrs[]<br/>Array of chunk MRs"]
        KSM_DVMR["dvmr<br/>KSM wrapper"]
    end
    
    BASE --> MRS
    BASE --> INDIRECT_MR
    BASE --> INDIRECT_KEY
    BASE --> ATOMIC_MR
    BASE --> ATOMIC_KEY
    MRS --> DEFAULT
    MRS --> STRICT
    BASE --> KSM
    KSM --> KSM_MRS
    KSM --> KSM_DVMR
```

**Sources:** [src/uct/ib/mlx5/dv/ib_mlx5dv_md.c:542-575](), [src/uct/ib/mlx5/dv/ib_mlx5dv_md.c:593-616]()

### KSM (Kernel Shared Memory) Registration

KSM allows creating an indirect memory key that points to multiple underlying memory regions:

```mermaid
graph TB
    subgraph "Input"
        ADDR["Virtual Address"]
        LEN["Length"]
        ATOMIC_FLAG["atomic flag"]
    end
    
    subgraph "KLM List Creation"
        ALLOC["Allocate KLM array<br/>uct_ib_mlx5_alloc_mkey_inbox()"]
        FILL["Fill KLM entries<br/>uct_ib_mlx5_devx_klm_entry_set()"]
    end
    
    subgraph "KSM Creation"
        MKEY_IN["create_mkey_in"]
        SET_ADDR["Set start_addr, length"]
        SET_MODE["Set access_mode = KSM"]
        SET_TRANS["Set translations_octword_size"]
        DEVX["mlx5dv_devx_obj_create()"]
    end
    
    subgraph "Output"
        MKEY["MKEY Index"]
        RKEY["rkey = (mkey_index << 8) | mkey_tag"]
    end
    
    ADDR --> ALLOC
    LEN --> ALLOC
    ALLOC --> FILL
    FILL --> MKEY_IN
    MKEY_IN --> SET_ADDR
    SET_ADDR --> SET_MODE
    SET_MODE --> SET_TRANS
    SET_TRANS --> DEVX
    DEVX --> MKEY
    MKEY --> RKEY
    ATOMIC_FLAG --> SET_MODE
```

KSM registration creates a hardware memory key that references a list of KLM (Key-List-Memory) entries, where each entry points to an underlying memory region. This enables:
1. Wrapping multiple MRs with a single rkey
2. Creating atomic-aligned indirect keys
3. Supporting very large memory registrations

**Sources:** [src/uct/ib/mlx5/dv/ib_mlx5dv_md.c:136-189](), [src/uct/ib/mlx5/dv/ib_mlx5dv_md.c:214-227](), [src/uct/ib/mlx5/dv/ib_mlx5dv_md.c:324-350]()

### Indirect and Atomic Keys

MLX5 creates specialized keys for different access patterns:

| Key Type | Purpose | Creation |
|----------|---------|----------|
| Direct Key | Standard RMA operations | From `ibv_mr->rkey` |
| Indirect Key | Single key for multi-MR regions | `uct_ib_mlx5_devx_reg_indirect_key()` |
| Atomic Key | Atomic operations with alignment | `uct_ib_mlx5_devx_reg_atomic_key()` |

**Atomic Key Requirements:**
- Address aligned to `UCT_IB_MD_MAX_MR_SIZE` (2GB)
- Length aligned to device atomic_align
- Offset added for actual atomic access address

**Sources:** [src/uct/ib/mlx5/dv/ib_mlx5dv_md.c:542-575](), [src/uct/ib/mlx5/dv/ib_mlx5dv_md.c:593-616](), [src/uct/ib/mlx5/dv/ib_mlx5dv_md.c:324-350]()

## LRU Cache for Indirect Keys

MLX5 maintains an LRU (Least Recently Used) cache for indirect memory keys to avoid recreating them:

```mermaid
graph LR
    subgraph "LRU Structure"
        LIST["lru_rkeys.list<br/>ucs_list_head"]
        HASH["lru_rkeys.hash<br/>kh_rkeys_t"]
        COUNT["lru_rkeys.count<br/>Total created"]
    end
    
    subgraph "Cache Entry"
        ENTRY["uct_ib_mlx5_mem_lru_entry_t"]
        RKEY["rkey<br/>uint32_t"]
        MR["indirect_mr<br/>mlx5dv_devx_obj*"]
        DUMMY["is_dummy<br/>bool"]
    end
    
    subgraph "Operations"
        PUSH["uct_ib_md_mlx5_devx_mr_lru_push()"]
        POP["uct_ib_mlx5_devx_md_mr_lru_pop()"]
        UPDATE["Update entry"]
    end
    
    LIST --> ENTRY
    HASH --> ENTRY
    ENTRY --> RKEY
    ENTRY --> MR
    ENTRY --> DUMMY
    
    PUSH --> HASH
    POP --> LIST
```

The LRU cache:
- Stores up to `max_idle_rkey_count` entries (default 16)
- Evicts oldest entry when full
- Enables RKEY reuse without HW resources
- Increments `mkey_tag` periodically to prevent collisions

**Sources:** [src/uct/ib/mlx5/dv/ib_mlx5dv_md.c:376-404](), [src/uct/ib/mlx5/dv/ib_mlx5dv_md.c:429-492](), [src/uct/ib/mlx5/dv/ib_mlx5dv_md.c:494-513]()

## Special Features

### On-Demand Paging (ODP)

ODP enables registration without pre-faulting pages:

```mermaid
graph TB
    subgraph "Registration"
        CHECK["Check ODP support<br/>md->reg_nonblock_mem_types"]
        FLAG["Set UCT_IB_MEM_FLAG_ODP"]
        ACCESS["Add IBV_ACCESS_ON_DEMAND"]
        REG["ibv_reg_mr() with ODP"]
    end
    
    subgraph "Page Fault Handling"
        FAULT["Page Fault on Access"]
        KERNEL["Kernel Handler"]
        PIN["Pin Page"]
        RETRY["Retry Access"]
    end
    
    subgraph "Optional Prefetch"
        CONFIG["IB_ODP_PREFETCH=y"]
        ADVISE["ibv_advise_mr()<br/>IBV_ADVISE_MR_ADVICE_PREFETCH_WRITE"]
        POPULATE["Populate Pages"]
    end
    
    CHECK --> FLAG
    FLAG --> ACCESS
    ACCESS --> REG
    REG --> FAULT
    FAULT --> KERNEL
    KERNEL --> PIN
    PIN --> RETRY
    
    CONFIG --> ADVISE
    ADVISE --> POPULATE
```

ODP registration:
- Uses `UCT_MD_MEM_FLAG_NONBLOCK` flag
- Sets `memh->flags |= UCT_IB_MEM_FLAG_ODP`
- Adds `IBV_ACCESS_ON_DEMAND` to access flags
- Optionally prefetches via `uct_ib_mem_prefetch()`

**Sources:** [src/uct/ib/base/ib_md.c:592-631](), [src/uct/ib/base/ib_md.c:546-577](), [src/uct/ib/base/ib_md.c:579-590]()

### Relaxed Ordering

PCIe relaxed ordering improves performance on some systems:

```mermaid
graph LR
    subgraph "Configuration"
        CONFIG["IB_PCI_RELAXED_ORDERING=try/yes/no"]
        PARSE["Parse setting"]
        CHECK["Check HW support"]
    end
    
    subgraph "MR Creation"
        DEFAULT["Default MR<br/>With relaxed order"]
        STRICT["Strict Order MR<br/>Without relaxed order"]
    end
    
    subgraph "Selection"
        ATOMIC["Atomic operations?"]
        SELECT_STRICT["Use STRICT MR"]
        SELECT_DEFAULT["Use DEFAULT MR"]
    end
    
    CONFIG --> PARSE
    PARSE --> CHECK
    CHECK --> DEFAULT
    CHECK --> STRICT
    
    ATOMIC -->|yes| SELECT_STRICT
    ATOMIC -->|no| SELECT_DEFAULT
    SELECT_STRICT --> STRICT
    SELECT_DEFAULT --> DEFAULT
```

When enabled:
- Creates two MRs: `UCT_IB_MR_DEFAULT` (relaxed), `UCT_IB_MR_STRICT_ORDER`
- Atomic operations use strict-order MR
- Adds `IBV_ACCESS_RELAXED_ORDERING` flag to default MR
- Atomic RKEY provides strict-order access

**Sources:** [src/uct/ib/base/ib_md.c:648-703](), [src/uct/ib/base/ib_md.h:128-135](), [src/uct/ib/base/ib_md.c:634-646]()

### Symmetric Keys

Symmetric keys enable RKEY comparison across peers:

```mermaid
graph TB
    subgraph "Allocation"
        FLAG["UCP_MEM_MAP_SYMMETRIC_RKEY"]
        RESERVE["mkey_by_name_reserve<br/>Reserved MKEY range"]
        BLOCK["smkey_block_size<br/>Block allocation"]
    end
    
    subgraph "Registration"
        CREATE["Create symmetric MKEY"]
        INDEX["Use reserved index"]
        DEVX["mlx5dv_devx_obj_create()"]
    end
    
    subgraph "Properties"
        COMPARE["Keys from different<br/>nodes are comparable"]
        OFFSET["Consistent offset<br/>between direct/atomic"]
        REUSE["Can interchange keys"]
    end
    
    FLAG --> RESERVE
    RESERVE --> BLOCK
    BLOCK --> CREATE
    CREATE --> INDEX
    INDEX --> DEVX
    DEVX --> COMPARE
    COMPARE --> OFFSET
    OFFSET --> REUSE
```

Symmetric keys are allocated from a reserved MKEY space, ensuring that peers registering the same memory region get comparable keys.

**Sources:** [test/gtest/uct/ib/test_ib_md.cc:190-249](), [src/ucp/api/ucp.h:574-575]()

## Memory Types and GPU Support

UCX supports heterogeneous memory including GPU memory.

### Memory Type Detection

```mermaid
graph TB
    subgraph "Memory Type Enum"
        HOST["UCS_MEMORY_TYPE_HOST<br/>Standard host memory"]
        CUDA["UCS_MEMORY_TYPE_CUDA<br/>NVIDIA GPU memory"]
        CUDA_MANAGED["UCS_MEMORY_TYPE_CUDA_MANAGED<br/>Unified memory"]
        ROCM["UCS_MEMORY_TYPE_ROCM<br/>AMD GPU memory"]
        ROCM_MANAGED["UCS_MEMORY_TYPE_ROCM_MANAGED<br/>AMD unified memory"]
    end
    
    subgraph "Detection"
        DETECT["ucs_memtype_detect()"]
        CACHE["Memory type cache"]
        QUERY["Query device APIs"]
    end
    
    subgraph "Registration"
        CHECK_TYPE["Check md->reg_mem_types"]
        SUPPORT["Verify type supported"]
        GPU_REG["GPU-specific registration"]
    end
    
    DETECT --> CACHE
    DETECT --> QUERY
    CACHE --> CHECK_TYPE
    QUERY --> CHECK_TYPE
    CHECK_TYPE --> SUPPORT
    SUPPORT --> GPU_REG
```

Memory types are detected and cached. Each memory domain reports supported types via `md_attr.reg_mem_types`.

**Sources:** [src/ucp/api/ucp.h:396-397](), [src/uct/ib/base/ib_md.h:158-160]()

### GPU Direct RDMA

GPU Direct RDMA enables direct NIC-to-GPU transfers:

```mermaid
graph LR
    subgraph "GPU Memory"
        GPU_BUF["GPU Buffer<br/>cudaMalloc/hipMalloc"]
        GPU_PHYSICAL["Physical GPU Pages"]
    end
    
    subgraph "Registration"
        CHECK_GDR["IB_GPU_DIRECT_RDMA=try/yes"]
        REG["ibv_reg_mr() with GPU buffer"]
        PIN["Pin GPU pages<br/>via driver"]
    end
    
    subgraph "RDMA Operations"
        NIC["IB NIC"]
        DMA["Direct DMA<br/>NIC <-> GPU"]
        NO_CPU["Bypass CPU"]
    end
    
    GPU_BUF --> GPU_PHYSICAL
    GPU_PHYSICAL --> CHECK_GDR
    CHECK_GDR --> REG
    REG --> PIN
    PIN --> NIC
    NIC --> DMA
    DMA --> NO_CPU
```

GPU Direct RDMA:
- Enabled via `IB_GPU_DIRECT_RDMA` configuration
- Requires GPU driver support (nvidia-peermem, ROCm KFD)
- Registers GPU memory directly with IB NIC
- Enables zero-copy GPU-to-GPU transfers

**Sources:** [src/uct/ib/base/ib_md.c:118-120](), [src/uct/ib/base/ib_md.h:207]()

### DMA-BUF Support

DMA-BUF provides another mechanism for GPU memory:

```mermaid
graph TB
    subgraph "DMA-BUF Export"
        GPU_MEM["GPU Memory"]
        EXPORT["Export as DMA-BUF"]
        FD["DMA-BUF File Descriptor"]
        OFFSET["Buffer Offset"]
    end
    
    subgraph "Registration"
        PARAMS["UCT_MD_MEM_REG_FIELD_DMABUF_FD"]
        DMABUF_REG["ibv_reg_dmabuf_mr()"]
        MR["Memory Region"]
    end
    
    subgraph "Properties"
        SHARE["Shareable across processes"]
        IMPORT["Can import from other device"]
    end
    
    GPU_MEM --> EXPORT
    EXPORT --> FD
    EXPORT --> OFFSET
    FD --> PARAMS
    OFFSET --> PARAMS
    PARAMS --> DMABUF_REG
    DMABUF_REG --> MR
    MR --> SHARE
    MR --> IMPORT
```

DMA-BUF allows GPU memory to be:
- Exported as a file descriptor
- Registered with `ibv_reg_dmabuf_mr()`
- Shared across processes
- Imported from other devices

**Sources:** [src/uct/ib/base/ib_md.c:483-486](), [src/uct/ib/base/ib_md.c:507-514]()

## Memory Registration Statistics

UCX tracks memory registration costs for optimization:

```mermaid
graph LR
    subgraph "Cost Model"
        OVERHEAD["MEM_REG_OVERHEAD<br/>Fixed cost (16us)"]
        GROWTH["MEM_REG_GROWTH<br/>Per-byte cost (0.06ns)"]
        FORMULA["Cost = overhead + size * growth"]
    end
    
    subgraph "Statistics"
        MEM_ALLOC["UCT_IB_MD_STAT_MEM_ALLOC<br/>Allocations"]
        MEM_REG["UCT_IB_MD_STAT_MEM_REG<br/>Registrations"]
    end
    
    subgraph "Usage"
        PROFILE["UCS_PROFILE_CALL"]
        TRACE["Registration tracing"]
        TIMING["Measure actual time"]
    end
    
    OVERHEAD --> FORMULA
    GROWTH --> FORMULA
    FORMULA --> MEM_REG
    MEM_ALLOC --> PROFILE
    MEM_REG --> TRACE
    TRACE --> TIMING
```

The cost model helps UCX decide between eager, zcopy, and rendezvous protocols based on registration overhead.

**Sources:** [src/uct/ib/base/ib_md.c:55-59](), [src/uct/ib/base/ib_md.c:192-200](), [src/uct/ib/base/ib_md.h:50-54]()

## Key API Functions Summary

### UCP Layer

| Function | Purpose | Returns |
|----------|---------|---------|
| `ucp_mem_map()` | Register or allocate memory | `ucs_status_t` |
| `ucp_mem_unmap()` | Unregister memory | `ucs_status_t` |
| `ucp_mem_query()` | Query memory attributes | `ucs_status_t` |
| `ucp_memh_pack()` | Serialize memory handle | `ucs_status_t` |
| `ucp_ep_rkey_unpack()` | Deserialize remote key | `ucs_status_t` |
| `ucp_rkey_destroy()` | Release remote key | `void` |

### UCT Layer

| Function | Purpose | File Location |
|----------|---------|---------------|
| `uct_md_mem_reg()` | Register memory | [src/uct/ib/base/ib_md.c:648-703]() |
| `uct_md_mem_dereg()` | Deregister memory | [src/uct/ib/base/ib_md.c:706-730]() |
| `uct_md_mkey_pack()` | Pack memory key | [src/uct/ib/base/ib_md.c:732-752]() |
| `uct_ib_reg_mr()` | IB registration | [src/uct/ib/base/ib_md.c:469-528]() |
| `uct_ib_dereg_mr()` | IB deregistration | [src/uct/ib/base/ib_md.c:530-544]() |

### MLX5 DEVX

| Function | Purpose | File Location |
|----------|---------|---------------|
| `uct_ib_mlx5_devx_reg_ksm_data()` | Create KSM key | [src/uct/ib/mlx5/dv/ib_mlx5dv_md.c:519-540]() |
| `uct_ib_mlx5_devx_reg_indirect_key()` | Register indirect key | [src/uct/ib/mlx5/dv/ib_mlx5dv_md.c:542-575]() |
| `uct_ib_mlx5_devx_reg_atomic_key()` | Register atomic key | [src/uct/ib/mlx5/dv/ib_mlx5dv_md.c:593-616]() |
| `uct_ib_md_mlx5_devx_mr_lru_push()` | Add to LRU cache | [src/uct/ib/mlx5/dv/ib_mlx5dv_md.c:429-492]() |

**Sources:** [src/ucp/api/ucp.h:369-400](), [src/uct/ib/base/ib_md.c:241-268](), [src/uct/ib/base/ib_md.h:354-440]()

---

