<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/fission · page 3 Example Implementations · fetched 2026-10-26 -->

# Example Implementations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/fission-hellofs/main.go](examples/fission-hellofs/main.go)
- [examples/fission-ramfs/main.go](examples/fission-ramfs/main.go)
- [examples/fission-s3rofs/main.go](examples/fission-s3rofs/main.go)
- [examples/fission-swiftfs/main.go](examples/fission-swiftfs/main.go)

</details>



## Purpose and Scope

This document provides an overview of the four example filesystem implementations included in the fission repository. Each example demonstrates different patterns for implementing the `Callbacks` interface (see [API Design and Interfaces](#2.1)) and showcases various use cases from minimal learning examples to production-ready cloud storage filesystems.

For detailed documentation on individual implementations, see:
- [fission-ramfs](#3.1) - Full-featured read-write filesystem
- [fission-s3rofs](#3.2) - S3-backed read-only filesystem  
- [fission-swiftfs](#3.3) - Swift object storage filesystem
- [fission-hellofs](#3.4) - Minimal example

For information about the core library these implementations use, see [Core Library](#2).

---

## Implementation Comparison

The following table summarizes the key characteristics of each example implementation:

| Implementation | Storage Backend | Read/Write | Persistence | Cache Strategy | Primary Use Case |
|---------------|----------------|------------|-------------|----------------|------------------|
| fission-ramfs | In-memory maps | Read-Write | Volatile | None (all in RAM) | Full POSIX filesystem testing |
| fission-s3rofs | Amazon S3 | Read-Only | Persistent | 2-tier (RAM + Disk) | Cloud object storage access |
| fission-swiftfs | Swift Storage | Read-Only | Persistent | 1-tier (RAM only) | OpenStack Swift access |
| fission-hellofs | Static data | Read-Only | Static | None | Learning the API |

### Lines of Code

| Implementation | Main File LOC | Callbacks File LOC | Total Complexity |
|---------------|--------------|-------------------|------------------|
| fission-ramfs | ~356 | ~2000+ | Highest |
| fission-s3rofs | ~510 | ~800+ | High |
| fission-swiftfs | ~572 | ~700+ | Medium |
| fission-hellofs | ~296 | ~200+ | Lowest |

**Sources:** [examples/fission-ramfs/main.go](), [examples/fission-s3rofs/main.go](), [examples/fission-swiftfs/main.go](), [examples/fission-hellofs/main.go]()

---

## Architecture Overview

### Interface Implementation Pattern

All four implementations follow the same architectural pattern: they implement the `Callbacks` interface and delegate lifecycle management to the core library's `Volume`.

```mermaid
graph TB
    subgraph "Fission Core Library"
        Volume["fission.Volume<br/>(volume.go)"]
        Callbacks["Callbacks Interface<br/>(api.go)"]
    end
    
    subgraph "Implementation Packages"
        RAMFS["fission-ramfs<br/>globalsStruct"]
        S3RO["fission-s3rofs<br/>globalsStruct"]
        Swift["fission-swiftfs<br/>globalsStruct"]
        Hello["fission-hellofs<br/>globalsStruct"]
    end
    
    Volume -->|"calls callbacks on"| Callbacks
    
    RAMFS -.->|"implements"| Callbacks
    S3RO -.->|"implements"| Callbacks
    Swift -.->|"implements"| Callbacks
    Hello -.->|"implements"| Callbacks
    
    RAMFS -->|"fission.NewVolume()"| Volume
    S3RO -->|"fission.NewVolume()"| Volume
    Swift -->|"fission.NewVolume()"| Volume
    Hello -->|"fission.NewVolume()"| Volume
```

**Sources:** [examples/fission-ramfs/main.go:89-105](), [examples/fission-s3rofs/main.go:129-143](), [examples/fission-swiftfs/main.go:100-118](), [examples/fission-hellofs/main.go:59-71]()

---

## Global State Structure Comparison

Each implementation maintains its state in a `globalsStruct` but with different contents based on requirements.

### State Structure Diagram

```mermaid
graph LR
    subgraph "fission-ramfs"
        RAM_G["globalsStruct"]
        RAM_G --> RAM_TL["tryLock<br/>*tryLockStruct"]
        RAM_G --> RAM_IM["inodeMap<br/>map[uint64]*inodeStruct"]
        RAM_G --> RAM_FH["fhMap<br/>map[uint64]uint32"]
        RAM_G --> RAM_V["volume<br/>fission.Volume"]
    end
    
    subgraph "fission-s3rofs"
        S3_G["globalsStruct"]
        S3_G --> S3_CFG["config<br/>*configStruct"]
        S3_G --> S3_CLI["s3Client<br/>*s3.Client"]
        S3_G --> S3_IT["inodeTable<br/>[]*inodeStruct"]
        S3_G --> S3_FCM["fileCacheMap<br/>map[cacheLineTagStruct]*"]
        S3_G --> S3_RCM["ramCacheMap<br/>map[cacheLineTagStruct]*"]
        S3_G --> S3_V["volume<br/>fission.Volume"]
    end
    
    subgraph "fission-swiftfs"
        SW_G["globalsStruct"]
        SW_G --> SW_CFG["config<br/>*configStruct"]
        SW_G --> SW_AUTH["authToken<br/>string"]
        SW_G --> SW_FIM["fileInodeMap<br/>map[uint64]*fileInodeStruct"]
        SW_G --> SW_RCM["readCacheMap<br/>map[cacheLineTagStruct]*"]
        SW_G --> SW_V["volume<br/>fission.Volume"]
    end
    
    subgraph "fission-hellofs"
        H_G["globalsStruct"]
        H_G --> H_RA["rootInodeAttr<br/>*fission.Attr"]
        H_G --> H_HA["helloInodeAttr<br/>*fission.Attr"]
        H_G --> H_DE["dirEnt<br/>[]fission.DirEnt"]
        H_G --> H_V["volume<br/>fission.Volume"]
    end
```

**Sources:** [examples/fission-ramfs/main.go:89-105](), [examples/fission-s3rofs/main.go:129-143](), [examples/fission-swiftfs/main.go:100-118](), [examples/fission-hellofs/main.go:59-71]()

---

## Initialization Patterns

### Mount Initialization Flow

```mermaid
sequenceDiagram
    participant M as main()
    participant GS as globalsStruct
    participant V as fission.Volume
    participant K as Kernel FUSE
    
    M->>GS: Initialize state structures
    M->>GS: Setup storage backend
    Note over GS: ramfs: inodeMap<br/>s3rofs: enumerate S3<br/>swiftfs: list container<br/>hellofs: static data
    M->>V: fission.NewVolume()
    M->>V: DoMount()
    V->>K: Mount FUSE filesystem
    K-->>V: INIT handshake
    V->>GS: DoInit() callback
    GS-->>V: InitOut flags
    Note over M: Wait for signal
    M->>V: DoUnmount()
    V->>K: Unmount
```

### Initialization Code Locations

| Implementation | Volume Creation | DoMount | Cleanup |
|---------------|----------------|---------|---------|
| fission-ramfs | [main.go:197]() | [main.go:199]() | [main.go:216]() |
| fission-s3rofs | [main.go:447]() | [main.go:449]() | [main.go:465]() |
| fission-swiftfs | [main.go:406]() | [main.go:408]() | [main.go:425]() |
| fission-hellofs | [main.go:249]() | [main.go:251]() | [main.go:268]() |

**Sources:** [examples/fission-ramfs/main.go:197-220](), [examples/fission-s3rofs/main.go:447-476](), [examples/fission-swiftfs/main.go:406-429](), [examples/fission-hellofs/main.go:249-272]()

---

## Data Structure Patterns

### Inode Representation

Each implementation uses different strategies for representing filesystem inodes:

```mermaid
graph TB
    subgraph "fission-ramfs"
        RAM_IS["inodeStruct"]
        RAM_IS --> RAM_TL["tryLock<br/>*tryLockStruct"]
        RAM_IS --> RAM_ATTR["attr<br/>fission.Attr"]
        RAM_IS --> RAM_XM["xattrMap<br/>sortedmap.LLRBTree"]
        RAM_IS --> RAM_DEM["dirEntryMap<br/>sortedmap.LLRBTree"]
        RAM_IS --> RAM_FD["fileData<br/>[]byte"]
        RAM_IS --> RAM_SD["symlinkData<br/>[]byte"]
    end
    
    subgraph "fission-s3rofs"
        S3_IS["inodeStruct"]
        S3_IS --> S3_INO["inodeNumber<br/>uint64"]
        S3_IS --> S3_SZ["size<br/>uint64"]
        S3_IS --> S3_LM["lastModified<br/>time.Time"]
        S3_IS --> S3_MODE["mode<br/>uint32"]
        S3_IS --> S3_DT["dirTable<br/>sortedmap.LLRBTree"]
        S3_IS --> S3_OK["objectKey<br/>string"]
    end
    
    subgraph "fission-swiftfs"
        SW_FIS["fileInodeStruct"]
        SW_FIS --> SW_RWM["sync.RWMutex"]
        SW_FIS --> SW_ON["objectName<br/>string"]
        SW_FIS --> SW_INO["inodeNumber<br/>uint64"]
        SW_FIS --> SW_CA["cachedAttr<br/>*fission.Attr"]
    end
    
    subgraph "fission-hellofs"
        H_ATTR["Static Attrs"]
        H_ATTR --> H_RA["rootInodeAttr"]
        H_ATTR --> H_HA["helloInodeAttr"]
    end
```

**Sources:** [examples/fission-ramfs/main.go:73-80](), [examples/fission-s3rofs/main.go:100-108](), [examples/fission-swiftfs/main.go:81-86](), [examples/fission-hellofs/main.go:66-67]()

---

## Storage Backend Integration

### Backend Access Patterns

```mermaid
graph LR
    subgraph "Application Layer"
        READ["Read Request"]
        WRITE["Write Request"]
        LOOKUP["Lookup Request"]
    end
    
    subgraph "fission-ramfs"
        RAM_CB["callbacks.go"]
        RAM_MAP["inodeMap<br/>fileData []byte"]
        READ -->|"DoRead"| RAM_CB
        WRITE -->|"DoWrite"| RAM_CB
        LOOKUP -->|"DoLookup"| RAM_CB
        RAM_CB --> RAM_MAP
    end
    
    subgraph "fission-s3rofs"
        S3_CB["callbacks.go"]
        S3_CACHE["2-tier Cache"]
        S3_SDK["aws-sdk-go-v2"]
        S3_STOR["Amazon S3"]
        READ -->|"DoRead"| S3_CB
        LOOKUP -->|"DoLookup"| S3_CB
        S3_CB --> S3_CACHE
        S3_CACHE -->|"miss"| S3_SDK
        S3_SDK --> S3_STOR
    end
    
    subgraph "fission-swiftfs"
        SW_CB["callbacks.go"]
        SW_CACHE["RAM Cache"]
        SW_HTTP["http.Client"]
        SW_STOR["Swift Storage"]
        READ -->|"DoRead"| SW_CB
        LOOKUP -->|"DoLookup"| SW_CB
        SW_CB --> SW_CACHE
        SW_CACHE -->|"miss"| SW_HTTP
        SW_HTTP --> SW_STOR
    end
    
    subgraph "fission-hellofs"
        H_CB["callbacks.go"]
        H_DATA["Static Arrays"]
        READ -->|"DoRead"| H_CB
        LOOKUP -->|"DoLookup"| H_CB
        H_CB --> H_DATA
    end
```

**Sources:** [examples/fission-ramfs/callbacks.go](), [examples/fission-s3rofs/callbacks.go](), [examples/fission-swiftfs/callbacks.go](), [examples/fission-hellofs/callbacks.go]()

---

## Callback Implementation Coverage

The following table shows which FUSE callbacks are implemented in each example:

| Callback Category | ramfs | s3rofs | swiftfs | hellofs |
|------------------|-------|--------|---------|---------|
| **Init/Destroy** | ✓ | ✓ | ✓ | ✓ |
| DoInit | ✓ | ✓ | ✓ | ✓ |
| DoDestroy | ✓ | ✓ | ✓ | ✓ |
| **Lookup/Stat** | ✓ | ✓ | ✓ | ✓ |
| DoLookup | ✓ | ✓ | ✓ | ✓ |
| DoGetAttr | ✓ | ✓ | ✓ | ✓ |
| DoSetAttr | ✓ | - | - | - |
| **File I/O** | ✓ | ✓ | ✓ | ✓ |
| DoOpen | ✓ | ✓ | ✓ | ✓ |
| DoRead | ✓ | ✓ | ✓ | ✓ |
| DoWrite | ✓ | - | - | - |
| DoRelease | ✓ | ✓ | ✓ | ✓ |
| **Directory Ops** | ✓ | ✓ | ✓ | ✓ |
| DoReadDir | ✓ | ✓ | ✓ | ✓ |
| DoReadDirPlus | ✓ | ✓ | ✓ | ✓ |
| DoMkDir | ✓ | - | - | - |
| DoRmDir | ✓ | - | - | - |
| **Creation** | ✓ | - | - | - |
| DoCreate | ✓ | - | - | - |
| DoMkNod | ✓ | - | - | - |
| DoSymlink | ✓ | - | - | - |
| **Deletion** | ✓ | - | - | - |
| DoUnlink | ✓ | - | - | - |
| **Extended Attrs** | ✓ | - | - | - |
| DoGetXAttr | ✓ | - | - | - |
| DoSetXAttr | ✓ | - | - | - |
| DoListXAttr | ✓ | - | - | - |
| DoRemoveXAttr | ✓ | - | - | - |
| **Links** | ✓ | - | - | - |
| DoLink | ✓ | - | - | - |
| DoRename | ✓ | - | - | - |
| **Other** | ✓ | ✓ | ✓ | ✓ |
| DoStatFS | ✓ | ✓ | ✓ | ✓ |
| DoFlush | ✓ | ✓ | ✓ | ✓ |
| DoFSync | ✓ | ✓ | ✓ | ✓ |
| DoAccess | ✓ | ✓ | ✓ | ✓ |

✓ = Implemented, - = Returns `syscall.ENOSYS` or similar

**Sources:** [examples/fission-ramfs/callbacks.go](), [examples/fission-s3rofs/callbacks.go](), [examples/fission-swiftfs/callbacks.go](), [examples/fission-hellofs/callbacks.go]()

---

## Configuration and Dependencies

### External Dependencies by Implementation

```mermaid
graph TB
    subgraph "fission-ramfs"
        RAM["main.go"]
        RAM --> FISSION1["github.com/NVIDIA/fission/v3"]
        RAM --> SM1["github.com/NVIDIA/sortedmap"]
        RAM --> SYS1["golang.org/x/sys/unix"]
    end
    
    subgraph "fission-s3rofs"
        S3["main.go"]
        S3 --> FISSION2["github.com/NVIDIA/fission/v3"]
        S3 --> SM2["github.com/NVIDIA/sortedmap"]
        S3 --> AWS_CFG["aws-sdk-go-v2/config"]
        S3 --> AWS_CRED["aws-sdk-go-v2/credentials"]
        S3 --> AWS_S3["aws-sdk-go-v2/service/s3"]
        S3 --> SYS2["golang.org/x/sys/unix"]
    end
    
    subgraph "fission-swiftfs"
        SW["main.go"]
        SW --> FISSION3["github.com/NVIDIA/fission/v3"]
        SW --> SM3["github.com/NVIDIA/sortedmap"]
        SW --> HTTP["net/http"]
        SW --> SYS3["golang.org/x/sys/unix"]
    end
    
    subgraph "fission-hellofs"
        H["main.go"]
        H --> FISSION4["github.com/NVIDIA/fission/v3"]
        H --> SYS4["golang.org/x/sys/unix"]
    end
```

### Configuration Methods

| Implementation | Config Source | Key Parameters |
|---------------|--------------|----------------|
| fission-ramfs | Command-line args | `<mount_point>` |
| fission-s3rofs | JSON config file | `S3Endpoint`, `S3Bucket`, `S3Prefix`, cache settings |
| fission-swiftfs | JSON config file | `ContainerURL`, `AuthURL`, `AuthToken`, cache settings |
| fission-hellofs | Command-line args | `<mount_point>` |

**Sources:** [examples/fission-ramfs/main.go:119-122](), [examples/fission-s3rofs/main.go:82-98](), [examples/fission-swiftfs/main.go:62-73](), [examples/fission-hellofs/main.go:83-86]()

---

## Concurrency Models

### Locking Strategy Comparison

```mermaid
graph TB
    subgraph "fission-ramfs"
        RAM_LOCK["Locking Strategy"]
        RAM_LOCK --> RAM_GL["Global tryLock<br/>globals.tryLock"]
        RAM_LOCK --> RAM_IL["Per-Inode tryLock<br/>inodeStruct.tryLock"]
        RAM_LOCK --> RAM_GLS["grantedLockSetStruct<br/>Tracks acquired locks"]
        RAM_LOCK --> RAM_RESTART["Restart on Contention<br/>freeAll() + retry"]
    end
    
    subgraph "fission-s3rofs"
        S3_LOCK["Locking Strategy"]
        S3_LOCK --> S3_MUTEX["globals.Mutex<br/>Protects cache maps"]
        S3_LOCK --> S3_WG["WaitGroup per CacheLine<br/>Prevents duplicate fetches"]
        S3_LOCK --> S3_LRU["LRU List Operations<br/>Protected by Mutex"]
    end
    
    subgraph "fission-swiftfs"
        SW_LOCK["Locking Strategy"]
        SW_LOCK --> SW_MUTEX["globals.Mutex<br/>Protects auth + cache"]
        SW_LOCK --> SW_AUTHWG["authWG<br/>Token fetch coordination"]
        SW_LOCK --> SW_RWMUTEX["fileInode.RWMutex<br/>Lazy attr loading"]
        SW_LOCK --> SW_WG["Cache WaitGroup<br/>Per-line coordination"]
    end
    
    subgraph "fission-hellofs"
        H_LOCK["Locking Strategy"]
        H_LOCK --> H_NONE["No Locks<br/>Read-only static data"]
    end
```

**Sources:** [examples/fission-ramfs/main.go:65-71](), [examples/fission-ramfs/main.go:234-309](), [examples/fission-s3rofs/main.go:129-143](), [examples/fission-swiftfs/main.go:81-86](), [examples/fission-swiftfs/main.go:100-118]()

---

## Init Flags Configuration

Each implementation declares which FUSE features it supports via `InitOut` flags returned from `DoInit()`:

### Init Flags by Implementation

| Flag | ramfs | s3rofs | swiftfs | hellofs | Purpose |
|------|-------|--------|---------|---------|---------|
| `InitFlagsAsyncRead` | ✓ | ✓ | ✓ | ✓ | Enable async reads |
| `InitFlagsFileOps` | ✓ | ✓ | ✓ | ✓ | File handle operations |
| `InitFlagsAtomicOTrunc` | ✓ | - | - | ✓ | Atomic open+truncate |
| `InitFlagsBigWrites` | ✓ | - | - | - | Large write support |
| `InitFlagsAutoInvalData` | ✓ | - | - | ✓ | Auto invalidate data |
| `InitFlagsDoReadDirPlus` | ✓ | ✓ | ✓ | ✓ | ReadDirPlus support |
| `InitFlagsReaddirplusAuto` | ✓ | ✓ | ✓ | ✓ | Auto ReadDirPlus |
| `InitFlagsParallelDirops` | ✓ | ✓ | ✓ | ✓ | Parallel dir ops |
| `InitFlagsMaxPages` | ✓ | ✓ | ✓ | ✓ | Max pages support |
| `InitFlagsExplicitInvalData` | ✓ | ✓ | ✓ | ✓ | Explicit invalidation |
| `InitFlagsNoOpendirSupport` | - | ✓ | ✓ | - | No DoOpenDir needed |

**Constants:**
- ramfs: [main.go:25-35]()
- s3rofs: [main.go:37-45]()
- swiftfs: [main.go:31-39]()
- hellofs: [main.go:22-32]()

**Sources:** [examples/fission-ramfs/main.go:25-35](), [examples/fission-s3rofs/main.go:37-45](), [examples/fission-swiftfs/main.go:31-39](), [examples/fission-hellofs/main.go:22-32]()

---

## Cache Architecture

### Cache Type and Strategy

```mermaid
graph TB
    subgraph "No Caching"
        H["fission-hellofs"]
        H --> H_STATIC["Static Data<br/>No cache needed"]
        
        RAM["fission-ramfs"]
        RAM --> RAM_MEM["All in Memory<br/>No cache needed"]
    end
    
    subgraph "Single-Tier Cache"
        SW["fission-swiftfs"]
        SW --> SW_LRU["readCacheLRU<br/>*list.List"]
        SW --> SW_MAP["readCacheMap<br/>map[cacheLineTagStruct]*cacheLineStruct"]
        SW_LRU -.->|"eviction"| SW_MAP
        SW --> SW_HTTP["Swift HTTP API"]
    end
    
    subgraph "Two-Tier Cache"
        S3["fission-s3rofs"]
        S3 --> S3_RAM["RAM Cache Tier"]
        S3_RAM --> S3_RLRU["ramCacheLRU<br/>*list.List"]
        S3_RAM --> S3_RMAP["ramCacheMap<br/>map[cacheLineTagStruct]*ramCacheLineStruct"]
        
        S3 --> S3_FILE["File Cache Tier"]
        S3_FILE --> S3_FLRU["fileCacheLRU<br/>*list.List"]
        S3_FILE --> S3_FMAP["fileCacheMap<br/>map[cacheLineTagStruct]*fileCacheLineStruct"]
        
        S3_RAM -->|"evict to"| S3_FILE
        S3_FILE -->|"evict to"| S3_S3["Amazon S3"]
    end
```

### Cache Line Structure

| Implementation | Tag Structure | Content Storage | Synchronization |
|---------------|--------------|-----------------|-----------------|
| s3rofs | `inodeNumber` + `lineNumber` | RAM: `[]byte`, File: file path | `sync.WaitGroup` per line |
| swiftfs | `inodeNumber` + `lineNumber` | RAM: `[]byte` | `sync.WaitGroup` per line |

**Sources:** [examples/fission-s3rofs/main.go:110-127](), [examples/fission-swiftfs/main.go:88-98]()

---

## Use Case Summary

### When to Use Each Implementation

```mermaid
graph TB
    USECASE["Use Case Selection"]
    
    USECASE --> Q1{"Persistent<br/>Storage?"}
    Q1 -->|"No"| Q2{"Full POSIX<br/>Support?"}
    Q2 -->|"Yes"| RAMFS["fission-ramfs<br/>Full-featured testing"]
    Q2 -->|"No"| HELLOFS["fission-hellofs<br/>Learning/prototyping"]
    
    Q1 -->|"Yes"| Q3{"Storage<br/>Backend?"}
    Q3 -->|"Amazon S3"| S3ROFS["fission-s3rofs<br/>S3 object access"]
    Q3 -->|"Swift"| SWIFTFS["fission-swiftfs<br/>Swift object access"]
    Q3 -->|"Other"| CUSTOM["Custom Implementation<br/>Follow ramfs pattern"]
```

### Recommended Starting Point by Goal

| Goal | Start With | Reason |
|------|-----------|--------|
| Learn the fission API | hellofs | Minimal code, clear structure |
| Implement read-write filesystem | ramfs | Complete example with all operations |
| Add S3 backend | s3rofs | Two-tier cache pattern, enumeration strategy |
| Add HTTP-based storage | swiftfs | Authentication, single-tier cache |
| Test FUSE operations | ramfs | Supports all POSIX operations |
| Mount existing data | s3rofs or swiftfs | Read-only, efficient caching |

**Sources:** [examples/fission-hellofs/main.go](), [examples/fission-ramfs/main.go](), [examples/fission-s3rofs/main.go](), [examples/fission-swiftfs/main.go]()

---

## Command-Line Usage

### Invocation Examples

**fission-ramfs:**
```bash
./fission-ramfs /mnt/ramfs
```

**fission-s3rofs:**
```bash
./fission-s3rofs config.json
```

Where `config.json` contains S3 credentials, bucket, prefix, and cache configuration.

**fission-swiftfs:**
```bash
./fission-swiftfs config.json
```

Where `config.json` contains Swift URL, authentication, and cache configuration.

**fission-hellofs:**
```bash
./fission-hellofs /mnt/hellofs
```

### Signal Handling

All implementations handle the same termination signals:

- `SIGINT` (Ctrl+C)
- `SIGTERM` (kill command)
- `SIGHUP` (terminal hangup)

**Signal handling code:** [examples/fission-ramfs/main.go:205-214](), [examples/fission-s3rofs/main.go:454-463](), [examples/fission-swiftfs/main.go:414-423](), [examples/fission-hellofs/main.go:257-266]()

**Sources:** [examples/fission-ramfs/main.go:205-214](), [examples/fission-s3rofs/main.go:171-198](), [examples/fission-swiftfs/main.go:145-165](), [examples/fission-hellofs/main.go:83-86]()

---

