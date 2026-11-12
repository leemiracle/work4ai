> 来源: [https://deepwiki.com/Tencent/WeKnora/9-deployment-and-operations](https://deepwiki.com/Tencent/WeKnora/9-deployment-and-operations)
> DeepWiki Tencent/WeKnora

# Deployment and Operations

  Relevant source files 
 - [.github/workflows/docker-image.yml](https://github.com/Tencent/WeKnora/blob/10973ed3/.github/workflows/docker-image.yml)
 - [.github/workflows/frontend.yml](https://github.com/Tencent/WeKnora/blob/10973ed3/.github/workflows/frontend.yml)
 - [Makefile](https://github.com/Tencent/WeKnora/blob/10973ed3/Makefile)
 - [docker/Dockerfile.app](https://github.com/Tencent/WeKnora/blob/10973ed3/docker/Dockerfile.app)
 - [docker/Dockerfile.docreader](https://github.com/Tencent/WeKnora/blob/10973ed3/docker/Dockerfile.docreader)
 - [frontend/.dockerignore](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/.dockerignore)
 - [frontend/Dockerfile](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/Dockerfile)
 - [scripts/build_frontend_dist.sh](https://github.com/Tencent/WeKnora/blob/10973ed3/scripts/build_frontend_dist.sh)
 - [scripts/build_images.sh](https://github.com/Tencent/WeKnora/blob/10973ed3/scripts/build_images.sh)
 - [scripts/get_version.sh](https://github.com/Tencent/WeKnora/blob/10973ed3/scripts/get_version.sh)
 - [scripts/start_all.sh](https://github.com/Tencent/WeKnora/blob/10973ed3/scripts/start_all.sh)
 - [website-docs/01-getting-started/02-installation.md](https://github.com/Tencent/WeKnora/blob/10973ed3/website-docs/01-getting-started/02-installation.md?plain=1)
 - [website-docs/02-architecture/01-overview.md](https://github.com/Tencent/WeKnora/blob/10973ed3/website-docs/02-architecture/01-overview.md?plain=1)
 - [website-docs/05-clients/01-frontend.md](https://github.com/Tencent/WeKnora/blob/10973ed3/website-docs/05-clients/01-frontend.md?plain=1)
 - [website-docs/06-development/01-dev-guide.md](https://github.com/Tencent/WeKnora/blob/10973ed3/website-docs/06-development/01-dev-guide.md?plain=1)
 
  This page serves as the high-level gateway for deploying and operating WeKnora in production environments. It provides an overview of the system's microservice topology, container orchestration, build pipelines, configuration workflows, and persistent data management. Detailed deployment guides, environment-specific best practices, migration processes, and monitoring strategies are covered in linked child pages to maintain clarity and depth.

 
---

 
## Service Topology

 WeKnora is architected as a set of loosely coupled microservices deployed primarily with Docker Compose. The core user-facing frontend served by Nginx communicates with the Go-based backend application. Backend dependencies include a Python-based document reader service, PostgreSQL or other supported databases for metadata and index storage, Redis for caching and task queues, and Ollama for local or remote LLM inference.

 This topology is defined and managed through `docker-compose.yml`, with environment variables injected from `.env` files or direct environment configurations. The build and orchestration is orchestrated through the Makefile along with helper scripts.

 
```

```

 Sources: [docker-compose.yml1-156](https://github.com/Tencent/WeKnora/blob/10973ed3/docker-compose.yml#L1-L156) [docker/Dockerfile.app1-157](https://github.com/Tencent/WeKnora/blob/10973ed3/docker/Dockerfile.app#L1-L157) [scripts/start_all.sh1-243](https://github.com/Tencent/WeKnora/blob/10973ed3/scripts/start_all.sh#L1-L243) [Makefile16-33](https://github.com/Tencent/WeKnora/blob/10973ed3/Makefile#L16-L33)

 
---

 
## Core Services Overview

 The WeKnora system runs inside specialized Docker containers, each built and deployed with their respective Dockerfiles and managed via Compose profiles.

 
| Service | Docker Image Name | Build Definition | Role |
|---|---|---|---|
| WeKnora-frontend | wechatopenai/weknora-ui | frontend/Dockerfile1-77 | Vue.js SPA served by Nginx, frontend UI. Proxies API calls to backend. |
| WeKnora-app | wechatopenai/weknora-app | docker/Dockerfile.app1-157 | Main Go backend service handling API, RAG pipeline, and agents. |
| WeKnora-docreader | wechatopenai/weknora-docreader | docker/Dockerfile.docreader1-159 | Python gRPC service for advanced document parsing, image extraction. |
| WeKnora-sandbox | wechatopenai/weknora-sandbox | Dockerfile and deployment in dev Compose | Isolated runtime for executing code skills and agent tools. |

 Each container exposes relevant network ports and uses environment variables to configure connectivity and features.

 Sources: [docker-compose.yml2-48](https://github.com/Tencent/WeKnora/blob/10973ed3/docker-compose.yml#L2-L48) [docker/Dockerfile.app1-157](https://github.com/Tencent/WeKnora/blob/10973ed3/docker/Dockerfile.app#L1-L157) [docker/Dockerfile.docreader1-159](https://github.com/Tencent/WeKnora/blob/10973ed3/docker/Dockerfile.docreader#L1-L159) [Makefile16-33](https://github.com/Tencent/WeKnora/blob/10973ed3/Makefile#L16-L33)

 
---

 
## Deployment Strategies

 WeKnora provides multiple deployment scenarios to tailor to development, testing, production, or lightweight local usage.

 
### 1. Docker Deployment

 This method uses `docker-compose.yml` to orchestrate all services, networking, and persistent volumes. The main application container and frontend operate behind Nginx proxy. User configuration is injected from `.env` files.

 
 - **Profile-based Service Selection:** Optional Docker Compose profiles enable or disable auxiliary services like Langfuse observability or alternative vector databases.
 - **Ollama LLM Service:** Controlled via `OLLAMA_BASE_URL`, WeKnora can connect to a locally installed Ollama instance or remote inference service.
 - **Environment Variables:** Managed in `.env` (created by copying `.env.example`) and used for Docker Compose and runtime configuration.
 
 For step-by-step instructions, see [Docker Deployment](https://deepwiki.com/Tencent/WeKnora/9.1-docker-deployment).

 
### 2. Production Setup and Best Practices

 Production deployment recommendations including Helm/Kubernetes charts, cloud image deployment via Tencent Lighthouse, security hardening, resource scaling, and automated backup procedures.

 For full recommendations, see [Production Setup and Best Practices](https://deepwiki.com/Tencent/WeKnora/9.2-production-setup-and-best-practices).

 
### 3. Database Migrations and Maintenance

 Document the versioned migration system supporting Postgres, ParadeDB, MySQL, and SQLite, along with the migration runner and database maintenance procedures.

 For operational instructions, see [Database Migrations and Maintenance](https://deepwiki.com/Tencent/WeKnora/9.3-database-migrations-and-maintenance).

 
### 4. Monitoring and Troubleshooting

 Guide to monitoring integration with Jaeger and Langfuse, logging configurations, runtime queue inspection, health checks, and debugging techniques.

 For troubleshooting help, see [Monitoring and Troubleshooting](https://deepwiki.com/Tencent/WeKnora/9.4-monitoring-and-troubleshooting).

 Sources: [docker-compose.yml1-156](https://github.com/Tencent/WeKnora/blob/10973ed3/docker-compose.yml#L1-L156) [Makefile13-68](https://github.com/Tencent/WeKnora/blob/10973ed3/Makefile#L13-L68) [scripts/start_all.sh1-243](https://github.com/Tencent/WeKnora/blob/10973ed3/scripts/start_all.sh#L1-L243)

 
---

 
## Runtime Configuration and Database Migrations

 WeKnora supports a dynamic runtime configuration system where specific settings can be adjusted without taking the system offline.

 
 - The `systemSettingSvc` controls registered keys that can be updated in the UI or API, such as `auth.registration_mode` or `tenant.max_owned_per_user`.
 - Configuration changes propagate immediately via Redis Pub/Sub to all backend replicas, ensuring consistent live behavior.
 
 Database schema management is automated with a migration runner supporting multiple backends (`postgres`, `mysql`, `sqlite`) and version tracking.

 
 - Migrations can run automatically on startup if `AUTO_MIGRATE` is enabled in the environment.
 - Manual migration control is available through the Makefile with targets such as `migrate-up`, `migrate-down`, and `migrate-force`.
 
 For full operational details, see [Database Migrations and Maintenance](https://deepwiki.com/Tencent/WeKnora/9.3-database-migrations-and-maintenance).

 
```

```

 Sources: [docker/Dockerfile.app1-157](https://github.com/Tencent/WeKnora/blob/10973ed3/docker/Dockerfile.app#L1-L157) [Makefile190-215](https://github.com/Tencent/WeKnora/blob/10973ed3/Makefile#L190-L215) [scripts/start_all.sh100-125](https://github.com/Tencent/WeKnora/blob/10973ed3/scripts/start_all.sh#L100-L125)

 
---

 
## Volume and Data Management

 Persistent storage uses Docker volumes and shared directories to secure user data, knowledge bases, and runtime-generated content:

 
| Data Type | Volume / Host Path | Purpose / Notes |
|---|---|---|
| Uploaded Files | /data/files | User-uploaded documents and media, configured via LOCAL_STORAGE_BASE_DIR. |
| Database Storage | postgres-data-dev (Docker volume) | Persisted PostgreSQL storage (ParadeDB). |
| DocReader Temp | /tmp/docreader | Shared temporary directory for document images extracted by docreader. |
| Custom Skills | /app/skills/preloaded | Mounted directory for user-defined or preloaded agent skills. |

 Adequate volume mounts ensure data durability across container restarts and upgrades.

 Sources: [docker-compose.yml39-48](https://github.com/Tencent/WeKnora/blob/10973ed3/docker-compose.yml#L39-L48) [docker/Dockerfile.app129-132](https://github.com/Tencent/WeKnora/blob/10973ed3/docker/Dockerfile.app#L129-L132) [docker/Dockerfile.docreader153-154](https://github.com/Tencent/WeKnora/blob/10973ed3/docker/Dockerfile.docreader#L153-L154)

 
---

 
## Subpages

 
 - **[Docker Deployment](https://deepwiki.com/Tencent/WeKnora/9.1-docker-deployment)**
 Detailed walkthrough of Docker Compose deployment, profile selection for features (e.g., `--profile qdrant`), volume configuration, and container networking.
 - **[Production Setup and Best Practices](https://deepwiki.com/Tencent/WeKnora/9.2-production-setup-and-best-practices)**
 Guidance for deploying WeKnora to production with Helm/Kubernetes charts, cloud images on Tencent Lighthouse, recommendations for security hardening, autoscaling, and backup procedures.
 - **[Database Migrations and Maintenance](https://deepwiki.com/Tencent/WeKnora/9.3-database-migrations-and-maintenance)**
 Comprehensive documentation for managing database versions, running migration commands, backouts, and maintenance workflows.
 - **[Monitoring and Troubleshooting](https://deepwiki.com/Tencent/WeKnora/9.4-monitoring-and-troubleshooting)**
 Instructions on enabling observability using Jaeger and Langfuse, log capture configuration, task queue inspection, health checks, and debugging practices.
 
 
---

 
# Visual Bridge from Natural Language Components to Code Entities

 
## Diagram 1: Natural Language Space to Core Code Entities

 
```

```

 Sources: [frontend/Dockerfile1-77](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/Dockerfile#L1-L77) [docker/Dockerfile.app1-157](https://github.com/Tencent/WeKnora/blob/10973ed3/docker/Dockerfile.app#L1-L157) [docker/Dockerfile.docreader1-159](https://github.com/Tencent/WeKnora/blob/10973ed3/docker/Dockerfile.docreader#L1-L159) [docker-compose.yml1-156](https://github.com/Tencent/WeKnora/blob/10973ed3/docker-compose.yml#L1-L156)

 
## Diagram 2: Deployment Orchestration and Build Pipeline

 
```

```

 Sources: [Makefile1-215](https://github.com/Tencent/WeKnora/blob/10973ed3/Makefile#L1-L215) [scripts/build_images.sh1-255](https://github.com/Tencent/WeKnora/blob/10973ed3/scripts/build_images.sh#L1-L255) [scripts/start_all.sh1-243](https://github.com/Tencent/WeKnora/blob/10973ed3/scripts/start_all.sh#L1-L243) [docker-compose.yml1-156](https://github.com/Tencent/WeKnora/blob/10973ed3/docker-compose.yml#L1-L156)

 
---

 This overview page connects you to specialized child pages providing comprehensive deployment and operation instructions for WeKnora. For the detailed step-by-step guides and best practices, please continue to the respective subpages linked above.
