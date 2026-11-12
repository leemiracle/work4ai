<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/qa-use · page 2 Getting Started · fetched 2026-10-30 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [docker-compose.dev.yaml](docker-compose.dev.yaml)
- [docker-compose.yaml](docker-compose.yaml)
- [media/run.png](media/run.png)
- [media/suite.png](media/suite.png)
- [next.config.ts](next.config.ts)
- [src/lib/api/client.ts](src/lib/api/client.ts)

</details>



This document covers the initial setup, deployment, and configuration of the QA Use platform. It provides step-by-step instructions for getting the system running locally or in production environments.

For information about the core data model and testing concepts, see [Core Concepts](#3). For details about the user interface and test management workflows, see [User Interface](#4).

## Prerequisites

The QA Use platform requires the following components before installation:

| Component | Purpose | Required |
|-----------|---------|----------|
| Docker & Docker Compose | Container orchestration | Yes |
| BrowserUse API Key | AI agent execution | Yes |
| Resend API Key | Email notifications | No |

### Obtaining API Keys

**BrowserUse API Key**: Register at [cloud.browser-use.com/billing](https://cloud.browser-use.com/billing) to obtain your API key for AI agent execution.

**Resend API Key**: Sign up at [resend.com](https://resend.com) for email notification capabilities. This is optional but recommended for production deployments.

Sources: [README.md:16-20]()

## Environment Configuration

The platform uses environment variables for external service integration and database connectivity. All configuration is managed through a `.env` file.

### Environment Variable Setup

```bash
# Copy the example configuration
cp .env.example .env
```

### Required Configuration

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `BROWSER_USE_API_KEY` | BrowserUse Cloud API authentication | `bu_live_xxx...` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@postgres:5432/qa-use` |

### Optional Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `RESEND_API_KEY` | Email service authentication | - |
| `RESEND_FROM_EMAIL` | Email sender address | `onboarding@resend.dev` |
| `INNGEST_SIGNING_KEY` | Background job security | - |
| `INNGEST_BASE_URL` | Inngest service endpoint | `http://inngest:8288` |

Sources: [.env.example:1-9](), [README.md:46-63]()

## Deployment Architecture

The platform consists of multiple containerized services orchestrated through Docker Compose. Two deployment configurations are available: development and production.

### Service Architecture

```mermaid
graph TB
    subgraph "QA Use Platform Services"
        app["app<br/>(Next.js Application)"]
        postgres["postgres<br/>(PostgreSQL Database)"]
        inngest["inngest<br/>(Background Jobs)"]
        migrate["migrate<br/>(Database Migration)"]
    end
    
    subgraph "External APIs"
        browseruse["BrowserUse Cloud API<br/>(api.browser-use.com)"]
        resend["Resend Email API<br/>(resend.com)"]
    end
    
    subgraph "Data Storage"
        pgdata["./data/postgres<br/>(Persistent Volume)"]
    end
    
    app --> postgres
    app --> inngest
    app --> browseruse
    app --> resend
    migrate --> postgres
    postgres --> pgdata
    inngest --> app
    
    app -.->|"Port 3000"| external[External Access]
    inngest -.->|"Port 8288"| external
    postgres -.->|"Port 5432"| external
```

Sources: [docker-compose.yaml:1-68](), [docker-compose.dev.yaml:1-107]()

### Development vs Production Configuration

The platform provides two Docker Compose configurations optimized for different use cases:

**Development** (`docker-compose.dev.yaml`):
- Hot reload with file watching
- Source code synchronization
- Development environment variables
- Debug-friendly container setup

**Production** (`docker-compose.yaml`):
- Optimized container builds
- Production environment settings
- Minimal resource footprint
- Security-hardened configuration

Sources: [docker-compose.dev.yaml:8-25](), [docker-compose.yaml:2-20]()

## Installation Process

### Quick Start Installation

The following commands will get the platform running with default settings:

```bash
# 1. Clone the repository
git clone https://github.com/browser-use/qa-use.git
cd qa-use

# 2. Configure environment variables
cp .env.example .env
# Edit .env with your API keys

# 3. Launch the platform
docker compose up
```

### Development Environment Setup

For active development with hot reload capabilities:

```bash
# Start development environment with file watching
docker compose -f docker-compose.dev.yaml up --watch
```

The `--watch` flag enables automatic container rebuilds when configuration files change.

Sources: [README.md:24-35](), [README.md:105-106]()

### Container Build Process

The platform uses a multi-stage Dockerfile for optimized builds:

```mermaid
graph LR
    subgraph "Build Stages"
        deps["deps<br/>(Dependencies)"]
        builder["builder<br/>(Build Assets)"]
        runner["runner<br/>(Production)"]
    end
    
    subgraph "Build Inputs"
        packagejson["package.json"]
        pnpmlock["pnpm-lock.yaml"]
        srccode["Source Code"]
    end
    
    subgraph "Build Outputs"
        nodemodules["node_modules"]
        buildassets["Built Assets"]
        prodimage["Production Image"]
    end
    
    packagejson --> deps
    pnpmlock --> deps
    deps --> nodemodules
    
    nodemodules --> builder
    srccode --> builder
    builder --> buildassets
    
    buildassets --> runner
    runner --> prodimage
```

Sources: [Dockerfile:1-37]()

## Service Dependencies and Startup Order

The platform services have specific dependency relationships that determine startup order:

```mermaid
graph TD
    postgres["postgres<br/>(Database Service)"]
    migrate["migrate<br/>(Schema Migration)"]
    app["app<br/>(Next.js Application)"]
    inngest["inngest<br/>(Background Processor)"]
    
    postgres -->|"health check"| migrate
    postgres -->|"service_healthy"| app
    migrate -->|"service_completed_successfully"| app
    app -->|"startup complete"| inngest
    
    postgres -.->|"Port 5432"| external["External Access"]
    app -.->|"Port 3000"| external
    inngest -.->|"Port 8288"| external
```

The startup sequence ensures:
1. PostgreSQL becomes healthy
2. Database migrations complete successfully  
3. Next.js application starts
4. Inngest connects to the application

Sources: [docker-compose.yaml:14-18](), [docker-compose.dev.yaml:39-43]()

## Initial Access and Verification

After successful deployment, the platform provides several access points:

| Service | URL | Purpose |
|---------|-----|---------|
| Main Application | http://localhost:3000 | Test suite management interface |
| Inngest Dashboard | http://localhost:8288 | Background job monitoring |
| PostgreSQL | localhost:5432 | Direct database access |

### Health Check Verification

Verify service health using the following endpoints:

```bash
# Check application health
curl http://localhost:3000

# Check database connectivity
docker compose logs postgres

# Check Inngest service
curl http://localhost:8288
```

### Database Migration Status

The `migrate` service automatically applies database schema changes during startup. Check migration status:

```bash
# View migration logs
docker compose logs migrate

# Check database schema
docker compose exec postgres psql -U postgres -d qa-use -c "\dt"
```

Sources: [README.md:44](), [docker-compose.yaml:52-64]()

## Troubleshooting Common Issues

### API Key Configuration

If tests fail to execute, verify BrowserUse API key configuration:

```bash
# Check environment variable loading
docker compose exec app printenv | grep BROWSER_USE_API_KEY

# Validate API connectivity
docker compose logs app | grep "browser-use"
```

### Database Connection Issues

For database connectivity problems:

```bash
# Check PostgreSQL service health
docker compose ps postgres

# View database logs
docker compose logs postgres

# Test database connection
docker compose exec postgres pg_isready -U postgres
```

### Container Build Failures

If containers fail to build:

```bash
# Clean build cache
docker system prune -f

# Rebuild without cache
docker compose build --no-cache

# Check build logs
docker compose logs app
```

Sources: [src/lib/api/client.ts:7-10](), [docker-compose.yaml:33-49]()

---

