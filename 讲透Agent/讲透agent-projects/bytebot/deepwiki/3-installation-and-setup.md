<!-- source: DeepWiki mcp.deepwiki.com · repo bytebot-ai/bytebot · page 3 Installation and Setup · fetched 2026-10-29 -->

# Installation and Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/api-reference/agent/tasks.mdx](docs/api-reference/agent/tasks.mdx)
- [docs/core-concepts/desktop-environment.mdx](docs/core-concepts/desktop-environment.mdx)
- [docs/deployment/railway.mdx](docs/deployment/railway.mdx)
- [docs/guides/task-creation.mdx](docs/guides/task-creation.mdx)
- [docs/introduction.mdx](docs/introduction.mdx)
- [docs/quickstart.mdx](docs/quickstart.mdx)

</details>



This document provides an overview of deploying and configuring the Bytebot AI desktop agent system. It covers the available deployment methods, system requirements, and initial configuration steps required to run all four core services.

For detailed deployment instructions using Docker Compose, see [Docker Deployment](#3.1). For Kubernetes deployments, see [Kubernetes Deployment](#3.2). For comprehensive configuration options, see [Configuration](#3.3).

## Deployment Methods Overview

Bytebot supports multiple deployment approaches depending on your infrastructure requirements and operational preferences.

```mermaid
graph TB
    subgraph "One-Click Deployment"
        RailwayBtn["Deploy on Railway Button"]
        RailwayTemplate["railway.com/deploy/bytebot"]
    end
    
    subgraph "Self-Hosted Options"
        DockerCompose["docker-compose.yml"]
        K8sHelm["Kubernetes + Helm"]
        LocalDev["Local Development"]
    end
    
    subgraph "Container Registry"
        GHCR["ghcr.io/bytebot-ai"]
        UIImage["bytebot-ui:edge"]
        AgentImage["bytebot-agent:edge"] 
        DesktopImage["bytebot-desktop:edge"]
    end
    
    RailwayBtn --> RailwayTemplate
    DockerCompose --> GHCR
    K8sHelm --> GHCR
    LocalDev --> GHCR
    
    GHCR --> UIImage
    GHCR --> AgentImage
    GHCR --> DesktopImage
```

**Deployment Architecture and Container Images**

Sources: [docs/deployment/railway.mdx:1-90](), [docker/docker-compose.yml:1-87]()

## System Architecture

The complete Bytebot system consists of four interconnected services that must be deployed and configured together.

```mermaid
graph TB
    subgraph "bytebot-ui:9992"
        NextJS["Next.js Application"]
        VNCViewer["VNC Client Integration"]
        TaskInterface["Task Management UI"]
    end
    
    subgraph "bytebot-agent:9991"
        NestJSAgent["NestJS Service"]
        TasksService["TasksService"]
        AgentProcessor["AgentProcessor"] 
        MessagesService["MessagesService"]
        TasksGateway["TasksGateway WebSocket"]
    end
    
    subgraph "bytebot-desktop:9990"
        BytebotdDaemon["bytebotd NestJS Daemon"]
        ComputerUseService["ComputerUseService"]
        XfceDesktop["Ubuntu + XFCE Desktop"]
        VNCServer["VNC/noVNC Server"]
    end
    
    subgraph "postgres:5432"
        PostgresDB["PostgreSQL Database"]
        TasksTable["Tasks Table"]
        MessagesTable["Messages Table"]
    end
    
    NextJS -->|"HTTP API Calls"| NestJSAgent
    VNCViewer -->|"WebSocket VNC"| VNCServer
    TasksGateway -->|"Real-time Updates"| TaskInterface
    
    AgentProcessor -->|"Computer Actions"| ComputerUseService
    TasksService -->|"Task Persistence"| PostgresDB
    MessagesService -->|"Message Storage"| PostgresDB
```

**Service Dependencies and Network Communication**

Sources: [docker/docker-compose.yml:38-79](), [docker/docker-compose.yml:3-36]()

## Container Images and Build Process

All Bytebot services are distributed as multi-architecture Docker images built automatically from the main branch.

| Service | Container Image | Build Trigger | Platforms |
|---------|-----------------|---------------|-----------|
| `bytebot-ui` | `ghcr.io/bytebot-ai/bytebot-ui:edge` | UI/shared code changes | `linux/amd64`, `linux/arm64` |
| `bytebot-agent` | `ghcr.io/bytebot-ai/bytebot-agent:edge` | Agent/shared code changes | `linux/amd64`, `linux/arm64` |
| `bytebot-desktop` | `ghcr.io/bytebot-ai/bytebot-desktop:edge` | Desktop/bytebotd changes | `linux/amd64`, `linux/arm64` |

The build process uses GitHub Actions workflows that automatically trigger on code changes and push multi-architecture images to GitHub Container Registry.

```mermaid
graph LR
    subgraph "GitHub Actions"
        BuildUI[".github/workflows/build-ui.yaml"]
        BuildAgent[".github/workflows/build-agent.yaml"] 
        BuildDesktop[".github/workflows/build-desktop.yaml"]
    end
    
    subgraph "Build Context"
        PackagesDir["./packages/"]
        UIDockerfile["bytebot-ui/Dockerfile"]
        AgentDockerfile["bytebot-agent/Dockerfile"]
        DesktopDockerfile["bytebotd/Dockerfile"]
    end
    
    subgraph "Registry"
        GHCRRegistry["ghcr.io/bytebot-ai"]
    end
    
    BuildUI --> UIDockerfile
    BuildAgent --> AgentDockerfile
    BuildDesktop --> DesktopDockerfile
    
    UIDockerfile --> GHCRRegistry
    AgentDockerfile --> GHCRRegistry
    DesktopDockerfile --> GHCRRegistry
```

**Automated Container Build Pipeline**

Sources: [.github/workflows/build-ui.yaml:1-51](), [.github/workflows/build-agent.yaml:1-50](), [.github/workflows/build-desktop.yaml:1-61]()

## Quick Start Options

### Railway One-Click Deployment

The fastest way to deploy Bytebot is using the Railway template, which handles all service orchestration, networking, and database provisioning automatically.

```mermaid
sequenceDiagram
    participant User
    participant Railway as "Railway Platform"
    participant Template as "Bytebot Template"
    participant GHCR as "GitHub Container Registry"
    
    User->>Railway: Click "Deploy on Railway" button
    Railway->>Template: Load bytebot template configuration
    Template->>GHCR: Pull latest edge images
    Railway->>Railway: Create postgres service
    Railway->>Railway: Setup private networking
    Railway->>User: Provide public URL for bytebot-ui
    User->>Railway: Add AI API keys (ANTHROPIC_API_KEY, etc.)
    Railway->>User: Deployment ready (~2 minutes)
```

**Railway Deployment Flow**

Sources: [docs/deployment/railway.mdx:6-56]()

### Docker Compose Local Deployment

For local development or self-hosted deployments, use the provided Docker Compose configuration:

```bash
# Clone repository and navigate to docker directory
git clone https://github.com/bytebot-ai/bytebot
cd bytebot/docker

# Set required environment variables
export ANTHROPIC_API_KEY="your-key-here"
# or OPENAI_API_KEY, GEMINI_API_KEY

# Deploy all services
docker-compose up -d
```

The `docker-compose.yml` file defines all four services with proper networking and dependency management.

Sources: [docker/docker-compose.yml:1-87]()

## Environment Variables

The core environment variables required across all deployment methods:

| Variable | Service | Purpose | Example |
|----------|---------|---------|---------|
| `DATABASE_URL` | bytebot-agent | PostgreSQL connection | `postgresql://postgres:postgres@postgres:5432/bytebotdb` |
| `BYTEBOT_DESKTOP_BASE_URL` | bytebot-agent | Desktop service URL | `http://bytebot-desktop:9990` |
| `BYTEBOT_AGENT_BASE_URL` | bytebot-ui | Agent service URL | `http://bytebot-agent:9991` |
| `BYTEBOT_DESKTOP_VNC_URL` | bytebot-ui | VNC WebSocket URL | `http://bytebot-desktop:9990/websockify` |
| `ANTHROPIC_API_KEY` | bytebot-agent | Claude API access | `sk-ant-...` |
| `OPENAI_API_KEY` | bytebot-agent | GPT API access | `sk-...` |
| `GEMINI_API_KEY` | bytebot-agent | Gemini API access | `AI...` |

At minimum, one AI provider API key is required for the system to function.

Sources: [docker/docker-compose.yml:48-76]()

## Network Architecture

All services communicate through internal networking with only the UI service exposed publicly.

```mermaid
graph TB
    subgraph "Public Access"
        PublicURL["https://your-domain.com:9992"]
    end
    
    subgraph "Internal Network: bytebot-network"
        UI["bytebot-ui:9992<br/>Public Port: 9992"]
        Agent["bytebot-agent:9991<br/>Internal Only"]
        Desktop["bytebot-desktop:9990<br/>Internal Only"] 
        DB["postgres:5432<br/>Internal Only"]
    end
    
    PublicURL --> UI
    UI -->|"HTTP API"| Agent
    UI -->|"WebSocket VNC"| Desktop
    Agent -->|"SQL Queries"| DB
    Agent -->|"Computer Actions"| Desktop
    
    style UI fill:#e1f5fe
    style Agent fill:#f3e5f5  
    style Desktop fill:#e8f5e8
    style DB fill:#fff3e0
```

**Service Network Topology**

Sources: [docker/docker-compose.yml:81-83](), [docs/deployment/railway.mdx:60-66]()

## System Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 10GB available space
- **Network**: Internet access for AI provider APIs

### Desktop Service Requirements
The `bytebot-desktop` service requires additional resources as it runs a full Ubuntu desktop environment:
- **Shared Memory**: 2GB (`shm_size: "2g"`)
- **Privileged Mode**: Required for desktop functionality
- **Display**: Virtual display `:0` configured

Sources: [docker/docker-compose.yml:11-20](), [docker/docker-compose.core.yml:11-19]()

## Next Steps

After completing the initial installation:

1. **Configure AI Providers**: Add API keys for your preferred AI services (see [Configuration](#3.3))
2. **Set Up Authentication**: Consider adding authentication for production deployments
3. **Customize Desktop Environment**: Modify the desktop service configuration as needed
4. **Monitor Services**: Set up logging and monitoring for production environments

For production deployments, see [Kubernetes Deployment](#3.2) for scalable orchestration options.

Sources: [docs/deployment/railway.mdx:86-90]()

---

