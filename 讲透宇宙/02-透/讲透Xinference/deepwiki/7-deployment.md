> 来源: [https://deepwiki.com/xorbitsai/inference/7-deployment](https://deepwiki.com/xorbitsai/inference/7-deployment)
> DeepWiki xorbitsai/inference | Last indexed: 30 July 2026 (d97e09

# Deployment

  Relevant source files 
 - [.dockerignore](https://github.com/xorbitsai/inference/blob/d97e0970/.dockerignore)
 - [xinference/conftest.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/conftest.py)
 - [xinference/deploy/docker/Dockerfile](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/docker/Dockerfile)
 - [xinference/deploy/docker/Dockerfile.cpu](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/docker/Dockerfile.cpu)
 - [xinference/deploy/docker/pypiserver/Dockerfile.pypiserver](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/docker/pypiserver/Dockerfile.pypiserver)
 - [xinference/deploy/docker/pypiserver/README.md](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/docker/pypiserver/README.md?plain=1)
 - [xinference/deploy/docker/pypiserver/download_packages.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/docker/pypiserver/download_packages.py)
 - [xinference/deploy/docker/pypiserver/generate_package_lists.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/docker/pypiserver/generate_package_lists.py)
 - [xinference/deploy/docker/pypiserver/selfcheck.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/docker/pypiserver/selfcheck.py)
 - [xinference/deploy/docker/pypiserver/tests/test_scripts.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/docker/pypiserver/tests/test_scripts.py)
 - [xinference/deploy/local.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/local.py)
 - [xinference/deploy/supervisor.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/supervisor.py)
 - [xinference/deploy/test/test_utils.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/test/test_utils.py)
 - [xinference/deploy/utils.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/utils.py)
 - [xinference/deploy/worker.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/worker.py)
 
  This page provides comprehensive documentation for deploying Xinference in various environments. It covers the three deployment modes (local, supervisor, and worker), containerization with Docker, environment configuration, and operational monitoring.

 For information about the distributed actor architecture and cluster coordination, see [System Architecture](https://deepwiki.com/xorbitsai/inference/2-system-architecture). For API server configuration and authentication, see [RESTful API](https://deepwiki.com/xorbitsai/inference/5-restful-api) and [Authentication and Authorization](https://deepwiki.com/xorbitsai/inference/5.5-authentication-and-authorization). For client-side connection setup, see [Client Interfaces](https://deepwiki.com/xorbitsai/inference/6-client-interfaces).

 
---

 
## Overview

 Xinference supports three deployment modes that provide flexibility for different scales and infrastructure requirements:

 
| Deployment Mode | Entry Point | Use Case | Process Architecture |
|---|---|---|---|
| Local | xinference-local | Single-machine deployment, development, testing | Supervisor + Worker in subprocess, API in main process |
| Supervisor | xinference-supervisor | Distributed coordinator node | Supervisor actor only, no worker components |
| Worker | xinference-worker | Distributed compute node | Worker actor only, connects to remote supervisor |

 All three modes share common infrastructure:

 
 - Actor-based process management via `xoscar` [xinference/deploy/local.py24](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/local.py#L24-L24)
 - Health check system with configurable thresholds [xinference/deploy/utils.py152-187](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/utils.py#L152-L187)
 - Multi-process safety for logs with `SafeRotatingFileHandler` [xinference/deploy/utils.py47-171](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/utils.py#L47-L171)
 - Multiprocessing with `spawn` method (required for CUDA compatibility) [xinference/deploy/local.py163](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/local.py#L163-L163) [xinference/deploy/worker.py98](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/worker.py#L98-L98)
 
 **Sources:** [xinference/deploy/local.py15-36](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/local.py#L15-L36) [xinference/deploy/supervisor.py22-32](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/supervisor.py#L22-L32) [xinference/deploy/worker.py15-27](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/worker.py#L15-L27) [xinference/deploy/utils.py47-73](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/utils.py#L47-L73)

 
---

 
## Deployment Mode Architecture

 
```

```

 **Key Implementation Details:**

 
 - **Local mode subprocess isolation:** The supervisor and worker actors run in a separate process created by `multiprocessing.Process` with `daemon=True` [xinference/deploy/local.py130-137](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/local.py#L130-L137) The parent process communicates via `multiprocessing.Pipe` to verify startup [xinference/deploy/local.py129-145](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/local.py#L129-L145)
 - **Spawn method enforcement:** All deployment modes call `multiprocessing.set_start_method("spawn")` to prevent CUDA initialization errors in subprocesses [xinference/deploy/local.py163](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/local.py#L163-L163) [xinference/deploy/worker.py98](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/worker.py#L98-L98)
 
 **Sources:** [xinference/deploy/local.py42-188](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/local.py#L42-L188) [xinference/deploy/supervisor.py35-104](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/supervisor.py#L35-L104) [xinference/deploy/worker.py30-119](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/worker.py#L30-L119)

 
---

 
## Local Deployment

 For details, see [Local Deployment](https://deepwiki.com/xorbitsai/inference/7.1-local-deployment).

 
### Command Line Interface

 Local deployment is typically started via the `xinference-local` command, which invokes `xinference.deploy.local.main`.

 
### Process Initialization Flow

 
```

```

 **Key Functions:**

 
 - **`main()` entry point:** [xinference/deploy/local.py153-188](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/local.py#L153-L188) - Orchestrates subprocess creation, health checks, and API startup.
 - **`run_in_subprocess()`:** [xinference/deploy/local.py123-151](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/local.py#L123-L151) - Creates the actor pool subprocess with pipe communication.
 - **`_start_local_cluster()`:** [xinference/deploy/local.py42-86](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/local.py#L42-L86) - Async function that initializes supervisor and worker actors.
 - **Subprocess ready signal:** The constant `READY = "ok"` is sent through the pipe when initialization completes [xinference/deploy/local.py39](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/local.py#L39-L39) [xinference/deploy/local.py77](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/local.py#L77-L77)
 
 **Sources:** [xinference/deploy/local.py39-188](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/local.py#L39-L188) [xinference/deploy/worker.py30-58](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/worker.py#L30-L58)

 
---

 
## Distributed Deployment

 For details, see [Distributed Deployment](https://deepwiki.com/xorbitsai/inference/7.2-distributed-deployment).

 
### Supervisor Node

 The supervisor node acts as the cluster coordinator. It runs `SupervisorActor` [xinference/deploy/supervisor.py47-49](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/supervisor.py#L47-L49) and the RESTful API [xinference/deploy/supervisor.py96-101](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/supervisor.py#L96-L101)

 
### Worker Node

 Worker nodes handle model execution. They detect GPUs via `get_available_device_env_name()` and `gpu_count()` [xinference/deploy/worker.py39-45](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/worker.py#L39-L45) then create a `WorkerActor` [xinference/deploy/worker.py47-57](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/worker.py#L47-L57)

 **Sources:** [xinference/deploy/supervisor.py35-104](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/supervisor.py#L35-L104) [xinference/deploy/worker.py30-119](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/worker.py#L30-L119)

 
---

 
## Docker and Kubernetes

 For details, see [Docker and Kubernetes](https://deepwiki.com/xorbitsai/inference/7.3-docker-and-kubernetes).

 Xinference provides optimized Docker images for both GPU and CPU environments.

 
### Dockerfile Structure (GPU)

 The GPU image is based on `nvidia/cuda:13.0.2-devel-ubuntu22.04` [xinference/deploy/docker/Dockerfile55](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/docker/Dockerfile#L55-L55) It uses a multi-stage build to compile the Web UI [xinference/deploy/docker/Dockerfile41-51](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/docker/Dockerfile#L41-L51) and then sets up a Python 3.12 environment [xinference/deploy/docker/Dockerfile81-86](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/docker/Dockerfile#L81-L86)

 **Key Features:**

 
 - **Shared Torch Stack:** Installs `torch`, `torchvision`, `torchaudio`, and `torchcodec` in the parent image to be reused by model virtual environments [xinference/deploy/docker/Dockerfile95-101](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/docker/Dockerfile#L95-L101)
 - **Virtual Environment Support:** Uses `uv` for fast, parallel installation of model-specific dependencies into per-model venvs [xinference/deploy/docker/Dockerfile111-128](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/docker/Dockerfile#L111-L128)
 - **Multi-arch:** The Dockerfile is designed to build for both `amd64` and `arm64` [xinference/deploy/docker/Dockerfile31-36](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/docker/Dockerfile#L31-L36)
 
 
### CPU Image

 The CPU variant uses `continuumio/miniconda3` and installs the CPU version of PyTorch [xinference/deploy/docker/Dockerfile.cpu11-21](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/docker/Dockerfile.cpu#L11-L21)

 **Sources:** [xinference/deploy/docker/Dockerfile1-139](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/docker/Dockerfile#L1-L139) [xinference/deploy/docker/Dockerfile.cpu1-42](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/docker/Dockerfile.cpu#L1-L42)

 
---

 
## Environment Configuration

 For details, see [Environment Configuration](https://deepwiki.com/xorbitsai/inference/7.4-environment-configuration).

 Xinference configuration is managed via environment variables and constants defined in `xinference/constants.py`.

 **Path Configuration:**

 
 - `XINFERENCE_LOG_DIR`: Derived from `XINFERENCE_HOME` [xinference/deploy/utils.py37](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/utils.py#L37-L37)
 - `XINFERENCE_DEFAULT_LOG_FILE_NAME`: Default name for log files [xinference/deploy/utils.py36](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/utils.py#L36-L36)
 
 **Health Check Parameters:**

 
 - `XINFERENCE_HEALTH_CHECK_FAILURE_THRESHOLD` [xinference/deploy/supervisor.py26](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/supervisor.py#L26-L26)
 - `XINFERENCE_HEALTH_CHECK_INTERVAL` [xinference/deploy/supervisor.py27](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/supervisor.py#L27-L27)
 - `XINFERENCE_HEALTH_CHECK_TIMEOUT` [xinference/deploy/local.py30](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/local.py#L30-L30)
 
 **Sources:** [xinference/deploy/local.py27-31](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/local.py#L27-L31) [xinference/deploy/supervisor.py25-28](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/supervisor.py#L25-L28) [xinference/deploy/utils.py35-39](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/utils.py#L35-L39)

 
---

 
## Observability: Metrics, Dashboards, and Logging

 For details, see [Observability: Metrics, Dashboards, and Logging](https://deepwiki.com/xorbitsai/inference/7.5-observability:-metrics-dashboards-and-logging).

 
### Logging System

 Xinference implements a sophisticated logging system designed for multi-process environments.

 
 - **SafeRotatingFileHandler:** A custom handler that ensures parent directories are created [xinference/deploy/utils.py76](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/utils.py#L76-L76) and uses `fcntl` file locks to serialize log rotation across processes [xinference/deploy/utils.py86-98](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/utils.py#L86-L98)
 - **SafeTimedAndSizeRotatingFileHandler:** Combines time-based and size-based rotation [xinference/deploy/utils.py181-182](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/utils.py#L181-L182)
 - **Log Collection:** Includes logic for hybrid cleanup based on retention days [xinference/deploy/utils.py190-191](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/utils.py#L190-L191)
 
 
### Metrics

 The system supports Prometheus metrics and OpenTelemetry. The `WorkerActor` accepts `metrics_exporter_host` and `metrics_exporter_port` during initialization [xinference/deploy/worker.py55-56](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/worker.py#L55-L56)

 **Sources:** [xinference/deploy/utils.py47-191](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/utils.py#L47-L191) [xinference/deploy/worker.py30-57](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/worker.py#L30-L57) [xinference/conftest.py35-98](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/conftest.py#L35-L98)
