> 来源: [https://deepwiki.com/Tencent/WeKnora/2-getting-started](https://deepwiki.com/Tencent/WeKnora/2-getting-started)
> DeepWiki Tencent/WeKnora

# Getting Started

  Relevant source files 
 - [.github/workflows/docker-image.yml](https://github.com/Tencent/WeKnora/blob/10973ed3/.github/workflows/docker-image.yml)
 - [.github/workflows/frontend.yml](https://github.com/Tencent/WeKnora/blob/10973ed3/.github/workflows/frontend.yml)
 - [CHANGELOG.md](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1)
 - [Makefile](https://github.com/Tencent/WeKnora/blob/10973ed3/Makefile)
 - [README.md](https://github.com/Tencent/WeKnora/blob/10973ed3/README.md?plain=1)
 - [README_CN.md](https://github.com/Tencent/WeKnora/blob/10973ed3/README_CN.md?plain=1)
 - [README_JA.md](https://github.com/Tencent/WeKnora/blob/10973ed3/README_JA.md?plain=1)
 - [README_KO.md](https://github.com/Tencent/WeKnora/blob/10973ed3/README_KO.md?plain=1)
 - [VERSION](https://github.com/Tencent/WeKnora/blob/10973ed3/VERSION)
 - [docker/Dockerfile.app](https://github.com/Tencent/WeKnora/blob/10973ed3/docker/Dockerfile.app)
 - [docker/Dockerfile.docreader](https://github.com/Tencent/WeKnora/blob/10973ed3/docker/Dockerfile.docreader)
 - [docs/QA.md](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/QA.md?plain=1)
 - [docs/images/architecture.png](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/images/architecture.png)
 - [frontend/.dockerignore](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/.dockerignore)
 - [frontend/Dockerfile](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/Dockerfile)
 - [frontend/package-lock.json](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/package-lock.json)
 - [frontend/package.json](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/package.json)
 - [helm/Chart.yaml](https://github.com/Tencent/WeKnora/blob/10973ed3/helm/Chart.yaml)
 - [scripts/build_frontend_dist.sh](https://github.com/Tencent/WeKnora/blob/10973ed3/scripts/build_frontend_dist.sh)
 - [scripts/build_images.sh](https://github.com/Tencent/WeKnora/blob/10973ed3/scripts/build_images.sh)
 - [scripts/get_version.sh](https://github.com/Tencent/WeKnora/blob/10973ed3/scripts/get_version.sh)
 - [scripts/start_all.sh](https://github.com/Tencent/WeKnora/blob/10973ed3/scripts/start_all.sh)
 - [website-docs/01-getting-started/02-installation.md](https://github.com/Tencent/WeKnora/blob/10973ed3/website-docs/01-getting-started/02-installation.md?plain=1)
 - [website-docs/02-architecture/01-overview.md](https://github.com/Tencent/WeKnora/blob/10973ed3/website-docs/02-architecture/01-overview.md?plain=1)
 - [website-docs/05-clients/01-frontend.md](https://github.com/Tencent/WeKnora/blob/10973ed3/website-docs/05-clients/01-frontend.md?plain=1)
 - [website-docs/06-development/01-dev-guide.md](https://github.com/Tencent/WeKnora/blob/10973ed3/website-docs/06-development/01-dev-guide.md?plain=1)
 
  This page serves as a high-level overview for setting up, deploying, and initializing WeKnora. It outlines the core workflows from environment preparation and Docker Compose orchestration to initial system configuration and account registration.

 As a parent overview page, this document summarizes key setup phases. For comprehensive details, please refer to the dedicated child pages:

 
 - **System Requirements and Prerequisites**: For hardware, software, and external service requirements, see [System Requirements and Prerequisites](https://deepwiki.com/Tencent/WeKnora/2.1-system-requirements-and-prerequisites).
 - **Installation and Deployment**: For step-by-step installation instructions, profile selections, and environment configurations, see [Installation and Deployment](https://deepwiki.com/Tencent/WeKnora/2.2-installation-and-deployment).
 - **Quick Start Guide**: For a fast-track guide to running WeKnora and creating your first knowledge base, see [Quick Start Guide](https://deepwiki.com/Tencent/WeKnora/2.3-quick-start-guide).
 - **System Initialization and Configuration**: For setup wizards, model integrations, and Ollama configurations, see [System Initialization and Configuration](https://deepwiki.com/Tencent/WeKnora/2.4-system-initialization-and-configuration).
 
 
## Deployment Architecture

 WeKnora uses Docker Compose to manage multi-container services, supporting both production mode (all services containerized) and development mode (infrastructure containerized with local application execution). Observability leverages Langfuse OTLP/OTel tracing via the OpenTelemetry Go SDK [CHANGELOG.md61](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1#L61-L61)

 "Production Environment Stack"

 
```

```

 Sources: [website-docs/01-getting-started/02-installation.md16-38](https://github.com/Tencent/WeKnora/blob/10973ed3/website-docs/01-getting-started/02-installation.md?plain=1#L16-L38) [CHANGELOG.md61](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1#L61-L61)

 
| Service | Container Name | Ports | Profile | Description |
|---|---|---|---|---|
| frontend | WeKnora-frontend | 80 | default | Nginx serving Vue.js SPA and proxying API requests website-docs/01-getting-started/02-installation.md83 |
| app | WeKnora-app | 8080 | default | Main Go application backend website-docs/01-getting-started/02-installation.md84 |
| postgres | WeKnora-postgres | 5432 | default | PostgreSQL with pgvector (paradedb image) website-docs/01-getting-started/02-installation.md86 |
| redis | WeKnora-redis | 6379 | default | Redis for caching and stream management website-docs/01-getting-started/02-installation.md87 |
| docreader | WeKnora-docreader | 50051 | default | gRPC service for document parsing website-docs/01-getting-started/02-installation.md85 |
| minio | WeKnora-minio | 9000, 9001 | minio, full | Object storage (optional) website-docs/01-getting-started/02-installation.md96 |
| neo4j | WeKnora-neo4j | 7474, 7687 | neo4j, full | Graph database for GraphRAG (optional) website-docs/01-getting-started/02-installation.md97 |
| qdrant | WeKnora-qdrant | 6333, 6334 | qdrant, full | Vector database alternative (optional) website-docs/01-getting-started/02-installation.md98 |
| langfuse | langfuse-web | 3000 | langfuse | Observability via OTLP/OTel CHANGELOG.md61 website-docs/01-getting-started/02-installation.md103 |

 For comprehensive deployment instructions, see [Installation and Deployment](https://deepwiki.com/Tencent/WeKnora/2.2-installation-and-deployment).

 
## Getting Started Workflow

 The standard deployment and initialization pipeline transitions from repository checkout to fully operational application instances.

 "Setup and Initialization Flow"

 
```

```

 Sources: [README.md42-45](https://github.com/Tencent/WeKnora/blob/10973ed3/README.md?plain=1#L42-L45)

 For quick operational steps, see the [Quick Start Guide](https://deepwiki.com/Tencent/WeKnora/2.3-quick-start-guide).

 
## Environment Configuration Overview

 WeKnora relies on environment variables set in `.env` to configure operational parameters, database drivers, storage backends, and integrations.

 
| Category | Important Variables | Default | Description |
|---|---|---|---|
| Core System | GIN_MODE, LOG_LEVEL, AUTO_MIGRATE | release, debug, true | Framework mode and DB migration control |
| Storage | STORAGE_TYPE, LOCAL_STORAGE_BASE_DIR | local, /data/files | File storage backend configuration |
| Observability | LANGFUSE_ENABLED, LANGFUSE_HOST | - | Enable OTLP tracing for Langfuse website-docs/01-getting-started/02-installation.md103 |
| Database | DB_DRIVER, DB_HOST, DB_NAME | postgres, postgres, WeKnora | Relational database settings |
| Vector Store | RETRIEVE_DRIVER | postgres | Config for vector DB (Postgres, Qdrant, Milvus, etc.) |
| Model Integration | OLLAMA_SERVICE_URL | - | Endpoint for local Ollama service |

 For initialization details and model configurations, see [System Initialization and Configuration](https://deepwiki.com/Tencent/WeKnora/2.4-system-initialization-and-configuration).

 
## Service Startup Dependencies

 Services utilize health checks and explicit dependency constraints to guarantee proper initialization order.

 "Container Dependency Graph"

 
```

```

 Sources: [website-docs/01-getting-started/02-installation.md79-88](https://github.com/Tencent/WeKnora/blob/10973ed3/website-docs/01-getting-started/02-installation.md?plain=1#L79-L88)

 
## Bridging Natural Language to Code Entities

 
### Startup and Deployment Mapping

 This diagram associates natural language setup steps with specific code entities and files.

 "Deployment Step to Code Entity Mapping"

 
```

```

 Sources: [website-docs/01-getting-started/02-installation.md52-64](https://github.com/Tencent/WeKnora/blob/10973ed3/website-docs/01-getting-started/02-installation.md?plain=1#L52-L64) [README.md42-45](https://github.com/Tencent/WeKnora/blob/10973ed3/README.md?plain=1#L42-L45)

 
### Dependency Injection and Service Layer

 Mapping system components to the initialization logic within the `container` package.

 "Container Initialization Mapping"

 
```

```

 Sources: [internal/container/container.go116-137](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/container/container.go#L116-L137)

 
---

 **Sources:**
 [CHANGELOG.md61](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1#L61-L61)
 [README.md42-45](https://github.com/Tencent/WeKnora/blob/10973ed3/README.md?plain=1#L42-L45)
 [internal/container/container.go116-137](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/container/container.go#L116-L137)
 [website-docs/01-getting-started/02-installation.md16-38](https://github.com/Tencent/WeKnora/blob/10973ed3/website-docs/01-getting-started/02-installation.md?plain=1#L16-L38)
 [website-docs/01-getting-started/02-installation.md52-64](https://github.com/Tencent/WeKnora/blob/10973ed3/website-docs/01-getting-started/02-installation.md?plain=1#L52-L64)
 [website-docs/01-getting-started/02-installation.md79-88](https://github.com/Tencent/WeKnora/blob/10973ed3/website-docs/01-getting-started/02-installation.md?plain=1#L79-L88)
 [website-docs/01-getting-started/02-installation.md91-106](https://github.com/Tencent/WeKnora/blob/10973ed3/website-docs/01-getting-started/02-installation.md?plain=1#L91-L106)
