<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/OpenHarness · page 12 Configuration and State · fetched 2026-11-09 -->

# Configuration and State

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/openharness/auth/manager.py](src/openharness/auth/manager.py)
- [src/openharness/channels/impl/manager.py](src/openharness/channels/impl/manager.py)
- [src/openharness/channels/impl/telegram.py](src/openharness/channels/impl/telegram.py)
- [src/openharness/config/schema.py](src/openharness/config/schema.py)
- [src/openharness/config/settings.py](src/openharness/config/settings.py)
- [tests/test_channels/test_telegram_security.py](tests/test_channels/test_telegram_security.py)
- [tests/test_config/test_schema.py](tests/test_config/test_schema.py)
- [tests/test_config/test_settings.py](tests/test_config/test_settings.py)

</details>



The Configuration and State subsystem manages the persistence, resolution, and runtime tracking of OpenHarness settings and environment data. It provides a unified interface for accessing global configurations, project-specific overrides, and the current state of the application across different execution modes.

### System Overview

OpenHarness uses a hierarchical configuration strategy where settings are resolved from multiple sources with a defined precedence: CLI arguments, environment variables (e.g., `ANTHROPIC_API_KEY`, `OPENHARNESS_MODEL`), a global configuration file (`~/.openharness/settings.json`), and finally, hardcoded defaults [src/openharness/config/settings.py:3-8](). The system relies on a standardized directory structure to store logs, session data, and persistent caches.

### Configuration Precedence and Resolution

The following diagram illustrates how the `Settings` model is populated and how it maps to specific code entities within the `config` module.

**Configuration Resolution Flow**
```mermaid
graph TD
    subgraph "Natural Language Sources"
        [Defaults] --> ["Settings()"]
        ["settings.json"] --> ["load_settings()"]
        [EnvVars] --> ["_apply_env_overrides()"]
        [CLI_Args] --> ["merge_cli_overrides()"]
    end

    subgraph "Code Entity Space"
        ["Settings()"] --> [Settings_Class]
        ["load_settings()"] --> [Settings_Class]
        ["_apply_env_overrides()"] --> [Settings_Class]
        ["merge_cli_overrides()"] --> [Settings_Class]
        [Settings_Class] -- "resolve_auth()" --> [ResolvedAuth]
        [Settings_Class] -- "normalize_anthropic_model_name()" --> [Model_String]
    end

    [Settings_Class] -- "Defined in: src/openharness/config/settings.py" --> [Settings_Class]
```
Sources: [src/openharness/config/settings.py:3-8](), [src/openharness/config/settings.py:140-146](), [src/openharness/config/settings.py:180-193]()

---

### Settings Model

The `Settings` class is a Pydantic `BaseModel` that serves as the central schema for all application behaviors [src/openharness/config/settings.py:19-20](). It is composed of several specialized sub-models:

*   **PermissionSettings**: Controls `PermissionMode` (DEFAULT, PLAN, FULL_AUTO), allowed/denied tools, and path glob rules [src/openharness/config/settings.py:50-58]().
*   **MemorySettings**: Configures the persistent memory system, including entrypoint line limits, auto-compaction thresholds, and "dreaming" parameters [src/openharness/config/settings.py:60-75]().
*   **SandboxSettings**: Manages the `sandbox-runtime` integration, including OS-level network restrictions (`SandboxNetworkSettings`) and filesystem restrictions (`SandboxFilesystemSettings`) [src/openharness/config/settings.py:104-114]().
*   **ProviderProfile**: Defines named provider workflows (e.g., `claude-api`, `openai-compatible`) with specific API formats, auth sources, and model normalization logic [src/openharness/config/settings.py:124-138]().
*   **ChannelConfigs**: Defines settings for multi-platform messaging (Telegram, Slack, Discord, etc.) used primarily by the `ohmo` gateway [src/openharness/config/schema.py:102-115]().

For details on all fields and environment variable overrides, see [Settings Model](#12.1).

**Sources:** [src/openharness/config/settings.py:50-114](), [src/openharness/config/settings.py:196-212](), [src/openharness/config/schema.py:102-120]()

---

### File Paths and Directory Layout

OpenHarness follows XDG-like conventions for data storage. By default, it uses `~/.openharness/` as the base directory for global configuration and `~/.ohmo/` for personal agent workspaces.

The directory structure is partitioned into several functional areas, managed by the `paths.py` utility and the `AppStateStore`.

**Directory Structure and Code Mapping**
```mermaid
graph LR
    [BaseDir] -- "get_config_dir()" --> [Config_Dir]
    [Config_Dir] -- "get_config_file_path()" --> ["settings.json"]
    [BaseDir] -- "get_data_dir()" --> [Data_Dir]
    [Data_Dir] -- "get_sessions_dir()" --> [Sessions_Storage]
    [Data_Dir] -- "get_tasks_dir()" --> [Task_Logs]
    [Data_Dir] -- "get_cron_registry_path()" --> ["cron_jobs.json"]
    [CWD] -- "get_project_config_dir()" --> [Project_Dot_OpenHarness]
    [AppStateStore] -- "manages" --> [AppState]
```
Sources: [src/openharness/config/settings.py:3-8](), [src/openharness/auth/manager.py:88-93]()

For details on the filesystem layout and the `AppState` management, see [File Paths and Application State](#12.2).

---

### Sandbox Runtime

OpenHarness supports an optional `sandbox-runtime` (SRT) for secure tool execution. The configuration for this environment is governed by `SandboxSettings` [src/openharness/config/settings.py:104-114]().

*   **Capability Detection**: The system detects platform capabilities to determine sandbox availability.
*   **Restriction Enforcement**: Tools like `BashTool` check sandbox availability before execution. If the sandbox is enabled but unavailable, a `SandboxUnavailableError` is raised.
*   **Network and Filesystem**: OS-level restrictions can be applied to allowed/denied domains and read/write paths [src/openharness/config/settings.py:77-91]().
*   **Docker Integration**: Supports specific Docker settings including image names, CPU/Memory limits, and extra mounts [src/openharness/config/settings.py:93-102]().

For details on platform detection and sandbox enforcement, see [Sandbox Runtime](#12.3).

**Sources:** [src/openharness/config/settings.py:77-114](), [tests/test_config/test_settings.py:33-34]()

---

### Sub-pages

*   **[Settings Model](#12.1)**: Deep dive into the `Settings` Pydantic model, sub-models for `PermissionSettings`, `MemorySettings`, and `ProviderProfile`, and the logic for resolving API keys and merging CLI overrides.
*   **[File Paths and Application State](#12.2)**: Documentation of the directory layout, the persistent state stored in `.openharness/`, and the `AppStateStore` which maintains the live application state.
*   **[Sandbox Runtime](#12.3)**: Details on the `sandbox/` subsystem, including `SandboxSettings`, network/filesystem allow-lists, and integration with the `srt` CLI.

**Sources:** [src/openharness/config/settings.py:1-212](), [src/openharness/config/schema.py:1-120](), [src/openharness/auth/manager.py:71-115]()

---

