<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/dataset-viewer · page 1 Overview · fetched 2026-10-26 -->

# Overview

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
- [front/admin_ui/poetry.lock](front/admin_ui/poetry.lock)
- [jobs/cache_maintenance/README.md](jobs/cache_maintenance/README.md)
- [jobs/cache_maintenance/poetry.lock](jobs/cache_maintenance/poetry.lock)
- [jobs/cache_maintenance/src/cache_maintenance/backfill.py](jobs/cache_maintenance/src/cache_maintenance/backfill.py)
- [jobs/cache_maintenance/src/cache_maintenance/config.py](jobs/cache_maintenance/src/cache_maintenance/config.py)
- [jobs/cache_maintenance/src/cache_maintenance/main.py](jobs/cache_maintenance/src/cache_maintenance/main.py)
- [jobs/mongodb_migration/poetry.lock](jobs/mongodb_migration/poetry.lock)
- [libs/libapi/poetry.lock](libs/libapi/poetry.lock)
- [libs/libcommon/poetry.lock](libs/libcommon/poetry.lock)
- [services/admin/poetry.lock](services/admin/poetry.lock)
- [services/api/poetry.lock](services/api/poetry.lock)
- [services/rows/poetry.lock](services/rows/poetry.lock)
- [services/search/poetry.lock](services/search/poetry.lock)
- [services/sse-api/poetry.lock](services/sse-api/poetry.lock)
- [services/worker/poetry.lock](services/worker/poetry.lock)

</details>



The dataset-viewer is a microservices backend system that powers the Hugging Face Dataset Viewer interface. It provides pre-computed dataset information and content through REST APIs for all datasets on the Hugging Face Hub. The system automatically processes datasets into optimized formats, extracts metadata, and serves paginated data access, search capabilities, and statistical insights.

This document covers the overall system architecture, core services, and data processing pipeline. For specific service implementation details, see the individual service documentation in sections [3.1](#3.1) through [3.5]. For deployment and infrastructure details, see [7.1](#7.1).

## System Architecture

The dataset-viewer implements a cloud-native microservices architecture deployed on Kubernetes, with services organized into API, processing, and storage layers.

### High-Level Architecture

```mermaid
graph TB
    subgraph "External"
        HF["Hugging Face Hub<br/>datasets-server.huggingface.co"]
        Users["External Users"]
    end
    
    subgraph "Load Balancing"
        ALB["AWS Application Load Balancer"]
    end
    
    subgraph "API Services"
        API["api-service<br/>:8080"]
        Rows["rows-service<br/>:8082"] 
        Search["search-service<br/>:8083"]
        Admin["admin-service<br/>:8081"]
        SSE["sse-api-service<br/>:8085"]
        Webhook["webhook-service<br/>:8087"]
    end
    
    subgraph "Processing"
        WorkerHeavy["worker-heavy<br/>difficulty: 70-100"]
        WorkerMedium["worker-medium<br/>difficulty: 40-70"]
        WorkerLight["worker-light<br/>difficulty: 0-40"]
    end
    
    subgraph "Storage"
        MongoDB["MongoDB<br/>cache & queue databases"]
        S3["S3 Storage<br/>parquet files & assets"]
        DuckDB["DuckDB Indexes<br/>search & filter data"]
    end
    
    Users --> ALB
    ALB --> API
    ALB --> Rows
    ALB --> Search
    ALB --> Admin
    ALB --> SSE
    
    HF --> Webhook
    Webhook --> WorkerHeavy
    Webhook --> WorkerMedium  
    Webhook --> WorkerLight
    
    API --> MongoDB
    Rows --> MongoDB
    Rows --> S3
    Search --> DuckDB
    Admin --> MongoDB
    
    WorkerHeavy --> MongoDB
    WorkerHeavy --> S3
    WorkerMedium --> MongoDB
    WorkerLight --> MongoDB
```

Sources: [chart/env/prod.yaml:1-585](), [chart/values.yaml:1-630](), [README.md:1-67]()

## Core Services

The system consists of six primary microservices, each with distinct responsibilities for serving and processing dataset information.

### Service Architecture Diagram

```mermaid
graph LR
    subgraph "Client Layer"
        WebUI["Dataset Viewer UI"]
        APIClients["API Clients"]
    end
    
    subgraph "Service Layer"
        API["api-service<br/>PORT_API=8180<br/>dataset metadata"]
        Rows["rows-service<br/>PORT_ROWS=8182<br/>paginated content"]
        Search["search-service<br/>PORT_SEARCH=8183<br/>full-text search"]
        Admin["admin-service<br/>PORT_ADMIN=8181<br/>management UI"]
        SSE["sse-api-service<br/>PORT_SSE_API=8185<br/>real-time updates"]
        Webhook["webhook-service<br/>PORT_WEBHOOK=8187<br/>hub integration"]
    end
    
    subgraph "Data Layer"
        Cache["MongoDB<br/>datasets_server_cache"]
        Queue["MongoDB<br/>datasets_server_queue"]
        Assets["S3<br/>hf-datasets-server-statics"]
        Indexes["DuckDB<br/>search indexes"]
    end
    
    WebUI --> API
    WebUI --> Rows
    WebUI --> Search
    APIClients --> API
    
    API --> Cache
    Rows --> Cache
    Rows --> Assets
    Search --> Indexes
    Admin --> Cache
    Admin --> Queue
    SSE --> Cache
    Webhook --> Queue
```

Sources: [Makefile:2-13](), [chart/values.yaml:162-167](), [chart/env/prod.yaml:138-143]()

### Service Responsibilities

| Service | Purpose | Key Features |
|---------|---------|--------------|
| `api-service` | Dataset metadata and configuration | Config names, split info, dataset info endpoints |
| `rows-service` | Paginated dataset content access | Parquet file streaming, asset serving, row slicing |
| `search-service` | Full-text search and filtering | DuckDB integration, search indexing, filter operations |
| `admin-service` | System administration and monitoring | Gradio UI, cache reports, job management |
| `sse-api-service` | Server-sent events for real-time updates | Live status updates, progress streaming |
| `webhook-service` | Hugging Face Hub integration | Dataset change notifications, job triggering |

Sources: [chart/values.yaml:439-629](), [chart/env/prod.yaml:274-584]()

## Data Processing Pipeline

The system processes datasets through a multi-stage pipeline that converts raw datasets into optimized formats for fast access and search.

```mermaid
graph TD
    subgraph "Input"
        HubDataset["Hugging Face Hub<br/>Dataset Repository"]
    end
    
    subgraph "Processing Steps"
        ConfigNames["dataset-config-names<br/>extract configurations"]
        SplitNames["dataset-split-names<br/>identify data splits"] 
        ParquetConv["dataset-parquet<br/>convert to parquet"]
        ParquetMeta["parquet-and-info<br/>extract metadata"]
        FirstRows["dataset-first-rows<br/>sample preview data"]
        Statistics["dataset-statistics<br/>compute descriptive stats"]
        SearchIndex["dataset-duckdb-index<br/>build search indexes"]
    end
    
    subgraph "Output Storage"
        CacheDB["MongoDB Cache<br/>processed results"]
        ParquetFiles["S3 Storage<br/>refs/convert/parquet"]
        DuckDBFiles["DuckDB Indexes<br/>refs/convert/duckdb"]
    end
    
    HubDataset --> ConfigNames
    ConfigNames --> SplitNames
    ConfigNames --> ParquetConv
    ParquetConv --> ParquetMeta
    ParquetMeta --> FirstRows
    ParquetMeta --> Statistics  
    ParquetMeta --> SearchIndex
    
    ParquetConv --> ParquetFiles
    FirstRows --> CacheDB
    Statistics --> CacheDB
    SearchIndex --> DuckDBFiles
```

Sources: [chart/values.yaml:199-271](), [chart/env/prod.yaml:127-153]()

## Deployment Configuration

The system deploys to production at `datasets-server.huggingface.co` with the following service scaling:

| Service | Replicas | Resources | Node Selector |
|---------|----------|-----------|---------------|
| `api` | 20 | 4 CPU, 14Gi RAM | `role-datasets-server-api` |
| `rows` | 12 | 1-4 CPU, 6.5Gi RAM | `role-datasets-server-rows` |
| `search` | 3 | 1-64 CPU, 250Gi RAM | `role-datasets-server-search` |
| `worker-heavy` | 4-40 (autoscaling) | 8 CPU, 44Gi RAM | `role-datasets-server-worker` |
| `worker-medium` | 10-80 (autoscaling) | 2 CPU, 14Gi RAM | `role-datasets-server-worker` |
| `worker-light` | 4-50 (autoscaling) | 200m-2 CPU, 1Gi RAM | `role-datasets-server-worker-light` |

Sources: [chart/env/prod.yaml:318-550]()

## Storage Systems

The architecture uses three primary storage systems:

- **MongoDB**: Stores processed cache responses and job queue data in `datasets_server_cache` and `datasets_server_queue` databases
- **S3**: Hosts converted Parquet files and static assets under `hf-datasets-server-statics/` with CloudFront CDN distribution  
- **DuckDB**: Provides search indexes stored as files for full-text search and filtering capabilities

Sources: [chart/values.yaml:162-271](), [chart/env/prod.yaml:138-153]()

---

