> 来源: [https://deepwiki.com/deepseek-ai/3FS/7-networking-layer](https://deepwiki.com/deepseek-ai/3FS/7-networking-layer)
> DeepWiki deepseek-ai/3FS

# Networking Layer

  Relevant source files 
 - [configs/storage_main.toml](https://github.com/deepseek-ai/3FS/blob/22fca045/configs/storage_main.toml)
 - [src/common/net/IOWorker.cc](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/net/IOWorker.cc)
 - [src/common/net/Listener.cc](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/net/Listener.cc)
 - [src/common/net/Listener.h](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/net/Listener.h)
 - [src/common/net/ib/IBConnect.cc](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/net/ib/IBConnect.cc)
 - [src/common/net/ib/IBSocket.cc](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/net/ib/IBSocket.cc)
 - [src/common/net/ib/IBSocket.h](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/net/ib/IBSocket.h)
 - [src/storage/store/StorageTargets.cc](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/store/StorageTargets.cc)
 
  The 3FS Networking Layer provides a high-performance, multi-protocol communication infrastructure designed specifically for distributed storage workloads. It leverages RDMA (Remote Direct Memory Access) via InfiniBand or RoCE for low-latency data transfers, while maintaining a robust TCP fallback for control plane operations and environments without RDMA hardware.

 The layer is architected around an asynchronous event-driven model using `folly::coro` and a dedicated `IOWorker` pool to ensure high throughput and efficient CPU utilization.

 
### Architecture Overview

 The networking stack is organized into several functional components that bridge high-level RPC requests to low-level hardware transports.

 
#### Code Entity Map

 The following diagram maps high-level networking concepts to their primary C++ implementation classes.

 **Networking Entity Mapping**

 
```

```

 **Sources:** [src/common/net/Listener.h18-78](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/net/Listener.h#L18-L78) [src/common/net/IOWorker.h1-58](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/net/IOWorker.h#L1-L58) [src/common/net/ib/IBSocket.h81-152](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/net/ib/IBSocket.h#L81-L152)

 
---

 
### RDMA and InfiniBand Transport

 3FS implements a custom RDMA transport layer optimized for storage. Unlike standard socket-based RDMA (RSockets), 3FS uses Verbs directly to implement a credit-based flow control system and zero-copy data transfers.

 
 - **IBSocket**: The core abstraction for an RDMA connection, managing Queue Pairs (QP), Completion Queues (CQ), and memory registration (MR) [src/common/net/ib/IBSocket.h81-122](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/net/ib/IBSocket.h#L81-L122)
 - **RDMA Operations**: Supports standard `rdmaRead` and `rdmaWrite` operations, as well as `RDMAReqBatch` for combining multiple RDMA requests into a single hardware post to reduce CPU overhead [src/common/net/ib/IBSocket.h155-200](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/net/ib/IBSocket.h#L155-L200)
 - **Connection Handshake**: RDMA connections are established via a TCP-based handshake managed by `IBConnectService`. This service exchanges GIDs, QPNs, and PSNs between peers before transitioning the RDMA QP to the Ready-to-Send (RTS) state [src/common/net/ib/IBConnect.cc134-177](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/net/ib/IBConnect.cc#L134-L177)
 
 For details, see [RDMA and InfiniBand Transport](https://deepwiki.com/deepseek-ai/3FS/7.1-rdma-and-infiniband-transport).

 **Sources:** [src/common/net/ib/IBSocket.cc169-190](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/net/ib/IBSocket.cc#L169-L190) [src/common/net/ib/IBConnect.cc95-132](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/net/ib/IBConnect.cc#L95-L132)

 
---

 
### Network Listener and IOWorker

 The lifecycle of network connections and the execution of I/O events are managed by the `Listener` and `IOWorker` classes.

 
 - **Listener**: Responsible for binding to local interfaces and accepting incoming connections. It automatically detects available NICs and can filter by prefix (e.g., `eth`, `ib`, `bond`) [src/common/net/Listener.cc33-49](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/net/Listener.cc#L33-L49) It handles both standard TCP `ServerSocket` and the complex RDMA handshake initiation [src/common/net/Listener.cc119-127](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/net/Listener.cc#L119-L127)
 - **IOWorker**: Acts as the engine for the networking layer. It maintains a pool of `Transport` objects and runs an `epoll`-based event loop [src/common/net/IOWorker.cc28-44](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/net/IOWorker.cc#L28-L44)
 - **Event Loop**: I/O events (EPOLLIN/EPOLLOUT) trigger callbacks on the `Transport`. Depending on configuration, the actual read/write operations can be performed directly in the event thread or offloaded to a thread pool to prevent blocking the loop [src/common/net/IOWorker.cc118-136](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/net/IOWorker.cc#L118-L136)
 
 **Connection Flow**

 
```

```

 **Sources:** [src/common/net/Listener.cc94-116](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/net/Listener.cc#L94-L116) [src/common/net/IOWorker.cc46-58](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/net/IOWorker.cc#L46-L58)

 For details, see [Network Listener and IOWorker](https://deepwiki.com/deepseek-ai/3FS/7.2-network-listener-and-ioworker).

 
---

 
### RPC and Serialization Framework

 The networking layer serves as the transport for the 3FS RPC framework. This framework uses a `serde`-based approach for efficient serialization of request and response objects.

 
 - **Service Definitions**: Services like `StorageSerde` or `MgmtdService` define their RPC interfaces, which are then bound to a `ServiceGroup` for dispatching [configs/storage_main.toml106-165](https://github.com/deepseek-ai/3FS/blob/22fca045/configs/storage_main.toml#L106-L165)
 - **Protocol Support**: The RPC layer is transport-agnostic, allowing the same service logic to run over TCP (for control messages) or RDMA (for data-heavy operations).
 - **Serialization**: High-performance serialization is critical for 3FS. The framework supports compression for large responses and integrates with the `RDMABuf` pool for zero-copy data transmission in storage operations [configs/storage_main.toml158-223](https://github.com/deepseek-ai/3FS/blob/22fca045/configs/storage_main.toml#L158-L223)
 
 For details, see [RPC and Serialization Framework](https://deepwiki.com/deepseek-ai/3FS/7.3-rpc-and-serialization-framework).

 **Sources:** [src/common/net/ib/IBSocket.h73-79](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/net/ib/IBSocket.h#L73-L79) [configs/storage_main.toml102-110](https://github.com/deepseek-ai/3FS/blob/22fca045/configs/storage_main.toml#L102-L110)
