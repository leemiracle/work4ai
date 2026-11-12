<!-- source: DeepWiki mcp.deepwiki.com · repo yikart/AiToEarn · page 7 Deployment and Configuration · fetched 2026-10-30 -->

# Deployment and Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [DOCKER_DEPLOYMENT_CN.md](DOCKER_DEPLOYMENT_CN.md)
- [DOCKER_DEPLOYMENT_EN.md](DOCKER_DEPLOYMENT_EN.md)
- [README.md](README.md)
- [README_CN.md](README_CN.md)
- [docker-compose.yml](docker-compose.yml)
- [presentation/agent_0.png](presentation/agent_0.png)
- [presentation/display-1.5.2png.png](presentation/display-1.5.2png.png)
- [wechat.jpg](wechat.jpg)

</details>



This document provides a comprehensive overview of deploying and configuring the AiToEarn platform. It covers the Docker-based deployment architecture, configuration management strategies, and key considerations for both development and production environments.

For step-by-step deployment instructions, see [Docker Deployment Guide](#7.1). For detailed environment variable reference, see [Environment Configuration](#7.2). For database and storage setup details, see [Storage and Database Setup](#7.3).

## Deployment Overview

AiToEarn is designed to be deployed as a containerized application using Docker Compose. The platform consists of seven primary services orchestrated through a single `docker-compose.yml` file, providing a complete deployment with minimal configuration required.

The deployment supports two primary modes:
- **Docker Compose deployment** (recommended): All services run in containers with automated dependency management
- **Development mode**: Backend and frontend run manually outside Docker, connecting to containerized databases

Sources: [README.md:158-189](), [docker-compose.yml:1-286]()

## Docker Compose Service Architecture

The following diagram illustrates the complete service topology as defined in `docker-compose.yml`, including container names, internal ports, and network relationships:

```mermaid
graph TB
    subgraph "External Access"
        Browser["Browser Client"]
        Console["Admin/Developer"]
    end
    
    subgraph "aitoearn-network (bridge)"
        subgraph "Reverse Proxy"
            nginx["nginx<br/>container: aitoearn-nginx<br/>port 8080->80"]
        end
        
        subgraph "Application Services"
            web["aitoearn-web<br/>container: aitoearn-web<br/>internal port 3000<br/>Next.js 14"]
            server["aitoearn-server<br/>container: aitoearn-server<br/>internal port 3002<br/>NestJS"]
            ai["aitoearn-ai<br/>container: aitoearn-ai<br/>internal port 3010<br/>NestJS"]
        end
        
        subgraph "Data Layer"
            mongodb["mongodb<br/>container: aitoearn-mongodb<br/>port 27017<br/>volumes: mongodb-data, mongodb-config"]
            redis["redis<br/>container: aitoearn-redis<br/>port 6379<br/>volume: redis-data"]
            rustfs["rustfs<br/>container: aitoearn-rustfs<br/>hostname: rustfs.local<br/>ports 9000, 9001<br/>volume: rustfs-data"]
        end
        
        init["rustfs-init<br/>container: aitoearn-rustfs-init<br/>mc (MinIO client)"]
    end
    
    Browser -->|"http://localhost:8080"| nginx
    Console -->|"http://localhost:9001"| rustfs
    
    nginx -->|"proxy /"| web
    nginx -->|"proxy /api"| server
    
    web -.->|"SSR calls"| server
    server --> ai
    server --> mongodb
    server --> redis
    server -->|"http://rustfs.local:9000"| rustfs
    ai --> mongodb
    ai --> redis
    ai -->|"http://rustfs.local:9000"| rustfs
    
    init -.->|"create bucket 'aitoearn'"| rustfs
```

Sources: [docker-compose.yml:1-275](), [DOCKER_DEPLOYMENT_EN.md:6-36]()

### Service Dependency Chain

The startup order and health check dependencies ensure proper initialization:

```mermaid
graph TD
    mongodb["mongodb<br/>healthcheck: mongosh ping"]
    redis["redis<br/>healthcheck: redis-cli incr"]
    rustfs["rustfs<br/>healthcheck: curl /health"]
    
    ai["aitoearn-ai<br/>healthcheck: http://localhost:3010/health<br/>depends_on: mongodb, redis (healthy)"]
    
    server["aitoearn-server<br/>healthcheck: http://localhost:3002/health<br/>depends_on: mongodb, redis, ai (healthy)"]
    
    web["aitoearn-web<br/>depends_on: server (healthy)"]
    
    nginx["nginx<br/>healthcheck: wget /_nhealth<br/>depends_on: web, server, ai (healthy)"]
    
    init["rustfs-init<br/>depends_on: rustfs (healthy)"]
    
    mongodb --> ai
    redis --> ai
    
    mongodb --> server
    redis --> server
    ai --> server
    
    server --> web
    
    web --> nginx
    server --> nginx
    ai --> nginx
    
    rustfs --> init
```

Sources: [docker-compose.yml:16-21](), [docker-compose.yml:34-39](), [docker-compose.yml:58-63](), [docker-compose.yml:129-134](), [docker-compose.yml:227-232]()

## Configuration Architecture

AiToEarn employs a two-tier configuration strategy combining environment variables with application-specific config files.

### Configuration Flow Diagram

```mermaid
graph LR
    subgraph "Configuration Sources"
        dcyml["docker-compose.yml<br/>environment sections"]
        configjs_ai["config/aitoearn-ai.config.js"]
        configjs_server["config/aitoearn-server.config.js"]
        gcs["config/gcs-placeholder.json"]
    end
    
    subgraph "Runtime Environment"
        env_ai["aitoearn-ai container<br/>process.env"]
        env_server["aitoearn-server container<br/>process.env"]
        env_web["aitoearn-web container<br/>process.env"]
    end
    
    subgraph "Application Configuration"
        config_ai["AI Service Config<br/>/app/config.js<br/>models, storage, auth"]
        config_server["Server Config<br/>/app/config.js<br/>oauth, mail, storage"]
    end
    
    dcyml -->|"95-128"| env_ai
    dcyml -->|"151-227"| env_server
    dcyml -->|"244-246"| env_web
    
    configjs_ai -->|"mounted read-only"| config_ai
    configjs_server -->|"mounted read-only"| config_server
    gcs -->|"mounted read-only"| config_ai
    
    env_ai -->|"process.env"| config_ai
    env_server -->|"process.env"| config_server
```

Sources: [docker-compose.yml:81-134](), [docker-compose.yml:136-232](), [DOCKER_DEPLOYMENT_EN.md:98-110]()

### Environment Variable Categories

The configuration is organized into distinct functional categories:

| Category | Variables | Services | Purpose |
|----------|-----------|----------|---------|
| **Database** | `MONGODB_HOST`, `MONGODB_PORT`, `MONGODB_USERNAME`, `MONGODB_PASSWORD` | aitoearn-ai, aitoearn-server | MongoDB connection |
| **Cache/Queue** | `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD` | aitoearn-ai, aitoearn-server | Redis connection |
| **Authentication** | `JWT_SECRET`, `INTERNAL_TOKEN` | aitoearn-ai, aitoearn-server | JWT signing and inter-service auth |
| **Inter-Service** | `SERVER_URL`, `AI_URL` | aitoearn-ai, aitoearn-server | Service-to-service URLs |
| **AI Providers** | `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_KEY_PAIRS`, etc. | aitoearn-ai | AI service credentials |
| **OAuth** | `TIKTOK_CLIENT_ID`, `GOOGLE_CLIENT_ID`, `FACEBOOK_CLIENT_ID`, etc. | aitoearn-server | Platform OAuth credentials |
| **Cloud Services** | `ALI_SMS_ACCESS_KEY_ID`, `ALI_GREEN_ACCESS_KEY_ID` | aitoearn-server | Aliyun services |
| **Object Storage** | `RUSTFS_ACCESS_KEY`, `RUSTFS_SECRET_KEY` | rustfs | S3-compatible storage |
| **Frontend** | `NEXT_PUBLIC_API_URL` | aitoearn-web | Browser-facing API endpoint |

Sources: [docker-compose.yml:95-228](), [DOCKER_DEPLOYMENT_EN.md:138-281]()

### Configuration File Structure

The `config/` directory contains JavaScript configuration modules that are mounted into containers:

```mermaid
graph TB
    subgraph "Host: config/"
        ai_config["aitoearn-ai.config.js<br/>- port: 3010<br/>- logger config<br/>- redis/mongodb URIs<br/>- auth settings<br/>- AI model definitions<br/>- assets (RustFS) config"]
        
        server_config["aitoearn-server.config.js<br/>- port: 3002<br/>- logger config<br/>- redis/mongodb URIs<br/>- OAuth callbacks<br/>- mail settings<br/>- assets (RustFS) config"]
        
        gcs_file["gcs-placeholder.json<br/>Google Cloud placeholder"]
    end
    
    subgraph "Container: aitoearn-ai"
        ai_config_mount["/app/config.js (read-only)"]
        gcs_mount["/app/config/gcs-placeholder.json (read-only)"]
    end
    
    subgraph "Container: aitoearn-server"
        server_config_mount["/app/config.js (read-only)"]
    end
    
    ai_config -->|"volume mount"| ai_config_mount
    gcs_file -->|"volume mount"| gcs_mount
    server_config -->|"volume mount"| server_config_mount
```

Sources: [docker-compose.yml:90-92](), [docker-compose.yml:147-148](), [DOCKER_DEPLOYMENT_EN.md:98-110]()

## Network and Port Mapping

The `aitoearn-network` bridge network enables service discovery via container names:

| Service | Container Name | Internal Port | External Port | Access Method |
|---------|----------------|---------------|---------------|---------------|
| nginx | `aitoearn-nginx` | 80 | 8080 | `localhost:8080` |
| aitoearn-web | `aitoearn-web` | 3000 | - | via nginx proxy |
| aitoearn-server | `aitoearn-server` | 3002 | - | via nginx proxy (`/api`) |
| aitoearn-ai | `aitoearn-ai` | 3010 | - | internal only |
| mongodb | `aitoearn-mongodb` | 27017 | 27017 | `localhost:27017` |
| redis | `aitoearn-redis` | 6379 | 6379 | `localhost:6379` |
| rustfs | `aitoearn-rustfs` | 9000, 9001 | 9000, 9001 | `localhost:9000` (API), `localhost:9001` (console) |

**Internal service communication examples:**
- `aitoearn-ai` calls `aitoearn-server` via `http://aitoearn-server:3002` ([docker-compose.yml:112]())
- `aitoearn-server` calls `aitoearn-ai` via `http://aitoearn-ai:3010` ([docker-compose.yml:171]())
- Both services access RustFS via `http://rustfs.local:9000` ([docker-compose.yml:44](), [docker-compose.yml:55-57]())

Sources: [docker-compose.yml:9-10](), [docker-compose.yml:28-29](), [docker-compose.yml:49-51](), [docker-compose.yml:259-260](), [docker-compose.yml:272-275]()

## Volume Persistence

Data persistence is managed through named Docker volumes:

```mermaid
graph LR
    subgraph "Docker Volumes"
        vol_mongo_data["mongodb-data<br/>(driver: local)"]
        vol_mongo_config["mongodb-config<br/>(driver: local)"]
        vol_redis["redis-data<br/>(driver: local)"]
        vol_rustfs["rustfs-data<br/>(driver: local)"]
    end
    
    subgraph "Containers"
        mongodb["mongodb<br/>/data/db<br/>/data/configdb"]
        redis["redis<br/>/data"]
        rustfs["rustfs<br/>/data"]
    end
    
    vol_mongo_data -->|"/data/db"| mongodb
    vol_mongo_config -->|"/data/configdb"| mongodb
    vol_redis -->|"/data"| redis
    vol_rustfs -->|"/data"| rustfs
```

All volumes use the `local` driver and persist data on the Docker host filesystem. Data survives container restarts and recreations but is lost if volumes are explicitly deleted with `docker compose down -v`.

Sources: [docker-compose.yml:11-13](), [docker-compose.yml:30-31](), [docker-compose.yml:52-53](), [docker-compose.yml:277-285]()

## Deployment Workflow

The standard deployment process follows this sequence:

```mermaid
stateDiagram-v2
    [*] --> Clone: git clone repo
    Clone --> Configure: Edit docker-compose.yml<br/>Update passwords, secrets<br/>Add API keys
    Configure --> ConfigFiles: Review/modify config/*.js<br/>Update storage settings<br/>Add AI model configs
    ConfigFiles --> Start: docker compose up -d
    
    Start --> PullImages: Pull images from registry
    PullImages --> CreateNetwork: Create aitoearn-network
    CreateNetwork --> CreateVolumes: Create named volumes
    CreateVolumes --> StartMongo: Start mongodb + healthcheck
    
    StartMongo --> StartRedis: Start redis + healthcheck
    StartRedis --> StartRustFS: Start rustfs + healthcheck
    
    StartRustFS --> InitRustFS: Run rustfs-init<br/>mc mb aitoearn bucket
    StartRustFS --> StartAI: Start aitoearn-ai<br/>Wait for mongo, redis healthy
    
    StartAI --> HealthAI: Healthcheck /health
    HealthAI --> StartServer: Start aitoearn-server<br/>Wait for ai healthy
    
    StartServer --> HealthServer: Healthcheck /health
    HealthServer --> StartWeb: Start aitoearn-web<br/>Wait for server healthy
    
    StartWeb --> StartNginx: Start nginx<br/>Wait for web, server, ai
    StartNginx --> HealthNginx: Healthcheck /_nhealth
    
    HealthNginx --> Ready: Application ready
    Ready --> [*]
    
    note right of Configure
        Required changes:
        - MONGO_INITDB_ROOT_PASSWORD
        - REDIS password (in command)
        - JWT_SECRET
        - INTERNAL_TOKEN
        - APP_DOMAIN (production)
    end note
    
    note right of StartAI
        Depends on:
        - mongodb (healthy)
        - redis (healthy)
    end note
    
    note right of StartServer
        Depends on:
        - mongodb (healthy)
        - redis (healthy)
        - aitoearn-ai (healthy)
    end note
```

Sources: [README.md:163-167](), [docker-compose.yml:85-134](), [docker-compose.yml:140-232]()

## Production Deployment Considerations

### Required Configuration Changes

For production deployment, the following changes are mandatory:

| Configuration | Location | Default | Production Requirement |
|---------------|----------|---------|------------------------|
| `MONGO_INITDB_ROOT_PASSWORD` | [docker-compose.yml:8]() | `password` | Strong random password (32+ chars) |
| `redis --requirepass` | [docker-compose.yml:27]() | `password` | Strong random password (32+ chars) |
| `JWT_SECRET` | [docker-compose.yml:109](), [docker-compose.yml:173]() | `change-this-jwt-secret` | Random secret (use `openssl rand -hex 32`) |
| `INTERNAL_TOKEN` | [docker-compose.yml:110](), [docker-compose.yml:174]() | `change-this-secret-token` | Random token (use `openssl rand -hex 32`) |
| `APP_DOMAIN` | [docker-compose.yml:155]() | `localhost` | Production domain (e.g., `aitoearn.com`) |
| `NEXT_PUBLIC_API_URL` | [docker-compose.yml:246]() | `http://localhost:8080/api` | Public API URL (e.g., `https://aitoearn.com/api`) |
| `RUSTFS_ACCESS_KEY` / `RUSTFS_SECRET_KEY` | [docker-compose.yml:47-48]() | `rustfsadmin` | Strong credentials or switch to AWS S3/Aliyun OSS |

**Critical:** All password/secret changes must be synchronized across all services that reference them. For example, `MONGODB_PASSWORD` appears in three services: `mongodb`, `aitoearn-ai`, and `aitoearn-server`.

Sources: [DOCKER_DEPLOYMENT_EN.md:66-95](), [DOCKER_DEPLOYMENT_CN.md:64-95]()

### OAuth Callback URL Configuration

When `APP_DOMAIN` is changed from `localhost`, OAuth callback URLs must be registered with each platform using the format:

```
https://{APP_DOMAIN}/api/plat/{platform}/auth/back
```

Where `{platform}` is one of: `bilibili`, `google`, `kwai`, `pinterest`, `tiktok`, `twitter`, `facebook`, `threads`, `instagram`, `linkedin`, `youtube`, `wxplat`, `doyin`.

The callback URLs are generated dynamically in the server configuration based on the `APP_DOMAIN` environment variable.

Sources: [DOCKER_DEPLOYMENT_EN.md:269](), [docker-compose.yml:155]()

### External Storage Configuration

For production with AWS S3 or Aliyun OSS, modify the `assets` configuration in both config files:

- [config/aitoearn-ai.config.js]() - Update the `assets` object with provider, region, bucket, endpoint, credentials
- [config/aitoearn-server.config.js]() - Update the `assets` object (must match AI service config)

The configuration should specify:
- `provider`: `'s3'` or `'oss'`
- `region`: AWS region or OSS region
- `bucketName`: Bucket name
- `endpoint`: Service endpoint URL
- `accessKeyId`: Access key
- `secretAccessKey`: Secret key
- `cdnEndpoint`: Optional CDN URL for public access

Sources: [DOCKER_DEPLOYMENT_EN.md:189-202](), [DOCKER_DEPLOYMENT_CN.md:189-202]()

### Statistics Database Separation

By default, the statistics database shares the main MongoDB instance. For production workloads, separate the statistics database by updating:

```yaml
# In aitoearn-server service environment
STATISTICS_DB_HOST: separate-mongo-host
STATISTICS_DB_PORT: 27017
STATISTICS_DB_USERNAME: stats_user
STATISTICS_DB_PASSWORD: stats_password
```

Sources: [docker-compose.yml:162-165](), [DOCKER_DEPLOYMENT_EN.md:162-171]()

### AI Provider Configuration

The recommended approach for AI services is to use a relay/proxy service like [new-api](https://github.com/Calcium-Ion/new-api) or [one-api](https://github.com/songquanpeng/one-api) to consolidate all AI model access through a single endpoint:

```yaml
# In both aitoearn-ai and aitoearn-server services
OPENAI_BASE_URL: https://your-relay-service.com/v1
OPENAI_API_KEY: sk-your-relay-key
```

This approach:
- Simplifies credential management (one key instead of many)
- Provides unified rate limiting and monitoring
- Enables model fallback and load balancing
- Supports multiple AI providers (OpenAI, Claude, Gemini, etc.) through a single interface

Without a relay service, each provider requires separate configuration:
- `OPENAI_API_KEY`, `OPENAI_BASE_URL` ([docker-compose.yml:115-116]())
- `ANTHROPIC_API_KEY`, `ANTHROPIC_BASE_URL` ([docker-compose.yml:117-118]())
- `VOLCENGINE_API_KEY`, `VOLCENGINE_ACCESS_KEY_ID`, `VOLCENGINE_SECRET_ACCESS_KEY` ([docker-compose.yml:119-122]())
- `GROK_API_KEY` ([docker-compose.yml:123]())
- `GEMINI_KEY_PAIRS` as JSON array ([docker-compose.yml:126]())

Sources: [DOCKER_DEPLOYMENT_EN.md:206-247](), [DOCKER_DEPLOYMENT_CN.md:206-247]()

## Health Checks and Monitoring

Each service implements health checks to ensure proper startup ordering and runtime monitoring:

| Service | Health Check | Interval | Timeout | Retries | Start Period |
|---------|--------------|----------|---------|---------|--------------|
| `mongodb` | `mongosh ping` | 10s | 5s | 5 | 40s |
| `redis` | `redis-cli incr ping` | 10s | 3s | 5 | 30s |
| `rustfs` | `curl /health` | 10s | 5s | 5 | 30s |
| `aitoearn-ai` | `http://localhost:3010/health` | 30s | 10s | 3 | 60s |
| `aitoearn-server` | `http://localhost:3002/health` | 30s | 10s | 3 | 60s |
| `nginx` | `wget /_nhealth` | 10s | 5s | 3 | 10s |

Application services expose `/health` endpoints that return HTTP 200 when ready. The nginx service includes a custom health check endpoint at `/_nhealth`.

Check service health status:
```bash
docker compose ps
docker inspect aitoearn-server --format='{{.State.Health.Status}}'
```

Sources: [docker-compose.yml:16-21](), [docker-compose.yml:34-39](), [docker-compose.yml:58-63](), [docker-compose.yml:129-134](), [docker-compose.yml:227-232](), [docker-compose.yml:265-270]()

## Development Mode Deployment

For local development with hot-reload capabilities, services can run outside Docker while using containerized databases:

### Backend Development

```bash
cd project/aitoearn-backend
pnpm install

# Terminal 1: Start AI service
npx nx serve aitoearn-ai

# Terminal 2: Start main server
npx nx serve aitoearn-server
```

The backend services will connect to MongoDB and Redis running in Docker using the exposed ports (27017, 6379). Configuration is read from local config files instead of container-mounted volumes.

Sources: [README.md:199-206](), [README_CN.md:184-191]()

### Frontend Development

```bash
# In repository root
pnpm install
pnpm run dev
```

The Next.js development server runs on port 3000 with hot module replacement. It proxies API requests to the backend services (either containerized or running locally).

Sources: [README.md:210-213](), [README_CN.md:196-199]()

### Mixed Mode Configuration

When running some services in Docker and others locally:

1. Keep MongoDB, Redis, and RustFS running in Docker: `docker compose up -d mongodb redis rustfs rustfs-init`
2. Update local config files to point to `localhost:27017`, `localhost:6379`, `localhost:9000`
3. Run backend/frontend services locally with environment variables matching the Docker configuration

This mode is useful for debugging specific services while maintaining infrastructure stability.

## Common Operations

### View Logs

```bash
# All services
docker compose logs

# Specific service with follow
docker compose logs -f aitoearn-server

# Last 100 lines
docker compose logs --tail=100 aitoearn-ai
```

### Restart Services

```bash
# Restart specific service
docker compose restart aitoearn-server

# Restart after config changes
docker compose up -d --force-recreate aitoearn-server
```

### Update Configuration

After modifying `docker-compose.yml` environment variables or `config/*.js` files:

```bash
# Recreate affected services
docker compose up -d --force-recreate aitoearn-ai aitoearn-server

# Or restart everything
docker compose down
docker compose up -d
```

### Data Backup

```bash
# MongoDB backup
docker exec aitoearn-mongodb mongodump --out /data/backup --authenticationDatabase admin -u admin -p password

# Redis backup (RDB snapshot)
docker exec aitoearn-redis redis-cli --pass password SAVE

# RustFS backup (copy volume)
docker run --rm -v rustfs-data:/data -v $(pwd):/backup alpine tar czf /backup/rustfs-backup.tar.gz /data
```

### Stop and Remove

```bash
# Stop all services (preserves volumes)
docker compose down

# Stop and remove all data (WARNING: deletes all volumes)
docker compose down -v
```

Sources: [README.md:163-167]()

## Related Documentation

- **[Docker Deployment Guide](#7.1)**: Step-by-step deployment instructions with detailed command explanations
- **[Environment Configuration](#7.2)**: Complete reference for all environment variables and their purposes
- **[Storage and Database Setup](#7.3)**: MongoDB configuration, Redis setup, and object storage options including backup strategies

For information about the system architecture, see [System Architecture](#2). For Docker Compose service details, see [Docker Compose Service Architecture](#2.1).

---

