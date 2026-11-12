> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/3.6-data-migration-and-versioning](https://deepwiki.com/thinkinaixyz/deepchat/3.6-data-migration-and-versioning)（Wayback 快照 2026-03-06）
> DeepWiki deepchat/3.6-data-migration-and-versioning

# Data Migration and Versioning

  Relevant source files 
 - [src/main/events.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/events.ts)
 - [src/main/index.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/index.ts)
 - [src/main/presenter/configPresenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/index.ts)
 - [src/main/presenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/index.ts)
 - [src/renderer/src/events.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/events.ts)
 - [src/shared/logger.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/shared/logger.ts)
 - [src/shared/presenter.d.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/shared/presenter.d.ts)
 
  This document describes the version-based migration system in `ConfigPresenter`, which ensures backward compatibility when upgrading DeepChat across versions. The system detects version changes at application startup, executes version-specific migrations to update configuration schemas, and delegates subsystem-specific upgrades to specialized helpers like `McpConfHelper`. For information about the provider and model database structure, see [Provider and Model Database](https://deepwiki.com/thinkinaixyz/deepchat/3.2-provider-and-model-database). For model configuration versioning, see [Model Configuration and Capabilities](https://deepwiki.com/thinkinaixyz/deepchat/3.3-model-configuration-and-capabilities).

 
## Purpose and Architecture

 The migration system in `ConfigPresenter` addresses several concerns:

 
 - **Schema evolution**: Configuration formats change across versions (e.g., storage location, key names, data structures)
 - **Provider changes**: Provider definitions, API types, and base URLs may need correction or migration
 - **Feature additions**: New features may require initializing default settings or migrating legacy data
 - **Backward compatibility**: Existing installations must upgrade seamlessly without data loss
 
 The system is implemented in `ConfigPresenter` with a central `migrateConfigData()` method that contains version-specific migration logic. The application version is stored in `ElectronStore` and compared on each startup.

 **Sources:** [src/main/presenter/configPresenter/index.ts62-93](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/index.ts#L62-L93) [src/main/presenter/configPresenter/index.ts241-247](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/index.ts#L241-L247)

 <old_str>

 
## Migration Execution Workflow

 
### Central Migration Method

 The `migrateConfigData(oldVersion)` method contains version-specific migration logic using version comparison. Each migration is guarded by a version check using the `compare-versions` library.

 **Title:** Migration Execution Sequence

 
```

```

 **Sources:** [src/main/presenter/configPresenter/index.ts241-247](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/index.ts#L241-L247) [src/main/presenter/configPresenter/index.ts325-476](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/index.ts#L325-L476)

 
### Version Comparison Logic

 Each migration uses `compare(oldVersion, targetVersion, '<')` to determine if the migration should run. This ensures migrations execute exactly once when upgrading through a specific version.

 
```

```

 The comparison operator `'<'` ensures the migration runs for any version strictly less than the target. If a user upgrades from 0.2.0 → 0.5.0, all intermediate migrations execute in order.

 **Sources:** [src/main/presenter/configPresenter/index.ts31](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/index.ts#L31-L31) [src/main/presenter/configPresenter/index.ts327-447](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/index.ts#L327-L447) </old_str> <new_str>

 
## Version Detection and Storage

 
### Application Version Tracking

 The `ConfigPresenter` stores the application version in `ElectronStore` under the `appVersion` key. On each startup, the stored version is compared against the current version obtained from `app.getVersion()`.

 **Title:** ConfigPresenter Version Detection Flow

 
```

```

 **Sources:** [src/main/presenter/configPresenter/index.ts131-132](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/index.ts#L131-L132) [src/main/presenter/configPresenter/index.ts241-247](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/index.ts#L241-L247)

 
### ElectronStore Schema

 The `ConfigPresenter` uses `ElectronStore<IAppSettings>` to persist application settings. The `appVersion` field tracks the last run version for migration detection.

 
| Store Key | Type | Purpose |
|---|---|---|
| appVersion | string | Last run application version (e.g., '0.3.5') |
| language | string | UI language setting |
| providers | LLM_PROVIDER[] | Provider configurations |
| closeToQuit | boolean | Window close behavior |
| proxyMode | string | Proxy configuration mode |
| customShortKey | ShortcutKeySetting | Custom keyboard shortcuts |
| default_system_prompt | string | Default system prompt text |
| hooksNotifications | HooksNotificationsSettings | Hooks and notifications config |
| ... | ... | Additional settings |

 **Sources:** [src/main/presenter/configPresenter/index.ts62-93](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/index.ts#L62-L93) [src/main/presenter/configPresenter/index.ts134-162](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/index.ts#L134-L162)

 
## Core Architecture

 
### ModelConfigHelper Version Tracking

 The `ModelConfigHelper` class manages model configurations with built-in version tracking. Each instance is initialized with the application version and maintains a metadata object in the configuration store.

 
```

```

 **Sources:** [src/main/presenter/configPresenter/modelConfig.ts19-31](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/modelConfig.ts#L19-L31) [src/main/presenter/configPresenter/modelConfig.ts33-43](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/modelConfig.ts#L33-L43) [src/main/presenter/configPresenter/modelConfig.ts160-167](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/modelConfig.ts#L160-L167)

 
### Configuration Source Tracking

 Each configuration entry is tagged with a `source` field indicating whether it was user-defined or provider-derived. This metadata determines persistence behavior during version migrations.

 
```

```

 **Sources:** [src/main/presenter/configPresenter/modelConfig.ts12-15](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/modelConfig.ts#L12-L15) [src/shared/presenter.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/shared/presenter.ts) (IModelConfig type definition)

 
## Specific Version Migrations

 
### Version 0.0.10: Model Storage Restructure

 Before version 0.0.10, model data was stored directly in `app-settings.json`. This migration moves model data to separate per-provider stores and extracts the `enabled` flag to independent status storage.

 **Title:** Model Storage Migration (v0.0.10)

 
```

```

 **Sources:** [src/main/presenter/configPresenter/index.ts336-392](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/index.ts#L336-L392)

 
### Version 0.0.17: Provider Removal

 This migration removes the obsolete `qwenlm` provider by filtering it from the providers array.

 
```

```

 **Sources:** [src/main/presenter/configPresenter/index.ts395-407](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/index.ts#L395-L407)

 
### Version 0.2.4: Minimax Base URL Correction

 Early versions had an incorrect `baseUrl` for the minimax provider. This migration corrects it to the proper API endpoint.

 
```

```

 **Sources:** [src/main/presenter/configPresenter/index.ts327-335](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/index.ts#L327-L335)

 
### Version 0.3.5: System Prompt Migration

 This migration handles the transition from a single `default_system_prompt` setting to a structured system prompts store with multiple named prompts.

 **Title:** System Prompt Migration (v0.3.5)

 
```

```

 **Sources:** [src/main/presenter/configPresenter/index.ts409-447](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/index.ts#L409-L447)

 
### Version 0.5.8: API Type Semantics Split

 This migration disambiguates `openai-compatible` and `openai` API types, splitting them into `openai-completions` and `openai-responses` to reflect different API endpoints.

 **Title:** OpenAI API Type Migration (v0.5.8)

 
```

```

 **Sources:** [src/main/presenter/configPresenter/index.ts449-476](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/index.ts#L449-L476)

 
## Provider-Specific Migrations

 
### Minimax Provider Format Migration

 The `migrateMinimaxProvider()` method handles a special case where the minimax provider was restructured from OpenAI-compatible format to Anthropic-compatible format. This migration runs independently of version checks.

 **Title:** Minimax Provider API Format Migration

 
```

```

 **Sources:** [src/main/presenter/configPresenter/index.ts478-508](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/index.ts#L478-L508)

 
### New Provider Addition

 When new providers are added to `DEFAULT_PROVIDERS`, the constructor automatically merges them into existing configurations without overwriting user settings.

 
```

```

 **Sources:** [src/main/presenter/configPresenter/index.ts252-260](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/index.ts#L252-L260)

 
## MCP Configuration Upgrades

 
### McpConfHelper Version Migration

 The `McpConfHelper` manages MCP server configurations in a separate `ElectronStore`. When `ConfigPresenter` detects a version change, it delegates MCP-specific migrations to `mcpConfHelper.onUpgrade(oldVersion)`.

 **Title:** MCP Configuration Upgrade Delegation

 
```

```

 MCP configuration upgrades may include:

 
 - Updating server command formats
 - Migrating environment variable structures
 - Updating NPM registry cache schemas
 - Correcting server transport configurations
 
 **Sources:** [src/main/presenter/configPresenter/index.ts246](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/index.ts#L246-L246) [src/main/presenter/configPresenter/mcpConfHelper.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/mcpConfHelper.ts) (referenced but not provided)

 
### Hooks and Notifications Configuration

 The `hooksNotifications` setting is initialized with a default configuration created by `createDefaultHooksNotificationsConfig()`. This ensures new installations have consistent default behavior.

 
```

```

 **Sources:** [src/main/presenter/configPresenter/index.ts160](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/index.ts#L160-L160) [src/main/presenter/configPresenter/index.ts52-60](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/index.ts#L52-L60)

 
## Migration Event Broadcasting

 
### Configuration Change Events

 When migrations modify configuration data, the `ConfigPresenter` broadcasts events through the `eventBus` to notify other components. This ensures UI and other presenters stay synchronized.

 **Title:** Migration Event Flow

 
```

```

 **Sources:** [src/main/presenter/configPresenter/index.ts519-532](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/index.ts#L519-L532) [src/main/presenter/configPresenter/index.ts537-540](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/index.ts#L537-L540) [src/main/events.ts12-47](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/events.ts#L12-L47)

 
### Provider Change Propagation

 The `CONFIG_EVENTS.PROVIDER_CHANGED` event triggers updates in `LLMProviderPresenter` to rebuild provider instances with the new configurations.

 
```

```

 **Sources:** [src/main/presenter/index.ts236-239](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/index.ts#L236-L239) [src/main/events.ts13](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/events.ts#L13-L13)

 
## Integration with Subsystem Helpers

 
### Delegation Pattern

 The `ConfigPresenter` uses a delegation pattern where specialized helper classes manage specific configuration domains. Each helper is initialized with references to the main store and methods.

 **Title:** ConfigPresenter Helper Architecture

 
```

```

 **Sources:** [src/main/presenter/configPresenter/index.ts118-126](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/index.ts#L118-L126) [src/main/presenter/configPresenter/index.ts164-231](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/index.ts#L164-L231)

 
### Model Configuration Versioning

 The `ModelConfigHelper` implements its own versioning system that is separate from but coordinated with the main application version. When the application version changes, model configurations are revalidated against the provider database. For detailed information on model configuration versioning, see [Model Configuration and Capabilities](https://deepwiki.com/thinkinaixyz/deepchat/3.3-model-configuration-and-capabilities).

 
```

```

 **Sources:** [src/main/presenter/configPresenter/index.ts220](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/index.ts#L220-L220) [src/main/presenter/configPresenter/index.ts34](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/index.ts#L34-L34)

 
## Version Migration Best Practices

 
### Adding New Migrations

 When adding a new version migration to `migrateConfigData()`, follow these patterns:

 
 - **Version Gate Pattern**: Use `compare(oldVersion, targetVersion, '<')` to guard migration logic
 - **Defensive Checks**: Verify data exists before accessing it
 - **Idempotency**: Ensure migrations can run multiple times safely
 - **Data Preservation**: Never delete user data without explicit backup
 
 
```

```

 **Sources:** [src/main/presenter/configPresenter/index.ts325-476](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/index.ts#L325-L476)

 
### Testing Migrations

 Migration logic should be tested by:

 
 - Creating a mock store with data from the old version
 - Initializing `ConfigPresenter` with the old version
 - Simulating version upgrade by creating a new instance with the new version
 - Verifying data was migrated correctly and user data was preserved
 
 **Sources:** Test patterns demonstrated in [src/main/presenter/configPresenter/index.ts325-508](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/index.ts#L325-L508)

 
## Summary

 The version migration system in `ConfigPresenter` provides:

 
 - **Automatic detection**: Version changes are detected on every application startup
 - **Sequential execution**: Migrations run in order for users upgrading across multiple versions
 - **Subsystem coordination**: Specialized helpers (MCP, model config, etc.) handle domain-specific migrations
 - **Event notification**: Configuration changes are broadcast to keep UI and other components synchronized
 - **Backward compatibility**: Legacy installations upgrade transparently without data loss
 
 The system ensures DeepChat can evolve its configuration schema while preserving user settings and maintaining a seamless upgrade experience. For model-specific configuration versioning, see [Model Configuration and Capabilities](https://deepwiki.com/thinkinaixyz/deepchat/3.3-model-configuration-and-capabilities). For MCP-specific configuration management, see [MCP Configuration Management](https://deepwiki.com/thinkinaixyz/deepchat/4.7-mcp-configuration-management).

 
## Summary of Key Mechanisms

 The version migration system implements the following guarantees:

 
 - **Version-scoped caching**: Provider-derived configurations are tied to the application version and invalidated on version changes
 - **User data persistence**: Explicitly user-defined configurations survive all version migrations
 - **Lazy regeneration**: Configurations are regenerated from the provider database on-demand after invalidation
 - **Legacy compatibility**: Pre-versioning stores are transparently migrated using the `isUserDefined` flag
 - **Atomic updates**: Version metadata updates are atomic with configuration changes to prevent inconsistent states
 
 The system balances three competing concerns: ensuring fresh provider database data, preserving user preferences, and maintaining backward compatibility.
