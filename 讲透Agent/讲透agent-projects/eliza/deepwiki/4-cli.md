<!-- source: DeepWiki mcp.deepwiki.com · repo elizaOS/eliza · page 4 CLI · fetched 2026-10-29 -->

# CLI

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitattributes](.gitattributes)
- [.gitignore](.gitignore)
- [packages/app/test/ui-smoke/apps-utility-interactions.spec.ts](packages/app/test/ui-smoke/apps-utility-interactions.spec.ts)
- [packages/app/test/ui-smoke/remote-capability-view.spec.ts](packages/app/test/ui-smoke/remote-capability-view.spec.ts)
- [packages/cloud-frontend/tests/e2e/api-explorer-flow.spec.ts](packages/cloud-frontend/tests/e2e/api-explorer-flow.spec.ts)
- [packages/core/src/__tests__/action-structure-audit.test.ts](packages/core/src/__tests__/action-structure-audit.test.ts)
- [packages/core/src/generated/action-docs.ts](packages/core/src/generated/action-docs.ts)
- [packages/core/src/utils/context-catalog.ts](packages/core/src/utils/context-catalog.ts)
- [packages/elizaos/templates-manifest.json](packages/elizaos/templates-manifest.json)
- [packages/examples/a2a/tsconfig.json](packages/examples/a2a/tsconfig.json)
- [packages/examples/agent-console/tsconfig.json](packages/examples/agent-console/tsconfig.json)
- [packages/examples/aws/tsconfig.json](packages/examples/aws/tsconfig.json)
- [packages/examples/bluesky/tsconfig.json](packages/examples/bluesky/tsconfig.json)
- [packages/examples/setup-guide.html](packages/examples/setup-guide.html)
- [packages/prompts/scripts/generate-plugin-action-spec.js](packages/prompts/scripts/generate-plugin-action-spec.js)
- [packages/prompts/specs/actions/plugins.generated.json](packages/prompts/specs/actions/plugins.generated.json)
- [packages/ui/src/bridge/capacitor-bridge.ts](packages/ui/src/bridge/capacitor-bridge.ts)
- [packages/ui/src/bridge/plugin-bridge.ts](packages/ui/src/bridge/plugin-bridge.ts)
- [packages/ui/src/components/apps/GameView.tsx](packages/ui/src/components/apps/GameView.tsx)
- [packages/ui/src/components/apps/load-apps-catalog.ts](packages/ui/src/components/apps/load-apps-catalog.ts)
- [packages/ui/src/components/character/CharacterEditor.tsx](packages/ui/src/components/character/CharacterEditor.tsx)
- [plugins/plugin-browser/src/actions/browser.ts](plugins/plugin-browser/src/actions/browser.ts)
- [plugins/plugin-coding-tools/src/services/ripgrep-service.ts](plugins/plugin-coding-tools/src/services/ripgrep-service.ts)
- [tsconfig.dist-paths.json](tsconfig.dist-paths.json)
- [turbo.json](turbo.json)

</details>



The elizaOS command-line interface (CLI) is the primary entry point for managing agent lifecycles, developing plugins, and deploying to production environments. It provides a unified toolset for interacting with the multi-agent framework across different runtimes and platforms.

## Overview

The CLI is packaged as `elizaos` and serves as a tool for scaffolding, upgrading, and managing elizaOS projects [packages/elizaos/templates-manifest.json:5-23](). It is designed to be "location-aware," automatically detecting and delegating commands to local installations within a project directory when available.

### Key Features
- **Project Scaffolding**: Initialize new agents and plugins using the `create` command, utilizing pre-defined templates for `plugin` and `project` kinds [packages/elizaos/templates-manifest.json:7-22]().
- **Lifecycle Management**: Tools to `upgrade` existing projects and retrieve system `info`.
- **Deployment**: Integrated `deploy` commands for pushing agents to cloud infrastructure like AWS ECS and Docker-based targets.
- **Environment Management**: Handles configuration and authentication for the elizaOS ecosystem.

## Architecture and Packages

The CLI infrastructure is distributed across several packages to support different runtime environments and deployment targets.

| Package | Role | Key File |
|---------|------|----------|
| `elizaos` | Main CLI entry point and project manager | `packages/elizaos/package.json` |
| `@elizaos/agent` | Standalone agent and backend server | `packages/agent/src/api/server.ts` |
| `@elizaos/core` | Core TypeScript runtime and logic | `packages/core/src/runtime.ts` |
| `@elizaos/plugin-cli` | Plugin providing CLI-specific actions | `turbo.json:182-185` |

### CLI Execution Flow
The following diagram illustrates how the CLI determines whether to run globally or delegate to a local project instance.

**CLI Delegation Logic**
```mermaid
graph TD
    "UserCommand"["User runs 'elizaos start'"] --> "CheckLocal"["Check node_modules/@elizaos/cli"]
    "CheckLocal" --> "Exists?"{"Exists?"}
    "Exists?" -- "Yes" --> "CheckEnv"["Check Delegation Env Vars"]
    "Exists?" -- "No" --> "RunGlobal"["Execute Global CLI"]
    
    "CheckEnv" --> "IsTestMode?"{"ELIZA_CONFIG_SKIP_LOCAL_CLI_DELEGATION == 'true'?"}
    "IsTestMode?" -- "Yes" --> "RunGlobal"
    "IsTestMode?" -- "No" --> "Delegate"["Execute node_modules/@elizaos/cli/dist/index.js"]
    
    subgraph "LocalProjectSpace"["Local Project Space"]
        "Delegate"
    end
    
    subgraph "GlobalSpace"["Global Space"]
        "RunGlobal"
    end
```
Sources: `scripts/debug-cli-delegation.ts`

## CLI Commands and Usage

The `elizaos` CLI manages its command structure to facilitate rapid development. It provides a user-friendly interface for interactive scaffolding.

Common commands include:
- `create`: Scaffolds a new project from templates. Available templates include `plugin` (TypeScript) and `project` (package-first with optional local source mode) [packages/elizaos/templates-manifest.json:7-22]().
- `upgrade`: Updates project dependencies and templates to the latest version.
- `info`: Displays diagnostic information about the current environment.

For details on the primary commands and their parameters, see [CLI Deploy Command](#4.2).

## Deployment

The CLI includes a robust `deploy` command designed to streamline the transition from local development to production. It handles containerization and cloud provisioning, specifically targeting environments like AWS ECS and Docker-based hosts.

For details on configuring and running deployments, see [CLI Deploy Command](#4.2).

## Code Entity Mapping

The CLI bridges natural language commands to specific code entities within the monorepo.

**CLI Component Association**
```mermaid
graph LR
    subgraph "CLIEntitySpace"["CLI Entity Space"]
        "templates_manifest"["packages/elizaos/templates-manifest.json"]
        "agent_server"["packages/agent/src/api/server.ts"]
        "action_docs"["packages/core/src/generated/action-docs.ts"]
        "ripgrep_service"["plugins/plugin-coding-tools/src/services/ripgrep-service.ts"]
    end

    subgraph "Functionality"["Functionality"]
        "scaffolding"["Project Scaffolding (create)"]
        "orchestration"["Agent API & Orchestration"]
        "prompt_gen"["Action Spec Generation"]
        "search_tools"["CLI Search (RipgrepService)"]
    end

    "templates_manifest" --> "scaffolding"
    "agent_server" --> "orchestration"
    "action_docs" --> "prompt_gen"
    "ripgrep_service" --> "search_tools"
```
Sources: [packages/elizaos/templates-manifest.json:1-24](), [packages/core/src/generated/action-docs.ts:1-75](), [plugins/plugin-coding-tools/src/services/ripgrep-service.ts:41-43]()

### Action Documentation Generation
The CLI ecosystem includes scripts to generate action and provider documentation from specifications [packages/core/src/generated/action-docs.ts:1-4](). This ensures that the agent's available capabilities, such as `REPLY`, `IGNORE`, and `NONE`, are always synchronized with the core logic [packages/core/src/generated/action-docs.ts:77-274](). This is handled by specialized scripts like `generate-plugin-action-spec.js` which parses TypeScript files for action definitions [packages/prompts/scripts/generate-plugin-action-spec.js:1-5]() and maps them to contexts [packages/core/src/utils/context-catalog.ts:3-162]().

Sources:
- [packages/elizaos/templates-manifest.json:1-24]()
- [packages/core/src/generated/action-docs.ts:1-274]()
- [packages/prompts/specs/actions/plugins.generated.json:1-220]()
- [packages/prompts/scripts/generate-plugin-action-spec.js:1-157]()
- [packages/core/src/utils/context-catalog.ts:3-162]()

---

