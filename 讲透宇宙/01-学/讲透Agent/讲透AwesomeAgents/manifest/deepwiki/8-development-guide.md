<!-- source: DeepWiki mcp.deepwiki.com · repo mnfst/manifest · page 8 Development Guide · fetched 2026-10-26 -->

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.changeset/README.md](.changeset/README.md)
- [.changeset/config.json](.changeset/config.json)
- [.github/dependabot.yml](.github/dependabot.yml)
- [.gitignore](.gitignore)
- [.husky/pre-commit](.husky/pre-commit)
- [.prettierrc](.prettierrc)
- [CLAUDE.md](CLAUDE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [LICENSE](LICENSE)
- [README.md](README.md)
- [eslint.config.mjs](eslint.config.mjs)
- [package-lock.json](package-lock.json)
- [package.json](package.json)
- [packages/backend/package.json](packages/backend/package.json)
- [turbo.json](turbo.json)

</details>



This guide provides an overview of the development practices, infrastructure, and workflows for the Manifest codebase. Manifest is built as a TypeScript monorepo using **npm workspaces**, featuring a NestJS backend and a SolidJS frontend.

For detailed instructions on specific areas, please refer to the following child pages:

*   [Environment Setup](#8.1) — Local development prerequisites (Node.js 24, Docker, PostgreSQL 16), `MANIFEST_MODE=cloud` requirements, and monorepo build pipeline.
*   [Testing Infrastructure](#8.2) — Unit, E2E, and smoke testing suites using Jest and Vitest across the monorepo.
*   [CI/CD and Release Process](#8.3) — GitHub Actions workflows, Turborepo orchestration, and automated versioning with Changesets.

## Monorepo Structure

The codebase is organized into distinct packages to separate concerns while sharing logic through a common library. The monorepo is managed by **Turborepo** [package.json:25-25]().

| Package Path | Entity Name | Description |
|:---|:---|:---|
| `packages/backend` | `manifest-backend` | NestJS server handling routing, analytics, and OTLP ingestion [packages/backend/package.json:2-2](). |
| `packages/frontend` | `manifest-frontend` | SolidJS dashboard for workspace management and monitoring [package.json:31-31](). |
| `packages/shared` | `manifest-shared` | Shared TypeScript types, schemas, and utility functions [packages/shared/package.json:2-2](). |
| `packages/wingman` | `manifest-wingman` | Dev-only gateway tester for agent impersonation [CONTRIBUTING.md:144-146](). |

Sources: [package.json:29-34](), [CLAUDE.md:62-66](), [CONTRIBUTING.md:24-34]()

## Development Workflow Overview

Development typically involves running the backend in `cloud` mode to utilize a PostgreSQL database [CLAUDE.md:13-15](). Every development session should use a **fresh PostgreSQL database** via Docker to avoid cross-run data pollution and intermittent failures [CLAUDE.md:15-32]().

### From Code to Deployment

The following diagram bridges the natural language development concepts to the specific code entities and scripts used in the workflow.

**Development Lifecycle Mapping**
```mermaid
graph TD
    subgraph "Natural Language Space"
        "Developer"
        "Pull Request"
        "Release"
    end

    subgraph "Code Entity Space"
        ["npm workspaces"]
        ["turbo build"]
        ["npm test"]
        ["npx changeset"]
        
        subgraph "Backend (NestJS)"
            ["packages/backend/src/main.ts"]
            ["DatabaseSeederService"]
        end

        subgraph "Frontend (SolidJS)"
            ["vite build"]
            ["packages/frontend/dist/"]
        end
    end

    "Developer" --> ["npm workspaces"]
    ["npm workspaces"] --> ["turbo build"]
    ["npm workspaces"] --> ["npm test"]
    ["turbo build"] --> ["packages/backend/src/main.ts"]
    ["turbo build"] --> ["vite build"]
    "Pull Request" --> ["npx changeset"]
    ["npx changeset"] --> "Release"
    ["DatabaseSeederService"] --> ["packages/backend/src/main.ts"]
```
Sources: [package.json:36-48](), [CLAUDE.md:60-116](), [CONTRIBUTING.md:38-48]()

## System Verification

Manifest employs a multi-layered testing strategy to ensure reliability. Tests are run via Turborepo to leverage caching and parallelization [package.json:39-39]().

**Verification Flow**
```mermaid
graph LR
    subgraph "Testing Layers"
        "Unit Tests"
        "E2E Integration"
        "Linting"
    end

    subgraph "Code Entities"
        ["Jest (Backend)"]
        ["Vitest (Frontend)"]
        ["packages/backend/test/"]
        ["eslint.config.mjs"]
    end

    "Unit Tests" --> ["Jest (Backend)"]
    "Unit Tests" --> ["Vitest (Frontend)"]
    "E2E Integration" --> ["packages/backend/test/"]
    "Linting" --> ["eslint.config.mjs"]
```
Sources: [package.json:39-42](), [packages/backend/package.json:10-12](), [CLAUDE.md:54-60]()

### Key Development Commands

| Command | Scope | Purpose |
|:---|:---|:---|
| `npm run dev` | Frontend/Wingman | Starts the dev servers for frontend and the Wingman tester [package.json:37-37](). |
| `npm run build` | Global | Compiles all packages via Turborepo [package.json:38-38](). |
| `npm test` | Global | Runs all unit tests across the monorepo [package.json:39-39](). |
| `npm run test:e2e` | Backend | Runs API integration tests against a live PostgreSQL DB [packages/backend/package.json:12-12](). |
| `npx changeset` | Release | Generates a new version bump entry for the release process [package.json:44-44](). |
| `npm run lint` | Global | Runs ESLint across shared, backend, frontend, and wingman [package.json:42-42](). |

For details on setting up your local machine, see [Environment Setup](#8.1).
For details on the testing suites, see [Testing Infrastructure](#8.2).
For details on how changes reach production via Docker, see [CI/CD and Release Process](#8.3).

---

