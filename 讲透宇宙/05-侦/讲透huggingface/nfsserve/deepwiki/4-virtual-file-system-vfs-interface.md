<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/nfsserve · page 4 Virtual File System (VFS) Interface · fetched 2026-10-26 -->

# Virtual File System (VFS) Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/vfs.rs](src/vfs.rs)

</details>



The Virtual File System (VFS) interface is the primary abstraction layer in `nfsserve`. It decouples the NFS protocol logic from the underlying storage mechanism. By implementing a single Rust trait, developers can expose any hierarchical data source—whether in-memory, on a local disk, or backed by a remote API—as a mountable NFS export.

### The NFSFileSystem Trait

The core of the VFS is the `NFSFileSystem` trait [src/vfs.rs:95-95](). This trait defines the contract for all filesystem operations, such as looking up files, reading data, and managing attributes. It is designed to be asynchronous, allowing implementations to perform I/O without blocking the RPC server's event loop.

For a complete breakdown of every method and its requirements, see the [NFSFileSystem Trait Reference](#4.1).

### File Handle Generation Scheme

NFS relies on "File Handles" (FH) to uniquely identify files across requests. In `nfsserve`, these handles are automatically managed to simplify implementation for the developer.

1.  **File IDs**: Implementations only need to manage 64-bit `fileid3` values (similar to Unix inodes) [src/vfs.rs:71-71]().
2.  **Generation Number**: A global `GENERATION_NUMBER` is initialized at server startup using the current system time [src/vfs.rs:49-59]().
3.  **Opaque FH**: The system combines the `GENERATION_NUMBER` and the `fileid3` to create a 128-bit opaque handle [src/vfs.rs:72-75](). This ensures that if the server restarts, old client handles safely expire (stale handles).

### VFS Component Interaction

The following diagram illustrates how the VFS interface bridges the gap between the NFS protocol handlers and concrete storage implementations.

**VFS Integration Architecture**
```mermaid
graph TD
    subgraph "Protocol Space (NFS v3)"
        [nfs_handler.rs] -- "calls" --> [NFSFileSystem]
    end

    subgraph "Abstraction Layer (VFS)"
        [NFSFileSystem] -- "identifies by" --> [fileid3]
        [NFSFileSystem] -- "uses" --> [GENERATION_NUMBER]
        [NFSFileSystem] -- "returns" --> [fattr3]
    end

    subgraph "Implementation Space"
        [NFSFileSystem] <|-- [DemoFS]
        [NFSFileSystem] <|-- [MirrorFS]
        [MirrorFS] -- "uses" --> [fs_util.rs]
    end

    style [NFSFileSystem] stroke-width:4px
```
Sources: [src/vfs.rs:49-59](), [src/vfs.rs:95-95](), [src/nfs_handler.rs:1-20]()

### Concrete Implementations

The codebase provides two reference implementations that demonstrate how to fulfill the `NFSFileSystem` contract:

| Implementation | Purpose | Key Features |
| :--- | :--- | :--- |
| **DemoFS** | In-memory testing | Uses `FSEntry` and `FSContents` to store data in a `Vec`. Ideal for ephemeral mocks. |
| **MirrorFS** | Local disk proxy | Uses `intaglio` for path interning and `std::fs` for actual I/O. Maps local paths to `fileid3`. |

*   For details on the in-memory implementation, see [DemoFS — In-Memory Filesystem](#4.2).
*   For details on the local disk proxy, see [MirrorFS — Local Filesystem Proxy](#4.3).

### Utility Pipeline

Implementing a filesystem often involves repetitive tasks like converting `std::fs::Metadata` into NFS-compatible `fattr3` structures or handling Unix permission masks. The `fs_util` module provides these common helpers.

**Metadata Conversion Flow**
```mermaid
graph LR
    subgraph "Host OS"
        [std::fs::Metadata]
    end

    subgraph "fs_util.rs"
        [metadata_to_fattr3]
        [mode_unmask]
    end

    subgraph "NFS Wire Format"
        [fattr3]
    end

    [std::fs::Metadata] --> [metadata_to_fattr3]
    [metadata_to_fattr3] --> [mode_unmask]
    [mode_unmask] --> [fattr3]
```
Sources: [src/fs_util.rs:1-50]()

For a guide on these helper functions, see [Filesystem Utilities (fs_util)](#4.4).

### Implementation Requirements
*   **Speed**: Methods like `getattr` and `lookup` must be highly optimized as they are called frequently by NFS clients [src/vfs.rs:91-91]().
*   **Pagination**: `readdir` uses a `start_after` ID rather than complex cookies to simplify stateless operation [src/vfs.rs:79-82]().
*   **Reserved IDs**: The `fileid` 0 is reserved and must not be used by any implementation [src/vfs.rs:93-93]().

Sources: [src/vfs.rs:49-107](), [src/vfs.rs:168-173]()

---

