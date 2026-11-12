> 来源: [https://deepwiki.com/LearningCircuit/local-deep-research/2-getting-started](https://deepwiki.com/LearningCircuit/local-deep-research/2-getting-started)
> DeepWiki LearningCircuit/local-deep-research | Last indexed: 6 May 2026 (4a6a90

# Getting Started

  Relevant source files 
 - [.github/CODEOWNERS](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/CODEOWNERS)
 - [Dockerfile](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/Dockerfile)
 - [README.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/README.md?plain=1)
 - [cookiecutter-docker/cookiecutter.json](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/cookiecutter-docker/cookiecutter.json)
 - [cookiecutter-docker/hooks/post_gen_project.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/cookiecutter-docker/hooks/post_gen_project.py)
 - [cookiecutter-docker/hooks/pre_prompt.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/cookiecutter-docker/hooks/pre_prompt.py)
 - [cookiecutter-docker/{{cookiecutter.config_name}}/docker-compose.{{cookiecutter.config_name}}.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/cookiecutter-docker/{{cookiecutter.config_name}}/docker-compose.{{cookiecutter.config_name}}.yml)
 - [docker-compose.gpu.override.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docker-compose.gpu.override.yml)
 - [docker-compose.unraid.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docker-compose.unraid.yml)
 - [docker-compose.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docker-compose.yml)
 - [docs/CI_CD_INFRASTRUCTURE.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/CI_CD_INFRASTRUCTURE.md?plain=1)
 - [docs/CUSTOM_LLM_INTEGRATION.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/CUSTOM_LLM_INTEGRATION.md?plain=1)
 - [docs/SECURITY_REVIEW_PROCESS.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/SECURITY_REVIEW_PROCESS.md?plain=1)
 - [docs/SQLCIPHER_INSTALL.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/SQLCIPHER_INSTALL.md?plain=1)
 - [docs/analytics-dashboard.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/analytics-dashboard.md?plain=1)
 - [docs/architecture.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/architecture.md?plain=1)
 - [docs/architecture/DATABASE_SCHEMA.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/architecture/DATABASE_SCHEMA.md?plain=1)
 - [docs/architecture/OVERVIEW.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/architecture/OVERVIEW.md?plain=1)
 - [docs/decisions/0001-remove-detect-secrets.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/decisions/0001-remove-detect-secrets.md?plain=1)
 - [docs/decisions/0004-nullpool-for-sqlcipher.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/decisions/0004-nullpool-for-sqlcipher.md?plain=1)
 - [docs/deployment/unraid.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/deployment/unraid.md?plain=1)
 - [docs/developing.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/developing.md?plain=1)
 - [docs/developing/EXTENDING.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/developing/EXTENDING.md?plain=1)
 - [docs/docker-compose-guide.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/docker-compose-guide.md?plain=1)
 - [docs/env_configuration.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/env_configuration.md?plain=1)
 - [docs/faq.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/faq.md?plain=1)
 - [docs/features.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/features.md?plain=1)
 - [docs/install-pip.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/install-pip.md?plain=1)
 - [docs/installation.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/installation.md?plain=1)
 - [docs/library-and-rag.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/library-and-rag.md?plain=1)
 - [docs/mcp-server.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/mcp-server.md?plain=1)
 - [docs/search-engines.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/search-engines.md?plain=1)
 - [docs/troubleshooting.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/troubleshooting.md?plain=1)
 - [scripts/.gitkeep](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/scripts/.gitkeep)
 - [scripts/ollama_entrypoint.sh](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/scripts/ollama_entrypoint.sh)
 - [src/local_deep_research/database/sqlcipher_compat.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/database/sqlcipher_compat.py)
 - [src/local_deep_research/web/database/README.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/database/README.md?plain=1)
 - [tests/api_tests_with_login/puppeteer_config.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/api_tests_with_login/puppeteer_config.js)
 - [tests/database/test_post_login_settings_atomicity.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/database/test_post_login_settings_atomicity.py)
 - [tests/mcp/test_mcp_strategy.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/mcp/test_mcp_strategy.py)
 - [tests/ui_tests/puppeteer_config.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/ui_tests/puppeteer_config.js)
 - [tests/ui_tests/test_login_validation.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/ui_tests/test_login_validation.js)
 - [tests/web/routes/test_history_routes_extended.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/web/routes/test_history_routes_extended.py)
 - [unraid-templates/local-deep-research.xml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/unraid-templates/local-deep-research.xml)
 
  This page guides you through initial setup and running your first research query. It covers deployment method selection, installation, and basic configuration to get Local Deep Research (LDR) running on your system.

 **Scope**: This page provides quick-start instructions for all deployment methods. For detailed deployment configuration, see [Docker Deployment](https://deepwiki.com/LearningCircuit/local-deep-research/2.1-docker-deployment). For environment variable reference, see [Environment Configuration](https://deepwiki.com/LearningCircuit/local-deep-research/2.2-environment-configuration). For development from source, see [Local Development Setup](https://deepwiki.com/LearningCircuit/local-deep-research/2.3-local-development-setup).

 
---

 
## Choosing Your Deployment Method

 Local Deep Research supports multiple deployment methods. Choose based on your use case:

 
| Method | Best For | Complexity | Encryption |
|---|---|---|---|
| Docker Compose | Most users, production | Low | ✅ Built-in |
| Docker Run | Quick testing | Low | ✅ Built-in |
| pip install | Developers, integration | Medium | ✅ Pre-built wheels |
| Unraid | Home server users | Low | ✅ Built-in |

 
### Deployment Selection Logic

 "Natural Language Space" to "Code Entity Space" bridge:

 
 - `docker-compose.yml`: Base CPU configuration.
 - `docker-compose.gpu.override.yml`: NVIDIA hardware acceleration.
 - `sqlcipher3-binary`: Pre-built encrypted database drivers.
 - `ldr-web`: The Flask entry point [pyproject.toml111](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/pyproject.toml#L111-L111)
 
 
```

```

 **Sources**: [README.md46-91](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/README.md?plain=1#L46-L91) [docker-compose.yml1-17](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docker-compose.yml#L1-L17) [docs/docker-compose-guide.md7-24](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/docker-compose-guide.md?plain=1#L7-L24) [pyproject.toml111](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/pyproject.toml#L111-L111) [unraid-templates/local-deep-research.xml1-10](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/unraid-templates/local-deep-research.xml#L1-L10)

 
---

 
## Prerequisites

 
### For Docker Deployment

 
 - **Docker Engine**: 20.10+ (Docker Desktop on macOS/Windows) [Dockerfile4-52](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/Dockerfile#L4-L52)
 - **Docker Compose**: V2 (included with Docker Desktop) [docker-compose.yml1-17](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docker-compose.yml#L1-L17)
 - **System Memory**: 8GB minimum (16GB recommended for larger models) [docs/faq.md55-61](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/faq.md?plain=1#L55-L61)
 - **Disk Space**: ~10-20GB for images and models [docs/faq.md62-66](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/faq.md?plain=1#L62-L66)
 
 
### For pip Installation

 
 - **Python**: 3.12+ (supports up to 3.14.4) [pyproject.toml10](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/pyproject.toml#L10-L10) [Dockerfile4](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/Dockerfile#L4-L4)
 - **SQLCipher**: System library required for database encryption. [README.md87](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/README.md?plain=1#L87-L87) [docs/SQLCIPHER_INSTALL.md1-10](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/SQLCIPHER_INSTALL.md?plain=1#L1-L10)
 - **Node.js**: 24.x LTS (required for building the frontend from source) [Dockerfile23-44](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/Dockerfile#L23-L44)
 - **PDM**: Python package manager [pyproject.toml1-3](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/pyproject.toml#L1-L3) [Dockerfile51-52](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/Dockerfile#L51-L52)
 
 
---

 
## Quick Start: Docker Compose (Recommended)

 Docker Compose orchestrates the `local-deep-research` service, `ollama` (LLM), and `searxng` (search).

 
### Step 1: Download Configuration

 **Linux/macOS/Windows**:

 
```

```

 For NVIDIA GPU (Linux):

 
```

```

 **Sources**: [README.md67-81](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/README.md?plain=1#L67-L81) [docs/docker-compose-guide.md7-24](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/docker-compose-guide.md?plain=1#L7-L24)

 
### Step 2: Initialization Flow

 The first startup pulls the LLM model (default: `gemma3:12b`) [docs/docker-compose-guide.md66](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/docker-compose-guide.md?plain=1#L66-L66)

 
```

```

 **Sources**: [docker-compose.yml19-77](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docker-compose.yml#L19-L77) [cookiecutter-docker/{{cookiecutter.config_name}}/docker-compose.{{cookiecutter.config_name}}.yml61-103](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/cookiecutter-docker/{{cookiecutter.config_name}}/docker-compose.{{cookiecutter.config_name}}.yml#L61-L103) [scripts/ollama_entrypoint.sh25-42](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/scripts/ollama_entrypoint.sh#L25-L42)

 
### Step 3: Access Web Interface

 Open `http://localhost:5000` after ~30 seconds [README.md81](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/README.md?plain=1#L81-L81)

 
 - **Register**: Create your account. This process creates an encrypted database using `SQLCipher` and derives a key from your password [tests/ui_tests/puppeteer_config.js31-33](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/ui_tests/puppeteer_config.js#L31-L33)
 - **Login**: Access the dashboard. ⚠️ **Warning**: No password recovery exists due to the zero-knowledge encryption architecture [docs/SQLCIPHER_INSTALL.md105](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/SQLCIPHER_INSTALL.md?plain=1#L105-L105)
 
 
---

 
## Quick Start: Docker Run

 For minimal setup without a compose file:

 
```

```

 **Sources**: [README.md50-65](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/README.md?plain=1#L50-L65)

 
---

 
## Quick Start: pip Install

 
```

```

 
 - **Windows/macOS/Linux**: Includes pre-built SQLCipher wheels (`sqlcipher3-binary` or `sqlcipher3`) for major platforms [pyproject.toml85-87](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/pyproject.toml#L85-L87) [README.md87](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/README.md?plain=1#L87-L87)
 - **Unencrypted Fallback**: If encryption fails or is not desired for development, set `export LDR_BOOTSTRAP_ALLOW_UNENCRYPTED=true` to use standard SQLite [README.md89](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/README.md?plain=1#L89-L89) [docs/developing.md83-86](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/developing.md?plain=1#L83-L86)
 - **PDF Export**: Windows requires Pango [README.md88](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/README.md?plain=1#L88-L88)
 
 
---

 
## Running Your First Research Query

 
### Research Execution Lifecycle

 When you submit a query, the system follows this internal path:

 
```

```

 
 - **Submit**: Go to `http://localhost:5000/research`.
 - **Configure**: Select a strategy (e.g., `Standard`, `Academic`, or `langgraph-agent`) [README.md102-104](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/README.md?plain=1#L102-L104)
 - **Execute**: Monitor real-time logs via WebSockets.
 - **Result**: View the generated Markdown report with citations [README.md100](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/README.md?plain=1#L100-L100)
 
 **Sources**: [README.md93-116](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/README.md?plain=1#L93-L116) [docs/architecture.md1-20](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/architecture.md?plain=1#L1-L20)

 
---

 
## Basic Configuration

 
### Environment Overrides

 Environment variables starting with `LDR_` override and **lock** settings in the UI, making them read-only [docs/env_configuration.md27-29](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/env_configuration.md?plain=1#L27-L29) [docs/docker-compose-guide.md53-57](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/docker-compose-guide.md?plain=1#L53-L57)

 
| Variable | Description | Default |
|---|---|---|
| LDR_WEB_PORT | Internal server port | 5000 |
| LDR_DATA_DIR | Storage location | /data (Docker) |
| LDR_LLM_MODEL | Default model name | gemma3:12b |
| LDR_LLM_OLLAMA_URL | Ollama API endpoint | http://ollama:11434 |

 **Sources**: [docker-compose.yml55-77](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docker-compose.yml#L55-L77) [docs/docker-compose-guide.md57-65](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/docker-compose-guide.md?plain=1#L57-L65) [docs/env_configuration.md122-135](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/env_configuration.md?plain=1#L122-L135)

 
### External Providers

 To use cloud models like Claude or GPT-4, configure these in the UI or via env:

 
```

```

 **Sources**: [docker-compose.yml95-104](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docker-compose.yml#L95-L104) [docs/env_configuration.md71-77](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/env_configuration.md?plain=1#L71-L77)

 
---

 
## Next Steps

 
 - **[Docker Deployment](https://deepwiki.com/LearningCircuit/local-deep-research/2.1-docker-deployment)**: Deep dive into GPU setup, volume management, and `cookiecutter` configuration.
 - **[Environment Configuration](https://deepwiki.com/LearningCircuit/local-deep-research/2.2-environment-configuration)**: Full list of `LDR_*` variables and the bootstrap system.
 - **[Local Development Setup](https://deepwiki.com/LearningCircuit/local-deep-research/2.3-local-development-setup)**: How to build from source using `PDM`, manage Node.js assets, and run tests.
