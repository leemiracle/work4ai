<!-- source: DeepWiki mcp.deepwiki.com · repo openai/tunnel-client · page 8 Deployment · fetched 2026-10-26 -->

# Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [adminui/package.json](adminui/package.json)
- [adminui/pnpm-workspace.yaml](adminui/pnpm-workspace.yaml)
- [docs/deployment/docker.md](docs/deployment/docker.md)
- [docs/deployment/kubernetes-dedicated.md](docs/deployment/kubernetes-dedicated.md)
- [docs/deployment/kubernetes-sidecar.md](docs/deployment/kubernetes-sidecar.md)
- [docs/enterprise-customer-onboarding.md](docs/enterprise-customer-onboarding.md)

</details>



This page provides a high-level overview of the deployment models supported by `tunnel-client` and the fundamental network requirements for establishing a secure tunnel. The `tunnel-client` is designed to be a portable, lightweight binary that can run in diverse environments ranging from developer laptops to hardened enterprise Kubernetes clusters.

## Network Requirements

The `tunnel-client` operates on an outbound-only connectivity model [docs/enterprise-customer-onboarding.md:14-16](). It does not require any inbound ports to be opened on your firewall for core tunneling functionality.

### Egress Requirements
The client must be able to make outbound HTTPS connections to the OpenAI Control Plane.
*   **Control Plane Host**: Defaults to `api.openai.com` [docs/enterprise-customer-onboarding.md:89-91]().
*   **Port**: `443/TCP`.
*   **Key Operations**: 
    *   Long-polling: `GET /v1/tunnels/{tunnel_id}/poll` [docs/enterprise-customer-onboarding.md:80]().
    *   Posting responses: `POST /v1/tunnels/{tunnel_id}/response` [docs/enterprise-customer-onboarding.md:81]().

### Internal Connectivity
The client must have network line-of-sight to your private MCP servers, configured via the `MCP_SERVER_URL` environment variable or profile setting [docs/enterprise-customer-onboarding.md:97-98]().

### Deployment Topology
The following diagram illustrates the relationship between the code entities and the network boundaries:

**Network Connectivity Flow**
```mermaid
graph LR
    subgraph "CustomerNetwork"["Customer Network"]
        [tunnel-client]:::codeEntity
        [Private_MCP_Server]:::networkEntity
    end

    subgraph "OpenAICloud"["OpenAI Cloud"]
        [Tunnel_Control_Plane]:::networkEntity
    end

    [tunnel-client] -- "Poll/PostResponse" --> [Tunnel_Control_Plane]
    [tunnel-client] -- "JSON-RPC" --> [Private_MCP_Server]

    classDef codeEntity stroke-dasharray: 5 5
```
**Sources:** [docs/enterprise-customer-onboarding.md:18-41](), [docs/enterprise-customer-onboarding.md:76-82]()

## Deployment Patterns

The `tunnel-client` is distributed as a statically linked binary (via `CGO_ENABLED=0`) [Dockerfile:68](), making it highly compatible with containerized and virtualized environments.

### Containerization (Docker and Kubernetes)
The project includes a multi-stage `Dockerfile` that builds the `adminui` Svelte frontend and embeds the assets into the final Go binary [Dockerfile:9-70]().
*   **Docker**: Multi-architecture images (amd64/arm64) are published to `ghcr.io/openai/tunnel-client` [docs/deployment/docker.md:5-6]().
*   **Kubernetes Sidecar**: Deploying as a sidecar container allows the client to reach the MCP server over `localhost` [docs/deployment/kubernetes-sidecar.md:3]().
*   **Kubernetes Dedicated Pod**: Running as a standalone Deployment for active-active scaling, provided the MCP backend is stateless or session-aware [docs/deployment/kubernetes-dedicated.md:3-55]().

For details, see [Docker and Kubernetes Deployment](#8.1).

### Virtual Machines and Bare Metal
For environments not using containers, the `tunnel-client` can be managed as a standard background service.
*   **Systemd**: On Linux, a systemd unit file is the recommended way to manage the process lifecycle and logging.
*   **Environment Files**: Configuration is typically managed via environment variables or YAML profiles.

For details, see [Systemd and VM Deployment](#8.2).

## Health and Observability

The `tunnel-client` exposes a health server (defaulting to `:8080`) that provides endpoints for orchestration and monitoring [docs/deployment/docker.md:82-84]().

| Endpoint | Purpose |
| :--- | :--- |
| `/healthz` | Liveness check for the process [docs/deployment/kubernetes-dedicated.md:41]() |
| `/readyz` | Readiness check (validates control plane connectivity) [docs/deployment/kubernetes-dedicated.md:44]() |
| `/metrics` | Prometheus-formatted metrics |

**Sources:** [docs/deployment/kubernetes-dedicated.md:40-46](), [Dockerfile:101]()

## Build and Runtime Entities

The following diagram maps the build-time stages to the resulting runtime entities.

**Build to Runtime Mapping**
```mermaid
graph TD
    subgraph "BuildStage"["Build Stage (Dockerfile)"]
        [ui-builder] -- "pnpm build" --> [assets]
        [builder] -- "go build -ldflags" --> [tunnel-client_binary]
        [assets] -- "pkg/adminui/assets" --> [tunnel-client_binary]
    end

    subgraph "RuntimeExecution"["Runtime Execution"]
        [tunnel-client_binary] -- "cmd/client/run" --> [Runtime_Process]
        [Runtime_Process] -- "Listen" --> [Health_Port_8080]
    end
```
**Sources:** [Dockerfile:9-70](), [adminui/package.json:7](), [Dockerfile:101-103]()

## Summary of Child Pages
*   **[Docker and Kubernetes Deployment](#8.1)**: Detailed instructions on using the `Dockerfile`, image builds, and K8s manifests for sidecar or dedicated pod patterns.
*   **[Systemd and VM Deployment](#8.2)**: Guide for setting up the client on traditional Linux distributions using systemd and environment file management.

---

