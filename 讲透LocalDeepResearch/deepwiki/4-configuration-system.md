> 来源: [https://deepwiki.com/LearningCircuit/local-deep-research/4-configuration-system](https://deepwiki.com/LearningCircuit/local-deep-research/4-configuration-system)
> DeepWiki LearningCircuit/local-deep-research | Last indexed: 6 May 2026 (4a6a90

# Configuration System

  Relevant source files 
 - [docs/BENCHMARKING.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/BENCHMARKING.md?plain=1)
 - [docs/CONFIGURATION.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/CONFIGURATION.md?plain=1)
 - [package-lock.json](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/package-lock.json)
 - [package.json](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/package.json)
 - [src/local_deep_research/__init__.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/__init__.py)
 - [src/local_deep_research/__version__.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/__version__.py)
 - [src/local_deep_research/advanced_search_system/questions/browsecomp_question.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/advanced_search_system/questions/browsecomp_question.py)
 - [src/local_deep_research/advanced_search_system/questions/flexible_browsecomp_question.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/advanced_search_system/questions/flexible_browsecomp_question.py)
 - [src/local_deep_research/advanced_search_system/strategies/langgraph_agent_strategy.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/advanced_search_system/strategies/langgraph_agent_strategy.py)
 - [src/local_deep_research/advanced_search_system/strategies/topic_organization_strategy.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/advanced_search_system/strategies/topic_organization_strategy.py)
 - [src/local_deep_research/advanced_search_system/tools/fetch/__init__.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/advanced_search_system/tools/fetch/__init__.py)
 - [src/local_deep_research/advanced_search_system/tools/fetch/prompts.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/advanced_search_system/tools/fetch/prompts.py)
 - [src/local_deep_research/api/__init__.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/api/__init__.py)
 - [src/local_deep_research/benchmarks/models/__init__.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/benchmarks/models/__init__.py)
 - [src/local_deep_research/config/llm_config.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/config/llm_config.py)
 - [src/local_deep_research/database/migrations/versions/0009_default_fetch_mode_summary.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/database/migrations/versions/0009_default_fetch_mode_summary.py)
 - [src/local_deep_research/defaults/default_settings.json](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/defaults/default_settings.json)
 - [src/local_deep_research/news/__init__.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/news/__init__.py)
 - [src/local_deep_research/search_system_factory.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/search_system_factory.py)
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
 - [src/local_deep_research/web/static/js/components/settings.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/components/settings.js)
 - [src/local_deep_research/web/static/js/mobile-navigation.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/mobile-navigation.js)
 - [src/local_deep_research/web/static/js/security/url-validator.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/security/url-validator.js)
 - [src/local_deep_research/web/static/js/services/formatting.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/services/formatting.js)
 - [tests/advanced_search_system/tools/test_fetch_modes.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/advanced_search_system/tools/test_fetch_modes.py)
 - [tests/config/test_llm_config_extra_coverage.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/config/test_llm_config_extra_coverage.py)
 - [tests/database/test_migration_0009_default_fetch_mode.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/database/test_migration_0009_default_fetch_mode.py)
 - [tests/infrastructure_tests/test_urls.test.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/infrastructure_tests/test_urls.test.js)
 - [tests/settings/golden_master_settings.json](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/settings/golden_master_settings.json)
 - [tests/settings/test_settings_defaults_integrity.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/settings/test_settings_defaults_integrity.py)
 - [tests/strategies/test_langgraph_agent_strategy.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/strategies/test_langgraph_agent_strategy.py)
 - [tests/web/services/test_socket_service_coverage.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/web/services/test_socket_service_coverage.py)
 - [tests/web/services/test_socket_service_extra_coverage.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/web/services/test_socket_service_extra_coverage.py)
 - [tests/web_services/test_socket_service.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/web_services/test_socket_service.py)
 - [vite.config.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/vite.config.js)
 
  The Configuration System provides hierarchical, user-scoped configuration management for Local Deep Research. It implements a five-tier precedence system (Locked > Bootstrap > Environment > Database > Defaults) with type coercion, validation, and administrative locking capabilities. Settings are stored in per-user encrypted SQLCipher databases with thread-safe snapshot access for background research threads.

 For details on the underlying management architecture, see [Settings Management](https://deepwiki.com/LearningCircuit/local-deep-research/4.1-settings-management). For LLM provider-specific configuration, see [LLM Provider Configuration](https://deepwiki.com/LearningCircuit/local-deep-research/4.2-llm-provider-configuration). For search engine configuration, see [Search Engine Configuration](https://deepwiki.com/LearningCircuit/local-deep-research/4.3-search-engine-configuration). For library and RAG parameters, see [Library and Collection Settings](https://deepwiki.com/LearningCircuit/local-deep-research/4.4-library-and-collection-settings).

 
---

 
## Configuration Hierarchy and Precedence

 Local Deep Research uses a five-tier configuration system where settings can be defined in multiple locations with explicit precedence rules. The `SettingsManager` resolves these tiers in descending order of priority.

 **Diagram: Settings Priority Resolution Flow**

 
```

```

 **Sources:** [src/local_deep_research/settings/manager.py188-214](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/settings/manager.py#L188-L214) [docs/CONFIGURATION.md1-25](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/CONFIGURATION.md?plain=1#L1-L25) [src/local_deep_research/defaults/default_settings.json1-15](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/defaults/default_settings.json#L1-L15)

 
### Five-Tier Precedence Rules

 The precedence order (highest to lowest) ensures that administrative locks and environmental requirements always supersede user preferences:

 
 - **Locked Settings**: Keys defined in the `LDR_LOCKED_SETTINGS` environment variable. These are read-only in the UI and **must** have a corresponding `LDR_*` environment variable value [docs/CONFIGURATION.md14-25](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/CONFIGURATION.md?plain=1#L14-L25)
 - **Bootstrap Settings**: Environment-only settings required before the database is initialized, such as `LDR_BOOTSTRAP_DATABASE_URL` or `LDR_BOOTSTRAP_ENCRYPTION_KEY` [docs/CONFIGURATION.md27-58](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/CONFIGURATION.md?plain=1#L27-L58)
 - **Environment Variables**: Overrides using the `LDR_<SETTING_KEY>` format (e.g., `LDR_APP_DEBUG` for `app.debug`). The system converts keys to uppercase and replaces dots with underscores [docs/CONFIGURATION.md6-12](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/CONFIGURATION.md?plain=1#L6-L12)
 - **Database Settings**: Per-user preferences stored in the encrypted `Setting` table of the user's database [src/local_deep_research/database/models/__init__.py11-16](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/database/models/__init__.py#L11-L16) [src/local_deep_research/web/routes/settings_routes.py148-155](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/routes/settings_routes.py#L148-L155)
 - **Default JSON**: The baseline configuration defined in `default_settings.json` [src/local_deep_research/defaults/default_settings.json1-199](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/defaults/default_settings.json#L1-L199)
 
 
---

 
## SettingsManager and Type Coercion

 The `SettingsManager` class provides the primary interface for configuration access. It handles type coercion from strings (from env/DB) to Python objects based on the `ui_element` metadata defined in the schema.

 **Diagram: Configuration Entity Mapping**

 
```

```

 **Sources:** [src/local_deep_research/settings/manager.py188-214](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/settings/manager.py#L188-L214) [src/local_deep_research/web/routes/settings_routes.py171-180](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/routes/settings_routes.py#L171-L180)

 
### Key Coercion Logic

 The system uses `get_typed_setting_value` to ensure data integrity across the stack:

 
 - **Checkboxes**: Coerced to `bool` using `parse_boolean`, which follows HTML checkbox semantics (presence = True, explicit "false"/"off" = False) [src/local_deep_research/settings/manager.py29-92](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/settings/manager.py#L29-L92)
 - **Numbers/Sliders**: Coerced to `int` or `float` using `_parse_number` [src/local_deep_research/settings/manager.py95-100](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/settings/manager.py#L95-L100)
 - **JSON/Multiselect**: Parsed from string representations into Python dictionaries or lists using `_parse_json_value` or `_parse_multiselect` [src/local_deep_research/settings/manager.py103-143](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/settings/manager.py#L103-L143)
 
 
---

 
## Configuration Categories

 The system categorizes settings to manage the array of research parameters. These categories are defined in the `default_settings.json` metadata.

 
| Category | Purpose | Example Key |
|---|---|---|
| App Interface | Web server, UI themes, and concurrency limits | app.port, app.max_concurrent_researches |
| LLM Parameters | Model selection, provider config, and API keys | llm.provider, llm.model |
| Search Parameters | Search engine API keys and query lengths | search.tool, app.max_user_query_length |
| Research Strategy | Strategy selection and iteration parameters | search.search_strategy |
| Report Generation | Output formatting and citation styles | report.citation_format |

 **Sources:** [src/local_deep_research/defaults/default_settings.json2-150](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/defaults/default_settings.json#L2-L150) [tests/settings/golden_master_settings.json1-155](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/settings/golden_master_settings.json#L1-L155)

 
---

 
## Thread Safety and Snapshots

 Research processes do not query the database for settings at runtime to avoid database contention and ensure consistency. Instead, they receive a **Settings Snapshot** created at the start of the research task.

 
### Snapshot Mechanism

 The `SnapshotSettingsContext` is used during research execution to provide a consistent view of settings for the duration of a thread [src/local_deep_research/web/services/research_service.py12-13](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/services/research_service.py#L12-L13) This is critical for maintaining integrity when settings are changed in the UI while a research task is already running.

 
### Thread-Local Context

 The system uses `get_setting_from_snapshot` to retrieve values from the current thread's context [src/local_deep_research/config/llm_config.py25-28](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/config/llm_config.py#L25-L28) If a snapshot is not present, it typically raises a `NoSettingsContextError`.

 For details on thread-safe management, see [Settings Management](https://deepwiki.com/LearningCircuit/local-deep-research/4.1-settings-management).

 
---

 
## Related Pages

 
 - [Settings Management](https://deepwiki.com/LearningCircuit/local-deep-research/4.1-settings-management) — Detailed class structures, validation logic, and the `env_registry`.
 - [LLM Provider Configuration](https://deepwiki.com/LearningCircuit/local-deep-research/4.2-llm-provider-configuration) — Specifics on provider availability checks and context window rules.
 - [Search Engine Configuration](https://deepwiki.com/LearningCircuit/local-deep-research/4.3-search-engine-configuration) — Adaptive rate limiting and engine-specific configuration.
 - [Library and Collection Settings](https://deepwiki.com/LearningCircuit/local-deep-research/4.4-library-and-collection-settings) — Vector store parameters and library storage modes.
 
 **Sources:** [src/local_deep_research/settings/manager.py1-214](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/settings/manager.py#L1-L214) [docs/CONFIGURATION.md1-116](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/CONFIGURATION.md?plain=1#L1-L116) [src/local_deep_research/config/llm_config.py194-220](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/config/llm_config.py#L194-L220)
