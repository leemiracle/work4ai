<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/genesys · page 7 Deployment and Infrastructure · fetched 2026-10-26 -->

# Deployment and Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.skiff/cloudbuild-deploy.yaml](.skiff/cloudbuild-deploy.yaml)
- [.skiff/webapp.jsonnet](.skiff/webapp.jsonnet)
- [Dockerfile](Dockerfile)

</details>



This document provides a comprehensive guide to containerization, Kubernetes deployment, and CI/CD pipeline for the Genesys system. It covers Docker container build process, Kubernetes resource templates, and the automated deployment workflow using Google Cloud Build.

For application-specific configuration management, see page 6 (Configuration and Environment). For distributed node coordination, see page 5.4 (Distributed Coordination).

## 7.1 Docker Containerization

The Genesys system is containerized using Docker with GPU support for machine learning workloads. The container configuration is defined in the root `Dockerfile`.

### Base Image and Dependencies

The container uses a CUDA-enabled base image to support GPU-accelerated training and inference operations:

```dockerfile
FROM ghcr.io/allenai/cuda:11.8-cudnn8-dev-ubuntu20.04
```

The build process installs PyTorch with CPU-only dependencies initially, then adds the full requirements stack:

- PyTorch 2.4.1 for deep learning operations
- Hugging Face transformers and datasets
- Streamlit for the web interface
- Custom dependencies including `paperswithcode-client` and `hf_xet`

### Environment Setup

The container establishes standard directory structures and environment variables:

| Variable | Default Path | Purpose |
|----------|--------------|---------|
| `DATA_DIR` | `/root/genesys/data` | Training data and datasets |
| `CKPT_DIR` | `/root/genesys/ckpt` | Model checkpoints and artifacts |
| `WORKDIR` | `/root/genesys` | Application root directory |

### Container Lifecycle

The container exposes port 8501 for the Streamlit application and includes health checks via the `/_stcore/health` endpoint. The default entrypoint runs `genesys gui` to start the web interface.

**Container Build and Deployment Architecture**

```mermaid
graph TB
    subgraph "Build Process"
        DOCKERFILE["Dockerfile"]
        BASE_IMAGE["ghcr.io/allenai/cuda:11.8-cudnn8-dev-ubuntu20.04"]
        REQUIREMENTS["requirements.txt"]
        DEMO_DATA["scripts/demo_data_download.py"]
    end
    
    subgraph "Container Runtime"
        CONTAINER["genesys-demo Container"]
        STREAMLIT_PORT["Port 8501"]
        HEALTH_CHECK["/_stcore/health"]
        ENV_VARS["Environment Variables"]
    end
    
    subgraph "Registry"
        GCP_REGISTRY["us-central1-docker.pkg.dev/model-discovery/genesys"]
        IMAGE_TAG["genesys-demo-gcp:latest"]
    end
    
    BASE_IMAGE --> DOCKERFILE
    REQUIREMENTS --> DOCKERFILE
    DEMO_DATA --> DOCKERFILE
    DOCKERFILE --> CONTAINER
    
    CONTAINER --> STREAMLIT_PORT
    CONTAINER --> HEALTH_CHECK
    CONTAINER --> ENV_VARS
    
    CONTAINER --> GCP_REGISTRY
    GCP_REGISTRY --> IMAGE_TAG
```

Sources: [Dockerfile:1-74]()

## 7.2 Kubernetes Deployment Configuration

The Kubernetes deployment is managed through Jsonnet templates that generate environment-specific configurations. The main template is `webapp.jsonnet` which uses utility functions from `util.libsonnet`.

### Resource Configuration

The deployment creates several Kubernetes resources:

**Core Resources:**
- `Namespace`: Isolates application resources
- `Deployment`: Manages pod replicas and rolling updates
- `Service`: Provides internal load balancing
- `Ingress`: Handles external traffic routing
- `PodDisruptionBudget`: Ensures availability during updates

**Multi-Domain Support:**
The system supports multiple TLD configurations:
- `.allenai.org` domains (primary)
- `.allen.ai` domains (secondary)
- `.semanticscholar.org` domains (conditional)

### GPU and Resource Management

The deployment template includes sophisticated GPU configuration:

```jsonnet
local gpuLimits = if gpuInConfig then
    if config.gpu == "a100-40gbx2" then
        { 'nvidia.com/gpu': 2 }
    else if config.gpu == "t4x4" then
        { 'nvidia.com/gpu': 4 }
    else
        { 'nvidia.com/gpu': 1 }
else {};
```

**Resource Allocation:**
- CPU: 8 cores requested
- Memory: 16GB requested
- GPU: Dynamic allocation based on configuration

### High Availability Configuration

The deployment implements pod anti-affinity rules to ensure instances are distributed across nodes:

```jsonnet
local antiAffinityLabels = {
    onlyOneOfPerNode: config.appName + '-' + env
};
```

**Kubernetes Deployment Architecture**

```mermaid
graph TB
    subgraph "Configuration Layer"
        CONFIG["skiff.json"]
        WEBAPP_JSONNET[".skiff/webapp.jsonnet"]
        UTIL_LIBSONNET[".skiff/util.libsonnet"]
    end
    
    subgraph "Kubernetes Resources"
        NAMESPACE["Namespace"]
        DEPLOYMENT["Deployment"]
        SERVICE["Service"]
        INGRESS_ALLENAI["Ingress (.allenai.org)"]
        INGRESS_ALLEN["Ingress (.allen.ai)"]
        INGRESS_SCHOLAR["Ingress (.semanticscholar.org)"]
        PDB["PodDisruptionBudget"]
    end
    
    subgraph "Pod Configuration"
        CONTAINER_SPEC["Container Spec"]
        RESOURCE_LIMITS["Resource Limits"]
        GPU_CONFIG["GPU Configuration"]
        ANTI_AFFINITY["Anti-Affinity Rules"]
        HEALTH_PROBES["Health Probes"]
    end
    
    subgraph "External Dependencies"
        TLS_CERTS["TLS Certificates"]
        SECRETS["Kubernetes Secrets"]
        LOAD_BALANCER["Load Balancer"]
    end
    
    CONFIG --> WEBAPP_JSONNET
    UTIL_LIBSONNET --> WEBAPP_JSONNET
    WEBAPP_JSONNET --> NAMESPACE
    WEBAPP_JSONNET --> DEPLOYMENT
    WEBAPP_JSONNET --> SERVICE
    WEBAPP_JSONNET --> INGRESS_ALLENAI
    WEBAPP_JSONNET --> INGRESS_ALLEN
    WEBAPP_JSONNET --> INGRESS_SCHOLAR
    WEBAPP_JSONNET --> PDB
    
    DEPLOYMENT --> CONTAINER_SPEC
    CONTAINER_SPEC --> RESOURCE_LIMITS
    CONTAINER_SPEC --> GPU_CONFIG
    CONTAINER_SPEC --> ANTI_AFFINITY
    CONTAINER_SPEC --> HEALTH_PROBES
    
    INGRESS_ALLENAI --> TLS_CERTS
    INGRESS_ALLEN --> TLS_CERTS
    INGRESS_SCHOLAR --> TLS_CERTS
    CONTAINER_SPEC --> SECRETS
    SERVICE --> LOAD_BALANCER
```

Sources: [.skiff/webapp.jsonnet:1-512]()

## Environment and Secret Management

The deployment manages sensitive configuration through Kubernetes secrets. All API keys and paths are injected as environment variables:

### Secret Configuration

| Environment Variable | Secret Key | Purpose |
|---------------------|------------|---------|
| `CKPT_DIR` | `openaikey.CKPT_DIR` | Model checkpoint storage path |
| `DATA_DIR` | `openaikey.DATA_DIR` | Training data storage path |
| `MY_OPENAI_KEY` | `openaikey.MY_OPENAI_KEY` | OpenAI API authentication |
| `PINECONE_API_KEY` | `openaikey.PINECONE_API_KEY` | Pinecone vector search |
| `S2_API_KEY` | `openaikey.S2_API_KEY` | Semantic Scholar API |

### Network and Security

The deployment enforces HTTPS through automatic SSL redirect and supports authentication annotations for different domains. Health checks are implemented at both the proxy level (port 8080) and application level (port 8501).

**Environment and Secret Management Flow**

```mermaid
graph LR
    subgraph "Secret Sources"
        K8S_SECRETS["Kubernetes Secrets"]
        OPENAI_SECRET["openaikey Secret"]
    end
    
    subgraph "Environment Injection"
        ENV_VARS["Environment Variables"]
        CKPT_DIR_VAR["CKPT_DIR"]
        DATA_DIR_VAR["DATA_DIR"]
        OPENAI_KEY_VAR["MY_OPENAI_KEY"]
        PINECONE_KEY_VAR["PINECONE_API_KEY"]
        S2_KEY_VAR["S2_API_KEY"]
    end
    
    subgraph "Application Runtime"
        CONTAINER_RUNTIME["Container Runtime"]
        GENESYS_APP["Genesys Application"]
        EXTERNAL_APIS["External APIs"]
    end
    
    K8S_SECRETS --> OPENAI_SECRET
    OPENAI_SECRET --> ENV_VARS
    ENV_VARS --> CKPT_DIR_VAR
    ENV_VARS --> DATA_DIR_VAR
    ENV_VARS --> OPENAI_KEY_VAR
    ENV_VARS --> PINECONE_KEY_VAR
    ENV_VARS --> S2_KEY_VAR
    
    CKPT_DIR_VAR --> CONTAINER_RUNTIME
    DATA_DIR_VAR --> CONTAINER_RUNTIME
    OPENAI_KEY_VAR --> CONTAINER_RUNTIME
    PINECONE_KEY_VAR --> CONTAINER_RUNTIME
    S2_KEY_VAR --> CONTAINER_RUNTIME
    
    CONTAINER_RUNTIME --> GENESYS_APP
    GENESYS_APP --> EXTERNAL_APIS
```

Sources: [.skiff/webapp.jsonnet:377-454]()

## Network Configuration and Load Balancing

The system implements sophisticated networking with multiple ingress configurations for different domains and TLS termination.

### Port Configuration

| Service | Port | Purpose |
|---------|------|---------|
| Proxy | 8080 | NGINX proxy endpoint |
| Application | 8501 | Streamlit application |
| Health Check | 8501 | Application health monitoring |

### Ingress and TLS

The deployment creates separate ingress resources for each supported domain with automated TLS certificate management through Let's Encrypt integration.

**Network Architecture and Traffic Flow**

```mermaid
graph TB
    subgraph "External Traffic"
        INTERNET["Internet Traffic"]
        DOMAIN_ALLENAI["*.allenai.org"]
        DOMAIN_ALLEN["*.allen.ai"]
        DOMAIN_SCHOLAR["*.semanticscholar.org"]
    end
    
    subgraph "Load Balancing Layer"
        INGRESS_CONTROLLER["NGINX Ingress Controller"]
        TLS_TERMINATION["TLS Termination"]
        SSL_REDIRECT["SSL Redirect"]
    end
    
    subgraph "Kubernetes Services"
        SERVICE_8080["Service Port 8080"]
        LOAD_BALANCER_SVC["Load Balancer"]
    end
    
    subgraph "Pod Network"
        POD_REPLICA_1["Pod Replica 1"]
        POD_REPLICA_2["Pod Replica 2"]
        POD_REPLICA_N["Pod Replica N"]
        APP_PORT_8501["Application Port 8501"]
    end
    
    subgraph "Health Monitoring"
        READINESS_PROBE["Readiness Probe"]
        HEALTH_ENDPOINT["/?check=rdy"]
    end
    
    INTERNET --> DOMAIN_ALLENAI
    INTERNET --> DOMAIN_ALLEN
    INTERNET --> DOMAIN_SCHOLAR
    
    DOMAIN_ALLENAI --> INGRESS_CONTROLLER
    DOMAIN_ALLEN --> INGRESS_CONTROLLER
    DOMAIN_SCHOLAR --> INGRESS_CONTROLLER
    
    INGRESS_CONTROLLER --> TLS_TERMINATION
    TLS_TERMINATION --> SSL_REDIRECT
    SSL_REDIRECT --> SERVICE_8080
    
    SERVICE_8080 --> LOAD_BALANCER_SVC
    LOAD_BALANCER_SVC --> POD_REPLICA_1
    LOAD_BALANCER_SVC --> POD_REPLICA_2
    LOAD_BALANCER_SVC --> POD_REPLICA_N
    
    POD_REPLICA_1 --> APP_PORT_8501
    POD_REPLICA_2 --> APP_PORT_8501
    POD_REPLICA_N --> APP_PORT_8501
    
    APP_PORT_8501 --> READINESS_PROBE
    READINESS_PROBE --> HEALTH_ENDPOINT
```

Sources: [.skiff/webapp.jsonnet:125-190](), [.skiff/webapp.jsonnet:462-481]()

## Scaling and Replica Management

The deployment implements environment-specific scaling policies with production deployments running multiple replicas for high availability.

### Replica Configuration

```jsonnet
local numReplicas = if env == 'prod' then config.replicas.prod else 1;
```

### Rolling Update Strategy

The deployment uses a rolling update strategy with `maxSurge` set to `numReplicas` to enable faster deployments while maintaining availability.

### Pod Disruption Budget

A `PodDisruptionBudget` ensures at least one replica remains available during maintenance operations when multiple replicas are running.

Sources: [.skiff/webapp.jsonnet:52-53](), [.skiff/webapp.jsonnet:280-285](), [.skiff/webapp.jsonnet:483-497]()

---

