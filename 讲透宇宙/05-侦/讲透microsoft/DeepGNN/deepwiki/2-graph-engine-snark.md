<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/DeepGNN · page 2 Graph Engine (Snark) · fetched 2026-10-26 -->

# Graph Engine (Snark)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/cc/lib/graph/metadata.cc](src/cc/lib/graph/metadata.cc)
- [src/cc/lib/graph/metadata.h](src/cc/lib/graph/metadata.h)
- [src/cc/lib/graph/partition.cc](src/cc/lib/graph/partition.cc)
- [src/cc/lib/py_graph.h](src/cc/lib/py_graph.h)
- [src/python/deepgnn/graph_engine/snark/converter/writers.py](src/python/deepgnn/graph_engine/snark/converter/writers.py)
- [src/python/deepgnn/graph_engine/snark/distributed.py](src/python/deepgnn/graph_engine/snark/distributed.py)
- [src/python/deepgnn/graph_engine/snark/tests/e2e_test.py](src/python/deepgnn/graph_engine/snark/tests/e2e_test.py)
- [src/python/deepgnn/graph_engine/snark/tests/sparse_features_test.py](src/python/deepgnn/graph_engine/snark/tests/sparse_features_test.py)

</details>



The Graph Engine, internally known as Snark, is the core distributed graph storage and query engine for DeepGNN. It provides efficient storage, retrieval, and sampling operations for large-scale graphs across multiple partitions and servers. Snark handles both static and temporal graphs, supporting node and edge features, weighted sampling, and distributed operations through a client-server architecture.

For information about data processing and conversion pipelines that feed into Snark, see [Data Conversion Pipeline](#3.2). For ML framework integration that uses Snark, see [Machine Learning Integration](#4).

## Architecture Overview

Snark employs a multi-layered architecture with Python client interfaces, C++ backend processing, and flexible storage options. The system supports both local in-memory graphs and distributed multi-server deployments.

### Core System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        LocalClient[Client]
        DistClient[distributed.Client]
        MemGraph[MemoryGraph]
    end
    
    subgraph "Python Interface"
        ClientPy[client.py]
        ServerPy[server.py] 
        LocalPy[local.py]
    end
    
    subgraph "C++ Backend"
        PyGraph[PyGraph]
        PyServer[PyServer]
        Partition[snark::Partition]
        GRPCServer[snark::GRPCServer]
    end
    
    subgraph "Storage Layer"
        MemStorage[MemoryStorage]
        DiskStorage[DiskStorage] 
        HDFSStorage[HDFSStorage]
    end
    
    subgraph "Data Files"
        NodeMap[node_X.map]
        EdgeIndex[edge_X.index]
        Features[features_X.data]
        MetaJson[meta.json]
    end
    
    LocalClient --> LocalPy
    DistClient --> ClientPy
    MemGraph --> LocalPy
    
    LocalPy --> PyGraph
    ServerPy --> PyServer
    ClientPy --> GRPCServer
    
    PyGraph --> Partition
    PyServer --> GRPCServer
    GRPCServer --> Partition
    
    Partition --> MemStorage
    Partition --> DiskStorage  
    Partition --> HDFSStorage
    
    MemStorage --> NodeMap
    DiskStorage --> EdgeIndex
    HDFSStorage --> Features
    Partition --> MetaJson
```

**Sources:** [src/python/deepgnn/graph_engine/snark/distributed.py:18-42](), [src/cc/lib/py_graph.h:30-44](), [src/cc/lib/graph/partition.cc:138-150]()

## Client APIs

Snark provides two primary client interfaces: local clients for single-machine deployments and distributed clients for multi-server setups.

### Local vs Distributed Clients

```mermaid
graph LR
    subgraph "Local Client Path"
        App1[Application] --> LocalClient[local.Client]
        LocalClient --> MemGraph[MemoryGraph]
        MemGraph --> PyGraph1[PyGraph C++]
        PyGraph1 --> LocalPartition[Local Partitions]
    end
    
    subgraph "Distributed Client Path"
        App2[Application] --> DistClient[distributed.Client]
        DistClient --> GRPC[gRPC Client]
        GRPC --> Server1[Server 1]
        GRPC --> Server2[Server N]
        Server1 --> PyGraph2[PyGraph C++]
        Server2 --> PyGraph3[PyGraph C++]
    end
```

**Sources:** [src/python/deepgnn/graph_engine/snark/distributed.py:18-56](), [src/python/deepgnn/graph_engine/snark/tests/e2e_test.py:164-167]()

### Client Interface Operations

The client APIs support comprehensive graph operations including:

| Operation Category | Methods | Description |
|---|---|---|
| Node Operations | `node_features()`, `node_types()`, `node_string_features()` | Retrieve node attributes and features |
| Edge Operations | `edge_features()`, `neighbors()`, `neighbor_count()` | Access edge data and connectivity |
| Sampling | `NodeSampler`, `EdgeSampler` | Weighted and uniform sampling |
| Graph Queries | `get_node_type_count()`, `get_edge_type_count()` | Graph statistics |

**Sources:** [src/python/deepgnn/graph_engine/snark/tests/e2e_test.py:168-176](), [src/cc/lib/py_graph.h:96-125]()

## Server Components

The distributed server architecture enables horizontal scaling across multiple machines while maintaining data locality and efficient query processing.

### Server Initialization and Configuration

```mermaid
graph TB
    subgraph "Server Startup"
        ServerClass[distributed.Server]
        MetaDownload[download_meta]
        ServerInit[server.Server]
        PartitionConfig[Partition Configuration]
    end
    
    subgraph "Storage Options"
        MemoryType[PartitionStorageType.memory]
        DiskType[PartitionStorageType.disk]
        HDFSType[HDFS Integration]
    end
    
    subgraph "SSL Configuration"
        SSLKey[ssl_key]
        SSLCert[ssl_cert] 
        SSLRoot[ssl_root]
    end
    
    ServerClass --> MetaDownload
    MetaDownload --> ServerInit
    ServerInit --> PartitionConfig
    
    PartitionConfig --> MemoryType
    PartitionConfig --> DiskType
    PartitionConfig --> HDFSType
    
    ServerInit --> SSLKey
    ServerInit --> SSLCert
    ServerInit --> SSLRoot
```

**Sources:** [src/python/deepgnn/graph_engine/snark/distributed.py:62-111](), [src/cc/lib/py_graph.h:84-89]()

## Data Storage and Partitioning

Snark uses a sophisticated partitioning scheme to distribute graph data across multiple storage backends while maintaining query efficiency.

### Partition Structure

The `snark::Partition` class manages individual graph partitions with the following key components:

- **Node Storage**: Node mappings, types, and feature indices
- **Edge Storage**: Edge indices, neighbor relationships, and timestamps
- **Feature Storage**: Dense and sparse feature data
- **Metadata**: Partition-specific statistics and configuration

**Sources:** [src/cc/lib/graph/partition.cc:138-201]()

### Storage Type Hierarchy

```mermaid
graph TB
    subgraph "Storage Abstraction"
        BaseStorage[BaseStorage]
        MemoryStorage[MemoryStorage]
        DiskStorage[DiskStorage]
        HDFSStorage[HDFSStorage]
        HDFSStreamStorage[HDFSStreamStorage]
    end
    
    subgraph "File Operations"
        NodeMap[ReadNodeMap]
        EdgeRead[ReadEdges]
        FeatureRead[ReadNodeFeatures]
        MetaRead[Metadata]
    end
    
    BaseStorage --> MemoryStorage
    BaseStorage --> DiskStorage
    BaseStorage --> HDFSStorage
    BaseStorage --> HDFSStreamStorage
    
    MemoryStorage --> NodeMap
    DiskStorage --> EdgeRead
    HDFSStorage --> FeatureRead
    MemoryStorage --> MetaRead
```

**Sources:** [src/cc/lib/graph/partition.cc:152-201](), [src/cc/lib/graph/partition.cc:396-455]()

### Binary File Format

Snark stores graph data in an optimized binary format with separate files for different data types:

| File Type | Purpose | Format |
|---|---|---|
| `node_X.map` | Node ID to internal ID mapping | `[node_id: 8b, internal_id: 8b, type: 4b]` |
| `edge_X.index` | Edge connectivity data | `[dst: 8b, feature_offset: 8b, type: 4b, weight: 4b]` |
| `neighbors_X.index` | Neighbor list indices | `[offset: 8b]` |
| `node_features_X.data` | Node feature storage | Variable length binary data |
| `meta.json` | Graph metadata | JSON metadata |

**Sources:** [src/cc/lib/graph/partition.cc:269-337](), [src/python/deepgnn/graph_engine/snark/converter/writers.py:214-221]()

## Metadata Management

The metadata system provides essential graph statistics and configuration information required for distributed operations.

### Metadata Structure

```mermaid
graph LR
    subgraph "Metadata Components"
        Version[m_version]
        NodeCount[m_node_count]
        EdgeCount[m_edge_count]
        TypeCounts[m_node_type_count]
        FeatureCounts[m_node_feature_count]
        Partitions[m_partition_count]
        Weights[m_partition_weights]
        Watermark[m_watermark]
    end
    
    subgraph "Configuration"
        ConfigPath[m_config_path]
        StoragePath[m_path]
        HDFSConfig[HDFS Settings]
    end
    
    Version --> NodeCount
    NodeCount --> EdgeCount
    EdgeCount --> TypeCounts
    TypeCounts --> FeatureCounts
    FeatureCounts --> Partitions
    Partitions --> Weights
    Weights --> Watermark
    
    ConfigPath --> StoragePath
    StoragePath --> HDFSConfig
```

**Sources:** [src/cc/lib/graph/metadata.h:18-44](), [src/cc/lib/graph/metadata.cc:19-111]()

## Data Conversion Pipeline

The conversion pipeline transforms raw graph data into Snark's optimized binary format through a multi-stage process.

### Binary Writer Architecture

```mermaid
graph TB
    subgraph "Writer Components"
        BinaryWriter[BinaryWriter]
        NodeWriter[NodeWriter]
        EdgeWriter[EdgeWriter]
        NodeFeatureWriter[NodeFeatureWriter]
        EdgeFeatureWriter[EdgeFeatureWriter]
    end
    
    subgraph "Alias Tables"
        NodeAlias[NodeAliasWriter]
        EdgeAlias[EdgeAliasWriter]
        VoseAlias[alias.Vose]
    end
    
    subgraph "Output Files"
        NodeFiles[node_X.*]
        EdgeFiles[edge_X.*]
        FeatureFiles[*_features_X.*]
        AliasFiles[*_alias_X.*]
    end
    
    BinaryWriter --> NodeWriter
    BinaryWriter --> EdgeWriter
    NodeWriter --> NodeFeatureWriter
    EdgeWriter --> EdgeFeatureWriter
    
    BinaryWriter --> NodeAlias
    BinaryWriter --> EdgeAlias
    NodeAlias --> VoseAlias
    EdgeAlias --> VoseAlias
    
    NodeWriter --> NodeFiles
    EdgeWriter --> EdgeFiles
    NodeFeatureWriter --> FeatureFiles
    NodeAlias --> AliasFiles
```

**Sources:** [src/python/deepgnn/graph_engine/snark/converter/writers.py:19-172](), [src/python/deepgnn/graph_engine/snark/converter/writers.py:487-576]()

## Key Operations and Interfaces

### C++ Interface Layer

The C interface in `py_graph.h` defines the core operations available to Python clients:

| Function Category | Key Functions | Purpose |
|---|---|---|
| Graph Creation | `CreateLocalGraph`, `CreateRemoteClient` | Initialize graph instances |
| Server Management | `StartServer`, `ResetServer` | Manage distributed servers |
| Node Operations | `GetNodeType`, `GetNodeFeature`, `GetNodeSparseFeature` | Node data access |
| Edge Operations | `GetEdgeFeature`, `GetNeighbors`, `NeighborCount` | Edge data access |
| Sampling | `CreateWeightedNodeSampler`, `SampleNodes`, `SampleEdges` | Random sampling |

**Sources:** [src/cc/lib/py_graph.h:80-183]()

### Feature Handling

Snark supports multiple feature types including dense arrays, sparse features, and string features with temporal versioning:

```mermaid
graph LR
    subgraph "Feature Types"
        DenseFeatures[Dense Arrays]
        SparseFeatures[Sparse Coordinates + Values]
        StringFeatures[Binary String Data]
        TemporalFeatures[Timestamped Features]
    end
    
    subgraph "Storage Format"
        FeatureIndex[Feature Index]
        FeatureData[Feature Data]
        TemporalIndex[Temporal Index]
    end
    
    DenseFeatures --> FeatureIndex
    SparseFeatures --> FeatureIndex
    StringFeatures --> FeatureData
    TemporalFeatures --> TemporalIndex
    
    FeatureIndex --> FeatureData
    TemporalIndex --> FeatureData
```

**Sources:** [src/cc/lib/graph/partition.cc:33-71](), [src/python/deepgnn/graph_engine/snark/converter/writers.py:680-736](), [src/python/deepgnn/graph_engine/snark/tests/sparse_features_test.py:24-53]()

---

