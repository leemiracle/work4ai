<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/qa-use · page 9 Development Guide · fetched 2026-10-30 -->

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [docker-compose.dev.yaml](docker-compose.dev.yaml)
- [media/run.png](media/run.png)
- [media/suite.png](media/suite.png)
- [next.config.ts](next.config.ts)
- [package.json](package.json)

</details>



This document provides guidance for developers working on the QA Use platform, covering development environment setup, project structure, and key development workflows. It focuses on the technical aspects of building and maintaining the AI-powered E2E testing platform.

For information about the overall system architecture and core concepts, see [Overview](#1) and [Core Concepts](#3). For deployment and production configuration, see [Getting Started](#2).

## Development Environment Setup

The QA Use platform uses a containerized development environment that provides hot reloading and automatic database migrations. The development setup consists of four main services orchestrated through Docker Compose.

### Development Services Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        DEV_APP["app<br/>Next.js Dev Server<br/>Port 3000"]
        DEV_DB["postgres<br/>PostgreSQL Database<br/>Port 5432"]
        DEV_INNGEST["inngest<br/>Background Job Server<br/>Port 8288"]
        DEV_MIGRATE["migrate<br/>Database Migration Service"]
    end
    
    subgraph "Host Machine"
        SRC["./src<br/>Source Code"]
        DATA["./data/postgres<br/>Database Volume"]
        ENV[".env<br/>Environment Variables"]
    end
    
    DEV_APP --> DEV_DB
    DEV_APP --> DEV_INNGEST
    DEV_MIGRATE --> DEV_DB
    
    SRC -.->|Hot Reload| DEV_APP
    DATA -.->|Persistence| DEV_DB
    ENV -.->|Configuration| DEV_APP
    
    DEV_INNGEST -.->|API Calls| DEV_APP
```

**Sources:** [docker-compose.dev.yaml:1-107]()

### Service Configuration

The development environment is configured through `docker-compose.dev.yaml` with the following key services:

**Application Service (`app`)**
- Built from `Dockerfile.dev` with hot reloading enabled
- Watches source files in `./src` with automatic sync
- Exposes port 3000 for the Next.js development server
- Environment variables: `WATCHPACK_POLLING=true`, `INNGEST_DEV=1`

**Database Service (`postgres`)**
- PostgreSQL 15 with health checks
- Default credentials: `postgres/postgres`
- Database name: `qa-use`
- Data persisted in `./data/postgres` volume

**Background Processing (`inngest`)**
- Inngest development server for job orchestration
- Connects to app service at `http://app:3000/api/inngest`
- Web interface available at port 8288

**Migration Service (`migrate`)**
- Runs Drizzle database migrations on startup
- Depends on healthy PostgreSQL service
- Restarts on failure to ensure migrations complete

**Sources:** [docker-compose.dev.yaml:2-46](), [docker-compose.dev.yaml:57-90]()

### Package Management and Scripts

The project uses `pnpm` as the package manager with the following key scripts defined in `package.json`:

| Script | Purpose |
|--------|---------|
| `dev` | Start Next.js development server with Turbopack |
| `build` | Create production build |
| `start` | Start production server |
| `lint` | Run ESLint checks |
| `test:types` | TypeScript type checking |
| `openapi:gen` | Generate TypeScript definitions from BrowserUse API |

**Sources:** [package.json:5-12]()

### Key Dependencies

The platform relies on several critical dependencies:

**Framework and UI:**
- `next` (15.4.2) - React framework
- `react` (19.1.0) - UI library
- `@radix-ui/*` - UI component primitives
- `tailwindcss` (^4) - CSS framework

**Data and API:**
- `drizzle-orm` (0.44.3) - Type-safe database ORM
- `pg` (8.16.3) - PostgreSQL client
- `openapi-fetch` (0.14.0) - Type-safe API client
- `zod` (4.0.5) - Schema validation

**Background Processing and AI:**
- `inngest` (3.40.1) - Background job orchestration
- `openai` (5.10.2) - OpenAI API client
- `resend` (4.7.0) - Email service

**Sources:** [package.json:13-34]()

## Development Workflow

### Local Development Process

```mermaid
flowchart TD
    START["Start Development"]
    SETUP["docker compose -f docker-compose.dev.yaml up"]
    HEALTH["Wait for Services Health Check"]
    MIGRATE["Auto-run Database Migrations"]
    DEV["Development Ready"]
    
    EDIT["Edit Source Files"]
    RELOAD["Hot Reload"]
    TEST["Test Changes"]
    
    API_GEN["Generate API Types"]
    TYPE_CHECK["Type Checking"]
    LINT["Lint Code"]
    
    START --> SETUP
    SETUP --> HEALTH
    HEALTH --> MIGRATE
    MIGRATE --> DEV
    
    DEV --> EDIT
    EDIT --> RELOAD
    RELOAD --> TEST
    TEST --> EDIT
    
    DEV --> API_GEN
    API_GEN --> TYPE_CHECK
    TYPE_CHECK --> LINT
```

**Sources:** [docker-compose.dev.yaml:8-26](), [package.json:5-12]()

### File Watching and Hot Reload

The development environment provides comprehensive file watching with different strategies for different file types:

**Hot Reload Files (sync):**
- `./src/**/*` - All source code changes trigger immediate reload

**Restart Triggers (sync+restart):**
- `./drizzle.config.ts` - Database configuration changes
- `./next.config.ts` - Next.js configuration changes  
- `./tsconfig.json` - TypeScript configuration changes

**Rebuild Triggers (rebuild):**
- `./package.json` - Dependency changes require container rebuild

**Sources:** [docker-compose.dev.yaml:10-26]()

### API Type Generation

The platform maintains type safety with external APIs through automated type generation:

```bash
pnpm openapi:gen
```

This command fetches the OpenAPI specification from `https://api.browser-use.com/openapi.json` and generates TypeScript definitions at `./src/lib/api/v1.d.ts`.

**Sources:** [package.json:11]()

## Build and Deployment

### Production Build Process

The production build uses a multi-stage Docker approach optimized for size and performance:

```mermaid
graph LR
    subgraph "Build Stages"
        DEPS["deps<br/>node:23-alpine<br/>Install Dependencies"]
        BUILDER["builder<br/>node:23-alpine<br/>Build Application"]
        RUNNER["runner<br/>node:23-alpine<br/>Production Runtime"]
    end
    
    DEPS -->|node_modules| BUILDER
    BUILDER -->|Built App| RUNNER
    
    DEPS_FILES["package.json<br/>pnpm-lock.yaml"] --> DEPS
    SOURCE["Source Code"] --> BUILDER
    FINAL["Production Image"] --> RUNNER
```

**Sources:** [Dockerfile:1-37]()

### Build Stage Details

**Dependencies Stage (`deps`):**
- Base: `node:23-alpine` 
- Installs pnpm and project dependencies
- Uses frozen lockfile for reproducible builds

**Builder Stage (`builder`):**
- Copies dependencies from deps stage
- Copies source code and builds the application
- Runs `pnpm build` to create production assets

**Runner Stage (`runner`):**
- Production-only runtime environment
- Sets `NODE_ENV=production`
- Exposes port 3000
- Runs `pnpm start` command

**Sources:** [Dockerfile:1-8](), [Dockerfile:10-21](), [Dockerfile:24-37]()

### Environment Configuration

The application requires several environment variables for proper operation. The development environment provides defaults for local services, while production requires proper configuration:

**Database Configuration:**
- `DATABASE_URL` - PostgreSQL connection string
- Default dev: `postgresql://postgres:postgres@postgres:5432/qa-use`

**External API Keys:**
- `BROWSER_USE_API_KEY` - BrowserUse API authentication
- `RESEND_API_KEY` - Email service authentication

**Background Processing:**
- `INNGEST_DEV=1` - Enables development mode for Inngest
- `INNGEST_BASE_URL` - Inngest service endpoint

**Sources:** [docker-compose.dev.yaml:28-36]()

### Development vs Production Configuration

The platform uses different configuration files for development and production environments:

| Environment | Compose File | Purpose |
|-------------|--------------|---------|
| Development | `docker-compose.dev.yaml` | Hot reload, file watching, dev services |
| Production | `docker-compose.yaml` | Optimized builds, production settings |

**Sources:** [docker-compose.dev.yaml:1-2]()

This development guide provides the foundation for working with the QA Use platform's codebase. The containerized approach ensures consistent development environments while the hot reloading capabilities enable rapid iteration during development.

---

