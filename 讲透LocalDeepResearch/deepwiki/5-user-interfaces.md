> 来源: [https://deepwiki.com/LearningCircuit/local-deep-research/5-user-interfaces](https://deepwiki.com/LearningCircuit/local-deep-research/5-user-interfaces)
> DeepWiki LearningCircuit/local-deep-research | Last indexed: 6 May 2026 (4a6a90

# User Interfaces

  Relevant source files 
 - [.github/CODEOWNERS](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/CODEOWNERS)
 - [README.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/README.md?plain=1)
 - [docker-compose.gpu.override.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docker-compose.gpu.override.yml)
 - [docs/CI_CD_INFRASTRUCTURE.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/CI_CD_INFRASTRUCTURE.md?plain=1)
 - [docs/SECURITY_REVIEW_PROCESS.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/SECURITY_REVIEW_PROCESS.md?plain=1)
 - [docs/SQLCIPHER_INSTALL.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/SQLCIPHER_INSTALL.md?plain=1)
 - [docs/decisions/0001-remove-detect-secrets.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/decisions/0001-remove-detect-secrets.md?plain=1)
 - [docs/developing.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/developing.md?plain=1)
 - [docs/docker-compose-guide.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/docker-compose-guide.md?plain=1)
 - [docs/install-pip.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/install-pip.md?plain=1)
 - [docs/installation.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/installation.md?plain=1)
 - [eslint.config.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/eslint.config.js)
 - [src/local_deep_research/__init__.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/__init__.py)
 - [src/local_deep_research/api/__init__.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/api/__init__.py)
 - [src/local_deep_research/config/llm_config.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/config/llm_config.py)
 - [src/local_deep_research/database/sqlcipher_compat.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/database/sqlcipher_compat.py)
 - [src/local_deep_research/news/__init__.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/news/__init__.py)
 - [src/local_deep_research/utilities/log_utils.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/utilities/log_utils.py)
 - [src/local_deep_research/web/app.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/app.py)
 - [src/local_deep_research/web/app_factory.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/app_factory.py)
 - [src/local_deep_research/web/models/database.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/models/database.py)
 - [src/local_deep_research/web/routes/api_routes.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/routes/api_routes.py)
 - [src/local_deep_research/web/routes/history_routes.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/routes/history_routes.py)
 - [src/local_deep_research/web/routes/research_routes.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/routes/research_routes.py)
 - [src/local_deep_research/web/routes/settings_routes.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/routes/settings_routes.py)
 - [src/local_deep_research/web/services/research_service.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/services/research_service.py)
 - [src/local_deep_research/web/services/socket_service.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/services/socket_service.py)
 - [src/local_deep_research/web/static/js/components/fallback/ui.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/components/fallback/ui.js)
 - [src/local_deep_research/web/static/js/components/history.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/components/history.js)
 - [src/local_deep_research/web/static/js/components/library_search.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/components/library_search.js)
 - [src/local_deep_research/web/static/js/components/logpanel.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/components/logpanel.js)
 - [src/local_deep_research/web/static/js/components/research.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/components/research.js)
 - [src/local_deep_research/web/static/js/components/settings.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/components/settings.js)
 - [src/local_deep_research/web/static/js/components/subscription-manager.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/components/subscription-manager.js)
 - [src/local_deep_research/web/static/js/pages/news.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/pages/news.js)
 - [src/local_deep_research/web/static/js/pages/subscriptions.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/pages/subscriptions.js)
 - [src/local_deep_research/web/static/js/research_form.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/research_form.js)
 - [src/local_deep_research/web/static/js/security/xss-protection.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/security/xss-protection.js)
 - [src/local_deep_research/web/static/js/services/socket.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/services/socket.js)
 - [src/local_deep_research/web/static/js/services/ui.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/services/ui.js)
 - [src/local_deep_research/web/static/js/utils/log-helpers.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/utils/log-helpers.js)
 - [src/local_deep_research/web/templates/pages/research.html](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/templates/pages/research.html)
 - [tests/config/test_llm_config_extra_coverage.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/config/test_llm_config_extra_coverage.py)
 - [tests/infrastructure_tests/test_xss_protection.test.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/infrastructure_tests/test_xss_protection.test.js)
 - [tests/js/utils/form-validation.test.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/js/utils/form-validation.test.js)
 - [tests/ui_tests/playwright/tests/theme-visual-regression.spec.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/ui_tests/playwright/tests/theme-visual-regression.spec.js)
 - [tests/web/services/test_socket_service_coverage.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/web/services/test_socket_service_coverage.py)
 - [tests/web/services/test_socket_service_extra_coverage.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/web/services/test_socket_service_extra_coverage.py)
 - [tests/web_services/test_socket_service.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/web_services/test_socket_service.py)
 
  This page provides a high-level overview of the multiple access patterns available in Local Deep Research: the **web UI**, the **HTTP REST API**, the **Python programmatic API**, **CLI tools**, and the **MCP server**. It serves as a map of entry points and their relationships to the application core.

 For the underlying request lifecycle once a query is submitted, see [Research Service and Execution Lifecycle](https://deepwiki.com/LearningCircuit/local-deep-research/3.3-research-service-and-execution-lifecycle). For settings that control what the UI exposes, see [Settings Management](https://deepwiki.com/LearningCircuit/local-deep-research/4.1-settings-management). Detailed documentation for each access pattern is in the child pages: [Web Interface](https://deepwiki.com/LearningCircuit/local-deep-research/5.1-web-interface), [REST API](https://deepwiki.com/LearningCircuit/local-deep-research/5.2-rest-api), [Python API](https://deepwiki.com/LearningCircuit/local-deep-research/5.3-python-api), and [CLI Tools and MCP Server](https://deepwiki.com/LearningCircuit/local-deep-research/5.4-cli-tools-and-mcp-server).

 
---

 
## Access Patterns Summary

 
| Pattern | Entry Point | Typical User |
|---|---|---|
| Web UI | http://localhost:5000 | Interactive research, configuration, history browsing, library management, and news monitoring. |
| HTTP REST API | POST /api/start | Automated scripts, external web integrations, monitoring tools. |
| Python API | local_deep_research.api | Enterprise Python applications, LangChain/LlamaIndex pipelines. |
| CLI | ldr, ldr-web, ldr-mcp | Server administration, local terminal research, AI IDE integration. |
| MCP Server | ldr-mcp | Claude Desktop/Code users via Model Context Protocol. |

 All patterns ultimately converge on the same `AdvancedSearchSystem` [src/local_deep_research/web/services/research_service.py24](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/services/research_service.py#L24-L24) and `IntegratedReportGenerator` [src/local_deep_research/web/services/research_service.py23](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/services/research_service.py#L23-L23) in the research core. Entry points are defined as console scripts in the project configuration. Authentication is required for the web UI and REST API to unlock per-user encrypted SQLCipher databases [src/local_deep_research/web/app_factory.py141-152](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/app_factory.py#L141-L152)

 
---

 
## Architecture: Access Patterns to Code Entities

 The following diagram bridges the gap between natural language interaction and the specific code entities that handle them.

 **Diagram: Access Patterns and Their Code-Level Entry Points**

 
```

```

 Sources: [src/local_deep_research/web/app_factory.py60-105](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/app_factory.py#L60-L105) [src/local_deep_research/web/routes/api_routes.py75-87](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/routes/api_routes.py#L75-L87) [src/local_deep_research/web/services/research_service.py58-60](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/services/research_service.py#L58-L60) [src/local_deep_research/web/routes/research_routes.py72-113](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/routes/research_routes.py#L72-L113)

 
---

 
## Web Interface

 The web interface is a Flask-rendered application [src/local_deep_research/web/app_factory.py105](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/app_factory.py#L105-L105) utilizing a Vite-built frontend. It is designed for privacy-first interaction with comprehensive research controls and a modern dark-themed UI.

 **Diagram: Frontend Components and Logic**

 
```

```

 Sources: [src/local_deep_research/web/routes/research_routes.py72-113](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/routes/research_routes.py#L72-L113) [src/local_deep_research/web/routes/settings_routes.py83](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/routes/settings_routes.py#L83-L83) [src/local_deep_research/web/static/js/components/research.js80-96](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/components/research.js#L80-L96) [src/local_deep_research/web/static/js/pages/news.js141-145](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/pages/news.js#L141-L145) [src/local_deep_research/web/static/js/components/logpanel.js38-70](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/components/logpanel.js#L38-L70)

 
### Key UI Features

 
 - **Research Form:** Supports "Quick Summary" and "Detailed Report" modes [src/local_deep_research/web/templates/pages/research.html52-69](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/templates/pages/research.html#L52-L69) It features a dynamic model provider selector that updates available models from providers like Ollama, OpenAI, and Anthropic [src/local_deep_research/web/static/js/components/research.js98-117](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/components/research.js#L98-L117)
 - **Settings Dashboard:** Manages complex configuration state across categories. It supports dual-mode submission: `AJAX/JSON` for modern browsers and traditional `POST` for accessibility [src/local_deep_research/web/routes/settings_routes.py8-38](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/routes/settings_routes.py#L8-L38)
 - **News Feed:** A specialized page for monitoring breaking news stories with semantic search capabilities [src/local_deep_research/web/static/js/pages/news.js82-88](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/pages/news.js#L82-L88) It uses an optimized table query template to synthesize news from real, verifiable sources [src/local_deep_research/web/static/js/pages/news.js91-138](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/pages/news.js#L91-L138)
 - **Log Panel:** A persistent component for monitoring research progress in real-time [src/local_deep_research/web/static/js/components/logpanel.js24-32](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/components/logpanel.js#L24-L32) It handles log entry display, filtering, and auto-scrolling for active research tasks [src/local_deep_research/web/static/js/components/logpanel.js113-115](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/components/logpanel.js#L113-L115)
 
 For details, see [Web Interface](https://deepwiki.com/LearningCircuit/local-deep-research/5.1-web-interface).

 
---

 
## REST API

 The REST API provides programmatic access to the research engine via standard HTTP methods. It is secured by the same `ProxyFix` and `SecureCookieMiddleware` as the web interface [src/local_deep_research/web/app_factory.py129-152](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/app_factory.py#L129-L152)

 
 - **Endpoint Control:** The API supports starting research [src/local_deep_research/web/routes/api_routes.py75-87](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/routes/api_routes.py#L75-L87) checking status [src/local_deep_research/web/routes/api_routes.py90-134](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/routes/api_routes.py#L90-L134) and terminating active processes [src/local_deep_research/web/routes/api_routes.py137-168](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/routes/api_routes.py#L137-L168)
 - **Concurrency Control:** API requests respect the `_global_research_semaphore` (defaulting to 10 concurrent tasks) to prevent system overload [src/local_deep_research/web/services/research_service.py37-40](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/services/research_service.py#L37-L40)
 - **Rate Limiting:** Protects endpoints using `flask-limiter`, with specific limits for settings updates [src/local_deep_research/web/routes/settings_routes.py69](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/routes/settings_routes.py#L69-L69) and file uploads [src/local_deep_research/web/routes/research_routes.py31-34](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/routes/research_routes.py#L31-L34)
 
 For details, see [REST API](https://deepwiki.com/LearningCircuit/local-deep-research/5.2-rest-api).

 
---

 
## Python API

 The Python API allows developers to integrate Local Deep Research directly into their Python applications. It is defined in the `local_deep_research.api` module.

 
 - **LDRClient:** The primary interface for programmatic interaction.
 - **Research Functions:** Provides convenience functions like `quick_query` and `quick_summary` for rapid integration.
 - **Thread Safety:** Ensures that background research tasks do not conflict with the main application thread through the `@thread_cleanup` decorator [src/local_deep_research/web/services/research_service.py20](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/services/research_service.py#L20-L20) and `SnapshotSettingsContext` [src/local_deep_research/web/services/research_service.py12](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/services/research_service.py#L12-L12)
 
 For details, see [Python API](https://deepwiki.com/LearningCircuit/local-deep-research/5.3-python-api).

 
---

 
## CLI Tools and MCP Server

 The project provides several command-line entry points for different operational modes.

 
 - **CLI Commands:** 
 - `ldr`: Direct command-line research execution.
 - `ldr-web`: Launches the Flask application factory using the custom `DiskSpoolingRequest` for memory-efficient file handling [src/local_deep_research/web/app_factory.py45-58](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/app_factory.py#L45-L58)
 - **MCP Server:** The `ldr-mcp` command starts a Model Context Protocol server. This allows AI agents (like Claude Desktop) to use Local Deep Research as a tool. It leverages the `MCPServer` to expose tools like `quick_research` and `generate_report` to external LLM agents.
 
 For details, see [CLI Tools and MCP Server](https://deepwiki.com/LearningCircuit/local-deep-research/5.4-cli-tools-and-mcp-server).

 Sources: [src/local_deep_research/web/app_factory.py122-136](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/app_factory.py#L122-L136) [src/local_deep_research/web/services/research_service.py37-40](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/services/research_service.py#L37-L40) [src/local_deep_research/web/routes/api_routes.py137-147](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/routes/api_routes.py#L137-L147) [src/local_deep_research/web/routes/settings_routes.py8-38](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/routes/settings_routes.py#L8-L38)
