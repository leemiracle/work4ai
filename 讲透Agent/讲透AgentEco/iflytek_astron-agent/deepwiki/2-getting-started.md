<!-- source: DeepWiki mcp.deepwiki.com · repo iflytek/astron-agent · page 2 Getting Started · fetched 2026-10-27 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [console/backend/hub/src/main/resources/application.yml](console/backend/hub/src/main/resources/application.yml)
- [console/frontend/index.html](console/frontend/index.html)
- [console/frontend/public/runtime-config.js](console/frontend/public/runtime-config.js)
- [docker/astronAgent/.env.example](docker/astronAgent/.env.example)
- [docker/astronAgent/casdoor/conf/app.conf](docker/astronAgent/casdoor/conf/app.conf)
- [docker/astronAgent/casdoor/conf/init_data.json](docker/astronAgent/casdoor/conf/init_data.json)
- [docker/astronAgent/casdoor/conf/init_data.json.template](docker/astronAgent/casdoor/conf/init_data.json.template)
- [docker/astronAgent/casdoor/entrypoint.sh](docker/astronAgent/casdoor/entrypoint.sh)
- [docker/astronAgent/docker-compose-auth.yml](docker/astronAgent/docker-compose-auth.yml)
- [docker/astronAgent/docker-compose-with-auth.yaml](docker/astronAgent/docker-compose-with-auth.yaml)
- [docker/astronAgent/docker-compose.yaml](docker/astronAgent/docker-compose.yaml)
- [docker/astronAgent/nginx/nginx.conf](docker/astronAgent/nginx/nginx.conf)
- [docker/ragflow/docker-compose-macos.yml](docker/ragflow/docker-compose-macos.yml)
- [docker/ragflow/docker-compose.yml](docker/ragflow/docker-compose.yml)
- [docs/CONFIGURATION.md](docs/CONFIGURATION.md)
- [docs/CONFIGURATION_zh.md](docs/CONFIGURATION_zh.md)
- [docs/CONTRIBUTING_CN.md](docs/CONTRIBUTING_CN.md)
- [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)
- [docs/DEPLOYMENT_GUIDE_WITH_AUTH.md](docs/DEPLOYMENT_GUIDE_WITH_AUTH.md)
- [docs/DEPLOYMENT_GUIDE_WITH_AUTH_RPA.md](docs/DEPLOYMENT_GUIDE_WITH_AUTH_RPA.md)
- [docs/DEPLOYMENT_GUIDE_WITH_AUTH_RPA_zh.md](docs/DEPLOYMENT_GUIDE_WITH_AUTH_RPA_zh.md)
- [docs/DEPLOYMENT_GUIDE_WITH_AUTH_zh.md](docs/DEPLOYMENT_GUIDE_WITH_AUTH_zh.md)
- [docs/DEPLOYMENT_GUIDE_zh.md](docs/DEPLOYMENT_GUIDE_zh.md)
- [docs/README-zh.md](docs/README-zh.md)

</details>



This guide provides step-by-step instructions for deploying the Astron Agent platform for the first time. It covers the essential setup process, from system requirements through initial configuration to service startup. By the end of this guide, you will have a fully functional Astron Agent platform running on your local machine or server.

For detailed information about specific components, see:
- System architecture and component overview: [Astron Agent Platform Overview](#1)
- Individual service configurations: [Core Services Architecture](#3)
- Production deployment considerations: [Infrastructure and Deployment](#11)

---

## Deployment Overview

The Astron Agent platform can be deployed using two primary methods to meet different scenario requirements:

| Method | Use Case | Status | Complexity |
|--------|----------|--------|------------|
| **Docker Compose** | Quick start, development, testing | ✅ Available | Low |
| **Helm Charts** | Production Kubernetes deployments | 🚧 In Development | Medium |

This guide focuses on the Docker Compose deployment method, which is recommended for initial setup and evaluation.

**Sources**: [README.md:47-94]()

---

## System Requirements

Before beginning, ensure your system meets the following minimum requirements for a stable experience.

### Core Platform Requirements
The core agent system requires the following resources to manage service orchestration and database operations:

| Component | Minimum Specification |
|-----------|----------------------|
| **CPU** | 2 cores |
| **RAM** | 4 GiB |
| **Disk** | 50 GB |
| **OS** | Linux, macOS, or Windows with WSL2 |

### Optional RagFlow Knowledge Base Requirements
If you choose to deploy the optional RagFlow service for advanced RAG capabilities, additional resources are required:

| Component | Minimum Specification |
|-----------|----------------------|
| **CPU** | 4 cores |
| **RAM** | 16 GB |
| **Disk** | 50 GB (additional) |

### Required Software
- **Docker**: Version 20.10 or later
- **Docker Compose**: Version 2.0 or later
- **Git**: For cloning the repository

**Sources**: [docs/DEPLOYMENT_GUIDE_zh.md:17-26](), [docs/DEPLOYMENT_GUIDE.md:15-26]()

---

## Quick Start Process

### Step 1: Clone the Repository

```bash
# Clone the Astron Agent repository
git clone https://github.com/iflytek/astron-agent.git

# Navigate to the deployment directory
cd astron-agent/docker/astronAgent
```

**Sources**: [README.md:52-56]()

### Step 2: Configuration Files Setup

The deployment uses environment variables defined in a `.env` file for configuration. This file must be created from the provided template [docker/astronAgent/.env.example:1-3]():

```bash
# Copy the example environment file
cp .env.example .env

# Edit the configuration file
vim .env
```

#### Configuration Files Architecture

The following diagram illustrates how configuration flows from the `.env` file to individual services and the frontend runtime.

**Configuration Flow Diagram**
```mermaid
graph TB
    subgraph "Configuration_Files"
        [".env"] --> ["docker-compose.yaml"]
        [".env"] --> ["docker-compose-with-auth.yaml"]
    end
    
    ["docker-compose.yaml"] --> ["core-tenant"]
    ["docker-compose.yaml"] --> ["core-database"]
    ["docker-compose.yaml"] --> ["core-agent"]
    ["docker-compose.yaml"] --> ["core-workflow"]
    
    subgraph "Frontend_Runtime"
        ["entrypoint.sh"] --> ["runtime-config.js"]
        ["runtime-config.js"] --> ["window.__APP_CONFIG__"]
    end
    
    [".env"] --> ["entrypoint.sh"]
```

**Sources**: [docker/astronAgent/.env.example:1-2](), [docker/astronAgent/docker-compose.yaml:165-189](), [console/frontend/index.html:14-17]()

### Step 3: Essential Environment Variables

The `.env` file requires configuration of several key parameters. These variables are organized into functional groups in [docker/astronAgent/.env.example:4-205]():

#### Required iFLYTEK Platform Credentials
These credentials enable the platform's AI capabilities, including the Spark Large Language Model.

```env
# iFLYTEK Open Platform credentials
SPARK_APP_ID=your-app-id
SPARK_API_KEY=your-api-key
SPARK_API_SECRET=your-api-secret

# AI Ability configuration for prompt optimization and one-sentence bot creation
AI_ABILITY_CHAT_BASE_URL=https://spark-api-open.xf-yun.com/v1
AI_ABILITY_CHAT_MODEL=xxx
AI_ABILITY_CHAT_API_KEY=xxx
```

**Sources**: [console/backend/hub/src/main/resources/application.yml:127-149](), [docs/DEPLOYMENT_GUIDE.md:161-194]()

#### Required Casdoor Authentication Configuration
Casdoor provides the identity layer for the platform. Default settings are provided for a quick start.

```env
# Casdoor OAuth2 server configuration
CONSOLE_CASDOOR_URL=${HOST_BASE_ADDRESS}:${CASDOOR_PORT}
CONSOLE_CASDOOR_ID=astron-agent-client
CONSOLE_CASDOOR_APP=astron-agent-app
CONSOLE_CASDOOR_ORG=built-in
```

**Sources**: [docker/astronAgent/.env.example:108-111](), [docs/DEPLOYMENT_GUIDE.md:115-127]()

#### Required Host Configuration
Define where the platform is hosted to ensure proper routing by the Nginx proxy.

```env
# Base address for the platform
HOST_BASE_ADDRESS=http://localhost
# Nginx port
EXPOSE_NGINX_PORT=80
```

**Sources**: [docker/astronAgent/.env.example:83-85](), [docker/astronAgent/nginx/nginx.conf:46-47]()

### Step 4: Start the Platform

Once the `.env` file is configured, start all services using Docker Compose. The recommended command includes the authentication service:

```bash
# Start all services including Casdoor authentication
docker compose -f docker-compose-with-auth.yaml up -d

# Verify service status
docker compose ps
```

**Sources**: [docs/DEPLOYMENT_GUIDE.md:31-39](), [README.md:67-70]()

---

## Service Startup Sequence

The platform follows a strict dependency chain to ensure data availability before service logic starts.

**System Startup Dependencies**
```mermaid
graph TD
    subgraph "Infrastructure_Layer"
        ["astron-agent-postgres"]
        ["astron-agent-mysql"]
        ["astron-agent-redis"]
        ["astron-agent-minio"]
    end
    
    subgraph "Core_Services_Layer"
        ["core-tenant"]
        ["core-database"]
        ["core-agent"]
        ["core-workflow"]
    end
    
    subgraph "Console_Layer"
        ["console-hub"]
        ["console-frontend"]
        ["nginx"]
    end
    
    ["astron-agent-postgres"] --> ["core-tenant"]
    ["astron-agent-mysql"] --> ["core-tenant"]
    ["astron-agent-redis"] --> ["core-tenant"]
    ["astron-agent-minio"] --> ["core-tenant"]
    
    ["core-tenant"] --> ["console-hub"]
    ["core-database"] --> ["console-hub"]
    ["core-agent"] --> ["console-hub"]
    ["core-workflow"] --> ["console-hub"]
    
    ["console-hub"] --> ["nginx"]
    ["console-frontend"] --> ["nginx"]
```

**Sources**: [docker/astronAgent/docker-compose.yaml:7-186](), [docker/astronAgent/nginx/nginx.conf:152-178]()

---

## Service Access Points

After successful startup, the platform services are accessible at the following URLs:

### Primary Application Access

| Service | URL | Default Credentials | Purpose |
|---------|-----|---------------------|---------|
| **Astron Agent Console** | http://localhost/ | Via Casdoor SSO | Main application interface [docker/astronAgent/nginx/nginx.conf:167-168]() |
| **Casdoor Admin** | http://localhost:8000 | admin / 123 | OAuth2 management [README.md:77-84]() |

### Internal Service Ports

| Service | Port | Protocol | Source |
|---------|------|----------|--------|
| `core-tenant` | 5052 | HTTP | [docker/astronAgent/.env.example:95]() |
| `core-database` | 7990 | HTTP | [docker/astronAgent/.env.example:96]() |
| `core-workflow` | 7880 | HTTP | [docker/astronAgent/.env.example:102]() |
| `console-hub` | 8080 | HTTP | [console/backend/hub/src/main/resources/application.yml:2]() |

---

## Verification and Health Checks

Infrastructure services include built-in health checks to ensure they are ready to accept connections:

- **PostgreSQL**: `pg_isready -U ${POSTGRES_USER} -d sparkdb_manager` [docker/astronAgent/docker-compose.yaml:22]()
- **MySQL**: `mysqladmin ping -h localhost` [docker/astronAgent/docker-compose.yaml:40]()
- **Redis**: `redis-cli ping` [docker/astronAgent/docker-compose.yaml:56]()
- **MinIO**: `curl -f http://localhost:9000/minio/health/live` [docker/astronAgent/docker-compose.yaml:143]()

**Sources**: [docker/astronAgent/docker-compose.yaml:21-146]()

---

## Next Steps

This page is a high-level guide. For detailed configuration and advanced setup, refer to the child pages:

1. **[Prerequisites and Requirements](#2.1)** — Detailed hardware and software compatibility matrix.
2. **[Quick Start with Docker Compose](#2.2)** — Step-by-step deployment for standard and authenticated environments.
3. **[Environment Configuration](#2.3)** — Deep dive into the `.env` variables and service-specific overrides.
4. **[Authentication Setup with Casdoor](#2.4)** — How to configure OAuth2 applications, organizations, and redirect URLs.
5. **[Optional Services Configuration](#2.5)** — Setup for RagFlow knowledge bases and Spark RAG cloud services.

**Sources**: [README.md:107-115](), [docs/DEPLOYMENT_GUIDE.md:5-11]()

---

