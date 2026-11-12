<!-- source: DeepWiki mcp.deepwiki.com · repo yikart/AiToEarn · page 8 Development Guide · fetched 2026-10-30 -->

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [DOCKER_DEPLOYMENT_CN.md](DOCKER_DEPLOYMENT_CN.md)
- [DOCKER_DEPLOYMENT_EN.md](DOCKER_DEPLOYMENT_EN.md)
- [README.md](README.md)
- [README_CN.md](README_CN.md)
- [docker-compose.yml](docker-compose.yml)
- [presentation/agent_0.png](presentation/agent_0.png)
- [presentation/display-1.5.2png.png](presentation/display-1.5.2png.png)
- [wechat.jpg](wechat.jpg)

</details>



This guide provides essential information for developers who want to contribute to or extend the AiToEarn platform. It covers the development environment setup, codebase structure, architecture patterns, and common workflows.

For step-by-step instructions on running services in development mode, see [Development Mode Setup](#8.1). For detailed information about the project structure and coding conventions, see [Project Structure and Conventions](#8.2). For deployment-related configuration, see [Deployment and Configuration](#7).

## Prerequisites and Technology Stack

### Required Tools

| Tool | Version | Purpose |
|------|---------|---------|
| **Node.js** | 20.18.x | Runtime for all services |
| **pnpm** | Latest | Package manager for monorepo |
| **Docker** | 20.10+ | Container runtime (recommended for dependencies) |
| **Docker Compose** | 2.0+ | Multi-container orchestration |
| **Git** | Latest | Version control |

**Node.js Version Enforcement**: The project strictly requires Node.js 20.18.x as indicated in [README.md:8]().

**Why pnpm?**: The codebase uses pnpm for efficient monorepo package management with workspace support. Both the backend and frontend use pnpm as shown in [README.md:202-214]().

### Core Technology Stack

The AiToEarn platform is built on the following technologies:

**Frontend Stack**:
- **Next.js 14** - React framework with server-side rendering
- **React 18** - UI library
- **TypeScript** - Type-safe JavaScript

**Backend Stack**:
- **NestJS** - Node.js framework for both `aitoearn-server` and `aitoearn-ai`
- **TypeScript** - Type-safe JavaScript
- **Nx** - Monorepo build system for the backend

**Data Layer**:
- **MongoDB** - Primary document database
- **Redis** - Caching and job queue
- **RustFS** - S3-compatible object storage

**Infrastructure**:
- **Docker & Docker Compose** - Containerization
- **Nginx** - Reverse proxy

Sources: [README.md:1-267](), [docker-compose.yml:1-286]()

## Development Approaches

AiToEarn supports two development approaches, each suited for different scenarios:

### Approach 1: Docker Compose (Recommended for Full Stack)

Use Docker Compose when you need all services running together, including databases and storage. This is the easiest way to get started.

**Advantages**:
- Complete environment with one command
- No need to manually install MongoDB, Redis, or RustFS
- Matches production environment closely
- Isolated from your local system

**Use Cases**:
- Testing the complete system
- Working on features that span multiple services
- Reproducing production issues

**Getting Started**: See [Docker Deployment Guide](#7.1).

### Approach 2: Manual Development Mode (Recommended for Active Development)

Run services manually when actively developing backend or frontend code. This approach provides hot-reload capabilities for faster iteration.

**Advantages**:
- Fast hot-reload for code changes
- Direct access to logs and debugging
- Lower resource usage
- Full control over each service

**Use Cases**:
- Backend API development
- Frontend UI development
- Debugging specific services

**Getting Started**: See [Development Mode Setup](#8.1).

### Hybrid Approach

Many developers use a hybrid approach: Docker Compose for dependencies (MongoDB, Redis, RustFS) while running application services manually for hot-reload.

Sources: [README.md:158-217](), [DOCKER_DEPLOYMENT_EN.md:1-52]()

## Monorepo Structure

```mermaid
graph TB
    Root["AiToEarn Repository Root"]
    
    Root --> Backend["project/aitoearn-backend/<br/>(Nx Monorepo)"]
    Root --> Frontend["aitoearn-web/<br/>(Next.js App)"]
    Root --> Config["config/<br/>(Service Configurations)"]
    Root --> Docker["docker-compose.yml<br/>nginx/"]
    Root --> Docs["README.md<br/>DOCKER_DEPLOYMENT_*.md"]
    
    Backend --> AIService["apps/aitoearn-ai/<br/>(NestJS Service)"]
    Backend --> ServerService["apps/aitoearn-server/<br/>(NestJS Service)"]
    Backend --> SharedLibs["libs/<br/>(Shared Libraries)"]
    
    Config --> AIConfig["aitoearn-ai.config.js"]
    Config --> ServerConfig["aitoearn-server.config.js"]
    Config --> GCSPlaceholder["gcs-placeholder.json"]
    
    Frontend --> Pages["pages/<br/>(Routes)"]
    Frontend --> Components["components/<br/>(UI Components)"]
    Frontend --> PublicAssets["public/<br/>(Static Assets)"]
    
    Docker --> ComposeFile["docker-compose.yml<br/>(Service Definitions)"]
    Docker --> NginxConf["nginx/nginx.conf<br/>(Reverse Proxy)"]
    
    classDef backend fill:#e8f5e9
    classDef frontend fill:#e3f2fd
    classDef config fill:#fff3e0
    classDef infra fill:#f3e5f5
    
    class Backend,AIService,ServerService,SharedLibs backend
    class Frontend,Pages,Components,PublicAssets frontend
    class Config,AIConfig,ServerConfig,GCSPlaceholder config
    class Docker,ComposeFile,NginxConf infra
```

**Repository Structure**: The AiToEarn codebase is organized as a multi-package monorepo with separate directories for backend services, frontend application, and configuration files.

### Backend Monorepo (`project/aitoearn-backend`)

The backend uses **Nx** as a monorepo build system to manage multiple NestJS services that share common code. Commands like `npx nx serve aitoearn-ai` and `npx nx serve aitoearn-server` are used to run individual services as shown in [README.md:202-207]().

**Key Characteristics**:
- Nx workspace for build orchestration
- Shared TypeScript libraries in `libs/`
- Two main applications: `aitoearn-ai` and `aitoearn-server`
- Common configuration and utilities

### Frontend Application (`aitoearn-web`)

The frontend is a standalone Next.js 14 application at the repository root level (not inside the backend monorepo).

**Key Characteristics**:
- Independent Next.js project
- Separate `package.json` and dependencies
- Development server: `pnpm run dev` as shown in [README.md:212-214]()

### Configuration Directory (`config/`)

Service configuration files mounted into Docker containers as shown in [docker-compose.yml:91-92, 148]():
- `aitoearn-ai.config.js` - AI service configuration
- `aitoearn-server.config.js` - Backend server configuration  
- `gcs-placeholder.json` - Google Cloud credentials placeholder

### Desktop Application (Separate Repository)

The Electron desktop application is maintained in a separate repository at `https://github.com/yikart/AttAiToEarn` as noted in [README.md:221-243]().

Sources: [README.md:202-214](), [docker-compose.yml:91-92, 148]()

## Service Architecture and Communication

```mermaid
graph TB
    subgraph "Client Layer"
        Browser["Browser<br/>(localhost:8080)"]
        DesktopApp["Electron Desktop App<br/>(AttAiToEarn repo)"]
    end
    
    subgraph "Reverse Proxy"
        Nginx["nginx<br/>container: aitoearn-nginx<br/>port: 8080:80"]
    end
    
    subgraph "Application Services"
        Web["aitoearn-web<br/>container: aitoearn-web<br/>internal port: 3000<br/>Next.js 14"]
        Server["aitoearn-server<br/>container: aitoearn-server<br/>internal port: 3002<br/>NestJS"]
        AI["aitoearn-ai<br/>container: aitoearn-ai<br/>internal port: 3010<br/>NestJS"]
    end
    
    subgraph "Data Layer"
        MongoDB["mongodb<br/>container: aitoearn-mongodb<br/>port: 27017"]
        Redis["redis<br/>container: aitoearn-redis<br/>port: 6379"]
        RustFS["rustfs<br/>container: aitoearn-rustfs<br/>ports: 9000, 9001"]
    end
    
    subgraph "Docker Network"
        Network["aitoearn-network<br/>(bridge driver)"]
    end
    
    Browser --> Nginx
    DesktopApp --> Nginx
    
    Nginx -->|"/ → :3000"| Web
    Nginx -->|"/api → :3002"| Server
    
    Web -->|"NEXT_PUBLIC_API_URL"| Server
    Server -->|"AI_URL=http://aitoearn-ai:3010"| AI
    AI -->|"SERVER_URL=http://aitoearn-server:3002"| Server
    
    Server --> MongoDB
    Server --> Redis
    Server -->|"http://rustfs.local:9000"| RustFS
    
    AI --> MongoDB
    AI --> Redis
    AI -->|"http://rustfs.local:9000"| RustFS
    
    Web -.->|"runs in"| Network
    Server -.->|"runs in"| Network
    AI -.->|"runs in"| Network
    MongoDB -.->|"runs in"| Network
    Redis -.->|"runs in"| Network
    RustFS -.->|"runs in"| Network
    Nginx -.->|"runs in"| Network
```

**Container Names and Networking**: All services communicate via the `aitoearn-network` Docker bridge network defined in [docker-compose.yml:272-275](). Container names (e.g., `aitoearn-mongodb`, `aitoearn-redis`) serve as DNS names within this network.

**Service Communication Patterns**:

1. **Frontend to Backend**: The web frontend connects to the backend via `NEXT_PUBLIC_API_URL` environment variable, which is set to `http://localhost:8080/api` by default in [docker-compose.yml:246]() but proxied through Nginx.

2. **Server to AI Service**: The main server calls the AI service using `AI_URL=http://aitoearn-ai:3010` as configured in [docker-compose.yml:171]().

3. **AI to Server**: The AI service calls back to the server using `SERVER_URL=http://aitoearn-server:3002` as configured in [docker-compose.yml:112]().

4. **RustFS Access**: Both backend services access RustFS via the hostname alias `rustfs.local` defined in [docker-compose.yml:56-57]().

**Port Mapping**:
- External port `8080` maps to Nginx's internal port `80` ([docker-compose.yml:260]())
- MongoDB, Redis, and RustFS expose ports directly for development access
- Application services (web, server, ai) are only accessible through Nginx or the Docker network

Sources: [docker-compose.yml:1-286](), [DOCKER_DEPLOYMENT_EN.md:6-36]()

## Development Workflow

```mermaid
graph LR
    subgraph "Local Development"
        Code["Edit Code<br/>(VSCode/IDE)"]
        Install["pnpm install<br/>(Install Dependencies)"]
        DevServer["Start Dev Server<br/>(Hot Reload)"]
        Test["Manual Testing<br/>(Browser/API Client)"]
    end
    
    subgraph "Backend Development"
        BackendCode["Edit TypeScript<br/>in project/aitoearn-backend"]
        NxServe["npx nx serve<br/>aitoearn-server<br/>or aitoearn-ai"]
        BackendTest["Test API Endpoints<br/>(Postman/curl)"]
    end
    
    subgraph "Frontend Development"
        FrontendCode["Edit React/Next.js<br/>in aitoearn-web"]
        NextDev["pnpm run dev<br/>(Next.js Dev Server)"]
        BrowserTest["Test UI<br/>(localhost:3000)"]
    end
    
    subgraph "Dependencies"
        Docker["docker compose up -d<br/>(MongoDB, Redis, RustFS)"]
    end
    
    Code --> Install
    Install --> DevServer
    DevServer --> Test
    
    BackendCode --> NxServe
    NxServe --> BackendTest
    
    FrontendCode --> NextDev
    NextDev --> BrowserTest
    
    NxServe -.->|"requires"| Docker
    NextDev -.->|"calls"| NxServe
```

### Typical Development Workflow

**For Backend Development**:

1. **Start Dependencies** (one-time per session):
   ```bash
   docker compose up -d mongodb redis rustfs
   ```

2. **Navigate to Backend Directory**:
   ```bash
   cd project/aitoearn-backend
   ```

3. **Install Dependencies** (first time or after package changes):
   ```bash
   pnpm install
   ```

4. **Start Service with Hot Reload**:
   ```bash
   # For AI service
   npx nx serve aitoearn-ai
   
   # For main server (in another terminal)
   npx nx serve aitoearn-server
   ```

5. **Make Changes**: Edit TypeScript files in `apps/aitoearn-ai/` or `apps/aitoearn-server/`

6. **Hot Reload**: Changes automatically trigger rebuild and server restart

**For Frontend Development**:

1. **Ensure Backend is Running** (see above)

2. **Navigate to Frontend Directory**:
   ```bash
   cd aitoearn-web  # (from repository root)
   ```

3. **Install Dependencies** (first time or after package changes):
   ```bash
   pnpm install
   ```

4. **Start Development Server**:
   ```bash
   pnpm run dev
   ```

5. **Access Frontend**: Open browser to `http://localhost:3000`

6. **Make Changes**: Edit files in `pages/`, `components/`, etc.

7. **Hot Reload**: Changes appear immediately in browser via Next.js Fast Refresh

**For Full Stack Testing**:

Use the Docker Compose approach to run everything together:
```bash
docker compose up -d
```
Access at `http://localhost:8080` as shown in [README.md:163-181]().

Sources: [README.md:194-217](), [DOCKER_DEPLOYMENT_EN.md:52-135]()

## Architecture Patterns

### NestJS Module Pattern

Both backend services (`aitoearn-server` and `aitoearn-ai`) follow NestJS architecture patterns:

**Module Organization**:
- **Controllers**: Handle HTTP requests and routing
- **Services**: Contain business logic
- **Providers**: Injectable dependencies
- **Modules**: Group related functionality

**Typical Module Structure**:
```
apps/aitoearn-server/src/
  ├── auth/           (Authentication module)
  ├── plat/           (Platform integration module)
  ├── ai/             (AI integration module)
  └── app.module.ts   (Root module)
```

**Dependency Injection**: NestJS uses decorators like `@Injectable()`, `@Controller()`, and `@Module()` for dependency management.

### Next.js App Structure

The frontend follows Next.js conventions:

**File-Based Routing**: Files in `pages/` directory automatically become routes
- `pages/index.tsx` → `/`
- `pages/dashboard.tsx` → `/dashboard`
- `pages/api/[...].ts` → API routes (if used)

**Component Organization**: Reusable UI components live in `components/` directory

**Static Assets**: Public files (images, fonts, etc.) in `public/` directory

### Shared Configuration Pattern

Configuration is centralized in the `config/` directory and mounted as read-only volumes:
- [docker-compose.yml:91-92]() mounts `aitoearn-ai.config.js`
- [docker-compose.yml:148]() mounts `aitoearn-server.config.js`

This allows changing configuration without rebuilding Docker images.

### Environment-Based Configuration

Services read configuration from multiple sources with precedence:
1. Environment variables (from `docker-compose.yml`)
2. Config files (`config/*.config.js`)
3. Default values in code

Example from [docker-compose.yml:95-98]():
```yaml
NODE_ENV: production
APP_ENV: production
APP_NAME: aitoearn-ai
```

Sources: [docker-compose.yml:81-135, 136-232]()

## Key Development Concepts

### Internal Service Authentication

Services authenticate with each other using the `INTERNAL_TOKEN` environment variable. Both `aitoearn-server` and `aitoearn-ai` must have matching tokens as configured in [docker-compose.yml:110, 174]().

### JWT-Based User Authentication

User authentication uses JWT tokens signed with the `JWT_SECRET`. The same secret must be configured across services ([docker-compose.yml:109, 173]()).

### Monorepo Task Execution

The backend uses Nx for task execution:
- `npx nx serve <app>` - Run development server
- `npx nx build <app>` - Build application
- `npx nx test <app>` - Run tests
- `npx nx lint <app>` - Run linter

### Hot Reload Mechanism

**Backend**: Nx watch mode automatically rebuilds and restarts services when TypeScript files change

**Frontend**: Next.js Fast Refresh updates React components in browser without losing state

### Database Connection

Services connect to MongoDB using connection strings constructed from environment variables. Example from [docker-compose.yml:100-103]():
```yaml
MONGODB_HOST: mongodb
MONGODB_PORT: 27017
MONGODB_USERNAME: admin
MONGODB_PASSWORD: password
```

The actual connection URI is built in the service's config file.

### Redis for Caching and Queues

Redis serves dual purposes:
- **Caching**: Session data, frequently accessed data
- **Job Queue**: Background tasks, scheduled content publishing

Configuration in [docker-compose.yml:105-107]().

### Object Storage Integration

Services access RustFS (or external S3) for asset storage. The storage configuration is defined in the `config/*.config.js` files and includes:
- Provider type (`s3`, `rustfs`)
- Endpoint URL
- Access credentials
- Bucket name

Sources: [docker-compose.yml:81-232](), [DOCKER_DEPLOYMENT_EN.md:173-202]()

## Version Control and Collaboration

### Ignored Files

The `.gitignore` configuration excludes:

**Build Artifacts**: `dist`, `dist-ssr`, `dist-electron`, `release` ([.gitignore:10-13]())

**Dependencies**: `node_modules` ([.gitignore:9]())

**Environment Files**: `.env` is commented out, meaning environment files ARE tracked in the repo ([.gitignore:25]())

**Lock Files**: Package lock files are commented out, meaning they ARE tracked ([.gitignore:28-30]())

**Local Files**: `*.local` ([.gitignore:14]())

**IDE Directories**: `.vscode`, `.idea` ([.gitignore:15-18]())

**Database Files**: `*.db` ([.gitignore:36]())

**Executables**: `*.exe` ([.gitignore:39]())

**Binary Directories**: `public/bin/*` with exceptions ([.gitignore:42-44]())

**Custom Paths**: `sh/*`, `project/web/.cursor/` ([.gitignore:46-47]())

### Package Manager Choice

The project uses **pnpm** exclusively. Lock files (`pnpm-lock.yaml`) are tracked in version control, ensuring consistent dependency versions across environments.

### Monorepo Coordination

When making changes that affect multiple services:
1. Update shared libraries in `project/aitoearn-backend/libs/`
2. Update affected services
3. Rebuild all services to ensure compatibility
4. Test integration between services

Sources: [.gitignore:1-48]()

## Testing and Debugging

### Local Testing

**Backend API Testing**:
- Use tools like Postman, Insomnia, or curl
- Backend API runs on `http://localhost:3002` when started manually
- Through Docker/Nginx: `http://localhost:8080/api`

**Frontend Testing**:
- Access `http://localhost:3000` in development mode
- Through Docker/Nginx: `http://localhost:8080`

**Database Access**:
- MongoDB: `mongodb://admin:password@localhost:27017` (when running via Docker)
- Redis: `redis://localhost:6379` with password `password`
- RustFS Console: `http://localhost:9001`

### Health Checks

Services expose health check endpoints:
- `aitoearn-server`: `/health` endpoint ([docker-compose.yml:228]())
- `aitoearn-ai`: `/health` endpoint ([docker-compose.yml:130]())
- Nginx: `/_nhealth` endpoint ([docker-compose.yml:266]())

### Log Access

**Docker Logs**:
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f aitoearn-server
```

**Development Mode Logs**: 
Logs appear directly in the terminal where you ran `npx nx serve` or `pnpm run dev`

Sources: [docker-compose.yml:129-134, 227-232, 265-270]()

## External Dependencies and Services

### Third-Party Platform Integration

The platform integrates with 14+ social media platforms. OAuth configuration is required for each platform in [docker-compose.yml:183-213](). See [Supported Platforms](#4.2) for details.

Each platform requires:
- Client ID
- Client Secret  
- Callback URL configuration (format: `https://{APP_DOMAIN}/api/plat/{platform}/auth/back`)

### AI Provider Configuration

Multiple AI providers are supported. See [AI Integration System](#3) for architecture details.

**Recommended Approach**: Use a relay service like new-api or one-api to manage all AI models through a single endpoint as documented in [DOCKER_DEPLOYMENT_EN.md:206-220]().

Configuration in [docker-compose.yml:114-128]().

### Cloud Services

**Aliyun SMS** (optional): For SMS notifications ([docker-compose.yml:214-218]())

**Aliyun Content Safety** (optional): For content moderation ([docker-compose.yml:220-222]())

**Email Service** (optional): AWS SES SMTP credentials ([docker-compose.yml:176-177]())

Sources: [docker-compose.yml:114-227](), [DOCKER_DEPLOYMENT_EN.md:206-281]()

## Next Steps

Now that you understand the development environment and architecture:

1. **Set Up Your Development Environment**: Follow the step-by-step instructions in [Development Mode Setup](#8.1) to get your local environment running.

2. **Understand the Codebase Structure**: Read [Project Structure and Conventions](#8.2) for detailed information about directory layout, naming conventions, and important files.

3. **Review Architecture Details**: 
   - [System Architecture](#2) for high-level system design
   - [AI Integration System](#3) for AI service details
   - [Platform Integration System](#4) for social media integration

4. **Configure Your Environment**: See [Environment Configuration](#7.2) for comprehensive environment variable reference.

5. **Explore Deployment**: Review [Docker Deployment Guide](#7.1) to understand how the application is deployed.

Sources: [README.md:1-267](), [docker-compose.yml:1-286](), [.gitignore:1-48](), [DOCKER_DEPLOYMENT_EN.md:1-135]()

---

