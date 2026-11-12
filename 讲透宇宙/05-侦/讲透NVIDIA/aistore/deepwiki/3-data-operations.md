<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/aistore · page 3 Data Operations · fetched 2026-10-26 -->

# Data Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ais/tgtimpl.go](ais/tgtimpl.go)
- [ais/tgtobj.go](ais/tgtobj.go)
- [cmn/err.go](cmn/err.go)
- [cmn/owt.go](cmn/owt.go)
- [core/mock/target_mock.go](core/mock/target_mock.go)
- [core/target.go](core/target.go)
- [mirror/utils.go](mirror/utils.go)
- [mirror/utils_test.go](mirror/utils_test.go)
- [transport/README.md](transport/README.md)
- [transport/api.go](transport/api.go)
- [transport/base.go](transport/base.go)
- [transport/bundle/dmover.go](transport/bundle/dmover.go)
- [transport/collect.go](transport/collect.go)
- [transport/header.go](transport/header.go)
- [transport/obj_test.go](transport/obj_test.go)
- [transport/pdu.go](transport/pdu.go)
- [transport/recv.go](transport/recv.go)
- [transport/sendobj.go](transport/sendobj.go)
- [transport/stream_bundle_test.go](transport/stream_bundle_test.go)

</details>



This document describes the core data operations within AIStore, focusing on how data is stored, retrieved, moved, and transmitted across the system. It covers the primary object operations (PUT, GET, APPEND, COPY), their implementation, and the underlying transport mechanisms that move data between nodes.

For information about storage backends and cloud integration, see [Storage Backends](#4).

## Overview of Data Operations

AIStore's data operations provide methods for moving objects into, out of, and across the storage cluster. These operations include:

- **PUT**: Storing objects in the system
- **GET**: Retrieving objects from the system
- **APPEND**: Appending data to existing objects
- **COPY**: Copying objects between locations

These operations are implemented by target nodes, which handle the actual data storage and retrieval. The operations can involve both local storage and remote storage backends.

```mermaid
graph TB
    subgraph "Client Applications"
        client["Client Application"]
    end
    
    subgraph "AIStore Cluster"
        proxy["Proxy Node"]
        
        subgraph "Target Node"
            target["Target"]
            dataOps["Data Operations"]
            dataOps --> put["PUT"]
            dataOps --> get["GET"]
            dataOps --> append["APPEND"]
            dataOps --> copy["COPY"]
            
            storage["Storage Layer"]
            put --> storage
            get --> storage
            append --> storage
            copy --> storage
            
            storage --> local["Local Filesystem"]
            storage --> remote["Remote Backend"]
        end
        
        subgraph "Transport"
            transport["Transport Layer"]
            streams["Stream Bundles"]
            dm["Data Mover (DM)"]
        end
    end
    
    client -- "HTTP Request" --> proxy
    proxy -- "Forward Request" --> target
    target -- "Intra-cluster" --> transport
    transport --> streams
    streams --> dm
    dm -- "Send to" --> target
```

Sources: [ais/tgtobj.go:1-48](), [core/target.go:1-30]()

## Core Data Structures

AIStore implements data operations through several key structures that encapsulate the necessary functionality:

```mermaid
classDiagram
    class putOI {
        +lom *core.LOM
        +r io.ReadCloser
        +workFQN string
        +cksumToUse *cos.Cksum
        +atime int64
        +do(http.Header, *http.Request, *dpq) (int, error)
        -putObject() (int, error)
        -write() ([]byte, *memsys.Slab, cos.LomWriter, error)
        -fini() (int, error)
    }
    
    class getOI {
        +lom *core.LOM
        +w http.ResponseWriter
        +req *http.Request
        +ranges byteRanges
        +atime int64
        +getObject() (int, error)
        -get() (int, error)
        -coldPut(*core.GetReaderResult) (int, error)
        -txfini() (int, error)
    }
    
    class apndOI {
        +lom *core.LOM
        +r io.ReadCloser
        +cksum *cos.Cksum
        +op string
        +size int64
    }
    
    class core.LOM {
        +FQN string
        +Lock(bool)
        +Unlock(bool)
        +Load(bool, bool) error
        +Persist() error
    }
    
    putOI --> "1" core.LOM: operates on
    getOI --> "1" core.LOM: operates on
    apndOI --> "1" core.LOM: operates on
```

Sources: [ais/tgtobj.go:50-140](), [core/target.go:27-69]()

## PUT Operations

The PUT operation stores objects in AIStore. It handles everything from simple file writes to complex operations involving checksums, compression, and distribution across the cluster.

### PUT Flow

```mermaid
sequenceDiagram
    participant Client
    participant Target
    participant putOI
    participant LOM
    participant Backend
    
    Client->>Target: PUT Request
    Target->>putOI: Initialize (do method)
    
    Note over putOI: Check if checksums match
    
    putOI->>putOI: write() to temporary file
    Note over putOI: Validate checksum if needed
    
    putOI->>putOI: finalize()
    
    alt Remote Bucket
        putOI->>Backend: putRemote()
    end
    
    putOI->>LOM: Lock
    putOI->>LOM: IncVersion (for AIS buckets)
    putOI->>LOM: RenameFinalize (temporary to final)
    putOI->>LOM: PersistMain (metadata)
    
    alt Erasure Coding Enabled
        putOI->>LOM: ECM.EncodeObject()
    end
    
    alt Mirroring Enabled
        putOI->>LOM: putMirror()
    end
    
    putOI->>Target: Update Statistics
    Target->>Client: Response
```

The PUT operation follows these steps:

1. A PUT request is received and the `putOI` structure is initialized
2. The object is written to a temporary file with optional checksum validation
3. For remote buckets, the object is sent to the backend provider
4. The object is finalized by:
   - Locking the LOM (Lock Object Metadata)
   - Handling version control for AIS buckets
   - Renaming from temporary to final location
   - Persisting metadata
5. Optional erasure coding and mirroring are performed
6. Statistics are updated and a response is sent

Sources: [ais/tgtobj.go:142-579]()

### Error Handling in PUT

The PUT operation includes comprehensive error handling for:
- Checksum validation
- Filesystem errors
- Backend errors for remote buckets
- Space constraints
- Concurrent access conflicts

```mermaid
graph TD
    Start["putObject()"] --> CheckVC["Check skipVC and checksums"]
    CheckVC --> Write["write()"]
    Write --> ChecksumErr{Checksum Error?}
    
    ChecksumErr -- Yes --> ReturnError1["Return Error"]
    ChecksumErr -- No --> Finalize["finalize()"]
    
    Finalize --> IsRemote{Remote Bucket?}
    IsRemote -- Yes --> PutRemote["putRemote()"]
    IsRemote -- No --> Fini["fini()"]
    
    PutRemote --> RemoteErr{Remote Error?}
    RemoteErr -- Yes --> Retry503{Status 503?}
    RemoteErr -- No --> Fini
    
    Retry503 -- Yes --> RetryPutRemote["Retry putRemote()"]
    Retry503 -- No --> ReturnError2["Return Error"]
    
    RetryPutRemote --> RetryErr{Error?}
    RetryErr -- Yes --> ReturnError3["Return Error"]
    RetryErr -- No --> Fini
    
    Fini --> ECEnabled{Erasure Coding?}
    ECEnabled -- Yes --> EncodeObject["ECM.EncodeObject()"]
    ECEnabled -- No --> MirrorObject["putMirror()"]
    
    EncodeObject --> ECErr{EC Error?}
    ECErr -- Yes --> ReturnError4["Return Error"]
    ECErr -- No --> MirrorObject
    
    MirrorObject --> Success["Return Success"]
```

Sources: [ais/tgtobj.go:178-246](), [cmn/err.go:500-520]()

## GET Operations

The GET operation retrieves objects from AIStore. It supports retrieving objects from local storage, other nodes in the cluster, and remote backends.

### GET Flow

```mermaid
sequenceDiagram
    participant Client
    participant Target
    participant getOI
    participant LOM
    participant Backend
    
    Client->>Target: GET Request
    Target->>getOI: Initialize
    
    getOI->>LOM: Lock(read)
    getOI->>LOM: Load(true, true)
    
    alt Object Not Found
        alt Has Remote Backend
            getOI->>Backend: Cold GET
            Backend->>getOI: Object Data
            getOI->>getOI: coldPut() to store locally
        else AIS Bucket
            getOI->>getOI: restoreFromAny() (EC/replica)
        end
    end
    
    alt Checksum Validation Enabled
        getOI->>getOI: validateRecover()
        alt Corrupted Object
            getOI->>getOI: Recover from copies/EC
        end
    end
    
    getOI->>getOI: txfini()
    
    alt Range Request
        getOI->>getOI: _txrng()
    else Archive Request
        getOI->>getOI: _txarch()
    else Regular
        getOI->>getOI: _txreg()
    end
    
    getOI->>getOI: transmit()
    getOI->>Client: Object Data
    getOI->>Target: Update Statistics
```

The GET operation follows these steps:

1. A GET request is received and the `getOI` structure is initialized
2. The LOM is read-locked and loaded
3. If the object is not found:
   - For remote buckets, a cold GET is performed from the backend
   - For AIS buckets, restoration from alternate sources is attempted
4. If checksum validation is enabled, the object integrity is checked
5. The object is transmitted based on the request type:
   - Regular retrieval
   - Range requests for partial objects
   - Archive extraction for specific files
6. Statistics are updated and a response is sent

Sources: [ais/tgtobj.go:584-1269]()

### Cold GET Processing

When an object isn't found locally but exists in a remote backend, AIStore performs a "cold GET" to retrieve it:

```mermaid
graph TD
    ColdGET["coldPut()"] --> UpgradeLock["Upgrade read lock to write lock"]
    UpgradeLock --> SetAttrs["Set attributes (atime, etc.)"]
    SetAttrs --> GetObjReader["Backend.GetObjReader()"]
    
    GetObjReader --> Method{Transmission Method}
    Method -- "Streaming" --> ColdStream["coldStream()"]
    Method -- "Regular" --> ColdReopen["coldReopen()"]
    Method -- "PDU/Checksum" --> RegularPut["Regular putObject()"]
    
    ColdStream --> Response["Send to client"]
    ColdReopen --> Response
    RegularPut --> RegularGet["Regular GET flow"]
    RegularGet --> Response
```

Sources: [ais/tgtobj.go:764-800]()

## APPEND Operations

APPEND operations allow adding data to existing objects or creating new ones. This is particularly useful for log files or any scenario where data accumulates over time.

### APPEND Structure and Flow

The `apndOI` structure represents an APPEND operation:

```mermaid
graph TB
    AppendOp["Append Operation"] --> Initialize["Initialize apndOI"]
    Initialize --> Operation{Operation Type}
    
    Operation -- "apc.AppendOp" --> CreateHandle["Create/Get handle"]
    Operation -- "apc.FlushOp" --> Flush["flush()"]
    
    CreateHandle --> Append["Append data to temporary file"]
    Append --> UpdatePartialCksum["Update partial checksum"]
    
    Flush --> FinalizeChecksum["Finalize checksum"]
    FinalizeChecksum --> ValidateChecksum["Validate checksum"]
    ValidateChecksum --> StoreObject["Store as regular object via PUT"]
```

APPEND operations work in two phases:
1. **Append Phase**: Data is appended to a temporary file with a handle
2. **Flush Phase**: The temporary file is finalized and stored as a regular object

Sources: [ais/tgtobj.go:99-116]()

## COPY Operations

COPY operations duplicate objects within or across buckets. This can involve transferring data between targets or transforming objects during the copy process.

### COPY Flow

```mermaid
sequenceDiagram
    participant Client
    participant Target
    participant CopyOI
    participant DM
    participant DestTarget
    
    Client->>Target: COPY Request
    Target->>CopyOI: Initialize coi
    
    alt Source Not Local
        CopyOI->>Target: GetCold to get from backend
    end
    
    CopyOI->>CopyOI: Determine destination
    
    alt Different Target
        CopyOI->>DM: Send object to destination target
        DM->>DestTarget: Forward object
        DestTarget->>DestTarget: Store with PutObject
    else Same Target
        CopyOI->>Target: Local copy
    end
    
    CopyOI->>Client: Response
```

COPY operations handle several scenarios:
- Copying within the same bucket
- Copying between different buckets
- Copying between targets (using the Data Mover)
- Copying from remote backends

Sources: [ais/tgtimpl.go:114-117]()

## Transport Layer

The transport layer is responsible for moving data between nodes in the AIStore cluster. It provides reliable, efficient data transfer with features like streaming, chunking, and compression.

### Transport Architecture

```mermaid
graph TB
    subgraph "Transport API"
        API["transport API"] --> Stream["Stream"]
        API --> Handle["Handle (receive)"]
    end
    
    subgraph "Sender"
        Stream --> SendObj["Send(obj)"]
        SendObj --> ObjHeader["Object Header"]
        SendObj --> ObjData["Object Data"]
        
        ObjSize{Size Known?} -- "Yes" --> DirectSend["Direct Send"]
        ObjSize -- "No or Large" --> PDU["Use PDUs"]
        
        subgraph "PDU (Protocol Data Unit)"
            PDU --> PDUHeader["PDU Header"]
            PDU --> PDUFragment["PDU Fragment"]
            PDU --> PDUFlags["Flags (last, etc.)"]
        end
    end
    
    subgraph "HTTP Layer"
        DirectSend --> HTTP["HTTP Transport"]
        PDU --> HTTP
        HTTP --> TCPConnection["TCP Connection"]
    end
    
    subgraph "Receiver"
        TCPConnection --> RxHandler["RxAnyStream"]
        RxHandler --> ParseProtoHdr["Parse Protocol Header"]
        ParseProtoHdr --> IsPDU{Is PDU?}
        
        IsPDU -- "Yes" --> DecodePDU["Decode PDU"]
        IsPDU -- "No" --> DirectReceive["Direct Receive"]
        
        DecodePDU --> Reassemble["Reassemble Object"]
        DirectReceive --> Deliver["Deliver Object"]
        Reassemble --> Deliver
        
        Deliver --> UserCallback["User Callback"]
    end
```

The transport layer has these key components:

1. **Stream**: Handles sending objects to a destination
2. **Object**: Contains a header and data
3. **PDU (Protocol Data Unit)**: Used for breaking large objects into smaller chunks
4. **Receiver**: Processes incoming objects and delivers them to callbacks

Sources: [transport/api.go:1-50](), [transport/recv.go:1-100](), [transport/sendobj.go:1-100]()

### Object Streaming

Objects are sent asynchronously through streams, which provides several benefits:
- Multiple objects can be sent over a single HTTP connection
- Objects are queued and sent in order
- Callbacks can be registered for send completion
- The system can handle errors and retries

```mermaid
sequenceDiagram
    participant Code
    participant Stream
    participant WorkCh
    participant HTTP
    participant Receiver
    participant CmplCh
    
    Code->>Stream: Send(obj)
    Stream->>WorkCh: Queue object
    
    Note over Stream,WorkCh: "Send Queue (SQ)"
    
    Stream->>Stream: sendLoop()
    Stream->>HTTP: Read() called by HTTP
    HTTP->>Receiver: Object transferred
    Receiver->>Receiver: Process object
    
    Stream->>CmplCh: Post completion
    
    Note over Stream,CmplCh: "Send Completion Queue (SCQ)"
    
    Stream->>Stream: cmplLoop()
    Stream->>Code: Callback invoked
```

Sources: [transport/sendobj.go:147-179](), [transport/README.md:42-54]()

### PDU-Based Transfer

When objects are large or of unknown size, they're broken into Protocol Data Units (PDUs):

```mermaid
graph TD
    Stream["Stream"] --> UsePDU{Use PDU?}
    
    UsePDU -- "Yes" --> SendPDU["Send using PDUs"]
    UsePDU -- "No" --> SendDirect["Send directly"]
    
    SendPDU --> BreakObject["Break object into chunks"]
    BreakObject --> SetFlags["Set PDU flags"]
    SetFlags --> TransmitPDU["Transmit PDU"]
    
    TransmitPDU --> IsLast{Last chunk?}
    IsLast -- "No" --> BreakObject
    IsLast -- "Yes" --> SetLastFlag["Set last flag"]
    SetLastFlag --> TransmitFinal["Transmit final PDU"]
```

PDUs allow efficient handling of:
- Large objects that exceed memory limits
- Objects of unknown size (streamed content)
- Objects that are generated on-the-fly

Sources: [transport/pdu.go:1-80](), [transport/README.md:109-125]()

## Data Mover

The Data Mover (DM) orchestrates data transfers between target nodes in the cluster, providing a higher-level abstraction above the transport layer.

### Data Mover Architecture

```mermaid
graph TB
    subgraph "Client Code (e.g., Rebalance)"
        XactCode["Xaction Code"] --> InitDM["Initialize DM"]
    end
    
    subgraph "Data Mover (DM)"
        InitDM --> RegisterRecv["Register Receive Handlers"]
        InitDM --> OpenStreams["Open Streams"]
        
        RegisterRecv --> DataHandler["Data Receive Handler"]
        RegisterRecv --> ACKHandler["ACK Receive Handler"]
        
        OpenStreams --> DataStreams["Data Streams"]
        OpenStreams --> ACKStreams["ACK Streams"]
        
        DataStreams --> SendObj["Send(obj)"]
        ACKStreams --> SendACK["ACK(hdr)"]
        
        SendObj --> ErrorHandling["Error Handling"]
        ErrorHandling --> Retry["Retry"]
        ErrorHandling --> Abort["Abort"]
    end
    
    subgraph "Transport Layer"
        SendObj --> Streams["Stream Bundle"]
        SendACK --> Streams
        Streams --> HTTPTransport["HTTP Transport"]
    end
    
    subgraph "Receiver Node"
        HTTPTransport --> RecvHandler["Receive Handler"]
        RecvHandler --> DataRecvHandler["Data Handler"]
        RecvHandler --> ACKRecvHandler["ACK Handler"]
        
        DataRecvHandler --> UserCallback["User Callback"]
    end
```

The Data Mover provides:
1. **Stream Bundle Management**: Creates and manages streams to multiple target nodes
2. **Send/Receive Registration**: Registers handlers for receiving data and acknowledgments
3. **Coordinated Data Transfer**: Sends objects to specific targets or broadcasts to all targets
4. **ACK System**: Enables acknowledgments for reliable data transfer
5. **Error Handling**: Manages retries and aborts on failure

Sources: [transport/bundle/dmover.go:1-100](), [transport/bundle/dmover.go:179-225](), [transport/stream_bundle_test.go:1-50]()

### DM Lifecycle

```mermaid
sequenceDiagram
    participant Client
    participant DM
    participant StreamBundle
    participant Transport
    participant TargetNode
    
    Client->>DM: NewDM(trname, recvCB, owt)
    Client->>DM: RegRecv()
    
    DM->>Transport: Handle(trname, wrapRecvData)
    DM->>Transport: Handle(ackTrname, wrapRecvACK)
    
    Client->>DM: Open()
    
    DM->>StreamBundle: New(dataArgs)
    DM->>StreamBundle: New(ackArgs)
    
    Client->>DM: Send(obj, reader, target)
    DM->>StreamBundle: Send(obj, reader)
    StreamBundle->>Transport: HTTP PUT
    Transport->>TargetNode: Data Transfer
    
    TargetNode->>Transport: HTTP Handler
    Transport->>DM: wrapRecvData
    DM->>Client: recvCB
    
    Client->>DM: Close(nil)
    DM->>StreamBundle: Close(graceful)
    
    Client->>DM: UnregRecv()
    DM->>Transport: Unhandle(trname)
    DM->>Transport: Unhandle(ackTrname)
```

The Data Mover lifecycle involves:
1. Creation with `NewDM`
2. Registration of receive handlers with `RegRecv`
3. Opening streams with `Open`
4. Sending objects with `Send` or `Bcast`
5. Closing streams with `Close`
6. Unregistering handlers with `UnregRecv`

Sources: [transport/bundle/dmover.go:68-176](), [transport/bundle/dmover.go:266-314]()

## Conclusion

Data operations are at the core of AIStore's functionality, providing the mechanisms for storing, retrieving, and moving data across the cluster. The system's architecture balances performance, reliability, and flexibility through:

1. **Core Object Operations**: PUT, GET, APPEND, and COPY operations that handle the fundamental data management tasks
2. **Transport Layer**: Efficient data movement between nodes using streams, PDUs, and compression
3. **Data Mover**: Orchestration of complex data transfers with reliability and error handling

Together, these components create a robust distributed storage system capable of handling diverse workloads and storage requirements.

Sources: [ais/tgtobj.go](), [transport/api.go](), [transport/bundle/dmover.go]()

---

