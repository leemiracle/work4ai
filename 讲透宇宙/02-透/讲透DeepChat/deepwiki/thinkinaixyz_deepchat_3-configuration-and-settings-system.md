> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/3-configuration-and-settings-system](https://deepwiki.com/thinkinaixyz/deepchat/3-configuration-and-settings-system)（Wayback 快照 2025-10-07）
> DeepWiki deepchat/3-configuration-and-settings-system

# Configuration and Settings System

  Relevant source files 
 - [src/main/events.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/events.ts)
 - [src/main/presenter/configPresenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts)
 - [src/main/presenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/index.ts)
 - [src/renderer/src/components/settings/BuiltinKnowledgeSettings.vue](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/components/settings/BuiltinKnowledgeSettings.vue)
 - [src/renderer/src/events.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/events.ts)
 - [src/renderer/src/i18n/en-US/settings.json](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/i18n/en-US/settings.json)
 - [src/renderer/src/i18n/fa-IR/settings.json](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/i18n/fa-IR/settings.json)
 - [src/renderer/src/i18n/fr-FR/settings.json](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/i18n/fr-FR/settings.json)
 - [src/renderer/src/i18n/ja-JP/settings.json](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/i18n/ja-JP/settings.json)
 - [src/renderer/src/i18n/ko-KR/settings.json](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/i18n/ko-KR/settings.json)
 - [src/renderer/src/i18n/ru-RU/settings.json](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/i18n/ru-RU/settings.json)
 - [src/renderer/src/i18n/zh-CN/settings.json](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/i18n/zh-CN/settings.json)
 - [src/renderer/src/i18n/zh-HK/settings.json](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/i18n/zh-HK/settings.json)
 - [src/renderer/src/i18n/zh-TW/settings.json](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/i18n/zh-TW/settings.json)
 - [src/renderer/src/stores/settings.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/stores/settings.ts)
 - [src/shared/presenter.d.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/shared/presenter.d.ts)
 
  The Configuration and Settings System manages all application configuration, user preferences, and persistent settings in DeepChat. It provides a centralized configuration management layer that coordinates between the main process (backend) and renderer process (frontend), ensuring consistent state synchronization across the application.

 This system handles provider configurations, model settings, application preferences, MCP server configurations, and user interface customizations. The architecture is built around `ElectronStore` for persistence, `ConfigPresenter` for backend management, and `useSettingsStore` for frontend state synchronization.

 For information about specific LLM provider configurations, see page 3.2 Provider and Model Configuration. For MCP-specific configuration details, see page 6.4 MCP Configuration System.

 
## Architecture Overview

 The Configuration and Settings System follows a presenter pattern with event-driven synchronization between the main and renderer processes. The system is built around `ConfigPresenter` as the central configuration authority and `useSettingsStore` as the frontend state manager.

 
### Core Configuration Architecture

 
#### Configuration System Component Diagram

 
```

```

 Sources: [src/main/presenter/configPresenter/index.ts91-192](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts#L91-L192) [src/renderer/src/stores/settings.ts19-46](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/stores/settings.ts#L19-L46) [src/main/events.ts11-38](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/events.ts#L11-L38)

 
## ElectronStore Persistence Layer

 The storage system uses multiple `ElectronStore` instances to organize different types of configuration data. Each store is created with specific schemas, default values, and file paths in the user data directory.

 
### Storage Initialization and Structure

 The `ConfigPresenter` constructor initializes all storage instances with their respective configurations:

 
```

```

 Sources: [src/main/presenter/configPresenter/index.ts106-160](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts#L106-L160) [src/main/presenter/configPresenter/index.ts201-214](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts#L201-L214)

 
#### ElectronStore Storage Hierarchy

 
```

```

 Sources: [src/main/presenter/configPresenter/index.ts92-96](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts#L92-L96) [src/main/presenter/configPresenter/index.ts194-199](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts#L194-L199) [src/main/presenter/configPresenter/index.ts101-105](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts#L101-L105)

 
### Key Storage Components

 
| Storage Component | Interface | Purpose | File Location |
|---|---|---|---|
| this.store | ElectronStore<IAppSettings> | Main application settings, providers, proxy config, feature flags | app-settings.json |
| this.providersModelStores | Map<string, ElectronStore<IModelStore>> | Per-provider model lists and custom models | provider_models/models_{providerId}.json |
| this.customPromptsStore | ElectronStore<{ prompts: Prompt[] }> | User-defined custom prompts | custom_prompts.json |
| this.systemPromptsStore | ElectronStore<{ prompts: SystemPrompt[] }> | System prompt templates | system_prompts.json |
| this.modelStatusCache | Map<string, boolean> | Runtime cache for model enable/disable state | Memory only |
| this.customPromptsCache | Prompt[] \| null | Runtime cache for custom prompts | Memory only |

 The `IAppSettings` interface includes:

 
 - `language`: Application language setting
 - `providers`: Array of `LLM_PROVIDER` configurations
 - `closeToQuit`: Exit behavior preference
 - `proxyMode`: Proxy configuration ('system' | 'none' | 'custom')
 - `customProxyUrl`: Custom proxy address
 - `artifactsEffectEnabled`, `searchPreviewEnabled`, `contentProtectionEnabled`: Feature toggles
 - `fontSizeLevel`: UI font size preference
 - `loggingEnabled`, `copyWithCotEnabled`, `soundEnabled`: Additional feature flags
 - `appVersion`: Used for data migration triggers
 
 Sources: [src/main/presenter/configPresenter/index.ts42-66](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts#L42-L66) [src/main/presenter/configPresenter/index.ts68-73](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts#L68-L73)

 
### Key Storage Components

 
| Storage Component | Purpose | Schema | File Location |
|---|---|---|---|
| ElectronStore<IAppSettings> | Main application settings | IAppSettings interface | app-settings.json |
| ElectronStore<IModelStore> | Provider model data | {models: MODEL_META[], custom_models: MODEL_META[]} | provider_models/models_{providerId}.json |
| Custom Prompts Store | User-defined prompts | {prompts: Prompt[]} | custom_prompts.json |
| System Prompts Store | System prompt templates | {prompts: SystemPrompt[]} | system_prompts.json |
| Model Status Cache | Runtime model enable/disable state | Map<string, boolean> | Memory only |

 Sources: [src/main/presenter/configPresenter/index.ts42-66](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts#L42-L66) [src/main/presenter/configPresenter/index.ts68-73](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts#L68-L73)

 
## Configuration Flow Patterns

 The settings management follows a unidirectional data flow with event-driven synchronization to maintain consistency between the main and renderer processes. All configuration changes originate from the renderer process and are persisted by the main process.

 
### Standard Configuration Update Flow

 
```

```

 Sources: [src/renderer/src/stores/settings.ts872-909](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/stores/settings.ts#L872-L909) [src/main/presenter/configPresenter/index.ts403-429](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts#L403-L429) [src/main/eventbus/index.ts1-50](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/eventbus/index.ts#L1-L50)

 
### Configuration Initialization Flow

 At application startup, the settings store initializes by loading all configuration from the main process:

 
```

```

 Sources: [src/renderer/src/stores/settings.ts295-380](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/stores/settings.ts#L295-L380)

 
### Settings Store API

 The `useSettingsStore` provides reactive state management with the following key operations:

 
| Category | Method | Purpose | Backend Delegation |
|---|---|---|---|
| Provider Management | updateProviderConfig(providerId, updates) | Atomic provider configuration updates | configP.updateProviderAtomic(providerId, updates) |
| Provider Management | updateProviderStatus(providerId, enable) | Enable/disable provider | updateProviderConfig(providerId, { enable }) |
| Provider Management | addCustomProvider(provider) | Add custom provider | configP.addProviderAtomic(provider) |
| Provider Management | removeProvider(providerId) | Delete provider | configP.removeProviderAtomic(providerId) |
| Model Status | updateModelStatus(providerId, modelId, enabled) | Enable/disable individual models | llmP.updateModelStatus(providerId, modelId, enabled) |
| Custom Models | addCustomModel(providerId, model) | Add user-defined models | llmP.addCustomModel(providerId, model) |
| Custom Models | removeCustomModel(providerId, modelId) | Remove custom model | configP.removeCustomModel(providerId, modelId) |
| Custom Models | updateCustomModel(providerId, modelId, updates) | Update custom model properties | llmP.updateCustomModel(providerId, modelId, updates) |
| Search Engines | setSearchEngine(engineId) | Configure active search engine | threadP.setSearchEngine(engineId) |
| UI Preferences | updateFontSizeLevel(level) | Adjust interface font size | configP.setSetting('fontSizeLevel', level) |
| Feature Toggles | setCopyWithCotEnabled(enabled) | Toggle chain-of-thought copying | Backend update via events |

 All methods use `usePresenter` composable to make IPC calls to the main process presenters (`configP`, `llmP`, `threadP`).

 Sources: [src/renderer/src/stores/settings.ts872-909](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/stores/settings.ts#L872-L909) [src/renderer/src/stores/settings.ts807-815](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/stores/settings.ts#L807-L815) [src/renderer/src/stores/settings.ts856-870](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/stores/settings.ts#L856-L870) [src/renderer/src/stores/settings.ts1066-1108](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/stores/settings.ts#L1066-L1108)

 
## Provider and Model Configuration

 The system manages complex provider and model configurations with hierarchical settings, status tracking, and custom model support.

 
### Provider Configuration Structure

 
```

```

 Sources: [src/main/presenter/configPresenter/index.ts74-82](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts#L74-L82) [src/renderer/src/stores/settings.ts25-41](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/stores/settings.ts#L25-L41) [src/main/presenter/configPresenter/index.ts494-547](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts#L494-L547)

 
### Model Status Management

 The system implements efficient model status tracking with memory caching and batch operations:

 
```

```

 Sources: [src/main/presenter/configPresenter/index.ts494-547](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts#L494-L547) [src/main/presenter/configPresenter/index.ts88-90](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts#L88-L90)

 
## Event-Driven Synchronization

 The configuration system uses a comprehensive event system to maintain synchronization between components and processes. Events are broadcast from the main process to all renderer windows via `eventBus.send(eventName, SendTarget.ALL_WINDOWS, payload)`.

 
### Configuration Event Categories

 
#### CONFIG_EVENTS Constants

 
| Event Name | Purpose | Payload Type | Triggered By |
|---|---|---|---|
| CONFIG_EVENTS.PROVIDER_CHANGED | Complete provider list changed | None | ConfigPresenter.setProviders() |
| CONFIG_EVENTS.PROVIDER_ATOMIC_UPDATE | Single provider configuration change | ProviderChange | ConfigPresenter.updateProviderAtomic() |
| CONFIG_EVENTS.PROVIDER_BATCH_UPDATE | Multiple provider changes | ProviderBatchUpdate | ConfigPresenter.updateProvidersBatch() |
| CONFIG_EVENTS.MODEL_STATUS_CHANGED | Model enable/disable state | {providerId, modelId, enabled} | ConfigPresenter.setModelStatus() |
| CONFIG_EVENTS.MODEL_LIST_CHANGED | Provider model list update | providerId: string | ConfigPresenter.addCustomModel(), etc. |
| CONFIG_EVENTS.SETTING_CHANGED | Generic setting changed | (key: string, value: unknown) | ConfigPresenter.setSetting() |
| CONFIG_EVENTS.FONT_SIZE_CHANGED | Font size preference change | number | ConfigPresenter.setSetting('fontSizeLevel', value) |
| CONFIG_EVENTS.LANGUAGE_CHANGED | Language preference change | string | ConfigPresenter.setLanguage() |
| CONFIG_EVENTS.CONTENT_PROTECTION_CHANGED | Screen sharing protection toggle | boolean | Feature toggle |
| CONFIG_EVENTS.COPY_WITH_COT_CHANGED | Chain-of-thought copy toggle | boolean | Feature toggle |
| CONFIG_EVENTS.THEME_CHANGED | Theme preference change | string | Theme system |

 The `ProviderChange` interface for atomic updates:

 
```

```

 Sources: [src/main/events.ts12-38](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/events.ts#L12-L38) [src/shared/provider-operations.ts1-50](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/shared/provider-operations.ts#L1-L50)

 
### Event Handling in Settings Store

 The settings store sets up comprehensive event listeners in `setupProviderListener()` to maintain synchronization:

 
```

```

 The `updateLocalModelStatus()` function updates the local cache without triggering backend requests, optimizing reactivity for model status changes that have already been persisted.

 Sources: [src/renderer/src/stores/settings.ts655-746](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/stores/settings.ts#L655-L746)

 
## Configuration Helpers and Extensions

 The system includes specialized configuration helpers for different functional areas, each managing specific configuration domains.

 
### Configuration Helper Architecture

 
```

```

 Sources: [src/main/presenter/configPresenter/index.ts98-170](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts#L98-L170) [src/main/presenter/configPresenter/index.ts1002-1059](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts#L1002-L1059) [src/main/presenter/configPresenter/index.ts1067-1120](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts#L1067-L1120)

 
### Helper Integration Patterns

 Each configuration helper follows a consistent integration pattern with the main `ConfigPresenter`:

 
| Helper | Integration Method | Configuration Scope |
|---|---|---|
| McpConfHelper | getMcpConfHelper() | MCP server configurations, default servers, enabled state |
| ModelConfigHelper | Direct method delegation | Model metadata, capabilities, custom configurations |
| KnowledgeConfHelper | Direct method delegation | Built-in knowledge base configurations, RAG settings |

 The helpers provide specialized configuration management while maintaining consistency with the overall configuration architecture through the central `ConfigPresenter` interface.

 Sources: [src/main/presenter/configPresenter/index.ts1056-1059](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts#L1056-L1059) [src/main/presenter/configPresenter/index.ts162-169](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts#L162-L169)
