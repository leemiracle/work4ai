> 来源: [https://deepwiki.com/deepseek-ai/3FS/9-foundationdb-integration](https://deepwiki.com/deepseek-ai/3FS/9-foundationdb-integration)
> DeepWiki deepseek-ai/3FS

# FoundationDB Integration

  Relevant source files 
 - [docs/design_notes.md](https://github.com/deepseek-ai/3FS/blob/22fca045/docs/design_notes.md?plain=1)
 - [specs/README.md](https://github.com/deepseek-ai/3FS/blob/22fca045/specs/README.md?plain=1)
 - [src/common/kv/mem/MemTransaction.h](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/kv/mem/MemTransaction.h)
 - [src/fdb/FDBTransaction.cc](https://github.com/deepseek-ai/3FS/blob/22fca045/src/fdb/FDBTransaction.cc)
 - [src/lib/api/UsrbIo.md](https://github.com/deepseek-ai/3FS/blob/22fca045/src/lib/api/UsrbIo.md?plain=1)
 - [src/stubs/CMakeLists.txt](https://github.com/deepseek-ai/3FS/blob/22fca045/src/stubs/CMakeLists.txt)
 
  3FS utilizes FoundationDB (FDB) as its primary transactional metadata store. By leveraging FDB's distributed ACID transactions and ordered key-value semantics, 3FS achieves high-performance metadata operations with strong consistency guarantees [docs/design_notes.md9-11](https://github.com/deepseek-ai/3FS/blob/22fca045/docs/design_notes.md?plain=1#L9-L11) The system abstracts interaction with the persistence layer through a KV engine interface, allowing for transaction management, retry logic, and specialized key-value operations like versionstamping.

 
## Architectural Overview

 The metadata service in 3FS is stateless; it acts as a translation layer between filesystem RPCs (e.g., `create`, `mkdir`, `rename`) and FoundationDB transactions [docs/design_notes.md9-11](https://github.com/deepseek-ai/3FS/blob/22fca045/docs/design_notes.md?plain=1#L9-L11) This disaggregated architecture allows metadata services to scale horizontally while FoundationDB handles data durability and concurrency control.

 
### System Entity Mapping

 The following diagram illustrates how high-level metadata concepts map to specific C++ classes and the underlying FDB storage.

 **Metadata Persistence Mapping**

 
```

```

 Sources: [src/fdb/FDBTransaction.cc84-101](https://github.com/deepseek-ai/3FS/blob/22fca045/src/fdb/FDBTransaction.cc#L84-L101) [docs/design_notes.md9-11](https://github.com/deepseek-ai/3FS/blob/22fca045/docs/design_notes.md?plain=1#L9-L11)

 
## Key-Value Engine Abstraction

 3FS does not bind itself exclusively to FoundationDB's C API. Instead, it defines a set of interfaces to manage transactions and key-value operations. This abstraction facilitates testing (via in-memory implementations) and potential support for other backends.

 
 - **`IKVEngine`**: The base interface for the key-value storage engine.
 - **`ITransaction`**: An interface representing a single unit of work. It supports standard operations such as `get`, `set`, `clear`, and `getRange` [common/kv/mem/MemTransaction.h59-75](https://github.com/deepseek-ai/3FS/blob/22fca045/common/kv/mem/MemTransaction.h#L59-L75)
 - **`IReadWriteTransaction`**: Extends `ITransaction` with mutation capabilities, including specialized `setVersionstampedKey` and `setVersionstampedValue` methods [common/kv/mem/MemTransaction.h121-149](https://github.com/deepseek-ai/3FS/blob/22fca045/common/kv/mem/MemTransaction.h#L121-L149)
 
 For a deep dive into these interfaces and the hybrid engine used for caching, see **[FDB Transaction Layer](https://deepwiki.com/deepseek-ai/3FS/9.1-fdb-transaction-layer)**.

 
## Transaction Management and Retries

 Because FoundationDB uses optimistic concurrency control, transactions may fail due to conflicts or transient network issues. 3FS implements a robust retry mechanism within its transaction layer.

 
### Transaction Lifecycle

 
 - **Creation**: A transaction is instantiated via the `FDBKVEngine`.
 - **Execution**: The metadata service performs multiple reads and writes.
 - **Conflict Tracking**: 3FS can manually add read/write conflict ranges using `addReadConflict` [src/fdb/FDBTransaction.cc92](https://github.com/deepseek-ai/3FS/blob/22fca045/src/fdb/FDBTransaction.cc#L92-L92)
 - **Commit**: The transaction attempts to commit. If a conflict is detected (e.g., `error_code_not_committed`), the transaction is retried [src/fdb/FDBTransaction.cc37-42](https://github.com/deepseek-ai/3FS/blob/22fca045/src/fdb/FDBTransaction.cc#L37-L42)
 - **Fault Injection**: For testing robustness, 3FS includes macros to inject random failures during commit or get operations [src/fdb/FDBTransaction.cc54-70](https://github.com/deepseek-ai/3FS/blob/22fca045/src/fdb/FDBTransaction.cc#L54-L70)
 
 **Transaction Execution Flow**

 
```

```

 Sources: [src/fdb/FDBTransaction.cc32-52](https://github.com/deepseek-ai/3FS/blob/22fca045/src/fdb/FDBTransaction.cc#L32-L52) [common/kv/mem/MemTransaction.h151-155](https://github.com/deepseek-ai/3FS/blob/22fca045/common/kv/mem/MemTransaction.h#L151-L155)

 
## Metadata Schema

 3FS maps the filesystem hierarchy into FDB's flat key-value space using specific prefixes. This includes:

 
 - **Inodes (INOD)**: Storing file/directory attributes.
 - **Directory Entries (DENT)**: Mapping filenames to Inode IDs.
 - **Versionstamping**: Utilizing FDB's versionstamp feature to provide strictly increasing transaction versions for metadata consistency [src/fdb/FDBTransaction.cc96-97](https://github.com/deepseek-ai/3FS/blob/22fca045/src/fdb/FDBTransaction.cc#L96-L97)
 
 For detailed information on the key structure and how filesystem operations are implemented, see **[Metadata Schema and Operations](https://deepwiki.com/deepseek-ai/3FS/9.2-metadata-schema-and-operations)**.

 
## Child Pages

 
 - **[FDB Transaction Layer](https://deepwiki.com/deepseek-ai/3FS/9.1-fdb-transaction-layer)**: Detailed documentation of `FDBTransaction`, `FDBKVEngine`, `HybridKvEngine`, and retry strategies.
 - **[Metadata Schema and Operations](https://deepwiki.com/deepseek-ai/3FS/9.2-metadata-schema-and-operations)**: Documentation of the FoundationDB key schema (INOD/DENT prefixes) and `MetaStore` operation implementations.
