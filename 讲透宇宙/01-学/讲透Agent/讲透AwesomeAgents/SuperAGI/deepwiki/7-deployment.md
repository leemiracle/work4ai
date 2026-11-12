<!-- source: DeepWiki mcp.deepwiki.com · repo TransformerOptimus/SuperAGI · page 7 Deployment · fetched 2026-10-26 -->

# Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [.gitignore](.gitignore)
- [Dockerfile](Dockerfile)
- [Dockerfile-gpu](Dockerfile-gpu)
- [README.MD](README.MD)
- [config_template.yaml](config_template.yaml)
- [docker-compose-gpu.yml](docker-compose-gpu.yml)
- [docker-compose.yaml](docker-compose.yaml)
- [entrypoint.sh](entrypoint.sh)
- [entrypoint_celery.sh](entrypoint_celery.sh)
- [gui/.dockerignore](gui/.dockerignore)
- [gui/Dockerfile](gui/Dockerfile)
- [gui/DockerfileProd](gui/DockerfileProd)
- [gui/next.config.js](gui/next.config.js)
- [gui/pages/Content/Agents/ActionConsole.js](gui/pages/Content/Agents/ActionConsole.js)
- [gui/pages/Content/Agents/RunHistory.js](gui/pages/Content/Agents/RunHistory.js)
- [nginx/default.conf](nginx/default.conf)
- [requirements.txt](requirements.txt)
- [superagi/helper/llm_loader.py](superagi/helper/llm_loader.py)
- [superagi/llms/llm_model_factory.py](superagi/llms/llm_model_factory.py)
- [superagi/llms/local_llm.py](superagi/llms/local_llm.py)
- [superagi/types/model_source_types.py](superagi/types/model_source_types.py)
- [tests/unit_tests/tools/duck_duck_go/test_duckduckgo_results.py](tests/unit_tests/tools/duck_duck_go/test_duckduckgo_results.py)
- [wait-for-it.sh](wait-for-it.sh)

</details>



This page provides a comprehensive guide to deploying SuperAGI in various environments. It covers the requirements, configuration options, and step-by-step procedures for setting up and running the system. For specific information about configuring models, please see [LLM Integration](#6) and for detailed configuration settings, refer to [Configuration Options](#7.2).

## Deployment Options Overview

SuperAGI offers multiple deployment options to accommodate different user needs:

```mermaid
flowchart TD
    Start["Deployment Choice"] --> Cloud["SuperAGI Cloud"]
    Start --> LocalDocker["Local Docker Deployment"]
    Start --> DigitalOcean["DigitalOcean Deployment"]
    
    LocalDocker --> Standard["Standard Docker Deployment"]
    LocalDocker --> GPU["GPU-Accelerated Docker Deployment"]
    
    Cloud --> |"Managed Service"| NoSetup["No Setup Required\nVisit app.superagi.com"]
    Standard --> |"Basic Setup"| CPUBased["CPU-Based\nFor General Use"]
    GPU --> |"Advanced Setup"| GPUAccel["GPU-Accelerated\nFor Local LLM Integration"]
    DigitalOcean --> |"One-Click Deploy"| DODeploy["DigitalOcean App Platform"]
```

Sources: [README.MD:100-147]()

## Prerequisites

Before deploying SuperAGI, ensure you have the following prerequisites:

| Requirement | Standard Deployment | GPU Deployment | Notes |
|-------------|---------------------|----------------|-------|
| Docker | Required | Required | Docker Desktop or Docker Engine |
| Docker Compose | Required | Required | Usually included with Docker Desktop |
| Git | Required | Required | To clone the repository |
| NVIDIA GPU | Not required | Required | With CUDA support |
| NVIDIA Drivers | Not required | Required | Compatible with CUDA 12.1.1 |
| Storage Space | ~2GB minimum | ~10GB minimum | For Docker images and data |

Sources: [README.MD:114-128](), [Dockerfile:1-39](), [Dockerfile-gpu:1-45]()

## Standard Docker Deployment

The standard deployment uses Docker Compose to run SuperAGI on CPU:

1. Clone the repository:
```bash
git clone https://github.com/TransformerOptimus/SuperAGI.git
```

2. Navigate to the cloned directory:
```bash
cd SuperAGI
```

3. Create a configuration file:
```bash
cp config_template.yaml config.yaml
```

4. Edit the `config.yaml` file to add your API keys and customize settings

5. Start the application:
```bash
docker compose -f docker-compose.yaml up --build
```

6. Access the application at http://localhost:3000

```mermaid
graph TD
    subgraph "SuperAGI Deployment"
        User["User Browser"] -->|"HTTP/Port 3000"| Proxy["Nginx Proxy"]
        
        Proxy -->|"Frontend Requests"| GUI["GUI Container"]
        Proxy -->|"API Requests /api/*"| Backend["Backend Container"]
        
        Backend -->|"Database Operations"| Postgres["super__postgres\nPostgreSQL Database"]
        Backend -->|"Queue Jobs"| Redis["super__redis\nRedis Server"]
        
        Celery["Celery Worker"] -->|"Process Jobs"| Redis
        Celery -->|"Database Operations"| Postgres
        Celery -->|"File Operations"| Storage["File Storage\n(workspace/ directory)"]
    end
```

Sources: [docker-compose.yaml:1-76](), [README.MD:114-146](), [nginx/default.conf:1-27]()

## GPU-Accelerated Deployment

For users who want to run local LLMs with GPU acceleration:

1. Follow steps 1-4 from the standard deployment

2. Start the application with the GPU-enabled compose file:
```bash
docker compose -f docker-compose-gpu.yml up --build
```

3. Access the application at http://localhost:3000

4. Update your `config.yaml` file to use local LLMs by uncommenting:
```yaml
#OPENAI_API_BASE: "http://super__tgwui:5001/v1"
```

The GPU deployment includes additional CUDA libraries and configurations to leverage NVIDIA GPUs for accelerated performance when running local language models.

```mermaid
graph TD
    subgraph "GPU Deployment Architecture"
        User["User Browser"] -->|"HTTP/Port 3000"| Proxy["Nginx Proxy"]
        
        Proxy -->|"Frontend Requests"| GUI["GUI Container"]
        Proxy -->|"API Requests /api/*"| Backend["Backend Container\nwith CUDA support"]
        
        Backend -->|"Database Operations"| Postgres["super__postgres\nPostgreSQL Database"]
        Backend -->|"Queue Jobs"| Redis["super__redis\nRedis Server"]
        Backend -->|"GPU Operations"| GPU["NVIDIA GPU\nvia CUDA Libraries"]
        
        Celery["Celery Worker\nwith CUDA support"] -->|"Process Jobs"| Redis
        Celery -->|"Database Operations"| Postgres
        Celery -->|"GPU Operations"| GPU
        Celery -->|"File Operations"| Storage["File Storage\n(workspace/ directory)"]
        
        LLMHelper["LLMLoader Class"] -->|"Load Local Models"| GPU
    end
```

Sources: [docker-compose-gpu.yml:1-96](), [Dockerfile-gpu:1-45](), [superagi/helper/llm_loader.py:1-38](), [superagi/llms/local_llm.py:1-92]()

## Container Architecture

The SuperAGI deployment consists of the following containers:

| Container | Purpose | Source |
|-----------|---------|--------|
| backend | FastAPI server that handles API requests | [Dockerfile:1-39]() |
| celery | Background task processing | [entrypoint_celery.sh:1-9]() |
| gui | Next.js frontend application | [gui/Dockerfile:1-20]() |
| super__redis | Redis for task queuing and caching | [docker-compose.yaml:35-43]() |
| super__postgres | PostgreSQL database for data storage | [docker-compose.yaml:45-57]() |
| proxy | Nginx proxy for routing requests | [nginx/default.conf:1-27]() |

The containers communicate over a Docker network and use volumes for persistent storage:

```mermaid
graph TB
    subgraph "Volume Management"
        PGVol["superagi_postgres_data\nPersistent Volume"] <-->|"Store Database Data"| PG["super__postgres"]
        RedisVol["redis_data\nPersistent Volume"] <-->|"Store Redis Data"| Redis["super__redis"]
        WorkspaceVol["./workspace\nHost-Mounted Volume"] <-->|"Store Agent Resources"| Celery["celery"]
    end
    
    subgraph "Network Communication"
        Backend["backend"] <-->|"API Requests"| Proxy["proxy"]
        GUI["gui"] <-->|"Web Requests"| Proxy
        Backend <-->|"Database Queries"| PG
        Backend <-->|"Queue Management"| Redis
        Celery <-->|"Task Processing"| Redis
        Celery <-->|"Data Storage"| PG
    end
    
    subgraph "External Access"
        User["External User"] -->|"HTTP Port 3000"| Proxy
    end
```

Sources: [docker-compose.yaml:1-76](), [docker-compose-gpu.yml:1-96]()

## Configuration

SuperAGI is configured through the `config.yaml` file, which contains settings for:

1. API keys for external services (OpenAI, Pinecone, etc.)
2. Database connection details
3. Storage configuration (local or S3)
4. LLM provider settings
5. Tool-specific configurations

The configuration file is loaded at startup and used throughout the application. Any changes require a restart of the containers.

```mermaid
graph LR
    subgraph "Configuration Flow"
        ConfigFile["config.yaml"] -->|"Read at Startup"| Backend["Backend Container"]
        ConfigFile -->|"Read at Startup"| Celery["Celery Container"]
        
        subgraph "Key Configuration Sections"
            APIKeys["API Keys\n(OpenAI, Pinecone, etc.)"]
            DBConfig["Database Configuration"]
            StorageConfig["Storage Configuration\n(File or S3)"]
            ToolConfig["Tool Configuration"]
            ModelConfig["LLM Model Configuration"]
        end
        
        ConfigFile ---|"Contains"| APIKeys
        ConfigFile ---|"Contains"| DBConfig
        ConfigFile ---|"Contains"| StorageConfig
        ConfigFile ---|"Contains"| ToolConfig
        ConfigFile ---|"Contains"| ModelConfig
    end
```

Sources: [config_template.yaml:1-126]()

## Cloud Deployment

### SuperAGI Cloud

For users who prefer a managed solution without setup complexity:

1. Visit [SuperAGI Cloud](https://app.superagi.com)
2. Log in using your GitHub account
3. Configure your API keys in account settings
4. Start creating and running agents

### DigitalOcean One-Click Deployment

SuperAGI provides a one-click deployment option for DigitalOcean:

1. Click the "Deploy to DigitalOcean" button in the README
2. Log in to your DigitalOcean account
3. Configure the deployment options
4. Deploy the application

This option automates the deployment process on DigitalOcean's App Platform.

Sources: [README.MD:144-147]()

## Environment Variables

SuperAGI uses several environment variables that can be set in the `config.yaml` file or in your environment:

| Variable | Purpose | Default | Notes |
|----------|---------|---------|-------|
| OPENAI_API_KEY | API key for OpenAI | None | Required for OpenAI models |
| PINECONE_API_KEY | API key for Pinecone | None | For vector database integration |
| STORAGE_TYPE | Storage backend type | "FILE" | "FILE" or "S3" |
| DB_URL | Database connection string | postgresql://superagi:password@super__postgres:5432/super_agi_main | For PostgreSQL connection |
| REDIS_URL | Redis connection string | "super__redis:6379" | For Redis connection |
| GPU_LAYERS | GPU layers for local LLMs | None | Used in GPU deployment |

Sources: [config_template.yaml:1-126](), [docker-compose.yaml:1-76](), [docker-compose-gpu.yml:1-96]()

## External Resource Directory

By default, SuperAGI stores resources in the `workspace` directory. For custom locations, you can set the `EXTERNAL_RESOURCE_DIR` environment variable:

```bash
EXTERNAL_RESOURCE_DIR=/custom/path docker compose -f docker-compose.yaml up
```

This is especially useful when you need to persist agent inputs/outputs across container restarts or when sharing resources between multiple SuperAGI instances.

Sources: [docker-compose.yaml:15-16](), [docker-compose-gpu.yml:15-16]()

## LLM Integration Architecture

SuperAGI supports multiple LLM providers, including local LLMs that can leverage GPU acceleration:

```mermaid
graph TD
    subgraph "LLM Provider Integration"
        LLMFactory["LLM Model Factory\nllm_model_factory.py"] --> OpenAI["OpenAI Provider"]
        LLMFactory --> GooglePalm["Google Palm Provider"]
        LLMFactory --> Replicate["Replicate Provider"]
        LLMFactory --> HuggingFace["Hugging Face Provider"]
        LLMFactory --> LocalLLM["Local LLM Provider"]
        
        LocalLLM -->|"GPU Acceleration"| LLMLoader["LLMLoader\nllm_loader.py"]
        LLMLoader -->|"Load Models"| Llama["Llama CPP\nPython Binding"]
    end
    
    Agent["Agent Executor"] -->|"Get Model"| LLMFactory
    Config["config.yaml"] -->|"Configure"| LLMFactory
```

Sources: [superagi/llms/llm_model_factory.py:1-55](), [superagi/helper/llm_loader.py:1-38](), [superagi/llms/local_llm.py:1-92](), [superagi/types/model_source_types.py:1-33]()

## Troubleshooting Deployment

Common issues and their solutions:

1. **Container startup failures**:
   - Check Docker logs: `docker compose logs`
   - Ensure correct configuration in `config.yaml`
   - Verify port 3000 is not in use by another application

2. **Database connection issues**:
   - Ensure PostgreSQL container is running: `docker compose ps`
   - Check database connection string in `config.yaml`

3. **GPU not detected in GPU deployment**:
   - Verify NVIDIA drivers are installed and working
   - Check NVIDIA Docker runtime is installed
   - Run `nvidia-smi` to confirm GPU is accessible

4. **API key errors**:
   - Ensure all required API keys are correctly set in `config.yaml`
   - Check for spaces or special characters in API keys

5. **File permission issues**:
   - Ensure the `workspace` directory has appropriate permissions
   - For custom external resource directories, check permissions

Sources: [README.MD:190-196](), [entrypoint.sh:1-14](), [wait-for-it.sh:1-183]()

## Deployment Security Considerations

When deploying SuperAGI, consider these security best practices:

1. **API Keys Protection**:
   - Do not commit `config.yaml` with API keys to version control
   - Use environment variables for sensitive information in production

2. **Network Security**:
   - By default, SuperAGI exposes port 3000
   - Use a reverse proxy with HTTPS for production deployments
   - Consider network isolation for production environments

3. **Database Security**:
   - Change the default PostgreSQL password in production
   - Consider using a managed database service for production

4. **Resource Limits**:
   - Set appropriate container resource limits for CPU and memory
   - Monitor resource usage in production environments

Sources: [docker-compose.yaml:1-76](), [config_template.yaml:1-126](), [.gitignore:1-23]()

## System Requirements

Minimum hardware requirements for running SuperAGI:

| Deployment Type | CPU | RAM | Storage | GPU |
|-----------------|-----|-----|---------|-----|
| Standard | 2 cores | 4GB | 10GB | Not required |
| With Local LLMs | 4 cores | 8GB | 20GB | NVIDIA GPU with 8GB+ VRAM |
| Production | 4+ cores | 16GB+ | 40GB+ | Optional |

Sources: [requirements.txt:1-161](), [Dockerfile:1-39](), [Dockerfile-gpu:1-45]()

---

