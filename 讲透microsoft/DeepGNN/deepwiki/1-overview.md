<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/DeepGNN · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.readthedocs.yaml](.readthedocs.yaml)
- [docs/BUILD](docs/BUILD)
- [docs/graph_engine/custom_decoder.rst](docs/graph_engine/custom_decoder.rst)
- [docs/requirements.txt](docs/requirements.txt)
- [docs/tf/index.rst](docs/tf/index.rst)
- [requirements.txt](requirements.txt)

</details>



## Purpose and Scope

DeepGNN is a distributed graph neural network framework designed for large-scale graph processing and machine learning tasks. This framework provides a complete pipeline from graph data ingestion and storage through distributed training of graph neural network models.

The framework consists of a high-performance graph engine (Snark), data conversion utilities, and integrations with popular machine learning frameworks including PyTorch and TensorFlow. For detailed information about specific components, see [Graph Engine (Snark)](#2), [Datasets and Data Processing](#3), [Machine Learning Integration](#4), and [Development and Deployment](#5).

## High-Level Architecture

**DeepGNN System Architecture**

```mermaid
graph TB
    subgraph "Application Layer"
        APP["Application Code"]
        EXAMPLES["Example Scripts"]
        NOTEBOOKS["Jupyter Notebooks"]
    end
    
    subgraph "ML Framework Layer"
        PT["PyTorch Integration"]
        TF["TensorFlow Integration"]
        GAT["GAT Models"]
        GCN["GCN Models"]
        SAGE["GraphSAGE"]
    end
    
    subgraph "Graph Engine Core"
        SNARK["Snark Engine"]
        MEMORYGRAPH["MemoryGraph"]
        DISTCLIENT["distributed.Client"]
        LOCALCLIENT["local.Client"]
    end
    
    subgraph "Data Pipeline"
        CONVERTER["MultiWorkersConverter"]
        DECODERS["JSON/EdgeList/TSV Decoders"]
        BINARYWRITER["BinaryWriter"]
    end
    
    subgraph "Storage & Distribution"
        HDFS["HDFS Storage"]
        AZURE["Azure Data Lake"]
        GRPC["gRPC Services"]
    end
    
    subgraph "Build System"
        BAZEL["Bazel Build"]
        CI["GitHub Actions"]
        PACKAGING["Python Packaging"]
    end
    
    APP --> PT
    APP --> TF
    EXAMPLES --> PT
    EXAMPLES --> TF
    
    PT --> SNARK
    TF --> SNARK
    GAT --> PT
    GAT --> TF
    GCN --> PT
    GCN --> TF
    SAGE --> PT
    
    SNARK --> MEMORYGRAPH
    SNARK --> DISTCLIENT
    SNARK --> LOCALCLIENT
    
    CONVERTER --> BINARYWRITER
    DECODERS --> CONVERTER
    BINARYWRITER --> SNARK
    
    SNARK --> HDFS
    SNARK --> AZURE
    SNARK --> GRPC
    
    BAZEL --> SNARK
    BAZEL --> PT
    BAZEL --> TF
    CI --> BAZEL
    CI --> PACKAGING
```

Sources: [requirements.txt:1-274](), [docs/BUILD:8-287](), [docs/graph_engine/custom_decoder.rst:1-151]()

## Core Components

### Graph Engine (Snark)

The Snark graph engine provides the foundational graph storage and processing capabilities. It supports both in-memory and distributed graph operations through multiple client interfaces.

**Graph Engine Component Architecture**

```mermaid
graph TB
    subgraph "Client Interfaces"
        PY_CLIENT["Python Client API"]
        MEMORY_GRAPH["MemoryGraph"]
        DIST_CLIENT["distributed.Client"]
        LOCAL_CLIENT["local.Client"]
    end
    
    subgraph "Core Engine"
        PY_GRAPH["py_graph.cc"]
        PY_SERVER["py_server.cc"]
        GRAPH_BACKEND["snark::Graph"]
        PARTITION["snark::Partition"]
    end
    
    subgraph "Services"
        GRPC_SERVER["gRPC Server"]
        GRAPH_ENGINE_SERVICE["GraphEngineService"]
        GRAPH_SAMPLER_SERVICE["GraphSamplerService"]
    end
    
    subgraph "Storage Backends"
        MEMORY_STORAGE["Memory Storage"]
        DISK_STORAGE["Disk Storage"]
        HDFS_STORAGE["HDFS Storage"]
    end
    
    subgraph "Data Formats"
        META_JSON["meta.json"]
        BINARY_FILES["Binary Graph Files"]
        ALIAS_TABLES["Alias Tables"]
        INDEX_FILES["Index Files"]
    end
    
    PY_CLIENT --> MEMORY_GRAPH
    PY_CLIENT --> DIST_CLIENT
    PY_CLIENT --> LOCAL_CLIENT
    
    MEMORY_GRAPH --> PY_GRAPH
    DIST_CLIENT --> GRPC_SERVER
    LOCAL_CLIENT --> PY_GRAPH
    
    PY_GRAPH --> GRAPH_BACKEND
    PY_SERVER --> GRAPH_BACKEND
    GRPC_SERVER --> GRAPH_ENGINE_SERVICE
    GRPC_SERVER --> GRAPH_SAMPLER_SERVICE
    
    GRAPH_BACKEND --> PARTITION
    PARTITION --> MEMORY_STORAGE
    PARTITION --> DISK_STORAGE
    PARTITION --> HDFS_STORAGE
    
    GRAPH_BACKEND --> META_JSON
    GRAPH_BACKEND --> BINARY_FILES
    GRAPH_BACKEND --> ALIAS_TABLES
    GRAPH_BACKEND --> INDEX_FILES
```

The engine supports multiple storage backends and provides both synchronous and asynchronous graph operations. Client applications interact with the graph through Python APIs that abstract the underlying C++ implementation.

Sources: [docs/BUILD:8-37](), [docs/graph_engine/custom_decoder.rst:135-151]()

### Data Processing Pipeline

The data conversion system transforms various input formats into the graph engine's optimized binary representation. This pipeline supports multiple input formats and provides extensible decoder interfaces.

**Data Conversion Flow**

```mermaid
graph LR
    subgraph "Input Sources"
        JSON_INPUT["JSON Files"]
        CSV_INPUT["CSV/EdgeList"]
        TSV_INPUT["TSV Files"]
        AVRO_INPUT["Avro Files"]
        NETWORKX_INPUT["NetworkX Graphs"]
    end
    
    subgraph "Decoders"
        JSON_DECODER["JsonDecoder"]
        EDGELIST_DECODER["EdgeListDecoder"] 
        TSV_DECODER["TsvDecoder"]
        AVRO_DECODER["AvroDecoder"]
    end
    
    subgraph "Conversion Engine"
        MULTI_WORKERS["MultiWorkersConverter"]
        QUEUE_DISPATCHER["QueueDispatcher"]
        WORKER_THREADS["Worker Threads"]
    end
    
    subgraph "Binary Writers"
        BINARY_WRITER["BinaryWriter"]
        NODE_WRITER["NodeWriter"]
        EDGE_WRITER["EdgeWriter"]
        ALIAS_WRITER["AliasWriter"]
    end
    
    subgraph "Output Files"
        NODE_MAP["node_X.map"]
        NODE_INDEX["node_X.index"] 
        EDGE_INDEX["edge_X.index"]
        META_OUTPUT["meta.json"]
    end
    
    JSON_INPUT --> JSON_DECODER
    CSV_INPUT --> EDGELIST_DECODER
    TSV_INPUT --> TSV_DECODER
    AVRO_INPUT --> AVRO_DECODER
    NETWORKX_INPUT --> EDGELIST_DECODER
    
    JSON_DECODER --> MULTI_WORKERS
    EDGELIST_DECODER --> MULTI_WORKERS
    TSV_DECODER --> MULTI_WORKERS
    AVRO_DECODER --> MULTI_WORKERS
    
    MULTI_WORKERS --> QUEUE_DISPATCHER
    QUEUE_DISPATCHER --> WORKER_THREADS
    WORKER_THREADS --> BINARY_WRITER
    
    BINARY_WRITER --> NODE_WRITER
    BINARY_WRITER --> EDGE_WRITER
    BINARY_WRITER --> ALIAS_WRITER
    
    NODE_WRITER --> NODE_MAP
    NODE_WRITER --> NODE_INDEX
    EDGE_WRITER --> EDGE_INDEX
    BINARY_WRITER --> META_OUTPUT
```

The pipeline supports custom decoders through the `Decoder` base class, allowing users to implement domain-specific data transformation logic while maintaining compatibility with the graph engine's storage format.

Sources: [docs/graph_engine/custom_decoder.rst:80-107](), [docs/BUILD:40-51]()

## Machine Learning Framework Integration

### PyTorch Integration

DeepGNN provides native PyTorch integration through specialized dataset classes, samplers, and model implementations. The integration supports distributed training scenarios and popular GNN architectures.

Key components include:
- `GraphSAGE` encoders and sampling utilities
- Custom PyTorch datasets for graph data
- Integration with PyTorch Geometric (`torch_geometric`)
- Ray-based distributed training support

### TensorFlow Integration

The TensorFlow integration offers similar capabilities with TensorFlow-specific implementations:
- Graph Attention Network (`GAT`) models
- Graph Convolutional Network (`GCN`) implementations  
- TensorFlow-compatible data loaders
- Ray distributed training integration

Sources: [requirements.txt:250-258](), [docs/BUILD:99-159](), [docs/BUILD:161-237](), [docs/tf/index.rst:1-11]()

## External System Integration

DeepGNN integrates with several external systems for data storage and distributed processing:

| System | Purpose | Configuration |
|--------|---------|---------------|
| Azure Data Lake | Cloud storage backend | Via `azure-datalake-store` package |
| HDFS | Distributed file storage | Native HDFS integration |
| Apache Spark | Data preprocessing | Through `pyspark` integration |
| Ray | Distributed training | For both PyTorch and TensorFlow |
| gRPC | Service communication | For distributed graph operations |

The framework automatically handles data partitioning and distribution across these systems, enabling scalable graph processing workflows.

Sources: [requirements.txt:20-35](), [requirements.txt:88-90](), [requirements.txt:185](), [requirements.txt:196]()

## Build and Deployment System

DeepGNN uses Bazel as its primary build system, providing reproducible builds across different platforms. The build configuration supports:

- Cross-platform C++ compilation with manylinux compatibility
- Python package generation and distribution
- Automated testing through GitHub Actions
- Documentation generation using Sphinx

The build system handles complex dependencies including C++ libraries, Python packages, and external frameworks, ensuring consistent deployment across development and production environments.

Sources: [docs/BUILD:1-287](), [docs/requirements.txt:1-31](), [.readthedocs.yaml:1-13]()

---

