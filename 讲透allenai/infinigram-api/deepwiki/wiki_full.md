# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [api/README.md](api/README.md)
- [api/app.py](api/app.py)
- [attribution_worker/README.md](attribution_worker/README.md)
- [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
- [docs/indexes.md](docs/indexes.md)
- [packages/infini-gram-processor/README.md](packages/infini-gram-processor/README.md)

</details>



This document provides an overview of the infinigram-api repository, a system designed to expose the capabilities of [infini-gram](https://infini-gram.io) through a scalable API interface. For detailed information about specific system components, deployment, or development processes, refer to the specialized wiki pages linked throughout this document.

Sources: [README.md:1-3]()

## Purpose and Scope

The infinigram-api system serves as a scalable, high-performance interface to the underlying infinigram technology, which enables working with n-gram language models trained on vast amounts of text. It was developed to make the research capabilities described in the following paper accessible through an API:

> Liu, Jiacheng and Min, Sewon and Zettlemoyer, Luke and Choi, Yejin and Hajishirzi, Hannaneh (2024).
> Infini-gram: Scaling Unbounded n-gram Language Models to a Trillion Tokens.
> arXiv preprint arXiv:2401.17377

The API supports multiple types of operations, with attribution requests being the most computationally intensive, requiring dedicated worker processes to handle efficiently.

For more information about the detailed system architecture, see [System Architecture](#2).

Sources: [README.md:5-9]()

## Repository Structure

The infinigram-api repository is structured as a uv workspace containing three main components:

1. **API Service** (`api/`): A FastAPI-based web service that handles user requests and interfaces with infinigram indices
2. **Attribution Worker** (`attribution_worker/`): A worker service that processes long-running attribution tasks offloaded from the API
3. **Infini-gram Processor** (`packages/infini-gram-processor/`): A shared library containing code used by both the API and worker components

Sources: [README.md:3](), [api/README.md:1-3](), [attribution_worker/README.md:1-3](), [packages/infini-gram-processor/README.md:1-3]()

## Key Components and Their Relationships

### Main System Components

```mermaid
graph TB
    Client["Client"]
    Proxy["Web Proxy (NGINX)"]
    API["API Service (FastAPI)"]
    Worker["Attribution Worker"]
    Queue[("Queue (PostgreSQL)")]
    Cache[("Cache (Redis)")]
    Indices[("Infinigram Arrays (ML Models)")]
    
    Client --> Proxy
    Proxy --> API
    
    API <--> Queue
    Worker <--> Queue
    
    API --> Cache
    Worker --> Cache
    
    API --> Indices
    Worker --> Indices
```

The system consists of several key components that work together to provide infinigram functionality:

- **API Service**: Handles incoming requests through FastAPI endpoints
- **Attribution Worker**: Processes attribution requests which are too time-intensive for synchronous handling
- **Queue**: PostgreSQL-based queue system that facilitates communication between the API and worker
- **Cache**: Redis-based caching system for storing results and improving performance
- **Infinigram Arrays**: ML models that power the text processing capabilities, mounted as persistent volumes

The API and Attribution Worker are deployed as separate services, allowing them to be scaled independently based on workload requirements.

Sources: [README.md:19-41](), [api/app.py:15-25](), [docs/CONTRIBUTING.md:39-50]()

### Code Organization

```mermaid
graph TB
    subgraph "API Application"
        AppPy["app.py (Main Application)"]
        HealthRouter["health_router.py"]
        InfinigramRouter["infinigram_router.py"]
        AttributionRouter["attribution_router.py"]
        QueueService["attribution_queue_service.py"]
        RedisCache["redis.py"]
        Config["config.py"]
    end
    
    subgraph "Worker Application"
        WorkerPy["worker.py"]
    end
    
    subgraph "Shared Library"
        InfiniGramProcessor["infini_gram_processor"]
    end
    
    AppPy --> Config
    AppPy --> HealthRouter
    AppPy --> InfinigramRouter
    AppPy --> AttributionRouter
    AttributionRouter --> QueueService
    AttributionRouter --> RedisCache
    
    WorkerPy --> QueueService
    WorkerPy --> RedisCache
    
    AttributionRouter --> InfiniGramProcessor
    InfinigramRouter --> InfiniGramProcessor
    WorkerPy --> InfiniGramProcessor
```

The code is organized into several key modules:

- The main API application (`app.py`) integrates multiple routers:
  - `health_router` for health check endpoints
  - `infinigram_router` for index-related operations
  - `attribution_router` for attribution request handling

- The worker application handles jobs from the queue, processes them with the infinigram processor, and stores results

- Both the API and worker use the shared infinigram processor library for core functionality

Sources: [api/app.py:1-69](), [README.md:1-3]()

## Request Flow

### Standard vs. Attribution Request Processing

```mermaid
sequenceDiagram
    participant Client as "Client"
    participant API as "API Service"
    participant Cache as "Redis Cache"
    participant Queue as "PostgreSQL Queue"
    participant Worker as "Attribution Worker"
    participant Processor as "InfiniGram Processor"
    
    Client->>API: Standard Request (Index/Document)
    API->>Processor: Process Request
    Processor-->>API: Result
    API-->>Client: Return Result (200 OK)
    
    Client->>API: Attribution Request
    API->>Cache: Check Cache
    
    alt Cache Hit
        Cache-->>API: Return Cached Result
        API-->>Client: Return Result (200 OK)
    else Cache Miss
        API->>Queue: Add Job
        API-->>Client: Return Job ID (202 Accepted)
        
        Worker->>Queue: Poll Job
        Worker->>Processor: Process Attribution
        Processor-->>Worker: Attribution Result
        Worker->>Cache: Store Result
        Worker->>Queue: Update Job Status
        
        Client->>API: Poll for Result (Job ID)
        API->>Cache: Get Result
        Cache-->>API: Return Result
        API-->>Client: Return Result (200 OK)
    end
```

The system handles two main types of request flows:

1. **Standard Requests** (Infinigram index operations, document retrieval):
   - Processed synchronously by the API service
   - Results returned directly to the client

2. **Attribution Requests** (computationally intensive):
   - API checks cache for existing results
   - If not found, job is added to queue and client receives a job ID
   - Attribution Worker picks up the job, processes it using the Infinigram Processor
   - Results are stored in cache
   - Client polls for results using the job ID

This separation allows the system to efficiently handle both quick queries and resource-intensive attribution operations without blocking the API service.

Sources: [README.md:28-40](), [api/app.py:15-25](), [api/app.py:52-54]()

## Technology Stack

The infinigram-api system leverages several modern technologies:

| Component | Technology |
|-----------|------------|
| API Framework | FastAPI |
| Queue System | SAQ (Simple Async Queue) with PostgreSQL |
| Caching | Redis |
| Containerization | Docker |
| Orchestration | Kubernetes (via Ai2's Skiff platform) |
| Observability | OpenTelemetry |
| Development | uv (Python package management) |

Sources: [api/app.py:6-14](), [api/app.py:56-69](), [docs/CONTRIBUTING.md:12-16]()

## Infinigram Indices

The system works with various infinigram indices (also called arrays), which are the ML models that power text processing capabilities. These indices are stored as array files and mounted as persistent volumes to both the API and worker services.

For information about adding new indices, see [Adding New Indices](#5.3).

Sources: [docs/indexes.md:1-102](), [README.md:14-15]()

## Development and Deployment

The system can be run locally using Docker Compose, which starts all required services with proper connections. For production, it's deployed on Ai2's Skiff platform (a Kubernetes wrapper).

For detailed information about local development setup, see [Local Development](#5.1). For deployment details, see [Kubernetes Deployment](#5.2).

Sources: [docs/CONTRIBUTING.md:39-50](), [README.md:36-40]()

---

# Page: System Architecture

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

# Page: Components

# Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/README.md](api/README.md)
- [api/app.py](api/app.py)
- [attribution_worker/README.md](attribution_worker/README.md)
- [docker-compose.yaml](docker-compose.yaml)
- [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
- [docs/indexes.md](docs/indexes.md)
- [packages/infini-gram-processor/README.md](packages/infini-gram-processor/README.md)

</details>



This page details the main components of the Infinigram API system and their responsibilities. It provides an overview of how these components fit together to deliver attribution services and other functionality. For information about data flow between these components, see [Data Flow](#2.2).

## Core Components Overview

The Infinigram API system consists of several distinct components that work together to provide attribution and document services. Each component has specific responsibilities and interfaces with other components in well-defined ways.

```mermaid
graph TB
    subgraph "Client Layer"
        Client["Client Applications"]
    end
    
    subgraph "Frontend Layer"
        Proxy["NGINX Proxy"]
    end
    
    subgraph "Application Layer"
        API["FastAPI Application<br>(app.py)"]
        Worker["Attribution Worker<br>(worker.py)"]
    end
    
    subgraph "Infrastructure Layer"
        Queue["Queue<br>(PostgreSQL)"]
        Cache["Cache<br>(Redis)"]
        OtelCol["OpenTelemetry<br>Collector"]
    end
    
    subgraph "Data Layer"
        Arrays["Infinigram Arrays<br>(ML Models)"]
    end
    
    Client --> Proxy
    Proxy --> API
    API --> Queue
    API --> Cache
    API --> Arrays
    API --> OtelCol
    Worker --> Queue
    Worker --> Cache
    Worker --> Arrays
    Worker --> OtelCol
```

Sources: [docker-compose.yaml:7-82](), [api/app.py:46-69]()

## FastAPI Application

The FastAPI application serves as the primary entry point for client requests. It handles direct requests for infinigram indices and document information, and manages the queuing of longer-running attribution requests.

### API Components

```mermaid
graph TB
    subgraph "API Application"
        App["app.py<br>(FastAPI application)"]
        
        subgraph "Routers"
            Health["health_router.py"]
            Infinigram["infinigram_router.py"]
            Attribution["attribution_router.py"]
            Documents["documents_router.py"]
        end
        
        subgraph "Services"
            AttrService["attribution_service.py"]
            AttrQueueService["attribution_queue_service.py"]
            DocService["documents_service.py"]
            Redis["redis.py<br>(Cache Service)"]
        end
        
        Config["config.py"]
    end
    
    App --> Health
    App --> Infinigram
    App --> Attribution
    App --> Documents
    App --> Config
    
    Attribution --> AttrService
    AttrService --> AttrQueueService
    AttrService --> Redis
    Documents --> DocService
```

Sources: [api/app.py:1-55](), [api/README.md:1-3]()

### API Responsibilities

| Component | Responsibility |
|-----------|----------------|
| `app.py` | Main FastAPI application entry point that configures routers, middleware, and telemetry |
| `health_router.py` | Handles health check endpoints for monitoring system status |
| `infinigram_router.py` | Manages endpoints for querying available infinigram indices |
| `attribution_router.py` | Processes attribution requests, checking cache and queueing long-running tasks |
| `documents_router.py` | Handles document retrieval requests |
| `attribution_service.py` | Core business logic for attribution operations |
| `attribution_queue_service.py` | Manages interaction with the PostgreSQL queue |
| `redis.py` | Handles caching of attribution results |
| `config.py` | Manages application configuration from environment variables |

Sources: [api/app.py:16-25](), [api/README.md:1-3]()

## Attribution Worker

The Attribution Worker is a separate service that processes long-running attribution tasks asynchronously. It polls the PostgreSQL queue for jobs, processes them using the Infinigram arrays, and stores results in the Redis cache for later retrieval by the API.

```mermaid
graph LR
    subgraph "Attribution Worker"
        Worker["worker.py"]
        WorkerConfig["config.py"]
    end
    
    subgraph "External Services"
        Queue["PostgreSQL Queue"]
        Cache["Redis Cache"]
        Arrays["Infinigram Arrays"]
    end
    
    Worker --> WorkerConfig
    Worker --> Queue
    Worker --> Cache
    Worker --> Arrays
```

Sources: [attribution_worker/README.md:1-3](), [docker-compose.yaml:29-46]()

## Proxy (NGINX)

The NGINX proxy sits in front of the API service and handles routing of client requests. It provides a unified entry point for all API calls and can handle SSL termination, load balancing, and other frontend responsibilities.

Sources: [docker-compose.yaml:48-53]()

## Queue (PostgreSQL)

The PostgreSQL database serves as a queue for storing attribution jobs. It provides persistent, reliable storage for jobs that need to be processed by the Attribution Worker, ensuring no work is lost even if services are restarted.

```mermaid
graph TB
    subgraph "Queue System"
        PG["PostgreSQL Database"]
        Schema["SQL Schema"]
    end
    
    subgraph "Queue Users"
        API["API<br>(enqueues jobs)"]
        Worker["Attribution Worker<br>(dequeues jobs)"]
    end
    
    API --> PG
    Worker --> PG
    Schema --> PG
```

Sources: [docker-compose.yaml:67-76]()

## Cache (Redis)

Redis is used as a caching mechanism for storing the results of attribution operations. This reduces the need to recompute expensive attribution results for repeated requests and improves response times for clients.

Sources: [docker-compose.yaml:78-81](), [api/app.py:38]()

## OpenTelemetry Collector

The OpenTelemetry collector receives telemetry data (traces, metrics, logs) from the API and Attribution Worker. It processes this data and forwards it to appropriate monitoring and observability systems, allowing for detailed performance analysis and troubleshooting.

Sources: [docker-compose.yaml:55-65](), [api/app.py:11-14](), [api/app.py:56-67]()

## Infinigram Arrays (ML Models)

The Infinigram arrays are the core ML models that power the attribution functionality. They are mounted as volumes into both the API and Attribution Worker containers. Each array corresponds to a specific model with its own characteristics.

### Available Arrays

| Array Name | Path | Description |
|------------|------|-------------|
| v4_pileval_llama | `/mnt/infinigram-array/v4_pileval_llama` | Pileval Llama model |
| olmoe-mix-0924-dclm | `/mnt/infinigram-array/olmoe-mix-0924-dclm` | OLMoE Mix model with DCLM |
| olmoe-mix-0924-nodclm | `/mnt/infinigram-array/olmoe-mix-0924-nodclm` | OLMoE Mix model without DCLM |
| v4-olmoe-0125-1b-7b-anneal-adapt | `/mnt/infinigram-array/v4-olmoe-0125-1b-7b-anneal-adapt` | OLMoE 1B-7B model |
| v4-olmo-2-1124-13b-anneal-adapt | `/mnt/infinigram-array/v4-olmo-2-1124-13b-anneal-adapt` | OLMo-2 13B model |
| v4-olmo-2-0325-32b-anneal-adapt | `/mnt/infinigram-array/v4-olmo-2-0325-32b-anneal-adapt` | OLMo-2 32B model |

Sources: [docker-compose.yaml:16-22](), [docker-compose.yaml:39-45](), [docs/indexes.md:1-103]()

## Shared Libraries

### Infini-Gram Processor

Despite its name, this is a package containing code shared between different components of the Infinigram API system, including both the API and the Attribution Worker. It provides common functionality for working with Infinigram arrays and processing attribution requests.

Sources: [packages/infini-gram-processor/README.md:1-3](), [api/app.py:8]()

## Environment Setup

The Infinigram API system requires several environment variables to function properly. These include:

| Environment Variable | Purpose |
|----------------------|---------|
| `PYTHONUNBUFFERED` | Controls Python output buffering |
| `INDEX_BASE_PATH` | Path to the mounted Infinigram arrays |
| `ATTRIBUTION_QUEUE_URL` | Connection string for the PostgreSQL queue |
| `PYTHON_ENV` | Deployment environment (development/production) |
| `LOG_LEVEL` | Controls logging verbosity |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Endpoint for the OpenTelemetry collector |
| `CACHE_URL` | Connection string for the Redis cache |

Sources: [docker-compose.yaml:1-27]()

## Development vs. Production Environment

```mermaid
graph TB
    subgraph "Development (Docker Compose)"
        DevAPI["Local API Container"]
        DevWorker["Local Worker Container"]
        DevProxy["Local Proxy Container"]
        DevQueue["Local PostgreSQL Container"]
        DevCache["Local Redis Container"]
        DevOtel["Local OpenTelemetry Container"]
        DevVolumes["Local Volumes<br>(./infinigram-array/*)"]
    end
    
    subgraph "Production (Kubernetes)"
        ProdAPI["API Deployment"]
        ProdWorker["Worker Deployment"]
        ProdIngress["Kubernetes Ingress"]
        ProdService["Kubernetes Service"]
        ProdPDB["PodDisruptionBudget"]
        ProdPV["Persistent Volumes<br>(infinigram-*)"]
        ExternalServices["External Services<br>(Redis, PostgreSQL, OTLP)"]
    end
    
    DevAPI --> DevVolumes
    DevWorker --> DevVolumes
    
    ProdAPI --> ProdPV
    ProdWorker --> ProdPV
    ProdAPI --> ExternalServices
    ProdWorker --> ExternalServices
```

Sources: [docker-compose.yaml:1-82](), [docs/CONTRIBUTING.md:38-50](), [docs/indexes.md:77-95]()

---

# Page: Data Flow

# Data Flow

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/attribution/attribution_queue_service.py](api/src/attribution/attribution_queue_service.py)
- [api/src/attribution/attribution_service.py](api/src/attribution/attribution_service.py)
- [attribution_worker/config.py](attribution_worker/config.py)
- [attribution_worker/worker.py](attribution_worker/worker.py)

</details>



This document details how data flows through the infinigram-api system, with primary focus on attribution request processing. It explains the path that requests take from initial API call through to response delivery, including the asynchronous processing architecture. For information about the system components themselves, see [Components](#2.1).

## Overview

The infinigram-api system utilizes an asynchronous processing model for handling attribution requests, which can be computationally intensive. This architecture allows the system to remain responsive while performing complex operations like span attribution and document retrieval.

```mermaid
flowchart TD
    subgraph "Client"
        A["Client Request"]
        F["Poll for Result"]
    end
    
    subgraph "API Layer"
        B["Attribution Endpoint"]
        C["Cache Check"]
        D["Queue Job"]
    end
    
    subgraph "Processing Layer"
        E["Attribution Worker"]
    end
    
    subgraph "Storage"
        G["Redis Cache"]
        H["Infinigram Arrays"]
    end
    
    A -->|"1. POST /attribution"| B
    B -->|"2. Check cache"| C
    C -->|"3a. Cache miss"| D
    C -->|"3b. Cache hit"| G
    G -->|"3c. Return cached result"| B
    D -->|"4. Enqueue job"| E
    B -->|"3d. Return 202 Accepted"| A
    E -->|"5. Process attribution"| H
    H -->|"6. Return data"| E
    E -->|"7. Store result"| G
    F -->|"8. GET /attribution/{job_id}"| B
    B -->|"9. Check cache"| G
    G -->|"10. Return result"| B
```

Sources: [api/src/attribution/attribution_service.py:161-228](), [attribution_worker/worker.py:58-142]()

## Attribution Request Flow

The attribution request flow follows a pattern of cache checking, asynchronous processing, and result retrieval.

### Initial Request Processing

When a client submits an attribution request, the API first attempts to retrieve a cached result to avoid redundant computation.

```mermaid
sequenceDiagram
    participant Client
    participant AttributionRouter
    participant AttributionService
    participant RedisCache
    
    Client->>AttributionRouter: POST /attribution
    AttributionRouter->>AttributionService: get_attribution_for_response()
    AttributionService->>RedisCache: _get_cached_response()
    
    alt Cache hit
        RedisCache->>AttributionService: Return AttributionResponse
        AttributionService->>AttributionRouter: Return result
        AttributionRouter->>Client: 200 OK with result
    else Cache miss
        RedisCache->>AttributionService: Return None
        Note over AttributionService: Continue to job creation
    end
```

Sources: [api/src/attribution/attribution_service.py:101-137]()

### Job Creation and Queuing

If no cached result exists, the system generates a unique job ID and queues the attribution task for asynchronous processing.

```mermaid
sequenceDiagram
    participant AttributionService
    participant Queue as "SAQ Queue"
    participant Client
    
    AttributionService->>AttributionService: Generate UUID for job
    AttributionService->>Queue: queue.apply("attribute", ...)
    Note over Queue: Job added to queue
    AttributionService->>Client: 202 Accepted with job ID
```

Sources: [api/src/attribution/attribution_service.py:161-228](), [api/src/attribution/attribution_queue_service.py:1-25]()

### Asynchronous Processing

The attribution worker processes the queued job, performing the computationally intensive attribution operations.

```mermaid
flowchart TD
    subgraph "Attribution Worker"
        A["Poll Queue"] -->|"Job found"| B["Process Job"]
        B --> C["Get Infinigram Index"]
        C --> D["Perform Attribution"]
        D --> E["Sort Spans by Ranking Method"]
        E --> F["Get Document Requests"]
        F --> G["Retrieve Documents"]
        G --> H["Format Response"]
        H --> I["Store in Cache"]
    end
    
    subgraph "Data Sources"
        J["Infinigram Index"]
        K["Redis Cache"]
    end
    
    C -->|"Load index"| J
    G -->|"Query documents"| J
    I -->|"Store result"| K
```

Sources: [attribution_worker/worker.py:58-142]()

### Result Retrieval

The client polls for the result, which is retrieved from the cache once processing is complete.

```mermaid
sequenceDiagram
    participant Client
    participant AttributionRouter
    participant AttributionService
    participant RedisCache
    
    loop Until result is available
        Client->>AttributionRouter: GET /attribution/{job_id}
        AttributionRouter->>AttributionService: get_attribution_for_response()
        AttributionService->>RedisCache: _get_cached_response()
        
        alt Result available
            RedisCache->>AttributionService: Return AttributionResponse
            AttributionService->>AttributionRouter: Return result
            AttributionRouter->>Client: 200 OK with result
        else Result not ready
            RedisCache->>AttributionService: Return None
            AttributionService->>AttributionRouter: Still processing
            AttributionRouter->>Client: 202 Accepted (try again)
        end
        
        Note over Client: Wait before retry
    end
```

Sources: [api/src/attribution/attribution_service.py:101-137]()

## Cache System

The caching mechanism is central to the system's performance and user experience.

```mermaid
flowchart TD
    subgraph "AttributionService"
        A["_get_cache_key()"] -->|"Generate key"| B["SHA256 hash"]
        C["_get_cached_response()"] -->|"Check cache"| A
        D["_cache_response()"] -->|"Store in cache"| A
    end
    
    subgraph "Redis Cache"
        E["getex()"]
        F["set()"]
    end
    
    B -->|"Use as lookup key"| E
    B -->|"Use as storage key"| F
    C -->|"Retrieve with TTL extension"| E
    D -->|"Store with TTL"| F
```

Sources: [api/src/attribution/attribution_service.py:91-159]()

### Cache Key Generation

Cache keys are generated by combining the request type, index, and serialized request data, then hashing with SHA256:

```mermaid
flowchart LR
    A["Request Class Name"] -->|"Combine"| D["Concatenated String"]
    B["Index Name"] -->|"Combine"| D
    C["JSON Dump of Request"] -->|"Combine"| D
    D -->|"SHA256 Hash"| E["Cache Key"]
```

Sources: [api/src/attribution/attribution_service.py:91-99]()

### Cache TTL Management

The system uses different expiration times for cache entries:
- Newly cached results: 1 hour (3,600 seconds)
- Accessed cached results: Extended to 12 hours (43,200 seconds)

This approach keeps frequently accessed results available longer while allowing less popular results to expire sooner.

Sources: [api/src/attribution/attribution_service.py:101-137](), [api/src/attribution/attribution_service.py:139-159]()

## Attribution Worker Details

The attribution worker is responsible for the actual processing of attribution requests.

```mermaid
classDiagram
    class AttributionJob {
        +process(ctx, index, input, delimiters, etc)
        -get_infini_gram_index()
        -attribute()
        -sort_and_cap_spans()
        -get_document_requests()
        -get_documents_by_pointers()
        -get_spans_with_documents()
        -format_response()
    }
    
    class Queue {
        +connect()
        +disconnect()
        +apply()
    }
    
    AttributionJob --> Queue : uses
```

Sources: [attribution_worker/worker.py:58-142]()

### Worker Process Flow

The worker performs several key steps when processing an attribution job:

1. Extract OpenTelemetry context for distributed tracing
2. Retrieve the appropriate Infinigram index
3. Perform attribution on the input text
4. Sort and filter spans based on ranking method and density
5. Generate document requests for the selected spans
6. Retrieve documents from the Infinigram index
7. Format the response with spans and their associated documents
8. Store the result in Redis cache

Sources: [attribution_worker/worker.py:58-142]()

## Error Handling and Timeouts

The system includes mechanisms to handle errors and timeouts in the attribution process.

```mermaid
sequenceDiagram
    participant Client
    participant AttributionService
    participant Queue
    
    Client->>AttributionService: Request attribution
    AttributionService->>Queue: Apply job with timeout (60s)
    
    alt Job times out
        Queue->>AttributionService: Raise TimeoutError
        AttributionService->>AttributionService: Log error and update span
        AttributionService->>Queue: Abort job
        AttributionService->>Client: 503 Server Overloaded
    end
```

Sources: [api/src/attribution/attribution_service.py:212-228]()

## Data Models and Structures

The system uses several key data structures to represent attribution data:

| Model | Purpose | Key Fields |
|-------|---------|------------|
| `AttributionRequest` | Input parameters for attribution | `response`, `delimiters`, `minimum_span_length`, etc. |
| `AttributionResponse` | Complete attribution results | `spans`, `input_tokens`, `index` |
| `AttributionSpan` | Information about an attributed text span | `left`, `right`, `length`, `documents` |
| `AttributionDocument` | Document that contains a span | `text_long`, `text_snippet`, offsets |

Sources: [api/src/attribution/attribution_service.py:40-65]()

## Queue Configuration

The queue system is configured based on the application environment:

```mermaid
flowchart TD
    A["Config"] -->|"Defines"| B["attribution_queue_url"]
    A -->|"Defines"| C["attribution_queue_name"]
    
    B -->|"Format: redis://host:port"| D["Queue Connection"]
    C -->|"Format: infini-gram-attribution-{env}"| D
    
    D -->|"Creates"| E["SAQ Queue"]
```

Sources: [attribution_worker/config.py:1-25](), [api/src/attribution/attribution_queue_service.py:1-25]()

## End-to-End Attribution Flow

This diagram illustrates the complete flow of an attribution request through the system, connecting code entities with their roles:

```mermaid
sequenceDiagram
    participant Client
    participant AttributionRouter as "attribution_router.py"
    participant AttributionService as "attribution_service.py"
    participant RedisCache as "Redis (cache)"
    participant Queue as "SAQ (attribution_queue_service.py)"
    participant Worker as "worker.py"
    participant InfiniGramProcessor as "InfiniGramProcessor"
    
    Client->>AttributionRouter: POST /attribution
    AttributionRouter->>AttributionService: get_attribution_for_response()
    AttributionService->>RedisCache: _get_cached_response()
    
    alt Cache hit
        RedisCache->>AttributionService: Return AttributionResponse
        AttributionService->>AttributionRouter: Return result
        AttributionRouter->>Client: 200 OK with result
    else Cache miss
        RedisCache->>AttributionService: Return None
        AttributionService->>AttributionService: Generate UUID job_key
        AttributionService->>Queue: queue.apply("attribute", ...)
        Queue->>AttributionService: Acknowledge job
        AttributionService->>AttributionRouter: Job accepted
        AttributionRouter->>Client: 202 Accepted
        
        Queue->>Worker: Worker polls queue
        Worker->>InfiniGramProcessor: attribute()
        InfiniGramProcessor->>Worker: Raw attribution result
        Worker->>InfiniGramProcessor: get_documents_by_pointers()
        InfiniGramProcessor->>Worker: Documents
        Worker->>Worker: Format AttributionResponse
        Worker->>RedisCache: Store result
        
        loop Until result available
            Client->>AttributionRouter: GET /attribution/{job_id}
            AttributionRouter->>AttributionService: get_attribution_for_response()
            AttributionService->>RedisCache: _get_cached_response()
            
            alt Result ready
                RedisCache->>AttributionService: AttributionResponse
                AttributionService->>AttributionRouter: Return result
                AttributionRouter->>Client: 200 OK with result
            else Still processing
                RedisCache->>AttributionService: None
                AttributionService->>AttributionRouter: Still processing
                AttributionRouter->>Client: 202 Accepted
            end
        end
    end
```

Sources: [api/src/attribution/attribution_service.py:161-228](), [attribution_worker/worker.py:58-142](), [api/src/attribution/attribution_queue_service.py:1-25]()

---

# Page: API

# API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.vscode/extensions.json](.vscode/extensions.json)
- [api/app.py](api/app.py)
- [api/src/config.py](api/src/config.py)
- [api/src/health.py](api/src/health.py)
- [api/src/infinigram/__init__.py](api/src/infinigram/__init__.py)
- [packages/infini-gram-processor/src/infini_gram_processor/processor_config.py](packages/infini-gram-processor/src/infini_gram_processor/processor_config.py)

</details>



This page documents the API service of the infinigram-api system, which serves as the primary interface for client applications to interact with Infinigram's functionality. The API provides endpoints for retrieving infinigram indices, requesting text attribution, and accessing document information. For information about the Attribution Worker component, see [Attribution Worker](#4).

## Overview

The Infinigram API is built using FastAPI and serves as the central component that handles client requests. It exposes several endpoints grouped into logical routers and provides async processing for longer-running attribution tasks.

```mermaid
graph TD
    subgraph "API Components"
        API["FastAPI Application<br>app.py"]
        Config["Configuration<br>config.py"]
        
        subgraph "Routers"
            Health["Health Router<br>health.py"]
            Infinigram["Infinigram Router<br>infinigram_router.py"]
            Attribution["Attribution Router<br>attribution_router.py"]
        end
        
        subgraph "Services"
            AttributionService["Attribution Service"]
            QueueService["Queue Service"]
            CacheService["Redis Cache"]
        end
        
        subgraph "External Dependencies"
            InfinigramProcessor["InfiniGram Processor"]
            Telemetry["OpenTelemetry"]
        end
    end
    
    API --> Config
    API --> Health
    API --> Infinigram
    API --> Attribution
    
    Attribution --> AttributionService
    AttributionService --> QueueService
    AttributionService --> CacheService
    AttributionService --> InfinigramProcessor
    
    API --> Telemetry
```

Sources: [api/app.py:1-70](), [api/src/config.py:1-32](), [api/src/health.py:1-12](), [api/src/infinigram/__init__.py:1-2]()

## API Configuration

The API configuration is managed through the `Config` class defined in `config.py`, which uses Pydantic's `BaseSettings` for environment-based configuration. This allows for flexible runtime configuration through environment variables or `.env` files.

| Configuration Parameter | Description | Default Value |
|-------------------------|-------------|---------------|
| `index_base_path` | Base path for infinigram array files | "/mnt/infinigram-array" |
| `profiling_enabled` | Toggle for profiling features | False |
| `application_name` | Name of the application | "infini-gram-api" |
| `attribution_queue_url` | URL for the attribution job queue | "redis://localhost:6379" |
| `python_env` | Deployment environment | "prod" |
| `cache_url` | URL for the Redis cache | "redis://localhost:6379" |
| `attribution_queue_name` | Computed queue name based on environment | "infini-gram-attribution-{env}" |

Sources: [api/src/config.py:1-32]()

## API Application Structure

The FastAPI application is defined in `app.py` and serves as the entrypoint for the API service. It includes several components:

### Main Application

```mermaid
flowchart TD
    subgraph "API Application Initialization"
        A["Create FastAPI app<br>app = FastAPI()"]
        B["Add exception handlers"]
        C["Include routers:<br>- health_router<br>- infinigram_router<br>- attribution_router"]
        D["Set up OpenTelemetry"]
        E["Instrument FastAPI app"]
        
        A --> B
        B --> C
        C --> D
        D --> E
    end
```

Sources: [api/app.py:46-69]()

### Application Lifecycle

The API uses FastAPI's lifespan feature to manage connections and resources during startup and shutdown:

```mermaid
sequenceDiagram
    participant App as FastAPI App
    participant Config as Configuration
    participant Redis as Redis Cache
    participant Queue as Attribution Queue
    
    Note over App: Application Startup
    App->>Config: get_config()
    App->>Redis: create_connection_pool(config.cache_url)
    App->>Queue: connect_to_attribution_queue()
    
    Note over App: Application Running
    
    Note over App: Application Shutdown
    App->>Queue: disconnect_from_attribution_queue()
```

Sources: [api/app.py:34-43]()

## Routers

The API organizes endpoints into logical routers, each handling a specific domain of functionality:

### Health Router

The health router provides a simple health check endpoint that returns a 204 No Content response. This endpoint is used by Kubernetes to determine if the service is ready to receive traffic.

```
GET /health/ → 204 No Content
```

Sources: [api/src/health.py:1-12]()

### Infinigram Router

The infinigram router exposes endpoints for querying infinigram indices and related functionality. This router is imported from the `infinigram` package.

Sources: [api/src/infinigram/__init__.py:1-2]()

### Attribution Router

The attribution router handles text attribution requests, which may be processed asynchronously via a queue. This is one of the primary functionalities of the API.

Sources: [api/app.py:54]()

## Error Handling

The API implements custom exception handling for `InfiniGramEngineException`, which ensures that client applications receive proper error responses when issues occur with the underlying infinigram processor.

```mermaid
flowchart TD
    A["Client Request"] --> B["API Endpoint"]
    B --> C["InfiniGram Processor"]
    C -->|Error| D["InfiniGramEngineException"]
    D --> E["infini_gram_engine_exception_handler"]
    E --> F["Return Problem+JSON response"]
```

Sources: [api/app.py:46-50]()

## Telemetry

The API integrates with OpenTelemetry for observability. The implementation automatically creates spans for HTTP requests and responses, providing insights into API usage and performance.

Different telemetry configurations are used based on the environment:
- In development: Uses a Simple Span Processor with OTLP exporter
- In production: Uses a Batch Span Processor with Cloud Trace exporter for Google Cloud

The health endpoint is excluded from instrumentation to prevent excessive telemetry data from health checks.

Sources: [api/app.py:56-69]()

## Integration with Infinigram Processor

The API interfaces with the Infinigram Processor library, which provides the core functionality for working with infinigram arrays. The processor is configured to use the same `index_base_path` as the API, ensuring that both components can access the same infinigram data.

```mermaid
flowchart LR
    subgraph "API Layer"
        API["FastAPI App"]
        Routers["API Routers"]
    end
    
    subgraph "Processing Layer"
        Processor["InfiniGram Processor"]
        Arrays["Infinigram Arrays<br>(index_base_path)"]
    end
    
    API --> Routers
    Routers --> Processor
    Processor --> Arrays
```

Sources: [api/src/config.py:12](), [packages/infini-gram-processor/src/infini_gram_processor/processor_config.py:1-15]()

## Request Processing Flow

The following diagram illustrates how the API processes different types of requests:

```mermaid
sequenceDiagram
    participant Client
    participant API as API (FastAPI)
    participant Router as Router (Health/Infinigram/Attribution)
    participant Service as Service Layer
    participant Processor as InfiniGram Processor
    participant Cache as Redis Cache
    participant Queue as Attribution Queue
    
    Client->>API: HTTP Request
    API->>Router: Route Request
    
    alt Health Check
        Router->>Client: 204 No Content
    else Infinigram/Document Request
        Router->>Service: Process Request
        Service->>Processor: Query Infinigram Data
        Processor-->>Service: Return Results
        Service-->>Router: Format Response
        Router-->>Client: JSON Response
    else Attribution Request
        Router->>Service: Process Attribution
        Service->>Cache: Check Cache
        
        alt Cache Hit
            Cache-->>Service: Return Cached Result
            Service-->>Router: Format Response
            Router-->>Client: JSON Response
        else Cache Miss
            Service->>Queue: Enqueue Attribution Job
            Service-->>Router: Return Job ID
            Router-->>Client: 202 Accepted
        end
    end
```

This diagram shows how different types of requests are handled by the API, including the use of caching and asynchronous processing for attribution requests.

Sources: [api/app.py:1-70](), [api/src/health.py:1-12]()

## Conclusion

The Infinigram API provides a well-structured interface to the Infinigram functionality, with separate routers for different domains and asynchronous processing for longer-running tasks. It integrates with various components such as Redis for caching, a job queue for attribution requests, and the Infinigram Processor library for the core functionality.

The API is designed with observability in mind, using OpenTelemetry for tracing and monitoring, and includes proper error handling to provide meaningful responses to client applications.

---

# Page: Endpoints

# Endpoints

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.vscode/extensions.json](.vscode/extensions.json)
- [.vscode/settings.json](.vscode/settings.json)
- [api/src/attribution/attribution_router.py](api/src/attribution/attribution_router.py)
- [api/src/documents/documents_router.py](api/src/documents/documents_router.py)
- [api/src/documents/documents_service.py](api/src/documents/documents_service.py)
- [api/src/health.py](api/src/health.py)
- [api/src/infinigram/__init__.py](api/src/infinigram/__init__.py)
- [api/src/infinigram/infinigram_router.py](api/src/infinigram/infinigram_router.py)

</details>



## Purpose

This document details the API endpoints provided by the Infinigram API system, their parameters, expected request/response formats, and usage patterns. For information about the overall API architecture, see [API](#3).

## Endpoint Overview

The Infinigram API provides four categories of endpoints:

1. Health Endpoint - For system health monitoring
2. Infinigram Endpoints - For retrieving index information
3. Documents Endpoints - For document retrieval and search
4. Attribution Endpoints - For text attribution analysis

### Endpoint Structure

```mermaid
graph LR
    Client["Client"]
    subgraph "Infinigram API"
        Health["Health Endpoint<br>/health/"]
        Infinigram["Infinigram Endpoint<br>/indexes"]
        
        subgraph "Documents Endpoints"
            DocSearch["Search<br>/{index}/documents/"]
            DocSingle["Get Document<br>/{index}/documents/{document_index}"]
            DocMultiple["Get Multiple Documents<br>/{index}/documents"]
        end
        
        Attribution["Attribution Endpoint<br>/{index}/attribution"]
    end
    
    Client --> Health
    Client --> Infinigram
    Client --> DocSearch
    Client --> DocSingle
    Client --> DocMultiple
    Client --> Attribution
```

Sources: [api/src/health.py](), [api/src/infinigram/infinigram_router.py](), [api/src/documents/documents_router.py](), [api/src/attribution/attribution_router.py]()

## Health Endpoint

The health endpoint is used by Kubernetes to determine if the application is ready to receive traffic.

### Endpoint Details

| Method | Path     | Description      | Response Code |
|--------|----------|------------------|---------------|
| GET    | /health/ | System health check | 204 No Content |

This endpoint returns a 204 No Content response when the system is healthy and is primarily used by Kubernetes (Skiff) to verify application readiness.

```mermaid
sequenceDiagram
    participant Client
    participant HealthEndpoint as "Health Endpoint"
    
    Client->>HealthEndpoint: GET /health/
    HealthEndpoint-->>Client: 204 No Content
```

Sources: [api/src/health.py:9-11]()

## Infinigram Endpoints

### Get Available Indexes

Retrieves a list of all available infinigram indices that can be used with other endpoints.

#### Endpoint Details

| Method | Path     | Description      | Response |
|--------|----------|------------------|----------|
| GET    | /indexes | Get available indices | Array of index IDs |

#### Response Format

```json
[
  "pileval-gpt2",
  "olmoe-mix-0924",
  "olmoe-mix-0924-nodclm",
  "v4-olmoe-0125-1b-7b-anneal-adapt",
  "v4-olmo-2-1124-13b-anneal-adapt",
  "v4-olmo-2-0325-32b-anneal-adapt"
]
```

```mermaid
sequenceDiagram
    participant Client
    participant InfinigramRouter as "Infinigram Router"
    
    Client->>InfinigramRouter: GET /indexes
    InfinigramRouter-->>Client: JSON Array of Available Indices
```

Sources: [api/src/infinigram/infinigram_router.py:7-9]()

## Documents Endpoints

The Documents API provides three endpoints for searching and retrieving documents.

### Search Documents

Searches for documents using a query string.

#### Endpoint Details

| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| GET | /{index}/documents/ | Search documents | See below |

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| search | string | Yes | - | The search query string |
| maximum_document_display_length | int | No | 10 | Maximum length in tokens of the returned document text |
| page | int | No | 0 | The page of documents to retrieve |
| page_size | int | No | 10 | Number of documents to return per page |

#### Response

Returns a `SearchResponse` object with the following structure:

```json
{
  "index": "string",
  "documents": [
    {
      "text": "string",
      "document_index": 0,
      "document_length": 0,
      "display_length": 0,
      "needle_offset": 0,
      "metadata": {},
      "token_ids": []
    }
  ],
  "page": 0,
  "page_size": 10,
  "page_count": 0,
  "total_documents": 0
}
```

### Get Document by Index

Retrieves a specific document by its index.

#### Endpoint Details

| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| GET | /{index}/documents/{document_index} | Get document by index | See below |

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| index | string | Yes | The infinigram index |
| document_index | int | Yes | The index of the document to retrieve |

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| maximum_document_display_length | int | No | 10 | Maximum length in tokens of the returned document text |

#### Response

Returns an `InfiniGramDocumentResponse` object with the following structure:

```json
{
  "index": "string",
  "document_index": 0,
  "document_length": 0,
  "display_length": 0,
  "needle_offset": 0,
  "metadata": {},
  "token_ids": [],
  "text": "string"
}
```

### Get Multiple Documents by Index

Retrieves multiple documents by their indices.

#### Endpoint Details

| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| GET | /{index}/documents | Get multiple documents by index | See below |

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| document_indexes | array[int] | Yes | - | A list of document indices to retrieve |
| maximum_document_display_length | int | No | 10 | Maximum length in tokens of the returned document text |

#### Response

Returns an `InfiniGramDocumentsResponse` object with the following structure:

```json
{
  "index": "string",
  "documents": [
    {
      "document_index": 0,
      "document_length": 0,
      "display_length": 0,
      "needle_offset": 0,
      "metadata": {},
      "token_ids": [],
      "text": "string"
    }
  ]
}
```

### Documents Request Flow

```mermaid
sequenceDiagram
    participant Client
    participant Router as "Documents Router"
    participant Service as "Documents Service"
    participant Processor as "InfiniGram Processor"
    
    Client->>Router: GET /{index}/documents/
    Router->>Service: search_documents()
    Service->>Processor: search_documents()
    Processor-->>Service: Document Results
    Service-->>Router: SearchResponse
    Router-->>Client: JSON Response
    
    Client->>Router: GET /{index}/documents/{document_index}
    Router->>Service: get_document_by_index()
    Service->>Processor: get_document_by_index()
    Processor-->>Service: Document
    Service-->>Router: InfiniGramDocumentResponse
    Router-->>Client: JSON Response
    
    Client->>Router: GET /{index}/documents?document_indexes=[...]
    Router->>Service: get_multiple_documents_by_index()
    Service->>Processor: get_documents_by_indexes()
    Processor-->>Service: Documents
    Service-->>Router: InfiniGramDocumentsResponse
    Router-->>Client: JSON Response
```

Sources: [api/src/documents/documents_router.py:26-85](), [api/src/documents/documents_service.py:33-118]()

## Attribution Endpoints

### Get Document Attributions

Performs attribution analysis on text.

#### Endpoint Details

| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| POST | /{index}/attribution | Get document attributions | See below |

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| index | string | Yes | The infinigram index to use for attribution |

#### Request Body

The request body should be an `AttributionRequest` object with the following structure:

```json
{
  "query": "string",
  "top_k": 10
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| query | string | Yes | - | The text to analyze for attribution |
| top_k | int | No | 10 | The maximum number of attribution results to return |

#### Response

Returns an `AttributionResponse` object containing the attribution results.

#### Error Responses

| Status Code | Description |
|-------------|-------------|
| 408 | Attribution Timeout Error |

```mermaid
sequenceDiagram
    participant Client
    participant Router as "Attribution Router"
    participant Service as "Attribution Service"
    
    Client->>Router: POST /{index}/attribution
    Router->>Service: get_attribution_for_response()
    Service-->>Router: AttributionResponse
    Router-->>Client: JSON Response
    
    Note over Client,Router: Error Handling
    
    Router->>Service: get_attribution_for_response()
    Service--x Router: AttributionTimeoutError
    Router-->>Client: 408 Timeout Error
```

Sources: [api/src/attribution/attribution_router.py:16-31]()

## Implementation Mapping

The following diagram shows how API endpoints map to specific code implementations:

```mermaid
graph TB
    subgraph "API Routes"
        Health["/health/"]
        Indexes["/indexes"]
        DocSearch["/{index}/documents/"]
        DocSingle["/{index}/documents/{document_index}"]
        DocMultiple["/{index}/documents"]
        Attribution["/{index}/attribution"]
    end
    
    subgraph "Route Functions"
        HealthFunc["health() function<br>health_router.py:9-11"]
        IndexesFunc["get_available_indexes() function<br>infinigram_router.py:7-9"]
        SearchFunc["search_documents() function<br>documents_router.py:26-52"]
        DocSingleFunc["get_document_by_index() function<br>documents_router.py:55-66"]
        DocMultipleFunc["get_documents_by_index() function<br>documents_router.py:69-85"]
        AttributionFunc["get_document_attributions() function<br>attribution_router.py:24-31"]
    end
    
    Health --> HealthFunc
    Indexes --> IndexesFunc
    DocSearch --> SearchFunc
    DocSingle --> DocSingleFunc
    DocMultiple --> DocMultipleFunc
    Attribution --> AttributionFunc
    
    subgraph "Service Classes"
        DocumentsServiceClass["DocumentsService class<br>documents_service.py:33-118"]
        AttributionServiceClass["AttributionService class"]
    end
    
    SearchFunc --> DocumentsServiceClass
    DocSingleFunc --> DocumentsServiceClass
    DocMultipleFunc --> DocumentsServiceClass
    AttributionFunc --> AttributionServiceClass
    
    subgraph "Core Service Methods"
        SearchMethod["search_documents() method<br>documents_service.py:39-74"]
        DocSingleMethod["get_document_by_index() method<br>documents_service.py:76-94"]
        DocMultipleMethod["get_multiple_documents_by_index() method<br>documents_service.py:96-118"]
        AttributionMethod["get_attribution_for_response() method"]
    end
    
    DocumentsServiceClass --> SearchMethod
    DocumentsServiceClass --> DocSingleMethod
    DocumentsServiceClass --> DocMultipleMethod
    AttributionServiceClass --> AttributionMethod
```

Sources: [api/src/health.py](), [api/src/infinigram/infinigram_router.py](), [api/src/documents/documents_router.py](), [api/src/documents/documents_service.py](), [api/src/attribution/attribution_router.py]()

---

# Page: Attribution Service

# Attribution Service

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/attribution/attribution_router.py](api/src/attribution/attribution_router.py)
- [api/src/attribution/attribution_service.py](api/src/attribution/attribution_service.py)

</details>



The Attribution Service is a core component of the Infinigram API that processes attribution requests to identify the origins of generated text. It handles the computation-intensive task of attributing spans of text to source documents, implementing efficient caching and asynchronous processing to manage resource utilization effectively. This page documents the service's architecture, components, data flow, and implementation details.

For information about the API endpoints that interface with this service, see [Endpoints](#3.1). For details on the worker that processes attribution jobs, see [Attribution Worker](#4).

## Overview

The Attribution Service acts as a bridge between client requests for attribution and the actual processing of those requests. It manages:

1. Processing incoming attribution requests
2. Checking/storing results in the Redis cache
3. Queueing attribution jobs for asynchronous processing
4. Returning attribution results to clients

```mermaid
graph TD
    subgraph "Attribution Service Components"
        API["API Endpoint"] --> AS["AttributionService"]
        AS --> Cache["Redis Cache"]
        AS --> Queue["Attribution Queue"]
        AS --> IGP["InfiniGramProcessor"]
        Queue --> Worker["Attribution Worker"]
        Worker --> Cache
    end

    Client["Client"] --> API
    Worker --> IGP
```

Sources: [api/src/attribution/attribution_service.py:72-90](api/src/attribution/attribution_service.py:72-90), [api/src/attribution/attribution_router.py:16-31]()

## Data Models

The Attribution Service uses several key data models:

### AttributionRequest

The `AttributionRequest` model represents incoming attribution requests from clients. It contains parameters such as:
- `response`: The text to be attributed
- `delimiters`: Delimiters for tokenization
- `minimum_span_length`: Minimum length for attributable spans
- `maximum_documents_per_span`: Maximum number of documents to return per span
- Other configuration parameters for controlling attribution behavior

### AttributionResponse

The `AttributionResponse` extends `BaseInfiniGramResponse` and represents the result of an attribution operation:

```mermaid
classDiagram
    class AttributionResponse {
        +spans: Sequence[AttributionSpan]
        +input_tokens: Optional[Sequence[str]]
    }

    class AttributionSpan {
        +left: int
        +right: int
        +length: int
        +count: int
        +unigram_logprob_sum: float
        +text: str
        +token_ids: Sequence[int]
        +documents: List[AttributionDocument]
    }

    class AttributionDocument {
        +display_length_long: int
        +needle_offset_long: int
        +text_long: str
        +display_offset_snippet: int
        +needle_offset_snippet: int
        +text_snippet: str
        +id: str
        +text: str
        +score: float
        +index: str
    }

    AttributionResponse --> AttributionSpan: contains
    AttributionSpan --> AttributionDocument: references
```

Sources: [api/src/attribution/attribution_service.py:40-65]()

## Service Implementation

The `AttributionService` class is the central implementation of the attribution service functionality.

### Constructor and Dependencies

The service uses dependency injection to receive its required components:

```python
def __init__(
    self,
    infini_gram_processor: InfiniGramProcessorDependency,
    documents_service: DocumentsServiceDependency,
    attribution_queue: AttributionQueueDependency,
    cache: CacheDependency,
):
    self.infini_gram_processor = infini_gram_processor
    self.documents_service = documents_service
    self.attribution_queue = attribution_queue
    self.cache = cache
```

Sources: [api/src/attribution/attribution_service.py:79-89]()

## Request Processing Flow

The following diagram illustrates how attribution requests flow through the system:

```mermaid
sequenceDiagram
    participant Client
    participant Router as "AttributionRouter"
    participant Service as "AttributionService"
    participant Cache as "Redis Cache"
    participant Queue as "SAQ Queue"
    participant Worker as "Attribution Worker"
    participant Processor as "InfiniGramProcessor"

    Client->>Router: POST /{index}/attribution
    Router->>Service: get_attribution_for_response(index, request)
    
    Service->>+Cache: Check cache (_get_cached_response)
    
    alt Cache hit
        Cache-->>Service: Return cached response
        Service-->>Router: Return AttributionResponse
        Router-->>Client: Return JSON response
    else Cache miss
        Cache-->>-Service: Return None
        
        Service->>+Queue: Queue attribution job (attribution_queue.apply)
        
        note over Service,Queue: With OpenTelemetry tracing context
        
        Queue-->>Service: Wait for job completion
        
        Queue->>Worker: Process attribution job
        Worker->>Processor: Process attribution
        Processor-->>Worker: Return attribution result
        Worker->>Queue: Store result
        
        Queue-->>-Service: Return attribution result JSON
        
        Service->>Service: Parse JSON to AttributionResponse
        Service->>Cache: Cache response (_cache_response)
        Service-->>Router: Return AttributionResponse
        Router-->>Client: Return JSON response
    end
```

Sources: [api/src/attribution/attribution_service.py:161-228](), [api/src/attribution/attribution_router.py:24-31]()

## Caching Implementation

The Attribution Service implements efficient caching to avoid redundant processing of identical requests:

1. **Cache Key Generation**: A unique cache key is created by hashing a combination of the index and request data
2. **Cache Retrieval**: Cached responses are retrieved with an extended expiration time
3. **Cache Storage**: New attribution results are stored with a 1-hour expiration time

```mermaid
flowchart TB
    Request["Attribution Request"] --> Hash["Generate Cache Key\nsha256(index + request)"]
    Hash --> Check["Check Redis Cache"]
    
    Check --> CacheHit{{"Cache Hit?"}}
    
    CacheHit -->|"Yes"| Extend["Extend Expiration (12h)"]
    Extend --> Return["Return Cached Response"]
    
    CacheHit -->|"No"| Process["Process Attribution Request"]
    Process --> Store["Store in Cache (1h expiration)"]
    Store --> Return
```

Sources: [api/src/attribution/attribution_service.py:91-159]()

### Cache Key Generation

The service generates cache keys by:
1. Combining the request class name, index, and serialized request data
2. Hashing the combined string using SHA-256

```python
def _get_cache_key(self, index: str, request: AttributionRequest) -> bytes:
    combined_index_and_request = (
        f"{request.__class__.__qualname__}::{index}{request.model_dump_json()}"
    )
    key = sha256(
        combined_index_and_request.encode("utf-8", errors="ignore")
    ).digest()

    return key
```

Sources: [api/src/attribution/attribution_service.py:91-99]()

### Cache Retrieval

When retrieving cached responses, the service:
1. Gets the cache key for the request
2. Retrieves the cached JSON from Redis
3. Extends the expiration time to 12 hours
4. Deserializes the JSON into an `AttributionResponse` object

Source: [api/src/attribution/attribution_service.py:101-137]()

### Cache Storage

When storing new attribution results, the service:
1. Gets the cache key for the request
2. Stores the raw JSON response
3. Sets an expiration time of 1 hour

Source: [api/src/attribution/attribution_service.py:139-159]()

## Asynchronous Processing

Attribution requests are processed asynchronously through a queue system:

1. If a response is not in the cache, an attribution job is queued with a unique ID
2. The job includes the request parameters and OpenTelemetry tracing context
3. The service awaits the job's completion
4. Upon completion, the result is cached and returned to the client

Source: [api/src/attribution/attribution_service.py:174-211]()

## Error Handling

The Attribution Service has robust error handling, particularly for timeouts:

1. If job processing exceeds the timeout (60 seconds), a `TimeoutError` is raised
2. The error is logged and traced with OpenTelemetry
3. The job is aborted in the queue
4. An `AttributionTimeoutError` is returned to the client with a 503 status code

```mermaid
flowchart TD
    TimeoutError["TimeoutError detected"] --> Log["Log error with job details"]
    Log --> Span["Update OpenTelemetry span\nwith error status"]
    Span --> Abort["Abort job in queue"]
    Abort --> Raise["Raise AttributionTimeoutError\nwith 503 status"]
```

Source: [api/src/attribution/attribution_service.py:212-228](), [api/src/attribution/attribution_service.py:67-72]()

## API Integration

The Attribution Service is exposed via a FastAPI router that defines a POST endpoint for attribution requests:

```python
@attribution_router.post(
    path="/{index}/attribution",
    responses={
        AttributionTimeoutError.status: generate_swagger_response(
            AttributionTimeoutError
        )
    },
)
async def get_document_attributions(
    index: str,
    body: AttributionRequest,
    attribution_service: Annotated[AttributionService, Depends()],
) -> AttributionResponse:
    result = await attribution_service.get_attribution_for_response(index, body)
    return result
```

Source: [api/src/attribution/attribution_router.py:16-31]()

## Observability

The Attribution Service integrates with OpenTelemetry for tracing and monitoring:

1. Every key method is wrapped with a span for detailed tracing
2. Events are added to spans for important operations (cache hits, etc.)
3. Error states are properly recorded in spans
4. Tracing context is propagated to the worker for end-to-end visibility

Source: [api/src/attribution/attribution_service.py:101-101](), [api/src/attribution/attribution_service.py:139-139](), [api/src/attribution/attribution_service.py:161-161](), [api/src/attribution/attribution_service.py:174-186]()

## Summary

The Attribution Service is a critical component that enables the attribution of text spans to source documents. Its design emphasizes:

1. **Efficiency**: Through caching and asynchronous processing
2. **Resilience**: With robust error handling and timeouts
3. **Observability**: Via comprehensive tracing
4. **Scalability**: By offloading computation to a dedicated worker

This design allows the service to handle potentially resource-intensive attribution tasks while maintaining API responsiveness.

---

# Page: Documents Service

# Documents Service

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/documents/documents_router.py](api/src/documents/documents_router.py)
- [api/src/documents/documents_service.py](api/src/documents/documents_service.py)

</details>



## Purpose and Scope

The Documents Service is responsible for retrieving and handling document data within the Infinigram API system. It provides functionality for searching documents, retrieving individual documents by their index, and fetching multiple documents in a single request. This service is a core component of the API layer that interacts with the underlying Infinigram arrays (ML models) to access document content.

For information about the Attribution Service which may use document data for attribution analysis, see [Attribution Service](#3.2).

Sources: [api/src/documents/documents_service.py:33-118](), [api/src/documents/documents_router.py:1-86]()

## Architecture

The Documents Service fits into the Infinigram API system as follows:

```mermaid
graph TB
    subgraph "Client"
        ClientApp["Client Application"]
    end

    subgraph "API Layer"
        FastAPI["FastAPI Application"]
        DocRouter["documents_router.py"]
    end

    subgraph "Service Layer"
        DocService["DocumentsService"]
    end

    subgraph "Processing Layer"
        InfiniGramProcessor["InfiniGramProcessor"]
    end

    subgraph "Data Layer"
        InfinigramArrays["Infinigram Arrays"]
    end

    ClientApp -->|"HTTP Request"| FastAPI
    FastAPI -->|"Routes Request"| DocRouter
    DocRouter -->|"Calls"| DocService
    DocService -->|"Processes Documents"| InfiniGramProcessor
    InfiniGramProcessor -->|"Accesses"| InfinigramArrays

    classDef service fill:#f9f,stroke:#333,stroke-width:2px;
    class DocService service;
```

The Documents Service acts as an intermediary between the API endpoints and the InfiniGramProcessor, which interacts directly with the Infinigram arrays. It provides a structured interface for accessing document data and handles the transformation of raw document data into standardized response objects.

Sources: [api/src/documents/documents_service.py:33-39](), [api/src/documents/documents_router.py:13-24]()

## Components and Data Models

### Class Structure

```mermaid
classDiagram
    class DocumentsService {
        +InfiniGramProcessor infini_gram_processor
        +search_documents(search, maximum_context_length, page_size, page)
        +get_document_by_index(document_index, maximum_context_length)
        +get_multiple_documents_by_index(document_requests)
    }

    class BaseInfiniGramResponse {
        +String index
    }

    class Document {
        +String text
        +int document_index
        +int document_length
        +int display_length
        +int needle_offset
        +Dict metadata
        +List token_ids
    }

    class InfiniGramDocumentResponse {
        +inherits Document
        +inherits BaseInfiniGramResponse
    }

    class InfiniGramDocumentsResponse {
        +Iterable~Document~ documents
    }

    class SearchResponse {
        +List~Document~ documents
        +int page
        +int page_size
        +int page_count
        +int total_documents
    }

    BaseInfiniGramResponse <|-- InfiniGramDocumentResponse
    Document <|-- InfiniGramDocumentResponse
    BaseInfiniGramResponse <|-- InfiniGramDocumentsResponse
    BaseInfiniGramResponse <|-- SearchResponse
```

### Key Components

1. **DocumentsService**: The main service class that processes document requests
2. **Response Models**:
   - `InfiniGramDocumentResponse`: Represents a single document response
   - `InfiniGramDocumentsResponse`: Contains multiple documents
   - `SearchResponse`: Used for search results with pagination information

Sources: [api/src/documents/documents_service.py:18-32](), [api/src/documents/documents_service.py:33-118]()

## API Endpoints

The Documents Service exposes three main API endpoints:

| Endpoint | Method | Description | Parameters | Response |
|----------|--------|-------------|------------|----------|
| `/{index}/documents/` | GET | Search for documents | `search`, `maximum_document_display_length`, `page`, `page_size` | `SearchResponse` |
| `/{index}/documents/{document_index}` | GET | Get a specific document | `document_index`, `maximum_document_display_length` | `InfiniGramDocumentResponse` |
| `/{index}/documents` | GET | Get multiple documents | `document_indexes`, `maximum_document_display_length` | `InfiniGramDocumentsResponse` |

### Common Parameters

- `index`: The Infinigram index to query
- `maximum_document_display_length`: The maximum length in tokens of the returned document text (default: 10)

Sources: [api/src/documents/documents_router.py:26-85]()

## Request Flow

### Document Search Flow

```mermaid
sequenceDiagram
    participant Client
    participant DocRouter as "documents_router"
    participant DocService as "DocumentsService"
    participant IGProcessor as "InfiniGramProcessor"
    
    Client->>DocRouter: GET /{index}/documents/?search=query
    DocRouter->>DocService: search_documents(query, max_length, page, page_size)
    
    DocService->>+IGProcessor: search_documents(query, max_length, page, page_size)
    IGProcessor-->>-DocService: search_documents_result
    
    DocService->>DocService: Map documents to response format
    DocService->>DocRouter: Return SearchResponse
    DocRouter->>Client: JSON Response
```

### Document Retrieval Flow

```mermaid
sequenceDiagram
    participant Client
    participant DocRouter as "documents_router"
    participant DocService as "DocumentsService"
    participant IGProcessor as "InfiniGramProcessor"
    
    Client->>DocRouter: GET /{index}/documents/{document_index}
    DocRouter->>DocService: get_document_by_index(document_index, max_length)
    
    DocService->>+IGProcessor: get_document_by_index(document_index, max_length)
    IGProcessor-->>-DocService: document
    
    DocService->>DocRouter: Return InfiniGramDocumentResponse
    DocRouter->>Client: JSON Response
```

Sources: [api/src/documents/documents_service.py:39-74](), [api/src/documents/documents_service.py:76-94](), [api/src/documents/documents_router.py:26-52](), [api/src/documents/documents_router.py:55-66]()

## Implementation Details

### Search Documents

The `search_documents` method queries the InfiniGramProcessor to find documents matching a search query. It handles pagination and converts the raw document data into the standardized `SearchResponse` format.

```
search_documents(
    search: str,               # The search query
    maximum_context_length: int, # Max document display length
    page_size: int,            # Number of documents per page
    page: int                  # Page number (0-indexed)
) -> SearchResponse
```

Key operations:
1. Query the InfiniGramProcessor with the search parameters
2. Map the returned documents to the standard Document format
3. Calculate pagination details (total pages, etc.)
4. Return a structured SearchResponse

Sources: [api/src/documents/documents_service.py:39-74]()

### Get Document by Index

The `get_document_by_index` method retrieves a single document using its index identifier.

```
get_document_by_index(
    document_index: int,         # The index of the document to retrieve
    maximum_context_length: int  # Max document display length
) -> InfiniGramDocumentResponse
```

Key operations:
1. Request a specific document from the InfiniGramProcessor
2. Map the returned document to the InfiniGramDocumentResponse format
3. Return the formatted response

Sources: [api/src/documents/documents_service.py:76-94]()

### Get Multiple Documents by Index

The `get_multiple_documents_by_index` method retrieves multiple documents in a single operation.

```
get_multiple_documents_by_index(
    document_requests: Iterable[GetDocumentByIndexRequest]  # List of document requests
) -> InfiniGramDocumentsResponse
```

Key operations:
1. Request multiple documents from the InfiniGramProcessor
2. Map each returned document to the standard Document format
3. Return all documents in an InfiniGramDocumentsResponse

Sources: [api/src/documents/documents_service.py:96-118]()

## Observability

The Documents Service uses OpenTelemetry for tracing request handling. Each public method in the DocumentsService class is decorated with `@tracer.start_as_current_span` to create spans for monitoring service performance and debugging issues.

Example traces:
- `documents_service/search_documents`
- `documents_service/get_document_by_index`
- `documents_service/get_multiple_documents_by_index`

Sources: [api/src/documents/documents_service.py:39](), [api/src/documents/documents_service.py:76](), [api/src/documents/documents_service.py:96]()

## Integration with Other Services

The Documents Service primarily interacts with the InfiniGramProcessor, which serves as the interface to the underlying Infinigram arrays. It may also be used by the Attribution Service when performing attribution analysis that requires document context.

The service follows a clean architectural pattern where:
1. The router handles HTTP request parsing and validation
2. The service contains the business logic
3. The InfiniGramProcessor provides access to the data layer

Sources: [api/src/documents/documents_service.py:33-39](), [api/src/documents/documents_router.py:13-24]()

---

# Page: Infinigram Service

# Infinigram Service

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.vscode/settings.json](.vscode/settings.json)
- [api/src/infinigram/infinigram_router.py](api/src/infinigram/infinigram_router.py)
- [bin/download-infini-gram-array.sh](bin/download-infini-gram-array.sh)

</details>



## Purpose

The Infinigram Service is a component of the infinigram-api system that provides information about available Infinigram indices. These indices represent different machine learning models that power the attribution and document retrieval functionalities. The service acts as an interface for clients to discover which models are available for use with the API.

For information about how these indices are used for attribution, see [Attribution Service](#3.2). For information about document retrieval using these indices, see [Documents Service](#3.3).

## Service Structure

The Infinigram Service is implemented as a FastAPI router that exposes a single endpoint to retrieve available indices. The service is intentionally lightweight, serving primarily as a discovery mechanism for available Infinigram indices.

```mermaid
graph TD
    subgraph "Infinigram Service Components"
        InfinigramRouter["infinigram_router.py"]
        IndexesEndpoint["/indexes endpoint"]
        
        InfinigramRouter --> IndexesEndpoint
    end
    
    subgraph "Dependencies"
        IndexMappings["index_mappings.py"]
        AvailableIndices["AvailableInfiniGramIndexId enum"]
        
        IndexMappings --> AvailableIndices
    end
    
    IndexesEndpoint -->|"Queries"| AvailableIndices
```

Sources: [api/src/infinigram/infinigram_router.py:1-10]()

## API Endpoint

The Infinigram Service provides a single GET endpoint that returns all available Infinigram indices:

### `GET /indexes`

This endpoint retrieves a list of all available Infinigram indices based on the `AvailableInfiniGramIndexId` enum from the `infini_gram_processor.index_mappings` module.

**Response:** A JSON array containing all available Infinigram index IDs.

The implementation is straightforward:

```python
@infinigram_router.get(path="/indexes")
def get_available_indexes() -> list[AvailableInfiniGramIndexId]:
    return [index for index in AvailableInfiniGramIndexId]
```

Sources: [api/src/infinigram/infinigram_router.py:7-9]()

## Supported Infinigram Indices

The Infinigram Service provides access to several indices, each representing a different machine learning model. Based on the download script configuration, the following indices are supported:

| Index Name | Model Type | Storage |
|------------|------------|---------|
| v4_pileval_llama | Base Infinigram array | Downloaded from S3 |
| olmoe-mix-0924-dclm | OLMo-E mix model | Symlink to base array |
| olmoe-mix-0924-nodclm | OLMo-E mix model (no DCLM) | Symlink to base array |
| v4-olmoe-0125-1b-7b-anneal-adapt | OLMo-E 1B-7B model | Symlink to base array |
| v4-olmo-2-1124-13b-anneal-adapt | OLMo-2 13B model | Symlink to base array |
| v4-olmo-2-0325-32b-anneal-adapt | OLMo-2 32B model | Symlink to base array |

In the development environment, these arrays are set up using a script that downloads the base array and creates symbolic links for the other indices.

Sources: [bin/download-infini-gram-array.sh:1-36]()

## Array Setup and Management

The Infinigram arrays, which contain the actual machine learning models, are stored in the `infinigram-array` directory. During development, these arrays are downloaded or symlinked using the `download-infini-gram-array.sh` script:

```mermaid
graph TD
    subgraph "Array Setup Process"
        Script["download-infini-gram-array.sh"]
        S3["S3 Bucket: infini-gram-lite"]
        BaseArray["v4_pileval_llama array"]
        DerivedArrays["Multiple symlinked arrays"]
        
        Script -->|"Downloads"| S3
        S3 -->|"Provides"| BaseArray
        Script -->|"Creates symlinks"| DerivedArrays
        BaseArray -->|"Basis for"| DerivedArrays
    end
```

The script checks if the base array is already downloaded, and if not, downloads it from S3. Then it creates symbolic links for the other indices, all pointing to the base array.

Sources: [bin/download-infini-gram-array.sh:8-36]()

## System Integration

The Infinigram Service integrates with the broader system architecture as shown below:

```mermaid
graph TB
    subgraph "Client Layer"
        Client["Client Application"]
    end
    
    subgraph "API Layer"
        API["FastAPI Application (app.py)"]
        InfinigramRouter["infinigram_router.py"]
        AttributionRouter["attribution_router.py"]
        DocumentsRouter["documents_router.py"]
    end
    
    subgraph "Processing Layer"
        InfiniGramProcessor["infini_gram_processor"]
        IndexMappings["index_mappings.py"]
    end
    
    subgraph "Data Layer"
        InfinigramArrays["Infinigram Arrays (ML Models)"]
    end
    
    Client -->|"Queries for indices"| API
    API -->|"Routes request"| InfinigramRouter
    API -->|"Routes request"| AttributionRouter
    API -->|"Routes request"| DocumentsRouter
    
    InfinigramRouter -->|"Queries available indices"| IndexMappings
    AttributionRouter -->|"Uses indices for attribution"| InfiniGramProcessor
    DocumentsRouter -->|"Uses indices for document retrieval"| InfiniGramProcessor
    
    InfiniGramProcessor -->|"References"| IndexMappings
    InfiniGramProcessor -->|"Accesses model data"| InfinigramArrays
```

The Infinigram Service primarily interacts with the `index_mappings.py` module from the `infini_gram_processor` package to retrieve information about available indices. The actual processing using these indices is handled by the Attribution and Documents services.

Sources: [api/src/infinigram/infinigram_router.py:1-10]()

## Usage Workflow

A typical workflow involving the Infinigram Service is as follows:

```mermaid
sequenceDiagram
    participant Client
    participant InfinigramEndpoint as "Infinigram Endpoint (/indexes)"
    participant IndexMappings as "AvailableInfiniGramIndexId"
    participant OtherServices as "Attribution/Documents Services"
    
    Client->>InfinigramEndpoint: GET /indexes
    InfinigramEndpoint->>IndexMappings: Query available indices
    IndexMappings-->>InfinigramEndpoint: Return list of indices
    InfinigramEndpoint-->>Client: Return JSON array of indices
    
    Note over Client: Select appropriate index
    
    Client->>OtherServices: Make API calls with chosen index
    OtherServices-->>Client: Return results using specified index
```

This workflow enables clients to discover what indices (models) are available in the system and select the appropriate one for their attribution or document retrieval tasks.

Sources: [api/src/infinigram/infinigram_router.py:7-9]()

## Summary

The Infinigram Service is a simple but essential component that provides discovery functionality for the available machine learning models in the system. While the service itself has minimal functionality, it plays an important role in the overall system by allowing clients to query which models are available for use with the more complex Attribution and Documents services.

---

# Page: Attribution Worker

# Attribution Worker

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/README.md](api/README.md)
- [api/src/attribution/attribution_queue_service.py](api/src/attribution/attribution_queue_service.py)
- [attribution_worker/Dockerfile](attribution_worker/Dockerfile)
- [attribution_worker/README.md](attribution_worker/README.md)
- [attribution_worker/config.py](attribution_worker/config.py)
- [attribution_worker/pyproject.toml](attribution_worker/pyproject.toml)
- [attribution_worker/worker.py](attribution_worker/worker.py)
- [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
- [docs/indexes.md](docs/indexes.md)
- [packages/infini-gram-processor/README.md](packages/infini-gram-processor/README.md)

</details>



The Attribution Worker is a dedicated asynchronous processing service within the infinigram-api system responsible for handling computationally intensive attribution tasks. By offloading these tasks from the main API service, the system remains responsive while processing potentially long-running attribution requests. This page describes the worker's architecture, configuration, and operation within the system.

For information about the API components that interact with the worker, see [Attribution Service](#3.2).

## Architecture Overview

The Attribution Worker operates separately from the main API service, retrieving jobs from a shared queue, processing them using the Infinigram processor library, and storing results. It's designed to scale independently from the API layer.

### Component Diagram

```mermaid
graph TB
    subgraph "API Layer"
        API["FastAPI Application"]
        AttributionRouter["attribution_router.py"]
        AttributionService["attribution_service.py"]
        QueueService["attribution_queue_service.py"]
    end
    
    subgraph "Queue"
        SAQ["SAQ (Simple Async Queue)"]
    end
    
    subgraph "Attribution Worker"
        Worker["worker.py"]
        WorkerConfig["config.py"]
    end
    
    subgraph "Shared Components"
        InfinigramProcessor["infini_gram_processor"]
        InfinigramArrays["Infinigram Arrays"]
    end
    
    subgraph "Storage"
        Redis["Redis Cache"]
    end
    
    API --> AttributionRouter
    AttributionRouter --> AttributionService
    AttributionService --> QueueService
    QueueService --> SAQ
    
    SAQ --> Worker
    Worker --> WorkerConfig
    Worker --> InfinigramProcessor
    Worker --> Redis
    
    InfinigramProcessor --> InfinigramArrays
    
    classDef primary stroke-width:2px;
    class Worker,InfinigramProcessor primary;
```

Sources: [attribution_worker/worker.py](), [attribution_worker/config.py](), [api/src/attribution/attribution_queue_service.py]()

## Configuration

The worker is configured through environment variables, with defaults defined in the `Config` class. Key configuration settings include:

| Configuration Parameter | Default Value | Description |
|------------------------|---------------|-------------|
| `index_base_path` | `/mnt/infinigram-array` | Base path to the Infinigram index arrays |
| `application_name` | `infini-gram-api-worker` | Name used for logging and telemetry |
| `attribution_queue_url` | `redis://localhost:6379` | URL for the attribution queue |
| `python_env` | `prod` | Environment (prod/dev) |
| `attribution_queue_name` | Computed as `infini-gram-attribution-{env}` | Name of the queue to process |

Sources: [attribution_worker/config.py:5-21]()

## Job Processing Flow

The Attribution Worker processes jobs from the queue through the `attribution_job` function. Here's the flow of how attribution tasks are processed:

```mermaid
sequenceDiagram
    participant API as "API Service"
    participant Queue as "SAQ Queue"
    participant Worker as "attribution_job"
    participant Processor as "infini_gram_processor"
    participant Arrays as "Infinigram Arrays"
    participant Redis as "Redis Cache"
    
    API->>Queue: Enqueue attribution task
    Worker->>+Queue: Poll for job
    Queue-->>-Worker: Return attribution job
    
    Note over Worker: Begin processing with OpenTelemetry tracing
    
    Worker->>+Processor: Get index for specified model
    Processor-->>-Worker: Return InfiniGramIndex
    
    Worker->>+Processor: attribute(input, delimiters, parameters)
    Processor->>Arrays: Access index arrays
    Processor-->>-Worker: Return attribute_result
    
    Worker->>Worker: sort_and_cap_spans(spans)
    Worker->>Worker: get_document_requests(spans)
    
    Worker->>+Processor: get_documents_by_pointers(document_request_by_span)
    Processor->>Arrays: Retrieve document data
    Processor-->>-Worker: Return documents_by_span
    
    Worker->>Worker: get_spans_with_documents(spans, documents)
    
    Worker->>Worker: Create AttributionResponse
    Worker->>Redis: Store response in cache
    Worker->>Queue: Mark job as complete
    
    API->>Redis: Retrieve completed attribution result
```

Sources: [attribution_worker/worker.py:58-142]()

## Attribution Job Function

The core of the worker is the `attribution_job` function that processes attribution requests:

1. **Initialization and Tracing**:
   - Extracts the OpenTelemetry context and starts a span for tracing
   - Sets up messaging attributes for observability

2. **Index Retrieval**:
   - Gets the appropriate `InfiniGramIndex` for the specified model

3. **Attribution Processing**:
   - Calls the index's `attribute` method asynchronously on a separate thread
   - Passes parameters including:
     - `input`: The text to analyze
     - `delimiters`: List of delimiters to use
     - `allow_spans_with_partial_words`: Whether to allow partial word matches
     - `minimum_span_length`: Minimum span length to consider
     - `maximum_frequency`: Maximum frequency threshold

4. **Span Sorting and Limiting**:
   - Limits the density of spans based on `maximum_span_density`
   - Sorts spans according to the specified `span_ranking_method`

5. **Document Retrieval**:
   - Generates document requests for each span
   - Retrieves documents asynchronously using `get_documents_by_pointers`
   - Builds spans with document contexts

6. **Response Creation**:
   - Assembles the final `AttributionResponse`
   - Returns the result as JSON

Sources: [attribution_worker/worker.py:58-142]()

## Technical Implementation Details

### Queue Integration

The worker uses the Simple Async Queue (SAQ) library to process jobs. The queue is configured with:

```python
queue = Queue.from_url(config.attribution_queue_url, name=config.attribution_queue_name)

settings = SettingsDict(
    queue=queue, functions=[("attribute", attribution_job)], concurrency=1
)
```

This configuration registers the `attribution_job` function to handle tasks with the name "attribute" and sets the concurrency to 1, meaning only one attribution job will be processed at a time.

Sources: [attribution_worker/worker.py:37-147]()

### OpenTelemetry Integration

The worker includes comprehensive OpenTelemetry instrumentation to enable distributed tracing:

- Creates a `TracerProvider` and configures span processors
- Uses different exporters based on the environment:
  - `SimpleSpanProcessor` with `OTLPSpanExporter` for development
  - `BatchSpanProcessor` with `CloudTraceSpanExporter` for production
- Propagates trace context from the API to maintain continuous traces

This allows tracking the performance and behavior of attribution jobs across the system.

Sources: [attribution_worker/worker.py:39-52](), [attribution_worker/worker.py:75-93]()

## Deployment

The Attribution Worker is containerized using Docker with a multi-stage build process:

1. **Builder Stage**:
   - Uses `uv` for Python dependency management
   - Installs dependencies according to the lock file
   - Copies the application code

2. **Final Stage**:
   - Starts from a clean Python image
   - Copies only the necessary files from the builder stage
   - Sets environment variables for OpenTelemetry
   - Runs the worker using the SAQ command

Two deployment variants are provided:
- `dev`: For development with verbose logging
- `prod`: For production deployment

Sources: [attribution_worker/Dockerfile:1-62]()

## Integration with API

The API service interacts with the worker through a shared queue. The API:

1. Enqueues attribution jobs with parameters
2. Provides a tracking ID to the client
3. Allows the client to poll for results
4. Retrieves results from the cache once the worker completes the job

Both the API and worker access the same queue, enabling asynchronous processing of attribution tasks.

Sources: [api/src/attribution/attribution_queue_service.py:1-25]()

---

# Page: Development Guide

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [.vscode/launch.json](.vscode/launch.json)
- [api/.env](api/.env)
- [api/pyproject.toml](api/pyproject.toml)
- [docker-compose.yaml](docker-compose.yaml)
- [uv.lock](uv.lock)

</details>



This guide provides comprehensive instructions for developers working with the infinigram-api repository. It covers local development environment setup, development workflow, and deployment procedures. For system architecture overview, see [System Architecture](#2), and for API-specific details, see [API](#3).

## Local Development Setup

To get started with local development on the infinigram-api project, follow these steps to set up your development environment:

### Prerequisites

1. **Docker and Docker Compose** - Required to run the system locally
2. **Python 3.12+** - The project requires Python 3.12 or higher
3. **uv** - Recommended for dependency management
4. **Git** - For version control

### Setting Up Local Environment

The repository uses Docker Compose to manage all required services locally. This includes the API, attribution worker, PostgreSQL database, Redis cache, and other supporting services.

```mermaid
graph TD
    subgraph "Local Development Environment"
        Dev["Developer Machine"]
        Docker["Docker Engine"]
        DockerCompose["docker-compose.yaml"]
        
        subgraph "Containers"
            API["api"]
            Worker["attribution-worker"]
            Proxy["proxy (nginx)"]
            Queue["queue (postgres)"]
            Cache["cache (redis)"]
            OTEL["otelcol"]
        end
        
        subgraph "Volumes"
            V1["infinigram-array volumes"]
            Logs["logs"]
            PGData["pgdata"]
        end
    end
    
    Dev -->|"runs"| DockerCompose
    DockerCompose -->|"defines"| Docker
    Docker -->|"creates"| Containers
    Docker -->|"mounts"| V1
    Docker -->|"mounts"| Logs
    Docker -->|"mounts"| PGData
    
    API -->|"uses"| V1
    Worker -->|"uses"| V1
    API -->|"connects to"| Queue
    API -->|"connects to"| Cache
    Worker -->|"connects to"| Queue
    Proxy -->|"routes to"| API
```

Sources: [docker-compose.yaml:1-85]()

#### 1. Clone the Repository

```bash
git clone https://github.com/allenai/infinigram-api.git
cd infinigram-api
```

#### 2. Download the Infinigram Arrays

The system requires several Infinigram array files to function. These are large ML model files that need to be downloaded to the `infinigram-array` directory. The docker-compose file expects the following array directories:

- v4_pileval_llama
- olmoe-mix-0924-dclm
- olmoe-mix-0924-nodclm
- v4-olmoe-0125-1b-7b-anneal-adapt
- v4-olmo-2-1124-13b-anneal-adapt
- v4-olmo-2-0325-32b-anneal-adapt

Sources: [docker-compose.yaml:14-22](), [docker-compose.yaml:39-45]()

#### 3. Start the Services

With Docker Compose installed and the arrays downloaded, you can start all the required services:

```bash
docker-compose up
```

This command starts all services defined in the `docker-compose.yaml` file. The API will be available at http://localhost:8080.

### Configuration

The system uses environment variables for configuration. Key environment variables include:

| Environment Variable | Description | Default (Local Development) |
|---------------------|-------------|----------------------------|
| `LOG_LEVEL` | Logging level | DEBUG |
| `INDEX_BASE_PATH` | Path to Infinigram arrays | ../infinigram-array |
| `ATTRIBUTION_QUEUE_URL` | PostgreSQL connection URL | postgres://infini-gram:llmz@localhost:5432/infini-gram?sslmode=disable&application_name=infini-gram-attribution-worker |
| `PYTHON_ENV` | Environment (development, production) | development |
| `CACHE_URL` | Redis connection URL | redis://localhost:6379 |
| `VENDOR_BASE_PATH` | Path to vendor files | ../vendor |

Sources: [api/.env:1-6](), [docker-compose.yaml:1-5](), [docker-compose.yaml:23-27](), [docker-compose.yaml:46]()

### Running the API Service Directly (for Development)

For faster development cycles, you can run the API service directly using uvicorn:

```bash
cd api
uvicorn app:app --reload
```

VS Code users can use the provided debugger configuration:

```mermaid
graph TD
    subgraph "VS Code Debug Configuration"
        Launch["launch.json"]
        Module["uvicorn module"]
        App["app:app"]
        Reload["--reload flag"]
    end
    
    Launch -->|"runs"| Module
    Module -->|"loads"| App
    Module -->|"with"| Reload
```

Sources: [.vscode/launch.json:1-20]()

## Project Structure

The infinigram-api project is organized into several key components:

```mermaid
graph TD
    subgraph "Repository Structure"
        API["api/"]
        Worker["attribution_worker/"]
        Proxy["proxy/"]
        Docker["docker-compose.yaml"]
        Schema["schema/"]
        OTEL["otel-collector/"]
    end
    
    subgraph "API Components"
        App["app.py"]
        Config["config.py"]
        Health["health.py"]
        
        InfinigramModule["infinigram/"]
        AttributionModule["attribution/"]
        DocumentsModule["documents/"]
        CacheModule["cache/"]
    end
    
    subgraph "Worker Components"
        WorkerPy["worker.py"]
        WorkerConfig["config.py"]
    end
    
    subgraph "Shared Dependencies"
        InfinigramProcessor["infini-gram-processor"]
    end
    
    API --> App
    API --> Config
    API --> Health
    API --> InfinigramModule
    API --> AttributionModule
    API --> DocumentsModule
    API --> CacheModule
    
    Worker --> WorkerPy
    Worker --> WorkerConfig
    
    AttributionModule --> InfinigramProcessor
    DocumentsModule --> InfinigramProcessor
    WorkerPy --> InfinigramProcessor
```

Sources: [docker-compose.yaml:7-82](), [api/pyproject.toml:1-25]()

### Key Components and Their Roles

1. **API Service** (api/): FastAPI application that handles incoming HTTP requests
2. **Attribution Worker** (attribution_worker/): Background worker that processes attribution jobs
3. **Proxy** (proxy/): NGINX proxy that routes requests to the API
4. **Queue** (PostgreSQL): Stores attribution jobs for the worker to process
5. **Cache** (Redis): Caches attribution results for faster retrieval
6. **Infinigram Arrays**: ML models used for processing requests

## Development Workflow

### Making Changes

1. **API Changes**: Modify the appropriate files in the `api/` directory
2. **Worker Changes**: Modify the appropriate files in the `attribution_worker/` directory
3. **Proxy Changes**: Modify the configuration in the `proxy/` directory

### Testing Changes

For testing your changes, you can use the following approaches:

1. **Local Testing**: Run the services using Docker Compose and test via HTTP requests
2. **API Testing**: Run the API service directly using uvicorn for faster iteration
3. **Integration Testing**: Test the full system by running all services with Docker Compose

## Deploying to Kubernetes

The infinigram-api system is designed to be deployed to Kubernetes. The deployment architecture looks like this:

```mermaid
graph TD
    subgraph "Kubernetes Deployment"
        Ingress["Ingresses (3 TLDs)"]
        Service["Service (proxy)"]
        ApiDeploy["API Deployment"]
        WorkerDeploy["Attribution Worker Deployment"]
        PDB["PodDisruptionBudget"]
        
        subgraph "Persistent Volumes"
            PV1["infinigram-pileval-gpt2"]
            PV2["infinigram-olmoe-mix-0924"]
            PV3["infinigram-olmoe-mix-0924-nodclm"]
            PV4["infinigram-v4-olmoe-0125-1b-7b-anneal-adapt"]
            PV5["infinigram-v4-olmo-2-1124-13b-anneal-adapt"]
            PV6["infinigram-v4-olmo-2-0325-32b-anneal-adapt"]
        end
        
        subgraph "External Services"
            Redis["Redis Cache"]
            Postgres["PostgreSQL Queue"]
            OTLP["OpenTelemetry Collector"]
        end
    end
    
    Ingress --> Service
    Service --> ApiDeploy
    PDB --> ApiDeploy
    PDB --> WorkerDeploy
    
    ApiDeploy --> PV1
    ApiDeploy --> PV2
    ApiDeploy --> PV3
    ApiDeploy --> PV4
    ApiDeploy --> PV5
    ApiDeploy --> PV6
    
    WorkerDeploy --> PV1
    WorkerDeploy --> PV2
    WorkerDeploy --> PV3
    WorkerDeploy --> PV4
    WorkerDeploy --> PV5
    WorkerDeploy --> PV6
    
    ApiDeploy --> Redis
    ApiDeploy --> Postgres
    ApiDeploy --> OTLP
    
    WorkerDeploy --> Redis
    WorkerDeploy --> Postgres
    WorkerDeploy --> OTLP
```

Sources: This diagram is based on understanding the system architecture from [docker-compose.yaml:1-85]() and extrapolating to a Kubernetes environment.

### Deployment Configuration

To deploy the system to Kubernetes, you need to configure:

1. **Environment Variables**: Configure the appropriate environment variables for the deployment environment
2. **Persistent Volumes**: Ensure the necessary persistent volumes are available for the Infinigram arrays
3. **External Services**: Configure connections to Redis, PostgreSQL, and OpenTelemetry

## Adding New Infinigram Indices

To add a new Infinigram index (array) to the system:

### 1. Place the New Array File

Add the new array file to the appropriate location:

- For local development: Place in `./infinigram-array/` directory
- For Kubernetes: Create a new persistent volume for the array

### 2. Update Docker Compose Configuration

If adding for local development, update the `docker-compose.yaml` file to include the new volume:

```yaml
volumes:
  - ./infinigram-array/new-array-name:/mnt/infinigram-array/new-array-name
```

Update both the API and attribution worker services.

Sources: [docker-compose.yaml:14-22](), [docker-compose.yaml:39-45]()

### 3. Update Kubernetes Configuration

For Kubernetes deployment, update the persistent volume claims to include the new array.

### 4. Verify the Addition

After adding the new index:

1. Restart the system
2. Verify the new index appears in the available indices list
3. Test queries against the new index

## Troubleshooting

### Common Issues

1. **Missing Infinigram Arrays**: Ensure all required array files are downloaded and in the correct locations
2. **Connection Issues**: Check that PostgreSQL and Redis are running and accessible
3. **Permission Problems**: Ensure proper file permissions for the infinigram-array directories

### Logging

The system uses Python's logging system with the level configurable via the `LOG_LEVEL` environment variable. For debugging, set it to `DEBUG`:

```
LOG_LEVEL=DEBUG
```

Sources: [api/.env:1](), [docker-compose.yaml:24]()

### Accessing Services

| Service | Local URL | Description |
|---------|-----------|-------------|
| API | http://localhost:8080 | The main API endpoint |
| Attribution Worker | http://localhost:8081 | Worker status endpoint |
| PostgreSQL | localhost:5432 | Queue database |
| Redis | localhost:6379 | Cache service |

Sources: [docker-compose.yaml:31-32](), [docker-compose.yaml:49-51](), [docker-compose.yaml:69-71](), [docker-compose.yaml:79-81]()

## Conclusion

This development guide provides the essential information for working with the infinigram-api repository. For more detailed information about specific components, refer to the other sections of the wiki, such as [API](#3), [Attribution Worker](#4), or [Infrastructure](#6).

---

# Page: Local Development

# Local Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [.vscode/launch.json](.vscode/launch.json)
- [api/.env](api/.env)
- [bin/download-infini-gram-array.sh](bin/download-infini-gram-array.sh)
- [docker-compose.yaml](docker-compose.yaml)

</details>



This page provides a comprehensive guide to setting up and running the Infinigram API system in a local development environment. This documentation focuses on the local development workflow using Docker Compose to create a fully functional development environment with all necessary components.

For information about deploying to Kubernetes, see [Kubernetes Deployment](#5.2). For adding new indices to the system, refer to [Adding New Indices](#5.3).

## System Overview

The Infinigram API local development environment consists of several interconnected services managed through Docker Compose:

```mermaid
graph TD
    subgraph "Docker Compose Environment"
        subgraph "Core Services"
            API["api (FastAPI)"]
            Worker["attribution-worker"]
            Proxy["proxy (NGINX)"]
        end
        
        subgraph "Supporting Services"
            Queue["queue (PostgreSQL)"]
            Cache["cache (Redis)"]
            OTEL["otelcol (OpenTelemetry)"]
        end
        
        subgraph "Volumes"
            Arrays["infinigram-array volumes"]
            PGData["pgdata volume"]
            Logs["logs volume"]
        end
        
        Client["Developer Browser/API Client"]
        Client -- "HTTP requests<br>(port 8080)" --> Proxy
        Proxy --> API
        
        API --> Queue
        API --> Cache
        API --> OTEL
        API --> Arrays
        
        Worker --> Queue
        Worker --> Cache
        Worker --> OTEL
        Worker --> Arrays
        
        Queue --> PGData
    end
```

Sources: [docker-compose.yaml:7-82]()

## Prerequisites

Before setting up the local development environment, ensure you have:

1. **Docker and Docker Compose** installed on your machine
2. Git for accessing the repository
3. At least 10GB free disk space (for Infinigram arrays)
4. AWS CLI configured (for downloading model arrays)

## Setting Up the Local Environment

### Step 1: Clone the Repository

```bash
git clone https://github.com/allenai/infinigram-api.git
cd infinigram-api
```

### Step 2: Download Infinigram Arrays

The system requires several model arrays to function properly. Use the provided script to download them:

```bash
./bin/download-infini-gram-array.sh
```

This script will:
1. Create the `infinigram-array` directory
2. Download the `v4_pileval_llama` array from S3
3. Create symbolic links for the other required arrays to save disk space

Sources: [bin/download-infini-gram-array.sh:1-36]()

### Step 3: Environment Configuration

The default configuration in the repository should work for most development needs. The key configuration files are:

1. **Docker Compose configuration**: [docker-compose.yaml]() - Defines all services
2. **API environment variables**: [api/.env]() - Default configuration for local API service
3. **Shared environment variables**: Defined in `docker-compose.yaml` as `x-shared-env`

**Important Environment Variables:**

| Variable | Description | Default Value |
|----------|-------------|---------------|
| INDEX_BASE_PATH | Path to Infinigram arrays | /mnt/infinigram-array |
| ATTRIBUTION_QUEUE_URL | PostgreSQL connection URL | postgres://infini-gram:llmz@queue:5432/infini-gram?sslmode=disable&application_name=infini-gram-attribution-worker |
| PYTHON_ENV | Environment name | development |
| LOG_LEVEL | Logging verbosity | DEBUG |
| CACHE_URL | Redis connection URL | redis://cache:6379 |
| OTEL_EXPORTER_OTLP_ENDPOINT | OpenTelemetry endpoint | http://otelcol:4318 |

Sources: [docker-compose.yaml:1-6](), [docker-compose.yaml:23-27](), [api/.env:1-6]()

## Running the System

### Starting the Environment

To start all services defined in the Docker Compose configuration:

```bash
docker-compose up
```

This command will:
1. Build Docker images for the API and attribution worker
2. Start all services (API, worker, proxy, queue, cache, OpenTelemetry collector)
3. Mount the appropriate volumes for code and data

To run in detached mode (background):

```bash
docker-compose up -d
```

### Service Architecture in Development Mode

```mermaid
graph TD
    subgraph "Code Volumes"
        APICode["./api"]
        WorkerCode["./attribution_worker"]
    end
    
    subgraph "Data Volumes"
        Array1["./infinigram-array/v4_pileval_llama"]
        Array2["./infinigram-array/olmoe-mix-0924-dclm"]
        Array3["./infinigram-array/olmoe-mix-0924-nodclm"]
        Array4["./infinigram-array/v4-olmoe-0125-1b-7b-anneal-adapt"]
        Array5["./infinigram-array/v4-olmo-2-1124-13b-anneal-adapt"]
        Array6["./infinigram-array/v4-olmo-2-0325-32b-anneal-adapt"]
    end
    
    subgraph "Docker Services"
        API["api container"]
        Worker["attribution-worker container"]
        Proxy["proxy container"]
        Queue["queue container"]
        Cache["cache container"]
        OTEL["otelcol container"]
    end
    
    APICode --> API
    WorkerCode --> Worker
    
    Array1 --> API
    Array2 --> API
    Array3 --> API
    Array4 --> API
    Array5 --> API
    Array6 --> API
    
    Array1 --> Worker
    Array2 --> Worker
    Array3 --> Worker
    Array4 --> Worker
    Array5 --> Worker
    Array6 --> Worker
    
    Client["Client (browser/curl)"] -- "Port 8080" --> Proxy
    Proxy --> API
    API <--> Worker
    API --> Queue
    API --> Cache
    Worker --> Queue
    Worker --> Cache
    
    API -- "Telemetry" --> OTEL
    Worker -- "Telemetry" --> OTEL
```

Sources: [docker-compose.yaml:8-46]()

### Accessing the Services

Once all services are running:

| Service | URL | Description |
|---------|-----|-------------|
| API | http://localhost:8080 | Main API endpoint |
| API Documentation | http://localhost:8080/docs | Swagger/OpenAPI documentation |
| Attribution Worker | http://localhost:8081:8080 | Worker service (if needed for debugging) |

Sources: [docker-compose.yaml:30-32](), [docker-compose.yaml:49-53]()

### Monitoring and Logs

To view logs for all services:

```bash
docker-compose logs -f
```

To view logs for a specific service:

```bash
docker-compose logs -f api
```

### Stopping the Environment

To stop all services:

```bash
docker-compose down
```

To stop and remove volumes:

```bash
docker-compose down -v
```

## Development Workflow

The local development environment is configured for active development, with automatic code reloading and volume mapping.

### Code Structure

```
infinigram-api/
├── api/                  # API service code
├── attribution_worker/   # Attribution worker code
├── bin/                  # Utility scripts
├── infinigram-array/     # Downloaded model arrays
├── proxy/                # NGINX proxy configuration
├── schema/               # Database schema
└── otel-collector/       # OpenTelemetry configuration
```

### Code Hot-Reloading

Both the API and attribution worker services are configured with volume mounts that map the local code directories to the containers:

- API: `./api:/app/api`
- Worker: `./attribution_worker:/app/attribution_worker`

This allows you to make changes to the code on your local machine, and the changes will be immediately reflected in the running containers.

Sources: [docker-compose.yaml:14-15](), [docker-compose.yaml:37-38]()

### Debugging with VS Code

A VS Code launch configuration is provided for debugging the FastAPI application:

1. Open the project in VS Code
2. Set breakpoints in your code
3. Use the "Python Debugger: FastAPI" configuration to start debugging

Sources: [.vscode/launch.json:1-20]()

## Development Workflow Sequence

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Local as "Local Files"
    participant Docker as "Docker Compose"
    participant API as "API Container"
    participant Worker as "Worker Container"
    participant Browser as "Web Browser"
    
    Dev->>Local: Edit code in ./api or ./attribution_worker
    Dev->>Docker: docker-compose up
    Docker->>API: Start API with volume mounts
    Docker->>Worker: Start worker with volume mounts
    
    Note over Local,API: Code changes are automatically synced
    
    Dev->>Browser: Access API at localhost:8080
    Browser->>API: Send HTTP request
    API->>Worker: Process attribution (if needed)
    API->>Browser: Return response
    
    Dev->>Local: Make more code changes
    Note over Local,API: Changes reflected immediately
    
    Dev->>Docker: View logs with docker-compose logs
    Docker->>Dev: Stream container logs
    
    Dev->>Docker: docker-compose down when finished
```

## Common Issues and Troubleshooting

### Issue: Failed to Start Services

**Problem**: Docker Compose fails to start services with port conflicts.

**Solution**: Check if any of the required ports (8080, 8081, 5432, 6379) are already in use by other applications. Either stop those applications or modify the port mappings in `docker-compose.yaml`.

### Issue: Missing Infinigram Arrays

**Problem**: Service fails due to missing Infinigram arrays.

**Solution**: Run the download script again or check that the symbolic links were created correctly:

```bash
./bin/download-infini-gram-array.sh
```

### Issue: Attribution Worker Not Processing Jobs

**Problem**: Attribution jobs are queued but not being processed.

**Solution**: 
1. Check the worker logs: `docker-compose logs attribution-worker`
2. Verify the PostgreSQL queue is properly initialized with the schema files in `./schema`
3. Ensure the `ATTRIBUTION_QUEUE_URL` environment variable is correctly set

Sources: [docker-compose.yaml:67-76](), [docker-compose.yaml:29-46]()

### Issue: Changes Not Reflected in Running Containers

**Problem**: Code changes aren't being detected or reflected in the running services.

**Solution**: 
1. Verify the volume mounts in `docker-compose.yaml`
2. Restart the services: `docker-compose restart api attribution-worker`
3. Check if any `.dockerignore` rules might be preventing file syncing

Sources: [.dockerignore:1-11]()

---

# Page: Kubernetes Deployment

# Kubernetes Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.skiff/webapp.jsonnet](.skiff/webapp.jsonnet)

</details>



This document details how the Infinigram API system is deployed to Kubernetes using Skiff, an internal Allen AI deployment platform. It covers the Kubernetes resources, deployment configurations, and infrastructure components required for running the system in production and staging environments. For local development setup, see [Local Development](#5.1).

## Overview

The Infinigram API system is deployed to Kubernetes as a set of interrelated resources within a dedicated namespace. The deployment consists of two main components:

1. **API Deployment** - Runs the FastAPI application with an NGINX proxy
2. **Attribution Worker Deployment** - Processes asynchronous attribution jobs

Both components share access to the same set of persistent volumes containing Infinigram arrays (ML models) needed for processing requests.

```mermaid
flowchart TB
    subgraph "Kubernetes Cluster"
        subgraph "infinigram-api Namespace"
            direction LR
            
            subgraph "Ingress"
                ing1["Primary Ingress<br/>(.allenai.org)"]
                ing2["Secondary Ingress<br/>(.allen.ai)"]
                ing3["Tertiary Ingress<br/>(.semanticscholar.org)"]
            end
            
            subgraph "API"
                svc["Service (proxy)"]
                api["API Deployment"]
                pdb["PodDisruptionBudget"]
            end
            
            worker["Attribution Worker<br/>Deployment"]
            
            subgraph "PersistentVolumes"
                pv1["infinigram-pileval-gpt2"]
                pv2["infinigram-olmoe-mix-0924"]
                pv3["infinigram-olmoe-mix-0924-nodclm"]
                pv4["infinigram-v4-olmoe-0125-1b-7b-anneal-adapt"]
                pv5["infinigram-v4-olmo-2-1124-13b-anneal-adapt"]
                pv6["infinigram-v4-olmo-2-0325-32b-anneal-adapt"]
            end
            
            ing1 --> svc
            ing2 --> svc
            ing3 --> svc
            svc --> api
            
            api --> pv1 & pv2 & pv3 & pv4 & pv5 & pv6
            worker --> pv1 & pv2 & pv3 & pv4 & pv5 & pv6
        end
        
        extRedis["Redis Cache"]
        extQueue["PostgreSQL Queue"]
        extOtlp["OpenTelemetry Collector"]
        
        api --> extRedis
        api --> extQueue
        api --> extOtlp
        worker --> extQueue
        worker --> extRedis
        worker --> extOtlp
    end
```

Sources: [.skiff/webapp.jsonnet:17-44](), [.skiff/webapp.jsonnet:702-715]()

## Deployment Components

The Kubernetes deployment consists of the following resources:

1. **Namespace** - A dedicated namespace for all Infinigram API resources
2. **Ingresses** - Three ingress resources for different TLDs
3. **Service** - Exposes the NGINX proxy to the ingresses
4. **Deployments** - Two deployments: API and Attribution Worker
5. **PodDisruptionBudget** - Ensures availability during cluster maintenance
6. **PersistentVolumeClaims** - Used to mount Infinigram arrays (ML models)

```mermaid
flowchart TB
    subgraph "Kubernetes Resources"
        direction TB
        
        ns["Namespace<br/>(infinigram-api)"]
        
        subgraph "API Resources"
            ing["Ingresses"]
            svc["Service<br/>(infinigram-api-{env})"]
            deploy["Deployment<br/>(infinigram-api-{env})"]
            pdb["PodDisruptionBudget"]
        end
        
        subgraph "Worker Resources"
            workerDeploy["Deployment<br/>(infinigram-api-{env}-attribution-worker)"]
        end
        
        subgraph "Shared Resources"
            pvcs["PersistentVolumeClaims<br/>(Infinigram Arrays)"]
        end
        
        ns --> ing & svc & deploy & pdb & workerDeploy
        deploy --> pvcs
        workerDeploy --> pvcs
    end
```

Sources: [.skiff/webapp.jsonnet:145-152](), [.skiff/webapp.jsonnet:160-235](), [.skiff/webapp.jsonnet:372-524](), [.skiff/webapp.jsonnet:526-544](), [.skiff/webapp.jsonnet:546-560](), [.skiff/webapp.jsonnet:576-700]()

## API Deployment

The API deployment runs two containers:

1. **API Container** - The FastAPI application that handles API requests
2. **Proxy Container** - An NGINX proxy that sits in front of the API

The deployment is configured with:

- Anti-affinity rules to ensure high availability
- Resource requests for CPU and memory
- Readiness probes to ensure healthy operation
- Volume mounts for Infinigram arrays

```mermaid
flowchart TB
    subgraph "API Deployment"
        direction TB
        
        subgraph "Pod"
            api["API Container<br/>(FastAPI App)"]
            proxy["Proxy Container<br/>(NGINX)"]
            
            api <--> proxy
        end
        
        subgraph "Configuration"
            res["Resources<br/>CPU: 63<br/>Memory: 257G"]
            probe["Readiness Probe<br/>/health?check=rdy"]
            env["Environment Variables"]
        end
        
        subgraph "Volumes"
            vol1["infinigram-array-pileval-gpt2"]
            vol2["infinigram-array-olmoe-mix-0924-dclm"]
            vol3["infinigram-array-olmoe-mix-0924-nodclm"]
            vol4["infinigram-array-v4-olmoe-0125-1b-7b-anneal-adapt"]
            vol5["infinigram-array-v4-olmo-2-1124-13b-anneal-adapt"]
            vol6["infinigram-array-v4-olmo-2-0325-32b-anneal-adapt"]
        end
        
        api --> res
        api --> probe
        api --> env
        api --> vol1 & vol2 & vol3 & vol4 & vol5 & vol6
    end
```

Sources: [.skiff/webapp.jsonnet:372-524]()

## Attribution Worker Deployment

The Attribution Worker deployment runs a single container that processes attribution jobs from the queue. It has similar configuration to the API deployment:

- Anti-affinity rules for high availability
- Resource requests for CPU and memory
- Readiness probe
- The same volume mounts as the API deployment

```mermaid
flowchart TB
    subgraph "Attribution Worker Deployment"
        direction TB
        
        subgraph "Pod"
            worker["Attribution Worker Container"]
        end
        
        subgraph "Configuration"
            res["Resources<br/>CPU: 63<br/>Memory: 257G"]
            probe["Readiness Probe<br/>/"]
            env["Environment Variables"]
        end
        
        subgraph "Volumes"
            vol1["infinigram-array-pileval-gpt2"]
            vol2["infinigram-array-olmoe-mix-0924-dclm"]
            vol3["infinigram-array-olmoe-mix-0924-nodclm"]
            vol4["infinigram-array-v4-olmoe-0125-1b-7b-anneal-adapt"]
            vol5["infinigram-array-v4-olmo-2-1124-13b-anneal-adapt"]
            vol6["infinigram-array-v4-olmo-2-0325-32b-anneal-adapt"]
        end
        
        worker --> res
        worker --> probe
        worker --> env
        worker --> vol1 & vol2 & vol3 & vol4 & vol5 & vol6
    end
```

Sources: [.skiff/webapp.jsonnet:576-700]()

## Ingress Configuration

The deployment includes up to three ingress resources for different top-level domains:

1. **Primary Ingress** (.allenai.org) - The main ingress for the application
2. **Allen.ai Ingress** (.allen.ai) - Secondary ingress with the same configuration
3. **Semantic Scholar Ingress** (.semanticscholar.org) - Optional tertiary ingress

All ingresses are configured with TLS, rate limiting, authentication, and other security features.

| Ingress | TLD | Rate Limit | Auth |
|---------|-----|------------|------|
| Primary | .allenai.org | 5 rps | Yes |
| Allen.ai | .allen.ai | 5 rps | Yes |
| Scholar | .semanticscholar.org | 5 rps | Yes |

Sources: [.skiff/webapp.jsonnet:160-196](), [.skiff/webapp.jsonnet:198-235](), [.skiff/webapp.jsonnet:237-274]()

## Persistent Volumes

The system uses six persistent volume claims to mount Infinigram arrays (ML models):

| PVC Name | Mount Path | Purpose |
|----------|------------|---------|
| infinigram-pileval-gpt2 | /mnt/infinigram-array/v4_pileval_llama | GPT-2 model arrays |
| infinigram-olmoe-mix-0924 | /mnt/infinigram-array/olmoe-mix-0924-dclm | OLMoE mix model arrays (DCLM) |
| infinigram-olmoe-mix-0924-nodclm | /mnt/infinigram-array/olmoe-mix-0924-nodclm | OLMoE mix model arrays (no DCLM) |
| infinigram-v4-olmoe-0125-1b-7b-anneal-adapt | /mnt/infinigram-array/v4-olmoe-0125-1b-7b-anneal-adapt | OLMoE 1B-7B model arrays |
| infinigram-v4-olmo-2-1124-13b-anneal-adapt | /mnt/infinigram-array/v4-olmo-2-1124-13b-anneal-adapt | OLMo 2 13B model arrays |
| infinigram-v4-olmo-2-0325-32b-anneal-adapt | /mnt/infinigram-array/v4-olmo-2-0325-32b-anneal-adapt | OLMo 2 32B model arrays |

Sources: [.skiff/webapp.jsonnet:293-337](), [.skiff/webapp.jsonnet:339-370]()

## Environment Configuration

The system is configured using environment variables. Some key environment variables include:

| Variable | Purpose | Source |
|----------|---------|--------|
| PYTHON_ENV | Current environment (staging/prod) | Set during deployment |
| ATTRIBUTION_QUEUE_URL | URL for the attribution job queue | Secret |
| CACHE_URL | URL for the Redis cache | Secret |
| OTEL_SERVICE_NAME | Service name for OpenTelemetry | Set during deployment |
| LOG_FORMAT | Format for logging (google:json) | Set during deployment |

Sources: [.skiff/webapp.jsonnet:277-291](), [.skiff/webapp.jsonnet:485-502](), [.skiff/webapp.jsonnet:689-694]()

## Resource Requirements

Both the API and Attribution Worker deployments have significant resource requirements:

| Component | CPU | Memory | Node Pool |
|-----------|-----|--------|-----------|
| API | 63 | 257G | cpu64-256g |
| Attribution Worker | 63 | 257G | cpu64-256g |
| Proxy | 0.1 | 100M | cpu64-256g |

This indicates that the application requires large CPU and memory resources due to the nature of the ML models it's working with.

Sources: [.skiff/webapp.jsonnet:477-484](), [.skiff/webapp.jsonnet:513-518](), [.skiff/webapp.jsonnet:682-687]()

## High Availability Configuration

The system is configured for high availability in production:

1. **Multiple Replicas** - In production, both the API and Attribution Worker are deployed with multiple replicas (configured in skiff.json)
2. **Pod Anti-Affinity** - Ensures pods are scheduled on different nodes
3. **PodDisruptionBudget** - Ensures at least one pod remains available during voluntary disruptions

```mermaid
flowchart TB
    subgraph "High Availability"
        direction TB
        
        subgraph "Production Environment"
            apiReplicas["API Replicas<br/>(config.replicas.prod)"]
            workerReplicas["Worker Replicas<br/>(config.attributionWorkerReplicas.prod)"]
        end
        
        subgraph "HA Configuration"
            antiAffinity["Pod Anti-Affinity<br/>(Different Nodes)"]
            pdb["PodDisruptionBudget<br/>(minAvailable: 1)"]
        end
        
        apiReplicas --> antiAffinity
        apiReplicas --> pdb
        workerReplicas --> antiAffinity
    end
```

Sources: [.skiff/webapp.jsonnet:52](), [.skiff/webapp.jsonnet:407-424](), [.skiff/webapp.jsonnet:546-560](), [.skiff/webapp.jsonnet:562]()

## Deployment Process

The Infinigram API is deployed to Kubernetes using Skiff, which uses the Jsonnet template to generate the Kubernetes manifests. The deployment process involves:

1. Building container images for API, Proxy, and Attribution Worker
2. Applying the generated Kubernetes manifests to the cluster
3. Rollout of new deployments with rolling updates

The template takes several parameters:

| Parameter | Description |
|-----------|-------------|
| apiImage | Docker image for the API container |
| proxyImage | Docker image for the NGINX proxy container |
| workerImage | Docker image for the Attribution Worker container |
| cause | Deployment cause for annotation |
| sha | Git SHA of the deployed code |
| env | Deployment environment (staging/prod) |
| branch | Git branch being deployed |
| repo | Git repository name |
| buildId | Build identifier |

Sources: [.skiff/webapp.jsonnet:14-17]()

## Conclusion

The Kubernetes deployment of the Infinigram API system is designed to be scalable, highly available, and resource-efficient. It leverages Kubernetes features such as rolling updates, resource requests, probes, and PodDisruptionBudgets to ensure reliable operation. The deployment is configured to handle the specific requirements of the Infinigram API, including large ML models mounted as persistent volumes and significant CPU and memory resources.

For adding new Infinigram indices to the system, see [Adding New Indices](#5.3). For information about observability and monitoring, see [Observability](#6.2).

---

# Page: Adding New Indices

# Adding New Indices

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [bin/download-infini-gram-array.sh](bin/download-infini-gram-array.sh)
- [indexing/indexing_olmo2-13b-anneal-adapt.sh](indexing/indexing_olmo2-13b-anneal-adapt.sh)
- [indexing/indexing_olmo2-32b-anneal-adapt.sh](indexing/indexing_olmo2-32b-anneal-adapt.sh)
- [indexing/indexing_olmoe-1b-7b-anneal-adapt.sh](indexing/indexing_olmoe-1b-7b-anneal-adapt.sh)
- [indexing/transform_hf_to_raw.py](indexing/transform_hf_to_raw.py)
- [indexing/transform_hf_to_raw_olmo2.py](indexing/transform_hf_to_raw_olmo2.py)
- [volume-claims/pileval-gpt2.yaml](volume-claims/pileval-gpt2.yaml)

</details>



This guide explains the process of adding new infinigram indices to the infinigram-api system. It covers the full workflow from preparing data to deploying the indices in both local development and production environments.

For information about using existing indices in the API, see [Infinigram Service](#3.4).

## Overview of the Indexing Process

Adding a new index to the infinigram-api system involves several distinct steps:

1. Preparing the source data
2. Running the indexing process
3. Making the index available in the development environment
4. Deploying the index to production

```mermaid
flowchart TD
    A["Raw Data Sources"]
    B["Data Transformation"]
    C["Indexing Process"]
    D["Local Development"]
    E["Kubernetes Deployment"]
    
    A -->|"transform_hf_to_raw.py"| B
    B -->|"indexing_*.sh"| C
    C -->|"S3 Storage"| D
    C -->|"Persistent Volumes"| E
    
    subgraph "Data Preparation"
        A
        B
    end
    
    subgraph "Index Creation"
        C
    end
    
    subgraph "Deployment"
        D
        E
    end
```

Sources: [indexing/transform_hf_to_raw.py](), [indexing/indexing_olmo2-32b-anneal-adapt.sh](), [bin/download-infini-gram-array.sh](), [volume-claims/pileval-gpt2.yaml]()

## Preparing Data for Indexing

### Data Format Requirements

The infinigram indexing process expects data in a specific JSON Lines format, with each line containing a JSON object with at least a `text` field. The source data is typically stored in Hugging Face datasets and needs to be transformed.

```mermaid
flowchart LR
    A["Hugging Face Dataset"] -->|"transform_hf_to_raw.py"| B["Raw JSONL Files"]
    B -->|"Input to indexing process"| C["Infinigram Index"]
    
    subgraph "Source Data Structure"
        A
    end
    
    subgraph "Target Data Structure"
        B["Raw JSONL Files\n{text: string, source: string}"]
    end
```

Sources: [indexing/transform_hf_to_raw.py](), [indexing/transform_hf_to_raw_olmo2.py]()

### Transforming Hugging Face Datasets

The repository includes scripts for transforming Hugging Face datasets into the required format. These scripts handle different dataset structures:

1. **SFT (Supervised Fine-Tuning) datasets**: Messages are transformed into a conversation format
2. **DPO (Direct Preference Optimization) datasets**: Both chosen and rejected responses are included
3. **RLVR (Reinforcement Learning) datasets**: User messages are extracted

Example of the transformation process for SFT datasets:

```
HF Dataset Entry → {
  messages: [
    {role: "user", content: "..."},
    {role: "assistant", content: "..."}
  ]
}

Transformed Entry → {
  text: "<|user|>\n...<|assistant|>\n...",
  source: "dataset_name"
}
```

Sources: [indexing/transform_hf_to_raw.py:8-20](), [indexing/transform_hf_to_raw_olmo2.py:7-21]()

## Running the Indexing Process

The indexing process uses the `infini-gram` package to create index files from the prepared data. This is typically run on high-performance compute clusters using Gantry.

### Indexing Script Structure

```mermaid
flowchart TD
    A["Gantry Run Configuration"]
    B["Environment Setup"]
    C["Indexing Process"]
    D["S3 Sync"]
    
    A --> B
    B --> C
    C --> D
    
    subgraph "indexing_*.sh"
        A["Gantry Run\n- Computing Resources\n- Storage Access\n- Environment Variables"]
        B["Install dependencies\n- infini-gram\n- transformers\n- etc."]
        C["Run indexing.py with parameters\n- tokenizer type\n- data directory\n- output directory"]
        D["Upload index to S3"]
    end
```

Sources: [indexing/indexing_olmo2-32b-anneal-adapt.sh](), [indexing/indexing_olmoe-1b-7b-anneal-adapt.sh](), [indexing/indexing_olmo2-13b-anneal-adapt.sh]()

### Indexing Parameters

The indexing process accepts several key parameters:

| Parameter | Description | Example Value |
|-----------|-------------|---------------|
| `--tokenizer` | Tokenizer type to use | `llama` |
| `--cpus` | Number of CPU cores to use | `64` |
| `--mem` | Memory limit in GB | `900` |
| `--shards` | Number of shards to create | `1` |
| `--add_metadata` | Flag to add metadata to the index | `--add_metadata` |
| `--ulimit` | Maximum memory map size | `524288` |
| `--data_dir` | Input data directory | `/path/to/raw/data` |
| `--save_dir` | Output directory for the index | `/path/to/index` |

Sources: [indexing/indexing_olmo2-32b-anneal-adapt.sh:30-34](), [indexing/indexing_olmoe-1b-7b-anneal-adapt.sh:30-34]()

## Adding the Index to Local Development

For local development, the infinigram arrays are stored in the `infinigram-array` directory. The `download-infini-gram-array.sh` script is used to download the necessary files.

### Modifying the Download Script

To add a new index to the local development environment:

1. Add a new conditional block to `bin/download-infini-gram-array.sh`
2. Either download the index from S3 or create a symbolic link to an existing index

```mermaid
flowchart LR
    A["bin/download-infini-gram-array.sh"] -->|"Downloads or links"| B["infinigram-array/"]
    B -->|"Mounted in"| C["Docker Container"]
    
    subgraph "Local Development"
        A["Script downloads arrays\nor creates symbolic links"]
        B["Local directory structure:\n- infinigram-array/\n  - v4_pileval_llama/\n  - olmoe-mix-0924-dclm/\n  - etc."]
        C["Docker containers access\nindices via volume mounts"]
    end
```

Example of adding a new index (from the script):

```
if [ ! -d $INFINIGRAM_ARRAY_DIR/new_index_name ]; then
    echo "Downloading new_index_name array"
    aws s3 cp --no-sign-request --recursive s3://infini-gram/index/new_index_name $INFINIGRAM_ARRAY_DIR/new_index_name
fi
```

Sources: [bin/download-infini-gram-array.sh:8-10]()

### Updating Docker Compose

After modifying the download script, you also need to update the Docker Compose configuration to mount the new index volume. This ensures the API service can access the new index.

> Note: The comment in the download script reminds developers to add any new array to the `docker-compose.yaml` file as well.

Sources: [bin/download-infini-gram-array.sh:5]()

## Deploying the Index to Kubernetes

For production deployment, the indices are stored as persistent volumes in Kubernetes.

### Creating a Persistent Volume

To add a new index to the Kubernetes deployment:

1. Create a new PersistentVolume and PersistentVolumeClaim YAML file
2. Apply the configuration to the Kubernetes cluster

```mermaid
flowchart TD
    A["Define StorageClass"]
    B["Create PersistentVolume"]
    C["Create PersistentVolumeClaim"]
    D["Update Deployment to Mount Volume"]
    
    A --> B
    B --> C
    C --> D
    
    subgraph "Kubernetes Volume Setup"
        A["StorageClass: 'infinigram'"]
        B["PersistentVolume:\n- Name: infinigram-[index-name]\n- Storage: Size\n- AccessMode: ReadOnlyMany"]
        C["PersistentVolumeClaim:\n- Name: infinigram-[index-name]\n- Namespace: infinigram-api"]
        D["Deployment YAML:\n- volumeMounts\n- volumes"]
    end
```

Example structure based on existing volume claims:

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: infinigram-new-index-name
spec:
  storageClassName: "infinigram"
  capacity:
    storage: 10Gi  # Adjust size as needed
  accessModes:
    - ReadOnlyMany
  claimRef:
    namespace: infinigram-api
    name: infinigram-new-index-name
  csi:
    driver: pd.csi.storage.gke.io
    volumeHandle: projects/ai2-reviz/zones/us-west1-b/disks/infinigram-new-index
    fsType: ext4
    readOnly: true
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  namespace: infinigram-api
  name: infinigram-new-index-name
spec:
  storageClassName: "infinigram"
  volumeName: infinigram-new-index-name
  accessModes:
    - ReadOnlyMany
  resources:
    requests:
      storage: 10Gi  # Adjust size as needed
```

Sources: [volume-claims/pileval-gpt2.yaml]()

## Complete Workflow: From Data to Deployment

The complete workflow for adding a new index involves multiple steps across different environments:

```mermaid
flowchart TD
    A["Hugging Face Dataset"]
    B["Raw JSONL Files"]
    C["Indexing Process"]
    D["S3 Storage"]
    E["Local Development"]
    F["GCP Disk"]
    G["Kubernetes PV/PVC"]
    H["API Deployment"]
    
    A -->|"transform_hf_to_raw.py"| B
    B -->|"indexing_*.sh"| C
    C -->|"aws s3 sync"| D
    
    D -->|"download-infini-gram-array.sh"| E
    D -->|"Create disk from data"| F
    F -->|"volume-claims/*.yaml"| G
    G -->|"Mount volumes"| H
    
    E -->|"Local testing"| I["Verification"]
    H -->|"Production deployment"| I["Verification"]
    
    subgraph "Data Preparation"
        A
        B
    end
    
    subgraph "Index Creation"
        C
        D
    end
    
    subgraph "Local Environment"
        E
    end
    
    subgraph "Production Environment"
        F
        G
        H
    end
    
    subgraph "Testing"
        I
    end
```

Sources: [indexing/transform_hf_to_raw.py](), [indexing/indexing_olmo2-32b-anneal-adapt.sh](), [bin/download-infini-gram-array.sh](), [volume-claims/pileval-gpt2.yaml]()

## Summary

Adding a new index to the infinigram-api system requires several steps:

1. **Data Preparation**: Transform source data into the required format using the transformation scripts.
2. **Index Creation**: Run the indexing process using the `infini-gram` package and upload the results to S3.
3. **Local Development**: Update the download script and Docker Compose configuration to make the index available locally.
4. **Production Deployment**: Create persistent volumes in Kubernetes and update the deployment to mount these volumes.

Following this process ensures that new indices are properly integrated into both development and production environments, making them available for use by the infinigram-api system.

---

# Page: Infrastructure

# Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.skiff/webapp.jsonnet](.skiff/webapp.jsonnet)
- [docker-compose.yaml](docker-compose.yaml)

</details>



This page describes the infrastructure components that support the Infinigram API system. It covers the deployment architecture, storage systems, networking configurations, external services, and resource allocation for both production and development environments.

For information on how to deploy the system, see [Kubernetes Deployment](#5.2). For information on local development setup, see [Local Development](#5.1).

## Infrastructure Overview

The Infinigram API infrastructure is deployed on Kubernetes and consists of several key components:

- **API Service**: The main FastAPI application that handles client requests
- **Attribution Worker**: A separate service that processes attribution jobs asynchronously
- **Proxy**: An NGINX proxy that routes requests to the API service
- **Persistent Volumes**: Storage for the Infinigram arrays (ML models)
- **External Services**: Redis for caching and PostgreSQL for job queuing
- **Observability**: OpenTelemetry collector for monitoring and tracing

```mermaid
graph TB
    subgraph "Client Applications"
        Client["Client Requests"]
    end
    
    subgraph "Kubernetes Cluster"
        subgraph "infinigram-api Namespace"
            Ingress["Ingresses"]
            Service["Service (proxy)"]
            ApiDeployment["API Deployment"]
            WorkerDeployment["Attribution Worker Deployment"]
            
            subgraph "Storage"
                PVs["Infinigram Arrays (PVs)"]
            end
        end
        
        subgraph "External Services"
            Redis["Redis Cache"]
            PostgreSQL["PostgreSQL Queue"]
            OTLP["OpenTelemetry Collector"]
        end
    end
    
    Client --> Ingress
    Ingress --> Service
    Service --> ApiDeployment
    ApiDeployment --> PVs
    ApiDeployment --> Redis
    ApiDeployment --> PostgreSQL
    ApiDeployment --> OTLP
    
    WorkerDeployment --> PVs
    WorkerDeployment --> PostgreSQL
    WorkerDeployment --> Redis
    WorkerDeployment --> OTLP
```

Sources: [.skiff/webapp.jsonnet:1-716](), [docker-compose.yaml:1-85]()

## Kubernetes Deployment Architecture

The system is deployed to Kubernetes using Skiff, AI2's Kubernetes deployment tool. The main components of the deployment are:

1. **Namespace**: All resources are deployed to the `infinigram-api` namespace
2. **Ingresses**: Three ingress configurations to handle traffic from different domains (.allenai.org, .allen.ai, .semanticscholar.org)
3. **Service**: Routes traffic to the proxy container
4. **API Deployment**: Runs the FastAPI application and NGINX proxy in a pod
5. **Attribution Worker Deployment**: Runs the attribution worker in separate pods
6. **PodDisruptionBudget**: Ensures availability during cluster maintenance

```mermaid
graph TB
    subgraph "Kubernetes Resources"
        Namespace["infinigram-api Namespace"]
        
        subgraph "Ingresses"
            MainIngress["Main Ingress (.allenai.org)"]
            AllenAIIngress["Allen AI Ingress (.allen.ai)"]
            ScholarIngress["Scholar Ingress (.semanticscholar.org)"]
        end
        
        Service["Service (proxy)"]
        PDB["PodDisruptionBudget"]
        
        subgraph "API Deployment"
            APIPod1["API Pod 1"]
            APIPod2["API Pod 2 (prod only)"]
            
            subgraph "Pod Contents"
                APIContainer["API Container"]
                ProxyContainer["Proxy Container"]
            end
        end
        
        subgraph "Worker Deployment"
            WorkerPod1["Worker Pod 1"]
            WorkerPod2["Worker Pod 2 (prod only)"]
        end
    end
    
    Namespace --> MainIngress
    Namespace --> AllenAIIngress
    Namespace --> ScholarIngress
    Namespace --> Service
    Namespace --> PDB
    Namespace --> APIPod1
    Namespace --> APIPod2
    Namespace --> WorkerPod1
    Namespace --> WorkerPod2
    
    MainIngress --> Service
    AllenAIIngress --> Service
    ScholarIngress --> Service
    
    Service --> APIPod1
    Service --> APIPod2
    
    PDB --> APIPod1
    PDB --> APIPod2
    
    APIPod1 --> APIContainer
    APIPod1 --> ProxyContainer
    APIPod2 --> APIContainer
    APIPod2 --> ProxyContainer
```

Sources: [.skiff/webapp.jsonnet:144-715]()

### Resource Allocation

The system requires significant CPU and memory resources, especially for the API and worker components that process ML models:

| Component | CPU | Memory | GPU (if configured) | Node Pool |
|-----------|-----|--------|---------------------|-----------|
| API | 63 CPU cores | 257GB | Optional | cpu64-256g |
| Proxy | 0.1 CPU cores | 100MB | N/A | cpu64-256g |
| Attribution Worker | 63 CPU cores | 257GB | Optional | cpu64-256g |

Sources: [.skiff/webapp.jsonnet:474-483](), [.skiff/webapp.jsonnet:512-518](), [.skiff/webapp.jsonnet:682-688]()

### Scaling and Availability

The system uses the following configurations to ensure availability and proper scaling:

1. **Replicas**: In production, the number of API replicas is configured in `skiff.json` (typically 2 replicas). For all other environments, 1 replica is used.
2. **Pod Anti-Affinity**: Ensures that pods are scheduled on different nodes to avoid a single node failure affecting all instances.
3. **PodDisruptionBudget**: Ensures at least 1 replica remains available during voluntary disruptions in production.
4. **RollingUpdate Strategy**: Updates are performed with rolling strategy, ensuring zero downtime during deployments.

Sources: [.skiff/webapp.jsonnet:45-52](), [.skiff/webapp.jsonnet:383-389](), [.skiff/webapp.jsonnet:407-423](), [.skiff/webapp.jsonnet:545-560]()

## Storage Architecture

The Infinigram API relies on persistent volumes to store and access the ML models (infinigram arrays). These volumes are mounted to both the API and worker pods.

```mermaid
graph TB
    subgraph "Storage Architecture"
        subgraph "Persistent Volume Claims"
            pv1["infinigram-pileval-gpt2"]
            pv2["infinigram-olmoe-mix-0924"]
            pv3["infinigram-olmoe-mix-0924-nodclm"]
            pv4["infinigram-v4-olmoe-0125-1b-7b-anneal-adapt"]
            pv5["infinigram-v4-olmo-2-1124-13b-anneal-adapt"]
            pv6["infinigram-v4-olmo-2-0325-32b-anneal-adapt"]
        end
        
        subgraph "API Pod"
            api["API Container"]
        end
        
        subgraph "Worker Pod"
            worker["Worker Container"]
        end
        
        subgraph "Mount Paths"
            mp1["/mnt/infinigram-array/v4_pileval_llama"]
            mp2["/mnt/infinigram-array/olmoe-mix-0924-dclm"]
            mp3["/mnt/infinigram-array/olmoe-mix-0924-nodclm"]
            mp4["/mnt/infinigram-array/v4-olmoe-0125-1b-7b-anneal-adapt"]
            mp5["/mnt/infinigram-array/v4-olmo-2-1124-13b-anneal-adapt"]
            mp6["/mnt/infinigram-array/v4-olmo-2-0325-32b-anneal-adapt"]
        end
    end
    
    pv1 --> mp1
    pv2 --> mp2
    pv3 --> mp3
    pv4 --> mp4
    pv5 --> mp5
    pv6 --> mp6
    
    mp1 --> api
    mp2 --> api
    mp3 --> api
    mp4 --> api
    mp5 --> api
    mp6 --> api
    
    mp1 --> worker
    mp2 --> worker
    mp3 --> worker
    mp4 --> worker
    mp5 --> worker
    mp6 --> worker
```

Sources: [.skiff/webapp.jsonnet:293-370](), [docker-compose.yaml:16-22](), [docker-compose.yaml:39-45]()

### Infinigram Arrays

The system currently uses the following Infinigram arrays:

| Persistent Volume Claim | Mount Path | Description |
|-------------------------|------------|-------------|
| infinigram-pileval-gpt2 | /mnt/infinigram-array/v4_pileval_llama | Pileval GPT-2 model |
| infinigram-olmoe-mix-0924 | /mnt/infinigram-array/olmoe-mix-0924-dclm | OLMoE Mix 0924 with document-context language model |
| infinigram-olmoe-mix-0924-nodclm | /mnt/infinigram-array/olmoe-mix-0924-nodclm | OLMoE Mix 0924 without document-context language model |
| infinigram-v4-olmoe-0125-1b-7b-anneal-adapt | /mnt/infinigram-array/v4-olmoe-0125-1b-7b-anneal-adapt | OLMoE v4 1B-7B anneal adapt model |
| infinigram-v4-olmo-2-1124-13b-anneal-adapt | /mnt/infinigram-array/v4-olmo-2-1124-13b-anneal-adapt | OLMo 2 v4 13B anneal adapt model |
| infinigram-v4-olmo-2-0325-32b-anneal-adapt | /mnt/infinigram-array/v4-olmo-2-0325-32b-anneal-adapt | OLMo 2 v4 32B anneal adapt model |

Sources: [.skiff/webapp.jsonnet:293-336](), [docker-compose.yaml:16-22](), [docker-compose.yaml:39-45]()

## Networking

The application exposes services through multiple ingresses to support different domain names:

1. **Main Ingress**: Handles traffic for .allenai.org domains
2. **Allen AI Ingress**: Handles traffic for .allen.ai domains
3. **Scholar Ingress**: Handles traffic for .semanticscholar.org domains (if configured)

All ingresses route traffic to the service, which directs it to the proxy container running in the API pod. The proxy container then forwards requests to the API container.

```mermaid
graph LR
    subgraph "External Traffic"
        Internet["Client Requests"]
    end
    
    subgraph "Ingresses"
        Ingress1["Main Ingress (.allenai.org)"]
        Ingress2["Allen AI Ingress (.allen.ai)"]
        Ingress3["Scholar Ingress (.semanticscholar.org)"]
    end
    
    subgraph "Service"
        SVC["infinigram-api Service (port 8080)"]
    end
    
    subgraph "API Pod"
        Proxy["Proxy Container (port 8080)"]
        API["API Container (port 8000)"]
    end
    
    Internet --> Ingress1
    Internet --> Ingress2
    Internet --> Ingress3
    
    Ingress1 --> SVC
    Ingress2 --> SVC
    Ingress3 --> SVC
    
    SVC --> Proxy
    Proxy --> API
```

Sources: [.skiff/webapp.jsonnet:159-274](), [.skiff/webapp.jsonnet:526-544]()

### Network Policies

The ingresses are configured with several security and performance annotations:

- **Rate Limiting**: 5 requests per second with a burst multiplier of 1
- **SSL Redirect**: Forces HTTPS connections
- **Authentication**: Uses Skiff Login for authentication
- **Timeout**: 120-second proxy read timeout for long-running requests

Sources: [.skiff/webapp.jsonnet:154-157](), [.skiff/webapp.jsonnet:167-170]()

## External Services

The application integrates with several external services:

### Redis Cache

Used for caching attribution results to improve performance. Connected via the `CACHE_URL` environment variable.

Sources: [.skiff/webapp.jsonnet:494-502](), [docker-compose.yaml:26](), [docker-compose.yaml:78-81]()

### PostgreSQL Queue

Used for queuing attribution jobs for asynchronous processing by the worker. Connected via the `ATTRIBUTION_QUEUE_URL` environment variable.

Sources: [.skiff/webapp.jsonnet:283-290](), [docker-compose.yaml:4](), [docker-compose.yaml:67-76]()

### OpenTelemetry Collector

Used for distributed tracing, metrics collection, and logging. The API and worker services are instrumented with OpenTelemetry to send telemetry data to the collector.

```mermaid
graph TB
    subgraph "Observability Architecture"
        subgraph "Application Components"
            API["API Container"]
            Worker["Worker Container"]
        end
        
        subgraph "Telemetry Pipeline"
            OtelCollector["OpenTelemetry Collector"]
            CloudMonitoring["Cloud Monitoring"]
        end
    end
    
    API -- "OTEL_SERVICE_NAME=infinigram-api" --> OtelCollector
    Worker -- "OTEL_SERVICE_NAME=infinigram-api-worker" --> OtelCollector
    OtelCollector --> CloudMonitoring
```

Sources: [.skiff/webapp.jsonnet:486-489](), [.skiff/webapp.jsonnet:690-693](), [docker-compose.yaml:25](), [docker-compose.yaml:55-65]()

## Local Development Infrastructure

For local development, the infrastructure is defined in `docker-compose.yaml` and includes the same components as the production environment but configured for local use:

1. **API**: FastAPI application with volumes mounted for code and infinigram arrays
2. **Attribution Worker**: Worker service with volumes mounted
3. **Proxy**: NGINX proxy that routes requests to the API
4. **Queue**: PostgreSQL database for job queuing
5. **Cache**: Redis for caching
6. **OpenTelemetry Collector**: For monitoring and tracing

All these services are configured to run on the developer's machine using Docker Compose.

```mermaid
graph TB
    subgraph "Local Development Environment"
        subgraph "API Service"
            API["FastAPI App"]
            APIVolumes["Code & Infinigram Arrays"]
        end
        
        subgraph "Attribution Worker Service"
            Worker["Worker App"]
            WorkerVolumes["Code & Infinigram Arrays"]
        end
        
        Proxy["NGINX Proxy (Port 8080)"]
        Queue["PostgreSQL (Port 5432)"]
        Cache["Redis (Port 6379)"]
        OtelCollector["OpenTelemetry Collector"]
    end
    
    API --> APIVolumes
    Worker --> WorkerVolumes
    
    Proxy --> API
    API --> Queue
    API --> Cache
    API --> OtelCollector
    
    Worker --> Queue
    Worker --> Cache
    Worker --> OtelCollector
```

Sources: [docker-compose.yaml:1-85]()

### Environment Variables

The local development environment uses the following environment variables:

| Variable | Description | Value |
|----------|-------------|-------|
| PYTHONUNBUFFERED | Prevents Python from buffering stdout and stderr | 1 |
| INDEX_BASE_PATH | Base path for infinigram arrays | /mnt/infinigram-array |
| ATTRIBUTION_QUEUE_URL | Connection URL for the PostgreSQL queue | postgres://infini-gram:llmz@queue:5432/infini-gram?sslmode=disable&application_name=infini-gram-attribution-worker |
| PYTHON_ENV | Environment name | development |
| CACHE_URL | Connection URL for Redis cache | redis://cache:6379 |
| OTEL_EXPORTER_OTLP_ENDPOINT | Endpoint for OpenTelemetry collector | http://otelcol:4318 |

Sources: [docker-compose.yaml:1-27]()

---

# Page: Storage

# Storage

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [bin/download-infini-gram-array.sh](bin/download-infini-gram-array.sh)
- [volume-claims/pileval-gpt2.yaml](volume-claims/pileval-gpt2.yaml)

</details>



## Purpose and Scope

This document details the storage system used in the infinigram-api, focusing on how infinigram arrays (ML models) are stored, accessed, and managed both in local development environments and in Kubernetes deployments. The storage system is designed to provide efficient, read-only access to large model index files that power the attribution and document retrieval features of the API.

For information about observability components, see [Observability](#6.2).

## Infinigram Arrays Overview

Infinigram arrays are pre-computed index files that contain vector representations of text documents, enabling fast attribution and retrieval operations. These arrays form the core data assets of the infinigram-api system and are accessed by both the API service and the Attribution Worker.

```mermaid
graph TB
    subgraph "Infinigram Arrays Storage"
        Arrays["InfinigramArrays"]
        v4pileval["v4_pileval_llama<br>(Primary Array)"]
        olmoemix1["olmoe-mix-0924-dclm<br>(Symlink)"]
        olmoemix2["olmoe-mix-0924-nodclm<br>(Symlink)"]
        olmoe1b7b["v4-olmoe-0125-1b-7b-anneal-adapt<br>(Symlink)"]
        olmo13b["v4-olmo-2-1124-13b-anneal-adapt<br>(Symlink)"]
        olmo32b["v4-olmo-2-0325-32b-anneal-adapt<br>(Symlink)"]
        
        Arrays --> v4pileval
        v4pileval --- olmoemix1
        v4pileval --- olmoemix2
        v4pileval --- olmoe1b7b
        v4pileval --- olmo13b
        v4pileval --- olmo32b
    end
    
    subgraph "Services"
        API["API Service"]
        Worker["Attribution Worker"]
    end
    
    API --> Arrays
    Worker --> Arrays
```

**Diagram: Infinigram Arrays Structure and Service Access**

Sources: [bin/download-infini-gram-array.sh:1-37]()

## Storage Architecture

The storage architecture differs between development and production environments but maintains consistent access patterns through volume mounting.

```mermaid
graph TB
    subgraph "Production (Kubernetes)"
        k8s["Kubernetes Cluster"]
        pv["PersistentVolumes"]
        pvc["PersistentVolumeClaims"]
        sclass["StorageClass: infinigram"]
        
        k8s --> sclass
        sclass --> pv
        pv --> pvc
        
        subgraph "Persistent Volumes"
            pv1["infinigram-pileval-gpt2"]
            pv2["infinigram-olmoe-mix-0924"]
            pv3["infinigram-olmoe-mix-0924-nodclm"]
            pv4["infinigram-v4-olmoe-0125-1b-7b-anneal-adapt"]
            pv5["infinigram-v4-olmo-2-1124-13b-anneal-adapt"]
            pv6["infinigram-v4-olmo-2-0325-32b-anneal-adapt"]
        end
        
        pvc --> pv1
        pvc --> pv2
        pvc --> pv3
        pvc --> pv4
        pvc --> pv5
        pvc --> pv6
    end
    
    subgraph "Development"
        docker["Docker Compose"]
        volume["Local Volumes"]
        s3["S3 Bucket: infini-gram-lite"]
        script["download-infini-gram-array.sh"]
        
        docker --> volume
        s3 --> script
        script --> volume
    end
```

**Diagram: Storage Infrastructure in Production and Development Environments**

Sources: [volume-claims/pileval-gpt2.yaml:1-43](), [bin/download-infini-gram-array.sh:1-37]()

## Storage Implementation

### Kubernetes Storage Configuration

In the production environment, infinigram arrays are stored on Google Kubernetes Engine (GKE) persistent disks and mounted as read-only volumes to the API and worker pods. This configuration ensures data consistency and allows multiple pods to access the same data concurrently.

```mermaid
graph LR
    subgraph "Kubernetes Resources"
        sc["StorageClass<br>Name: infinigram<br>Provisioner: pd.csi.storage.gke.io"]
        pv["PersistentVolume<br>Name: infinigram-pileval-gpt2<br>Size: 10Gi<br>AccessMode: ReadOnlyMany"]
        pvc["PersistentVolumeClaim<br>Name: infinigram-pileval-gpt2<br>Namespace: infinigram-api"]
        
        sc --> pv
        pv --> pvc
    end
    
    subgraph "Deployments"
        api["API Deployment"]
        worker["Attribution Worker"]
    end
    
    pvc --> api
    pvc --> worker
```

**Diagram: Kubernetes Storage Resources**

Sources: [volume-claims/pileval-gpt2.yaml:1-43]()

Each array is configured with:

- A StorageClass named `infinigram` using the GKE persistent disk CSI driver
- A PersistentVolume that references a specific disk
- A PersistentVolumeClaim in the `infinigram-api` namespace

The key characteristics of the storage configuration:

| Attribute | Value | Purpose |
|-----------|-------|---------|
| AccessMode | ReadOnlyMany | Allows multiple pods to concurrently read from the volume |
| StorageClass | infinigram | Custom storage class for Infinigram arrays |
| Size | 10Gi (example) | Allocated storage for the array data |
| FsType | ext4 | File system type used for the volume |
| ReadOnly | true | Prevents accidental writes to the array data |

Sources: [volume-claims/pileval-gpt2.yaml:1-43]()

### Local Development Storage

For local development, a script is provided to download the required arrays from an S3 bucket and set up symbolic links to optimize disk space usage.

```mermaid
flowchart TD
    start["Start download-infini-gram-array.sh"]
    check["Check if v4_pileval_llama exists"]
    download["Download v4_pileval_llama from S3"]
    symlink1["Create symlink: v4_pileval_llama -> olmoe-mix-0924-dclm"]
    symlink2["Create symlink: v4_pileval_llama -> olmoe-mix-0924-nodclm"]
    symlink3["Create symlink: v4_pileval_llama -> v4-olmoe-0125-1b-7b-anneal-adapt"]
    symlink4["Create symlink: v4_pileval_llama -> v4-olmo-2-1124-13b-anneal-adapt"]
    symlink5["Create symlink: v4_pileval_llama -> v4-olmo-2-0325-32b-anneal-adapt"]
    end_["End"]
    
    start --> check
    check -- "No" --> download
    download --> symlink1
    check -- "Yes" --> symlink1
    symlink1 --> symlink2
    symlink2 --> symlink3
    symlink3 --> symlink4
    symlink4 --> symlink5
    symlink5 --> end_
```

**Diagram: Local Array Download and Setup Process**

Sources: [bin/download-infini-gram-array.sh:1-37]()

The script performs the following operations:

1. Sets `INFINIGRAM_ARRAY_DIR` to point to the `../infinigram-array` directory
2. Checks if the primary array (`v4_pileval_llama`) exists
3. If not, downloads it from the S3 bucket `infini-gram-lite`
4. Creates symbolic links from the primary array to other required array directories

## Storage Access Pattern

The infinigram arrays stored in these volumes are accessed by both the API service and the Attribution Worker through the InfiniGramProcessor component. This component provides a consistent interface for interacting with the arrays, hiding the underlying storage details from the application code.

```mermaid
sequenceDiagram
    participant Client
    participant API as "API Service"
    participant Worker as "Attribution Worker"
    participant Processor as "InfiniGramProcessor"
    participant Storage as "Infinigram Arrays"
    
    Client->>API: Request attribution/documents
    
    alt Direct Request
        API->>Processor: Query array data
        Processor->>Storage: Access array files
        Storage-->>Processor: Return data
        Processor-->>API: Return processed results
        API-->>Client: Return response
    else Attribution Request
        API->>Worker: Queue attribution job
        Worker->>Processor: Process attribution
        Processor->>Storage: Access array files
        Storage-->>Processor: Return data
        Processor-->>Worker: Return processed results
        Worker-->>API: Store result
        API-->>Client: Return response
    end
```

**Diagram: Data Access Flow for Infinigram Arrays**

Sources: [bin/download-infini-gram-array.sh:1-37](), [volume-claims/pileval-gpt2.yaml:1-43]()

## Adding New Arrays

To add a new infinigram array to the system, the following steps are required:

1. **For local development:**
   - Update the `download-infini-gram-array.sh` script to download or symlink the new array
   - Add volume mapping in the `docker-compose.yaml` file

2. **For production deployment:**
   - Create a new persistent disk in GKE
   - Define a new YAML configuration with StorageClass, PersistentVolume, and PersistentVolumeClaim
   - Update deployment configurations to mount the new volume

Sources: [bin/download-infini-gram-array.sh:5-6]()

## Performance Considerations

The storage system is optimized for read performance, as the arrays are only read, never written to during normal operation. Key performance considerations include:

- Arrays are mounted as read-only to prevent accidental writes
- In local development, symbolic links are used to avoid duplicating large arrays
- In production, the GKE persistent disk type is set to `pd-balanced` for a good balance of performance and cost
- The volumes use `WaitForFirstConsumer` binding mode to ensure they're created in the same zone as the consuming pods

Sources: [volume-claims/pileval-gpt2.yaml:1-43]()

---

# Page: Observability

# Observability

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/Dockerfile](api/Dockerfile)
- [api/app.py](api/app.py)
- [api/src/glog.py](api/src/glog.py)
- [otel-collector/otel-collector-config.yaml](otel-collector/otel-collector-config.yaml)

</details>



This page documents the observability infrastructure in the infinigram-api system, including logging, tracing, and monitoring. The page focuses on how telemetry data is collected, processed, and exported to facilitate debugging, performance monitoring, and operational insights.

For information about the overall system architecture, see [System Architecture](#2).

## Overview

The infinigram-api implements comprehensive observability using OpenTelemetry for distributed tracing and structured logging. The system is configured to work in both development and production environments, with appropriate exporters for each.

```mermaid
graph TD
    subgraph "Infinigram API"
        API["FastAPI Application"]
        Tracing["OpenTelemetry Tracing"]
        Logging["Structured Logging"]
    end
    
    subgraph "Telemetry Collection"
        OTELCollector["OpenTelemetry Collector"]
    end
    
    subgraph "Backends"
        CloudTrace["Google Cloud Trace"]
        CloudLogging["Google Cloud Logging"]
    end
    
    API --> Tracing
    API --> Logging
    
    Tracing --> OTELCollector
    Logging --> OTELCollector
    
    OTELCollector --> CloudTrace
    OTELCollector --> CloudLogging
```

Sources: [api/app.py:9-69](api/app.py:9-69), [api/Dockerfile:51-62](api/Dockerfile:51-62), [otel-collector/otel-collector-config.yaml:15-136](otel-collector/otel-collector-config.yaml:15-136)

## Tracing Configuration

The system uses OpenTelemetry to instrument code and generate distributed traces. Tracing is set up differently based on the environment:

- **Development**: Uses a `SimpleSpanProcessor` with `OTLPSpanExporter` to send traces to a local OpenTelemetry Collector
- **Production**: Uses a `BatchSpanProcessor` with `CloudTraceSpanExporter` to send traces directly to Google Cloud Trace

```mermaid
flowchart TD
    subgraph "Tracing Setup in app.py"
        InitProvider["TracerProvider initialization"]
        EnvCheck["Environment check\nENV == development?"]
        DevProcessor["SimpleSpanProcessor with\nOTLPSpanExporter"]
        ProdProcessor["BatchSpanProcessor with\nCloudTraceSpanExporter"]
        SetProvider["Set global tracer provider"]
        InstrumentApp["Instrument FastAPI app"]
    end
    
    InitProvider --> EnvCheck
    EnvCheck -->|Yes| DevProcessor
    EnvCheck -->|No| ProdProcessor
    DevProcessor --> SetProvider
    ProdProcessor --> SetProvider
    SetProvider --> InstrumentApp
```

The API automatically captures incoming HTTP requests thanks to the `FastAPIInstrumentor` that instruments the application. Health endpoints are excluded from tracing to avoid excessive telemetry data.

Sources: [api/app.py:56-69](api/app.py:56-69), [api/Dockerfile:51-62](api/Dockerfile:51-62)

## Logging Configuration

The system supports structured JSON logging in a format compatible with Google Cloud Logging. This is enabled by setting the `LOG_FORMAT` environment variable to `google:json`.

### Structured Logging

The `glog.py` module provides a custom JSON formatter that:

1. Maps standard Python logging fields to Google Cloud Logging fields
2. Includes OpenTelemetry trace context in logs for correlation
3. Uses timestamps in ISO 8601 format

Key field mappings:

| Python Logging Field | Google Cloud Logging Field |
|----------------------|----------------------------|
| levelname            | severity                   |
| asctime              | timestamp                  |
| otelTraceID          | logging.googleapis.com/trace |
| otelSpanID           | logging.googleapis.com/spanId |
| otelTraceSampled     | logging.googleapis.com/trace_sampled |

Sources: [api/src/glog.py:1-27](api/src/glog.py:1-27), [api/app.py:27-31](api/app.py:27-31)

## OpenTelemetry Collector

The system includes an OpenTelemetry Collector that receives, processes, and exports telemetry data. This collector is primarily used in development environments, but a similar configuration can be deployed in production.

```mermaid
flowchart LR
    subgraph "OTLP Receivers"
        HTTPReceiver["OTLP HTTP\n(port 4318)"]
        GRPCReceiver["OTLP gRPC\n(port 4317)"]
        FileLogReceiver["FileLog Receiver\n(/var/log/app.log)"]
    end
    
    subgraph "Processors"
        Batch["batch"]
        ResourceDetection["resourcedetection"]
        Resource["resource"]
    end
    
    subgraph "Exporters"
        Debug["debug"]
    end
    
    subgraph "Pipelines"
        TracePipeline["traces"]
        MetricsPipeline["metrics"]
        LogsPipeline["logs"]
    end
    
    HTTPReceiver --> TracePipeline
    GRPCReceiver --> TracePipeline
    HTTPReceiver --> MetricsPipeline
    GRPCReceiver --> MetricsPipeline
    FileLogReceiver --> LogsPipeline
    
    TracePipeline --> Batch
    TracePipeline --> ResourceDetection
    MetricsPipeline --> Batch
    MetricsPipeline --> ResourceDetection
    MetricsPipeline --> Resource
    LogsPipeline --> Batch
    LogsPipeline --> ResourceDetection
    
    Batch --> Debug
    ResourceDetection --> Debug
    Resource --> Debug
```

The collector is configured to handle:

- **Traces and Metrics**: Received via OTLP HTTP and gRPC protocols
- **Logs**: Collected from the application log file, parsed, and processed to extract trace context

Sources: [otel-collector/otel-collector-config.yaml:15-136](otel-collector/otel-collector-config.yaml:15-136)

## Observability in Code

In the infinigram-api codebase, observability is set up in the main application entrypoint. The key components include:

1. **Logging Setup**: Configuring Python's logging system to use structured JSON logs if requested
2. **OpenTelemetry Setup**: Initializing the trace provider and exporters
3. **FastAPI Instrumentation**: Automatically capturing traces for all FastAPI endpoints

### Code Structure

```mermaid
classDiagram
    class app_py {
        +setup_logging()
        +setup_tracing()
        +instrument_app()
    }
    
    class glog_py {
        +create_stream_handler()
    }
    
    class FastAPIInstrumentor {
        +instrument_app()
    }
    
    class TracerProvider {
        +add_span_processor()
    }
    
    class OTLPSpanExporter {
    }
    
    class CloudTraceSpanExporter {
    }
    
    app_py --> glog_py: Uses for logging
    app_py --> TracerProvider: Creates
    app_py --> FastAPIInstrumentor: Uses for instrumentation
    TracerProvider --> OTLPSpanExporter: Uses in development
    TracerProvider --> CloudTraceSpanExporter: Uses in production
```

Sources: [api/app.py:9-69](api/app.py:9-69), [api/src/glog.py:1-27](api/src/glog.py:1-27)

## Environment Variables

The system uses environment variables to configure observability. These are set in the Dockerfile or can be overridden at runtime:

| Environment Variable | Purpose | Default Value |
|----------------------|---------|--------------|
| `LOG_FORMAT` | Format for logging output | Standard Python logging (or `google:json` for structured logs) |
| `LOG_LEVEL` | Logging verbosity | `INFO` |
| `OTEL_SERVICE_NAME` | Service name for telemetry | `infinigram-api` (prod) or `infinigram-api-dev` (dev) |
| `OTEL_TRACES_EXPORTER` | Trace exporter type | `otlp` |
| `OTEL_METRICS_EXPORTER` | Metrics exporter type | `otlp` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Endpoint for OTLP exporter | Development: `http://otelcol:4318` |

Sources: [api/Dockerfile:51-62](api/Dockerfile:51-62), [api/app.py:27-31](api/app.py:27-31)

## Correlation Between Traces and Logs

One key feature of the observability setup is the correlation between distributed traces and logs. When a log entry is emitted during a traced operation, the trace context is automatically included in the log entry, allowing for easier debugging and analysis.

```mermaid
sequenceDiagram
    participant Client
    participant API as "FastAPI App"
    participant OTel as "OpenTelemetry SDK"
    participant Logger as "Python Logger"
    participant Collector as "OTel Collector"
    participant CloudObs as "Cloud Observability"
    
    Client->>API: HTTP Request
    activate API
    API->>OTel: Begin span
    activate OTel
    
    API->>Logger: Log message
    Logger->>OTel: Get current trace context
    OTel-->>Logger: Return trace ID, span ID
    Logger->>Collector: Send structured log with trace context
    
    API->>OTel: End span
    OTel->>Collector: Send trace data
    deactivate OTel
    deactivate API
    
    Collector->>CloudObs: Export logs and traces
    CloudObs->>CloudObs: Correlate logs with traces
```

Sources: [api/src/glog.py:13-24](api/src/glog.py:13-24), [otel-collector/otel-collector-config.yaml:52-83](otel-collector/otel-collector-config.yaml:52-83)

## Best Practices

When developing for the infinigram-api system, follow these observability best practices:

1. **Use structured logging**: Always use the logger rather than print statements
2. **Include contextual information**: Add relevant context to log messages to make debugging easier
3. **Create spans for significant operations**: Use the OpenTelemetry API to create spans for important operations, especially those that are time-consuming or cross service boundaries
4. **Set appropriate log levels**: Use the right log level for each message (DEBUG, INFO, WARNING, ERROR)
5. **Add attributes to spans**: Include relevant attributes in spans to provide more context for distributed traces

---

# Page: Testing and Evaluation

# Testing and Evaluation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [scripts/distrib_of_score.py](scripts/distrib_of_score.py)
- [scripts/eval_corpuslink_relevance.py](scripts/eval_corpuslink_relevance.py)
- [scripts/repro_ui.py](scripts/repro_ui.py)
- [scripts/stress_test_api.py](scripts/stress_test_api.py)

</details>



This document covers the testing and evaluation tools available for the infinigram-api system. These tools help assess system performance, reliability, and attribution quality. The focus is on scripts that enable stress testing, relevance evaluation, and analysis of attribution results.

## Overview of Testing Ecosystem

The infinigram-api project provides several specialized scripts for testing different aspects of the system:

```mermaid
graph TB
    subgraph "Testing Infrastructure"
        StressTest["stress_test_api.py"]
        DocEval["eval_corpuslink_relevance.py"]
        ScoreAnalysis["distrib_of_score.py"]
        UIRepro["repro_ui.py"]
    end

    subgraph "API System"
        AttributionEndpoint["/attribution endpoint"]
    end

    subgraph "External Services"
        OpenAI["OpenAI API (GPT-4)"]
    end

    StressTest -->|"Concurrent POST requests"| AttributionEndpoint
    DocEval -->|"Evaluate attribution results"| AttributionEndpoint
    DocEval -->|"Judge document relevance"| OpenAI
    ScoreAnalysis -->|"Analyze score distributions"| AttributionEndpoint
    UIRepro -->|"Single request visualization"| AttributionEndpoint
```

Sources: [scripts/stress_test_api.py](), [scripts/eval_corpuslink_relevance.py](), [scripts/distrib_of_score.py](), [scripts/repro_ui.py]()

## Stress Testing

The `stress_test_api.py` script enables evaluating API performance under concurrent load. It sends multiple attribution requests in parallel and processes the results, helping identify performance bottlenecks or reliability issues.

```mermaid
sequenceDiagram
    participant Client as "stress_test_api.py"
    participant Pool as "mp.Pool(NUM_CONCURRENT_REQUESTS)"
    participant API as "Attribution Endpoint"

    Client->>Pool: "Create pool with NUM_CONCURRENT_REQUESTS workers"
    loop "For each concurrent request"
        Client->>Client: "Generate random numeric response"
    end
    Client->>Pool: "Map issue_request() to all responses"
    
    par Parallel Processing
        Pool->>API: "POST request to attribution endpoint"
        API-->>Pool: "Attribution results with spans"
    end
    
    Pool-->>Client: "Aggregated results"
    Client->>Client: "Display span information (left, right, text)"
```

### Key Components

- **Concurrent Requests**: Configurable via `NUM_CONCURRENT_REQUESTS` (default: 32)
- **Test Data Generation**: Creates random numeric responses of length `NUM_TOKENS` (default: 500)
- **Parallelization**: Utilizes Python's multiprocessing to handle multiple simultaneous requests
- **Attribution Parameters**: Uses a standard set of attribution parameters including delimiters, minimum span length, and ranking method

### Example Configuration

```python
PAYLOAD = {
    'prompt': '',
    'response': '',
    'delimiters': ['\n', '.'],
    'allowSpansWithPartialWords': False,
    'minimumSpanLength': 1,
    'maximumFrequency': 1000000,
    'maximumSpanDensity': 0.05,
    'spanRankingMethod': 'unigram_logprob_sum',
    'maximumDocumentsPerSpan': 10,
    'maximumContextLength': 250,
    'maximumContextLengthLong': 250,
    'maximumContextLengthSnippet': 40,
}
```

Sources: [scripts/stress_test_api.py:1-47]()

## Document Relevance Evaluation

The `eval_corpuslink_relevance.py` script assesses the quality of documents retrieved during attribution. It provides a structured way to evaluate whether the documents retrieved by the system are relevant to the user's prompt and the model's response.

```mermaid
sequenceDiagram
    participant Script as "eval_corpuslink_relevance.py"
    participant API as "Attribution API"
    participant OpenAI as "OpenAI API"
    participant Output as "JSON Output"

    Note over Script: "Load dataset with prompts and responses"
    loop "For each item in dataset"
        Script->>API: "POST /olmoe/attribution"
        API-->>Script: "Attribution results (spans and documents)"
        Script->>Script: "Process and organize documents by documentIndex"
        
        loop "For top N documents"
            Script->>OpenAI: "Rate document relevance (0-3 scale)"
            OpenAI-->>Script: "Relevance rating"
            Script->>Script: "Store rating with document"
        end
    end
    
    Script->>Script: "Calculate evaluation metrics"
    Note over Script: "avg_rating_top1, ratio_relevant_top5, etc."
    Script->>Output: "Write evaluated dataset to JSON"
    Script->>Script: "Display summary statistics"
```

### Evaluation Process

1. **Data Processing**: Loads a dataset of prompts and responses
2. **Attribution**: Sends each prompt-response pair to the attribution API
3. **Document Organization**: Extracts and organizes retrieved documents
4. **Relevance Rating**: Uses OpenAI's GPT-4 model to rate document relevance on a 0-3 scale:
   - 0: Document is about a different topic
   - 1: Document is about a broader topic or has insufficient information
   - 2: Document is on the right topic but in a slightly different context
   - 3: Document is a direct match for user intent
5. **Metrics Calculation**: Computes metrics like average rating and percentage of relevant documents

### Key Metrics

The script calculates and reports:

- Average rating for top-1 and top-5 documents
- Percentage of relevant documents (rating ≥ 2) in top-1 and top-5 positions

Sources: [scripts/eval_corpuslink_relevance.py:1-155]()

## Score Distribution Analysis

The `distrib_of_score.py` script analyzes how attribution scores are distributed across responses of different lengths. This helps understand patterns in attribution quality and how it varies with response characteristics.

```mermaid
sequenceDiagram
    participant Script as "distrib_of_score.py"
    participant API as "Attribution API"
    participant Matplotlib as "matplotlib.pyplot"
    participant Output as "PNG Visualization"

    Note over Script: "Load dataset with prompts and responses"
    loop "For each item in dataset"
        Script->>API: "POST /olmo-2-1124-13b/attribution"
        API-->>Script: "Attribution results"
        Script->>Script: "Extract score metrics:"
        Note over Script: "max_doc_score, min_doc_score"
        Note over Script: "max_span_score, min_span_score"
        Note over Script: "response_len_chars"
    end
    
    Script->>Matplotlib: "Create document score plot"
    Note over Matplotlib: "x-axis: response_len_chars"
    Note over Matplotlib: "y-axis: document scores"
    
    Script->>Matplotlib: "Create span score plot"
    Note over Matplotlib: "x-axis: response_len_chars"
    Note over Matplotlib: "y-axis: span scores"
    
    Matplotlib->>Output: "Save plots as PNG files"
```

### Key Features

- **Score Extraction**: Processes attribution results to extract document and span scores
- **Correlation Analysis**: Relates scores to response length (in characters)
- **Visualization**: Generates scatter plots showing the distribution of scores
- **Separate View**: Creates separate visualizations for document scores and span scores

### Visualization Output

The script produces two visualization files:
- `*_doc.png`: Shows the distribution of document scores vs. response length
- `*_span.png`: Shows the distribution of span scores vs. response length

Sources: [scripts/distrib_of_score.py:1-107]()

## UI Reproduction

The `repro_ui.py` script helps reproduce and test the user interface for attribution results. It sends a single attribution request and formats the results in a way that resembles how they would appear in the UI.

### Process Flow

1. **Input Definition**: Define a prompt and response to test
2. **Attribution Request**: Send the prompt and response to the attribution API
3. **Result Processing**: Process the attribution results, organizing documents by index
4. **Result Display**: Format and display the most relevant documents and their associated spans

### Example Configuration

```python
payload = {
    'prompt': prompt,
    'response': response,
    'delimiters': ['\n', '.'],
    'allowSpansWithPartialWords': False,
    'minimumSpanLength': 1,
    'maximumFrequency': 10,
    'maximumSpanDensity': 0.05,
    'spanRankingMethod': 'length',
    'includeDocuments': True,
    'maximumDocumentsPerSpan': 10,
    'maximumDocumentDisplayLength': 100,
    'filterMethod': 'bm25',
    'filterBm25FieldsConsidered': 'response',
    'filterBm25RatioToKeep': 1.0,
    'includeInputAsTokens': True,
}
```

This script is particularly useful for:
- Debugging attribution results
- Testing with specific prompt-response pairs
- Visualizing how results will appear to end-users
- Understanding the relationship between spans and documents

Sources: [scripts/repro_ui.py:1-191]()

## Common Attribution Parameters

All testing scripts use similar parameters when making attribution requests. The table below summarizes the key parameters:

| Parameter | Description | Typical Value |
|-----------|-------------|---------------|
| `delimiters` | Characters that define span boundaries | `['\n', '.']` |
| `allowSpansWithPartialWords` | Whether spans can include partial words | `False` |
| `minimumSpanLength` | Minimum length of spans to consider | `1` |
| `maximumFrequency` | Maximum frequency threshold for n-grams | `1000000` or `10` |
| `maximumSpanDensity` | Maximum density of spans in response | `0.05` |
| `spanRankingMethod` | Method to rank spans | `unigram_logprob_sum` or `length` |
| `includeDocuments` | Whether to include documents in results | `True` |
| `maximumDocumentsPerSpan` | Maximum documents to return per span | `10` |
| `filterMethod` | Method to filter candidate documents | `bm25` |
| `filterBm25FieldsConsidered` | Fields for BM25 filtering | `prompt\|response` or `response` |
| `filterBm25RatioToKeep` | Fraction of documents to keep after filtering | `1.0` |

These parameters can be adjusted to test different configurations and observe how they affect attribution quality and performance.

Sources: [scripts/stress_test_api.py:8-21](), [scripts/distrib_of_score.py:20-35](), [scripts/eval_corpuslink_relevance.py:22-36](), [scripts/repro_ui.py:141-157]()

---

# Page: Containerization

# Containerization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/Dockerfile](api/Dockerfile)
- [api/src/attribution/attribution_request.py](api/src/attribution/attribution_request.py)
- [api/src/cache/__init__.py](api/src/cache/__init__.py)
- [api/src/cache/redis.py](api/src/cache/redis.py)
- [api/src/glog.py](api/src/glog.py)
- [attribution_worker/Dockerfile](attribution_worker/Dockerfile)
- [attribution_worker/pyproject.toml](attribution_worker/pyproject.toml)
- [otel-collector/otel-collector-config.yaml](otel-collector/otel-collector-config.yaml)
- [proxy/Dockerfile](proxy/Dockerfile)

</details>



This document details how the infinigram-api system components are containerized using Docker, including the build process, environment configurations, and container interactions. For information about deploying these containers to Kubernetes, see [Kubernetes Deployment](#5.2).

## Container Architecture

The infinigram-api system uses a containerized microservices architecture with several key components:

1. **API Container**: Handles HTTP requests using FastAPI
2. **Attribution Worker**: Processes attribution jobs asynchronously
3. **NGINX Proxy**: Routes client requests to the API
4. **Supporting Services**: Redis (caching), PostgreSQL (job queue), and OpenTelemetry (observability)

### System Container Architecture

```mermaid
graph TB
    subgraph "Infinigram API System"
        proxy["NGINX_Proxy"]
        api["API_Service"]
        worker["Attribution_Worker"]
        redis["Redis_Cache"]
        postgres["PostgreSQL_Queue"]
        otel["OpenTelemetry_Collector"]
        
        proxy --> api
        api --> redis
        api --> postgres
        worker --> redis
        worker --> postgres
        api --> otel
        worker --> otel
    end
```

Sources: [api/Dockerfile](), [attribution_worker/Dockerfile](), [proxy/Dockerfile](), [otel-collector/otel-collector-config.yaml]()

## Multi-Stage Build Process

Both the API and Attribution Worker containers use multi-stage builds to optimize image size and security:

```mermaid
graph TB
    subgraph "Multi-Stage Build Process"
        builder["Builder_Stage (Python3.12 + uv)"]
        runner["Runner_Stage (Python3.12-slim)"]
        dev["Dev_Target"]
        prod["Prod_Target"]
        
        builder --> runner
        runner --> dev
        runner --> prod
    end
```

Sources: [api/Dockerfile:4-64](), [attribution_worker/Dockerfile:4-61]()

The multi-stage build approach provides several benefits:
- Smaller final image size by excluding build tools
- Improved security by reducing attack surface
- Separation of development and production configurations

## API Container

The API container uses a four-stage build process defined in [api/Dockerfile]():

1. **Builder Stage** [api/Dockerfile:4-29]():
   - Uses Python 3.12-slim base image
   - Copies `uv` package manager from a separate image
   - Installs dependencies using `uv sync` with lockfile for reproducibility
   - Mounts dependencies as caches for faster builds

2. **Runner Stage** [api/Dockerfile:33-48]():
   - Uses Python 3.12-slim-bookworm base image
   - Copies only the application and installed dependencies from builder
   - Includes model files needed for operation

3. **Development Target** [api/Dockerfile:51-58]():
   - Sets OpenTelemetry configuration for local development
   - Uses FastAPI development server with hot reloading

4. **Production Target** [api/Dockerfile:60-64]():
   - Minimal configuration for production
   - Uses FastAPI production server

Sources: [api/Dockerfile:4-64]()

## Attribution Worker Container

The Attribution Worker container follows a similar pattern in [attribution_worker/Dockerfile]():

1. **Builder Stage** [attribution_worker/Dockerfile:4-28]():
   - Uses Python 3.12-slim base image with `uv`
   - Dependencies specified in [attribution_worker/pyproject.toml]() including:
     - `saq[postgres,web]` for job processing
     - `infini-gram-processor` for attribution calculations
     - OpenTelemetry libraries for monitoring

2. **Base Stage** [attribution_worker/Dockerfile:32-47]():
   - Uses Python 3.12-slim-bookworm
   - Copies application code and dependencies from builder

3. **Development Target** [attribution_worker/Dockerfile:49-57]():
   - OpenTelemetry configuration for local development
   - Runs SAQ (Simple Async Queue) with verbose logging

4. **Production Target** [attribution_worker/Dockerfile:59-61]():
   - Runs SAQ without verbose logging for production

Sources: [attribution_worker/Dockerfile:4-61](), [attribution_worker/pyproject.toml:1-17]()

## NGINX Proxy Container

The NGINX proxy container uses a simpler single-stage build:

```
FROM nginx:1.27.4-alpine
COPY nginx.conf /etc/nginx/nginx.conf
ARG CONF_FILE=local.conf
COPY $CONF_FILE /etc/nginx/conf.d/default.conf
```

The container uses the lightweight Alpine variant of NGINX and accepts a configuration file argument to support different environments.

Sources: [proxy/Dockerfile:1-7]()

## Environment-Specific Configurations

The containers have different configurations for development and production environments:

### Development Environment

```mermaid
graph TB
    subgraph "Development Configuration"
        api_dev["API_Container_Dev"]
        worker_dev["Worker_Container_Dev"]
        otel["OpenTelemetry"]
        
        api_dev -->|"OTEL_SERVICE_NAME=infinigram-api-dev"| otel
        api_dev -->|"ENV=development"| env["Environment"]
        api_dev -->|"fastapi dev app.py --port 8000"| cmd["Commands"]
        
        worker_dev -->|"OTEL_SERVICE_NAME=infinigram-api-worker-dev"| otel
        worker_dev -->|"ENV=development"| env
        worker_dev -->|"saq --verbose --web"| cmd
    end
```

Sources: [api/Dockerfile:51-58](), [attribution_worker/Dockerfile:49-57]()

### Production Environment

```mermaid
graph TB
    subgraph "Production Configuration"
        api_prod["API_Container_Prod"]
        worker_prod["Worker_Container_Prod"]
        otel["OpenTelemetry"]
        
        api_prod -->|"OTEL_SERVICE_NAME=infinigram-api"| otel
        api_prod -->|"ENV=production"| env["Environment"]
        api_prod -->|"fastapi run app.py --port 8000"| cmd["Commands"]
        
        worker_prod -->|"saq --web"| cmd
    end
```

Sources: [api/Dockerfile:60-64](), [attribution_worker/Dockerfile:59-61]()

## Container Data Flow

The containers interact to process attribution requests as follows:

```mermaid
sequenceDiagram
    participant Client
    participant NGINX_Proxy
    participant API_Service
    participant Redis_Cache
    participant PostgreSQL_Queue
    participant Attribution_Worker
    participant OTEL_Collector
    
    Client->>NGINX_Proxy: HTTP Request
    NGINX_Proxy->>API_Service: Forward Request
    
    alt Simple Request
        API_Service->>Redis_Cache: Check Cache
        Redis_Cache-->>API_Service: Return Data (if available)
        API_Service->>NGINX_Proxy: Response
        NGINX_Proxy->>Client: Forward Response
    else Attribution Request
        API_Service->>Redis_Cache: Check Cache via get_redis()
        Redis_Cache-->>API_Service: Cache Miss
        API_Service->>PostgreSQL_Queue: Enqueue Attribution Job
        API_Service->>NGINX_Proxy: 202 Accepted
        NGINX_Proxy->>Client: Forward Response
        
        Attribution_Worker->>PostgreSQL_Queue: Poll for Jobs
        PostgreSQL_Queue-->>Attribution_Worker: Job Details
        Attribution_Worker->>Attribution_Worker: Process AttributionRequest
        Attribution_Worker->>Redis_Cache: Store Result
        Attribution_Worker->>OTEL_Collector: Send Telemetry
        
        Client->>NGINX_Proxy: Poll for Result
        NGINX_Proxy->>API_Service: Forward Request
        API_Service->>Redis_Cache: Check Cache
        Redis_Cache-->>API_Service: Result
        API_Service->>NGINX_Proxy: Response
        NGINX_Proxy->>Client: Forward Response
    end
    
    API_Service->>OTEL_Collector: Send Telemetry
```

Sources: [api/Dockerfile](), [attribution_worker/Dockerfile](), [api/src/cache/redis.py:1-18](), [api/src/attribution/attribution_request.py:1-63]()

## Observability Integration

The containers are configured with structured logging and OpenTelemetry integration:

```mermaid
graph TB
    subgraph "Observability Configuration"
        api["API_Container"]
        worker["Worker_Container"]
        otel["OpenTelemetry_Collector"]
        logs["JSON_Structured_Logs"]
        
        api -->|"create_stream_handler()"| logs
        worker -->|"JSON Log Format"| logs
        
        api -->|"OTLP HTTP Exporter"| otel
        worker -->|"OTLP HTTP Exporter"| otel
        
        logs --> otel
    end
```

Key observability features:
- JSON-structured logging using `jsonlogger.JsonFormatter`
- Trace context propagation for distributed tracing
- OpenTelemetry integration configured via environment variables
- Log severity mapping for Google Cloud compatibility

Sources: [api/src/glog.py:1-27](), [otel-collector/otel-collector-config.yaml:15-84](), [api/Dockerfile:52-55](), [attribution_worker/Dockerfile:51-54]()

## Redis Caching Implementation

The Redis cache is used by both the API and Attribution Worker for storing attribution results:

```mermaid
graph TB
    subgraph "Redis Cache Integration"
        api["API_Service"]
        worker["Attribution_Worker"]
        redis["Redis_Cache"]
        conn_pool["ConnectionPool"]
        
        api -->|"get_redis()"| conn_pool
        worker -->|"get_redis()"| conn_pool
        conn_pool -->|"create_connection_pool()"| redis
    end
```

The Redis connection is established through a dependency injection pattern:
- `create_connection_pool()` creates a connection pool (with `@lru_cache` for efficiency)
- `get_redis()` returns a Redis client using the pool
- `CacheDependency` provides the Redis client to FastAPI endpoints

Sources: [api/src/cache/redis.py:1-18](), [api/src/cache/__init__.py:1-9]()

## Conclusion

The infinigram-api system uses a well-structured containerization approach that enables:
- Efficient development workflow with hot reloading
- Optimized production images using multi-stage builds
- Consistent environments with reproducible builds using `uv`
- Comprehensive observability with OpenTelemetry
- Separation of API and Worker components for scalability

The containerization strategy creates a foundation for deployment to Kubernetes while maintaining developer productivity in local environments.

Sources: [api/Dockerfile](), [attribution_worker/Dockerfile](), [proxy/Dockerfile]()

---

# Page: Error Handling

# Error Handling

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/app.py](api/app.py)
- [api/src/camel_case_model.py](api/src/camel_case_model.py)
- [api/src/infini_gram_exception_handler.py](api/src/infini_gram_exception_handler.py)

</details>



This document outlines the error handling mechanisms implemented in the Infinigram API system. It covers how exceptions are processed, the structure of error responses, and the custom exception handlers used throughout the application.

## Error Handling Architecture

The Infinigram API implements a structured approach to error handling using FastAPI's exception handling system combined with the RFC 9457 Problem Details standard for HTTP APIs. This provides consistent, machine-readable error responses across the application.

```mermaid
flowchart TD
    subgraph "Request Flow"
        Client["Client Request"] --> API["FastAPI Application"]
        API --> Router["Router"]
        Router --> Handler["Request Handler"]
    end

    subgraph "Error Handling Flow"
        Handler -- "Raises Exception" --> Exception["Exception"]
        Exception --> FastAPIHandler["FastAPI Exception Handler"]
        FastAPIHandler --> CustomHandler["Custom Exception Handler"]
        CustomHandler --> ProblemResponse["Problem Response"]
        ProblemResponse --> Client
    end

    classDef main stroke-width:2px;
    class Exception,CustomHandler,ProblemResponse main;
```

**Diagram: Error Handling Flow**

Sources: [api/app.py:46-50](), [api/src/infini_gram_exception_handler.py:8-16]()

The error handling system:
1. Catches exceptions raised during request processing
2. Routes them through the appropriate exception handler
3. Transforms exceptions into structured Problem Details responses
4. Returns the formatted error to the client

## Exception Types and Handlers

The Infinigram API uses both built-in FastAPI exception types and custom exceptions specific to the Infinigram engine.

```mermaid
classDiagram
    class Exception {
        +__str__()
        +__repr__()
    }
    
    class HTTPException {
        +status_code: int
        +detail: str
        +headers: dict
    }
    
    class InfiniGramEngineException {
        +detail: str
    }
    
    class Problem {
        +title: str
        +status: int
        +detail: str
        +type: str
        +instance: str
        +extensions: dict
    }
    
    Exception <|-- HTTPException
    Exception <|-- InfiniGramEngineException
    InfiniGramEngineException --> Problem : transforms to
    
```

**Diagram: Exception Hierarchy and Transformation**

Sources: [api/app.py:7-8](), [api/src/infini_gram_exception_handler.py:1-4]()

### Custom Exception Handler

The system implements a custom exception handler specifically for `InfiniGramEngineException`, which handles errors from the Infinigram engine. When these exceptions occur, they are converted to RFC 9457 Problem Details objects.

The exception handler is registered in the FastAPI application:

```mermaid
flowchart LR
    subgraph "Exception Registration"
        App["FastAPI App"] -- "add_exception_handler" --> HandlerMap["Exception Handlers Map"]
        HandlerMap -- "maps" --> Handler["infini_gram_engine_exception_handler"]
        ExceptionType["InfiniGramEngineException"] -- "handled by" --> Handler
    end
```

**Diagram: Exception Handler Registration**

Sources: [api/app.py:46-50]()

## Error Response Format

The Infinigram API follows the RFC 9457 Problem Details standard for HTTP APIs, which provides a consistent way to return error details to clients.

The structure of error responses follows this format:

| Field | Type | Description |
|-------|------|-------------|
| title | string | Short, human-readable summary of the problem |
| status | number | HTTP status code |
| detail | string | Human-readable explanation specific to this problem |
| type | string | URI reference that identifies the problem type |
| instance | string (optional) | URI reference that identifies the specific occurrence of the problem |
| extensions | object (optional) | Additional information about the error |

Example of an error response from the Infinigram API:

```json
{
  "title": "infini-gram error",
  "status": 500,
  "detail": "Model failed to process the input text",
  "type": "https://errors.infinigram.ai/engine-failure"
}
```

Sources: [api/src/infini_gram_exception_handler.py:11-16]()

## Implementation Details

### Custom Handler Implementation

The custom exception handler for `InfiniGramEngineException` is defined in [api/src/infini_gram_exception_handler.py]() and transforms engine exceptions into structured Problem responses:

```python
def infini_gram_engine_exception_handler(
    handler: ExceptionHandler, request: Request, exception: InfiniGramEngineException
) -> Problem:
    return Problem(
        title="infini-gram error",
        status=500,
        detail=exception.detail,
        type=error_class_to_type(exception),
    )
```

This handler:
1. Takes the exception handler, HTTP request, and the exception instance
2. Creates a new Problem object with appropriate error details
3. Uses the `error_class_to_type` function to determine the type URI from the exception class
4. Returns a 500 status code (Internal Server Error) for engine exceptions

Sources: [api/src/infini_gram_exception_handler.py:8-16]()

### Registration in FastAPI Application

The exception handler is registered in the main FastAPI application during startup:

```python
app = FastAPI(title="infini-gram API", version="0.0.1", lifespan=lifespan)
add_exception_handler(
    app,
    handlers={InfiniGramEngineException: infini_gram_engine_exception_handler},
)
```

This connects the custom exception type with its corresponding handler in the FastAPI framework.

Sources: [api/app.py:46-50]()

## Error Handling Flow

The complete error handling flow in the Infinigram API is illustrated below:

```mermaid
sequenceDiagram
    participant Client
    participant API as "FastAPI App"
    participant Handler as "Request Handler"
    participant ExHandler as "Exception Handler"
    participant Problem as "Problem Response"
    
    Client->>API: HTTP Request
    API->>Handler: Process Request
    
    alt Request Processing Succeeds
        Handler->>API: Return Result
        API->>Client: 200 OK Response
    else Request Processing Fails
        Handler-->>API: Raise Exception
        API->>ExHandler: Handle Exception
        ExHandler->>Problem: Create Problem Response
        Problem->>API: Return Formatted Error
        API->>Client: Error Response (e.g., 500)
    end
```

**Diagram: Error Handling Sequence**

Sources: [api/app.py:46-50](), [api/src/infini_gram_exception_handler.py:8-16]()

## Best Practices for Error Handling

When working with or extending the Infinigram API, consider these error handling best practices:

1. **Use Specific Exceptions**: When adding new functionality, create specific exception types that provide clear context about what went wrong.

2. **Provide Detailed Messages**: Include specific details in exception messages to help with debugging and client understanding.

3. **Map Exceptions to Appropriate Status Codes**: Different types of errors should map to the most appropriate HTTP status codes.

4. **Follow the Problem Details Standard**: Maintain consistency with the RFC 9457 format for all error responses.

5. **Handle Both Expected and Unexpected Errors**: While custom handlers address known error cases, ensure the system has appropriate fallbacks for unexpected errors.

Sources: [api/app.py:7-8](), [api/src/infini_gram_exception_handler.py:1-16]()