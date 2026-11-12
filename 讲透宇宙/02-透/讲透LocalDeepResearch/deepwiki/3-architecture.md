> 来源: [https://deepwiki.com/LearningCircuit/local-deep-research/3-architecture](https://deepwiki.com/LearningCircuit/local-deep-research/3-architecture)
> DeepWiki LearningCircuit/local-deep-research | Last indexed: 6 May 2026 (4a6a90

# Architecture

  Relevant source files 
 - [.github/CODEOWNERS](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/CODEOWNERS)
 - [README.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/README.md?plain=1)
 - [docker-compose.gpu.override.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docker-compose.gpu.override.yml)
 - [docker-compose.unraid.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docker-compose.unraid.yml)
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
 - [src/local_deep_research/__init__.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/__init__.py)
 - [src/local_deep_research/api/__init__.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/api/__init__.py)
 - [src/local_deep_research/config/llm_config.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/config/llm_config.py)
 - [src/local_deep_research/database/sqlcipher_compat.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/database/sqlcipher_compat.py)
 - [src/local_deep_research/news/__init__.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/news/__init__.py)
 - [src/local_deep_research/utilities/log_utils.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/utilities/log_utils.py)
 - [src/local_deep_research/web/app.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/app.py)
 - [src/local_deep_research/web/app_factory.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/app_factory.py)
 - [src/local_deep_research/web/database/README.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/database/README.md?plain=1)
 - [src/local_deep_research/web/models/database.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/models/database.py)
 - [src/local_deep_research/web/routes/api_routes.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/routes/api_routes.py)
 - [src/local_deep_research/web/routes/history_routes.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/routes/history_routes.py)
 - [src/local_deep_research/web/routes/research_routes.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/routes/research_routes.py)
 - [src/local_deep_research/web/routes/settings_routes.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/routes/settings_routes.py)
 - [src/local_deep_research/web/services/research_service.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/services/research_service.py)
 - [src/local_deep_research/web/services/socket_service.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/services/socket_service.py)
 - [src/local_deep_research/web/static/js/components/settings.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/components/settings.js)
 - [tests/config/test_llm_config_extra_coverage.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/config/test_llm_config_extra_coverage.py)
 - [tests/database/test_post_login_settings_atomicity.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/database/test_post_login_settings_atomicity.py)
 - [tests/mcp/test_mcp_strategy.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/mcp/test_mcp_strategy.py)
 - [tests/web/routes/test_history_routes_extended.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/web/routes/test_history_routes_extended.py)
 - [tests/web/services/test_socket_service_coverage.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/web/services/test_socket_service_coverage.py)
 - [tests/web/services/test_socket_service_extra_coverage.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/web/services/test_socket_service_extra_coverage.py)
 - [tests/web_services/test_socket_service.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/web_services/test_socket_service.py)
 - [unraid-templates/local-deep-research.xml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/unraid-templates/local-deep-research.xml)
 
  This document provides a comprehensive overview of Local Deep Research's system architecture, describing how major components interact to deliver AI-powered research capabilities. It covers the multi-layered design, component relationships, data flow patterns, and key architectural decisions that enable per-user data isolation, concurrent research execution, and extensible search strategies.

 For deployment-specific details, see [Docker Deployment](https://deepwiki.com/LearningCircuit/local-deep-research/2.1-docker-deployment) and [Production Configuration and Hardening](https://deepwiki.com/LearningCircuit/local-deep-research/9.3-production-configuration-and-hardening). For development setup and contribution guidelines, see [Development Guide](https://deepwiki.com/LearningCircuit/local-deep-research/7-development-guide). For user-facing interface details, see [User Interfaces](https://deepwiki.com/LearningCircuit/local-deep-research/5-user-interfaces).

 
---

 
## System Overview

 Local Deep Research implements a four-layer architecture: **User Interface Layer** (web UI, REST API, Python API, MCP server), **Application Layer** (Flask routes, service classes, queue processor), **Core Engine Layer** (search system, LLM integration, report generation), and **Data Layer** (per-user encrypted SQLCipher databases, FAISS vector stores).

 
### High-Level Component Diagram

 
```

```

 **Sources:** [src/local_deep_research/web/app_factory.py60-124](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/app_factory.py#L60-L124) [src/local_deep_research/web/services/socket_service.py14-131](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/services/socket_service.py#L14-L131)

 
---

 
## Flask Application Initialization

 The Flask application is created via `create_app()` in `app_factory.py`, which configures middleware, security headers, rate limiting, CSRF protection, and registers blueprints. The application uses a custom request class (`DiskSpoolingRequest`) to prevent memory exhaustion from large file uploads.

 
### Application Factory Flow

 
```

```

 Key initialization steps:

 
 - **Logging Setup** ([src/local_deep_research/web/app_factory.py67-91](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/app_factory.py#L67-L91)): Routes stdlib loggers (`werkzeug`, `apscheduler`) through `loguru` via `InterceptHandler`.
 - **Security Configuration** ([src/local_deep_research/web/app_factory.py126-140](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/app_factory.py#L126-L140)): Configures proxy support via `ProxyFix` and dynamic cookie security via `SecureCookieMiddleware`.
 - **Middleware Stack** ([src/local_deep_research/web/app_factory.py129-140](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/app_factory.py#L129-L140)): Middleware layers wrap the application to handle `X-Forwarded-For` and secure session cookies.
 - **Disk Spooling** ([src/local_deep_research/web/app_factory.py45-57](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/app_factory.py#L45-L57)): The `DiskSpoolingRequest` class ensures that files larger than 5MB are spooled to disk rather than held in memory.
 
 For details, see [Flask Web Application](https://deepwiki.com/LearningCircuit/local-deep-research/3.1-flask-web-application).

 **Sources:** [src/local_deep_research/web/app_factory.py45-140](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/app_factory.py#L45-L140)

 
---

 
## Research Execution Architecture

 Research execution follows a multi-stage pipeline coordinated by the `AdvancedSearchSystem`. The system uses a global semaphore `_global_research_semaphore` to limit concurrent research across all users and provides real-time updates via `SocketIOService`.

 
### Research Execution Flow

 
```

```

 **Key Components:**

 
 - **Dynamic Provider Loading** ([src/local_deep_research/config/llm_config.py159-191](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/config/llm_config.py#L159-L191)): The system dynamically fetches available LLM providers (Ollama, OpenAI, Anthropic, Google, etc.) using `get_available_providers`.
 - **Real-time Updates** ([src/local_deep_research/web/services/socket_service.py171-210](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/services/socket_service.py#L171-L210)): `SocketIOService` handles targeted emission of research progress to specific subscribers using unique research IDs.
 - **Concurrency Control** ([src/local_deep_research/web/services/research_service.py36-40](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/services/research_service.py#L36-L40)): A global semaphore `_global_research_semaphore` limits the total number of active research tasks server-wide.
 - **Throttled Emission** ([src/local_deep_research/web/services/research_service.py42-47](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/services/research_service.py#L42-L47)): Socket.IO emissions are throttled using `_EMIT_THROTTLE_SECONDS` to prevent UI lag during high-frequency research updates.
 
 For details, see [Research Service and Execution Lifecycle](https://deepwiki.com/LearningCircuit/local-deep-research/3.3-research-service-and-execution-lifecycle) and [Search System Architecture](https://deepwiki.com/LearningCircuit/local-deep-research/3.5-search-system-architecture).

 **Sources:** [src/local_deep_research/config/llm_config.py159-191](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/config/llm_config.py#L159-L191) [src/local_deep_research/web/services/socket_service.py171-210](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/services/socket_service.py#L171-L210) [src/local_deep_research/web/services/research_service.py36-60](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/services/research_service.py#L36-L60)

 
---

 
## Database Architecture and Per-User Isolation

 Local Deep Research uses per-user encrypted SQLCipher databases. Authentication is tied directly to the ability to decrypt the database file using a password-derived key.

 
### Database Connection Lifecycle

 
```

```

 **Isolation Strategy:**

 
 - **Per-User DBs**: Each user has a unique database file that remains encrypted at rest via SQLCipher.
 - **Session Context Management** ([src/local_deep_research/database/session_context.py19-20](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/database/session_context.py#L19-L20)): The system uses context managers to ensure database sessions are properly opened and closed within the request lifecycle or background threads.
 - **Cleanup Schedulers** ([src/local_deep_research/web/app.py107-120](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/app.py#L107-L120)): A periodic background task (`start_connection_cleanup_scheduler`) ensures idle database connections are closed to free file descriptors.
 - **Graceful Shutdown** ([src/local_deep_research/web/app.py132-140](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/app.py#L132-L140)): The system registers `atexit` handlers to close all database connections via `db_manager.close_all_databases()` when the server stops.
 
 For details, see [Database Architecture and Security](https://deepwiki.com/LearningCircuit/local-deep-research/3.8-database-architecture-and-security) and [Thread-Safe Settings and Context Management](https://deepwiki.com/LearningCircuit/local-deep-research/3.4-thread-safe-settings-and-context-management).

 **Sources:** [src/local_deep_research/web/app.py107-160](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/app.py#L107-L160) [src/local_deep_research/database/session_context.py19-62](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/database/session_context.py#L19-L62)

 
---

 
## Settings and Configuration System

 The application uses a robust settings management system that supports environment variable overrides, per-user database persistence, and thread-safe snapshots.

 
 - **Dual-Mode Submission** ([src/local_deep_research/web/routes/settings_routes.py6-38](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/routes/settings_routes.py#L6-L38)): Settings can be saved via AJAX/JSON (primary) or traditional POST (fallback for accessibility).
 - **Validation** ([src/local_deep_research/web/routes/settings_routes.py158-202](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/routes/settings_routes.py#L158-L202)): Settings are validated against their defined types (checkbox, number, slider, select) and constraints (min/max).
 - **Snapshots** ([src/local_deep_research/web/services/research_service.py12-13](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/services/research_service.py#L12-L13)): Before a research task starts, a `SnapshotSettingsContext` is created to ensure the research uses a consistent set of parameters even if the user changes settings mid-execution.
 - **Namespace Validation** ([src/local_deep_research/web/routes/settings_routes.py93-131](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/routes/settings_routes.py#L93-L131)): New settings are validated against `ALLOWED_SETTING_PREFIXES` and `BLOCKED_SETTING_PREFIXES` to prevent unauthorized configuration changes.
 
 For details, see [Thread-Safe Settings and Context Management](https://deepwiki.com/LearningCircuit/local-deep-research/3.4-thread-safe-settings-and-context-management) and [Settings Management](https://deepwiki.com/LearningCircuit/local-deep-research/4.1-settings-management).

 **Sources:** [src/local_deep_research/web/routes/settings_routes.py6-202](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/routes/settings_routes.py#L6-L202) [src/local_deep_research/web/services/research_service.py12-13](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/services/research_service.py#L12-L13)

 
---

 
## Frontend Build and Design System

 The frontend is built with a focus on local-first accessibility and consistent styling.

 
 - **Vite-based architecture**: Handles asset bundling and CSS management.
 - **LDR Prefix**: CSS classes use an `ldr-` prefix to provide a clean namespace.
 - **Dynamic Dropdowns** ([src/local_deep_research/web/static/js/components/settings.js59-103](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/components/settings.js#L59-L103)): Custom dropdowns for model and search engine selection are rendered dynamically to handle provider-specific options.
 - **Theme System**: Themes (system, dark, sepia) are applied before content visibility to prevent flashes of unstyled content.
 
 
### UI Layout Structure

 
| Component | Route | Responsibility |
|---|---|---|
| Research Form | / | Main research interface src/local_deep_research/web/routes/research_routes.py88-92 |
| History Viewer | /history | View past research sessions src/local_deep_research/web/routes/history_routes.py33-37 |
| Settings Dashboard | /settings | Configuration management src/local_deep_research/web/routes/research_routes.py117-121 |
| Research Details | /details/<id> | Detailed progress and logs src/local_deep_research/web/routes/research_routes.py95-99 |

 For details, see [Frontend Build System](https://deepwiki.com/LearningCircuit/local-deep-research/3.2-frontend-build-system).

 **Sources:** [src/local_deep_research/web/routes/research_routes.py88-121](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/routes/research_routes.py#L88-L121) [src/local_deep_research/web/routes/history_routes.py33-37](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/routes/history_routes.py#L33-L37) [src/local_deep_research/web/static/js/components/settings.js59-103](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/components/settings.js#L59-L103)

 
---

 
## Report Generation and Export

 Reports are synthesized into Markdown and can be exported to various formats using the `IntegratedReportGenerator`.

 
 - **Export Formats** ([src/local_deep_research/web/services/research_service.py83-128](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/services/research_service.py#L83-L128)): The `export_report_to_memory` function uses an `ExporterRegistry` to support formats like PDF, LaTeX, ODT, and RIS.
 - **Citation Handling** ([src/local_deep_research/web/services/research_service.py64-80](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/services/research_service.py#L64-L80)): The `CitationFormatter` manages various citation modes (number hyperlinks, domain hyperlinks, etc.) based on user settings like `report.citation_format`.
 - **Think-Tag Removal** ([src/local_deep_research/config/llm_config.py10](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/config/llm_config.py#L10-L10)): The system automatically cleanses LLM output of internal "thought" tokens before synthesis using `remove_think_tags`.
 
 For details, see [Report Generation and Export System](https://deepwiki.com/LearningCircuit/local-deep-research/3.9-report-generation-and-export-system).

 **Sources:** [src/local_deep_research/web/services/research_service.py64-128](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/services/research_service.py#L64-L128) [src/local_deep_research/config/llm_config.py10](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/config/llm_config.py#L10-L10)

 
---

 This architecture enables Local Deep Research to provide privacy-focused, concurrent AI research capabilities while maintaining security through per-user database isolation and robust request handling. For implementation details of specific subsystems, see the child pages (3.1-3.9).
