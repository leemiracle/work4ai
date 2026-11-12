<!-- source: DeepWiki mcp.deepwiki.com · repo Mellanox/libvma · page 3 Network Layer · fetched 2026-11-11 -->

# Network Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/vma/dev/net_device_table_mgr.cpp](src/vma/dev/net_device_table_mgr.cpp)
- [src/vma/dev/net_device_table_mgr.h](src/vma/dev/net_device_table_mgr.h)
- [src/vma/dev/net_device_val.cpp](src/vma/dev/net_device_val.cpp)
- [src/vma/dev/net_device_val.h](src/vma/dev/net_device_val.h)
- [src/vma/infra/sender.h](src/vma/infra/sender.h)
- [src/vma/proto/dst_entry.cpp](src/vma/proto/dst_entry.cpp)
- [src/vma/proto/dst_entry.h](src/vma/proto/dst_entry.h)
- [src/vma/proto/dst_entry_tcp.cpp](src/vma/proto/dst_entry_tcp.cpp)
- [src/vma/proto/dst_entry_tcp.h](src/vma/proto/dst_entry_tcp.h)
- [src/vma/proto/dst_entry_udp.cpp](src/vma/proto/dst_entry_udp.cpp)
- [src/vma/proto/dst_entry_udp.h](src/vma/proto/dst_entry_udp.h)
- [src/vma/proto/igmp_handler.cpp](src/vma/proto/igmp_handler.cpp)
- [src/vma/proto/neighbour.cpp](src/vma/proto/neighbour.cpp)
- [src/vma/proto/neighbour.h](src/vma/proto/neighbour.h)
- [src/vma/proto/netlink_socket_mgr.h](src/vma/proto/netlink_socket_mgr.h)
- [src/vma/proto/route_table_mgr.cpp](src/vma/proto/route_table_mgr.cpp)
- [src/vma/proto/route_table_mgr.h](src/vma/proto/route_table_mgr.h)
- [src/vma/proto/rule_table_mgr.cpp](src/vma/proto/rule_table_mgr.cpp)
- [src/vma/proto/rule_table_mgr.h](src/vma/proto/rule_table_mgr.h)
- [src/vma/proto/rule_val.cpp](src/vma/proto/rule_val.cpp)
- [src/vma/proto/rule_val.h](src/vma/proto/rule_val.h)
- [src/vma/util/utils.cpp](src/vma/util/utils.cpp)
- [src/vma/util/utils.h](src/vma/util/utils.h)

</details>



The Network Layer in VMA (Versatile Message Accelerator) is responsible for managing network devices, handling routing decisions, resolving network addresses, and facilitating high-performance packet transmission. It sits between the [Socket Layer](#2) and the [Hardware Abstraction Layer](#4), providing critical networking functionality while enabling RDMA/InfiniBand acceleration.

## Component Overview

The Network Layer consists of four main subsystems:

```mermaid
graph TD
    subgraph "Network Layer"
        ND["Network Device Management"]
        RS["Routing Subsystem"]
        NB["Neighbor Discovery"]
        DE["Destination Entry System"]
    end
    
    Socket["Socket Layer"] --> ND
    Socket --> RS
    Socket --> NB
    Socket --> DE
    
    ND --> HAL["Hardware Abstraction Layer"]
    RS --> HAL
    NB --> HAL
    DE --> HAL
    
    ND <--> RS
    ND <--> NB
    RS <--> DE
    NB <--> DE
```

Sources:
- [src/vma/dev/net_device_table_mgr.h:28-104]()
- [src/vma/proto/route_table_mgr.h:32-60]()
- [src/vma/proto/neighbour.h:32-101]()
- [src/vma/proto/dst_entry.h:44-162]()

## Network Device Management

The Network Device Management subsystem discovers, initializes, and manages network interfaces that VMA can use for acceleration. It maintains a database of available devices and their capabilities.

### Core Components

```mermaid
classDiagram
    class net_device_val {
        +get_if_idx(): int
        +get_local_addr(): in_addr_t
        +get_l2_address(): L2_address*
        +get_state(): state
        +reserve_ring(): ring*
        +release_ring(): int
    }
    
    class net_device_val_eth {
        +get_vlan(): uint16_t
    }
    
    class net_device_val_ib {
        +get_pkey(): uint16_t
    }
    
    class net_device_table_mgr {
        +get_net_device_val(in_addr_t): net_device_val*
        +get_net_device_val(int): net_device_val*
        +update_tbl(): void
        +global_ring_poll_and_process_element(): int
    }
    
    net_device_val <|-- net_device_val_eth
    net_device_val <|-- net_device_val_ib
    net_device_table_mgr o-- "many" net_device_val: manages
```

Sources:
- [src/vma/dev/net_device_val.h:156-294]()
- [src/vma/dev/net_device_table_mgr.h:28-104]()

### Device Discovery Process

```mermaid
sequenceDiagram
    participant Netlink as "Netlink Socket"
    participant NDTM as "net_device_table_mgr"
    participant NDV as "net_device_val"
    participant IBCtx as "ib_ctx_handler_collection"
    
    NDTM->>Netlink: Request interface information (RTM_GETLINK)
    Netlink-->>NDTM: Interface data
    
    loop For each interface
        NDTM->>NDTM: Check if interface exists in map
        alt New interface
            NDTM->>NDV: Create new net_device_val
            
            alt Interface type
                NDV->>NDV: Create net_device_val_eth
                NDV->>NDV: Create net_device_val_ib
            end
            
            NDV->>NDTM: Check state (valid/invalid)
            alt Valid device
                NDV->>IBCtx: Query IB context
                NDV->>NDV: Set slaves array
                NDV->>NDV: Configure L2 addressing
                NDTM->>NDTM: Add to device map
            end
        end
    end
```

Sources:
- [src/vma/dev/net_device_table_mgr.cpp:148-261]()
- [src/vma/dev/net_device_val.cpp:155-286]()

The network device management system uses netlink sockets to discover network interfaces, creating `net_device_val` objects for each valid device. Each object represents an interface that can be used for offloaded operations, maintaining information about:

- IP addresses assigned to the interface
- L2 (MAC/link) addresses 
- Interface state and capabilities
- Bond configurations (for bonded interfaces)
- Associated InfiniBand contexts

Each network device also manages "rings" - abstractions of hardware queues used for packet transmission and reception.

```
Interface States:
- DOWN: Interface exists but is down
- UP: Interface is up but not running
- RUNNING: Interface is fully operational
- INVALID: Interface cannot be used for offloading
```

Sources:
- [src/vma/dev/net_device_val.h:159-164]()
- [src/vma/dev/net_device_val.cpp:539-642]()

## Routing Subsystem

The Routing Subsystem determines the appropriate next-hop and outgoing interface for packet transmission based on destination address and other parameters.

### Core Components

```mermaid
classDiagram
    class route_table_mgr {
        +route_resolve(): bool
        +create_new_entry(): route_entry*
        +update_entry(): void
    }
    
    class rule_table_mgr {
        +rule_resolve(): bool
        +create_new_entry(): rule_entry*
    }
    
    class route_entry {
        +get_val(): bool
        +get_key(): route_rule_table_key
    }
    
    class route_val {
        +get_dst_addr(): in_addr_t
        +get_src_addr(): in_addr_t
        +get_gw_addr(): in_addr_t
        +get_if_index(): int
        +get_mtu(): uint16_t
    }
    
    route_table_mgr o-- "many" route_entry: manages
    route_entry o-- route_val: contains
    route_table_mgr --> rule_table_mgr: uses
```

Sources:
- [src/vma/proto/route_table_mgr.h:32-60]()
- [src/vma/proto/rule_table_mgr.h:21-28]()

### Route Resolution Process

```mermaid
sequenceDiagram
    participant DE as "dst_entry"
    participant RTM as "route_table_mgr"
    participant RM as "rule_table_mgr"
    participant NL as "Netlink Socket"
    
    DE->>RTM: resolve_net_dev(dst_ip, src_ip, tos)
    RTM->>RM: rule_resolve(dst_ip, src_ip, tos)
    RM->>NL: Query rule tables
    NL-->>RM: Rule information
    RM-->>RTM: Routing table ID
    
    RTM->>NL: Query routes
    NL-->>RTM: Route information
    
    RTM->>RTM: Find matching route
    RTM-->>DE: Return route (next_hop, src_addr, if_idx)
```

Sources:
- [src/vma/proto/dst_entry.cpp:199-248]()
- [src/vma/proto/route_table_mgr.cpp:223-266]()

The routing subsystem maintains a cache of the kernel's routing tables and rules, updated through netlink events. When determining how to route a packet, the system:

1. First consults the rule table (via `rule_table_mgr`) to determine which routing table to use
2. Then consults the appropriate routing table (via `route_table_mgr`) to find the best route
3. Returns routing information including:
   - Next-hop address (gateway, if applicable)
   - Source address to use
   - Outgoing interface index
   - Path MTU

The routing subsystem uses the Observer pattern to notify interested components about route changes.

Sources:
- [src/vma/proto/route_table_mgr.cpp:96-176]()
- [src/vma/proto/rule_table_mgr.cpp:45-57]()

## Neighbor Discovery

The Neighbor Discovery system resolves network layer addresses (IPv4) to link layer addresses (MAC/InfiniBand GID) and manages the neighbor cache.

### Core Components

```mermaid
classDiagram
    class neighbour_table_mgr {
        +register_observer(): bool
        +get_neighbour(): neigh_entry*
    }
    
    class neigh_entry {
        +get_peer_info(): bool
        +send_arp(): void
        +send(): int
    }
    
    class neigh_eth {
        +build_uc_neigh_val(): int
        +build_mc_neigh_val(): int
    }
    
    class neigh_ib {
        +build_uc_neigh_val(): int
        +build_mc_neigh_val(): int
    }
    
    class neigh_val {
        +get_l2_address(): const L2_address*
    }
    
    class neigh_eth_val {
    }
    
    class neigh_ib_val {
        +get_ah(): ibv_ah*
        +get_qpn(): uint32_t
    }
    
    neighbour_table_mgr o-- "many" neigh_entry: manages
    neigh_entry <|-- neigh_eth
    neigh_entry <|-- neigh_ib
    neigh_val <|-- neigh_eth_val
    neigh_val <|-- neigh_ib_val
    neigh_entry o-- neigh_val: contains
```

Sources:
- [src/vma/proto/neighbour.h:32-101]()
- [src/vma/proto/neighbour.cpp:54-235]()

### Neighbor Resolution Process

```mermaid
sequenceDiagram
    participant DE as "dst_entry"
    participant NTM as "neighbour_table_mgr"
    participant NE as "neigh_entry"
    participant Sock as "Socket API"
    
    DE->>NTM: resolve_neigh(dst_addr, netdev)
    NTM->>NTM: Find/create neigh_entry
    
    alt Existing entry
        NTM->>NE: get_peer_info()
        NE-->>NTM: Return cached info
    else New entry
        NE->>NE: Initialize state machine
        activate NE
        NE->>NE: send_arp()
        NE->>Sock: sendto(ARP request)
        Sock-->>NE: ARP reply
        NE->>NE: Process ARP reply
        NE->>NE: Update L2 address
        deactivate NE
    end
    
    NTM-->>DE: Return neighbor info
```

Sources:
- [src/vma/proto/dst_entry.cpp:252-276]()
- [src/vma/proto/neighbour.cpp:320-365]()

The neighbor discovery system resolves IP addresses to link-layer addresses (MAC addresses for Ethernet, GIDs for InfiniBand). Key functions include:

1. Sending ARP requests for address resolution
2. Processing ARP replies to update the neighbor cache
3. Managing a state machine for each neighbor entry
4. Providing L2 addressing information to the destination entry system

For Ethernet neighbors, the system resolves MAC addresses. For InfiniBand neighbors, it resolves additional information such as Queue Pair Numbers (QPN) and Address Handles (AH) needed for RDMA operations.

Neighbor entries have a state machine that tracks:
- Initial resolution state
- Active resolution state (ARP in progress)
- Ready state (address resolved)
- Error states

Sources:
- [src/vma/proto/neighbour.cpp:54-129]()
- [src/vma/proto/neighbour.cpp:320-365]()

## Destination Entry System

The Destination Entry system manages connections to remote endpoints and handles packet transmission, tying together the routing and neighbor discovery components.

### Core Components

```mermaid
classDiagram
    class dst_entry {
        +prepare_to_send(): bool
        +resolve_net_dev(): bool
        +resolve_neigh(): bool
        +resolve_ring(): bool
        +send_ring_buffer(): void
    }
    
    class dst_entry_udp {
        +fast_send(): ssize_t
        +fast_send_fragmented(): ssize_t
    }
    
    class dst_entry_tcp {
        +fast_send(): ssize_t
    }
    
    dst_entry <|-- dst_entry_udp
    dst_entry <|-- dst_entry_tcp
    
    dst_entry --> route_table_mgr: resolves routes
    dst_entry --> neighbour_table_mgr: resolves neighbors
    dst_entry --> net_device_val: reserves rings
    dst_entry --> ring: sends packets
```

Sources:
- [src/vma/proto/dst_entry.h:44-162]()
- [src/vma/proto/dst_entry_tcp.h:13-16]()
- [src/vma/proto/dst_entry_udp.h:13-16]()

### Packet Transmission Process

```mermaid
sequenceDiagram
    participant App as "Application"
    participant Sock as "Socket API"
    participant DE as "dst_entry"
    participant Ring as "ring"
    participant HW as "Hardware"
    
    App->>Sock: sendto()/send()
    Sock->>DE: prepare_to_send()
    
    alt First send or route changed
        DE->>DE: resolve_net_dev()
        DE->>DE: resolve_neigh()
        DE->>DE: resolve_ring()
        DE->>DE: configure_headers()
    end
    
    alt UDP
        Sock->>DE: fast_send(iov)
        alt Single packet
            DE->>DE: fast_send_not_fragmented()
        else Multiple packets
            DE->>DE: fast_send_fragmented()
        end
    else TCP
        Sock->>DE: fast_send(iov)
    end
    
    DE->>Ring: send_ring_buffer()
    Ring->>HW: Post Send WQ
    HW-->>App: Data transmitted
```

Sources:
- [src/vma/proto/dst_entry.cpp:85-175]()
- [src/vma/proto/dst_entry_udp.cpp:54-153]()
- [src/vma/proto/dst_entry_tcp.cpp:45-184]()

The destination entry system is responsible for:

1. Creating and managing destination entries for each remote endpoint
2. Resolving the route to the destination
3. Resolving the neighbor (L2 address) for the next hop
4. Allocating and managing rings for packet transmission
5. Preparing packet headers (L2, IP, UDP/TCP)
6. Handling packet fragmentation for large UDP datagrams
7. Managing TCP segmentation and acknowledgment

Each protocol (UDP/TCP) has specialized destination entry classes that handle protocol-specific requirements:

- `dst_entry_udp`: Handles UDP packet transmission, including fragmentation
- `dst_entry_tcp`: Handles TCP packet transmission, including segmentation

Sources:
- [src/vma/proto/dst_entry.cpp:199-248]()
- [src/vma/proto/dst_entry.cpp:252-276]()
- [src/vma/proto/dst_entry_udp.cpp:155-302]()

## Network Data Flow

This section illustrates how the network layer components work together to process packets.

```mermaid
flowchart TD
    subgraph "Application"
        App["Application Code"]
    end

    subgraph "Socket Layer"
        Socket["sockinfo"]
    end

    subgraph "Network Layer"
        DstEntry["dst_entry"]
        RouteTbl["route_table_mgr"]
        NeighTbl["neighbour_table_mgr"]
        NetDev["net_device_val"]
    end

    subgraph "Hardware Abstraction"
        Ring["ring"]
        QP["qp_mgr"]
        CQ["cq_mgr"]
    end

    subgraph "Network Hardware"
        HW["NIC/HCA"]
    end

    App-->|"socket(), bind(), connect()"| Socket
    App-->|"send(), sendto()"| Socket
    Socket-->|"prepare_to_send()"| DstEntry
    
    DstEntry-->|"resolve_net_dev()"| RouteTbl
    DstEntry-->|"resolve_neigh()"| NeighTbl
    DstEntry-->|"reserve_ring()"| NetDev
    
    RouteTbl-->|"return route"| DstEntry
    NeighTbl-->|"return L2 address"| DstEntry
    NetDev-->|"return ring"| DstEntry
    
    DstEntry-->|"send_ring_buffer()"| Ring
    Ring-->|"send()"| QP
    QP-->|"post_send()"| HW
    
    HW-->|"completion event"| CQ
    CQ-->Ring
    Ring-->Socket
```

Sources:
- [src/vma/proto/dst_entry.cpp:53-107]()
- [src/vma/proto/dst_entry_udp.cpp:54-153]()
- [src/vma/dev/net_device_val.cpp:946-992]()

### Outbound Packet Path

For outbound packets, the flow is:

1. Application calls send/sendto/write on a socket
2. Socket layer creates a destination entry if one doesn't exist
3. Destination entry resolves:
   - Route to destination via route_table_mgr
   - Next-hop link address via neighbour_table_mgr
   - Network device and ring via net_device_val
4. Destination entry prepares packet headers
5. Destination entry sends packet via ring
6. Ring posts send request to hardware
7. Hardware transmits packet

### UDP vs TCP Handling

| Feature | UDP Handling | TCP Handling |
|---------|-------------|-------------|
| Fragmentation | Handled by dst_entry_udp | N/A (TCP segments) |
| Checksum | Hardware or software | Hardware or software |
| Header preparation | Per-packet | Connection-based |
| Retransmission | None | Handled by TCP stack |
| Memory management | Buffer pools | Zero-copy when possible |

Sources:
- [src/vma/proto/dst_entry_udp.cpp:155-302]()
- [src/vma/proto/dst_entry_tcp.cpp:44-184]()

## Network Layer Integration

The Network Layer integrates with other VMA components to provide a complete networking solution:

```mermaid
graph TD
    subgraph "Socket Layer"
        Socket["Socket API"]
    end
    
    subgraph "Network Layer"
        NetDev["Network Device Management"]
        Route["Routing Subsystem"]
        Neigh["Neighbor Discovery"]
        Dst["Destination Entry System"]
    end
    
    subgraph "Hardware Abstraction Layer"
        Ring["Ring Layer"]
        RDMA["RDMA/InfiniBand Layer"]
    end
    
    Socket -->|"Uses"| Dst
    
    NetDev -->|"Provides devices"| Dst
    Route -->|"Provides routes"| Dst
    Neigh -->|"Provides L2 addresses"| Dst
    
    Dst -->|"Sends through"| Ring
    Ring -->|"Uses"| RDMA
    
    NetDev -->|"Manages"| Ring
```

Sources:
- [src/vma/dev/net_device_table_mgr.cpp:274-290]()
- [src/vma/proto/dst_entry.cpp:252-276]()

The Network Layer's components work together to provide:

1. Transparent acceleration of network traffic
2. Efficient memory management through buffer pooling
3. Hardware offload capabilities for checksum and segmentation
4. Integration with RDMA/InfiniBand features
5. Support for various network configurations (bonding, VLANs, etc.)

By abstracting these networking details, the VMA library allows applications to benefit from high-performance networking without code changes.

---

