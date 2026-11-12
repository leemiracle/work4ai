<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/open-infra-index · extra page 3FS (Fire-Flyer File System) · fetched 2026-10-30 -->

# 3FS (Fire-Flyer File System)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This document covers the Fire-Flyer File System (3FS), a high-performance parallel file system designed to support DeepSeek's AI training and inference workloads. 3FS provides disaggregated storage with strong consistency semantics, optimized for modern SSD and RDMA network hardware.

For information about the data processing framework that operates on top of 3FS, see [Smallpond](#2.3.2). For broader context on DeepSeek's storage and data processing infrastructure, see [Storage & Data Processing](#2.3).

Sources: [README.md:76-87]()

## System Overview

3FS is a parallel file system that serves as the primary storage backbone for DeepSeek's AI infrastructure. It achieves exceptional throughput by fully utilizing modern hardware capabilities, including high-speed SSDs and RDMA networking technologies.

### Key Characteristics

| Characteristic | Specification |
|---|---|
| **Aggregate Read Throughput** | 6.6 TiB/s (180-node cluster) |
| **GraySort Benchmark** | 3.66 TiB/min (25-node cluster) |
| **Per-Client Peak Throughput** | 40+ GiB/s for KVCache lookup |
| **Architecture** | Disaggregated with strong consistency |
| **Network Technology** | RDMA-optimized |
| **Storage Hardware** | Modern SSD utilization |

Sources: [README.md:80-83]()

## System Architecture

### 3FS Infrastructure Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        V3_TRAINING["V3/R1 Training Nodes"]
        V3_INFERENCE["V3/R1 Inference Nodes"]
        SMALLPOND_CLIENT["Smallpond Framework"]
        OTHER_CLIENTS["Other AI Workloads"]
    end
    
    subgraph "3FS Cluster (180 nodes)"
        subgraph "Metadata Layer"
            META_PRIMARY["Primary Metadata Server"]
            META_SECONDARY["Secondary Metadata Servers"]
            CONSISTENCY_MGR["Strong Consistency Manager"]
        end
        
        subgraph "Storage Nodes"
            STORAGE_1["Storage Node 1<br/>Modern SSDs"]
            STORAGE_2["Storage Node 2<br/>Modern SSDs"]
            STORAGE_N["Storage Node N<br/>Modern SSDs"]
        end
        
        subgraph "Network Infrastructure"
            RDMA_FABRIC["RDMA Network Fabric"]
            BANDWIDTH_AGGREGATOR["Bandwidth Aggregation"]
        end
    end
    
    subgraph "Hardware Layer"
        SSD_HARDWARE["Modern SSD Hardware<br/>Full Bandwidth Utilization"]
        RDMA_HARDWARE["RDMA Network Hardware<br/>High-speed Interconnect"]
    end
    
    %% Client connections
    V3_TRAINING --> META_PRIMARY
    V3_INFERENCE --> META_PRIMARY
    SMALLPOND_CLIENT --> META_PRIMARY
    OTHER_CLIENTS --> META_PRIMARY
    
    %% Metadata management
    META_PRIMARY --> META_SECONDARY
    META_PRIMARY --> CONSISTENCY_MGR
    
    %% Storage access
    V3_TRAINING --> STORAGE_1
    V3_TRAINING --> STORAGE_2
    V3_TRAINING --> STORAGE_N
    
    V3_INFERENCE --> STORAGE_1
    V3_INFERENCE --> STORAGE_2
    V3_INFERENCE --> STORAGE_N
    
    %% Network layer
    STORAGE_1 --> RDMA_FABRIC
    STORAGE_2 --> RDMA_FABRIC
    STORAGE_N --> RDMA_FABRIC
    RDMA_FABRIC --> BANDWIDTH_AGGREGATOR
    
    %% Hardware mapping
    STORAGE_1 --> SSD_HARDWARE
    STORAGE_2 --> SSD_HARDWARE
    STORAGE_N --> SSD_HARDWARE
    RDMA_FABRIC --> RDMA_HARDWARE
```

Sources: [README.md:78-84]()

### Data Flow and Access Patterns

```mermaid
graph TB
    subgraph "Workload Types"
        TRAINING_DATA["Training Data<br/>Preprocessing & Loading"]
        CHECKPOINT_OPS["Checkpoint Operations<br/>Save/Reload"]
        KVCACHE_LOOKUP["KVCache Lookups<br/>40+ GiB/s per node"]
        EMBEDDING_SEARCH["Embedding Vector Search"]
    end
    
    subgraph "3FS Core Services"
        PARALLEL_ACCESS["Parallel File Access<br/>6.6 TiB/s aggregate"]
        CONSISTENCY_ENGINE["Strong Consistency Engine<br/>Disaggregated Architecture"]
        BANDWIDTH_OPTIMIZER["Bandwidth Optimization<br/>Full SSD Utilization"]
    end
    
    subgraph "Storage Operations"
        SEQUENTIAL_READ["Sequential Reads<br/>Training Data Streaming"]
        RANDOM_ACCESS["Random Access<br/>KVCache & Embeddings"]
        CHECKPOINT_IO["Large Block I/O<br/>Model Checkpoints"]
        METADATA_OPS["Metadata Operations<br/>File System Management"]
    end
    
    subgraph "Performance Characteristics"
        GRAYSORT_PERF["GraySort Benchmark<br/>3.66 TiB/min (25-node)"]
        CLIENT_THROUGHPUT["Per-Client Performance<br/>40+ GiB/s peak"]
        AGGREGATE_BANDWIDTH["Cluster Aggregate<br/>6.6 TiB/s read"]
    end
    
    %% Workload mapping
    TRAINING_DATA --> PARALLEL_ACCESS
    CHECKPOINT_OPS --> CONSISTENCY_ENGINE
    KVCACHE_LOOKUP --> BANDWIDTH_OPTIMIZER
    EMBEDDING_SEARCH --> PARALLEL_ACCESS
    
    %% Service to operation mapping
    PARALLEL_ACCESS --> SEQUENTIAL_READ
    PARALLEL_ACCESS --> RANDOM_ACCESS
    CONSISTENCY_ENGINE --> CHECKPOINT_IO
    CONSISTENCY_ENGINE --> METADATA_OPS
    BANDWIDTH_OPTIMIZER --> RANDOM_ACCESS
    
    %% Performance outcomes
    SEQUENTIAL_READ --> GRAYSORT_PERF
    RANDOM_ACCESS --> CLIENT_THROUGHPUT
    PARALLEL_ACCESS --> AGGREGATE_BANDWIDTH
```

Sources: [README.md:84-87]()

## Performance Characteristics

### Benchmark Results

3FS demonstrates exceptional performance across different workload patterns:

| Benchmark | Configuration | Performance |
|---|---|---|
| **Aggregate Read Throughput** | 180-node cluster | 6.6 TiB/s |
| **GraySort Benchmark** | 25-node cluster | 3.66 TiB/min |
| **KVCache Lookup** | Per-client node | 40+ GiB/s peak |

### Hardware Utilization

The system achieves high performance through:

- **Full SSD Bandwidth Utilization**: Maximizes the throughput potential of modern SSD hardware
- **RDMA Network Optimization**: Leverages high-speed RDMA interconnects for low-latency, high-bandwidth communication
- **Disaggregated Architecture**: Separates compute and storage for better resource utilization and scalability

Sources: [README.md:80-83]()

## Integration with DeepSeek Infrastructure

### AI Workload Support

3FS serves as the foundational storage layer for multiple DeepSeek AI workloads:

#### Training Workloads
- **Data Preprocessing**: High-throughput access to raw training datasets
- **Dataset Loading**: Efficient streaming of preprocessed training data to GPU clusters
- **Checkpoint Operations**: Fast save and reload of model checkpoints during training

#### Inference Workloads  
- **KVCache Storage**: High-performance storage and retrieval of key-value caches for attention mechanisms
- **Embedding Vector Search**: Fast access to embedding vectors for semantic search and retrieval operations

### System Integration Architecture

```mermaid
graph TB
    subgraph "DeepSeek AI Infrastructure"
        subgraph "Training System"
            V3_TRAINING_CLUSTER["V3/R1 Training<br/>DeepSpeed + PyTorch"]
            TRAINING_CHECKPOINTS["Model Checkpoints<br/>Periodic Saves"]
            TRAINING_DATA_PIPELINE["Training Data Pipeline<br/>Preprocessing & Loading"]
        end
        
        subgraph "Inference System"
            V3_INFERENCE_CLUSTER["V3/R1 Inference<br/>vLLM-based Engine"]
            KVCACHE_MANAGER["KVCache Manager<br/>FlashMLA Integration"]
            EMBEDDING_SERVICE["Embedding Service<br/>Vector Search"]
        end
        
        subgraph "Data Processing Layer"
            SMALLPOND_FRAMEWORK["Smallpond Framework<br/>Data Processing on 3FS"]
            SPARK_OFFLINE["Spark Offline Processing<br/>Analytics & ETL"]
        end
    end
    
    subgraph "3FS Storage Cluster"
        FS_CORE["3FS Core System<br/>6.6 TiB/s aggregate"]
        CONSISTENCY_LAYER["Strong Consistency<br/>Disaggregated Architecture"]
        RDMA_NETWORK["RDMA Network<br/>High-speed Interconnect"]
    end
    
    %% Training connections
    V3_TRAINING_CLUSTER --> TRAINING_CHECKPOINTS
    TRAINING_CHECKPOINTS --> FS_CORE
    TRAINING_DATA_PIPELINE --> FS_CORE
    
    %% Inference connections  
    V3_INFERENCE_CLUSTER --> KVCACHE_MANAGER
    KVCACHE_MANAGER --> FS_CORE
    EMBEDDING_SERVICE --> FS_CORE
    
    %% Data processing
    SMALLPOND_FRAMEWORK --> FS_CORE
    SPARK_OFFLINE --> FS_CORE
    
    %% Internal 3FS architecture
    FS_CORE --> CONSISTENCY_LAYER
    FS_CORE --> RDMA_NETWORK
```

Sources: [README.md:84-87]()

## Use Cases and Applications

### Primary Use Cases

1. **Training Data Management**
   - Preprocessing large-scale training datasets
   - Streaming data to distributed training clusters
   - Managing dataset versions and transformations

2. **Model Lifecycle Management** 
   - Saving training checkpoints at regular intervals
   - Loading checkpoints for training resumption or fine-tuning
   - Managing multiple model versions and experiments

3. **Inference Optimization**
   - High-speed KVCache storage and retrieval for attention mechanisms
   - Supporting FlashMLA's paged KV cache requirements
   - Embedding vector storage for semantic search operations

4. **Data Processing Workflows**
   - Serving as the storage backend for Smallpond framework
   - Supporting Spark-based offline analytics and ETL operations
   - Enabling data-intensive AI research and experimentation

### Performance Requirements Met

- **High Throughput**: 6.6 TiB/s aggregate read performance supports massive parallel training workloads
- **Low Latency**: 40+ GiB/s per-client throughput enables real-time inference serving
- **Strong Consistency**: Disaggregated architecture ensures data integrity across distributed operations
- **Scalability**: 180-node cluster demonstrates horizontal scaling capabilities

Sources: [README.md:84-87]()

---

