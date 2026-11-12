<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/aistore · page 2 Core Architecture · fetched 2026-10-26 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ais/bucketmeta.go](ais/bucketmeta.go)
- [ais/clustermap.go](ais/clustermap.go)
- [ais/daemon.go](ais/daemon.go)
- [ais/earlystart.go](ais/earlystart.go)
- [ais/htcommon.go](ais/htcommon.go)
- [ais/htrun.go](ais/htrun.go)
- [ais/kalive.go](ais/kalive.go)
- [ais/metasync.go](ais/metasync.go)
- [ais/proxy.go](ais/proxy.go)
- [ais/prxclu.go](ais/prxclu.go)
- [ais/prxtxn.go](ais/prxtxn.go)
- [ais/rebmeta.go](ais/rebmeta.go)
- [ais/target.go](ais/target.go)
- [ais/tgtcp.go](ais/tgtcp.go)
- [ais/tgttxn.go](ais/tgttxn.go)
- [ais/txn.go](ais/txn.go)
- [ais/vote.go](ais/vote.go)
- [api/bucket.go](api/bucket.go)
- [api/client.go](api/client.go)
- [api/object.go](api/object.go)
- [cmd/aisinit/config.go](cmd/aisinit/config.go)
- [cmn/api.go](cmn/api.go)
- [cmn/config.go](cmn/config.go)
- [cmn/iter_fields.go](cmn/iter_fields.go)
- [cmn/tests/api_test.go](cmn/tests/api_test.go)
- [cmn/tests/common_test.go](cmn/tests/common_test.go)
- [cmn/tests/config_test.go](cmn/tests/config_test.go)
- [cmn/tests/configs/config.json](cmn/tests/configs/config.json)
- [cmn/tests/iter_fields_test.go](cmn/tests/iter_fields_test.go)
- [deploy/dev/local/aisnode_config.fspaths.sh](deploy/dev/local/aisnode_config.fspaths.sh)
- [deploy/dev/local/aisnode_config.sh](deploy/dev/local/aisnode_config.sh)

</details>



This document describes the fundamental architecture of AIStore (AIS), including its node types, core components, and their interactions. For information about specific subsystems like rebalancing or erasure coding, please refer to their dedicated sections in the documentation.

## Overview

AIStore is a distributed object storage system designed for high-performance AI and deep learning workloads. It follows a clustered architecture with two primary node types:

1. **Proxy nodes**: The entry points for client requests that manage cluster state and coordinate operations
2. **Target nodes**: Storage nodes that handle data operations and manage physical storage resources

One proxy in the cluster is designated as the **primary** (leader), responsible for cluster-wide decision making, metadata management, and orchestrating distributed operations.

```mermaid
graph TB
    subgraph "External Clients"
        client["Client Applications"]
        cli["CLI Tool"]
        s3client["S3 Clients"]
        pythonsdk["Python SDK"]
    end

    subgraph "API Layer"
        restapi["REST API"]
        s3api["S3 API"]
    end

    subgraph "Cluster Management"
        proxy["Proxy Nodes"]
        primary["Primary Proxy"]
        smap["Cluster Map (Smap)"]
        bmd["Bucket Metadata (BMD)"]
    end

    subgraph "Storage Layer"
        target["Target Nodes"]
        fs["File System"]
        backend["Backend Providers"]
    end

    client --> restapi
    cli --> restapi
    s3client --> s3api
    pythonsdk --> restapi

    restapi --> proxy
    s3api --> proxy
    
    proxy --> primary
    primary --> smap
    primary --> bmd
    proxy --> target
    
    target --> fs
    target --> backend
    
    backend --> aws["AWS S3"]
    backend --> gcp["Google Cloud Storage"]
    backend --> azure["Azure Blob Storage"]
    backend --> ais["Remote AIS Clusters"]
```

Sources:
- [ais/proxy.go:55-83]()
- [ais/target.go:56-76]()
- [api/client.go]()

## Common Node Infrastructure

Both proxy and target nodes are built on a common foundation called `htrun` (HTTP runner), which provides shared infrastructure for:

- HTTP server and request handling
- Node identity management
- Metadata access
- Configuration management
- Memory management
- Stats collection

```mermaid
classDiagram
    class htrun {
        +owner: struct
        +keepalive: keepaliver
        +statsT: stats.Tracker
        +si: *meta.Snode
        +gmm: *memsys.MMSA
        +smm: *memsys.MMSA
        +ratelim: ratelim
        +startup: struct
        +init()
        +run()
        +parseReq()
        +cluMeta()
    }
    
    class proxy {
        +htrun
        +authn: *authManager
        +metasyncer: *metasyncer
        +ic: ic
        +rproxy: reverseProxy
        +notifs: notifs
        +lstca: lstca
        +reg: struct
        +remais: struct
        +ec: struct
        +bucketHandler()
        +objectHandler()
        +healthHandler()
        +daemonHandler()
    }
    
    class target {
        +htrun
        +bps: backends
        +rlbps: rlbackends
        +fshc: *health.FSHC
        +fsprg: fsprungroup
        +reb: *reb.Reb
        +res: *res.Res
        +txns: txns
        +regstate: regstate
        +bucketHandler()
        +objectHandler()
        +txnHandler()
        +Backend()
    }
    
    htrun <|-- proxy
    htrun <|-- target
```

Sources:
- [ais/htrun.go:75-93]()
- [ais/proxy.go:55-83]()
- [ais/target.go:56-76]()

## Proxy Nodes

Proxy nodes handle client requests and manage cluster metadata. The primary proxy has additional responsibilities for cluster management and metadata distribution.

Key components and functionalities of proxy nodes include:

1. **API Handlers**: Process client HTTP requests for various endpoints
2. **Request Routing**: Direct requests to appropriate target nodes based on consistent hashing
3. **Metadata Management**: Manage and distribute cluster metadata (Smap, BMD)
4. **Information Center (IC)**: Handle inter-node communication and notifications
5. **Metasync**: Distribute metadata changes across the cluster

### Request Handlers

Proxy nodes register HTTP handlers for various endpoints, which process client requests and either respond directly or redirect to appropriate target nodes:

```mermaid
flowchart TD
    client["Client"] --> requests["HTTP Requests"]
    
    requests --> bhandler["bucketHandler
    GET/PUT/DELETE/POST
    /v1/buckets"]
    
    requests --> ohandler["objectHandler
    GET/PUT/DELETE/POST
    /v1/objects"]
    
    requests --> dhandler["daemonHandler
    /v1/daemon"]
    
    requests --> chandler["clusterHandler
    /v1/cluster"]
    
    requests --> hhandler["healthHandler
    /v1/health"]
    
    requests --> other["Other Handlers
    (download, etl, etc)"]
    
    bhandler --> bprocess["Process or Redirect"]
    ohandler --> oprocess["Process or Redirect"]
    
    bprocess --> response["Response to Client"]
    oprocess --> response
    dhandler --> response
    chandler --> response
    hhandler --> response
    other --> response
```

Sources:
- [ais/proxy.go:207-257]()
- [ais/proxy.go:437-493]()
- [ais/proxy.go:656-912]()

## Target Nodes

Target nodes handle actual data storage and retrieval operations, managing the local file system and integration with backend storage providers.

Key components and functionalities of target nodes include:

1. **Object Operations**: Handle GET, PUT, DELETE for objects
2. **Backend Integration**: Connect with various storage backends (AWS, GCP, Azure, etc.)
3. **File System Management**: Manage local storage resources
4. **Transaction Handling**: Execute distributed transactions
5. **Extended Actions**: Perform rebalancing, erasure coding, and other maintenance operations

### Backend Providers

Target nodes implement a common backend interface for interacting with different storage systems:

```mermaid
classDiagram
    class Backend {
        <<interface>>
        +CreateBucket()
        +HeadBucket() 
        +ListObjects()
        +HeadObj()
        +GetObj()
        +PutObj()
        +DeleteObj()
    }
    
    class AISbp {
        +Backend
    }
    
    class AWSbp {
        +Backend
    }
    
    class GCPbp {
        +Backend
    }
    
    class Azurebp {
        +Backend
    }
    
    Backend <|-- AISbp
    Backend <|-- AWSbp
    Backend <|-- GCPbp
    Backend <|-- Azurebp
    
    class target {
        +bps: map[string]Backend
        +Backend()
    }
    
    target --> Backend
```

Sources:
- [ais/target.go:107-127]()
- [ais/target.go:137-161]()

## Metadata Management

AIStore manages cluster state through several key metadata structures:

### Cluster Map (Smap)

The Cluster Map (Smap) represents the cluster's topology and is the source of truth for:
- Which nodes are in the cluster (proxies and targets)
- Their roles, network addresses, and capabilities
- Which proxy is the primary

The Smap is versioned and immutable - updates create new versions that are distributed through the metasync system:

```mermaid
classDiagram
    class meta.Smap {
        +Primary: *meta.Snode
        +Pmap: map[string]*meta.Snode
        +Tmap: map[string]*meta.Snode
        +Version: int64
        +UUID: string
        +validate()
        +GetTarget()
        +GetProxy()
    }
    
    class smapX {
        +Smap: meta.Smap
        +staffIC: meta.NodeMap
        +IsPrimary()
        +validateUUID()
        +clone()
        +merge()
        +marshal()
    }
    
    class smapOwner {
        -smap: atomic.Pointer[smapX]
        +get()
        +put()
        +synchronize()
        +modify()
    }
    
    meta.Smap <|-- smapX
    smapOwner --> smapX
```

Sources:
- [ais/clustermap.go]()

### Bucket Metadata (BMD)

The Bucket Metadata (BMD) manages bucket configurations and properties:

```mermaid
classDiagram
    class meta.BMD {
        +Version: int64
        +UUID: string
        +Providers: map[string]bool
        +RemoteBck: map[string]*cmn.Bck
        +Namespace: cmn.Ns
    }
    
    class bucketMD {
        +BMD: meta.BMD
        +propsRef: atomic.Pointer
        +oldVer: atomic.Int64
        +add()
        +del()
        +get()
        +validate()
        +clone()
    }
    
    class bmdOwner {
        -bmd: atomic.Pointer[bucketMD]
        +get()
        +put()
        +init()
    }
    
    meta.BMD <|-- bucketMD
    bmdOwner --> bucketMD
```

Sources:
- [ais/bucketmeta.go]()

## Object Operations

AIStore implements a redirection-based approach for object operations. Here's how a typical object GET flow works:

```mermaid
sequenceDiagram
    participant Client
    participant Proxy
    participant Target
    participant Storage as "Local Storage"
    participant Backend as "Cloud Backend"
    
    Client->>Proxy: GET /v1/objects/bucket/object
    Note over Proxy: Determine target via<br>consistent hashing (HRW)
    Proxy-->>Client: HTTP 301 Redirect to target
    
    Client->>Target: GET /v1/objects/bucket/object
    
    alt Object exists locally
        Target->>Storage: Read object
        Storage-->>Target: Object data
    else Object in remote backend
        Target->>Backend: Fetch object
        Backend-->>Target: Object data
        Target->>Storage: Cache object locally
    end
    
    Target-->>Client: Object data + Metadata
```

And for a PUT operation:

```mermaid
sequenceDiagram
    participant Client
    participant Proxy
    participant Target
    participant Storage as "Local Storage"
    participant Backend as "Cloud Backend"
    
    Client->>Proxy: PUT /v1/objects/bucket/object
    Note over Proxy: Determine target via<br>consistent hashing (HRW)
    Proxy-->>Client: HTTP 307 Redirect to target
    
    Client->>Target: PUT /v1/objects/bucket/object
    Target->>Storage: Store object
    
    alt Cloud bucket with write-through
        Target->>Backend: Write to cloud
        Backend-->>Target: Success
    end
    
    Target-->>Client: Success + Metadata
```

Sources:
- [ais/proxy.go:709-771]()
- [ais/proxy.go:774-870]()
- [ais/target.go:732-768]()
- [ais/target.go:888-963]()

## Transaction System

AIStore uses a two-phase commit protocol for distributed transactions, with components on both proxy and target nodes:

```mermaid
classDiagram
    class txnCln {
        +p: *proxy
        +smap: *smapX
        +msg: *actMsgExt
        +uuid: string
        +path: string
        +req: cmn.HreqArgs
        +selected: meta.Nodes
        +timeout: struct
        +init()
        +begin()
        +commit()
        +bcastAbort()
    }
    
    class txnSrv {
        +t: *target
        +msg: *actMsgExt
        +bck: *meta.Bck
        +bckTo: *meta.Bck
        +query: url.Values
        +uuid: string
        +phase: string
        +callerName: string
        +callerID: string
        +timeout: struct
        +init()
    }
    
    class txns {
        +t: *target
        +table: map[string]*txn
        +begin()
        +find()
        +wait()
        +commitBefore()
        +commitAfter()
        +term()
    }
    
    txnCln --> "initiates" txnSrv
    txnSrv --> "uses" txns
```

Transaction flow for operations like create bucket:

```mermaid
sequenceDiagram
    participant Client
    participant Proxy
    participant Target1
    participant Target2
    
    Client->>Proxy: Create bucket request
    
    Proxy->>Proxy: Create txnCln
    
    Proxy->>Target1: BEGIN phase
    Proxy->>Target2: BEGIN phase
    Target1-->>Proxy: OK
    Target2-->>Proxy: OK
    
    Proxy->>Proxy: Update BMD locally
    Proxy->>Proxy: Distribute BMD via metasync
    
    Proxy->>Target1: COMMIT phase
    Proxy->>Target2: COMMIT phase
    Target1-->>Proxy: OK (with xaction ID)
    Target2-->>Proxy: OK (with xaction ID)
    
    Proxy-->>Client: Success
```

Sources:
- [ais/prxtxn.go:33-157]()
- [ais/tgttxn.go:37-178]()
- [ais/txn.go]()

## Metadata Synchronization

The metasync system ensures that metadata changes (Smap, BMD) are consistently propagated throughout the cluster:

```mermaid
classDiagram
    class metasyncer {
        +p: *proxy
        +smap: *smapX
        +callbackCnt: int
        +last: atomic.Int64
        +listeners: map[string]metasyncer.Listener
        +prev: atomic.Pointer[cluMeta]
        +sync()
    }
    
    class cluMeta {
        +SI: *meta.Snode
        +Smap: *smapX
        +BMD: *bucketMD
        +Config: *cmn.Config
        +RMD: *rebMD
        +EtlMD: *etlMD
        +PrimeTime: int64
        +Flags: cos.BitFlags
    }
    
    metasyncer --> cluMeta: distributes
    
    class htrun {
        +receiveSmap()
        +receiveBMD()
        +receiveConfig()
    }
    
    cluMeta --> htrun: received by
```

Primary proxy initiates metadata synchronization by creating a `cluMeta` package with updated metadata and distributing it to all nodes in the cluster.

Sources:
- [ais/metasync.go]()
- [ais/htrun.go]()

## Startup and Initialization

AIStore nodes follow a carefully designed startup sequence:

### Proxy Startup

```mermaid
flowchart TD
    start["Start proxy"] --> init["Initialize htrun:
    - Parse configuration
    - Set node ID
    - Register handlers"]
    
    init --> loadmeta["Load local metadata
    (Smap, BMD)"]
    
    loadmeta --> checkrole{"Determine role
    (primary or not)"}
    
    checkrole -- "Primary" --> pstart["Primary startup:
    - Wait for targets to join
    - Initialize metadata
    - Start metasync"]
    
    checkrole -- "Non-primary" --> npstart["Non-primary startup:
    - Join existing cluster
    - Receive metadata"]
    
    pstart --> ready["Ready to serve requests"]
    npstart --> ready
```

### Target Startup

```mermaid
flowchart TD
    start["Start target"] --> init["Initialize htrun:
    - Parse configuration
    - Set node ID
    - Register handlers"]
    
    init --> initfs["Initialize file system:
    - Register mountpaths
    - Check available space"]
    
    initfs --> initb["Initialize backends:
    - AWS, GCP, Azure, etc."]
    
    initb --> join["Join cluster:
    - Contact proxy
    - Register self"]
    
    join --> recvmeta["Receive cluster metadata:
    - Smap
    - BMD"]
    
    recvmeta --> ready["Ready to serve requests"]
```

Sources:
- [ais/daemon.go]()
- [ais/proxy.go:183-254]()
- [ais/target.go:368-477]()
- [ais/earlystart.go:53-105]()

## Configuration System

AIStore uses a hierarchical configuration system that includes:

1. **Global (Cluster) Configuration**: Shared across all nodes
2. **Local Configuration**: Node-specific settings

The configuration is stored in a `cmn.Config` structure:

```mermaid
classDiagram
    class Config {
        +LocalConfig: LocalConfig
        +ClusterConfig: ClusterConfig
        +role: string
    }
    
    class LocalConfig {
        +FSP: FSPConf
        +ConfigDir: string
        +LogDir: string
        +TestFSP: TestFSPConf
        +HostNet: LocalNetConfig
    }
    
    class ClusterConfig {
        +Backend: BackendConf
        +Mirror: MirrorConf
        +EC: ECConf
        +Versioning: VersionConf
        +Net: NetConf
        +Timeout: TimeoutConf
        +Space: SpaceConf
        +LRU: LRUConf
        +Disk: DiskConf
        +Rebalance: RebalanceConf
        +Client: ClientConf
        +Features: feat.Flags
    }
    
    Config *-- LocalConfig
    Config *-- ClusterConfig
```

Configuration changes follow the same transaction and metasync patterns as other metadata updates.

Sources:
- [cmn/config.go:51-168]()

## Conclusion

AIStore's core architecture is designed for scalability, performance, and flexibility. The clear separation between proxy and target nodes, coupled with robust metadata management and synchronization, provides a solid foundation for a high-performance distributed object storage system.

Key architectural strengths include:
- Clear separation of concerns between proxy and target nodes
- Robust metadata management with versioning and consistent distribution
- Flexible backend integration supporting multiple cloud providers
- Scalable design with horizontal scaling of both proxy and target nodes
- Transaction-based approach for maintaining system consistency

Sources:
- [ais/proxy.go]()
- [ais/target.go]()
- [ais/htrun.go]()
- [cmn/config.go]()

---

