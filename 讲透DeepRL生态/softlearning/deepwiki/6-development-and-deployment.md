> 来源: [https://deepwiki.com/rail-berkeley/softlearning/6-development-and-deployment](https://deepwiki.com/rail-berkeley/softlearning/6-development-and-deployment)
> DeepWiki rail-berkeley/softlearning | Last indexed: 25 June 2025 (13cf18

# Development and Deployment

  Relevant source files 
 - [.env](https://github.com/rail-berkeley/softlearning/blob/13cf187c/.env)
 - [.gitignore](https://github.com/rail-berkeley/softlearning/blob/13cf187c/.gitignore)
 - [docker/Dockerfile.softlearning](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/Dockerfile.softlearning)
 - [docker/Dockerfile.softlearning.base.cpu](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/Dockerfile.softlearning.base.cpu)
 - [docker/Dockerfile.softlearning.base.gpu](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/Dockerfile.softlearning.base.gpu)
 - [docker/cloudbuild.yaml](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/cloudbuild.yaml)
 - [docker/docker-compose.cloud.yml](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/docker-compose.cloud.yml)
 - [docker/docker-compose.dev.cpu.yml](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/docker-compose.dev.cpu.yml)
 - [docker/docker-compose.dev.gpu.yml](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/docker-compose.dev.gpu.yml)
 - [docker/entrypoint.sh](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/entrypoint.sh)
 
  This document covers the development environment setup, containerization strategy, and deployment workflows for the softlearning framework. It provides an overview of Docker-based development environments, build processes, and cloud deployment configurations.

 For detailed Docker development setup instructions, see [Docker Development Environment](https://deepwiki.com/rail-berkeley/softlearning/6.1-docker-development-environment). For cloud deployment specifics, see [Cloud Deployment](https://deepwiki.com/rail-berkeley/softlearning/6.2-cloud-deployment).

 
## Development Environment Architecture

 The softlearning framework provides a comprehensive Docker-based development environment that supports both CPU and GPU configurations. The system is designed to enable reproducible development environments across different platforms while maintaining compatibility with cloud deployment scenarios.

 
```

```

 **Sources:** [docker/docker-compose.dev.cpu.yml1-32](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/docker-compose.dev.cpu.yml#L1-L32) [docker/docker-compose.dev.gpu.yml1-32](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/docker-compose.dev.gpu.yml#L1-L32) [docker/Dockerfile.softlearning.base.cpu1-144](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/Dockerfile.softlearning.base.cpu#L1-L144) [docker/Dockerfile.softlearning.base.gpu1-183](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/Dockerfile.softlearning.base.gpu#L1-L183)

 
## Container Architecture

 The Docker infrastructure follows a layered approach with specialized base images for different deployment scenarios. The containers are configured with comprehensive development tools and maintain consistency between local development and cloud deployment environments.

 
```

```

 **Sources:** [docker/Dockerfile.softlearning.base.gpu32](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/Dockerfile.softlearning.base.gpu#L32-L32) [docker/Dockerfile.softlearning.base.cpu30](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/Dockerfile.softlearning.base.cpu#L30-L30) [docker/docker-compose.dev.gpu.yml22-27](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/docker-compose.dev.gpu.yml#L22-L27) [docker/entrypoint.sh5-7](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/entrypoint.sh#L5-L7)

 
## Build Process and Dependencies

 The build process includes comprehensive dependency installation and environment configuration. The system handles both CUDA-enabled GPU environments and CPU-only configurations with appropriate optimizations for each platform.

 
| Component | CPU Version | GPU Version | Purpose |
|---|---|---|---|
| Base OS | Ubuntu 18.04 | Ubuntu 18.04 + CUDA 10.0 | Operating system foundation |
| Python | Miniconda3 | Miniconda3 | Python environment management |
| ML Libraries | TensorFlow CPU | TensorFlow GPU + cuDNN 7.4.1.5 | Deep learning framework |
| Physics Engine | MuJoCo 1.50/2.00 | MuJoCo 1.50/2.00 | Physics simulation |
| Cloud Tools | Google Cloud SDK | Google Cloud SDK | Cloud platform integration |
| Display | Xvfb | Xvfb + OpenGL | Headless rendering |

 **Sources:** [docker/Dockerfile.softlearning.base.gpu28-40](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/Dockerfile.softlearning.base.gpu#L28-L40) [docker/Dockerfile.softlearning.base.cpu28-33](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/Dockerfile.softlearning.base.cpu#L28-L33) [docker/Dockerfile.softlearning.base.gpu73-103](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/Dockerfile.softlearning.base.gpu#L73-L103) [docker/Dockerfile.softlearning.base.gpu149-159](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/Dockerfile.softlearning.base.gpu#L149-L159)

 
## Development Workflow

 The development environment supports multiple workflow patterns through Docker Compose configurations. The system provides interactive development capabilities with live code mounting and persistent result storage.

 
```

```

 **Sources:** [docker/docker-compose.dev.gpu.yml28-31](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/docker-compose.dev.gpu.yml#L28-L31) [docker/entrypoint.sh1-24](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/entrypoint.sh#L1-L24) [docker/Dockerfile.softlearning.base.gpu176-177](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/Dockerfile.softlearning.base.gpu#L176-L177)

 
## Cloud Deployment Pipeline

 The framework includes automated cloud deployment capabilities through Google Cloud Build with encrypted secret management for sensitive configuration like MuJoCo licenses.

 
```

```

 **Sources:** [docker/cloudbuild.yaml1-94](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/cloudbuild.yaml#L1-L94) [docker/cloudbuild.yaml64-85](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/cloudbuild.yaml#L64-L85)

 
## Environment Configuration

 The development environment uses standardized configuration through environment variables and Docker Compose settings. Version tags are managed centrally to ensure consistency across different deployment scenarios.

 
| Configuration | File | Purpose |
|---|---|---|
| Docker Tags | .env | Version control for container images |
| Build Exclusions | .gitignore | Development artifacts exclusion |
| MuJoCo Setup | install_mujoco.py | Physics engine installation |
| Display Config | entrypoint.sh | Headless rendering setup |
| Conda Environment | environment.yml | Python dependencies |

 **Sources:** [.env1-4](https://github.com/rail-berkeley/softlearning/blob/13cf187c/.env#L1-L4) [.gitignore105-118](https://github.com/rail-berkeley/softlearning/blob/13cf187c/.gitignore#L105-L118) [docker/Dockerfile.softlearning.base.gpu150-154](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/Dockerfile.softlearning.base.gpu#L150-L154) [docker/entrypoint.sh5-7](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/entrypoint.sh#L5-L7)

 
## Container Runtime Configuration

 The containers are configured with specific runtime requirements including GPU access, interactive capabilities, and comprehensive port exposure for development tools. The setup ensures compatibility with both local development and distributed cloud execution.

 
```

```

 **Sources:** [docker/docker-compose.dev.gpu.yml10-31](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/docker-compose.dev.gpu.yml#L10-L31) [docker/docker-compose.dev.cpu.yml10-31](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/docker-compose.dev.cpu.yml#L10-L31) [.env1-4](https://github.com/rail-berkeley/softlearning/blob/13cf187c/.env#L1-L4)
