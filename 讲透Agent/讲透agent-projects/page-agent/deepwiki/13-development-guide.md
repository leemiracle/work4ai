<!-- source: DeepWiki mcp.deepwiki.com · repo alibaba/page-agent · page 13 Development Guide · fetched 2026-10-29 -->

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.github/workflows/deploy-website.yml](.github/workflows/deploy-website.yml)
- [.github/workflows/main-ci.yml](.github/workflows/main-ci.yml)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [.gitignore](.gitignore)
- [AGENTS.md](AGENTS.md)
- [CLAUDE.md](CLAUDE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)

</details>



This document provides high-level guidance for contributors setting up a local development environment and understanding the core development workflows for the PageAgent project. It covers repository setup, build processes, feature development patterns, and quality assurance practices.

For information about the monorepo package structure, see [Monorepo Structure](#2). For deployment and publishing workflows, see [Deployment and Distribution](#14). For general contribution guidelines and project conventions, refer to [CONTRIBUTING.md]().

## Purpose and Scope

The PageAgent development environment is designed as a source-first monorepo to facilitate rapid iteration across packages. This guide serves as the entry point for developers to understand how to interact with the codebase, run the system locally, and extend its capabilities while maintaining strict module boundaries.

## Prerequisites and Environment Setup

The project requires a modern Node.js environment. The release pipeline specifically targets Node.js version 24. [ .github/workflows/release.yml:23-23]()

- **Node.js**: Version 24 is used in CI and release workflows. [ .github/workflows/ci.yml:20-20](), [ .github/workflows/release.yml:23-23]()
- **Package Manager**: `npm >= 11`. [ .github/workflows/release.yml:28-28]()
- **Workflow**: Contributors should use `npm ci` for clean dependency installation. [ .github/workflows/ci.yml:24-24]()

For detailed installation steps and environment troubleshooting, see [Development Setup](#13.1).

**Sources:** [ .github/workflows/ci.yml:17-24](), [ .github/workflows/release.yml:20-31]()

## Development Environment Architecture

### System to Code Mapping

The following diagram bridges high-level system components to their specific locations and implementation classes within the codebase.

```mermaid
graph TB
    subgraph "Natural Language Space (Systems)"
        CORE_SYS["Core Agent Logic"]
        LLM_SYS["LLM Interaction"]
        DOM_SYS["DOM Controller"]
        UI_SYS["User Interface"]
        EXT_SYS["Browser Extension"]
    end
    
    subgraph "Code Entity Space (Implementation)"
        CORE_CLS["PageAgentCore<br/>packages/core/src/PageAgentCore.ts"]
        LLM_CLS["LLM Client<br/>packages/llms/src/index.ts"]
        PC_CLS["PageController<br/>packages/page-controller/src/PageController.ts"]
        UI_CLS["Panel Component<br/>packages/ui/src/"]
        EXT_PKG["Extension Contexts<br/>packages/extension/"]
    end
    
    CORE_SYS -.-> ["Associates with"] CORE_CLS
    LLM_SYS -.-> ["Associates with"] LLM_CLS
    DOM_SYS -.-> ["Associates with"] PC_CLS
    UI_SYS -.-> ["Associates with"] UI_CLS
    EXT_SYS -.-> ["Associates with"] EXT_PKG
    
    CORE_CLS --> LLM_CLS
    CORE_CLS --> PC_CLS
    CORE_CLS --> UI_CLS
```

**Sources:** [AGENTS.md:36-44](), [AGENTS.md:93-93](), [AGENTS.md:102-102](), [AGENTS.md:110-110](), [AGENTS.md:51-55]()

### Monorepo Workflow

The project uses npm workspaces. During development, library `package.json` exports point directly to `src/*.ts` files, enabling live-reloading across the entire stack. [AGENTS.md:33-34](). A custom script `scripts/pre-publish.js` manages the transition from source-first to distribution-ready packages by swapping `publishConfig` fields. [AGENTS.md:34-34]()

**Sources:** [AGENTS.md:31-47]()

## Development Workflows

Contributors primarily interact with the codebase through a set of standardized npm scripts. These scripts handle everything from starting the documentation website to building the Chrome extension.

| Command | Purpose |
|---------|---------|
| `npm start` | Starts the website dev server for testing the core agent in a browser environment. [AGENTS.md:21-21]() |
| `npm run build` | Compiles all packages for production. [AGENTS.md:22-22]() |
| `npm run build:libs` | Specifically builds the library packages (core, llms, etc.). [AGENTS.md:23-23]() |
| `npm run build:ext` | Builds and zips the browser extension package. [AGENTS.md:24-24]() |
| `npm run typecheck` | Runs TypeScript compiler checks across all packages. [AGENTS.md:25-25]() |
| `npm run lint` | Runs ESLint to ensure code quality. [AGENTS.md:27-27]() |

For a complete reference of all available scripts and how to configure local development, see [Development Workflows](#13.2).

**Sources:** [AGENTS.md:18-28]()

## Adding Features

Adding new capabilities typically involves a bottom-up approach: starting with DOM actions in the `page-controller`, exposing them as tools in `core`, and finally reflecting them in the UI.

### Feature Implementation Flow

```mermaid
graph LR
    subgraph "Feature: New Browser Tool"
        A["1. Implement Action"]
        B["2. Expose in Controller"]
        C["3. Register Tool"]
    end
    
    subgraph "Code Entity Space"
        ACT["packages/page-controller/src/actions.ts"]
        PC["packages/page-controller/src/PageController.ts"]
        TOOL["packages/core/src/tools/index.ts"]
    end
    
    A --> ["Modify"] ACT
    B --> ["Modify"] PC
    C --> ["Modify"] TOOL
    
    ACT -.->|internal logic| PC
    PC -.->|DOM interface| TOOL
```

**Guidelines:**
- **DOM Ops**: New browser interactions must first be added to `packages/page-controller/src/actions.ts`. [AGENTS.md:125-125]()
- **Agent Tools**: Tools are defined in `packages/core/src/tools/index.ts` and should delegate DOM work to the `PageController`. [AGENTS.md:119-121]()

For detailed implementation patterns and module boundary rules, see [Adding Features](#13.3).

**Sources:** [AGENTS.md:115-128]()

## Testing and Quality

The project maintains high standards for code quality, including strict rules against "vibe coding" (AI-generated code without oversight) for core logic.

- **Unit Testing**: Powered by Vitest. Tests are co-located with source files (e.g., `src/foo.test.ts`). [AGENTS.md:131-132]()
- **Live Tests**: Tests hitting real external APIs are named `*.live.test.ts` and excluded from standard CI runs. [AGENTS.md:135-135]()
- **AI Policy**: AI assistance is recommended for UI and tests, but **not allowed** for the core library or extension logic. [CONTRIBUTING.md:27-33]()
- **Traceability**: Predictability and error visibility are prioritized over raw success rates. [AGENTS.md:150-152]()

For information on running tests, writing live API tests, and linting conventions, see [Testing and Quality](#13.4).

**Sources:** [AGENTS.md:129-143](), [CONTRIBUTING.md:18-40](), [ .github/workflows/ci.yml:26-29]()

## Child Pages
- [Development Setup](#13.1) — Instructions for cloning, installing dependencies, and running the dev server
- [Development Workflows](#13.2) — Document npm scripts for development: start, build, dev:ext, dev:demo, lint
- [Adding Features](#13.3) — Guidelines for adding new agent tools, page controller actions, and maintaining module boundaries
- [Testing and Quality](#13.4) — Document testing approaches, linting, code formatting, and commit conventions

---

