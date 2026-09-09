> 来源: [https://deepwiki.com/deepseek-ai/3FS/6-distributed-services](https://deepwiki.com/deepseek-ai/3FS/6-distributed-services)
> DeepWiki deepseek-ai/3FS

# Distributed Services

  Relevant source files 
 - [docs/design_notes.md](https://github.com/deepseek-ai/3FS/blob/22fca045/docs/design_notes.md?plain=1)
 - [specs/README.md](https://github.com/deepseek-ai/3FS/blob/22fca045/specs/README.md?plain=1)
 - [src/common/utils/SimpleRingBuffer.h](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/utils/SimpleRingBuffer.h)
 - [src/lib/api/UsrbIo.md](https://github.com/deepseek-ai/3FS/blob/22fca045/src/lib/api/UsrbIo.md?plain=1)
 - [src/mgmtd/ops/SetChainTableOperation.cc](https://github.com/deepseek-ai/3FS/blob/22fca045/src/mgmtd/ops/SetChainTableOperation.cc)
 - [src/storage/service/ReliableForwarding.cc](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/service/ReliableForwarding.cc)
 - [src/storage/service/StorageOperator.cc](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/service/StorageOperator.cc)
 - [src/stubs/CMakeLists.txt](https://github.com/deepseek-ai/3FS/blob/22fca045/src/stubs/CMakeLists.txt)
 - [tests/mgmtd/TestMgmtdOperator.cc](https://github.com/deepseek-ai/3FS/blob/22fca045/tests/mgmtd/TestMgmtdOperator.cc)
 
  The 3FS distributed file system is composed of four primary services that communicate over an RDMA-capable network (InfiniBand or RoCE) to provide a high-performance, POSIX-like file system. The architecture is disaggregated, separating cluster management, metadata persistence, and data storage.

 
## System Architecture Overview

 The interaction between these services follows a control-plane and data-plane split. The **Management Service (mgmtd)** and **Metadata Service (meta)** handle the control plane (cluster state and file hierarchy), while the **Storage Service** and **FUSE Client** handle the data plane (high-throughput I/O).

 
### Service Interaction Diagram

 This diagram maps the high-level service interactions to the specific RPC operations and classes found in the codebase.

 
```

```

 **Sources:** [docs/design_notes.md5-13](https://github.com/deepseek-ai/3FS/blob/22fca045/docs/design_notes.md?plain=1#L5-L13) [src/mgmtd/service/MgmtdOperator.h1-100](https://github.com/deepseek-ai/3FS/blob/22fca045/src/mgmtd/service/MgmtdOperator.h#L1-L100) [src/storage/service/StorageOperator.cc82-85](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/service/StorageOperator.cc#L82-L85)

 
---

 
## 6.1 Management Service (mgmtd)

 The Management Service (`mgmtd`) acts as the central coordinator for the 3FS cluster. It is responsible for maintaining the cluster's membership through heartbeats and distributing routing information (chain tables) to all other components.

 
 - **Primary Election:** Uses a lease-based mechanism to elect a primary mgmtd node from a set of replicas [docs/design_notes.md7](https://github.com/deepseek-ai/3FS/blob/22fca045/docs/design_notes.md?plain=1#L7-L7)
 - **Heartbeats:** Collects `HeartbeatReq` from storage and metadata nodes to monitor health [tests/mgmtd/TestMgmtdOperator.cc72-77](https://github.com/deepseek-ai/3FS/blob/22fca045/tests/mgmtd/TestMgmtdOperator.cc#L72-L77)
 - **Routing Distribution:** Manages the `RoutingInfo`, which includes the mapping of `ChainId` to physical `StorageTarget` nodes [src/mgmtd/ops/SetChainTableOperation.cc7-32](https://github.com/deepseek-ai/3FS/blob/22fca045/src/mgmtd/ops/SetChainTableOperation.cc#L7-L32)
 
 For details, see [Management Service (mgmtd)](https://deepwiki.com/deepseek-ai/3FS/6.1-management-service-(mgmtd)).

 **Sources:** [docs/design_notes.md7](https://github.com/deepseek-ai/3FS/blob/22fca045/docs/design_notes.md?plain=1#L7-L7) [tests/mgmtd/TestMgmtdOperator.cc140-165](https://github.com/deepseek-ai/3FS/blob/22fca045/tests/mgmtd/TestMgmtdOperator.cc#L140-L165) [src/mgmtd/ops/SetChainTableOperation.cc35-87](https://github.com/deepseek-ai/3FS/blob/22fca045/src/mgmtd/ops/SetChainTableOperation.cc#L35-L87)

 
---

 
## 6.2 Metadata Service (meta)

 The Metadata Service provides the file system namespace and implements POSIX semantics (e.g., atomic renames, hard links). It is designed to be stateless, delegating persistence to FoundationDB.

 
 - **Stateless Design:** Clients can connect to any metadata node, as all state is stored in the transactional KV store [docs/design_notes.md9](https://github.com/deepseek-ai/3FS/blob/22fca045/docs/design_notes.md?plain=1#L9-L9)
 - **Namespace Management:** Handles directory operations and inode management using a key schema optimized for FoundationDB [docs/design_notes.md19-23](https://github.com/deepseek-ai/3FS/blob/22fca045/docs/design_notes.md?plain=1#L19-L23)
 - **Chain Allocation:** Assigns storage chains to files during creation or expansion.
 
 For details, see [Metadata Service (meta)](https://deepwiki.com/deepseek-ai/3FS/6.2-metadata-service-(meta)).

 **Sources:** [docs/design_notes.md9-11](https://github.com/deepseek-ai/3FS/blob/22fca045/docs/design_notes.md?plain=1#L9-L11) [src/stubs/CMakeLists.txt2](https://github.com/deepseek-ai/3FS/blob/22fca045/src/stubs/CMakeLists.txt#L2-L2)

 
---

 
## 6.3 Storage Service

 The Storage Service manages local SSDs and provides a chunk-based interface for data I/O. It implements the **CRAQ (Chain Replication with Apportioned Queries)** protocol to ensure strong consistency while maximizing read throughput.

 
 - **CRAQ Implementation:** Uses a "write-all-read-any" approach. Writes are forwarded along a chain via `ReliableForwarding`, while reads can be satisfied by any node in the chain if the data is committed [docs/design_notes.md11](https://github.com/deepseek-ai/3FS/blob/22fca045/docs/design_notes.md?plain=1#L11-L11) [src/storage/service/ReliableForwarding.cc33-58](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/service/ReliableForwarding.cc#L33-L58)
 - **High Performance I/O:** Utilizes `StorageOperator` to handle `batchRead` and `batchWrite` RPCs, leveraging RDMA for zero-copy data transfer [src/storage/service/StorageOperator.cc82-95](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/service/StorageOperator.cc#L82-L95)
 - **Background Workers:** Includes `AllocateWorker` for disk space management and `CheckWorker` for data integrity.
 
 For details, see [Storage Service](https://deepwiki.com/deepseek-ai/3FS/6.3-storage-service).

 **Sources:** [docs/design_notes.md11](https://github.com/deepseek-ai/3FS/blob/22fca045/docs/design_notes.md?plain=1#L11-L11) [src/storage/service/StorageOperator.cc1-15](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/service/StorageOperator.cc#L1-L15) [src/storage/service/ReliableForwarding.cc113-136](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/service/ReliableForwarding.cc#L113-L136)

 
---

 
## 6.4 FUSE Client

 The FUSE Client (`hf3fs_fuse_main`) provides the primary interface for applications to access 3FS. While it supports standard POSIX access via the FUSE kernel module, it also includes a high-performance **USRBIO** interface.

 
 - **USRBIO API:** A user-space ring-based I/O interface that bypasses FUSE kernel bottlenecks by using shared memory (`Iov`) and submission/completion queues (`Ior`) [src/lib/api/UsrbIo.md3-11](https://github.com/deepseek-ai/3FS/blob/22fca045/src/lib/api/UsrbIo.md?plain=1#L3-L11)
 - **Parallel I/O:** Supports `PioV` for parallelized I/O operations across multiple storage chains [docs/design_notes.md49-50](https://github.com/deepseek-ai/3FS/blob/22fca045/docs/design_notes.md?plain=1#L49-L50)
 - **Zero-Copy:** Integrated with RDMA to allow direct data transfer between application memory and the storage service [docs/design_notes.md45-48](https://github.com/deepseek-ai/3FS/blob/22fca045/docs/design_notes.md?plain=1#L45-L48)
 
 For details, see [FUSE Client](https://deepwiki.com/deepseek-ai/3FS/6.4-fuse-client).

 
### USRBIO Code Entity Mapping

 The following diagram shows how the USRBIO API structures relate to the internal communication rings.

 
```

```

 **Sources:** [src/lib/api/UsrbIo.md15-30](https://github.com/deepseek-ai/3FS/blob/22fca045/src/lib/api/UsrbIo.md?plain=1#L15-L30) [src/lib/api/UsrbIo.md71-85](https://github.com/deepseek-ai/3FS/blob/22fca045/src/lib/api/UsrbIo.md?plain=1#L71-L85) [src/common/utils/SimpleRingBuffer.h11-20](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/utils/SimpleRingBuffer.h#L11-L20)
