<!-- source: DeepWiki mcp.deepwiki.com · repo datenlord/async-rdma · page 1 Overview · fetched 2026-11-11 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [Cargo.toml](Cargo.toml)
- [ChangeLog.md](ChangeLog.md)
- [LICENSE](LICENSE)
- [README.md](README.md)
- [src/lib.rs](src/lib.rs)

</details>



This document provides a comprehensive introduction to the async-rdma library, a framework for writing asynchronous RDMA (Remote Direct Memory Access) applications in Rust. This overview covers the purpose, architecture, and key features of the library to help users understand how to utilize it effectively.

## What is async-rdma?

Async-rdma is a high-level Rust framework that provides asynchronous abstractions over RDMA technology. RDMA enables direct memory access from one computer to the memory of another without involving the operating system or CPU, resulting in:

- **High throughput** and **low latency** network communication
- **Zero-copy** data transfer between applications
- **Kernel bypass** for improved performance
- **CPU offloading** for network operations

Rather than requiring developers to work with complex low-level RDMA APIs directly, async-rdma offers a more ergonomic interface with Rust's safety guarantees and asynchronous programming model.

Sources: [src/lib.rs:1-16](). [README.md:1-32]().

## Key Components and Architecture

The library consists of several interconnected components that work together to provide a comprehensive RDMA solution:

```mermaid
flowchart TD
    subgraph "Application Layer"
        App["User Application"]
        App -->|uses| RdmaBuilder
        RdmaBuilder -->|creates| Rdma
    end

    subgraph "API Layer"
        Rdma -->|provides| Ops["Data Operations\n(read/write/send/receive)"]
        Rdma -->|provides| MrMgmt["Memory Management\n(alloc/request/send/receive)"]
    end

    subgraph "Resource Management Layer"
        Rdma -->|uses| Context
        Context -->|creates| PD["ProtectionDomain"]
        PD -->|creates| QP["QueuePair"]
        Rdma -->|uses| MrAlloc["MrAllocator"]
    end

    subgraph "Communication Layer"
        Rdma -->|uses| Agent
        Agent -->|posts operations to| QP
        QP -->|uses| CQListener["CQEventListener"]
        CQListener -->|monitors| CQ["CompletionQueue"]
    end

    subgraph "Memory Layer"
        MrAlloc -->|allocates| LocalMr
        Agent -->|requests| RemoteMr
        Agent -->|manages| RMRMgr["RemoteMrManager"]
    end
```

Sources: [src/lib.rs:123-165](). [Cargo.toml:1-40]().

### Core Components

1. **RdmaBuilder**: Entry point for configuring and establishing RDMA connections
2. **Rdma**: Primary interface for performing RDMA operations
3. **Context**: Represents an RDMA device and provides factory methods for other resources
4. **ProtectionDomain**: Provides security isolation for memory regions
5. **QueuePair**: Core communication channel between RDMA endpoints
6. **Agent**: Orchestrates high-level communication patterns and memory management
7. **MrAllocator**: Manages memory region allocation and registration
8. **LocalMr/RemoteMr**: Represents local and remote memory regions for RDMA operations

Sources: [src/lib.rs:167-204](). [src/lib.rs:327-368]().

## Key Features

### Connection Establishment

Async-rdma provides multiple ways to establish connections between RDMA endpoints:

```mermaid
sequenceDiagram
    participant Client
    participant Server
    
    alt TCP Socket-based Connection
        Client->>Client: RdmaBuilder::default()
        Client->>Server: connect(addr)
        Server->>Server: RdmaBuilder::default()
        Server->>Server: listen(addr)
        Client->>Server: Exchange QP attributes
        Note over Client,Server: QP Handshake
    else RDMA CM-based Connection
        Client->>Client: RdmaBuilder::default().set_conn_type(RCCM)
        Client->>Server: cm_connect(node, service)
        Server->>Server: RDMA CM Server (external)
        Note over Client,Server: CM establishes connection
    else Raw IBV Connection
        Client->>Client: RdmaBuilder::default().set_conn_type(RCIBV)
        Client->>Server: ibv_connect(remote_endpoint)
        Note over Client,Server: Direct connection with QP info
    end
```

Sources: [src/lib.rs:371-421](). [src/lib.rs:545-562](). [src/lib.rs:435-455]().

### Memory Management System

Async-rdma provides a sophisticated memory management system that handles allocation, registration, and deallocation of memory regions:

```mermaid
flowchart TD
    subgraph "Memory Region Types"
        LocalMr["LocalMr\n(Local access)"]
        RemoteMr["RemoteMr\n(Remote access)"]
        LocalMrSlice["LocalMrSlice\n(Read-only slice)"]
        LocalMrSliceMut["LocalMrSliceMut\n(Mutable slice)"]
        RemoteMrSlice["RemoteMrSlice\n(Remote slice)"]
    end

    subgraph "Access Traits"
        MrAccess["MrAccess"]
        LocalMrReadAccess["LocalMrReadAccess"]
        LocalMrWriteAccess["LocalMrWriteAccess"]
        RemoteMrReadAccess["RemoteMrReadAccess"]
        RemoteMrWriteAccess["RemoteMrWriteAccess"]
    end

    subgraph "Allocation Strategies"
        Jemalloc["Jemalloc Strategy"]
        Raw["Raw Allocation"]
    end

    MrAlloc["MrAllocator"]
    MrAlloc -->|creates| LocalMr
    MrAlloc -->|"uses strategy"| Jemalloc
    MrAlloc -->|"uses strategy"| Raw
    
    Rdma -->|"alloc_local_mr()"| MrAlloc
    Rdma -->|"request_remote_mr()"| Agent
    
    Agent -->|obtains| RemoteMr
    
    LocalMr -->|"implements"| LocalMrReadAccess
    LocalMr -->|"implements"| LocalMrWriteAccess
    RemoteMr -->|"implements"| RemoteMrReadAccess
    RemoteMr -->|"implements"| RemoteMrWriteAccess
    
    LocalMr -->|"sliced into"| LocalMrSlice
    LocalMr -->|"sliced into"| LocalMrSliceMut
    RemoteMr -->|"sliced into"| RemoteMrSlice
    
    MrAccess -->|"base trait"| LocalMrReadAccess
    MrAccess -->|"base trait"| RemoteMrReadAccess
    LocalMrReadAccess -->|"extends"| LocalMrWriteAccess
    RemoteMrReadAccess -->|"extends"| RemoteMrWriteAccess
```

Sources: [src/lib.rs:178-182](). [src/lib.rs:183-184]().

### Data Transfer Operations

Async-rdma supports several RDMA operation patterns:

1. **Read/Write Operations**: Direct memory access between local and remote memory regions
2. **Send/Receive Operations**: Two-sided communication with notifications
3. **Atomic Operations**: Compare-and-swap operations on remote memory

```mermaid
sequenceDiagram
    participant Client
    participant Server
    
    note over Client,Server: RDMA Write Pattern
    Client->>Server: request_remote_mr(layout)
    Server-->>Client: Remote MR token
    Client->>Client: alloc_local_mr(layout)
    Client->>Client: Write data to local MR
    Client->>Server: RDMA Write to Remote MR
    Client->>Server: send_remote_mr(rmr)
    Server->>Server: Receive notification & use data
    
    note over Client,Server: RDMA Send/Receive Pattern
    Client->>Client: alloc_local_mr(layout)
    Client->>Client: Write data to local MR
    Client->>Server: send_local_mr(lmr)
    Server->>Server: receive_local_mr()
    Server->>Server: Read data from received MR
```

Sources: [src/lib.rs:25-71](). [README.md:126-179]().

## Basic Usage Example

Below is a simple example demonstrating how async-rdma can be used to establish a connection, allocate memory regions, and perform RDMA operations:

```rust
// Client side
async fn client(addr: SocketAddrV4) -> io::Result<()> {
    let layout = Layout::new::<[u8; 8]>();
    let rdma = RdmaBuilder::default().connect(addr).await?;
    // Request 8 bytes remote memory
    let mut rmr = rdma.request_remote_mr(layout).await?;
    // Allocate 8 bytes local memory
    let mut lmr = rdma.alloc_local_mr(layout)?;
    // Write data into local memory
    lmr.as_mut_slice().write(&[1_u8; 8])?;
    // Write data to remote memory
    rdma.write(&lmr.get(4..8).unwrap(), &mut rmr.get_mut(4..8).unwrap()).await?;
    // Send remote MR back to make server aware of it
    rdma.send_remote_mr(rmr).await?;
    Ok(())
}

// Server side
async fn server(addr: SocketAddrV4) -> io::Result<()> {
    let rdma = RdmaBuilder::default().listen(addr).await?;
    // Receive MR metadata from client
    let lmr = rdma.receive_local_mr().await?;
    // Read data that was written by client
    let data = *lmr.as_slice();
    println!("Data written by the client: {:?}", data);
    Ok(())
}
```

Sources: [src/lib.rs:33-59](). [README.md:141-166]().

## Underlying Architecture

Async-rdma builds upon RDMA system libraries and abstracts them with a Rust-friendly asynchronous API:

```mermaid
flowchart TD
    subgraph "User Application"
        App["Application Code"]
    end
    
    subgraph "async-rdma Library"
        HighLevel["High-level API\n(Rdma, RdmaBuilder)"]
        Agent["Agent & Background Tasks"]
        MemoryMgmt["Memory Management\n(MrAllocator, LocalMr, RemoteMr)"]
        QpMgmt["Queue Pair Management\n(QueuePair, CQEventListener)"]
    end
    
    subgraph "System Libraries"
        RdmaSys["rdma-sys\n(Rust bindings)"]
        Verbs["libibverbs\n(RDMA Verbs)"]
        CM["librdmacm\n(RDMA Connection Manager)"]
    end
    
    subgraph "RDMA Hardware/Kernel"
        RdmaKernel["RDMA Kernel Modules"]
        RdmaHW["RDMA Hardware\n(NIC/HCA)"]
    end
    
    App -->|"uses"| HighLevel
    HighLevel -->|"uses"| Agent
    HighLevel -->|"uses"| MemoryMgmt
    HighLevel -->|"uses"| QpMgmt
    
    Agent -->|"uses"| RdmaSys
    MemoryMgmt -->|"uses"| RdmaSys
    QpMgmt -->|"uses"| RdmaSys
    
    RdmaSys -->|"wraps"| Verbs
    RdmaSys -->|"wraps"| CM
    
    Verbs -->|"interacts with"| RdmaKernel
    CM -->|"interacts with"| RdmaKernel
    
    RdmaKernel -->|"controls"| RdmaHW
```

Sources: [Cargo.toml:11-39](). [src/lib.rs:124-164]().

## Conclusion

Async-rdma provides an ergonomic, high-performance Rust interface to RDMA technology. By abstracting away many of the complexities of RDMA programming, it allows developers to focus on their application logic while benefiting from the performance advantages of RDMA.

For more detailed information on specific aspects of the library:
- For connection establishment details, see [Connection Management](#3.1)
- For memory management details, see [Memory Management](#3.2)
- For data transfer operations, see [Data Transfer Operations](#3.3)
- For usage examples, see [Examples & Patterns](#5)

---

