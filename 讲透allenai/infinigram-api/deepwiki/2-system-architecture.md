<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/infinigram-api · page 2 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [api/app.py](api/app.py)
- [docker-compose.yaml](docker-compose.yaml)

</details>



This document provides a comprehensive overview of the infinigram-api system architecture, describing its core components and how they interact to provide infinigram capabilities as a scalable service. For detailed information about individual components, refer to the specific component pages referenced throughout this document.

## Purpose and Scope

The infinigram-api system serves as a wrapper over the [infini-gram](https://infini-gram.io) technology, allowing it to be accessed through a web API. The architecture is designed to handle both quick, synchronous requests and long-running attribution tasks efficiently. This document explains:

- Core system components and their responsibilities
- How data flows through the system
- How components interact with each other
- Deployment architecture

For detailed information about the API endpoints, see [API](#3). For specifics on the Attribution Worker, see [Attribution Worker](#4).

## System Overview

The infinigram-api consists of several components that work together to provide a scalable and reliable service.

```mermaid
graph TB
    subgraph "Client Applications"
        Client["Client"]
    end
    
    subgraph "Frontend Layer"
        Proxy["NGINX Proxy<br>(/proxy)"]
    end
    
    subgraph "API Layer"
        API["FastAPI Application<br>(/api/app.py)"]
        HealthRouter["Health Router<br>(health_router)"]
        InfinigramRouter["Infinigram Router<br>(infinigram_router)"]
        AttributionRouter["Attribution Router<br>(attribution_router)"]
    end
    
    subgraph "Worker Layer"
        AttributionWorker["Attribution Worker<br>(/attribution_worker)"]
    end
    
    subgraph "Shared Services"
        Queue["Queue<br>(PostgreSQL)"]
        RedisCache["Cache<br>(Redis)"]
        OtelCollector["OpenTelemetry Collector<br>(otelcol)"]
    end
    
    subgraph "Data Layer"
        InfinigramArrays["Infinigram Arrays<br>(/mnt/infinigram-array)"]
    end
    
    Client --> Proxy
    Proxy --> API
    
    API --> HealthRouter
    API --> InfinigramRouter
    API --> AttributionRouter
    
    AttributionRouter --> Queue
    AttributionWorker --> Queue
    
    API --> RedisCache
    AttributionWorker --> RedisCache
    
    API --> InfinigramArrays
    AttributionWorker --> InfinigramArrays
    
    API --> OtelCollector
    AttributionWorker --> OtelCollector
```

Sources: [docker-compose.yaml:7-82](), [api/app.py:36-54](), [README.md:17-34]()

## Core Components

### API Service

The API service is built using FastAPI and serves as the main entry point for all client requests. It handles:

- Health checks for system status monitoring
- Infinigram index queries
- Document retrieval requests
- Coordination of attribution requests (queuing for processing by the worker)

The API connects to Redis for caching and PostgreSQL for the job queue. It uses OpenTelemetry for observability.

### Attribution Worker

The Attribution Worker is a separate service responsible for processing attribution requests asynchronously. These requests are typically more compute-intensive and would block the API if processed synchronously. The worker:

- Pulls attribution jobs from the PostgreSQL queue
- Processes them using the infinigram arrays
- Stores results back in the queue and Redis cache

### Proxy

An NGINX proxy sits in front of the API, providing:
- Load balancing
- SSL termination
- Request routing

### Queue

PostgreSQL is used as a job queue for attribution requests:
- The API adds attribution jobs to the queue
- The Attribution Worker pulls jobs from the queue
- Results are stored back in the queue for retrieval

### Cache

Redis provides caching for attribution results to improve performance for repeated requests.

### Infinigram Arrays

The infinigram arrays are machine learning models mounted as volumes in the system:
- v4_pileval_llama
- olmoe-mix-0924-dclm
- olmoe-mix-0924-nodclm 
- v4-olmoe-0125-1b-7b-anneal-adapt
- v4-olmo-2-1124-13b-anneal-adapt
- v4-olmo-2-0325-32b-anneal-adapt

### OpenTelemetry Collector

The OpenTelemetry collector gathers and exports observability data (traces, metrics) for monitoring the system's performance and health.

Sources: [docker-compose.yaml:7-82](), [api/app.py:36-54](), [README.md:17-34]()

## Request Flow

The flow of data through the system depends on the type of request:

```mermaid
sequenceDiagram
    participant Client
    participant Proxy as "NGINX Proxy"
    participant API as "FastAPI App (/api/app.py)"
    participant Cache as "Redis Cache"
    participant Queue as "PostgreSQL Queue"
    participant Worker as "Attribution Worker"
    participant Arrays as "Infinigram Arrays"
    
    Client->>+Proxy: HTTP Request
    Proxy->>+API: Forward Request
    
    alt Health Check
        API->>Proxy: 204 No Content
        Proxy->>Client: 204 No Content
    else Infinigram Index Query
        API->>+Arrays: Query Available Indexes
        Arrays-->>-API: Index Information
        API->>Proxy: Return Index List
        Proxy->>Client: JSON Response
    else Attribution Request
        API->>+Cache: Check Cache
        
        alt Cache Hit
            Cache-->>-API: Cached Attribution Result
            API->>Proxy: Return Attribution
            Proxy->>Client: JSON Response
        else Cache Miss
            Cache-->>-API: No Cache Entry
            API->>+Queue: Enqueue Attribution Job
            API->>Proxy: Accepted Job (202)
            Proxy->>Client: 202 Accepted
            
            Worker->>+Queue: Pull Attribution Job
            Worker->>+Arrays: Process Attribution
            Arrays-->>-Worker: Attribution Result
            Worker->>Cache: Store Result
            Worker->>-Queue: Store Result
            
            Client->>+Proxy: Poll for Result
            Proxy->>+API: Forward Poll Request
            API->>+Cache: Check Cache
            Cache-->>-API: Attribution Result
            API->>-Proxy: Return Attribution
            Proxy->>-Client: JSON Response
        end
    end
```

Sources: [api/app.py:36-54](), [README.md:17-34]()

## Application Startup Flow

The following diagram illustrates the startup process for the API application:

```mermaid
flowchart TD
    Start["Application Start"]
    -->ConfigLogging["Configure Logging"]
    -->SetupLifespan["Setup Lifespan Context Manager"]
    -->CreateFastAPI["Create FastAPI Application"]
    -->AddHandlers["Add Exception Handlers"]
    -->IncludeRouters["Include Routers:<br>health, infinigram, attribution"]
    -->SetupTracing["Setup OpenTelemetry Tracing"]
    -->InstrumentApp["Instrument App with FastAPIInstrumentor"]
    -->AppReady["Application Ready"]
    
    subgraph "Lifespan Context Manager"
        OnStartup["On Startup:<br>1. Get config<br>2. Create Redis connection pool<br>3. Connect to attribution queue"]
        OnShutdown["On Shutdown:<br>1. Disconnect from attribution queue"]
    end
    
    SetupLifespan --> OnStartup
    OnStartup --> OnShutdown
```

Sources: [api/app.py:1-69]()

## Deployment Architecture

The system is deployed on AI2's Skiff platform, which is a wrapper over Kubernetes. The architecture is designed to be scalable and resilient:

```mermaid
graph TB
    subgraph "Kubernetes Cluster"
        subgraph "infinigram-api Namespace"
            Ingress["Ingress"]
            Service["Service (proxy)"]
            ApiDeployment["API Deployment"]
            WorkerDeployment["Attribution Worker Deployment"]
            PDB["PodDisruptionBudget"]
            
            subgraph "Persistent Volumes"
                pv1["v4_pileval_llama"]
                pv2["olmoe-mix-0924-dclm"]
                pv3["olmoe-mix-0924-nodclm"]
                pv4["v4-olmoe-0125-1b-7b-anneal-adapt"]
                pv5["v4-olmo-2-1124-13b-anneal-adapt"]
                pv6["v4-olmo-2-0325-32b-anneal-adapt"]
            end
            
            Ingress --> Service
            Service --> ApiDeployment
            PDB --> ApiDeployment
            
            ApiDeployment --> pv1
            ApiDeployment --> pv2
            ApiDeployment --> pv3
            ApiDeployment --> pv4
            ApiDeployment --> pv5
            ApiDeployment --> pv6
            
            WorkerDeployment --> pv1
            WorkerDeployment --> pv2
            WorkerDeployment --> pv3
            WorkerDeployment --> pv4
            WorkerDeployment --> pv5
            WorkerDeployment --> pv6
        end
        
        ExternalServices["External Services<br>(Redis, PostgreSQL, OTLP)"]
        ApiDeployment --> ExternalServices
        WorkerDeployment --> ExternalServices
    end
```

Key deployment characteristics:
- The API and Attribution Worker are deployed as separate deployments for independent scaling
- Both have access to the same set of infinigram arrays mounted as persistent volumes
- External services (Redis, PostgreSQL, OpenTelemetry) are used for caching, queuing, and observability
- A Pod Disruption Budget ensures service availability during maintenance

Sources: [docker-compose.yaml:7-82](), [README.md:36-41]()

## Component Integration Map

This diagram shows how the code components relate to each other:

```mermaid
graph TB
    subgraph "API Components"
        AppPy["app.py (FastAPI Application)"]
        HealthRouter["health_router.py"]
        ConfigPy["config.py"]
        
        subgraph "Infinigram Module"
            InfinigramRouter["infinigram_router.py"]
        end
        
        subgraph "Attribution Module"
            AttributionRouter["attribution_router.py"]
            AttributionService["attribution_service.py"]
            AttributionQueueService["attribution_queue_service.py"]
        end
        
        subgraph "Cache Module"
            RedisCache["redis.py"]
        end
        
        AppPy --> HealthRouter
        AppPy --> ConfigPy
        AppPy --> InfinigramRouter
        AppPy --> AttributionRouter
        
        AttributionRouter --> AttributionService
        AttributionService --> AttributionQueueService
        AttributionService --> RedisCache
    end
    
    subgraph "Worker Components"
        WorkerPy["worker.py"]
        WorkerConfig["config.py"]
    end
    
    subgraph "Shared Components"
        InfinigramProcessor["infini-gram-processor"]
    end
    
    AttributionService --> InfinigramProcessor
    InfinigramRouter --> InfinigramProcessor
    WorkerPy --> InfinigramProcessor
```

Sources: [api/app.py:15-26](), [README.md:1-10]()

## Environmental Configuration

The system's configuration is managed through environment variables. The following table shows the key configuration variables used:

| Environment Variable | Purpose | Default/Example |
|---|---|---|
| INDEX_BASE_PATH | Base path for infinigram array files | /mnt/infinigram-array |
| ATTRIBUTION_QUEUE_URL | Connection URL for PostgreSQL queue | postgres://infini-gram:llmz@queue:5432/infini-gram |
| PYTHON_ENV | Environment type | development |
| LOG_LEVEL | Logging verbosity | DEBUG |
| OTEL_EXPORTER_OTLP_ENDPOINT | OpenTelemetry collector endpoint | http://otelcol:4318 |
| CACHE_URL | Redis connection URL | redis://cache:6379 |

Sources: [docker-compose.yaml:1-27]()

## Summary

The infinigram-api system employs a microservices architecture with separate components for handling API requests, processing long-running attribution tasks, and storing/caching data. The architecture is designed to be scalable, with the API and Attribution Worker deployed separately to allow independent scaling. Both components share access to the infinigram arrays, which are mounted as persistent volumes.

The system uses Redis for caching attribution results, PostgreSQL as a job queue, and OpenTelemetry for observability. An NGINX proxy sits in front of the API to handle load balancing, SSL termination, and request routing.

For more detailed information about individual components, refer to their respective wiki pages.

---

