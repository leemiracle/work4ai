<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/fission · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api.go](api.go)
- [examples/fission-hellofs/main.go](examples/fission-hellofs/main.go)
- [go.mod](go.mod)
- [go.sum](go.sum)

</details>



## Purpose and Scope

The **fission** repository is a Go library that provides a high-level abstraction for building FUSE (Filesystem in Userspace) filesystems. It handles the low-level FUSE protocol communication with the Linux kernel, exposing an idiomatic Go callback interface that developers implement to create custom filesystems. The library manages `/dev/fuse` device communication, protocol marshalling, and goroutine lifecycle, allowing filesystem implementers to focus on business logic rather than FUSE protocol details.

This document provides a high-level overview of the fission architecture, its core components, and example implementations. For detailed information about specific subsystems, see:
- Core library internals: [Core Library](#2)
- Example filesystem implementations: [Example Implementations](#3)
- Build and development setup: [Development and Build Setup](#5)

**Sources:** [api.go:1-96](), [go.mod:1-11]()

---

## Repository Purpose

Fission solves the complexity of implementing FUSE filesystems by:

1. **Abstracting FUSE protocol details**: Handles binary protocol parsing, struct marshalling, and kernel communication
2. **Providing type-safe interfaces**: 40+ callback methods with structured Go types instead of raw byte buffers
3. **Managing lifecycle**: Automatic goroutine management, buffer pooling, and mount/unmount coordination
4. **Enabling rapid development**: Example implementations demonstrate patterns from minimal (hellofs) to production-ready (s3rofs)

The library is designed as a **reusable core** with **pluggable implementations**. Users implement the `Callbacks` interface to define filesystem behavior, while fission handles all FUSE protocol mechanics.

**Sources:** [api.go:30-83](), [examples/fission-hellofs/main.go:1-273]()

---

## High-Level Architecture

```mermaid
graph TB
    subgraph Kernel["Linux Kernel Space"]
        VFS["Virtual File System"]
        FUSE_K["FUSE Kernel Module<br/>/dev/fuse device"]
    end
    
    subgraph Core["Fission Core Library (github.com/NVIDIA/fission/v3)"]
        Volume["volume.go<br/>Volume interface<br/>DoMount/DoUnmount<br/>devFuseFDReader/Writer"]
        Callbacks["callbacks.go<br/>Protocol Marshalling<br/>InHeader/OutHeader<br/>Request Dispatcher"]
        API["api.go<br/>Callbacks interface<br/>40+ callback methods<br/>FUSE data structures"]
    end
    
    subgraph Impl["User Implementations"]
        RAMFS["fission-ramfs<br/>Full POSIX filesystem<br/>In-memory storage"]
        S3["fission-s3rofs<br/>S3 read-only<br/>2-tier cache"]
        Swift["fission-swiftfs<br/>Swift object storage<br/>Auth management"]
        Hello["fission-hellofs<br/>Minimal example<br/>2 static inodes"]
    end
    
    VFS --> FUSE_K
    FUSE_K -->|"binary protocol"| Volume
    Volume -->|"raw bytes"| Callbacks
    Callbacks -->|"structured types"| API
    API -->|"callback invocation"| RAMFS
    API -->|"callback invocation"| S3
    API -->|"callback invocation"| Swift
    API -->|"callback invocation"| Hello
```

**Fission Architecture**: The library operates as a three-layer translation stack between the Linux kernel's FUSE module and user filesystem implementations. The `volume.go` layer handles device I/O, `callbacks.go` performs protocol marshalling, and `api.go` defines the callback contract.

**Sources:** [api.go:11-95](), Diagram 1, Diagram 2

---

## Core Components and Code Mapping

```mermaid
graph LR
    subgraph api.go["api.go"]
        Volume_IF["Volume interface<br/>DoMount()<br/>DoUnmount()"]
        Callbacks_IF["Callbacks interface<br/>DoLookup()<br/>DoRead()<br/>DoWrite()<br/>...40+ methods"]
        NewVolume["NewVolume()<br/>factory function"]
        Structs["FUSE Data Structures<br/>Attr<br/>InHeader<br/>OutHeader<br/>LookupIn/Out<br/>ReadIn/Out<br/>WriteIn/Out"]
    end
    
    subgraph volume.go["volume.go (internal)"]
        volumeStruct["volumeStruct<br/>implements Volume"]
        DoMount_Impl["DoMount()<br/>fusermount exec<br/>devFuseFDReader start"]
        DoUnmount_Impl["DoUnmount()<br/>cleanup & wait"]
        Reader["devFuseFDReader()<br/>goroutine<br/>read from /dev/fuse"]
        Writer["devFuseFDWriter()<br/>goroutine<br/>write to /dev/fuse"]
    end
    
    subgraph callbacks.go["callbacks.go (internal)"]
        Dispatcher["Request Dispatcher<br/>OpCode switch<br/>call appropriate callback"]
        Marshaller["Protocol Marshaller<br/>parse InHeader<br/>construct OutHeader"]
    end
    
    NewVolume --> volumeStruct
    volumeStruct --> DoMount_Impl
    volumeStruct --> DoUnmount_Impl
    DoMount_Impl --> Reader
    Reader --> Dispatcher
    Dispatcher --> Marshaller
    Marshaller --> Callbacks_IF
    Callbacks_IF -.implemented by.- User["User Implementation<br/>e.g., fission-ramfs"]
    
    Volume_IF -.defines.- volumeStruct
    Structs -.used in.- Callbacks_IF
```

**Code Entity Mapping**: This diagram shows the relationship between the public API surface and internal implementation. Users interact only with `Volume` and `Callbacks` interfaces from `api.go`, while `volume.go` and `callbacks.go` provide the internal machinery.

| Component | File | Key Types/Functions | Visibility |
|-----------|------|---------------------|------------|
| **Public API** | `api.go` | `Volume`, `Callbacks`, `NewVolume()` | Exported |
| **Data Structures** | `api.go` | `Attr`, `InHeader`, `OutHeader`, 40+ request/response structs | Exported |
| **Volume Management** | `volume.go` | `volumeStruct`, `DoMount()`, `DoUnmount()`, `devFuseFDReader()` | Internal |
| **Protocol Layer** | `callbacks.go` | Request dispatcher, marshalling functions | Internal |

**Sources:** [api.go:11-1203](), Diagram 1

---

## Example Implementations Comparison

The repository includes four example implementations that demonstrate different filesystem patterns:

| Implementation | Purpose | Storage Backend | Operations | Complexity |
|----------------|---------|-----------------|------------|------------|
| **fission-hellofs** | Learning example | Static hardcoded data | Read-only, 2 inodes | Minimal |
| **fission-ramfs** | Full POSIX filesystem | In-memory (volatile) | Read/write, xattr, locking | High |
| **fission-s3rofs** | Cloud storage frontend | Amazon S3 | Read-only, cached | Medium |
| **fission-swiftfs** | Object storage frontend | OpenStack Swift | Read-only, cached | Medium |

```mermaid
graph TB
    subgraph HelloFS["fission-hellofs"]
        H_Main["main.go<br/>2 static inodes<br/>rootInodeAttr<br/>helloInodeAttr"]
        H_CB["Callbacks implementation<br/>DoLookup<br/>DoGetAttr<br/>DoRead<br/>DoReadDir"]
    end
    
    subgraph RAMFS["fission-ramfs"]
        R_Main["main.go<br/>globalsStruct<br/>inodeTable<br/>lockSystem"]
        R_CB["callbacks.go<br/>Full POSIX operations<br/>tryLock pattern<br/>xattr support"]
        R_Store["In-Memory Storage<br/>sortedmap<br/>[]byte fileData"]
    end
    
    subgraph S3["fission-s3rofs"]
        S3_Main["main.go<br/>S3 client init<br/>ListObjectsV2<br/>inode enumeration"]
        S3_CB["callbacks.go<br/>Read operations<br/>cache management"]
        S3_Cache["2-Tier Cache<br/>RAM LRU<br/>Disk LRU<br/>GetObject ranges"]
    end
    
    subgraph Swift["fission-swiftfs"]
        SW_Main["main.go<br/>HTTP client<br/>auth token mgmt<br/>container listing"]
        SW_CB["callbacks.go<br/>Read operations<br/>concurrent attrs"]
        SW_Cache["RAM Cache<br/>LRU eviction<br/>HTTP Range"]
    end
    
    H_Main --> H_CB
    R_Main --> R_CB
    R_CB --> R_Store
    S3_Main --> S3_CB
    S3_CB --> S3_Cache
    SW_Main --> SW_CB
    SW_CB --> SW_Cache
    
    H_CB -.implements.- API["fission.Callbacks"]
    R_CB -.implements.- API
    S3_CB -.implements.- API
    SW_CB -.implements.- API
```

**Implementation Patterns**: Each example filesystem implements the `fission.Callbacks` interface but uses different storage backends and concurrency strategies. The hellofs example demonstrates the minimum viable implementation, while ramfs shows a full-featured POSIX filesystem with sophisticated locking.

**Sources:** [examples/fission-hellofs/main.go:1-273](), Diagram 3

---

## FUSE Request Flow

```mermaid
sequenceDiagram
    participant App as "User Application<br/>(ls, cat, etc.)"
    participant VFS as "VFS Layer"
    participant Kernel as "FUSE Kernel<br/>/dev/fuse"
    participant Reader as "devFuseFDReader()<br/>goroutine"
    participant Dispatcher as "callbacks.go<br/>dispatcher"
    participant UserFS as "User Implementation<br/>(e.g., DoRead)"
    
    App->>VFS: syscall (e.g., read())
    VFS->>Kernel: FUSE request
    Kernel->>Reader: write binary request
    Reader->>Reader: parse InHeader
    Reader->>Dispatcher: dispatch by OpCode
    Dispatcher->>Dispatcher: unmarshal request struct
    Dispatcher->>UserFS: invoke callback (e.g., DoRead)
    UserFS->>UserFS: perform operation
    UserFS-->>Dispatcher: return response + errno
    Dispatcher->>Dispatcher: marshal OutHeader
    Dispatcher->>Kernel: write binary response
    Kernel-->>VFS: FUSE response
    VFS-->>App: syscall return
```

**Request Processing Pipeline**: When a user application performs a filesystem operation, the request flows through the kernel to fission's reader goroutine, which dispatches it to the appropriate callback. The response follows the reverse path back to the application.

**Sources:** [api.go:17-27](), Diagram 2

---

## Key Features

### Protocol Version Support

Fission supports FUSE protocol versions 7.17 through 7.44 (Linux kernels 3.1 through 6.16), with automatic version negotiation during mount via the `DoInit()` callback.

**Sources:** [api.go:97-134]()

### Operation Coverage

The library exposes 40+ FUSE operations through the `Callbacks` interface:

| Category | Operations |
|----------|------------|
| **Inode Operations** | `DoLookup`, `DoGetAttr`, `DoSetAttr`, `DoReadLink`, `DoAccess`, `DoStatX` |
| **File Operations** | `DoOpen`, `DoRead`, `DoWrite`, `DoRelease`, `DoFSync`, `DoFAllocate`, `DoLSeek` |
| **Directory Operations** | `DoOpenDir`, `DoReadDir`, `DoReadDirPlus`, `DoReleaseDir`, `DoFSyncDir` |
| **Namespace Operations** | `DoMkNod`, `DoMkDir`, `DoUnlink`, `DoRmDir`, `DoRename`, `DoRename2`, `DoLink`, `DoSymLink`, `DoCreate` |
| **Extended Attributes** | `DoSetXAttr`, `DoGetXAttr`, `DoListXAttr`, `DoRemoveXAttr` |
| **File Locking** | `DoGetLK`, `DoSetLK`, `DoSetLKW` |
| **Lifecycle** | `DoInit`, `DoDestroy`, `DoForget`, `DoBatchForget`, `DoInterrupt` |
| **Special** | `DoStatFS`, `DoFlush`, `DoBMap`, `DoPoll` |

Not all implementations need to support all operations. Read-only filesystems like s3rofs implement only read operations and return `syscall.ENOSYS` for write operations.

**Sources:** [api.go:40-83]()

### Concurrency and Buffer Management

- **Goroutine Management**: `devFuseFDReader()` spawns per-request handler goroutines, coordinated via `sync.WaitGroup`
- **Buffer Pooling**: `sync.Pool` for read buffers reduces GC pressure in high-throughput scenarios
- **Thread Safety**: User implementations are responsible for their own locking; fission callbacks may be invoked concurrently

**Sources:** Diagram 5

### Mount Options

The `NewVolume()` factory function accepts configuration parameters:

```go
NewVolume(
    volumeName string,           // Displayed in mount output
    mountpointDirPath string,    // Where to mount
    fuseSubtype string,          // Filesystem type suffix (e.g., "fission.ramfs")
    maxRead uint32,              // Maximum read size (typically 1MiB)
    maxWrite uint32,             // Maximum write size (0 = read-only)
    defaultPermissions bool,     // Enable kernel permission checking
    allowOther bool,             // Allow non-owner access
    callbacks Callbacks,         // User implementation
    logger *log.Logger,          // For debugging
    errChan chan error,          // Mount lifecycle errors
)
```

**Sources:** [api.go:85-95](), [examples/fission-hellofs/main.go:249]()

---

## Dependencies

```mermaid
graph TB
    Core["fission/v3<br/>Core Library"]
    
    SM["github.com/NVIDIA/sortedmap<br/>v1.30.0<br/>LLRB tree for directories"]
    Sys["golang.org/x/sys<br/>v0.13.0<br/>System calls & FUSE protocol"]
    
    subgraph AWS["AWS SDK v2 (S3 Example Only)"]
        SDK["aws-sdk-go-v2<br/>v1.21.2"]
        Config["config v1.19.1"]
        Creds["credentials v1.13.43"]
        S3Service["service/s3 v1.40.2"]
    end
    
    Core --> SM
    Core --> Sys
    
    S3Example["fission-s3rofs"] --> Core
    S3Example --> SDK
    S3Example --> Config
    S3Example --> Creds
    S3Example --> S3Service
    
    RAMExample["fission-ramfs"] --> Core
    RAMExample --> SM
    
    SwiftExample["fission-swiftfs"] --> Core
    SwiftExample --> SM
    
    HelloExample["fission-hellofs"] --> Core
```

**Dependency Graph**: The core library has minimal dependencies (sortedmap for directory management and golang.org/x/sys for syscalls). Example implementations add dependencies as needed (e.g., AWS SDK for S3 integration).

| Package | Version | Purpose | Used By |
|---------|---------|---------|---------|
| `github.com/NVIDIA/sortedmap` | v1.30.0 | LLRB tree for ordered directory entries | Core, ramfs, s3rofs, swiftfs |
| `golang.org/x/sys` | v0.13.0 | Linux syscalls, FUSE protocol constants | Core |
| `github.com/aws/aws-sdk-go-v2` | v1.21.2 | AWS SDK core framework | s3rofs only |
| `github.com/aws/aws-sdk-go-v2/service/s3` | v1.40.2 | S3 client for GetObject/ListObjects | s3rofs only |

**Sources:** [go.mod:1-30](), [go.sum:1-52](), Diagram 4

---

## Getting Started

To use fission in your project:

1. **Import the library**:
   ```go
   import "github.com/NVIDIA/fission/v3"
   ```

2. **Implement the `Callbacks` interface**: Define filesystem behavior by implementing callback methods for the operations you support.

3. **Create a `Volume`**: Call `fission.NewVolume()` with your callbacks and configuration.

4. **Mount the filesystem**: Invoke `volume.DoMount()` to begin handling requests.

5. **Handle signals**: Wait for termination signals, then call `volume.DoUnmount()` to cleanly unmount.

The `fission-hellofs` example demonstrates this pattern with minimal code (approximately 600 lines including boilerplate), showing only the essential operations for a read-only filesystem with static content.

**Sources:** [examples/fission-hellofs/main.go:75-273]()

---

