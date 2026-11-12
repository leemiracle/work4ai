<!-- source: DeepWiki mcp.deepwiki.com · repo openucx/ucx · page 2 UCP (Unified Communication Protocol) · fetched 2026-11-11 -->

# UCP (Unified Communication Protocol)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

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
- [test/gtest/ucp/test_ucp_ep.cc](test/gtest/ucp/test_ucp_ep.cc)

</details>



**Purpose**: UCP is the high-level protocol layer in UCX that provides portable, feature-rich communication APIs for HPC and data-center applications. This document covers UCP's architecture, core abstractions, communication protocols, and connection establishment mechanisms.

**Scope**: This page focuses on UCP layer implementation (protocol logic, endpoint management, wireup). For UCT transport layer details, see [UCT (Unified Communication Transport)](#3). For memory registration and remote keys, see [Memory Management](#4).

---

## UCP Layer Position in UCX Architecture

UCP sits above the UCT (Unified Communication Transport) layer and provides:
- **Protocol-level features**: Tagged messaging, streams, RMA, active messages, rendezvous
- **Transport abstraction**: Hides UCT complexity from applications
- **Multi-lane optimization**: Uses multiple transports simultaneously for bandwidth
- **Connection management**: Automatic wireup and transport selection

```mermaid
graph TB
    subgraph "Application Layer"
        APP["Application Code"]
    end
    
    subgraph "UCP Layer"
        UCP_API["UCP API<br/>ucp.h"]
        UCP_CONTEXT["ucp_context_t<br/>Resource Management"]
        UCP_WORKER["ucp_worker_t<br/>Progress Engine"]
        UCP_EP["ucp_ep_t<br/>Endpoint Management"]
        
        UCP_API --> UCP_CONTEXT
        UCP_CONTEXT --> UCP_WORKER
        UCP_WORKER --> UCP_EP
    end
    
    subgraph "UCT Layer"
        UCT_API["UCT Transport API"]
    end
    
    APP --> UCP_API
    UCP_EP --> UCT_API
```

**Sources**: [src/ucp/api/ucp.h:1-900](), [Diagram 1 from overview]()

---

## Core Abstractions

### Context: `ucp_context_t`

The UCP context represents a single communication instance and holds global configuration and resources.

```mermaid
graph TB
    subgraph "Context Initialization"
        ucp_init["ucp_init()"]
        ucp_params_t["ucp_params_t<br/>features, request_size"]
        ucp_config_t["ucp_config_t<br/>Performance tuning"]
        
        ucp_params_t --> ucp_init
        ucp_config_t --> ucp_init
    end
    
    subgraph "ucp_context_t Structure"
        config["config<br/>Thresholds & modes"]
        tl_rscs["tl_rscs[]<br/>Transport resources"]
        tl_cmpts["tl_cmpts[]<br/>Transport components"]
        tl_mds["tl_mds[]<br/>Memory domains"]
        num_tls["num_tls<br/>Resource count"]
        
        config -.contains.-> tl_rscs
        tl_rscs --> num_tls
    end
    
    subgraph "Key Configuration Fields"
        bcopy_thresh["bcopy_thresh<br/>Buffer copy threshold"]
        rndv_thresh["rndv_thresh<br/>Rendezvous threshold"]
        zcopy_thresh["zcopy_thresh<br/>Zero-copy threshold"]
        rndv_mode["rndv_mode<br/>RNDV scheme selection"]
    end
    
    ucp_init --> ucp_context_t
    ucp_context_t --> config
    config --> bcopy_thresh
    config --> rndv_thresh
    config --> zcopy_thresh
    config --> rndv_mode
```

**Key Fields**:
- `config.features`: Enabled features (TAG, RMA, AMO, STREAM, AM)
- `tl_rscs[]`: Array of available transport resources
- `tl_cmpts[]`: Array of UCT components
- `tl_mds[]`: Array of memory domains for registration

**Configuration Parameters** (from `ucp_context_config_t`):
- `bcopy_thresh`: When to switch from short to buffer-copy protocol
- `rndv_thresh`: When to switch from eager to rendezvous (intra/inter node)
- `zcopy_thresh`: When to use zero-copy operations
- `rndv_mode`: Rendezvous scheme (auto, get_zcopy, put_zcopy, rkey_ptr, am)
- `max_eager_lanes`, `max_rndv_lanes`, `max_rma_lanes`: Multi-lane limits

**Sources**: [src/ucp/core/ucp_context.h:56-283](), [src/ucp/core/ucp_context.c:161-452](), [src/ucp/api/ucp.h:119-173]()

---

### Worker: `ucp_worker_t`

The worker is the progress engine that drives communication. Each worker has its own set of UCT interfaces and manages multiple endpoints.

```mermaid
graph TB
    subgraph "Worker Creation"
        ucp_worker_create["ucp_worker_create()"]
        ucp_worker_params_t["ucp_worker_params_t<br/>thread_mode, cpu_mask"]
        
        ucp_worker_params_t --> ucp_worker_create
    end
    
    subgraph "ucp_worker_t Core"
        context["context: ucp_context_h"]
        uct["uct: uct_worker_h<br/>UCT progress engine"]
        async["async: ucs_async_context_t<br/>Thread safety"]
        
        ifaces["ifaces[]: ucp_worker_iface_t*<br/>UCT interface wrappers"]
        num_ifaces["num_ifaces"]
        
        all_eps["all_eps: list<br/>All endpoints"]
        internal_eps["internal_eps: list<br/>Internal endpoints"]
        num_all_eps["num_all_eps"]
    end
    
    subgraph "ucp_worker_iface_t"
        iface["iface: uct_iface_h<br/>UCT interface"]
        rsc_index["rsc_index<br/>Resource index"]
        attr["attr: uct_iface_attr_t<br/>Capabilities"]
        activate_count["activate_count<br/>Reference count"]
    end
    
    subgraph "Progress and Events"
        ucp_worker_progress["ucp_worker_progress()<br/>Drive communication"]
        ucp_worker_arm["ucp_worker_arm()<br/>Wait for events"]
        event_fd["event_fd<br/>Wakeup descriptor"]
        
        ucp_worker_progress --> ifaces
        ucp_worker_arm --> event_fd
    end
    
    ucp_worker_create --> ucp_worker_t
    ucp_worker_t --> context
    ucp_worker_t --> uct
    ucp_worker_t --> ifaces
    ifaces --> ucp_worker_iface_t
    ucp_worker_iface_t --> iface
    ucp_worker_t --> all_eps
```

**Key Responsibilities**:
1. **Progress Engine**: `ucp_worker_progress()` polls UCT interfaces
2. **Interface Management**: Opens and activates UCT interfaces on demand
3. **Endpoint Management**: Tracks all endpoints created on this worker
4. **Event Handling**: Supports wakeup via `UCP_FEATURE_WAKEUP`

**Worker Interface (`ucp_worker_iface_t`)** wraps each UCT interface with:
- `activate_count`: Reference counting for on-demand activation
- `proxy_recv_count`: Counts messages received via proxy AM handlers
- `flags`: `UCP_WORKER_IFACE_FLAG_OFFLOAD_ACTIVATED`, `UCP_WORKER_IFACE_FLAG_ON_ARM_LIST`

**Sources**: [src/ucp/core/ucp_worker.h:206-439](), [src/ucp/core/ucp_worker.c:282-375](), [src/ucp/core/ucp_worker.c:576-609]()

---

### Endpoint: `ucp_ep_t`

An endpoint represents a connection to a remote worker. It manages multiple lanes (transport paths) for different operation types.

```mermaid
graph TB
    subgraph "Endpoint Creation"
        ucp_ep_create["ucp_ep_create()"]
        ucp_ep_params_t["ucp_ep_params_t<br/>address, sockaddr, flags"]
        
        ucp_ep_params_t --> ucp_ep_create
    end
    
    subgraph "ucp_ep_t Structure"
        worker["worker: ucp_worker_h"]
        cfg_index["cfg_index<br/>Configuration index"]
        flags["flags: ucp_ep_flags_t<br/>Connection state"]
        
        uct_eps["uct_eps[UCP_MAX_FAST_PATH_LANES]<br/>Fast path lanes"]
        ext["ext: ucp_ep_ext_t*<br/>Extended fields"]
        
        am_lane["am_lane<br/>Active message lane"]
        refcount["refcount<br/>Reference counter"]
    end
    
    subgraph "ucp_ep_ext_t Extended Fields"
        uct_eps_ext["uct_eps[]<br/>Additional lanes"]
        local_ep_id["local_ep_id<br/>PTR_MAP key"]
        remote_ep_id["remote_ep_id<br/>Remote peer ID"]
        cm_idx["cm_idx<br/>CM resource index"]
        err_cb["err_cb<br/>Error handler"]
        user_data["user_data"]
    end
    
    subgraph "ucp_ep_config_t Lookup"
        ep_config["ucp_ep_config_t<br/>key, proto_select"]
        key["key: ucp_ep_config_key_t<br/>Lane configuration"]
        lanes["lanes[]<br/>Per-lane settings"]
        
        cfg_index --> ep_config
        ep_config --> key
        key --> lanes
    end
    
    ucp_ep_create --> ucp_ep_t
    ucp_ep_t --> worker
    ucp_ep_t --> cfg_index
    ucp_ep_t --> uct_eps
    ucp_ep_t --> ext
    ext --> ucp_ep_ext_t
    ucp_ep_ext_t --> local_ep_id
    ucp_ep_ext_t --> remote_ep_id
```

**Key Fields**:
- `cfg_index`: Index into worker's `ep_config[]` array
- `uct_eps[]`: Array of UCT endpoints (one per lane)
- `am_lane`: Primary lane for active messages
- `flags`: Connection state (`UCP_EP_FLAG_LOCAL_CONNECTED`, `UCP_EP_FLAG_REMOTE_CONNECTED`, `UCP_EP_FLAG_FAILED`)

**Endpoint Configuration Key** (`ucp_ep_config_key_t`):
- `num_lanes`: Number of active lanes
- `lanes[]`: Per-lane configuration (resource index, MD index, lane types)
- `am_lane`, `tag_lane`, `wireup_msg_lane`, `cm_lane`, `keepalive_lane`: Special purpose lanes
- `rma_lanes[]`, `rma_bw_lanes[]`, `amo_lanes[]`, `am_bw_lanes[]`: Sorted by priority

**Sources**: [src/ucp/core/ucp_ep.h:207-335](), [src/ucp/core/ucp_ep.c:183-264](), [src/ucp/core/ucp_ep.c:363-417]()

---

### Lanes: Multi-Transport Communication

UCP uses a **lane-based architecture** where each lane uses a different UCT endpoint/transport. Different operation types are mapped to different lanes for optimal performance.

```mermaid
graph LR
    subgraph "UCP Endpoint"
        EP["ucp_ep_t"]
    end
    
    subgraph "Lane Configuration"
        L0["Lane 0: AM<br/>rc_mlx5/mlx5_0:1"]
        L1["Lane 1: RMA_BW<br/>rc_mlx5/mlx5_0:1"]
        L2["Lane 2: RMA_BW<br/>rc_mlx5/mlx5_1:1"]
        L3["Lane 3: Keepalive<br/>ud_mlx5/mlx5_0:1"]
        L4["Lane 4: CM<br/>tcp/eth0"]
    end
    
    subgraph "Operation Mapping"
        TAG_SEND["Tag Send"]
        RMA_PUT["RMA Put"]
        RMA_GET["RMA Get"]
        KEEPALIVE["Keepalive"]
        
        TAG_SEND --> L0
        RMA_PUT --> L1
        RMA_PUT --> L2
        RMA_GET --> L1
        RMA_GET --> L2
        KEEPALIVE --> L3
    end
    
    EP --> L0
    EP --> L1
    EP --> L2
    EP --> L3
    EP --> L4
```

**Lane Types** (`ucp_lane_type_t`):
- `UCP_LANE_TYPE_AM`: Active messages and tag matching
- `UCP_LANE_TYPE_AM_BW`: High-bandwidth active messages
- `UCP_LANE_TYPE_RMA`: Remote memory access
- `UCP_LANE_TYPE_RMA_BW`: High-bandwidth RMA (multi-lane)
- `UCP_LANE_TYPE_AMO`: Atomic operations
- `UCP_LANE_TYPE_TAG`: Hardware tag matching offload
- `UCP_LANE_TYPE_KEEPALIVE`: Connection liveness checking
- `UCP_LANE_TYPE_CM`: Connection manager

**Multi-Lane Optimization**: For large transfers, UCP can stripe data across multiple lanes simultaneously to utilize aggregate bandwidth. Configuration controls:
- `max_eager_lanes`: Max lanes for eager messages
- `max_rndv_lanes`: Max lanes for rendezvous
- `max_rma_lanes`: Max lanes for RMA operations

**Sources**: [src/ucp/core/ucp_ep.h:207-250](), [src/ucp/proto/lane_type.h]()

---

## Connection Establishment (Wireup)

UCP implements a sophisticated wireup protocol to establish connections and select optimal transports.

### Wireup Protocol Flow

```mermaid
sequenceDiagram
    participant C as Client EP
    participant CW as Client Wireup EP
    participant S as Server EP
    participant SW as Server Wireup EP
    
    Note over C,SW: Phase 1: Initial Connection
    C->>CW: Create wireup_ep
    CW->>SW: WIREUP_MSG_REQUEST<br/>(local address, capabilities)
    
    Note over S,SW: Server selects transports
    SW->>S: Select lanes based on<br/>client address
    SW->>CW: WIREUP_MSG_REPLY<br/>(server address, selected lanes)
    
    Note over C,CW: Client configures lanes
    CW->>C: Configure ep_config
    C->>S: Create UCT endpoints
    C->>SW: WIREUP_MSG_ACK<br/>(confirmation)
    
    Note over C,S: Phase 2: Connected
    C->>S: Direct communication<br/>on selected lanes
    
    Note over C,S: Replace wireup_ep with real EPs
    CW->>C: Destroy wireup_ep
    C->>S: Use configured UCT EPs
```

**Wireup Message Types**:
- `UCP_WIREUP_MSG_PRE_REQUEST`: Pre-connection request (CM-based)
- `UCP_WIREUP_MSG_REQUEST`: Connection request with local address
- `UCP_WIREUP_MSG_REPLY`: Connection reply with selected configuration
- `UCP_WIREUP_MSG_ACK`: Acknowledgment, connection complete

**Wireup Endpoint** (`ucp_wireup_ep_t`): A proxy endpoint that queues operations during connection establishment:
- `pending_q`: Queue of pending operations
- `aux_ep`: Auxiliary UCT endpoint for wireup messages
- `flags`: `UCP_WIREUP_EP_FLAG_READY`, `UCP_WIREUP_EP_FLAG_LOCAL_CONNECTED`, `UCP_WIREUP_EP_FLAG_REMOTE_CONNECTED`

**Sources**: [src/ucp/wireup/wireup.c:50-216](), [src/ucp/wireup/wireup.h:40-52](), [src/ucp/wireup/wireup_ep.h:44-60]()

---

### Transport Selection

Transport selection happens during wireup based on multiple criteria.

```mermaid
graph TB
    subgraph "Selection Input"
        LOCAL_ADDR["Local Worker Address<br/>Available transports"]
        REMOTE_ADDR["Remote Worker Address<br/>Peer capabilities"]
        CRITERIA["Selection Criteria<br/>Operation type, performance"]
    end
    
    subgraph "ucp_wireup_select_transport()"
        FILTER["Filter Transports<br/>Check capabilities"]
        SCORE["Calculate Scores<br/>Bandwidth, latency"]
        SORT["Sort by Score<br/>Highest first"]
        SELECT["Select Best<br/>Per lane type"]
        
        FILTER --> SCORE
        SCORE --> SORT
        SORT --> SELECT
    end
    
    subgraph "Selection Criteria"
        MD_FLAGS["MD Flags<br/>REG, ALLOC required"]
        IFACE_FLAGS["Interface Flags<br/>AM, PUT, GET, TAG"]
        EVENT_FLAGS["Event Flags<br/>Wakeup support"]
        KEEPALIVE["Keepalive<br/>EP_CHECK, EP_KEEPALIVE"]
        
        MD_FLAGS --> FILTER
        IFACE_FLAGS --> FILTER
        EVENT_FLAGS --> FILTER
        KEEPALIVE --> FILTER
    end
    
    subgraph "Output"
        LANE_DESC["ucp_wireup_lane_desc_t[]<br/>Selected lanes"]
        EP_CONFIG_KEY["ucp_ep_config_key_t<br/>Lane configuration"]
    end
    
    LOCAL_ADDR --> ucp_wireup_select_transport
    REMOTE_ADDR --> ucp_wireup_select_transport
    CRITERIA --> ucp_wireup_select_transport
    ucp_wireup_select_transport --> SELECT
    SELECT --> LANE_DESC
    LANE_DESC --> EP_CONFIG_KEY
```

**Selection Algorithm** (`ucp_wireup_select_transport()`):
1. **Filter**: Check mandatory capabilities (MD flags, iface flags, events)
2. **Score**: Calculate transport score based on bandwidth/latency
3. **Prioritize**: Consider device distance, memory type support
4. **Select**: Choose highest scoring transport per lane type

**Scoring Functions**:
- `ucp_wireup_rma_score()`: RMA bandwidth divided by latency
- `ucp_wireup_amo_score()`: Atomic operation support
- `ucp_wireup_am_score()`: Active message bandwidth/latency
- `ucp_wireup_tag_score()`: Tag matching offload capability

**Multi-Lane Selection**: For bandwidth-intensive operations, multiple lanes of same type selected based on:
- `multi_lane_max_ratio`: Max ratio between slowest/fastest lane (default: 4)
- `multi_path_ratio`: Bandwidth efficiency when using multiple paths per device

**Sources**: [src/ucp/wireup/select.c:391-600](), [src/ucp/wireup/select.c:1200-1450](), [src/ucp/wireup/wireup.c:219-252]()

---

## Communication Protocols

### Protocol Selection

UCP dynamically selects communication protocols based on message size and memory type.

```mermaid
graph TB
    subgraph "Message Size Thresholds"
        SIZE["Message Size"]
        
        BCOPY_THRESH["bcopy_thresh<br/>~8KB"]
        ZCOPY_THRESH["zcopy_thresh<br/>~auto calculated"]
        RNDV_THRESH["rndv_thresh<br/>~auto calculated"]
        
        SIZE --> BCOPY_THRESH
        SIZE --> ZCOPY_THRESH
        SIZE --> RNDV_THRESH
    end
    
    subgraph "Protocol Selection"
        SHORT["size < bcopy_thresh<br/>SHORT Protocol<br/>Inline data"]
        BCOPY["size < zcopy_thresh<br/>BCOPY Protocol<br/>Buffer copy"]
        ZCOPY["size < rndv_thresh<br/>ZCOPY Protocol<br/>Zero-copy"]
        RNDV["size >= rndv_thresh<br/>RNDV Protocol<br/>Multi-stage"]
        
        BCOPY_THRESH --> SHORT
        BCOPY_THRESH --> BCOPY
        ZCOPY_THRESH --> ZCOPY
        RNDV_THRESH --> RNDV
    end
    
    subgraph "Tagged Message Protocols"
        TAG_SHORT["ucp_tag_send_short"]
        TAG_BCOPY["ucp_tag_send_bcopy"]
        TAG_ZCOPY["ucp_tag_send_zcopy"]
        TAG_RNDV["ucp_tag_send_rndv"]
        
        SHORT --> TAG_SHORT
        BCOPY --> TAG_BCOPY
        ZCOPY --> TAG_ZCOPY
        RNDV --> TAG_RNDV
    end
    
    subgraph "Active Message IDs"
        AM_EAGER_ONLY["UCP_AM_ID_EAGER_ONLY"]
        AM_EAGER_FIRST["UCP_AM_ID_EAGER_FIRST<br/>+EAGER_MIDDLE"]
        AM_EAGER_SYNC["UCP_AM_ID_EAGER_SYNC_ONLY<br/>+SYNC_ACK"]
        AM_RNDV_RTS["UCP_AM_ID_RNDV_RTS<br/>+RTR/ATS/ATP/DATA"]
        
        TAG_SHORT --> AM_EAGER_ONLY
        TAG_BCOPY --> AM_EAGER_FIRST
        TAG_ZCOPY --> AM_EAGER_SYNC
        TAG_RNDV --> AM_RNDV_RTS
    end
```

**Protocol Thresholds**:
- `bcopy_thresh`: Switch from inline (short) to buffer-copy (default: auto)
- `zcopy_thresh`: Switch from buffer-copy to zero-copy (default: auto)
- `rndv_thresh`: Switch from eager to rendezvous (default: auto, separate intra/inter node)

**Threshold Calculation**: UCP auto-calculates thresholds based on:
- Transport bandwidth and latency
- Memory copy bandwidth (`bcopy_bw`)
- Memory registration overhead
- Message size distribution

**Sources**: [src/ucp/core/ucp_context.h:56-90](), [src/ucp/core/ucp_context.c:161-199]()

---

### Rendezvous Protocol

The rendezvous protocol is a multi-stage protocol for large messages.

```mermaid
sequenceDiagram
    participant S as Sender
    participant R as Receiver
    
    Note over S,R: Stage 1: Request-to-Send
    S->>R: RTS (Rendezvous Request-to-Send)<br/>tag, length, sender_reqptr
    
    Note over R: Match receive request<br/>or queue as unexpected
    
    Note over R: Allocate buffer<br/>Register memory (if needed)
    
    Note over S,R: Stage 2: Ready-to-Receive
    R->>S: RTR (Ready-to-Receive)<br/>receiver_address, rkey, offset
    
    Note over S,R: Stage 3: Data Transfer
    alt RNDV_MODE_GET_ZCOPY
        S->>R: (passive) Data in memory
        R->>S: GET operations
    else RNDV_MODE_PUT_ZCOPY
        S->>R: PUT operations
    else RNDV_MODE_AM
        S->>R: AM data chunks
    end
    
    Note over S,R: Stage 4: Completion
    S->>R: ATP (Ack-to-Put)<br/>or implicit completion
    
    Note over R: Complete receive request
```

**Rendezvous Modes** (`ucp_rndv_mode_t`):
- `UCP_RNDV_MODE_GET_ZCOPY`: Receiver pulls data via GET operations
- `UCP_RNDV_MODE_PUT_ZCOPY`: Sender pushes data via PUT operations
- `UCP_RNDV_MODE_GET_PIPELINE`: Pipelined GET with staging buffers
- `UCP_RNDV_MODE_PUT_PIPELINE`: Pipelined PUT with staging buffers
- `UCP_RNDV_MODE_AM`: Active message-based transfer
- `UCP_RNDV_MODE_RKEY_PTR`: Direct memory access via rkey_ptr
- `UCP_RNDV_MODE_AUTO`: Runtime selection (default)

**Pipeline Protocol**: For GPU memory and large transfers:
- `rndv_frag_size[]`: Fragment size per memory type (default: 512KB host, 4MB GPU)
- `rndv_num_frags[]`: Number of fragments to pre-allocate (default: 128)
- Allows overlapping data movement with copy operations

**Active Message IDs for Rendezvous**:
- `UCP_AM_ID_RNDV_RTS`: Request-to-Send
- `UCP_AM_ID_RNDV_ATS`: Ack-to-Send (alternative flow)
- `UCP_AM_ID_RNDV_RTR`: Ready-to-Receive
- `UCP_AM_ID_RNDV_DATA`: Data chunks (AM mode)
- `UCP_AM_ID_RNDV_ATP`: Ack-to-Put (completion)

**Sources**: [src/ucp/core/ucp_context.h:79-83](), [src/ucp/rndv/](), [Diagram 7 from overview]()

---

## Request Management

UCP uses an asynchronous request-based model for all communication operations.

```mermaid
graph TB
    subgraph "Request Structure"
        REQ["ucp_request_t"]
        
        send["send union<br/>Send operation state"]
        recv["recv union<br/>Receive operation state"]
        
        flags["flags<br/>Request state flags"]
        status["status<br/>Completion status"]
        
        REQ --> send
        REQ --> recv
        REQ --> flags
        REQ --> status
    end
    
    subgraph "Request Send State"
        ep["ep: ucp_ep_h"]
        lane["lane: ucp_lane_index_t"]
        buffer["buffer: void*"]
        length["length: size_t"]
        datatype["datatype: ucp_datatype_t"]
        uct_func["uct.func<br/>Progress function"]
        
        send --> ep
        send --> lane
        send --> buffer
        send --> length
        send --> datatype
        send --> uct_func
    end
    
    subgraph "Request Lifecycle"
        ALLOC["ucp_request_get()<br/>From worker mpool"]
        INIT["ucp_request_send_state_init()"]
        SEND["ucp_request_send()<br/>Enqueue or send"]
        PROGRESS["Progress function<br/>Drive to completion"]
        COMPLETE["ucp_request_complete()"]
        RELEASE["ucp_request_release()"]
        
        ALLOC --> INIT
        INIT --> SEND
        SEND --> PROGRESS
        PROGRESS --> COMPLETE
        COMPLETE --> RELEASE
    end
    
    subgraph "Completion Models"
        INLINE["Inline completion<br/>Status returned"]
        PTR["Pointer returned<br/>Check later"]
        CALLBACK["Callback invoked<br/>Async notification"]
        
        PROGRESS --> INLINE
        PROGRESS --> PTR
        PROGRESS --> CALLBACK
    end
```

**Request Flags**:
- `UCP_REQUEST_FLAG_COMPLETED`: Request finished
- `UCP_REQUEST_FLAG_RELEASED`: User called release
- `UCP_REQUEST_FLAG_CALLBACK`: Has completion callback
- `UCP_REQUEST_FLAG_RECV_TAG`: Tagged receive
- `UCP_REQUEST_FLAG_RECV_AM`: Active message receive
- `UCP_REQUEST_FLAG_SEND`: Send operation

**Memory Pool**: Requests allocated from worker's memory pool (`ucp_worker_t.req_mp`)

**Progress Functions**: Each request type has a progress function:
- `ucp_proto_progress_am_bcopy()`: Active message bcopy
- `ucp_proto_progress_rma_zcopy()`: RMA zero-copy  
- `ucp_rndv_progress_rts()`: Rendezvous RTS
- `ucp_wireup_msg_progress()`: Wireup messages

**Sources**: [src/ucp/core/ucp_request.h](), [src/ucp/core/ucp_request.inl](), [Diagram 7 from overview]()

---

## Connection Manager (CM) Integration

UCP supports CM-based connection establishment for client-server workflows.

```mermaid
graph TB
    subgraph "Client-Server with CM"
        LISTENER["ucp_listener_create()<br/>Bind to sockaddr"]
        CLIENT["Client: ucp_ep_create()<br/>UCP_EP_PARAMS_FLAGS_CLIENT_SERVER"]
        
        LISTENER --> CONN_REQ["ucp_conn_request_h<br/>Incoming connection"]
        CONN_REQ --> ACCEPT["ucp_ep_create()<br/>UCP_EP_PARAM_FIELD_CONN_REQUEST"]
        
        CLIENT --> CM_LANE["CM Lane<br/>UCT CM endpoint"]
        ACCEPT --> CM_LANE
    end
    
    subgraph "CM Wireup Flow"
        CM_CONNECT["uct_ep_connect_to_ep_v2()<br/>UCT CM connect"]
        PRIV_DATA["Private Data<br/>ucp_wireup_sockaddr_data"]
        CM_CONNECTED["CM Connected<br/>UCP_EP_FLAG_LOCAL_CONNECTED"]
        WIREUP_EXCHANGE["Wireup message exchange<br/>Select transports"]
        FINAL_CONFIG["Final EP configuration<br/>Multiple lanes"]
        
        CM_CONNECT --> PRIV_DATA
        PRIV_DATA --> CM_CONNECTED
        CM_CONNECTED --> WIREUP_EXCHANGE
        WIREUP_EXCHANGE --> FINAL_CONFIG
    end
    
    subgraph "Private Data Structure"
        sa_data_base["ucp_wireup_sockaddr_data_base_t"]
        err_mode["err_mode<br/>Error handling"]
        addr_mode["addr_mode<br/>Address mode"]
        ep_id["ep_id<br/>Remote endpoint ID"]
        dev_addr["Device address<br/>CM transport"]
        
        sa_data_base --> err_mode
        sa_data_base --> addr_mode
        sa_data_base --> ep_id
        sa_data_base --> dev_addr
    end
    
    CLIENT --> CM_CONNECT
    ACCEPT --> CM_CONNECT
```

**CM Workflow**:
1. **Server**: `ucp_listener_create()` creates listener on sockaddr
2. **Client**: `ucp_ep_create()` with `UCP_EP_PARAMS_FLAGS_CLIENT_SERVER` flag
3. **UCT CM Connect**: Initial connection via `uct_ep_connect_to_ep_v2()`
4. **Private Data Exchange**: UCP address and configuration in CM private data
5. **Wireup**: Complete transport selection and lane configuration
6. **Multi-Lane**: Final configuration may use multiple transports beyond CM

**CM Lane**: Special lane type (`UCP_LANE_TYPE_CM`) holds the connection manager endpoint:
- Used for initial connection only
- May be replaced or supplemented by other lanes after wireup
- `cm_idx` in `ucp_ep_ext_t` stores CM resource index

**Sources**: [src/ucp/wireup/wireup_cm.c:1-800](), [src/ucp/wireup/wireup_cm.h:1-67](), [src/ucp/core/ucp_listener.c]()

---

## Key API Functions

### Initialization and Cleanup

| Function | Purpose | Key Parameters |
|----------|---------|----------------|
| `ucp_init()` | Initialize UCP context | `ucp_params_t` (features, request_size) |
| `ucp_cleanup()` | Cleanup UCP context | `ucp_context_h` |
| `ucp_worker_create()` | Create worker | `ucp_worker_params_t` (thread_mode, cpu_mask) |
| `ucp_worker_destroy()` | Destroy worker | `ucp_worker_h` |

### Endpoint Management

| Function | Purpose | Key Parameters |
|----------|---------|----------------|
| `ucp_ep_create()` | Create endpoint | `ucp_ep_params_t` (address, sockaddr, flags) |
| `ucp_ep_close_nbx()` | Close endpoint (async) | `ucp_ep_h`, flags |
| `ucp_ep_flush()` | Flush pending operations | `ucp_ep_h` |

### Communication Operations

| Function | Purpose | Protocol |
|----------|---------|----------|
| `ucp_tag_send_nbx()` | Send tagged message | Eager or Rendezvous |
| `ucp_tag_recv_nbx()` | Receive tagged message | Tag matching |
| `ucp_stream_send()` | Send stream data | Ordered delivery |
| `ucp_stream_recv_nbx()` | Receive stream data | FIFO ordering |
| `ucp_am_send_nbx()` | Send active message | User-defined handler |
| `ucp_put_nbx()` | RMA put | Zero-copy PUT |
| `ucp_get_nbx()` | RMA get | Zero-copy GET |
| `ucp_atomic_op_nbx()` | Atomic operation | AMO32/AMO64 |

**Sources**: [src/ucp/api/ucp.h:1-2000]()

---

## Configuration Parameters

Key UCP configuration parameters (environment variables or config file):

| Parameter | Default | Description |
|-----------|---------|-------------|
| `UCX_BCOPY_THRESH` | auto | Threshold for buffer copy protocol |
| `UCX_RNDV_THRESH` | auto | Threshold for rendezvous (intra/inter) |
| `UCX_ZCOPY_THRESH` | auto | Threshold for zero-copy |
| `UCX_RNDV_SCHEME` | auto | Rendezvous mode selection |
| `UCX_MAX_EAGER_RAILS` | 1 | Max lanes for eager messages |
| `UCX_MAX_RNDV_RAILS` | 2 | Max lanes for rendezvous |
| `UCX_MAX_RMA_RAILS` | 1 | Max lanes for RMA |
| `UCX_TM_THRESH` | 1024 | Tag offload threshold |
| `UCX_UNIFIED_MODE` | n | Homogeneous environment optimizations |
| `UCX_CM_USE_ALL_DEVICES` | y | Use all devices in CM mode |
| `UCX_PROTO_ENABLE` | y | Enable protocol selection |

**Sources**: [src/ucp/core/ucp_context.c:161-452]()

---

