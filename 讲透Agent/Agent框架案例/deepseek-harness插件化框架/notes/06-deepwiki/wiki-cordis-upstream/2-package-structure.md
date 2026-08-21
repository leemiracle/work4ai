---
deepwiki-url: https://deepwiki.com/cordiverse/cordis/2-package-structure
indexed: 2026-08-16
commit: 8cc9e33f (upstream master)
---

# Package Structure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/build.yml](.github/workflows/build.yml)
- [README.md](README.md)
- [package.json](package.json)
- [packages/core/package.json](packages/core/package.json)
- [packages/create/package.json](packages/create/package.json)
- [packages/create/src/bin.ts](packages/create/src/bin.ts)
- [packages/create/src/index.ts](packages/create/src/index.ts)
- [packages/group/package.json](packages/group/package.json)
- [packages/hmr/package.json](packages/hmr/package.json)
- [packages/include/package.json](packages/include/package.json)
- [packages/loader/package.json](packages/loader/package.json)
- [packages/timer/package.json](packages/timer/package.json)
- [packages/utils/package.json](packages/utils/package.json)
- [tsconfig.base.json](tsconfig.base.json)

</details>



This document explains the monorepo organization, workspace configuration, and relationships between different packages in the Cordis ecosystem. It covers the physical structure of the codebase, package naming conventions, and interdependencies.

For information about the runtime architecture and how these packages interact during execution, see [Core Architecture](). For details about the development workflow and build system, see [Development Tools]().

## Monorepo Organization

Cordis is organized as a monorepo using Yarn workspaces, with packages distributed across two main directories: `packages/*` for core framework components and `external/*` for extended functionality.

Title: Cordis Workspace Hierarchy
```mermaid
graph TB
    subgraph ["Cordis Monorepo (@root/cordis)"]
        Root["package.json<br/>Root workspace"]
        
        subgraph ["packages/*"]
            Core["cordis<br/>Core framework"]
            Loader["@cordisjs/plugin-loader<br/>Configuration loader"]
            Timer["@cordisjs/plugin-timer<br/>Timer service"]
            HMR["@cordisjs/plugin-hmr<br/>Hot module replacement"]
            Utils["@cordisjs/utils<br/>Internal utilities"]
            Include["@cordisjs/plugin-include<br/>Config inclusion"]
            Group["@cordisjs/plugin-group<br/>Plugin grouping"]
            Create["create-cordis<br/>Scaffolding tool"]
        end
        
        subgraph ["external/*"]
            External["Additional packages<br/>(external plugins)"]
        end
        
        subgraph ["Development Tools"]
            DevDeps["Dev dependencies<br/>yakumo, esbuild, vitest"]
            Scripts["Build scripts<br/>test, lint, yakumo"]
        end
    end
    
    Root --> Core
    Root --> Loader
    Root --> Timer
    Root --> HMR
    Root --> External
    Root --> DevDeps
    Root --> Scripts
```

**Workspace Configuration**

The root workspace is configured with Yarn workspaces that automatically discover packages in the specified directories:

- **`packages/*`**: Contains core framework components and official plugins. [package.json:9]()
- **`external/*`**: Contains additional packages that extend the framework. [package.json:8]()

Sources: [package.json:1-10]()

## Core Framework Package

The `cordis` package (located in `packages/core`) serves as the foundational framework containing the Context system, service management, event handling, and plugin infrastructure.

| Property | Value |
|----------|--------|
| Package Name | `cordis` |
| Version | `4.0.0-rc.8` |
| Entry Point | `lib/index.js` |
| Types | `lib/index.d.ts` |
| Bin | `bin.js` |

**Key Characteristics:**
- **Standalone Core**: Minimal dependencies, primarily `cosmokit` and `@standard-schema/spec`. [packages/core/package.json:45-48]()
- **Type Definitions**: Provides comprehensive TypeScript definitions via `lib/index.d.ts`. [packages/core/package.json:12]()
- **Export Strategy**: Uses modern ES module exports with conditional exports for source access. [packages/core/package.json:10-17]()
- **Tree Shaking**: Marked as side-effect free for optimal bundling. [packages/core/package.json:5]()

Sources: [packages/core/package.json:1-49]()

## Plugin Ecosystem

The plugin packages follow consistent naming conventions and provide specific functionality that extends the core framework.

Title: Plugin Dependency and Service Mapping
```mermaid
graph LR
    subgraph ["Plugin Packages"]
        PluginLoader["@cordisjs/plugin-loader"]
        PluginTimer["@cordisjs/plugin-timer"]
        PluginHMR["@cordisjs/plugin-hmr"]
        PluginInclude["@cordisjs/plugin-include"]
    end
    
    subgraph ["Core Package"]
        CoreFramework["cordis"]
    end
    
    subgraph ["Cordis Service Space"]
        TimerService["timer service"]
        LoaderService["loader service"]
    end
    
    PluginLoader -- "peerDependency" --> CoreFramework
    PluginTimer -- "peerDependency" --> CoreFramework
    PluginHMR -- "peerDependency" --> CoreFramework
    
    PluginTimer -- "provides" --> TimerService
    PluginLoader -- "provides" --> LoaderService
    PluginHMR -- "requires" --> TimerService
    PluginInclude -- "requires" --> LoaderService
```

### Plugin Package Specifications

| Package | Version | Service/Role | Key Dependencies |
|---------|---------|---------|-------------|
| `@cordisjs/plugin-loader` | 1.0.0-rc.5 | Configuration loading | `cosmokit` |
| `@cordisjs/plugin-timer` | 1.1.2 | `timer` service | `cosmokit` |
| `@cordisjs/plugin-hmr` | 1.0.15 | Hot Module Replacement | `chokidar`, `picomatch`, `schemastery` |
| `@cordisjs/plugin-include` | 1.0.4 | Config file inclusion | `js-yaml`, `cosmokit` |
| `@cordisjs/plugin-group` | 1.0.0 | Plugin grouping | N/A |

**Service Declaration Patterns:**

Plugins use metadata in their `package.json` to declare service contracts. For example, `plugin-hmr` declares a requirement for the `timer` service. [packages/hmr/package.json:33-38]()

Sources: [packages/loader/package.json:1-54](), [packages/timer/package.json:1-45](), [packages/hmr/package.json:1-64](), [packages/include/package.json:1-34](), [packages/group/package.json:1-29]()

## Scaffolding Tool

The `create-cordis` package provides a CLI tool for setting up new Cordis applications. It handles project initialization, directory preparation, and toolchain setup (specifically Yarn binary staging).

**Key Functions:**
- **`stageYarnBin()`**: Manages the injection of specific Yarn versions into the target project based on `.yarnrc.yml` or global versions. [packages/create/src/index.ts:88-168]()
- **`Scaffold` Class**: Orchestrates the project creation process, including registry detection and template fetching. [packages/create/src/index.ts:170-229]()

Sources: [packages/create/package.json:1-50](), [packages/create/src/index.ts:1-230]()

## Development Infrastructure

The monorepo includes comprehensive development tooling managed through the root workspace and the `yakumo` toolchain.

### Build System Dependencies

| Tool | Purpose | Source |
|------|---------|---------------|
| `yakumo` | Build orchestration | [package.json:33]() |
| `yakumo-tsc` | TypeScript compilation | [package.json:35]() |
| `yakumo-esbuild` | Code bundling | [package.json:34]() |
| `yakumo-vitest` | Test execution | [package.json:36]() |
| `tsx` | TypeScript execution | [package.json:29]() |

### Script Commands

The root package defines standardized commands for development workflows:

```json
{
  "yakumo": "node --expose-internals --import tsx --import @cordisjs/unyaml node_modules/yakumo/lib/cli.js",
  "build": "yarn yakumo esbuild && yarn yakumo tsc",
  "test": "yarn yakumo vitest --import tsx",
  "lint": "eslint --cache"
}
```

Sources: [package.json:12-20]()

## Package Dependency Strategy

### Peer Dependencies
All plugin packages declare `cordis` as a peer dependency, ensuring that only one instance of the framework core is active in the application context. [packages/hmr/package.json:46](), [packages/timer/package.json:40]()

### Internal Utilities
The `@cordisjs/utils` package provides internal shared logic. It is marked as `private: true` to prevent accidental public publishing while serving as a shared resource for other packages in the monorepo. [packages/utils/package.json:4]()

Sources: [packages/utils/package.json:1-36](), [packages/hmr/package.json:44-47]()

## Export Strategies

Packages use modern ES module exports with conditional exports to provide type safety and environment-specific entry points:

```json
"exports": {
  ".": {
    "types": "./lib/index.d.ts",
    "default": "./lib/index.js"
  },
  "./src/*": "./src/*",
  "./package.json": "./package.json"
}
```

This configuration allows the `yakumo` build system and consumer tools to resolve the appropriate files whether they are looking for compiled code, source files, or TypeScript definitions.

Sources: [packages/core/package.json:10-17](), [packages/loader/package.json:8-15]()
