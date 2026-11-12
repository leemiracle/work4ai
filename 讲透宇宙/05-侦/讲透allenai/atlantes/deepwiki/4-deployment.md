<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/atlantes · page 4 Deployment · fetched 2026-10-26 -->

# Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ais/Dockerfile](ais/Dockerfile)
- [ais/docker-compose.yml](ais/docker-compose.yml)

</details>



This document provides a technical overview of how the Atlantes system is deployed and operated in production environments. It covers the Docker-based containerization strategy, service configuration, and deployment architecture. For details on CI/CD pipelines, see [CI/CD Pipeline](#4.3), and for specific Docker configuration details, see [Docker Configuration](#4.1).

## Deployment Architecture

Atlantes follows a containerized microservice architecture where each functional component runs as a separate Docker container. The system deploys four primary services that collectively provide the full functionality of the ATLAS modeling system.

```mermaid
flowchart TD
    subgraph "Atlantes Deployment"
        subgraph "Docker Containers"
            ActivityService["test_activity
            Port: 8000
            Command: main_activity.py"]
            
            EntityService["test_entity
            Port: 8001
            Command: main_entity.py"]
            
            CPDService["test_cpd_grpc
            Port: 5206
            Command: atlantes/cpd/serve/serve_grpc.py"]
            
            EntityPostprocessor["test_entity_postprocessor_grpc
            Port: 5207
            Command: atlantes/inference/atlas_entity/grpc_serve/serve_grpc.py"]
        end
        
        Credentials["GCP Credentials
        Mounted at: /mnt/gcloud/gcp_application_credentials.json"]
        
        MarineData["Marine Infrastructure Data
        Downloaded at: /ais/src/atlantes/data/latest_marine_infrastructure.geojson"]
    end
    
    Client["Client Applications"] --> ActivityService
    Client --> EntityService
    Client --> CPDService
    Client --> EntityPostprocessor
    
    Credentials --> ActivityService
    Credentials --> EntityService
    Credentials --> CPDService
    Credentials --> EntityPostprocessor
    
    MarineData --> ActivityService
```

Sources: [ais/docker-compose.yml:8-100](), [ais/Dockerfile:52-57]()

## Container Image Configuration

All services use the same base Docker image defined in the Dockerfile, built on PyTorch with CUDA support for GPU acceleration. The container image is configured with:

- PyTorch 2.1.2 with CUDA 12.1 and cuDNN 8 support
- Python 3.12 environment
- GCP credentials configuration
- Required Python dependencies
- Downloaded marine infrastructure data

```mermaid
flowchart TD
    Base["pytorch/pytorch:2.1.2-cuda12.1-cudnn8-runtime"] --> Install["Install System Dependencies
    - wget
    - netcat
    - Python 3.12"]
    
    Install --> PyTorch["Install PyTorch Ecosystem
    - torch==2.1.2
    - torchvision==0.16.2
    - torchaudio==2.1.2"]
    
    PyTorch --> RequirementsInstall["Install Python Dependencies
    from requirements.txt"]
    
    RequirementsInstall --> CodeCopy["Copy Application Code
    to /ais"]
    
    CodeCopy --> MarineData["Download Marine Infrastructure Data
    to /ais/src/atlantes/data/"]
    
    MarineData --> PackageInstall["Install Package
    pip install ."]
```

Sources: [ais/Dockerfile:1-60]()

## Service Configuration

Each service in the Atlantes deployment is configured with specific environment variables, ports, and health checks to ensure reliable operation.

| Service | Port | Environment Variables | Health Check | Command |
|---------|------|----------------------|--------------|---------|
| Activity Service | 8000 | `PORT=8000` | TCP check on port 8000 | `python3 src/main_activity.py` |
| Entity Service | 8001 | `PORT=8001` | TCP check on port 8001 | `python3 src/main_entity.py` |
| CPD gRPC Service | 5206 | `CPD_ADDRESS=0.0.0.0`<br>`CPD_PORT=5206` | TCP check on port 5206 | `python3 /ais/src/atlantes/cpd/serve/serve_grpc.py` |
| Entity Postprocessor gRPC | 5207 | `ENTITY_POSTPROCESSOR_GRPC_ADDRESS=0.0.0.0`<br>`ENTITY_POSTPROCESSOR_GRPC_PORT=5207` | TCP check on port 5207 | `python3 /ais/src/atlantes/inference/atlas_entity/grpc_serve/serve_grpc.py` |

Sources: [ais/docker-compose.yml:9-100]()

## Deployment Workflow

The deployment process for Atlantes follows these main steps:

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Build as Build System
    participant Docker as Docker Registry
    participant Env as Deployment Environment
    
    Dev->>Build: Commit code changes
    Note over Build: CI/CD triggers build
    Build->>Build: Build Docker image
    Build->>Docker: Push image to registry
    
    Build->>Env: Deploy using docker-compose
    Env->>Env: Pull latest image
    Env->>Env: Configure credentials
    Env->>Env: Start services
    Env->>Env: Run health checks
    Note over Env: Services up and running
```

Sources: [ais/docker-compose.yml:24-97]()

## Shared Resource Configuration

All containers utilize shared resources and configurations:

- **Shared Memory**: Each container is allocated 4.77GB of shared memory (`shm_size: '4.77gb'`)
- **Host Access**: Containers are configured with `host.docker.internal` mapping for communicating with the host machine
- **GCP Credentials**: Google Cloud Platform credentials are mounted from the host into each container
- **Container Network**: All containers are connected on the same Docker network for inter-service communication

```mermaid
flowchart TD
    subgraph "Resource Configuration"
        SharedMem["Shared Memory: 4.77GB"]
        GCPCreds["GCP Credentials Mount"]
        HostAccess["Host Access Configuration"]
        Network["Container Network"]
    end
    
    subgraph "Services"
        Activity["Activity Service"]
        Entity["Entity Service"]
        CPD["CPD gRPC Service"]
        EntityPost["Entity Postprocessor"]
    end
    
    SharedMem --> Activity
    SharedMem --> Entity
    SharedMem --> CPD
    SharedMem --> EntityPost
    
    GCPCreds --> Activity
    GCPCreds --> Entity
    GCPCreds --> CPD
    GCPCreds --> EntityPost
    
    HostAccess --> Activity
    HostAccess --> Entity
    HostAccess --> CPD
    HostAccess --> EntityPost
    
    Network --> Activity
    Network --> Entity
    Network --> CPD
    Network --> EntityPost
```

Sources: [ais/docker-compose.yml:12-97]()

## Health Monitoring

Each service has configured health checks to ensure they are running correctly:

- **HTTP Services** (Activity and Entity): 
  - Check interval: 1 second
  - Timeout: 1 second
  - Retries: 30
  - Method: TCP port check using netcat

- **gRPC Services** (CPD and Entity Postprocessor):
  - Check interval: 2 seconds
  - Timeout: 2 seconds
  - Retries: 120
  - Method: TCP port check using netcat

These health checks ensure that services are properly started and remain operational during deployment.

Sources: [ais/docker-compose.yml:24-100]()

## Environmental Requirements

The Atlantes deployment has the following environmental prerequisites:

1. Docker runtime environment with Docker Compose support
2. CUDA-capable GPU for optimal performance
3. Google Cloud Platform credentials for accessing GCP services
4. Sufficient system resources:
   - CPU: Multiple cores recommended
   - RAM: Minimum 8GB (16GB+ recommended)
   - Storage: At least 10GB for container images and data
   - GPU: NVIDIA GPU with CUDA 12.1 support (for optimal performance)

## Connectivity Architecture

The Atlantes services are designed to be accessed by client applications through their respective ports:

```mermaid
flowchart LR
    Client["Client Applications"] --> Port8000["Port 8000
    Activity Service
    HTTP Interface"]
    
    Client --> Port8001["Port 8001
    Entity Service
    HTTP Interface"]
    
    Client --> Port5206["Port 5206
    CPD Service
    gRPC Interface"]
    
    Client --> Port5207["Port 5207
    Entity Postprocessor
    gRPC Interface"]
    
    subgraph "Docker Network"
        Port8000 --> Activity["Activity Service Container"]
        Port8001 --> Entity["Entity Service Container"]
        Port5206 --> CPD["CPD Service Container"]
        Port5207 --> EntityPostProcessor["Entity Postprocessor Container"]
        
        Activity <--> Entity
        Activity <--> CPD
        Entity <--> EntityPostProcessor
    end
```

Sources: [ais/docker-compose.yml:18-91]()

---

