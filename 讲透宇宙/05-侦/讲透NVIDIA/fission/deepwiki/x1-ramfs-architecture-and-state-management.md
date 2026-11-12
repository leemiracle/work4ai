<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/fission · extra page RAMFS Architecture and State Management · fetched 2026-10-26 -->

# RAMFS Architecture and State Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/fission-ramfs/callbacks.go](examples/fission-ramfs/callbacks.go)
- [examples/fission-ramfs/main.go](examples/fission-ramfs/main.go)

</details>



## Purpose and Scope

This document details the core data structures and state management architecture of the `fission-ramfs` in-memory filesystem implementation. It covers how the filesystem maintains its state using `globalsStruct` and `inodeStruct`, how inodes are organized and accessed through the `inodeMap`, and how different filesystem object types (files, directories, symlinks) are represented in memory.

For information about the concurrency control mechanisms and locking strategy used to protect this state, see [RAMFS Concurrency and Locking](#3.1.2). For documentation of specific filesystem operations (read, write, mkdir, etc.), see [RAMFS File and Directory Operations](#3.1.3).

---

## Global State Architecture

The fission-ramfs filesystem maintains all state in a single global variable `globals` of type `globalsStruct`. This singleton pattern provides centralized access to the filesystem's in-memory state from all FUSE callback handlers.

### globalsStruct Overview

```mermaid
graph TB
    subgraph "globalsStruct (Singleton)"
        tryLock["tryLock<br/>*tryLockStruct<br/>Global filesystem lock"]
        programMeta["programPath, mountPoint<br/>programName, volumeName<br/>Configuration metadata"]
        logger["logger<br/>*log.Logger<br/>Logging interface"]
        errChan["errChan<br/>chan error<br/>Error reporting channel"]
        inodeMap["inodeMap<br/>map[uint64]*inodeStruct<br/>NodeID → Inode lookup"]
        lastNodeID["lastNodeID<br/>uint64<br/>Inode allocation counter"]
        fhMap["fhMap<br/>map[uint64]uint32<br/>File handle → flags"]
        lastFH["lastFH<br/>uint64<br/>File handle counter"]
        volume["volume<br/>fission.Volume<br/>FUSE communication"]
        dummies["xattrMapDummy<br/>dirEntryMapDummy<br/>sortedmap callbacks"]
    end
    
    inodeMap --> inodeStruct1["inodeStruct<br/>(NodeID=1, root)"]
    inodeMap --> inodeStruct2["inodeStruct<br/>(NodeID=2)"]
    inodeMap --> inodeStructN["inodeStruct<br/>(NodeID=N)"]
    
    lastNodeID -.->|"allocates next"| inodeMap
    lastFH -.->|"allocates next"| fhMap
```

**Sources:** [examples/fission-ramfs/main.go:89-105]()

The `globalsStruct` contains the following key components:

| Field | Type | Purpose |
|-------|------|---------|
| `tryLock` | `*tryLockStruct` | Global lock for filesystem-level operations |
| `inodeMap` | `map[uint64]*inodeStruct` | Primary inode lookup table, keyed by NodeID |
| `lastNodeID` | `uint64` | Counter for allocating unique NodeIDs; starts at 1 |
| `fhMap` | `map[uint64]uint32` | Maps file handles to open flags |
| `lastFH` | `uint64` | Counter for allocating unique file handles |
| `volume` | `fission.Volume` | Interface to FUSE kernel communication layer |
| `logger` | `*log.Logger` | Structured logging for debugging and errors |
| `errChan` | `chan error` | Channel for reporting asynchronous errors |

**Sources:** [examples/fission-ramfs/main.go:89-105]()

---

## Inode Structure

Each filesystem object (file, directory, or symlink) is represented by an `inodeStruct`. This structure contains all metadata and data for the object.

### inodeStruct Fields

```mermaid
graph TB
    subgraph "inodeStruct"
        tryLock["tryLock<br/>*tryLockStruct<br/>Per-inode lock"]
        attr["attr<br/>fission.Attr<br/>POSIX metadata"]
        xattrMap["xattrMap<br/>sortedmap.LLRBTree<br/>Extended attributes"]
        dirEntryMap["dirEntryMap<br/>sortedmap.LLRBTree<br/>Directory entries"]
        fileData["fileData<br/>[]byte<br/>File contents"]
        symlinkData["symlinkData<br/>[]byte<br/>Symlink target"]
    end
    
    attr --> attrFields["Ino: uint64 (NodeID)<br/>Size: uint64<br/>Mode: uint32<br/>NLink: uint32<br/>UID, GID: uint32<br/>Timestamps"]
    
    xattrMap --> xattrEntries["Key: []byte (xattr name)<br/>Value: []byte (xattr data)"]
    
    dirEntryMap --> dirEntries["Key: []byte (basename)<br/>Value: uint64 (child NodeID)"]
    
    fileData -.->|"Used only if<br/>Mode & S_IFMT == S_IFREG"| RegularFile
    dirEntryMap -.->|"Used only if<br/>Mode & S_IFMT == S_IFDIR"| Directory
    symlinkData -.->|"Used only if<br/>Mode & S_IFMT == S_IFLNK"| Symlink
```

**Sources:** [examples/fission-ramfs/main.go:73-80]()

| Field | Type | Usage by Inode Type |
|-------|------|---------------------|
| `tryLock` | `*tryLockStruct` | All types: provides per-inode concurrency control |
| `attr` | `fission.Attr` | All types: stores POSIX metadata (mode, size, times, owner) |
| `xattrMap` | `sortedmap.LLRBTree` | All types: stores extended attributes as name→data mappings |
| `dirEntryMap` | `sortedmap.LLRBTree` | **Directories only**: maps entry names to child NodeIDs |
| `fileData` | `[]byte` | **Regular files only**: stores file contents up to `attr.Size` |
| `symlinkData` | `[]byte` | **Symlinks only**: stores target path as byte slice |

**Sources:** [examples/fission-ramfs/main.go:73-80]()

### Inode Type Discrimination

The inode type is encoded in `attr.Mode & syscall.S_IFMT` and determines which fields are valid:

- **`syscall.S_IFDIR`**: Directory inode, `dirEntryMap` is populated, `fileData` and `symlinkData` are `nil`
- **`syscall.S_IFREG`**: Regular file inode, `fileData` is populated, `dirEntryMap` and `symlinkData` are `nil`
- **`syscall.S_IFLNK`**: Symlink inode, `symlinkData` is populated, `dirEntryMap` and `fileData` are `nil`

**Sources:** [examples/fission-ramfs/main.go:75](), [examples/fission-ramfs/callbacks.go:44-48]()

---

## Inode Map Organization

The `inodeMap` is the central lookup table for all filesystem objects. It maps NodeIDs (which are also stored in `attr.Ino`) to their corresponding `inodeStruct` pointers.

### Inode Map Structure

```mermaid
graph LR
    subgraph "globals.inodeMap"
        map["map[uint64]*inodeStruct"]
    end
    
    map -->|"NodeID: 1"| root["Root Directory<br/>Mode: S_IFDIR<br/>NLink: 2<br/>dirEntryMap: {'.':1, '..':1}"]
    map -->|"NodeID: 2"| file1["Regular File<br/>Mode: S_IFREG<br/>NLink: 1<br/>fileData: []byte"]
    map -->|"NodeID: 3"| dir1["Subdirectory<br/>Mode: S_IFDIR<br/>NLink: 2<br/>dirEntryMap: entries"]
    map -->|"NodeID: 4"| symlink1["Symlink<br/>Mode: S_IFLNK<br/>NLink: 1<br/>symlinkData: target"]
    map -->|"NodeID: N"| inodeN["Inode N<br/>..."]
    
    root -.->|"dirEntryMap['subdir']"| dir1
    dir1 -.->|"dirEntryMap['file.txt']"| file1
```

**Sources:** [examples/fission-ramfs/main.go:99](), [examples/fission-ramfs/main.go:185-189]()

### NodeID Allocation Strategy

NodeIDs are allocated sequentially using a simple counter:

1. NodeID `1` is reserved for the root directory (created during initialization)
2. `globals.lastNodeID` tracks the most recently allocated NodeID
3. When creating a new inode, `globals.lastNodeID++` generates the next NodeID
4. The new inode is immediately inserted into `globals.inodeMap[newNodeID]`

**Sources:** [examples/fission-ramfs/main.go:189](), [examples/fission-ramfs/callbacks.go:386-387](), [examples/fission-ramfs/callbacks.go:518]()

Example from `DoMkDir`:

```
globals.lastNodeID++

dirEntInode = &inodeStruct{
    tryLock: makeTryLock(),
    attr: fission.Attr{
        Ino:   globals.lastNodeID,
        ...
    },
    ...
}

globals.inodeMap[dirEntInode.attr.Ino] = dirEntInode
```

**Sources:** [examples/fission-ramfs/callbacks.go:518-577]()

---

## Root Inode Initialization

The root directory (NodeID 1) is created during filesystem initialization in `main()`. It is the only pre-existing inode when the filesystem mounts.

### Root Inode Setup Sequence

```mermaid
sequenceDiagram
    participant main as "main()"
    participant rootInode as "rootInode"
    participant dirMap as "dirEntryMap"
    participant globals as "globals.inodeMap"
    
    main->>rootInode: Create inodeStruct
    Note over rootInode: Ino=1, Mode=S_IFDIR|0777<br/>NLink=2, UID=0, GID=0
    
    main->>rootInode: Initialize xattrMap
    main->>rootInode: Initialize dirEntryMap
    
    main->>dirMap: Put(".", 1)
    Note over dirMap: Self-reference
    
    main->>dirMap: Put("..", 1)
    Note over dirMap: Parent reference (root is its own parent)
    
    main->>globals: inodeMap[1] = rootInode
    main->>main: Set lastNodeID = 1
```

**Sources:** [examples/fission-ramfs/main.go:141-189]()

Key characteristics of the root inode:

- **NodeID**: Always `1` (hardcoded)
- **Mode**: `S_IFDIR | 0777` (directory with full permissions)
- **NLink**: `2` (one for itself, one for `.` entry)
- **Directory entries**: Initially contains only `.` and `..`, both pointing to NodeID 1
- **Timestamps**: Set to current time at mount

**Sources:** [examples/fission-ramfs/main.go:141-184]()

---

## Directory Entry Management

Directories use `dirEntryMap` to maintain their child entries as a sorted map of basename→NodeID.

### Directory Entry Structure

```mermaid
graph TB
    subgraph "Directory Inode (NodeID=3)"
        dirInode["attr.Mode: S_IFDIR<br/>attr.NLink: 2+N"]
        dirEntryMap["dirEntryMap<br/>sortedmap.LLRBTree"]
    end
    
    dirEntryMap --> dot["Key: '.'<br/>Value: 3<br/>(self)"]
    dirEntryMap --> dotdot["Key: '..'<br/>Value: 1<br/>(parent)"]
    dirEntryMap --> file1["Key: 'file.txt'<br/>Value: 5<br/>(child file)"]
    dirEntryMap --> subdir["Key: 'subdir'<br/>Value: 7<br/>(child directory)"]
    
    file1 -.->|"lookup in globals.inodeMap"| childInode1["inodeStruct<br/>NodeID=5"]
    subdir -.->|"lookup in globals.inodeMap"| childInode2["inodeStruct<br/>NodeID=7"]
```

**Sources:** [examples/fission-ramfs/main.go:77](), [examples/fission-ramfs/callbacks.go:547-564]()

The `dirEntryMap` uses `sortedmap.LLRBTree` (Left-Leaning Red-Black Tree) for efficient ordered storage:

- **Key**: `[]byte` containing the entry's basename (e.g., `"file.txt"`)
- **Value**: `uint64` containing the child inode's NodeID
- **Comparator**: `sortedmap.CompareByteSlice` for lexicographic ordering
- **Special entries**: `.` points to the directory itself, `..` points to parent directory

**Sources:** [examples/fission-ramfs/main.go:159](), [examples/fission-ramfs/callbacks.go:540]()

### Directory Link Count

The `NLink` field in a directory's attributes follows POSIX conventions:

- Base count of `2` (one for itself, one for `.` entry)
- Increment by `1` for each subdirectory (due to its `..` entry pointing back)
- Regular files do not affect parent directory link count

**Sources:** [examples/fission-ramfs/callbacks.go:533](), [examples/fission-ramfs/callbacks.go:575]()

---

## File Data Storage

Regular files store their contents directly in the `fileData` byte slice within the inode.

### File Data Layout

```mermaid
graph TB
    subgraph "Regular File Inode"
        attr["attr.Mode: S_IFREG<br/>attr.Size: N bytes<br/>attr.Blocks: ceil(N/512)"]
        fileData["fileData: []byte"]
    end
    
    fileData --> data["len(fileData) == attr.Size<br/>Direct byte storage<br/>Zero-filled holes"]
    
    attr -.->|"Size metadata"| fileData
    
    subgraph "Operations"
        DoWrite["DoWrite()<br/>Appends or overwrites<br/>Extends fileData as needed"]
        DoRead["DoRead()<br/>Returns slice of fileData"]
        DoSetAttr["DoSetAttr()<br/>Truncates or extends<br/>with zero padding"]
    end
    
    DoWrite --> fileData
    DoRead --> fileData
    DoSetAttr --> fileData
```

**Sources:** [examples/fission-ramfs/main.go:78](), [examples/fission-ramfs/callbacks.go:234-241]()

File data characteristics:

- **Storage**: Direct `[]byte` slice within inode, no separate block allocation
- **Size synchronization**: `len(fileData)` always equals `attr.Size`
- **Growth**: On write beyond EOF, `fileData` is extended with `append()`
- **Truncation**: On size reduction, slice is resliced; on growth, zeros are appended
- **Block count**: Calculated as `(attr.Size + 511) / 512` for reporting to stat calls

**Sources:** [examples/fission-ramfs/callbacks.go:234-242](), [examples/fission-ramfs/callbacks.go:1084-1109](), [examples/fission-ramfs/callbacks.go:2276-2286]()

Example from `DoWrite`:

```
if writeOffsetActual < fileInode.attr.Size {
    if writeOffsetPlusSize <= fileInode.attr.Size {
        _ = copy(fileInode.fileData[writeOffsetActual:writeOffsetPlusSize], writeIn.Data)
    } else {
        overwriteSize = fileInode.attr.Size - writeOffsetActual
        _ = copy(fileInode.fileData[writeOffsetActual:], writeIn.Data[:overwriteSize])
        fileInode.fileData = append(fileInode.fileData, writeIn.Data[overwriteSize:]...)
        fileInode.attr.Size = writeOffsetPlusSize
    }
} else {
    if writeOffsetActual > fileInode.attr.Size {
        fileInode.fileData = append(fileInode.fileData, make([]byte, (writeOffsetActual-fileInode.attr.Size))...)
    }
    fileInode.fileData = append(fileInode.fileData, writeIn.Data...)
    fileInode.attr.Size = writeOffsetPlusSize
}
```

**Sources:** [examples/fission-ramfs/callbacks.go:1086-1109]()

---

## Extended Attribute Storage

All inodes (files, directories, and symlinks) support extended attributes stored in their `xattrMap`.

### Extended Attribute Structure

```mermaid
graph TB
    subgraph "Any Inode"
        xattrMap["xattrMap<br/>sortedmap.LLRBTree"]
    end
    
    xattrMap --> xattr1["Key: 'user.comment'<br/>Value: []byte('metadata')"]
    xattrMap --> xattr2["Key: 'user.mime_type'<br/>Value: []byte('text/plain')"]
    xattrMap --> xattrN["Key: 'user.custom'<br/>Value: []byte(...)"]
    
    subgraph "Operations"
        DoSetXAttr["DoSetXAttr()<br/>PatchByKey or Put"]
        DoGetXAttr["DoGetXAttr()<br/>GetByKey"]
        DoListXAttr["DoListXAttr()<br/>Iterate all keys"]
        DoRemoveXAttr["DoRemoveXAttr()<br/>DeleteByKey"]
    end
    
    DoSetXAttr --> xattrMap
    DoGetXAttr --> xattrMap
    DoListXAttr --> xattrMap
    DoRemoveXAttr --> xattrMap
```

**Sources:** [examples/fission-ramfs/main.go:76](), [examples/fission-ramfs/callbacks.go:1255-1262]()

Extended attribute characteristics:

- **Key**: `[]byte` containing the attribute name (e.g., `"user.comment"`)
- **Value**: `[]byte` containing arbitrary attribute data
- **Storage**: Separate `sortedmap.LLRBTree` per inode for ordered iteration
- **Operations**: Support set, get, list, and remove operations
- **Namespace**: No filtering; all namespaces accepted (user, system, security, trusted)

**Sources:** [examples/fission-ramfs/callbacks.go:1228-1472]()

---

## Inode Lifecycle Management

Inodes are created, accessed, and deleted through well-defined patterns enforced by reference counting.

### Inode Creation Flow

```mermaid
sequenceDiagram
    participant CB as "FUSE Callback<br/>(DoMkDir/DoCreate/DoSymLink)"
    participant G as "globals"
    participant Parent as "Parent Directory Inode"
    participant New as "New Inode"
    
    CB->>G: Acquire locks on parent
    CB->>Parent: Check name doesn't exist<br/>dirEntryMap.GetByKey()
    
    CB->>G: lastNodeID++
    CB->>New: Allocate inodeStruct<br/>with new NodeID
    
    Note over New: Initialize attr, tryLock,<br/>type-specific fields
    
    CB->>Parent: Add entry<br/>dirEntryMap.Put(name, newNodeID)
    CB->>G: inodeMap[newNodeID] = newInode
    
    CB->>CB: Update parent NLink if dir
    CB->>CB: Release locks
```

**Sources:** [examples/fission-ramfs/callbacks.go:466-611](), [examples/fission-ramfs/callbacks.go:1935-2069]()

### Inode Access Pattern

All filesystem operations follow a consistent pattern for accessing inodes:

1. **Lookup in map**: `inode, ok := globals.inodeMap[nodeID]`
2. **Check existence**: If `!ok`, return `syscall.ENOENT`
3. **Acquire lock**: Use `grantedLockSet.try(inode.tryLock)` (may trigger restart)
4. **Perform operation**: Read or modify inode fields
5. **Release locks**: `grantedLockSet.freeAll(false)`

**Sources:** [examples/fission-ramfs/callbacks.go:27-42](), [examples/fission-ramfs/callbacks.go:122-137]()

### Inode Deletion Flow

```mermaid
sequenceDiagram
    participant CB as "FUSE Callback<br/>(DoUnlink/DoRmDir)"
    participant Parent as "Parent Directory"
    participant Target as "Target Inode"
    participant G as "globals.inodeMap"
    
    CB->>Parent: Acquire locks
    CB->>Parent: Lookup entry<br/>dirEntryMap.GetByKey(name)
    CB->>Target: Acquire lock on target
    
    CB->>Parent: Remove entry<br/>dirEntryMap.DeleteByKey(name)
    CB->>Target: Decrement target.attr.NLink
    
    alt NLink == 0
        CB->>G: delete(inodeMap, targetNodeID)
        Note over Target: Inode memory freed<br/>by Go GC
    else NLink > 0
        Note over Target: Inode retained<br/>(hard links exist)
    end
    
    CB->>CB: Release locks
```

**Sources:** [examples/fission-ramfs/callbacks.go:613-698](), [examples/fission-ramfs/callbacks.go:700-796]()

Reference counting rules:

- **Regular files**: Start with `NLink=1`, deleted when reaches `0`
- **Directories**: Start with `NLink=2`, must be empty (only `.` and `..`) before deletion
- **Hard links**: Increment `NLink` on `DoLink()`, decrement on `DoUnlink()`
- **Open file handles**: Deletion deferred until `DoRelease()` if `NLink=0` while file is open

**Sources:** [examples/fission-ramfs/callbacks.go:688-692](), [examples/fission-ramfs/callbacks.go:1182-1184]()

---

## File Handle Management

The `fhMap` tracks open file handles and their associated flags, separate from the inode table.

### File Handle Mapping

```mermaid
graph TB
    subgraph "globals.fhMap"
        fhMap["map[uint64]uint32"]
    end
    
    fhMap -->|"FH: 1"| flags1["Flags: O_RDONLY"]
    fhMap -->|"FH: 2"| flags2["Flags: O_WRONLY|O_APPEND"]
    fhMap -->|"FH: 3"| flags3["Flags: O_RDWR"]
    fhMap -->|"FH: N"| flagsN["Flags: ..."]
    
    subgraph "Lifecycle"
        DoOpen["DoOpen() / DoCreate()<br/>Allocate FH<br/>Store flags"]
        DoRead["DoRead() / DoWrite()<br/>Lookup FH<br/>Check flags"]
        DoRelease["DoRelease()<br/>Delete FH"]
    end
    
    DoOpen --> fhMap
    DoRead --> fhMap
    DoRelease --> fhMap
```

**Sources:** [examples/fission-ramfs/main.go:101-102](), [examples/fission-ramfs/callbacks.go:948-950]()

File handle characteristics:

- **Allocation**: `globals.lastFH++` on `DoOpen()` or `DoCreate()`
- **Stored flags**: Open flags from `{open|create}In.Flags` (e.g., `O_RDONLY`, `O_WRONLY`, `O_APPEND`)
- **Validation**: `DoRead()` checks for write-only, `DoWrite()` checks for read-only
- **Cleanup**: Removed from `fhMap` on `DoRelease()`
- **No inode link**: File handle doesn't hold a reference; deletion happens when `NLink=0`

**Sources:** [examples/fission-ramfs/callbacks.go:943-961](), [examples/fission-ramfs/callbacks.go:977-987](), [examples/fission-ramfs/callbacks.go:1047-1057](), [examples/fission-ramfs/callbacks.go:1180]()

---

## State Persistence and Volatility

The ramfs implementation stores all data in memory with no persistence mechanism.

### Volatility Characteristics

| Component | Volatility | Consequence |
|-----------|-----------|-------------|
| `inodeMap` | Volatile | All files/directories lost on unmount |
| `fileData` | Volatile | File contents lost on unmount |
| `dirEntryMap` | Volatile | Directory structure lost on unmount |
| `xattrMap` | Volatile | Extended attributes lost on unmount |
| `fhMap` | Volatile | Open handles invalidated on unmount |

On filesystem unmount:
1. `DoUnmount()` is called
2. All goroutines terminate
3. `globals` goes out of scope
4. Go garbage collector reclaims all memory

There is no persistence layer, journal, or recovery mechanism. This design prioritizes simplicity and performance for temporary storage use cases.

**Sources:** [examples/fission-ramfs/main.go:216-220]()

---

## Summary

The fission-ramfs state management architecture uses a straightforward in-memory design:

- **Central state**: `globalsStruct` singleton holds all filesystem state
- **Inode table**: `map[uint64]*inodeStruct` provides O(1) lookup by NodeID
- **Type discrimination**: `attr.Mode & S_IFMT` determines which inode fields are valid
- **Directory organization**: `sortedmap.LLRBTree` provides ordered directory entries
- **File storage**: Direct `[]byte` slice storage within each inode
- **Reference counting**: `attr.NLink` tracks references, deletion at zero
- **Sequential allocation**: Monotonically increasing NodeID and FH counters

This architecture balances simplicity with functionality, providing a complete POSIX-like filesystem interface backed entirely by Go's native data structures and memory management.

**Sources:** [examples/fission-ramfs/main.go:1-356](), [examples/fission-ramfs/callbacks.go:1-2495]()

---

