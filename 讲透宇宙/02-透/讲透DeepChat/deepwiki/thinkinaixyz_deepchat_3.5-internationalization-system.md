> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/3.5-internationalization-system](https://deepwiki.com/thinkinaixyz/deepchat/3.5-internationalization-system)（Wayback 快照 2026-01-20）
> DeepWiki deepchat/3.5-internationalization-system

# Internationalization System

  Relevant source files 
 - [src/renderer/src/i18n/en-US/settings.json](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/en-US/settings.json)
 - [src/renderer/src/i18n/fa-IR/settings.json](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/fa-IR/settings.json)
 - [src/renderer/src/i18n/fr-FR/settings.json](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/fr-FR/settings.json)
 - [src/renderer/src/i18n/ja-JP/settings.json](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/ja-JP/settings.json)
 - [src/renderer/src/i18n/ko-KR/settings.json](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/ko-KR/settings.json)
 - [src/renderer/src/i18n/pt-BR/settings.json](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/pt-BR/settings.json)
 - [src/renderer/src/i18n/ru-RU/settings.json](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/ru-RU/settings.json)
 - [src/renderer/src/i18n/zh-CN/settings.json](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/zh-CN/settings.json)
 - [src/renderer/src/i18n/zh-HK/settings.json](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/zh-HK/settings.json)
 - [src/renderer/src/i18n/zh-TW/settings.json](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/zh-TW/settings.json)
 
  
## Purpose and Scope

 This document covers the internationalization (i18n) system in DeepChat, which provides multi-language support for the application's user interface. The system manages translation files, language selection, and dynamic language switching across 10+ supported locales.

 For configuration management of language settings, see [Configuration Management Architecture](https://deepwiki.com/thinkinaixyz/deepchat/3.1-configuration-management-architecture). For the settings UI where language selection occurs, see [Settings User Interface](https://deepwiki.com/thinkinaixyz/deepchat/3.4-settings-user-interface).

 
---

 
## System Architecture

 The i18n system follows a JSON-based, file-per-locale architecture where each supported language has its own translation file in the renderer process. The system integrates with Vue's reactivity to enable instant language switching without application restart.

 
```

```

 **Sources**: [src/renderer/src/i18n/en-US/settings.json1-1000](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/en-US/settings.json#L1-L1000) [src/renderer/src/i18n/zh-CN/settings.json1-1000](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/zh-CN/settings.json#L1-L1000) [src/renderer/src/i18n/ja-JP/settings.json1-1000](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/ja-JP/settings.json#L1-L1000) [src/renderer/src/i18n/ko-KR/settings.json1-1000](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/ko-KR/settings.json#L1-L1000)

 
---

 
## Supported Locales

 DeepChat currently supports the following locales, each with a complete translation file:

 
| Locale Code | Language | Region | Translation File |
|---|---|---|---|
| en-US | English | United States | src/renderer/src/i18n/en-US/settings.json |
| zh-CN | Chinese | Simplified (Mainland) | src/renderer/src/i18n/zh-CN/settings.json |
| zh-TW | Chinese | Traditional (Taiwan) | src/renderer/src/i18n/zh-TW/settings.json |
| zh-HK | Chinese | Traditional (Hong Kong) | src/renderer/src/i18n/zh-HK/settings.json |
| ja-JP | Japanese | Japan | src/renderer/src/i18n/ja-JP/settings.json |
| ko-KR | Korean | South Korea | src/renderer/src/i18n/ko-KR/settings.json |
| fr-FR | French | France | src/renderer/src/i18n/fr-FR/settings.json |
| ru-RU | Russian | Russia | src/renderer/src/i18n/ru-RU/settings.json |
| fa-IR | Persian | Iran | src/renderer/src/i18n/fa-IR/settings.json |

 The system uses BCP 47 language tags (e.g., `en-US`, `zh-CN`) as locale identifiers, which are also the directory names under `src/renderer/src/i18n/`.

 **Sources**: [src/renderer/src/i18n/en-US/settings.json1-10](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/en-US/settings.json#L1-L10) [src/renderer/src/i18n/zh-CN/settings.json1-10](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/zh-CN/settings.json#L1-L10) [src/renderer/src/i18n/ja-JP/settings.json1-10](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/ja-JP/settings.json#L1-L10)

 
---

 
## Translation File Structure

 Each locale has a `settings.json` file that contains all UI strings organized in a hierarchical JSON structure. The structure mirrors the application's settings organization.

 
### Top-Level Categories

 
```

```

 **Sources**: [src/renderer/src/i18n/en-US/settings.json1-100](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/en-US/settings.json#L1-L100) [src/renderer/src/i18n/zh-CN/settings.json1-100](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/zh-CN/settings.json#L1-L100)

 
### Nested Structure Example

 The translation keys are nested to group related strings. For example, the `common` section contains general settings strings:

 
```

```

 Similarly, complex sections like `provider` contain nested structures for dialogs and forms:

 
```

```

 **Sources**: [src/renderer/src/i18n/en-US/settings.json1-100](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/en-US/settings.json#L1-L100) [src/renderer/src/i18n/en-US/settings.json288-450](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/en-US/settings.json#L288-L450)

 
### Translation Key Consistency

 All locale files maintain the same key structure. If a key exists in `en-US/settings.json`, it must exist in all other locale files with the appropriate translation. The key paths are identical across locales:

 
| Key Path | en-US | zh-CN | ja-JP |
|---|---|---|---|
| common.title | "Common Settings" | "通用设置" | "一般設定" |
| common.language | "Language" | "语言" | "言語" |
| model.title | "Model Settings" | "模型设置" | "モデル設定" |
| provider.enable | "Enable Service" | "开启服务" | "サービスを有効にする" |

 **Sources**: [src/renderer/src/i18n/en-US/settings.json4-7](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/en-US/settings.json#L4-L7) [src/renderer/src/i18n/zh-CN/settings.json4-7](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/zh-CN/settings.json#L4-L7) [src/renderer/src/i18n/ja-JP/settings.json4-7](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/ja-JP/settings.json#L4-L7)

 
---

 
## Translation Access Pattern

 Vue components access translations using the `$t()` function provided by the i18n plugin. The function takes a dot-notation key path and optional interpolation parameters.

 
```

```

 
### Basic Usage

 
```

```

 
### Dynamic Keys

 Components can construct translation keys dynamically:

 
```

```

 **Sources**: [src/renderer/src/i18n/en-US/settings.json1-500](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/en-US/settings.json#L1-L500)

 
---

 
## Language Selection and Switching

 The language selection mechanism integrates with the configuration system through `UiSettingsHelper` and provides immediate UI updates through Vue's reactivity.

 
```

```

 
### Language Detection Priority

 On application startup, the system determines the locale to use based on the following priority:

 
 - **User Preference**: Value stored in `ElectronStore` under the UI settings key
 - **System Locale**: Operating system language setting
 - **Fallback**: `en-US` if no match is found
 
 
### Configuration Storage

 The selected language is persisted in the Electron store:

 
```

```

 The `UiSettingsHelper` manages this configuration, emitting `CONFIG_EVENTS` when the language changes to trigger updates across the application.

 **Sources**: Based on architectural patterns described in the overview diagrams and configuration system description

 
---

 
## String Interpolation and Formatting

 Translation strings support parameter interpolation for dynamic content using curly brace syntax `{paramName}`.

 
### Simple Interpolation

 
```

```

 Usage in components:

 
```

```

 
### Complex Interpolation

 Some translations use multiple parameters and special formatting:

 
```

```

 
### Pluralization Handling

 The system handles plural forms using conditional logic in the translation keys:

 
```

```

 **Sources**: [src/renderer/src/i18n/en-US/settings.json315-320](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/en-US/settings.json#L315-L320) [src/renderer/src/i18n/en-US/settings.json437-442](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/en-US/settings.json#L437-L442) [src/renderer/src/i18n/en-US/settings.json588-592](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/en-US/settings.json#L588-L592)

 
---

 
## Adding New Translations

 To add support for a new language to DeepChat, follow this process:

 
### 1. Create Locale Directory

 Create a new directory under `src/renderer/src/i18n/` using the BCP 47 language tag:

 
```
src/renderer/src/i18n/
├── en-US/
├── zh-CN/
├── ja-JP/
└── [new-locale]/  # e.g., de-DE for German
    └── settings.json
```

 
### 2. Copy and Translate

 Copy the `en-US/settings.json` file to the new locale directory and translate all values while preserving the key structure:

 
```

```

 
### 3. Maintain Key Consistency

 Ensure all keys from the English version are present in the new translation. Missing keys will cause fallback to the default locale or display the key path itself.

 
### 4. Register Locale

 Register the new locale in the i18n configuration (location determined by the build system and Vue I18n setup).

 
### 5. Update Language Selector

 Add the new language option to the language selector UI component:

 
```

```

 
### Translation Guidelines

 
| Guideline | Description |
|---|---|
| Preserve Interpolation | Keep parameter placeholders like {model}, {name}, {count} intact |
| Match HTML Entities | If the source uses HTML entities (e.g., &nbsp;), preserve them |
| Maintain Line Breaks | Keep \n line break characters where they appear |
| Respect Character Limits | UI elements have space constraints; keep translations concise |
| Test Edge Cases | Verify translations with maximum-length strings to check for UI overflow |

 **Sources**: [src/renderer/src/i18n/en-US/settings.json1-1000](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/en-US/settings.json#L1-L1000) [src/renderer/src/i18n/zh-CN/settings.json1-1000](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/zh-CN/settings.json#L1-L1000)

 
---

 
## Locale-Specific Considerations

 Different languages and regions require specific formatting and cultural considerations:

 
### Right-to-Left (RTL) Support

 Persian (`fa-IR`) is a right-to-left language. The i18n system should coordinate with CSS to apply RTL layout when this locale is active:

 
```

```

 
### Character Encoding

 All translation files use UTF-8 encoding to support international characters. Files include:

 
 - Latin alphabets (English, French)
 - Cyrillic (Russian)
 - CJK characters (Chinese, Japanese, Korean)
 - Arabic script (Persian)
 
 
### Regional Variants

 Chinese has three regional variants with different character sets and terminology:

 
| Locale | Description | Character Set | Example |
|---|---|---|---|
| zh-CN | Mainland China | Simplified Chinese | "设置" |
| zh-TW | Taiwan | Traditional Chinese | "設定" |
| zh-HK | Hong Kong | Traditional Chinese (Cantonese terms) | "設定" |

 While `zh-TW` and `zh-HK` use the same character set, they may differ in technical terminology and phrasing preferences.

 **Sources**: [src/renderer/src/i18n/zh-CN/settings.json1-50](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/zh-CN/settings.json#L1-L50) [src/renderer/src/i18n/zh-TW/settings.json1-50](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/zh-TW/settings.json#L1-L50) [src/renderer/src/i18n/zh-HK/settings.json1-50](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/zh-HK/settings.json#L1-L50) [src/renderer/src/i18n/fa-IR/settings.json1-50](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/fa-IR/settings.json#L1-L50)

 
---

 
## Translation Coverage

 Each translation file contains over 1,000 individual strings covering all areas of the application:

 
```

```

 
### Most Complex Sections

 The following sections have the most translation keys due to their UI complexity:

 
 - **MCP Settings** (`mcp`): ~250 strings for server configuration, tools, prompts, and resources
 - **Provider Settings** (`provider`): ~200 strings for 40+ LLM provider configurations
 - **Model Configuration** (`model`): ~150 strings for model parameters and capabilities
 - **ACP Agent** (`acp`): ~150 strings for agent profiles and debug interface
 
 **Sources**: [src/renderer/src/i18n/en-US/settings.json646-850](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/en-US/settings.json#L646-L850) [src/renderer/src/i18n/en-US/settings.json288-530](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/en-US/settings.json#L288-L530) [src/renderer/src/i18n/en-US/settings.json121-287](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/en-US/settings.json#L121-L287)

 
---

 
## Performance Considerations

 
### Lazy Loading

 Translation files are only loaded for the active locale, not all supported languages at once. This reduces initial bundle size and memory usage.

 
### Caching

 Once loaded, translations are cached in memory. Language switching reuses cached data if the user switches back to a previously used locale within the same session.

 
### Bundle Size

 Each `settings.json` file is approximately 50-70 KB, containing 1,000+ translation strings. With 9+ supported locales, the total translation data is ~500-600 KB, but only one locale is active at a time.

 
| Locale | File Size (approx.) | Character Count |
|---|---|---|
| en-US | 60 KB | ~50,000 chars |
| zh-CN | 70 KB | ~40,000 chars (CJK) |
| ja-JP | 68 KB | ~42,000 chars (CJK) |
| ru-RU | 75 KB | ~48,000 chars (Cyrillic) |

 **Sources**: Based on file analysis of translation files in [src/renderer/src/i18n/](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n)
