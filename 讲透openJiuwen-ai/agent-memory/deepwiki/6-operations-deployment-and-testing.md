<!-- source: DeepWiki mcp.deepwiki.com · repo openJiuwen-ai/agent-memory · page 6 Operations, Deployment and Testing · fetched 2026-11-02 -->

# Operations, Deployment and Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deploy/.env.example](deploy/.env.example)
- [deploy/Dockerfile](deploy/Dockerfile)
- [deploy/deploy.sh](deploy/deploy.sh)
- [deploy/docker-compose.yml](deploy/docker-compose.yml)

</details>



This page covers the operations, deployment assets, documentation framework, and test infrastructure for the JiuwenMemory (`agent-memory`) codebase. As a parent page, it provides a high-level overview of how the service is packaged, containerized, configured, and validated, while delegating deep technical specifics to dedicated child pages.

```
+-------------------------------------------------------------------------------------------------+
|                               6. Operations, Deployment and Testing                              |
+-------------------------------------------------------------------------------------------------+
         |                                           |                                   |
         v                                           v                                   v
+-----------------------------+             +-------------------------------+   +-----------------------------+
| 6.1 Deployment              |             | 6.2 Testing Strategy          |   | 6.3 Documentation & License |
| (deploy/Dockerfile,         |             | (tests/unit_tests/,           |   | (docs/en, docs/zh,          |
|  deploy/docker-compose.yml, |             |  conftest fixtures,           |   |  README bilingual pair,     |
|  deploy/deploy.sh,          |             |  store integration tests)     |   |  open-source notice)        |
|  deploy/.env.example)       |             |                               |   |                             |
+-----------------------------+             +-------------------------------+   +-----------------------------+
```

Sources:
- `deploy/Dockerfile`
- `deploy/docker-compose.yml`
- `deploy/deploy.sh`
- `deploy/env.example`

---

## 6.1 Deployment

The deployment framework is centered around containerization assets located in the `deploy/` directory [deploy/Dockerfile:1-60](). It supports deploying the Python FastAPI memory engine as an independent microservice that can communicate with Java management platforms (such as `spring-ai-ascend`) over a shared Docker bridge network [deploy/docker-compose.yml:1-70]().

Key components of the deployment architecture include:
- **`Dockerfile`**: A multi-stage Python 3.11 slim image definition that installs optional extras (`[chromadb,sqlite,gaussdb,elasticsearch,server]`), configures a non-root `app` user, and exposes the `memory-server` entry point on port `8000` [deploy/Dockerfile:11-60]().
- **`docker-compose.yml`**: Defines the `agent-memory` service configuration, volume mapping for persistent data (`memory_data`), environment variables for model providers and storage adapters, and the `agent-memory-net` bridge network [deploy/docker-compose.yml:1-70]().
- **`deploy.sh`**: An automated shell script that handles pre-flight `.env` checks, container teardown, image building using Docker BuildKit, container startup with port mapping, and health check validation via `/health` [deploy/deploy.sh:1-83]().
- **`.env.example`**: A comprehensive configuration template covering service bindings, embedding and LLM provider parameters, API authentication tokens, and storage backend types (`KV_STORE_TYPE`, `DB_STORE_TYPE`, `VECTOR_STORE_TYPE`) [deploy/.env.example:1-62]().

For detailed configuration variables, step-by-step startup instructions, and environment templates for both the engine and platform, see [Deployment](#6.1).

Sources:
- `deploy/Dockerfile:1-61`
- `deploy/docker-compose.yml:1-71`
- `deploy/deploy.sh:1-84`
- `deploy/.env.example:1-63`

---

## 6.2 Testing Strategy

The test suite validates correctness across storage abstractions, server endpoints, and core engine lifecycles. It is organized under the `tests/` directory and relies heavily on modular fixtures and configuration mocks.

Testing layers include:
- **Server Endpoint Tests**: FastAPI routing and middleware tests verifying authentication, payload validation, and error handling.
- **Conftest Fixtures**: Shared pytest fixtures providing isolated database instances, mock LLM clients, and temporary storage directories.
- **Core Engine Tests**: Verification of the `LongTermMemory` singleton lifecycle, memory managers, and extraction/generation pipelines.
- **Store Integration Tests**: End-to-end validation of vector indices, relational database backends, and simple key-value stores.

For details on test layouts, fixture definitions, and execution commands, see [Testing Strategy](#6.2).

Sources:
- `deploy/Dockerfile:1-61`

---

## 6.3 Documentation and Licensing

The project maintains a bilingual documentation and licensing footprint to support global developers and enterprise deployments.

The documentation assets comprise:
- **API Documentation (`docs/en` and `docs/zh`)**: Comprehensive guides and reference documentation translated into English and Chinese.
- **Bilingual README Pair**: Project root documentation providing quick-start instructions, architecture summaries, and contribution guidelines in both languages.
- **Open-Source Notice and License**: Licensing headers and legal terms governing the usage and redistribution of the codebase.

For details on documentation structure, API spec locations, and licensing terms, see [Documentation and Licensing](#6.3).

Sources:
- `deploy/Dockerfile:31-31`

---

