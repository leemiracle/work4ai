<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/DeepTutor · page 2 Getting Started · fetched 2026-11-09 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/README/README_AR.md](assets/README/README_AR.md)
- [assets/README/README_CN.md](assets/README/README_CN.md)
- [assets/README/README_ES.md](assets/README/README_ES.md)
- [assets/README/README_FR.md](assets/README/README_FR.md)
- [assets/README/README_HI.md](assets/README/README_HI.md)
- [assets/README/README_JA.md](assets/README/README_JA.md)
- [assets/README/README_PL.md](assets/README/README_PL.md)
- [assets/README/README_PT.md](assets/README/README_PT.md)
- [assets/README/README_RU.md](assets/README/README_RU.md)
- [assets/README/README_TH.md](assets/README/README_TH.md)
- [deeptutor/__version__.py](deeptutor/__version__.py)
- [deeptutor/services/search/consolidation.py](deeptutor/services/search/consolidation.py)
- [deeptutor/services/search/providers/__init__.py](deeptutor/services/search/providers/__init__.py)
- [deeptutor/services/search/providers/google_browser_scraper.py](deeptutor/services/search/providers/google_browser_scraper.py)
- [deeptutor/services/search/providers/perplexity.py](deeptutor/services/search/providers/perplexity.py)
- [deeptutor/services/search/providers/serply.py](deeptutor/services/search/providers/serply.py)
- [deeptutor/services/search/providers/youcom.py](deeptutor/services/search/providers/youcom.py)
- [deeptutor_cli/init_wizard.py](deeptutor_cli/init_wizard.py)
- [tests/cli/test_init_wizard_probe.py](tests/cli/test_init_wizard_probe.py)
- [tests/services/search/test_search_providers.py](tests/services/search/test_search_providers.py)
- [web/public/provider-icons/youcom.ico](web/public/provider-icons/youcom.ico)

</details>



DeepTutor provides a streamlined onboarding experience designed to get your agent-native lifelong personalized tutoring workspace running locally or in production within minutes [README.md:4-4](). The installation process establishes the runtime environment, initializes directory structures, configures provider settings, and starts the integrated Next.js frontend and FastAPI backend stack [assets/README/README_CN.md:71-71]().

For detailed deployment, configuration, runtime launcher, and desktop app packaging instructions, see the child pages below:
- [Docker Deployment](#2.1) — Multi-stage builds, supervisord orchestration, docker-compose files, and containerization notes.
- [Configuration Guide](#2.2) — Environment variables, settings JSON files (`model_catalog`, `system`, `auth`, `interface`), and the runtime settings service.
- [Local Runtime and Launcher](#2.3) — `deeptutor start`/`stop` launcher, process management, port conflict resolution, and the proxy between Next.js and FastAPI.
- [Desktop App Packaging](#2.4) — Electron-style desktop preview, runtime sealing, Windows NSIS installer, and macOS signing/notarization.

---

## Prerequisites and Initialization

DeepTutor requires Python 3.11+ [README.md:30-30]() and Node.js 22+ for manual installations, or Docker/Podman for containerized setups [assets/README/README_CN.md:93-93](). The CLI initialization wizard configures necessary home directories and persistence paths under `DEEPTUTOR_HOME` or local `data/user/settings/` directories [assets/README/README_CN.md:71-71]().

### Initialization Architecture Mapping

```mermaid
graph TB
    subgraph "Natural_Language_Space"
        ["CLI_Init_Wizard"] -- "sets_up" --> ["Runtime_Home"]
        ["User_Environment"] -- "supplies" --> ["Environment_Variables"]
    end

    subgraph "Code_Entity_Space"
        ["deeptutor_cli.init_cmd.run_init"] -- "invokes" --> ["deeptutor.services.config.service"]
        ["Dockerfile"] -- "prepares" --> ["/app/data"]
        ["pyproject.toml"] -- "declares" --> ["typer_cli_commands"]
    end

    ["CLI_Init_Wizard"] --> ["deeptutor_cli.init_cmd.run_init"]
    ["Environment_Variables"] --> ["deeptutor.services.config.service"]
```

**Sources:** [assets/README/README_CN.md:71-71](), [README.md:30-30]()

---

## Deployment Overviews

### Docker and Podman Deployment
For containerized deployments, DeepTutor uses a multi-stage container build that packages the Next.js standalone frontend and FastAPI backend into a single image managed by `supervisord` [README.md:93-102](). Production deployments can utilize Docker Compose for orchestration alongside sidecars like vector stores and isolated sandbox runners [README.md:93-102](). For full details on container layers, image pulling, and containerization notes, see [Docker Deployment](#2.1).

**Sources:** [README.md:93-102]()

### Configuration and Environment Setup
Runtime behavior, model selection, authentication, and interface parameters are managed through configuration files under `data/user/settings` [assets/README/README_CN.md:71-71]() and various environment variables [assets/README/README_CN.md:71-71](). The runtime settings service automatically validates and loads models, system prompts, and provider catalogs [deeptutor/__version__.py:1-9](). For comprehensive documentation on JSON schemas, YAML settings, and environment variables, see [Configuration Guide](#2.2).

**Sources:** [assets/README/README_CN.md:71-71](), [deeptutor/__version__.py:1-9]()

### Local Runtime and Process Launcher
When running outside of containers, the `deeptutor start` and `stop` CLI commands manage local process lifecycles, handle port conflict resolution, manage frontend build caching, and proxy requests between Next.js and FastAPI [assets/README/README_CN.md:71-71](). For details on process management, port resolution, and self-update workers, see [Local Runtime and Launcher](#2.3).

**Sources:** [assets/README/README_CN.md:71-71]()

### Desktop App Packaging
For desktop environments, the `apps/desktop` packaging pipeline bundles Python, Node.js, and the complete learning workspace into standalone previews and installer packages for Windows and macOS [assets/README/README_CN.md:74-87](). For details on runtime sealing, NSIS installers, and signing workflows, see [Desktop App Packaging](#2.4).

**Sources:** [assets/README/README_CN.md:74-87]()

---

## System Component Mapping

```mermaid
graph LR
    subgraph "Client_Space"
        ["Browser_UI"]
        ["deeptutor_chat_REPL"]
    end

    subgraph "Application_Runtime"
        ["Next.js_Frontend"]
        ["FastAPI_Backend"]
        ["deeptutor_cli_main"]
    end

    subgraph "Persistence_Layer"
        ["DEEPTUTOR_HOME/data/user/settings"]
        ["DEEPTUTOR_HOME/data/knowledge_bases"]
        ["DEEPTUTOR_HOME/data/system"]
    end

    ["Browser_UI"] -- "HTTP" --> ["Next.js_Frontend"]
    ["Next.js_Frontend"] -- "proxy.ts" --> ["FastAPI_Backend"]
    ["deeptutor_cli_main"] -- "starts" --> ["FastAPI_Backend"]
    ["FastAPI_Backend"] -- "reads/writes" --> ["DEEPTUTOR_HOME/data/user/settings"]
    ["FastAPI_Backend"] -- "reads/writes" --> ["DEEPTUTOR_HOME/data/knowledge_bases"]
```

**Sources:** [assets/README/README_CN.md:71-71](), [deeptutor/__version__.py:1-9]()

---

