<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/dataset-viewer · page 2 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Makefile](Makefile)
- [README.md](README.md)
- [chart/Chart.yaml](chart/Chart.yaml)
- [chart/env/prod.yaml](chart/env/prod.yaml)
- [chart/env/staging.yaml](chart/env/staging.yaml)
- [chart/templates/_common/_helpers.tpl](chart/templates/_common/_helpers.tpl)
- [chart/templates/cron-jobs/backfill/_container.tpl](chart/templates/cron-jobs/backfill/_container.tpl)
- [chart/values.yaml](chart/values.yaml)
- [jobs/cache_maintenance/README.md](jobs/cache_maintenance/README.md)
- [jobs/cache_maintenance/src/cache_maintenance/backfill.py](jobs/cache_maintenance/src/cache_maintenance/backfill.py)
- [jobs/cache_maintenance/src/cache_maintenance/config.py](jobs/cache_maintenance/src/cache_maintenance/config.py)
- [jobs/cache_maintenance/src/cache_maintenance/main.py](jobs/cache_maintenance/src/cache_maintenance/main.py)
- [libs/libcommon/src/libcommon/processing_graph.py](libs/libcommon/src/libcommon/processing_graph.py)
- [libs/libcommon/tests/test_backfill_on_real_graph.py](libs/libcommon/tests/test_backfill_on_real_graph.py)
- [libs/libcommon/tests/test_processing_graph.py](libs/libcommon/tests/test_processing_graph.py)
- [services/worker/src/worker/dtos.py](services/worker/src/worker/dtos.py)
- [services/worker/src/worker/job_runners/dataset/compatible_libraries.py](services/worker/src/worker/job_runners/dataset/compatible_libraries.py)
- [services/worker/src/worker/job_runners/dataset/hub_cache.py](services/worker/src/worker/job_runners/dataset/hub_cache.py)
- [services/worker/tests/job_runners/dataset/test_compatible_libraries.py](services/worker/tests/job_runners/dataset/test_compatible_libraries.py)
- [services/worker/tests/job_runners/dataset/test_hub_cache.py](services/worker/tests/job_runners/dataset/test_hub_cache.py)

</details>



## Purpose and Scope

This document provides a comprehensive overview of the dataset-viewer system architecture, covering the microservices design, data processing pipeline, storage systems, and deployment infrastructure. The dataset-viewer is a backend service that processes datasets from the Hugging Face Hub and provides APIs for dataset viewing, search, and metadata access.

For information about specific service implementations, see [Core Services](#3). For details about shared libraries and utilities, see [Shared Libraries](#4). For data processing job runners, see [Data Processing](#5).

## High-Level Architecture Overview

The dataset-viewer follows a microservices architecture with clear separation of concerns. The system processes datasets through a directed acyclic graph of processing steps, caches results in MongoDB, stores assets in S3, and serves data through multiple specialized API services.

### System Components Diagram

```mermaid
graph TB
    subgraph "External Systems"
        HF["Hugging Face Hub<br/>Dataset Repository"]
        Users["External Users<br/>API Clients"]
    end
    
    subgraph "Load Balancing Layer"
        ALB["AWS ALB<br/>datasets-server.huggingface.co"]
    end
    
    subgraph "API Services Layer"
        API["api service<br/>:8080"]
        Rows["rows service<br/>:8082"] 
        Search["search service<br/>:8083"]
        Admin["admin service<br/>:8081"]
        SSE["sse-api service<br/>:8085"]
        Webhook["webhook service<br/>:8087"]
    end
    
    subgraph "Processing Layer"
        WorkerHeavy["worker-heavy<br/>difficulty 70-100"]
        WorkerMedium["worker-medium<br/>difficulty 40-70"] 
        WorkerLight["worker-light<br/>difficulty 0-40"]
    end
    
    subgraph "Storage Layer"
        MongoDB[("MongoDB<br/>cache & queue")]
        S3[("S3 Storage<br/>parquet & assets")]
        DuckDB["DuckDB Indexes<br/>search & filter"]
    end
    
    subgraph "Maintenance Jobs"
        Backfill["backfill job<br/>cache_maintenance"]
        Metrics["metrics collection<br/>queue & cache"]
    end
    
    Users --> ALB
    ALB --> API
    ALB --> Rows  
    ALB --> Search
    ALB --> Admin
    ALB --> SSE
    ALB --> Webhook
    
    HF --> Webhook
    Webhook --> WorkerHeavy
    Webhook --> WorkerMedium
    Webhook --> WorkerLight
    
    API --> MongoDB
    Rows --> MongoDB
    Search --> MongoDB
    Search --> DuckDB
    Admin --> MongoDB
    SSE --> MongoDB
    
    WorkerHeavy --> MongoDB
    WorkerHeavy --> S3
    WorkerMedium --> MongoDB
    WorkerLight --> MongoDB
    
    Backfill --> MongoDB
    Metrics --> MongoDB
```

Sources: [chart/env/prod.yaml:1-585](), [Makefile:1-64](), [chart/values.yaml:1-630]()

### Processing Graph Architecture

The system uses a directed acyclic graph defined in `ProcessingGraph` to orchestrate dataset processing steps with dependencies.

```mermaid
graph TD
    subgraph "Root Steps"
        ConfigNames["dataset-config-names<br/>ProcessingStep"]
        Filetypes["dataset-filetypes<br/>ProcessingStep"]
    end
    
    subgraph "Config Level Processing"
        ParquetAndInfo["config-parquet-and-info<br/>triggered_by: dataset-config-names"]
        SplitNames["config-split-names<br/>triggered_by: [dataset-config-names, config-info]"]
        Parquet["config-parquet<br/>triggered_by: config-parquet-and-info"]
        Info["config-info<br/>triggered_by: config-parquet-and-info"]
    end
    
    subgraph "Split Level Processing"  
        FirstRows["split-first-rows<br/>triggered_by: [config-split-names, config-parquet-metadata]"]
        Statistics["split-descriptive-statistics<br/>triggered_by: config-parquet-metadata"]
        ImageUrls["split-image-url-columns<br/>triggered_by: split-first-rows"]
    end
    
    subgraph "Dataset Level Aggregation"
        DatasetInfo["dataset-info<br/>triggered_by: [dataset-config-names, config-info]"]
        DatasetSize["dataset-size<br/>triggered_by: [dataset-config-names, config-size]"]
        HubCache["dataset-hub-cache<br/>triggered_by: [dataset-is-valid, dataset-size, ...]"]
    end
    
    ConfigNames --> ParquetAndInfo
    ConfigNames --> SplitNames
    ParquetAndInfo --> Parquet
    ParquetAndInfo --> Info
    Parquet --> FirstRows
    Info --> SplitNames
    SplitNames --> FirstRows
    FirstRows --> ImageUrls
    Info --> DatasetInfo
    DatasetInfo --> HubCache
```

Sources: [libs/libcommon/src/libcommon/processing_graph.py:490-705](), [libs/libcommon/tests/test_processing_graph.py:1-402]()

## Service Architecture  

### Core Service Components

The system consists of six main microservices, each with specific responsibilities:

| Service | Port | Purpose | Key Classes |
|---------|------|---------|-------------|
| `api` | 8080 | Dataset metadata APIs | N/A |
| `rows` | 8082 | Paginated dataset content | N/A |
| `search` | 8083 | Full-text search & filtering | N/A |
| `admin` | 8081 | System administration | N/A |
| `sse-api` | 8085 | Server-sent events | N/A |
| `webhook` | 8087 | Hub webhook integration | N/A |

### Worker Service Architecture

The worker service implements a difficulty-based job distribution system with three worker types:

```mermaid
graph LR
    subgraph "Job Queue"
        Queue[("MongoDB Queue<br/>JobDocument")]
    end
    
    subgraph "Worker Pools"
        Heavy["worker-heavy<br/>workerDifficultyMin: 70<br/>workerDifficultyMax: 100<br/>replicas: 4-40"]
        Medium["worker-medium<br/>workerDifficultyMin: 40<br/>workerDifficultyMax: 70<br/>replicas: 10-80"] 
        Light["worker-light<br/>workerDifficultyMin: 0<br/>workerDifficultyMax: 40<br/>replicas: 4-50"]
    end
    
    subgraph "Job Runners"
        ConfigNames["DatasetConfigNamesJobRunner<br/>difficulty: 50"]
        ParquetConv["ConfigParquetAndInfoJobRunner<br/>difficulty: 70"]
        FirstRows["SplitFirstRowsJobRunner<br/>difficulty: 70"]
        Stats["SplitDescriptiveStatisticsJobRunner<br/>difficulty: 70"]
    end
    
    Queue --> Heavy
    Queue --> Medium  
    Queue --> Light
    
    Heavy --> ParquetConv
    Heavy --> FirstRows
    Heavy --> Stats
    Medium --> ConfigNames
    Light --> ConfigNames
```

Sources: [chart/env/prod.yaml:462-550](), [services/worker/src/worker/dtos.py:11-14](), [libs/libcommon/src/libcommon/processing_graph.py:490-705]()

### Service Communication Pattern

```mermaid
sequenceDiagram
    participant User
    participant ALB as "AWS ALB"
    participant API as "api service"
    participant Cache as "MongoDB Cache"
    participant Queue as "MongoDB Queue"  
    participant Worker as "worker service"
    participant S3 as "S3 Storage"
    
    User->>ALB: GET /dataset-info
    ALB->>API: Forward request
    API->>Cache: get_previous_step_or_raise()
    
    alt Cache Hit
        Cache-->>API: Return cached response
        API-->>User: Dataset info
    else Cache Miss
        API->>Queue: Queue job if missing
        Queue-->>API: Job queued
        API-->>User: 404 or processing status
        
        Worker->>Queue: start_job()
        Worker->>S3: Process dataset
        Worker->>Cache: upsert_response()
        Worker->>Queue: finish_job()
    end
```

Sources: [libcommon/simple_cache.py functions referenced in services](), [Queue operations in worker service]()

## Data Processing Pipeline

### Processing Step Execution Flow

The data processing follows the `ProcessingGraph` specification with automatic dependency resolution:

```mermaid
graph TD
    subgraph "Job Orchestration"
        Orchestrator["orchestrator.py<br/>backfill_dataset()"]
        Plan["DatasetBackfillPlan<br/>get_dataset_backfill_plan()"]
    end
    
    subgraph "Job Execution"
        JobRunner["DatasetJobRunner<br/>ConfigJobRunner<br/>SplitJobRunner"]
        ResultHandler["JobResult<br/>CompleteJobResult"]
    end
    
    subgraph "Processing Steps"
        Step1["dataset-config-names<br/>job_runner_version: 1<br/>difficulty: 50"]
        Step2["config-parquet-and-info<br/>job_runner_version: 4<br/>difficulty: 70"]
        Step3["split-first-rows<br/>job_runner_version: 4<br/>difficulty: 70"]
    end
    
    Orchestrator --> Plan
    Plan --> JobRunner
    JobRunner --> Step1
    Step1 --> Step2
    Step2 --> Step3
    Step3 --> ResultHandler
```

Sources: [libs/libcommon/src/libcommon/operations.py functions](), [services/worker/src/worker/dtos.py:16-30](), [libs/libcommon/src/libcommon/processing_graph.py:82-122]()

### Job Runner Implementation Pattern

Each processing step is implemented as a job runner following a common pattern:

```mermaid
classDiagram
    class JobRunner {
        +compute() JobResult
        +pre_compute() None
        +post_compute() None
    }
    
    class DatasetJobRunner {
        +dataset: str
        +get_job_type() str
    }
    
    class ConfigJobRunner {
        +dataset: str
        +config: str
    }
    
    class SplitJobRunner {
        +dataset: str
        +config: str  
        +split: str
    }
    
    class DatasetConfigNamesJobRunner {
        +compute() JobResult
    }
    
    class SplitFirstRowsJobRunner {
        +compute() JobResult
    }
    
    JobRunner <|-- DatasetJobRunner
    JobRunner <|-- ConfigJobRunner  
    JobRunner <|-- SplitJobRunner
    DatasetJobRunner <|-- DatasetConfigNamesJobRunner
    SplitJobRunner <|-- SplitFirstRowsJobRunner
```

Sources: [services/worker/src/worker/job_runners/ directory structure](), [services/worker/src/worker/dtos.py:17-29]()

## Storage Architecture

### MongoDB Schema and Collections

The system uses MongoDB for caching processed results and managing job queues:

```mermaid
graph LR
    subgraph "MongoDB Databases"
        CacheDB["datasets_server_cache<br/>CacheMongoResource"]
        QueueDB["datasets_server_queue<br/>QueueMongoResource"]
        MaintenanceDB["datasets_server_maintenance<br/>Migration history"]
    end
    
    subgraph "Cache Collections"
        CacheEntries["Cache Entries<br/>CachedArtifact documents<br/>kind + dataset + config + split"]
    end
    
    subgraph "Queue Collections" 
        Jobs["Job Documents<br/>JobDocument<br/>type + params + priority"]
        Locks["Job Locks<br/>Concurrency control"]
    end
    
    CacheDB --> CacheEntries
    QueueDB --> Jobs
    QueueDB --> Locks
```

Sources: [chart/values.yaml:162-167](), [libs/libcommon/resources.py MongoDB classes](), [libs/libcommon/simple_cache.py cache operations]()

### S3 Storage Organization

Assets and processed datasets are stored in S3 with organized bucket structure:

```mermaid
graph TD
    subgraph "S3 Buckets"
        Assets["hf-datasets-server-statics<br/>assets/"]
        CachedAssets["hf-datasets-server-statics<br/>cached-assets/"]
        Parquet["Dataset Repositories<br/>refs/convert/parquet"]
    end
    
    subgraph "Asset Types"
        Images["Image assets<br/>.jpg, .png files"]
        Audio["Audio assets<br/>.wav, .mp3 files"]
        Thumbnails["Generated thumbnails<br/>Processed images"]
    end
    
    subgraph "Parquet Files"
        ConfigParquet["config parquet files<br/>train.parquet, test.parquet"]
        Metadata["parquet metadata<br/>.parquet.metadata files"]
    end
    
    Assets --> Images
    Assets --> Audio
    CachedAssets --> Thumbnails
    Parquet --> ConfigParquet
    Parquet --> Metadata
```

Sources: [chart/env/prod.yaml:137-143](), [chart/values.yaml:240-252](), [libcommon/storage_client.py S3 operations]()

### DuckDB Search Indexes

The search service uses DuckDB for efficient filtering and full-text search:

```mermaid
graph LR
    subgraph "DuckDB Storage"
        LocalCache["/tmp/duckdb-index<br/>Local cache directory"]
        IndexFiles["dataset-split.duckdb<br/>Per-split index files"]
    end
    
    subgraph "Index Operations"
        Builder["DuckDB index builder<br/>From parquet files"]
        Query["Query processor<br/>Filter & search operations"]
    end
    
    subgraph "Data Sources"
        ParquetFiles["Parquet files<br/>From S3 storage"]
        Metadata["Parquet metadata<br/>Schema information"]
    end
    
    ParquetFiles --> Builder
    Metadata --> Builder
    Builder --> IndexFiles
    IndexFiles --> LocalCache
    LocalCache --> Query
```

Sources: [chart/values.yaml:258-271](), [libapi/duckdb.py DuckDB operations](), [search service DuckDB integration]()

## Deployment Architecture

### Kubernetes Deployment Structure

The system is deployed on Kubernetes with environment-specific configurations:

```mermaid
graph TB
    subgraph "Production Environment"
        ProdIngress["ALB Ingress<br/>datasets-server.huggingface.co<br/>hub-datasets-server-prod"]
        ProdServices["Production Services<br/>api: 20 replicas<br/>rows: 12 replicas<br/>search: 3 replicas"]
    end
    
    subgraph "Staging Environment"  
        StagingIngress["ALB Ingress<br/>datasets-server.us.dev.moon.huggingface.tech<br/>hub-datasets-server-staging"]
        StagingServices["Staging Services<br/>All services: 1 replica"]
    end
    
    subgraph "Scheduled Jobs"
        BackfillJob["backfill CronJob<br/>schedule: '05 12 * * *'<br/>Daily at 12:05"]
        MetricsJob["metrics CronJob<br/>schedule: '*/10 * * * *'<br/>Every 10 minutes"]
        RetryJob["retry errors CronJob<br/>schedule: '0 */2 * * *'<br/>Every 2 hours"]
    end
    
    subgraph "Storage Persistence"
        DuckDBPVC["datasets-server-duckdb-pvc<br/>DuckDB index storage"]
        ParquetPVC["datasets-server-parquet-pvc<br/>Parquet metadata storage"]
    end
```

Sources: [chart/env/prod.yaml:255-585](), [chart/env/staging.yaml:160-329](), [chart/values.yaml:307-374]()

### Resource Allocation and Scaling

The deployment uses different resource allocations and autoscaling for each service type:

| Service | CPU Request | Memory Request | CPU Limit | Memory Limit | Autoscaling |
|---------|-------------|----------------|-----------|--------------|-------------|
| `api` | 4 | 14Gi | 4 | 14Gi | 20 replicas |
| `rows` | 1 | 6500Mi | 4 | 6500Mi | 12 replicas |
| `search` | 1 | 250Gi | 64 | 250Gi | 3 replicas |
| `worker-heavy` | 8 | 34Gi | 8 | 44Gi | 4-40 replicas |
| `worker-medium` | 2 | 14Gi | 2 | 14Gi | 10-80 replicas |
| `worker-light` | 200m | 100Mi | 2 | 1Gi | 4-50 replicas |

Sources: [chart/env/prod.yaml:345-549]()

### Monitoring and Maintenance

```mermaid
graph LR
    subgraph "Monitoring Stack"
        Prometheus["Prometheus<br/>Metrics collection"]
        Grafana["Grafana<br/>Dashboard visualization"] 
        Alerts["Alert Manager<br/>Notification system"]
    end
    
    subgraph "Maintenance Jobs"
        BackfillAction["backfill action<br/>cache_maintenance.backfill"]
        MetricsCollection["collect-queue-metrics<br/>collect-cache-metrics"]
        CleanupJobs["Directory cleaning<br/>Expired file removal"]
    end
    
    subgraph "Job Configuration"
        JobConfig["JobConfig.from_env()<br/>Environment-based config"]
        Actions["Action types:<br/>backfill, collect-*-metrics, post-messages"]
    end
    
    Prometheus --> Grafana
    Prometheus --> Alerts
    JobConfig --> BackfillAction
    JobConfig --> MetricsCollection
    MetricsCollection --> Prometheus
```

Sources: [jobs/cache_maintenance/src/cache_maintenance/main.py:19-118](), [jobs/cache_maintenance/src/cache_maintenance/config.py:69-97](), [chart/env/prod.yaml:170-253]()

---

