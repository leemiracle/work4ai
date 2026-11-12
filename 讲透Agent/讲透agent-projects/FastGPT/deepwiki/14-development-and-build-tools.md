<!-- source: DeepWiki mcp.deepwiki.com · repo labring/FastGPT · page 14 Development and Build Tools · fetched 2026-10-29 -->

# Development and Build Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [document/package.json](document/package.json)
- [package.json](package.json)
- [packages/global/package.json](packages/global/package.json)
- [packages/service/package.json](packages/service/package.json)
- [packages/web/package.json](packages/web/package.json)
- [pnpm-lock.yaml](pnpm-lock.yaml)
- [pnpm-workspace.yaml](pnpm-workspace.yaml)
- [projects/app/package.json](projects/app/package.json)
- [projects/marketplace/Dockerfile](projects/marketplace/Dockerfile)
- [projects/marketplace/package.json](projects/marketplace/package.json)
- [projects/mcp_server/Dockerfile](projects/mcp_server/Dockerfile)
- [projects/mcp_server/package.json](projects/mcp_server/package.json)
- [scripts/icon/package.json](scripts/icon/package.json)

</details>



This document provides a high-level overview of the development ecosystem, build processes, package management, and quality assurance tools used in the FastGPT monorepo. It serves as a guide for developers to understand how the codebase is structured, tested, typed, and maintained.

For detailed technical specifications, refer to the child pages:  
- [Build System and Scripts](#14.1) — Turbo, pnpm scripts, Dockerfiles, worker builds, icon/i18n scripts and deploy init.  
- [Testing Framework](#14.2) — Vitest setup, `test/` mocks and utils, integration tests, and per-package test configs.  
- [TypeScript Configuration](#14.3) — `tsconfig.json` settings and path aliases (`@fastgpt/*`, `@test`) across the monorepo.  
- [Agent Workflows and Repository Conventions](#14.4) — The `.agents` directory, `AGENTS.md` conventions, issue templates, and `.vscode` setup.  
- [Data Migration Framework](#14.5) — `projects/app/src/migration` registry, runner, task structure, and version-specific backfill tasks.

## Package Management with pnpm

FastGPT leverages **pnpm workspaces** to efficiently manage dependencies and packages in this monorepo. The key workspace components are:

- **Lockfile and Catalogs**: Dependency versions and catalogs centrally managed in `pnpm-lock.yaml` ensure consistency across the monorepo [pnpm-lock.yaml:1-132]().
- **Engines Enforcement**: The root `package.json` mandates Node.js ≥ 22.23.2 and pnpm 10.x to standardize runtime environments [package.json:52-55]().
- **Workspace Packages**:
  - `packages/`: Shared libraries like `@fastgpt/global` (types & OpenAPI schemas), `@fastgpt/service` (backend logic), and `@fastgpt/web` (UI components) [packages/global/package.json:2](), [packages/service/package.json:2](), [packages/web/package.json:2]().
  - `projects/`: End-user deployable apps including the main `app`, `marketplace`, `mcp_server`, and various sandboxes [projects/app/package.json:2](), [projects/marketplace/package.json:2](), [projects/mcp_server/package.json:2]().
  - `sdk/`: Observability and storage SDKs which underpin tracing, logging, and sandbox communication.
- **Internal Dependencies**: Packages refer to one another via the `workspace:*` protocol enabling real-time incremental builds and dependency linking [projects/app/package.json:30-32]().

This structure allows fast installation, deduplication of dependencies, and seamless cross-package referencing in development.

For details about build scripts, Dockerfiles, and automation, see [Build System and Scripts](#14.1).

Sources: [pnpm-lock.yaml:1-132](), [package.json:52-55](), [packages/global/package.json:2](), [packages/service/package.json:2](), [packages/web/package.json:2](), [projects/app/package.json:2-32](), [projects/marketplace/package.json:2](), [projects/mcp_server/package.json:2]()

---

## Testing Framework Overview

FastGPT adopts **Vitest** as its principal testing framework to maintain code stability across the repo:

- **Multi-Package Testing**: Each package and project is configured with dedicated Vitest config files for unit, integration, and performance tests [packages/service/package.json:6-11](), [projects/app/package.json:20-21]().
- **Workspace-Level Orchestration**: Scripts in the root `package.json` coordinate tests across targeted packages using Turbo as well, enabling fast parallel test runs [package.json:17-28]().
- **Test Utilities & Mocks**: Shared mocks and utilities exist to facilitate isolated environment tests, including in-memory DBs (e.g., `mongodb-memory-server`).
- **Integration Tests**: Specialized integration tests ensure inter-package and full system behavior for critical subsystems like sandboxes and API servers.

For more details and per-package test setup, see [Testing Framework](#14.2).

Sources: [projects/app/package.json:20-21](), [packages/service/package.json:6-11](), [package.json:17-28]()

---

## TypeScript Configuration and Path Aliases

The repository employs a centralized TypeScript config system to ensure consistent typing, compilation, and path resolution:

- **Base Configuration**: Root `tsconfig.json` defines global compiler options and references subordinate configs across packages and projects [tsconfig.json:1-60]().
- **Path Aliases** configured for clear code import semantics:
  - `@fastgpt/*` aliases map to source folders within `packages/*`
  - `@/*` points to project-specific source roots such as `projects/app/src/`
  - `@test/*` points to shared test utilities in the root `test/` folder
- **Project Extensions**: Each package/project extends the base configs to add scoped type roots, libs, and references enforcing strict type safety and IntelliSense [projects/app/tsconfig.json:1-33]().

For a comprehensive explanation of the TypeScript setup and pathing, see [TypeScript Configuration](#14.3).

Sources: [tsconfig.json:1-60](), [projects/app/tsconfig.json:1-33]()

---

## Agent Workflows and Repository Conventions

FastGPT incorporates agent workflows directly into the repository structure to augment developer productivity and consistency:

- **`.agents` Directory**: Houses agent workflow designs, skills such as `pr-review`, `i18n-translate`, and AI prompt patterns that automate and guide development tasks.
- **`AGENTS.md`**: Document outlining repository-level conventions for these AI-powered agents and instructions for contributors.
- **Issue Templates & IDE Config**: `.vscode` folder includes shared settings and task configurations for streamlining local development and agent invocation in editors.

These conventions provide a framework for collaborative AI-agent aided development processes.

See [Agent Workflows and Repository Conventions](#14.4) for full details.

---

## Data Migration Framework

To support schema evolution and backward-compatible upgrades, FastGPT includes an in-house migration framework:

- **Migration Registry and Runner** located in `projects/app/src/migration` tracks and executes registered migration tasks during app startup [projects/app/tsconfig.json:1-33]().
- **Version-Specific Tasks** handle backfilling data, updating indexes, and schema modifications required by new versions.
- This migration system ensures smooth upgrade paths for production deployments and automated data consistency.

Consult [Data Migration Framework](#14.5) for migration task development instructions and tooling interfaces.

Sources: [projects/app/tsconfig.json:1-33]()

---

## Code-to-System Mapping Diagrams

### Build and Script Execution Flow

This diagram illustrates the relationship between common developer commands, package scripts, and build/test configuration entities:

```mermaid
graph TD
    subgraph "Natural Language Space"
        "DevCommand"["pnpm run dev"]
        "BuildCommand"["pnpm run build"]
        "TestCommand"["pnpm run test"]
    end

    subgraph "Code Entity Space"
        "AppPkg"["projects/app/package.json"]
        "WorkerScript"["projects/app/scripts/build-workers.ts"]
        "NextDev"["next dev"]
        "RootPkg"["package.json (root)"]
        "VitestConfig"["vitest.config.mts"]
        "McpPkg"["projects/mcp_server/package.json"]
        "BunBuild"["bun build script"]
    end

    "DevCommand" --> "AppPkg"
    "AppPkg" --runs--> "WorkerScript"
    "AppPkg" --spawns--> "NextDev"

    "BuildCommand" --> "McpPkg"
    "McpPkg" --executes--> "BunBuild"

    "TestCommand" --> "RootPkg"
    "RootPkg" --executes--> "VitestConfig"
```

Sources: [package.json:6-31](), [projects/app/package.json:13-25](), [projects/mcp_server/package.json:10-13]()

---

### Monorepo Path Aliases and TypeScript Scope

This diagram maps natural language import aliases to their corresponding source folders configured in TypeScript:

```mermaid
graph LR
    subgraph "Natural Language"
        "GlobalAlias"["'@fastgpt/*'"]
        "AppAlias"["'@/*'"]
        "TestAlias"["'@test/*'"]
    end

    subgraph "Code Entity"
        "RootTsConfig"["tsconfig.json (root)"]
        "TestTsConfig"["test/tsconfig.json"]
        "PackagesDir"["packages/*"]
        "AppSrcDir"["projects/app/src/*"]
        "TestDir"["test/*"]
    end

    "RootTsConfig" --> "TestTsConfig"
    "GlobalAlias" --> "PackagesDir"
    "AppAlias" --> "AppSrcDir"
    "TestAlias" --> "TestDir"

    "TestTsConfig" -.configures.-> "GlobalAlias"
    "TestTsConfig" -.configures.-> "AppAlias"
    "TestTsConfig" -.configures.-> "TestAlias"
```

Sources: [tsconfig.json:1-60](), [test/tsconfig.json:1-26]()

---

For more details, see:  
- [Build System and Scripts](#14.1)  
- [Testing Framework](#14.2)  
- [TypeScript Configuration](#14.3)  
- [Agent Workflows and Repository Conventions](#14.4)  
- [Data Migration Framework](#14.5)

---

