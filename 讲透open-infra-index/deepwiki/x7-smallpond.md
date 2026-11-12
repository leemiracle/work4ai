<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/open-infra-index · extra page Smallpond · fetched 2026-10-30 -->

# Smallpond

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

Smallpond is a data processing framework that operates on top of the 3FS (Fire-Flyer File System) to provide efficient data pipeline management for DeepSeek's AI infrastructure. This framework handles data preprocessing, transformation, and workflow orchestration tasks required for both training and inference workloads in the DeepSeek ecosystem.

For information about the underlying file system that Smallpond operates on, see [3FS (Fire-Flyer File System)](#2.3.1). For details about the broader inference system architecture, see [Inference System Architecture](#3.1).

## Architecture Overview

Smallpond is designed as a layer above 3FS that provides data processing abstractions while leveraging the high-performance characteristics of the underlying file system. The framework integrates with the broader DeepSeek infrastructure to support both offline batch processing and online inference data needs.

### System Architecture

```mermaid
graph TB
    subgraph "Data Sources"
        TRAINING_DATA["Training Datasets"]
        INFERENCE_DATA["Inference Requests"]
        CHECKPOINTS["Model Checkpoints"]
        EMBEDDINGS["Embedding Vectors"]
    end
    
    subgraph "Smallpond Framework"
        PIPELINE_MANAGER["Pipeline Manager"]
        WORKFLOW_ENGINE["Workflow Engine"]
        DATA_PROCESSOR["Data Processor"]
        TASK_SCHEDULER["Task Scheduler"]
    end
    
    subgraph "3FS File System Layer"
        FS_CLIENT["3FS Client"]
        FS_METADATA["Metadata Service"]
        FS_STORAGE["Distributed Storage"]
    end
    
    subgraph "Processing Workers"
        PREPROCESS["Preprocessing Workers"]
        TRANSFORM["Transform Workers"]
        VALIDATE["Validation Workers"]
    end
    
    subgraph "Output Systems"
        V3_TRAINING["V3/R1 Training"]
        V3_INFERENCE["V3/R1 Inference"]
        SPARK_JOBS["Spark Analytics"]
    end
    
    TRAINING_DATA --> PIPELINE_MANAGER
    INFERENCE_DATA --> PIPELINE_MANAGER
    CHECKPOINTS --> PIPELINE_MANAGER
    EMBEDDINGS --> PIPELINE_MANAGER
    
    PIPELINE_MANAGER --> WORKFLOW_ENGINE
    WORKFLOW_ENGINE --> DATA_PROCESSOR
    DATA_PROCESSOR --> TASK_SCHEDULER
    
    TASK_SCHEDULER --> PREPROCESS
    TASK_SCHEDULER --> TRANSFORM
    TASK_SCHEDULER --> VALIDATE
    
    PREPROCESS --> FS_CLIENT
    TRANSFORM --> FS_CLIENT
    VALIDATE --> FS_CLIENT
    
    FS_CLIENT --> FS_METADATA
    FS_CLIENT --> FS_STORAGE
    
    FS_STORAGE --> V3_TRAINING
    FS_STORAGE --> V3_INFERENCE
    FS_STORAGE --> SPARK_JOBS
```

Sources: [README.md:87]()

### Data Processing Pipeline

```mermaid
graph LR
    subgraph "Input Stage"
        RAW_DATA["Raw Data Files"]
        METADATA_EXTRACT["Metadata Extraction"]
    end
    
    subgraph "Processing Stage"
        DATA_VALIDATION["Data Validation"]
        FORMAT_CONVERSION["Format Conversion"]
        TOKENIZATION["Tokenization"]
        BATCHING["Batching"]
    end
    
    subgraph "Output Stage"
        PREPROCESSED["Preprocessed Data"]
        TRAINING_READY["Training Ready"]
        INFERENCE_CACHE["Inference Cache"]
    end
    
    subgraph "3FS Integration"
        FS_READ["3FS Read Operations"]
        FS_WRITE["3FS Write Operations"]
        CONSISTENCY_CHECK["Consistency Validation"]
    end
    
    RAW_DATA --> METADATA_EXTRACT
    METADATA_EXTRACT --> DATA_VALIDATION
    DATA_VALIDATION --> FORMAT_CONVERSION
    FORMAT_CONVERSION --> TOKENIZATION
    TOKENIZATION --> BATCHING
    
    DATA_VALIDATION --> FS_READ
    FORMAT_CONVERSION --> FS_READ
    TOKENIZATION --> FS_READ
    
    BATCHING --> FS_WRITE
    FS_WRITE --> CONSISTENCY_CHECK
    
    CONSISTENCY_CHECK --> PREPROCESSED
    PREPROCESSED --> TRAINING_READY
    PREPROCESSED --> INFERENCE_CACHE
```

Sources: [README.md:84-87]()

## Core Components

### Pipeline Manager

The Pipeline Manager serves as the central orchestration component that coordinates data processing workflows. It manages the lifecycle of data processing jobs and ensures proper resource allocation across the 3FS cluster.

### Workflow Engine

The Workflow Engine handles the execution of complex data processing workflows, providing capabilities for:
- Task dependency management
- Error handling and retry logic
- Progress monitoring and reporting
- Resource scheduling optimization

### Data Processor

The Data Processor component implements the core data transformation logic, supporting various data formats and processing operations required for AI/ML workloads:
- Text preprocessing for language models
- Image processing for vision tasks
- Vector embedding operations
- Data format conversions

### Task Scheduler

The Task Scheduler manages the distribution of processing tasks across available worker nodes, optimizing for:
- Load balancing across the cluster
- Efficient utilization of 3FS bandwidth
- Minimization of data movement overhead

## Integration with 3FS

Smallpond is designed to leverage the high-performance characteristics of 3FS, including:

| 3FS Feature | Smallpond Utilization |
|-------------|----------------------|
| 6.6 TiB/s aggregate throughput | Parallel data processing workflows |
| Strong consistency semantics | Reliable pipeline state management |
| 40+ GiB/s per node performance | High-speed data transformation |
| Disaggregated architecture | Scalable worker deployment |

### Performance Optimization

```mermaid
graph TB
    subgraph "Smallpond Optimizations"
        PARALLEL_IO["Parallel I/O Operations"]
        BATCH_PROCESSING["Batch Processing"]
        LOCALITY_AWARE["Data Locality Awareness"]
        PIPELINE_CACHE["Pipeline Caching"]
    end
    
    subgraph "3FS Features"
        HIGH_BANDWIDTH["6.6 TiB/s Throughput"]
        CONSISTENCY["Strong Consistency"]
        CLIENT_PERF["40+ GiB/s per Client"]
        RDMA_NETWORK["RDMA Networks"]
    end
    
    PARALLEL_IO --> HIGH_BANDWIDTH
    BATCH_PROCESSING --> CLIENT_PERF
    LOCALITY_AWARE --> RDMA_NETWORK
    PIPELINE_CACHE --> CONSISTENCY
```

Sources: [README.md:78-84]()

## Data Processing Workflows

### Training Data Preprocessing

Smallpond handles preprocessing of training datasets for DeepSeek V3 and R1 models, including:
- Dataset loading and validation
- Text tokenization and encoding
- Batch preparation and shuffling
- Checkpoint data management

### Inference Data Management

For inference workloads, Smallpond manages:
- KV cache data organization
- Embedding vector indexing
- Request preprocessing pipelines
- Response caching strategies

### Integration with Spark

Smallpond works alongside Spark for offline analytics and large-scale batch processing:

```mermaid
graph LR
    subgraph "Data Sources"
        LOGS["System Logs"]
        METRICS["Performance Metrics"]
        USER_DATA["User Interaction Data"]
    end
    
    subgraph "Processing Layer"
        SMALLPOND_JOBS["Smallpond Jobs"]
        SPARK_JOBS["Spark Jobs"]
    end
    
    subgraph "Storage Layer"
        FS_STORAGE["3FS Distributed Storage"]
    end
    
    subgraph "Output"
        TRAINING_DATASETS["Training Datasets"]
        ANALYTICS_REPORTS["Analytics Reports"]
    end
    
    LOGS --> SMALLPOND_JOBS
    METRICS --> SPARK_JOBS
    USER_DATA --> SMALLPOND_JOBS
    
    SMALLPOND_JOBS --> FS_STORAGE
    SPARK_JOBS --> FS_STORAGE
    
    FS_STORAGE --> TRAINING_DATASETS
    FS_STORAGE --> ANALYTICS_REPORTS
```

Sources: [README.md:84-87]()

## Performance Characteristics

Smallpond is designed to maximize utilization of the underlying 3FS infrastructure while providing efficient data processing capabilities:

- **Throughput**: Leverages 3FS's 6.6 TiB/s aggregate read throughput for large-scale data processing
- **Scalability**: Operates across 180-node clusters with disaggregated architecture
- **Consistency**: Maintains strong consistency semantics for reliable pipeline execution
- **Integration**: Seamlessly integrates with V3/R1 training and inference workflows

The framework supports the data requirements of DeepSeek's production services, handling training data preprocessing, dataset loading, checkpoint operations, and embedding vector search operations that power the V3 and R1 model deployments.

Sources: [README.md:78-87]()

---

