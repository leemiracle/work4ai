> 来源: [https://deepwiki.com/deepseek-ai/3FS/13-glossary](https://deepwiki.com/deepseek-ai/3FS/13-glossary)
> DeepWiki deepseek-ai/3FS

# Glossary

  Relevant source files 
 - [.clang-tidy](https://github.com/deepseek-ai/3FS/blob/22fca045/.clang-tidy)
 - [CMakeLists.txt](https://github.com/deepseek-ai/3FS/blob/22fca045/CMakeLists.txt)
 - [README.md](https://github.com/deepseek-ai/3FS/blob/22fca045/README.md?plain=1)
 - [dockerfile/dev.opencloudos9.dockerfile](https://github.com/deepseek-ai/3FS/blob/22fca045/dockerfile/dev.opencloudos9.dockerfile)
 - [docs/design_notes.md](https://github.com/deepseek-ai/3FS/blob/22fca045/docs/design_notes.md?plain=1)
 - [specs/README.md](https://github.com/deepseek-ai/3FS/blob/22fca045/specs/README.md?plain=1)
 - [src/common/net/ib/IBConnect.cc](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/net/ib/IBConnect.cc)
 - [src/common/net/ib/IBConnect.h](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/net/ib/IBConnect.h)
 - [src/common/net/ib/IBSocket.cc](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/net/ib/IBSocket.cc)
 - [src/common/net/ib/IBSocket.h](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/net/ib/IBSocket.h)
 - [src/common/utils/Shuffle.h](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/utils/Shuffle.h)
 - [src/common/utils/SimpleRingBuffer.h](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/utils/SimpleRingBuffer.h)
 - [src/common/utils/UtcTimeSerde.h](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/utils/UtcTimeSerde.h)
 - [src/fbs/meta/Schema.cc](https://github.com/deepseek-ai/3FS/blob/22fca045/src/fbs/meta/Schema.cc)
 - [src/fbs/storage/Common.h](https://github.com/deepseek-ai/3FS/blob/22fca045/src/fbs/storage/Common.h)
 - [src/lib/api/UsrbIo.md](https://github.com/deepseek-ai/3FS/blob/22fca045/src/lib/api/UsrbIo.md?plain=1)
 - [src/meta/components/ChainAllocator.h](https://github.com/deepseek-ai/3FS/blob/22fca045/src/meta/components/ChainAllocator.h)
 - [src/mgmtd/ops/SetChainTableOperation.cc](https://github.com/deepseek-ai/3FS/blob/22fca045/src/mgmtd/ops/SetChainTableOperation.cc)
 - [src/storage/chunk_engine/src/bin/bench.rs](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/src/bin/bench.rs)
 - [src/storage/chunk_engine/src/core/engine.rs](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/src/core/engine.rs)
 - [src/storage/chunk_engine/src/cxx.rs](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/src/cxx.rs)
 - [src/storage/chunk_engine/src/meta/meta_store.rs](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/src/meta/meta_store.rs)
 - [src/storage/chunk_engine/src/utils/aligned.rs](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/src/utils/aligned.rs)
 - [src/storage/store/StorageTargets.cc](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/store/StorageTargets.cc)
 - [src/stubs/CMakeLists.txt](https://github.com/deepseek-ai/3FS/blob/22fca045/src/stubs/CMakeLists.txt)
 - [tests/common/utils/TestShuffle.cc](https://github.com/deepseek-ai/3FS/blob/22fca045/tests/common/utils/TestShuffle.cc)
 - [tests/mgmtd/TestMgmtdOperator.cc](https://github.com/deepseek-ai/3FS/blob/22fca045/tests/mgmtd/TestMgmtdOperator.cc)
 
  This page provides definitions and technical context for 3FS-specific terminology, jargon, and architectural concepts.

 
## Core Architectural Terms

 
### Disaggregated Architecture

 A design where compute and storage resources are scaled independently. In 3FS, this allows thousands of SSDs and hundreds of storage nodes to be accessed by applications as a single, shared pool of storage [README.md9](https://github.com/deepseek-ai/3FS/blob/22fca045/README.md?plain=1#L9-L9)

 
### CRAQ (Chain Replication with Apportioned Queries)

 A consistency model used by the 3FS storage service to ensure strong consistency while maximizing read throughput. It utilizes a "write-all-read-any" approach across a replication chain [README.md10-11](https://github.com/deepseek-ai/3FS/blob/22fca045/README.md?plain=1#L10-L11)

 
 - **Code Pointer**: `hf3fs::storage::StorageOperator` implements the RPC handling for these replication chains.
 
 
### Replication Chain

 A sequence of storage targets (usually across different nodes) that store replicas of the same data chunks.

 
 - **ChainId**: A unique identifier for a replication chain, defined in [src/fbs/storage/Common.h23](https://github.com/deepseek-ai/3FS/blob/22fca045/src/fbs/storage/Common.h#L23-L23)
 - **ChainVer**: A versioning mechanism to handle membership changes within a chain [src/fbs/storage/Common.h24](https://github.com/deepseek-ai/3FS/blob/22fca045/src/fbs/storage/Common.h#L24-L24)
 
 
### Chunk

 The fundamental unit of data storage in 3FS. Files are split into equally sized chunks (typically 1MB or 4MB) and distributed across replication chains [docs/design_notes.md11-12](https://github.com/deepseek-ai/3FS/blob/22fca045/docs/design_notes.md?plain=1#L11-L12)

 
 - **ChunkId**: A unique identifier for a data chunk, often represented as a 128-bit ID [src/fbs/storage/Common.h82-110](https://github.com/deepseek-ai/3FS/blob/22fca045/src/fbs/storage/Common.h#L82-L110)
 - **ChunkEngine**: The underlying storage engine (implemented in Rust) responsible for managing chunks on local SSDs [src/storage/chunk_engine/src/core/engine.rs19-28](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/src/core/engine.rs#L19-L28)
 
 
---

 
## Networking and I/O Concepts

 
### USRBIO (User Space Ring Based I/O)

 A high-performance, asynchronous zero-copy I/O interface that allows applications to bypass the Linux kernel's VFS/FUSE overhead [src/lib/api/UsrbIo.md3-4](https://github.com/deepseek-ai/3FS/blob/22fca045/src/lib/api/UsrbIo.md?plain=1#L3-L4)

 
### Iov (I/O Vector)

 A large shared memory region used for zero-copy data transfer between the application process and the 3FS client. It is registered with the RDMA NIC (InfiniBand/RoCE) [src/lib/api/UsrbIo.md7](https://github.com/deepseek-ai/3FS/blob/22fca045/src/lib/api/UsrbIo.md?plain=1#L7-L7)

 
### Ior (I/O Ring)

 A shared-memory ring buffer used for request submission and completion between the user process and the 3FS client, similar to Linux `io_uring` [src/lib/api/UsrbIo.md9](https://github.com/deepseek-ai/3FS/blob/22fca045/src/lib/api/UsrbIo.md?plain=1#L9-L9)

 
### RDMA (Remote Direct Memory Access)

 The primary transport mechanism for 3FS, supporting both InfiniBand and RoCE.

 
 - **IBSocket**: The core class managing RDMA Queue Pairs (QP) and data transmission [src/common/net/ib/IBSocket.h81](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/net/ib/IBSocket.h#L81-L81)
 - **Memory Registration (MR)**: The process of pinning memory and providing the NIC with a translation table for RDMA operations [src/common/net/ib/IBSocket.cc183](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/net/ib/IBSocket.cc#L183-L183)
 
 
---

 
## Storage Engine Jargon

 
### Target

 A logical storage unit managed by a storage service, usually corresponding to a specific directory on an NVMe SSD [src/storage/store/StorageTargets.cc108-110](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/store/StorageTargets.cc#L108-L110)

 
### MetaStore

 A RocksDB-backed metadata store within the `chunk_engine` that tracks the physical location and state of chunks on a local disk [src/storage/chunk_engine/src/core/engine.rs32-41](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/src/core/engine.rs#L32-L41)

 
### WritingList

 An in-memory structure in the `chunk_engine` that tracks chunks currently being written or updated before they are committed [src/storage/chunk_engine/src/core/engine.rs27-28](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/src/core/engine.rs#L27-L28)

 
---

 
## System Mapping: Natural Language to Code Entities

 The following diagrams map conceptual system operations to specific code classes and functions.

 
### Data Path: Application to SSD

 This diagram shows how a write request flows from the USRBIO interface down to the physical storage.

 
```

```

 **Sources**: [src/lib/api/UsrbIo.md150-165](https://github.com/deepseek-ai/3FS/blob/22fca045/src/lib/api/UsrbIo.md?plain=1#L150-L165) [src/storage/chunk_engine/src/cxx.rs143-148](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/src/cxx.rs#L143-L148) [src/storage/chunk_engine/src/core/engine.rs41-44](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/src/core/engine.rs#L41-L44)

 
### Control Path: Management and Routing

 This diagram shows how the Management Service (`mgmtd`) coordinates cluster state.

 
```

```

 **Sources**: [tests/mgmtd/TestMgmtdOperator.cc49-60](https://github.com/deepseek-ai/3FS/blob/22fca045/tests/mgmtd/TestMgmtdOperator.cc#L49-L60) [docs/design_notes.md7-9](https://github.com/deepseek-ai/3FS/blob/22fca045/docs/design_notes.md?plain=1#L7-L9) [src/fbs/storage/Common.h11-21](https://github.com/deepseek-ai/3FS/blob/22fca045/src/fbs/storage/Common.h#L11-L21)

 
---

 
## Technical Terms Table

 
| Term | Definition | Code Entity |
|---|---|---|
| ETag | A version tag for a chunk to prevent stale writes. | Chunk::raw_etag src/storage/chunk_engine/src/cxx.rs57-59 |
| ChainTable | A table mapping file stripes to specific replication chains. | flat::ChainTableId tests/mgmtd/TestMgmtdOperator.cc108-112 |
| Shuffle Method | A build-time configuration to ensure deterministic std::shuffle behavior across different GCC versions. | SHUFFLE_METHOD CMakeLists.txt30-32 |
| ChecksumInfo | Metadata used to verify data integrity using CRC32C or CRC32. | hf3fs::storage::ChecksumInfo src/fbs/storage/Common.h113-115 |
| NodeId | A unique identifier for any service node (storage, meta, mgmtd) in the cluster. | hf3fs::flat::NodeId src/fbs/storage/Common.h26 |

 **Sources**: [src/storage/chunk_engine/src/cxx.rs](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/src/cxx.rs) [tests/mgmtd/TestMgmtdOperator.cc](https://github.com/deepseek-ai/3FS/blob/22fca045/tests/mgmtd/TestMgmtdOperator.cc) [CMakeLists.txt](https://github.com/deepseek-ai/3FS/blob/22fca045/CMakeLists.txt) [src/fbs/storage/Common.h](https://github.com/deepseek-ai/3FS/blob/22fca045/src/fbs/storage/Common.h)
