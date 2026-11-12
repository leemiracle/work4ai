<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/rslearn · page 8 Development and Deployment · fetched 2026-10-26 -->

# Development and Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/build-test.yml](.github/workflows/build-test.yml)
- [Dockerfile](Dockerfile)

</details>



This document covers the development workflow, continuous integration/continuous deployment (CI/CD) pipelines, containerization, testing infrastructure, and deployment procedures for the rslearn framework. It provides technical details on how code changes are built, tested, and deployed through automated GitHub Actions workflows and Docker-based infrastructure.

For information about the core ML training and inference workflows, see [Machine Learning Framework](#7). For dataset preparation and management procedures, see [Dataset Management](#5).

## CI/CD Pipeline Architecture

The rslearn project uses GitHub Actions for automated building, testing, and deployment. The primary workflow handles Docker image creation, comprehensive testing, and container registry publishing.

### GitHub Actions Workflow Structure

```mermaid
graph TD
    subgraph "Triggers"
        PUSH["Push to master"]
        PR["Pull Request Events"]
    end
    
    subgraph "Build Job"
        CHECKOUT["Checkout repository"]
        LOGIN["Login to ghcr.io"]
        META["Extract metadata"]
        CLEANUP["Cleanup disk space"]
        BUILD["Build and push Docker image"]
        STORE["Store image names"]
    end
    
    subgraph "Test Job"
        PULL["Pull latest image"]
        UNIT["Run Unit Tests"]
        GCP_AUTH["Authenticate GCP"]
        INTEGRATION["Run Integration Tests"]
        CLEAN["Cleanup resources"]
    end
    
    subgraph "Outputs"
        GHCR["ghcr.io registry"]
        RESULTS["Test results"]
    end
    
    PUSH --> CHECKOUT
    PR --> CHECKOUT
    
    CHECKOUT --> LOGIN
    LOGIN --> META
    META --> CLEANUP
    CLEANUP --> BUILD
    BUILD --> STORE
    
    STORE --> PULL
    PULL --> UNIT
    UNIT --> GCP_AUTH
    GCP_AUTH --> INTEGRATION
    INTEGRATION --> CLEAN
    
    BUILD --> GHCR
    INTEGRATION --> RESULTS
```

**Sources:** [.github/workflows/build-test.yml:1-131]()

### Pipeline Configuration Details

The CI/CD pipeline operates with the following key configurations:

| Component | Configuration | Purpose |
|-----------|---------------|---------|
| Registry | `ghcr.io` | GitHub Container Registry for Docker images |
| Concurrency | `${{ github.workflow }}-${{ github.ref }}` | Prevents parallel runs on same branch |
| Image Tags | SHA-based + latest | Immutable versioning with convenient latest tag |
| Test Environment | `test-bucket-rslearn` | Isolated GCS bucket for integration tests |

The workflow implements automatic cleanup procedures including Docker image pruning and disk space management to optimize runner performance.

**Sources:** [.github/workflows/build-test.yml:10-16](), [.github/workflows/build-test.yml:48-55]()

## Docker Infrastructure

The rslearn framework uses a multi-stage Docker setup based on PyTorch CUDA runtime for GPU-accelerated machine learning workloads.

### Container Architecture

```mermaid
graph TD
    subgraph "Base Image"
        PYTORCH["pytorch/pytorch:2.5.0-cuda11.8-cudnn9-runtime"]
    end
    
    subgraph "Dependency Installation"
        REQ1["requirements.txt"]
        REQ2["extra_requirements.txt"] 
        REQ3["test_requirements.txt"]
    end
    
    subgraph "Application Layer"
        COPY["Copy source code"]
        INSTALL["pip install rslearn"]
    end
    
    subgraph "Runtime Environment"
        WORKDIR["/rslearn working directory"]
        ENTRYPOINT["rslearn CLI available"]
    end
    
    PYTORCH --> REQ1
    REQ1 --> REQ2
    REQ2 --> REQ3
    REQ3 --> COPY
    COPY --> INSTALL
    INSTALL --> WORKDIR
    WORKDIR --> ENTRYPOINT
```

**Sources:** [Dockerfile:1-20]()

### Docker Build Process

The containerization follows a layered approach to optimize build caching:

1. **Base Layer**: PyTorch 2.5.0 with CUDA 11.8 and cuDNN 9 runtime
2. **Dependencies**: Sequential installation of `requirements.txt`, `extra_requirements.txt`, and `test_requirements.txt`
3. **Application**: Source code copy and package installation
4. **Configuration**: Working directory setup at `/rslearn`

The `--no-cache-dir` flag is used consistently to minimize image size by preventing pip cache accumulation.

**Sources:** [Dockerfile:10-19]()

## Testing Framework

The testing infrastructure implements a two-tier approach with unit tests and integration tests running in containerized environments.

### Test Execution Pipeline

```mermaid
graph TD
    subgraph "Unit Testing"
        UNIT_CMD["pytest -n auto tests/ -vv"]
        EXCLUDE1["--ignore tests/integration/"]
        EXCLUDE2["--ignore tests/unit/models/"]
    end
    
    subgraph "Integration Testing"
        INT_CMD["pytest tests/integration/"]
        EXCLUDE3["--ignore tests/integration/data_sources/"]
        GCP_CREDS["GCP credentials mounting"]
        ENV_VARS["Environment variables"]
    end
    
    subgraph "Test Environment"
        DOCKER_RUN["docker run --rm"]
        TEST_BUCKET["test-bucket-rslearn"]
        GCS_PROJECT["skylight-proto-1"]
    end
    
    UNIT_CMD --> EXCLUDE1
    EXCLUDE1 --> EXCLUDE2
    
    INT_CMD --> EXCLUDE3
    EXCLUDE3 --> GCP_CREDS
    GCP_CREDS --> ENV_VARS
    
    DOCKER_RUN --> TEST_BUCKET
    DOCKER_RUN --> GCS_PROJECT
```

**Sources:** [.github/workflows/build-test.yml:102-109](), [.github/workflows/build-test.yml:115-124]()

### Test Configuration

The testing framework uses the following key configurations:

| Test Type | Command | Exclusions | Environment |
|-----------|---------|------------|-------------|
| Unit | `pytest -n auto` | `tests/integration/`, `tests/unit/models/` | Container only |
| Integration | `pytest tests/integration/` | `tests/integration/data_sources/` | GCP credentials, test bucket |

Integration tests require Google Cloud Platform authentication through mounted service account credentials and access to the `test-bucket-rslearn` GCS bucket.

**Sources:** [.github/workflows/build-test.yml:97-101](), [.github/workflows/build-test.yml:110-113]()

## Deployment Process

The deployment process centers on automated Docker image publishing to GitHub Container Registry with tag-based versioning.

### Image Publishing Workflow

```mermaid
graph TD
    subgraph "Image Metadata"
        SHA_LONG["type=sha,format=long"]
        SHA_SHORT["type=sha,format=short"] 
        LATEST["type=raw,value=latest"]
    end
    
    subgraph "Registry Operations"
        LOGIN_GHCR["docker/login-action@v3"]
        METADATA["docker/metadata-action@v5"]
        BUILD_PUSH["docker/build-push-action@v6"]
    end
    
    subgraph "Output Processing"
        DIGEST["Build digest extraction"]
        LOWERCASE["Image name normalization"]
        OUTPUT_VARS["GitHub output variables"]
    end
    
    SHA_LONG --> METADATA
    SHA_SHORT --> METADATA
    LATEST --> METADATA
    
    LOGIN_GHCR --> BUILD_PUSH
    METADATA --> BUILD_PUSH
    
    BUILD_PUSH --> DIGEST
    DIGEST --> LOWERCASE
    LOWERCASE --> OUTPUT_VARS
```

**Sources:** [.github/workflows/build-test.yml:37-47](), [.github/workflows/build-test.yml:56-63]()

### Registry Configuration

The deployment uses GitHub Container Registry (`ghcr.io`) with the following naming convention:

- **Registry**: `ghcr.io/${{ github.repository }}`
- **Authentication**: GitHub token-based
- **Permissions**: Contents read, packages write
- **Tags**: SHA-based (long/short) plus latest for default branch

Image names are normalized to lowercase to comply with Docker registry requirements, and the full image digest is captured for downstream job dependencies.

**Sources:** [.github/workflows/build-test.yml:70-77]()

## Development Workflow

The development workflow integrates code changes through automated validation and containerized testing before deployment.

### Branch Protection and Testing

```mermaid
graph TD
    subgraph "Developer Actions"
        FEATURE["Feature branch"]
        COMMIT["Code changes"]
        PR_CREATE["Create pull request"]
    end
    
    subgraph "Automated Validation"
        TRIGGER["Workflow trigger"]
        BUILD_TEST["Build and test"]
        STATUS_CHECK["Status checks"]
    end
    
    subgraph "Merge Process"
        APPROVAL["Code review"]
        MERGE["Merge to master"]
        DEPLOY["Deploy latest"]
    end
    
    FEATURE --> COMMIT
    COMMIT --> PR_CREATE
    
    PR_CREATE --> TRIGGER
    TRIGGER --> BUILD_TEST
    BUILD_TEST --> STATUS_CHECK
    
    STATUS_CHECK --> APPROVAL
    APPROVAL --> MERGE
    MERGE --> DEPLOY
```

**Sources:** [.github/workflows/build-test.yml:3-8]()

### Environment Management

The development workflow maintains separate environments for different stages:

| Environment | Trigger | Purpose | Resources |
|-------------|---------|---------|-----------|
| Development | Pull request | Validation testing | Ephemeral containers |
| Production | Master branch | Latest deployment | `ghcr.io` registry |
| Testing | Both | Integration validation | GCS test bucket |

The workflow includes automatic cleanup procedures to prevent resource accumulation and manages concurrent execution through GitHub's concurrency controls.

**Sources:** [.github/workflows/build-test.yml:14-16](), [.github/workflows/build-test.yml:126-131]()