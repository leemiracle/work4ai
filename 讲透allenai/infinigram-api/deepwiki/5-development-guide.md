<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/infinigram-api · page 5 Development Guide · fetched 2026-10-26 -->

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

