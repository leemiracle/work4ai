<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/infinigram-api · page 6 Infrastructure · fetched 2026-10-26 -->

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

