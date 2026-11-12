> 来源: [https://deepwiki.com/LearningCircuit/local-deep-research/9-deployment-strategies](https://deepwiki.com/LearningCircuit/local-deep-research/9-deployment-strategies)
> DeepWiki LearningCircuit/local-deep-research | Last indexed: 6 May 2026 (4a6a90

# Deployment Strategies

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
 
  
## Purpose and Scope

 This document provides an overview of deployment strategies for Local Deep Research (LDR) across different environments and platforms. It covers container-based deployment (Docker and Docker Compose), multi-architecture support, GPU acceleration, and the CI/CD pipeline that ensures secure, reproducible builds.

 For detailed Docker Compose configuration, see [Docker Compose Deployment](https://deepwiki.com/LearningCircuit/local-deep-research/9.1-docker-compose-deployment). For GPU setup, see [GPU-Accelerated Deployment](https://deepwiki.com/LearningCircuit/local-deep-research/9.2-gpu-accelerated-deployment). For production security practices, see [Production Configuration and Hardening](https://deepwiki.com/LearningCircuit/local-deep-research/9.3-production-configuration-and-hardening).

 
## Deployment Options

 Local Deep Research supports several primary deployment methods, each suited to different use cases:

 
| Method | Use Case | Complexity | Encryption Support | Dependencies Bundled |
|---|---|---|---|---|
| Docker Compose | Production, self-hosting | Low | Yes (built-in) | Yes (Ollama, SearXNG) |
| Docker Run | Quick testing, single-user | Medium | Yes (built-in) | No (manual setup) |
| pip Install | Development, integration | High | Yes (via wheels) | No |
| Unraid | Home server (NAS) | Low | Yes (built-in) | Yes (via template) |

 **Recommended**: Docker Compose for most users. It bundles all dependencies into a single orchestrated stack [docker-compose.yml19-132](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docker-compose.yml#L19-L132)

 Sources: [README.md50-91](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/README.md?plain=1#L50-L91) [docs/docker-compose-guide.md5-27](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/docker-compose-guide.md?plain=1#L5-L27) [docker-compose.yml1-17](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docker-compose.yml#L1-L17)

 
## Multi-Stage Container Build

 The production container is built using a multi-stage `Dockerfile` that optimizes for both testing and production deployment:

 Title: LDR Docker Build Lifecycle (Code Entities)

 
```

```

 
### Stage Responsibilities:

 
 - **`builder-base`**: Base stage with system dependencies shared by all builds, including `libsqlcipher-dev`, `sqlcipher`, and Node.js 24.x [Dockerfile4-45](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/Dockerfile#L4-L45) It pins critical tools like `pdm==2.26.2` and `playwright==1.58.0` [Dockerfile51-52](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/Dockerfile#L51-L52)
 - **`builder`**: Production dependency installation. Runs `npm ci`, `npm run build` for the frontend (Vite), and `pdm install --prod` for the Python backend [Dockerfile84-100](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/Dockerfile#L84-L100)
 - **`ldr-test`**: Testing infrastructure used in CI. Includes Chromium, Playwright, and XVFB for UI and accessibility tests [Dockerfile105-196](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/Dockerfile#L105-L196)
 - **`ldr`**: Final production image. Minimal footprint, runs as a non-root `ldruser` (UID 1000) [Dockerfile229-283](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/Dockerfile#L229-L283)
 
 Sources: [Dockerfile1-283](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/Dockerfile#L1-L283)

 
## Container Privilege Model

 The production container implements a defense-in-depth privilege model to minimize the attack surface:

 Title: LDR Container Security Escalation/De-escalation (System Flow)

 
```

```

 The container drops all capabilities (`cap_drop: ALL`) and uses `setpriv` to irreversibly switch to a non-privileged user [cookiecutter-docker/{{cookiecutter.config_name}}/docker-compose.{{cookiecutter.config_name}}.yml37-48](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/cookiecutter-docker/{{cookiecutter.config_name}}/docker-compose.{{cookiecutter.config_name}}.yml#L37-L48) The entrypoint script handles necessary root-level tasks like directory ownership before de-escalating [Dockerfile245-256](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/Dockerfile#L245-L256)

 Sources: [Dockerfile229-283](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/Dockerfile#L229-L283) [cookiecutter-docker/{{cookiecutter.config_name}}/docker-compose.{{cookiecutter.config_name}}.yml37-48](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/cookiecutter-docker/{{cookiecutter.config_name}}/docker-compose.{{cookiecutter.config_name}}.yml#L37-L48)

 
## Docker Compose Orchestration

 Docker Compose orchestrates three primary services on a shared network:

 
 - **`local-deep-research`**: The main Flask web application [docker-compose.yml20-173](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docker-compose.yml#L20-L173)
 - **`ollama`**: Local LLM inference engine [docker-compose.yml175-201](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docker-compose.yml#L175-L201)
 - **`searxng`**: Privacy-focused meta search engine [docker-compose.yml203-209](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docker-compose.yml#L203-L209)
 
 Title: LDR Service Architecture (Docker Space)

 
```

```

 Sources: [docker-compose.yml19-218](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docker-compose.yml#L19-L218) [docs/docker-compose-guide.md41-50](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/docker-compose-guide.md?plain=1#L41-L50) [cookiecutter-docker/{{cookiecutter.config_name}}/docker-compose.{{cookiecutter.config_name}}.yml1-128](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/cookiecutter-docker/{{cookiecutter.config_name}}/docker-compose.{{cookiecutter.config_name}}.yml#L1-L128)

 
## Override Pattern for GPU Support

 GPU acceleration uses Docker Compose's override pattern. This allows the same base configuration to work on all platforms while opting into hardware acceleration where available.

 
 - **NVIDIA GPU**: Handled via `docker-compose.gpu.override.yml` using the `nvidia` driver and `gpu` capabilities [docs/docker-compose-guide.md15-25](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/docker-compose-guide.md?plain=1#L15-L25) [docker-compose.yml10-13](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docker-compose.yml#L10-L13)
 - **AMD GPU**: Supported via `rocm` images and device passthrough (`/dev/kfd`, `/dev/dri`) [cookiecutter-docker/{{cookiecutter.config_name}}/docker-compose.{{cookiecutter.config_name}}.yml63-98](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/cookiecutter-docker/{{cookiecutter.config_name}}/docker-compose.{{cookiecutter.config_name}}.yml#L63-L98)
 - **Cookiecutter Detection**: The `cookiecutter-docker` system includes logic in `pre_prompt.py` to detect GPU types via `check_gpu_linux` and `check_gpu_windows` [cookiecutter-docker/hooks/pre_prompt.py27-90](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/cookiecutter-docker/hooks/pre_prompt.py#L27-L90)
 
 Sources: [docs/docker-compose-guide.md15-25](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/docker-compose-guide.md?plain=1#L15-L25) [cookiecutter-docker/{{cookiecutter.config_name}}/docker-compose.{{cookiecutter.config_name}}.yml63-98](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/cookiecutter-docker/{{cookiecutter.config_name}}/docker-compose.{{cookiecutter.config_name}}.yml#L63-L98) [cookiecutter-docker/hooks/pre_prompt.py27-90](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/cookiecutter-docker/hooks/pre_prompt.py#L27-L90) [docker-compose.yml10-13](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docker-compose.yml#L10-L13)

 
## Multi-Architecture Support

 LDR supports both `amd64` and `arm64` architectures. The Docker build process utilizes `builder-base` to handle platform-specific SQLCipher requirements:

 
 - **Architecture Detection**: PDM automatically selects the correct Python binding (e.g., `sqlcipher3-binary` for x86_64 Linux vs building from source for ARM64) [docs/SQLCIPHER_INSTALL.md21-25](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/SQLCIPHER_INSTALL.md?plain=1#L21-L25)
 - **Buildx Support**: Docker images are published with multi-arch manifests for `amd64` and `arm64` [README.md24](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/README.md?plain=1#L24-L24)
 
 Sources: [Dockerfile11-45](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/Dockerfile#L11-L45) [docs/SQLCIPHER_INSTALL.md21-25](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/SQLCIPHER_INSTALL.md?plain=1#L21-L25) [README.md24](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/README.md?plain=1#L24-L24)

 
## Build and Release Pipeline

 The CI/CD pipeline enforces rigorous security gates before publishing:

 
 - **Security Scanning**: Includes CodeQL, Semgrep, and other static analysis tools to maintain OSSF Scorecard compliance [README.md17-25](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/README.md?plain=1#L17-L25) [docs/CI_CD_INFRASTRUCTURE.md90-109](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/CI_CD_INFRASTRUCTURE.md?plain=1#L90-L109)
 - **Container Security**: Scans for vulnerabilities (Grype, Dockle) and ensures non-root execution [Dockerfile229-283](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/Dockerfile#L229-L283) [docs/CI_CD_INFRASTRUCTURE.md100-101](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/CI_CD_INFRASTRUCTURE.md?plain=1#L100-L101)
 - **Automated Testing**: Runs unit tests via `pytest` and UI tests via `Puppeteer` in the `ldr-test` stage [Dockerfile105-196](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/Dockerfile#L105-L196) [docs/CI_CD_INFRASTRUCTURE.md81-87](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/CI_CD_INFRASTRUCTURE.md?plain=1#L81-L87)
 
 Sources: [Dockerfile105-283](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/Dockerfile#L105-L283) [docs/CI_CD_INFRASTRUCTURE.md1-154](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/CI_CD_INFRASTRUCTURE.md?plain=1#L1-L154) [README.md17-25](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/README.md?plain=1#L17-L25)

 
## Platform-Specific Considerations

 
 - **Unraid**: Deployment is supported via the Docker Compose Manager plugin and dedicated templates [docker-compose.yml8](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docker-compose.yml#L8-L8) [docker-compose.unraid.yml1-50](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docker-compose.unraid.yml#L1-L50)
 - **Windows/macOS**: Supported via Docker Desktop; use `host.docker.internal` to reach services running on the host machine (like LM Studio) [docker-compose.yml26-30](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docker-compose.yml#L26-L30)
 - **Headless CI**: `puppeteer_config.js` is tuned for resource-constrained CI environments, including a 10-minute protocol timeout for encrypted DB initialization [tests/ui_tests/puppeteer_config.js27-43](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/ui_tests/puppeteer_config.js#L27-L43)
 
 Sources: [docs/docker-compose-guide.md1-110](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/docker-compose-guide.md?plain=1#L1-L110) [tests/ui_tests/puppeteer_config.js27-43](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/ui_tests/puppeteer_config.js#L27-L43) [docker-compose.yml26-30](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docker-compose.yml#L26-L30) [docker-compose.unraid.yml1-50](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docker-compose.unraid.yml#L1-L50)
