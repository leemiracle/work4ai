<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/dataset-viewer · page 7 Deployment and Operations · fetched 2026-10-26 -->

# Deployment and Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [chart/Chart.yaml](chart/Chart.yaml)
- [chart/env/prod.yaml](chart/env/prod.yaml)
- [chart/env/staging.yaml](chart/env/staging.yaml)
- [chart/templates/_common/_helpers.tpl](chart/templates/_common/_helpers.tpl)
- [chart/templates/cron-jobs/backfill/_container.tpl](chart/templates/cron-jobs/backfill/_container.tpl)
- [chart/values.yaml](chart/values.yaml)
- [front/admin_ui/README.md](front/admin_ui/README.md)
- [front/admin_ui/app.py](front/admin_ui/app.py)
- [front/admin_ui/packages.txt](front/admin_ui/packages.txt)
- [front/admin_ui/pyproject.toml](front/admin_ui/pyproject.toml)
- [front/admin_ui/requirements.txt](front/admin_ui/requirements.txt)
- [jobs/cache_maintenance/README.md](jobs/cache_maintenance/README.md)
- [jobs/cache_maintenance/src/cache_maintenance/backfill.py](jobs/cache_maintenance/src/cache_maintenance/backfill.py)
- [jobs/cache_maintenance/src/cache_maintenance/config.py](jobs/cache_maintenance/src/cache_maintenance/config.py)
- [jobs/cache_maintenance/src/cache_maintenance/main.py](jobs/cache_maintenance/src/cache_maintenance/main.py)
- [tools/Docker.mk](tools/Docker.mk)

</details>



This page covers the infrastructure deployment, configuration management, and operational procedures for the dataset-viewer system. It provides technical details on Kubernetes deployments, service configuration, monitoring capabilities, and administrative tools.

For information about the individual microservices and their APIs, see [Core Services](#3). For configuration of shared libraries and common functionality, see [Shared Libraries](#4).

## Infrastructure Overview

The dataset-viewer system deploys as a microservices architecture on Kubernetes, using Helm charts for configuration management. The deployment includes API services, worker processes, scheduled jobs, and administrative interfaces.

### Deployment Architecture

```mermaid
graph TB
    subgraph "AWS Load Balancers"
        ALB["ALB<br/>datasets-server.huggingface.co"]
        InternalALB["Internal ALB<br/>internal.datasets-server.huggingface.co"]
    end
    
    subgraph "Kubernetes Cluster"
        subgraph "API Services"
            API["api<br/>20 replicas<br/>Port 8080"]
            Rows["rows<br/>12 replicas<br/>Port 8080"] 
            Search["search<br/>3 replicas<br/>Port 8080"]
            Admin["admin<br/>2 replicas<br/>Port 8080"]
            SSE["sse-api<br/>2 replicas<br/>Port 8080"]
            Webhook["webhook<br/>4 replicas<br/>Port 8080"]
        end
        
        subgraph "Worker Pools"
            HeavyWorker["heavy<br/>4-40 replicas<br/>Difficulty 70-100"]
            MediumWorker["medium<br/>10-80 replicas<br/>Difficulty 40-70"]
            LightWorker["light<br/>4-50 replicas<br/>Difficulty 0-40"]
        end
        
        subgraph "Scheduled Jobs"
            Backfill["backfill<br/>Daily 12:05"]
            BackfillRetry["backfillRetryableErrors<br/>Every 2 hours"]
            QueueMetrics["queueMetricsCollector<br/>Every 10 minutes"]
            CacheMetrics["cacheMetricsCollector<br/>Every 3 hours"]
        end
    end
    
    subgraph "External Services"
        MongoDB["MongoDB Atlas<br/>Cache & Queue"]
        S3["S3 Buckets<br/>Assets & Parquet"]
        CloudFront["CloudFront CDN"]
    end
    
    ALB --> API
    ALB --> Rows
    ALB --> Search
    ALB --> SSE
    ALB --> Webhook
    InternalALB --> Admin
    
    API --> MongoDB
    Rows --> MongoDB
    Search --> MongoDB
    Admin --> MongoDB
    
    HeavyWorker --> MongoDB
    HeavyWorker --> S3
    MediumWorker --> MongoDB
    LightWorker --> MongoDB
    
    Backfill --> MongoDB
    BackfillRetry --> MongoDB
    QueueMetrics --> MongoDB
    CacheMetrics --> MongoDB
    
    S3 --> CloudFront
```

Sources: [chart/env/prod.yaml:1-585](), [chart/values.yaml:1-630](), [chart/env/staging.yaml:1-329]()

### Service Node Distribution

```mermaid
graph TB
    subgraph "Node Groups"
        subgraph "API Tier Nodes"
            APINodes["role-datasets-server-api<br/>API Service Nodes"]
            RowsNodes["role-datasets-server-rows<br/>Rows Service Nodes"]
            SearchNodes["role-datasets-server-search<br/>Search Service Nodes"]
            GeneralNodes["role-datasets-server<br/>General Service Nodes"]
        end
        
        subgraph "Worker Tier Nodes"
            WorkerNodes["role-datasets-server-worker<br/>Heavy/Medium Workers"]
            LightNodes["role-datasets-server-worker-light<br/>Light Workers"]
            WebhookNodes["role-datasets-server-webhook<br/>Webhook Service"]
        end
    end
    
    subgraph "Service Placement"
        API["api service"] --> APINodes
        Rows["rows service"] --> RowsNodes
        Search["search service"] --> SearchNodes
        Admin["admin service"] --> GeneralNodes
        SSE["sse-api service"] --> GeneralNodes
        
        HeavyWorker["heavy workers"] --> WorkerNodes
        MediumWorker["medium workers"] --> WorkerNodes
        LightWorker["light workers"] --> LightNodes
        Webhook["webhook service"] --> WebhookNodes
    end
    
    subgraph "Tolerations & Taints"
        APINodes -.-> APItaint["huggingface.co/datasets-server-api"]
        RowsNodes -.-> Rowstaint["huggingface.co/datasets-server-rows"]
        SearchNodes -.-> Searchtaint["huggingface.co/datasets-server-search"]
        GeneralNodes -.-> Generaltaint["huggingface.co/datasets-server"]
        WorkerNodes -.-> Workertaint["huggingface.co/datasets-server-worker"]
        LightNodes -.-> Lighttaint["huggingface.co/datasets-server-worker-light"]
        WebhookNodes -.-> Webhooktaint["huggingface.co/datasets-server-webhook"]
    end
```

Sources: [chart/env/prod.yaml:323-533](), [chart/env/prod.yaml:557-561]()

## Kubernetes Deployment

The system uses Helm charts for Kubernetes deployment with environment-specific value overrides. The main chart is located in the `chart/` directory with templates for all services and jobs.

### Helm Chart Structure

The Helm chart includes:
- **Services**: `admin`, `api`, `rows`, `search`, `sseApi`, `webhook`, `workers`
- **Jobs**: `mongodbMigration` (pre-install hook)  
- **CronJobs**: `backfill`, `backfillRetryableErrors`, `queueMetricsCollector`, `cacheMetricsCollector`, `postMessages`
- **Ingress**: ALB configuration for external and internal access
- **Secrets**: Infisical integration for secret management

### Container Image Management

```mermaid
graph LR
    subgraph "Image Registry"
        Registry["huggingface registry"]
    end
    
    subgraph "Service Images"
        AdminImg["datasets-server-services-admin:sha-fb3399a"]
        APIImg["datasets-server-services-api:sha-fb3399a"]
        RowsImg["datasets-server-services-rows:sha-fb3399a"]
        SearchImg["datasets-server-services-search:sha-fb3399a"]
        SSEImg["datasets-server-services-sse-api:sha-fb3399a"]
        WorkerImg["datasets-server-services-worker:sha-fb3399a"]
        WebhookImg["datasets-server-services-webhook:sha-fb3399a"]
    end
    
    subgraph "Job Images"
        MigrationImg["datasets-server-jobs-mongodb_migration:sha-fb3399a"]
        MaintenanceImg["datasets-server-jobs-cache_maintenance:sha-fb3399a"]
    end
    
    Registry --> AdminImg
    Registry --> APIImg
    Registry --> RowsImg
    Registry --> SearchImg
    Registry --> SSEImg
    Registry --> WorkerImg
    Registry --> WebhookImg
    Registry --> MigrationImg
    Registry --> MaintenanceImg
```

Sources: [chart/env/prod.yaml:17-66](), [chart/values.yaml:24-78]()

### Resource Allocation

The production environment defines specific resource requests and limits for each service:

| Service | CPU Request | Memory Request | CPU Limit | Memory Limit | Replicas |
|---------|-------------|----------------|-----------|--------------|-----------|
| `api` | 4 | 14Gi | 4 | 14Gi | 20 |
| `rows` | 1 | 6500Mi | 4 | 6500Mi | 12 |
| `search` | 1 | 250Gi | 64 | 250Gi | 3 |
| `admin` | 1 | 8Gi | 4 | 8Gi | 2 |
| `sse-api` | 1 | 512Mi | 4 | 4Gi | 2 |
| `webhook` | 4 | 4Gi | 4 | 4Gi | 4 |

Worker pools have different resource profiles based on workload difficulty:
- **Heavy Workers**: 8 CPU, 34-44Gi memory, 4-40 replicas
- **Medium Workers**: 2 CPU, 14Gi memory, 10-80 replicas  
- **Light Workers**: 200m-2 CPU, 100Mi-1Gi memory, 4-50 replicas

Sources: [chart/env/prod.yaml:307-584]()

### Autoscaling Configuration

Workers implement Horizontal Pod Autoscaling based on queue metrics:

```mermaid
graph TB
    subgraph "Autoscaling Metrics"
        QueueMetric["worker_size_jobs_count<br/>Queue Length Metric"]
    end
    
    subgraph "Scaling Targets"
        HeavyTarget["Heavy Workers<br/>Target: 50 jobs<br/>Min: 4, Max: 40"]
        MediumTarget["Medium Workers<br/>Target: 150 jobs<br/>Min: 10, Max: 80"]
        LightTarget["Light Workers<br/>Target: 150 jobs<br/>Min: 4, Max: 50"]
    end
    
    QueueMetric --> HeavyTarget
    QueueMetric --> MediumTarget
    QueueMetric --> LightTarget
    
    subgraph "Worker Difficulty Ranges"
        HeavyRange["Heavy: 70-100 difficulty"]
        MediumRange["Medium: 40-70 difficulty"]
        LightRange["Light: 0-40 difficulty"]
    end
    
    HeavyTarget -.-> HeavyRange
    MediumTarget -.-> MediumRange
    LightTarget -.-> LightRange
```

Sources: [chart/env/prod.yaml:477-542]()

## Configuration Management

Configuration is managed through Helm values with environment-specific overrides. The system uses Infisical for secret management and supports both file-based and S3-based storage protocols.

### Environment Configuration

The system supports multiple deployment environments:
- **Production**: `chart/env/prod.yaml` - Full-scale deployment with high availability
- **Staging**: `chart/env/staging.yaml` - Reduced resources for testing

Key configuration differences between environments:

| Setting | Production | Staging |
|---------|------------|---------|
| Domain | `datasets-server.huggingface.co` | `datasets-server.us.dev.moon.huggingface.tech` |
| Log Level | `INFO` | `DEBUG` |
| Backfill | Enabled daily | Disabled |
| Worker Replicas | 4-40 (Heavy) | 1-5 (All) |
| Resource Limits | High (64 CPU for search) | Low (1 CPU limit) |

Sources: [chart/env/prod.yaml:115-122](), [chart/env/staging.yaml:113-119]()

### Secret Management

```mermaid
graph LR
    subgraph "Infisical"
        InfisicalProd["prod-us-east-1 environment"]
        InfisicalStaging["ephemeral-us-east-1 environment"]
    end
    
    subgraph "Kubernetes Secrets"
        MongoSecret["mongo-url"]
        HFTokenSecret["app-hf-token"]
        ParquetTokenSecret["app-parquet-converter-hf-token"]
        WebhookSecret["hf-webhook-secret"]
        S3Secrets["s3-access-key-id<br/>s3-secret-access-key"]
        CloudFrontSecrets["cloudfront-key-pair-id<br/>cloudfront-private-key"]
    end
    
    subgraph "Application Usage"
        Services["API Services<br/>Workers<br/>Jobs"]
    end
    
    InfisicalProd --> MongoSecret
    InfisicalProd --> HFTokenSecret
    InfisicalProd --> ParquetTokenSecret
    InfisicalProd --> WebhookSecret
    InfisicalProd --> S3Secrets
    InfisicalProd --> CloudFrontSecrets
    
    MongoSecret --> Services
    HFTokenSecret --> Services
    ParquetTokenSecret --> Services
    WebhookSecret --> Services
    S3Secrets --> Services
    CloudFrontSecrets --> Services
```

Sources: [chart/env/prod.yaml:67-102](), [chart/values.yaml:92-140]()

### Storage Configuration

The system supports multiple storage backends for different asset types:

| Asset Type | Storage Protocol | Production Root | Staging Root |
|------------|------------------|-----------------|--------------|
| Assets | `s3` | `hf-datasets-server-statics/assets` | `hf-datasets-server-statics-staging/assets` |
| Cached Assets | `s3` | `hf-datasets-server-statics/cached-assets` | `hf-datasets-server-statics-staging/cached-assets` |
| Parquet Metadata | PVC | `datasets-server-parquet-pvc` | `datasets-server-parquet-pvc` |
| DuckDB Index | PVC | `datasets-server-duckdb-pvc` | `datasets-server-duckdb-pvc` |

Sources: [chart/env/prod.yaml:137-148](), [chart/env/staging.yaml:127-133]()

## Administration and Monitoring

The system provides comprehensive administration and monitoring capabilities through the admin service and scheduled maintenance jobs.

### Admin UI Interface

```mermaid
graph TB
    subgraph "Admin UI Components"
        GradioApp["front/admin_ui/app.py<br/>Gradio Application"]
        
        subgraph "Dashboard Tabs"
            HomeTab["Home Dashboard<br/>Dataset Coverage Stats"]
            JobsTab["View Pending Jobs<br/>Job Queue Analysis"]
            RefreshTab["Refresh Dataset Step<br/>Force Job Creation"]
            RecreateTab["Recreate Dataset<br/>Full Dataset Reset"]
            StatusTab["Dataset Status<br/>Cache & Job Inspection"]
        end
    end
    
    subgraph "Backend APIs"
        AdminAPI["admin service<br/>Port 8081"]
        
        subgraph "Admin Endpoints"
            HealthCheck["/admin/healthcheck"]
            PendingJobs["/admin/pending-jobs"]
            DatasetStatus["/admin/dataset-status"]
            ForceRefresh["/admin/force-refresh/{job_type}"]
            RecreateDataset["/admin/recreate-dataset"]
            NumInfos["/admin/num-dataset-infos-by-builder-name"]
        end
    end
    
    GradioApp --> AdminAPI
    HomeTab --> HealthCheck
    HomeTab --> NumInfos
    JobsTab --> PendingJobs
    RefreshTab --> ForceRefresh
    RecreateTab --> RecreateDataset
    StatusTab --> DatasetStatus
```

Sources: [front/admin_ui/app.py:35-44](), [front/admin_ui/app.py:115-272](), [front/admin_ui/app.py:459-526]()

### Scheduled Maintenance Jobs

The system runs several CronJob resources for automated maintenance:

```mermaid
graph TB
    subgraph "CronJob Schedule"
        Daily["Daily Jobs<br/>12:05 UTC"]
        Hourly["Every 2 Hours"]
        TenMin["Every 10 Minutes"]
        ThreeHour["Every 3 Hours"]
    end
    
    subgraph "Maintenance Actions"
        Backfill["backfill<br/>Update all datasets<br/>CACHE_MAINTENANCE_ACTION=backfill"]
        RetryErrors["backfillRetryableErrors<br/>Retry failed datasets<br/>CACHE_MAINTENANCE_ACTION=backfill-retryable-errors"]
        QueueMetrics["queueMetricsCollector<br/>Collect queue statistics<br/>CACHE_MAINTENANCE_ACTION=collect-queue-metrics"]
        CacheMetrics["cacheMetricsCollector<br/>Collect cache statistics<br/>CACHE_MAINTENANCE_ACTION=collect-cache-metrics"]
    end
    
    subgraph "Implementation"
        MaintenanceMain["cache_maintenance/main.py<br/>run_job()"]
        BackfillModule["cache_maintenance/backfill.py<br/>backfill_all_datasets()"]
        MetricsModules["cache_maintenance/queue_metrics.py<br/>cache_maintenance/cache_metrics.py"]
    end
    
    Daily --> Backfill
    Hourly --> RetryErrors
    TenMin --> QueueMetrics
    ThreeHour --> CacheMetrics
    
    Backfill --> MaintenanceMain
    RetryErrors --> MaintenanceMain
    QueueMetrics --> MaintenanceMain
    CacheMetrics --> MaintenanceMain
    
    MaintenanceMain --> BackfillModule
    MaintenanceMain --> MetricsModules
```

Sources: [chart/env/prod.yaml:170-252](), [jobs/cache_maintenance/src/cache_maintenance/main.py:19-110](), [jobs/cache_maintenance/src/cache_maintenance/backfill.py:43-142]()

### Metrics Collection and Monitoring

The maintenance jobs collect various operational metrics:

- **Queue Metrics**: Job counts by type, status, and worker difficulty
- **Cache Metrics**: Response cache hit rates, error distributions
- **Worker Size Metrics**: `worker_size_jobs_count` for autoscaling
- **Dataset Coverage**: Statistics on dataset processing success rates

Metrics are stored in MongoDB and exposed through the admin API for monitoring dashboards.

Sources: [jobs/cache_maintenance/src/cache_maintenance/main.py:76-90](), [chart/env/prod.yaml:220-252]()

### Operational Procedures

**Deployment Process:**
1. Update image tags in environment-specific values files
2. Deploy using Helm: `helm upgrade -f chart/env/prod.yaml`
3. Monitor deployment through admin UI and Kubernetes events

**Dataset Refresh:**
- Use admin UI "Refresh Dataset Step" tab to force processing
- Select job type, dataset, config, split, difficulty, and priority
- Jobs are queued based on processing graph dependencies

**Error Recovery:**
- `backfillRetryableErrors` CronJob runs every 2 hours to retry failed jobs
- Manual dataset recreation available through admin UI for severe issues
- Full dataset reset deletes all cache entries and assets

Sources: [front/admin_ui/app.py:459-526](), [front/admin_ui/app.py:543-581]()

---

