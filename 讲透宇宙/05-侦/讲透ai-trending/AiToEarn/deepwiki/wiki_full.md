# Page: Overview

# Overview

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



AiToEarn is a comprehensive AI-powered content marketing platform that enables creators, brands, and businesses to build, distribute, and monetize content across 14+ global social media platforms. The system provides an integrated environment for AI-assisted content creation, multi-platform publishing, automated engagement, and analytics through both web and desktop interfaces.

Sources: [README.md:2-21](), [README.md:66-70]()

## System Purpose

AiToEarn serves as a full-stack growth and monetization platform designed to streamline the entire content marketing lifecycle. The platform addresses key pain points for content creators and businesses:

**Content Creation & Management**
- AI-powered content generation for text, images, and video
- Content drafting and version control
- Multi-format content support
- Calendar-based content scheduling

**Multi-Platform Distribution**
- One-click publishing to 14+ platforms simultaneously
- Platform-specific content adaptation
- Scheduled and calendar-timed publishing
- Import and redistribution of historical content

**Engagement & Growth**
- Automated comment responses and interaction management
- Hotspot and trend detection across platforms
- Brand monitoring and content discovery
- Precision user mining through comment analysis

**Analytics & Monetization**
- Cross-platform performance tracking
- Full-funnel data analysis
- Revenue tracking and campaign management

**AI Automation**
- All In Agent: Autonomous AI agent for content creation and platform operation
- Multi-provider AI model orchestration (OpenAI, Claude, Gemini, Grok, Doubao, AICSO)

Sources: [README.md:66-158](), [README.md:30-36]()

## Supported Platforms

AiToEarn integrates with the widest range of global social media platforms:

| Platform Category | Platforms |
|-------------------|-----------|
| **Chinese Platforms** | Douyin, Xiaohongshu (Rednote), WeChat Channels, WeChat Official Accounts, Kuaishou, Bilibili |
| **Global Platforms** | TikTok, YouTube, Facebook, Instagram, Threads, Twitter/X, Pinterest, LinkedIn |

Sources: [README.md:18-20]()

## System Architecture

AiToEarn follows a microservices architecture with three main application services, orchestrated through Docker Compose.

### High-Level Service Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Browser["Web Browser"]
        Desktop["AttAiToEarn Desktop<br/>(Electron)"]
    end
    
    subgraph "Reverse Proxy"
        Nginx["nginx:80<br/>aitoearn-nginx"]
    end
    
    subgraph "Application Services"
        Web["aitoearn-web:3000<br/>Next.js Frontend"]
        Server["aitoearn-server:3002<br/>NestJS Backend API"]
        AI["aitoearn-ai:3010<br/>NestJS AI Service"]
    end
    
    subgraph "Data Layer"
        MongoDB["mongodb:27017<br/>aitoearn-mongodb<br/>Document Database"]
        Redis["redis:6379<br/>aitoearn-redis<br/>Cache & Queue"]
        RustFS["rustfs:9000/9001<br/>aitoearn-rustfs<br/>S3-Compatible Storage"]
    end
    
    subgraph "External Services"
        AI_Providers["AI Providers<br/>OpenAI, Claude, Gemini<br/>Grok, Doubao, AICSO"]
        Social_Platforms["Social Media APIs<br/>TikTok, YouTube, Twitter<br/>Instagram, LinkedIn, etc."]
        Cloud_Services["Cloud Services<br/>Aliyun SMS<br/>Content Safety"]
    end
    
    Browser --> Nginx
    Desktop --> Nginx
    Nginx --> Web
    Nginx --> Server
    
    Web --> Server
    Server --> AI
    
    Server --> MongoDB
    Server --> Redis
    Server --> RustFS
    
    AI --> MongoDB
    AI --> Redis
    AI --> RustFS
    
    AI --> AI_Providers
    Server --> Social_Platforms
    Server --> Cloud_Services
```

**Docker Compose Service Architecture**

Sources: [docker-compose.yml:1-286]()

The system consists of seven containerized services defined in `docker-compose.yml`:

| Service Container | Image | Internal Port | External Port | Purpose |
|-------------------|-------|---------------|---------------|---------|
| `aitoearn-nginx` | nginx:alpine | 80 | 8080 | Reverse proxy and unified entry point |
| `aitoearn-web` | aitoearn/aitoearn-web | 3000 | - | Next.js frontend application |
| `aitoearn-server` | aitoearn/aitoearn-server | 3002 | - | Main backend API service |
| `aitoearn-ai` | aitoearn/aitoearn-ai | 3010 | - | AI orchestration service |
| `aitoearn-mongodb` | mongo:latest | 27017 | 27017 | Primary database |
| `aitoearn-redis` | redis:latest | 6379 | 6379 | Cache and job queue |
| `aitoearn-rustfs` | rustfs/rustfs | 9000, 9001 | 9000, 9001 | Object storage for assets |

All services communicate through a Docker bridge network named `aitoearn-network`.

Sources: [docker-compose.yml:2-271]()

### Request Flow

```mermaid
sequenceDiagram
    participant User
    participant Nginx as "nginx<br/>:8080"
    participant Web as "aitoearn-web<br/>:3000"
    participant Server as "aitoearn-server<br/>:3002"
    participant AI as "aitoearn-ai<br/>:3010"
    participant MongoDB
    participant Redis
    participant RustFS as "rustfs<br/>:9000"
    
    User->>Nginx: HTTP Request
    
    alt Static Assets / Frontend
        Nginx->>Web: Proxy to Next.js
        Web->>User: HTML/JS/CSS
    else API Calls
        Nginx->>Server: Proxy to /api/*
        Server->>MongoDB: Query Data
        Server->>Redis: Cache Check
        
        alt AI Operation
            Server->>AI: AI Request
            AI->>MongoDB: Save AI State
            AI-->>Server: AI Response
        end
        
        Server->>RustFS: Store/Retrieve Assets
        Server->>User: JSON Response
    end
```

Sources: [docker-compose.yml:248-270](), [README.md:170-182]()

### Access Points

After deployment, the system is accessible through:

| Endpoint | URL | Description |
|----------|-----|-------------|
| Web Frontend | http://localhost:8080 | Main user interface |
| Backend API | http://localhost:8080/api | RESTful API endpoints |
| RustFS Console | http://localhost:9001 | Object storage management |
| MongoDB | localhost:27017 | Database (internal) |
| Redis | localhost:6379 | Cache/Queue (internal) |

Sources: [README.md:170-182]()

## Core Capabilities

### 1. All In Agent - Autonomous AI Assistant

The All In Agent is an autonomous AI agent that can automatically generate content, publish to platforms, and help operate AiToEarn. This agent represents the most advanced automation layer of the platform.

Sources: [README.md:33-33](), [README.md:71-76]()

### 2. Multi-Platform Content Publishing

**One-Click Multi-Platform Distribution**
- Simultaneous publishing to 14+ platforms
- Platform-specific content adaptation
- Calendar-based scheduling system
- Historical content import and redistribution

**Content Types Supported**
- Video content
- Image/text posts
- Stories and short-form content

Sources: [README.md:79-89]()

### 3. Hotspot Analysis & Trending Content

**Viral Inspiration Engine**
- Case library of high-engagement content (10,000+ likes)
- Real-time trend detection across platforms
- Topic discovery for content ideation
- Reduces creator anxiety through data-driven insights

Sources: [README.md:91-100]()

### 4. Content Search & Brand Monitoring

**Market Insights**
- Real-time brand conversation tracking
- Content discovery by topic and community
- Targeted engagement opportunities
- Competitor analysis

Sources: [README.md:102-112]()

### 5. Comment Search & User Mining

**Precision User Identification**
- Smart comment detection (e.g., "link please", "how to buy")
- High-conversion signal identification
- Instant reply capabilities
- Sales funnel optimization

Sources: [README.md:115-122]()

### 6. Engagement Automation

**Growth Engine**
- Unified interaction management dashboard
- Proactive trending conversation participation
- Automated comment responses
- Community building tools

Sources: [README.md:124-132]()

### 7. Cross-Platform Analytics

**Full-Funnel Data Analysis**
- Performance comparison across platforms
- Traffic flow monitoring
- End-to-end conversion tracking
- Growth path visualization

Sources: [README.md:134-139]()

### 8. AI Content Creation (Coming Soon)

**End-to-End AI Assistant**
- AI-generated titles, captions, and descriptions
- AI-powered commenting for engagement
- Image and card generation
- Video editing assistance
- Multi-language translation for global distribution

**Supported AI Models**
- Video: Seedance, Kling, Hailuo, Veo, Midjourney, Sora, Pika, Runway
- Image: GPT, Flux

Sources: [README.md:141-149]()

## Technology Stack

### Frontend Layer

| Technology | Purpose |
|------------|---------|
| Next.js 14 | React framework with SSR/SSG |
| React 18 | UI component library |
| TypeScript | Type-safe development |

Sources: [README.md:1-267]()

### Backend Services

| Service | Technology | Purpose |
|---------|------------|---------|
| aitoearn-server | NestJS + Node.js + TypeScript | Main API service, OAuth management, platform integration |
| aitoearn-ai | NestJS + Node.js + TypeScript | AI model orchestration, content generation |

Sources: [docker-compose.yml:136-233](), [docker-compose.yml:81-134]()

### Data Layer

| Component | Technology | Purpose |
|-----------|------------|---------|
| Primary Database | MongoDB | User data, content metadata, OAuth tokens |
| Cache & Queue | Redis | Session management, job queues, rate limiting |
| Object Storage | RustFS (S3-compatible) | Images, videos, documents |

Sources: [docker-compose.yml:2-40](), [docker-compose.yml:41-79]()

### Infrastructure

| Component | Technology |
|-----------|------------|
| Containerization | Docker & Docker Compose |
| Reverse Proxy | Nginx |
| Networking | Docker bridge network (aitoearn-network) |
| Persistence | Docker volumes |

Sources: [docker-compose.yml:272-286]()

### External Integrations

**AI Providers**
- OpenAI (GPT-5)
- Anthropic (Claude Opus 4.5/4.6)
- Google (Gemini 2.5/3.1)
- xAI (Grok)
- Volcengine (Doubao)
- AICSO

**Social Media Platforms**
- OAuth 2.0 authentication for all 14+ platforms
- Platform-specific API clients
- Webhook handlers for real-time events

**Cloud Services**
- Aliyun SMS for notifications
- Aliyun Content Safety for moderation

Sources: [docker-compose.yml:114-128](), [docker-compose.yml:184-226]()

## Deployment Architecture

AiToEarn uses Docker Compose for orchestration, providing easy deployment and scaling.

### Production Deployment Flow

```mermaid
graph TB
    subgraph "Docker Host"
        subgraph "Frontend Tier"
            LB["nginx<br/>Load Balancer<br/>:8080"]
        end
        
        subgraph "Application Tier"
            Web1["aitoearn-web<br/>Next.js SSR<br/>:3000"]
            Server1["aitoearn-server<br/>NestJS API<br/>:3002"]
            AI1["aitoearn-ai<br/>AI Service<br/>:3010"]
        end
        
        subgraph "Data Tier"
            Mongo["mongodb<br/>Replica Set<br/>:27017"]
            Redis_Master["redis<br/>Master<br/>:6379"]
            S3["rustfs<br/>S3 Storage<br/>:9000"]
        end
        
        subgraph "Persistence"
            MongoVol["mongodb-data<br/>volume"]
            RedisVol["redis-data<br/>volume"]
            RustFSVol["rustfs-data<br/>volume"]
        end
    end
    
    LB --> Web1
    LB --> Server1
    
    Web1 --> Server1
    Server1 --> AI1
    
    Server1 --> Mongo
    Server1 --> Redis_Master
    Server1 --> S3
    
    AI1 --> Mongo
    AI1 --> Redis_Master
    AI1 --> S3
    
    Mongo -.->|persists to| MongoVol
    Redis_Master -.->|persists to| RedisVol
    S3 -.->|persists to| RustFSVol
```

Sources: [docker-compose.yml:1-286]()

### Environment Configuration

The system uses environment variables for configuration, all defined in `docker-compose.yml`. Key configuration categories:

**Service Credentials**
- MongoDB root password and connection strings
- Redis authentication
- JWT secrets for authentication
- Internal service communication tokens

**AI Service Configuration**
- API keys for OpenAI, Anthropic, Google, xAI, Volcengine, AICSO
- Base URLs for AI providers (supports proxy configuration)
- Model-specific credentials (e.g., `GEMINI_KEY_PAIRS`)

**OAuth Configuration**
- Client IDs and secrets for 14+ platforms
- Callback URL configuration via `APP_DOMAIN`

**Storage Configuration**
- RustFS/S3 credentials and endpoints
- CDN configuration
- Bucket names and regions

**Optional Services**
- Email service (AWS SES SMTP)
- Aliyun SMS credentials
- Aliyun Content Safety credentials

Sources: [docker-compose.yml:6-227](), [DOCKER_DEPLOYMENT_EN.md:138-281]()

### Desktop Application

AiToEarn also provides an Electron desktop application (`AttAiToEarn`) in a separate repository. The desktop app connects to the same backend API services but offers native OS integration:

- Native window management
- System tray integration
- Local database for offline access
- Desktop notifications

Sources: [README.md:220-242]()

## Summary

AiToEarn represents a sophisticated solution for content creators targeting Chinese social media platforms. By providing a unified interface and powerful automation tools, it simplifies the management of multiple accounts across different platforms. The application's modular architecture allows for easy extension with new platforms and features.

For more detailed information about specific subsystems, refer to the following pages:
- For platform integration details, see [Platform Integration System](#3)
- For content publishing workflow, see [Content Publishing System](#4)
- For automated engagement features, see [Automated Engagement System](#5)
- For AI tools integration, see [AI Tools Integration](#8)

---

# Page: System Architecture

# System Architecture

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



AiToEarn is a full-stack AI-powered content marketing system built on a microservices architecture. The platform enables content creators, brands, and businesses to create, publish, engage, and monetize content across 14+ social media platforms with AI automation.

This document provides a high-level overview of the system architecture, including the microservices design, technology stack, and how components interact.

For an introduction to the application's purpose and capabilities, see [Overview](#1).

## Architectural Overview

AiToEarn implements a microservices architecture with three primary application services orchestrated through Docker Compose, fronted by an nginx reverse proxy, and backed by MongoDB for persistence, Redis for caching/queuing, and S3-compatible object storage (RustFS) for media assets.

### High-Level System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Browser["Web Browser"]
        Desktop["Desktop App<br/>(Electron)"]
    end
    
    subgraph "Gateway Layer"
        Nginx["nginx:80<br/>Reverse Proxy"]
    end
    
    subgraph "Application Layer"
        Web["aitoearn-web:3000<br/>Next.js 14 Frontend"]
        Server["aitoearn-server:3002<br/>NestJS Backend API"]
        AI["aitoearn-ai:3010<br/>NestJS AI Service"]
    end
    
    subgraph "Data Layer"
        MongoDB["mongodb:27017<br/>Document Database"]
        Redis["redis:6379<br/>Cache & Queue"]
        RustFS["rustfs:9000/9001<br/>S3-Compatible Storage"]
    end
    
    subgraph "External Services"
        SocialPlatforms["Social Media APIs<br/>TikTok, YouTube, Twitter, etc."]
        AIProviders["AI Providers<br/>OpenAI, Claude, Gemini, etc."]
        CloudServices["Cloud Services<br/>Aliyun SMS, Content Safety"]
    end
    
    Browser --> Nginx
    Desktop --> Nginx
    Nginx --> Web
    Nginx --> Server
    Nginx --> AI
    
    Web --> Server
    Server --> AI
    
    Server --> MongoDB
    Server --> Redis
    Server --> RustFS
    
    AI --> MongoDB
    AI --> Redis
    AI --> RustFS
    
    Server --> SocialPlatforms
    Server --> CloudServices
    AI --> AIProviders
    
    style Nginx fill:#f9f9f9
    style Web fill:#e1f5ff
    style Server fill:#fff4e1
    style AI fill:#e8f5e9
    style MongoDB fill:#e8f5e9
    style Redis fill:#e8f5e9
    style RustFS fill:#e8f5e9
```

Sources: [docker-compose.yml:1-286](), [README.md:158-183]()

### Service Container Architecture

The Docker Compose configuration defines seven interconnected services running on a dedicated bridge network (`aitoearn-network`). Each service has defined health checks and dependency ordering to ensure proper startup sequence.

#### Service Dependency Graph

```mermaid
graph TD
    subgraph "Service Dependencies"
        MongoDB["mongodb<br/>health: ping"]
        Redis["redis<br/>health: ping"]
        RustFS["rustfs<br/>health: /health"]
        RustFSInit["rustfs-init<br/>one-time setup"]
        AI["aitoearn-ai<br/>health: :3010/health"]
        Server["aitoearn-server<br/>health: :3002/health"]
        Web["aitoearn-web"]
        Nginx["nginx<br/>health: /_nhealth"]
    end
    
    MongoDB -.->|healthy| AI
    Redis -.->|healthy| AI
    MongoDB -.->|healthy| Server
    Redis -.->|healthy| Server
    RustFS -.->|healthy| RustFSInit
    AI -.->|healthy| Server
    Server -.->|healthy| Web
    Web -.->|started| Nginx
    Server -.->|healthy| Nginx
    AI -.->|healthy| Nginx
```

Sources: [docker-compose.yml:2-286]()

The startup sequence ensures data services are ready before application services begin, and all application services are healthy before nginx begins accepting traffic. The `rustfs-init` container runs once to create the storage bucket and set permissions.

### Network Communication

All services communicate over a dedicated Docker bridge network (`aitoearn-network`) using internal DNS resolution. External access is routed through nginx on port 8080.

#### Port Mapping

| Service | Internal Port | External Port | Purpose |
|---------|--------------|---------------|---------|
| nginx | 80 | 8080 | HTTP gateway |
| aitoearn-web | 3000 | - | Next.js SSR |
| aitoearn-server | 3002 | - | Backend API |
| aitoearn-ai | 3010 | - | AI service API |
| mongodb | 27017 | 27017 | Database (dev access) |
| redis | 6379 | 6379 | Cache (dev access) |
| rustfs | 9000 | 9000 | S3 API |
| rustfs | 9001 | 9001 | Management console |

Sources: [docker-compose.yml:10-11](), [docker-compose.yml:29-30](), [docker-compose.yml:49-51](), [docker-compose.yml:260]()

Services use internal hostnames (e.g., `mongodb`, `redis`, `rustfs.local`) for inter-service communication, while nginx handles all external routing.

## Core Services

AiToEarn's functionality is distributed across three specialized NestJS microservices, each with distinct responsibilities.

### aitoearn-web (Frontend Service)

The web frontend is a Next.js 14 application serving the user interface. It runs in production mode within a Docker container and communicates with backend services through nginx.

**Technology Stack:**
- Next.js 14 with React 18
- TypeScript
- Server-Side Rendering (SSR)

**Environment Configuration:**
- `NEXT_PUBLIC_API_URL`: Public API endpoint for browser-side requests (default: `http://localhost:8080/api`)
- `NODE_ENV`: Set to `production` in Docker deployment
- `NEXT_TELEMETRY_DISABLED`: Telemetry disabled for privacy

Sources: [docker-compose.yml:234-246](), [README.md:66-157]()

### aitoearn-server (Backend API Service)

The main backend service handles core business logic, user management, OAuth flows, platform integrations, and content publishing.

**Responsibilities:**
- User authentication and authorization (JWT)
- OAuth 2.0 flows for 14+ social media platforms
- Multi-platform content publishing
- Engagement automation
- Analytics data collection
- Third-party service integrations (SMS, content safety)

**Configuration:**
```yaml
# Key environment variables
JWT_SECRET: JWT signing key
INTERNAL_TOKEN: Inter-service authentication
APP_DOMAIN: Domain for OAuth callbacks

# Database connections
MONGODB_HOST: mongodb
REDIS_HOST: redis

# AI service communication
AI_URL: http://aitoearn-ai:3010

# Platform OAuth credentials
TIKTOK_CLIENT_ID/SECRET
YOUTUBE_CLIENT_ID/SECRET
TWITTER_CLIENT_ID/SECRET
# ... (14+ platforms)

# Cloud services
ALI_SMS_ACCESS_KEY_ID/SECRET
ALI_GREEN_ACCESS_KEY_ID/SECRET
```

Sources: [docker-compose.yml:136-232](), [DOCKER_DEPLOYMENT_EN.md:251-270]()

### aitoearn-ai (AI Engine Service)

The AI service orchestrates multiple AI providers for content generation, providing a unified interface for text, image, and video generation across different models.

**Responsibilities:**
- AI model selection and routing
- Multi-provider API orchestration (OpenAI, Claude, Gemini, Grok, Doubao, AICSO)
- Content generation (text, images, videos)
- Hotspot analysis and trend detection
- AI-powered content optimization

**Configuration:**
```yaml
# AI Provider APIs
OPENAI_API_KEY/BASE_URL
ANTHROPIC_API_KEY/BASE_URL
GEMINI_KEY_PAIRS: JSON array of Google Cloud credentials
VOLCENGINE_API_KEY/ACCESS_KEY_ID/SECRET_ACCESS_KEY
GROK_API_KEY
AICSO_API_KEY/BASE_URL
AI_PROXY_URL: Optional proxy for AI API access

# Inter-service communication
SERVER_URL: http://aitoearn-server:3002
```

**AI Model Configuration:**
AI model definitions (available models, pricing, capabilities) are hardcoded in the config file at `config/aitoearn-ai.config.js`, which is mounted as a read-only volume.

Sources: [docker-compose.yml:81-134](), [DOCKER_DEPLOYMENT_EN.md:206-249]()

## Data Persistence Layer

AiToEarn implements a three-tier data storage strategy, with each tier optimized for different access patterns and data types.

### Storage Architecture

```mermaid
graph TD
    subgraph "Application Services"
        Server["aitoearn-server"]
        AI["aitoearn-ai"]
    end
    
    subgraph "Data Storage Tier"
        MongoDB["MongoDB<br/>Document Store"]
        Redis["Redis<br/>Cache & Queue"]
        RustFS["RustFS<br/>Object Storage"]
    end
    
    subgraph "Data Categories"
        UserData["User Data<br/>OAuth Tokens<br/>Metadata"]
        CachedData["Sessions<br/>Rate Limits<br/>Job Queues"]
        MediaFiles["Images<br/>Videos<br/>Documents"]
    end
    
    Server --> MongoDB
    Server --> Redis
    Server --> RustFS
    AI --> MongoDB
    AI --> Redis
    AI --> RustFS
    
    MongoDB -.-> UserData
    Redis -.-> CachedData
    RustFS -.-> MediaFiles
```

Sources: [docker-compose.yml:2-64]()

### MongoDB (Document Database)

**Container:** `aitoearn-mongodb` (mongo:latest)
**Port:** 27017 (exposed for development access)

MongoDB stores structured application data including user accounts, OAuth tokens, content metadata, publication records, and analytics data.

**Configuration:**
- Root username: `admin` (configurable via `MONGO_INITDB_ROOT_USERNAME`)
- Root password: `password` (must be changed via `MONGO_INITDB_ROOT_PASSWORD`)
- Database name: `aitoearn` (primary) and statistics database (defaults to same instance)

**Persistence:**
- `mongodb-data` volume: Database files at `/data/db`
- `mongodb-config` volume: Configuration at `/data/configdb`

**Health Check:** `mongosh` ping command every 10s

Sources: [docker-compose.yml:2-21](), [docker-compose.yml:100-103](), [docker-compose.yml:278-281]()

### Redis (Cache and Job Queue)

**Container:** `aitoearn-redis` (redis:latest)
**Port:** 6379 (exposed for development access)

Redis provides high-performance caching for session data, rate limiting, and job queue management for scheduled tasks (e.g., calendar-based content publishing).

**Configuration:**
- Password protection: `--requirepass password` (must be changed in docker-compose.yml)
- Persistence: RDB snapshots to volume

**Persistence:**
- `redis-data` volume: Snapshots at `/data`

**Health Check:** `redis-cli ping` every 10s

Sources: [docker-compose.yml:23-39](), [docker-compose.yml:105-107](), [docker-compose.yml:283]()

### RustFS (Object Storage)

**Container:** `aitoearn-rustfs` (rustfs/rustfs:latest)
**Ports:** 9000 (S3 API), 9001 (web console)

RustFS provides S3-compatible object storage for media assets (images, videos, documents). It runs locally within Docker Compose for development and testing, but can be replaced with AWS S3, Aliyun OSS, or other S3-compatible services in production.

**Configuration:**
- Access Key: `rustfsadmin` (via `RUSTFS_ACCESS_KEY`)
- Secret Key: `rustfsadmin` (via `RUSTFS_SECRET_KEY`)
- Bucket: `aitoearn` (auto-created by `rustfs-init` container)
- Public read access enabled for the bucket

**Management Console:** http://localhost:9001
- Login with access key and secret key

**Persistence:**
- `rustfs-data` volume: Object storage at `/data`

**Health Check:** HTTP GET to `/health` endpoint every 10s

Sources: [docker-compose.yml:41-78](), [docker-compose.yml:285](), [DOCKER_DEPLOYMENT_EN.md:174-203]()

#### Switching to External Storage

For production deployments, update the `assets` configuration in both `config/aitoearn-ai.config.js` and `config/aitoearn-server.config.js` to point to AWS S3, Aliyun OSS, or another S3-compatible service.

Sources: [DOCKER_DEPLOYMENT_EN.md:188-203]()

## Request Routing and API Gateway

### Nginx Reverse Proxy

**Container:** `aitoearn-nginx` (nginx:alpine)
**Port:** 8080 (public-facing)

Nginx serves as the unified gateway for all HTTP traffic, routing requests to the appropriate backend service and serving the Next.js frontend.

#### Routing Configuration

```mermaid
graph LR
    subgraph "External Requests"
        Client["HTTP Client<br/>:8080"]
    end
    
    subgraph "nginx Routes"
        Root["/"]
        API["/api/*"]
        Health["/_nhealth"]
    end
    
    subgraph "Backend Services"
        Web["aitoearn-web:3000"]
        Server["aitoearn-server:3002"]
        NginxHealth["nginx health endpoint"]
    end
    
    Client --> Root
    Client --> API
    Client --> Health
    
    Root --> Web
    API --> Server
    Health --> NginxHealth
```

Sources: [docker-compose.yml:248-270](), [README.md:174-180]()

**Configuration File:** Nginx configuration is mounted from `nginx/nginx.conf` as a read-only volume. The file defines:

- **Route `/`**: Proxies to `aitoearn-web:3000` (Next.js frontend)
- **Route `/api/`**: Proxies to `aitoearn-server:3002` (NestJS backend API)
- **Route `/_nhealth`**: Internal health check endpoint for nginx monitoring

Sources: [docker-compose.yml:261-262]()

### Inter-Service Communication

Backend services communicate directly using internal DNS hostnames on the Docker bridge network, bypassing nginx for improved performance.

#### Service-to-Service API Calls

```mermaid
sequenceDiagram
    participant Web as aitoearn-web
    participant Server as aitoearn-server:3002
    participant AI as aitoearn-ai:3010
    
    Note over Web,Server: Public API Request (via nginx)
    Web->>Server: POST /api/content/generate
    
    Note over Server,AI: Internal Service Communication
    Server->>AI: POST http://aitoearn-ai:3010/ai/generate
    AI->>Server: AI-generated content
    
    Server->>Web: Generated content response
```

**Authentication:**
- Inter-service requests use `INTERNAL_TOKEN` header for authentication
- JWT tokens validate user requests at the API gateway (aitoearn-server)
- Internal services trust requests authenticated by aitoearn-server

Sources: [docker-compose.yml:109-110](), [docker-compose.yml:112](), [docker-compose.yml:171](), [docker-compose.yml:174]()

## Technical Stack

AiToEarn is built with a modern technology stack as defined in its package.json:

| Layer | Technologies |
|-------|--------------|
| **Frontend** | React, Ant Design, React Router, Zustand, SCSS |
| **Backend** | Electron, Node.js, TypeORM, SQLite |
| **Media Processing** | FFmpeg, Sharp |
| **Build Tools** | Vite, TypeScript, Electron Builder |
| **External Integrations** | Axios, WebView |

Sources: [package.json:32-83]()

## Cross-Platform Support

The application includes platform-specific adjustments for Windows and macOS, particularly in the UI layer:

```mermaid
flowchart TD
    subgraph "Platform-Specific Adaptations"
        Navigation["Navigation Component"]
        WindowControls["Window Control Buttons"]
        TitleBar["Title Bar Styling"]
    end
    
    OS["Operating System Detection"] --> Navigation
    OS --> WindowControls
    OS --> TitleBar
    
    Navigation --> Win32["Windows Styling"]
    Navigation --> Darwin["macOS Styling"]
    WindowControls --> PlatformUI["Platform-specific UI"]
```

Sources: [src/layout/Navigation/index.tsx](), [src/layout/Navigation/navigation.module.scss:69-81](), [src/components/WindowControlButtons/windowControlButtons.module.scss]()

The system adapts the navigation bar appearance and window controls based on the platform, ensuring a native-like experience on each operating system.

## Conclusion

AiToEarn's architecture showcases a well-structured Electron application with clear separation of concerns. The use of the Adapter pattern for platform integrations, component-based UI design, and robust IPC communication creates a flexible and maintainable system capable of handling complex social media management tasks across multiple platforms.

The application's structured architecture, with modular components and clear subsystem boundaries, enables efficient development and maintenance while providing a robust platform for social media management across multiple Chinese platforms.

Sources: [electron/main/index.ts](), [src/router/index.tsx](), [package.json]()

---

# Page: Docker Compose Service Architecture

# Docker Compose Service Architecture

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



This document details the Docker Compose orchestration configuration that defines AiToEarn's containerized deployment architecture. It covers each service defined in [docker-compose.yml](), their roles, port mappings, network communication patterns, health check mechanisms, and dependency relationships.

For information about the data storage strategy (MongoDB, Redis, RustFS volumes), see [Data Persistence Layer](#2.2). For details on the frontend application structure, see [Frontend Architecture](#2.3). For deployment procedures and environment variable configuration, see [Docker Deployment Guide](#7.1).

---

## Service Topology

The Docker Compose stack consists of seven primary services plus one initialization container, all communicating over a dedicated bridge network called `aitoearn-network`.

**Service Dependency and Communication Flow**

```mermaid
graph TB
    Client["External Client<br/>(Browser)"]
    
    subgraph "Docker Compose Stack"
        Nginx["nginx<br/>container: aitoearn-nginx<br/>port: 8080→80"]
        Web["aitoearn-web<br/>container: aitoearn-web<br/>port: 3000 (internal)"]
        Server["aitoearn-server<br/>container: aitoearn-server<br/>port: 3002 (internal)"]
        AI["aitoearn-ai<br/>container: aitoearn-ai<br/>port: 3010 (internal)"]
        MongoDB["mongodb<br/>container: aitoearn-mongodb<br/>port: 27017"]
        Redis["redis<br/>container: aitoearn-redis<br/>port: 6379"]
        RustFS["rustfs<br/>container: aitoearn-rustfs<br/>ports: 9000, 9001"]
        RustFSInit["rustfs-init<br/>container: aitoearn-rustfs-init<br/>(one-time init)"]
    end
    
    Client -->|"HTTP :8080"| Nginx
    Nginx -->|"proxy to :3000"| Web
    Nginx -->|"proxy /api/* to :3002"| Server
    Web -.->|"SSR calls"| Server
    Server -->|"HTTP :3010"| AI
    Server -->|":27017"| MongoDB
    Server -->|":6379"| Redis
    Server -->|"S3 API :9000"| RustFS
    AI -->|":27017"| MongoDB
    AI -->|":6379"| Redis
    AI -->|"S3 API :9000"| RustFS
    RustFSInit -.->|"mc commands :9000"| RustFS
    
    Client -.->|"Console :9001"| RustFS
```

Sources: [docker-compose.yml:1-286]()

---

## Network Configuration

All services communicate over a single Docker bridge network named `aitoearn-network`, defined at [docker-compose.yml:272-275](). This provides:

- Internal DNS resolution using service names (e.g., `mongodb`, `aitoearn-server`)
- Network isolation from the host and other Docker networks
- Simplified inter-service communication without exposing internal ports

The `rustfs` service has a network alias `rustfs.local` defined at [docker-compose.yml:55-57](), used by the initialization container and application services for S3 endpoint configuration.

**Exposed Ports to Host**

| Host Port | Service | Container Port | Purpose |
|-----------|---------|----------------|---------|
| 8080 | nginx | 80 | Main application entry point |
| 27017 | mongodb | 27017 | MongoDB database (optional external access) |
| 6379 | redis | 6379 | Redis cache (optional external access) |
| 9000 | rustfs | 9000 | RustFS S3 API |
| 9001 | rustfs | 9001 | RustFS web console |

Internal-only services (`aitoearn-web`, `aitoearn-server`, `aitoearn-ai`) do not expose ports to the host and are accessed only through nginx.

Sources: [docker-compose.yml:10](), [docker-compose.yml:29](), [docker-compose.yml:49-51](), [docker-compose.yml:260]()

---

## Core Services

### nginx

**Container**: `aitoearn-nginx`  
**Image**: `nginx:alpine`  
**Port Mapping**: `8080:80`

The nginx service acts as the reverse proxy and unified entry point for all HTTP traffic. Configuration is mounted from [nginx/nginx.conf]() as a read-only volume at [docker-compose.yml:262]().

**Routing Rules**:
- `/` → `http://aitoearn-web:3000` (Next.js frontend)
- `/api/*` → `http://aitoearn-server:3002` (Backend API)
- `/_nhealth` → nginx health check endpoint

**Dependencies**: Requires `aitoearn-web`, `aitoearn-server`, and `aitoearn-ai` to be running (specified at [docker-compose.yml:252-258]()).

**Health Check**: Configured at [docker-compose.yml:265-270]() using `wget` to check `http://localhost/_nhealth` every 10 seconds.

Sources: [docker-compose.yml:248-270]()

---

### aitoearn-web

**Container**: `aitoearn-web`  
**Image**: `aitoearn/aitoearn-web:latest`  
**Internal Port**: 3000

The Next.js 14 frontend application serving the web user interface. This service runs in production mode and communicates with the backend API through nginx's reverse proxy.

**Key Environment Variables**:
- `NODE_ENV=production` - Enables production optimizations
- `NEXT_TELEMETRY_DISABLED=1` - Disables Next.js telemetry
- `NEXT_PUBLIC_API_URL=http://localhost:8080/api` - Public-facing API endpoint (browser-side)

Configured at [docker-compose.yml:234-247]().

**Dependency**: `aitoearn-server` must reach healthy status before this service starts ([docker-compose.yml:238-240]()).

**No Health Check**: This service relies on nginx's ability to proxy requests; nginx handles retries if the web service is temporarily unavailable.

Sources: [docker-compose.yml:234-247]()

---

### aitoearn-server

**Container**: `aitoearn-server`  
**Image**: `aitoearn/aitoearn-server:latest`  
**Internal Port**: 3002

The NestJS backend API service handling all business logic, OAuth flows, platform integrations, and user management.

**Key Environment Variables**:
- `APP_NAME=aitoearn-server`
- `APP_DOMAIN=localhost` - Used to construct OAuth callback URLs
- `MONGODB_HOST=mongodb`, `MONGODB_PORT=27017` - Primary database connection
- `STATISTICS_DB_HOST=mongodb`, `STATISTICS_DB_PORT=27017` - Analytics database (can be separate instance)
- `REDIS_HOST=redis`, `REDIS_PORT=6379` - Cache and job queue
- `AI_URL=http://aitoearn-ai:3010` - Internal URL to AI service
- `JWT_SECRET`, `INTERNAL_TOKEN` - Must match `aitoearn-ai` configuration

Configured at [docker-compose.yml:136-232]().

**Configuration Volume**: [config/aitoearn-server.config.js]() mounted read-only at `/app/config.js` ([docker-compose.yml:148]()).

**Dependencies**: Waits for `mongodb`, `redis`, and `aitoearn-ai` to reach healthy status ([docker-compose.yml:140-146]()).

**Health Check**: Node.js HTTP check at `http://localhost:3002/health` every 30 seconds ([docker-compose.yml:227-232]()).

**OAuth Callback URL Pattern**: `https://{APP_DOMAIN}/api/plat/{platform}/auth/back`

Sources: [docker-compose.yml:136-232]()

---

### aitoearn-ai

**Container**: `aitoearn-ai`  
**Image**: `aitoearn/aitoearn-ai:latest`  
**Internal Port**: 3010

The NestJS AI service responsible for orchestrating multiple AI providers (OpenAI, Claude, Gemini, Grok, Doubao, AICSO) and managing AI-powered content generation.

**Key Environment Variables**:
- `APP_NAME=aitoearn-ai`
- `MONGODB_HOST=mongodb`, `MONGODB_PORT=27017`
- `REDIS_HOST=redis`, `REDIS_PORT=6379`
- `SERVER_URL=http://aitoearn-server:3002` - Internal URL to backend service
- `JWT_SECRET`, `INTERNAL_TOKEN` - Must match `aitoearn-server` configuration
- AI Provider Keys: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `VOLCENGINE_*`, `GROK_API_KEY`, `AICSO_API_KEY`, `GEMINI_KEY_PAIRS`

Configured at [docker-compose.yml:81-134]().

**Configuration Volumes**:
- [config/aitoearn-ai.config.js]() → `/app/config.js` (read-only)
- [config/gcs-placeholder.json]() → `/app/config/gcs-placeholder.json` (read-only)

Both mounted at [docker-compose.yml:91-92]().

**Dependencies**: Waits for `mongodb` and `redis` to reach healthy status ([docker-compose.yml:85-89]()).

**Health Check**: Node.js HTTP check at `http://localhost:3010/health` every 30 seconds ([docker-compose.yml:129-134]()).

Sources: [docker-compose.yml:81-134]()

---

## Data Services

### mongodb

**Container**: `aitoearn-mongodb`  
**Image**: `mongo:latest`  
**Port Mapping**: `27017:27017`

The primary MongoDB database storing user data, content, OAuth tokens, and application state.

**Authentication**:
- `MONGO_INITDB_ROOT_USERNAME=admin`
- `MONGO_INITDB_ROOT_PASSWORD=password` (must be changed in production)

Configured at [docker-compose.yml:2-21]().

**Volumes**:
- `mongodb-data:/data/db` - Database files
- `mongodb-config:/data/configdb` - MongoDB configuration

Both defined as named Docker volumes at [docker-compose.yml:278-281]().

**Health Check**: Runs `mongosh` ping command every 10 seconds with a 40-second initial delay ([docker-compose.yml:16-21]()).

**Restart Policy**: `unless-stopped` ensures automatic restart except when explicitly stopped ([docker-compose.yml:5]()).

Sources: [docker-compose.yml:2-21](), [docker-compose.yml:278-281]()

---

### redis

**Container**: `aitoearn-redis`  
**Image**: `redis:latest`  
**Port Mapping**: `6379:6379`

The Redis service providing:
- Session storage
- Job queue management for scheduled publishing
- Rate limiting data
- Application caching layer

**Authentication**: Password protection enabled via command flag at [docker-compose.yml:27]():
```yaml
command: redis-server --requirepass password
```

Configured at [docker-compose.yml:23-39]().

**Volume**: `redis-data:/data` for persistence, defined at [docker-compose.yml:283]().

**Health Check**: Uses `redis-cli` to increment a ping counter every 10 seconds ([docker-compose.yml:34-39]()).

**Restart Policy**: `unless-stopped`

Sources: [docker-compose.yml:23-39](), [docker-compose.yml:283]()

---

### rustfs

**Container**: `aitoearn-rustfs`  
**Image**: `rustfs/rustfs:latest`  
**Port Mapping**: `9000:9000` (S3 API), `9001:9001` (Web Console)  
**Hostname**: `rustfs.local`

RustFS provides S3-compatible object storage for images, videos, and documents. This is a lightweight alternative to AWS S3 or MinIO, suitable for development and small-scale deployments.

**Credentials**:
- `RUSTFS_ACCESS_KEY=rustfsadmin`
- `RUSTFS_SECRET_KEY=rustfsadmin`

Configured at [docker-compose.yml:41-63]().

**Network Configuration**: Aliased as `rustfs.local` in the `aitoearn-network` ([docker-compose.yml:55-57]()), allowing application services to connect using consistent DNS name.

**Volume**: `rustfs-data:/data` for object storage, defined at [docker-compose.yml:284-285]().

**Health Check**: HTTP GET to `http://localhost:9000/health` every 10 seconds ([docker-compose.yml:58-63]()).

**Web Console**: Accessible at `http://localhost:9001` for bucket management and file browsing.

Sources: [docker-compose.yml:41-63](), [docker-compose.yml:284-285]()

---

### rustfs-init

**Container**: `aitoearn-rustfs-init`  
**Image**: `minio/mc:latest` (MinIO client)

A one-time initialization container that creates the required `aitoearn` bucket and sets public read permissions. This container runs to completion and then exits.

**Initialization Script** (defined at [docker-compose.yml:73-79]()):
```bash
mc alias set rustfs http://rustfs.local:9000 rustfsadmin rustfsadmin;
mc mb rustfs/aitoearn --ignore-existing;
mc anonymous set download rustfs/aitoearn;
exit 0;
```

**Operations**:
1. Configure MinIO client alias pointing to `rustfs.local:9000`
2. Create bucket `aitoearn` (skip if exists)
3. Set download policy to allow public reads
4. Exit successfully

**Dependency**: Waits for `rustfs` to reach healthy status ([docker-compose.yml:68-70]()).

Sources: [docker-compose.yml:65-79]()

---

## Service Startup Sequence

The dependency chain ensures services start in the correct order with proper health verification:

```mermaid
graph TD
    Start["docker compose up"]
    
    MongoDB["mongodb starts<br/>wait for healthy"]
    Redis["redis starts<br/>wait for healthy"]
    RustFS["rustfs starts<br/>wait for healthy"]
    
    RustFSInit["rustfs-init runs<br/>creates bucket"]
    AI["aitoearn-ai starts<br/>wait for healthy"]
    
    Server["aitoearn-server starts<br/>wait for healthy"]
    Web["aitoearn-web starts"]
    
    Nginx["nginx starts"]
    Ready["Stack Ready"]
    
    Start --> MongoDB
    Start --> Redis
    Start --> RustFS
    
    RustFS --> RustFSInit
    MongoDB --> AI
    Redis --> AI
    
    MongoDB --> Server
    Redis --> Server
    AI --> Server
    
    Server --> Web
    
    Web --> Nginx
    Server --> Nginx
    AI --> Nginx
    
    Nginx --> Ready
```

**Health Check Conditions**:

| Service | Condition Type | Check Details |
|---------|----------------|---------------|
| mongodb | `service_healthy` | mongosh ping every 10s, 5 retries, 40s start period |
| redis | `service_healthy` | redis-cli incr every 10s, 5 retries, 30s start period |
| rustfs | `service_healthy` | curl health endpoint every 10s, 5 retries, 30s start period |
| aitoearn-ai | `service_healthy` | Node.js HTTP GET /health every 30s, 3 retries, 60s start period |
| aitoearn-server | `service_healthy` | Node.js HTTP GET /health every 30s, 3 retries, 60s start period |
| aitoearn-web | `service_started` | No health check, just wait for container start |

Configured at:
- MongoDB: [docker-compose.yml:16-21]()
- Redis: [docker-compose.yml:34-39]()
- RustFS: [docker-compose.yml:58-63]()
- AI: [docker-compose.yml:129-134]()
- Server: [docker-compose.yml:227-232]()
- Nginx: [docker-compose.yml:265-270]()

Sources: [docker-compose.yml:68-70](), [docker-compose.yml:85-89](), [docker-compose.yml:140-146](), [docker-compose.yml:238-240](), [docker-compose.yml:252-258]()

---

## Volume Management

Four named volumes provide data persistence across container restarts:

**Volume Definitions** ([docker-compose.yml:277-285]()):

```mermaid
graph LR
    subgraph "Docker Volumes (local driver)"
        V1["mongodb-data"]
        V2["mongodb-config"]
        V3["redis-data"]
        V4["rustfs-data"]
    end
    
    subgraph "Container Mount Points"
        M1["mongodb:/data/db"]
        M2["mongodb:/data/configdb"]
        M3["redis:/data"]
        M4["rustfs:/data"]
    end
    
    V1 -.-> M1
    V2 -.-> M2
    V3 -.-> M3
    V4 -.-> M4
```

| Volume Name | Mount Point | Service | Contents |
|-------------|-------------|---------|----------|
| `mongodb-data` | `/data/db` | mongodb | Database collections and indexes |
| `mongodb-config` | `/data/configdb` | mongodb | MongoDB configuration files |
| `redis-data` | `/data` | redis | RDB snapshots, AOF logs |
| `rustfs-data` | `/data` | rustfs | Object storage files |

All volumes use the `local` driver, storing data on the Docker host filesystem. Volume locations can be inspected with:
```bash
docker volume inspect aitoearn_mongodb-data
```

**Configuration File Volumes** (read-only bind mounts):

| Host Path | Container Path | Service |
|-----------|----------------|---------|
| `./config/aitoearn-ai.config.js` | `/app/config.js` | aitoearn-ai |
| `./config/aitoearn-server.config.js` | `/app/config.js` | aitoearn-server |
| `./config/gcs-placeholder.json` | `/app/config/gcs-placeholder.json` | aitoearn-ai |
| `./nginx/nginx.conf` | `/etc/nginx/nginx.conf` | nginx |

All configuration files are mounted with `:ro` flag for read-only access ([docker-compose.yml:91-92](), [docker-compose.yml:148](), [docker-compose.yml:262]()).

Sources: [docker-compose.yml:12-13](), [docker-compose.yml:31](), [docker-compose.yml:53](), [docker-compose.yml:277-285]()

---

## Service Communication Patterns

### External → nginx → Services

Browser clients access the system through port 8080, which nginx routes based on request path:

```mermaid
sequenceDiagram
    participant Browser
    participant nginx
    participant Web as aitoearn-web:3000
    participant Server as aitoearn-server:3002
    
    Browser->>nginx: GET / HTTP/1.1
    nginx->>Web: proxy_pass http://aitoearn-web:3000
    Web->>nginx: HTML Response
    nginx->>Browser: HTTP/1.1 200 OK
    
    Browser->>nginx: POST /api/users/login
    nginx->>Server: proxy_pass http://aitoearn-server:3002
    Server->>nginx: JSON Response
    nginx->>Browser: HTTP/1.1 200 OK
```

### Server ↔ AI Communication

The backend makes HTTP calls to the AI service for content generation:

```mermaid
sequenceDiagram
    participant Server as aitoearn-server
    participant AI as aitoearn-ai:3010
    
    Server->>AI: POST /ai/generate
    Note over Server,AI: Uses INTERNAL_TOKEN for auth
    AI->>Server: Generated content
```

Server uses `AI_URL=http://aitoearn-ai:3010` environment variable ([docker-compose.yml:171]()).  
AI uses `SERVER_URL=http://aitoearn-server:3002` for callbacks ([docker-compose.yml:112]()).

### Service → Database/Cache Access

Both `aitoearn-server` and `aitoearn-ai` connect to MongoDB and Redis using container DNS names:

```mermaid
graph LR
    Server["aitoearn-server"]
    AI["aitoearn-ai"]
    
    MongoDB["mongodb:27017"]
    Redis["redis:6379"]
    RustFS["rustfs.local:9000"]
    
    Server -->|"MongoDB URI"| MongoDB
    Server -->|"Redis connection"| Redis
    Server -->|"S3 API"| RustFS
    
    AI -->|"MongoDB URI"| MongoDB
    AI -->|"Redis connection"| Redis
    AI -->|"S3 API"| RustFS
```

**Connection Strings**:
- MongoDB: `mongodb://admin:password@mongodb:27017/aitoearn`
- Redis: `redis://:password@redis:6379`
- RustFS: `http://rustfs.local:9000` with S3 SDK

Sources: [docker-compose.yml:100-107](), [docker-compose.yml:157-169](), [docker-compose.yml:171]()

---

## Production Considerations

### Security Hardening

**Required Changes in [docker-compose.yml]()**:

1. **Database Passwords** - Change default `password` values:
   - `MONGO_INITDB_ROOT_PASSWORD` ([docker-compose.yml:8]())
   - `MONGODB_PASSWORD` in both services ([docker-compose.yml:103](), [docker-compose.yml:160]())
   - `REDIS_PASSWORD` ([docker-compose.yml:27](), [docker-compose.yml:107](), [docker-compose.yml:169]())

2. **Authentication Secrets** - Generate random tokens:
   - `JWT_SECRET` ([docker-compose.yml:109](), [docker-compose.yml:173]())
   - `INTERNAL_TOKEN` ([docker-compose.yml:110](), [docker-compose.yml:174]())

3. **RustFS Credentials** - Update in three locations:
   - `RUSTFS_ACCESS_KEY/SECRET_KEY` ([docker-compose.yml:47-48]())
   - `rustfs-init` entrypoint ([docker-compose.yml:75]())
   - Config files: [config/aitoearn-ai.config.js](), [config/aitoearn-server.config.js]()

4. **Domain Configuration**:
   - `APP_DOMAIN` ([docker-compose.yml:155]()) - Must match production domain for OAuth
   - `NEXT_PUBLIC_API_URL` ([docker-compose.yml:246]()) - Public API endpoint

### Port Exposure

For production, consider removing port mappings for direct database access:

```yaml
# Remove or comment out these lines:
# ports:
#   - "27017:27017"  # MongoDB
#   - "6379:6379"    # Redis
```

Only expose nginx (8080) and optionally RustFS console (9001). Access databases through Docker exec or internal tooling.

### Scaling Limitations

Current limitations of the Docker Compose setup:

- **Single-instance services**: No horizontal scaling for stateful services
- **Volume locality**: Named volumes are tied to single Docker host
- **No load balancing**: Nginx proxies to single backend instances

For multi-node deployments, consider:
- Migrating to Docker Swarm mode (see deployment guides)
- Using Kubernetes with provided manifests
- External MongoDB/Redis clusters with replica sets
- Object storage migration to AWS S3 or managed MinIO

### Resource Constraints

The stack requires approximately:
- **Memory**: 4GB+ (MongoDB ~1GB, Redis ~500MB, Node services ~2GB combined)
- **Disk**: 20GB+ for volumes and images
- **CPU**: 2+ cores recommended for concurrent AI processing

Resource limits can be added to service definitions:
```yaml
services:
  aitoearn-server:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1024M
```

Sources: [DOCKER_DEPLOYMENT_EN.md:38-50](), [DOCKER_DEPLOYMENT_CN.md:38-50]()

---

## Troubleshooting

### Service Health Checks

Monitor service health status:
```bash
docker compose ps
```

Check specific service logs:
```bash
docker compose logs -f aitoearn-server
docker compose logs -f aitoearn-ai
```

### Common Issues

**MongoDB Connection Failures**:
- Verify health check passing: `docker compose ps mongodb`
- Check password consistency across services
- Ensure 40-second start period elapsed ([docker-compose.yml:21]())

**Redis Authentication Errors**:
- Confirm `REDIS_PASSWORD` matches command flag ([docker-compose.yml:27]())
- Check both services use same password ([docker-compose.yml:107](), [docker-compose.yml:169]())

**AI Service Unavailable**:
- Verify `SERVER_URL` and `AI_URL` use correct container names
- Check health endpoint: `docker exec aitoearn-ai curl http://localhost:3010/health`
- Ensure `INTERNAL_TOKEN` matches between services

**RustFS Bucket Not Created**:
- Check `rustfs-init` container logs: `docker compose logs rustfs-init`
- Verify RustFS health before init runs ([docker-compose.yml:68-70]())
- Manually create bucket via console at http://localhost:9001

### Network Debugging

Inspect the Docker network:
```bash
docker network inspect aitoearn-network
```

Test inter-service connectivity:
```bash
docker exec aitoearn-server curl http://aitoearn-ai:3010/health
docker exec aitoearn-ai curl http://aitoearn-server:3002/health
```

Sources: [docker-compose.yml:16-21](), [docker-compose.yml:129-134](), [docker-compose.yml:227-232]()

---

# Page: Data Persistence Layer

# Data Persistence Layer

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



## Purpose and Scope

This document explains the data persistence layer of AiToEarn, which consists of three storage systems working together to provide document storage, caching/queuing, and asset storage. Each system is deployed as a containerized service with dedicated Docker volumes for data persistence. For deployment procedures, see [Docker Deployment Guide](#7.1). For environment configuration details, see [Environment Configuration](#7.2).

**Sources:** [docker-compose.yml:1-286](), [DOCKER_DEPLOYMENT_EN.md:1-326](), [DOCKER_DEPLOYMENT_CN.md:1-326]()

---

## Three-Tier Storage Architecture

AiToEarn implements a three-tier data persistence strategy where each storage layer serves a specific purpose:

### Storage Layer Overview

```mermaid
graph TB
    subgraph Applications["Application Services"]
        AiService["aitoearn-ai<br/>:3010"]
        ServerService["aitoearn-server<br/>:3002"]
    end
    
    subgraph Storage["Data Persistence Layer"]
        MongoDB["MongoDB<br/>aitoearn-mongodb:27017<br/>Document Database"]
        Redis["Redis<br/>aitoearn-redis:6379<br/>Cache & Queue"]
        RustFS["RustFS<br/>aitoearn-rustfs:9000/9001<br/>Object Storage"]
    end
    
    subgraph Volumes["Docker Volumes"]
        MongoData["mongodb-data<br/>/data/db"]
        MongoConfig["mongodb-config<br/>/data/configdb"]
        RedisData["redis-data<br/>/data"]
        RustFSData["rustfs-data<br/>/data"]
    end
    
    AiService -->|"Read/Write Documents"| MongoDB
    AiService -->|"Cache/Jobs"| Redis
    AiService -->|"Upload/Download Assets"| RustFS
    
    ServerService -->|"Read/Write Documents"| MongoDB
    ServerService -->|"Cache/Jobs"| Redis
    ServerService -->|"Upload/Download Assets"| RustFS
    
    MongoDB -.->|"Persist"| MongoData
    MongoDB -.->|"Config"| MongoConfig
    Redis -.->|"Persist"| RedisData
    RustFS -.->|"Persist"| RustFSData
```

**Sources:** [docker-compose.yml:2-64](), [DOCKER_DEPLOYMENT_EN.md:6-36]()

### Storage Type Comparison

| Storage System | Purpose | Data Type | Access Pattern | Persistence Volume |
|----------------|---------|-----------|----------------|-------------------|
| **MongoDB** | Primary data store | Structured documents (users, content, OAuth tokens) | Indexed queries, transactions | `mongodb-data`, `mongodb-config` |
| **Redis** | Fast cache and job queue | Key-value pairs, sessions, rate limits | In-memory access, pub/sub | `redis-data` |
| **RustFS** | Asset storage | Binary files (images, videos, documents) | HTTP S3 API | `rustfs-data` |

**Sources:** [docker-compose.yml:2-64](), [DOCKER_DEPLOYMENT_EN.md:163-203](), [DOCKER_DEPLOYMENT_CN.md:163-203]()

---

## MongoDB Document Storage

### Service Configuration

MongoDB serves as the primary document database for AiToEarn, storing user accounts, content drafts, OAuth credentials, analytics data, and application state.

```mermaid
graph LR
    subgraph MongoDB["aitoearn-mongodb Container"]
        MongoProcess["mongod process<br/>Port: 27017"]
    end
    
    subgraph Volumes["Host Volumes"]
        DataVol["mongodb-data<br/>Driver: local"]
        ConfigVol["mongodb-config<br/>Driver: local"]
    end
    
    subgraph Clients["Application Clients"]
        AiService["aitoearn-ai<br/>MONGODB_HOST=mongodb"]
        ServerService["aitoearn-server<br/>MONGODB_HOST=mongodb<br/>STATISTICS_DB_HOST=mongodb"]
    end
    
    MongoProcess -->|"Data files"| DataVol
    MongoProcess -->|"Config files"| ConfigVol
    AiService -->|"Connection:<br/>admin/password"| MongoProcess
    ServerService -->|"Connection:<br/>admin/password"| MongoProcess
```

**Container Definition:**

[docker-compose.yml:2-21]()

```yaml
mongodb:
  image: mongo:latest
  container_name: aitoearn-mongodb
  restart: unless-stopped
  environment:
    MONGO_INITDB_ROOT_USERNAME: admin
    MONGO_INITDB_ROOT_PASSWORD: password
  ports:
    - "27017:27017"
  volumes:
    - mongodb-data:/data/db
    - mongodb-config:/data/configdb
```

**Sources:** [docker-compose.yml:2-21]()

### Volume Mounting Details

| Volume Name | Mount Point | Purpose | Persistence |
|-------------|-------------|---------|-------------|
| `mongodb-data` | `/data/db` | Database files, collections, indexes | Survives container recreation |
| `mongodb-config` | `/data/configdb` | MongoDB configuration data | Survives container recreation |

**Sources:** [docker-compose.yml:12-13](), [docker-compose.yml:278-281]()

### Database Structure

MongoDB hosts two logical databases accessed by different services:

| Database | Used By | Purpose | Connection Environment Variables |
|----------|---------|---------|----------------------------------|
| `aitoearn` (primary) | aitoearn-ai, aitoearn-server | User data, content, OAuth tokens | `MONGODB_HOST`, `MONGODB_PORT`, `MONGODB_USERNAME`, `MONGODB_PASSWORD` |
| Statistics DB | aitoearn-server | Analytics and performance metrics | `STATISTICS_DB_HOST`, `STATISTICS_DB_PORT`, `STATISTICS_DB_USERNAME`, `STATISTICS_DB_PASSWORD` |

By default, both databases use the same MongoDB instance, but can be configured separately in production.

**Sources:** [docker-compose.yml:100-103](), [docker-compose.yml:157-165](), [DOCKER_DEPLOYMENT_EN.md:163-171]()

### Healthcheck Mechanism

MongoDB includes a built-in healthcheck that runs every 10 seconds:

[docker-compose.yml:16-21]()

```yaml
healthcheck:
  test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 40s
```

The healthcheck uses `mongosh` (MongoDB shell) to execute a ping command. Services depending on MongoDB wait for this check to pass before starting.

**Sources:** [docker-compose.yml:16-21]()

---

## Redis Cache and Queue

### Service Configuration

Redis provides in-memory data storage for caching, session management, rate limiting, and job queuing via BullMQ.

```mermaid
graph TB
    subgraph Redis["aitoearn-redis Container"]
        RedisServer["redis-server<br/>--requirepass password<br/>Port: 6379"]
    end
    
    subgraph Volume["Host Volume"]
        RedisVol["redis-data<br/>Driver: local<br/>Mount: /data"]
    end
    
    subgraph Clients["Application Clients"]
        AiClient["aitoearn-ai<br/>REDIS_HOST=redis<br/>REDIS_PASSWORD=password"]
        ServerClient["aitoearn-server<br/>REDIS_HOST=redis<br/>REDIS_PASSWORD=password"]
    end
    
    subgraph UseCases["Redis Usage Patterns"]
        Cache["Cache Layer<br/>Session data<br/>API responses"]
        Queue["Job Queue<br/>BullMQ<br/>Scheduled tasks"]
        RateLimit["Rate Limiting<br/>API throttling"]
        PubSub["Pub/Sub<br/>Real-time events"]
    end
    
    RedisServer -->|"Persistence (AOF/RDB)"| RedisVol
    AiClient -->|"Read/Write"| RedisServer
    ServerClient -->|"Read/Write"| RedisServer
    
    RedisServer -.-> Cache
    RedisServer -.-> Queue
    RedisServer -.-> RateLimit
    RedisServer -.-> PubSub
```

**Container Definition:**

[docker-compose.yml:23-39]()

```yaml
redis:
  image: redis:latest
  container_name: aitoearn-redis
  restart: unless-stopped
  command: redis-server --requirepass password
  ports:
    - "6379:6379"
  volumes:
    - redis-data:/data
```

**Sources:** [docker-compose.yml:23-39]()

### Volume Configuration

| Volume Name | Mount Point | Purpose | Persistence Mechanism |
|-------------|-------------|---------|----------------------|
| `redis-data` | `/data` | RDB snapshots, AOF logs | Configurable via Redis persistence settings |

Redis persistence can be configured via RDB (snapshotting) or AOF (append-only file) modes. The default Redis configuration enables both mechanisms.

**Sources:** [docker-compose.yml:31](), [docker-compose.yml:283]()

### Redis Use Cases in AiToEarn

| Use Case | Implementation | Data Structure |
|----------|----------------|----------------|
| Session Storage | User authentication sessions | Hash sets with TTL |
| API Cache | Response caching for external API calls | String values with expiration |
| Job Queue | BullMQ for calendar timing, publishing tasks | Lists, sorted sets |
| Rate Limiting | API request throttling | Counters with expiration |
| Distributed Locks | Redlock implementation for concurrent operations | String keys with NX option |

**Sources:** [DOCKER_DEPLOYMENT_EN.md:297-316](), [DOCKER_DEPLOYMENT_CN.md:297-316]()

### Healthcheck Mechanism

[docker-compose.yml:34-39]()

```yaml
healthcheck:
  test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
  interval: 10s
  timeout: 3s
  retries: 5
  start_period: 30s
```

The healthcheck increments a `ping` key to verify Redis is accepting commands. Authentication is handled automatically via the `--raw` flag.

**Sources:** [docker-compose.yml:34-39]()

---

## RustFS Object Storage

### Service Configuration

RustFS provides S3-compatible object storage for user-generated assets including images, videos, and documents. It eliminates the need for external cloud storage services during development and testing.

```mermaid
graph TB
    subgraph RustFS["RustFS Services"]
        RustFSAPI["aitoearn-rustfs<br/>API: :9000<br/>Console: :9001"]
        RustFSInit["aitoearn-rustfs-init<br/>minio/mc client<br/>Initialization"]
    end
    
    subgraph Volume["Host Volume"]
        RustFSVol["rustfs-data<br/>Driver: local<br/>Mount: /data"]
    end
    
    subgraph Network["Docker Network Alias"]
        Alias["rustfs.local<br/>Internal DNS"]
    end
    
    subgraph Clients["Application Clients"]
        AiClient["aitoearn-ai<br/>Endpoint: http://rustfs.local:9000"]
        ServerClient["aitoearn-server<br/>Endpoint: http://rustfs.local:9000"]
    end
    
    subgraph BucketInit["Bucket Initialization"]
        CreateBucket["mc mb rustfs/aitoearn"]
        SetPolicy["mc anonymous set download"]
    end
    
    RustFSAPI -->|"Store objects"| RustFSVol
    RustFSAPI -.->|"Accessible via"| Alias
    RustFSInit -->|"Configure"| RustFSAPI
    RustFSInit --> CreateBucket
    RustFSInit --> SetPolicy
    
    AiClient -->|"S3 API calls"| Alias
    ServerClient -->|"S3 API calls"| Alias
```

**Container Definition:**

[docker-compose.yml:41-63]()

```yaml
rustfs:
  image: rustfs/rustfs:latest
  container_name: aitoearn-rustfs
  hostname: rustfs.local
  restart: unless-stopped
  environment:
    RUSTFS_ACCESS_KEY: rustfsadmin
    RUSTFS_SECRET_KEY: rustfsadmin
  ports:
    - "9000:9000"  # S3 API
    - "9001:9001"  # Web Console
  volumes:
    - rustfs-data:/data
```

**Sources:** [docker-compose.yml:41-63]()

### Network Alias Configuration

RustFS uses a Docker network alias `rustfs.local` to provide stable DNS resolution within the `aitoearn-network`:

[docker-compose.yml:55-57]()

```yaml
networks:
  aitoearn-network:
    aliases:
      - rustfs.local
```

This allows application services to connect using `http://rustfs.local:9000` regardless of container recreation.

**Sources:** [docker-compose.yml:55-57]()

### Bucket Initialization

A separate `rustfs-init` container runs once after RustFS starts to configure the storage:

[docker-compose.yml:65-79]()

```yaml
rustfs-init:
  image: minio/mc:latest
  container_name: aitoearn-rustfs-init
  depends_on:
    rustfs:
      condition: service_healthy
  entrypoint: >
    /bin/sh -c "
    mc alias set rustfs http://rustfs.local:9000 rustfsadmin rustfsadmin;
    mc mb rustfs/aitoearn --ignore-existing;
    mc anonymous set download rustfs/aitoearn;
    exit 0;
    "
```

**Initialization Steps:**
1. Create alias `rustfs` pointing to `http://rustfs.local:9000`
2. Create bucket `aitoearn` (if not exists)
3. Set bucket policy to allow public downloads
4. Exit (container does not run continuously)

**Sources:** [docker-compose.yml:65-79]()

### S3 API Compatibility

RustFS implements the S3 API protocol, allowing standard S3 clients to interact with it:

| S3 Operation | Support | Usage in AiToEarn |
|--------------|---------|-------------------|
| PutObject | ✓ | Upload images, videos, documents |
| GetObject | ✓ | Retrieve assets for serving |
| DeleteObject | ✓ | Remove old or unwanted assets |
| ListObjects | ✓ | Browse bucket contents |
| HeadObject | ✓ | Check file existence and metadata |

Application services configure the S3 client to point to `http://rustfs.local:9000` with credentials `rustfsadmin:rustfsadmin`.

**Sources:** [DOCKER_DEPLOYMENT_EN.md:175-203](), [DOCKER_DEPLOYMENT_CN.md:175-203]()

### Web Console Access

RustFS provides a web-based management console accessible at `http://localhost:9001`:

| Feature | Description |
|---------|-------------|
| Bucket Management | Create, delete, and configure buckets |
| File Browser | Upload, download, and delete objects |
| Access Control | Manage bucket policies and user permissions |
| Monitoring | View storage usage and access logs |

**Default Credentials:**
- Username: `rustfsadmin`
- Password: `rustfsadmin`

**Sources:** [DOCKER_DEPLOYMENT_EN.md:179-181](), [DOCKER_DEPLOYMENT_CN.md:179-181]()

### Healthcheck Mechanism

[docker-compose.yml:58-63]()

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:9000/health"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

The healthcheck polls the `/health` endpoint to verify RustFS is accepting S3 API requests.

**Sources:** [docker-compose.yml:58-63]()

---

## Volume Configuration and Management

### Docker Volume Definitions

All persistent data is stored in Docker-managed local volumes defined at the bottom of the Compose file:

[docker-compose.yml:277-285]()

```yaml
volumes:
  mongodb-data:
    driver: local
  mongodb-config:
    driver: local
  redis-data:
    driver: local
  rustfs-data:
    driver: local
```

**Volume Properties:**

| Volume Name | Driver | Location (default) | Typical Size |
|-------------|--------|-------------------|--------------|
| `mongodb-data` | local | `/var/lib/docker/volumes/mongodb-data/_data` | 1-10GB+ |
| `mongodb-config` | local | `/var/lib/docker/volumes/mongodb-config/_data` | <100MB |
| `redis-data` | local | `/var/lib/docker/volumes/redis-data/_data` | 100MB-1GB |
| `rustfs-data` | local | `/var/lib/docker/volumes/rustfs-data/_data` | 10GB-1TB+ |

**Sources:** [docker-compose.yml:277-285]()

### Data Persistence Guarantees

```mermaid
graph TB
    subgraph Lifecycle["Container Lifecycle"]
        Running["Container Running"]
        Stopped["Container Stopped<br/>docker compose stop"]
        Removed["Container Removed<br/>docker compose down"]
        VolumeRemoved["Volume Removed<br/>docker compose down -v"]
    end
    
    subgraph DataState["Data State"]
        DataIntact["Data Intact ✓"]
        DataLost["Data Lost ✗"]
    end
    
    Running -->|"Stop"| Stopped
    Stopped -->|"Remove container"| Removed
    Removed -->|"Remove volumes"| VolumeRemoved
    
    Running --> DataIntact
    Stopped --> DataIntact
    Removed --> DataIntact
    VolumeRemoved --> DataLost
    
    Note1["Volumes persist across<br/>container lifecycle"]
    Note2["Only explicit volume deletion<br/>removes data"]
    
    DataIntact -.-> Note1
    VolumeRemoved -.-> Note2
```

**Persistence Behavior:**

| Command | Container State | Volume State | Data Preserved |
|---------|----------------|--------------|----------------|
| `docker compose stop` | Stopped | Unchanged | ✓ Yes |
| `docker compose down` | Removed | Unchanged | ✓ Yes |
| `docker compose down -v` | Removed | Removed | ✗ No |
| System restart | Restarted | Unchanged | ✓ Yes |

**Sources:** [DOCKER_DEPLOYMENT_EN.md:1-326]()

### Backup and Restore Considerations

For production deployments, regular backups should be implemented:

**MongoDB Backup:**
```bash
docker exec aitoearn-mongodb mongodump --archive=/data/backup.archive --gzip
docker cp aitoearn-mongodb:/data/backup.archive ./backup-$(date +%Y%m%d).archive
```

**Redis Backup:**
```bash
docker exec aitoearn-redis redis-cli --rdb /data/dump.rdb SAVE
docker cp aitoearn-redis:/data/dump.rdb ./redis-backup-$(date +%Y%m%d).rdb
```

**RustFS Backup:**
```bash
docker exec aitoearn-rustfs mc mirror rustfs/aitoearn /tmp/backup
docker cp aitoearn-rustfs:/tmp/backup ./rustfs-backup-$(date +%Y%m%d)
```

**Sources:** [DOCKER_DEPLOYMENT_EN.md:276-326](), [DOCKER_DEPLOYMENT_CN.md:276-326]()

---

## Application Integration

### Connection Configuration Flow

```mermaid
graph LR
    subgraph EnvVars["docker-compose.yml<br/>Environment Variables"]
        MongoEnv["MONGODB_HOST=mongodb<br/>MONGODB_PORT=27017<br/>MONGODB_PASSWORD=password"]
        RedisEnv["REDIS_HOST=redis<br/>REDIS_PORT=6379<br/>REDIS_PASSWORD=password"]
        RustFSEnv["S3 credentials in config files"]
    end
    
    subgraph ConfigFiles["Config Files<br/>(Mounted Volumes)"]
        AiConfig["config/aitoearn-ai.config.js<br/>→ /app/config.js"]
        ServerConfig["config/aitoearn-server.config.js<br/>→ /app/config.js"]
    end
    
    subgraph AppServices["Application Services"]
        AiService["aitoearn-ai:3010"]
        ServerService["aitoearn-server:3002"]
    end
    
    subgraph Storage["Storage Services"]
        MongoDB["mongodb:27017"]
        Redis["redis:6379"]
        RustFS["rustfs.local:9000"]
    end
    
    MongoEnv -->|"Process env"| AiService
    MongoEnv -->|"Process env"| ServerService
    RedisEnv -->|"Process env"| AiService
    RedisEnv -->|"Process env"| ServerService
    
    AiConfig -->|"Mounted"| AiService
    ServerConfig -->|"Mounted"| ServerService
    
    AiService -->|"MongoDB URI"| MongoDB
    AiService -->|"Redis connection"| Redis
    AiService -->|"S3 API"| RustFS
    
    ServerService -->|"MongoDB URI"| MongoDB
    ServerService -->|"Redis connection"| Redis
    ServerService -->|"S3 API"| RustFS
```

**Sources:** [docker-compose.yml:81-135](), [docker-compose.yml:136-232]()

### Service-to-Storage Connection Matrix

| Storage | aitoearn-ai | aitoearn-server | Connection Method |
|---------|-------------|-----------------|-------------------|
| **MongoDB** | ✓ Primary DB | ✓ Primary DB + Statistics DB | `mongodb://admin:password@mongodb:27017` |
| **Redis** | ✓ Cache + Jobs | ✓ Cache + Jobs | `redis://:password@redis:6379` |
| **RustFS** | ✓ Asset uploads | ✓ Asset uploads | S3 client → `http://rustfs.local:9000` |

**Sources:** [docker-compose.yml:100-112](), [docker-compose.yml:157-174]()

### MongoDB Connection Configuration

**aitoearn-ai:**

[docker-compose.yml:100-103]()
```yaml
MONGODB_HOST: mongodb
MONGODB_PORT: 27017
MONGODB_USERNAME: admin
MONGODB_PASSWORD: password
```

**aitoearn-server:**

[docker-compose.yml:157-165]()
```yaml
MONGODB_HOST: mongodb
MONGODB_PORT: 27017
MONGODB_USERNAME: admin
MONGODB_PASSWORD: password

STATISTICS_DB_HOST: mongodb
STATISTICS_DB_PORT: 27017
STATISTICS_DB_USERNAME: admin
STATISTICS_DB_PASSWORD: password
```

The application services construct MongoDB connection URIs from these environment variables in the format:
`mongodb://username:password@host:port/database`

**Sources:** [docker-compose.yml:100-103](), [docker-compose.yml:157-165]()

### Redis Connection Configuration

Both services use identical Redis configuration:

[docker-compose.yml:105-107]()
```yaml
REDIS_HOST: redis
REDIS_PORT: 6379
REDIS_PASSWORD: password
```

Redis connections use the standard format: `redis://:password@host:port`

**Sources:** [docker-compose.yml:105-107](), [docker-compose.yml:167-169]()

### RustFS (S3) Connection Configuration

RustFS connection details are stored in the mounted configuration files rather than environment variables for security:

**Configuration File Mounting:**

[docker-compose.yml:91-92]()
```yaml
volumes:
  - ./config/aitoearn-ai.config.js:/app/config.js:ro
```

[docker-compose.yml:148]()
```yaml
volumes:
  - ./config/aitoearn-server.config.js:/app/config.js:ro
```

The config files (`config/aitoearn-ai.config.js` and `config/aitoearn-server.config.js`) contain an `assets` section with S3 credentials:

```javascript
assets: {
  provider: 's3',
  region: 'auto',
  bucketName: 'aitoearn',
  endpoint: 'http://rustfs.local:9000',
  accessKeyId: 'rustfsadmin',
  secretAccessKey: 'rustfsadmin',
}
```

**Sources:** [docker-compose.yml:91-92](), [docker-compose.yml:148](), [DOCKER_DEPLOYMENT_EN.md:98-110]()

### Dependency Management

Services use health checks and `depends_on` conditions to ensure storage layers are ready before application services start:

[docker-compose.yml:85-89]()
```yaml
aitoearn-ai:
  depends_on:
    mongodb:
      condition: service_healthy
    redis:
      condition: service_healthy
```

[docker-compose.yml:140-147]()
```yaml
aitoearn-server:
  depends_on:
    mongodb:
      condition: service_healthy
    redis:
      condition: service_healthy
    aitoearn-ai:
      condition: service_healthy
```

This ensures:
1. MongoDB and Redis are healthy before aitoearn-ai starts
2. All storage services + aitoearn-ai are healthy before aitoearn-server starts
3. Prevents connection errors during initialization

**Sources:** [docker-compose.yml:85-89](), [docker-compose.yml:140-147]()

---

## Data Flow Patterns

### Typical Request Data Flow

```mermaid
sequenceDiagram
    participant Client as Browser/API Client
    participant Nginx as nginx:80
    participant Web as aitoearn-web:3000
    participant Server as aitoearn-server:3002
    participant AI as aitoearn-ai:3010
    participant Redis as redis:6379
    participant Mongo as mongodb:27017
    participant RustFS as rustfs.local:9000

    Client->>Nginx: HTTP Request
    Nginx->>Web: Forward (if /*)
    Nginx->>Server: Forward (if /api/*)
    
    Server->>Redis: Check cache
    alt Cache Hit
        Redis-->>Server: Cached data
        Server-->>Nginx: Response
    else Cache Miss
        Server->>Mongo: Query database
        Mongo-->>Server: Document data
        Server->>Redis: Store cache
        Server-->>Nginx: Response
    end
    
    Note over Server,AI: AI Operations
    Server->>AI: AI request
    AI->>Mongo: Save generation metadata
    AI->>RustFS: Upload generated asset
    RustFS-->>AI: Asset URL
    AI-->>Server: Response with URL
    
    Note over Server: Background Jobs
    Server->>Redis: Enqueue job (BullMQ)
    Redis-->>Server: Job ID
    
    Nginx->>Client: HTTP Response
```

**Sources:** [docker-compose.yml:1-286]()

### Data Lifecycle by Type

| Data Type | Primary Storage | Cache Layer | Backup Storage | Lifecycle |
|-----------|----------------|-------------|----------------|-----------|
| User accounts | MongoDB | Redis (sessions) | - | Persistent |
| Content drafts | MongoDB | - | - | Persistent |
| OAuth tokens | MongoDB | Redis (active) | - | TTL-based |
| Published content metadata | MongoDB | - | - | Persistent |
| Asset files (images/videos) | RustFS | - | External CDN | Persistent |
| API responses | - | Redis | - | TTL (5-60 min) |
| Job queue | - | Redis (BullMQ) | - | Processed then deleted |
| Analytics events | MongoDB (statistics DB) | - | - | Persistent |
| Rate limit counters | - | Redis | - | TTL (1 hour) |

**Sources:** [DOCKER_DEPLOYMENT_EN.md:141-172](), [DOCKER_DEPLOYMENT_CN.md:141-172]()

---

## Network Topology

### aitoearn-network Bridge Configuration

All storage and application services communicate over a dedicated Docker bridge network:

[docker-compose.yml:272-275]()
```yaml
networks:
  aitoearn-network:
    driver: bridge
    name: aitoearn-network
```

**Network Characteristics:**

| Property | Value | Purpose |
|----------|-------|---------|
| Driver | `bridge` | Isolated network for service-to-service communication |
| Name | `aitoearn-network` | Explicit naming for network inspection |
| DNS | Automatic | Service names resolve to container IPs |
| Isolation | Internal | External access only via exposed ports |

**Service Discovery:**

Services reference each other by container name:
- `mongodb` resolves to the MongoDB container IP
- `redis` resolves to the Redis container IP  
- `rustfs.local` resolves to the RustFS container IP (via alias)
- `aitoearn-server` resolves to the server container IP
- `aitoearn-ai` resolves to the AI service container IP

**Sources:** [docker-compose.yml:14-15](), [docker-compose.yml:32-33](), [docker-compose.yml:54-57](), [docker-compose.yml:272-275]()

### Port Exposure

```mermaid
graph LR
    subgraph External["External Access<br/>(localhost)"]
        Port8080["8080<br/>(Nginx)"]
        Port9000["9000<br/>(RustFS API)"]
        Port9001["9001<br/>(RustFS Console)"]
        Port27017["27017<br/>(MongoDB)"]
        Port6379["6379<br/>(Redis)"]
    end
    
    subgraph Internal["aitoearn-network<br/>(Internal Only)"]
        Web["aitoearn-web:3000"]
        Server["aitoearn-server:3002"]
        AI["aitoearn-ai:3010"]
    end
    
    subgraph Storage["Storage Services<br/>(Dual Access)"]
        MongoDB["mongodb:27017"]
        Redis["redis:6379"]
        RustFS["rustfs:9000/9001"]
    end
    
    Port8080 -.-> |"Proxies to"| Web
    Port8080 -.-> |"Proxies to"| Server
    Port27017 -.-> MongoDB
    Port6379 -.-> Redis
    Port9000 -.-> RustFS
    Port9001 -.-> RustFS
    
    Web --> Server
    Server --> AI
    Server --> MongoDB
    Server --> Redis
    Server --> RustFS
    AI --> MongoDB
    AI --> Redis
    AI --> RustFS
```

**Exposed Ports:**

| Service | Internal Port | External Port | Access Purpose |
|---------|---------------|---------------|----------------|
| nginx | 80 | 8080 | Web UI and API gateway |
| mongodb | 27017 | 27017 | Database access for debugging |
| redis | 6379 | 6379 | Cache access for debugging |
| rustfs | 9000 | 9000 | S3 API (optional external access) |
| rustfs | 9001 | 9001 | Web console |

**Internal-Only Ports:**

| Service | Port | Access |
|---------|------|--------|
| aitoearn-web | 3000 | Via nginx only |
| aitoearn-server | 3002 | Via nginx only |
| aitoearn-ai | 3010 | Via aitoearn-server only |

**Sources:** [docker-compose.yml:10](), [docker-compose.yml:29](), [docker-compose.yml:49-51](), [docker-compose.yml:260]()

---

# Page: Frontend Architecture

# Frontend Architecture

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



This document describes the Next.js frontend application architecture for AiToEarn, including its deployment structure, API integration patterns, and how it communicates with backend services through the Nginx reverse proxy.

For information about the complete Docker service orchestration, see [Docker Compose Service Architecture](#2.1). For details on how the frontend interacts with data storage, see [Data Persistence Layer](#2.2). For the Electron desktop application, see [Electron Desktop Application](#2.4).

---

## Technology Stack

The AiToEarn frontend is built with modern web technologies optimized for server-side rendering and client-side interactivity:

| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 14 | React framework with SSR/SSG capabilities |
| **React** | 18 | UI component library |
| **TypeScript** | - | Type-safe JavaScript |
| **Node.js** | 20.18.x | Runtime environment |

The frontend runs as a standalone Next.js server inside a Docker container, serving both server-rendered pages and static assets.

**Sources:** [README.md:8](), [README_CN.md:7](), [DOCKER_DEPLOYMENT_EN.md:16-18]()

---

## Service Architecture in Docker

The frontend service is deployed as a containerized application that integrates with the broader AiToEarn platform through Docker Compose.

### Frontend Service Deployment

```mermaid
graph TB
    subgraph "Docker Host"
        subgraph "Nginx Container :8080"
            Nginx["Nginx Reverse Proxy"]
        end
        
        subgraph "Frontend Container"
            NextJS["aitoearn-web<br/>Next.js Server :3000"]
            EnvConfig["Environment Variables<br/>NEXT_PUBLIC_API_URL<br/>NODE_ENV"]
        end
        
        subgraph "Backend Container"
            Server["aitoearn-server :3002"]
        end
        
        subgraph "Docker Network: aitoearn-network"
            NetworkLayer["Internal DNS Resolution"]
        end
    end
    
    Browser["Web Browser"] -->|HTTP :8080| Nginx
    Nginx -->|Proxy Pass /<br/>http://aitoearn-web:3000| NextJS
    Nginx -->|Proxy Pass /api/*<br/>http://aitoearn-server:3002| Server
    NextJS -.->|API Calls via Browser<br/>NEXT_PUBLIC_API_URL| Nginx
    
    EnvConfig --> NextJS
    NextJS --> NetworkLayer
    Server --> NetworkLayer
    Nginx --> NetworkLayer
```

**Docker Compose Configuration:**

The `aitoearn-web` service is defined with minimal configuration, relying on the built image to contain all necessary dependencies:

```yaml
# Key configuration from docker-compose.yml
aitoearn-web:
  image: aitoearn/aitoearn-web:latest
  container_name: aitoearn-web
  restart: unless-stopped
  depends_on:
    aitoearn-server:
      condition: service_healthy
  networks:
    - aitoearn-network
  environment:
    NODE_ENV: production
    NEXT_TELEMETRY_DISABLED: 1
    NEXT_PUBLIC_API_URL: http://localhost:8080/api
```

**Sources:** [docker-compose.yml:234-246](), [DOCKER_DEPLOYMENT_EN.md:28-36]()

---

## Network Communication Pattern

### Request Routing Through Nginx

The frontend is accessed through Nginx, which acts as a unified reverse proxy for all services. This architecture provides:

1. **Single port exposure** - All traffic enters through port 8080
2. **Path-based routing** - Static files and API calls are routed differently
3. **Service isolation** - Frontend runs on internal port 3000, not exposed externally

```mermaid
sequenceDiagram
    participant Browser
    participant Nginx as Nginx :8080
    participant Web as aitoearn-web :3000
    participant Server as aitoearn-server :3002
    
    Note over Browser,Server: Initial Page Load
    Browser->>Nginx: GET / HTTP/1.1
    Nginx->>Web: Proxy to aitoearn-web:3000
    Web->>Web: Server-side render
    Web->>Nginx: HTML response
    Nginx->>Browser: HTML page
    
    Note over Browser,Server: Client-side API Call
    Browser->>Nginx: GET /api/user HTTP/1.1<br/>(NEXT_PUBLIC_API_URL)
    Nginx->>Server: Proxy to aitoearn-server:3002
    Server->>Server: Process request
    Server->>Nginx: JSON response
    Nginx->>Browser: JSON data
    
    Note over Browser,Server: Static Asset
    Browser->>Nginx: GET /_next/static/...
    Nginx->>Web: Proxy to aitoearn-web:3000
    Web->>Nginx: Static file
    Nginx->>Browser: Asset (CSS/JS/Image)
```

**Nginx Configuration Pattern:**

The Nginx configuration routes requests based on path patterns:
- `/` → `aitoearn-web:3000` (frontend pages)
- `/api/*` → `aitoearn-server:3002` (backend API)
- `/_next/*` → `aitoearn-web:3000` (Next.js static assets)

**Sources:** [docker-compose.yml:248-270](), [DOCKER_DEPLOYMENT_EN.md:8-26]()

---

## Environment Configuration

### Build-time vs Runtime Configuration

The frontend uses Next.js environment variable patterns to handle configuration at different stages:

| Variable Type | Prefix | Available | Example |
|--------------|--------|-----------|---------|
| **Public (Client-side)** | `NEXT_PUBLIC_*` | Browser + Server | `NEXT_PUBLIC_API_URL` |
| **Server-side only** | No prefix | Server only | `NODE_ENV` |

```mermaid
graph LR
    subgraph "Build Time"
        BuildEnv["Build Environment<br/>NEXT_TELEMETRY_DISABLED<br/>NODE_ENV"]
    end
    
    subgraph "Runtime Container"
        RuntimeEnv["Container Environment<br/>NEXT_PUBLIC_API_URL"]
        NextServer["Next.js Server"]
    end
    
    subgraph "Browser"
        ClientCode["Client JavaScript"]
        PublicEnv["window.__NEXT_DATA__<br/>NEXT_PUBLIC_API_URL"]
    end
    
    BuildEnv -->|Docker Build| RuntimeEnv
    RuntimeEnv --> NextServer
    NextServer -->|SSR/Hydration| ClientCode
    NextServer -.->|Injected at Runtime| PublicEnv
    ClientCode --> PublicEnv
```

### Key Environment Variables

**`NEXT_PUBLIC_API_URL`** - The most critical frontend configuration variable:

```yaml
# Default configuration for local development
NEXT_PUBLIC_API_URL: http://localhost:8080/api

# Production configuration example
NEXT_PUBLIC_API_URL: https://your-domain.com/api
```

This variable determines where client-side API calls are directed. It must match the public-facing URL of the Nginx proxy, not the internal service URLs.

**`NODE_ENV`** - Controls Next.js optimization level:
- `production` - Optimized builds, no dev tools
- `development` - Hot reload, verbose errors

**`NEXT_TELEMETRY_DISABLED`** - Disables Next.js telemetry data collection:
```yaml
NEXT_TELEMETRY_DISABLED: 1
```

**Sources:** [docker-compose.yml:243-246](), [DOCKER_DEPLOYMENT_EN.md:148-151]()

---

## API Integration Pattern

### Client-side API Communication

The frontend makes API calls exclusively through the browser using the `NEXT_PUBLIC_API_URL` environment variable. This pattern ensures all API traffic flows through Nginx, maintaining consistent routing and security policies.

```mermaid
graph TB
    subgraph "Browser Context"
        Component["React Component"]
        APIClient["API Client Layer"]
        EnvVar["NEXT_PUBLIC_API_URL<br/>http://localhost:8080/api"]
    end
    
    subgraph "Network Boundary"
        Nginx["Nginx :8080"]
    end
    
    subgraph "Backend Services"
        APIServer["aitoearn-server :3002<br/>/api/*"]
        AIServer["aitoearn-ai :3010<br/>/api/ai/*"]
    end
    
    Component -->|"fetch('/api/user')"| APIClient
    APIClient --> EnvVar
    EnvVar -->|"HTTP Request<br/>http://localhost:8080/api/user"| Nginx
    Nginx -->|"Proxy to<br/>aitoearn-server:3002"| APIServer
    Nginx -.->|"AI-specific routes"| AIServer
    
    APIServer -->|"JSON Response"| Nginx
    Nginx -->|"Response"| APIClient
    APIClient -->|"Update State"| Component
```

### No Server-side Backend Calls

The Next.js server component does **not** make direct internal API calls to `aitoearn-server`. All data fetching happens client-side through the public API endpoint. This architecture:

1. Simplifies authentication (tokens in browser storage)
2. Reduces server-side complexity
3. Leverages Next.js client-side data fetching patterns
4. Maintains clear separation between frontend and backend services

**Sources:** [docker-compose.yml:234-246](), [DOCKER_DEPLOYMENT_EN.md:129-135]()

---

## Container Health and Dependencies

### Service Dependencies

The frontend service has explicit dependency ordering to ensure backend services are ready before accepting traffic:

```mermaid
graph TB
    subgraph "Startup Sequence"
        MongoDB["mongodb<br/>Health: mongosh ping"]
        Redis["redis<br/>Health: redis-cli incr ping"]
        AI["aitoearn-ai<br/>Health: HTTP /health"]
        Server["aitoearn-server<br/>Health: HTTP /health"]
        Web["aitoearn-web<br/>No health check"]
        Nginx["nginx<br/>Health: wget /_nhealth"]
    end
    
    MongoDB -->|healthy| Redis
    Redis -->|healthy| AI
    MongoDB -->|healthy| Server
    Redis -->|healthy| Server
    AI -->|healthy| Server
    Server -->|healthy| Web
    Web -->|started| Nginx
```

**Dependency Configuration:**

```yaml
# aitoearn-web depends on backend being healthy
depends_on:
  aitoearn-server:
    condition: service_healthy
```

The frontend service itself **does not have a health check** defined, as Next.js servers are considered ready once the container starts. The Nginx service waits for the web service to be in `running` state before starting.

**Sources:** [docker-compose.yml:238-241](), [docker-compose.yml:252-258](), [docker-compose.yml:16-21](), [docker-compose.yml:34-39](), [docker-compose.yml:129-134](), [docker-compose.yml:227-232]()

---

## Development vs Production Modes

### Production Deployment (Docker)

In production mode via Docker Compose:

1. **Pre-built image** - `aitoearn/aitoearn-web:latest` contains the compiled Next.js application
2. **Production server** - Next.js runs in production mode (`NODE_ENV=production`)
3. **Optimized bundles** - Static assets are pre-optimized during image build
4. **No hot reload** - Code changes require image rebuild

```bash
# Production startup command (inside Docker)
docker compose up -d aitoearn-web
```

### Development Mode (Manual)

For local development without Docker:

```bash
# Install dependencies
pnpm install

# Start development server with hot reload
pnpm run dev
```

In development mode:
- **Hot module replacement** - Code changes reload automatically
- **Verbose errors** - Detailed error messages and stack traces
- **Direct backend access** - Can point `NEXT_PUBLIC_API_URL` to local backend

Development mode is covered in more detail in [Development Mode Setup](#8.1).

**Sources:** [README.md:209-214](), [README_CN.md:196-199](), [docker-compose.yml:234-246]()

---

## Routing and Nginx Integration

### URL Path Handling

The frontend integrates with Nginx through path-based routing rules:

| Path Pattern | Routed To | Purpose |
|--------------|-----------|---------|
| `/` | `aitoearn-web:3000` | Root page / home |
| `/login`, `/dashboard`, etc. | `aitoearn-web:3000` | Application pages |
| `/_next/static/*` | `aitoearn-web:3000` | Next.js static assets (JS, CSS) |
| `/_next/image/*` | `aitoearn-web:3000` | Next.js Image Optimization API |
| `/api/*` | `aitoearn-server:3002` | Backend API calls |

```mermaid
graph LR
    subgraph "Client Browser"
        Request["HTTP Request"]
    end
    
    subgraph "Nginx :8080"
        Router["Path-based Router"]
    end
    
    subgraph "Services"
        Web["aitoearn-web :3000<br/>Next.js App"]
        Server["aitoearn-server :3002<br/>NestJS API"]
    end
    
    Request --> Router
    Router -->|"/, /_next/*"| Web
    Router -->|"/api/*"| Server
```

**Nginx Configuration Reference:**

The Nginx configuration file is mounted into the container at:
```yaml
volumes:
  - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
```

This read-only mount ensures the Nginx configuration is synchronized with the repository and cannot be modified at runtime.

**Sources:** [docker-compose.yml:261-262](), [README.md:172-180](), [DOCKER_DEPLOYMENT_EN.md:129-135]()

---

## Static Asset Management

### Next.js Asset Pipeline

Next.js handles static assets through several mechanisms:

1. **`/_next/static/` directory** - Hashed, immutable build artifacts
2. **`/public/` directory** - Public static files served at root
3. **Image Optimization API** - `/_next/image/*` for automatic image optimization

All static assets are served through the Next.js server running on port 3000, which is proxied by Nginx. This allows Next.js to:

- Apply cache headers automatically
- Serve optimized images based on device capabilities
- Handle static file compression

### Asset Upload and User-Generated Content

User-uploaded assets (images, videos, documents) are **not** stored or served by the frontend. Instead:

1. Files are uploaded directly to object storage (RustFS/S3)
2. Backend generates signed URLs or public URLs
3. Frontend displays assets via `<img>` tags pointing to storage URLs

For details on object storage configuration, see [Data Persistence Layer](#2.2).

**Sources:** [docker-compose.yml:234-246](), [DOCKER_DEPLOYMENT_EN.md:173-203]()

---

## Network Isolation and Security

### Internal Docker Network

The frontend communicates with other services exclusively through the `aitoearn-network` bridge network:

```mermaid
graph TB
    subgraph "aitoearn-network (Bridge Network)"
        Web["aitoearn-web<br/>Internal: 172.x.x.x:3000"]
        Server["aitoearn-server<br/>Internal: 172.x.x.x:3002"]
        AI["aitoearn-ai<br/>Internal: 172.x.x.x:3010"]
        Nginx["nginx<br/>Internal: 172.x.x.x:80"]
        
        DNS["Docker DNS<br/>Service Resolution"]
    end
    
    External["External Traffic<br/>0.0.0.0:8080"] -->|Port Mapping| Nginx
    
    Nginx --> Web
    Nginx --> Server
    
    Web -.->|No direct connection| Server
    Web -.->|No direct connection| AI
    
    DNS --> Web
    DNS --> Server
    DNS --> AI
    DNS --> Nginx
```

**Network Configuration:**

```yaml
networks:
  aitoearn-network:
    driver: bridge
    name: aitoearn-network
```

All services join this network, allowing Docker DNS to resolve service names (e.g., `aitoearn-server` resolves to the container's IP). However, the frontend **does not make internal network requests** - all API calls flow through the browser to Nginx.

**Sources:** [docker-compose.yml:272-275](), [docker-compose.yml:241-242]()

---

## Summary

The AiToEarn frontend architecture is characterized by:

1. **Next.js 14** - Modern React framework with SSR capabilities
2. **Docker containerization** - Isolated, reproducible deployments
3. **Nginx proxy integration** - All traffic routed through single entry point
4. **Client-side API calls** - Browser makes requests via `NEXT_PUBLIC_API_URL`
5. **Environment-based configuration** - Different settings for dev/production
6. **Service dependency management** - Waits for backend health before starting

This architecture provides a clear separation between frontend rendering and backend API services, with Nginx acting as the unified gateway that routes requests based on URL paths.

**Sources:** [README.md:1-267](), [docker-compose.yml:234-270](), [DOCKER_DEPLOYMENT_EN.md:1-450]()

---

# Page: Electron Desktop Application

# Electron Desktop Application

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



The AttAiToEarn Electron desktop application provides a native desktop client for the AiToEarn platform. This application is maintained in a separate repository from the main web application and offers desktop-specific features such as system tray integration and native window management.

## Overview

AttAiToEarn is a standalone Electron desktop application located at https://github.com/yikart/AttAiToEarn. It provides the same content creation and publishing functionality as the web interface ([2.3](#2.3)), but packages it as a native desktop application for Windows, macOS, and Linux.

The desktop application follows standard Electron architecture with two primary processes:

- **Main Process**: Node.js runtime that controls the application lifecycle, system integration, and window management
- **Renderer Process**: Chromium-based process that renders the UI using web technologies

```mermaid
graph TB
    subgraph "AttAiToEarn Desktop Application"
        mainProcess["Main Process<br/>(Node.js)"]
        rendererProcess["Renderer Process<br/>(Chromium + React)"]
        
        mainProcess --> windowMgmt["Window Management"]
        mainProcess --> lifecycle["App Lifecycle"]
        mainProcess --> systemIntegration["System Integration"]
        
        rendererProcess --> ui["Desktop UI"]
        rendererProcess --> apiClient["Backend API Client"]
        
        mainProcess <-->|"IPC"| rendererProcess
    end
    
    subgraph "Backend Services"
        backend["aitoearn-server<br/>:3002"]
        aiService["aitoearn-ai<br/>:3010"]
    end
    
    apiClient -->|"HTTP/WebSocket"| backend
    apiClient -->|"HTTP"| aiService
```

Sources: [README.md:220-242]()

## Repository Location

The Electron desktop application is maintained in a separate repository from the main AiToEarn platform:

**Repository**: https://github.com/yikart/AttAiToEarn

This separation allows independent versioning and releases of the desktop client while consuming the same backend services ([2.1](#2.1)) as the web application.

## Building and Running

### Prerequisites

- **Node.js**: Version 20.18.x or compatible
- **npm**: Comes with Node.js
- **Python**: Required for compiling native dependencies (better-sqlite3)
- **node-gyp**: Build tool for native Node.js modules

On Windows, you may need to install Windows Build Tools:
```bash
npm install --global windows-build-tools
```

### Development Mode

To run the desktop application in development mode:

```bash
# Clone the repository
git clone https://github.com/yikart/AttAiToEarn.git

# Enter directory
cd AttAiToEarn

# Install dependencies
npm i

# Compile SQLite native module (requires node-gyp and Python)
npm run rebuild

# Start development mode
npm run dev
```

Sources: [README.md:220-242]()

In development mode, the Electron app typically connects to:
- Local backend at `http://localhost:3002` (aitoearn-server)
- Local AI service at `http://localhost:3010` (aitoearn-ai)

Or to the Docker Compose stack if running:
- Backend API at `http://localhost:8080/api` (via nginx)

### Building for Distribution

The desktop application uses Electron Builder for creating distributable packages:

```bash
# Build for production
npm run build
```

This creates platform-specific installers in the `dist/` directory:
- **Windows**: `.exe` installer
- **macOS**: `.dmg` disk image
- **Linux**: `.AppImage` or `.deb` package

### SQLite Compilation

The desktop application uses `better-sqlite3` for local data storage, which requires native compilation:

```bash
npm run rebuild
```

This step is necessary because:
- `better-sqlite3` contains native C++ code
- Must be compiled against the Electron runtime (not Node.js runtime)
- Requires Python and C++ build tools installed on the system

Sources: [README.md:233-234]()

## Development and Build Pipeline

The application uses Vite for development and Electron Builder for packaging:

```javascript
"scripts": {
  "dev": "chcp 65001 && vite",
  "dev:mac": "vite",
  "build": "tsc && vite build && electron-builder",
  "build:notsc": "vite build && electron-builder"
}
```

Sources: [package.json:18-31]()

### Development Environment

During development:
1. Vite starts a development server for the renderer process
2. Electron loads content from the Vite dev server URL
3. Hot module replacement enables rapid UI changes

```javascript
// Development path configuration
export const VITE_DEV_SERVER_URL = process.env.VITE_DEV_SERVER_URL;

// Conditional content loading
if (VITE_DEV_SERVER_URL) {
  await win.loadURL(VITE_DEV_SERVER_URL);
} else {
  await win.loadFile(indexHtml);
}
```

Sources: [electron/main/index.ts:24-28](), [electron/main/index.ts:92-96]()

### Production Build

For production builds:
1. TypeScript is compiled
2. Vite bundles the renderer process
3. Electron Builder packages the application for distribution

The main entry point for the packaged application is specified in package.json:

```json
{
  "name": "aiToEarn",
  "version": "0.6.0-alpha.4",
  "main": "dist-electron/main/index.js"
}
```

Sources: [package.json:1-4]()

## Conclusion

AiToEarn follows the standard Electron architecture with clear separation between main and renderer processes. The application employs custom window chrome, platform-specific adjustments, and a secure IPC system for communication between processes. The build pipeline supports both development and production environments using modern tooling like Vite and Electron Builder.

---

# Page: AI Integration System

# AI Integration System

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



## Purpose and Scope

This document provides an overview of AiToEarn's AI integration capabilities, explaining how the platform orchestrates multiple AI service providers to power content generation, analysis, and autonomous agent features. This page covers the high-level architecture, supported AI providers, and the communication patterns between the AI service and the main backend.

For detailed information about the AI service's internal architecture and HTTP routes, see [AI Service Architecture](#3.1). For configuration specifics of individual AI providers and environment variables, see [Multi-Provider Configuration](#3.2). For the autonomous AI agent feature, see [All In Agent](#3.3).

**Sources:** [README.md:1-267](), [docker-compose.yml:81-134]()

## Architecture Overview

The AI integration system is built around a dedicated **aitoearn-ai** microservice that provides a unified interface to multiple AI providers. This service runs as a separate NestJS application, isolating AI operations from the main backend and allowing independent scaling and deployment.

```mermaid
graph TB
    subgraph "Client Layer"
        WebUI["aitoearn-web<br/>(Next.js Frontend)"]
    end
    
    subgraph "Application Services"
        Server["aitoearn-server<br/>(NestJS Backend)<br/>Port 3002"]
        AIService["aitoearn-ai<br/>(NestJS AI Service)<br/>Port 3010"]
    end
    
    subgraph "Data Layer"
        MongoDB[("MongoDB<br/>AI metadata storage")]
        Redis[("Redis<br/>Job queues & cache")]
        S3["RustFS / S3<br/>Generated assets"]
    end
    
    subgraph "External AI Providers"
        OpenAI["OpenAI API<br/>OPENAI_API_KEY"]
        Claude["Anthropic Claude<br/>ANTHROPIC_API_KEY"]
        Gemini["Google Gemini<br/>GEMINI_KEY_PAIRS"]
        Grok["xAI Grok<br/>GROK_API_KEY"]
        Doubao["Volcengine Doubao<br/>VOLCENGINE_API_KEY"]
        AICSO["AICSO<br/>AICSO_API_KEY"]
    end
    
    WebUI -->|HTTP requests| Server
    Server -->|"HTTP: AI_URL<br/>http://aitoearn-ai:3010"| AIService
    AIService -->|INTERNAL_TOKEN auth| Server
    
    AIService --> MongoDB
    AIService --> Redis
    AIService --> S3
    
    AIService -->|API calls| OpenAI
    AIService -->|API calls| Claude
    AIService -->|API calls| Gemini
    AIService -->|API calls| Grok
    AIService -->|API calls| Doubao
    AIService -->|API calls| AICSO
```

**Service Communication Flow:**

1. **User requests** flow from the web frontend to `aitoearn-server`
2. **aitoearn-server** delegates AI operations to `aitoearn-ai` via internal HTTP calls
3. **aitoearn-ai** selects the appropriate AI provider based on the request and model configuration
4. **AI responses** are processed, stored in MongoDB/S3, and returned to the caller
5. **Generated assets** (images, videos) are stored in object storage (RustFS or S3)

**Sources:** [docker-compose.yml:81-134](), [docker-compose.yml:136-232](), [DOCKER_DEPLOYMENT_EN.md:1-600]()

## Supported AI Providers

AiToEarn integrates with six major AI service providers, each offering different model capabilities. The system is designed to be provider-agnostic, allowing flexible model selection based on task requirements, cost, and availability.

| Provider | Environment Variable | Primary Use Cases | Models |
|----------|---------------------|-------------------|---------|
| **OpenAI** | `OPENAI_API_KEY`<br/>`OPENAI_BASE_URL` | Text generation, chat, embeddings | GPT-4, GPT-3.5, GPT-4 Turbo |
| **Anthropic Claude** | `ANTHROPIC_API_KEY`<br/>`ANTHROPIC_BASE_URL` | Long-form content, analysis | Claude Opus 4.5, Claude Opus 4.6 |
| **Google Gemini** | `GEMINI_KEY_PAIRS`<br/>`GEMINI_LOCATION` | Multimodal tasks, video analysis | Gemini 2.5, Gemini 3.1 |
| **xAI Grok** | `GROK_API_KEY` | Real-time data, social media content | Grok models |
| **Volcengine Doubao** | `VOLCENGINE_API_KEY`<br/>`VOLCENGINE_ACCESS_KEY_ID`<br/>`VOLCENGINE_SECRET_ACCESS_KEY` | Video generation, Chinese content | Doubao models |
| **AICSO** | `AICSO_API_KEY`<br/>`AICSO_BASE_URL` | Specialized AI operations | AICSO models |

**Configuration Location:** All AI provider credentials are configured as environment variables in the `aitoearn-ai` service within [docker-compose.yml:114-128]().

**Proxy Support:** An optional `AI_PROXY_URL` environment variable [docker-compose.yml:128]() allows routing AI API requests through a proxy server for access control, rate limiting, or geographic routing.

**Sources:** [docker-compose.yml:114-128](), [README.md:146-148](), [DOCKER_DEPLOYMENT_EN.md:206-240]()

## AI Provider Orchestration

```mermaid
graph LR
    subgraph "Request Flow"
        Request["User Request<br/>(text/image/video)"]
        Server["aitoearn-server"]
        AIService["aitoearn-ai"]
        
        Request --> Server
        Server -->|"POST /api/ai/*"| AIService
    end
    
    subgraph "Model Selection Logic"
        AIService --> Selector["Model Selector<br/>(config.js models)"]
        Selector -->|Select provider| Router["Provider Router"]
    end
    
    subgraph "Provider Handlers"
        Router --> OpenAIHandler["OpenAI Handler"]
        Router --> ClaudeHandler["Claude Handler"]
        Router --> GeminiHandler["Gemini Handler"]
        Router --> GrokHandler["Grok Handler"]
        Router --> DoubaoHandler["Doubao Handler"]
        Router --> AICSOHandler["AICSO Handler"]
    end
    
    subgraph "Response Processing"
        OpenAIHandler --> Processor["Response Processor"]
        ClaudeHandler --> Processor
        GeminiHandler --> Processor
        GrokHandler --> Processor
        DoubaoHandler --> Processor
        AICSOHandler --> Processor
        
        Processor --> Storage["Store to MongoDB/S3"]
        Processor --> Response["Return to Server"]
    end
```

**Key Components:**

- **Model Selector**: Determines which AI provider and model to use based on task type, user preferences, and model availability. Model definitions are stored in `config/aitoearn-ai.config.js`.

- **Provider Router**: Directs requests to the appropriate provider-specific handler based on the selected model.

- **Provider Handlers**: Implement provider-specific API protocols, authentication, and response parsing.

- **Response Processor**: Normalizes responses from different providers into a consistent format, handles error conditions, and manages storage of generated content.

**Sources:** [docker-compose.yml:81-134](), [DOCKER_DEPLOYMENT_EN.md:285-400]()

## Content Generation Capabilities

The AI integration system powers multiple content generation features across the AiToEarn platform:

```mermaid
graph TB
    subgraph "Text Generation"
        T1["AI Copywriting<br/>Titles & captions"]
        T2["Content Expansion<br/>Abbreviation"]
        T3["Tag Generation<br/>SEO optimization"]
        T4["Comment Generation<br/>Engagement"]
    end
    
    subgraph "Image Generation"
        I1["GPT Image Models"]
        I2["Flux Models"]
        I3["Midjourney Integration"]
    end
    
    subgraph "Video Generation"
        V1["Seedance"]
        V2["Kling"]
        V3["Hailuo"]
        V4["Veo"]
        V5["Sora"]
        V6["Pika"]
        V7["Runway"]
    end
    
    subgraph "AI Agent"
        A1["All In Agent<br/>Autonomous operation"]
        A2["Content Scheduling"]
        A3["Auto Publishing"]
    end
    
    AIService["aitoearn-ai Service"]
    
    AIService --> T1
    AIService --> T2
    AIService --> T3
    AIService --> T4
    AIService --> I1
    AIService --> I2
    AIService --> I3
    AIService --> V1
    AIService --> V2
    AIService --> V3
    AIService --> V4
    AIService --> V5
    AIService --> V6
    AIService --> V7
    AIService --> A1
    AIService --> A2
    AIService --> A3
```

**Core Features:**

1. **AI-Powered Text Generation** [README.md:143-145]()
   - Automatic generation of titles, captions, and descriptions
   - Content expansion and abbreviation
   - Hashtag/tag generation for social media optimization
   - Smart commenting for engagement and traffic attraction

2. **Image Generation** [README.md:147]()
   - Support for GPT-based image models
   - Flux integration for image creation
   - Card and graphic generation for content workflows

3. **Video Generation** [README.md:146]()
   - Integration with multiple video AI models: Seedance, Kling, Hailuo, Veo, Midjourney, Sora, Pika, Runway
   - Video editing and enhancement capabilities

4. **All In Agent** [README.md:72-76]()
   - Autonomous AI agent that can automatically generate and publish content
   - Assists users in operating the AiToEarn platform
   - For details, see [All In Agent](#3.3)

**Sources:** [README.md:141-149](), [README_CN.md:130-138]()

## Service Communication and Authentication

Communication between `aitoearn-server` and `aitoearn-ai` is secured through internal authentication tokens and occurs over the Docker internal network.

**Authentication Mechanism:**

| Component | Environment Variable | Purpose |
|-----------|---------------------|---------|
| **JWT Secret** | `JWT_SECRET` | Signs and verifies JWT tokens for user authentication |
| **Internal Token** | `INTERNAL_TOKEN` | Authenticates inter-service communication between aitoearn-server and aitoearn-ai |

Both services must share the same `JWT_SECRET` and `INTERNAL_TOKEN` values [docker-compose.yml:109-110]() and [docker-compose.yml:173-174]().

**Service Endpoints:**

```mermaid
graph LR
    subgraph "aitoearn-server"
        ServerEnv["Environment:<br/>AI_URL=http://aitoearn-ai:3010"]
    end
    
    subgraph "aitoearn-ai"
        AIEnv["Environment:<br/>SERVER_URL=http://aitoearn-server:3002"]
        Health["GET /health<br/>(healthcheck)"]
        AIRoutes["POST /api/ai/*<br/>(AI operations)"]
    end
    
    ServerEnv -->|Internal HTTP| AIRoutes
    AIEnv -->|Callback requests| ServerEnv
    
    Docker["Docker Network:<br/>aitoearn-network"]
    
    ServerEnv -.->|"Resolves via DNS"| Docker
    AIEnv -.->|"Resolves via DNS"| Docker
```

**Network Configuration:**
- Both services run on the `aitoearn-network` Docker bridge network [docker-compose.yml:272-275]()
- Service discovery uses Docker's internal DNS (service names resolve to container IPs)
- No direct external access to `aitoearn-ai`; all requests proxy through `aitoearn-server` or Nginx

**Health Checks:**
- The `aitoearn-ai` service exposes a `/health` endpoint [docker-compose.yml:130]()
- Docker Compose monitors service health and ensures dependencies are ready before starting dependent services [docker-compose.yml:145-146]()

**Sources:** [docker-compose.yml:109-112](), [docker-compose.yml:171-174](), [docker-compose.yml:129-134](), [DOCKER_DEPLOYMENT_EN.md:153-161]()

## Data Persistence and Storage

The AI service persists data across three storage layers:

```mermaid
graph TB
    AIService["aitoearn-ai Service"]
    
    subgraph "Metadata Storage"
        MongoDB[("MongoDB<br/>Port 27017")]
        MongoUse["AI task records<br/>Model usage logs<br/>Generated content metadata"]
    end
    
    subgraph "Cache & Queues"
        Redis[("Redis<br/>Port 6379")]
        RedisUse["Rate limiting<br/>Request caching<br/>Job queues for async tasks"]
    end
    
    subgraph "Asset Storage"
        RustFS["RustFS / S3<br/>Port 9000"]
        S3Use["Generated images<br/>Generated videos<br/>Large response payloads"]
    end
    
    AIService --> MongoDB
    AIService --> Redis
    AIService --> RustFS
    
    MongoDB --> MongoUse
    Redis --> RedisUse
    RustFS --> S3Use
```

**MongoDB Storage** [docker-compose.yml:100-103]():
- Connection configured via `MONGODB_HOST`, `MONGODB_PORT`, `MONGODB_USERNAME`, `MONGODB_PASSWORD`
- Stores AI task metadata, model selection history, and content generation records
- Database name: `aitoearn` (shared with main application)

**Redis Storage** [docker-compose.yml:105-107]():
- Connection configured via `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`
- Used for rate limiting AI provider requests
- Caches frequently-used AI responses
- Manages job queues for asynchronous AI tasks (e.g., video generation)

**Object Storage** (configured in `config/aitoearn-ai.config.js`):
- Stores generated binary assets (images, videos)
- Default: RustFS (S3-compatible) [docker-compose.yml:41-63]()
- Configurable to external S3, Aliyun OSS, or other providers
- Access credentials: `RUSTFS_ACCESS_KEY`, `RUSTFS_SECRET_KEY` [docker-compose.yml:47-48]()

**Sources:** [docker-compose.yml:85-93](), [docker-compose.yml:100-107](), [DOCKER_DEPLOYMENT_EN.md:173-203]()

## Configuration Approach

AI provider configuration follows a two-tier approach: environment variables for sensitive credentials and configuration files for model definitions and behavior settings.

**Environment Variables (docker-compose.yml):**

All sensitive API keys and credentials are configured as environment variables in the `aitoearn-ai` service section [docker-compose.yml:95-128]():

```yaml
# Example from docker-compose.yml
environment:
  # OpenAI Configuration
  OPENAI_API_KEY: sk-placeholder
  OPENAI_BASE_URL: https://api.openai.com/v1
  
  # Anthropic Claude Configuration
  ANTHROPIC_API_KEY: sk-placeholder
  ANTHROPIC_BASE_URL: https://api.anthropic.com
  
  # Google Gemini Configuration
  GEMINI_KEY_PAIRS: '[{"projectId":"...","apiKey":"..."}]'
  GEMINI_LOCATION: us-central1
  
  # Additional providers...
```

**Configuration Files (config):**

Application-level settings are stored in `config/aitoearn-ai.config.js`, mounted as a read-only volume [docker-compose.yml:91]():

| Configuration Aspect | Location | Purpose |
|---------------------|----------|---------|
| Model Definitions | `config/aitoearn-ai.config.js` | Available models, pricing, capabilities |
| Storage Settings | `config/aitoearn-ai.config.js` | S3/RustFS endpoints, bucket names |
| Service Behavior | `config/aitoearn-ai.config.js` | Timeouts, retry logic, rate limits |
| GCS Credentials | `config/gcs-placeholder.json` | Google Cloud service account key (for Gemini) |

**Relay Service Support:**

The deployment guides recommend using an API relay service like [new-api](https://github.com/Calcium-Ion/new-api) or [one-api](https://github.com/songquanpeng/one-api) [DOCKER_DEPLOYMENT_EN.md:206-218](). This approach:

- Consolidates all AI provider access through a single endpoint
- Simplifies credential management
- Enables centralized rate limiting and cost tracking
- Requires only setting `OPENAI_BASE_URL` to the relay service URL and `OPENAI_API_KEY` to the relay service key

For detailed configuration of each AI provider, see [Multi-Provider Configuration](#3.2).

**Sources:** [docker-compose.yml:91-128](), [DOCKER_DEPLOYMENT_EN.md:98-111](), [DOCKER_DEPLOYMENT_EN.md:206-240](), [DOCKER_DEPLOYMENT_CN.md:206-247]()

---

# Page: AI Service Architecture

# AI Service Architecture

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



## Purpose and Scope

This document details the architecture of the `aitoearn-ai` NestJS service, which orchestrates AI capabilities for the AiToEarn platform. The service manages multi-provider AI integration, handles text/image/video generation requests, and provides HTTP endpoints for AI operations. 

For specific AI provider configuration details (API keys, model definitions), see [Multi-Provider Configuration](#3.2). For the autonomous AI agent implementation, see [All In Agent](#3.3).

This page covers:
- Service architecture and internal structure
- HTTP API endpoints and request handling
- Communication patterns with `aitoearn-server`
- Model selection and routing logic
- Deployment configuration

## Service Overview

The `aitoearn-ai` service is a standalone NestJS application that serves as the AI orchestration layer for the AiToEarn platform. It runs on port `3010` within the Docker network and is accessed internally by `aitoearn-server`.

### Architecture Position

```mermaid
graph TB
    subgraph "External AI Providers"
        OpenAI["OpenAI API<br/>GPT models"]
        Claude["Anthropic API<br/>Claude models"]
        Gemini["Google Vertex AI<br/>Gemini models"]
        Grok["xAI API<br/>Grok models"]
        Doubao["Volcengine API<br/>Doubao models"]
        AICSO["AICSO API"]
    end
    
    subgraph "AiToEarn Backend"
        Server["aitoearn-server<br/>:3002<br/>Main Backend API"]
        AI["aitoearn-ai<br/>:3010<br/>AI Orchestration Service"]
    end
    
    subgraph "Data Layer"
        MongoDB["MongoDB<br/>:27017"]
        Redis["Redis<br/>:6379"]
        S3["RustFS/S3<br/>Asset Storage"]
    end
    
    Server -->|"HTTP requests<br/>with INTERNAL_TOKEN"| AI
    
    AI -->|"API calls"| OpenAI
    AI -->|"API calls"| Claude
    AI -->|"API calls"| Gemini
    AI -->|"API calls"| Grok
    AI -->|"API calls"| Doubao
    AI -->|"API calls"| AICSO
    
    AI -->|"Store data"| MongoDB
    AI -->|"Cache/Queue"| Redis
    AI -->|"Upload assets"| S3
    
    Server -->|"Callback<br/>results"| Server
```

**Sources:** [docker-compose.yml:81-134](), [DOCKER_DEPLOYMENT_EN.md:13-26]()

### Key Characteristics

| Aspect | Details |
|--------|---------|
| **Technology Stack** | NestJS, TypeScript, Node.js |
| **Internal Port** | `3010` (not exposed externally) |
| **Health Check** | `GET /health` |
| **Authentication** | `INTERNAL_TOKEN` for inter-service communication |
| **Configuration** | Environment variables + `/app/config.js` |
| **Container Name** | `aitoearn-ai` |
| **Docker Network** | `aitoearn-network` |

**Sources:** [docker-compose.yml:81-134](), [DOCKER_DEPLOYMENT_EN.md:29-36]()

## Service Architecture

### NestJS Module Structure

The service is organized as a standard NestJS application with modules, controllers, and services handling different aspects of AI functionality.

```mermaid
graph TB
    subgraph "aitoearn-ai Service"
        Main["main.ts<br/>Bootstrap @ port 3010"]
        
        subgraph "HTTP Layer"
            Controllers["Controllers<br/>Handle HTTP requests"]
            Guards["Auth Guards<br/>Validate INTERNAL_TOKEN"]
        end
        
        subgraph "Business Logic"
            Services["AI Services<br/>Model selection & routing"]
            Providers["Provider Clients<br/>OpenAI, Claude, Gemini, etc."]
        end
        
        subgraph "Data Access"
            DB["MongoDB Client<br/>Store AI metadata"]
            Cache["Redis Client<br/>Queue/Cache"]
            Storage["S3 Client<br/>Upload generated assets"]
        end
        
        Config["config.js<br/>Configuration"]
    end
    
    Main --> Controllers
    Controllers --> Guards
    Guards --> Services
    Services --> Providers
    Services --> DB
    Services --> Cache
    Services --> Storage
    Config --> Services
    Config --> Providers
```

**Sources:** [docker-compose.yml:81-134](), [config/aitoearn-ai.config.js referenced in DOCKER_DEPLOYMENT_EN.md:98-110]()

### Configuration Loading

The service loads configuration from two sources:

1. **Environment Variables**: Set in `docker-compose.yml` environment section
2. **Configuration File**: Mounted at `/app/config.js` containing AI model definitions, storage endpoints, and service settings

```mermaid
graph LR
    EnvVars["Environment Variables<br/>docker-compose.yml"]
    ConfigFile["config.js<br/>Model definitions<br/>Storage config"]
    ProcessEnv["process.env<br/>Runtime variables"]
    
    EnvVars -->|"Docker container"| ProcessEnv
    ConfigFile -->|"Volume mount"| AppConfig["Application Config<br/>Merged configuration"]
    ProcessEnv --> AppConfig
    
    AppConfig --> Services["AI Services<br/>Use config"]
```

**Sources:** [docker-compose.yml:91-92](), [DOCKER_DEPLOYMENT_CN.md:96-111]()

## HTTP API Endpoints

The `aitoearn-ai` service exposes HTTP endpoints for AI operations. All requests must include the `INTERNAL_TOKEN` for authentication.

### Endpoint Categories

```mermaid
graph TB
    Client["aitoearn-server<br/>Caller"]
    
    subgraph "aitoearn-ai Endpoints"
        Health["GET /health<br/>Health check"]
        
        Text["Text Generation<br/>POST /ai/text/generate"]
        Image["Image Generation<br/>POST /ai/image/generate"]
        Video["Video Generation<br/>POST /ai/video/generate"]
        
        Models["GET /ai/models<br/>List available models"]
        Status["GET /ai/status<br/>Provider status"]
    end
    
    Client -->|"INTERNAL_TOKEN"| Health
    Client -->|"INTERNAL_TOKEN<br/>+ request body"| Text
    Client -->|"INTERNAL_TOKEN<br/>+ request body"| Image
    Client -->|"INTERNAL_TOKEN<br/>+ request body"| Video
    Client -->|"INTERNAL_TOKEN"| Models
    Client -->|"INTERNAL_TOKEN"| Status
```

### Request Authentication Flow

```mermaid
sequenceDiagram
    participant Server as aitoearn-server
    participant Guard as Auth Guard
    participant Controller as AI Controller
    participant Service as AI Service
    participant Provider as AI Provider
    
    Server->>Guard: HTTP Request with<br/>Header: INTERNAL_TOKEN
    
    alt Token valid
        Guard->>Controller: Allow request
        Controller->>Service: Process request<br/>(model, prompt, params)
        Service->>Service: Select provider<br/>based on model
        Service->>Provider: API call
        Provider-->>Service: AI response
        Service-->>Controller: Formatted result
        Controller-->>Server: HTTP 200<br/>JSON response
    else Token invalid
        Guard-->>Server: HTTP 401 Unauthorized
    end
```

**Sources:** [docker-compose.yml:109-110](), [docker-compose.yml:173-174]()

### Key Endpoint Patterns

| Endpoint | Method | Purpose | Authentication |
|----------|--------|---------|----------------|
| `/health` | GET | Container health check | None (public) |
| `/ai/text/generate` | POST | Generate text using AI models | INTERNAL_TOKEN required |
| `/ai/image/generate` | POST | Generate images | INTERNAL_TOKEN required |
| `/ai/video/generate` | POST | Generate videos | INTERNAL_TOKEN required |
| `/ai/models` | GET | List available models | INTERNAL_TOKEN required |

**Sources:** [docker-compose.yml:130-134]()

## Model Selection and Routing

The AI service implements routing logic to direct requests to the appropriate AI provider based on the requested model.

### Model Selection Flow

```mermaid
graph TB
    Request["Incoming Request<br/>model: 'gpt-4o'<br/>prompt: '...'"]
    
    Parse["Parse Request<br/>Extract model ID"]
    
    Lookup["Config Lookup<br/>Find provider for model"]
    
    Decision{"Model<br/>Found?"}
    
    subgraph "Provider Routing"
        OpenAIClient["OpenAI Client<br/>gpt-* models"]
        ClaudeClient["Claude Client<br/>claude-* models"]
        GeminiClient["Gemini Client<br/>gemini-* models"]
        GrokClient["Grok Client<br/>grok-* models"]
        DoubaoClient["Doubao Client<br/>ep-* models"]
    end
    
    Error["Return Error<br/>Model not found"]
    
    Response["Format Response<br/>Return to caller"]
    
    Request --> Parse
    Parse --> Lookup
    Lookup --> Decision
    
    Decision -->|"Yes"| OpenAIClient
    Decision -->|"Yes"| ClaudeClient
    Decision -->|"Yes"| GeminiClient
    Decision -->|"Yes"| GrokClient
    Decision -->|"Yes"| DoubaoClient
    
    Decision -->|"No"| Error
    
    OpenAIClient --> Response
    ClaudeClient --> Response
    GeminiClient --> Response
    GrokClient --> Response
    DoubaoClient --> Response
```

### Provider Configuration

The service reads provider credentials from environment variables:

| Provider | Environment Variables | Base URL Variable |
|----------|----------------------|-------------------|
| OpenAI | `OPENAI_API_KEY` | `OPENAI_BASE_URL` |
| Anthropic (Claude) | `ANTHROPIC_API_KEY` | `ANTHROPIC_BASE_URL` |
| Google (Gemini) | `GEMINI_KEY_PAIRS` (JSON) | N/A (uses Vertex AI) |
| xAI (Grok) | `GROK_API_KEY` | N/A |
| Volcengine (Doubao) | `VOLCENGINE_API_KEY`, `VOLCENGINE_ACCESS_KEY_ID`, `VOLCENGINE_SECRET_ACCESS_KEY` | N/A |
| AICSO | `AICSO_API_KEY` | `AICSO_BASE_URL` |

**Sources:** [docker-compose.yml:114-128](), [DOCKER_DEPLOYMENT_EN.md:222-240]()

## Communication with aitoearn-server

The AI service operates as a backend service that is called by `aitoearn-server`. Communication is synchronous HTTP-based.

### Service-to-Service Communication Pattern

```mermaid
sequenceDiagram
    participant User as User/Frontend
    participant Server as aitoearn-server<br/>:3002
    participant AI as aitoearn-ai<br/>:3010
    participant Provider as AI Provider<br/>(OpenAI/Claude/etc)
    participant Storage as RustFS/S3
    
    User->>Server: POST /api/content/generate<br/>JWT token
    Server->>Server: Validate user<br/>Check permissions
    
    Server->>AI: POST http://aitoearn-ai:3010/ai/text/generate<br/>Header: INTERNAL_TOKEN<br/>Body: {model, prompt, params}
    
    AI->>AI: Validate INTERNAL_TOKEN
    AI->>AI: Select provider<br/>based on model
    
    AI->>Provider: API request<br/>with provider credentials
    Provider-->>AI: AI response<br/>(text/image/video)
    
    alt Generated asset (image/video)
        AI->>Storage: Upload asset<br/>S3 API
        Storage-->>AI: Asset URL
    end
    
    AI->>AI: Store metadata<br/>in MongoDB
    AI-->>Server: HTTP 200<br/>{result, assetUrl}
    
    Server->>Server: Store result<br/>Associate with user
    Server-->>User: HTTP 200<br/>Generation result
```

**Sources:** [docker-compose.yml:112](), [docker-compose.yml:171](), [DOCKER_DEPLOYMENT_EN.md:155-161]()

### Internal Service URLs

| Direction | Environment Variable | Value | Purpose |
|-----------|---------------------|-------|---------|
| AI → Server | `SERVER_URL` | `http://aitoearn-server:3002` | Callback/webhook endpoints |
| Server → AI | `AI_URL` | `http://aitoearn-ai:3010` | AI request forwarding |

**Sources:** [docker-compose.yml:112](), [docker-compose.yml:171]()

### Authentication Mechanism

Both services share the same `INTERNAL_TOKEN` for mutual authentication:

```mermaid
graph LR
    ComposeFile["docker-compose.yml"]
    
    subgraph "aitoearn-ai"
        AIToken["INTERNAL_TOKEN<br/>Used to validate<br/>incoming requests"]
    end
    
    subgraph "aitoearn-server"
        ServerToken["INTERNAL_TOKEN<br/>Sent in request headers<br/>to aitoearn-ai"]
    end
    
    ComposeFile -->|"Set environment"| AIToken
    ComposeFile -->|"Set environment"| ServerToken
    
    ServerToken -->|"Must match"| AIToken
```

**Sources:** [docker-compose.yml:110](), [docker-compose.yml:174]()

## Data Management

The AI service interacts with three data storage systems:

### Storage Architecture

```mermaid
graph TB
    AI["aitoearn-ai<br/>Service"]
    
    subgraph "Data Stores"
        MongoDB["MongoDB<br/>mongodb:27017<br/>Database: aitoearn"]
        Redis["Redis<br/>redis:6379<br/>Password protected"]
        S3["RustFS/S3<br/>rustfs.local:9000<br/>Bucket: aitoearn"]
    end
    
    AI -->|"Store AI request metadata<br/>Generation history<br/>Model usage stats"| MongoDB
    
    AI -->|"Cache model lists<br/>Queue generation jobs<br/>Rate limiting data"| Redis
    
    AI -->|"Upload generated images<br/>Upload generated videos<br/>S3 API protocol"| S3
    
    S3 -->|"Return asset URLs"| AI
```

### MongoDB Usage

The AI service uses MongoDB to store:
- AI generation request history
- Model usage statistics
- User quota tracking
- Generation metadata

**Connection details from environment:**
- Host: `MONGODB_HOST=mongodb`
- Port: `MONGODB_PORT=27017`
- Username: `MONGODB_USERNAME=admin`
- Password: `MONGODB_PASSWORD` (configured in compose)
- Database: `aitoearn` (default)

**Sources:** [docker-compose.yml:100-103](), [DOCKER_DEPLOYMENT_EN.md:298-309]()

### Redis Usage

Redis is used for:
- Caching model availability
- Job queue for async operations
- Rate limiting per user/model
- Distributed locks (via Redlock)

**Connection details:**
- Host: `REDIS_HOST=redis`
- Port: `REDIS_PORT=6379`
- Password: `REDIS_PASSWORD` (configured in compose)

**Sources:** [docker-compose.yml:105-107](), [DOCKER_DEPLOYMENT_EN.md:298-309]()

### Asset Storage (RustFS/S3)

Generated images and videos are uploaded to S3-compatible storage:

```mermaid
graph LR
    Generate["Generate Image/Video"]
    Save["Save to local temp"]
    Upload["Upload to S3<br/>using assets config"]
    URL["Get public URL"]
    Cleanup["Delete local temp"]
    Return["Return URL to caller"]
    
    Generate --> Save
    Save --> Upload
    Upload --> URL
    URL --> Cleanup
    Cleanup --> Return
```

**Storage configuration** is loaded from `config.js` and includes:
- Provider: `s3` or `rustfs`
- Endpoint: `http://rustfs.local:9000` (internal) or external S3
- Bucket: `aitoearn`
- Credentials: `accessKeyId` and `secretAccessKey`

**Sources:** [DOCKER_DEPLOYMENT_EN.md:173-202](), [config/aitoearn-ai.config.js referenced in docker-compose.yml:91]()

## Deployment and Containerization

### Docker Service Definition

The `aitoearn-ai` service is defined in Docker Compose with the following characteristics:

```yaml
# Simplified view of docker-compose.yml
aitoearn-ai:
  image: aitoearn/aitoearn-ai:latest
  container_name: aitoearn-ai
  restart: unless-stopped
  ports: [] # No external ports exposed
  networks:
    - aitoearn-network
  depends_on:
    - mongodb (healthy)
    - redis (healthy)
  volumes:
    - ./config/aitoearn-ai.config.js:/app/config.js:ro
    - ./config/gcs-placeholder.json:/app/config/gcs-placeholder.json:ro
  environment:
    - NODE_ENV=production
    - APP_ENV=production
    - APP_NAME=aitoearn-ai
    # ... MongoDB, Redis, AI provider credentials
```

**Sources:** [docker-compose.yml:81-134]()

### Service Dependencies

```mermaid
graph TB
    MongoDB["MongoDB<br/>Health check:<br/>mongosh ping"]
    Redis["Redis<br/>Health check:<br/>redis-cli incr ping"]
    
    AI["aitoearn-ai<br/>Health check:<br/>GET /health"]
    
    Server["aitoearn-server<br/>Depends on AI"]
    
    MongoDB -->|"service_healthy"| AI
    Redis -->|"service_healthy"| AI
    AI -->|"service_healthy"| Server
```

The service will not start until MongoDB and Redis are healthy, ensuring database connections are available on startup.

**Sources:** [docker-compose.yml:86-89](), [docker-compose.yml:145-146]()

### Health Check Configuration

The container health check ensures the service is ready to accept requests:

```yaml
healthcheck:
  test: ["CMD", "node", "-e", 
    "require('http').get('http://localhost:3010/health', 
      (r) => { process.exit(r.statusCode === 200 ? 0 : 1) })"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 60s
```

**Sources:** [docker-compose.yml:129-134]()

### Volume Mounts

| Host Path | Container Path | Mode | Purpose |
|-----------|---------------|------|---------|
| `./config/aitoearn-ai.config.js` | `/app/config.js` | Read-only | AI service configuration |
| `./config/gcs-placeholder.json` | `/app/config/gcs-placeholder.json` | Read-only | Google Cloud credentials |

Configuration files are mounted as read-only volumes. Changes require container restart.

**Sources:** [docker-compose.yml:91-92]()

### Network Configuration

The service communicates on the `aitoearn-network` Docker bridge network:

```mermaid
graph TB
    subgraph "aitoearn-network (Bridge)"
        Nginx["nginx<br/>aitoearn-nginx"]
        Web["aitoearn-web"]
        Server["aitoearn-server<br/>aitoearn-server:3002"]
        AI["aitoearn-ai<br/>aitoearn-ai:3010"]
        MongoDB["mongodb<br/>mongodb:27017"]
        Redis["redis<br/>redis:6379"]
        RustFS["rustfs<br/>rustfs.local:9000"]
    end
    
    Nginx -->|"HTTP"| Web
    Nginx -->|"HTTP proxy"| Server
    Server -->|"HTTP"| AI
    AI --> MongoDB
    AI --> Redis
    AI --> RustFS
```

**Internal DNS resolution:**
- `aitoearn-ai` resolves to the AI container
- `mongodb` resolves to the MongoDB container
- `redis` resolves to the Redis container
- `rustfs.local` resolves to the RustFS container

**Sources:** [docker-compose.yml:93-94](), [docker-compose.yml:272-275]()

### Environment Variable Categories

The service requires environment variables in several categories:

| Category | Variables | Purpose |
|----------|-----------|---------|
| **Node.js** | `NODE_ENV`, `APP_ENV`, `APP_NAME` | Runtime environment |
| **Database** | `MONGODB_HOST`, `MONGODB_PORT`, `MONGODB_USERNAME`, `MONGODB_PASSWORD` | MongoDB connection |
| **Cache** | `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD` | Redis connection |
| **Authentication** | `JWT_SECRET`, `INTERNAL_TOKEN` | Service authentication |
| **OpenAI** | `OPENAI_API_KEY`, `OPENAI_BASE_URL` | OpenAI integration |
| **Anthropic** | `ANTHROPIC_API_KEY`, `ANTHROPIC_BASE_URL` | Claude integration |
| **Google** | `GEMINI_KEY_PAIRS`, `GEMINI_LOCATION` | Gemini integration |
| **Volcengine** | `VOLCENGINE_API_KEY`, `VOLCENGINE_ACCESS_KEY_ID`, `VOLCENGINE_SECRET_ACCESS_KEY`, `VOLCENGINE_VOD_SPACE_NAME` | Doubao integration |
| **xAI** | `GROK_API_KEY` | Grok integration |
| **AICSO** | `AICSO_API_KEY`, `AICSO_BASE_URL` | AICSO integration |
| **Proxy** | `AI_PROXY_URL` | Optional HTTP proxy for AI APIs |
| **Service Communication** | `SERVER_URL` | URL to reach aitoearn-server |

**Sources:** [docker-compose.yml:95-128]()

### Startup Sequence

```mermaid
sequenceDiagram
    participant Compose as Docker Compose
    participant MongoDB
    participant Redis
    participant AI as aitoearn-ai
    participant Server as aitoearn-server
    
    Compose->>MongoDB: Start container
    Compose->>Redis: Start container
    
    MongoDB->>MongoDB: Wait for ready<br/>Health check passes
    Redis->>Redis: Wait for ready<br/>Health check passes
    
    Compose->>AI: Start container<br/>(after deps healthy)
    AI->>AI: Load config.js
    AI->>MongoDB: Connect to DB
    AI->>Redis: Connect to cache
    AI->>AI: Initialize AI clients
    AI->>AI: Start HTTP server :3010
    AI->>AI: Health check passes
    
    Compose->>Server: Start container<br/>(after AI healthy)
    Server->>AI: Verify connectivity
```

**Sources:** [docker-compose.yml:86-89](), [docker-compose.yml:145-146]()

## Configuration File Structure

The `/app/config.js` file mounted into the container defines:

### Model Definitions

The configuration includes arrays of available models for each provider:

```javascript
// Example structure (not actual code)
{
  aiModels: {
    openai: [
      { id: 'gpt-4o', name: 'GPT-4 Omni', pricing: {...} },
      { id: 'gpt-4-turbo', name: 'GPT-4 Turbo', pricing: {...} },
      // ...
    ],
    claude: [
      { id: 'claude-opus-4.5', name: 'Claude Opus 4.5', pricing: {...} },
      // ...
    ],
    // ... other providers
  }
}
```

### Storage Configuration

Defines how to access the asset storage system:

```javascript
// Example structure
{
  assets: {
    provider: 's3',
    endpoint: 'http://rustfs.local:9000',
    region: 'us-east-1',
    bucketName: 'aitoearn',
    accessKeyId: process.env.RUSTFS_ACCESS_KEY || 'rustfsadmin',
    secretAccessKey: process.env.RUSTFS_SECRET_KEY || 'rustfsadmin',
    cdnEndpoint: null
  }
}
```

**Sources:** [DOCKER_DEPLOYMENT_EN.md:98-110](), [DOCKER_DEPLOYMENT_CN.md:96-111]()

### Service Configuration

Additional settings for logging, database connections, and service behavior are defined in the config file, reading from `process.env` where appropriate.

**Sources:** [config/aitoearn-ai.config.js referenced in DOCKER_DEPLOYMENT_CN.md:286-323]()

---

# Page: Multi-Provider Configuration

# Multi-Provider Configuration

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



## Purpose and Scope

This document explains how to configure multiple AI providers in the AiToEarn platform. It covers environment variable setup, configuration file structure, model definitions, and the recommended use of API relay services to manage multiple AI backends through a unified interface.

For information about the overall AI system architecture and how AI services communicate with the backend, see [AI Service Architecture](#3.1). For details about the autonomous AI agent implementation, see [All In Agent](#3.3).

---

## Overview

AiToEarn supports six AI providers simultaneously, enabling the platform to leverage multiple models for different use cases. The multi-provider architecture consists of:

- **Environment variables** for API credentials and endpoints
- **Configuration files** defining available models, pricing, and capabilities
- **Optional API proxy/relay** for unified model access
- **Service-specific provider usage** (aitoearn-ai vs aitoearn-server)

**Sources:** [README.md:115-119](), [docker-compose.yml:114-128](), [DOCKER_DEPLOYMENT_EN.md:206-247]()

---

## Configuration Architecture

```mermaid
graph TB
    subgraph "Configuration Sources"
        ENV["docker-compose.yml<br/>Environment Variables"]
        CONFIG_AI["config/aitoearn-ai.config.js"]
        CONFIG_SERVER["config/aitoearn-server.config.js"]
        GCS_FILE["config/gcs-placeholder.json<br/>Gemini Credentials"]
    end
    
    subgraph "Runtime Services"
        AI_SERVICE["aitoearn-ai:3010<br/>NestJS Service"]
        SERVER_SERVICE["aitoearn-server:3002<br/>NestJS Service"]
    end
    
    subgraph "AI Providers"
        OPENAI["OpenAI API<br/>api.openai.com/v1"]
        ANTHROPIC["Anthropic API<br/>api.anthropic.com"]
        GEMINI["Google Gemini API<br/>Vertex AI"]
        GROK["xAI Grok API<br/>api.x.ai"]
        VOLCENGINE["Volcengine API<br/>Doubao Models"]
        AICSO["AICSO API"]
        RELAY["Optional Relay Service<br/>new-api / one-api"]
    end
    
    ENV -->|"Mounted as process.env"| AI_SERVICE
    ENV -->|"Mounted as process.env"| SERVER_SERVICE
    CONFIG_AI -->|"/app/config.js"| AI_SERVICE
    CONFIG_SERVER -->|"/app/config.js"| SERVER_SERVICE
    GCS_FILE -->|"Gemini keyFile"| AI_SERVICE
    
    AI_SERVICE -->|"OPENAI_API_KEY<br/>ANTHROPIC_API_KEY<br/>GEMINI_KEY_PAIRS<br/>etc."| RELAY
    AI_SERVICE -->|"Direct Access"| OPENAI
    AI_SERVICE -->|"Direct Access"| ANTHROPIC
    AI_SERVICE -->|"Direct Access"| GEMINI
    AI_SERVICE -->|"Direct Access"| GROK
    AI_SERVICE -->|"Direct Access"| VOLCENGINE
    AI_SERVICE -->|"Direct Access"| AICSO
    
    SERVER_SERVICE -->|"OPENAI_API_KEY only"| RELAY
    SERVER_SERVICE -->|"Direct Access"| OPENAI
    
    RELAY -.->|"Unified Interface"| OPENAI
    RELAY -.->|"Unified Interface"| ANTHROPIC
    RELAY -.->|"Unified Interface"| GEMINI
    RELAY -.->|"Unified Interface"| GROK
```

**Diagram: Multi-Provider Configuration Flow**

The configuration flows from `docker-compose.yml` environment variables through mounted config files to the runtime services, which then connect to AI providers either directly or through an optional relay service.

**Sources:** [docker-compose.yml:81-134](), [docker-compose.yml:136-232](), [DOCKER_DEPLOYMENT_EN.md:98-110]()

---

## Supported AI Providers

| Provider | Service | Models | Environment Variables Required |
|----------|---------|--------|-------------------------------|
| **OpenAI** | GPT models | GPT-4, GPT-3.5, etc. | `OPENAI_API_KEY`, `OPENAI_BASE_URL` |
| **Anthropic** | Claude models | Claude Opus 4.5/4.6, Sonnet, etc. | `ANTHROPIC_API_KEY`, `ANTHROPIC_BASE_URL` |
| **Google Gemini** | Gemini models | Gemini 2.5, 3.1 | `GEMINI_KEY_PAIRS`, `GEMINI_LOCATION` |
| **xAI** | Grok models | Grok | `GROK_API_KEY` |
| **Volcengine** | Doubao models | Doubao (豆包) | `VOLCENGINE_API_KEY`, `VOLCENGINE_ACCESS_KEY_ID`, `VOLCENGINE_SECRET_ACCESS_KEY`, `VOLCENGINE_VOD_SPACE_NAME` |
| **AICSO** | AICSO models | Custom models | `AICSO_API_KEY`, `AICSO_BASE_URL` |

**Sources:** [README.md:115-119](), [DOCKER_DEPLOYMENT_EN.md:222-240]()

---

## Environment Variable Configuration

### Core AI Provider Variables

All AI provider credentials are configured as environment variables in the `aitoearn-ai` service within [docker-compose.yml:81-134]().

```yaml
# OpenAI Configuration (used by both aitoearn-ai and aitoearn-server)
OPENAI_API_KEY: sk-placeholder
OPENAI_BASE_URL: https://api.openai.com/v1

# Anthropic Claude Configuration
ANTHROPIC_API_KEY: sk-placeholder
ANTHROPIC_BASE_URL: https://api.anthropic.com

# Volcengine (Doubao) Configuration
VOLCENGINE_API_KEY: ""
VOLCENGINE_ACCESS_KEY_ID: ""
VOLCENGINE_SECRET_ACCESS_KEY: ""
VOLCENGINE_VOD_SPACE_NAME: ""

# xAI Grok Configuration
GROK_API_KEY: ""

# AICSO Configuration
AICSO_API_KEY: ""
AICSO_BASE_URL: ""

# Google Gemini Configuration (JSON array format)
GEMINI_KEY_PAIRS: '[{"projectId":"placeholder","apiKey":"placeholder","keyFile":"/app/config/gcs-placeholder.json","bucket":"placeholder"}]'
GEMINI_LOCATION: us-central1

# Optional AI Proxy
AI_PROXY_URL: ""
```

**Sources:** [docker-compose.yml:114-128](), [DOCKER_DEPLOYMENT_EN.md:222-240]()

### Gemini Key Pairs Format

The `GEMINI_KEY_PAIRS` variable accepts a JSON array of credential objects:

```json
[
  {
    "projectId": "your-gcp-project-id",
    "apiKey": "your-gemini-api-key",
    "keyFile": "/app/config/gcs-placeholder.json",
    "bucket": "your-gcs-bucket"
  }
]
```

Each object represents a separate Google Cloud project with Vertex AI enabled. Multiple projects can be configured for load balancing or quota management.

**Sources:** [DOCKER_DEPLOYMENT_EN.md:242-247](), [docker-compose.yml:126]()

### Service-Specific Provider Usage

```mermaid
graph LR
    subgraph "aitoearn-ai Service"
        AI_ALL["All 6 Providers<br/>OpenAI, Anthropic, Gemini,<br/>Grok, Volcengine, AICSO"]
    end
    
    subgraph "aitoearn-server Service"
        SERVER_OPENAI["OpenAI Only<br/>Limited AI Features"]
    end
    
    AI_ALL -->|"Primary AI Engine"| CONTENT_GEN["Content Generation<br/>Image Generation<br/>Video Generation"]
    SERVER_OPENAI -->|"Supplementary Features"| SIMPLE_AI["Simple AI Tasks<br/>Text Processing"]
```

**Diagram: Provider Usage by Service**

The `aitoearn-ai` service uses all six AI providers for comprehensive content generation, while `aitoearn-server` only uses OpenAI for simpler tasks.

**Sources:** [docker-compose.yml:114-128](), [docker-compose.yml:179-181]()

---

## API Proxy and Relay Services

### Recommended Approach: Using API Relay

The deployment guides strongly recommend using an API relay service like **new-api** or **one-api** to manage all AI providers through a single endpoint.

**Benefits:**
- Single API key and endpoint for all models
- Centralized quota and billing management
- Load balancing and failover
- Model switching without application reconfiguration

**Popular Relay Services:**
- [new-api](https://github.com/Calcium-Ion/new-api) - Multi-model API relay
- [one-api](https://github.com/songquanpeng/one-api) - OpenAI API management system

**Sources:** [DOCKER_DEPLOYMENT_EN.md:206-211]()

### Relay Service Configuration

After deploying a relay service, configure both the `aitoearn-ai` and `aitoearn-server` services:

```yaml
# In docker-compose.yml for both services
OPENAI_BASE_URL: https://your-new-api-host/v1
OPENAI_API_KEY: sk-your-new-api-key
```

The relay service then handles routing requests to the appropriate underlying provider (OpenAI, Claude, Gemini, etc.) based on the model name in the request.

**Sources:** [DOCKER_DEPLOYMENT_EN.md:213-218]()

### AI Proxy URL

The `AI_PROXY_URL` environment variable provides an additional layer of proxying for direct AI API calls:

```yaml
AI_PROXY_URL: "http://your-proxy-server:port"
```

This is useful for:
- Routing traffic through a corporate proxy
- Adding custom request/response logging
- Implementing regional restrictions

**Sources:** [docker-compose.yml:128](), [DOCKER_DEPLOYMENT_EN.md:239]()

---

## Configuration Files Structure

### Config File Mounting

Configuration files are mounted as read-only volumes into the services:

| File | Mounted To | Purpose |
|------|------------|---------|
| `config/aitoearn-ai.config.js` | `aitoearn-ai:/app/config.js` | AI model definitions, pricing, capabilities |
| `config/aitoearn-server.config.js` | `aitoearn-server:/app/config.js` | Backend configuration including OAuth |
| `config/gcs-placeholder.json` | `aitoearn-ai:/app/config/gcs-placeholder.json` | Google Cloud service account credentials |

**Sources:** [docker-compose.yml:90-92](), [docker-compose.yml:147-148](), [DOCKER_DEPLOYMENT_EN.md:98-110]()

### Model Definitions in config.js

The `config/aitoearn-ai.config.js` file contains model definitions that specify:

- Available models from each provider
- Model capabilities (text, image, video generation)
- Pricing information
- Model-specific parameters

```mermaid
graph TB
    CONFIG["config/aitoearn-ai.config.js"]
    
    CONFIG --> MODELS["models: {<br/>  provider: 'openai',<br/>  name: 'gpt-4',<br/>  capabilities: [...],<br/>  pricing: {...}<br/>}"]
    
    CONFIG --> PROVIDERS["providers: {<br/>  openai: {...},<br/>  anthropic: {...},<br/>  gemini: {...}<br/>}"]
    
    CONFIG --> ASSETS["assets: {<br/>  provider: 's3',<br/>  endpoint: 'http://rustfs.local:9000',<br/>  credentials: {...}<br/>}"]
    
    MODELS --> RUNTIME["Runtime Model Selection<br/>Based on User Request"]
    PROVIDERS --> AUTH["Provider Authentication<br/>API Key Management"]
    ASSETS --> STORAGE["Generated Asset Storage<br/>Images, Videos, etc."]
```

**Diagram: aitoearn-ai.config.js Structure**

**Sources:** [DOCKER_DEPLOYMENT_EN.md:286-362]()

### Environment Variable Integration

Configuration files read environment variables set in `docker-compose.yml`:

```javascript
// Example from config/aitoearn-ai.config.js
module.exports = {
  redis: {
    host: process.env.REDIS_HOST,
    port: parseInt(process.env.REDIS_PORT),
    password: process.env.REDIS_PASSWORD,
  },
  
  auth: {
    secret: process.env.JWT_SECRET,
    internalToken: process.env.INTERNAL_TOKEN,
  },
  
  // AI provider configs read from environment
  openai: {
    apiKey: process.env.OPENAI_API_KEY,
    baseUrl: process.env.OPENAI_BASE_URL,
  },
  
  // Model definitions are hardcoded in config
  models: [
    {
      provider: 'openai',
      name: 'gpt-4',
      // ...
    }
  ]
}
```

**Sources:** [DOCKER_DEPLOYMENT_EN.md:286-362]()

---

## Placeholder vs Production Configuration

### Default Placeholder Values

The default `docker-compose.yml` contains placeholder values that allow the application to start without errors:

```yaml
OPENAI_API_KEY: sk-placeholder
ANTHROPIC_API_KEY: sk-placeholder
GEMINI_KEY_PAIRS: '[{"projectId":"placeholder","apiKey":"placeholder",...}]'
```

**Behavior with placeholders:**
- Services start successfully
- Health checks pass
- AI features return errors at runtime when actually invoked
- Users see error messages indicating missing API keys

**Sources:** [docker-compose.yml:115](), [docker-compose.yml:117](), [DOCKER_DEPLOYMENT_EN.md:220]()

### Production Configuration Steps

1. **Obtain API keys** from each provider's developer portal
2. **Update docker-compose.yml** with real credentials
3. **Configure relay service** (recommended) or use direct provider access
4. **Update config files** if using non-default models
5. **Restart services** to apply changes:

```bash
docker compose down
docker compose up -d
```

**Sources:** [DOCKER_DEPLOYMENT_EN.md:206-247]()

---

## Provider-Specific Configuration Details

### OpenAI Configuration

Used by both `aitoearn-ai` and `aitoearn-server` services.

```yaml
# In aitoearn-ai service
OPENAI_API_KEY: sk-your-key
OPENAI_BASE_URL: https://api.openai.com/v1

# In aitoearn-server service (duplicate required)
OPENAI_API_KEY: sk-your-key
OPENAI_BASE_URL: https://api.openai.com/v1
```

**Why duplicated:** Both services make independent OpenAI API calls for different features.

**Sources:** [docker-compose.yml:115-116](), [docker-compose.yml:180-181]()

### Anthropic (Claude) Configuration

Only used by `aitoearn-ai` service.

```yaml
ANTHROPIC_API_KEY: sk-ant-your-key
ANTHROPIC_BASE_URL: https://api.anthropic.com
```

**Default base URL** is `https://api.anthropic.com` and typically doesn't need modification unless using a proxy.

**Sources:** [docker-compose.yml:117-118]()

### Volcengine (Doubao) Configuration

Requires multiple credentials for full functionality:

```yaml
VOLCENGINE_API_KEY: "your-api-key"
VOLCENGINE_ACCESS_KEY_ID: "your-access-key-id"
VOLCENGINE_SECRET_ACCESS_KEY: "your-secret-access-key"
VOLCENGINE_VOD_SPACE_NAME: "your-vod-space"
```

- **API Key**: For Doubao model API access
- **Access Key ID/Secret**: For Volcengine cloud services
- **VOD Space Name**: For video-on-demand storage

**Sources:** [docker-compose.yml:119-122](), [DOCKER_DEPLOYMENT_EN.md:232]()

### Gemini Configuration

Requires Google Cloud project setup with Vertex AI enabled:

```yaml
GEMINI_KEY_PAIRS: '[{
  "projectId": "your-gcp-project-id",
  "apiKey": "your-gemini-api-key",
  "keyFile": "/app/config/gcs-placeholder.json",
  "bucket": "your-gcs-bucket"
}]'
GEMINI_LOCATION: us-central1
```

**Key file setup:**
1. Create a Google Cloud service account
2. Download the JSON credentials file
3. Replace `config/gcs-placeholder.json` with the real credentials
4. Update the `keyFile` path in `GEMINI_KEY_PAIRS`

**Sources:** [docker-compose.yml:126-127](), [DOCKER_DEPLOYMENT_EN.md:242-247]()

### Grok Configuration

Simplest configuration - only requires API key:

```yaml
GROK_API_KEY: "your-grok-api-key"
```

Obtain from [xAI Developer Console](https://console.x.ai).

**Sources:** [docker-compose.yml:123](), [DOCKER_DEPLOYMENT_EN.md:234]()

### AICSO Configuration

Requires both API key and base URL:

```yaml
AICSO_API_KEY: "your-aicso-key"
AICSO_BASE_URL: "https://api.aicso.com"
```

**Sources:** [docker-compose.yml:124-125](), [DOCKER_DEPLOYMENT_EN.md:235-236]()

---

## Configuration Validation

```mermaid
sequenceDiagram
    participant DC as docker-compose.yml
    participant ENV as Process Environment
    participant CONFIG as config.js
    participant SERVICE as aitoearn-ai Service
    participant HEALTH as Health Check
    participant PROVIDER as AI Provider
    
    DC->>ENV: Set environment variables
    CONFIG->>ENV: Read process.env values
    SERVICE->>CONFIG: Load configuration
    SERVICE->>SERVICE: Validate required fields
    HEALTH->>SERVICE: GET /health
    SERVICE->>HEALTH: 200 OK (even with placeholders)
    
    Note over SERVICE,PROVIDER: Runtime - User Request
    SERVICE->>CONFIG: Get provider credentials
    CONFIG->>SERVICE: Return API key
    SERVICE->>PROVIDER: API call with credentials
    
    alt Valid Credentials
        PROVIDER->>SERVICE: Success response
    else Invalid/Placeholder Credentials
        PROVIDER->>SERVICE: 401 Unauthorized
        SERVICE->>SERVICE: Log error
        SERVICE-->>User: Error: Invalid API key
    end
```

**Diagram: Configuration Validation Flow**

The system validates configuration at multiple stages:
- **Startup**: Basic format validation
- **Health check**: Service connectivity (passes with placeholders)
- **Runtime**: Actual API call validation (fails with placeholders)

**Sources:** [docker-compose.yml:129-134]()

---

## Troubleshooting

### Common Configuration Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| **Missing API Key** | Runtime errors: "Invalid API key" | Add real key to `docker-compose.yml`, restart service |
| **Mismatched Passwords** | Service startup fails, health check fails | Ensure MongoDB/Redis passwords match across all services |
| **Invalid GEMINI_KEY_PAIRS** | JSON parse error on startup | Validate JSON syntax, ensure proper escaping |
| **Wrong Base URL** | Connection timeout or 404 errors | Verify provider endpoint, check for typos |
| **Stale Configuration** | Changes not taking effect | Run `docker compose down && docker compose up -d` |

**Sources:** [DOCKER_DEPLOYMENT_EN.md:206-247]()

### Verifying Provider Configuration

Check service logs to verify provider initialization:

```bash
# View aitoearn-ai logs
docker logs aitoearn-ai

# Look for provider initialization messages
# Should see: "OpenAI provider initialized"
# Should see: "Anthropic provider initialized"
# etc.
```

**Sources:** [DOCKER_DEPLOYMENT_EN.md:122-125]()

---

## Related Configuration

- **OAuth Platform Configuration**: See [DOCKER_DEPLOYMENT_EN.md:249-270]() for third-party platform credentials
- **Storage Configuration**: RustFS and S3 setup is documented in [Storage and Database Setup](#7.3)
- **Email Configuration**: SMTP credentials in [DOCKER_DEPLOYMENT_EN.md:275-278]()

**Sources:** [DOCKER_DEPLOYMENT_EN.md:249-281]()

---

# Page: All In Agent

# All In Agent

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



## Purpose and Scope

This document describes the **All In Agent**, an autonomous AI agent introduced in AiToEarn v1.4.3 that can automatically generate content, publish to multiple platforms, and assist users in operating the AiToEarn platform. For information about the AI service infrastructure that powers the agent, see [AI Service Architecture](#3.1). For multi-provider AI configuration details, see [Multi-Provider Configuration](#3.2).

The All In Agent represents the highest level of automation in AiToEarn, combining content creation, platform publishing, and operational assistance into a unified intelligent system.

**Sources:** [README.md:33](), [README.md:71-76](), [README_CN.md:32](), [README_CN.md:58-64]()

## Overview

The All In Agent is an autonomous AI-powered system that operates within the AiToEarn platform to:

1. **Automatically generate content** - Creates text, images, and video content using multiple AI providers
2. **Automatically publish content** - Distributes generated content across 14+ social media platforms
3. **Assist platform operation** - Provides intelligent recommendations and automation for user workflows

This feature was introduced in December 2024 (v1.4.3) and represents a significant step toward fully autonomous content marketing operations.

**Key Capabilities:**
- Autonomous content generation without manual intervention
- Multi-platform content distribution with intelligent scheduling
- User workflow assistance and smart recommendations
- Integration with hotspot analysis for trending content
- Coordination across the entire content lifecycle (creation → publishing → engagement)

**Sources:** [README.md:30-33](), [README.md:66-77](), [README_CN.md:28-32]()

## System Architecture

### Position in Overall Architecture

The All In Agent sits at the intersection of multiple functional domains within AiToEarn:

```mermaid
graph TB
    subgraph "Intelligence Layer"
        AllInAgent["All In Agent<br/>Autonomous Operation<br/>Smart Recommendations"]
        HotspotAnalysis["Hotspot Analysis<br/>Trend Detection"]
        SearchAssist["Search Assistant<br/>Content Discovery"]
    end
    
    subgraph "Content Management"
        Creation["Content Creation<br/>AI Generation"]
        Publishing["Multi-Platform Publishing<br/>Scheduling"]
        Drafts["Draft Management"]
    end
    
    subgraph "Engagement"
        EngagementEngine["Engagement Engine<br/>Auto Comments"]
        Analytics["Analytics Dashboard"]
    end
    
    subgraph "Platform Integration"
        OAuth["OAuth Management<br/>14 Platforms"]
        APIGateway["API Gateway"]
    end
    
    AllInAgent --> Creation
    AllInAgent --> Publishing
    AllInAgent --> EngagementEngine
    HotspotAnalysis --> AllInAgent
    SearchAssist --> AllInAgent
    
    Creation --> Drafts
    Publishing --> OAuth
    Publishing --> APIGateway
    EngagementEngine --> OAuth
    
    Analytics -.->|"Feedback"| AllInAgent
```

**Agent Decision Flow**

The All In Agent operates through a coordinated workflow:

**Sources:** Based on architectural diagrams provided in system overview

### Service-Level Architecture

The All In Agent functionality is distributed across the AiToEarn microservices architecture:

```mermaid
graph TB
    subgraph "Docker Services"
        Web["aitoearn-web<br/>:3000<br/>User Interface"]
        Server["aitoearn-server<br/>:3002<br/>Orchestration Logic"]
        AI["aitoearn-ai<br/>:3010<br/>AI Model Inference"]
    end
    
    subgraph "Data Layer"
        MongoDB[("MongoDB<br/>:27017<br/>Agent State & History")]
        Redis[("Redis<br/>:6379<br/>Job Queue & Cache")]
        RustFS[("RustFS<br/>:9000<br/>Generated Assets")]
    end
    
    subgraph "External Services"
        AIProviders["AI Providers<br/>OpenAI, Claude, Gemini, etc."]
        SocialPlatforms["Social Media APIs<br/>TikTok, YouTube, etc."]
    end
    
    Web -->|"Agent Commands"| Server
    Server -->|"Content Generation"| AI
    Server -->|"State Management"| MongoDB
    Server -->|"Task Queue"| Redis
    
    AI -->|"Model Calls"| AIProviders
    AI -->|"Store Assets"| RustFS
    
    Server -->|"Publish Content"| SocialPlatforms
    Server -->|"Retrieve Trends"| SocialPlatforms
```

**Service Responsibilities:**

| Service | Agent Responsibilities |
|---------|----------------------|
| `aitoearn-web` | Agent UI, command input, status display |
| `aitoearn-server` | Agent orchestration, workflow logic, platform publishing |
| `aitoearn-ai` | AI model selection, content generation, asset creation |
| `MongoDB` | Agent configuration, execution history, content drafts |
| `Redis` | Task queuing, scheduled operations, job status |
| `RustFS` | Generated images, videos, documents |

**Sources:** [docker-compose.yml:81-134](), [docker-compose.yml:136-232](), [docker-compose.yml:234-246]()

### Agent Workflow

The All In Agent executes content operations through multiple phases:

```mermaid
flowchart TB
    Start([User Activates Agent])
    
    Start --> AnalyzeTrends["1. Analyze Trends<br/>Hotspot Analysis API<br/>Fetch trending topics"]
    
    AnalyzeTrends --> SelectTopic["2. Select Topic<br/>AI-powered topic selection<br/>Based on engagement metrics"]
    
    SelectTopic --> GenerateContent["3. Generate Content<br/>aitoearn-ai service<br/>Multi-provider generation"]
    
    GenerateContent --> ContentType{Content Type?}
    
    ContentType -->|Text| TextGen["Text Generation<br/>GPT/Claude/Gemini"]
    ContentType -->|Image| ImageGen["Image Generation<br/>DALL-E/Flux"]
    ContentType -->|Video| VideoGen["Video Generation<br/>Seedance/Kling/Runway"]
    
    TextGen --> OptimizeContent
    ImageGen --> StoreAssets["Store to RustFS<br/>S3-compatible storage"]
    VideoGen --> StoreAssets
    
    StoreAssets --> OptimizeContent["4. Optimize Content<br/>Apply hotspot insights<br/>Platform-specific formatting"]
    
    OptimizeContent --> CreateDraft["5. Create Draft<br/>Store in MongoDB<br/>draft collection"]
    
    CreateDraft --> ReviewDecision{Auto-Publish<br/>Enabled?}
    
    ReviewDecision -->|Yes| SchedulePublish["6. Schedule Publishing<br/>Redis job queue<br/>Calendar timing"]
    ReviewDecision -->|No| NotifyUser["Notify User<br/>Draft ready for review"]
    
    SchedulePublish --> MultiPlatform["7. Multi-Platform Publish<br/>OAuth-authenticated APIs<br/>TikTok, YouTube, etc."]
    
    MultiPlatform --> TrackMetrics["8. Track Metrics<br/>Store to statistics DB<br/>MongoDB analytics"]
    
    TrackMetrics --> EngageAuto["9. Auto-Engagement<br/>Scheduled comments<br/>Interaction monitoring"]
    
    EngageAuto --> CollectFeedback["10. Collect Feedback<br/>Performance data<br/>Learn for next cycle"]
    
    CollectFeedback --> End([Agent Cycle Complete])
    NotifyUser --> End
```

**Sources:** Based on content workflow diagram in system overview, [README.md:141-149]()

## Component Interactions

### AI Model Selection

The All In Agent leverages the multi-provider AI system to select optimal models for different content types:

```mermaid
graph LR
    Agent["All In Agent"]
    
    subgraph "AI Model Router"
        ModelSelector["Model Selection Logic<br/>aitoearn-ai service"]
    end
    
    subgraph "Text Models"
        GPT["GPT-4/5<br/>OpenAI"]
        Claude["Claude Opus 4.5/4.6<br/>Anthropic"]
        Gemini["Gemini 2.5/3.1<br/>Google"]
        Grok["Grok<br/>xAI"]
    end
    
    subgraph "Image Models"
        DALLE["DALL-E<br/>OpenAI"]
        Flux["Flux<br/>Various"]
    end
    
    subgraph "Video Models"
        Seedance["Seedance"]
        Kling["Kling"]
        Runway["Runway"]
        Sora["Sora"]
    end
    
    Agent -->|"Content Request"| ModelSelector
    
    ModelSelector -->|"Text"| GPT
    ModelSelector -->|"Text"| Claude
    ModelSelector -->|"Text"| Gemini
    ModelSelector -->|"Text"| Grok
    
    ModelSelector -->|"Image"| DALLE
    ModelSelector -->|"Image"| Flux
    
    ModelSelector -->|"Video"| Seedance
    ModelSelector -->|"Video"| Kling
    ModelSelector -->|"Video"| Runway
    ModelSelector -->|"Video"| Sora
```

**Model Selection Criteria:**
- **Cost optimization** - Select based on pricing for task complexity
- **Quality requirements** - Higher quality models for final content
- **Speed requirements** - Faster models for drafts and previews
- **Platform requirements** - Platform-specific constraints (video length, format, etc.)

**Sources:** [README.md:141-149](), [docker-compose.yml:114-128]()

### Platform Publishing Integration

The agent coordinates with the OAuth authentication system and platform APIs:

```mermaid
graph TB
    Agent["All In Agent<br/>Publishing Orchestrator"]
    
    subgraph "Platform Selection"
        PlatformConfig["Platform Configuration<br/>Target platforms<br/>Scheduling rules"]
    end
    
    subgraph "OAuth Management"
        TokenStore[("Token Store<br/>MongoDB oauth_tokens")]
        TokenRefresh["Token Refresh Logic<br/>Re-authentication flow"]
    end
    
    subgraph "Content Adaptation"
        FormatAdapt["Format Adapter<br/>Platform-specific formatting"]
        AssetResize["Asset Resizing<br/>Platform requirements"]
    end
    
    subgraph "Platform APIs"
        TikTok["TikTok API"]
        YouTube["YouTube API"]
        Twitter["Twitter/X API"]
        Instagram["Instagram API"]
        Others["11 more platforms..."]
    end
    
    Agent --> PlatformConfig
    PlatformConfig --> TokenStore
    TokenStore -->|"Check validity"| TokenRefresh
    
    TokenRefresh -->|"Valid tokens"| FormatAdapt
    FormatAdapt --> AssetResize
    
    AssetResize --> TikTok
    AssetResize --> YouTube
    AssetResize --> Twitter
    AssetResize --> Instagram
    AssetResize --> Others
    
    TikTok -.->|"Publish result"| Agent
    YouTube -.->|"Publish result"| Agent
    Twitter -.->|"Publish result"| Agent
```

**Publishing Flow:**
1. Agent selects target platforms based on content type and user configuration
2. Retrieves OAuth tokens from MongoDB
3. Validates token expiration, triggers re-auth if needed
4. Adapts content format for each platform (character limits, hashtag styles, etc.)
5. Resizes/converts assets to meet platform requirements
6. Executes parallel publishing to all selected platforms
7. Records publish metadata and results

**Sources:** [docker-compose.yml:183-212](), based on platform integration architecture

## Configuration

### Environment Variables

The All In Agent relies on configuration from multiple services in the Docker Compose stack:

**AI Service Configuration** (`aitoearn-ai` service):

| Variable | Purpose | Default |
|----------|---------|---------|
| `OPENAI_API_KEY` | Access to GPT models for text generation | `sk-placeholder` |
| `OPENAI_BASE_URL` | OpenAI API endpoint or relay service | `https://api.openai.com/v1` |
| `ANTHROPIC_API_KEY` | Access to Claude models | `sk-placeholder` |
| `GEMINI_KEY_PAIRS` | Google Gemini configuration (JSON array) | Placeholder JSON |
| `VOLCENGINE_API_KEY` | Volcengine (Doubao) access | Empty |
| `GROK_API_KEY` | xAI Grok access | Empty |
| `AI_PROXY_URL` | Optional AI API proxy for geo-restricted models | Empty |

**Backend Service Configuration** (`aitoearn-server` service):

| Variable | Purpose | Default |
|----------|---------|---------|
| `INTERNAL_TOKEN` | Authentication between services | `change-this-secret-token` |
| `JWT_SECRET` | User session management | `change-this-jwt-secret` |
| `AI_URL` | URL to aitoearn-ai service | `http://aitoearn-ai:3010` |
| Platform OAuth variables | Credentials for 14+ platforms | Empty (optional) |

**Sources:** [docker-compose.yml:95-128](), [docker-compose.yml:151-227]()

### Recommended Setup for Production

**Using AI Relay Services:**

The agent works best with a relay service like [new-api](https://github.com/Calcium-Ion/new-api) or [one-api](https://github.com/songquanpeng/one-api) to manage multiple AI providers through a single endpoint:

```yaml
# In docker-compose.yml aitoearn-ai service:
OPENAI_BASE_URL: https://your-new-api-host/v1
OPENAI_API_KEY: sk-your-relay-api-key

# All models (GPT, Claude, Gemini, etc.) accessible through relay
```

**OAuth Configuration:**

For the agent to publish autonomously, configure OAuth credentials for target platforms:

```yaml
# Example: TikTok configuration
TIKTOK_CLIENT_ID: "your-client-id"
TIKTOK_CLIENT_SECRET: "your-client-secret"

# Callback URL format: https://{APP_DOMAIN}/api/plat/tiktok/auth/back
```

**Sources:** [DOCKER_DEPLOYMENT_EN.md:206-220](), [DOCKER_DEPLOYMENT_EN.md:251-270]()

### Application Configuration Files

The agent behavior is also controlled through configuration files mounted into containers:

**AI Service Config** (`config/aitoearn-ai.config.js`):
- AI model definitions and pricing
- Model selection preferences
- Asset storage configuration
- Generation parameters

**Server Config** (`config/aitoearn-server.config.js`):
- Platform-specific publishing rules
- OAuth callback URLs
- Content optimization settings
- Scheduling policies

**Sources:** [docker-compose.yml:91-92](), [docker-compose.yml:148]()

## Agent Presentation

The All In Agent feature is prominently displayed in the AiToEarn user interface:

```mermaid
graph TB
    LandingPage["Landing Page<br/>README screenshots"]
    
    AgentSection["Agent Section<br/>presentation/agent_0.png<br/>Visual demonstration"]
    
    Features["Feature List<br/>- Auto content generation<br/>- Auto publishing<br/>- Operation assistance"]
    
    LandingPage --> AgentSection
    AgentSection --> Features
    
    AgentSection -.->|"Showcases"| UI1["Agent Dashboard"]
    AgentSection -.->|"Showcases"| UI2["Generation Progress"]
    AgentSection -.->|"Showcases"| UI3["Publishing Status"]
```

**Visual Assets:**
- Main agent showcase: `presentation/agent_0.png`
- Demonstrates the agent interface and capabilities
- Part of the v1.5.2 display materials

**Sources:** [README.md:71-76](), [presentation/agent_0.png:1](), [presentation/display-1.5.2png.png:1]()

## Technical Limitations

**Note:** The specific implementation details of the All In Agent feature are not visible in the provided codebase files. The information in this document is derived from:

1. **Documentation** - README files describing feature capabilities
2. **Architecture diagrams** - System-level overview of component relationships
3. **Configuration** - Docker Compose and environment variable setup
4. **Inference** - Logical integration with existing AI and publishing systems

For detailed implementation, refer to:
- Agent-specific service modules in `aitoearn-server` and `aitoearn-ai`
- Agent workflow orchestration code
- Agent state management in MongoDB schemas
- Agent UI components in `aitoearn-web`

The agent leverages all the infrastructure described in:
- [AI Service Architecture](#3.1) for content generation
- [Multi-Platform Publishing](#4.3) for content distribution
- [Calendar Timing and Scheduling](#5.2) for automation
- [Hotspot Analysis](#5.3) for trend detection

**Sources:** Analysis based on provided file listing and README documentation

---

# Page: Platform Integration System

# Platform Integration System

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



## Purpose and Scope

The Platform Integration System enables AiToEarn to connect with 14+ social media platforms for multi-channel content distribution, engagement tracking, and analytics collection. This system handles OAuth 2.0 authentication flows, manages access tokens, provides platform-specific API adapters, and coordinates cross-platform publishing operations.

This document provides an overview of the integration architecture. For detailed information on specific aspects:
- OAuth authentication flow mechanics and token management: see [OAuth Authentication Flow](#4.1)
- Platform-specific configuration and API capabilities: see [Supported Platforms](#4.2)  
- Multi-platform content publishing workflows: see [Multi-Platform Publishing](#4.3)

For AI-powered content generation features that work with this system, see [AI Integration System](#3). For content scheduling and calendar features, see [Calendar Timing and Scheduling](#5.2).

## System Architecture

### Integration Overview

The Platform Integration System operates as a middleware layer between AiToEarn's core services and external social media platform APIs. The `aitoearn-server` service manages all platform integrations through a unified interface while maintaining platform-specific adapters.

**Platform Integration Architecture**

```mermaid
graph TB
    subgraph "Client Applications"
        WebUI["aitoearn-web<br/>:3000"]
        DesktopApp["Electron Desktop"]
    end
    
    subgraph "Backend Services"
        Server["aitoearn-server<br/>:3002"]
        AI["aitoearn-ai<br/>:3010"]
    end
    
    subgraph "Data Layer"
        MongoDB[("MongoDB<br/>:27017<br/>OAuth Tokens<br/>User Accounts<br/>Publish History")]
        Redis[("Redis<br/>:6379<br/>Session Cache<br/>Rate Limits")]
    end
    
    subgraph "External Platforms"
        direction LR
        TikTok["TikTok API"]
        YouTube["YouTube API"]
        Twitter["Twitter/X API"]
        Instagram["Instagram API"]
        Facebook["Facebook API"]
        LinkedIn["LinkedIn API"]
        Threads["Threads API"]
        Pinterest["Pinterest API"]
        Bilibili["Bilibili API"]
        Douyin["Douyin API"]
        Kuaishou["Kuaishou API"]
        Xiaohongshu["Xiaohongshu API"]
        WeChat["WeChat Channels"]
        WXPlat["WeChat Official"]
    end
    
    WebUI --> Server
    DesktopApp --> Server
    Server --> MongoDB
    Server --> Redis
    Server --> AI
    
    Server -->|"OAuth Flow<br/>API Calls"| TikTok
    Server -->|"OAuth Flow<br/>API Calls"| YouTube
    Server -->|"OAuth Flow<br/>API Calls"| Twitter
    Server -->|"OAuth Flow<br/>API Calls"| Instagram
    Server -->|"OAuth Flow<br/>API Calls"| Facebook
    Server -->|"OAuth Flow<br/>API Calls"| LinkedIn
    Server -->|"OAuth Flow<br/>API Calls"| Threads
    Server -->|"OAuth Flow<br/>API Calls"| Pinterest
    Server -->|"OAuth Flow<br/>API Calls"| Bilibili
    Server -->|"OAuth Flow<br/>API Calls"| Douyin
    Server -->|"OAuth Flow<br/>API Calls"| Kuaishou
    Server -->|"OAuth Flow<br/>API Calls"| Xiaohongshu
    Server -->|"OAuth Flow<br/>API Calls"| WeChat
    Server -->|"OAuth Flow<br/>API Calls"| WXPlat
```

Sources: [README.md:18-20](), [docker-compose.yml:183-212](), system architecture diagrams provided

### Component Responsibilities

| Component | Responsibility |
|-----------|---------------|
| **aitoearn-server** | OAuth coordination, token management, platform API calls, publish orchestration |
| **MongoDB** | Persistent storage of OAuth tokens, user-platform bindings, publish metadata |
| **Redis** | Session state, OAuth state tokens, rate limiting counters |
| **aitoearn-web** | User interface for platform connection, publish triggers |
| **Platform APIs** | External social media platform endpoints (OAuth, publishing, analytics) |

Sources: [docker-compose.yml:136-232](), [DOCKER_DEPLOYMENT_EN.md:28-36]()

## OAuth Configuration

### Environment Variables

Platform credentials are configured via environment variables in the `aitoearn-server` service. Each platform requires a client ID and client secret obtained from the platform's developer console.

**OAuth Credential Configuration**

| Platform | Environment Variables | Developer Portal |
|----------|---------------------|------------------|
| TikTok | `TIKTOK_CLIENT_ID`, `TIKTOK_CLIENT_SECRET` | https://developers.tiktok.com |
| YouTube | `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET` | https://console.cloud.google.com |
| Twitter/X | `TWITTER_CLIENT_ID`, `TWITTER_CLIENT_SECRET` | https://developer.x.com |
| Instagram | `INSTAGRAM_CLIENT_ID`, `INSTAGRAM_CLIENT_SECRET` | https://developers.facebook.com |
| Facebook | `FACEBOOK_CLIENT_ID`, `FACEBOOK_CLIENT_SECRET`, `FACEBOOK_CONFIG_ID` | https://developers.facebook.com |
| LinkedIn | `LINKEDIN_CLIENT_ID`, `LINKEDIN_CLIENT_SECRET` | https://linkedin.com/developers |
| Threads | `THREADS_CLIENT_ID`, `THREADS_CLIENT_SECRET` | https://developers.facebook.com |
| Pinterest | `PINTEREST_CLIENT_ID`, `PINTEREST_CLIENT_SECRET`, `PINTEREST_TEST_AUTHORIZATION` | https://developers.pinterest.com |
| Bilibili | `BILIBILI_CLIENT_ID`, `BILIBILI_CLIENT_SECRET` | https://open.bilibili.com |
| Douyin | `DOYIN_CLIENT_ID`, `DOYIN_CLIENT_SECRET` | https://open.douyin.com |
| Kuaishou | `KWAI_CLIENT_ID`, `KWAI_CLIENT_SECRET` | https://open.kuaishou.com |
| Google (YouTube) | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | https://console.cloud.google.com |
| WeChat Official | `WXPLAT_APP_ID`, `WXPLAT_APP_SECRET`, `WXPLAT_ENCODING_AES_KEY` | https://mp.weixin.qq.com |

Sources: [docker-compose.yml:183-212](), [DOCKER_DEPLOYMENT_CN.md:250-267](), [DOCKER_DEPLOYMENT_EN.md:252-269]()

### Callback URL Structure

OAuth callback URLs follow a consistent pattern across all platforms:

```
https://{APP_DOMAIN}/api/plat/{platform}/auth/back
```

Where:
- `{APP_DOMAIN}`: Configured via the `APP_DOMAIN` environment variable in `aitoearn-server` [docker-compose.yml:155]()
- `{platform}`: Platform identifier (e.g., `tiktok`, `youtube`, `twitter`, `instagram`)

The `APP_DOMAIN` must be accessible from the public internet for OAuth callbacks to function correctly.

Sources: [DOCKER_DEPLOYMENT_CN.md:269](), [DOCKER_DEPLOYMENT_EN.md:271]()

## OAuth Authentication Flow

### High-Level Flow

**OAuth 2.0 Authorization Code Flow**

```mermaid
sequenceDiagram
    participant User as "User Browser"
    participant Web as "aitoearn-web"
    participant Server as "aitoearn-server<br/>/api/plat/{platform}"
    participant Redis as "Redis<br/>State Tokens"
    participant Platform as "Platform OAuth"
    participant MongoDB as "MongoDB<br/>Tokens Collection"
    
    User->>Web: "Click 'Connect Platform'"
    Web->>Server: "GET /api/plat/{platform}/auth"
    Server->>Redis: "Generate & store state token"
    Redis-->>Server: "state_token"
    Server-->>User: "Redirect to Platform OAuth"
    
    User->>Platform: "Authorize AiToEarn"
    Platform->>User: "Redirect with code & state"
    User->>Server: "GET /api/plat/{platform}/auth/back?code=xxx&state=yyy"
    
    Server->>Redis: "Validate state token"
    Redis-->>Server: "Valid"
    Server->>Platform: "POST /oauth/token (exchange code)"
    Platform-->>Server: "access_token, refresh_token"
    
    Server->>Platform: "GET /api/user (fetch profile)"
    Platform-->>Server: "user_id, username, etc"
    
    Server->>MongoDB: "Store tokens + profile"
    MongoDB-->>Server: "OK"
    Server-->>Web: "Redirect to success page"
    Web-->>User: "Platform connected successfully"
```

Sources: [DOCKER_DEPLOYMENT_CN.md:269](), [DOCKER_DEPLOYMENT_EN.md:271]()

### State Token Management

OAuth state tokens are ephemeral security tokens stored in Redis with a short TTL (typically 10-15 minutes). They prevent CSRF attacks by ensuring the callback request originates from a legitimate authorization initiation.

**State Token Lifecycle**:
1. Generated when user initiates OAuth flow
2. Stored in Redis with user session ID
3. Validated on callback
4. Deleted after validation (one-time use)

Sources: [docker-compose.yml:105-107](), [docker-compose.yml:168-169]()

### Token Storage Schema

OAuth tokens are stored in MongoDB with the following conceptual structure:

| Field | Type | Description |
|-------|------|-------------|
| `userId` | ObjectId | Reference to user document |
| `platform` | String | Platform identifier (e.g., "tiktok") |
| `platformUserId` | String | User ID on external platform |
| `platformUsername` | String | Username on external platform |
| `accessToken` | String (encrypted) | OAuth access token |
| `refreshToken` | String (encrypted) | OAuth refresh token |
| `expiresAt` | DateTime | Access token expiration timestamp |
| `scope` | Array | OAuth scopes granted |
| `createdAt` | DateTime | Token creation timestamp |
| `updatedAt` | DateTime | Last token refresh timestamp |

Tokens are encrypted at rest in MongoDB to protect user credentials.

Sources: [docker-compose.yml:100-103](), [docker-compose.yml:157-160](), MongoDB schema implied from architecture

## Platform API Integration

### Unified Platform Interface

The system provides a unified interface for platform operations while maintaining platform-specific implementations. Each platform has dedicated modules for:

- **Authentication**: OAuth flow handling, token refresh
- **Publishing**: Content formatting, API calls, error handling  
- **Fetching**: Retrieve published content metadata, analytics
- **Engagement**: Comments, likes, interactions management

### Rate Limiting

Rate limits are enforced at two levels:

1. **Redis-based Application Limits**: Track API calls per user per platform to stay within platform quotas
2. **Platform-native Limits**: Handle HTTP 429 responses with exponential backoff

Rate limit counters are stored in Redis with keys like:
```
rate_limit:{userId}:{platform}:{endpoint}
```

Sources: [docker-compose.yml:168-169](), Redis usage from architecture

### Error Handling

Platform integration errors are categorized and handled appropriately:

| Error Type | Handling Strategy |
|------------|-------------------|
| OAuth expired | Automatic refresh token flow |
| Rate limit exceeded | Queue request with backoff |
| Platform unavailable | Retry with exponential backoff |
| Invalid content format | Return validation error to user |
| Permission denied | Prompt user to re-authorize |

Failed publish attempts are logged to MongoDB for retry and debugging.

Sources: Architecture patterns from deployment documentation

## Content Publishing Flow

### Multi-Platform Publishing

**Content Distribution Workflow**

```mermaid
graph TB
    User["User Creates Content"]
    Draft["Draft Storage<br/>MongoDB"]
    Schedule["Schedule Check<br/>Redis Queue"]
    Publish["Publish Orchestrator<br/>aitoearn-server"]
    
    subgraph "Platform Adapters"
        TikTokAdapter["TikTok Adapter"]
        YouTubeAdapter["YouTube Adapter"]
        TwitterAdapter["Twitter Adapter"]
        InstagramAdapter["Instagram Adapter"]
        OtherAdapters["Other Platform Adapters"]
    end
    
    subgraph "Platform APIs"
        TikTokAPI["TikTok API"]
        YouTubeAPI["YouTube API"]
        TwitterAPI["Twitter API"]
        InstagramAPI["Instagram API"]
        OtherAPIs["Other APIs"]
    end
    
    Results["Publish Results<br/>MongoDB"]
    Analytics["Analytics Collection"]
    
    User --> Draft
    Draft --> Schedule
    Schedule --> Publish
    
    Publish --> TikTokAdapter
    Publish --> YouTubeAdapter
    Publish --> TwitterAdapter
    Publish --> InstagramAdapter
    Publish --> OtherAdapters
    
    TikTokAdapter --> TikTokAPI
    YouTubeAdapter --> YouTubeAPI
    TwitterAdapter --> TwitterAPI
    InstagramAdapter --> InstagramAPI
    OtherAdapters --> OtherAPIs
    
    TikTokAPI --> Results
    YouTubeAPI --> Results
    TwitterAPI --> Results
    InstagramAPI --> Results
    OtherAPIs --> Results
    
    Results --> Analytics
```

Sources: High-level workflow diagram from system overview, [README.md:79-89]()

### Platform-Specific Adaptations

Each platform requires specific content adaptations:

| Platform | Adaptations |
|----------|-------------|
| TikTok | Video aspect ratio (9:16), duration limits, hashtag formatting |
| YouTube | Video metadata (title, description, tags), thumbnail upload, category selection |
| Twitter/X | Character limits (280), media attachment limits, thread support |
| Instagram | Image aspect ratios, caption length, hashtag limits (30 max) |
| Facebook | Link preview optimization, image dimensions, video specs |
| LinkedIn | Professional tone suggestions, document format support |
| Threads | Text-first formatting, parent-child post relationships |
| Pinterest | Image pins, board selection, rich pin metadata |

Platform adapters in `aitoearn-server` handle these transformations automatically.

Sources: [README.md:18-20](), platform requirements from integration architecture

## Data Persistence

### Storage Architecture

**Platform Integration Data Model**

```mermaid
graph LR
    subgraph "MongoDB Collections"
        Users["users<br/>User accounts"]
        Platforms["platforms<br/>Connected platforms"]
        Tokens["oauth_tokens<br/>Access tokens"]
        Drafts["drafts<br/>Content drafts"]
        Publishes["publishes<br/>Publish records"]
        Analytics["statistics<br/>Analytics data"]
    end
    
    subgraph "Redis Keys"
        Sessions["sessions:*<br/>User sessions"]
        States["oauth_state:*<br/>OAuth states"]
        RateLimits["rate_limit:*<br/>API quotas"]
        Queue["publish_queue<br/>Pending publishes"]
    end
    
    Users --> Tokens
    Users --> Platforms
    Users --> Drafts
    Drafts --> Publishes
    Publishes --> Analytics
    
    Sessions -.->|Reference| Users
    States -.->|Temporary| Sessions
```

Sources: [docker-compose.yml:157-171](), [DOCKER_DEPLOYMENT_CN.md:161-171](), MongoDB and Redis usage patterns

### Database Configuration

MongoDB connection configuration in `aitoearn-server`:
- **Host**: `mongodb` (Docker internal network)
- **Port**: `27017`
- **Database**: `aitoearn`
- **Credentials**: Configured via `MONGODB_USERNAME` and `MONGODB_PASSWORD` environment variables

Redis connection configuration:
- **Host**: `redis` (Docker internal network)  
- **Port**: `6379`
- **Password**: Configured via `REDIS_PASSWORD` environment variable

Sources: [docker-compose.yml:157-169](), [docker-compose.yml:100-107]()

## Security Considerations

### Token Encryption

OAuth access tokens and refresh tokens are encrypted before storage in MongoDB. The encryption keys are derived from the `JWT_SECRET` environment variable.

### OAuth State Validation

All OAuth callbacks validate the state parameter against Redis storage to prevent CSRF attacks. State tokens are:
- Cryptographically random (32+ bytes)
- Single-use (deleted after validation)
- Time-limited (10-15 minute TTL)
- Bound to user session

### API Key Management

Platform API credentials (client IDs and secrets) are:
- Configured via environment variables only
- Never logged or exposed in responses
- Isolated per deployment environment

Sources: [docker-compose.yml:109](), [docker-compose.yml:173-174](), security best practices from OAuth 2.0 spec

## Monitoring and Debugging

### Health Checks

The `aitoearn-server` service exposes a health endpoint for monitoring platform integration status:

```
GET http://localhost:3002/health
```

This endpoint is used by Docker healthchecks and monitoring systems.

Sources: [docker-compose.yml:227-232]()

### Logging

Platform integration operations are logged with structured logging including:
- User ID and platform identifier
- API endpoint called
- Response status codes
- Error messages and stack traces
- Request/response timing

Log output is controlled by environment variables in the AI and server services.

Sources: [docker-compose.yml:95-98](), [docker-compose.yml:152-154]()

## Related Configuration Files

The following configuration files contain platform-specific settings:

| File | Purpose | Mounted To |
|------|---------|------------|
| `config/aitoearn-server.config.js` | Backend platform configuration, OAuth settings | `aitoearn-server:/app/config.js` |
| `docker-compose.yml` | OAuth credentials, API endpoints | All services |

Sources: [docker-compose.yml:148](), [DOCKER_DEPLOYMENT_CN.md:96-111]()

---

# Page: OAuth Authentication Flow

# OAuth Authentication Flow

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



## Purpose and Scope

This document details the OAuth 2.0 authentication flow used by AiToEarn to connect and authorize with third-party social media platforms. It covers the complete authorization lifecycle: initiating OAuth requests, handling platform callbacks, exchanging authorization codes for access tokens, securely storing tokens, and managing state tokens to prevent CSRF attacks.

For information about which platforms are supported and their specific API capabilities, see [Supported Platforms](#4.2). For details on using authorized platform connections to publish content, see [Multi-Platform Publishing](#4.3).

**Sources:** [docker-compose.yml:183-212](), [DOCKER_DEPLOYMENT_EN.md:253-270](), [DOCKER_DEPLOYMENT_CN.md:251-268]()

## OAuth 2.0 Flow Overview

AiToEarn implements the standard OAuth 2.0 Authorization Code Grant flow for all supported platforms. The backend service (`aitoearn-server`) acts as the OAuth client, managing the authorization process and securely storing access tokens in MongoDB.

### Complete OAuth Flow Sequence

```mermaid
sequenceDiagram
    participant User as "User Browser"
    participant Web as "aitoearn-web<br/>(Next.js Frontend)"
    participant Nginx as "nginx<br/>(Reverse Proxy)"
    participant Server as "aitoearn-server<br/>(NestJS Backend)"
    participant Redis as "redis<br/>(State Storage)"
    participant Platform as "Platform OAuth<br/>(TikTok/YouTube/etc)"
    participant Mongo as "mongodb<br/>(Token Storage)"

    User->>Web: "1. Click 'Connect Platform'"
    Web->>Nginx: "2. GET /api/plat/{platform}/auth"
    Nginx->>Server: "3. Forward request"
    Server->>Redis: "4. Generate & store state token"
    Redis-->>Server: "5. State token saved"
    Server->>Server: "6. Build authorization URL<br/>with CLIENT_ID, state, callback"
    Server-->>User: "7. Redirect to Platform OAuth"
    
    User->>Platform: "8. Authorize application"
    Platform->>Platform: "9. User grants permissions"
    Platform-->>User: "10. Redirect to callback URL<br/>{APP_DOMAIN}/api/plat/{platform}/auth/back"
    
    User->>Nginx: "11. GET /api/plat/{platform}/auth/back<br/>?code=xxx&state=xxx"
    Nginx->>Server: "12. Forward callback"
    Server->>Redis: "13. Validate state token"
    Redis-->>Server: "14. State valid"
    Server->>Platform: "15. POST /token<br/>Exchange code for access_token<br/>(CLIENT_ID, CLIENT_SECRET, code)"
    Platform-->>Server: "16. Return access_token + refresh_token"
    Server->>Mongo: "17. Store tokens in User document"
    Mongo-->>Server: "18. Tokens saved"
    Server->>Redis: "19. Delete used state token"
    Server-->>User: "20. Redirect to frontend success page"
```

**Sources:** [docker-compose.yml:136-232](), [DOCKER_DEPLOYMENT_EN.md:269-270]()

## Configuration

### Environment Variables

OAuth credentials for each platform are configured as environment variables in the `aitoearn-server` service. These variables are set in `docker-compose.yml` and must match the credentials registered in each platform's developer console.

| Platform | Environment Variables | Developer Console URL |
|----------|----------------------|----------------------|
| TikTok | `TIKTOK_CLIENT_ID`, `TIKTOK_CLIENT_SECRET` | https://developers.tiktok.com |
| YouTube | `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET` | https://console.cloud.google.com/apis/credentials |
| Twitter/X | `TWITTER_CLIENT_ID`, `TWITTER_CLIENT_SECRET` | https://developer.x.com/en/portal |
| Facebook | `FACEBOOK_CLIENT_ID`, `FACEBOOK_CLIENT_SECRET`, `FACEBOOK_CONFIG_ID` | https://developers.facebook.com |
| Instagram | `INSTAGRAM_CLIENT_ID`, `INSTAGRAM_CLIENT_SECRET` | https://developers.facebook.com |
| Threads | `THREADS_CLIENT_ID`, `THREADS_CLIENT_SECRET` | https://developers.facebook.com |
| LinkedIn | `LINKEDIN_CLIENT_ID`, `LINKEDIN_CLIENT_SECRET` | https://www.linkedin.com/developers |
| Pinterest | `PINTEREST_CLIENT_ID`, `PINTEREST_CLIENT_SECRET`, `PINTEREST_TEST_AUTHORIZATION` | https://developers.pinterest.com |
| Bilibili | `BILIBILI_CLIENT_ID`, `BILIBILI_CLIENT_SECRET` | https://open.bilibili.com |
| Kuaishou | `KWAI_CLIENT_ID`, `KWAI_CLIENT_SECRET` | https://open.kuaishou.com |
| Google | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | https://console.cloud.google.com/apis/credentials |
| WeChat Platform | `WXPLAT_APP_ID`, `WXPLAT_APP_SECRET`, `WXPLAT_ENCODING_AES_KEY` | https://mp.weixin.qq.com |
| Douyin | `DOYIN_CLIENT_ID`, `DOYIN_CLIENT_SECRET` | https://open.douyin.com |

**Sources:** [docker-compose.yml:183-212](), [DOCKER_DEPLOYMENT_EN.md:253-268]()

### Callback URL Configuration

All platforms must be configured with the OAuth callback URL in their developer consoles. The callback URL follows this pattern:

```
https://{APP_DOMAIN}/api/plat/{platform}/auth/back
```

Where:
- `{APP_DOMAIN}` is set via the `APP_DOMAIN` environment variable in `aitoearn-server` (default: `localhost`)
- `{platform}` is the platform identifier (e.g., `tiktok`, `youtube`, `twitter`, `facebook`, `instagram`, `linkedin`, `pinterest`, `bilibili`, `kwai`, `google`, `wxplat`, `doyin`)

**Example callback URLs:**
- TikTok: `https://yourdomain.com/api/plat/tiktok/auth/back`
- YouTube: `https://yourdomain.com/api/plat/youtube/auth/back`
- Twitter: `https://yourdomain.com/api/plat/twitter/auth/back`

The `nginx` service routes all `/api/*` requests to `aitoearn-server:3002` via the internal Docker network `aitoearn-network`.

**Sources:** [docker-compose.yml:155](), [docker-compose.yml:248-270](), [DOCKER_DEPLOYMENT_EN.md:269-270]()

## System Components Involved in OAuth

```mermaid
graph TB
    subgraph "Client Layer"
        Browser["User Browser"]
        WebApp["aitoearn-web:3000<br/>Next.js Frontend"]
    end
    
    subgraph "Gateway Layer"
        Nginx["nginx:80<br/>Reverse Proxy<br/>(External Port 8080)"]
    end
    
    subgraph "Application Layer"
        Server["aitoearn-server:3002<br/>NestJS Backend<br/>OAuth Client"]
    end
    
    subgraph "Data Layer"
        Redis["redis:6379<br/>State Token Cache<br/>REDIS_PASSWORD"]
        Mongo["mongodb:27017<br/>Token Storage<br/>MONGODB_PASSWORD"]
    end
    
    subgraph "External Services"
        TikTok["TikTok OAuth<br/>TIKTOK_CLIENT_ID<br/>TIKTOK_CLIENT_SECRET"]
        YouTube["YouTube OAuth<br/>YOUTUBE_CLIENT_ID<br/>YOUTUBE_CLIENT_SECRET"]
        Twitter["Twitter OAuth<br/>TWITTER_CLIENT_ID<br/>TWITTER_CLIENT_SECRET"]
        Others["Facebook, Instagram,<br/>LinkedIn, Pinterest, etc."]
    end
    
    Browser -->|"HTTP"| Nginx
    WebApp -->|"Internal Network"| Nginx
    Nginx -->|"/api/plat/{platform}/auth/*"| Server
    
    Server -->|"Generate/Validate State"| Redis
    Server -->|"Store/Retrieve Tokens"| Mongo
    
    Server <-->|"OAuth 2.0 Flow"| TikTok
    Server <-->|"OAuth 2.0 Flow"| YouTube
    Server <-->|"OAuth 2.0 Flow"| Twitter
    Server <-->|"OAuth 2.0 Flow"| Others
```

**Sources:** [docker-compose.yml:1-286](), [docker-compose.yml:248-270]()

## Authorization Request Flow

### Step 1: User Initiates Connection

When a user wants to connect a social media platform account:

1. User clicks "Connect [Platform]" button in the frontend (`aitoearn-web`)
2. Frontend sends a GET request to `/api/plat/{platform}/auth`
3. Request is routed through `nginx:80` → `aitoearn-server:3002`

### Step 2: State Token Generation

The backend generates a cryptographically secure random state token to prevent CSRF attacks:

1. `aitoearn-server` generates a unique state token (typically a UUID or random string)
2. State token is stored in `redis` with an expiration time (typically 10-15 minutes)
3. State token is associated with the current user session

**Redis storage pattern:**
```
Key: oauth:state:{state_token}
Value: {user_id, platform, timestamp}
TTL: 900 seconds (15 minutes)
```

**Sources:** [docker-compose.yml:23-39](), [docker-compose.yml:105-107]()

### Step 3: Building the Authorization URL

The backend constructs the OAuth authorization URL with the following parameters:

```
https://platform-oauth-endpoint.com/authorize?
  client_id={CLIENT_ID}
  &redirect_uri={APP_DOMAIN}/api/plat/{platform}/auth/back
  &response_type=code
  &scope={requested_scopes}
  &state={state_token}
```

**Required parameters:**
- `client_id`: Platform-specific client ID from environment variables (e.g., `TIKTOK_CLIENT_ID`)
- `redirect_uri`: Callback URL registered with the platform
- `response_type`: Always `code` for Authorization Code Grant
- `scope`: Platform-specific permissions (e.g., `user.info.basic`, `video.upload`)
- `state`: CSRF protection token stored in Redis

### Step 4: User Redirection

The backend responds with an HTTP 302 redirect, sending the user's browser to the platform's OAuth authorization page.

**Sources:** [docker-compose.yml:183-212]()

## Callback Handling

### Step 1: Platform Redirects to Callback URL

After the user authorizes the application on the platform, the platform redirects the user back to:

```
{APP_DOMAIN}/api/plat/{platform}/auth/back?code={authorization_code}&state={state_token}
```

This request flows through:
1. User browser → `nginx:8080`
2. `nginx` → `aitoearn-server:3002` (via internal network `aitoearn-network`)

**Sources:** [docker-compose.yml:248-270](), [docker-compose.yml:272-275]()

### Step 2: State Token Validation

The backend validates the state token to prevent CSRF attacks:

1. Extract `state` parameter from the callback URL
2. Look up the state token in `redis` using key `oauth:state:{state_token}`
3. Verify the state token exists and has not expired
4. Verify the state token is associated with the current user session
5. Delete the state token from `redis` to prevent replay attacks

**Validation checks:**
- State token exists in Redis
- State token matches the user's session
- State token has not expired (TTL)
- Platform matches the stored platform value

If validation fails, the backend returns an error and does not proceed with token exchange.

**Sources:** [docker-compose.yml:23-39](), [docker-compose.yml:105-107]()

### Step 3: Authorization Code Extraction

Once the state is validated, the backend extracts the `code` parameter from the callback URL. This authorization code is a single-use token that will be exchanged for an access token.

**Sources:** [DOCKER_DEPLOYMENT_EN.md:269-270]()

## Token Exchange

### Exchange Request

The backend makes a server-to-server POST request to the platform's token endpoint to exchange the authorization code for an access token:

```
POST https://platform-token-endpoint.com/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&code={authorization_code}
&client_id={CLIENT_ID}
&client_secret={CLIENT_SECRET}
&redirect_uri={APP_DOMAIN}/api/plat/{platform}/auth/back
```

**Required parameters:**
- `grant_type`: Always `authorization_code`
- `code`: Authorization code received from callback
- `client_id`: Platform client ID from environment variables
- `client_secret`: Platform client secret from environment variables (e.g., `TIKTOK_CLIENT_SECRET`, `YOUTUBE_CLIENT_SECRET`)
- `redirect_uri`: Same callback URL used in the authorization request

**Sources:** [docker-compose.yml:183-212]()

### Token Response

The platform responds with a JSON payload containing:

```json
{
  "access_token": "platform_access_token_string",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "platform_refresh_token_string",
  "scope": "granted_scope_1 granted_scope_2"
}
```

**Key fields:**
- `access_token`: Used to authenticate API requests to the platform
- `expires_in`: Token lifetime in seconds
- `refresh_token`: Used to obtain new access tokens when the current one expires (not all platforms provide refresh tokens)
- `scope`: Actual permissions granted by the user

**Sources:** [DOCKER_DEPLOYMENT_EN.md:253-268]()

## Token Storage and Management

### MongoDB Storage Schema

Access tokens and refresh tokens are stored in the `mongodb` database within the user's document. The database connection is configured via environment variables:

- `MONGODB_HOST`: `mongodb` (Docker service name)
- `MONGODB_PORT`: `27017`
- `MONGODB_USERNAME`: `admin`
- `MONGODB_PASSWORD`: Set in `docker-compose.yml`

**Typical storage structure:**
```javascript
// User document in mongodb.aitoearn collection
{
  _id: ObjectId("..."),
  email: "user@example.com",
  platforms: {
    tiktok: {
      access_token: "encrypted_access_token",
      refresh_token: "encrypted_refresh_token",
      expires_at: ISODate("2024-12-31T23:59:59Z"),
      scope: "user.info.basic,video.upload",
      platform_user_id: "platform_specific_user_id",
      connected_at: ISODate("2024-01-01T00:00:00Z"),
      updated_at: ISODate("2024-01-15T12:00:00Z")
    },
    youtube: { /* similar structure */ },
    // ... other platforms
  }
}
```

**Sources:** [docker-compose.yml:2-21](), [docker-compose.yml:100-103](), [docker-compose.yml:157-160]()

### Token Encryption

Access tokens and refresh tokens are encrypted before storage in MongoDB using the `JWT_SECRET` configured in the `aitoearn-server` environment. This provides an additional layer of security beyond MongoDB authentication.

**Encryption configuration:**
- `JWT_SECRET`: Used for both JWT signing and token encryption
- Must be identical in both `aitoearn-ai` and `aitoearn-server` services

**Sources:** [docker-compose.yml:109](), [docker-compose.yml:173]()

### Token Refresh Flow

```mermaid
sequenceDiagram
    participant Job as "Background Job<br/>or API Request"
    participant Server as "aitoearn-server"
    participant Mongo as "mongodb"
    participant Platform as "Platform OAuth API"

    Job->>Server: "1. Attempt to use access token"
    Server->>Mongo: "2. Retrieve token from User doc"
    Mongo-->>Server: "3. Return token + expires_at"
    Server->>Server: "4. Check if expires_at < now"
    
    alt Token Expired
        Server->>Mongo: "5. Retrieve refresh_token"
        Mongo-->>Server: "6. Return refresh_token"
        Server->>Platform: "7. POST /token<br/>grant_type=refresh_token<br/>refresh_token=xxx<br/>CLIENT_ID, CLIENT_SECRET"
        Platform-->>Server: "8. Return new access_token"
        Server->>Mongo: "9. Update access_token + expires_at"
        Mongo-->>Server: "10. Tokens updated"
        Server-->>Job: "11. Proceed with new access_token"
    else Token Valid
        Server-->>Job: "12. Proceed with existing access_token"
    end
```

**Sources:** [docker-compose.yml:157-170](), [docker-compose.yml:183-212]()

## State Token Security

### CSRF Prevention

State tokens are the primary defense against Cross-Site Request Forgery (CSRF) attacks in the OAuth flow. The implementation ensures:

1. **Unpredictability**: State tokens are cryptographically random (UUID v4 or equivalent)
2. **Single-Use**: State tokens are deleted from Redis immediately after validation
3. **Time-Limited**: State tokens expire after 15 minutes (configured TTL in Redis)
4. **Session-Bound**: State tokens are tied to the user's authenticated session
5. **Integrity**: State tokens cannot be guessed or forged by attackers

### Redis-Based State Management

```mermaid
graph LR
    subgraph "Authorization Request"
        Gen["Generate<br/>state token"]
        Store["Store in Redis<br/>oauth:state:{token}"]
        Redirect["Redirect user<br/>with state param"]
    end
    
    subgraph "Callback Handling"
        Receive["Receive callback<br/>with state param"]
        Lookup["Lookup in Redis<br/>oauth:state:{token}"]
        Validate["Validate:<br/>- Exists?<br/>- Not expired?<br/>- Session match?"]
        Delete["Delete from Redis<br/>prevent replay"]
    end
    
    Gen --> Store
    Store --> Redirect
    Redirect -.->|User flow| Receive
    Receive --> Lookup
    Lookup --> Validate
    Validate --> Delete
```

**Redis configuration for state storage:**
- `REDIS_HOST`: `redis` (Docker service name)
- `REDIS_PORT`: `6379`
- `REDIS_PASSWORD`: Set in `docker-compose.yml`

**Sources:** [docker-compose.yml:23-39](), [docker-compose.yml:105-107](), [docker-compose.yml:168-169]()

## Platform-Specific Considerations

### Facebook, Instagram, and Threads

These platforms share the same OAuth infrastructure (Meta/Facebook):
- `FACEBOOK_CLIENT_ID`, `FACEBOOK_CLIENT_SECRET`, `FACEBOOK_CONFIG_ID`
- `INSTAGRAM_CLIENT_ID`, `INSTAGRAM_CLIENT_SECRET`
- `THREADS_CLIENT_ID`, `THREADS_CLIENT_SECRET`

All three use Facebook's OAuth endpoints and require configuration in the Facebook Developer Console at https://developers.facebook.com.

**Sources:** [docker-compose.yml:197-202]()

### YouTube and Google

YouTube OAuth is part of Google's OAuth system:
- Uses `YOUTUBE_CLIENT_ID` and `YOUTUBE_CLIENT_SECRET`
- Alternatively can use `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` for broader Google API access
- Both configured at https://console.cloud.google.com/apis/credentials

**Sources:** [docker-compose.yml:186-187](), [docker-compose.yml:206-207]()

### Pinterest Test Authorization

Pinterest includes an additional `PINTEREST_TEST_AUTHORIZATION` variable for sandbox/testing environments before production approval.

**Sources:** [docker-compose.yml:192]()

### WeChat Platform (WXPLAT)

WeChat uses different terminology and an additional security parameter:
- `WXPLAT_APP_ID` (equivalent to client_id)
- `WXPLAT_APP_SECRET` (equivalent to client_secret)
- `WXPLAT_ENCODING_AES_KEY` (for message encryption/decryption)

**Sources:** [docker-compose.yml:208-210]()

### Chinese Platforms (Douyin, Kuaishou, Bilibili)

These platforms follow standard OAuth 2.0 but use Chinese developer documentation:
- Douyin (抖音): https://open.douyin.com
- Kuaishou (快手): https://open.kuaishou.com
- Bilibili: https://open.bilibili.com

**Sources:** [docker-compose.yml:184-185](), [docker-compose.yml:188-189](), [docker-compose.yml:211-212](), [README.md:18-20]()

## Network Architecture for OAuth Flow

```mermaid
graph TB
    subgraph "External Network"
        User["User Browser"]
        Platforms["OAuth Providers<br/>(TikTok, YouTube, etc.)"]
    end
    
    subgraph "Docker Network: aitoearn-network"
        Nginx["nginx:80<br/>Exposed: 8080"]
        Web["aitoearn-web:3000"]
        Server["aitoearn-server:3002<br/>APP_DOMAIN<br/>CLIENT_ID/SECRET<br/>JWT_SECRET"]
        Redis["redis:6379<br/>REDIS_PASSWORD<br/>State tokens"]
        Mongo["mongodb:27017<br/>MONGODB_PASSWORD<br/>Access tokens"]
    end
    
    User -->|":8080/api/plat/*"| Nginx
    Nginx -->|"proxy_pass"| Server
    Web -->|"Internal"| Nginx
    
    Server -->|"State storage"| Redis
    Server -->|"Token storage"| Mongo
    
    Server <-->|"OAuth 2.0"| Platforms
    User <-->|"OAuth UI"| Platforms
```

All OAuth-related services communicate within the isolated Docker network `aitoearn-network`, which is created with the `bridge` driver. Only `nginx` exposes port 8080 to the external network.

**Sources:** [docker-compose.yml:248-275](), [docker-compose.yml:272-275]()

## Error Handling and Edge Cases

### Common OAuth Error Scenarios

| Scenario | Detection | Handling |
|----------|-----------|----------|
| Invalid state token | State not found in Redis | Return error, log security event |
| Expired state token | Redis TTL expired | Return error, prompt user to retry |
| State token replay | State already deleted | Return error, log security event |
| Token exchange failure | Platform returns error | Log error, return user-friendly message |
| Invalid client credentials | Platform returns `invalid_client` | Log error, check `CLIENT_ID`/`CLIENT_SECRET` |
| Scope mismatch | Granted scope < requested scope | Store actual scope, may limit functionality |
| Network timeout | Request to platform times out | Retry with exponential backoff |
| MongoDB connection lost | Cannot store tokens | Return error, prompt retry |
| Redis connection lost | Cannot validate state | Return error, prompt retry |

**Sources:** [docker-compose.yml:100-110](), [docker-compose.yml:157-174]()

### Token Expiration Handling

When an access token expires:

1. Backend detects expiration by checking `expires_at` timestamp in MongoDB
2. Retrieves `refresh_token` from MongoDB
3. Attempts to refresh the access token using the platform's refresh endpoint
4. If refresh succeeds, updates MongoDB with new tokens
5. If refresh fails (e.g., refresh token also expired), marks connection as disconnected and prompts user to re-authorize

**Sources:** [docker-compose.yml:157-160]()

## Security Best Practices

### Secrets Management

All OAuth credentials are managed as environment variables in `docker-compose.yml`:

1. **Never commit real credentials** to version control
2. Use placeholder values in the repository (e.g., `sk-placeholder`, empty strings)
3. Set actual credentials during deployment via environment variable override or secrets management service
4. Rotate credentials periodically
5. Use different credentials for development, staging, and production environments

**Sources:** [docker-compose.yml:183-212]()

### Token Protection Measures

| Layer | Protection Mechanism | Implementation |
|-------|---------------------|----------------|
| Transport | HTTPS only | Nginx SSL/TLS termination |
| Storage | Encryption at rest | Tokens encrypted with `JWT_SECRET` before MongoDB storage |
| Access Control | MongoDB authentication | `MONGODB_USERNAME` and `MONGODB_PASSWORD` |
| Network Isolation | Docker internal network | Services communicate via `aitoearn-network` bridge |
| State CSRF Protection | Random state tokens | Generated, stored in Redis, validated on callback |
| Token expiration | Time-based invalidation | `expires_at` timestamp checked before use |

**Sources:** [docker-compose.yml:109](), [docker-compose.yml:173](), [docker-compose.yml:100-103](), [docker-compose.yml:272-275]()

---

# Page: Supported Platforms

# Supported Platforms

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



## Overview

AiToEarn supports multi-platform content distribution across 14 major social media platforms, spanning both Chinese and international markets. This page documents the OAuth configuration requirements, API capabilities, and platform-specific considerations for each supported platform.

**Supported Platforms:**

| Platform | Type | OAuth Required | Primary Markets |
|----------|------|----------------|-----------------|
| TikTok | International Short Video | Yes | Global (excluding China) |
| YouTube | International Video | Yes | Global |
| Twitter (X) | International Microblog | Yes | Global |
| Instagram | International Photo/Video | Yes | Global |
| Facebook | International Social Network | Yes | Global |
| LinkedIn | International Professional Network | Yes | Global |
| Pinterest | International Visual Discovery | Yes | Global |
| Threads | International Microblog | Yes | Global |
| Douyin (抖音) | Chinese Short Video | Yes | China |
| Xiaohongshu/RED (小红书) | Chinese Lifestyle | No (Cookie-based) | China |
| Kuaishou (快手) | Chinese Short Video | Yes | China |
| Bilibili (哔哩哔哩) | Chinese Video | Yes | China |
| WeChat Video Account (视频号) | Chinese Short Video | No (Cookie-based) | China |
| WeChat Official Account (公众号) | Chinese Blog/Content | Yes | China |

Sources:
- [README.md:18-20]()
- [docker-compose.yml:184-212]()

## Platform Categories

### International Platforms

International platforms primarily use **OAuth 2.0** for authentication and provide RESTful APIs for content management and analytics.

```mermaid
graph TB
    subgraph "International Platforms"
        TikTok["TikTok<br/>Short Video Platform"]
        YouTube["YouTube<br/>Video Platform"]
        Twitter["Twitter/X<br/>Microblogging"]
        Instagram["Instagram<br/>Photo & Video"]
        Facebook["Facebook<br/>Social Network"]
        LinkedIn["LinkedIn<br/>Professional Network"]
        Pinterest["Pinterest<br/>Visual Discovery"]
        Threads["Threads<br/>Text-based Microblog"]
    end
    
    subgraph "OAuth 2.0 Flow"
        AuthServer["Platform OAuth Server"]
        AiToEarn["AiToEarn Backend"]
        UserBrowser["User Browser"]
    end
    
    TikTok --> AuthServer
    YouTube --> AuthServer
    Twitter --> AuthServer
    Instagram --> AuthServer
    Facebook --> AuthServer
    LinkedIn --> AuthServer
    Pinterest --> AuthServer
    Threads --> AuthServer
    
    UserBrowser -->|"1. Authorize"| AuthServer
    AuthServer -->|"2. Callback"| AiToEarn
    AiToEarn -->|"3. Access Token"| AuthServer
```

### Chinese Platforms

Chinese platforms use a mix of **OAuth 2.0** and **cookie-based authentication** depending on the platform's API availability.

```mermaid
graph TB
    subgraph "Chinese Platforms - OAuth"
        Douyin["Douyin 抖音<br/>Short Video"]
        Kuaishou["Kuaishou 快手<br/>Short Video"]
        Bilibili["Bilibili 哔哩哔哩<br/>Video Platform"]
        WxPlat["WeChat Official Account<br/>公众号"]
    end
    
    subgraph "Chinese Platforms - Cookie-based"
        XHS["Xiaohongshu 小红书<br/>Lifestyle Platform"]
        WxSph["WeChat Video Account<br/>视频号"]
    end
    
    subgraph "Authentication Methods"
        OAuth["OAuth 2.0"]
        Cookie["Browser Cookie Capture"]
    end
    
    Douyin --> OAuth
    Kuaishou --> OAuth
    Bilibili --> OAuth
    WxPlat --> OAuth
    
    XHS --> Cookie
    WxSph --> Cookie
```

Sources:
- [README.md:18-20]()
- [docker-compose.yml:184-212]()

## OAuth Configuration Requirements

### OAuth Callback URL Format

All OAuth-based platforms use callback URLs following this pattern:

```
https://{APP_DOMAIN}/api/plat/{platform}/auth/back
```

Where `{APP_DOMAIN}` is configured via the `APP_DOMAIN` environment variable in `aitoearn-server`, and `{platform}` is the platform identifier (e.g., `tiktok`, `youtube`, `twitter`).

**Example callback URLs:**
- TikTok: `https://yourdomain.com/api/plat/tiktok/auth/back`
- YouTube: `https://yourdomain.com/api/plat/youtube/auth/back`
- Twitter: `https://yourdomain.com/api/plat/twitter/auth/back`

Sources:
- [DOCKER_DEPLOYMENT_EN.md:269]()

### Platform OAuth Configuration Table

The following table lists all OAuth configuration requirements per platform. These are set as environment variables in the `aitoearn-server` service.

| Platform | Environment Variables | Developer Console | Notes |
|----------|----------------------|-------------------|-------|
| **TikTok** | `TIKTOK_CLIENT_ID`<br/>`TIKTOK_CLIENT_SECRET` | https://developers.tiktok.com | Requires app approval for publishing capabilities |
| **YouTube** | `YOUTUBE_CLIENT_ID`<br/>`YOUTUBE_CLIENT_SECRET` | https://console.cloud.google.com/apis/credentials | Also requires `GOOGLE_CLIENT_ID/SECRET` for Google OAuth |
| **Twitter/X** | `TWITTER_CLIENT_ID`<br/>`TWITTER_CLIENT_SECRET` | https://developer.x.com/en/portal | OAuth 2.0 with PKCE |
| **Instagram** | `INSTAGRAM_CLIENT_ID`<br/>`INSTAGRAM_CLIENT_SECRET` | https://developers.facebook.com | Part of Facebook Graph API |
| **Facebook** | `FACEBOOK_CLIENT_ID`<br/>`FACEBOOK_CLIENT_SECRET`<br/>`FACEBOOK_CONFIG_ID` | https://developers.facebook.com | Pages API requires specific permissions |
| **LinkedIn** | `LINKEDIN_CLIENT_ID`<br/>`LINKEDIN_CLIENT_SECRET` | https://www.linkedin.com/developers | Requires Marketing Developer Platform access |
| **Pinterest** | `PINTEREST_CLIENT_ID`<br/>`PINTEREST_CLIENT_SECRET`<br/>`PINTEREST_TEST_AUTHORIZATION` | https://developers.pinterest.com | Test authorization for sandbox testing |
| **Threads** | `THREADS_CLIENT_ID`<br/>`THREADS_CLIENT_SECRET` | https://developers.facebook.com | Uses Facebook developer platform |
| **Douyin** | `DOYIN_CLIENT_ID`<br/>`DOYIN_CLIENT_SECRET` | https://open.douyin.com | Chinese TikTok, separate from international TikTok |
| **Kuaishou** | `KWAI_CLIENT_ID`<br/>`KWAI_CLIENT_SECRET` | https://open.kuaishou.com | Requires China-based business registration |
| **Bilibili** | `BILIBILI_CLIENT_ID`<br/>`BILIBILI_CLIENT_SECRET` | https://open.bilibili.com | Video platform OAuth |
| **WeChat Official** | `WXPLAT_APP_ID`<br/>`WXPLAT_APP_SECRET`<br/>`WXPLAT_ENCODING_AES_KEY` | https://mp.weixin.qq.com | Requires verified WeChat Official Account |
| **Google (General)** | `GOOGLE_CLIENT_ID`<br/>`GOOGLE_CLIENT_SECRET` | https://console.cloud.google.com/apis/credentials | Used for YouTube and other Google services |

Sources:
- [docker-compose.yml:184-212]()
- [DOCKER_DEPLOYMENT_EN.md:253-268]()

### OAuth Flow Diagram

OAuth 2.0 Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend["AiToEarn Web Frontend"]
    participant Backend["aitoearn-server"]
    participant Platform["Platform OAuth Server<br/>(TikTok, YouTube, etc.)"]
    participant PlatformAPI["Platform API"]
    
    User->>Frontend: Click "Connect Platform"
    Frontend->>Backend: Initiate OAuth flow
    Backend->>Platform: Redirect to authorization URL
    Platform->>User: Show consent screen
    User->>Platform: Authorize application
    Platform->>Backend: Callback with authorization code
    Backend->>Platform: Exchange code for access token
    Platform-->>Backend: Return access token & refresh token
    Backend->>Backend: Store tokens in MongoDB
    Backend->>PlatformAPI: Fetch user info with token
    PlatformAPI-->>Backend: Return user profile
    Backend-->>Frontend: OAuth success
    Frontend-->>User: Show connected account
```

Sources:
- [docker-compose.yml:136-232]()

## Platform Capabilities Matrix

The following table summarizes the content types and capabilities supported by each platform:

| Platform | Video | Images | Text | Stories | Live | Comments | Analytics | Scheduling |
|----------|-------|--------|------|---------|------|----------|-----------|------------|
| **TikTok** | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ |
| **YouTube** | ✓ | ✗ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ |
| **Twitter/X** | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ |
| **Instagram** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Facebook** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **LinkedIn** | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ |
| **Pinterest** | ✗ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ |
| **Threads** | ✗ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ |
| **Douyin** | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ |
| **Xiaohongshu** | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ |
| **Kuaishou** | ✓ | ✗ | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ |
| **Bilibili** | ✓ | ✗ | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ |
| **WeChat Video** | ✓ | ✗ | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ |
| **WeChat Official** | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ |

**Legend:**
- **Video**: Support for video uploads
- **Images**: Support for image/photo uploads
- **Text**: Support for text-only posts
- **Stories**: Support for ephemeral stories/moments
- **Live**: Support for live streaming
- **Comments**: Support for automated commenting and engagement
- **Analytics**: Support for performance metrics and analytics
- **Scheduling**: Support for scheduled/timed publishing

Sources:
- [README.md:18-20]()
- [README.md:79-156]()

## Platform-Specific Details

### TikTok

**Platform Type:** International Short Video  
**OAuth Required:** Yes  
**Developer Portal:** https://developers.tiktok.com

**Configuration:**
```yaml
TIKTOK_CLIENT_ID: your-client-id
TIKTOK_CLIENT_SECRET: your-client-secret
```

**Key Features:**
- Video publishing with music, effects, and filters
- Image carousel posts (photo mode)
- Duet and Stitch capabilities
- Hashtag and mention support
- Publishing to specific audience (public/friends/private)
- Scheduled publishing

**API Capabilities:**
- Content Publishing API
- User Info API
- Video Management API
- Analytics API

**Callback URL:** `https://{APP_DOMAIN}/api/plat/tiktok/auth/back`

Sources:
- [docker-compose.yml:193-194]()
- [DOCKER_DEPLOYMENT_EN.md:254]()

### YouTube

**Platform Type:** International Video Platform  
**OAuth Required:** Yes  
**Developer Portal:** https://console.cloud.google.com/apis/credentials

**Configuration:**
```yaml
GOOGLE_CLIENT_ID: your-google-client-id
GOOGLE_CLIENT_SECRET: your-google-client-secret
YOUTUBE_CLIENT_ID: your-youtube-client-id
YOUTUBE_CLIENT_SECRET: your-youtube-client-secret
```

**Key Features:**
- Long-form video uploads (up to 12 hours for verified accounts)
- YouTube Shorts support
- Video metadata (title, description, tags, category)
- Thumbnail customization
- Playlist management
- Privacy settings (public/unlisted/private)
- Scheduled publishing

**API Capabilities:**
- YouTube Data API v3
- YouTube Analytics API
- Comment management
- Subscription info

**Callback URL:** `https://{APP_DOMAIN}/api/plat/youtube/auth/back`

Sources:
- [docker-compose.yml:186-187]()
- [docker-compose.yml:206-207]()
- [DOCKER_DEPLOYMENT_EN.md:255]()

### Twitter/X

**Platform Type:** International Microblogging  
**OAuth Required:** Yes (OAuth 2.0 with PKCE)  
**Developer Portal:** https://developer.x.com/en/portal

**Configuration:**
```yaml
TWITTER_CLIENT_ID: your-client-id
TWITTER_CLIENT_SECRET: your-client-secret
```

**Key Features:**
- Text posts up to 280 characters (or longer for Premium)
- Image and video attachments
- Thread creation
- Polls
- Hashtag and mention support
- Quote tweets

**API Capabilities:**
- Twitter API v2
- Tweet creation and management
- User timeline
- Engagement metrics
- Media upload

**Callback URL:** `https://{APP_DOMAIN}/api/plat/twitter/auth/back`

Sources:
- [docker-compose.yml:195-196]()
- [DOCKER_DEPLOYMENT_EN.md:256]()

### Instagram

**Platform Type:** International Photo/Video Platform  
**OAuth Required:** Yes  
**Developer Portal:** https://developers.facebook.com

**Configuration:**
```yaml
FACEBOOK_CLIENT_ID: your-facebook-app-id
FACEBOOK_CLIENT_SECRET: your-facebook-app-secret
INSTAGRAM_CLIENT_ID: your-instagram-client-id
INSTAGRAM_CLIENT_SECRET: your-instagram-client-secret
```

**Key Features:**
- Photo posts (single and carousel)
- Video posts (Reels and feed videos)
- Stories
- IGTV
- Shopping tags
- Location tagging
- Hashtag support

**API Capabilities:**
- Instagram Graph API
- Content Publishing API
- Instagram Insights API
- Comment moderation

**Note:** Requires a Facebook Business account and Instagram Business/Creator account.

**Callback URL:** `https://{APP_DOMAIN}/api/plat/instagram/auth/back`

Sources:
- [docker-compose.yml:197-200]()
- [docker-compose.yml:202-203]()
- [DOCKER_DEPLOYMENT_EN.md:257-258]()

### Facebook

**Platform Type:** International Social Network  
**OAuth Required:** Yes  
**Developer Portal:** https://developers.facebook.com

**Configuration:**
```yaml
FACEBOOK_CLIENT_ID: your-app-id
FACEBOOK_CLIENT_SECRET: your-app-secret
FACEBOOK_CONFIG_ID: your-config-id
```

**Key Features:**
- Text, photo, and video posts
- Stories
- Live video
- Events
- Groups posting
- Page management
- Scheduled posts

**API Capabilities:**
- Facebook Graph API
- Pages API
- Publishing API
- Insights API

**Callback URL:** `https://{APP_DOMAIN}/api/plat/facebook/auth/back`

Sources:
- [docker-compose.yml:197-199]()
- [DOCKER_DEPLOYMENT_EN.md:258]()

### LinkedIn

**Platform Type:** International Professional Network  
**OAuth Required:** Yes  
**Developer Portal:** https://www.linkedin.com/developers

**Configuration:**
```yaml
LINKEDIN_CLIENT_ID: your-client-id
LINKEDIN_CLIENT_SECRET: your-client-secret
```

**Key Features:**
- Professional content posting
- Image and video posts
- Document sharing
- Articles
- Company page management
- Hashtag support
- Scheduled publishing

**API Capabilities:**
- LinkedIn Share API
- UGC Post API
- Organization API
- Analytics API

**Note:** Requires Marketing Developer Platform access for advanced features.

**Callback URL:** `https://{APP_DOMAIN}/api/plat/linkedin/auth/back`

Sources:
- [docker-compose.yml:204-205]()
- [DOCKER_DEPLOYMENT_EN.md:259]()

### Pinterest

**Platform Type:** International Visual Discovery  
**OAuth Required:** Yes  
**Developer Portal:** https://developers.pinterest.com

**Configuration:**
```yaml
PINTEREST_CLIENT_ID: your-client-id
PINTEREST_CLIENT_SECRET: your-client-secret
PINTEREST_TEST_AUTHORIZATION: your-test-auth-token
```

**Key Features:**
- Pin creation (images/videos)
- Board management
- Rich pins
- Shopping features
- Idea pins
- Video pins

**API Capabilities:**
- Pinterest API v5
- Pin creation
- Board management
- Analytics

**Callback URL:** `https://{APP_DOMAIN}/api/plat/pinterest/auth/back`

Sources:
- [docker-compose.yml:190-192]()
- [DOCKER_DEPLOYMENT_EN.md:260]()

### Threads

**Platform Type:** International Text-based Microblog  
**OAuth Required:** Yes  
**Developer Portal:** https://developers.facebook.com

**Configuration:**
```yaml
THREADS_CLIENT_ID: your-client-id
THREADS_CLIENT_SECRET: your-client-secret
```

**Key Features:**
- Text posts up to 500 characters
- Image attachments
- Thread creation
- Mention and hashtag support
- Reply management

**API Capabilities:**
- Threads API (via Facebook platform)
- Post creation
- Insights
- Reply management

**Note:** Uses the same Facebook developer platform.

**Callback URL:** `https://{APP_DOMAIN}/api/plat/threads/auth/back`

Sources:
- [docker-compose.yml:200-201]()
- [DOCKER_DEPLOYMENT_EN.md:261]()

### Douyin (抖音)

**Platform Type:** Chinese Short Video  
**OAuth Required:** Yes  
**Developer Portal:** https://open.douyin.com

**Configuration:**
```yaml
DOYIN_CLIENT_ID: your-client-id
DOYIN_CLIENT_SECRET: your-client-secret
```

**Key Features:**
- Short video publishing (15s-10min)
- Image-text posts (carousel)
- Topic/hashtag support
- Location tagging
- @ mentions
- Privacy settings
- Scheduled publishing
- Comment management

**API Capabilities:**
- Video upload and publish
- Creator dashboard
- Analytics
- Comment API

**Note:** This is separate from international TikTok and requires China-based credentials.

**Callback URL:** `https://{APP_DOMAIN}/api/plat/douyin/auth/back`

Sources:
- [docker-compose.yml:211-212]()
- [DOCKER_DEPLOYMENT_EN.md:262]()

### Xiaohongshu / RED (小红书)

**Platform Type:** Chinese Lifestyle Platform  
**OAuth Required:** No (Cookie-based authentication)  
**Official Website:** https://www.xiaohongshu.com

**Authentication Method:** Browser cookie capture

**Key Features:**
- Image-text posts (lifestyle notes)
- Video posts
- Product tagging
- Location tagging
- Topic/hashtag support
- @ mentions
- Comment and like management

**API Capabilities:**
- Custom publishing API (via browser automation)
- Content management
- Comment retrieval
- Analytics

**Note:** Does not provide official OAuth API. Uses cookie-based authentication via browser automation.

Sources:
- [README.md:19]()

### Kuaishou (快手)

**Platform Type:** Chinese Short Video  
**OAuth Required:** Yes  
**Developer Portal:** https://open.kuaishou.com

**Configuration:**
```yaml
KWAI_CLIENT_ID: your-client-id
KWAI_CLIENT_SECRET: your-client-secret
```

**Key Features:**
- Short video publishing
- Live streaming support
- Topic/hashtag support
- Location tagging
- Comment management
- Privacy controls

**API Capabilities:**
- Video upload and publish
- User info
- Analytics
- Comment API

**Note:** Requires China-based business registration.

**Callback URL:** `https://{APP_DOMAIN}/api/plat/kuaishou/auth/back`

Sources:
- [docker-compose.yml:188-189]()
- [DOCKER_DEPLOYMENT_EN.md:263]()

### Bilibili (哔哩哔哩)

**Platform Type:** Chinese Video Platform  
**OAuth Required:** Yes  
**Developer Portal:** https://open.bilibili.com

**Configuration:**
```yaml
BILIBILI_CLIENT_ID: your-client-id
BILIBILI_CLIENT_SECRET: your-client-secret
```

**Key Features:**
- Long-form video uploads
- Multi-part video series
- Video categories
- Tags and topics
- Comment management
- Danmaku (bullet comments)
- Video analytics

**API Capabilities:**
- Video upload
- User info
- Video management
- Analytics

**Callback URL:** `https://{APP_DOMAIN}/api/plat/bilibili/auth/back`

Sources:
- [docker-compose.yml:184-185]()
- [DOCKER_DEPLOYMENT_EN.md:264]()

### WeChat Video Account (视频号)

**Platform Type:** Chinese Short Video  
**OAuth Required:** No (Cookie-based authentication)  
**Official Platform:** WeChat ecosystem

**Authentication Method:** Browser cookie capture via WeChat web interface

**Key Features:**
- Short video publishing
- Image-text posts
- WeChat integration
- Comment management
- Privacy controls

**API Capabilities:**
- Custom publishing API (via browser automation)
- Content management
- Analytics

**Note:** No official public API. Uses cookie-based authentication.

Sources:
- [README.md:19]()

### WeChat Official Account (公众号)

**Platform Type:** Chinese Blog/Content Platform  
**OAuth Required:** Yes  
**Developer Portal:** https://mp.weixin.qq.com

**Configuration:**
```yaml
WXPLAT_APP_ID: your-app-id
WXPLAT_APP_SECRET: your-app-secret
WXPLAT_ENCODING_AES_KEY: your-aes-key
```

**Key Features:**
- Article publishing
- Rich media (images, video, audio)
- Custom menus
- Message management
- User management
- Material library

**API Capabilities:**
- WeChat Official Account API
- Material upload
- Message sending
- User analytics

**Note:** Requires a verified WeChat Official Account.

**Callback URL:** `https://{APP_DOMAIN}/api/plat/wxplat/auth/back`

Sources:
- [docker-compose.yml:208-210]()
- [DOCKER_DEPLOYMENT_EN.md:267]()

## Platform-Specific Service Implementations

Each platform implementation uses a platform-specific service class to handle the low-level API interactions:

### Platform Service Classes

```mermaid
classDiagram
    direction LR
    
    class DouyinService {
        +loginOrView()
        +checkLoginStatus()
        +getUserInfo()
        +getDashboardFunc()
        +publishVideoWorkApi()
        +publishImageWorkApi()
        +getCreatorCommentList()
        +creatorCommentReply()
        +getTopics()
        +getUsers()
        +getLocationData()
    }
    
    class XiaohongshuService {
        +loginOrView()
        +getUserInfo()
        +getDashboardFunc()
        +publishVideoWorkApi()
        +publishImageWorkApi()
        +getCommentList()
        +commentPost()
        +getTopics()
        +getUsers()
        +getLocationData()
    }
    
    class ShipinhaoService {
        +loginOrView()
        +checkLoginStatus()
        +getUserInfo()
        +getDashboardFunc()
        +publishVideoWorkApi()
        +getCommentList()
        +createComment()
        +getTopics()
        +getUsers()
        +getLocationData()
    }
    
    class KwaiPub {
        +login()
        +getAccountInfo()
        +pubVideo()
        +getHomeInfo()
        +getHomeOverview()
        +getCommentList()
        +commentAdd()
        +getTopics()
        +getUsers()
        +getLocations()
    }
```

Sources:
- [electron/plat/douyin/index.ts:66-673](electron/plat/douyin/index.ts:66-673)
- [electron/plat/xiaohongshu/index.ts:48-760](electron/plat/xiaohongshu/index.ts:48-760)
- [electron/plat/shipinhao/index.ts:35-345](electron/plat/shipinhao/index.ts:35-345)
- [electron/plat/Kwai/index.ts:34-759](electron/plat/Kwai/index.ts:34-759)

### Authentication Methods

Platform services vary in how they handle authentication:

| Platform | Authentication Method |
|----------|----------------------|
| Douyin | Browser window with cookie capture |
| Xiaohongshu | Browser window with cookie and token capture |
| WeChat Video | Browser window with multiple URL redirections |
| Kuaishou | Browser window with session tokens |

Sources:
- [electron/plat/douyin/index.ts:98-152](electron/plat/douyin/index.ts:98-152)
- [electron/plat/xiaohongshu/index.ts:73-109](electron/plat/xiaohongshu/index.ts:73-109)
- [electron/plat/shipinhao/index.ts:73-109](electron/plat/shipinhao/index.ts:73-109)
- [electron/plat/Kwai/index.ts:274-349](electron/plat/Kwai/index.ts:274-349)

### API Communication Patterns

Each platform service uses slightly different API communication patterns:

- **Douyin**: Uses a combination of direct API requests and Electron browser window capture
- **Xiaohongshu**: Relies on a signature mechanism for API requests
- **WeChat Video Account**: Uses a web-based authentication and API pattern
- **Kuaishou**: Utilizes a custom signing mechanism for API requests

Sources:
- [electron/plat/douyin/index.ts:853-893](electron/plat/douyin/index.ts:853-893)
- [electron/plat/xiaohongshu/index.ts:406-447](electron/plat/xiaohongshu/index.ts:406-447)
- [electron/plat/Kwai/index.ts:224-260](electron/plat/Kwai/index.ts:224-260)

## Platform Controller Usage

The platform implementations are typically accessed through a controller layer that manages platform selection and method delegation:

```mermaid
flowchart LR
    A["Client/UI"] --> B["PlatController"]
    B --> C{"Select Platform"}
    C -->|"AccountType.Douyin"| D["Douyin"]
    C -->|"AccountType.Xhs"| E["Xhs"]
    C -->|"AccountType.WxSph"| F["WxSph"]
    C -->|"AccountType.KWAI"| G["Kwai"]
    
    D --> H["douyinService"]
    E --> I["xiaohongshuService"] 
    F --> J["shipinhaoService"]
    G --> K["kwaiPub"]
    
    H --> L["Douyin API"]
    I --> M["Xiaohongshu API"]
    J --> N["WeChat Video API"]
    K --> O["Kuaishou API"]
```

The account service uses the platform controller to interact with any platform:

```typescript
async getAccountDashboard(account: AccountModel, time?: [string, string]) {
  return await platController.getDashboard(account, time);
}
```

Sources:
- [electron/main/account/service.ts:118-121](electron/main/account/service.ts:118-121)

## Extension Points

The platform implementation architecture is designed to be extensible:

1. New platforms can be added by:
   - Creating a new class that extends `PlatformBase`
   - Implementing a platform-specific service
   - Registering the implementation with the platform controller

2. Existing implementations can be enhanced by:
   - Adding new methods to the platform implementation class
   - Extending the platform service with new API functionality

Sources:
- [electron/main/plat/platforms/douyin/index.ts:674-675](electron/main/plat/platforms/douyin/index.ts:674-675)
- [electron/main/plat/platforms/xhs/index.ts:660-661](electron/main/plat/platforms/xhs/index.ts:660-661)
- [electron/main/plat/platforms/wxSph/index.ts:485-486](electron/main/plat/platforms/wxSph/index.ts:485-486)
- [electron/main/plat/platforms/Kwai/index.ts:579-580](electron/main/plat/platforms/Kwai/index.ts:579-580)

## Limitations and Considerations

When working with platform implementations, consider the following:

1. **Authentication Expiration**: Platform cookies and tokens may expire, requiring re-authentication
2. **API Changes**: Platform APIs may change without notice, requiring implementation updates
3. **Rate Limiting**: Platforms may impose rate limits that affect reliability
4. **Content Moderation**: Posted content may be subject to platform-specific moderation rules

For platform-specific details, refer to the dedicated pages for each platform:
- [Douyin Integration](#3.2.1)
- [Kuaishou Integration](#3.2.2)

---

# Page: Multi-Platform Publishing

# Multi-Platform Publishing

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



This document describes the multi-platform content publishing system that enables one-click distribution of content across 14+ social media platforms. The publishing system handles platform authentication, content adaptation, API integration, scheduling, and error recovery.

For information about OAuth authentication with third-party platforms, see [OAuth Authentication Flow](#4.1). For details on content scheduling, see [Calendar Timing and Scheduling](#5.2). For content creation before publishing, see [Content Creation and AI Generation](#5.1).

---

## Overview

The multi-platform publishing system is a core feature of AiToEarn that allows users to distribute content to multiple social media platforms simultaneously. The system abstracts the complexity of different platform APIs, authentication mechanisms, and content format requirements into a unified publishing workflow.

**Key Capabilities:**
- **One-click distribution**: Publish to multiple platforms from a single interface
- **Scheduled publishing**: Queue content for future publication via the calendar timing system
- **Content adaptation**: Automatically format content according to each platform's requirements
- **OAuth management**: Handle authentication tokens and re-authorization flows
- **Error recovery**: Retry failed publications with exponential backoff
- **Status tracking**: Monitor publication status across all platforms

**Supported Platforms:**

| Platform | Region | Content Types | OAuth Required |
|----------|--------|---------------|----------------|
| TikTok | Global | Video, Images | Yes |
| YouTube | Global | Video | Yes |
| Twitter/X | Global | Text, Images, Video | Yes |
| Instagram | Global | Images, Video, Reels | Yes |
| Facebook | Global | Text, Images, Video | Yes |
| LinkedIn | Global | Text, Images, Articles | Yes |
| Threads | Global | Text, Images | Yes |
| Pinterest | Global | Images, Boards | Yes |
| Douyin (抖音) | China | Video, Images | Yes |
| Bilibili | China | Video | Yes |
| Kuaishou (快手) | China | Video | Yes |
| WeChat Channels (视频号) | China | Video | Yes |
| WeChat Official Accounts | China | Articles, Images | Yes |
| Xiaohongshu (小红书) | China | Images, Text, Video | Yes |

Sources: [README.md:18-20](), [README.md:81](), [docker-compose.yml:184-212](), [DOCKER_DEPLOYMENT_EN.md:252-268]()

---

## System Architecture

### Service Components

The multi-platform publishing system spans multiple services in the AiToEarn architecture:

```mermaid
graph TB
    subgraph "Frontend Layer"
        WebUI["aitoearn-web<br/>Next.js Frontend"]
    end
    
    subgraph "Backend Services"
        Server["aitoearn-server<br/>NestJS API<br/>:3002"]
        AI["aitoearn-ai<br/>NestJS AI Service<br/>:3010"]
    end
    
    subgraph "Data Layer"
        MongoDB[("MongoDB<br/>:27017<br/>- Draft Storage<br/>- OAuth Tokens<br/>- Publish Metadata")]
        Redis[("Redis<br/>:6379<br/>- Job Queue<br/>- Retry Queue<br/>- Rate Limiting")]
        RustFS[("RustFS<br/>:9000<br/>Asset Storage")]
    end
    
    subgraph "External Platforms"
        TikTok["TikTok API"]
        YouTube["YouTube API"]
        Twitter["Twitter/X API"]
        Instagram["Instagram API"]
        LinkedIn["LinkedIn API"]
        Facebook["Facebook API"]
        Douyin["Douyin API"]
        Bilibili["Bilibili API"]
        Others["Other Platform APIs"]
    end
    
    WebUI -->|"1. Publish Request"| Server
    Server -->|"2. Content Generation (Optional)"| AI
    Server -->|"3. Read Draft"| MongoDB
    Server -->|"4. Fetch Assets"| RustFS
    Server -->|"5. Queue Jobs"| Redis
    Server -->|"6. OAuth Validation"| MongoDB
    Server -.->|"7. API Calls"| TikTok
    Server -.->|"7. API Calls"| YouTube
    Server -.->|"7. API Calls"| Twitter
    Server -.->|"7. API Calls"| Instagram
    Server -.->|"7. API Calls"| LinkedIn
    Server -.->|"7. API Calls"| Facebook
    Server -.->|"7. API Calls"| Douyin
    Server -.->|"7. API Calls"| Bilibili
    Server -.->|"7. API Calls"| Others
    Server -->|"8. Store Results"| MongoDB
    Server -->|"9. Update Queue"| Redis
```

**Component Responsibilities:**

- **aitoearn-web**: User interface for selecting platforms, previewing content, and initiating publication
- **aitoearn-server**: Core publishing orchestration, OAuth token management, platform API integration
- **MongoDB**: Persistent storage for drafts, OAuth tokens (encrypted), and publication metadata
- **Redis**: Job queue for scheduled publications, retry queue for failed attempts, rate limiting counters
- **RustFS**: S3-compatible storage for media assets (images, videos) to be uploaded to platforms

Sources: [docker-compose.yml:2-286](), High-level architecture diagrams

---

### Publishing Data Flow

```mermaid
sequenceDiagram
    participant User
    participant WebUI as "aitoearn-web"
    participant Server as "aitoearn-server"
    participant MongoDB
    participant Redis
    participant RustFS
    participant PlatformAPI as "Platform API"
    
    User->>WebUI: Select platforms & initiate publish
    WebUI->>Server: POST /api/publish
    
    Server->>MongoDB: Fetch draft content
    MongoDB-->>Server: Draft data
    
    Server->>MongoDB: Validate OAuth tokens
    alt Token Expired
        Server-->>WebUI: OAuth re-auth required
        WebUI-->>User: Redirect to OAuth flow
    end
    
    Server->>RustFS: Fetch media assets
    RustFS-->>Server: Asset URLs/data
    
    alt Immediate Publish
        Server->>Server: Adapt content for each platform
        loop For each selected platform
            Server->>PlatformAPI: POST content
            alt Success
                PlatformAPI-->>Server: Post ID, URL
                Server->>MongoDB: Store publish metadata
            else Failure
                PlatformAPI-->>Server: Error response
                Server->>Redis: Enqueue retry job
                Server->>MongoDB: Store error status
            end
        end
        Server-->>WebUI: Publish results
    else Scheduled Publish
        Server->>Redis: Enqueue scheduled job
        Server->>MongoDB: Store scheduled status
        Server-->>WebUI: Scheduled confirmation
    end
    
    Note over Redis,PlatformAPI: Background Job Processing
    Redis->>Server: Process scheduled/retry job
    Server->>PlatformAPI: POST content
    PlatformAPI-->>Server: Response
    Server->>MongoDB: Update status
```

Sources: High-level workflow diagram, [docker-compose.yml:136-232]()

---

## Publishing Workflow

### 1. Content Preparation

Before publishing, content must exist as a **draft** in the system. Drafts are stored in MongoDB and contain:

- **Text content**: Title, description, captions, hashtags
- **Media references**: Pointers to assets in RustFS (images, videos)
- **Platform-specific metadata**: Custom fields for different platforms
- **Scheduling information**: Publish time if scheduled

Drafts can be created through:
- Manual content creation in the web interface
- AI-powered generation (via `aitoearn-ai` service)
- Import from other platforms
- Template-based creation

Sources: [README.md:82-85](), [README_CN.md:69-70](), High-level data flow diagram

---

### 2. Platform Selection

Users select which platforms to publish to through the web interface. The system supports:

- **Individual platform selection**: Choose specific platforms from the list
- **Platform groups**: Pre-configured groups (e.g., "All Western Platforms", "All Chinese Platforms")
- **Previous selections**: Remember last used platform combination

The interface shows platform status indicators:
- ✓ Connected (OAuth token valid)
- ⚠ Re-authentication required (token expired)
- ✗ Not connected

Sources: [README.md:79-85]()

---

### 3. OAuth Token Validation

Before publishing, the `aitoearn-server` validates OAuth tokens for selected platforms:

```mermaid
graph TD
    Start["Start Publish Request"]
    CheckTokens["Validate OAuth Tokens<br/>for Selected Platforms"]
    AllValid{"All Tokens<br/>Valid?"}
    AdaptContent["Adapt Content<br/>for Each Platform"]
    PublishAPI["Call Platform APIs"]
    
    ReAuthRequired["Return Re-auth Required"]
    ReAuthFlow["User Re-authenticates"]
    RetryPublish["Retry Publish"]
    
    Start --> CheckTokens
    CheckTokens --> AllValid
    AllValid -->|Yes| AdaptContent
    AllValid -->|No| ReAuthRequired
    ReAuthRequired --> ReAuthFlow
    ReAuthFlow --> RetryPublish
    RetryPublish --> CheckTokens
    AdaptContent --> PublishAPI
```

**Token Storage:**
- OAuth tokens are stored in MongoDB (encrypted)
- Token expiration times are tracked
- Refresh tokens are used to renew access tokens when possible

**OAuth Configuration:**
OAuth credentials for each platform are configured via environment variables in `docker-compose.yml`:

| Platform | Environment Variables | Callback URL |
|----------|----------------------|--------------|
| TikTok | `TIKTOK_CLIENT_ID`, `TIKTOK_CLIENT_SECRET` | `https://{APP_DOMAIN}/api/plat/tiktok/auth/back` |
| YouTube | `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET` | `https://{APP_DOMAIN}/api/plat/youtube/auth/back` |
| Twitter/X | `TWITTER_CLIENT_ID`, `TWITTER_CLIENT_SECRET` | `https://{APP_DOMAIN}/api/plat/twitter/auth/back` |
| Facebook | `FACEBOOK_CLIENT_ID`, `FACEBOOK_CLIENT_SECRET`, `FACEBOOK_CONFIG_ID` | `https://{APP_DOMAIN}/api/plat/facebook/auth/back` |
| Instagram | `INSTAGRAM_CLIENT_ID`, `INSTAGRAM_CLIENT_SECRET` | `https://{APP_DOMAIN}/api/plat/instagram/auth/back` |
| LinkedIn | `LINKEDIN_CLIENT_ID`, `LINKEDIN_CLIENT_SECRET` | `https://{APP_DOMAIN}/api/plat/linkedin/auth/back` |
| Douyin | `DOYIN_CLIENT_ID`, `DOYIN_CLIENT_SECRET` | `https://{APP_DOMAIN}/api/plat/douyin/auth/back` |

The `APP_DOMAIN` environment variable must be set to the public domain for OAuth callbacks to work correctly.

Sources: [docker-compose.yml:184-212](), [DOCKER_DEPLOYMENT_EN.md:252-270](), [DOCKER_DEPLOYMENT_CN.md:252-270]()

---

### 4. Content Adaptation

Each platform has different requirements for content format, media specifications, and metadata. The publishing system adapts content automatically:

**Text Adaptation:**
- **Character limits**: Truncate or split content (Twitter: 280 chars, LinkedIn: 3000 chars)
- **Hashtag formatting**: Platform-specific hashtag rules
- **Mention syntax**: Different platforms use different mention formats
- **Link handling**: Some platforms require URL shortening

**Media Adaptation:**
- **Video encoding**: Re-encode videos to meet platform requirements (codec, resolution, bitrate)
- **Image resizing**: Resize images to optimal dimensions for each platform
- **Aspect ratio**: Adjust for platform-specific aspect ratios (1:1, 16:9, 9:16)
- **File size limits**: Compress media to meet platform limits

**Metadata Mapping:**
```mermaid
graph LR
    Draft["Draft Content<br/>- Title<br/>- Description<br/>- Hashtags<br/>- Media"]
    
    TikTokPost["TikTok Post<br/>- description<br/>- video_id<br/>- privacy_level"]
    
    YouTubeVideo["YouTube Video<br/>- title<br/>- description<br/>- tags<br/>- categoryId"]
    
    TwitterTweet["Twitter Tweet<br/>- text<br/>- media_ids<br/>- poll_options"]
    
    InstagramPost["Instagram Post<br/>- caption<br/>- media_type<br/>- location"]
    
    Draft --> TikTokPost
    Draft --> YouTubeVideo
    Draft --> TwitterTweet
    Draft --> InstagramPost
```

Sources: [README.md:79-85](), High-level data flow diagram

---

### 5. API Calls and Publishing

The `aitoearn-server` makes HTTP requests to each platform's API:

```mermaid
graph TB
    Server["aitoearn-server"]
    
    subgraph "Platform APIs"
        TikTokAPI["TikTok Content Posting API<br/>POST /share/video/upload/"]
        YouTubeAPI["YouTube Data API v3<br/>POST /youtube/v3/videos"]
        TwitterAPI["Twitter API v2<br/>POST /2/tweets"]
        FacebookAPI["Facebook Graph API<br/>POST /{page-id}/feed"]
        InstagramAPI["Instagram Graph API<br/>POST /{ig-user-id}/media"]
        LinkedInAPI["LinkedIn Share API<br/>POST /v2/ugcPosts"]
    end
    
    subgraph "Response Handling"
        Success["200 OK<br/>Store Post ID & URL"]
        RateLimit["429 Rate Limit<br/>Enqueue Retry"]
        AuthError["401 Unauthorized<br/>Flag Re-auth Needed"]
        ServerError["5xx Server Error<br/>Enqueue Retry"]
        ValidationError["400 Bad Request<br/>Log Error Details"]
    end
    
    Server -->|OAuth Bearer Token| TikTokAPI
    Server -->|OAuth Bearer Token| YouTubeAPI
    Server -->|OAuth Bearer Token| TwitterAPI
    Server -->|OAuth Bearer Token| FacebookAPI
    Server -->|OAuth Bearer Token| InstagramAPI
    Server -->|OAuth Bearer Token| LinkedInAPI
    
    TikTokAPI --> Success
    TikTokAPI --> RateLimit
    TikTokAPI --> AuthError
    TikTokAPI --> ServerError
    TikTokAPI --> ValidationError
```

**API Integration Points:**

Each platform has its own API implementation within `aitoearn-server`. While specific code files are not provided, the integration follows this pattern:

- **Request construction**: Build platform-specific request payload
- **Authentication**: Attach OAuth bearer token from MongoDB
- **Media upload**: Upload assets from RustFS to platform's media endpoints
- **Post creation**: Submit post/video/tweet with media references
- **Response parsing**: Extract post ID, URL, and status

**Rate Limiting:**

The system implements rate limiting using Redis counters to avoid exceeding platform API limits:

- Track requests per platform per time window
- Apply backoff when approaching limits
- Queue excess requests for later processing

Sources: [docker-compose.yml:105-107](), [DOCKER_DEPLOYMENT_EN.md:154-161]()

---

### 6. Status Tracking and Storage

After publishing, metadata is stored in MongoDB:

**Publication Record Structure:**
```javascript
{
  draftId: ObjectId,
  platform: 'tiktok',
  status: 'published' | 'failed' | 'scheduled' | 'processing',
  publishedAt: ISODate,
  platformPostId: '7123456789',
  platformUrl: 'https://tiktok.com/@user/video/7123456789',
  errorMessage: null,
  retryCount: 0,
  scheduledFor: null,
  metadata: {
    views: 0,
    likes: 0,
    comments: 0,
    shares: 0
  }
}
```

This data feeds into the Analytics Dashboard (see [Analytics Dashboard](#6.2)).

Sources: High-level data flow diagram, [docker-compose.yml:157-165]()

---

## Scheduled Publishing

The multi-platform publishing system integrates with the Calendar Timing system (see [Calendar Timing and Scheduling](#5.2)) to support scheduled content distribution.

### Scheduling Workflow

```mermaid
graph TD
    User["User Schedules Post"]
    CalendarUI["Calendar Timing UI"]
    Server["aitoearn-server"]
    Redis["Redis Job Queue"]
    JobProcessor["Background Job Processor"]
    Publish["Execute Publish"]
    
    User --> CalendarUI
    CalendarUI -->|"POST /api/schedule"| Server
    Server -->|"Create Scheduled Job"| Redis
    Server -->|"Store Schedule"| MongoDB
    
    Redis -.->|"At Scheduled Time"| JobProcessor
    JobProcessor --> Publish
    Publish -->|"Same as Immediate Publish"| PlatformAPIs["Platform APIs"]
```

**Scheduled Job Structure in Redis:**
```javascript
{
  jobId: 'schedule:draft:abc123:1234567890',
  type: 'scheduled_publish',
  draftId: 'abc123',
  platforms: ['tiktok', 'youtube', 'twitter'],
  scheduledTime: 1234567890,
  retryAttempts: 0,
  status: 'pending'
}
```

**Calendar Timing Features:**
- **Drag-and-drop scheduling**: Visual interface for scheduling posts
- **Multi-platform coordination**: Schedule same content to different platforms at different times
- **Timezone handling**: Support for different user timezones
- **Conflict detection**: Warn about multiple posts scheduled too close together

Sources: [README.md:85-89](), [DOCKER_DEPLOYMENT_EN.md:154-161]()

---

## Error Handling and Retry Mechanism

### Failure Scenarios

The publishing system handles various failure scenarios:

| Failure Type | Detection | Action |
|--------------|-----------|--------|
| **OAuth Token Expired** | 401 Unauthorized response | Flag for re-authentication, don't retry |
| **Rate Limit Exceeded** | 429 Too Many Requests | Exponential backoff retry |
| **Platform Server Error** | 5xx response | Immediate retry up to 3 times |
| **Network Timeout** | Request timeout | Exponential backoff retry |
| **Invalid Content** | 400 Bad Request | Log error, notify user, don't retry |
| **Media Upload Failure** | Upload endpoint error | Retry upload, then retry post |

### Retry Queue System

```mermaid
graph TB
    FailedPublish["Failed Publish Attempt"]
    CheckRetryCount{"Retry Count<br/>< Max?"}
    EnqueueRetry["Enqueue Retry Job<br/>in Redis"]
    CalculateBackoff["Calculate Exponential<br/>Backoff Delay"]
    WaitDelay["Wait for Delay"]
    ProcessRetry["Process Retry Job"]
    AttemptPublish["Attempt Publish"]
    CheckSuccess{"Success?"}
    UpdateSuccess["Update Status:<br/>Published"]
    UpdateFailed["Update Status:<br/>Permanently Failed"]
    NotifyUser["Notify User"]
    
    FailedPublish --> CheckRetryCount
    CheckRetryCount -->|Yes| EnqueueRetry
    CheckRetryCount -->|No| UpdateFailed
    EnqueueRetry --> CalculateBackoff
    CalculateBackoff --> WaitDelay
    WaitDelay --> ProcessRetry
    ProcessRetry --> AttemptPublish
    AttemptPublish --> CheckSuccess
    CheckSuccess -->|Yes| UpdateSuccess
    CheckSuccess -->|No| CheckRetryCount
    UpdateFailed --> NotifyUser
    UpdateSuccess --> NotifyUser
```

**Retry Configuration:**
- **Max retry attempts**: 5
- **Backoff calculation**: `delay = base_delay * (2 ^ attempt_count)`
- **Base delay**: 60 seconds
- **Max delay**: 1 hour

**Retry Job Storage in Redis:**
```javascript
// Redis key: retry:publish:{draftId}:{platform}
{
  draftId: 'abc123',
  platform: 'tiktok',
  attemptCount: 2,
  lastError: 'Rate limit exceeded',
  nextRetryAt: 1234567890,
  originalScheduledTime: 1234560000
}
```

Sources: High-level data flow diagram, [docker-compose.yml:23-39]()

---

## Platform-Specific Considerations

### Video Platforms (TikTok, YouTube, Douyin, Bilibili)

**Video Upload Process:**
1. Download video from RustFS
2. Validate video codec, resolution, duration
3. Upload to platform's media endpoint (chunk upload for large files)
4. Poll for processing status
5. Create post with processed video ID

**Platform Requirements:**

| Platform | Max Size | Duration | Aspect Ratio | Codec |
|----------|----------|----------|--------------|-------|
| TikTok | 287.6 MB | 15s-10min | 9:16 (vertical) | H.264 |
| YouTube | 256 GB | No limit | Any | H.264, VP9 |
| Douyin | 300 MB | 15s-15min | 9:16 (vertical) | H.264 |
| Bilibili | 8 GB | No limit | 16:9 (horizontal) | H.264 |

Sources: [README.md:18-20]()

---

### Image Platforms (Instagram, Pinterest, Xiaohongshu)

**Image Upload Process:**
1. Fetch image from RustFS
2. Resize/crop to platform specifications
3. Upload to platform's media endpoint
4. Create post with uploaded image ID

**Platform Requirements:**

| Platform | Max Size | Dimensions | Format | Multiple Images |
|----------|----------|------------|--------|-----------------|
| Instagram | 30 MB | 1080x1080 (square) | JPG, PNG | Up to 10 (carousel) |
| Pinterest | 32 MB | 2:3 ratio recommended | JPG, PNG | 1 per Pin |
| Xiaohongshu | 20 MB | 3:4 ratio recommended | JPG | Up to 9 per post |

Sources: [README.md:81]()

---

### Text Platforms (Twitter/X, LinkedIn, Threads)

**Text Post Process:**
1. Format text content with hashtags and mentions
2. Upload media (if any) to media endpoint
3. Create tweet/post with media IDs
4. Handle thread creation for long content

**Platform Requirements:**

| Platform | Text Limit | Hashtag Limit | Media Limit |
|----------|------------|---------------|-------------|
| Twitter/X | 280 chars | 2-3 recommended | 4 images or 1 video |
| LinkedIn | 3000 chars | 3-5 recommended | 9 images or 1 video |
| Threads | 500 chars | No limit | 10 images or 1 video |

Sources: [README.md:81]()

---

### Chinese Platforms (WeChat Channels, WeChat Official Accounts)

**WeChat Official Accounts:**
- Uses different OAuth flow (WXPLAT_APP_ID, WXPLAT_APP_SECRET)
- Requires article HTML formatting
- Supports rich media embeds
- Special AES key for message encryption: WXPLAT_ENCODING_AES_KEY

**WeChat Channels (视频号):**
- Video-only platform
- Tight integration with WeChat ecosystem
- Requires real-name verification

Configuration in `docker-compose.yml`:
```yaml
WXPLAT_APP_ID: ""
WXPLAT_APP_SECRET: ""
WXPLAT_ENCODING_AES_KEY: ""
```

Sources: [docker-compose.yml:208-210](), [DOCKER_DEPLOYMENT_EN.md:266]()

---

## Integration with Other Systems

### Content Creation Pipeline

```mermaid
graph LR
    AIGen["AI Content<br/>Generation<br/>(aitoearn-ai)"]
    Draft["Draft<br/>Management<br/>(MongoDB)"]
    Hotspot["Hotspot<br/>Analysis"]
    Publish["Multi-Platform<br/>Publishing"]
    Analytics["Analytics<br/>Collection"]
    
    AIGen -->|"Generate Content"| Draft
    Hotspot -->|"Optimize Content"| Draft
    Draft -->|"Select & Publish"| Publish
    Publish -->|"Track Results"| Analytics
    Analytics -.->|"Feedback Loop"| AIGen
```

**Integration Points:**

1. **AI Generation** (see [Content Creation and AI Generation](#5.1)):
   - `aitoearn-ai` generates draft content
   - Draft saved to MongoDB
   - User selects platforms for publishing

2. **Hotspot Analysis** (see [Hotspot Analysis and Trending Content](#5.3)):
   - Trending topics inform content creation
   - AI optimizes content for better engagement
   - Published to platforms most likely to amplify

3. **Calendar Timing** (see [Calendar Timing and Scheduling](#5.2)):
   - Visual interface for scheduling posts
   - Redis job queue manages scheduled publications
   - Supports complex multi-platform schedules

4. **Analytics Dashboard** (see [Analytics Dashboard](#6.2)):
   - Collects post performance data from platforms
   - Stores in statistics database
   - Displays cross-platform metrics

Sources: High-level functional domain diagram

---

## Configuration Reference

### Environment Variables

The following environment variables in `docker-compose.yml` control multi-platform publishing:

**OAuth Credentials (aitoearn-server service):**

```yaml
# Western Platforms
TIKTOK_CLIENT_ID: ""
TIKTOK_CLIENT_SECRET: ""
YOUTUBE_CLIENT_ID: ""
YOUTUBE_CLIENT_SECRET: ""
TWITTER_CLIENT_ID: ""
TWITTER_CLIENT_SECRET: ""
FACEBOOK_CLIENT_ID: ""
FACEBOOK_CLIENT_SECRET: ""
FACEBOOK_CONFIG_ID: ""
INSTAGRAM_CLIENT_ID: ""
INSTAGRAM_CLIENT_SECRET: ""
LINKEDIN_CLIENT_ID: ""
LINKEDIN_CLIENT_SECRET: ""
THREADS_CLIENT_ID: ""
THREADS_CLIENT_SECRET: ""
PINTEREST_CLIENT_ID: ""
PINTEREST_CLIENT_SECRET: ""
PINTEREST_TEST_AUTHORIZATION: ""

# Chinese Platforms
DOYIN_CLIENT_ID: ""
DOYIN_CLIENT_SECRET: ""
BILIBILI_CLIENT_ID: ""
BILIBILI_CLIENT_SECRET: ""
KWAI_CLIENT_ID: ""
KWAI_CLIENT_SECRET: ""
WXPLAT_APP_ID: ""
WXPLAT_APP_SECRET: ""
WXPLAT_ENCODING_AES_KEY: ""
```

**Domain Configuration:**
```yaml
APP_DOMAIN: localhost  # Change to your public domain for OAuth callbacks
```

OAuth callback URLs follow the pattern: `https://{APP_DOMAIN}/api/plat/{platform}/auth/back`

Sources: [docker-compose.yml:183-212](), [DOCKER_DEPLOYMENT_EN.md:140-151](), [DOCKER_DEPLOYMENT_CN.md:64-91]()

---

### Service Configuration Files

**config/aitoearn-server.config.js:**

This file contains platform-specific configuration including:
- OAuth redirect URIs
- API endpoints for each platform
- Rate limiting configurations
- Media upload specifications

The config file reads from environment variables set in `docker-compose.yml`.

Sources: [docker-compose.yml:148](), [DOCKER_DEPLOYMENT_EN.md:96-110]()

---

## Deployment Considerations

### Production Deployment

When deploying the multi-platform publishing system in production:

1. **Set APP_DOMAIN**: Configure the public domain for OAuth callbacks
   ```yaml
   APP_DOMAIN: your-domain.com
   ```

2. **Configure OAuth Credentials**: Obtain and set credentials for each platform you want to support

3. **Storage Setup**: Ensure RustFS or S3-compatible storage is properly configured for media assets

4. **Rate Limiting**: Monitor Redis for rate limit counters and adjust publishing schedules if needed

5. **Error Monitoring**: Set up logging and alerting for failed publications

6. **Database Backups**: Regular backups of MongoDB to preserve OAuth tokens and publication history

Sources: [DOCKER_DEPLOYMENT_EN.md:54-135](), [DOCKER_DEPLOYMENT_CN.md:54-177]()

---

### Scaling Considerations

For high-volume publishing scenarios:

**Horizontal Scaling:**
- Multiple `aitoearn-server` instances can process publishing jobs in parallel
- Redis job queue provides distributed coordination
- MongoDB replica set for read scaling

**Rate Limiting Strategies:**
- Per-platform rate limit counters in Redis
- Automatic backoff when approaching limits
- Priority queue for important posts

**Media Processing:**
- Consider dedicated video encoding service
- CDN for RustFS asset delivery
- Pre-processing media during draft creation

Sources: High-level deployment architecture diagram, [docker-compose.yml:136-232]()

---

## Summary

The multi-platform publishing system is the core distribution mechanism of AiToEarn, enabling creators to amplify their reach across 14+ social media platforms with minimal effort. By abstracting OAuth authentication, content adaptation, API integration, and error handling into a unified workflow, the system dramatically simplifies the complexity of multi-platform content marketing.

**Key Features:**
- OAuth-based authentication with automatic token management
- Platform-specific content adaptation (text, images, videos)
- Scheduled publishing via calendar timing integration
- Robust error handling with exponential backoff retry
- Real-time status tracking and analytics integration

**Architecture:**
- `aitoearn-server`: Orchestrates publishing workflow and platform API calls
- MongoDB: Stores drafts, OAuth tokens, and publication metadata
- Redis: Job queue for scheduling and retry management
- RustFS: S3-compatible storage for media assets

For detailed OAuth flow implementation, see [OAuth Authentication Flow](#4.1). For scheduling configuration, see [Calendar Timing and Scheduling](#5.2).

Sources: [README.md:14-20](), [README.md:79-89](), High-level system diagrams

---

# Page: Content Management Features

# Content Management Features

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



## Overview

The Content Management system in AiToEarn provides a comprehensive workflow for creating, organizing, scheduling, and distributing content across multiple social media platforms. This module handles the entire content lifecycle from initial creation (whether manual or AI-generated) through draft management, timing/scheduling, trend analysis, and final multi-platform publication.

This page provides an overview of content management capabilities. For detailed information on specific subsystems:
- **Content creation and AI-powered generation**: See [Content Creation and AI Generation](#5.1)
- **Scheduling and calendar-based timing**: See [Calendar Timing and Scheduling](#5.2)
- **Trending content discovery and optimization**: See [Hotspot Analysis and Trending Content](#5.3)
- **Multi-platform publishing workflows**: See [Multi-Platform Publishing](#4.3)
- **Analytics and performance tracking**: See [Analytics Dashboard](#6.2)

**Sources:** [README.md:66-149]()

## Core Capabilities

AiToEarn's content management system provides four primary capabilities:

| Capability | Description | Key Technologies |
|------------|-------------|------------------|
| **Content Creation** | Manual editing and AI-powered generation of text, images, and video content | AI service (OpenAI, Claude, Gemini, etc.), MongoDB for drafts |
| **Smart Scheduling** | Calendar-based content planning with drag-and-drop interface and automated timing | Redis job queue, calendar UI components |
| **Trend Discovery** | Real-time hotspot analysis and viral content detection across platforms | Platform APIs, trend detection algorithms |
| **Multi-Platform Distribution** | One-click publishing to 14+ social media platforms with content adaptation | OAuth integration, platform-specific APIs |

The system supports simultaneous content creation and distribution to: Douyin, Xiaohongshu (Rednote), WeChat Channels, Kuaishou, Bilibili, WeChat Official Accounts, TikTok, YouTube, Facebook, Instagram, Threads, Twitter (X), Pinterest, and LinkedIn.

**Sources:** [README.md:18-21](), [README.md:79-89]()

## System Architecture

### Content Management Service Layer

```mermaid
graph TB
    subgraph "Frontend Layer"
        WebUI["aitoearn-web<br/>(Next.js :3000)"]
        DesktopApp["Electron Desktop App<br/>(AttAiToEarn)"]
    end
    
    subgraph "API Gateway"
        Nginx["nginx<br/>:8080"]
    end
    
    subgraph "Backend Services"
        Server["aitoearn-server<br/>(NestJS :3002)<br/>Content Management API"]
        AIService["aitoearn-ai<br/>(NestJS :3010)<br/>AI Generation Service"]
    end
    
    subgraph "Data Layer"
        MongoDB["MongoDB :27017<br/>- Drafts Collection<br/>- Published Content<br/>- User Content Metadata"]
        Redis["Redis :6379<br/>- Scheduling Jobs<br/>- Calendar Queue<br/>- Rate Limiting"]
        RustFS["RustFS :9000<br/>- Images/Videos<br/>- Generated Assets<br/>- Media Files"]
    end
    
    subgraph "External Services"
        Platforms["Social Media Platforms<br/>TikTok, YouTube, etc.<br/>(OAuth + Publishing APIs)"]
        AIProviders["AI Providers<br/>OpenAI, Claude, Gemini<br/>Grok, Doubao, AICSO"]
    end
    
    WebUI --> Nginx
    DesktopApp --> Nginx
    Nginx --> Server
    Nginx --> AIService
    
    Server --> MongoDB
    Server --> Redis
    Server --> RustFS
    Server --> Platforms
    Server --> AIService
    
    AIService --> MongoDB
    AIService --> Redis
    AIService --> RustFS
    AIService --> AIProviders
```

**Content Management Service Architecture**

This diagram shows how content management functionality is distributed across the AiToEarn services. The `aitoearn-server` handles content CRUD operations, scheduling, and platform publishing, while `aitoearn-ai` processes AI generation requests. Draft content and metadata are stored in MongoDB, scheduling jobs are managed via Redis queues, and media assets reside in RustFS (S3-compatible storage).

**Sources:** [docker-compose.yml:81-134](), [docker-compose.yml:136-232](), [DOCKER_DEPLOYMENT_EN.md:6-36]()

## Content Lifecycle Workflow

```mermaid
flowchart TB
    Start["User Initiates<br/>Content Creation"]
    
    Start --> CreateChoice{"Creation Method"}
    
    CreateChoice -->|"AI Generation"| AIFlow["Select AI Model<br/>(OpenAI/Claude/Gemini)"]
    CreateChoice -->|"Manual Entry"| ManualFlow["Manual Content Editor"]
    CreateChoice -->|"Import Existing"| ImportFlow["Smart Import from Platform"]
    
    AIFlow --> AIProcess["aitoearn-ai Service<br/>Text/Image/Video Generation"]
    AIProcess --> AssetUpload["Upload to RustFS<br/>/aitoearn bucket"]
    
    ImportFlow --> FetchContent["Fetch via Platform API<br/>(e.g., Xiaohongshu)"]
    FetchContent --> AssetUpload
    
    ManualFlow --> DraftSave
    AssetUpload --> DraftSave["Save Draft<br/>MongoDB drafts collection"]
    
    DraftSave --> EditReview["Review & Edit<br/>Web/Desktop UI"]
    
    EditReview --> OptimizeChoice{"Apply Hotspot<br/>Optimization?"}
    OptimizeChoice -->|"Yes"| HotspotAnalysis["Fetch Trending Topics<br/>Multi-Platform APIs"]
    OptimizeChoice -->|"No"| ScheduleChoice
    
    HotspotAnalysis --> AIOptimize["AI Optimize Content<br/>Based on Trends"]
    AIOptimize --> ScheduleChoice
    
    ScheduleChoice{"Publishing Timing"}
    ScheduleChoice -->|"Schedule Later"| CalendarUI["Calendar Timing UI<br/>Drag-and-Drop Interface"]
    ScheduleChoice -->|"Publish Now"| PlatformSelect
    
    CalendarUI --> RedisQueue["Add to Redis Job Queue<br/>CalendarTiming jobs"]
    RedisQueue --> JobExecutor["Job Executor<br/>(Scheduled Trigger)"]
    JobExecutor --> PlatformSelect
    
    PlatformSelect["Select Target Platforms<br/>(Multi-select UI)"]
    
    PlatformSelect --> OAuthCheck{"Valid OAuth<br/>Tokens?"}
    OAuthCheck -->|"No"| ReAuth["Re-authenticate<br/>OAuth Flow"]
    OAuthCheck -->|"Yes"| Publish
    
    ReAuth --> Publish["Multi-Platform Publishing<br/>Platform-Specific APIs"]
    
    Publish --> SaveMetadata["Store Published Metadata<br/>MongoDB content collection"]
    SaveMetadata --> Engagement["Engagement Tracking<br/>(Comments/Likes)"]
    Engagement --> Analytics["Analytics Collection<br/>Statistics Database"]
    
    Analytics --> End["End"]
```

**Complete Content Lifecycle from Creation to Analytics**

This workflow diagram illustrates the full journey of content through the AiToEarn system. Content can originate from AI generation (via `aitoearn-ai`), manual creation, or imported from existing platforms. All content passes through draft storage in MongoDB before entering the scheduling system (Redis-based job queue) or direct publishing. The calendar timing system allows users to plan content distribution, while hotspot analysis can optimize content based on current trends.

**Sources:** [README.md:79-89](), [README.md:91-100](), [README.md:141-148]()

## Key Components

### 1. Draft Management System

The draft management system stores all content in MongoDB before publication. Drafts include:
- Content text, title, and descriptions
- References to media assets stored in RustFS (`rustfs/aitoearn` bucket)
- Platform-specific formatting metadata
- Version history for collaborative editing
- User ownership and permissions

MongoDB collections used:
- `drafts` - Unpublished content
- `content` - Published content metadata
- `media` - Asset references and metadata

**Sources:** [docker-compose.yml:2-21](), [DOCKER_DEPLOYMENT_EN.md:308]()

### 2. AI-Powered Content Generation

The `aitoearn-ai` service orchestrates multiple AI providers for content generation:

| Provider | Environment Variable | Supported Models | Use Cases |
|----------|---------------------|------------------|-----------|
| OpenAI | `OPENAI_API_KEY` | GPT-4, GPT-5 | Text generation, copywriting |
| Anthropic | `ANTHROPIC_API_KEY` | Claude Opus 4.5/4.6 | Long-form content, analysis |
| Google | `GEMINI_KEY_PAIRS` | Gemini 2.5/3.1 | Multi-modal generation |
| xAI | `GROK_API_KEY` | Grok | Real-time content |
| Volcengine | `VOLCENGINE_API_KEY` | Doubao | Chinese language content |
| AICSO | `AICSO_API_KEY` | Custom models | Specialized generation |

AI generation requests flow through: User → `aitoearn-web` → `nginx` → `aitoearn-server` → `aitoearn-ai` → AI Provider API

For detailed AI configuration and model selection, see [AI Service Architecture](#3.1) and [Multi-Provider Configuration](#3.2).

**Sources:** [docker-compose.yml:114-128](), [DOCKER_DEPLOYMENT_EN.md:222-247]()

### 3. Calendar Timing System

The scheduling system uses Redis as a job queue to manage future publications:

**Key Components:**
- **CalendarTiming UI** - Drag-and-drop interface for planning content (see [Calendar Timing and Scheduling](#5.2))
- **Redis Job Queue** - Stores scheduled publication jobs with timestamps
- **Job Executor** - Background worker that processes scheduled jobs at specified times
- **CalendarTimingItem** - Individual scheduled content items with platform targets
- **RecordCore** - Core scheduling logic and state management

When users schedule content via the calendar UI, a job is created in Redis with:
- Scheduled execution time
- Target platform(s)
- Content draft ID reference
- Publishing parameters (hashtags, mentions, etc.)

The job executor polls Redis for jobs where `executionTime <= currentTime` and triggers the multi-platform publishing workflow.

**Sources:** [docker-compose.yml:23-39](), [README.md:85-89]()

### 4. Hotspot Analysis Engine

The hotspot analysis system monitors trending topics across platforms to optimize content:

**Capabilities:**
- **Case Library** - Collection of high-performing posts (10,000+ likes) for inspiration
- **Trend Radar** - Real-time detection of viral topics across platforms
- **Content Optimization** - AI-based suggestions to align content with current trends

The system fetches trending data from platform APIs (TikTok Discover, YouTube Trending, Twitter Trends, etc.) and uses AI to analyze patterns. When users opt to optimize content for trends, the system:

1. Queries trending topics from target platforms
2. Analyzes current trends using AI (OpenAI/Claude)
3. Suggests content modifications (hashtags, keywords, timing)
4. Updates draft with optimized version

For detailed information on trend detection algorithms and integration points, see [Hotspot Analysis and Trending Content](#5.3).

**Sources:** [README.md:91-100]()

### 5. Multi-Platform Publishing

The publishing system adapts content for each platform's requirements:

**Platform Integration Points:**
- OAuth authentication flow for 14+ platforms (see [OAuth Authentication Flow](#4.1))
- Platform-specific content formatters (character limits, media requirements)
- Batch publishing engine for simultaneous distribution
- Retry logic with exponential backoff for failed publishes
- Webhook handlers for post-publish status updates

OAuth credentials are configured via environment variables in `aitoearn-server`:

```
TIKTOK_CLIENT_ID/SECRET
YOUTUBE_CLIENT_ID/SECRET
FACEBOOK_CLIENT_ID/SECRET
INSTAGRAM_CLIENT_ID/SECRET
TWITTER_CLIENT_ID/SECRET
LINKEDIN_CLIENT_ID/SECRET
[and 8 more platforms]
```

OAuth callback URL format: `https://{APP_DOMAIN}/api/plat/{platform}/auth/back`

For detailed publishing workflows and platform-specific adaptations, see [Multi-Platform Publishing](#4.3).

**Sources:** [docker-compose.yml:183-212](), [DOCKER_DEPLOYMENT_EN.md:253-270]()

## Data Storage Architecture

### Content Data Model

```mermaid
graph LR
    subgraph "MongoDB Collections"
        Drafts["drafts<br/>- _id<br/>- userId<br/>- title<br/>- content<br/>- mediaRefs[]<br/>- platforms[]<br/>- status<br/>- createdAt<br/>- updatedAt"]
        
        Published["content<br/>- _id<br/>- draftId<br/>- userId<br/>- platformId<br/>- publishedUrl<br/>- publishedAt<br/>- metadata{}"]
        
        Media["media<br/>- _id<br/>- userId<br/>- type<br/>- rustfsPath<br/>- cdnUrl<br/>- size<br/>- createdAt"]
    end
    
    subgraph "Redis Keys"
        Schedule["calendar:jobs:{jobId}<br/>- executionTime<br/>- draftId<br/>- platforms[]<br/>- status"]
        
        RateLimit["ratelimit:publish:{platform}<br/>- TTL-based counters<br/>- Per-platform limits"]
    end
    
    subgraph "RustFS Storage"
        Images["aitoearn/images/<br/>user_id/filename.jpg"]
        Videos["aitoearn/videos/<br/>user_id/filename.mp4"]
        Generated["aitoearn/ai-generated/<br/>timestamp_model.png"]
    end
    
    Drafts -->|"References"| Media
    Published -->|"Links to"| Drafts
    Schedule -->|"References"| Drafts
    Media -->|"Storage path"| Images
    Media -->|"Storage path"| Videos
    Media -->|"Storage path"| Generated
```

**Content Data Storage Schema**

This diagram shows how content data is organized across the three storage systems. MongoDB stores structured metadata and relationships, Redis manages time-sensitive scheduling data and rate limiting, and RustFS holds the actual media files. Each draft can reference multiple media assets, and published content maintains references back to the original draft for tracking and analytics.

**Sources:** [docker-compose.yml:2-21](), [docker-compose.yml:41-79](), [DOCKER_DEPLOYMENT_EN.md:173-202]()

### Storage Configuration

The content management system uses a three-tier storage strategy:

| Storage Layer | Technology | Purpose | Configuration Location |
|---------------|-----------|---------|------------------------|
| **Document Storage** | MongoDB | Drafts, metadata, user content | `MONGODB_HOST/PORT/USERNAME/PASSWORD` in `docker-compose.yml` |
| **Job Queue & Cache** | Redis | Scheduled jobs, rate limiting, sessions | `REDIS_HOST/PORT/PASSWORD` in `docker-compose.yml` |
| **Asset Storage** | RustFS (S3-compatible) | Images, videos, AI-generated media | `assets` config in `config/aitoearn-ai.config.js` and `config/aitoearn-server.config.js` |

RustFS configuration (default):
- Endpoint: `http://rustfs.local:9000` (internal) or `http://localhost:9000` (external)
- Bucket: `aitoearn`
- Access Key: `rustfsadmin`
- Secret Key: `rustfsadmin`
- Console: http://localhost:9001

For production deployments, RustFS can be replaced with AWS S3, Aliyun OSS, or other S3-compatible services by updating the `assets` configuration in both config files.

**Sources:** [docker-compose.yml:41-79](), [DOCKER_DEPLOYMENT_EN.md:173-202]()

## Integration Points

### Frontend → Backend Communication

Content management operations flow through the following route structure:

1. **Web UI** (`aitoearn-web:3000`) → **Nginx** (`:8080`) → **Server API** (`aitoearn-server:3002`)
2. **Desktop App** → **Nginx** → **Server API**

The `NEXT_PUBLIC_API_URL` environment variable (default: `http://localhost:8080/api`) configures the frontend API endpoint.

### Backend → AI Service Communication

AI generation requests:

**Server** (`http://aitoearn-server:3002`) → **AI Service** (`http://aitoearn-ai:3010`)

Configured via `AI_URL` in `aitoearn-server` and `SERVER_URL` in `aitoearn-ai`.

Authentication between services uses `INTERNAL_TOKEN` for request verification.

**Sources:** [docker-compose.yml:234-246](), [docker-compose.yml:155-174]()

## Content Management API Endpoints

While the complete API documentation is beyond the scope of this overview, key endpoint patterns include:

| Endpoint Pattern | Method | Purpose | Service |
|-----------------|--------|---------|---------|
| `/api/content/drafts` | GET, POST | List and create drafts | aitoearn-server |
| `/api/content/drafts/{id}` | GET, PUT, DELETE | Retrieve, update, delete draft | aitoearn-server |
| `/api/content/schedule` | POST | Schedule content for later | aitoearn-server |
| `/api/content/publish` | POST | Publish to platforms immediately | aitoearn-server |
| `/api/ai/generate/text` | POST | AI text generation | aitoearn-ai |
| `/api/ai/generate/image` | POST | AI image generation | aitoearn-ai |
| `/api/hotspot/trends` | GET | Fetch trending topics | aitoearn-server |
| `/api/plat/{platform}/auth` | GET | Initiate OAuth flow | aitoearn-server |

All API routes are proxied through Nginx on port 8080, with requests to `/api/*` forwarded to the appropriate backend service.

**Sources:** [DOCKER_DEPLOYMENT_EN.md:129-135]()

## Summary

The AiToEarn content management system provides an integrated workflow for:

1. **Creating** content through manual editing, AI generation, or platform imports
2. **Storing** drafts and media in MongoDB and RustFS
3. **Optimizing** content using hotspot/trend analysis
4. **Scheduling** publications via Redis-based job queues and calendar UI
5. **Publishing** to 14+ platforms with OAuth integration
6. **Tracking** performance through engagement and analytics

For implementation details on specific subsystems:
- Content creation workflows and AI integration: [Content Creation and AI Generation](#5.1)
- Calendar UI components and scheduling logic: [Calendar Timing and Scheduling](#5.2)
- Trend detection and optimization algorithms: [Hotspot Analysis and Trending Content](#5.3)

**Sources:** [README.md:66-157](), [DOCKER_DEPLOYMENT_EN.md:6-36]()

---

# Page: Content Creation and AI Generation

# Content Creation and AI Generation

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



## Purpose and Scope

This document describes the content creation workflow in AiToEarn, focusing on how users generate content using AI-powered tools and manual editing capabilities. It covers the AI generation architecture, multi-provider model selection, asset storage, and draft management systems.

For information about scheduling and publishing created content, see [Calendar Timing and Scheduling](#5.2). For discovering trending content to inspire creation, see [Hotspot Analysis and Trending Content](#5.3).

---

## Content Creation Workflow Overview

The content creation process in AiToEarn supports both AI-assisted generation and manual editing. Content flows through multiple services before being stored as drafts in MongoDB, with generated media assets stored in S3-compatible object storage.

```mermaid
flowchart TB
    User["User initiates content creation"]
    
    User --> Decision{"Use AI Generation?"}
    
    Decision -->|Yes| ModelSelect["Select AI Model<br/>(OpenAI/Claude/Gemini/Grok/Doubao/AICSO)"]
    Decision -->|No| ManualEdit["Manual content editing<br/>in aitoearn-web"]
    
    ModelSelect --> AIRequest["HTTP request to<br/>aitoearn-server:3002"]
    AIRequest --> AIService["aitoearn-ai:3010<br/>processes generation"]
    
    AIService --> AIProvider["External AI API call<br/>(configured via OPENAI_BASE_URL, etc.)"]
    
    AIProvider --> AssetCheck{"Media asset<br/>generated?"}
    
    AssetCheck -->|Yes| RustFS["Store in RustFS/S3<br/>rustfs.local:9000/aitoearn"]
    AssetCheck -->|No| DraftDB
    
    RustFS --> AssetURL["Return asset URL"]
    AssetURL --> DraftDB["Save draft to MongoDB<br/>mongodb:27017/aitoearn"]
    
    ManualEdit --> DraftDB
    
    DraftDB --> DraftReady["Draft ready for<br/>review/scheduling"]
```

**Sources:** [docker-compose.yml:81-134](), [docker-compose.yml:136-232](), [README.md:141-149]()

---

## AI Service Architecture

The AI generation capabilities are powered by the `aitoearn-ai` service, which orchestrates requests to multiple AI providers based on user-selected models. The service acts as a unified interface for text, image, and video generation.

```mermaid
graph TB
    subgraph "aitoearn-web Frontend"
        UI["Content creation UI"]
    end
    
    subgraph "aitoearn-server:3002"
        API["/api/ai/* endpoints"]
        AuthMiddleware["JWT auth validation"]
    end
    
    subgraph "aitoearn-ai:3010"
        AIController["AI HTTP routes"]
        ModelSelector["Model selection logic"]
        
        subgraph "AI Providers"
            OpenAIClient["OpenAI client<br/>OPENAI_API_KEY<br/>OPENAI_BASE_URL"]
            ClaudeClient["Anthropic client<br/>ANTHROPIC_API_KEY<br/>ANTHROPIC_BASE_URL"]
            GeminiClient["Gemini client<br/>GEMINI_KEY_PAIRS<br/>GEMINI_LOCATION"]
            GrokClient["Grok client<br/>GROK_API_KEY"]
            DoubaoClient["Volcengine client<br/>VOLCENGINE_API_KEY"]
            AICSOClient["AICSO client<br/>AICSO_API_KEY<br/>AICSO_BASE_URL"]
        end
    end
    
    subgraph "External Services"
        OpenAI["OpenAI API"]
        Anthropic["Anthropic API"]
        Google["Google Vertex AI"]
        xAI["xAI Grok"]
        Volcengine["Volcengine Doubao"]
        AICSO["AICSO Service"]
    end
    
    subgraph "Storage Layer"
        MongoDB["mongodb:27017<br/>Draft metadata"]
        RustFS["rustfs.local:9000<br/>Generated media assets"]
    end
    
    UI --> API
    API --> AuthMiddleware
    AuthMiddleware --> AIController
    
    AIController --> ModelSelector
    
    ModelSelector --> OpenAIClient
    ModelSelector --> ClaudeClient
    ModelSelector --> GeminiClient
    ModelSelector --> GrokClient
    ModelSelector --> DoubaoClient
    ModelSelector --> AICSOClient
    
    OpenAIClient --> OpenAI
    ClaudeClient --> Anthropic
    GeminiClient --> Google
    GrokClient --> xAI
    DoubaoClient --> Volcengine
    AICSOClient --> AICSO
    
    AIController --> RustFS
    API --> MongoDB
```

**Sources:** [docker-compose.yml:81-134](), [docker-compose.yml:114-128](), [DOCKER_DEPLOYMENT_EN.md:206-223]()

---

## AI Provider Configuration

AI providers are configured through environment variables in the `aitoearn-ai` service. The application supports multiple providers simultaneously, allowing users to select the best model for their specific content generation needs.

### Configuration Variables by Provider

| Provider | Environment Variables | Purpose |
|----------|----------------------|---------|
| **OpenAI** | `OPENAI_API_KEY`<br/>`OPENAI_BASE_URL` | GPT models for text/image generation. Also used by `aitoearn-server`. Default base URL: `https://api.openai.com/v1` |
| **Anthropic** | `ANTHROPIC_API_KEY`<br/>`ANTHROPIC_BASE_URL` | Claude models for text generation. Default base URL: `https://api.anthropic.com` |
| **Google Gemini** | `GEMINI_KEY_PAIRS`<br/>`GEMINI_LOCATION`<br/>`gcs-placeholder.json` | Gemini models for multimodal generation. Key pairs in JSON array format with GCS credentials |
| **xAI Grok** | `GROK_API_KEY` | Grok models for text generation |
| **Volcengine Doubao** | `VOLCENGINE_API_KEY`<br/>`VOLCENGINE_ACCESS_KEY_ID`<br/>`VOLCENGINE_SECRET_ACCESS_KEY`<br/>`VOLCENGINE_VOD_SPACE_NAME` | Doubao models and video-on-demand storage |
| **AICSO** | `AICSO_API_KEY`<br/>`AICSO_BASE_URL` | AICSO service integration |

**Sources:** [docker-compose.yml:114-128](), [DOCKER_DEPLOYMENT_EN.md:222-247]()

### Recommended Setup: API Relay Services

For production deployments, it is recommended to use an API relay service like [new-api](https://github.com/Calcium-Ion/new-api) or [one-api](https://github.com/songquanpeng/one-api) to centralize API key management and provide unified access to multiple AI providers through a single endpoint.

Configuration with relay service:
```yaml
# In docker-compose.yml aitoearn-ai service
OPENAI_BASE_URL: https://your-new-api-host/v1
OPENAI_API_KEY: sk-your-unified-key
```

The relay service handles routing to the appropriate AI provider based on the requested model.

**Sources:** [DOCKER_DEPLOYMENT_EN.md:206-220]()

### AI Model Definitions

Specific AI models available for selection (including pricing, capabilities, and provider mappings) are defined in the application configuration file mounted at `/app/config.js` inside the `aitoearn-ai` container.

**Sources:** [docker-compose.yml:91](), [DOCKER_DEPLOYMENT_EN.md:246-247]()

---

## Text Generation

Text generation capabilities allow users to create content copy, titles, descriptions, and hashtags using large language models. The system supports both streaming and non-streaming responses.

### Supported Text Generation Features

- **Post copy generation**: Full-length social media post text
- **Title generation**: Catchy headlines and titles
- **Description generation**: Meta descriptions and summaries
- **Hashtag generation**: Relevant hashtags for social media platforms
- **Content expansion**: Expand brief notes into full content
- **Content abbreviation**: Shorten long-form content

**Sources:** [README.md:141-149](), [README_CN.md:130-137]()

### Text Generation Flow

```mermaid
sequenceDiagram
    participant User as "User in aitoearn-web"
    participant Server as "aitoearn-server:3002"
    participant AI as "aitoearn-ai:3010"
    participant Provider as "AI Provider API"
    participant DB as "mongodb:27017"
    
    User->>Server: POST /api/ai/generate/text<br/>{prompt, model, params}
    Server->>Server: Validate JWT token
    Server->>AI: Forward request to AI service<br/>with INTERNAL_TOKEN
    AI->>AI: Select model provider<br/>based on model parameter
    AI->>Provider: API call with provider-specific<br/>credentials and prompt
    Provider-->>AI: Generated text response
    AI-->>Server: Return generated content
    Server->>DB: Save draft document<br/>with generated text
    Server-->>User: Return draft ID and content
```

**Sources:** [docker-compose.yml:109-112](), [docker-compose.yml:173-174]()

---

## Image Generation

Image generation uses AI models like DALL-E (OpenAI), Flux, and Midjourney integrations to create visual content based on text prompts. Generated images are stored in RustFS/S3-compatible object storage.

### Supported Image Models

According to the README, supported AI image models include:
- **GPT (DALL-E)**: OpenAI's image generation
- **Flux**: Advanced image generation model

**Sources:** [README.md:147](), [README_CN.md:136]()

### Image Generation and Storage Flow

```mermaid
sequenceDiagram
    participant User as "User in aitoearn-web"
    participant Server as "aitoearn-server:3002"
    participant AI as "aitoearn-ai:3010"
    participant Provider as "Image Generation API"
    participant Storage as "rustfs.local:9000"
    participant DB as "mongodb:27017"
    
    User->>Server: POST /api/ai/generate/image<br/>{prompt, model, size, params}
    Server->>AI: Forward to AI service
    AI->>Provider: Generate image with prompt
    Provider-->>AI: Return image URL or binary
    
    alt Image URL returned
        AI->>AI: Download image from URL
    end
    
    AI->>Storage: PUT /aitoearn/images/{uuid}.png<br/>with RUSTFS_ACCESS_KEY
    Storage-->>AI: Return object URL
    AI->>AI: Construct CDN URL if configured
    AI-->>Server: Return image metadata<br/>{url, size, format}
    Server->>DB: Save draft with image reference
    Server-->>User: Return image URL and draft ID
```

**Sources:** [docker-compose.yml:41-79](), [DOCKER_DEPLOYMENT_EN.md:175-202]()

### Object Storage Configuration

Generated images and videos are stored in RustFS, an S3-compatible object storage service included in the Docker Compose setup.

**RustFS Configuration:**
- **Service**: `rustfs` container at `rustfs.local:9000`
- **Bucket**: `aitoearn` (auto-created by `rustfs-init` service)
- **Access**: Configured via `RUSTFS_ACCESS_KEY` and `RUSTFS_SECRET_KEY`
- **Console**: Accessible at `http://localhost:9001`
- **Default credentials**: `rustfsadmin` / `rustfsadmin`

The asset storage configuration is defined in both `config/aitoearn-ai.config.js` and `config/aitoearn-server.config.js` with the following structure:

```javascript
assets: {
  provider: 's3',
  region: 'us-east-1',
  bucketName: 'aitoearn',
  endpoint: 'http://rustfs.local:9000',
  accessKeyId: process.env.RUSTFS_ACCESS_KEY || 'rustfsadmin',
  secretAccessKey: process.env.RUSTFS_SECRET_KEY || 'rustfsadmin',
  cdnEndpoint: process.env.CDN_ENDPOINT || '',
}
```

**Sources:** [docker-compose.yml:41-79](), [docker-compose.yml:65-79](), [DOCKER_DEPLOYMENT_EN.md:175-188]()

---

## Video Generation

Video generation capabilities allow users to create video content using AI models. The README mentions support for multiple video generation models.

### Supported Video Models

According to the README, supported AI video models include:
- **Seedance**
- **Kling**
- **Hailuo** (海螺)
- **Veo** (Google)
- **Midjourney** (video features)
- **Sora** (OpenAI)
- **Pika**
- **Runway**

**Sources:** [README.md:146](), [README_CN.md:135]()

### Video Storage Integration

Videos are stored using the same RustFS/S3 infrastructure as images. For Volcengine Doubao integration, video-on-demand (VOD) storage is configured via:

- `VOLCENGINE_VOD_SPACE_NAME`: VOD space name for Volcengine video storage

**Sources:** [docker-compose.yml:122](), [DOCKER_DEPLOYMENT_EN.md:232]()

---

## Draft Management

Content drafts are stored in MongoDB, allowing users to save, edit, and manage content before publishing. The draft system supports versioning and metadata storage.

### Draft Storage Schema

Drafts are stored in the MongoDB database at `mongodb:27017/aitoearn`. The exact schema is defined in the application code, but typically includes:

- **Content metadata**: Title, description, tags
- **Platform configurations**: Target platforms for publishing
- **Media references**: URLs to images/videos in RustFS
- **AI generation metadata**: Model used, prompts, generation parameters
- **Timestamps**: Creation and modification times
- **User ownership**: User ID and permissions

### Draft Data Flow

```mermaid
graph LR
    subgraph "Draft Lifecycle"
        Create["Create Draft<br/>(manual or AI-generated)"]
        Store["Store in MongoDB<br/>mongodb:27017/aitoearn"]
        Edit["Edit Draft<br/>(aitoearn-web UI)"]
        Schedule["Schedule for Publishing<br/>(see section 5.2)"]
        Publish["Publish to Platforms<br/>(see section 4.3)"]
    end
    
    Create --> Store
    Store --> Edit
    Edit --> Store
    Store --> Schedule
    Schedule --> Publish
    
    subgraph "Asset References"
        RustFSAssets["Media URLs from<br/>rustfs.local:9000/aitoearn"]
    end
    
    Store -.->|References| RustFSAssets
```

**Sources:** [docker-compose.yml:2-21](), [docker-compose.yml:100-103](), [docker-compose.yml:157-160]()

### MongoDB Configuration

The MongoDB instance is configured in the Docker Compose setup:

- **Service name**: `mongodb`
- **Container name**: `aitoearn-mongodb`
- **Port**: `27017` (exposed to host and internal network)
- **Database name**: `aitoearn`
- **Authentication**: Username `admin`, password configurable via `MONGO_INITDB_ROOT_PASSWORD`
- **Data persistence**: Volumes `mongodb-data` and `mongodb-config`
- **Health check**: Mongosh ping command every 10 seconds

**Sources:** [docker-compose.yml:2-21](), [DOCKER_DEPLOYMENT_EN.md:143-146]()

---

## Manual Content Creation

In addition to AI-generated content, users can create content manually through the `aitoearn-web` frontend interface. This workflow bypasses the AI service and allows direct editing of text, upload of media files, and configuration of publishing parameters.

### Manual Creation Flow

```mermaid
flowchart TB
    UserInput["User enters content<br/>in aitoearn-web"]
    
    UserInput --> MediaUpload{"Upload media<br/>files?"}
    
    MediaUpload -->|Yes| UploadToRustFS["Upload to RustFS<br/>via aitoearn-server"]
    MediaUpload -->|No| SaveDraft
    
    UploadToRustFS --> GetURL["Get media URLs"]
    GetURL --> SaveDraft["Save draft to MongoDB<br/>via POST /api/drafts"]
    
    SaveDraft --> DraftStored["Draft stored with<br/>content and media references"]
```

Manual uploads follow the same asset storage patterns as AI-generated media, ensuring consistency in how media is referenced and accessed.

**Sources:** [docker-compose.yml:234-246]()

---

## Service Communication and Authentication

The content creation workflow involves secure communication between multiple services. Authentication and authorization are handled through JWT tokens for user requests and internal tokens for service-to-service communication.

### Authentication Flow

```mermaid
sequenceDiagram
    participant User as "User Browser"
    participant Web as "aitoearn-web:3000"
    participant Server as "aitoearn-server:3002"
    participant AI as "aitoearn-ai:3010"
    
    User->>Web: Login request
    Web->>Server: POST /api/auth/login
    Server->>Server: Validate credentials
    Server-->>Web: JWT token<br/>(signed with JWT_SECRET)
    Web->>Web: Store JWT in browser
    
    User->>Web: Request AI generation
    Web->>Server: POST /api/ai/generate<br/>Authorization: Bearer {JWT}
    Server->>Server: Verify JWT with JWT_SECRET
    Server->>AI: Forward request<br/>X-Internal-Token: INTERNAL_TOKEN
    AI->>AI: Verify INTERNAL_TOKEN
    AI-->>Server: AI response
    Server-->>Web: Generated content
    Web-->>User: Display result
```

**Configuration:**
- `JWT_SECRET`: Must be identical in both `aitoearn-ai` and `aitoearn-server` services
- `INTERNAL_TOKEN`: Must be identical in both services for inter-service authentication
- `JWT_SECRET` is used to sign/verify user authentication tokens
- `INTERNAL_TOKEN` is used to authenticate service-to-service requests

**Sources:** [docker-compose.yml:109-110](), [docker-compose.yml:173-174](), [DOCKER_DEPLOYMENT_EN.md:148-149]()

---

## Content Creation API Endpoints

The content creation functionality is exposed through HTTP endpoints in the `aitoearn-server` service. These endpoints handle both manual content creation and AI-assisted generation requests.

### Key API Routes

| Endpoint Pattern | Service | Purpose |
|-----------------|---------|---------|
| `POST /api/ai/*` | aitoearn-server:3002 | Forward AI generation requests to aitoearn-ai |
| `POST /api/drafts` | aitoearn-server:3002 | Create or update content drafts |
| `GET /api/drafts` | aitoearn-server:3002 | Retrieve user's draft list |
| `GET /api/drafts/:id` | aitoearn-server:3002 | Retrieve specific draft |
| `DELETE /api/drafts/:id` | aitoearn-server:3002 | Delete draft |
| Internal: `http://aitoearn-ai:3010/*` | aitoearn-ai:3010 | AI service HTTP routes |

All API endpoints are accessed through Nginx reverse proxy at `http://localhost:8080/api/*` which routes to `aitoearn-server:3002`.

**Sources:** [docker-compose.yml:248-270](), [docker-compose.yml:112]()

---

## Health Checks and Monitoring

Both the AI and server services implement health check endpoints to ensure the content creation pipeline is functioning correctly.

### Health Check Configuration

**aitoearn-ai health check:**
```yaml
test: ["CMD", "node", "-e", "require('http').get('http://localhost:3010/health', (r) => { process.exit(r.statusCode === 200 ? 0 : 1) })"]
interval: 30s
timeout: 10s
retries: 3
start_period: 60s
```

**aitoearn-server health check:**
```yaml
test: ["CMD", "node", "-e", "require('http').get('http://localhost:3002/health', (r) => { process.exit(r.statusCode === 200 ? 0 : 1) })"]
interval: 30s
timeout: 10s
retries: 3
start_period: 60s
```

Health checks verify that HTTP services are responding on their designated ports. The `start_period` allows services time to initialize before health checks affect container status.

**Sources:** [docker-compose.yml:129-134](), [docker-compose.yml:227-232]()

---

## Summary

The content creation and AI generation system in AiToEarn provides:

1. **Multi-provider AI integration**: Support for 6+ AI providers (OpenAI, Claude, Gemini, Grok, Doubao, AICSO) through a unified interface
2. **Multiple generation types**: Text, image, and video content generation
3. **Flexible storage**: S3-compatible object storage (RustFS) for media assets, MongoDB for draft metadata
4. **Manual and AI-assisted workflows**: Users can create content manually or use AI assistance
5. **Draft management**: MongoDB-based draft storage with versioning and metadata
6. **Secure inter-service communication**: JWT for user authentication, internal tokens for service-to-service calls
7. **Scalable architecture**: Separate services for web frontend, API backend, and AI processing

This architecture enables creators to generate high-quality content efficiently while maintaining flexibility in model selection and deployment configuration.

---

# Page: Calendar Timing and Scheduling

# Calendar Timing and Scheduling

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



## Purpose and Scope

This document describes the calendar-based content scheduling system in AiToEarn, which allows users to plan and coordinate multi-platform content distribution across time. The system provides a visual calendar interface for scheduling posts, manages scheduled jobs using Redis queues, and automates the publishing process at specified times.

For information about the content creation process that precedes scheduling, see [Content Creation and AI Generation](#5.1). For details about the actual multi-platform publishing mechanics, see [Multi-Platform Publishing](#4.3). For analytics and tracking of published content, see [Analytics Dashboard](#6.2).

---

## System Overview

The Calendar Timing and Scheduling system enables users to:

- **Visualize planned content** on a calendar interface across multiple platforms
- **Schedule posts** for future publication at specific dates and times
- **Drag and drop** scheduled items to reschedule them visually
- **Manage recurring** or one-time publication schedules
- **Queue jobs** in Redis for reliable execution
- **Automatically publish** content to connected platforms at the scheduled time

The system integrates three key architectural layers:

1. **Frontend UI Layer**: React-based calendar components for visual scheduling
2. **Backend API Layer**: NestJS services in `aitoearn-server` that manage schedule records
3. **Job Queue Layer**: Redis-backed job processing that executes scheduled publications

Sources: [README.md:85-86](), [README_CN.md:71](), [docker-compose.yml:23-39]()

---

## Architecture Components

### High-Level Architecture

```mermaid
graph TB
    subgraph "Frontend - aitoearn-web"
        CalendarUI["CalendarTiming Component"]
        CalendarItem["CalendarTimingItem Component"]
        RecordCore["RecordCore Component"]
    end
    
    subgraph "Backend - aitoearn-server"
        ScheduleAPI["Schedule API Endpoints"]
        ScheduleService["Schedule Service"]
        JobScheduler["Job Scheduler Service"]
    end
    
    subgraph "Data Layer"
        MongoDB[("MongoDB<br/>Schedule Records")]
        RedisQueue[("Redis<br/>Job Queue")]
    end
    
    subgraph "Execution Layer"
        JobWorker["Job Worker Process"]
        PublishService["Multi-Platform<br/>Publish Service"]
        PlatformAPIs["Platform APIs<br/>(TikTok, YouTube, etc)"]
    end
    
    CalendarUI --> ScheduleAPI
    CalendarItem --> ScheduleAPI
    RecordCore --> ScheduleAPI
    
    ScheduleAPI --> ScheduleService
    ScheduleService --> MongoDB
    ScheduleService --> JobScheduler
    
    JobScheduler --> RedisQueue
    
    RedisQueue --> JobWorker
    JobWorker --> PublishService
    PublishService --> PlatformAPIs
    
    JobWorker --> MongoDB
```

**Sources**: [docker-compose.yml:23-39](), [docker-compose.yml:136-232](), System Architecture Overview

### Component Responsibilities

| Component | Service | Responsibility |
|-----------|---------|----------------|
| **CalendarTiming** | aitoearn-web | Main calendar view component, renders monthly/weekly calendar grid |
| **CalendarTimingItem** | aitoearn-web | Individual scheduled post item, displays on calendar, handles drag events |
| **RecordCore** | aitoearn-web | Core data management for schedule records, handles CRUD operations |
| **Schedule API** | aitoearn-server | REST endpoints for creating, updating, deleting scheduled posts |
| **Schedule Service** | aitoearn-server | Business logic for managing schedule records in MongoDB |
| **Job Scheduler** | aitoearn-server | Enqueues jobs to Redis with appropriate delay/timing |
| **Job Worker** | aitoearn-server | Processes jobs from Redis queue, triggers publication |
| **Publish Service** | aitoearn-server | Handles actual API calls to social media platforms |

**Sources**: Table of Contents (Page 5.2 description), [docker-compose.yml:234-270]()

---

## UI Components

### CalendarTiming Component

The `CalendarTiming` component is the primary user interface for viewing and managing scheduled content. It provides:

- **Calendar Grid Rendering**: Monthly or weekly view of scheduled posts
- **Date Navigation**: Controls to move between months/weeks
- **Visual Post Indicators**: Shows scheduled items on their respective dates
- **Drag-and-Drop Support**: Enables rescheduling by dragging items between dates
- **Multi-Platform Display**: Color-codes or icons to indicate target platforms

**Typical User Workflow**:

```mermaid
sequenceDiagram
    participant User
    participant CalendarUI as "CalendarTiming Component"
    participant RecordCore as "RecordCore"
    participant API as "Schedule API"
    
    User->>CalendarUI: Opens calendar view
    CalendarUI->>RecordCore: Fetch scheduled records
    RecordCore->>API: GET /api/schedule/list
    API-->>RecordCore: Return schedule records
    RecordCore-->>CalendarUI: Update state with records
    CalendarUI-->>User: Display calendar with scheduled items
```

**Sources**: Table of Contents (Page 5.2 description)

### CalendarTimingItem Component

`CalendarTimingItem` represents an individual scheduled post within the calendar. Key features:

- **Post Summary Display**: Shows title, platforms, thumbnail
- **Status Indicators**: Visual cues for draft, scheduled, published, failed states
- **Drag Source**: Implements drag-and-drop source interface
- **Click Actions**: Opens detail view or edit modal
- **Context Menu**: Quick actions (reschedule, cancel, duplicate)

**Component Props** (typical structure):

| Prop | Type | Description |
|------|------|-------------|
| `scheduleId` | string | Unique identifier for the scheduled post |
| `title` | string | Post title/caption |
| `platforms` | string[] | Target platforms (e.g., ["tiktok", "youtube"]) |
| `scheduledTime` | Date | When to publish |
| `status` | enum | "draft", "scheduled", "publishing", "published", "failed" |
| `thumbnailUrl` | string | Preview image |
| `onDragStart` | function | Drag event handler |
| `onDragEnd` | function | Drag completion handler |

**Sources**: Table of Contents (Page 5.2 description)

### RecordCore Component

`RecordCore` serves as the data management layer for the calendar UI components. It acts as a bridge between the UI and backend API:

- **State Management**: Maintains local state of all schedule records
- **API Integration**: Handles HTTP requests to schedule endpoints
- **Cache Management**: Optimizes performance by caching fetched records
- **Real-time Updates**: May use WebSocket or polling for live updates
- **Optimistic UI**: Updates UI immediately while confirming with backend

**Core Methods** (conceptual):

```typescript
// Conceptual interface - actual implementation may vary
interface RecordCore {
  fetchSchedules(dateRange: DateRange): Promise<ScheduleRecord[]>
  createSchedule(record: ScheduleInput): Promise<ScheduleRecord>
  updateSchedule(id: string, updates: Partial<ScheduleInput>): Promise<ScheduleRecord>
  deleteSchedule(id: string): Promise<void>
  reschedule(id: string, newTime: Date): Promise<ScheduleRecord>
}
```

**Sources**: Table of Contents (Page 5.2 description)

---

## Drag-and-Drop Functionality

### Interaction Flow

The drag-and-drop feature enables intuitive rescheduling by allowing users to drag `CalendarTimingItem` components to new dates:

```mermaid
sequenceDiagram
    participant User
    participant Item as "CalendarTimingItem"
    participant Calendar as "CalendarTiming"
    participant RecordCore
    participant API as "Schedule API"
    participant Redis
    
    User->>Item: Start dragging item
    Item->>Calendar: onDragStart event
    Calendar->>Calendar: Show drop zones
    
    User->>Calendar: Drop on new date
    Calendar->>Calendar: Calculate new timestamp
    Calendar->>RecordCore: reschedule(id, newTime)
    
    RecordCore->>RecordCore: Optimistic update
    RecordCore->>Calendar: Update UI immediately
    
    RecordCore->>API: PUT /api/schedule/:id
    API->>API: Validate new time
    API->>Redis: Cancel old job
    API->>Redis: Enqueue new job
    
    alt Success
        API-->>RecordCore: Confirm success
        RecordCore-->>Calendar: Final state update
    else Failure
        API-->>RecordCore: Return error
        RecordCore->>Calendar: Revert to original
        RecordCore-->>User: Show error message
    end
```

### Implementation Considerations

1. **Drag Source**: `CalendarTimingItem` implements drag source interface (likely HTML5 Drag and Drop API or a library like `react-dnd`)
2. **Drop Targets**: Each date cell in `CalendarTiming` acts as a drop target
3. **Visual Feedback**: Shows preview/ghost image during drag, highlights valid drop zones
4. **Validation**: Backend validates new time is in the future and platform-appropriate
5. **Job Rescheduling**: Old Redis job is cancelled, new job is enqueued with updated delay

**Sources**: Table of Contents (Page 5.2 description)

---

## Redis Job Queue Integration

### Queue Architecture

AiToEarn uses Redis as a reliable job queue for scheduled publishing. Redis is configured in the deployment stack and accessible to `aitoearn-server`:

**Redis Configuration**:
- **Host**: `redis` (Docker network name) or `localhost:6379` (development)
- **Password**: Configured via `REDIS_PASSWORD` environment variable
- **Database**: Typically uses database 0 for main queue
- **Persistence**: Redis data persisted via Docker volume `redis-data`

```mermaid
graph LR
    subgraph "aitoearn-server Process"
        Scheduler["Job Scheduler"]
        Worker["Job Worker"]
    end
    
    subgraph "Redis Container"
        Queue["Scheduled Jobs Queue"]
        DelayedSet["Delayed Jobs Sorted Set"]
        ProcessingList["Processing List"]
    end
    
    Scheduler -->|"Enqueue with delay"| DelayedSet
    DelayedSet -->|"Due jobs move to"| Queue
    Worker -->|"Pop job"| Queue
    Worker -->|"Move to processing"| ProcessingList
    Worker -->|"Complete/fail"| ProcessingList
```

**Sources**: [docker-compose.yml:23-39](), [docker-compose.yml:105-107](), [docker-compose.yml:165-169]()

### Job Structure

Each scheduled publication is represented as a job in Redis with the following structure (conceptual):

```typescript
// Conceptual job structure
interface ScheduleJob {
  id: string                    // Unique job ID
  type: "scheduled_publish"     // Job type
  scheduleId: string            // Reference to MongoDB schedule record
  userId: string                // User who created the schedule
  content: {
    title: string
    body: string
    mediaUrls: string[]
    platforms: string[]         // ["tiktok", "youtube", etc.]
  }
  scheduledTime: number         // Unix timestamp (milliseconds)
  retry: {
    attempts: number            // Retry count
    maxAttempts: number         // Max retry limit (e.g., 3)
    backoff: number             // Backoff delay in ms
  }
  createdAt: number
  status: "pending" | "processing" | "completed" | "failed"
}
```

### Job Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Enqueued: User schedules post
    Enqueued --> Delayed: Job added to sorted set<br/>with delay
    Delayed --> Ready: Scheduled time reached
    Ready --> Processing: Worker picks up job
    Processing --> Publishing: Execute publish API calls
    
    Publishing --> Completed: All platforms succeed
    Publishing --> PartialFailure: Some platforms fail
    Publishing --> Failed: All platforms fail
    
    PartialFailure --> Retry: Retry failed platforms
    Failed --> Retry: Within retry limit
    
    Retry --> Processing: Retry attempt
    Failed --> DeadLetter: Max retries exceeded
    
    Completed --> [*]
    DeadLetter --> [*]
```

**Sources**: [docker-compose.yml:23-39]()

### Job Enqueuing Process

When a user schedules a post, the following occurs:

1. **API Request**: Frontend calls `POST /api/schedule` with post content and scheduled time
2. **Validation**: Backend validates time is in future, platforms are connected
3. **Database Record**: Schedule record saved to MongoDB with status "scheduled"
4. **Delay Calculation**: Calculate delay in milliseconds: `scheduledTime - now()`
5. **Redis Enqueue**: Job added to Redis with calculated delay
6. **Response**: API returns schedule record to frontend

**Job Enqueue Example** (pseudocode):

```javascript
// In Schedule Service (aitoearn-server)
async createSchedule(userId, scheduleData) {
  // Save to MongoDB
  const schedule = await this.scheduleRepository.create({
    userId,
    ...scheduleData,
    status: 'scheduled'
  });
  
  // Calculate delay
  const delay = scheduleData.scheduledTime - Date.now();
  
  // Enqueue to Redis
  await this.jobScheduler.enqueue({
    type: 'scheduled_publish',
    scheduleId: schedule.id,
    userId,
    content: scheduleData.content,
    scheduledTime: scheduleData.scheduledTime
  }, { delay });
  
  return schedule;
}
```

**Sources**: [docker-compose.yml:136-232]()

---

## Scheduling Workflow

### Complete Scheduling Flow

```mermaid
sequenceDiagram
    participant User
    participant UI as "Calendar UI"
    participant API as "Schedule API<br/>(aitoearn-server)"
    participant MongoDB
    participant RedisQueue as "Redis Queue"
    participant Worker as "Job Worker"
    participant PublishSvc as "Publish Service"
    participant Platforms as "Platform APIs"
    
    User->>UI: Create/edit scheduled post
    UI->>API: POST /api/schedule
    
    API->>API: Validate schedule time
    API->>API: Validate platform access
    
    API->>MongoDB: Save schedule record
    MongoDB-->>API: Return schedule ID
    
    API->>RedisQueue: Enqueue job with delay
    RedisQueue-->>API: Job enqueued
    
    API-->>UI: Return schedule record
    UI-->>User: Show confirmation
    
    Note over RedisQueue: Time passes...
    
    RedisQueue->>Worker: Job becomes ready
    Worker->>MongoDB: Fetch full schedule details
    MongoDB-->>Worker: Return content & metadata
    
    Worker->>PublishSvc: Publish to platforms
    
    loop For each platform
        PublishSvc->>Platforms: POST content
        Platforms-->>PublishSvc: Publication result
    end
    
    PublishSvc-->>Worker: Aggregated results
    
    alt All succeeded
        Worker->>MongoDB: Update status: "published"
        Worker->>RedisQueue: Mark job complete
    else Some failed
        Worker->>MongoDB: Update status: "partial_failure"
        Worker->>RedisQueue: Retry failed platforms
    else All failed
        Worker->>MongoDB: Update status: "failed"
        Worker->>RedisQueue: Retry or move to dead letter
    end
```

**Sources**: [README.md:85-86](), [docker-compose.yml:136-232]()

### Schedule Management Operations

| Operation | Endpoint | Effect on Redis Queue |
|-----------|----------|----------------------|
| **Create Schedule** | POST /api/schedule | New job enqueued with delay |
| **Update Time** | PUT /api/schedule/:id | Old job cancelled, new job enqueued |
| **Update Content** | PATCH /api/schedule/:id | Job data updated in queue |
| **Cancel Schedule** | DELETE /api/schedule/:id | Job removed from queue |
| **Publish Now** | POST /api/schedule/:id/publish-now | Job moved to ready queue immediately |

**Sources**: Based on common REST patterns for scheduling systems

---

## Publishing Process

### Job Worker Processing

The Job Worker runs continuously in the `aitoearn-server` process, monitoring Redis for ready jobs:

1. **Job Polling**: Worker checks Redis queue for jobs at scheduled time
2. **Job Lock**: Acquires lock on job to prevent duplicate processing
3. **Data Retrieval**: Fetches full content and metadata from MongoDB
4. **Platform Publishing**: Calls Multi-Platform Publish Service
5. **Result Handling**: Updates MongoDB with results, manages retries
6. **Job Completion**: Removes job from queue or schedules retry

### Multi-Platform Publishing

When a scheduled job executes, the Publish Service handles platform-specific publishing:

```mermaid
graph TD
    Worker["Job Worker"] --> Validate["Validate OAuth Tokens"]
    Validate --> Check{"All Tokens<br/>Valid?"}
    
    Check -->|No| Refresh["Refresh Tokens"]
    Check -->|Yes| Publish
    Refresh --> Publish["Publish Service"]
    
    Publish --> TikTok["TikTok API"]
    Publish --> YouTube["YouTube API"]
    Publish --> Twitter["Twitter API"]
    Publish --> Instagram["Instagram API"]
    Publish --> Others["Other Platforms..."]
    
    TikTok --> Aggregate["Aggregate Results"]
    YouTube --> Aggregate
    Twitter --> Aggregate
    Instagram --> Aggregate
    Others --> Aggregate
    
    Aggregate --> Update["Update Schedule<br/>Status in MongoDB"]
```

**Publishing Steps**:

1. **OAuth Validation**: Verify tokens for all target platforms are valid
2. **Token Refresh**: Refresh expired tokens if needed (see [OAuth Authentication Flow](#4.1))
3. **Content Adaptation**: Format content for each platform's requirements
4. **API Calls**: Execute platform-specific API calls in parallel
5. **Error Handling**: Capture errors per platform
6. **Result Aggregation**: Compile success/failure status for each platform
7. **Database Update**: Save publication results to MongoDB

**Sources**: [README.md:79-85](), System Architecture Overview

### Retry Logic

Failed publications are automatically retried with exponential backoff:

| Attempt | Delay | Max Attempts |
|---------|-------|--------------|
| 1st retry | 5 minutes | - |
| 2nd retry | 15 minutes | - |
| 3rd retry | 1 hour | Final attempt |

After max retries, the job moves to a dead letter queue and the schedule status is marked as "failed". Users are notified via the UI.

**Sources**: Common job queue patterns

---

## Data Models

### Schedule Record (MongoDB)

```typescript
// Conceptual MongoDB schema
interface ScheduleRecord {
  _id: ObjectId
  userId: ObjectId              // Reference to User
  draftId?: ObjectId            // Optional reference to Draft
  
  title: string
  content: {
    text: string
    mediaUrls: string[]
    hashtags: string[]
  }
  
  platforms: Array<{
    platform: string            // "tiktok", "youtube", etc.
    accountId: ObjectId
    platformSpecificData: any   // Platform-specific fields
  }>
  
  scheduledTime: Date
  timezone: string              // User's timezone
  
  status: "draft" | "scheduled" | "publishing" | "published" | "partial_failure" | "failed"
  
  publishResults: Array<{
    platform: string
    status: "success" | "failed"
    publishedUrl?: string
    error?: string
    publishedAt?: Date
  }>
  
  redisJobId: string            // Reference to Redis job
  
  createdAt: Date
  updatedAt: Date
  publishedAt?: Date
}
```

**Sources**: Inferred from system architecture and common content management patterns

### Configuration Options

Users can configure scheduling behavior:

- **Timezone**: Schedule posts in user's local timezone
- **Retry Settings**: Enable/disable auto-retry, set max retry count
- **Notifications**: Email/in-app alerts for successful/failed publications
- **Platform Priority**: Order of platform publication attempts
- **Fallback Actions**: Behavior when platform is down (skip vs. retry)

**Sources**: Common scheduling system features

---

## Integration Points

The Calendar Timing and Scheduling system integrates with:

1. **Content Creation** ([#5.1](#5.1)): Scheduled content originates from drafts
2. **OAuth Authentication** ([#4.1](#4.1)): Requires valid platform tokens for publishing
3. **Multi-Platform Publishing** ([#4.3](#4.3)): Executes actual API calls to platforms
4. **Analytics Dashboard** ([#6.2](#6.2)): Tracks performance of scheduled vs. immediate posts
5. **Engagement Engine** ([#6.1](#6.1)): May trigger automated engagement after publication

**Sources**: Table of Contents, System Architecture Overview

---

## Deployment Considerations

### Redis Configuration

Redis must be properly configured for reliable job scheduling:

**Docker Compose Setup**:
```yaml
# From docker-compose.yml
redis:
  image: redis:latest
  container_name: aitoearn-redis
  command: redis-server --requirepass password
  ports:
    - "6379:6379"
  volumes:
    - redis-data:/data
```

**Key Settings**:
- **Persistence**: Enabled via volume mount to prevent job loss on restart
- **Password**: Set via `--requirepass` flag and `REDIS_PASSWORD` env var
- **Memory Policy**: Should configure `maxmemory-policy` for production
- **Eviction**: Use `noeviction` or `allkeys-lru` depending on requirements

**Sources**: [docker-compose.yml:23-39]()

### Health Checks and Monitoring

The system should monitor:

1. **Redis Availability**: Health check endpoint to verify Redis connection
2. **Job Queue Length**: Alert if queue grows unusually large
3. **Job Processing Rate**: Track jobs processed per minute
4. **Failed Job Count**: Monitor dead letter queue size
5. **Worker Status**: Ensure job workers are running and processing
6. **MongoDB Connection**: Verify schedule record persistence

**Health Check Example**:
```typescript
// Conceptual health check endpoint
GET /api/schedule/health
Response: {
  redis: { status: "connected", queueLength: 42 },
  mongodb: { status: "connected" },
  worker: { status: "running", lastProcessed: "2024-01-15T10:30:00Z" }
}
```

**Sources**: [docker-compose.yml:34-39](), [docker-compose.yml:227-232]()

---

## Performance Optimization

### Caching Strategy

To minimize database load, the system caches:

- **User Schedule Lists**: Cache user's upcoming schedules for 5-10 minutes
- **Platform Tokens**: Cache OAuth tokens in Redis with TTL matching expiry
- **Job Metadata**: Store lightweight job data in Redis to avoid MongoDB lookups

### Scalability Considerations

For high-volume deployments:

1. **Horizontal Scaling**: Run multiple job worker instances
2. **Job Distribution**: Use Redis' built-in job distribution across workers
3. **Database Sharding**: Shard schedule records by userId if needed
4. **Queue Partitioning**: Separate queues for different priorities or platforms
5. **Rate Limiting**: Respect platform API rate limits in Publish Service

**Sources**: Common scaling patterns for job queue systems

---

**Document Sources**: [README.md:85-86](), [README_CN.md:71](), [docker-compose.yml:23-39](), [docker-compose.yml:136-232](), [docker-compose.yml:234-270](), Table of Contents (Page 5.2), System Architecture Overview

---

# Page: Hotspot Analysis and Trending Content

# Hotspot Analysis and Trending Content

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



## Purpose and Scope

The Hotspot Analysis and Trending Content system provides both content discovery and optimization capabilities across major social media platforms. This system serves two primary functions:

1. **Hotspot Analysis**: Detects trending topics, emerging themes, and viral patterns across platforms to identify content opportunities and optimize engagement strategies.

2. **Trending Content Discovery**: Monitors trending rankings, hot topics, viral titles, and popular content from platforms including Douyin (Chinese TikTok), Xiaohongshu (RED), WeChat Video Account, Kuaishou, and international platforms.

The system helps content creators:
- Identify trending topics and viral patterns before they peak
- Analyze successful content strategies from high-performing posts
- Optimize content titles, topics, and themes for better engagement
- Track cross-platform trends to maximize multi-channel distribution
- Reduce creator anxiety by providing data-driven content inspiration

The trending content feature is primarily implemented in [src/views/trending/index.tsx]() with backend API support from [src/api/platform.ts]().

Sources: [README.md:90-100](). [src/views/trending/index.tsx:1-2547](). [src/api/platform.ts:1-358]()

## System Architecture

### Component Architecture

The hotspot analysis and trending content feature is implemented as a React component (`src/views/trending/index.tsx`) that interfaces with the Platform API module (`src/api/platform.ts`) to fetch trending data from backend services.

**High-Level Component Flow**

```mermaid
graph TB
    TrendingIndex["trending/index.tsx<br/>Main Component"]
    
    subgraph "UI_Components[UI Layer]"
        Sidebar["Sidebar Navigation<br/>Section toggles<br/>Platform selection"]
        FilterControls["Filter Controls<br/>Category/Date/Type filters"]
        ContentDisplay["Content Display<br/>Grid/Table/List views"]
        PaginationComp["Pagination<br/>Page navigation"]
        PreviewModal["Content Preview Modal"]
    end
    
    subgraph "State_Management[State Management]"
        PlatformState["Platform States<br/>platforms, selectedPlatform"]
        RankingState["Ranking States<br/>rankingList, rankingContents"]
        FilterState["Filter States<br/>categories, dates, timeRange"]
        TopicState["Topic States<br/>topicContents, hotTopics"]
        ViralState["Viral Title States<br/>viralTitleData"]
    end
    
    subgraph "API_Layer[API Layer - platform.ts]"
        GetPlatformList["getPlatformList()"]
        GetPlatformRanking["getPlatformRanking()"]
        GetRankingContents["getRankingContents()"]
        GetAllHotTopics["getAllHotTopics()"]
        GetAllTopics["getAllTopics()"]
        FindViralTitles["findTopByPlatformAndCategories()"]
    end
    
    subgraph "Backend_Services[Backend Services]"
        RankingAPI["/ranking API<br/>Platform rankings<br/>Content lists"]
        HotTopicsAPI["/hot-topics API<br/>Trending topics<br/>Heat metrics"]
        TopicsAPI["/topics API<br/>Topic content<br/>Engagement data"]
        ViralTitlesAPI["/viral-titles API<br/>Top titles<br/>Category analytics"]
    end
    
    TrendingIndex --> Sidebar
    TrendingIndex --> FilterControls
    TrendingIndex --> ContentDisplay
    TrendingIndex --> PaginationComp
    TrendingIndex --> PreviewModal
    
    TrendingIndex --> PlatformState
    TrendingIndex --> RankingState
    TrendingIndex --> FilterState
    TrendingIndex --> TopicState
    TrendingIndex --> ViralState
    
    TrendingIndex -->|"API calls"| GetPlatformList
    TrendingIndex -->|"API calls"| GetPlatformRanking
    TrendingIndex -->|"API calls"| GetRankingContents
    TrendingIndex -->|"API calls"| GetAllHotTopics
    TrendingIndex -->|"API calls"| GetAllTopics
    TrendingIndex -->|"API calls"| FindViralTitles
    
    GetPlatformList --> RankingAPI
    GetPlatformRanking --> RankingAPI
    GetRankingContents --> RankingAPI
    GetAllHotTopics --> HotTopicsAPI
    GetAllTopics --> TopicsAPI
    FindViralTitles --> ViralTitlesAPI
```

Sources: [src/views/trending/index.tsx:1-2547](). [src/api/platform.ts:127-358]()

### Data Flow for Hotspot Analysis

The hotspot analysis workflow follows a typical pattern: user selects filters → component fetches data → API calls backend → data is processed and displayed with analytics.

**Hotspot Analysis Data Flow**

```mermaid
flowchart LR
    UserAction["User Action<br/>Select platform/filters"]
    ComponentState["Component State Update<br/>useState hooks"]
    APICall["Platform API Call<br/>platform.ts methods"]
    BackendFetch["Backend Fetch<br/>HTTP GET/POST"]
    DataProcess["Data Processing<br/>Transform & aggregate"]
    StateUpdate["State Update<br/>Set component state"]
    UIRender["UI Render<br/>Display results"]
    
    UserAction --> ComponentState
    ComponentState --> APICall
    APICall --> BackendFetch
    BackendFetch --> DataProcess
    DataProcess --> StateUpdate
    StateUpdate --> UIRender
    UIRender -.->|"User interaction"| UserAction
```

Sources: [src/views/trending/index.tsx:337-863](). [src/api/platform.ts:127-358]()

## Data Models

The Trending Content system works with several key data models:

```mermaid
classDiagram
    class Platform {
        id: string
        name: string
        icon: string
        type: string
        description: string
    }
    
    class PlatformRanking {
        id: string
        name: string
        platformId: string
        parentId: string
        type: string
        description: string
        updateFrequency: string
        updateTime: string
    }
    
    class RankingContent {
        id: string
        title: string
        type: string
        category: string
        url: string
        cover: string
        author: Author
        stats: Stats
        publishTime: string
        rankingPosition: number
    }
    
    class HotTopic {
        id: string
        title: string
        hotValue: number
        url: string
        rank: number
        rankChange: number
        isRising: boolean
        platformId: object
        hotValueHistory: array
    }
    
    class TopicContent {
        id: string
        title: string
        type: string
        description: string
        category: string
        author: string
        avatar: string
        cover: string
        topics: array
        likeCount: number
        shareCount: number
        commentCount: number
        collectCount: number
        publishTime: string
        url: string
    }
    
    class ViralTitle {
        id: string
        title: string
        platformId: string
        category: string
        publishTime: string
        engagement: number
        url: string
        rank: number
    }
    
    Platform "1" --> "*" PlatformRanking: has
    PlatformRanking "1" --> "*" RankingContent: contains
    Platform "1" --> "*" HotTopic: has
    Platform "1" --> "*" TopicContent: has
    Platform "1" --> "*" ViralTitle: has
```

Sources: [src/views/trending/index.tsx:31-135](). [src/api/platform.ts:11-126]()

## Content Discovery Sections

The Trending Content feature is organized into several major sections, each providing different views of trending content:

### 1. Hot Content (热门内容)

This section displays platform-specific rankings of popular content. Users can:

- Select from available platforms (Douyin, Xiaohongshu, etc.)
- Choose from different ranking types for each platform
- Filter content by category
- View historical rankings by date
- See detailed metrics (views, likes, comments, etc.)

```mermaid
flowchart TD
    SelectPlatform["Select Platform"]
    LoadRankings["Load Platform Rankings"]
    SelectRanking["Select Ranking Type"]
    LoadDates["Load Available Dates"]
    LoadCategories["Load Categories"]
    SelectDate["Select Date"]
    SelectCategory["Select Category"]
    LoadContent["Load Ranking Content"]
    DisplayContent["Display Content with Stats"]
    
    SelectPlatform -->|"handlePlatformSelect()"| LoadRankings
    LoadRankings -->|"fetchPlatformRanking()"| SelectRanking
    SelectRanking -->|"handleRankingSelect()"| LoadDates
    LoadDates -->|"fetchRankingDates()"| LoadCategories
    LoadCategories -->|"fetchRankingCategories()"| SelectDate
    SelectDate -->|"handleDateChange()"| SelectCategory
    SelectCategory -->|"handleCategorySelect()"| LoadContent
    LoadContent -->|"fetchRankingContents()"| DisplayContent
```

Sources: [src/views/trending/index.tsx:347-394](). [src/views/trending/index.tsx:427-542](). [src/views/trending/index.tsx:543-594]().

### 2. Hot Events (热点事件)

This section displays trending topics and events across multiple platforms, showing:

- Real-time popularity metrics
- Heat trends (increasing or decreasing)
- Visual trend graphs
- Cross-platform comparison

The system fetches hot topics data from all platforms and displays them in a grid layout, allowing users to compare trending topics across different platforms simultaneously.

Sources: [src/views/trending/index.tsx:997-1015](). [src/views/trending/index.tsx:1972-2162]().

### 3. Hot Topics (热门专题)

This section displays popular content organized by topic categories, allowing users to:

- Filter by content type (videos, articles, etc.)
- Filter by platform
- Filter by time range
- View detailed engagement metrics

The content is displayed in a table format with comprehensive metrics including likes, shares, comments, and collection counts.

Sources: [src/views/trending/index.tsx:794-863](). [src/views/trending/index.tsx:2163-2458]().

### 4. Viral Titles (爆款标题)

This section focuses specifically on trending content titles, organized by category:

- Filter by platform
- Filter by time range (7 days, 30 days, 90 days)
- Browse by content category
- View engagement metrics for each title

The system presents viral titles in a categorized view, with the option to see more titles within each category.

Sources: [src/views/trending/index.tsx:637-722](). [src/views/trending/index.tsx:1731-1971]().

## User Interface Components

The Trending Content UI is divided into two main sections:

```mermaid
graph LR
    subgraph "Trending Page"
        subgraph "Left Sidebar"
            HotContent["Hot Content Section"]
            subgraph "Platform List"
                Platform1["Platform 1"]
                Platform2["Platform 2"]
                PlatformN["..."]
            end
            HotEvents["Hot Events Section"]
            HotTopics["Hot Topics Section"]
            ViralTitles["Viral Titles Section"]
        end
        
        subgraph "Content Area"
            subgraph "Filter Controls"
                CategoryFilter["Category Filter"]
                DatePicker["Date Picker"]
                TimeRangeFilter["Time Range Filter"]
            end
            
            ContentList["Content List"]
            Pagination["Pagination Controls"]
            ContentModal["Content Preview Modal"]
        end
    end
    
    HotContent -.-> Platform1
    HotContent -.-> Platform2
    HotContent -.-> PlatformN
    
    Platform1 --> ContentArea
    HotEvents --> ContentArea
    HotTopics --> ContentArea
    ViralTitles --> ContentArea
```

Sources: [src/views/trending/index.tsx:1504-1548](). [src/views/trending/index.tsx:1730-2547]().

### Left Sidebar

The left sidebar serves as the primary navigation for the different trending content sections. It includes:

1. Hot Content section with platform list
2. Hot Events section
3. Hot Topics section
4. Viral Titles section

Each section can be expanded or collapsed, and selecting a section or platform loads the corresponding content in the main content area.

Sources: [src/views/trending/index.tsx:1508-1727]().

### Content Area

The content area is dynamically updated based on the selected sidebar section. It includes:

1. Filter controls specific to the selected content type
2. Content list with detailed metrics
3. Pagination controls
4. Content preview modal for viewing selected items

The layout and components displayed in the content area vary depending on the selected content type, providing a contextual interface for each section.

Sources: [src/views/trending/index.tsx:1730-2547]().

## Data Fetching and State Management

The Trending Content system uses React hooks for state management, with separate states for each content type and selection. The component makes API calls to fetch data based on user selections.

### Key State Groups

| State Group | Purpose | Key State Variables |
|-------------|---------|---------------------|
| Platform States | Manage platform selection | `platforms`, `selectedPlatform` |
| Ranking States | Manage ranking selection and data | `rankingList`, `selectedRanking`, `rankingContents` |
| Filter States | Manage content filters | `categories`, `selectedCategory`, `selectedDate` |
| Pagination States | Manage content pagination | `pagination`, `currentPage` |
| Section States | Track expanded/collapsed sections | `contentExpanded`, `hotEventExpanded`, `topicExpanded`, `viralTitleExpanded` |
| Topic States | Manage topic data and filters | `topicContents`, `selectedMsgType`, `selectedTimeRange` |
| Viral Title States | Manage viral title data and filters | `viralTitleData`, `selectedViralPlatform`, `selectedViralCategory` |

Sources: [src/views/trending/index.tsx:210-336]().

### API Integration

The Trending Component interfaces with the Platform API to fetch trending data. Key API methods include:

| API Method | Purpose | Endpoint |
|------------|---------|----------|
| `getPlatformList` | Get available platforms | `/hotinfo/platform` |
| `getPlatformRanking` | Get platform rankings | `/ranking/platform` |
| `getRankingContents` | Get ranking content items | `/ranking/{rankingId}/contents` |
| `getRankingLabel` | Get ranking categories | `/ranking/label/{rankingId}` |
| `getRankingDates` | Get available dates for rankings | `/ranking/hotinfo/{rankingId}/dates` |
| `getAllHotTopics` | Get hot topics across platforms | `/hot-topics/all` |
| `getAllTopics` | Get topic content with filters | `/topics` |
| `findPlatformsWithData` | Get platforms with viral title data | `/viral-titles/platforms` |
| `findTopByPlatformAndCategories` | Get top viral titles by category | `/viral-titles/platforms/{platformId}/top-by-categories` |

Sources: [src/api/platform.ts:127-302]().

## Error Handling and Edge Cases

The Trending Content system implements several error handling strategies:

1. **Loading States**: Each content type has its own loading state (e.g., `rankingLoading`, `topicLoading`) to show loading indicators during API calls.

2. **Error Recovery**: API calls are wrapped in try-catch blocks to handle errors and provide fallback states.

3. **Empty State Handling**: When no data is available, appropriate "no data" messages are displayed.

4. **Image Error Handling**: The system handles image loading errors by providing fallback displays.

Sources: [src/views/trending/index.tsx:339-346](). [src/views/trending/index.tsx:346-369]().

## Usage Examples

The Trending Content system helps users in several key scenarios:

1. **Content Research**: Identify trending content in specific niches to understand what resonates with audiences.

2. **Competitor Analysis**: Monitor hot content from competitors to benchmark performance.

3. **Title Optimization**: Review viral titles to improve content naming strategies.

4. **Topic Discovery**: Identify emerging trends and topics for timely content creation.

5. **Cross-Platform Insights**: Compare trending content across different platforms to optimize multi-platform strategies.

---

# Page: Engagement and Analytics

# Engagement and Analytics

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



## Overview

The Engagement and Analytics subsystem provides comprehensive tools for managing social media interactions and tracking content performance across multiple platforms. This system consists of two main components:

1. **Engagement Engine**: Automates interactions with content (comments, likes, collections) using AI-generated responses
2. **Analytics Dashboard**: Tracks performance metrics and provides insights across all connected platforms

Together, these capabilities enable users to maintain active social media presence while gaining data-driven insights into content effectiveness. The engagement system helps build audience relationships through automated interactions, while the analytics system measures the impact of published content and engagement activities.

For detailed information on each component:
- See [Engagement Engine](#6.1) for automation features
- See [Analytics Dashboard](#6.2) for performance tracking

Sources: [README.md:124-140](), [docker-compose.yml:162-165]()
</thinking>

## Engagement and Analytics System Architecture

```mermaid
flowchart TB
    subgraph "User Interface Layer"
        ReplyUI["Reply UI<br/>(src/views/reply)"]
        ReplyOtherUI["ReplyOther UI<br/>(src/views/replyother)"]
        AutoRunUI["AutoRun UI<br/>(src/views/reply/autoRun)"]
        AnalyticsUI["Analytics Dashboard<br/>(TBD)"]
    end
    
    subgraph "Application Services"
        ReplyService["ReplyService<br/>(electron/main/reply/service.ts)"]
        InteractionService["InteractionService<br/>(electron/main/interaction/service.ts)"]
        AutoRunService["AutoRunService<br/>(electron/main/autoRun/service.ts)"]
    end
    
    subgraph "Data Layer"
        MainDB["MongoDB<br/>(aitoearn database)"]
        StatsDB["Statistics Database<br/>(MongoDB - separate)"]
        ReplyRecords["ReplyCommentRecordModel"]
        InteractionRecords["InteractionRecordModel"]
        AutoRunRecords["AutoRunRecordModel"]
    end
    
    subgraph "External Systems"
        PlatformAPIs["Platform APIs<br/>(14+ platforms)"]
        AIServices["AI Services<br/>(OpenAI, Claude, etc.)"]
    end
    
    ReplyUI --> ReplyService
    ReplyOtherUI --> InteractionService
    AutoRunUI --> AutoRunService
    AnalyticsUI --> StatsDB
    
    ReplyService --> ReplyRecords
    InteractionService --> InteractionRecords
    AutoRunService --> AutoRunRecords
    
    ReplyRecords --> MainDB
    InteractionRecords --> MainDB
    AutoRunRecords --> MainDB
    
    ReplyService --> PlatformAPIs
    InteractionService --> PlatformAPIs
    
    ReplyService --> AIServices
    InteractionService --> AIServices
    
    PlatformAPIs -.->|"Performance Data"| StatsDB
    ReplyService -.->|"Engagement Metrics"| StatsDB
    InteractionService -.->|"Engagement Metrics"| StatsDB
```

The system architecture separates engagement operations from analytics data collection. Engagement services handle automated interactions and store their execution history in the main database, while performance metrics from platform APIs are collected into a dedicated statistics database for analysis.

Sources: [docker-compose.yml:162-171](), [electron/main/reply/controller.ts:23-386](), [electron/main/interaction/controller.ts:22-179]()

## Engagement System Components

The engagement system automates social media interactions across platforms to maintain audience relationships and grow social presence. It consists of three main subsystems:

### Core Subsystems

| Subsystem | Purpose | Key Components |
|-----------|---------|----------------|
| **Comment Reply System** | Automates responses to comments on user's own content | `ReplyService`, `ReplyController`, `ReplyCommentRecordModel` |
| **Interaction Service** | Manages automated interactions with others' content (likes, comments, collections) | `InteractionService`, `InteractionController`, `InteractionRecordModel` |
| **AutoRun System** | Schedules automated operations based on configurable time cycles | `AutoRunService`, `AutoRunController`, `AutoRunModel` |

### Engagement Workflow

```mermaid
sequenceDiagram
    participant User
    participant EngagementUI["Engagement UI"]
    participant EngagementSvc["Engagement Services"]
    participant AI["AI Services"]
    participant Platform["Platform APIs"]
    participant DB["Main Database"]
    participant StatsDB["Statistics DB"]
    
    User->>EngagementUI: Configure engagement task
    EngagementUI->>EngagementSvc: Submit task parameters
    
    loop For each content item
        EngagementSvc->>DB: Check interaction history
        DB-->>EngagementSvc: Return status
        
        alt Not previously interacted
            EngagementSvc->>AI: Generate contextual response
            AI-->>EngagementSvc: AI-generated content
            EngagementSvc->>Platform: Execute interaction
            Platform-->>EngagementSvc: Interaction result
            EngagementSvc->>DB: Store interaction record
            EngagementSvc->>StatsDB: Log engagement metrics
        end
    end
    
    EngagementSvc-->>EngagementUI: Return completion status
    EngagementUI-->>User: Display results
```

The engagement workflow demonstrates how automated interactions are executed, tracked, and measured. Each interaction is recorded in the main database to prevent duplicates, while engagement metrics are sent to the statistics database for analytics.

For detailed information on engagement automation features, see [Engagement Engine](#6.1).

Sources: [electron/main/reply/service.ts:112-276](), [electron/main/interaction/service.ts:111-325](), [docker-compose.yml:162-171]()

## Analytics System Components

The analytics system collects, processes, and visualizes performance data from all connected social media platforms. It provides insights into content effectiveness, audience engagement, and cross-platform comparison.

### Analytics Architecture

```mermaid
flowchart TB
    subgraph "Data Collection"
        PlatformAPIs["Platform APIs<br/>(14+ platforms)"]
        ContentPublish["Content Publishing Events"]
        EngagementEvents["Engagement Events"]
    end
    
    subgraph "Data Processing"
        DataCollectors["Data Collectors"]
        MetricsAggregator["Metrics Aggregator"]
    end
    
    subgraph "Storage"
        StatsDB["Statistics Database<br/>(MongoDB)"]
        MainDB["Main Database<br/>(user/content data)"]
    end
    
    subgraph "Analytics Layer"
        MetricsCalc["Metrics Calculation"]
        CrossPlatformAnalysis["Cross-Platform Analysis"]
        TrendAnalysis["Trend Analysis"]
    end
    
    subgraph "Presentation"
        AnalyticsDashboard["Analytics Dashboard UI"]
        Reports["Performance Reports"]
    end
    
    PlatformAPIs -->|"Views, Likes, Comments, Shares"| DataCollectors
    ContentPublish -->|"Publish metadata"| DataCollectors
    EngagementEvents -->|"Interaction data"| DataCollectors
    
    DataCollectors --> MetricsAggregator
    MetricsAggregator --> StatsDB
    MetricsAggregator --> MainDB
    
    StatsDB --> MetricsCalc
    MainDB --> MetricsCalc
    
    MetricsCalc --> CrossPlatformAnalysis
    MetricsCalc --> TrendAnalysis
    
    CrossPlatformAnalysis --> AnalyticsDashboard
    TrendAnalysis --> AnalyticsDashboard
    MetricsCalc --> Reports
```

### Statistics Database Configuration

The statistics database is configured separately from the main application database to handle high-volume analytics data independently. This separation allows for optimized query performance and data retention policies specific to analytics needs.

| Configuration Variable | Purpose | Default |
|----------------------|---------|---------|
| `STATISTICS_DB_HOST` | Statistics database hostname | `mongodb` |
| `STATISTICS_DB_PORT` | Database port | `27017` |
| `STATISTICS_DB_USERNAME` | Database username | `admin` |
| `STATISTICS_DB_PASSWORD` | Database password | `password` |

In production deployments, the statistics database can be hosted on a separate MongoDB instance with different performance characteristics and backup schedules than the main database.

Sources: [docker-compose.yml:162-171](), [DOCKER_DEPLOYMENT_EN.md:162-171](), [README.md:134-140]()

### Key Analytics Metrics

The analytics system tracks multiple performance indicators:

| Metric Category | Tracked Metrics | Purpose |
|----------------|-----------------|---------|
| **Content Performance** | Views, Likes, Comments, Shares, Completion Rate | Measure individual content effectiveness |
| **Engagement Metrics** | Reply Rate, Comment Sentiment, Interaction Speed | Understand audience engagement quality |
| **Cross-Platform Comparison** | Platform-specific performance, Best-performing channels | Optimize content distribution strategy |
| **Growth Metrics** | Follower Growth, Engagement Rate Trends | Track long-term account growth |
| **Monetization Tracking** | Revenue, Campaign Performance | Monitor monetization effectiveness |

### Analytics Features

The README highlights several key analytics capabilities:

1. **Cross-Platform Comparison**: Compare content performance across all connected platforms to identify which channels work best for specific content types
2. **Traffic Flow Analysis**: Track how platform-specific algorithms affect content visibility
3. **End-to-End Monitoring**: Full funnel tracking from content creation through publishing to audience engagement
4. **Path to Growth**: Data-driven insights for building audience to significant milestones (e.g., 1M+ followers)

For detailed information on the analytics dashboard implementation, see [Analytics Dashboard](#6.2).

Sources: [README.md:134-140](), [README_CN.md:124-128]()

## Data Models

The Automated Engagement System uses several database models to store configuration and track execution:

### AutoRunModel

Stores configuration for scheduled tasks:

```
- id: number                  // Primary key
- userId: string              // User ID
- accountId: number           // Platform account ID
- data: string                // JSON string with task data
- runCount: number            // Execution count
- status: AutoRunStatus       // DOING, PAUSE, DELETE
- type: AutoRunType           // Task type (ReplyComment)
- cycleType: string           // Schedule pattern
```

Sources: [electron/db/models/autoRun.ts:22-66]()

### AutoRunRecordModel

Tracks execution history of scheduled tasks:

```
- id: number                  // Primary key
- autoRunId: number           // Reference to AutoRunModel
- userId: string              // User ID
- status: AutoRunRecordStatus // DOING, FAIL, SUCCESS
- type: AutoRunType           // Task type
- cycleType: string           // Schedule pattern
- record: string              // Optional execution notes
```

Sources: [electron/db/models/autoRunRecord.ts:19-55]()

### ReplyCommentRecordModel and InteractionRecordModel

Store history of interactions to prevent duplicates and provide analytics:

```
- userId: string              // User ID
- accountId: number           // Platform account ID
- type: AccountType           // Platform type
- commentId/worksId: string   // Content identifier
- commentContent: string      // Original comment text
- replyContent: string        // Response text
```

Sources: [electron/main/reply/service.ts:50-67](), [electron/main/interaction/service.ts:43-66]()

## Security and Rate Limiting

To prevent platform detection of automation and potential account restrictions, the system implements several safety measures:

1. **Queue System**: Uses `PQueue` to limit concurrent operations
2. **Execution Delay**: Adds random delays between operations
3. **Interaction Tracking**: Prevents duplicate interactions
4. **Cache Mechanism**: Ensures only one process runs at a time
5. **Error Handling**: Gracefully manages platform API failures

Sources: [electron/main/reply/service.ts:29-34](), [electron/main/interaction/service.ts:29-34](), [electron/main/reply/service.ts:244]()

---

# Page: Engagement Engine

# Engagement Engine

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



The Engagement Engine is AiToEarn's automated system for managing comments, interactions, and community building across multiple social media platforms. It enables users to proactively engage with trending conversations, detect high-conversion opportunities through smart comment search, and manage all interactions from a unified interface, turning passive content operations into active traffic growth.

For content creation and publishing workflows, see [Content Creation and AI Generation](#5.1). For analytics and performance tracking, see [Analytics Dashboard](#6.2). For platform OAuth integration details, see [OAuth Authentication Flow](#4.1).

---

## Overview

The Engagement Engine provides automated and semi-automated tools for:

- **Unified Interaction Management**: Single interface to manage comments, replies, and messages across all connected platforms
- **Smart Comment Search**: Detection of high-conversion signals (e.g., "link please", "how to buy") in comments across platforms
- **Proactive Engagement**: Automated joining of trending conversations and targeted community building
- **Comment Filtering**: Advanced filtering to identify potential customers and engagement opportunities
- **Auto-Reply Capabilities**: Configurable automated responses to common queries and engagement patterns

The system transforms content operations from reactive (responding to notifications) to proactive (actively finding and engaging with target audiences).

Sources: [README.md:14-145]()

---

## Architecture Overview

### Position in System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WebUI["Web UI<br/>Comment Management Interface"]
        Desktop["Desktop App<br/>Engagement Dashboard"]
    end
    
    subgraph "Backend Services"
        Server["aitoearn-server:3002<br/>Engagement API Endpoints"]
        AI["aitoearn-ai:3010<br/>AI-Powered Analysis"]
    end
    
    subgraph "Data & Queue Layer"
        MongoDB["MongoDB<br/>Comments, Interactions,<br/>User Profiles"]
        Redis["Redis<br/>Job Queue,<br/>Rate Limiting"]
    end
    
    subgraph "External Platforms"
        TikTok["TikTok API"]
        YouTube["YouTube API"]
        Twitter["Twitter API"]
        Instagram["Instagram API"]
        OtherPlat["Other Platforms..."]
    end
    
    WebUI --> Server
    Desktop --> Server
    Server --> AI
    Server --> MongoDB
    Server --> Redis
    
    Server <-->|"OAuth + API Calls"| TikTok
    Server <-->|"OAuth + API Calls"| YouTube
    Server <-->|"OAuth + API Calls"| Twitter
    Server <-->|"OAuth + API Calls"| Instagram
    Server <-->|"OAuth + API Calls"| OtherPlat
    
    AI -->|"Sentiment Analysis<br/>Intent Detection"| Server
    Redis -->|"Scheduled Tasks<br/>Rate-Limited Requests"| Server
```

**Engagement Engine Position in System Architecture**

The Engagement Engine operates as a set of modules within the `aitoearn-server` service, coordinating with the AI service for intelligent analysis and external platform APIs for interaction execution.

Sources: [README.md:66-145](), High-level system diagrams provided in context

---

## Core Components

### Comment Collection and Search

The system continuously collects comments, mentions, and interactions from connected platforms through their APIs. The **Comment Search** feature enables users to:

- Search for specific keywords or phrases across all platforms
- Filter by platform, date range, engagement metrics, and sentiment
- Detect high-conversion signals like "link please", "how to buy", "DM me"
- Monitor brand mentions and product inquiries in real-time

```mermaid
graph LR
    subgraph "Comment Collection"
        Webhook["Platform Webhooks<br/>(Real-time)"]
        Polling["Scheduled Polling<br/>(Batch)"]
    end
    
    subgraph "Processing Pipeline"
        Collector["Comment Collector"]
        Parser["Content Parser"]
        AI_Analysis["AI Intent Analyzer"]
        Storage["MongoDB Storage"]
    end
    
    subgraph "Search Interface"
        SearchAPI["Search API Endpoint"]
        Filters["Filter Engine<br/>(Keywords, Platform, Date)"]
        Results["Search Results"]
    end
    
    Webhook --> Collector
    Polling --> Collector
    Collector --> Parser
    Parser --> AI_Analysis
    AI_Analysis --> Storage
    
    SearchAPI --> Filters
    Filters --> Storage
    Storage --> Results
```

**Comment Collection and Search Pipeline**

Sources: [README.md:115-122]()

---

### Interaction Management

The unified interaction dashboard consolidates all engagement activities:

| Component | Function | Data Source |
|-----------|----------|-------------|
| **Comment Inbox** | Centralized view of all comments requiring response | MongoDB comments collection |
| **Reply Queue** | Prioritized list of pending replies | Redis job queue |
| **Engagement History** | Historical record of all interactions | MongoDB interactions collection |
| **User Profiles** | Aggregated user interaction data across platforms | MongoDB users collection |
| **Analytics View** | Engagement metrics and conversion tracking | Statistics database |

Sources: [README.md:124-132](), [docker-compose.yml:136-232]()

---

## Comment Detection and Analysis Workflow

```mermaid
sequenceDiagram
    participant Platform as "Social Platform<br/>(TikTok/YouTube/etc)"
    participant Server as "aitoearn-server"
    participant AI as "aitoearn-ai"
    participant Redis as "Redis Queue"
    participant MongoDB as "MongoDB"
    participant User as "User Interface"
    
    Platform->>Server: New comment notification<br/>(webhook/polling)
    Server->>MongoDB: Store raw comment data
    Server->>AI: Analyze comment<br/>(intent, sentiment, keywords)
    
    AI-->>Server: Analysis result<br/>(high-conversion: true/false)
    
    alt High-Conversion Signal Detected
        Server->>MongoDB: Flag as high-priority
        Server->>Redis: Add to priority queue
        Server->>User: Push notification<br/>"Potential customer detected"
    else Normal Comment
        Server->>MongoDB: Store with standard priority
    end
    
    User->>Server: Request filtered comments<br/>(keyword: "how to buy")
    Server->>MongoDB: Query comments
    MongoDB-->>Server: Matching comments
    Server-->>User: Display results
    
    User->>Server: Reply to comment
    Server->>Redis: Queue reply task<br/>(rate-limited)
    Redis->>Server: Execute reply
    Server->>Platform: Post reply via API
    Platform-->>Server: Success/failure
    Server->>MongoDB: Log interaction
```

**Comment Detection, Analysis, and Response Flow**

The workflow demonstrates how comments are captured, analyzed by AI for intent and conversion potential, stored with appropriate priority, and surfaced to users for engagement.

Sources: [README.md:115-132](), [docker-compose.yml:100-134]()

---

## Automated Engagement Features

### Auto-Reply System

The auto-reply system enables semi-automated responses to common queries:

1. **Pattern Matching**: Configurable rules match comment patterns to response templates
2. **AI-Generated Responses**: Dynamic reply generation based on comment context
3. **Approval Workflow**: Optional human approval before posting
4. **Rate Limiting**: Redis-based rate limiting prevents platform spam detection

Configuration is managed through the `aitoearn-server` service environment and stored in MongoDB.

### Proactive Engagement

The system can proactively find and engage with content:

- **Trending Topic Monitoring**: Tracks trending hashtags and topics relevant to user's niche
- **Competitor Monitoring**: Identifies conversations happening on competitor content
- **Target Audience Identification**: Finds users matching demographic/interest profiles
- **Engagement Suggestions**: AI recommends specific posts/comments for engagement

```mermaid
graph TD
    subgraph "Discovery"
        Trends["Trending Topics<br/>Monitor"]
        Competitor["Competitor<br/>Content Tracker"]
        Audience["Target Audience<br/>Finder"]
    end
    
    subgraph "Analysis"
        Relevance["Relevance<br/>Scorer"]
        Opportunity["Opportunity<br/>Detector"]
        AI_Recommend["AI Recommendation<br/>Engine"]
    end
    
    subgraph "Action"
        Queue["Engagement<br/>Queue"]
        Auto["Automated<br/>Response"]
        Manual["Manual<br/>Review"]
        Execute["Post to<br/>Platform"]
    end
    
    Trends --> Relevance
    Competitor --> Relevance
    Audience --> Relevance
    
    Relevance --> Opportunity
    Opportunity --> AI_Recommend
    
    AI_Recommend --> Queue
    Queue --> Auto
    Queue --> Manual
    
    Auto --> Execute
    Manual --> Execute
```

**Proactive Engagement Discovery and Execution Pipeline**

Sources: [README.md:124-132]()

---

## Platform Integration

### Multi-Platform Comment APIs

The Engagement Engine integrates with comment/interaction APIs across 14+ platforms:

| Platform | API Features Used | OAuth Config |
|----------|-------------------|--------------|
| **TikTok** | Comments API, Mentions, DMs | `TIKTOK_CLIENT_ID/SECRET` |
| **YouTube** | Comments API, Community Posts | `YOUTUBE_CLIENT_ID/SECRET` |
| **Twitter/X** | Mentions, Replies, DMs | `TWITTER_CLIENT_ID/SECRET` |
| **Instagram** | Comments, DMs, Mentions | `INSTAGRAM_CLIENT_ID/SECRET` |
| **Facebook** | Comments, Post Interactions | `FACEBOOK_CLIENT_ID/SECRET` |
| **LinkedIn** | Comments, Messages | `LINKEDIN_CLIENT_ID/SECRET` |
| **Threads** | Replies, Mentions | `THREADS_CLIENT_ID/SECRET` |
| **Douyin** | Comments, Private Messages | `DOYIN_CLIENT_ID/SECRET` |
| **Bilibili** | Comments, Danmaku, DMs | `BILIBILI_CLIENT_ID/SECRET` |
| **Kuaishou** | Comments, Interactions | `KWAI_CLIENT_ID/SECRET` |

Each platform integration requires OAuth authentication (see [OAuth Authentication Flow](#4.1)) and handles platform-specific API limitations through Redis-based rate limiting.

Sources: [docker-compose.yml:184-212](), [DOCKER_DEPLOYMENT_EN.md:250-269]()

---

## Data Storage

### MongoDB Collections

The Engagement Engine uses several MongoDB collections:

| Collection | Purpose | Key Fields |
|------------|---------|------------|
| `comments` | Stores all collected comments | `platformId`, `postId`, `userId`, `text`, `timestamp`, `priority`, `aiAnalysis` |
| `interactions` | Records all engagement actions | `type`, `platformId`, `targetUserId`, `content`, `timestamp`, `status` |
| `engagement_rules` | Auto-reply rules and patterns | `pattern`, `responseTemplate`, `platforms`, `enabled` |
| `user_profiles` | Cross-platform user data | `platformAccounts`, `engagementHistory`, `conversionScore` |
| `engagement_queue` | Pending engagement tasks | `task`, `priority`, `scheduledTime`, `status` |

Database connection configuration is managed through environment variables in the `aitoearn-server` service:

- `MONGODB_HOST`: MongoDB hostname (default: `mongodb`)
- `MONGODB_PORT`: MongoDB port (default: `27017`)
- `MONGODB_USERNAME`: Database username
- `MONGODB_PASSWORD`: Database password

Sources: [docker-compose.yml:100-112](), [docker-compose.yml:157-165]()

---

## Job Queue and Rate Limiting

### Redis-Based Task Queue

All engagement actions (replies, likes, follows) are queued through Redis to ensure:

1. **Rate Limiting**: Prevents exceeding platform API limits
2. **Prioritization**: High-conversion opportunities processed first
3. **Retry Logic**: Failed operations are automatically retried
4. **Scheduled Execution**: Delay actions to appear more natural

```mermaid
graph LR
    subgraph "Task Creation"
        User["User Action<br/>(Reply/Like/Follow)"]
        Auto["Automated Task<br/>(Pattern Match)"]
    end
    
    subgraph "Redis Queue"
        Queue["Task Queue<br/>(Priority-based)"]
        RateLimit["Rate Limiter<br/>(Per Platform)"]
        Scheduler["Delayed Scheduler"]
    end
    
    subgraph "Execution"
        Worker["Queue Worker"]
        API["Platform API Call"]
        Retry["Retry Handler"]
    end
    
    User --> Queue
    Auto --> Queue
    
    Queue --> RateLimit
    RateLimit --> Scheduler
    Scheduler --> Worker
    
    Worker --> API
    API -->|Failure| Retry
    Retry --> Queue
    API -->|Success| Complete["Mark Complete<br/>& Log to MongoDB"]
```

**Redis Job Queue and Execution Flow**

Redis connection is configured via:
- `REDIS_HOST`: Redis hostname (default: `redis`)
- `REDIS_PORT`: Redis port (default: `6379`)
- `REDIS_PASSWORD`: Redis authentication password

Sources: [docker-compose.yml:105-107](), [docker-compose.yml:167-169]()

---

## AI-Powered Analysis

### Intent Detection and Sentiment Analysis

The `aitoearn-ai` service provides intelligent analysis of comments and interactions:

**AI Analysis Capabilities:**

1. **Intent Classification**: Identifies user intent (question, complaint, purchase inquiry, spam)
2. **Sentiment Analysis**: Determines emotional tone (positive, negative, neutral)
3. **Conversion Scoring**: Assigns likelihood score for conversion opportunity
4. **Entity Extraction**: Identifies mentioned products, competitors, or topics
5. **Response Suggestion**: Generates contextually appropriate reply suggestions

The AI service is accessed via internal API calls from `aitoearn-server` to `aitoearn-ai`:

- **Service URL**: `AI_URL=http://aitoearn-ai:3010` (configured in `aitoearn-server`)
- **Authentication**: Uses `INTERNAL_TOKEN` for service-to-service authentication
- **AI Models**: Leverages configured AI providers (OpenAI, Claude, Gemini, etc.)

Sources: [docker-compose.yml:81-134](), [DOCKER_DEPLOYMENT_EN.md:206-247]()

---

## Configuration

### Environment Variables

Key engagement-related configuration in `docker-compose.yml`:

| Variable | Service | Purpose | Default |
|----------|---------|---------|---------|
| `MONGODB_HOST` | aitoearn-server | Comment storage database | `mongodb` |
| `REDIS_HOST` | aitoearn-server | Task queue and rate limiter | `redis` |
| `AI_URL` | aitoearn-server | AI analysis service endpoint | `http://aitoearn-ai:3010` |
| `INTERNAL_TOKEN` | aitoearn-server, aitoearn-ai | Inter-service authentication | (must be set) |
| Platform OAuth credentials | aitoearn-server | API access for each platform | (see [OAuth Authentication Flow](#4.1)) |

### Rate Limiting Configuration

Platform-specific rate limits are typically configured in `config/aitoearn-server.config.js`:

```javascript
// Example rate limit structure (logical inference from architecture)
platformRateLimits: {
  tiktok: { requests: 100, window: 3600 },      // 100 requests per hour
  youtube: { requests: 10000, window: 86400 },  // 10k requests per day
  twitter: { requests: 300, window: 900 },      // 300 requests per 15 min
  // ... other platforms
}
```

Sources: [docker-compose.yml:136-227](), [DOCKER_DEPLOYMENT_EN.md:96-111]()

---

## Usage Workflow

### Typical User Flow

1. **Connect Platforms**: User authenticates platforms via OAuth (see [OAuth Authentication Flow](#4.1))
2. **Configure Rules**: Set up auto-reply patterns, keywords to monitor, and engagement targets
3. **Monitor Inbox**: View unified comment inbox with AI-powered priority flagging
4. **Search & Filter**: Use Comment Search to find specific opportunities (e.g., "looking to buy")
5. **Engage**: Reply directly or approve auto-generated responses
6. **Track Results**: View engagement analytics and conversion metrics (see [Analytics Dashboard](#6.2))

### API Endpoints (Logical Structure)

Based on the architecture, the Engagement Engine likely exposes endpoints such as:

- `GET /api/comments` - Retrieve comments with filtering
- `GET /api/comments/search` - Search comments by keyword
- `POST /api/comments/:id/reply` - Post a reply to a comment
- `GET /api/engagement/queue` - View pending engagement tasks
- `POST /api/engagement/rules` - Configure auto-reply rules
- `GET /api/engagement/analytics` - Retrieve engagement metrics

All endpoints are accessed through the Nginx reverse proxy at `http://localhost:8080/api/...`

Sources: [docker-compose.yml:248-270](), [README.md:115-132]()

---

## Integration with Other Systems

The Engagement Engine integrates with:

- **Content Publishing System** ([Multi-Platform Publishing](#4.3)): Links published content to engagement tracking
- **Hotspot Analysis** ([Hotspot Analysis and Trending Content](#5.3)): Uses trending data to guide proactive engagement
- **Analytics Dashboard** ([Analytics Dashboard](#6.2)): Feeds engagement data into performance analytics
- **All In Agent** ([All In Agent](#3.3)): AI agent can automate engagement based on learned patterns

Sources: [README.md:66-156](), High-level system diagrams

---

# Page: Analytics Dashboard

# Analytics Dashboard

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



## Purpose and Scope

The Analytics Dashboard provides comprehensive performance tracking and insights for content distributed across multiple social media platforms. It collects, aggregates, and displays metrics to help users understand content performance, optimize publishing strategies, and monitor growth trajectories.

This page covers the analytics data collection infrastructure, statistics database configuration, and how performance metrics are tracked across platforms. For information about content engagement automation, see [Engagement Engine](#6.1). For details about content publishing workflows, see [Multi-Platform Publishing](#4.3).

---

## System Architecture

The analytics system uses a dedicated statistics database to store performance metrics collected from published content across all connected platforms. This separation allows for optimized query performance and independent scaling of analytics workloads.

### Analytics Data Flow

```mermaid
flowchart TB
    subgraph "Platform_APIs"
        TikTok["TikTok API"]
        YouTube["YouTube API"]
        Instagram["Instagram API"]
        Twitter["Twitter/X API"]
        Others["Other Platform APIs"]
    end
    
    subgraph "aitoearn-server"
        PublishService["Publishing Service"]
        DataCollector["Analytics Data Collector"]
        StatsWriter["Statistics Writer"]
    end
    
    subgraph "Data_Layer"
        MainDB[("MongoDB<br/>(Main Database)<br/>aitoearn")]
        StatsDB[("MongoDB<br/>(Statistics Database)<br/>STATISTICS_DB_*")]
    end
    
    subgraph "aitoearn-web"
        Dashboard["Analytics Dashboard UI"]
        Charts["Charts & Visualizations"]
    end
    
    PublishService -->|"Publish content"| TikTok
    PublishService -->|"Publish content"| YouTube
    PublishService -->|"Publish content"| Instagram
    PublishService -->|"Publish content"| Twitter
    PublishService -->|"Publish content"| Others
    
    TikTok -->|"Performance metrics"| DataCollector
    YouTube -->|"Performance metrics"| DataCollector
    Instagram -->|"Performance metrics"| DataCollector
    Twitter -->|"Performance metrics"| DataCollector
    Others -->|"Performance metrics"| DataCollector
    
    PublishService -->|"Store publish metadata"| MainDB
    DataCollector -->|"Write metrics"| StatsWriter
    StatsWriter -->|"Store analytics data"| StatsDB
    
    StatsDB -->|"Query metrics"| Dashboard
    MainDB -->|"Query content metadata"| Dashboard
    Dashboard --> Charts
```

**Sources:** [docker-compose.yml:136-232](), [DOCKER_DEPLOYMENT_EN.md:162-171](), [README.md:134-139]()

---

## Statistics Database Configuration

The analytics system uses a separate database connection for statistics data, allowing independent configuration, scaling, and backup strategies optimized for time-series data and analytical queries.

### Database Connection Settings

The statistics database is configured via environment variables in the `aitoearn-server` service:

| Environment Variable | Purpose | Default Value |
|---------------------|---------|---------------|
| `STATISTICS_DB_HOST` | Statistics database host | `mongodb` |
| `STATISTICS_DB_PORT` | Statistics database port | `27017` |
| `STATISTICS_DB_USERNAME` | Database authentication username | `admin` |
| `STATISTICS_DB_PASSWORD` | Database authentication password | `password` |

**Sources:** [docker-compose.yml:162-171](), [DOCKER_DEPLOYMENT_EN.md:162-171]()

### Default vs. Production Configuration

```mermaid
flowchart LR
    subgraph "Development_Default"
        ServerDev["aitoearn-server"]
        SingleMongo[("MongoDB<br/>Single Instance<br/>:27017")]
        
        ServerDev -->|"Main DB"| SingleMongo
        ServerDev -->|"Statistics DB<br/>(same instance)"| SingleMongo
    end
    
    subgraph "Production_Separated"
        ServerProd["aitoearn-server"]
        MainMongo[("MongoDB Primary<br/>Main Database<br/>:27017")]
        StatsMongo[("MongoDB Analytics<br/>Statistics Database<br/>:27018")]
        
        ServerProd -->|"Main DB"| MainMongo
        ServerProd -->|"Statistics DB<br/>(separate instance)"| StatsMongo
    end
```

By default, both the main database and statistics database point to the same MongoDB instance. For production deployments with high analytics query loads, these can be separated to:

- **Isolate workloads**: Analytics queries don't impact operational database performance
- **Optimize indexing**: Statistics database can use time-series indexes
- **Scale independently**: Analytics database can be scaled horizontally for read replicas
- **Separate backup policies**: Time-series data may have different retention requirements

**Sources:** [docker-compose.yml:136-171](), [DOCKER_DEPLOYMENT_EN.md:162-171](), [DOCKER_DEPLOYMENT_CN.md:162-171]()

---

## Data Collection Pipeline

### Metrics Collection Flow

```mermaid
sequenceDiagram
    participant Platform as "Social Platform API"
    participant Server as "aitoearn-server"
    participant MainDB as "Main Database"
    participant StatsDB as "Statistics Database"
    participant Redis as "Redis Queue"
    
    Note over Server,Platform: Content Publishing Phase
    Server->>Platform: POST /publish (content)
    Platform-->>Server: 200 OK (post_id, initial_metrics)
    Server->>MainDB: Store publish record
    Server->>StatsDB: Store initial metrics
    
    Note over Server,Platform: Periodic Metrics Collection
    Server->>Redis: Schedule metrics collection job
    Redis-->>Server: Job trigger (every N minutes)
    Server->>Platform: GET /metrics (post_id)
    Platform-->>Server: Current metrics (views, likes, comments)
    Server->>StatsDB: Update metrics record
    
    Note over Server,Platform: Batch Analytics Update
    loop Every hour
        Server->>StatsDB: Aggregate metrics by platform
        Server->>StatsDB: Calculate growth rates
        Server->>StatsDB: Update summary tables
    end
```

**Sources:** [docker-compose.yml:23-39](), [README.md:79-89]()

### Collection Strategies

The analytics system employs multiple collection strategies based on platform capabilities and data freshness requirements:

1. **Real-time Collection**: Immediate metrics captured during publish operations
2. **Scheduled Polling**: Periodic API calls to fetch updated metrics (via Redis job queue)
3. **Webhook Events**: Platform-initiated updates for significant events (where supported)
4. **Batch Aggregation**: Hourly/daily rollups for dashboard performance

**Sources:** [docker-compose.yml:23-39](), [DOCKER_DEPLOYMENT_EN.md:280-281]()

---

## Performance Metrics Tracked

### Core Metrics by Platform

The analytics system tracks platform-specific metrics aligned with each platform's API capabilities:

| Platform | Metrics Tracked |
|----------|----------------|
| TikTok | Views, Likes, Comments, Shares, Play Time, Completion Rate |
| YouTube | Views, Likes, Comments, Shares, Watch Time, Subscribers Gained |
| Instagram | Likes, Comments, Saves, Reach, Impressions, Profile Visits |
| Twitter/X | Views, Likes, Retweets, Replies, Impressions, Engagement Rate |
| Facebook | Reactions, Comments, Shares, Reach, Video Views, Click-throughs |
| LinkedIn | Impressions, Clicks, Likes, Comments, Shares, Engagement Rate |
| Pinterest | Impressions, Saves, Pin Clicks, Outbound Clicks |
| Threads | Likes, Replies, Reposts, Quotes |

**Sources:** [README.md:18-21](), [docker-compose.yml:183-212]()

### Calculated Metrics

```mermaid
flowchart TB
    subgraph "Raw_Metrics"
        Views["Views/Impressions"]
        Likes["Likes/Reactions"]
        Comments["Comments"]
        Shares["Shares/Retweets"]
    end
    
    subgraph "Calculated_Metrics"
        EngagementRate["Engagement Rate =<br/>(Likes + Comments + Shares) / Views"]
        GrowthRate["Growth Rate =<br/>(Current - Previous) / Previous * 100"]
        AvgPerformance["Average Performance<br/>by Platform"]
        TopContent["Top Performing Content"]
    end
    
    subgraph "Dashboard_Insights"
        CrossPlatform["Cross-Platform<br/>Comparison"]
        TrendAnalysis["Trend Analysis"]
        ContentRanking["Content Ranking"]
    end
    
    Views --> EngagementRate
    Likes --> EngagementRate
    Comments --> EngagementRate
    Shares --> EngagementRate
    
    Views --> GrowthRate
    Likes --> GrowthRate
    
    EngagementRate --> AvgPerformance
    GrowthRate --> TopContent
    
    AvgPerformance --> CrossPlatform
    TopContent --> ContentRanking
    GrowthRate --> TrendAnalysis
```

**Sources:** [README.md:134-139]()

---

## Cross-Platform Analytics

### Platform Comparison Views

The analytics dashboard provides cross-platform insights that help users understand which platforms are performing best for their content:

```mermaid
flowchart LR
    subgraph "Data_Sources"
        TikTokStats[("TikTok<br/>Statistics")]
        YouTubeStats[("YouTube<br/>Statistics")]
        InstagramStats[("Instagram<br/>Statistics")]
        TwitterStats[("Twitter<br/>Statistics")]
        OtherStats[("Other Platforms<br/>Statistics")]
    end
    
    subgraph "Aggregation_Layer"
        Normalizer["Metrics Normalizer<br/>(Convert to common schema)"]
        Aggregator["Cross-Platform<br/>Aggregator"]
    end
    
    subgraph "Dashboard_Views"
        Overview["Overview Dashboard<br/>(All platforms summary)"]
        Comparison["Platform Comparison<br/>(Side-by-side metrics)"]
        BestPlatform["Best Performing Platform<br/>(Recommendations)"]
    end
    
    TikTokStats --> Normalizer
    YouTubeStats --> Normalizer
    InstagramStats --> Normalizer
    TwitterStats --> Normalizer
    OtherStats --> Normalizer
    
    Normalizer --> Aggregator
    Aggregator --> Overview
    Aggregator --> Comparison
    Aggregator --> BestPlatform
```

**Key Features:**

- **Normalized Metrics**: Different platform metrics are converted to comparable formats (e.g., "likes" vs "reactions" vs "favorites")
- **Performance Scores**: Weighted engagement scores allow fair comparison across platforms with different user bases
- **Traffic Distribution**: Identify which platforms are blocked or restricted and adjust content strategy
- **Growth Tracking**: Monitor follower/subscriber growth across all platforms from a single view

**Sources:** [README.md:134-139]()

---

## Database Schema Considerations

### Statistics Data Model

While the actual schema implementation is in the codebase, the statistics database typically stores:

**Time-Series Metrics Collections:**
- `platform_metrics`: Raw metrics collected from each platform API
- `content_performance`: Aggregated performance data per content piece
- `daily_summaries`: Daily rollups for historical trend analysis
- `platform_comparisons`: Pre-calculated cross-platform comparison data

**Indexing Strategy:**
- Compound indexes on `(user_id, platform, timestamp)` for user-specific queries
- Time-series indexes for efficient range queries on date ranges
- Platform-specific indexes for filtering by content type

**Data Retention:**
- Raw metrics: 90 days rolling window
- Daily summaries: 2 years
- Monthly aggregates: Permanent

**Sources:** [docker-compose.yml:162-171](), [DOCKER_DEPLOYMENT_EN.md:162-171]()

---

## Integration with Content Publishing

### Publish-to-Analytics Flow

```mermaid
flowchart TB
    subgraph "Content_Publishing"
        Draft["Content Draft"]
        Schedule["Calendar Timing"]
        Publish["Multi-Platform<br/>Publishing"]
    end
    
    subgraph "Metadata_Storage"
        MainDB[("Main Database")]
    end
    
    subgraph "Analytics_Pipeline"
        InitMetrics["Initialize Metrics Record"]
        StatsDB[("Statistics Database")]
        Collector["Periodic Metrics<br/>Collector"]
    end
    
    subgraph "User_Feedback"
        Dashboard["Analytics Dashboard"]
        Insights["Performance Insights"]
    end
    
    Draft --> Schedule
    Schedule --> Publish
    Publish -->|"Store publish record"| MainDB
    Publish -->|"Create initial metrics"| InitMetrics
    InitMetrics --> StatsDB
    
    StatsDB -->|"Schedule collection job"| Collector
    Collector -->|"Fetch updated metrics"| Publish
    Collector -->|"Update statistics"| StatsDB
    
    StatsDB -->|"Query for display"| Dashboard
    MainDB -->|"Content metadata"| Dashboard
    Dashboard --> Insights
    Insights -.->|"Inform future content"| Draft
```

This closed-loop system enables data-driven content creation:

1. **Publish Phase**: Content is distributed to platforms, initial metrics recorded
2. **Collection Phase**: Periodic updates gather performance data over time
3. **Analysis Phase**: Aggregated metrics reveal patterns and trends
4. **Optimization Phase**: Insights inform future content strategy

**Sources:** [docker-compose.yml:136-232](), [README.md:14-16](), [README.md:134-139]()

---

## Configuration Reference

### Environment Variables

All analytics-related configuration is set via environment variables in `docker-compose.yml`:

```yaml
# aitoearn-server service
STATISTICS_DB_HOST: mongodb
STATISTICS_DB_PORT: 27017
STATISTICS_DB_USERNAME: admin
STATISTICS_DB_PASSWORD: password
```

**Deployment Scenarios:**

| Scenario | Configuration | Purpose |
|----------|--------------|---------|
| **Development** | Point to same MongoDB | Simple setup, single database instance |
| **Staging** | Point to same MongoDB, separate DB name | Test with production-like data |
| **Production (Small)** | Same instance, separate credentials | Logical separation with credential isolation |
| **Production (Large)** | Separate MongoDB instance | Physical separation for performance and scaling |

**Sources:** [docker-compose.yml:162-171](), [DOCKER_DEPLOYMENT_EN.md:162-171]()

### Separating Statistics Database

To configure a separate MongoDB instance for statistics in production:

1. Deploy a dedicated MongoDB instance (e.g., on port 27018)
2. Update `docker-compose.yml`:
   ```yaml
   STATISTICS_DB_HOST: stats-mongodb.example.com
   STATISTICS_DB_PORT: 27018
   STATISTICS_DB_USERNAME: stats_admin
   STATISTICS_DB_PASSWORD: secure_stats_password
   ```
3. Ensure network connectivity between `aitoearn-server` and the statistics MongoDB
4. Configure appropriate indexes and retention policies on the statistics database

**Sources:** [DOCKER_DEPLOYMENT_EN.md:162-171](), [DOCKER_DEPLOYMENT_CN.md:162-171]()

---

## Performance and Scaling Considerations

### Query Optimization

Analytics queries can be resource-intensive. The separate database configuration enables:

- **Read Replicas**: Deploy MongoDB read replicas for analytics queries
- **Query Caching**: Redis caching layer for frequently accessed dashboard data
- **Materialized Views**: Pre-calculated aggregations for common query patterns
- **Data Partitioning**: Time-based partitioning for efficient historical queries

### High-Volume Deployments

For platforms with high publishing volumes:

1. **Batch Collection**: Group multiple content metrics into single API calls where supported
2. **Rate Limiting**: Respect platform API limits with Redis-based rate limiting
3. **Queue Management**: Use Redis Bull queues for asynchronous metrics collection
4. **Database Sharding**: Shard statistics database by user_id or timestamp ranges

**Sources:** [docker-compose.yml:23-39](), [DOCKER_DEPLOYMENT_EN.md:162-171]()

---

## Monitoring and Observability

The analytics system itself should be monitored to ensure reliable data collection:

- **Collection Success Rate**: Track percentage of successful metrics fetches
- **API Error Rates**: Monitor platform API failures and rate limit hits
- **Data Freshness**: Alert on stale data (metrics not updated in expected timeframe)
- **Database Performance**: Monitor query latency and index efficiency
- **Queue Health**: Track Redis job queue depth and processing rates

**Sources:** [docker-compose.yml:227-232](), [docker-compose.yml:265-270]()

---

## Related Systems

- **[Engagement Engine](#6.1)**: Uses analytics data to inform automated engagement strategies
- **[Multi-Platform Publishing](#4.3)**: Publishes content that generates analytics data
- **[Calendar Timing and Scheduling](#5.2)**: Uses historical analytics to optimize posting times
- **[Hotspot Analysis and Trending Content](#5.3)**: Cross-references platform analytics with trend data

**Sources:** [README.md:1-267]()

---

# Page: Deployment and Configuration

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

# Page: Docker Deployment Guide

# Docker Deployment Guide

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



This document provides step-by-step instructions for deploying the AiToEarn platform using Docker Compose. It covers the deployment architecture, service configuration, network setup, and operational procedures for running all platform components in containerized environments.

For manual development setup without Docker, see [Development Mode Setup](#8.1). For detailed environment variable configuration, see [Environment Configuration](#7.2). For storage and database setup details, see [Storage and Database Setup](#7.3).

---

## Architecture Overview

The AiToEarn platform deploys as a multi-container Docker Compose stack with seven core services orchestrated through a shared bridge network.

### Service Topology

```mermaid
graph TB
    subgraph "External Access"
        Client["Client Browser"]
        RustFSConsole["RustFS Console<br/>:9001"]
    end
    
    subgraph "Reverse Proxy Layer"
        Nginx["nginx<br/>aitoearn-nginx<br/>:8080→:80"]
    end
    
    subgraph "Application Layer"
        Web["aitoearn-web<br/>Next.js Frontend<br/>:3000"]
        Server["aitoearn-server<br/>NestJS Backend<br/>:3002"]
        AI["aitoearn-ai<br/>NestJS AI Service<br/>:3010"]
    end
    
    subgraph "Data Layer"
        MongoDB["mongodb<br/>aitoearn-mongodb<br/>:27017"]
        Redis["redis<br/>aitoearn-redis<br/>:6379"]
        RustFS["rustfs<br/>aitoearn-rustfs<br/>:9000"]
    end
    
    subgraph "Initialization"
        RustFSInit["rustfs-init<br/>mc client<br/>one-time"]
    end
    
    Client -->|http://localhost:8080| Nginx
    Client -->|http://localhost:9001| RustFSConsole
    
    Nginx -->|proxy_pass| Web
    Nginx -->|proxy_pass /api| Server
    
    Web -.->|NEXT_PUBLIC_API_URL| Server
    Server -->|AI_URL| AI
    AI -->|SERVER_URL| Server
    
    Server --> MongoDB
    Server --> Redis
    Server --> RustFS
    
    AI --> MongoDB
    AI --> Redis
    AI --> RustFS
    
    RustFSInit -.->|creates bucket| RustFS
    RustFS --> RustFSConsole
    
    MongoDB -.->|volume| MongoData[("mongodb-data<br/>mongodb-config")]
    Redis -.->|volume| RedisData[("redis-data")]
    RustFS -.->|volume| RustFSData[("rustfs-data")]
```

**Sources:** [docker-compose.yml:1-286]()

### Service Catalog

| Service Name | Container Name | Image | Internal Port | External Port | Purpose |
|-------------|----------------|-------|---------------|---------------|---------|
| `nginx` | `aitoearn-nginx` | `nginx:alpine` | 80 | 8080 | Reverse proxy and load balancer |
| `aitoearn-web` | `aitoearn-web` | `aitoearn/aitoearn-web:latest` | 3000 | - | Next.js 14 frontend application |
| `aitoearn-server` | `aitoearn-server` | `aitoearn/aitoearn-server:latest` | 3002 | - | NestJS backend API service |
| `aitoearn-ai` | `aitoearn-ai` | `aitoearn/aitoearn-ai:latest` | 3010 | - | NestJS AI orchestration service |
| `mongodb` | `aitoearn-mongodb` | `mongo:latest` | 27017 | 27017 | Document database |
| `redis` | `aitoearn-redis` | `redis:latest` | 6379 | 6379 | Cache and job queue |
| `rustfs` | `aitoearn-rustfs` | `rustfs/rustfs:latest` | 9000, 9001 | 9000, 9001 | S3-compatible object storage |
| `rustfs-init` | `aitoearn-rustfs-init` | `minio/mc:latest` | - | - | One-time bucket initialization |

**Sources:** [docker-compose.yml:1-286](), [DOCKER_DEPLOYMENT_EN.md:28-36]()

---

## Prerequisites

### System Requirements

- **Docker Engine**: 20.10 or later
- **Docker Compose**: 2.0 or later (using `docker compose` command)
- **RAM**: Minimum 4GB, recommended 8GB
- **Disk Space**: Minimum 20GB for images and volumes
- **Operating System**: Linux, macOS, or Windows with WSL2

### Verification Commands

```bash
# Check Docker version
docker --version

# Check Docker Compose version
docker compose version

# Verify Docker daemon is running
docker ps
```

**Sources:** [DOCKER_DEPLOYMENT_EN.md:38-50](), [README.md:158-167]()

---

## Deployment Steps

### Step 1: Clone Repository

```bash
git clone https://github.com/yikart/AiToEarn.git
cd AiToEarn
```

**Sources:** [README.md:164-165](), [DOCKER_DEPLOYMENT_EN.md:54-59]()

### Step 2: Configure Required Environment Variables

All environment variables are defined inline in [docker-compose.yml:1-286](). The following variables **must** be changed from their default placeholder values before production deployment:

#### Critical Security Variables

| Variable | Service(s) | Default | Required Action |
|----------|-----------|---------|-----------------|
| `MONGO_INITDB_ROOT_PASSWORD` | `mongodb` | `password` | Change to secure password |
| `MONGODB_PASSWORD` | `aitoearn-ai`, `aitoearn-server` | `password` | Match MongoDB password |
| `REDIS_PASSWORD` | `aitoearn-ai`, `aitoearn-server` | `password` | Match Redis `--requirepass` |
| `JWT_SECRET` | `aitoearn-ai`, `aitoearn-server` | `change-this-jwt-secret` | Generate random string (≥32 chars) |
| `INTERNAL_TOKEN` | `aitoearn-ai`, `aitoearn-server` | `change-this-secret-token` | Generate random string (≥32 chars) |

#### Domain Configuration

| Variable | Service | Default | Production Value |
|----------|---------|---------|------------------|
| `APP_DOMAIN` | `aitoearn-server` | `localhost` | Your public domain (e.g., `app.example.com`) |
| `NEXT_PUBLIC_API_URL` | `aitoearn-web` | `http://localhost:8080/api` | `https://app.example.com/api` |

**Password Generation Example:**
```bash
# Generate random 32-byte hex string
openssl rand -hex 32
```

**Sources:** [docker-compose.yml:6-174](), [DOCKER_DEPLOYMENT_EN.md:61-95]()

### Step 3: Configure Application Config Files

The `config/` directory contains service-specific configuration files mounted as read-only volumes:

```mermaid
graph LR
    subgraph "Host System"
        AIConfig["config/aitoearn-ai.config.js"]
        ServerConfig["config/aitoearn-server.config.js"]
        GCSFile["config/gcs-placeholder.json"]
    end
    
    subgraph "aitoearn-ai Container"
        AIAppConfig["/app/config.js"]
        AIGCSConfig["/app/config/gcs-placeholder.json"]
    end
    
    subgraph "aitoearn-server Container"
        ServerAppConfig["/app/config.js"]
    end
    
    AIConfig -->|ro volume| AIAppConfig
    ServerConfig -->|ro volume| ServerAppConfig
    GCSFile -->|ro volume| AIGCSConfig
```

| Config File | Mount Point | Purpose |
|------------|-------------|---------|
| `config/aitoearn-ai.config.js` | `aitoearn-ai:/app/config.js` | AI model definitions, storage endpoints, logger settings |
| `config/aitoearn-server.config.js` | `aitoearn-server:/app/config.js` | OAuth callbacks, SMTP settings, storage configuration |
| `config/gcs-placeholder.json` | `aitoearn-ai:/app/config/gcs-placeholder.json` | Google Cloud service account key (placeholder) |

**Default RustFS Configuration** (no changes needed for local deployment):
- The config files reference `http://rustfs.local:9000` as storage endpoint
- Credentials: `rustfsadmin` / `rustfsadmin`
- Bucket: `aitoearn`

**For External S3/OSS Storage**, modify the `assets` object in both config files:

```javascript
// Example for AWS S3
assets: {
  provider: 's3',
  region: 'us-east-1',
  bucketName: 'your-bucket-name',
  endpoint: 'https://s3.us-east-1.amazonaws.com',
  accessKeyId: process.env.AWS_ACCESS_KEY_ID,
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  cdnEndpoint: 'https://cdn.example.com',
}
```

**Sources:** [docker-compose.yml:90-92](), [docker-compose.yml:147-148](), [DOCKER_DEPLOYMENT_EN.md:97-110]()

### Step 4: Start All Services

```bash
# Start in detached mode
docker compose up -d

# View startup logs
docker compose logs -f
```

The startup sequence follows dependency order defined by `depends_on` conditions:

1. **Data Layer**: `mongodb`, `redis`, `rustfs` start and pass health checks
2. **Initialization**: `rustfs-init` creates the `aitoearn` bucket
3. **AI Service**: `aitoearn-ai` starts after MongoDB/Redis are healthy
4. **Backend**: `aitoearn-server` starts after `aitoearn-ai` is healthy
5. **Frontend**: `aitoearn-web` starts after `aitoearn-server` is healthy
6. **Proxy**: `nginx` starts after all application services are running

**Sources:** [docker-compose.yml:85-147](), [README.md:166]()

### Step 5: Verify Deployment

```bash
# Check all containers are running
docker compose ps

# Expected output: all services show "healthy" or "running" status
```

**Service Status Indicators:**

| Status | Meaning | Action |
|--------|---------|--------|
| `healthy` | Health check passing | None required |
| `running` | Container running (no health check) | None required |
| `starting` | Health check not yet passing | Wait 30-60 seconds |
| `unhealthy` | Health check failing | Check logs: `docker compose logs <service>` |
| `exited` | Container crashed | Check logs and restart |

**Sources:** [DOCKER_DEPLOYMENT_EN.md:120-126](), [docker-compose.yml:16-40]()

---

## Service Configuration Details

### Nginx Reverse Proxy

**Container:** `aitoearn-nginx` | **Port:** `8080:80`

The nginx service acts as the unified entry point, routing requests to backend services based on URL path.

```mermaid
graph LR
    Client["HTTP Client"] -->|":8080"| Nginx["nginx<br/>aitoearn-nginx"]
    
    Nginx -->|"/"| Web["aitoearn-web:3000"]
    Nginx -->|"/api/*"| Server["aitoearn-server:3002"]
    Nginx -->|"/_nhealth"| HealthCheck["nginx health endpoint"]
```

**Configuration Mount:**
- [nginx/nginx.conf]() → `/etc/nginx/nginx.conf` (read-only)

**Routing Rules:**
- `/` → `http://aitoearn-web:3000`
- `/api/*` → `http://aitoearn-server:3002/api/*`
- `/_nhealth` → nginx internal health check

**Health Check:**
```yaml
test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost/_nhealth"]
interval: 10s
timeout: 5s
retries: 3
```

**Sources:** [docker-compose.yml:248-270](), [DOCKER_DEPLOYMENT_EN.md:28-36]()

### Frontend Service (aitoearn-web)

**Container:** `aitoearn-web` | **Port:** `3000` (internal only)

Next.js 14 server-side rendered frontend application.

**Environment Variables:**
```yaml
NODE_ENV: production
NEXT_TELEMETRY_DISABLED: 1
NEXT_PUBLIC_API_URL: http://localhost:8080/api  # Browser-facing API URL
```

**Runtime Behavior:**
- Built as production optimized bundle
- Server-side rendering enabled
- API calls from browser go to `NEXT_PUBLIC_API_URL`
- Internal server-side API calls (if any) can use `http://aitoearn-server:3002`

**Dependency Chain:**
```
aitoearn-web → aitoearn-server (healthy) → nginx
```

**Sources:** [docker-compose.yml:234-246](), [DOCKER_DEPLOYMENT_EN.md:151]()

### Backend Service (aitoearn-server)

**Container:** `aitoearn-server` | **Port:** `3002` (internal only)

NestJS backend API handling OAuth, content management, platform integrations, and business logic.

**Critical Environment Variables:**

| Variable | Purpose | Default |
|----------|---------|---------|
| `MONGODB_HOST` | Main database host | `mongodb` |
| `STATISTICS_DB_HOST` | Analytics database host | `mongodb` |
| `REDIS_HOST` | Cache/queue host | `redis` |
| `AI_URL` | AI service endpoint | `http://aitoearn-ai:3010` |
| `JWT_SECRET` | JWT signing key | Must change |
| `INTERNAL_TOKEN` | Inter-service auth | Must change |
| `APP_DOMAIN` | OAuth callback domain | `localhost` |

**OAuth Callback URL Pattern:**
```
https://{APP_DOMAIN}/api/plat/{platform}/auth/back
```

Supported platforms: `bilibili`, `google`, `kwai`, `pinterest`, `tiktok`, `twitter`, `facebook`, `threads`, `instagram`, `linkedin`, `youtube`, `wxplat`, `doyin`

**Configuration Mount:**
- [config/aitoearn-server.config.js]() → `/app/config.js` (read-only)

**Health Check:**
```yaml
test: ["CMD", "node", "-e", "require('http').get('http://localhost:3002/health', (r) => { process.exit(r.statusCode === 200 ? 0 : 1) })"]
interval: 30s
timeout: 10s
retries: 3
start_period: 60s
```

**Sources:** [docker-compose.yml:136-232](), [DOCKER_DEPLOYMENT_EN.md:145-151]()

### AI Service (aitoearn-ai)

**Container:** `aitoearn-ai` | **Port:** `3010` (internal only)

NestJS service orchestrating multiple AI providers for content generation, image processing, and video creation.

**AI Provider Configuration:**

| Variable | Provider | Required |
|----------|----------|----------|
| `OPENAI_API_KEY` | OpenAI GPT models | Yes (or relay service) |
| `OPENAI_BASE_URL` | API endpoint | Default: `https://api.openai.com/v1` |
| `ANTHROPIC_API_KEY` | Claude models | Optional |
| `ANTHROPIC_BASE_URL` | API endpoint | Default: `https://api.anthropic.com` |
| `GEMINI_KEY_PAIRS` | Google Gemini | Optional (JSON array) |
| `GEMINI_LOCATION` | GCP region | Default: `us-central1` |
| `VOLCENGINE_API_KEY` | Doubao models | Optional |
| `GROK_API_KEY` | xAI Grok | Optional |
| `AICSO_API_KEY` | AICSO service | Optional |
| `AI_PROXY_URL` | HTTP proxy for AI APIs | Optional |

**GEMINI_KEY_PAIRS Format:**
```json
[
  {
    "projectId": "your-gcp-project",
    "apiKey": "your-api-key",
    "keyFile": "/app/config/gcs-placeholder.json",
    "bucket": "your-bucket"
  }
]
```

**Configuration Mounts:**
- [config/aitoearn-ai.config.js]() → `/app/config.js` (read-only)
- [config/gcs-placeholder.json]() → `/app/config/gcs-placeholder.json` (read-only)

**Health Check:**
```yaml
test: ["CMD", "node", "-e", "require('http').get('http://localhost:3010/health', (r) => { process.exit(r.statusCode === 200 ? 0 : 1) })"]
interval: 30s
timeout: 10s
retries: 3
start_period: 60s
```

**Recommended Setup: Use AI Relay Service**

Instead of configuring multiple AI providers directly, use [new-api](https://github.com/Calcium-Ion/new-api) or [one-api](https://github.com/songquanpeng/one-api) as a unified gateway:

```yaml
OPENAI_BASE_URL: https://your-new-api-host/v1
OPENAI_API_KEY: sk-your-relay-key
```

**Sources:** [docker-compose.yml:81-134](), [DOCKER_DEPLOYMENT_EN.md:204-248]()

---

## Data Layer Services

### MongoDB Database

**Container:** `aitoearn-mongodb` | **Port:** `27017:27017`

Document database storing user data, content, OAuth tokens, and application state.

**Configuration:**

```yaml
environment:
  MONGO_INITDB_ROOT_USERNAME: admin
  MONGO_INITDB_ROOT_PASSWORD: password  # Change this
ports:
  - "27017:27017"
volumes:
  - mongodb-data:/data/db
  - mongodb-config:/data/configdb
```

**Health Check:**
```yaml
test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
interval: 10s
timeout: 5s
retries: 5
start_period: 40s
```

**Connection String (internal):**
```
mongodb://admin:password@mongodb:27017
```

**Database Names:**
- `aitoearn` - Main application database
- Statistics database (defaults to same instance, configurable via `STATISTICS_DB_*` variables)

**Sources:** [docker-compose.yml:2-21]()

### Redis Cache and Queue

**Container:** `aitoearn-redis` | **Port:** `6379:6379`

In-memory data store used for:
- Session management
- Job queue (BullMQ)
- Rate limiting
- Caching frequently accessed data

**Configuration:**

```yaml
command: redis-server --requirepass password  # Change password
ports:
  - "6379:6379"
volumes:
  - redis-data:/data
```

**Health Check:**
```yaml
test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
interval: 10s
timeout: 3s
retries: 5
start_period: 30s
```

**Connection String (internal):**
```
redis://:password@redis:6379
```

**Sources:** [docker-compose.yml:23-39]()

### RustFS Object Storage

**Containers:** `aitoearn-rustfs`, `aitoearn-rustfs-init`

**Ports:** 
- `9000:9000` - S3-compatible API
- `9001:9001` - Web management console

S3-compatible object storage for uploaded images, videos, and documents. RustFS provides a lightweight alternative to AWS S3 for local/self-hosted deployments.

**Service Configuration:**

```yaml
rustfs:
  image: rustfs/rustfs:latest
  hostname: rustfs.local
  environment:
    RUSTFS_ACCESS_KEY: rustfsadmin
    RUSTFS_SECRET_KEY: rustfsadmin
  volumes:
    - rustfs-data:/data
  networks:
    aitoearn-network:
      aliases:
        - rustfs.local  # DNS alias for internal access
```

**Initialization Container:**

The `rustfs-init` service runs once at startup to create the `aitoearn` bucket and set public read access:

```yaml
rustfs-init:
  image: minio/mc:latest
  depends_on:
    rustfs:
      condition: service_healthy
  entrypoint: >
    /bin/sh -c "
    mc alias set rustfs http://rustfs.local:9000 rustfsadmin rustfsadmin;
    mc mb rustfs/aitoearn --ignore-existing;
    mc anonymous set download rustfs/aitoearn;
    exit 0;
    "
```

**Access Patterns:**

| Access Type | Endpoint | Credentials |
|------------|----------|-------------|
| Internal API calls | `http://rustfs.local:9000` | `rustfsadmin` / `rustfsadmin` |
| Web console (browser) | `http://localhost:9001` | `rustfsadmin` / `rustfsadmin` |
| S3 SDK connections | `http://localhost:9000` | `rustfsadmin` / `rustfsadmin` |

**Configuration in Application:**

Both [config/aitoearn-ai.config.js]() and [config/aitoearn-server.config.js]() define:

```javascript
assets: {
  provider: 's3',
  region: 'us-east-1',
  bucketName: 'aitoearn',
  endpoint: 'http://rustfs.local:9000',
  accessKeyId: 'rustfsadmin',
  secretAccessKey: 'rustfsadmin',
  s3ForcePathStyle: true,
}
```

**Sources:** [docker-compose.yml:41-79](), [DOCKER_DEPLOYMENT_EN.md:173-202]()

---

## Network Configuration

### Docker Network: aitoearn-network

All services communicate through a dedicated bridge network named `aitoearn-network`, providing DNS resolution and network isolation.

```mermaid
graph TB
    subgraph "aitoearn-network (bridge)"
        nginx["nginx<br/>aitoearn-nginx"]
        web["aitoearn-web"]
        server["aitoearn-server"]
        ai["aitoearn-ai"]
        mongodb["mongodb"]
        redis["redis"]
        rustfs["rustfs<br/>rustfs.local"]
    end
    
    subgraph "External"
        host["Host Machine<br/>localhost"]
    end
    
    host -->|8080:80| nginx
    host -->|27017:27017| mongodb
    host -->|6379:6379| redis
    host -->|9000:9000<br/>9001:9001| rustfs
    
    nginx -.->|internal DNS| web
    nginx -.->|internal DNS| server
    server -.->|internal DNS| ai
    server -.->|internal DNS| mongodb
    server -.->|internal DNS| redis
    server -.->|internal DNS| rustfs
    ai -.->|internal DNS| mongodb
    ai -.->|internal DNS| redis
    ai -.->|internal DNS| rustfs
```

**Network Definition:**

```yaml
networks:
  aitoearn-network:
    driver: bridge
    name: aitoearn-network
```

**DNS Resolution:**

Services communicate using container names as hostnames:
- `mongodb` → `aitoearn-mongodb` container
- `redis` → `aitoearn-redis` container
- `rustfs.local` → `aitoearn-rustfs` container (with network alias)
- `aitoearn-server` → `aitoearn-server` container
- `aitoearn-ai` → `aitoearn-ai` container

**Port Exposure Strategy:**

| Service | Internal Port | Exposed Port | Reason for Exposure |
|---------|--------------|--------------|---------------------|
| `nginx` | 80 | 8080 | Web UI and API access |
| `mongodb` | 27017 | 27017 | Development database access |
| `redis` | 6379 | 6379 | Development cache access |
| `rustfs` | 9000, 9001 | 9000, 9001 | API and console access |
| `aitoearn-web` | 3000 | - | Proxied through nginx |
| `aitoearn-server` | 3002 | - | Proxied through nginx |
| `aitoearn-ai` | 3010 | - | Internal only |

**Sources:** [docker-compose.yml:272-275]()

---

## Volume Management

### Persistent Volumes

Docker Compose creates four named volumes for data persistence:

```yaml
volumes:
  mongodb-data:
    driver: local
  mongodb-config:
    driver: local
  redis-data:
    driver: local
  rustfs-data:
    driver: local
```

**Volume Usage:**

| Volume Name | Mount Point | Service | Contents |
|------------|-------------|---------|----------|
| `mongodb-data` | `/data/db` | `mongodb` | Database files |
| `mongodb-config` | `/data/configdb` | `mongodb` | MongoDB configuration |
| `redis-data` | `/data` | `redis` | RDB snapshots, AOF logs |
| `rustfs-data` | `/data` | `rustfs` | Object storage files |

**Volume Inspection:**

```bash
# List all volumes
docker volume ls

# Inspect volume details
docker volume inspect aitoearn_mongodb-data

# Check disk usage
docker system df -v
```

**Backup Procedures:**

```bash
# Backup MongoDB
docker compose exec mongodb mongodump --uri="mongodb://admin:password@localhost:27017" --out=/tmp/backup
docker cp aitoearn-mongodb:/tmp/backup ./mongodb-backup

# Backup Redis
docker compose exec redis redis-cli --rdb /tmp/dump.rdb
docker cp aitoearn-redis:/tmp/dump.rdb ./redis-backup.rdb

# Backup RustFS (entire data directory)
docker run --rm -v aitoearn_rustfs-data:/data -v $(pwd):/backup alpine tar czf /backup/rustfs-backup.tar.gz /data
```

**Volume Cleanup (DANGER):**

```bash
# Remove all volumes (loses all data)
docker compose down -v

# Remove specific volume
docker volume rm aitoearn_mongodb-data
```

**Sources:** [docker-compose.yml:277-285](), [docker-compose.yml:12-13](), [docker-compose.yml:31](), [docker-compose.yml:53]()

---

## Health Check System

### Health Check Configuration

Each service defines health checks to ensure proper startup sequencing and monitor runtime health.

```mermaid
graph TD
    subgraph "Health Check Flow"
        Start["Container Starts"] --> StartPeriod["start_period<br/>Grace Period"]
        StartPeriod --> FirstCheck["First Health Check"]
        FirstCheck -->|Pass| Healthy["Status: healthy"]
        FirstCheck -->|Fail| Retry["Retry after interval"]
        Retry -->|retries exhausted| Unhealthy["Status: unhealthy"]
        Retry -->|Pass before retries| Healthy
    end
```

**Health Check Parameters:**

| Service | Test Command | Interval | Timeout | Retries | Start Period |
|---------|-------------|----------|---------|---------|--------------|
| `mongodb` | `mongosh ping` | 10s | 5s | 5 | 40s |
| `redis` | `redis-cli incr ping` | 10s | 3s | 5 | 30s |
| `rustfs` | `curl http://localhost:9000/health` | 10s | 5s | 5 | 30s |
| `aitoearn-ai` | Node.js HTTP GET `/health` | 30s | 10s | 3 | 60s |
| `aitoearn-server` | Node.js HTTP GET `/health` | 30s | 10s | 3 | 60s |
| `nginx` | `wget /_nhealth` | 10s | 5s | 3 | 10s |

**Dependency Chain:**

```
mongodb (healthy) ──┐
redis (healthy) ────┤
                    ├──> aitoearn-ai (healthy) ──> aitoearn-server (healthy) ──> aitoearn-web ──> nginx
rustfs (healthy) ───┘
```

**Checking Health Status:**

```bash
# View health status of all services
docker compose ps

# Watch health checks in real-time
watch -n 2 'docker compose ps'

# Inspect health check details
docker inspect --format='{{.State.Health.Status}}' aitoearn-server
```

**Sources:** [docker-compose.yml:16-21](), [docker-compose.yml:34-39](), [docker-compose.yml:58-63](), [docker-compose.yml:129-134](), [docker-compose.yml:227-232](), [docker-compose.yml:265-270]()

---

## Accessing Services

### Service Endpoints

After successful deployment, access services through the following URLs:

| Service | URL | Credentials | Purpose |
|---------|-----|-------------|---------|
| **Web Frontend** | http://localhost:8080 | User registration/login | Main application UI |
| **Backend API** | http://localhost:8080/api | JWT token from login | REST API endpoints |
| **Nginx Health** | http://localhost:8080/_nhealth | None | Nginx status check |
| **RustFS Console** | http://localhost:9001 | `rustfsadmin` / `rustfsadmin` | Object storage management |
| **MongoDB** | `localhost:27017` | `admin` / `password` | Database access (dev only) |
| **Redis** | `localhost:6379` | `password` | Cache access (dev only) |

**API Request Example:**

```bash
# Login to get JWT token
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# Use token in subsequent requests
curl http://localhost:8080/api/user/profile \
  -H "Authorization: Bearer <jwt-token>"
```

**Database Connection (MongoDB Compass):**

```
Connection String: mongodb://admin:password@localhost:27017
```

**Sources:** [README.md:173-180](), [DOCKER_DEPLOYMENT_EN.md:128-135]()

---

## Common Operations

### Starting and Stopping

```bash
# Start all services
docker compose up -d

# Start specific services
docker compose up -d nginx aitoearn-web aitoearn-server

# Stop all services (keeps data)
docker compose stop

# Stop and remove containers (keeps volumes)
docker compose down

# Stop and remove containers + volumes (LOSES DATA)
docker compose down -v
```

### Viewing Logs

```bash
# Follow logs from all services
docker compose logs -f

# Follow logs from specific service
docker compose logs -f aitoearn-server

# View last 100 lines
docker compose logs --tail=100 aitoearn-ai

# Filter logs by timestamp
docker compose logs --since 2024-01-01T00:00:00
```

### Restarting Services

```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart aitoearn-server

# Restart with rebuild (after config changes)
docker compose up -d --force-recreate aitoearn-server
```

### Scaling Services

```bash
# Scale aitoearn-server to 3 instances
docker compose up -d --scale aitoearn-server=3

# Note: Load balancing requires nginx configuration changes
```

### Updating Images

```bash
# Pull latest images
docker compose pull

# Recreate containers with new images
docker compose up -d

# Rebuild from Dockerfile (if building locally)
docker compose build
docker compose up -d
```

### Resource Monitoring

```bash
# View resource usage
docker stats

# View disk usage
docker system df

# Check container resource limits
docker inspect --format='{{.HostConfig.Memory}}' aitoearn-server
```

**Sources:** [README.md:166]()

---

## Troubleshooting

### Service Won't Start

**Symptom:** Container exits immediately or shows `unhealthy` status

**Diagnosis:**
```bash
# Check container logs
docker compose logs <service-name>

# Check last 50 lines of logs
docker compose logs --tail=50 <service-name>

# Inspect container exit code
docker compose ps
docker inspect <container-name> | grep ExitCode
```

**Common Causes:**

| Issue | Solution |
|-------|----------|
| Port already in use | Check `netstat -tuln \| grep <port>`, stop conflicting process |
| Invalid environment variable | Verify `docker-compose.yml` syntax, check for missing quotes |
| Volume permission error | Check `docker volume inspect`, ensure host directories exist |
| Health check failing too quickly | Increase `start_period` or decrease `retries` |
| Out of memory | Check `docker stats`, increase host RAM or reduce service count |

### Database Connection Failures

**Symptom:** `aitoearn-server` or `aitoearn-ai` cannot connect to MongoDB/Redis

**Diagnosis:**
```bash
# Test MongoDB connection from server container
docker compose exec aitoearn-server node -e "console.log(process.env.MONGODB_HOST)"

# Test Redis connection
docker compose exec aitoearn-server node -e "const redis = require('redis'); redis.createClient({host: 'redis', port: 6379, password: 'password'}).connect().then(() => console.log('OK')).catch(console.error)"
```

**Solutions:**
1. Verify MongoDB is healthy: `docker compose ps mongodb`
2. Check password matches across services
3. Ensure services are on same network: `docker network inspect aitoearn-network`
4. Verify DNS resolution: `docker compose exec aitoearn-server ping mongodb`

### RustFS Not Accessible

**Symptom:** Asset uploads fail or return 404

**Diagnosis:**
```bash
# Check rustfs health
docker compose ps rustfs

# Verify bucket exists
docker compose exec rustfs sh -c "ls /data"

# Test S3 API connectivity
curl http://localhost:9000/aitoearn
```

**Solutions:**
1. Verify `rustfs-init` completed successfully
2. Check network alias: `docker network inspect aitoearn-network | grep rustfs.local`
3. Recreate bucket manually:
   ```bash
   docker compose exec rustfs-init /bin/sh -c "mc alias set rustfs http://rustfs.local:9000 rustfsadmin rustfsadmin && mc mb rustfs/aitoearn --ignore-existing"
   ```

### Nginx 502 Bad Gateway

**Symptom:** Browser shows "502 Bad Gateway" error

**Diagnosis:**
```bash
# Check nginx error logs
docker compose logs nginx | grep error

# Verify upstream services are healthy
docker compose ps aitoearn-web aitoearn-server

# Test upstream directly
curl http://localhost:3000  # Should not work (not exposed)
docker compose exec nginx curl http://aitoearn-web:3000  # Should work
```

**Solutions:**
1. Ensure `aitoearn-web` and `aitoearn-server` are running and healthy
2. Check nginx config syntax: `docker compose exec nginx nginx -t`
3. Verify `depends_on` conditions are met
4. Restart nginx: `docker compose restart nginx`

### Permission Denied on Volumes

**Symptom:** Containers crash with "Permission denied" errors in logs

**Solutions:**
```bash
# Check volume ownership (Linux/Mac)
ls -la $(docker volume inspect aitoearn_mongodb-data --format '{{.Mountpoint}}')

# Fix permissions (run as root)
sudo chown -R 999:999 /var/lib/docker/volumes/aitoearn_mongodb-data/_data  # MongoDB UID
```

### Disk Space Issues

**Diagnosis:**
```bash
# Check Docker disk usage
docker system df -v

# Find large volumes
docker volume ls --format "{{.Name}}" | xargs -I {} docker volume inspect {} --format '{{.Name}}: {{.Mountpoint}}' | xargs -I {} sh -c 'du -sh {}'
```

**Cleanup:**
```bash
# Remove unused containers/images/volumes
docker system prune -a --volumes

# Remove only unused images
docker image prune -a

# Remove specific old images
docker images | grep '<none>' | awk '{print $3}' | xargs docker rmi
```

**Sources:** [DOCKER_DEPLOYMENT_EN.md]()

---

# Page: Environment Configuration

# Environment Configuration

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



This document provides a comprehensive reference for all environment variables used across the AiToEarn platform services. Environment configuration is the primary mechanism for deploying and customizing AiToEarn installations, controlling database connections, API integrations, authentication secrets, and external service credentials.

For deployment procedures using these environment variables, see [Docker Deployment Guide](#7.1). For database and storage setup details, see [Storage and Database Setup](#7.3). For development mode configuration without Docker, see [Development Mode Setup](#8.1).

## Configuration Architecture Overview

The AiToEarn platform uses a layered configuration architecture where environment variables defined in `docker-compose.yml` flow through to individual services, which may combine them with hardcoded configuration in JavaScript config files.

### Configuration Flow Diagram

```mermaid
graph TB
    subgraph "Configuration Sources"
        DC["docker-compose.yml<br/>Environment Variables"]
        CF1["config/aitoearn-ai.config.js<br/>Hardcoded Configs"]
        CF2["config/aitoearn-server.config.js<br/>Hardcoded Configs"]
        CF3["config/gcs-placeholder.json<br/>GCP Credentials"]
    end
    
    subgraph "Runtime Services"
        AI["aitoearn-ai<br/>:3010"]
        SRV["aitoearn-server<br/>:3002"]
        WEB["aitoearn-web<br/>:3000"]
        MONGO["mongodb<br/>:27017"]
        REDIS["redis<br/>:6379"]
        RUSTFS["rustfs<br/>:9000/9001"]
    end
    
    DC -->|"MONGODB_PASSWORD<br/>REDIS_PASSWORD<br/>JWT_SECRET<br/>AI Keys"| AI
    DC -->|"MONGODB_PASSWORD<br/>REDIS_PASSWORD<br/>JWT_SECRET<br/>OAuth Secrets"| SRV
    DC -->|"NEXT_PUBLIC_API_URL"| WEB
    DC -->|"MONGO_INITDB_ROOT_PASSWORD"| MONGO
    DC -->|"requirepass password"| REDIS
    DC -->|"RUSTFS_ACCESS_KEY<br/>RUSTFS_SECRET_KEY"| RUSTFS
    
    CF1 -->|"read-only mount"| AI
    CF2 -->|"read-only mount"| SRV
    CF3 -->|"read-only mount"| AI
    
    AI -->|"process.env + config.js"| AIRuntime["AI Service Runtime"]
    SRV -->|"process.env + config.js"| SRVRuntime["Server Runtime"]
    WEB -->|"process.env"| WEBRuntime["Web Runtime"]
```

**Sources:** [docker-compose.yml:1-286](), [DOCKER_DEPLOYMENT_EN.md:1-500]()

### Configuration Layer Responsibilities

| Layer | File/Location | Purpose | Modification Method |
|-------|---------------|---------|---------------------|
| **Environment Variables** | `docker-compose.yml` `environment` sections | Runtime secrets, credentials, service URLs | Edit docker-compose.yml, restart containers |
| **Application Config** | `config/aitoearn-ai.config.js`<br/>`config/aitoearn-server.config.js` | Service-specific settings, model definitions, storage endpoints | Edit config files, restart containers |
| **Credential Files** | `config/gcs-placeholder.json` | Google Cloud service account keys | Replace file, restart containers |
| **Nginx Config** | `nginx/nginx.conf` | Routing rules, upstream definitions | Edit nginx.conf, restart nginx container |

**Sources:** [docker-compose.yml:91-92](), [docker-compose.yml:148](), [docker-compose.yml:262]()

## Database and Cache Services Configuration

### MongoDB Configuration

MongoDB serves as the primary document database and statistics database for the platform.

#### MongoDB Environment Variables

```mermaid
graph LR
    subgraph "mongodb service"
        MROOT["MONGO_INITDB_ROOT_USERNAME<br/>Default: admin"]
        MRPASS["MONGO_INITDB_ROOT_PASSWORD<br/>Default: password"]
    end
    
    subgraph "Consuming Services"
        AI_MONGO["aitoearn-ai<br/>MONGODB_USERNAME<br/>MONGODB_PASSWORD<br/>MONGODB_HOST<br/>MONGODB_PORT"]
        SRV_MONGO["aitoearn-server<br/>MONGODB_USERNAME<br/>MONGODB_PASSWORD<br/>MONGODB_HOST<br/>MONGODB_PORT"]
        SRV_STATS["aitoearn-server<br/>STATISTICS_DB_USERNAME<br/>STATISTICS_DB_PASSWORD<br/>STATISTICS_DB_HOST<br/>STATISTICS_DB_PORT"]
    end
    
    MRPASS -->|"must match"| AI_MONGO
    MRPASS -->|"must match"| SRV_MONGO
    MRPASS -->|"usually same"| SRV_STATS
```

**MongoDB Service Environment Variables** ([docker-compose.yml:2-21]()):

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGO_INITDB_ROOT_USERNAME` | `admin` | MongoDB root user |
| `MONGO_INITDB_ROOT_PASSWORD` | `password` | MongoDB root password - **MUST CHANGE** |

**Consumer Service Variables** (aitoearn-ai: [docker-compose.yml:100-103](), aitoearn-server: [docker-compose.yml:157-160]()):

| Variable | Service | Default | Description |
|----------|---------|---------|-------------|
| `MONGODB_HOST` | aitoearn-ai, aitoearn-server | `mongodb` | MongoDB container hostname |
| `MONGODB_PORT` | aitoearn-ai, aitoearn-server | `27017` | MongoDB port |
| `MONGODB_USERNAME` | aitoearn-ai, aitoearn-server | `admin` | MongoDB username |
| `MONGODB_PASSWORD` | aitoearn-ai, aitoearn-server | `password` | MongoDB password - must match root password |

**Statistics Database Variables** ([docker-compose.yml:162-165]()):

| Variable | Service | Default | Description |
|----------|---------|---------|-------------|
| `STATISTICS_DB_HOST` | aitoearn-server | `mongodb` | Statistics DB host (can be separate instance) |
| `STATISTICS_DB_PORT` | aitoearn-server | `27017` | Statistics DB port |
| `STATISTICS_DB_USERNAME` | aitoearn-server | `admin` | Statistics DB username |
| `STATISTICS_DB_PASSWORD` | aitoearn-server | `password` | Statistics DB password |

**Sources:** [docker-compose.yml:2-21](), [docker-compose.yml:100-103](), [docker-compose.yml:157-165]()

### Redis Configuration

Redis provides caching, session storage, and job queue functionality.

#### Redis Environment Variables

**Redis Service** ([docker-compose.yml:23-39]()):

| Variable | Default | Description |
|----------|---------|-------------|
| `command` | `redis-server --requirepass password` | Redis startup command with password |

The password is embedded in the command line. To change it, modify both the command and all consumer service `REDIS_PASSWORD` variables.

**Consumer Service Variables** ([docker-compose.yml:105-107](), [docker-compose.yml:167-169]()):

| Variable | Service | Default | Description |
|----------|---------|---------|-------------|
| `REDIS_HOST` | aitoearn-ai, aitoearn-server | `redis` | Redis container hostname |
| `REDIS_PORT` | aitoearn-ai, aitoearn-server | `6379` | Redis port |
| `REDIS_PASSWORD` | aitoearn-ai, aitoearn-server | `password` | Redis password - must match command |

**Sources:** [docker-compose.yml:23-39](), [docker-compose.yml:105-107](), [docker-compose.yml:167-169]()

## Object Storage Configuration (RustFS)

RustFS provides S3-compatible object storage for media assets, generated content, and user uploads.

### RustFS Service Environment Variables

```mermaid
graph TB
    subgraph "rustfs service"
        RAKEY["RUSTFS_ACCESS_KEY<br/>Default: rustfsadmin"]
        RSKEY["RUSTFS_SECRET_KEY<br/>Default: rustfsadmin"]
    end
    
    subgraph "rustfs-init service"
        INIT["mc alias set command<br/>rustfsadmin / rustfsadmin"]
    end
    
    subgraph "Application Config Files"
        AI_CFG["aitoearn-ai.config.js<br/>assets.accessKeyId<br/>assets.secretAccessKey"]
        SRV_CFG["aitoearn-server.config.js<br/>assets.accessKeyId<br/>assets.secretAccessKey"]
    end
    
    RAKEY -->|"credentials"| INIT
    RSKEY -->|"credentials"| INIT
    RAKEY -.->|"must match"| AI_CFG
    RSKEY -.->|"must match"| AI_CFG
    RAKEY -.->|"must match"| SRV_CFG
    RSKEY -.->|"must match"| SRV_CFG
```

**RustFS Service Variables** ([docker-compose.yml:41-63]()):

| Variable | Default | Description |
|----------|---------|-------------|
| `RUSTFS_ACCESS_KEY` | `rustfsadmin` | S3-compatible access key ID |
| `RUSTFS_SECRET_KEY` | `rustfsadmin` | S3-compatible secret access key |

**RustFS Initialization** ([docker-compose.yml:65-79]()):

The `rustfs-init` service uses `minio/mc` to create the initial bucket. Credentials in the `entrypoint` command must match `RUSTFS_ACCESS_KEY` and `RUSTFS_SECRET_KEY`.

**Application Configuration Files:**

RustFS credentials are **not** passed as environment variables to `aitoearn-ai` or `aitoearn-server`. Instead, they are hardcoded in the config files that are mounted as read-only volumes. To change credentials:

1. Update `RUSTFS_ACCESS_KEY` and `RUSTFS_SECRET_KEY` in [docker-compose.yml:47-48]()
2. Update credentials in [docker-compose.yml:75]() `mc alias set` command
3. Edit `config/aitoearn-ai.config.js` assets configuration (search for `accessKeyId` and `secretAccessKey`)
4. Edit `config/aitoearn-server.config.js` assets configuration (search for `accessKeyId` and `secretAccessKey`)

**Sources:** [docker-compose.yml:41-79](), [DOCKER_DEPLOYMENT_EN.md:173-188]()

## Authentication and Security Configuration

### JWT and Internal Authentication

These variables control user authentication tokens and inter-service communication.

```mermaid
graph LR
    subgraph "Shared Secrets"
        JWT["JWT_SECRET<br/>User auth tokens"]
        INTERNAL["INTERNAL_TOKEN<br/>Service-to-service auth"]
    end
    
    subgraph "aitoearn-ai"
        AI_JWT["JWT_SECRET"]
        AI_INT["INTERNAL_TOKEN"]
    end
    
    subgraph "aitoearn-server"
        SRV_JWT["JWT_SECRET"]
        SRV_INT["INTERNAL_TOKEN"]
    end
    
    JWT -->|"MUST MATCH"| AI_JWT
    JWT -->|"MUST MATCH"| SRV_JWT
    INTERNAL -->|"MUST MATCH"| AI_INT
    INTERNAL -->|"MUST MATCH"| SRV_INT
```

**Authentication Variables** ([docker-compose.yml:109-110](), [docker-compose.yml:173-174]()):

| Variable | Services | Default | Description |
|----------|----------|---------|-------------|
| `JWT_SECRET` | aitoearn-ai, aitoearn-server | `change-this-jwt-secret` | JWT signing secret - **MUST MATCH** across services |
| `INTERNAL_TOKEN` | aitoearn-ai, aitoearn-server | `change-this-secret-token` | Bearer token for service-to-service calls - **MUST MATCH** |

**Critical:** Both `JWT_SECRET` and `INTERNAL_TOKEN` must have identical values in `aitoearn-ai` and `aitoearn-server` services. Mismatched values will cause authentication failures.

Generate secure random values:
```bash
openssl rand -hex 32  # For JWT_SECRET
openssl rand -hex 32  # For INTERNAL_TOKEN
```

**Sources:** [docker-compose.yml:109-110](), [docker-compose.yml:173-174](), [DOCKER_DEPLOYMENT_EN.md:142-151]()

### Application Domain Configuration

**Domain Variables** ([docker-compose.yml:155](), [docker-compose.yml:246]()):

| Variable | Service | Default | Description |
|----------|---------|---------|-------------|
| `APP_DOMAIN` | aitoearn-server | `localhost` | Public domain for OAuth callbacks |
| `NEXT_PUBLIC_API_URL` | aitoearn-web | `http://localhost:8080/api` | Browser-facing API URL |

`APP_DOMAIN` is used to construct OAuth callback URLs in the format:
```
https://{APP_DOMAIN}/api/plat/{platform}/auth/back
```

For production deployments, set `APP_DOMAIN` to your public domain (e.g., `aitoearn.example.com`) and `NEXT_PUBLIC_API_URL` to `https://aitoearn.example.com/api`.

**Sources:** [docker-compose.yml:155](), [docker-compose.yml:246](), [DOCKER_DEPLOYMENT_EN.md:269]()

## AI Service Configuration

AiToEarn integrates multiple AI providers for content generation, image creation, and video generation. All AI provider credentials are configured in the `aitoearn-ai` service, with some also duplicated in `aitoearn-server` for direct usage.

### AI Provider Environment Variables

```mermaid
graph TB
    subgraph "AI Provider Credentials"
        OPENAI["OPENAI_API_KEY<br/>OPENAI_BASE_URL"]
        ANTHROPIC["ANTHROPIC_API_KEY<br/>ANTHROPIC_BASE_URL"]
        GEMINI["GEMINI_KEY_PAIRS<br/>GEMINI_LOCATION"]
        GROK["GROK_API_KEY"]
        VOLC["VOLCENGINE_API_KEY<br/>VOLCENGINE_ACCESS_KEY_ID<br/>VOLCENGINE_SECRET_ACCESS_KEY<br/>VOLCENGINE_VOD_SPACE_NAME"]
        AICSO["AICSO_API_KEY<br/>AICSO_BASE_URL"]
        PROXY["AI_PROXY_URL"]
    end
    
    subgraph "aitoearn-ai service"
        AI_SVC["AI Service<br/>Orchestration Layer"]
    end
    
    subgraph "Model Definitions"
        AI_CFG["config/aitoearn-ai.config.js<br/>openai.models[]<br/>claude.models[]<br/>gemini.models[]<br/>etc."]
    end
    
    OPENAI --> AI_SVC
    ANTHROPIC --> AI_SVC
    GEMINI --> AI_SVC
    GROK --> AI_SVC
    VOLC --> AI_SVC
    AICSO --> AI_SVC
    PROXY --> AI_SVC
    AI_CFG --> AI_SVC
```

**Primary AI Providers** ([docker-compose.yml:114-128]()):

| Variable | Service | Default | Description |
|----------|---------|---------|-------------|
| `OPENAI_API_KEY` | aitoearn-ai, aitoearn-server | `sk-placeholder` | OpenAI API key or relay service key |
| `OPENAI_BASE_URL` | aitoearn-ai, aitoearn-server | `https://api.openai.com/v1` | OpenAI API endpoint or relay service URL |
| `ANTHROPIC_API_KEY` | aitoearn-ai | `sk-placeholder` | Anthropic (Claude) API key |
| `ANTHROPIC_BASE_URL` | aitoearn-ai | `https://api.anthropic.com` | Anthropic API endpoint |
| `GROK_API_KEY` | aitoearn-ai | `""` | xAI Grok API key |
| `AICSO_API_KEY` | aitoearn-ai | `""` | AICSO service API key |
| `AICSO_BASE_URL` | aitoearn-ai | `""` | AICSO service endpoint |
| `AI_PROXY_URL` | aitoearn-ai | `""` | Optional proxy for AI API requests |

**Volcengine (Doubao) Configuration** ([docker-compose.yml:119-122]()):

| Variable | Service | Description |
|----------|---------|-------------|
| `VOLCENGINE_API_KEY` | aitoearn-ai | Volcengine API key |
| `VOLCENGINE_ACCESS_KEY_ID` | aitoearn-ai | Volcengine access key ID |
| `VOLCENGINE_SECRET_ACCESS_KEY` | aitoearn-ai | Volcengine secret access key |
| `VOLCENGINE_VOD_SPACE_NAME` | aitoearn-ai | Volcengine VOD space name for video storage |

**Google Gemini Configuration** ([docker-compose.yml:126-127]()):

| Variable | Service | Description |
|----------|---------|-------------|
| `GEMINI_KEY_PAIRS` | aitoearn-ai | JSON array of Gemini project configurations |
| `GEMINI_LOCATION` | aitoearn-ai | GCP region for Vertex AI (default: `us-central1`) |

`GEMINI_KEY_PAIRS` format:
```json
[{
  "projectId": "your-gcp-project-id",
  "apiKey": "your-gemini-api-key", 
  "keyFile": "/app/config/gcs-placeholder.json",
  "bucket": "your-gcs-bucket"
}]
```

The `keyFile` path references the mounted GCS credentials file at [docker-compose.yml:92]().

**Sources:** [docker-compose.yml:114-128](), [docker-compose.yml:180-181](), [DOCKER_DEPLOYMENT_EN.md:206-247]()

### Using AI Relay Services (Recommended)

Instead of configuring individual AI providers, you can use a relay service like [new-api](https://github.com/Calcium-Ion/new-api) or [one-api](https://github.com/songquanpeng/one-api) to manage all AI models through a single endpoint.

**Configuration for Relay Service:**

```yaml
# In both aitoearn-ai and aitoearn-server services
OPENAI_BASE_URL: https://your-relay-service.com/v1
OPENAI_API_KEY: sk-your-relay-service-key
```

With a relay service, all other AI provider variables can remain as placeholders, since the relay handles routing to different models.

**Sources:** [DOCKER_DEPLOYMENT_EN.md:206-220]()

## OAuth Platform Integration Configuration

AiToEarn supports OAuth authentication with 14+ social media platforms. All OAuth credentials are configured in the `aitoearn-server` service.

### OAuth Credential Variables

```mermaid
graph TB
    subgraph "OAuth Platforms"
        TT["TikTok<br/>TIKTOK_CLIENT_ID<br/>TIKTOK_CLIENT_SECRET"]
        YT["YouTube<br/>YOUTUBE_CLIENT_ID<br/>YOUTUBE_CLIENT_SECRET"]
        TW["Twitter/X<br/>TWITTER_CLIENT_ID<br/>TWITTER_CLIENT_SECRET"]
        FB["Facebook<br/>FACEBOOK_CLIENT_ID<br/>FACEBOOK_CLIENT_SECRET<br/>FACEBOOK_CONFIG_ID"]
        INST["Instagram<br/>INSTAGRAM_CLIENT_ID<br/>INSTAGRAM_CLIENT_SECRET"]
        THR["Threads<br/>THREADS_CLIENT_ID<br/>THREADS_CLIENT_SECRET"]
        LINK["LinkedIn<br/>LINKEDIN_CLIENT_ID<br/>LINKEDIN_CLIENT_SECRET"]
        PIN["Pinterest<br/>PINTEREST_CLIENT_ID<br/>PINTEREST_CLIENT_SECRET<br/>PINTEREST_TEST_AUTHORIZATION"]
        BILI["Bilibili<br/>BILIBILI_CLIENT_ID<br/>BILIBILI_CLIENT_SECRET"]
        KWAI["Kuaishou<br/>KWAI_CLIENT_ID<br/>KWAI_CLIENT_SECRET"]
        DY["Douyin<br/>DOYIN_CLIENT_ID<br/>DOYIN_CLIENT_SECRET"]
        WX["WeChat Platform<br/>WXPLAT_APP_ID<br/>WXPLAT_APP_SECRET<br/>WXPLAT_ENCODING_AES_KEY"]
        GOOG["Google<br/>GOOGLE_CLIENT_ID<br/>GOOGLE_CLIENT_SECRET"]
    end
    
    subgraph "aitoearn-server"
        OAUTH["OAuth Controllers<br/>/api/plat/{platform}/auth"]
    end
    
    subgraph "OAuth Callback"
        CALLBACK["Callback URL:<br/>https://{APP_DOMAIN}/api/plat/{platform}/auth/back"]
    end
    
    TT --> OAUTH
    YT --> OAUTH
    TW --> OAUTH
    FB --> OAUTH
    INST --> OAUTH
    THR --> OAUTH
    LINK --> OAUTH
    PIN --> OAUTH
    BILI --> OAUTH
    KWAI --> OAUTH
    DY --> OAUTH
    WX --> OAUTH
    GOOG --> OAUTH
    
    OAUTH --> CALLBACK
```

**OAuth Platform Variables** ([docker-compose.yml:183-212]()):

| Platform | Variables | Developer Portal |
|----------|-----------|------------------|
| **TikTok** | `TIKTOK_CLIENT_ID`<br/>`TIKTOK_CLIENT_SECRET` | https://developers.tiktok.com |
| **YouTube** | `YOUTUBE_CLIENT_ID`<br/>`YOUTUBE_CLIENT_SECRET` | https://console.cloud.google.com/apis/credentials |
| **Twitter/X** | `TWITTER_CLIENT_ID`<br/>`TWITTER_CLIENT_SECRET` | https://developer.x.com/en/portal |
| **Facebook** | `FACEBOOK_CLIENT_ID`<br/>`FACEBOOK_CLIENT_SECRET`<br/>`FACEBOOK_CONFIG_ID` | https://developers.facebook.com |
| **Instagram** | `INSTAGRAM_CLIENT_ID`<br/>`INSTAGRAM_CLIENT_SECRET` | https://developers.facebook.com |
| **Threads** | `THREADS_CLIENT_ID`<br/>`THREADS_CLIENT_SECRET` | https://developers.facebook.com |
| **LinkedIn** | `LINKEDIN_CLIENT_ID`<br/>`LINKEDIN_CLIENT_SECRET` | https://www.linkedin.com/developers |
| **Pinterest** | `PINTEREST_CLIENT_ID`<br/>`PINTEREST_CLIENT_SECRET`<br/>`PINTEREST_TEST_AUTHORIZATION` | https://developers.pinterest.com |
| **Bilibili** | `BILIBILI_CLIENT_ID`<br/>`BILIBILI_CLIENT_SECRET` | https://open.bilibili.com |
| **Kuaishou** | `KWAI_CLIENT_ID`<br/>`KWAI_CLIENT_SECRET` | https://open.kuaishou.com |
| **Douyin** | `DOYIN_CLIENT_ID`<br/>`DOYIN_CLIENT_SECRET` | https://open.douyin.com |
| **WeChat Platform** | `WXPLAT_APP_ID`<br/>`WXPLAT_APP_SECRET`<br/>`WXPLAT_ENCODING_AES_KEY` | https://mp.weixin.qq.com |
| **Google** | `GOOGLE_CLIENT_ID`<br/>`GOOGLE_CLIENT_SECRET` | https://console.cloud.google.com/apis/credentials |

All OAuth platforms use the callback URL pattern:
```
https://{APP_DOMAIN}/api/plat/{platform}/auth/back
```

Where `{platform}` is the platform identifier (e.g., `tiktok`, `youtube`, `twitter`, etc.).

**Critical:** When registering OAuth applications with each platform, you must configure the callback URL using your actual `APP_DOMAIN` value. For localhost testing, use `http://localhost:8080/api/plat/{platform}/auth/back`.

**Sources:** [docker-compose.yml:183-212](), [DOCKER_DEPLOYMENT_EN.md:250-272]()

## Additional Service Configuration

### Email Configuration (AWS SES)

**Email Variables** ([docker-compose.yml:176-177]()):

| Variable | Service | Description |
|----------|---------|-------------|
| `MAIL_USER` | aitoearn-server | AWS SES SMTP username |
| `MAIL_PASS` | aitoearn-server | AWS SES SMTP password |

Used for transactional emails (password resets, notifications, etc.). Obtain credentials from AWS Console → SES → SMTP Settings.

**Sources:** [docker-compose.yml:176-177](), [DOCKER_DEPLOYMENT_EN.md:275-281]()

### Aliyun SMS Configuration

**Aliyun SMS Variables** ([docker-compose.yml:214-218]()):

| Variable | Service | Description |
|----------|---------|-------------|
| `ALI_SMS_ACCESS_KEY_ID` | aitoearn-server | Aliyun access key ID |
| `ALI_SMS_ACCESS_KEY_SECRET` | aitoearn-server | Aliyun access key secret |
| `ALI_SMS_SIGN_NAME` | aitoearn-server | SMS signature name |
| `ALI_SMS_TEMPLATE_CODE` | aitoearn-server | SMS template code |

Used for SMS verification codes and notifications. Obtain credentials from https://dysms.console.aliyun.com.

**Sources:** [docker-compose.yml:214-218]()

### Aliyun Content Safety

**Content Safety Variables** ([docker-compose.yml:220-222]()):

| Variable | Service | Description |
|----------|---------|-------------|
| `ALI_GREEN_ACCESS_KEY_ID` | aitoearn-server | Aliyun Green access key ID |
| `ALI_GREEN_ACCESS_KEY_SECRET` | aitoearn-server | Aliyun Green access key secret |

Used for content moderation (text, image, video). Obtain credentials from https://yundun.console.aliyun.com.

**Sources:** [docker-compose.yml:220-222]()

### Internal API Service

**New API Variables** ([docker-compose.yml:224-226]()):

| Variable | Service | Description |
|----------|---------|-------------|
| `NEW_API_URL` | aitoearn-server | Internal API relay service URL |
| `NEW_API_TOKEN` | aitoearn-server | Internal API authentication token |

Optional configuration for internal API management/relay services.

**Sources:** [docker-compose.yml:224-226]()

## Inter-Service Communication Configuration

### Service URL Configuration

These variables define how services communicate within the Docker network.

```mermaid
graph LR
    subgraph "aitoearn-ai :3010"
        AI["AI Service"]
        AI_SERVER_URL["SERVER_URL<br/>http://aitoearn-server:3002"]
    end
    
    subgraph "aitoearn-server :3002"
        SRV["Server Service"]
        SRV_AI_URL["AI_URL<br/>http://aitoearn-ai:3010"]
    end
    
    AI -->|"SERVER_URL"| SRV
    SRV -->|"AI_URL"| AI
```

**Service Communication Variables:**

| Variable | Service | Default | Description |
|----------|---------|---------|-------------|
| `SERVER_URL` | aitoearn-ai | `http://aitoearn-server:3002` | URL for AI service to call Server service |
| `AI_URL` | aitoearn-server | `http://aitoearn-ai:3010` | URL for Server service to call AI service |

These use Docker internal network hostnames and typically do not need modification unless services are deployed separately.

**Sources:** [docker-compose.yml:112](), [docker-compose.yml:171]()

## Configuration File System

In addition to environment variables, AiToEarn uses JavaScript configuration files that are mounted as read-only volumes into containers. These files combine environment variables with hardcoded settings.

### Configuration File Mapping

```mermaid
graph TB
    subgraph "Host System config/"
        AI_CFG_HOST["aitoearn-ai.config.js"]
        SRV_CFG_HOST["aitoearn-server.config.js"]
        GCS_HOST["gcs-placeholder.json"]
    end
    
    subgraph "aitoearn-ai Container"
        AI_CFG_MOUNT["/app/config.js<br/>(read-only)"]
        GCS_MOUNT["/app/config/gcs-placeholder.json<br/>(read-only)"]
    end
    
    subgraph "aitoearn-server Container"
        SRV_CFG_MOUNT["/app/config.js<br/>(read-only)"]
    end
    
    AI_CFG_HOST -->|"bind mount"| AI_CFG_MOUNT
    GCS_HOST -->|"bind mount"| GCS_MOUNT
    SRV_CFG_HOST -->|"bind mount"| SRV_CFG_MOUNT
    
    AI_CFG_MOUNT -.-> AI_RUNTIME["Application reads<br/>process.env + config.js"]
    SRV_CFG_MOUNT -.-> SRV_RUNTIME["Application reads<br/>process.env + config.js"]
```

**Configuration File Volumes** ([docker-compose.yml:90-92](), [docker-compose.yml:147-148]()):

| Host Path | Container Path | Service | Description |
|-----------|----------------|---------|-------------|
| `./config/aitoearn-ai.config.js` | `/app/config.js` | aitoearn-ai | AI service configuration |
| `./config/gcs-placeholder.json` | `/app/config/gcs-placeholder.json` | aitoearn-ai | Google Cloud credentials |
| `./config/aitoearn-server.config.js` | `/app/config.js` | aitoearn-server | Server service configuration |

### Configuration File Contents

**aitoearn-ai.config.js** contains:
- Port and logging configuration
- Redis and MongoDB connection details (from `process.env`)
- AI model definitions (OpenAI models, Claude models, Gemini models, etc.)
- Assets storage configuration (RustFS/S3 credentials and endpoints)
- Authentication settings (JWT secret, internal token from `process.env`)

**aitoearn-server.config.js** contains:
- Port and logging configuration
- Database connections (MongoDB, Statistics DB from `process.env`)
- Assets storage configuration (must match aitoearn-ai.config.js)
- OAuth callback URL patterns (uses `process.env.APP_DOMAIN`)
- Email service configuration
- Aliyun service configuration

**Key Points:**
1. Config files **read** many values from `process.env` (defined in docker-compose.yml)
2. Config files **hardcode** some values (storage endpoints, model lists, pricing)
3. Changes to config files require container restart
4. Files are mounted read-only to prevent accidental modification

**Sources:** [docker-compose.yml:90-92](), [docker-compose.yml:147-148](), [DOCKER_DEPLOYMENT_EN.md:98-111]()

## Environment Variable Dependencies

Several environment variables have cross-service dependencies that must be maintained.

### Critical Matching Requirements

```mermaid
graph TB
    subgraph "Secrets That Must Match"
        JWT_SECRET["JWT_SECRET"]
        INTERNAL_TOKEN["INTERNAL_TOKEN"]
        MONGO_PASS["MongoDB Password"]
        REDIS_PASS["Redis Password"]
    end
    
    subgraph "aitoearn-ai"
        AI_JWT["JWT_SECRET"]
        AI_INT["INTERNAL_TOKEN"]
        AI_MONGO["MONGODB_PASSWORD"]
        AI_REDIS["REDIS_PASSWORD"]
    end
    
    subgraph "aitoearn-server"
        SRV_JWT["JWT_SECRET"]
        SRV_INT["INTERNAL_TOKEN"]
        SRV_MONGO["MONGODB_PASSWORD"]
        SRV_STATS["STATISTICS_DB_PASSWORD"]
        SRV_REDIS["REDIS_PASSWORD"]
    end
    
    subgraph "mongodb service"
        MONGO_ROOT["MONGO_INITDB_ROOT_PASSWORD"]
    end
    
    subgraph "redis service"
        REDIS_CMD["command:<br/>redis-server --requirepass PASSWORD"]
    end
    
    JWT_SECRET -->|"MUST MATCH"| AI_JWT
    JWT_SECRET -->|"MUST MATCH"| SRV_JWT
    INTERNAL_TOKEN -->|"MUST MATCH"| AI_INT
    INTERNAL_TOKEN -->|"MUST MATCH"| SRV_INT
    MONGO_PASS -->|"MUST MATCH"| MONGO_ROOT
    MONGO_PASS -->|"MUST MATCH"| AI_MONGO
    MONGO_PASS -->|"MUST MATCH"| SRV_MONGO
    MONGO_PASS -->|"usually same"| SRV_STATS
    REDIS_PASS -->|"MUST MATCH"| REDIS_CMD
    REDIS_PASS -->|"MUST MATCH"| AI_REDIS
    REDIS_PASS -->|"MUST MATCH"| SRV_REDIS
```

**Dependency Table:**

| Variable Group | Services | Match Requirement |
|----------------|----------|-------------------|
| **JWT_SECRET** | aitoearn-ai, aitoearn-server | Must be identical |
| **INTERNAL_TOKEN** | aitoearn-ai, aitoearn-server | Must be identical |
| **MongoDB Password** | mongodb, aitoearn-ai, aitoearn-server | Must match `MONGO_INITDB_ROOT_PASSWORD` |
| **Statistics DB Password** | aitoearn-server | Usually same as MongoDB password (can differ if using separate DB) |
| **Redis Password** | redis command, aitoearn-ai, aitoearn-server | Must match `--requirepass` value in redis command |
| **RustFS Credentials** | rustfs, rustfs-init, config files | Must match across service environment, init script, and both config.js files |

**Sources:** [docker-compose.yml:8](), [docker-compose.yml:27](), [docker-compose.yml:47-48](), [docker-compose.yml:102](), [docker-compose.yml:107](), [docker-compose.yml:109-110](), [docker-compose.yml:159](), [docker-compose.yml:165](), [docker-compose.yml:169](), [docker-compose.yml:173-174]()

## Security Best Practices

### Password and Secret Management

**Critical Actions for Production:**

1. **Change All Default Passwords** - Never use the default values in production:
   - `MONGO_INITDB_ROOT_PASSWORD`: Change from `password`
   - Redis `--requirepass`: Change from `password`
   - `JWT_SECRET`: Change from `change-this-jwt-secret`
   - `INTERNAL_TOKEN`: Change from `change-this-secret-token`
   - `RUSTFS_ACCESS_KEY` / `RUSTFS_SECRET_KEY`: Change from `rustfsadmin`

2. **Generate Secure Random Values:**
   ```bash
   # Generate 32-byte hex strings for secrets
   openssl rand -hex 32
   ```

3. **Synchronized Updates** - When changing a password/secret:
   - Identify all locations where it appears (use the dependency table)
   - Update all occurrences simultaneously
   - Restart all affected containers

4. **Secret Rotation** - To rotate secrets:
   - Update environment variable in docker-compose.yml
   - Run `docker compose up -d` to restart affected services
   - For config file changes, restart is also required

**Sources:** [DOCKER_DEPLOYMENT_EN.md:66-94](), [DOCKER_DEPLOYMENT_CN.md:66-94]()

### Environment Variable Validation

Before starting services, validate that:

1. All passwords match across services
2. `JWT_SECRET` and `INTERNAL_TOKEN` are identical in aitoearn-ai and aitoearn-server
3. `APP_DOMAIN` is set correctly for production
4. OAuth credentials are present for platforms you intend to use
5. At least one AI provider has valid credentials (or relay service is configured)

**Health Check Endpoints:**

After deployment, verify services are healthy:
- http://localhost:8080/_nhealth - Nginx health
- http://localhost:8080/api/health - Server health (if endpoint exists)

**Sources:** [docker-compose.yml:129-134](), [docker-compose.yml:227-232](), [docker-compose.yml:265-270]()

---

This document provides a complete reference for configuring AiToEarn's environment variables. For deployment procedures, see [Docker Deployment Guide](#7.1). For detailed storage setup, see [Storage and Database Setup](#7.3).

---

# Page: Storage and Database Setup

# Storage and Database Setup

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



This page provides a comprehensive guide to configuring and managing the three-tier data storage system used by AiToEarn: MongoDB for document storage, Redis for caching and job queuing, and S3-compatible object storage (RustFS) for media assets.

For general deployment instructions, see [Docker Deployment Guide](#7.1). For environment variable reference, see [Environment Configuration](#7.2).

## Storage Architecture Overview

AiToEarn employs a three-tier data persistence strategy to optimize for different data types and access patterns:

```mermaid
graph TB
    subgraph "Application Services"
        Server["aitoearn-server<br/>:3002"]
        AI["aitoearn-ai<br/>:3010"]
        Web["aitoearn-web<br/>:3000"]
    end
    
    subgraph "Data Tier"
        MongoDB["MongoDB<br/>aitoearn-mongodb<br/>:27017"]
        Redis["Redis<br/>aitoearn-redis<br/>:6379"]
        RustFS["RustFS<br/>aitoearn-rustfs<br/>:9000/:9001"]
    end
    
    subgraph "Persistent Volumes"
        MongoVol1["mongodb-data<br/>/data/db"]
        MongoVol2["mongodb-config<br/>/data/configdb"]
        RedisVol["redis-data<br/>/data"]
        RustFSVol["rustfs-data<br/>/data"]
    end
    
    Server -->|"User data<br/>OAuth tokens<br/>Content metadata"| MongoDB
    Server -->|"Sessions<br/>Rate limits<br/>Job queue"| Redis
    Server -->|"Images<br/>Videos<br/>Documents"| RustFS
    
    AI -->|"AI metadata"| MongoDB
    AI -->|"Cache"| Redis
    AI -->|"Generated assets"| RustFS
    
    MongoDB -.->|"Persists to"| MongoVol1
    MongoDB -.->|"Config persists to"| MongoVol2
    Redis -.->|"Persists to"| RedisVol
    RustFS -.->|"Persists to"| RustFSVol
```

**Sources:** [docker-compose.yml:1-286]()

| Storage System | Purpose | Data Types | Access Pattern |
|----------------|---------|------------|----------------|
| **MongoDB** | Primary database | User accounts, OAuth tokens, content metadata, drafts, analytics | Random access, ACID transactions |
| **Redis** | Cache & queue | Sessions, rate limiting, scheduled jobs, temporary data | High-speed read/write, TTL-based expiry |
| **RustFS/S3** | Object storage | Images, videos, documents, AI-generated media | Large file storage, CDN delivery |

**Sources:** [README.md:158-183](), [DOCKER_DEPLOYMENT_EN.md:6-36]()

## MongoDB Configuration

### Container Setup

MongoDB runs as the `aitoearn-mongodb` container using the official `mongo:latest` image.

```mermaid
graph LR
    subgraph "MongoDB Container"
        MongoProcess["mongod process"]
    end
    
    subgraph "Host System"
        Port27017["Port 27017"]
        VolData["mongodb-data volume"]
        VolConfig["mongodb-config volume"]
    end
    
    subgraph "Application Containers"
        ServerConn["aitoearn-server<br/>MONGODB_HOST=mongodb"]
        AIConn["aitoearn-ai<br/>MONGODB_HOST=mongodb"]
    end
    
    Port27017 -->|"Mapped to"| MongoProcess
    MongoProcess -.->|"/data/db"| VolData
    MongoProcess -.->|"/data/configdb"| VolConfig
    ServerConn -->|"mongodb://admin:password@mongodb:27017"| MongoProcess
    AIConn -->|"mongodb://admin:password@mongodb:27017"| MongoProcess
```

**Sources:** [docker-compose.yml:2-21]()

### Database Configuration

**Default Credentials** (must be changed for production):
- Username: `admin` (set via `MONGO_INITDB_ROOT_USERNAME`)
- Password: `password` (set via `MONGO_INITDB_ROOT_PASSWORD`)

**Connection Configuration:**

The following environment variables must be synchronized across all services that connect to MongoDB:

```yaml
# In docker-compose.yml mongodb service
MONGO_INITDB_ROOT_USERNAME: admin
MONGO_INITDB_ROOT_PASSWORD: your-secure-password

# In aitoearn-server service
MONGODB_HOST: mongodb
MONGODB_PORT: 27017
MONGODB_USERNAME: admin
MONGODB_PASSWORD: your-secure-password

# In aitoearn-ai service
MONGODB_HOST: mongodb
MONGODB_PORT: 27017
MONGODB_USERNAME: admin
MONGODB_PASSWORD: your-secure-password
```

**Sources:** [docker-compose.yml:6-8](), [docker-compose.yml:100-103](), [docker-compose.yml:157-160]()

### Database Names

| Database | Service | Purpose |
|----------|---------|---------|
| `aitoearn` | aitoearn-server, aitoearn-ai | Primary application database |
| Statistics DB | aitoearn-server | Analytics and metrics (defaults to same MongoDB instance) |

The statistics database connection is configured separately to allow for future separation:

```yaml
# In aitoearn-server service
STATISTICS_DB_HOST: mongodb
STATISTICS_DB_PORT: 27017
STATISTICS_DB_USERNAME: admin
STATISTICS_DB_PASSWORD: password
```

**Sources:** [docker-compose.yml:162-165]()

### Health Check

MongoDB includes a health check that verifies the database is responsive:

```yaml
healthcheck:
  test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 40s
```

This health check is used by dependent services (`aitoearn-server` and `aitoearn-ai`) to ensure MongoDB is ready before they start.

**Sources:** [docker-compose.yml:16-21]()

### Volume Management

MongoDB uses two persistent volumes:

| Volume Name | Mount Point | Purpose | Typical Size |
|-------------|-------------|---------|--------------|
| `mongodb-data` | `/data/db` | Database files, indexes | 10GB+ (grows with data) |
| `mongodb-config` | `/data/configdb` | MongoDB configuration | <100MB |

**Volume Declaration:**
```yaml
volumes:
  mongodb-data:
    driver: local
  mongodb-config:
    driver: local
```

**Sources:** [docker-compose.yml:12-13](), [docker-compose.yml:278-281]()

### Backup and Restore

**Manual Backup:**

```bash
# Backup to host filesystem
docker exec aitoearn-mongodb mongodump \
  --username admin \
  --password your-password \
  --authenticationDatabase admin \
  --out /data/backup

# Copy backup from container to host
docker cp aitoearn-mongodb:/data/backup ./mongodb-backup-$(date +%Y%m%d)
```

**Restore from Backup:**

```bash
# Copy backup to container
docker cp ./mongodb-backup-20250101 aitoearn-mongodb:/data/restore

# Restore
docker exec aitoearn-mongodb mongorestore \
  --username admin \
  --password your-password \
  --authenticationDatabase admin \
  /data/restore
```

**Automated Backup Strategy:**

For production, configure automated backups using MongoDB tools or external backup solutions:
- Schedule daily `mongodump` via cron
- Use MongoDB Atlas for managed backups
- Implement point-in-time recovery with replica sets and oplog

**Sources:** [DOCKER_DEPLOYMENT_EN.md:173-232]()

## Redis Configuration

### Container Setup

Redis runs as the `aitoearn-redis` container using the official `redis:latest` image with password authentication enabled.

```mermaid
graph LR
    subgraph "Redis Container"
        RedisProcess["redis-server<br/>--requirepass password"]
    end
    
    subgraph "Host System"
        Port6379["Port 6379"]
        VolData["redis-data volume"]
    end
    
    subgraph "Application Containers"
        ServerConn["aitoearn-server<br/>REDIS_HOST=redis<br/>REDIS_PASSWORD=password"]
        AIConn["aitoearn-ai<br/>REDIS_HOST=redis<br/>REDIS_PASSWORD=password"]
    end
    
    Port6379 -->|"Mapped to"| RedisProcess
    RedisProcess -.->|"/data"| VolData
    ServerConn -->|"redis://:password@redis:6379"| RedisProcess
    AIConn -->|"redis://:password@redis:6379"| RedisProcess
```

**Sources:** [docker-compose.yml:23-39]()

### Redis Configuration

**Authentication:**
```yaml
# In docker-compose.yml redis service
command: redis-server --requirepass your-secure-password

# In application services
REDIS_HOST: redis
REDIS_PORT: 6379
REDIS_PASSWORD: your-secure-password
```

**Sources:** [docker-compose.yml:27](), [docker-compose.yml:105-107](), [docker-compose.yml:168-170]()

### Redis Usage Patterns

Redis is used for multiple purposes across the application:

| Use Case | Service | Key Pattern | TTL |
|----------|---------|-------------|-----|
| User sessions | aitoearn-server | `session:*` | 7 days (default) |
| Rate limiting | aitoearn-server | `ratelimit:*` | 1 hour (typical) |
| Job queue | aitoearn-server | `bull:*` | Until processed |
| AI response cache | aitoearn-ai | `ai:cache:*` | Variable |
| Distributed locks | aitoearn-ai, aitoearn-server | `redlock:*` | Short-lived |

**Sources:** [DOCKER_DEPLOYMENT_EN.md:306-309]()

### Health Check

Redis includes a health check using `redis-cli`:

```yaml
healthcheck:
  test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
  interval: 10s
  timeout: 3s
  retries: 5
  start_period: 30s
```

**Sources:** [docker-compose.yml:34-39]()

### Volume Management

Redis uses a single persistent volume for data:

```yaml
volumes:
  - redis-data:/data

# Volume declaration
volumes:
  redis-data:
    driver: local
```

**Data Persistence:** Redis is configured to persist data using RDB snapshots and AOF (Append-Only File) depending on the Redis configuration. The default `redis:latest` image enables RDB snapshots.

**Sources:** [docker-compose.yml:31](), [docker-compose.yml:283]()

### Backup and Restore

**Manual Backup:**

```bash
# Trigger a background save
docker exec aitoearn-redis redis-cli -a your-password BGSAVE

# Wait for save to complete
docker exec aitoearn-redis redis-cli -a your-password LASTSAVE

# Copy the RDB file
docker cp aitoearn-redis:/data/dump.rdb ./redis-backup-$(date +%Y%m%d).rdb
```

**Restore from Backup:**

```bash
# Stop Redis
docker compose stop redis

# Replace the RDB file
docker cp ./redis-backup-20250101.rdb aitoearn-redis:/data/dump.rdb

# Start Redis
docker compose start redis
```

**Sources:** [DOCKER_DEPLOYMENT_EN.md:173-232]()

## Object Storage Configuration (RustFS)

### RustFS Architecture

RustFS is an S3-compatible object storage system included in the Docker Compose setup. It provides out-of-the-box storage for images, videos, and other media files.

```mermaid
graph TB
    subgraph "RustFS Container"
        RustFSAPI["RustFS API<br/>:9000"]
        RustFSConsole["RustFS Console<br/>:9001"]
    end
    
    subgraph "Initialization"
        RustFSInit["rustfs-init<br/>(minio/mc)"]
    end
    
    subgraph "Host System"
        VolData["rustfs-data volume<br/>/data"]
        Port9000["Port 9000 (API)"]
        Port9001["Port 9001 (Console)"]
    end
    
    subgraph "Application Services"
        ServerUpload["aitoearn-server<br/>uploads media"]
        AIUpload["aitoearn-ai<br/>uploads AI-generated assets"]
    end
    
    RustFSInit -->|"1. mc alias set rustfs<br/>2. mc mb rustfs/aitoearn<br/>3. mc anonymous set download"| RustFSAPI
    Port9000 -->|"Mapped to"| RustFSAPI
    Port9001 -->|"Mapped to"| RustFSConsole
    RustFSAPI -.->|"Persists to"| VolData
    ServerUpload -->|"S3 API calls<br/>http://rustfs.local:9000"| RustFSAPI
    AIUpload -->|"S3 API calls<br/>http://rustfs.local:9000"| RustFSAPI
```

**Sources:** [docker-compose.yml:41-79]()

### RustFS Service Configuration

**Container Definition:**
```yaml
rustfs:
  image: rustfs/rustfs:latest
  container_name: aitoearn-rustfs
  hostname: rustfs.local
  environment:
    RUSTFS_ACCESS_KEY: rustfsadmin
    RUSTFS_SECRET_KEY: rustfsadmin
  ports:
    - "9000:9000"  # API
    - "9001:9001"  # Console
  volumes:
    - rustfs-data:/data
```

**Sources:** [docker-compose.yml:41-63]()

### Bucket Initialization

The `rustfs-init` container automatically creates and configures the `aitoearn` bucket on first startup:

```yaml
rustfs-init:
  image: minio/mc:latest
  entrypoint: >
    /bin/sh -c "
    mc alias set rustfs http://rustfs.local:9000 rustfsadmin rustfsadmin;
    mc mb rustfs/aitoearn --ignore-existing;
    mc anonymous set download rustfs/aitoearn;
    exit 0;
    "
```

This initialization:
1. Configures the MinIO client (`mc`) to connect to RustFS
2. Creates the `aitoearn` bucket (if it doesn't exist)
3. Sets the bucket to allow anonymous download access

**Sources:** [docker-compose.yml:65-79]()

### Application Configuration

Both `aitoearn-server` and `aitoearn-ai` must be configured to use RustFS. This configuration is stored in the config files, not environment variables:

**In `config/aitoearn-ai.config.js` and `config/aitoearn-server.config.js`:**

```javascript
assets: {
  provider: 's3',
  region: 'us-east-1',
  bucketName: 'aitoearn',
  endpoint: 'http://rustfs.local:9000',
  accessKeyId: 'rustfsadmin',
  secretAccessKey: 'rustfsadmin',
  cdnEndpoint: '',
  forcePathStyle: true,
}
```

**Sources:** [DOCKER_DEPLOYMENT_EN.md:173-202]()

### Accessing the RustFS Console

The RustFS console provides a web UI for managing buckets and objects:

- **URL:** http://localhost:9001
- **Username:** `rustfsadmin`
- **Password:** `rustfsadmin`

**Sources:** [docker-compose.yml:50-51](), [DOCKER_DEPLOYMENT_CN.md:176-181]()

### Changing RustFS Credentials

To change RustFS credentials, update **all three locations**:

1. **RustFS service environment variables:**
```yaml
# docker-compose.yml
rustfs:
  environment:
    RUSTFS_ACCESS_KEY: new-access-key
    RUSTFS_SECRET_KEY: new-secret-key
```

2. **Initialization script:**
```yaml
# docker-compose.yml
rustfs-init:
  entrypoint: >
    /bin/sh -c "
    mc alias set rustfs http://rustfs.local:9000 new-access-key new-secret-key;
    ...
```

3. **Application config files:**
```javascript
// config/aitoearn-ai.config.js and config/aitoearn-server.config.js
assets: {
  accessKeyId: 'new-access-key',
  secretAccessKey: 'new-secret-key',
  ...
}
```

**Sources:** [DOCKER_DEPLOYMENT_CN.md:183-187]()

### Switching to External S3/OSS

For production deployments, you may want to use AWS S3, Aliyun OSS, or other cloud storage providers instead of RustFS.

**Configuration Example (AWS S3):**

```javascript
// In config/aitoearn-ai.config.js and config/aitoearn-server.config.js
assets: {
  provider: 's3',
  region: 'ap-southeast-1',
  bucketName: 'your-bucket-name',
  endpoint: 'https://s3.ap-southeast-1.amazonaws.com',
  accessKeyId: 'AWS_ACCESS_KEY_ID',
  secretAccessKey: 'AWS_SECRET_ACCESS_KEY',
  cdnEndpoint: 'https://your-cloudfront-domain.com',
  forcePathStyle: false,
}
```

**Configuration Example (Aliyun OSS):**

```javascript
assets: {
  provider: 's3',
  region: 'oss-cn-hangzhou',
  bucketName: 'your-bucket-name',
  endpoint: 'https://oss-cn-hangzhou.aliyuncs.com',
  accessKeyId: 'ALIYUN_ACCESS_KEY_ID',
  secretAccessKey: 'ALIYUN_ACCESS_KEY_SECRET',
  cdnEndpoint: 'https://your-cdn-domain.com',
  forcePathStyle: false,
}
```

When using external storage, you can remove or comment out the `rustfs` and `rustfs-init` services from `docker-compose.yml`.

**Sources:** [DOCKER_DEPLOYMENT_CN.md:189-201]()

### Volume Management

RustFS uses a single volume for all stored objects:

```yaml
volumes:
  - rustfs-data:/data

# Volume declaration
volumes:
  rustfs-data:
    driver: local
```

**Sources:** [docker-compose.yml:53](), [docker-compose.yml:284-285]()

### Backup and Restore

**Using MinIO Client (mc):**

```bash
# Install mc client
docker run --rm -it --entrypoint=/bin/sh minio/mc

# Configure alias
docker exec aitoearn-rustfs mc alias set local http://localhost:9000 rustfsadmin rustfsadmin

# Mirror bucket to local directory
docker exec aitoearn-rustfs mc mirror local/aitoearn /backup/aitoearn

# Restore from backup
docker exec aitoearn-rustfs mc mirror /backup/aitoearn local/aitoearn
```

**Using Docker Volume Backup:**

```bash
# Backup entire volume
docker run --rm \
  -v aitoearn_rustfs-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/rustfs-backup-$(date +%Y%m%d).tar.gz -C /data .

# Restore volume
docker run --rm \
  -v aitoearn_rustfs-data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/rustfs-backup-20250101.tar.gz -C /data
```

**Sources:** [DOCKER_DEPLOYMENT_EN.md:173-232]()

## Volume Management and Persistence

### Docker Volume Overview

All persistent data in AiToEarn is stored in named Docker volumes, which survive container recreation and updates.

```mermaid
graph TB
    subgraph "Docker Volumes"
        MongoDataVol["mongodb-data<br/>(driver: local)"]
        MongoConfigVol["mongodb-config<br/>(driver: local)"]
        RedisDataVol["redis-data<br/>(driver: local)"]
        RustFSDataVol["rustfs-data<br/>(driver: local)"]
    end
    
    subgraph "Host Filesystem"
        VolumePath["/var/lib/docker/volumes/"]
    end
    
    subgraph "Container Mounts"
        MongoDB["/data/db<br/>/data/configdb"]
        Redis["/data"]
        RustFS["/data"]
    end
    
    VolumePath -.->|"Managed by Docker"| MongoDataVol
    VolumePath -.->|"Managed by Docker"| MongoConfigVol
    VolumePath -.->|"Managed by Docker"| RedisDataVol
    VolumePath -.->|"Managed by Docker"| RustFSDataVol
    
    MongoDataVol -->|"Mounted to"| MongoDB
    MongoConfigVol -->|"Mounted to"| MongoDB
    RedisDataVol -->|"Mounted to"| Redis
    RustFSDataVol -->|"Mounted to"| RustFS
```

**Sources:** [docker-compose.yml:277-285]()

### Volume Declaration

All volumes are declared at the bottom of `docker-compose.yml`:

```yaml
volumes:
  mongodb-data:
    driver: local
  mongodb-config:
    driver: local
  redis-data:
    driver: local
  rustfs-data:
    driver: local
```

**Sources:** [docker-compose.yml:277-285]()

### Volume Inspection

**List volumes:**
```bash
docker volume ls | grep aitoearn
```

**Inspect a volume:**
```bash
docker volume inspect aitoearn_mongodb-data
```

**Check volume size:**
```bash
docker system df -v
```

**Sources:** [docker-compose.yml:277-285]()

### Volume Backup Strategy

**Complete System Backup:**

```bash
#!/bin/bash
BACKUP_DIR="./backups/$(date +%Y%m%d-%H%M%S)"
mkdir -p $BACKUP_DIR

# Stop services (optional, for consistency)
docker compose stop

# Backup all volumes
for vol in mongodb-data mongodb-config redis-data rustfs-data; do
  docker run --rm \
    -v aitoearn_${vol}:/data \
    -v $(pwd)/$BACKUP_DIR:/backup \
    alpine tar czf /backup/${vol}.tar.gz -C /data .
done

# Restart services
docker compose start
```

**Restore from Backup:**

```bash
#!/bin/bash
BACKUP_DIR="./backups/20250101-120000"

# Stop services
docker compose down

# Restore all volumes
for vol in mongodb-data mongodb-config redis-data rustfs-data; do
  docker run --rm \
    -v aitoearn_${vol}:/data \
    -v $(pwd)/$BACKUP_DIR:/backup \
    alpine tar xzf /backup/${vol}.tar.gz -C /data
done

# Start services
docker compose up -d
```

**Sources:** [DOCKER_DEPLOYMENT_EN.md:173-232]()

### Volume Migration

**Moving volumes to a new host:**

```bash
# On source host
docker compose down
docker run --rm \
  -v aitoearn_mongodb-data:/data \
  alpine tar czf - -C /data . > mongodb-data.tar.gz

# Transfer file to destination host (scp, rsync, etc.)

# On destination host
docker volume create aitoearn_mongodb-data
docker run --rm \
  -v aitoearn_mongodb-data:/data \
  alpine tar xzf - -C /data < mongodb-data.tar.gz
```

Repeat for all volumes, then deploy the application on the new host.

**Sources:** [docker-compose.yml:277-285]()

## Scaling Considerations

### MongoDB Scaling

**Vertical Scaling:**
- Increase container resource limits in `docker-compose.yml`
- Add more storage to the host system
- Optimize MongoDB indexes and queries

**Horizontal Scaling (Replica Sets):**

For production high-availability, deploy MongoDB as a replica set:

```yaml
mongodb-primary:
  image: mongo:latest
  command: mongod --replSet rs0
  
mongodb-secondary1:
  image: mongo:latest
  command: mongod --replSet rs0
  
mongodb-secondary2:
  image: mongo:latest
  command: mongod --replSet rs0
```

Then initialize the replica set inside a container:

```javascript
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "mongodb-primary:27017" },
    { _id: 1, host: "mongodb-secondary1:27017" },
    { _id: 2, host: "mongodb-secondary2:27017" }
  ]
})
```

**Sources:** [docker-compose.yml:2-21]()

### Redis Scaling

**Vertical Scaling:**
- Increase memory allocation
- Enable RDB/AOF optimization
- Use Redis Cluster for horizontal scaling

**Redis Sentinel (High Availability):**

```yaml
redis-master:
  image: redis:latest
  command: redis-server --requirepass password
  
redis-replica:
  image: redis:latest
  command: redis-server --requirepass password --slaveof redis-master 6379
  
redis-sentinel:
  image: redis:latest
  command: redis-sentinel /etc/sentinel.conf
```

**Sources:** [docker-compose.yml:23-39]()

### Object Storage Scaling

**RustFS Limitations:**
- Single-node deployment
- Not recommended for high-traffic production

**Production Alternatives:**
- **AWS S3:** Unlimited scalability, global CDN integration
- **Aliyun OSS:** China-optimized, competitive pricing
- **MinIO Cluster:** Self-hosted S3-compatible with distributed mode
- **Google Cloud Storage:** Integrated with Gemini AI services

**Migration Path:**
1. Deploy external S3/OSS bucket
2. Update config files with new credentials
3. Migrate existing assets using `mc mirror` or `aws s3 sync`
4. Update application configuration
5. Remove RustFS services from `docker-compose.yml`

**Sources:** [DOCKER_DEPLOYMENT_CN.md:189-201]()

## Production Best Practices

### Security

**Database Security:**
- Change all default passwords immediately
- Use strong, randomly generated passwords (`openssl rand -hex 32`)
- Enable MongoDB authentication and authorization
- Restrict MongoDB/Redis ports to internal network only
- Use TLS/SSL for database connections in production

**Object Storage Security:**
- Use IAM roles instead of access keys when possible
- Implement bucket policies to restrict access
- Enable versioning for important buckets
- Configure CORS policies appropriately
- Use CDN with signed URLs for private content

**Sources:** [DOCKER_DEPLOYMENT_CN.md:62-95]()

### Monitoring

**Health Checks:**
All storage services include health checks that can be monitored:

```bash
# Check service health
docker compose ps

# View health check logs
docker inspect --format='{{json .State.Health}}' aitoearn-mongodb | jq
```

**Metrics Collection:**
- MongoDB: Use MongoDB Cloud Manager or Prometheus exporter
- Redis: Use redis_exporter for Prometheus
- RustFS/S3: Monitor via CloudWatch (AWS) or provider dashboards

**Sources:** [docker-compose.yml:16-21](), [docker-compose.yml:34-39](), [docker-compose.yml:58-63]()

### Backup Automation

**Automated Backup Schedule:**

```bash
# Add to crontab
# Daily backup at 2 AM
0 2 * * * /path/to/aitoearn/scripts/backup-all.sh

# Weekly full backup (Sunday 3 AM)
0 3 * * 0 /path/to/aitoearn/scripts/backup-full.sh

# Cleanup old backups (keep 30 days)
0 4 * * * find /backups -type f -mtime +30 -delete
```

**Backup Verification:**
- Regularly test restore procedures
- Verify backup integrity with checksums
- Monitor backup sizes for anomalies
- Maintain off-site backup copies

**Sources:** [DOCKER_DEPLOYMENT_EN.md:173-232]()

### Performance Tuning

**MongoDB:**
- Create indexes for frequently queried fields
- Use projection to limit returned fields
- Enable connection pooling
- Monitor slow queries with profiling
- Consider read replicas for analytics

**Redis:**
- Configure maxmemory policy (e.g., `allkeys-lru`)
- Use pipelining for batch operations
- Monitor memory usage and eviction stats
- Consider Redis Cluster for large datasets

**Object Storage:**
- Enable CDN caching for static assets
- Use multipart uploads for large files
- Implement client-side compression
- Optimize image/video formats before upload
- Use lifecycle policies to archive old data

**Sources:** [docker-compose.yml:1-286]()

## Troubleshooting

### Common Issues

**MongoDB connection refused:**
```bash
# Check if MongoDB is running
docker compose ps mongodb

# Check MongoDB logs
docker compose logs mongodb

# Verify health check
docker inspect --format='{{.State.Health.Status}}' aitoearn-mongodb

# Test connection manually
docker exec -it aitoearn-mongodb mongosh -u admin -p password
```

**Redis authentication failure:**
```bash
# Verify Redis password is consistent
grep REDIS_PASSWORD docker-compose.yml

# Test Redis connection
docker exec -it aitoearn-redis redis-cli -a password ping
```

**RustFS bucket not found:**
```bash
# Check if initialization completed
docker compose logs rustfs-init

# Manually create bucket
docker exec aitoearn-rustfs mc mb rustfs/aitoearn
```

**Volume data loss after restart:**
```bash
# Verify volume exists
docker volume ls | grep aitoearn

# Check volume mount points
docker inspect aitoearn-mongodb | grep -A 10 Mounts
```

**Sources:** [docker-compose.yml:1-286](), [DOCKER_DEPLOYMENT_EN.md:1-445]()

### Recovery Procedures

**Corrupted MongoDB data:**
```bash
# Stop the service
docker compose stop mongodb

# Repair database
docker run --rm \
  -v aitoearn_mongodb-data:/data/db \
  mongo:latest mongod --repair

# Restart service
docker compose start mongodb
```

**Redis persistence failure:**
```bash
# Check Redis logs
docker compose logs redis | grep -i error

# Force a background save
docker exec aitoearn-redis redis-cli -a password BGSAVE

# If AOF is corrupted, rebuild
docker exec aitoearn-redis redis-cli -a password BGREWRITEAOF
```

**Sources:** [docker-compose.yml:1-286]()

---

# Page: Development Guide

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

# Page: Development Mode Setup

# Development Mode Setup

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



This page describes how to run AiToEarn services in **development mode without Docker**. This setup is intended for local development and debugging, enabling hot-reload capabilities for rapid iteration on code changes.

For production deployment using Docker, see [Docker Deployment Guide](#7.1). For project structure and conventions, see [Project Structure and Conventions](#8.2).

---

## Overview

Development mode runs each service as a separate Node.js process with hot-reload enabled. You have two options for infrastructure dependencies (MongoDB and Redis):

1. **Use Docker for infrastructure only** (recommended) - Run MongoDB/Redis in Docker while running application services locally
2. **Self-managed infrastructure** - Install and run MongoDB/Redis directly on your machine

This allows developers to modify code and see changes immediately without rebuilding Docker images.

**Sources:** [README.md:193-216](), [README_CN.md:178-201]()

---

## Development Architecture

```mermaid
graph TB
    subgraph "Local Development Environment"
        subgraph "Application Services (Node.js processes)"
            Web["aitoearn-web<br/>Next.js Dev Server<br/>Port: 3000<br/>pnpm run dev"]
            Server["aitoearn-server<br/>NestJS Service<br/>Port: 3002<br/>npx nx serve aitoearn-server"]
            AI["aitoearn-ai<br/>NestJS Service<br/>Port: 3010<br/>npx nx serve aitoearn-ai"]
        end
        
        subgraph "Infrastructure (Docker or Local)"
            MongoDB["MongoDB<br/>Port: 27017"]
            Redis["Redis<br/>Port: 6379"]
            RustFS["RustFS (Optional)<br/>Ports: 9000/9001"]
        end
        
        Dev["Developer Browser<br/>http://localhost:3000"]
    end
    
    Dev -->|"HTTP"| Web
    Web -->|"API Calls"| Server
    Server -->|"AI Requests"| AI
    Server --> MongoDB
    Server --> Redis
    AI --> MongoDB
    AI --> Redis
    Server -.->|"Object Storage"| RustFS
    AI -.->|"Object Storage"| RustFS
```

**Development Mode Service Communication**

In development mode, services communicate via localhost ports instead of Docker internal networking:
- Frontend → Backend: `http://localhost:3002` (or configured API URL)
- Backend → AI: `http://localhost:3010`
- All services → MongoDB: `localhost:27017`
- All services → Redis: `localhost:6379`

**Sources:** [README.md:193-216](), [docker-compose.yml:1-286]()

---

## Prerequisites

### Required Software

| Tool | Minimum Version | Purpose | Installation |
|------|----------------|---------|--------------|
| **Node.js** | 20.18.x | JavaScript runtime | https://nodejs.org |
| **pnpm** | Latest | Package manager | `npm install -g pnpm` |
| **Docker** (optional) | 20.10+ | For MongoDB/Redis | https://docker.com |

Verify installation:

```bash
node --version   # Should show v20.18.x
pnpm --version   # Should show 8.x or higher
docker --version # (if using Docker for infrastructure)
```

**Sources:** [README.md:8]()

---

## Infrastructure Setup

You need MongoDB and Redis running before starting application services.

### Option 1: Use Docker for Infrastructure (Recommended)

Start only the infrastructure services from the provided `docker-compose.yml`:

```bash
# Start MongoDB and Redis only
docker compose up -d mongodb redis

# Optionally start RustFS for object storage
docker compose up -d rustfs rustfs-init
```

Verify services are running:

```bash
docker compose ps
# Should show mongodb, redis (and optionally rustfs) as "healthy"
```

**Connection details:**
- MongoDB: `mongodb://admin:password@localhost:27017` (default credentials from [docker-compose.yml:6-8]())
- Redis: `localhost:6379` with password `password` (from [docker-compose.yml:27]())
- RustFS: `http://localhost:9000` (if started)

### Option 2: Self-Managed Infrastructure

Install and run MongoDB and Redis directly on your machine:

**MongoDB:**
```bash
# macOS with Homebrew
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community

# Ubuntu/Debian
sudo apt-get install mongodb
sudo systemctl start mongodb
```

**Redis:**
```bash
# macOS with Homebrew
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server
```

**Sources:** [docker-compose.yml:2-39](), [DOCKER_DEPLOYMENT_EN.md:38-50]()

---

## Backend Services Setup

The backend is a monorepo managed by Nx, located in the `project/aitoearn-backend` directory.

### Repository Structure

```
project/aitoearn-backend/
├── apps/
│   ├── aitoearn-ai/          # AI service application
│   └── aitoearn-server/      # Main backend application
├── libs/                      # Shared libraries
├── nx.json                    # Nx workspace configuration
├── package.json               # Dependencies
└── tsconfig.base.json         # TypeScript configuration
```

### Installing Dependencies

Navigate to the backend directory and install dependencies:

```bash
cd project/aitoearn-backend
pnpm install
```

This installs all dependencies for both `aitoearn-ai` and `aitoearn-server` services.

**Sources:** [README.md:202-206]()

### Environment Configuration

Before running services, you need to configure environment variables. Copy or create configuration files:

```bash
# Create config.js for aitoearn-ai
cp config/aitoearn-ai.config.js project/aitoearn-backend/apps/aitoearn-ai/config.js

# Create config.js for aitoearn-server
cp config/aitoearn-server.config.js project/aitoearn-backend/apps/aitoearn-server/config.js
```

**Critical environment variables to configure:**

For both services, ensure these environment variables are set (either via shell exports or `.env` files):

```bash
# Database connections
export MONGODB_HOST=localhost
export MONGODB_PORT=27017
export MONGODB_USERNAME=admin
export MONGODB_PASSWORD=password

# Redis connection
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_PASSWORD=password

# Authentication secrets
export JWT_SECRET=your-dev-jwt-secret
export INTERNAL_TOKEN=your-dev-internal-token

# AI Service URL (for aitoearn-server)
export AI_URL=http://localhost:3010

# Server URL (for aitoearn-ai)
export SERVER_URL=http://localhost:3002
```

**Sources:** [docker-compose.yml:95-134](), [docker-compose.yml:151-232](), [DOCKER_DEPLOYMENT_EN.md:139-173]()

---

## Running Backend Services

### Starting aitoearn-ai

The AI service handles all AI model integrations and must be started before `aitoearn-server`.

```bash
# From project/aitoearn-backend directory
npx nx serve aitoearn-ai
```

The service will start on **port 3010** by default. You should see output indicating:
- Configuration loaded from `config.js`
- Connected to MongoDB
- Connected to Redis
- HTTP server listening on port 3010

**Hot Reload:** Nx automatically watches for file changes in `apps/aitoearn-ai/` and rebuilds/restarts the service.

### Starting aitoearn-server

The main backend service provides the primary API. Start it in a **separate terminal**:

```bash
# From project/aitoearn-backend directory (new terminal)
npx nx serve aitoearn-server
```

The service will start on **port 3002** by default. Verify it connects to:
- MongoDB
- Redis
- aitoearn-ai service at `http://localhost:3010`

**Sources:** [README.md:202-207]()

---

## Frontend Setup

The frontend is a Next.js application located in the `aitoearn_web` directory.

### Installing Dependencies

```bash
# From project root
cd aitoearn_web
pnpm install
```

### Environment Configuration

Create or update the `.env.local` file:

```bash
# aitoearn_web/.env.local
NEXT_PUBLIC_API_URL=http://localhost:3002
NODE_ENV=development
```

The `NEXT_PUBLIC_API_URL` variable tells the frontend where to find the backend API. In development mode, this points directly to `aitoearn-server` on port 3002 (no Nginx proxy).

### Starting the Development Server

```bash
# From aitoearn_web directory
pnpm run dev
```

The Next.js development server starts on **port 3000** with:
- Hot Module Replacement (HMR) enabled
- Fast Refresh for React components
- Automatic page reloading on file changes

Access the application at: **http://localhost:3000**

**Sources:** [README.md:211-214](), [docker-compose.yml:234-246]()

---

## Development Workflow Diagram

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Term1 as Terminal 1<br/>(aitoearn-ai)
    participant Term2 as Terminal 2<br/>(aitoearn-server)
    participant Term3 as Terminal 3<br/>(aitoearn-web)
    participant Docker as Docker<br/>(MongoDB/Redis)
    
    Dev->>Docker: docker compose up -d mongodb redis
    activate Docker
    Docker-->>Dev: Infrastructure ready
    
    Dev->>Term1: cd project/aitoearn-backend<br/>npx nx serve aitoearn-ai
    activate Term1
    Term1->>Docker: Connect to MongoDB/Redis
    Term1-->>Dev: AI service running on :3010
    
    Dev->>Term2: npx nx serve aitoearn-server
    activate Term2
    Term2->>Docker: Connect to MongoDB/Redis
    Term2->>Term1: Connect to AI service
    Term2-->>Dev: Server running on :3002
    
    Dev->>Term3: cd aitoearn_web<br/>pnpm run dev
    activate Term3
    Term3-->>Dev: Web server running on :3000
    
    Note over Dev,Term3: Development environment ready<br/>Edit files and services auto-reload
    
    Dev->>Term1: Edit aitoearn-ai code
    Term1->>Term1: Detect change, rebuild, restart
    Term1-->>Dev: Service reloaded
    
    Dev->>Term3: Edit React component
    Term3->>Term3: HMR updates browser
    Term3-->>Dev: Browser updated (no reload)
```

**Service Startup Order**

1. **Start infrastructure** (MongoDB/Redis via Docker)
2. **Start aitoearn-ai** (depends on MongoDB/Redis)
3. **Start aitoearn-server** (depends on MongoDB/Redis/AI)
4. **Start aitoearn-web** (depends on aitoearn-server)

**Sources:** [README.md:193-216]()

---

## Service Communication in Development

```mermaid
graph LR
    subgraph "Browser (http://localhost:3000)"
        Browser["User Browser"]
    end
    
    subgraph "aitoearn_web (Next.js)"
        NextJS["Next.js Dev Server<br/>Port: 3000<br/>process.env.NEXT_PUBLIC_API_URL"]
    end
    
    subgraph "project/aitoearn-backend"
        Server["aitoearn-server<br/>Port: 3002<br/>config.js: serverClient.baseUrl"]
        AI["aitoearn-ai<br/>Port: 3010<br/>config.js: auth.internalToken"]
    end
    
    subgraph "Docker Containers"
        DB["MongoDB<br/>localhost:27017"]
        Cache["Redis<br/>localhost:6379"]
    end
    
    Browser -->|"HTTP"| NextJS
    NextJS -->|"API: NEXT_PUBLIC_API_URL"| Server
    Server -->|"AI_URL"| AI
    Server -->|"MONGODB_HOST:PORT"| DB
    Server -->|"REDIS_HOST:PORT"| Cache
    AI -->|"MONGODB_HOST:PORT"| DB
    AI -->|"REDIS_HOST:PORT"| Cache
```

**Key Configuration Points:**

| Service | Config File/Env Var | Purpose |
|---------|-------------------|---------|
| `aitoearn-web` | `NEXT_PUBLIC_API_URL` | Browser-side API endpoint |
| `aitoearn-server` | `AI_URL` in environment | How to reach AI service |
| `aitoearn-ai` | `SERVER_URL` in environment | How to reach main server |
| Both backends | `MONGODB_HOST`, `MONGODB_PORT` | Database connection |
| Both backends | `REDIS_HOST`, `REDIS_PORT` | Cache connection |
| Both backends | `JWT_SECRET`, `INTERNAL_TOKEN` | Must match for auth |

**Sources:** [docker-compose.yml:95-232](), [DOCKER_DEPLOYMENT_EN.md:155-173]()

---

## Hot Reload Capabilities

### Backend Services (Nx)

**Nx watch mode** automatically:
- Monitors TypeScript files in `apps/aitoearn-ai/` and `apps/aitoearn-server/`
- Recompiles on changes
- Restarts the Node.js process

**Affected files trigger reload:**
- `apps/aitoearn-ai/src/**/*.ts`
- `apps/aitoearn-server/src/**/*.ts`
- Shared libraries in `libs/`

**Changes requiring manual restart:**
- `config.js` modifications
- Environment variable changes
- `package.json` dependency updates

### Frontend (Next.js)

**Fast Refresh** provides:
- Instant component updates without full page reload
- Preserves React component state
- Automatic error recovery

**Affected files:**
- `aitoearn_web/src/**/*.tsx` (React components)
- `aitoearn_web/src/**/*.ts` (TypeScript files)
- `aitoearn_web/app/**/*` (Next.js App Router pages)

**Changes requiring manual restart:**
- `next.config.js` modifications
- `.env.local` changes

**Sources:** [README.md:193-216]()

---

## Port Reference

| Service | Port | Access URL | Notes |
|---------|------|------------|-------|
| **aitoearn-web** | 3000 | http://localhost:3000 | Direct Next.js dev server |
| **aitoearn-server** | 3002 | http://localhost:3002 | Direct API access (no proxy) |
| **aitoearn-ai** | 3010 | http://localhost:3010 | Internal AI service |
| **MongoDB** | 27017 | localhost:27017 | Via Docker or local |
| **Redis** | 6379 | localhost:6379 | Via Docker or local |
| **RustFS** | 9000 | http://localhost:9000 | Optional, via Docker |
| **RustFS Console** | 9001 | http://localhost:9001 | Optional, via Docker |

**Nginx (port 8080) is NOT used in development mode.** Services communicate directly.

**Sources:** [docker-compose.yml:1-286]()

---

## Troubleshooting

### Service Won't Start

**Check infrastructure is running:**
```bash
docker compose ps
# Ensure mongodb and redis show "healthy"
```

**Check ports are not in use:**
```bash
lsof -i :3000  # aitoearn-web
lsof -i :3002  # aitoearn-server
lsof -i :3010  # aitoearn-ai
```

**Verify environment variables:**
```bash
# In the terminal where you're starting the service
echo $MONGODB_HOST
echo $REDIS_HOST
echo $JWT_SECRET
```

### Connection Errors

**Cannot connect to MongoDB/Redis:**
- Verify Docker containers are running: `docker compose ps`
- Check credentials match between environment and Docker: [docker-compose.yml:6-8](), [docker-compose.yml:27]()
- Test connection manually:
  ```bash
  # MongoDB
  mongosh mongodb://admin:password@localhost:27017
  
  # Redis
  redis-cli -h localhost -p 6379 -a password
  ```

**aitoearn-server cannot reach aitoearn-ai:**
- Ensure `AI_URL=http://localhost:3010` (NOT a Docker service name)
- Verify aitoearn-ai is running on port 3010

### Hot Reload Not Working

**Backend changes not applying:**
- Check terminal output for compilation errors
- Nx watch may have crashed - restart the service
- For config.js changes, always restart manually

**Frontend changes not applying:**
- Check browser console for errors
- Clear Next.js cache: `rm -rf aitoearn_web/.next`
- Restart dev server

### Build Errors

**Missing dependencies:**
```bash
cd project/aitoearn-backend
pnpm install

cd aitoearn_web
pnpm install
```

**TypeScript errors:**
- Check `tsconfig.json` is present
- Verify Node.js version matches requirements: [README.md:8]()

**Sources:** [README.md:193-216](), [docker-compose.yml:1-286]()

---

## Stopping Services

To stop all services:

1. **Stop frontend** (Terminal 3): Press `Ctrl+C`
2. **Stop aitoearn-server** (Terminal 2): Press `Ctrl+C`
3. **Stop aitoearn-ai** (Terminal 1): Press `Ctrl+C`
4. **Stop Docker infrastructure**:
   ```bash
   docker compose down
   # Or to keep data volumes:
   docker compose stop
   ```

**Sources:** [README.md:193-216]()

---

# Page: Project Structure and Conventions

# Project Structure and Conventions

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



This document describes the organization of the AiToEarn monorepo, including directory structure, naming conventions, module organization patterns, and important configuration files. Understanding this structure is essential for developers who want to contribute to or extend the platform.

For information about setting up a development environment, see [Development Mode Setup](#8.1). For deployment configuration details, see [Environment Configuration](#7.2).

## Repository Organization

AiToEarn uses a **monorepo structure** with separate directories for backend services, frontend application, infrastructure configuration, and deployment files. The repository is organized to support Docker-based deployment while also allowing independent development of each service.

**Key Characteristics:**
- **Backend**: NestJS monorepo in `project/aitoearn-backend/` containing two microservices
- **Frontend**: Next.js application in `aitoearn_web/`
- **Desktop**: Separate repository ([AttAiToEarn](https://github.com/yikart/AttAiToEarn)) for Electron app
- **Configuration**: Centralized config files in `config/` for Docker deployment
- **Infrastructure**: Docker Compose and Nginx configurations at root level

Sources: [README.md:158-216](), [README.md:220-242](), [docker-compose.yml:1-286]()

## Top-Level Directory Structure

```mermaid
graph TB
    root["AiToEarn Repository Root"]
    
    root --> backend["project/aitoearn-backend/<br/>(NestJS Monorepo)"]
    root --> web["aitoearn_web/<br/>(Next.js Frontend)"]
    root --> config["config/<br/>(Service Configs)"]
    root --> nginx_dir["nginx/<br/>(Nginx Config)"]
    root --> presentation["presentation/<br/>(Marketing Materials)"]
    root --> docker["docker-compose.yml"]
    root --> gitignore[".gitignore"]
    root --> readme["README.md / README_CN.md"]
    
    backend --> ai_service["apps/aitoearn-ai/<br/>(AI Service)"]
    backend --> server_service["apps/aitoearn-server/<br/>(Main Backend API)"]
    backend --> shared_libs["libs/<br/>(Shared Libraries)"]
    
    web --> web_src["src/<br/>(Source Code)"]
    web --> web_public["public/<br/>(Static Assets)"]
    web --> web_config["package.json<br/>next.config.js"]
    
    config --> ai_config["aitoearn-ai.config.js"]
    config --> server_config["aitoearn-server.config.js"]
    config --> gcs_config["gcs-placeholder.json"]
    
    nginx_dir --> nginx_conf["nginx.conf"]
    
    presentation --> screenshots["app-screenshot/"]
    presentation --> videos["display-*.png"]
    
    classDef services fill:#e8f5e9,stroke:#4caf50
    classDef config fill:#fff3e0,stroke:#f57c00
    classDef infra fill:#e3f2fd,stroke:#1976d2
    
    class backend,ai_service,server_service,web services
    class config,ai_config,server_config,nginx_dir,nginx_conf config
    class docker,gitignore infra
```

Sources: [README.md:158-242](), [docker-compose.yml:1-286](), [.gitignore:1-48]()

## Backend Services Structure

The backend is organized as a **NestJS monorepo** using Nx for build orchestration. It contains two main applications that share common libraries.

```mermaid
graph LR
    subgraph "project/aitoearn-backend/"
        nx["nx.json<br/>package.json<br/>tsconfig.base.json"]
        
        subgraph "apps/"
            ai["aitoearn-ai<br/>Port: 3010"]
            server["aitoearn-server<br/>Port: 3002"]
        end
        
        subgraph "libs/"
            shared["Shared Libraries<br/>(common code)"]
        end
        
        ai -.->|imports| shared
        server -.->|imports| shared
    end
    
    subgraph "Service Communication"
        ai -->|HTTP| server
        server -->|HTTP| ai
    end
```

**Build and Run Commands:**
- Build: `npx nx build aitoearn-ai` or `npx nx build aitoearn-server`
- Dev mode: `npx nx serve aitoearn-ai` or `npx nx serve aitoearn-server`
- Both services must be started separately in development mode

**Service Responsibilities:**
- **aitoearn-ai**: AI model orchestration, content generation, multi-provider integration
- **aitoearn-server**: Main business logic, OAuth, database operations, platform publishing

Sources: [README.md:199-207](), [docker-compose.yml:81-134](), [docker-compose.yml:136-232]()

## Frontend Application Structure

The frontend is a **Next.js 14** application using the App Router pattern with React 18 and TypeScript.

```mermaid
graph TB
    subgraph "aitoearn_web/"
        pkg["package.json<br/>pnpm workspace"]
        next_config["next.config.js"]
        
        subgraph "src/"
            app["app/<br/>(App Router)"]
            components["components/<br/>(React Components)"]
            lib["lib/<br/>(Utilities)"]
            styles["styles/<br/>(CSS/Styling)"]
        end
        
        subgraph "public/"
            static["Static Assets"]
            bin["bin/<br/>(Binary Files)"]
        end
        
        subgraph "Special Directories"
            channel_md["CHANNEL_Md/<br/>(Platform Docs)"]
            contrib["CONTRIBUTING.md"]
        end
    end
    
    app --> components
    app --> lib
    components --> lib
```

**Package Management:**
- Uses `pnpm` for dependency management
- Development: `pnpm run dev`
- Production build: `pnpm run build`

**API Integration:**
- Backend URL configured via `NEXT_PUBLIC_API_URL` environment variable
- Default: `http://localhost:8080/api` (via Nginx proxy)

Sources: [README.md:209-215](), [docker-compose.yml:234-247](), [README_CN.md:195-200]()

## Configuration Management

Configuration is split between **environment variables** (in `docker-compose.yml`) and **application config files** (in `config/` directory).

```mermaid
graph TB
    subgraph "Configuration Layer"
        compose["docker-compose.yml<br/>(Environment Variables)"]
        
        subgraph "config/"
            ai_cfg["aitoearn-ai.config.js"]
            server_cfg["aitoearn-server.config.js"]
            gcs["gcs-placeholder.json"]
        end
    end
    
    subgraph "Services"
        ai_svc["aitoearn-ai<br/>Container"]
        server_svc["aitoearn-server<br/>Container"]
    end
    
    compose -->|env vars| ai_svc
    compose -->|env vars| server_svc
    ai_cfg -->|mounted as<br/>/app/config.js| ai_svc
    server_cfg -->|mounted as<br/>/app/config.js| server_svc
    gcs -->|mounted as<br/>/app/config/gcs-placeholder.json| ai_svc
    
    ai_svc -->|reads process.env| ai_cfg
    server_svc -->|reads process.env| server_cfg
```

**Configuration File Mapping:**

| File | Mounted To | Purpose |
|------|------------|---------|
| `config/aitoearn-ai.config.js` | `/app/config.js` in `aitoearn-ai` | AI model definitions, storage config, service URLs |
| `config/aitoearn-server.config.js` | `/app/config.js` in `aitoearn-server` | OAuth callbacks, storage config, email settings |
| `config/gcs-placeholder.json` | `/app/config/gcs-placeholder.json` in `aitoearn-ai` | Google Cloud service account credentials |

**Environment Variable Pattern:**
- Database credentials: `MONGODB_HOST`, `MONGODB_PORT`, `MONGODB_USERNAME`, `MONGODB_PASSWORD`
- Redis credentials: `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`
- Service URLs: `SERVER_URL`, `AI_URL`, `NEXT_PUBLIC_API_URL`
- API keys: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.

Sources: [docker-compose.yml:91-127](), [docker-compose.yml:148-226](), [DOCKER_DEPLOYMENT_EN.md:98-110]()

## Docker Deployment Structure

All services are orchestrated through **Docker Compose** with a custom bridge network for inter-service communication.

```mermaid
graph TB
    subgraph "Docker Compose Stack"
        compose_file["docker-compose.yml"]
        
        subgraph "Data Services"
            mongo["mongodb<br/>mongo:latest<br/>Port: 27017"]
            redis["redis<br/>redis:latest<br/>Port: 6379"]
            rustfs["rustfs<br/>rustfs/rustfs:latest<br/>Ports: 9000, 9001"]
            rustfs_init["rustfs-init<br/>minio/mc:latest<br/>(Init Container)"]
        end
        
        subgraph "Application Services"
            ai["aitoearn-ai<br/>aitoearn/aitoearn-ai:latest"]
            server["aitoearn-server<br/>aitoearn/aitoearn-server:latest"]
            web["aitoearn-web<br/>aitoearn/aitoearn-web:latest"]
        end
        
        subgraph "Proxy Layer"
            nginx["nginx<br/>nginx:alpine<br/>Port: 8080"]
        end
        
        subgraph "Volumes"
            mongo_data["mongodb-data"]
            redis_data["redis-data"]
            rustfs_data["rustfs-data"]
        end
        
        subgraph "Network"
            network["aitoearn-network<br/>(bridge)"]
        end
    end
    
    mongo --> mongo_data
    redis --> redis_data
    rustfs --> rustfs_data
    
    rustfs_init -.->|initializes| rustfs
    
    ai -->|depends_on| mongo
    ai -->|depends_on| redis
    server -->|depends_on| mongo
    server -->|depends_on| redis
    server -->|depends_on| ai
    web -->|depends_on| server
    nginx -->|depends_on| web
    nginx -->|depends_on| server
    nginx -->|depends_on| ai
    
    mongo -.-> network
    redis -.-> network
    rustfs -.-> network
    ai -.-> network
    server -.-> network
    web -.-> network
    nginx -.-> network
```

**Container Naming Convention:**
- Database: `aitoearn-mongodb`, `aitoearn-redis`
- Storage: `aitoearn-rustfs`, `aitoearn-rustfs-init`
- Application: `aitoearn-ai`, `aitoearn-server`, `aitoearn-web`
- Proxy: `aitoearn-nginx`

**Network Configuration:**
- Network name: `aitoearn-network`
- Driver: `bridge`
- Internal DNS: Services accessible by container name (e.g., `mongodb`, `redis`, `rustfs.local`)

**Volume Persistence:**
- `mongodb-data`: MongoDB database files (`/data/db`, `/data/configdb`)
- `redis-data`: Redis persistence files (`/data`)
- `rustfs-data`: Object storage data (`/data`)

Sources: [docker-compose.yml:1-286](), [DOCKER_DEPLOYMENT_EN.md:6-36]()

## Nginx Routing Configuration

Nginx acts as a **reverse proxy** routing requests to the appropriate backend service.

```mermaid
graph LR
    client["Client Browser<br/>localhost:8080"]
    
    subgraph "Nginx :80"
        proxy["nginx.conf"]
    end
    
    subgraph "Backend Services"
        web_service["aitoearn-web:3000<br/>(Next.js)"]
        api_service["aitoearn-server:3002<br/>(NestJS API)"]
        ai_api["aitoearn-ai:3010<br/>(AI Service)"]
    end
    
    client -->|":8080"| proxy
    proxy -->|"/" <br/> "/_next"| web_service
    proxy -->|"/api"| api_service
    proxy -->|"/ai-api"| ai_api
    proxy -->|"/_nhealth"| health["Health Check"]
```

**Routing Rules (from nginx.conf):**
- `/` → `aitoearn-web:3000` (Frontend)
- `/api` → `aitoearn-server:3002` (Backend API)
- `/ai-api` → `aitoearn-ai:3010` (AI Service, if exposed)
- `/_nhealth` → Nginx health check endpoint

**Configuration File:**
- Location: `nginx/nginx.conf`
- Mounted to: `/etc/nginx/nginx.conf` in nginx container (read-only)

Sources: [docker-compose.yml:248-270](), [DOCKER_DEPLOYMENT_EN.md:130-135]()

## Git Ignore Patterns

The `.gitignore` file follows standard Node.js patterns with project-specific exclusions.

### Standard Exclusions

**Build Artifacts:**
- `node_modules` - npm dependencies
- `dist` - Production builds
- `dist-ssr` - Server-side rendering builds
- `dist-electron` - Electron build output
- `release` - Release packages
- `*.local` - Local environment files

**Development Files:**
- `.vscode` - VS Code settings (partial)
- `.vscode/.debug.env` - Debug environment (specific)
- `.idea` - JetBrains IDE settings
- `.DS_Store` - macOS metadata
- Editor temp files: `*.suo`, `*.ntvs*`, `*.njsproj`, `*.sln`, `*.sw?`

**Test Output:**
- `/test-results/`
- `/playwright-report/`
- `/playwright/.cache/`

Sources: [.gitignore:1-34]()

### Project-Specific Exclusions

**Database Files:**
```
*.db
```
All SQLite database files are excluded (likely used in Electron app for local data).

**Binary Files:**
```
*.exe
```
Executable files are excluded from version control.

**Binary Directory Exception:**
```
public/bin/*
!public/bin/webkit
!public/bin/*.md
```
- Excludes all files in `public/bin/`
- **Except**: `webkit` subdirectory and `.md` documentation files

**Custom Paths:**
```
sh/*
project/web/.cursor/
```
- `sh/*` - Shell scripts directory (entire directory excluded)
- `project/web/.cursor/` - Cursor AI editor cache

**Lockfile Policy:**
The following lines are commented out, meaning lockfiles **are committed**:
```
# package-lock.json
# pnpm-lock.yaml
# yarn.lock
```
This ensures consistent dependency versions across environments.

Sources: [.gitignore:35-48]()

## Naming Conventions

### Service Names

**Pattern:** `aitoearn-{service-name}`

| Service Type | Container Name | Docker Image | Internal Hostname |
|--------------|----------------|--------------|-------------------|
| AI Service | `aitoearn-ai` | `aitoearn/aitoearn-ai:latest` | `aitoearn-ai` |
| Backend API | `aitoearn-server` | `aitoearn/aitoearn-server:latest` | `aitoearn-server` |
| Frontend | `aitoearn-web` | `aitoearn/aitoearn-web:latest` | `aitoearn-web` |
| Database | `aitoearn-mongodb` | `mongo:latest` | `mongodb` |
| Cache | `aitoearn-redis` | `redis:latest` | `redis` |
| Storage | `aitoearn-rustfs` | `rustfs/rustfs:latest` | `rustfs.local` |
| Proxy | `aitoearn-nginx` | `nginx:alpine` | - |

**Rationale:**
- Container names use full `aitoearn-` prefix for clarity in `docker ps` output
- Internal hostnames omit prefix for brevity in configuration
- RustFS uses `.local` TLD to distinguish as internal service

### Environment Variables

**Pattern by Category:**

| Category | Pattern | Examples |
|----------|---------|----------|
| Database Connection | `{SERVICE}_HOST`, `{SERVICE}_PORT`, `{SERVICE}_USERNAME`, `{SERVICE}_PASSWORD` | `MONGODB_HOST`, `REDIS_PORT` |
| API Keys | `{PROVIDER}_API_KEY` | `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` |
| OAuth Credentials | `{PLATFORM}_CLIENT_ID`, `{PLATFORM}_CLIENT_SECRET` | `TIKTOK_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` |
| Service URLs | `{SERVICE}_URL` | `SERVER_URL`, `AI_URL` |
| Feature Flags | `{FEATURE}_{SETTING}` | `NEXT_TELEMETRY_DISABLED` |

### Configuration Files

**Pattern:** `{service-name}.config.js`

- `aitoearn-ai.config.js` - AI service configuration
- `aitoearn-server.config.js` - Backend service configuration

**Service Account Keys:** `{provider}-{purpose}.json`
- `gcs-placeholder.json` - Google Cloud Service account placeholder

Sources: [docker-compose.yml:1-286](), [DOCKER_DEPLOYMENT_EN.md:140-151]()

## Module Organization Patterns

### NestJS Monorepo Structure

The backend follows **Nx monorepo** conventions with apps and shared libraries:

```
project/aitoearn-backend/
├── apps/
│   ├── aitoearn-ai/          # AI microservice
│   └── aitoearn-server/      # Main API microservice
├── libs/                      # Shared libraries
├── nx.json                    # Nx workspace config
├── package.json               # Root package.json
└── tsconfig.base.json         # Base TypeScript config
```

**Build System:**
- Uses **Nx** for monorepo orchestration
- Command pattern: `npx nx {command} {app-name}`
- Examples:
  - `npx nx serve aitoearn-ai` - Start AI service in dev mode
  - `npx nx build aitoearn-server` - Build server for production

Sources: [README.md:199-207]()

### Configuration File Structure

Config files use a **functional export pattern** that reads from `process.env`:

```javascript
// Typical config.js structure (example pattern)
module.exports = {
  port: parseInt(process.env.PORT) || 3010,
  
  mongodb: {
    uri: `mongodb://${process.env.MONGODB_USERNAME}:${process.env.MONGODB_PASSWORD}@${process.env.MONGODB_HOST}:${process.env.MONGODB_PORT}`,
    dbName: 'aitoearn',
  },
  
  redis: {
    host: process.env.REDIS_HOST,
    port: parseInt(process.env.REDIS_PORT),
    password: process.env.REDIS_PASSWORD,
  },
  
  auth: {
    secret: process.env.JWT_SECRET,
    expiresIn: 604800,
  },
  
  // AI model definitions (hardcoded)
  aiModels: [ /* ... */ ],
  
  // Storage config (hardcoded + env vars)
  assets: {
    provider: 's3',
    endpoint: 'http://rustfs.local:9000',
    accessKeyId: process.env.RUSTFS_ACCESS_KEY || 'rustfsadmin',
    // ...
  },
};
```

**Pattern Rationale:**
- Environment variables for **secrets and environment-specific values**
- Hardcoded configuration for **model lists, routes, and business logic**
- Allows config files to be committed while keeping secrets in env vars

Sources: [DOCKER_DEPLOYMENT_EN.md:98-110](), [docker-compose.yml:91-127]()

### Package Manager Consistency

**Backend Services (NestJS):**
- Uses `pnpm` for package management
- Workspace configuration in `package.json`

**Frontend (Next.js):**
- Uses `pnpm` for package management
- Independent `package.json` in `aitoearn_web/`

**Desktop App (Electron):**
- Separate repository: [AttAiToEarn](https://github.com/yikart/AttAiToEarn)
- Uses `npm` for package management
- Requires `node-gyp` for native dependencies (`better-sqlite3`)

Sources: [README.md:199-242]()

## Volume and Data Persistence

Docker volumes follow a **{service}-data** naming pattern:

| Volume Name | Purpose | Container Mount Point |
|-------------|---------|----------------------|
| `mongodb-data` | MongoDB database files | `/data/db` |
| `mongodb-config` | MongoDB configuration | `/data/configdb` |
| `redis-data` | Redis persistence | `/data` |
| `rustfs-data` | Object storage files | `/data` |

**Local Driver:**
All volumes use the `local` driver, storing data in Docker's volume directory on the host.

**Volume Lifecycle:**
- Created automatically on first `docker compose up`
- Persist across container restarts and recreations
- Removed only with `docker compose down -v` (explicit volume deletion)

**Backup Considerations:**
- MongoDB data at: `$(docker volume inspect aitoearn_mongodb-data -f '{{.Mountpoint}}')`
- RustFS data at: `$(docker volume inspect aitoearn_rustfs-data -f '{{.Mountpoint}}')`

Sources: [docker-compose.yml:277-285]()

## Health Check Patterns

All critical services implement **health check endpoints** for monitoring and orchestration:

### Service Health Checks

| Service | Check Method | Endpoint/Command | Interval |
|---------|--------------|------------------|----------|
| MongoDB | mongosh command | `db.runCommand("ping")` on `localhost:27017/test` | 10s |
| Redis | redis-cli | `redis-cli --raw incr ping` | 10s |
| RustFS | HTTP GET | `http://localhost:9000/health` | 10s |
| aitoearn-ai | Node.js HTTP | `http://localhost:3010/health` | 30s |
| aitoearn-server | Node.js HTTP | `http://localhost:3002/health` | 30s |
| Nginx | wget | `http://localhost/_nhealth` | 10s |

**Dependency Ordering:**
Services use `depends_on` with `condition: service_healthy` to ensure proper startup sequence:

```yaml
aitoearn-ai:
  depends_on:
    mongodb:
      condition: service_healthy
    redis:
      condition: service_healthy

aitoearn-server:
  depends_on:
    mongodb:
      condition: service_healthy
    redis:
      condition: service_healthy
    aitoearn-ai:
      condition: service_healthy
```

This ensures:
1. Data services (MongoDB, Redis) start first
2. AI service waits for data services
3. Server waits for AI service
4. Frontend and Nginx wait for server

Sources: [docker-compose.yml:16-21](), [docker-compose.yml:34-39](), [docker-compose.yml:58-63](), [docker-compose.yml:129-134](), [docker-compose.yml:227-232](), [docker-compose.yml:265-270]()

## Development vs. Production Modes

### Development Mode (Manual)

**Backend Services:**
```bash
cd project/aitoearn-backend
pnpm install
npx nx serve aitoearn-ai      # Terminal 1
npx nx serve aitoearn-server  # Terminal 2
```

**Frontend:**
```bash
cd aitoearn_web
pnpm install
pnpm run dev
```

**Characteristics:**
- Hot reload enabled for all services
- Services run on host machine (not in Docker)
- Must manually start MongoDB/Redis or use Docker for data services only
- Environment variables from local `.env` files

### Production Mode (Docker)

```bash
docker compose up -d
```

**Characteristics:**
- All services in containers
- Environment variables from `docker-compose.yml`
- Config files mounted from `config/` directory
- Nginx handles routing and SSL termination
- Persistent volumes for data
- Health checks and automatic restart policies

**Key Differences:**

| Aspect | Development | Production (Docker) |
|--------|-------------|---------------------|
| Service startup | Manual, independent | Automated, orchestrated |
| Config source | Local files, `.env` | `docker-compose.yml`, mounted configs |
| Hot reload | Yes | No (requires rebuild) |
| Networking | localhost ports | Docker internal network |
| Logs | Terminal output | `docker compose logs` |

Sources: [README.md:193-216](), [DOCKER_DEPLOYMENT_EN.md:53-128]()

## Desktop Application Repository

The Electron desktop application is maintained in a **separate repository** with different build requirements.

**Repository:** https://github.com/yikart/AttAiToEarn

**Setup:**
```bash
git clone https://github.com/yikart/AttAiToEarn.git
cd AttAiToEarn
npm i
npm run rebuild  # Compile native dependencies (better-sqlite3)
npm run dev
```

**Key Dependencies:**
- `better-sqlite3` - Requires native compilation with `node-gyp`
- Python required for node-gyp build process

**Integration:**
- Communicates with backend via same API endpoints as web frontend
- Can be configured to connect to local development server or production deployment

Sources: [README.md:220-242](), [README_CN.md:204-225]()