<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/responsible-ai-toolbox · extra page TypeScript CI Workflows · fetched 2026-10-26 -->

# TypeScript CI Workflows

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.azure-devops/component-governance.yml](.azure-devops/component-governance.yml)
- [.github/workflows/CD.yml](.github/workflows/CD.yml)
- [.github/workflows/CI-codescan.yml](.github/workflows/CI-codescan.yml)
- [.github/workflows/CI-e2e-notebooks.yml](.github/workflows/CI-e2e-notebooks.yml)
- [.github/workflows/CI-notebook.yml](.github/workflows/CI-notebook.yml)
- [.github/workflows/CI-python.yml](.github/workflows/CI-python.yml)
- [.github/workflows/CI-rai_core_flask-pytest.yml](.github/workflows/CI-rai_core_flask-pytest.yml)
- [.github/workflows/CI-raiwidgets-pytest.yml](.github/workflows/CI-raiwidgets-pytest.yml)
- [.github/workflows/CI-typescript.yml](.github/workflows/CI-typescript.yml)
- [.github/workflows/GitHubPages.yml](.github/workflows/GitHubPages.yml)
- [.github/workflows/python-linting.yml](.github/workflows/python-linting.yml)
- [.github/workflows/release-rai-tabular.yml](.github/workflows/release-rai-tabular.yml)
- [apps/dashboard-e2e/src/describer/interpret/individualFeatureImportance/describeSubBarChart.ts](apps/dashboard-e2e/src/describer/interpret/individualFeatureImportance/describeSubBarChart.ts)
- [libs/e2e/src/lib/describer/interpretText/validateBarChart.ts](libs/e2e/src/lib/describer/interpretText/validateBarChart.ts)
- [libs/mlchartlib/src/lib/components/AccessibleChart.tsx](libs/mlchartlib/src/lib/components/AccessibleChart.tsx)
- [nx.json](nx.json)
- [package.json](package.json)
- [tsconfig.base.json](tsconfig.base.json)
- [workspace.json](workspace.json)
- [yarn.lock](yarn.lock)

</details>



This document describes the TypeScript continuous integration workflows that validate code quality, run tests, and build artifacts for the dashboard and TypeScript libraries in the Responsible AI Toolbox repository. These workflows ensure that all TypeScript and React code meets quality standards before merging.

For information about Python testing and CI, see [Python CI Workflows](#7.2.1). For deployment and release processes, see [Build and Deployment](#7.2.3) and [Release Process](#7.2.4).

## Purpose and Scope

The TypeScript CI system validates all frontend code through linting, unit testing, and end-to-end testing. The primary workflow is defined in [.github/workflows/CI-typescript.yml:1-51]() and executes on every pull request to the `main` branch. The workflow runs across multiple Node.js versions to ensure compatibility and uses the Nx build system to efficiently test and build all 14 TypeScript libraries in the monorepo.

## Workflow Trigger Configuration

The CI-typescript workflow triggers on pull requests only, distinguishing it from the CD workflow which also triggers on pushes to main:

```yaml
on:
  pull_request:
    branches: [main]
```

**Trigger Conditions:**
- Pull requests targeting the `main` branch
- All file types (no path filtering applied)
- Manual workflow dispatch not enabled

Sources: [.github/workflows/CI-typescript.yml:11-13]()

## Node.js Version Matrix

The workflow runs against multiple Node.js versions to ensure compatibility:

```mermaid
graph LR
    subgraph "CI Matrix Strategy"
        Workflow[CI-typescript Workflow]
        Node14["Node.js 14.x<br/>Legacy Support"]
        Node16["Node.js 16.x<br/>Primary Version"]
    end
    
    Workflow --> Node14
    Workflow --> Node16
    
    Node14 --> Jobs14["Linting<br/>Testing<br/>Building"]
    Node16 --> Jobs16["Linting<br/>Testing<br/>Building"]
```

Sources: [.github/workflows/CI-typescript.yml:19-21](), [package.json:42]()

## CI Pipeline Stages

The TypeScript CI pipeline executes a comprehensive validation sequence through the `yarn ci` command:

```mermaid
flowchart TD
    Start["Checkout Code<br/>actions/checkout@v4"] --> SetupNode["Setup Node.js<br/>actions/setup-node@v4"]
    SetupNode --> InstallYarn["Install Yarn<br/>npm install yarn -g"]
    InstallYarn --> YarnCI["yarn ci"]
    
    subgraph "yarn ci command"
        Install["yarn install<br/>--frozen-lock-file"] --> TestAll["yarn testall<br/>--codeCoverage"]
        TestAll --> LintAll["yarn lintall"]
        LintAll --> BuildAll["yarn buildall"]
        BuildAll --> Test["yarn test"]
        Test --> E2E["yarn e2e"]
    end
    
    YarnCI --> Install
    E2E --> UploadCoverage["Upload Artifacts<br/>unit-test-coverage"]
    E2E --> UploadE2E["Upload Artifacts<br/>e2e-screen-shot"]
    E2E --> UploadErrors["Upload Artifacts<br/>yarn-error.log"]
```

Sources: [.github/workflows/CI-typescript.yml:23-50](), [package.json:19]()

### Installation Phase

The installation phase locks dependencies to ensure reproducible builds:

**Command:** `yarn install --frozen-lock-file`

This command:
- Installs all dependencies from [yarn.lock:1-794617]()
- Fails if `package.json` and `yarn.lock` are out of sync
- Ensures exact version matching across CI runs

Sources: [package.json:19]()

### Linting Phase

The linting phase validates code quality across all libraries:

**Command:** `yarn lintall`

```mermaid
graph TB
    LintAll["yarn lintall"] --> WorkspaceLint["nx workspace-lint<br/>Validate workspace structure"]
    LintAll --> NxLint["nx run-many --target=lint --all<br/>NODE_OPTIONS=--max_old_space_size=4096"]
    LintAll --> Prettier["yarn prettier . --check<br/>Code formatting validation"]
    
    subgraph "Libraries Linted (14 total)"
        NxLint --> CoreUI["core-ui<br/>@nrwl/linter:eslint"]
        NxLint --> ErrorAnalysis["error-analysis<br/>@nrwl/linter:eslint"]
        NxLint --> ModelAssessment["model-assessment<br/>@nrwl/linter:eslint"]
        NxLint --> Others["causality, counterfactuals,<br/>fairness, interpret,<br/>interpret-text, interpret-vision,<br/>dataset-explorer, forecasting,<br/>localization, mlchartlib, e2e"]
    end
```

**ESLint Configuration:**
- Linter: `@nrwl/linter:eslint` builder
- Patterns: `**/*.js`, `**/*.jsx`, `**/*.ts`, `**/*.tsx`, `**/*.d.ts`
- Includes test files: `**/*.test.*`, `**/*.spec.*`

Sources: [package.json:31](), [workspace.json:10-28]()

### Unit Testing Phase

The unit testing phase executes Jest tests across all libraries with code coverage:

**Command:** `yarn testall --codeCoverage`

This expands to: `nx run-many --target=test --all --codeCoverage`

```mermaid
graph TB
    TestAll["nx run-many --target=test --all"] --> JestRunner["@nrwl/jest:jest builder"]
    
    subgraph "Test Execution per Library"
        JestRunner --> CoreUITest["core-ui<br/>libs/core-ui/jest.config.js<br/>coverage/libs/core-ui"]
        JestRunner --> ErrorTest["error-analysis<br/>libs/error-analysis/jest.config.js<br/>coverage/libs/error-analysis"]
        JestRunner --> DashboardTest["dashboard<br/>apps/dashboard/jest.config.js<br/>coverage/apps/dashboard"]
        JestRunner --> OtherTests["11 other libraries<br/>Individual jest.config.js<br/>Separate coverage dirs"]
    end
    
    JestRunner --> CoverageArtifact["Upload to<br/>unit-test-coverage-{node-version}"]
```

**Test Configuration per Library:**
- Builder: `@nrwl/jest:jest`
- Config location: `{library}/jest.config.js`
- Coverage output: `coverage/{library-path}`
- Option: `passWithNoTests: true`

Sources: [package.json:39](), [workspace.json:63-69](), [workspace.json:132-139]()

### Build Phase

The build phase compiles all TypeScript libraries for production:

**Command:** `yarn buildall`

This expands to: `cross-env NODE_OPTIONS=--max_old_space_size=6144 nx run-many --target=build --configuration=production --all`

```mermaid
graph TB
    BuildAll["yarn buildall<br/>NODE_OPTIONS=--max_old_space_size=6144"] --> NxBuild["nx run-many<br/>--target=build<br/>--configuration=production<br/>--all"]
    
    subgraph "Library Builds (@nrwl/web:package)"
        NxBuild --> CoreUI["core-ui<br/>→ dist/libs/core-ui<br/>rollup.config.js"]
        NxBuild --> ErrorAnalysis["error-analysis<br/>→ dist/libs/error-analysis<br/>rollup.config.js"]
        NxBuild --> ModelAssessment["model-assessment<br/>→ dist/libs/model-assessment<br/>rollup.config.js"]
        NxBuild --> OtherLibs["11 other libraries<br/>→ dist/libs/*"]
    end
    
    subgraph "Application Build (@nrwl/web:build)"
        NxBuild --> Dashboard["dashboard<br/>→ dist/apps/dashboard<br/>webpack.config.js<br/>memoryLimit: 4096"]
    end
    
    Dashboard --> ProdOptimizations["Production optimizations:<br/>optimization: true<br/>outputHashing: all<br/>sourceMap: false<br/>extractCss: true"]
```

**Build Configuration:**
- Libraries use `@nrwl/web:package` with Rollup
- Dashboard app uses `@nrwl/web:build` with Webpack
- External dependencies excluded: `react`, `react-dom`, `@fluentui/react`, `plotly.js`, etc.
- Memory allocation: 6GB for libraries, 4GB for dashboard
- Budget limits: 20MB warning, 50MB error for initial bundle

Sources: [package.json:17](), [workspace.json:99-130](), [workspace.json:217-266]()

### End-to-End Testing Phase

The E2E testing phase validates the dashboard application using Cypress:

**Command:** `yarn e2e`

This expands to: `nx e2e dashboard-e2e`

```mermaid
graph TB
    E2E["nx e2e dashboard-e2e"] --> CypressRunner["@nrwl/cypress:cypress builder"]
    
    CypressRunner --> Config["Configuration<br/>apps/dashboard-e2e/cypress.json<br/>apps/dashboard-e2e/tsconfig.e2e.json"]
    CypressRunner --> DevServer["devServerTarget: dashboard:serve<br/>Start development server"]
    
    DevServer --> DashboardServe["nx serve dashboard<br/>@nrwl/web:dev-server"]
    
    CypressRunner --> Tests["Execute Cypress tests<br/>apps/dashboard-e2e/src"]
    
    Tests --> Screenshots["Capture screenshots<br/>on test failures"]
    Screenshots --> Upload["Upload to<br/>e2e-screen-shot-{node-version}<br/>path: dist/cypress"]
```

Sources: [package.json:22](), [workspace.json:314-326]()

## Nx Monorepo Integration

The TypeScript CI workflow leverages Nx for efficient task execution across the monorepo:

```mermaid
graph TB
    subgraph "Nx Task Orchestration"
        NxConfig["nx.json<br/>npmScope: responsible-ai<br/>defaultBase: main"]
        WorkspaceConfig["workspace.json<br/>14 projects defined"]
        TSConfig["tsconfig.base.json<br/>Path mappings"]
        
        NxConfig --> TaskRunner["@nrwl/workspace/tasks-runners/default"]
        WorkspaceConfig --> TaskRunner
        
        TaskRunner --> Affected["Affected Command Analysis<br/>Only test/lint/build changed projects"]
        TaskRunner --> Dependencies["Target Dependencies<br/>build dependencies before building"]
    end
    
    subgraph "Project Types"
        TaskRunner --> Libraries["13 Libraries<br/>builder: @nrwl/web:package"]
        TaskRunner --> Dashboard["1 Application<br/>builder: @nrwl/web:build"]
        TaskRunner --> E2EProjects["2 E2E Projects<br/>builder: @nrwl/cypress:cypress"]
    end
```

**Nx Configuration:**
- Default task runner: `@nrwl/workspace/tasks-runners/default`
- Affected base: `main` branch
- Target dependencies: Build dependencies before building dependents

**Path Aliases:**
```typescript
"@responsible-ai/core-ui": ["libs/core-ui/src/index.ts"]
"@responsible-ai/error-analysis": ["libs/error-analysis/src/index.ts"]
"@responsible-ai/model-assessment": ["libs/model-assessment/src/index.ts"]
// ... 11 more library mappings
```

Sources: [nx.json:1-89](), [workspace.json:1-10](), [tsconfig.base.json:37-56]()

## Memory Allocation Strategy

TypeScript compilation and testing require significant memory allocation:

| Phase | Memory Limit | Configuration |
|-------|-------------|---------------|
| Linting | 4GB | `NODE_OPTIONS=--max_old_space_size=4096` |
| Testing | Default | No explicit limit |
| Building (libraries) | 6GB | `NODE_OPTIONS=--max_old_space_size=6144` |
| Building (dashboard) | 4GB | `memoryLimit: 4096` in workspace.json |

**Rationale:**
- Building all 14 libraries simultaneously requires 6GB heap space
- Dashboard webpack build configured with 4GB internal limit
- Linting requires 4GB due to parallel ESLint execution across all projects

Sources: [package.json:13-17](), [workspace.json:227]()

## Artifact Upload Strategy

The workflow uploads three types of artifacts for debugging and analysis:

```mermaid
graph LR
    subgraph "Artifact Uploads (if: always())"
        Coverage["unit-test-coverage-{node-version}<br/>Source: coverage/<br/>Jest HTML reports"]
        Screenshots["e2e-screen-shot-{node-version}<br/>Source: dist/cypress/<br/>Cypress screenshots/videos"]
        Errors["yarn-error.log-{node-version}<br/>Source: yarn-error.log<br/>Installation failures"]
    end
    
    CIRun["CI Run Completion"] --> Coverage
    CIRun --> Screenshots
    CIRun --> Errors
    
    Coverage --> Analysis["Code coverage analysis<br/>Per-library coverage reports"]
    Screenshots --> Debug["E2E test debugging<br/>Visual failure inspection"]
    Errors --> Troubleshoot["Dependency troubleshooting<br/>Installation errors"]
```

**Upload Conditions:**
- All uploads use `if: always()` to ensure artifacts are captured even on failure
- Artifacts are namespaced by Node.js version to prevent collisions
- Actions: `actions/upload-artifact@v4`

Sources: [.github/workflows/CI-typescript.yml:33-50]()

## Comparison with CD Workflow

While CI-typescript runs on pull requests, the CD workflow ([.github/workflows/CD.yml:1-243]()) handles builds on merge:

| Aspect | CI-typescript | CD |
|--------|--------------|-----|
| Trigger | Pull requests only | Push to main, PRs, manual |
| Node versions | 14.x, 16.x | 16.x only |
| Build configuration | Production | Production |
| Artifact destination | GitHub Actions | Azure Blob Storage |
| NPM publishing | No | Yes (on main/manual) |
| Python wheel building | No | Yes |

The CD workflow includes additional steps:
- Building Python wheels for `raiwidgets` and `responsibleai`
- Uploading to Azure Blob Storage at URLs like `https://responsibleai.blob.core.windows.net/latest/index.html`
- Publishing TypeScript packages to NPM registry
- 90-day retention policy for blob storage artifacts

Sources: [.github/workflows/CI-typescript.yml:1-51](), [.github/workflows/CD.yml:1-243]()

---

