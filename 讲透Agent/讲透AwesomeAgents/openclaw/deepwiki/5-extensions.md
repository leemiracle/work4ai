<!-- source: DeepWiki mcp.deepwiki.com · repo openclaw/openclaw · page 5 Extensions · fetched 2026-10-26 -->

# Extensions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/plugins/dependency-resolution.md](docs/plugins/dependency-resolution.md)
- [docs/plugins/manifest.md](docs/plugins/manifest.md)
- [docs/plugins/sdk-subpaths.md](docs/plugins/sdk-subpaths.md)
- [extensions/codex/src/app-server/attempt-startup.test.ts](extensions/codex/src/app-server/attempt-startup.test.ts)
- [extensions/codex/src/app-server/managed-binary.test.ts](extensions/codex/src/app-server/managed-binary.test.ts)
- [extensions/codex/src/app-server/managed-binary.ts](extensions/codex/src/app-server/managed-binary.ts)
- [extensions/codex/src/app-server/run-attempt-test-harness.ts](extensions/codex/src/app-server/run-attempt-test-harness.ts)
- [extensions/codex/src/app-server/runtime-artifact.test.ts](extensions/codex/src/app-server/runtime-artifact.test.ts)
- [extensions/codex/src/app-server/transport-stdio.config.test.ts](extensions/codex/src/app-server/transport-stdio.config.test.ts)
- [extensions/codex/src/node-exec-server.test.ts](extensions/codex/src/node-exec-server.test.ts)
- [extensions/tsconfig.package-boundary.paths.json](extensions/tsconfig.package-boundary.paths.json)
- [extensions/xai/tsconfig.json](extensions/xai/tsconfig.json)
- [scripts/build-external-plugin-local-dist.mts](scripts/build-external-plugin-local-dist.mts)
- [scripts/copy-bundled-plugin-metadata.mts](scripts/copy-bundled-plugin-metadata.mts)
- [scripts/lib/plugin-npm-package-manifest.mts](scripts/lib/plugin-npm-package-manifest.mts)
- [scripts/lib/plugin-npm-runtime-build.mjs](scripts/lib/plugin-npm-runtime-build.mjs)
- [scripts/lib/plugin-npm-runtime-build.mts](scripts/lib/plugin-npm-runtime-build.mts)
- [scripts/lib/plugin-sdk-entrypoints.json](scripts/lib/plugin-sdk-entrypoints.json)
- [scripts/lib/plugin-sdk-private-local-only-subpaths.json](scripts/lib/plugin-sdk-private-local-only-subpaths.json)
- [scripts/plugin-sdk-surface-report.mts](scripts/plugin-sdk-surface-report.mts)
- [scripts/sync-plugin-sdk-exports.mts](scripts/sync-plugin-sdk-exports.mts)
- [src/plugin-sdk/facade-resolution-shared.ts](src/plugin-sdk/facade-resolution-shared.ts)
- [src/plugin-sdk/windows-spawn.test.ts](src/plugin-sdk/windows-spawn.test.ts)
- [src/plugin-sdk/windows-spawn.ts](src/plugin-sdk/windows-spawn.ts)
- [src/plugins/copy-bundled-plugin-metadata.test.ts](src/plugins/copy-bundled-plugin-metadata.test.ts)
- [src/plugins/doctor-contract-artifact.ts](src/plugins/doctor-contract-artifact.ts)
- [src/plugins/package-entrypoints.ts](src/plugins/package-entrypoints.ts)
- [src/plugins/plugin-sdk-native-resolver.test.ts](src/plugins/plugin-sdk-native-resolver.test.ts)
- [src/plugins/plugin-sdk-native-resolver.ts](src/plugins/plugin-sdk-native-resolver.ts)
- [src/plugins/public-surface-runtime.ts](src/plugins/public-surface-runtime.ts)
- [src/plugins/root-artifact-path.ts](src/plugins/root-artifact-path.ts)
- [src/plugins/sdk-alias.test.ts](src/plugins/sdk-alias.test.ts)
- [src/plugins/sdk-alias.ts](src/plugins/sdk-alias.ts)
- [src/plugins/setup-registry.lifecycle.test.ts](src/plugins/setup-registry.lifecycle.test.ts)
- [src/plugins/setup-registry.ts](src/plugins/setup-registry.ts)
- [test/plugin-npm-package-manifest.test.ts](test/plugin-npm-package-manifest.test.ts)
- [test/plugin-npm-runtime-build.test.ts](test/plugin-npm-runtime-build.test.ts)
- [test/scripts/build-external-plugin-local-dist.test.ts](test/scripts/build-external-plugin-local-dist.test.ts)
- [test/scripts/plugin-npm-runtime-native-import.test.ts](test/scripts/plugin-npm-runtime-native-import.test.ts)
- [test/scripts/sync-plugin-sdk-exports.test.ts](test/scripts/sync-plugin-sdk-exports.test.ts)
- [test/vitest/vitest.shared.config.ts](test/vitest/vitest.shared.config.ts)

</details>



Extensions provide OpenClaw’s primary mechanism for adding new capabilities without modifying core source code. There are two main extension types supported by OpenClaw:

*   **Plugins** — Modular TypeScript/JavaScript packages that register runtime capabilities such as model providers, tools, hooks, and channels.
*   **Skills** — Markdown-based agent capability definitions that provide instructions, examples, and guiding context for agent behavior.

This page gives a high-level overview of these extension types, their architecture, and integration into the system. For deep technical detail and usage, see the respective child pages:

*   [Plugin Architecture](#5.1) — Full SDK reference, plugin registration API, exports, and discovery mechanisms.
*   [Skills System](#5.2) — `SKILL.md` format, requirements, installation, and execution model.
*   [Plugin Examples](#5.3) — Walkthroughs of OAuth plugins like Google Gemini CLI and Qwen Portal, including provider registration and authentication flows.

---

## Extension Types

| Extension Type | Format | Purpose | Distribution Examples |
| :--- | :--- | :--- | :--- |
| **Plugins** | TS/JS modules or bundles | Add providers, tools, hooks, channels, and more | Bundled (`extensions/*`), official external packages, or npm packages |
| **Skills** | Markdown files named `SKILL.md` | Define agent capabilities via instructions | ClawHub (community collection), repo-bundled (`./skills`) |

Plugins are code-driven extensions that integrate deeply with OpenClaw’s runtime system, while skills augment agent behavior through natural language instructions and examples.

---

## Plugin System Architecture

OpenClaw’s plugin system organizes plugin discovery, registration, and runtime integration into well-defined components. The system is "manifest-driven," meaning it reads `openclaw.plugin.json` to validate configuration and determine capabilities before executing any plugin code [docs/plugins/manifest.md:20-22]().

Title: Plugin Discovery and Registration Entity Mapping
```mermaid
graph TB
    subgraph "Plugin_Discovery_Space"
        ["extensions/"] -- "Bundled" --> ["listBundledPluginBuildEntries"]
        ["openclaw.plugin.json"] -- "Manifest" --> ["PluginManifestRegistry"]
    end

    subgraph "Code_Entities"
        ["listBundledPluginBuildEntries"] -- "Returns" --> ["PluginBuildEntries"]
        ["PluginManifestRegistry"] -- "Tracks" --> ["PluginManifestRecord"]
    end

    subgraph "Runtime_Activation"
        ["PluginManifestRecord"] -- "Informs" --> ["PluginSetupRegistry"]
        ["PluginSetupRegistry"] -- "Loads" --> ["OpenClawPluginModule"]
    end
```

**Discovery and Distribution:**

OpenClaw differentiates between bundled plugins and external packages. The system uses a specialized build process to manage these entries, ensuring that bundled plugins load from local paths during development while external ones use the `dist` artifacts [test/scripts/build-external-plugin-local-dist.test.ts:49-56](). The `openclaw.plugin.json` manifest acts as the source of truth for plugin identity, configuration schemas, and static capability snapshots [docs/plugins/manifest.md:24-40]().

**Sources:** [docs/plugins/manifest.md:20-40](), [test/scripts/build-external-plugin-local-dist.test.ts:49-56](), [src/plugins/setup-registry.ts:13-22]()

---

## Plugin SDK and Runtime Integration

OpenClaw provides a typed Plugin SDK that defines the interface between plugins and the Gateway core. The SDK is organized into focused subpaths (e.g., `plugin-sdk/core`, `plugin-sdk/agent-runtime`) to maintain a narrow public surface [docs/plugins/sdk-subpaths.md:10-13]().

| Component | Role | Code Entity Location |
| :--- | :--- | :--- |
| **Entry Definition** | Standardized plugin entry point | `definePluginEntry` [docs/plugins/sdk-subpaths.md:48-48]() |
| **Setup Registry** | Manages discovered setup entries | `PluginSetupRegistry` [src/plugins/setup-registry.ts:78-84]() |
| **SDK Alias Resolver** | Resolves public imports to local/dist files | `resolvePluginRuntimeModulePathWithDiagnostics` [src/plugins/sdk-alias.ts:19-21]() |

The runtime uses `jiti` for dynamic module loading, supporting TypeScript plugins directly while maintaining a filesystem cache for performance [src/plugins/sdk-alias.ts:102-104](). It also enforces boundaries between public SDK entrypoints and private internal helpers [scripts/plugin-sdk-surface-report.mts:60-65]().

Title: Plugin SDK Surface and Alias Resolution
```mermaid
graph LR
    subgraph "Natural Language"
        ["Plugin Import"] --> ["SDK Subpath"]
    end

    subgraph "Code Entity Space"
        ["SDK Subpath"] -- "maps to" --> ["plugin-sdk-entrypoints.json"]
        ["plugin-sdk-entrypoints.json"] -- "resolved by" --> ["resolvePluginRuntimeModulePathWithDiagnostics"]
        ["resolvePluginRuntimeModulePathWithDiagnostics"] -- "configures" --> ["buildPluginLoaderJitiOptions"]
    end
```

**Sources:** [docs/plugins/sdk-subpaths.md:10-54](), [src/plugins/sdk-alias.ts:102-104](), [src/plugins/setup-registry.ts:78-84](), [scripts/lib/plugin-sdk-entrypoints.json:1-258]()

---

## Extension Categories

OpenClaw extensions are categorized by their primary function within the system:

*   **Model Providers:** Add support for LLMs via `ProviderPlugin` interfaces [src/plugins/setup-registry.ts:31-31]().
*   **CLI Backends:** Integrate external CLI tools (e.g., `codex`) as agent backends [src/plugins/setup-registry.ts:26-26]().
*   **Messaging Channels:** Connect the Gateway to platforms like Discord or Slack using `defineChannelPluginEntry` [docs/plugins/sdk-subpaths.md:49-49]().
*   **Agent Harnesses:** Specialized runtimes for executing agent attempts, such as the Codex app-server integration [extensions/codex/src/app-server/attempt-startup.test.ts:120-158]().

For details on specific implementations, see [Plugin Examples](#5.3).

**Sources:** [src/plugins/setup-registry.ts:26-31](), [docs/plugins/sdk-subpaths.md:49-49](), [extensions/codex/src/app-server/attempt-startup.test.ts:120-158]()

---

