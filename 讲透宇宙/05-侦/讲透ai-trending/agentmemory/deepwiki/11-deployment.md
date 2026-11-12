<!-- source: DeepWiki mcp.deepwiki.com · repo rohitg00/agentmemory · page 11 Deployment · fetched 2026-10-30 -->

# Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deploy/coolify/Dockerfile](deploy/coolify/Dockerfile)
- [deploy/coolify/docker-compose.yml](deploy/coolify/docker-compose.yml)
- [deploy/fly/Dockerfile](deploy/fly/Dockerfile)
- [deploy/railway/Dockerfile](deploy/railway/Dockerfile)
- [deploy/render/Dockerfile](deploy/render/Dockerfile)
- [deploy/render/render.yaml](deploy/render/render.yaml)
- [docker-compose.yml](docker-compose.yml)
- [docs/recipes/pairings.md](docs/recipes/pairings.md)
- [plugin/skills/agentmemory-config/REFERENCE.md](plugin/skills/agentmemory-config/REFERENCE.md)
- [src/cli-data-dir.ts](src/cli-data-dir.ts)
- [test/cli-data-dir.test.ts](test/cli-data-dir.test.ts)

</details>



This page provides an overview of the deployment options for running `agentmemory` on managed infrastructure and local environments. The system is designed to be portable, relying on a containerized architecture that bundles the `agentmemory` CLI with the `iii-engine` [docker-compose.yml:16-22]().

## Deployment Architecture

`agentmemory` deployments follow a standardized structure across all platforms to ensure data persistence and security. Every template uses a `Dockerfile` that pulls the `@agentmemory/agentmemory` package from npm and copies the `iii` engine binary from the official `iiidev/iii` image [deploy/fly/Dockerfile:1-15]().

### Core Guarantees
Every deployment template (Cloud or Local) provides the following:
*   **Persistent Storage**: A volume must be mounted at `/data` to store the state store database and search indexes. Failure to mount this correctly results in volatile state [docker-compose.yml:2-7]().
*   **Automated Security**: An HMAC secret is typically generated on the first boot and stored within the data volume to ensure API authentication persistence [deploy/fly/Dockerfile:31-35]().
*   **Port Exposure**: Port `3111` (REST API) is the primary public interface [deploy/coolify/docker-compose.yml:13-14]().
*   **Privilege Management**: Entrypoint scripts are designed to drop from `root` to an unprivileged user (UID `65532`) after performing initial volume setup [docker-compose.yml:8-13]().

### Natural Language to Code Entity Mapping

The following diagram illustrates how deployment concepts map to specific files and configuration entities within the codebase.

**Deployment Entity Mapping**
```mermaid
graph TD
    subgraph "Deployment Logic"
        "Entrypoint_Script"["entrypoint.sh"]
        "Docker_Compose"["docker-compose.yml"]
        "Data_Dir_Resolver"["src/cli-data-dir.ts"]
    end

    subgraph "System Entities"
        "API_Port"["Port 3111"]
        "Stream_Port"["Port 3112"]
        "Data_Vol"["/data Volume"]
        "HMAC_File"["/data/.hmac"]
    end

    "Entrypoint_Script" -->|Generates| "HMAC_File"
    "Docker_Compose" -->|Mounts| "Data_Vol"
    "Data_Dir_Resolver" -->|Resolves| "AGENTMEMORY_DATA_DIR"
    "Docker_Compose" -->|Sets| "AGENTMEMORY_III_VERSION"
    "API_Port" --- "iii-engine"
    "Stream_Port" --- "iii-engine"
```
Sources: [docker-compose.yml:1-47](), [src/cli-data-dir.ts:86-139](), [deploy/coolify/docker-compose.yml:1-30]()

## Cloud Platform Deployments

`agentmemory` provides one-click templates for several popular cloud providers. These handle volume provisioning and container orchestration automatically.

| Platform | Best For | Technical Detail |
| :--- | :--- | :--- |
| **fly.io** | Lowest idle costs | Uses `tini` as subreaper for process management [deploy/fly/Dockerfile:29-35](). |
| **Railway** | Easy dashboard flow | Standardized Dockerfile deployment [deploy/railway/Dockerfile:1-35](). |
| **Render** | Blueprint-driven | Uses `render.yaml` for infrastructure-as-code [deploy/render/render.yaml:1-22](). |
| **Coolify** | Self-hosted VPS | Includes healthcheck via `/agentmemory/livez` [deploy/coolify/docker-compose.yml:17-22](). |

For detailed setup instructions for each provider, see [Cloud Platform Deployments](#11.1).

Sources: [deploy/render/render.yaml:1-22](), [deploy/coolify/docker-compose.yml:1-30](), [deploy/fly/Dockerfile:1-35]()

## Local & Self-Hosted Setup

For local development or hosting on your own hardware, `agentmemory` uses `docker-compose`. This setup ensures the engine and storage are correctly linked.

### Runtime Components
The deployment environment orchestrates two primary services in the standard compose file [docker-compose.yml:1-16]():
*   **iii-init**: A one-shot container that fixes volume permissions (chown to UID `65532`) before the engine starts [docker-compose.yml:8-14]().
*   **iii-engine**: The core memory engine, pinned to version `0.11.2` to maintain compatibility with the current worker model [docker-compose.yml:16-26]().

**Worker Orchestration**
```mermaid
graph LR
    subgraph "Container Boundary"
        "iii-engine"["iii-engine (v0.11.2)"]
        "agentmemory-cli"["agentmemory CLI"]
    end

    subgraph "Storage"
        "Data_Dir"["AGENTMEMORY_DATA_DIR"]
        "Config"["iii-config.docker.yaml"]
    end

    "iii-engine" -->|Depends On| "iii-init"
    "iii-engine" -->|Mounts| "Data_Dir"
    "iii-engine" -->|Reads| "Config"
    "agentmemory-cli" -->|Configures| "Data_Dir"
```
Sources: [docker-compose.yml:1-47](), [src/cli-data-dir.ts:86-139]()

For details on configuring environment variables and local volume management, see [Local Docker & Self-Hosted Setup](#11.2).

## Configuration Overview

The system recognizes 37 environment variables to tune behavior [plugin/skills/agentmemory-config/REFERENCE.md:6-45]().

| Variable | Purpose |
| :--- | :--- |
| `AGENTMEMORY_DATA_DIR` | Path to persistent storage; defaults based on platform (e.g., Application Support on macOS) [src/cli-data-dir.ts:44-64](). |
| `AGENTMEMORY_III_VERSION` | Sets the engine version (defaults to `0.11.2`) [docker-compose.yml:26](). |
| `AGENTMEMORY_SECRET` | The HMAC bearer token for API authentication [plugin/skills/agentmemory-config/REFERENCE.md:35](). |
| `AGENTMEMORY_PROVIDER` | Defines the LLM provider (e.g., Anthropic, OpenAI) [plugin/skills/agentmemory-config/REFERENCE.md:32](). |

Sources: [src/cli-data-dir.ts:86-139](), [plugin/skills/agentmemory-config/REFERENCE.md:1-45](), [docker-compose.yml:24-26]()

---

