<!-- source: DeepWiki mcp.deepwiki.com · repo Mellanox/libvma · page 2 Socket Layer · fetched 2026-11-11 -->

# Socket Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/vma/sock/pipeinfo.cpp](src/vma/sock/pipeinfo.cpp)
- [src/vma/sock/pipeinfo.h](src/vma/sock/pipeinfo.h)
- [src/vma/sock/sock-redirect.cpp](src/vma/sock/sock-redirect.cpp)
- [src/vma/sock/sock-redirect.h](src/vma/sock/sock-redirect.h)
- [src/vma/sock/socket_fd_api.cpp](src/vma/sock/socket_fd_api.cpp)
- [src/vma/sock/socket_fd_api.h](src/vma/sock/socket_fd_api.h)
- [src/vma/sock/sockinfo.cpp](src/vma/sock/sockinfo.cpp)
- [src/vma/sock/sockinfo.h](src/vma/sock/sockinfo.h)
- [src/vma/sock/sockinfo_tcp.cpp](src/vma/sock/sockinfo_tcp.cpp)
- [src/vma/sock/sockinfo_tcp.h](src/vma/sock/sockinfo_tcp.h)
- [src/vma/sock/sockinfo_udp.cpp](src/vma/sock/sockinfo_udp.cpp)
- [src/vma/sock/sockinfo_udp.h](src/vma/sock/sockinfo_udp.h)
- [src/vma/vma_extra.h](src/vma/vma_extra.h)

</details>



The Socket Layer in VMA provides the core mechanism for intercepting and processing standard socket operations to enable network acceleration. It serves as a bridge between the application's socket API calls and the RDMA/InfiniBand hardware abstraction layers, allowing transparent acceleration of networking operations while maintaining compatibility with standard socket APIs.

For information about the overall VMA architecture, see [Architecture Overview](#1.1). For details about how socket operations are intercepted, see [Socket Redirection](#2.1).

## Socket Layer Overview

The Socket Layer implements socket operations by either offloading them to hardware or passing them through to the operating system. This decision is made based on several factors including socket type, address family, and network device capabilities.

```mermaid
classDiagram
    class socket_fd_api {
        +int m_fd
        +socket_fd_api(int fd)
        +virtual ~socket_fd_api()
        +virtual void setPassthrough()
        +virtual bool isPassthrough()
        +virtual int rx(rx_call_t call_type, iovec* p_iov, ...)
        +virtual ssize_t tx(vma_tx_call_attr_t &tx_attr)
        +virtual bool is_readable()
        +virtual bool is_writeable()
        +virtual fd_type_t get_type()
    }
    
    class sockinfo {
        +sockinfo(int fd)
        +~sockinfo()
        +virtual bool attach_receiver(flow_tuple_with_local_if &flow_key)
        +virtual void handle_ip_pktinfo()
        +virtual int bind(const sockaddr*, socklen_t)
        +virtual void set_blocking(bool)
        +virtual int fcntl(int, unsigned long)
        +virtual bool try_un_offloading()
    }
    
    class sockinfo_tcp {
        +tcp_pcb m_pcb
        +tcp_sock_offload_e m_sock_offload
        +tcp_sock_state_e m_sock_state
        +tcp_conn_state_e m_conn_state
        +sockinfo_tcp(int fd)
        +~sockinfo_tcp()
        +static err_t rx_lwip_cb(void*, tcp_pcb*, pbuf*, err_t)
        +static err_t ip_output(pbuf*, void*, uint16_t)
    }
    
    class sockinfo_udp {
        +bool m_sock_offload
        +dst_entry_map_t m_dst_entry_map
        +sockinfo_udp(int fd)
        +~sockinfo_udp()
        +int poll_os()
        +int rx_wait(bool blocking)
    }
    
    socket_fd_api <|-- sockinfo
    sockinfo <|-- sockinfo_tcp
    sockinfo <|-- sockinfo_udp
```

*Socket class hierarchy diagram showing inheritance relationships*

Sources: [src/vma/sock/socket_fd_api.h](), [src/vma/sock/sockinfo.h](), [src/vma/sock/sockinfo_tcp.h](), [src/vma/sock/sockinfo_udp.h]()

## Socket Operations Flow

The following diagram illustrates how socket operations flow through the VMA Socket Layer:

```mermaid
flowchart TD
    A["Application"] -->|"socket(), bind(), connect()"| B["Socket Redirection"]
    B -->|"Check if offloadable"| C{"Offloadable?"}
    C -->|"Yes"| D["sockinfo creation"]
    C -->|"No"| E["OS Socket API"]
    D -->|"TCP socket"| F["sockinfo_tcp"]
    D -->|"UDP socket"| G["sockinfo_udp"]
    F --> H["TCP Operations"]
    G --> I["UDP Operations"]
    H -->|"RX/TX"| J["VMA Ring Layer"]
    I -->|"RX/TX"| J
    J -->|"Hardware access"| K["RDMA/InfiniBand Hardware"]
    E -->|"Standard networking"| L["OS Networking Stack"]
```

*Socket operations flow diagram*

Sources: [src/vma/sock/sock-redirect.cpp:800-831](), [src/vma/sock/sockinfo_tcp.cpp:193-290](), [src/vma/sock/sockinfo_udp.cpp:304-360]()

## Socket Initialization

When a socket is created through the standard `socket()` call, VMA intercepts this call and determines whether the socket can be offloaded:

1. The Socket Redirection layer intercepts the call
2. For supported socket types (SOCK_DGRAM, SOCK_STREAM), it creates appropriate socket objects
3. TCP sockets are handled by `sockinfo_tcp`, UDP sockets by `sockinfo_udp`
4. The socket objects maintain state and handle subsequent socket operations

Socket offloading eligibility depends on:
- Socket type (TCP or UDP)
- Address family (currently focused on AF_INET)
- Whether the underlying network device supports RDMA/InfiniBand features

```mermaid
sequenceDiagram
    participant App as Application
    participant Redir as Socket Redirection
    participant FD as FD Collection
    participant SI as sockinfo
    
    App->>Redir: socket(AF_INET, SOCK_STREAM, 0)
    Redir->>Redir: socket_internal()
    Redir->>FD: get_orig_funcs()
    Redir->>FD: orig_os_api.socket()
    Note over Redir,FD: Creates real OS socket
    
    alt socktype is SOCK_DGRAM or SOCK_STREAM
        Redir->>FD: addsocket(fd, domain, type)
        FD->>SI: Create sockinfo_tcp/sockinfo_udp
        SI->>SI: Initialize state
    end
    
    Redir-->>App: Return socket fd
```

*Socket initialization sequence diagram*

Sources: [src/vma/sock/sock-redirect.cpp:792-831](), [src/vma/sock/sockinfo_tcp.cpp:193-290](), [src/vma/sock/sockinfo_udp.cpp:304-360]()

## Socket Types and Implementation

VMA implements specialized socket classes for different socket types:

### Base Socket Classes

1. **socket_fd_api** - Abstract base class representing socket file descriptor API interface
   - Provides interface for all socket operations
   - Manages socket file descriptor and associated state
   - Implements basic socket functionality

2. **sockinfo** - Base class for socket information
   - Inherits from socket_fd_api
   - Implements common functionality across socket types
   - Manages socket blocking behavior, options, state transitions

### Specialized Socket Implementations

#### TCP Sockets (sockinfo_tcp)

The TCP socket implementation in VMA provides:
- Complete TCP state machine
- Integration with LWIP for wire-compatible TCP implementation
- Support for connection-oriented operations (listen, accept, connect)
- Managed through sockinfo_tcp class

Key components:
- TCP Protocol Control Block (PCB) from LWIP
- Socket state management (INITED, BOUND, CONNECTED, etc.)
- Connection state management (INIT, CONNECTING, CONNECTED, etc.)
- Support for socket options like TCP_NODELAY, SO_RCVBUF, etc.

```
TCP Socket States:
- TCP_SOCK_INITED
- TCP_SOCK_BOUND
- TCP_SOCK_LISTEN_READY
- TCP_SOCK_ACCEPT_READY
- TCP_SOCK_CONNECTED_RD
- TCP_SOCK_CONNECTED_WR
- TCP_SOCK_CONNECTED_RDWR
- TCP_SOCK_ASYNC_CONNECT
- TCP_SOCK_ACCEPT_SHUT
```

#### UDP Sockets (sockinfo_udp)

The UDP socket implementation provides:
- Datagram-based communication
- Support for multicast operations
- Zero-copy receive mechanisms
- Managed through sockinfo_udp class

Key components:
- Destination entry mapping (m_dst_entry_map)
- Buffer management for zero-copy operations
- Support for socket options like IP_MULTICAST_IF, SO_RCVBUF, etc.

Sources: [src/vma/sock/sockinfo_tcp.h:91-453](), [src/vma/sock/sockinfo_udp.h:63-275](), [src/vma/sock/sockinfo.h:131-347]()

## Socket States and Transitions

VMA socket implementations maintain state for proper handling of socket operations:

### Common Socket States

```mermaid
stateDiagram-v2
    [*] --> SOCKINFO_OPENED
    SOCKINFO_OPENED --> SOCKINFO_CLOSING: close/shutdown
    SOCKINFO_CLOSING --> SOCKINFO_CLOSED: cleanup complete
    SOCKINFO_CLOSED --> [*]
```

*Common socket state diagram*

### TCP Socket-Specific States

```mermaid
stateDiagram-v2
    [*] --> TCP_SOCK_INITED: socket()
    TCP_SOCK_INITED --> TCP_SOCK_BOUND: bind()
    TCP_SOCK_BOUND --> TCP_SOCK_LISTEN_READY: prepareListen()
    TCP_SOCK_LISTEN_READY --> TCP_SOCK_ACCEPT_READY: listen()
    TCP_SOCK_ACCEPT_READY --> TCP_SOCK_CONNECTED_RDWR: accept()
    
    TCP_SOCK_INITED --> TCP_SOCK_ASYNC_CONNECT: connect(non-blocking)
    TCP_SOCK_ASYNC_CONNECT --> TCP_SOCK_CONNECTED_RDWR: connection complete
    
    TCP_SOCK_INITED --> TCP_SOCK_CONNECTED_RDWR: connect(blocking)
    TCP_SOCK_BOUND --> TCP_SOCK_CONNECTED_RDWR: connect()
    
    TCP_SOCK_CONNECTED_RDWR --> TCP_SOCK_CONNECTED_WR: shutdown(RD)
    TCP_SOCK_CONNECTED_RDWR --> TCP_SOCK_CONNECTED_RD: shutdown(WR)
    
    TCP_SOCK_ACCEPT_READY --> TCP_SOCK_ACCEPT_SHUT: shutdown()
```

*TCP socket state diagram*

### TCP Connection States

```mermaid
stateDiagram-v2
    [*] --> TCP_CONN_INIT
    TCP_CONN_INIT --> TCP_CONN_CONNECTING: connect()
    TCP_CONN_CONNECTING --> TCP_CONN_CONNECTED: connection established
    TCP_CONN_CONNECTING --> TCP_CONN_FAILED: connection failed
    TCP_CONN_CONNECTING --> TCP_CONN_TIMEOUT: timeout
    TCP_CONN_CONNECTING --> TCP_CONN_ERROR: error
    TCP_CONN_CONNECTING --> TCP_CONN_RESETED: RST received
```

*TCP connection state diagram*

Sources: [src/vma/sock/sockinfo.h:137-141](), [src/vma/sock/sockinfo_tcp.h:31-60]()

## Data Flow in Socket Layer

### Receiving Data (RX Path)

The receive path in the Socket Layer is responsible for:
1. Retrieving data from network hardware (via Ring Layer)
2. Processing it through the appropriate protocol stack
3. Delivering it to the application

```mermaid
sequenceDiagram
    participant App as Application
    participant Sock as sockinfo_tcp/sockinfo_udp
    participant Ring as Ring Layer
    participant HW as Network Hardware
    
    App->>Sock: recv()/recvfrom()/read()
    
    alt Data already in receive queue
        Sock-->>App: Return buffered data
    else No data available
        alt Blocking mode
            Sock->>Ring: rx_wait()
            Ring->>HW: Poll for completions
            HW-->>Ring: Completion event
            Ring->>Sock: Packet available notification
            Sock->>Sock: Process packet
            Sock-->>App: Return data
        else Non-blocking mode
            Sock-->>App: Return EAGAIN
        end
    end
```

*Receive path sequence diagram*

Sources: [src/vma/sock/sockinfo_tcp.cpp:142-136](), [src/vma/sock/sockinfo_udp.cpp:92-284]()

### Sending Data (TX Path)

The transmit path is responsible for:
1. Preparing data for transmission
2. Sending it through the appropriate protocol stack
3. Submitting it to the network hardware

```mermaid
sequenceDiagram
    participant App as Application
    participant Sock as sockinfo_tcp/sockinfo_udp
    participant DST as dst_entry
    participant Ring as Ring Layer
    participant HW as Network Hardware
    
    App->>Sock: send()/sendto()/write()
    
    alt TCP
        Sock->>Sock: tcp_write()
        Sock->>DST: prepare_to_send()
    else UDP
        Sock->>DST: prepare_to_send()
    end
    
    DST->>Ring: send_buffer()
    Ring->>HW: Post Send Work Request
    HW-->>Ring: Completion
    Sock-->>App: Return bytes sent
```

*Transmit path sequence diagram*

Sources: [src/vma/sock/sockinfo_tcp.cpp:709-956](), [src/vma/sock/sockinfo_udp.cpp]()

## Socket Options Handling

The Socket Layer implements standard socket options as well as VMA-specific extensions:

### Standard Socket Options

- **SOL_SOCKET level options** - SO_RCVBUF, SO_SNDBUF, SO_REUSEADDR, etc.
- **IPPROTO_TCP level options** - TCP_NODELAY, TCP_KEEPALIVE, etc.
- **IPPROTO_IP level options** - IP_MULTICAST_IF, IP_TTL, etc.

### VMA-Specific Socket Options

- **SO_VMA_USER_DATA** - Associate custom user data with a socket
- **SO_VMA_RING_ALLOC_LOGIC** - Control ring allocation logic
- **SO_VMA_FLOW_TAG** - Set flow tag for a socket
- **SO_VMA_RING_USER_MEMORY** - Provide user memory for ring buffers

```mermaid
flowchart TD
    A["setsockopt() call"] --> B["sockinfo::setsockopt()"]
    B --> C{"Option level?"}
    
    C -->|"SOL_SOCKET"| D{"Option name?"}
    D -->|"Standard options"| E["Process standard option"]
    D -->|"VMA options"| F["Process VMA option"]
    E --> G["Update socket state"]
    F --> G
    
    C -->|"IPPROTO_TCP"| H["TCP option handling"]
    C -->|"IPPROTO_IP"| I["IP option handling"]
    
    H --> G
    I --> G
    
    G --> J{"Return value?"}
    J -->|"SOCKOPT_INTERNAL_VMA_SUPPORT"| K["Return success"]
    J -->|"SOCKOPT_NO_VMA_SUPPORT"| L["Return error"]
    J -->|"SOCKOPT_PASS_TO_OS"| M["Call OS setsockopt"]
```

*Socket option handling flow diagram*

Sources: [src/vma/sock/sockinfo.cpp:305-481](), [src/vma/sock/sockinfo_tcp.cpp](), [src/vma/sock/sockinfo_udp.cpp:640-768]()

## Offloading Decision Process

A key responsibility of the Socket Layer is deciding whether a socket can be offloaded or should be passed through to the OS:

```mermaid
flowchart TD
    A["New socket"] --> B{"Socket type?"}
    B -->|"SOCK_STREAM, SOCK_DGRAM"| C{"Address family?"}
    B -->|"Other"| D["Passthrough to OS"]
    
    C -->|"AF_INET"| E{"Network interface?"}
    C -->|"Other"| D
    
    E -->|"RDMA/IB capable"| F["Offload socket"]
    E -->|"Not capable"| D
    
    F --> G{"Operation compatible?"}
    G -->|"Yes"| H["Keep offloaded"]
    G -->|"No"| I["Switch to passthrough"]
```

*Offloading decision flow diagram*

Sources: [src/vma/sock/sock-redirect.cpp:793-828](), [src/vma/sock/sockinfo.cpp:532-544]()

## Socket Redirection Mechanism

The Socket Layer relies on the Socket Redirection mechanism to intercept standard socket API calls:

1. VMA replaces standard socket functions (socket, bind, connect, etc.) with its own implementations
2. When these functions are called, VMA intercepts them and routes them through the Socket Layer
3. The Socket Layer either handles the operation or passes it to the original OS implementation

```mermaid
sequenceDiagram
    participant App as Application
    participant Redir as VMA Socket Redirection
    participant SI as sockinfo
    participant OS as Original OS API
    
    App->>Redir: socket()
    Redir->>Redir: socket_internal()
    Redir->>OS: orig_os_api.socket()
    OS-->>Redir: fd
    Redir->>SI: Create sockinfo object
    Redir-->>App: Return fd
    
    App->>Redir: connect(fd, addr, addrlen)
    Redir->>Redir: get_sockfd(fd)
    Redir->>SI: si->connect(addr, addrlen)
    
    alt Offloaded connection
        SI->>SI: Handle connection
        SI-->>Redir: Status
    else Passthrough connection
        SI->>Redir: setPassthrough()
        Redir->>OS: orig_os_api.connect()
        OS-->>Redir: Status
    end
    
    Redir-->>App: Return status
```

*Socket redirection sequence diagram*

Sources: [src/vma/sock/sock-redirect.cpp:792-1002]()

## Integration with Other VMA Components

The Socket Layer integrates with several other components in the VMA system:

### Ring Layer Integration

Socket objects interact with the Ring Layer to send and receive data:
- Each socket is associated with one or more rings
- Rings provide the interface to the hardware queues
- Sockets use rings for data transmission and reception

### Protocol Implementation Integration

- TCP sockets integrate with the LWIP TCP implementation
- UDP sockets have a custom implementation in VMA
- Both implementations interface with the destination entry management system

### Buffer Management

Socket implementations handle buffer management for efficient data transfer:
- Zero-copy mechanisms to avoid unnecessary data copying
- Buffer pool integration for memory management
- Buffer reuse strategies for optimal performance

```mermaid
flowchart TD
    subgraph "Socket Layer"
        A["sockinfo_tcp"]
        B["sockinfo_udp"]
    end
    
    subgraph "Protocol Layer"
        C["LWIP TCP"]
        D["VMA UDP Implementation"]
    end
    
    subgraph "Routing Layer"
        E["dst_entry"]
        F["Flow Manager"]
    end
    
    subgraph "Ring Layer"
        G["ring"]
        H["ring_simple"]
        I["cq_mgr"]
    end
    
    subgraph "Memory Management"
        J["Buffer Pool"]
        K["Memory Registration"]
    end
    
    A --> C
    B --> D
    C --> E
    D --> E
    E --> F
    A --> G
    B --> G
    G --> H
    H --> I
    A --> J
    B --> J
    J --> K
```

*Socket Layer integration with other VMA components*

Sources: [src/vma/sock/sockinfo_tcp.cpp](), [src/vma/sock/sockinfo_udp.cpp](), [src/vma/sock/sockinfo.h]()

## Socket Performance Optimizations

The Socket Layer implements various optimizations to improve performance:

1. **Zero-copy data transfer** - Avoiding unnecessary data copies between user and kernel space
2. **Buffer reuse** - Efficient reuse of memory buffers to reduce memory allocations
3. **Batch processing** - Processing multiple operations together for better efficiency
4. **Event-driven polling** - Efficient notification mechanisms for socket readiness
5. **Direct hardware access** - Bypassing the kernel for data transfer operations

These optimizations enable VMA to achieve lower latency and higher throughput compared to standard socket implementations.

Sources: [src/vma/sock/sockinfo_tcp.cpp](), [src/vma/sock/sockinfo_udp.cpp]()

## Summary

The Socket Layer in VMA serves as the core component that enables transparent acceleration of socket operations by:

1. Intercepting standard socket API calls through redirection mechanisms
2. Implementing socket behavior for both TCP and UDP protocols
3. Making intelligent decisions about offloading vs. passthrough to OS
4. Managing socket state and operations
5. Integrating with other VMA components for efficient data transfer

This architecture allows applications to benefit from hardware acceleration without requiring code modifications, providing significant performance improvements for network-intensive applications.

---

