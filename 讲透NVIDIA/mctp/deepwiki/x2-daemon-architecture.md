<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/mctp · extra page Daemon Architecture · fetched 2026-10-26 -->

# Daemon Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/mctpd-util.h](src/mctpd-util.h)
- [src/mctpd.c](src/mctpd.c)

</details>



## Purpose and Scope

This page documents the internal architecture of the `mctpd` daemon, including its event-driven design, core data structures, and component interactions. This covers the fundamental building blocks and design patterns used throughout the daemon implementation.

For information about endpoint discovery and EID assignment workflows, see [Endpoint Management](#2.1.2). For configuration file options, see [Configuration](#2.1.3). For details on the D-Bus interfaces exposed by the daemon, see [D-Bus Interface](#4).

---

## Event-Driven Architecture

The daemon is built on a centralized event loop provided by systemd's `sd_event` library. All asynchronous operations—including D-Bus method calls, Netlink monitoring, and MCTP socket I/O—are coordinated through this event loop using callback-based handlers.

### Event Loop Structure

```mermaid
graph TB
    EventLoop["sd_event Loop<br/>(ctx->event)"]
    
    subgraph "Event Sources"
        DBus["D-Bus Socket<br/>(ctx->bus)"]
        Netlink["Netlink Monitor Socket<br/>cb_listen_monitor()"]
        MCTP["MCTP Control Socket<br/>cb_listen_control_msg()"]
        Timers["Recovery Timers<br/>(peer->recovery.source)"]
        BridgeTimer["Bridge Settle Timer<br/>(peer->bridge_settle_timer)"]
    end
    
    subgraph "Callback Handlers"
        MonitorCB["cb_listen_monitor()<br/>Process netlink changes"]
        ControlCB["cb_listen_control_msg()<br/>Handle control messages"]
        RecoveryCB["Recovery callback<br/>peer_endpoint_recover()"]
        BridgeCB["Bridge settle callback<br/>Populate bridged endpoints"]
        DBusCB["D-Bus method handlers<br/>(method_*() functions)"]
    end
    
    EventLoop --> DBus
    EventLoop --> Netlink
    EventLoop --> MCTP
    EventLoop --> Timers
    EventLoop --> BridgeTimer
    
    DBus --> DBusCB
    Netlink --> MonitorCB
    MCTP --> ControlCB
    Timers --> RecoveryCB
    BridgeTimer --> BridgeCB
```

The event loop is created during daemon initialization and runs indefinitely until shutdown. Event sources register file descriptors and timers, and the loop dispatches callbacks when events occur.

**Sources:** [src/mctpd.c:224-226](), [src/mctpd.c:1422-1482](), [src/mctpd.c:1595-1704]()

---

## Core Data Structures

The daemon maintains four primary data structures that represent the state of the MCTP network:

### Context Structure (`struct ctx`)

The global context structure holds all daemon-wide state, including configuration, event loop handles, and collections of networks, peers, and interfaces.

```mermaid
graph LR
    CTX["struct ctx"]
    
    CTX --> Event["sd_event *event<br/>Main event loop"]
    CTX --> Bus["sd_bus *bus<br/>D-Bus connection"]
    CTX --> NL["mctp_nl *nl<br/>Netlink interface"]
    CTX --> Config["Configuration<br/>dyn_eid_min/max<br/>mctp_timeout<br/>default_role"]
    CTX --> Peers["struct peer **peers<br/>num_peers"]
    CTX --> Nets["struct net **nets<br/>num_nets"]
    CTX --> UUID["uuid[16]<br/>Daemon UUID"]
    CTX --> Cache["cache_entries<br/>Routing info cache"]
```

Key fields in `struct ctx`:

| Field | Type | Purpose |
|-------|------|---------|
| `event` | `sd_event *` | Main event loop handle |
| `bus` | `sd_bus *` | D-Bus system bus connection |
| `nl` | `mctp_nl *` | Netlink abstraction for kernel interface |
| `peers` | `struct peer **` | Dynamic array of all known endpoints |
| `num_peers` | `size_t` | Current number of peers |
| `nets` | `struct net **` | Array of network structures |
| `num_nets` | `size_t` | Number of networks |
| `dyn_eid_min/max` | `mctp_eid_t` | EID allocation range |
| `mctp_timeout` | `uint64_t` | Timeout in microseconds for MCTP responses |
| `iid` | `uint8_t` | Next Instance ID for control messages |
| `default_role` | `enum endpoint_role` | Default operational mode |

**Sources:** [src/mctpd.c:224-271]()

### Network Structure (`struct net`)

Each network structure represents an MCTP network domain and maintains an EID-to-peer mapping table.

```mermaid
graph TB
    NET["struct net"]
    
    NET --> NetID["uint32_t net<br/>Network ID"]
    NET --> CTX["struct ctx *ctx<br/>Back-pointer"]
    NET --> Peers["struct peer *peers[256]<br/>EID lookup table"]
    NET --> Slot["sd_bus_slot *slot<br/>D-Bus object slot"]
    NET --> Path["char *path<br/>D-Bus object path"]
```

The `peers` array provides O(1) lookup of endpoints by EID within a network. Array indices correspond to EID values (0-255), with `NULL` entries indicating unused EIDs.

**Sources:** [src/mctpd.c:87-96](), [src/mctpd.c:349-356](), [src/mctpd.c:377-385]()

### Link Structure (`struct link`)

Link structures represent physical MCTP interfaces (e.g., `mctpi2c1`, `mctpusb0`) with their operational state and D-Bus registration.

```mermaid
graph TB
    LINK["struct link"]
    
    LINK --> IfIndex["int ifindex<br/>Kernel interface index"]
    LINK --> Role["enum endpoint_role<br/>Bus owner or endpoint"]
    LINK --> Published["bool published<br/>D-Bus visibility"]
    LINK --> Path["char *path<br/>D-Bus object path"]
    LINK --> Slots["D-Bus slots<br/>slot_iface<br/>slot_busowner<br/>slot_service_readiness"]
    LINK --> CTX["struct ctx *ctx<br/>Back-pointer"]
    LINK --> State["service_state<br/>Starting/Enabled"]
```

Each link has an associated operational role:
- **Bus Owner**: Actively assigns EIDs to discovered endpoints
- **Endpoint**: Passively accepts EID assignments from a remote bus owner

**Sources:** [src/mctpd.c:133-150](), [src/mctpd.c:103-131]()

### Peer Structure (`struct peer`)

Peer structures represent individual MCTP endpoints, both local and remote, with their routing information, properties, and recovery state.

```mermaid
graph TB
    PEER["struct peer"]
    
    subgraph "Identification"
        EID["mctp_eid_t eid"]
        NET["uint32_t net"]
        UUID["uint8_t *uuid<br/>(16 bytes)"]
    end
    
    subgraph "Routing"
        Phys["dest_phys phys<br/>Physical address"]
        State["enum state<br/>REMOTE or LOCAL"]
        HaveNeigh["bool have_neigh"]
        HaveRoute["bool have_route"]
        MTU["uint32_t mtu"]
    end
    
    subgraph "Properties"
        Types["uint8_t *message_types<br/>num_message_types"]
        EPType["uint8_t endpoint_type"]
        MedSpec["uint8_t medium_spec"]
    end
    
    subgraph "Bridge Support"
        PoolSize["uint8_t pool_size"]
        PoolStart["uint8_t pool_start"]
        IgnoreEIDs["mctp_eid_t *ignore_eids<br/>num_ignore_eids"]
        RoutingTable["struct get_routing_table_entry"]
    end
    
    subgraph "Recovery"
        Degraded["bool degraded"]
        Recovery["struct recovery<br/>Timer and retry state"]
    end
    
    subgraph "D-Bus"
        Published["bool published"]
        Slots["Multiple sd_bus_slot*"]
        Path["char *path"]
    end
    
    PEER --> EID
    PEER --> NET
    PEER --> UUID
    PEER --> Phys
    PEER --> State
    PEER --> Types
    PEER --> PoolSize
    PEER --> Degraded
    PEER --> Published
```

Key peer states:
- **REMOTE**: Regular endpoint reachable via physical addressing
- **LOCAL**: Represents a local interface's own EID

**Sources:** [src/mctpd.c:152-222]()

---

## Data Structure Relationships

```mermaid
graph TB
    CTX["struct ctx<br/>(Global context)"]
    
    NET1["struct net<br/>network 1"]
    NET2["struct net<br/>network N"]
    
    LINK1["struct link<br/>mctpi2c1"]
    LINK2["struct link<br/>mctpusb0"]
    
    PEER1["struct peer<br/>eid=8, net=1"]
    PEER2["struct peer<br/>eid=9, net=1"]
    PEER3["struct peer<br/>eid=8, net=2"]
    
    CTX -->|"nets[]"| NET1
    CTX -->|"nets[]"| NET2
    CTX -->|"peers[]"| PEER1
    CTX -->|"peers[]"| PEER2
    CTX -->|"peers[]"| PEER3
    CTX -->|"nl userdata"| LINK1
    CTX -->|"nl userdata"| LINK2
    
    NET1 -->|"peers[8]"| PEER1
    NET1 -->|"peers[9]"| PEER2
    NET2 -->|"peers[8]"| PEER3
    
    PEER1 -->|"ctx"| CTX
    PEER2 -->|"ctx"| CTX
    PEER3 -->|"ctx"| CTX
    
    NET1 -->|"ctx"| CTX
    NET2 -->|"ctx"| CTX
    
    LINK1 -->|"ctx"| CTX
    LINK2 -->|"ctx"| CTX
    
    LINK1 -.->|"ifindex"| PEER1
    LINK2 -.->|"ifindex"| PEER3
```

**Key relationships:**
- `ctx` contains arrays of all `peer` and `net` structures
- Each `net` has an EID lookup table pointing to `peer` structures
- `link` structures are stored as userdata in the `mctp_nl` (netlink) context
- All structures maintain back-pointers to `ctx` for accessing global state
- Peers reference their network by ID, not by pointer

**Sources:** [src/mctpd.c:87-96](), [src/mctpd.c:152-222](), [src/mctpd.c:224-271]()

---

## Component Interaction Patterns

### Callback Registration Pattern

The daemon extensively uses callback-based event handling. Components register callbacks with appropriate event sources:

```mermaid
graph LR
    subgraph "Registration Functions"
        ListenMon["listen_monitor()"]
        ListenCtrl["listen_control_msg()"]
        AddDBus["sd_bus_add_object_vtable()"]
    end
    
    subgraph "Event Sources"
        NetlinkFD["Netlink FD"]
        MctpFD["MCTP Socket FD"]
        DBusBus["D-Bus Connection"]
    end
    
    subgraph "Callbacks"
        CBMon["cb_listen_monitor()"]
        CBCtrl["cb_listen_control_msg()"]
        MethodCB["method_*()"]
    end
    
    ListenMon -->|"sd_event_add_io()"| NetlinkFD
    NetlinkFD --> CBMon
    
    ListenCtrl -->|"sd_event_add_io()"| MctpFD
    MctpFD --> CBCtrl
    
    AddDBus --> DBusBus
    DBusBus --> MethodCB
```

**Netlink Monitoring:** [src/mctpd.c:1692-1704]()
- `listen_monitor()` registers `cb_listen_monitor()` with the netlink socket
- Callback processes interface, address, and route changes

**MCTP Control Socket:** [src/mctpd.c:1422-1482]()
- `listen_control_msg()` registers `cb_listen_control_msg()` with MCTP socket
- Callback dispatches to specific control message handlers

**D-Bus Methods:** Various method handlers throughout [src/mctpd.c]()
- vtable arrays define method signatures and handlers
- Methods registered per object path (endpoints, networks, links)

**Sources:** [src/mctpd.c:1422-1482](), [src/mctpd.c:1595-1690](), [src/mctpd.c:1692-1704]()

### Peer Lifecycle Management

```mermaid
graph TB
    Start["Endpoint Discovered"]
    
    AddPeer["add_peer()<br/>Create peer structure<br/>Add to ctx->peers[]<br/>Add to net->peers[eid]"]
    
    SetupPeer["setup_added_peer()<br/>Add routes/neighbors<br/>Query properties"]
    
    QueryProps["query_peer_properties()<br/>Get message types<br/>Get UUID"]
    
    PublishPeer["publish_peer()<br/>Create D-Bus objects<br/>Emit signals"]
    
    Active["Active Peer"]
    
    Degrade["Peer Degraded<br/>(Communication failure)"]
    
    Recovery["peer_endpoint_recover()<br/>Periodic retry"]
    
    Remove["remove_peer()<br/>Unpublish D-Bus<br/>Delete routes<br/>Free memory"]
    
    End["Peer Removed"]
    
    Start --> AddPeer
    AddPeer --> SetupPeer
    SetupPeer --> QueryProps
    QueryProps --> PublishPeer
    PublishPeer --> Active
    
    Active -->|"Transport error"| Degrade
    Degrade -->|"Retry timer"| Recovery
    Recovery -->|"Success"| Active
    Recovery -->|"Permanent failure"| Remove
    Active -->|"Remove request"| Remove
    Remove --> End
```

**Key functions:**
- `add_peer()` [src/mctpd.c:2174-2223](): Allocates and initializes peer structure
- `setup_added_peer()` [src/mctpd.c:3368-3398](): Configures routing and queries properties
- `publish_peer()` [src/mctpd.c:3526-3633](): Exposes peer to D-Bus
- `remove_peer()` [src/mctpd.c:2285-2374](): Cleanup and deallocation
- `peer_endpoint_recover()` [src/mctpd.c:3951-4036](): Recovery state machine

**Sources:** [src/mctpd.c:2174-2223](), [src/mctpd.c:2285-2374](), [src/mctpd.c:3266-3398](), [src/mctpd.c:3526-3633](), [src/mctpd.c:3951-4036]()

### Control Message Dispatch

```mermaid
graph TB
    Recv["cb_listen_control_msg()<br/>EPOLLIN event on control socket"]
    
    ReadMsg["read_message()<br/>Receive from socket"]
    
    Dispatch{{"Switch on<br/>ctrl_msg->command_code"}}
    
    GetEID["handle_control_get_endpoint_id()"]
    SetEID["handle_control_set_endpoint_id()"]
    GetUUID["handle_control_get_endpoint_uuid()"]
    GetTypes["handle_control_get_message_type_support()"]
    GetVer["handle_control_get_version_support()"]
    Resolve["handle_control_resolve_endpoint_id()"]
    Notify["handle_control_discovery_notify()"]
    Routing["handle_control_routing_info_update()"]
    Unsup["handle_control_unsupported()"]
    
    Reply["reply_message()<br/>Send response"]
    
    Recv --> ReadMsg
    ReadMsg --> Dispatch
    
    Dispatch -->|"GET_ENDPOINT_ID"| GetEID
    Dispatch -->|"SET_ENDPOINT_ID"| SetEID
    Dispatch -->|"GET_ENDPOINT_UUID"| GetUUID
    Dispatch -->|"GET_MESSAGE_TYPE_SUPPORT"| GetTypes
    Dispatch -->|"GET_VERSION_SUPPORT"| GetVer
    Dispatch -->|"RESOLVE_ENDPOINT_ID"| Resolve
    Dispatch -->|"DISCOVERY_NOTIFY"| Notify
    Dispatch -->|"ROUTING_INFO_UPDATE"| Routing
    Dispatch -->|"Unknown"| Unsup
    
    GetEID --> Reply
    SetEID --> Reply
    GetUUID --> Reply
    GetTypes --> Reply
    GetVer --> Reply
    Resolve --> Reply
    Notify --> Reply
    Routing --> Reply
    Unsup --> Reply
```

The control message callback [src/mctpd.c:1323-1420]() implements a dispatch table for all MCTP control protocol commands. Each handler processes the request and calls `reply_message()` or `reply_message_phys()` to send the response.

**Sources:** [src/mctpd.c:1323-1420](), [src/mctpd.c:666-694](), [src/mctpd.c:641-663]()

---

## Memory Management Patterns

### Dynamic Arrays

The daemon uses dynamically-sized arrays for peers and networks that grow and shrink as endpoints are discovered or removed:

**Peer array growth** [src/mctpd.c:2203-2209]():
```c
tmp = realloc(ctx->peers, (ctx->num_peers + 1) * sizeof(*ctx->peers));
ctx->peers = tmp;
ctx->peers[ctx->num_peers] = peer;
ctx->num_peers++;
```

**Peer array shrinkage** [src/mctpd.c:2352-2369]():
```c
ctx->num_peers--;
memmove(ctx->peers + idx, ctx->peers + idx + 1,
        (ctx->num_peers - idx) * sizeof(struct peer *));
tmp = realloc(ctx->peers, ctx->num_peers * sizeof(struct peer *));
```

### Deferred Free Pattern

The `dfree()` function [src/mctpd.c:479-501]() provides automatic memory cleanup using the event loop:

```mermaid
graph LR
    Alloc["malloc() buffer"]
    Return["Return pointer<br/>wrapped in dfree()"]
    Use["Function uses pointer<br/>for logging, etc."]
    Defer["Event loop defer callback"]
    Free["free() buffer"]
    
    Alloc --> Return
    Return --> Use
    Use --> Defer
    Defer --> Free
```

This pattern is used for temporary string buffers in logging functions like `dest_phys_tostr()` [src/mctpd.c:409-422]() and `peer_tostr()` [src/mctpd.c:444-456](). The buffer remains valid until the next event loop iteration, avoiding manual memory management in callers.

**Sources:** [src/mctpd.c:479-501](), [src/mctpd.c:409-422](), [src/mctpd.c:444-456]()

---

## Socket and Network I/O Patterns

### Request-Response Pattern with Timeout

The daemon implements synchronous request-response communication with endpoints using a temporary event loop:

```mermaid
graph TB
    Create["endpoint_query_addr()<br/>Create temporary socket"]
    
    Send["sendto()<br/>Send control request"]
    
    Wait["wait_fd_timeout()<br/>Create temporary event loop<br/>Register socket + timer"]
    
    Loop["sd_event_loop()<br/>Wait for response or timeout"]
    
    Events{{"Event"}}
    
    Data["EPOLLIN<br/>Receive response"]
    Error["EPOLLERR<br/>Read error queue"]
    Timeout["Timer expires"]
    
    Close["close(socket)<br/>Return result"]
    
    Create --> Send
    Send --> Wait
    Wait --> Loop
    Loop --> Events
    
    Events -->|"Data"| Data
    Events -->|"Error"| Error
    Events -->|"Timeout"| Timeout
    
    Data --> Close
    Error --> Close
    Timeout --> Close
```

**Key functions:**
- `endpoint_query_addr()` [src/mctpd.c:1916-2033](): Base query function
- `endpoint_query_peer()` [src/mctpd.c:2037-2058](): Query by EID
- `endpoint_query_phys()` [src/mctpd.c:2062-2088](): Query by physical address
- `wait_fd_timeout()` [src/mctpd.c:522-548](): Synchronous wait with timeout

This pattern allows the daemon to make synchronous control protocol requests without blocking the main event loop.

**Sources:** [src/mctpd.c:1916-2033](), [src/mctpd.c:522-548](), [src/mctpd.c:2037-2058](), [src/mctpd.c:2062-2088]()

### Error Queue Processing

The daemon processes MCTP transport errors through the kernel's error queue mechanism:

```mermaid
graph TB
    Enable["setsockopt(MCTP_OPT_ENABLE_ERRQUEUE)"]
    
    Event["EPOLLERR event on socket"]
    
    Read["read_mctp_error_queue()<br/>recvmsg(MSG_ERRQUEUE)"]
    
    Extract["Extract mctp_error structure<br/>from control message"]
    
    Log["log_mctp_error()<br/>Emit TransportError D-Bus signal"]
    
    Enable --> Event
    Event --> Read
    Read --> Extract
    Extract --> Log
```

The error queue is enabled on control sockets [src/mctpd.c:1456-1467]() and query sockets [src/mctpd.c:1949-1955](). When errors occur, the `read_mctp_error_queue()` function [src/mctpd.c:1516-1592]() processes them and emits D-Bus signals for monitoring.

**Sources:** [src/mctpd.c:1456-1467](), [src/mctpd.c:1516-1592](), [src/mctpd.c:1484-1514]()

---

## Initialization and Shutdown

### Daemon Startup Sequence

```mermaid
graph TB
    Main["main()"]
    
    ParseArgs["Parse command line<br/>arguments"]
    
    ParseConf["parse_conf()<br/>Load /etc/mctpd.conf"]
    
    InitEvent["sd_event_default()<br/>Create event loop"]
    
    InitBus["sd_bus_default_system()<br/>Connect to D-Bus"]
    
    InitNL["mctp_nl_new()<br/>Create netlink context"]
    
    SetupNets["setup_nets()<br/>Discover interfaces<br/>Create link structures"]
    
    ListenMon["listen_monitor()<br/>Register netlink callback"]
    
    ListenCtrl["listen_control_msg()<br/>Register control socket"]
    
    ClaimName["sd_bus_request_name()<br/>au.com.codeconstruct.MCTP1"]
    
    EventLoop["sd_event_loop()<br/>Run until termination"]
    
    Main --> ParseArgs
    ParseArgs --> ParseConf
    ParseConf --> InitEvent
    InitEvent --> InitBus
    InitBus --> InitNL
    InitNL --> SetupNets
    SetupNets --> ListenMon
    ListenMon --> ListenCtrl
    ListenCtrl --> ClaimName
    ClaimName --> EventLoop
```

During initialization, the daemon:
1. Parses configuration to determine operational mode and EID ranges
2. Creates the event loop and connects to D-Bus
3. Initializes netlink monitoring for kernel MCTP state
4. Discovers existing interfaces and creates link objects
5. Registers event sources (netlink, control socket)
6. Claims the D-Bus service name
7. Enters the main event loop

**Sources:** [src/mctpd.c:4605-4950]()

---

## Design Principles

### Separation of Concerns

The architecture cleanly separates:
- **Transport Layer**: Netlink and MCTP socket operations ([src/mctp-netlink.c]())
- **Protocol Layer**: Control message encoding/decoding ([src/mctp-control-spec.h]())
- **Management Layer**: Peer lifecycle and state management ([src/mctpd.c]())
- **Interface Layer**: D-Bus API exposure ([src/mctpd.c]() vtables)

### Asynchronous-First Design

All I/O operations integrate with the event loop, preventing blocking:
- D-Bus method calls return immediately and use D-Bus's async reply mechanism
- Netlink monitoring uses non-blocking sockets with callbacks
- Long-running operations (discovery, recovery) use timers

### State Machine Approach

Complex workflows are implemented as state machines:
- **Peer recovery** [src/mctpd.c:3951-4036](): Tracks retry count and exponential backoff
- **Bridge endpoint discovery** [src/mctpd.c:3685-3793](): Polls bridged endpoints with settle timer
- **Link service readiness** [src/mctpd.c:146-149](): Starting → Enabled state transition

**Sources:** [src/mctpd.c:3951-4036](), [src/mctpd.c:3685-3793](), [src/mctpd.c:146-149]()

---

