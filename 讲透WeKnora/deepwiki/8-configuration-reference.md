> 来源: [https://deepwiki.com/Tencent/WeKnora/8-configuration-reference](https://deepwiki.com/Tencent/WeKnora/8-configuration-reference)
> DeepWiki Tencent/WeKnora

# Configuration Reference

  Relevant source files 
 - [.env.example](https://github.com/Tencent/WeKnora/blob/10973ed3/.env.example)
 - [config/config.yaml](https://github.com/Tencent/WeKnora/blob/10973ed3/config/config.yaml)
 - [docker-compose.dev.yml](https://github.com/Tencent/WeKnora/blob/10973ed3/docker-compose.dev.yml)
 - [docker-compose.yml](https://github.com/Tencent/WeKnora/blob/10973ed3/docker-compose.yml)
 - [frontend/src/api/skill/index.ts](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/api/skill/index.ts)
 - [frontend/vite.config.ts](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/vite.config.ts)
 - [go.mod](https://github.com/Tencent/WeKnora/blob/10973ed3/go.mod)
 - [go.sum](https://github.com/Tencent/WeKnora/blob/10973ed3/go.sum)
 - [internal/config/config.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/config/config.go)
 - [internal/container/container.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/container/container.go)
 - [internal/handler/skill_handler.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/skill_handler.go)
 - [internal/types/retriever.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/retriever.go)
 - [scripts/dev.sh](https://github.com/Tencent/WeKnora/blob/10973ed3/scripts/dev.sh)
 
  This page serves as a high-level parent reference for all configuration options, environment variables, and deployment profiles in WeKnora. WeKnora relies on a layered configuration system that combines environment variables, static YAML configuration files, database-backed system settings, and tenant-level configurations.

 For detailed domain-specific settings, refer to the child pages:

 
 - [Environment Variables](https://deepwiki.com/Tencent/WeKnora/8.1-environment-variables)
 - [Agent and Conversation Configuration](https://deepwiki.com/Tencent/WeKnora/8.2-agent-and-conversation-configuration)
 - [Model Configuration and Integration](https://deepwiki.com/Tencent/WeKnora/8.3-model-configuration-and-integration)
 - [Document Processing Configuration](https://deepwiki.com/Tencent/WeKnora/8.4-document-processing-configuration)
 - [Retrieval Engine Configuration](https://deepwiki.com/Tencent/WeKnora/8.5-retrieval-engine-configuration)
 
 
---

 
## Configuration Architecture Overview

 WeKnora implements a centralized configuration loader powered by `viper` [internal/config/config.go14](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/config/config.go#L14-L14) which aggregates settings into a master `Config` struct [internal/config/config.go19-42](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/config/config.go#L19-L42) At application startup, configuration values are loaded, validated, and injected through the dependency injection container builder `container.BuildContainer()` [internal/container/container.go103-144](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/container/container.go#L103-L144)

 The precedence order for configuration resolution from highest to lowest priority is:

 
 - **Tenant-level Configuration**: Database overrides per tenant [internal/types/tenant.go86-125](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/tenant.go#L86-L125)
 - **System Settings**: Dynamically editable runtime overrides [internal/application/service/system_setting.go65-95](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/system_setting.go#L65-L95)
 - **Environment Variables**: Primary operational overrides (.env / OS environment) [.env.example1-25](https://github.com/Tencent/WeKnora/blob/10973ed3/.env.example#L1-L25)
 - **YAML Configuration Files**: Static defaults defined in `config/config.yaml` [config/config.yaml1-48](https://github.com/Tencent/WeKnora/blob/10973ed3/config/config.yaml#L1-L48)
 - **Code Defaults**: Hardcoded internal fallbacks in Go packages [internal/config/config.go44-79](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/config/config.go#L44-L79)
 
 
```

```

 Sources: [.env.example1-185](https://github.com/Tencent/WeKnora/blob/10973ed3/.env.example#L1-L185) [docker-compose.yml1-150](https://github.com/Tencent/WeKnora/blob/10973ed3/docker-compose.yml#L1-L150) [config/config.yaml1-48](https://github.com/Tencent/WeKnora/blob/10973ed3/config/config.yaml#L1-L48) [internal/config/config.go1-79](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/config/config.go#L1-L79) [internal/container/container.go103-144](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/container/container.go#L103-L144)

 
---

 
## Configuration Domains

 
### 1. Environment Variables

 Environment variables control container runtimes, database connections, object storage credentials, system flags, and external endpoints. For complete specifications, see [Environment Variables](https://deepwiki.com/Tencent/WeKnora/8.1-environment-variables).

 Sources: [.env.example1-185](https://github.com/Tencent/WeKnora/blob/10973ed3/.env.example#L1-L185) [docker-compose.yml1-150](https://github.com/Tencent/WeKnora/blob/10973ed3/docker-compose.yml#L1-L150)

 
### 2. Agent and Conversation Configuration

 Defines dialogue bounds, RAG parameters, summary controls, prompt templates, and agent loop execution timeouts. For details, see [Agent and Conversation Configuration](https://deepwiki.com/Tencent/WeKnora/8.2-agent-and-conversation-configuration).

 Sources: [internal/config/config.go44-123](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/config/config.go#L44-L123) [config/config.yaml6-39](https://github.com/Tencent/WeKnora/blob/10973ed3/config/config.yaml#L6-L39)

 
### 3. Model Configuration and Integration

 Covers declarations and tuning for LLMs, embedding models, VLMs, rerankers, and ASR engines from multiple providers, including builtin YAML declarations. For details, see [Model Configuration and Integration](https://deepwiki.com/Tencent/WeKnora/8.3-model-configuration-and-integration).

 Sources: [internal/config/config.go27](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/config/config.go#L27-L27) [config/config.yaml1-48](https://github.com/Tencent/WeKnora/blob/10973ed3/config/config.yaml#L1-L48)

 
### 4. Document Processing Configuration

 Controls document parsing engine parameters, DocReader connectivity (`DocReaderConfig`), MinerU/OpenDataLoader integration, and file type handling. For details, see [Document Processing Configuration](https://deepwiki.com/Tencent/WeKnora/8.4-document-processing-configuration).

 Sources: [internal/config/config.go81-87](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/config/config.go#L81-L87) [config/config.yaml40-48](https://github.com/Tencent/WeKnora/blob/10973ed3/config/config.yaml#L40-L48)

 
### 5. Retrieval Engine Configuration

 Manages the vector store driver (`VectorDatabaseConfig`), hybrid search weighting, and index settings across supported backends like PostgreSQL (`pgvector`), Qdrant, Milvus, Weaviate, Elasticsearch, Doris, SQLite, Tencent VectorDB, and OpenSearch. For details, see [Retrieval Engine Configuration](https://deepwiki.com/Tencent/WeKnora/8.5-retrieval-engine-configuration).

 Sources: [internal/types/retriever.go4-27](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/retriever.go#L4-L27) [internal/config/config.go89-92](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/config/config.go#L89-L92)

 
---

 
## Docker Compose Profiles

 WeKnora uses Docker Compose profiles to manage optional infrastructure components in development and production deployments [docker-compose.dev.yml51-225](https://github.com/Tencent/WeKnora/blob/10973ed3/docker-compose.dev.yml#L51-L225)

 
| Profile | Description |
|---|---|
| full | Starts all optional auxiliary services (MinIO, Qdrant, Neo4j, SearXNG) docker-compose.dev.yml51-225 |
| minio | Starts MinIO S3-compatible object storage docker-compose.dev.yml84-105 |
| qdrant | Starts Qdrant vector database docker-compose.dev.yml107-120 |
| milvus | Starts Milvus vector database docker-compose.dev.yml177-204 |
| neo4j | Starts Neo4j graph database for GraphRAG docker-compose.dev.yml205-224 |
| searxng | Starts SearXNG web search instance docker-compose.dev.yml38-81 |
| opensearch | Starts OpenSearch k-NN cluster docker-compose.dev.yml122-176 |
| odl-hybrid | Starts OpenDataLoader hybrid service for advanced parsing scripts/dev.sh241-245 |

 Sources: [docker-compose.dev.yml38-225](https://github.com/Tencent/WeKnora/blob/10973ed3/docker-compose.dev.yml#L38-L225) [scripts/dev.sh213-245](https://github.com/Tencent/WeKnora/blob/10973ed3/scripts/dev.sh#L213-L245)

 
---

 
## Bridging Natural Language Context to Code Entities

 
### Diagram 1: From Configuration Sources to the Application Container

 
```

```

 This diagram maps user-facing configurations to `config.LoadConfig()` and dependency injection registration inside `container.BuildContainer()` [internal/container/container.go103-144](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/container/container.go#L103-L144)

 Sources: [internal/container/container.go103-144](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/container/container.go#L103-L144) [internal/config/config.go1-42](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/config/config.go#L1-L42) [.env.example1-185](https://github.com/Tencent/WeKnora/blob/10973ed3/.env.example#L1-L185)

 
---

 
### Diagram 2: Mapping Configuration to Supported Retrieval Engines

 
```

```

 The vector store type specified in the configuration maps directly to `RetrieverEngineType` constants and initializes the corresponding repository adapters [internal/types/retriever.go4-27](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/retriever.go#L4-L27) [internal/container/container.go35-48](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/container/container.go#L35-L48)

 Sources: [internal/types/retriever.go1-27](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/retriever.go#L1-L27) [internal/container/container.go22-49](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/container/container.go#L22-L49)
