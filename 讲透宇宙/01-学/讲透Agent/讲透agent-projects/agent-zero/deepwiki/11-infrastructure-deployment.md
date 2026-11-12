<!-- source: DeepWiki mcp.deepwiki.com · repo agent0ai/agent-zero · page 11 Infrastructure & Deployment · fetched 2026-10-29 -->

# Infrastructure & Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [docker/base/build.txt](docker/base/build.txt)
- [docker/run/Dockerfile](docker/run/Dockerfile)
- [docker/run/build.txt](docker/run/build.txt)
- [docker/run/docker-compose.yml](docker/run/docker-compose.yml)
- [docker/run/fs/exe/run_A0.sh](docker/run/fs/exe/run_A0.sh)
- [docker/run/fs/ins/install_A0.sh](docker/run/fs/ins/install_A0.sh)
- [docker/run/fs/ins/install_A02.sh](docker/run/fs/ins/install_A02.sh)

</details>



This page provides a high-level overview of the Agent Zero deployment lifecycle, focusing on its Docker-centric architecture, the dual-runtime environment, the automated CI/CD pipeline, the bootstrapping sequence, and the self-update mechanism that ensures long-running instances remain current. For detailed child page breakdown, see [Docker Architecture](#11.1), [Self-Update System](#11.2), [CI/CD Pipeline & Bundling](#11.3), and [Tunnel & Cloudflare Connectivity](#11.4).

## Docker Architecture

Agent Zero is distributed as a Docker container to provide a consistent, isolated environment for both the framework and the code it executes. The architecture utilizes a base and run image split to optimize build times and image size [docker/run/Dockerfile:1-4]().

*   **Base Image (`agent-zero-base`):** Built from a Linux foundation, it contains core OS dependencies, system libraries, and foundational Python environments [docker/base/build.txt:1-18]().
*   **Run Image:** Built on top of the base image [docker/run/Dockerfile:4](), it clones the specified branch [docker/run/fs/ins/install_A0.sh:22-27](), installs framework requirements via `uv` [docker/run/fs/ins/install_A0.sh:38](), and preloads framework configurations via `preload.py` [docker/run/fs/ins/install_A0.sh:44]().
*   **Process Management:** The container uses `supervisord` (invoked via `/exe/initialize.sh`) to manage multiple services, including the main application, SearXNG, and the tunnel API [docker/run/Dockerfile:33-36]().
*   **Composition:** Container deployment is orchestrated via `docker-compose.yml`, mounting local volumes and configuring port bindings and host gateways [docker/run/docker-compose.yml:1-14]().

For details on image layers, process management, virtual environment runtimes, and internal services like SearXNG and SSH, see [Docker Architecture](#11.1).

Title: Deployment Entity Mapping
```mermaid
graph TD
    "DockerBase"["docker/base/build.txt"] -->|"builds"| "BaseImg"["agent-zero-base"]
    "DockerRun"["docker/run/Dockerfile"] -->|"extends"| "BaseImg"
    "DockerRun" -->|"executes"| "InstallA0"["docker/run/fs/ins/install_A0.sh"]
    "InstallA0" -->|"runs"| "PreloadPy"["preload.py"]
    "DockerRun" -->|"invokes"| "InitSh"["docker/run/fs/exe/initialize.sh"]
    "InitSh" -->|"starts"| "Supervisord"["supervisord"]
    "Supervisord" -->|"launches"| "RunA0"["docker/run/fs/exe/run_A0.sh"]
```
Sources: [docker/base/build.txt:1-18](), [docker/run/Dockerfile:1-36](), [docker/run/fs/ins/install_A0.sh:1-44](), [docker/run/fs/exe/run_A0.sh:1-7]()

## Self-Update System & Bootstrap Sequence

Agent Zero includes a self-update system designed to update the framework without requiring a manual `docker pull` or container restart from the host.

*   **Update Manager:** A durable manager (`self_update_manager.py`) acts as a wrapper around the main application process, ensuring that the framework can pull updates from Git and restart itself [docker/run/fs/exe/run_A0.sh:7]().
*   **Cache Busting & Re-installation:** Optimization scripts like `install_A02.sh` handle repository cleanup and package cache purging to accelerate updates [docker/run/fs/ins/install_A02.sh:1-17]().
*   **Persistence:** The system preserves user data by mounting `/a0` as a volume in `docker-compose.yml` [docker/run/docker-compose.yml:5-6]().

For details on `self_update_manager.py`, trigger files, health checks, version locking, and CLI recovery, see [Self-Update System](#11.2).

Title: Bootstrap And Migration Flow
```mermaid
graph LR
    "RunScript"["docker/run/fs/exe/run_A0.sh"] -->|"calls"| "UpdateManager"["self_update_manager.py"]
    "UpdateManager" -->|"initializes"| "PreparePy"["prepare.py"]
    "PreparePy" -->|"triggers"| "StartupMigrate"["helpers/migration.py"]
```
Sources: [docker/run/fs/exe/run_A0.sh:1-7](), [docker/run/docker-compose.yml:5-6]()

## CI/CD Pipeline & Bundling

The project uses automated build scripts and Docker configurations to facilitate testing, building, and distribution of images across multiple environments.

*   **Docker Build Strategy:** The project supports local builds using a `CACHE_DATE` argument to invalidate specific layers and ensure fresh code is pulled [docker/run/build.txt:1-10]().
*   **Multi-Platform Support:** The infrastructure uses `docker buildx` to build images for both `linux/amd64` and `linux/arm64` to support a wide range of hardware architectures [docker/run/build.txt:32-38]().
*   **Branch-Based Tagging:** Images are built and tagged based on their source branch (e.g., `development`, `testing`, `latest`) to allow users to opt into different stability tiers [docker/run/build.txt:12-22]().

For details on GitHub Actions workflows, `docker_release_plan.py` tag strategies, and release notes automation, see [CI/CD Pipeline & Bundling](#11.3).

Title: CI/CD Pipeline Architecture
```mermaid
graph LR
    "GitPush"["Git Push/Tag"] --> "BuildTrigger"["Build Trigger"]
    
    subgraph "BuildProcess"
        "BuildTrigger" --> "DockerBuildx"["docker buildx build"]
        "DockerBuildx" --> "PlatformAMD"["linux/amd64"]
        "DockerBuildx" --> "PlatformARM"["linux/arm64"]
    end

    subgraph "Artifacts"
        "DockerBuildx" --> "DockerHubLatest"["agent0ai/agent-zero:latest"]
        "DockerHubDev" --> "DockerHubDevTarget"["agent0ai/agent-zero:development"]
        "DockerBuildx" --> "DockerHubVer"["agent0ai/agent-zero:vx.x.x"]
    end
```
Sources: [docker/run/build.txt:1-42](), [docker/run/Dockerfile:1-36](), [docker/run/fs/ins/install_A0.sh:22-27]()

## Tunnel & Cloudflare Connectivity

To facilitate remote access and mobile usage without complex firewall configurations, Agent Zero integrates with tunneling mechanisms.

*   **Tunnel API:** The framework includes a dedicated service for managing tunnel connectivity, initialized via `/exe/run_tunnel_api.sh` [docker/run/Dockerfile:33]().
*   **Secure Access:** This allows the internal Web UI (running on port 80 inside the container) to be exposed securely to the internet, mapped to port `50080` on the host [docker/run/docker-compose.yml:7-8]().
*   **Network Config:** The `docker-compose.yml` provides a standard configuration for port mapping, resource limits (`ulimits`), and `host.docker.internal` resolution to allow the container to communicate with the host machine [docker/run/docker-compose.yml:9-14]().

For details on `tunnel_manager.py`, `run_tunnel.py`, Cloudflare/Tailscale integration, and UI remote link settings, see [Tunnel & Cloudflare Connectivity](#11.4).

Sources: [docker/run/Dockerfile:31-33](), [docker/run/docker-compose.yml:7-14]()

---

