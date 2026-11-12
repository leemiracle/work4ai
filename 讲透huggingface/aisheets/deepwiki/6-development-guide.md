<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/aisheets · page 6 Development Guide · fetched 2026-10-26 -->

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.buld.yml](.github/workflows/ci.buld.yml)
- [Dockerfile](Dockerfile)
- [package.json](package.json)
- [pnpm-lock.yaml](pnpm-lock.yaml)

</details>



This document provides comprehensive guidance for developers working on the AI Sheets codebase, covering development environment setup, build processes, testing workflows, code quality standards, and deployment procedures. It serves as the primary reference for contributors and maintainers.

For information about the overall system architecture, see [Architecture](#4). For details about UI component development, see [UI Components](#5).

## Development Environment Setup

AI Sheets uses a modern JavaScript/TypeScript stack built on Qwik with Express.js backend integration. The development environment requires specific Node.js versions and uses pnpm as the package manager.

### Prerequisites and Dependencies

The application requires Node.js versions `^18.17.0 || ^20.3.0 || >=21.0.0` as specified in [package.json:4-6](). The development stack includes:

- **Package Manager**: pnpm for dependency management
- **Frontend Framework**: Qwik with SSR capabilities  
- **Backend**: Express.js server
- **Databases**: SQLite, DuckDB, and LanceDB
- **AI/ML**: Hugging Face ecosystem integration
- **Testing**: Vitest with Playwright for E2E testing

```mermaid
graph TB
    subgraph "Development Environment"
        NodeJS["Node.js 18.17+ | 20.3+ | 21+"]
        PNPM["pnpm Package Manager"]
        PlaywrightSetup["Playwright Browser Setup"]
    end
    
    subgraph "Core Dependencies"
        QwikCore["@builder.io/qwik"]
        ExpressJS["express"]
        ViteTooling["vite (Build Tool)"]
    end
    
    subgraph "AI/ML Stack"
        HFHub["@huggingface/hub"]
        HFInference["@huggingface/inference"]
        LanceDBLib["@lancedb/lancedb"]
        DuckDBLib["@duckdb/node-api"]
    end
    
    subgraph "Development Tools"
        Biome["@biomejs/biome (Linter)"]
        Vitest["vitest (Testing)"]
        TypeScript["typescript"]
    end
    
    NodeJS --> PNPM
    PNPM --> QwikCore
    PNPM --> ExpressJS  
    PNPM --> HFHub
    PNPM --> LanceDBLib
    PNPM --> Biome
    PNPM --> Vitest
    PlaywrightSetup --> Vitest
```

**Sources**: [package.json:4-6](), [package.json:70-94](), [package.json:36-69]()

### Local Development Setup

The development server runs in SSR mode using Vite with custom adapter configuration. The setup process includes automatic Playwright browser installation through the postinstall hook.

| Script | Command | Purpose |
|--------|---------|---------|
| `dev` | `vite --mode ssr` | Start development server with SSR |
| `dev.debug` | `node --inspect-brk ./node_modules/vite/bin/vite.js --mode ssr --force` | Debug development server |
| `start` | `vite --open --mode ssr` | Start dev server and open browser |

The postinstall script at [package.json:15]() handles Playwright installation with conditional skipping via `SKIP_POSTINSTALL` environment variable for Docker builds.

**Sources**: [package.json:14-15](), [package.json:22-30]()

## Build System Architecture

The build system uses Qwik's multi-target compilation approach with Vite as the underlying bundler. The system supports both client-side and server-side rendering with separate build targets.

### Build Targets and Output

```mermaid
flowchart TD
    SourceCode["Source Code (TypeScript/Qwik)"]
    
    subgraph "Build Commands"
        BuildMain["npm run build"]
        BuildClient["npm run build.client"]  
        BuildPreview["npm run build.preview"]
        BuildServer["npm run build.server"]
        BuildTypes["npm run build.types"]
    end
    
    subgraph "Build Outputs"
        DistClient["dist/ (Client Bundle)"]
        ServerBundle["server/ (Express Server)"]
        TypesOutput["Type Checking Output"]
    end
    
    SourceCode --> BuildMain
    BuildMain --> BuildClient
    BuildMain --> BuildServer
    
    BuildClient --> DistClient
    BuildServer --> ServerBundle
    BuildTypes --> TypesOutput
    
    BuildPreview --> DistClient
```

The primary build command `qwik build` orchestrates multiple compilation targets:

- **Client Build**: `vite build` - Creates optimized client bundle in `dist/`
- **Server Build**: `vite build -c adapters/express/vite.config.ts` - Compiles Express adapter
- **Preview Build**: `vite build --ssr src/entry.preview.tsx` - Preview deployment target
- **Type Checking**: `tsc --incremental --noEmit` - TypeScript validation without output

**Sources**: [package.json:16-21]()

### Production Deployment

The production server runs the compiled Express application using `node server/entry.express` as specified in [package.json:29](). The serve command directly executes the built server without development tooling.

**Sources**: [package.json:29]()

## Testing Strategy

The testing framework uses Vitest as the primary test runner with Playwright integration for end-to-end testing. The configuration supports both unit testing and UI-driven testing workflows.

### Test Execution Commands

| Command | Purpose | Configuration |
|---------|---------|---------------|
| `test` | `vitest` | Run all tests |
| `test.unit.ui` | `vitest --ui` | Interactive test UI |

The test setup includes automatic Playwright installation through the postinstall hook, ensuring browser dependencies are available for E2E tests. The `@vitest/ui` package provides a web-based test interface for development.

```mermaid
graph LR
    TestCommand["pnpm test"]
    
    subgraph "Test Execution"
        Vitest["vitest"]
        PlaywrightTests["Playwright E2E Tests"]
        VitestUI["@vitest/ui Interface"]
    end
    
    subgraph "Browser Automation"  
        ChromiumBrowser["Chromium"]
        WebDrivers["Browser Drivers"]
    end
    
    TestCommand --> Vitest
    Vitest --> PlaywrightTests
    PlaywrightTests --> ChromiumBrowser
    PlaywrightTests --> WebDrivers
    VitestUI --> Vitest
```

**Sources**: [package.json:31-32](), [package.json:53](), [package.json:88-89]()

## Code Quality and Linting

Code quality is maintained through Biome, a modern linter and formatter that replaces traditional ESLint/Prettier setups. The project also includes TypeScript ESLint configuration for additional type-aware linting rules.

### Biome Configuration

The primary code quality tools are:

- **Linting**: `biome lint . --write` - Lint and auto-fix issues
- **Formatting**: `biome format . --write` - Format code according to style rules  
- **Check Mode**: `biome lint .` and `biome format .` - Validation without changes

### Git Hooks Integration

Husky is configured to run pre-commit hooks ensuring code quality standards. The prepare script sets up git hooks automatically during development setup.

```mermaid
graph TD
    DevCommit["Developer Commit"]
    
    subgraph "Pre-commit Hooks"
        HuskyHook["husky"]
        BiomeLint["biome lint --write"]
        BiomeFormat["biome format --write"]  
    end
    
    subgraph "TypeScript Validation"
        TSLint["@typescript-eslint/eslint-plugin"]
        TSParser["@typescript-eslint/parser"]
    end
    
    DevCommit --> HuskyHook
    HuskyHook --> BiomeLint
    HuskyHook --> BiomeFormat
    BiomeLint --> TSLint
    TSLint --> TSParser
```

**Sources**: [package.json:24-27](), [package.json:34](), [package.json:58](), [package.json:123-128]()

## CI/CD Pipeline Architecture

The continuous integration pipeline is implemented using GitHub Actions with separate build and Docker deployment workflows. The pipeline supports multi-architecture builds and environment-specific deployments.

### Build Workflow

The build job runs on Ubuntu and executes the complete test and build cycle:

```mermaid
sequenceDiagram
    participant GH as "GitHub Actions"
    participant Ubuntu as "ubuntu-latest"
    participant PNPM as "pnpm@10"
    participant Node as "Node.js@20"
    
    GH->>Ubuntu: Checkout code
    Ubuntu->>PNPM: Setup pnpm v10
    PNPM->>Node: Setup Node.js 20 with cache
    Node->>PNPM: Install dependencies
    PNPM->>Ubuntu: Run tests (continue-on-error)
    Ubuntu->>PNPM: Build application
```

The workflow executes these commands in sequence:
1. `pnpm install` - Install dependencies
2. `pnpm test` - Run test suite (non-blocking)
3. `pnpm build` - Build for production

**Sources**: [.github/workflows/ci.buld.yml:1-35]()

### Docker Deployment Strategy  

The Docker workflow implements environment-specific deployment with multi-architecture support:

| Branch/Tag | Image | Platforms | Tag |
|------------|-------|-----------|-----|
| `main` | `aisheets/sheets` | `linux/amd64,linux/arm64` | `dev` |
| `stable` | `aisheets/sheets` | `linux/amd64,linux/arm64` | `latest` |
| `v*` tags | `aisheets/sheets` | `linux/amd64,linux/arm64` | version |
| Other branches | `aisheets/sheets-dev` | `linux/amd64` | branch name |

The deployment logic uses environment variable conditions to determine the target configuration:

```mermaid
flowchart TD
    TriggerPush["Git Push/Tag"]
    
    subgraph "Branch Detection"
        IsMain["IS_MAIN: github.ref == 'refs/heads/main'"]
        IsRelease["IS_RELEASE: startsWith(github.ref, 'refs/tags/v') || github.ref == 'refs/heads/stable'"]
        IsOther["Other Branches"]
    end
    
    subgraph "Docker Configuration"
        MainConfig["aisheets/sheets:dev<br/>linux/amd64,linux/arm64"]
        ReleaseConfig["aisheets/sheets:version<br/>linux/amd64,linux/arm64"]  
        DevConfig["aisheets/sheets-dev:branch<br/>linux/amd64"]
    end
    
    TriggerPush --> IsMain
    TriggerPush --> IsRelease
    TriggerPush --> IsOther
    
    IsMain --> MainConfig
    IsRelease --> ReleaseConfig
    IsOther --> DevConfig
```

**Sources**: [.github/workflows/ci.buld.yml:36-96](), [.github/workflows/ci.buld.yml:56-71]()

## Docker Development and Deployment

The Docker configuration uses a multi-stage build approach optimizing for both development convenience and production efficiency. The build process handles native dependencies and browser automation requirements.

### Multi-Stage Build Process

```mermaid
flowchart TD
    subgraph "Build Stage (node:22-slim)"
        BuildBase["Base: node:22-slim"]
        BuildDeps["Install: sqlite3, build-essential, python3"]
        PnpmInstall["pnpm install --frozen-lockfile"]
        PnpmBuild["pnpm build"]
    end
    
    subgraph "Production Stage (node:22-slim)"
        ProdBase["Base: node:22-slim"]  
        CopyArtifacts["Copy: node_modules, server/, dist/"]
        PlaywrightSetup["Install: playwright chromium"]
        ExposePort["Expose: 3000"]
        StartApp["CMD: node server/entry.express"]
    end
    
    BuildBase --> BuildDeps
    BuildDeps --> PnpmInstall
    PnpmInstall --> PnpmBuild
    
    PnpmBuild --> CopyArtifacts
    CopyArtifacts --> PlaywrightSetup
    PlaywrightSetup --> ExposePort
    ExposePort --> StartApp
```

### Build Optimizations

The build stage includes several optimizations:

- **Skip Postinstall**: `ENV SKIP_POSTINSTALL=1` prevents Playwright installation during build
- **Memory Allocation**: `ENV NODE_OPTIONS="--max-old-space-size=4096"` increases heap size
- **Frozen Lockfile**: `--frozen-lockfile` ensures reproducible builds
- **Playwright Optimization**: Browser installation only in production stage

The production stage configures Playwright for headless operation:
- `PLAYWRIGHT_BROWSERS_PATH=/home/node/ms-playwright` sets browser location
- `playwright install-deps && playwright install chromium --only-shell` installs minimal browser setup

**Sources**: [Dockerfile:1-61]()

## Development Workflow

The typical development workflow integrates the build system, testing framework, and code quality tools into an efficient development cycle.

### Local Development Cycle

```mermaid
graph TD
    StartDev["pnpm dev"]
    
    subgraph "Development Server"
        ViteSSR["vite --mode ssr"]
        HotReload["Hot Module Replacement"]
        TypeCheck["TypeScript Checking"]
    end
    
    subgraph "Code Quality Checks"
        BiomeLint["pnpm lint"]
        BiomeFormat["pnpm fmt"]  
        TestSuite["pnpm test"]
    end
    
    subgraph "Build Verification"
        BuildCheck["pnpm build"]
        ServeTest["pnpm serve"]
    end
    
    StartDev --> ViteSSR
    ViteSSR --> HotReload
    ViteSSR --> TypeCheck
    
    HotReload --> BiomeLint
    BiomeLint --> BiomeFormat
    BiomeFormat --> TestSuite
    TestSuite --> BuildCheck
    BuildCheck --> ServeTest
```

### Pre-commit Workflow

The Husky pre-commit hooks ensure code quality before commits:

1. **Formatting**: `biome format . --write` - Auto-format code
2. **Linting**: `biome lint . --write` - Fix linting issues
3. **Type Checking**: TypeScript validation via ESLint rules

**Sources**: [package.json:22-34]()

## Contribution Guidelines

Contributors should follow the established development patterns and quality standards maintained through the automated tooling and CI pipeline.

### Development Standards

- **Node.js Version**: Use supported versions specified in [package.json:4-6]()
- **Package Manager**: Use pnpm exclusively for consistent dependency resolution
- **Code Style**: Follow Biome formatting and linting rules
- **Testing**: Ensure test coverage for new features using Vitest
- **Type Safety**: Maintain TypeScript strict mode compliance

### Build Verification

Before submitting contributions, verify the complete build process:

1. `pnpm install` - Install dependencies
2. `pnpm lint` - Check code quality
3. `pnpm test` - Run test suite
4. `pnpm build` - Verify production build
5. `pnpm serve` - Test built application

The CI pipeline will automatically validate these steps, but local verification prevents build failures and accelerates the review process.

**Sources**: [package.json:14-34](), [.github/workflows/ci.buld.yml:25-33]()