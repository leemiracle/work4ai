<!-- source: DeepWiki mcp.deepwiki.com · repo sst/opencode · page 3 Configuration System · fetched 2026-10-27 -->

# Configuration System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/core/src/v1/config/provider.ts](packages/core/src/v1/config/provider.ts)
- [packages/opencode/src/acp/agent.ts](packages/opencode/src/acp/agent.ts)
- [packages/opencode/src/agent/agent.ts](packages/opencode/src/agent/agent.ts)
- [packages/opencode/src/command/template/initialize.txt](packages/opencode/src/command/template/initialize.txt)
- [packages/opencode/src/config/config.ts](packages/opencode/src/config/config.ts)
- [packages/opencode/src/config/tui.ts](packages/opencode/src/config/tui.ts)
- [packages/opencode/src/server/server.ts](packages/opencode/src/server/server.ts)
- [packages/opencode/test/agent/agent.test.ts](packages/opencode/test/agent/agent.test.ts)
- [packages/opencode/test/config/config.test.ts](packages/opencode/test/config/config.test.ts)
- [packages/opencode/test/config/tui.test.ts](packages/opencode/test/config/tui.test.ts)
- [packages/opencode/test/provider/header-timeout.test.ts](packages/opencode/test/provider/header-timeout.test.ts)
- [packages/sdk/js/src/gen/sdk.gen.ts](packages/sdk/js/src/gen/sdk.gen.ts)
- [packages/sdk/js/src/gen/types.gen.ts](packages/sdk/js/src/gen/types.gen.ts)
- [packages/sdk/js/src/v2/gen/sdk.gen.ts](packages/sdk/js/src/v2/gen/sdk.gen.ts)
- [packages/sdk/js/src/v2/gen/types.gen.ts](packages/sdk/js/src/v2/gen/types.gen.ts)
- [packages/sdk/openapi.json](packages/sdk/openapi.json)
- [packages/web/src/content/docs/config.mdx](packages/web/src/content/docs/config.mdx)
- [packages/web/src/content/docs/keybinds.mdx](packages/web/src/content/docs/keybinds.mdx)
- [packages/web/src/content/docs/rules.mdx](packages/web/src/content/docs/rules.mdx)
- [packages/web/src/content/docs/tui.mdx](packages/web/src/content/docs/tui.mdx)
- [perf/test-suite.md](perf/test-suite.md)

</details>



The configuration system provides hierarchical, merged configuration across multiple layers, from organizational defaults to runtime overrides. It supports JSON/JSONC files, environment variables, and filesystem-based extensions for agents, commands, and plugins.

**Scope**: This page covers the overall architecture, loading process, and merge strategies. For detailed child page references, see [Configuration Loading and Merging](#3.1), [Agent System](#3.2), and [Provider and Model Configuration](#3.3).

---

## Configuration Hierarchy and Code Entities

OpenCode loads configuration from multiple distinct layers with strict precedence rules. The system maps user-facing configuration files and environment parameters to internal code services like `Config.Service` [packages/opencode/src/config/config.ts:136]() and `TuiConfig.Service` [packages/opencode/src/config/tui.ts:47]().

```mermaid
graph TB
    subgraph "NaturalLanguageSpace"
        Remote[""Remote Config (.well-known/opencode)""]
        Global[""Global Config (~/.config/opencode/opencode.json)""]
        CustomPath[""Custom Config (OPENCODE_CONFIG env var)""]
        Project[""Project Config (opencode.json in project root)""]
        DotOpencode["".opencode/ directories (agents, commands, plugins)""]
        Inline[""Inline Config (OPENCODE_CONFIG_CONTENT env var)""]
        ManagedFile[""Managed Config (File-based: /Library/Application Support/opencode)""]
        ManagedMacOS[""Managed Config (macOS: ai.opencode.managed.plist)""]
    end

    subgraph "CodeEntitySpace"
        ConfigService[""Config.Service"" packages/opencode/src/config/config.ts:136]
        ConfigPaths[""ConfigPaths.directories()"" packages/opencode/src/config/paths.ts]
        ConfigParse[""ConfigParse.jsonc()"" packages/opencode/src/config/parse.ts]
        ConfigVariable[""ConfigVariable.substitute()"" packages/opencode/src/config/variable.ts]
        ConfigManaged[""ConfigManaged.Service"" packages/opencode/src/config/managed.ts]
        EnvService[""Env.Service"" packages/opencode/src/env.ts]
        AuthService[""Auth.Service"" packages/opencode/src/auth.ts]
        PluginService[""Plugin.Service"" packages/opencode/src/plugin.ts]
    end

    Remote --> ConfigVariable
    Global --> ConfigPaths
    CustomPath --> EnvService
    Project --> ConfigPaths
    DotOpencode --> PluginService
    Inline --> EnvService
    ManagedFile --> ConfigManaged
    ManagedMacOS --> ConfigManaged

    ConfigPaths --> ConfigParse
    ConfigParse --> ConfigVariable
    ConfigVariable --> ConfigService
    EnvService --> ConfigService
    AuthService --> ConfigService
    PluginService --> ConfigService
    ConfigManaged --> ConfigService

    style Remote fill:#f9f,stroke:#333,stroke-width:2px
    style Global fill:#bbf,stroke:#333,stroke-width:2px
    style CustomPath fill:#bfb,stroke:#333,stroke-width:2px
    style Project fill:#ffb,stroke:#333,stroke-width:2px
    style DotOpencode fill:#fbb,stroke:#333,stroke-width:2px
    style Inline fill:#ccf,stroke:#333,stroke-width:2px
    style ManagedFile fill:#fcf,stroke:#333,stroke-width:2px
    style ManagedMacOS fill:#cff,stroke:#333,stroke-width:2px
```
**Sources:** [packages/opencode/src/config/config.ts:131-185](), [packages/opencode/src/config/paths.ts:20-40](), [packages/opencode/src/config/parse.ts:8-33](), [packages/opencode/src/config/variable.ts:34-91](), [packages/opencode/src/config/managed.ts:1-20](), [packages/opencode/src/env.ts:1-10](), [packages/opencode/src/auth.ts:1-10](), [packages/opencode/src/plugin.ts:1-10]()

### Layer Definitions

| Layer | Source | Precedence | Code Entity / Reference |
|-------|--------|------------|-------------------------|
| 1. Remote | `.well-known/opencode` | Lowest | `substituteWellKnownRemoteConfig` [packages/opencode/src/config/config.ts:65-100]() |
| 2. Global | `~/.config/opencode/opencode.json` | Low | `globalConfigFile()` [packages/opencode/src/config/config.ts:140-148]() |
| 3. Custom | `OPENCODE_CONFIG` env var | Medium | `Env.Service` [packages/opencode/src/env.ts]() |
| 4. Project | `opencode.json` in project root | High | `ConfigPaths.directories` [packages/opencode/src/config/paths.ts]() |
| 5. .opencode | `.opencode/` subdirectories | Higher | `ConfigPlugin.resolvePluginSpec` [packages/opencode/src/config/plugin.ts:10-18]() |
| 6. Inline | `OPENCODE_CONFIG_CONTENT` env var | Highest | Runtime environment injection via `Env.Service` [packages/opencode/src/env.ts]() |
| 7. Managed (File-based) | `/Library/Application Support/opencode/` (macOS), `/etc/opencode/` (Linux), `%ProgramData%\opencode` (Windows) | Absolute | `ConfigManaged.dir` [packages/opencode/src/config/managed.ts]() |
| 8. Managed (macOS Preferences) | `ai.opencode.managed.plist` via MDM | Absolute | `ConfigManaged.Service` [packages/opencode/src/config/managed.ts]() |

**Sources:** [packages/opencode/src/config/config.ts:131-230](), [packages/opencode/src/config/managed.ts:1-20](), [packages/web/src/content/docs/config.mdx:45-55](), [packages/opencode/src/config/plugin.ts:10-18]()

---

## Configuration Service Architecture

The core configuration processing pipeline coordinates discovery, parsing, variable substitution, and schema validation.

```mermaid
graph LR
    subgraph "CodeEntitySpace"
        FS[""FSUtil.Service"" packages/core/fs-util.ts]
        Parse[""ConfigParse.schema()"" packages/opencode/src/config/parse.ts]
        Merge[""mergeConfigConcatArrays()"" packages/opencode/src/config/config.ts:46-52]
        Output[""ConfigV1.Info"" packages/core/src/v1/config/config.ts]
        ConfigService[""Config.Service"" packages/opencode/src/config/config.ts:136]
    end

    FS --> Parse
    Parse --> Merge
    Merge --> Output
    Output --> ConfigService
```

**Sources:** [packages/opencode/src/config/config.ts:46-52](), [packages/opencode/src/config/parse.ts:35-61](), [packages/opencode/src/config/config.ts:136]()

### Configuration Schema and Parsing

OpenCode uses `Effect.Schema` for runtime validation. Configuration files are parsed as JSONC (JSON with Comments), allowing users to document settings directly.

| Entity | Location | Description |
|------|------------|-------------|
| `Config.Service` | [packages/opencode/src/config/config.ts:136]() | Main Effect Service for accessing prioritized configuration. |
| `TuiConfig.Service` | [packages/opencode/src/config/tui.ts:47]() | Specialized service for TUI preferences (keybinds, themes). |
| `ConfigParse.jsonc` | [packages/opencode/src/config/parse.ts:8-33]() | Handles JSON with comments and trailing commas using `jsonc-parser`. |
| `ConfigVariable` | [packages/opencode/src/config/variable.ts]() | Performs variable substitution for `{env:VAR}` and `{file:path}`. |

**Sources:** [packages/opencode/src/config/config.ts:136](), [packages/opencode/src/config/tui.ts:47](), [packages/opencode/src/config/parse.ts:8-33](), [packages/opencode/src/config/variable.ts]()

---

## Loading and Merging Strategy

OpenCode employs a deep merge strategy for configuration objects, with custom handlers like `mergeConfigConcatArrays` to concatenate array fields (such as `instructions`) rather than overwriting them [packages/opencode/src/config/config.ts:46-52](). This ensures that configurations from different sources can contribute to lists without completely replacing them.

For complete details on layered precedence, remote fetching, and merge strategies, see [Configuration Loading and Merging](#3.1).

**Sources:** [packages/opencode/src/config/config.ts:41-52]()

---

## Agent and Plugin Discovery

The configuration system discovers custom agents, commands, and plugins located within the project's `.opencode/` directory or global paths [packages/opencode/src/config/config.ts:102-110](). Plugin origins are tracked to ensure correct relative path resolution [packages/opencode/src/config/config.ts:112-116](). The `Agent.Info` schema defines the structure for agent configurations, including permissions, models, and prompts [packages/opencode/src/agent/agent.ts:35-55]().

For detailed documentation on built-in agents and custom definitions, see [Agent System](#3.2).

**Sources:** [packages/opencode/src/config/config.ts:102-116](), [packages/opencode/src/agent/agent.ts:35-55]()

---

## UI, Provider, and Model Configuration

The Terminal User Interface (TUI) manages specialized settings like keybinds, themes, and attention notifications through `TuiConfig.Service` [packages/opencode/src/config/tui.ts:47](). AI providers, authentication methods, and model selection are configured via the providers schema, which is part of the OpenAPI specification [packages/sdk/openapi.json:1-36959](). Authentication details are handled by the `Auth` type, which supports `OAuth`, `ApiAuth`, and `WellKnownAuth` [packages/sdk/js/src/v2/gen/types.gen.ts:109-132]().

For detailed configuration parameters, see [Provider and Model Configuration](#3.3).

**Sources:** [packages/opencode/src/config/tui.ts:47](), [packages/web/src/content/docs/keybinds.mdx:6-20](), [packages/sdk/openapi.json:1-36959](), [packages/sdk/js/src/v2/gen/types.gen.ts:109-132]()

---

