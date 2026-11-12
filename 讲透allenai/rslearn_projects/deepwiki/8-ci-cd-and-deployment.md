<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/rslearn_projects · page 8 CI/CD and Deployment · fetched 2026-10-26 -->

# CI/CD and Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/landsat_vessel.yaml](.github/workflows/landsat_vessel.yaml)
- [.github/workflows/publish_project_docker_image.yaml](.github/workflows/publish_project_docker_image.yaml)
- [.github/workflows/sentinel2_vessel.yaml](.github/workflows/sentinel2_vessel.yaml)
- [rslp/sentinel2_vessels/Dockerfile](rslp/sentinel2_vessels/Dockerfile)
- [rslp/sentinel2_vessels/docker-compose.yaml](rslp/sentinel2_vessels/docker-compose.yaml)

</details>



This document covers the continuous integration, continuous deployment (CI/CD), and deployment infrastructure for the rslearn_projects repository. The CI/CD system automates building, testing, and publishing Docker images for various applications, primarily using GitHub Actions workflows and Docker containerization.

The deployment system supports multiple applications with standardized patterns for container publishing to GitHub Container Registry (GHCR) and integration with Beaker compute clusters. For information about the distributed worker system and job orchestration, see [Distributed Worker System](#2.4). For application-specific deployment details, see [Forest Loss Driver System](#3) and [Vessel Detection Systems](#4).

## CI/CD Architecture Overview

The CI/CD system follows a modular architecture with reusable workflows and standardized containerization patterns across all applications.

### CI/CD Workflow Architecture

```mermaid
graph TB
    subgraph "Trigger Events"
        manual_trigger["workflow_dispatch"]
        tag_push["Tag Push Events"]
        landsat_tag["landsat_vessels_v*"]
        sentinel2_tag["sentinel2_vessels_v*"]
    end
    
    subgraph "Project-Specific Workflows"
        landsat_workflow["landsat_vessel.yaml"]
        sentinel2_workflow["sentinel2_vessel.yaml"]
    end
    
    subgraph "Reusable Workflow"
        publish_workflow["publish_project_docker_image.yaml"]
        checkout_step["Checkout repository"]
        version_step["Extract version from tag"]
        login_step["Log in to GHCR"]
        build_push_step["Build and Push Docker Image"]
    end
    
    subgraph "Outputs"
        ghcr_registry["GitHub Container Registry"]
        sha_tagged["Image:sha-{SHORT_SHA}"]
        version_tagged["Image:{LATEST_TAG}"]
    end
    
    manual_trigger --> landsat_workflow
    manual_trigger --> sentinel2_workflow
    
    tag_push --> landsat_tag
    tag_push --> sentinel2_tag
    landsat_tag --> landsat_workflow
    sentinel2_tag --> sentinel2_workflow
    
    landsat_workflow --> publish_workflow
    sentinel2_workflow --> publish_workflow
    
    publish_workflow --> checkout_step
    checkout_step --> version_step
    version_step --> login_step
    login_step --> build_push_step
    
    build_push_step --> ghcr_registry
    ghcr_registry --> sha_tagged
    ghcr_registry --> version_tagged
```

Sources: [.github/workflows/landsat_vessel.yaml:1-15](), [.github/workflows/sentinel2_vessel.yaml:1-15](), [.github/workflows/publish_project_docker_image.yaml:1-62]()

### Docker Build and Deployment Flow

```mermaid
graph LR
    subgraph "Source Code"
        dockerfile["Dockerfile"]
        docker_compose["docker-compose.yaml"]
        base_dockerfile["Base Dockerfile"]
    end
    
    subgraph "Build Process"
        base_build["Build base-image:latest"]
        compose_build["docker compose build"]
        app_build["Build application image"]
    end
    
    subgraph "Tagging Strategy"
        sha_tag["Tag with sha-{SHORT_SHA}"]
        version_tag["Tag with {LATEST_TAG}"]
    end
    
    subgraph "Registry"
        ghcr_push["Push to ghcr.io/allenai"]
        image_variants["Multiple image tags"]
    end
    
    subgraph "Deployment"
        beaker_deploy["Beaker Platform"]
        api_services["FastAPI Services"]
        worker_nodes["Distributed Workers"]
    end
    
    dockerfile --> base_build
    docker_compose --> compose_build
    base_dockerfile --> base_build
    
    base_build --> app_build
    compose_build --> app_build
    
    app_build --> sha_tag
    app_build --> version_tag
    
    sha_tag --> ghcr_push
    version_tag --> ghcr_push
    ghcr_push --> image_variants
    
    image_variants --> beaker_deploy
    image_variants --> api_services
    image_variants --> worker_nodes
```

Sources: [.github/workflows/publish_project_docker_image.yaml:54-61](), [rslp/sentinel2_vessels/docker-compose.yaml:1-30]()

## GitHub Actions Workflows

The repository uses a standardized approach to CI/CD with project-specific trigger workflows that call a reusable workflow for Docker image publishing.

### Project-Specific Workflows

Each application maintains its own workflow file that defines trigger conditions and calls the shared publishing workflow:

| Application | Workflow File | Tag Pattern | Image Name |
|-------------|---------------|-------------|------------|
| Landsat Vessels | `landsat_vessel.yaml` | `landsat_vessels_v*` | `landsat-vessel-detection` |
| Sentinel-2 Vessels | `sentinel2_vessel.yaml` | `sentinel2_vessels_v*` | `sentinel2-vessel-detection` |

The workflows support two trigger mechanisms:
- **Manual Trigger**: `workflow_dispatch` allows manual execution
- **Tag-Based Trigger**: Automatic execution when version tags are pushed

Sources: [.github/workflows/landsat_vessel.yaml:3-14](), [.github/workflows/sentinel2_vessel.yaml:3-14]()

### Reusable Publishing Workflow

The `publish_project_docker_image.yaml` workflow implements the core CI/CD logic:

```mermaid
graph TB
    subgraph "Workflow Inputs"
        rslp_project["rslp_project (string)"]
        image_name["image_name (string)"]
    end
    
    subgraph "Environment Variables"
        registry["REGISTRY: ghcr.io"]
        org_name["ORG_NAME: allenai"]
    end
    
    subgraph "Workflow Steps"
        step1["Checkout repository"]
        step2["Fetch tags"]
        step3["Extract version and SHA"]
        step4["Log in to GHCR"]
        step5["Build and Push Docker Image"]
    end
    
    subgraph "Version Extraction"
        latest_tag["LATEST_TAG from git tags"]
        tag_commit["TAG_COMMIT from git rev-list"]
        short_sha["SHORT_SHA from git rev-parse"]
    end
    
    subgraph "Docker Operations"
        compose_build["docker compose build"]
        tag_sha["Tag with sha-{SHORT_SHA}"]
        tag_version["Tag with {LATEST_TAG}"]
        push_images["Push both tags to GHCR"]
    end
    
    rslp_project --> step1
    image_name --> step1
    registry --> step4
    org_name --> step5
    
    step1 --> step2
    step2 --> step3
    step3 --> latest_tag
    step3 --> tag_commit
    step3 --> short_sha
    step3 --> step4
    step4 --> step5
    
    step5 --> compose_build
    compose_build --> tag_sha
    compose_build --> tag_version
    tag_sha --> push_images
    tag_version --> push_images
```

Sources: [.github/workflows/publish_project_docker_image.yaml:6-13](), [.github/workflows/publish_project_docker_image.yaml:36-44](), [.github/workflows/publish_project_docker_image.yaml:54-61]()

## Docker Containerization

The containerization strategy uses a multi-stage approach with a shared base image and application-specific containers.

### Container Architecture

```mermaid
graph TB
    subgraph "Base Infrastructure"
        root_dockerfile["Root Dockerfile"]
        base_image["base-image:latest"]
        python_env["Python Environment"]
        rslearn_deps["rslearn Dependencies"]
    end
    
    subgraph "Application Containers"
        app_dockerfile["Application Dockerfile"]
        app_compose["docker-compose.yaml"]
        app_image["Application Image"]
    end
    
    subgraph "Runtime Configuration"
        env_vars["Environment Variables"]
        port_mapping["Port Mapping (5555)"]
        gpu_access["GPU Access"]
        shared_memory["Shared Memory (15G)"]
    end
    
    subgraph "Published Images"
        ghcr_images["GHCR Images"]
        tagged_variants["Multiple Tags"]
    end
    
    root_dockerfile --> base_image
    base_image --> python_env
    python_env --> rslearn_deps
    
    app_dockerfile --> app_image
    app_compose --> app_image
    base_image --> app_image
    
    env_vars --> app_image
    port_mapping --> app_image
    gpu_access --> app_image
    shared_memory --> app_image
    
    app_image --> ghcr_images
    ghcr_images --> tagged_variants
```

Sources: [rslp/sentinel2_vessels/Dockerfile:1-12](), [rslp/sentinel2_vessels/docker-compose.yaml:4-29]()

### Docker Compose Configuration

The `docker-compose.yaml` files define the build dependencies and runtime configuration:

**Key Configuration Elements:**
- **Base Image Dependency**: Applications depend on `base-image:latest`
- **GPU Support**: NVIDIA runtime with GPU device access
- **Memory Allocation**: 15GB shared memory for ML workloads
- **Port Exposure**: Standard port 5555 for API services
- **Environment Variables**: `PYTHONPATH` and application-specific variables

Sources: [rslp/sentinel2_vessels/docker-compose.yaml:12-29]()

### Image Tagging Strategy

The CI/CD system implements a dual-tagging strategy for Docker images:

1. **SHA-based Tags**: `sha-{SHORT_SHA}` for specific commit identification
2. **Version Tags**: `{LATEST_TAG}` for semantic versioning

This approach enables both pinned deployments (using SHA tags) and flexible version-based deployments (using version tags).

Sources: [.github/workflows/publish_project_docker_image.yaml:58-61]()

## Registry and Distribution

Docker images are published to GitHub Container Registry (GHCR) under the `ghcr.io/allenai` namespace. The registry serves as the central distribution point for all containerized applications.

### Published Images

Current applications with automated publishing:

| Application | Registry Path | Purpose |
|-------------|---------------|---------|
| Landsat Vessel Detection | `ghcr.io/allenai/landsat-vessel-detection` | Landsat vessel detection API |
| Sentinel-2 Vessel Detection | `ghcr.io/allenai/sentinel2-vessel-detection` | Sentinel-2 vessel detection API |

### Image Consumption

The published images are consumed by:
- **Beaker Platform**: For distributed training and inference jobs
- **API Services**: For FastAPI-based prediction services
- **Local Development**: For consistent development environments

Sources: [.github/workflows/publish_project_docker_image.yaml:16-17](), [.github/workflows/publish_project_docker_image.yaml:58-61]()

## Integration with Deployment Platforms

The CI/CD system integrates with the broader deployment infrastructure through standardized container interfaces.

### Beaker Integration

Docker images published to GHCR are consumed by Beaker clusters for:
- Model training jobs
- Large-scale inference tasks
- Distributed worker deployment

### API Service Deployment

Containerized applications support direct deployment as API services with:
- FastAPI framework integration
- Prometheus metrics exposure
- Swagger UI documentation
- GPU-accelerated inference

Sources: [rslp/sentinel2_vessels/Dockerfile:6-12](), [rslp/sentinel2_vessels/docker-compose.yaml:19-29]()

The CI/CD system provides the foundation for scalable, reproducible deployments across the entire rslearn_projects ecosystem, supporting both development workflows and production deployments.

---

