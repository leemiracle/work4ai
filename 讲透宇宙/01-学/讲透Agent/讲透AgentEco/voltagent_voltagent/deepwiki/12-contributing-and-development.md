<!-- source: DeepWiki mcp.deepwiki.com · repo voltagent/voltagent · page 12 Contributing and Development · fetched 2026-10-27 -->

# Contributing and Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/prerelease.yml](.github/workflows/prerelease.yml)
- [.github/workflows/pull-request.yml](.github/workflows/pull-request.yml)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [examples/with-google-ai/package.json](examples/with-google-ai/package.json)
- [examples/with-google-vertex-ai/package.json](examples/with-google-vertex-ai/package.json)
- [examples/with-groq-ai/package.json](examples/with-groq-ai/package.json)
- [examples/with-jwt-auth/src/index.ts](examples/with-jwt-auth/src/index.ts)
- [examples/with-mcp/package.json](examples/with-mcp/package.json)
- [examples/with-nextjs/package.json](examples/with-nextjs/package.json)
- [examples/with-playwright/src/index.ts](examples/with-playwright/src/index.ts)
- [package.json](package.json)
- [packages/core/package.json](packages/core/package.json)
- [packages/core/src/utils/message-helpers.spec.ts](packages/core/src/utils/message-helpers.spec.ts)
- [packages/core/src/utils/message-helpers.ts](packages/core/src/utils/message-helpers.ts)
- [pnpm-lock.yaml](pnpm-lock.yaml)
- [pnpm-workspace.yaml](pnpm-workspace.yaml)
- [website/docs/utils/message-helpers.md](website/docs/utils/message-helpers.md)

</details>



This document provides comprehensive guidelines for contributing to VoltAgent and developing new packages within the framework. It covers the development environment setup, monorepo architecture, development workflow, package creation, testing strategies, and CI/CD processes.

For information about using VoltAgent in your applications, see [Getting Started](#1.1). For API documentation, see [API Reference](#10). For deployment and production considerations, see [VoltOps Platform](#7.1).

## Development Environment Setup

VoltAgent uses a monorepo architecture managed with pnpm workspaces and Lerna. The development environment requires Node.js 20+ and pnpm 8+.

### Prerequisites

The development environment requires specific tools and versions as defined in [package.json:40-43]():

| Tool | Version Requirement | Defined In |
|------|---------------------|------------|
| Node.js | `>=20` | [package.json:41]() |
| pnpm | `>=8` | [package.json:42]() |

**Sources:** [package.json:40-43]()

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/voltagent/voltagent.git
cd voltagent

# Install dependencies (uses pnpm workspaces)
pnpm install

# Build all packages (uses lerna)
pnpm build:all

# Run tests to verify setup
pnpm test:all
```

#### Development Setup Flow

```mermaid
graph TB
    CLONE["git clone voltagent"]
    INSTALL["pnpm install"]
    BUILD["pnpm build:all"]
    TEST["pnpm test:all"]
    
    subgraph "pnpm install execution"
        WORKSPACE["Read pnpm-workspace.yaml"]
        DEPS["Install workspace dependencies"]
        LINK["Link workspace packages"]
    end
    
    subgraph "pnpm build:all execution"
        LERNA_BUILD["lerna run build"]
        SCOPE["--scope @voltagent/*"]
        IGNORE["--ignore @voltagent/sdk"]
        CONCURRENCY["--concurrency 1"]
    end
    
    subgraph "pnpm test:all execution"
        LERNA_TEST["lerna run test"]
        STREAM["--stream"]
        TEST_SCOPE["--scope @voltagent/*"]
    end
    
    CLONE --> INSTALL
    INSTALL --> WORKSPACE
    WORKSPACE --> DEPS
    DEPS --> LINK
    LINK --> BUILD
    BUILD --> LERNA_BUILD
    LERNA_BUILD --> SCOPE
    SCOPE --> IGNORE
    IGNORE --> CONCURRENCY
    CONCURRENCY --> TEST
    TEST --> LERNA_TEST
    LERNA_TEST --> STREAM
    STREAM --> TEST_SCOPE
```

The `pnpm install` command reads [pnpm-workspace.yaml:1-7]() to identify workspace packages and installs dependencies for all packages in `packages/*` and `examples/*`. The `pnpm build:all` script (defined in [package.json:63]()) uses Lerna to build packages in dependency order with `--concurrency 1` to avoid race conditions.

**Sources:** [package.json:40-43](), [package.json:56-95](), [pnpm-workspace.yaml:1-7]()

## Monorepo Architecture

### Workspace Structure

The VoltAgent monorepo follows a structured workspace layout defined in `pnpm-workspace.yaml`:

#### VoltAgent Monorepo Structure

```mermaid
graph TB
    subgraph "Root Level"
        ROOT["voltagent (root)"]
        CONFIG["Configuration Files"]
        SCRIPTS["Build Scripts"]
    end
    
    subgraph "Workspace Packages"
        PACKAGES["packages/*"]
        EXAMPLES["examples/*"]
        ARCHIVE["archive/** (excluded)"]
    end
    
    subgraph "Core Packages"
        CORE["@voltagent/core"]
        CLI["@voltagent/cli"] 
        LOGGER["@voltagent/logger"]
        SERVCORE["@voltagent/server-core"]
        SERVHONO["@voltagent/server-hono"]
    end
    
    subgraph "Storage Packages"
        POSTGRES["@voltagent/postgres"]
        SUPABASE["@voltagent/supabase"]
        LIBSQL["@voltagent/libsql"]
    end
    
    subgraph "Development Tools"
        CREATE["create-voltagent-app"]
        DOCSMCP["@voltagent/docs-mcp"]
        INTERNAL["@voltagent/internal"]
    end
    
    subgraph "Example Applications"
        EXAMPLES_APPS["voltagent-example-*"]
        INTEGRATION_EXAMPLES["Integration Examples"]
    end
    
    ROOT --> CONFIG
    ROOT --> SCRIPTS
    PACKAGES --> CORE
    PACKAGES --> CLI
    PACKAGES --> LOGGER
    PACKAGES --> SERVCORE
    PACKAGES --> SERVHONO
    PACKAGES --> POSTGRES
    PACKAGES --> SUPABASE
    PACKAGES --> LIBSQL
    PACKAGES --> CREATE
    PACKAGES --> DOCSMCP
    PACKAGES --> INTERNAL
    EXAMPLES --> EXAMPLES_APPS
    EXAMPLES --> INTEGRATION_EXAMPLES
    
    CORE --> SERVCORE
    SERVHONO --> SERVCORE
    POSTGRES --> CORE
    SUPABASE --> CORE
    LIBSQL --> CORE
```

**Sources:** [pnpm-workspace.yaml:1-8](), [package.json:100-103]()

### Package Management Tools

The monorepo uses several complementary tools for package management:

- **pnpm**: Workspace management and dependency installation
- **lerna**: Cross-package operations, builds, and publishing
- **changesets**: Version management and changelog generation
- **syncpack**: Dependency version synchronization

Key management scripts include `bootstrap`, `build:all`, `version-packages`, and `changeset publish`.

**Sources:** [package.json:31](), [package.json:64-66](), [package.json:68](), [package.json:92](), [package.json:98]()

## Development Workflow

### Development Scripts and Tools

VoltAgent provides extensive npm scripts in [package.json:56-96]() for common development tasks. These scripts are grouped by function:

| Script Category | Script Name | Command | Purpose |
|----------------|-------------|---------|---------|
| **Development** | `pnpm dev` | `lerna run dev --ignore voltagent-example-*` | Start dev servers for packages |
| **Building** | `pnpm build` | `lerna run build --ignore @voltagent/sdk...` | Build all packages |
| | `pnpm build:all` | `lerna run build --scope @voltagent/* --scope create-voltagent-app --concurrency 1` | Build all packages sequentially |
| **Testing** | `pnpm test` | `lerna run test --stream` | Run all tests |
| | `pnpm test:all` | `lerna run test --stream --scope @voltagent/*` | Run scoped package tests |
| | `pnpm test:coverage` | `pnpm test -- -- --coverage` | Generate coverage reports |
| **Linting** | `pnpm lint` | `biome check .` | Lint codebase |
| | `pnpm lint:ci` | `biome ci .` | CI-optimized linting |
| | `pnpm lint:fix` | `biome check . --apply` | Auto-fix lint issues |
| **Validation** | `pnpm publint:all` | `lerna run publint --scope @voltagent/*` | Validate package.json exports |
| | `pnpm attw:all` | `lerna run attw --scope @voltagent/*` | Check TypeScript types |
| | `pnpm sp lint` | `syncpack` | Check dependency version consistency |
| **Versioning** | `pnpm changeset` | `changeset` | Create changeset file |
| | `pnpm version-packages` | `pnpm changeset version && pnpm i --lockfile-only...` | Bump versions |
| **Maintenance** | `pnpm nuke` | Remove all node_modules, builds, lockfiles | Complete cleanup |
| | `pnpm coffee` | `pnpm nuke && pnpm i && pnpm build:all` | Fresh install and build |

#### Development Workflow with Package Scripts

```mermaid
graph TB
    subgraph "package.json root scripts"
        DEV["pnpm dev"]
        BUILD["pnpm build:all"]
        LINT["pnpm lint:ci"]
        TEST["pnpm test:all"]
    end
    
    subgraph "lerna execution"
        LERNA_DEV["lerna run dev"]
        LERNA_BUILD["lerna run build<br/>--scope @voltagent/*<br/>--concurrency 1"]
        LERNA_TEST["lerna run test<br/>--stream"]
    end
    
    subgraph "package-level scripts"
        CORE_BUILD["packages/core:<br/>tsup"]
        CORE_TEST["packages/core:<br/>vitest"]
        HONO_BUILD["packages/server-hono:<br/>tsup"]
        CLI_BUILD["packages/cli:<br/>tsup"]
    end
    
    subgraph "quality tools"
        BIOME["biome ci ."]
        SYNCPACK["syncpack lint"]
        PUBLINT["lerna run publint"]
        ATTW["lerna run attw"]
    end
    
    DEV --> LERNA_DEV
    BUILD --> LERNA_BUILD
    TEST --> LERNA_TEST
    
    LERNA_BUILD --> CORE_BUILD
    LERNA_BUILD --> HONO_BUILD
    LERNA_BUILD --> CLI_BUILD
    
    LERNA_TEST --> CORE_TEST
    
    LINT --> BIOME
    LINT --> SYNCPACK
    BUILD --> PUBLINT
    BUILD --> ATTW
```

**Sources:** [package.json:56-96](), [packages/core/package.json:65-76]()

### Code Quality Enforcement

The development workflow enforces code quality through multiple automated checks:

#### Linting and Formatting
- **Biome**: Primary linter and formatter with `biome check .` and `biome ci .`
- **Prettier**: Markdown formatting for documentation
- **lint-staged**: Pre-commit hooks for automatic formatting

#### Type Safety
- **TypeScript**: Strict type checking across all packages
- **publint**: Package.json validation for publishing
- **attw**: "Are The Types Wrong" checking for TypeScript exports

#### Dependency Management
- **syncpack**: Ensures consistent dependency versions across packages
- **Lerna**: Manages inter-package dependencies and build order

**Sources:** [package.json:73-77](), [package.json:48-55](), [package.json:89-90](), [package.json:92]()

### Branch and Release Strategy

The project uses a structured branching strategy:

- **main**: Stable releases, triggers production publishing
- **next**: Prerelease branch for beta versions
- **feature branches**: Development work via pull requests

Version management uses Changesets for automated versioning and changelog generation.

**Sources:** [.github/workflows/release.yml:3-7](), [.github/workflows/prerelease.yml:3-7]()

## Package Development

### Creating New Packages

New VoltAgent packages should follow the established patterns and structure. The `create-voltagent-app` tool demonstrates the standard package creation approach.

### Package Structure Standards

Each VoltAgent package follows a consistent structure with required files and scripts. The `@voltagent/core` package demonstrates the canonical structure.

#### Required Package Files

```
packages/[package-name]/
├── package.json          # Package manifest with exports, scripts, dependencies
├── tsconfig.json         # TypeScript configuration
├── tsup.config.ts        # Build configuration (for tsup-based packages)
├── src/
│   ├── index.ts         # Main entry point
│   └── **/*.ts          # Source files
├── dist/                 # Built output (generated, gitignored)
│   ├── index.js         # CommonJS output
│   ├── index.mjs        # ESM output
│   ├── index.d.ts       # CommonJS types
│   └── index.d.mts      # ESM types
├── CHANGELOG.md         # Package-specific changelog
└── README.md            # Package documentation
```

#### Standard package.json Scripts

All packages must implement these scripts as defined in [packages/core/package.json:65-76]():

| Script | Command | Purpose | Required |
|--------|---------|---------|----------|
| `build` | `tsup` | Build package with tsup | ✅ Yes |
| `dev` | `tsup --watch` | Development build with watch mode | ✅ Yes |
| `test` | `vitest --reporter=hanging-process --reporter=default --typecheck` | Run tests with type checking | ✅ Yes |
| `test:coverage` | `vitest run --coverage --typecheck` | Generate coverage report | ⚠️ Recommended |
| `lint` | `biome check .` | Lint package code | ✅ Yes |
| `lint:fix` | `biome check . --write` | Auto-fix lint issues | ⚠️ Recommended |
| `publint` | `publint --strict` | Validate package.json exports | ✅ Yes |
| `attw` | `attw --pack` | Validate TypeScript types export | ⚠️ Recommended |
| `typecheck` | `tsc --noEmit` | Type-check without emitting | ⚠️ Recommended |

#### Package Exports Configuration

Packages must define dual ESM/CommonJS exports in [packages/core/package.json:36-46]():

```json
{
  "exports": {
    ".": {
      "import": {
        "types": "./dist/index.d.mts",
        "default": "./dist/index.mjs"
      },
      "require": {
        "types": "./dist/index.d.ts",
        "default": "./dist/index.js"
      }
    }
  },
  "main": "dist/index.js",
  "module": "dist/index.mjs",
  "types": "dist/index.d.ts"
}
```

#### Example Package Structure: @voltagent/core

The core package demonstrates best practices with [packages/core/package.json:1-78]():

- **Peer Dependencies**: `ai`, `zod`, `@ai-sdk/provider-utils` (required by consumers)
- **Optional Peer Dependencies**: `@voltagent/logger` (runtime-optional)
- **Production Dependencies**: OpenTelemetry packages, internal utilities
- **Dev Dependencies**: Build tools (tsup), testing (vitest), types

**Sources:** [packages/core/package.json:1-78](), [packages/core/package.json:36-76]()

### Package Naming and Scoping

VoltAgent packages use the `@voltagent/` npm scope with descriptive names:

- Core functionality: `@voltagent/core`
- Server implementations: `@voltagent/server-*`
- Storage adapters: `@voltagent/postgres`, `@voltagent/supabase`
- Development tools: `@voltagent/cli`
- Utilities: `@voltagent/logger`, `@voltagent/internal`

The exception is `create-voltagent-app`, which uses no scope for easier CLI usage.

**Sources:** [packages/create-voltagent-app/package.json:2](), [packages/cli/package.json:2]()

### Provider Package Development

VoltAgent supports creating custom AI provider packages. The framework includes a provider generator and follows consistent patterns for provider integration.

## Testing Strategy

### Testing Framework and Tools

VoltAgent uses Vitest as the primary testing framework across all packages. The testing configuration is standardized in [packages/core/package.json:72-75]().

#### Test Script Configuration

```typescript
// From packages/core/package.json
{
  "scripts": {
    "test": "vitest --reporter=hanging-process --reporter=default --typecheck",
    "test:coverage": "vitest run --coverage --typecheck",
    "test:single": "vitest run --reporter=verbose"
  }
}
```

#### Test Organization and Naming

Tests follow a consistent file naming and location pattern:

| Test Type | File Pattern | Location | Example |
|-----------|-------------|----------|---------|
| Unit Tests | `*.spec.ts` | Alongside source files | [packages/core/src/utils/message-helpers.spec.ts]() |
| Integration Tests | `*.integration.spec.ts` | Package test directory | `packages/postgres/src/*.integration.spec.ts` |
| E2E Tests | `*.e2e.spec.ts` | Package test directory | `packages/server-hono/src/*.e2e.spec.ts` |

#### Example Unit Test Structure

VoltAgent unit tests use Vitest's `describe`/`it` pattern with comprehensive type checking. Example from [packages/core/src/utils/message-helpers.spec.ts:1-27]():

```typescript
import { describe, expect, it } from "vitest";
import type { UIMessage } from "ai";
import {
  isTextContent,
  extractText,
  MessageContentBuilder,
  // ... other imports
} from "./message-helpers";

describe("Message Helpers", () => {
  describe("Type Guards", () => {
    it("should identify text content", () => {
      expect(isTextContent("hello")).toBe(true);
      expect(isTextContent([])).toBe(false);
    });
  });
  
  describe("MessageContentBuilder", () => {
    it("should build simple text content", () => {
      const builder = new MessageContentBuilder();
      const content = builder.addText("hello").build();
      expect(content).toBe("hello");
    });
  });
});
```

#### Coverage Requirements

Test coverage is generated using `@vitest/coverage-v8` (defined in [package.json:62-64]()):

- **Root coverage**: `pnpm test:coverage` generates aggregate coverage
- **Package coverage**: `pnpm test:coverage` in individual packages
- **CI enforcement**: Coverage reports generated but not enforced as gate

**Sources:** [packages/core/package.json:72-75](), [packages/core/src/utils/message-helpers.spec.ts:1-27](), [package.json:62-64](), [package.json:94-97]()

### Database Integration Testing

Database packages include specialized integration tests that run against real database instances in CI/CD environments.

#### PostgreSQL Integration Test Configuration

The PostgreSQL integration tests use a containerized PostgreSQL 16 instance configured in GitHub Actions workflows. From [.github/workflows/pull-request.yml:118-131]():

```yaml
services:
  postgres:
    image: postgres:16
    env:
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
      POSTGRES_DB: voltagent_test
    ports:
      - 5432:5432
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
```

#### Conditional Test Execution

PostgreSQL tests run conditionally based on file changes to avoid unnecessary test execution. The workflow checks for changes in [.github/workflows/pull-request.yml:137-144]():

```yaml
- name: Check for PostgreSQL changes
  id: check_postgres
  run: |
    if git diff --name-only origin/main...HEAD | grep -E '^packages/postgres/'; then
      echo "postgres_changed=true" >> $GITHUB_OUTPUT
    else
      echo "postgres_changed=false" >> $GITHUB_OUTPUT
    fi
```

Tests only execute when `postgres_changed=true`, connecting to `postgresql://test:test@localhost:5432/voltagent_test` as defined in [.github/workflows/pull-request.yml:174]().

#### Integration Test Execution Flow

```mermaid
graph TB
    PR_CHANGE["Pull Request Changes"]
    CHECK_DIFF["git diff --name-only<br/>origin/main...HEAD"]
    GREP_PG["grep -E '^packages/postgres/'"]
    
    subgraph "Conditional Execution"
        CHANGED["postgres_changed=true"]
        SKIP["Skip integration tests"]
    end
    
    subgraph "PostgreSQL Service"
        PG_CONTAINER["postgres:16 container"]
        HEALTH_CHECK["pg_isready healthcheck"]
        PORT_5432["Port 5432:5432"]
    end
    
    subgraph "Test Execution"
        PNPM_INSTALL["pnpm install"]
        BUILD_CORE["pnpm build --scope @voltagent/core"]
        RUN_TESTS["npm run test:integration:ci"]
        DB_URL["DATABASE_URL=postgresql://test:test@localhost:5432/voltagent_test"]
    end
    
    PR_CHANGE --> CHECK_DIFF
    CHECK_DIFF --> GREP_PG
    GREP_PG -->|Match Found| CHANGED
    GREP_PG -->|No Match| SKIP
    
    CHANGED --> PG_CONTAINER
    PG_CONTAINER --> HEALTH_CHECK
    HEALTH_CHECK --> PORT_5432
    PORT_5432 --> PNPM_INSTALL
    PNPM_INSTALL --> BUILD_CORE
    BUILD_CORE --> RUN_TESTS
    RUN_TESTS --> DB_URL
```

**Sources:** [.github/workflows/pull-request.yml:112-175](), [.github/workflows/release.yml:64-78](), [.github/workflows/release.yml:109-114]()

## CI/CD Pipeline

### Pull Request Workflow

The PR workflow defined in [.github/workflows/pull-request.yml:1-175]() implements comprehensive quality gates with multiple parallel jobs.

#### GitHub Actions Job Matrix

| Job Name | Triggers | Node Versions | Concurrency Group | Purpose |
|----------|----------|---------------|-------------------|---------|
| `commit-lint` | Pull request events | N/A | `${{ github.ref }}-commit-lint` | Validate commit messages with `wagoid/commitlint-github-action@v5` |
| `lint` | Pull request events | 20, 22, 24 | `${{ github.ref }}-lint-${{ matrix.node-version }}` | Run `biome ci .` and `syncpack lint` |
| `build` | Pull request events | 20, 22, 24 | `${{ github.ref }}-pr-build-${{ matrix.node-version }}` | Build all packages and run `publint:all` |
| `test-packages` | Pull request events | 20 | `${{ github.ref }}-test-${{ matrix.package }}` | Test 11 packages in parallel |
| `postgres-integration` | Pull request events | 20 | `${{ github.ref }}-postgres-integration` | Run PostgreSQL integration tests (conditional) |

#### Test Package Matrix

The `test-packages` job tests 11 packages in parallel as defined in [.github/workflows/pull-request.yml:71-82]():

```yaml
strategy:
  matrix:
    package:
      - cli
      - core
      - create-voltagent-app
      - docs-mcp
      - internal
      - logger
      - postgres
      - supabase
      - voice
      - server-core
      - libsql
  fail-fast: false
```

Each package test job executes:
1. Checkout code with `actions/checkout@v4`
2. Setup pnpm with `pnpm/action-setup@v4`
3. Setup Node.js with `actions/setup-node@v4`
4. Install dependencies with `pnpm install`
5. Determine package scope (handle `create-voltagent-app` vs `@voltagent/*`)
6. Build package and dependencies with `lerna run build --scope $scope --include-dependencies`
7. Test package with `lerna run test --scope $scope`

#### Pull Request Quality Gate Flow

```mermaid
graph TB
    PR["pull_request event"]
    
    subgraph "Parallel Jobs"
        COMMITLINT["commit-lint job<br/>wagoid/commitlint-github-action@v5"]
        
        subgraph "lint job (Node 20,22,24)"
            LINT_BIOME["pnpm lint:ci<br/>(biome ci .)"]
            LINT_SYNC["pnpm sp lint<br/>(syncpack)"]
        end
        
        subgraph "build job (Node 20,22,24)"
            BUILD_INSTALL["pnpm install"]
            BUILD_ALL["pnpm build:all"]
            BUILD_PUBLINT["pnpm publint:all"]
        end
        
        subgraph "test-packages (11 packages)"
            TEST_CORE["@voltagent/core<br/>lerna run test"]
            TEST_CLI["@voltagent/cli<br/>lerna run test"]
            TEST_CREATE["create-voltagent-app<br/>lerna run test"]
            TEST_OTHERS["8 more packages..."]
        end
        
        subgraph "postgres-integration"
            PG_CHECK["Check git diff for<br/>^packages/postgres/"]
            PG_SERVICE["PostgreSQL 16 service<br/>localhost:5432"]
            PG_TEST["npm run test:integration:ci"]
        end
    end
    
    subgraph "Required Checks"
        ALL_PASS["All jobs must pass"]
        MERGE_READY["Ready to merge"]
    end
    
    PR --> COMMITLINT
    PR --> LINT_BIOME
    PR --> BUILD_INSTALL
    PR --> TEST_CORE
    PR --> PG_CHECK
    
    LINT_BIOME --> LINT_SYNC
    BUILD_INSTALL --> BUILD_ALL
    BUILD_ALL --> BUILD_PUBLINT
    
    TEST_CORE --> ALL_PASS
    TEST_CLI --> ALL_PASS
    TEST_CREATE --> ALL_PASS
    TEST_OTHERS --> ALL_PASS
    
    PG_CHECK -->|Changed| PG_SERVICE
    PG_SERVICE --> PG_TEST
    PG_TEST --> ALL_PASS
    
    COMMITLINT --> ALL_PASS
    LINT_SYNC --> ALL_PASS
    BUILD_PUBLINT --> ALL_PASS
    
    ALL_PASS --> MERGE_READY
```

**Sources:** [.github/workflows/pull-request.yml:1-175](), [.github/workflows/pull-request.yml:14-66](), [.github/workflows/pull-request.yml:67-111]()

### Release Automation

VoltAgent uses Changesets with GitHub Actions for fully automated releases. Two release workflows handle stable and prerelease publishing.

#### Release Workflow Comparison

| Aspect | Stable Release | Prerelease |
|--------|---------------|------------|
| **Workflow File** | [.github/workflows/release.yml]() | [.github/workflows/prerelease.yml]() |
| **Trigger Branch** | `main` | `next` |
| **NPM Tag** | `latest` (default) | `next` |
| **Changeset Command** | `pnpm changeset publish` | `pnpm changeset publish` (with pre mode) |
| **Version Command** | `pnpm version-packages` | `pnpm version-packages` |
| **GitHub Releases** | Created automatically | `createGithubReleases: false` |

#### Release Workflow Steps

Both workflows follow the same execution pattern defined in [.github/workflows/release.yml:78-127]():

```mermaid
graph TB
    TRIGGER["Push to main/next"]
    
    subgraph "test-packages job (parallel)"
        TEST_MATRIX["Matrix: 11 packages<br/>Node 20"]
        TEST_BUILD["lerna run build<br/>--scope $scope<br/>--include-dependencies"]
        TEST_RUN["lerna run test<br/>--scope $scope"]
    end
    
    subgraph "publish/prerelease job"
        CHECKOUT["actions/checkout@v3<br/>fetch-depth: 0"]
        SETUP_PNPM["pnpm/action-setup@v4"]
        SETUP_NODE["actions/setup-node@v4<br/>node-version: 20"]
        NPMRC["Create .npmrc<br/>//registry.npmjs.org/:_authToken"]
        
        INSTALL["pnpm install"]
        BUILD["pnpm build:all"]
        LINT["pnpm lint:ci"]
        SYNCPACK["pnpm sp lint"]
        PUBLINT["pnpm publint:all"]
        
        PG_TESTS["PostgreSQL Integration Tests<br/>npm run test:integration:ci"]
        
        CHANGESETS["changesets/action@v1<br/>version: pnpm version-packages<br/>publish: pnpm changeset publish"]
    end
    
    subgraph "PostgreSQL Service"
        PG_SERVICE["postgres:16<br/>localhost:5432<br/>DATABASE_URL=postgresql://test:test@localhost:5432/voltagent_test"]
    end
    
    TRIGGER --> TEST_MATRIX
    TEST_MATRIX --> TEST_BUILD
    TEST_BUILD --> TEST_RUN
    
    TEST_RUN --> CHECKOUT
    CHECKOUT --> SETUP_PNPM
    SETUP_PNPM --> SETUP_NODE
    SETUP_NODE --> NPMRC
    NPMRC --> INSTALL
    INSTALL --> BUILD
    BUILD --> LINT
    LINT --> SYNCPACK
    SYNCPACK --> PUBLINT
    
    PG_SERVICE --> PG_TESTS
    PUBLINT --> PG_TESTS
    PG_TESTS --> CHANGESETS
```

#### Changesets Version Bump Script

The `version-packages` script defined in [package.json:95]() executes multiple commands:

```bash
pnpm changeset version && \
pnpm i --ignore-scripts --lockfile-only --no-frozen-lockfile --reporter=ndjson --stream && \
git add pnpm-lock.yaml
```

This script:
1. Runs `changeset version` to bump package versions based on changesets
2. Updates `pnpm-lock.yaml` without running install scripts
3. Stages the updated lockfile for commit

#### Prerelease Mode

Prerelease workflow uses Changesets pre-release mode. Enter/exit commands in [package.json:81-82]():

```json
{
  "prerelease:enter": "pnpm changeset pre enter next",
  "prerelease:exit": "pnpm changeset pre exit"
}
```

When in prerelease mode, the `next` tag is automatically applied to NPM publishes.

**Sources:** [.github/workflows/release.yml:1-128](), [.github/workflows/prerelease.yml:1-147](), [package.json:81-96]()

### Quality Assurance Matrix

The CI/CD pipeline tests across multiple dimensions:

- **Node.js Versions**: 20, 22, 24 for maximum compatibility
- **Package Isolation**: Each package tested independently
- **Database Integration**: Real PostgreSQL testing in containerized environment
- **Documentation**: TSDoc link validation and completeness

**Sources:** [.github/workflows/pull-request.yml:16-18](), [.github/workflows/pull-request.yml:71-82]()

## Contributing Guidelines

### Commit Standards

VoltAgent enforces conventional commit standards using `@commitlint/config-conventional`:

- **feat**: New features
- **fix**: Bug fixes  
- **docs**: Documentation changes
- **test**: Test additions or modifications
- **chore**: Maintenance tasks

Commit messages are validated on every pull request using `wagoid/commitlint-github-action`.

**Sources:** [.github/workflows/pull-request.yml:5-13](), [package.json:14-15]()

### Development Utilities

Several utility scripts support the development workflow:

- **nuke**: Complete cleanup of node_modules, builds, and lockfiles
- **coffee**: Fresh install and build after cleanup
- **archive:deprecated**: Move deprecated packages to archive

These scripts help maintain a clean development environment and manage technical debt.

**Sources:** [package.json:60](), [package.json:70](), [package.json:78-81]()

### Documentation Standards

Documentation follows structured patterns:
- **Package README**: Each package requires comprehensive documentation
- **API Documentation**: TSDoc comments for all public APIs
- **Examples**: Working code examples in the `examples/` directory
- **Changelog**: Detailed changelog management via Changesets

The CI/CD pipeline validates documentation completeness and link integrity.

**Sources:** [.github/workflows/pull-request.yml:176-188]()

---

