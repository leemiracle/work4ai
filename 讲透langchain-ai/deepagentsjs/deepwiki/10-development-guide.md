<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/deepagentsjs · page 10 Development Guide · fetched 2026-10-26 -->

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.changeset/README.md](.changeset/README.md)
- [.changeset/config.json](.changeset/config.json)
- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.github/workflows/cli-release.yml](.github/workflows/cli-release.yml)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [libs/deepagents/package.json](libs/deepagents/package.json)
- [libs/providers/deno/vitest.config.ts](libs/providers/deno/vitest.config.ts)
- [package.json](package.json)
- [pnpm-lock.yaml](pnpm-lock.yaml)
- [pnpm-workspace.yaml](pnpm-workspace.yaml)

</details>



This page provides essential information for contributors and developers working on the DeepAgentsJS codebase. It covers the development environment setup, workflow, and tooling used throughout the monorepo. For detailed information about specific aspects of development, see the dedicated sub-pages: [Monorepo Structure](#10.1), [Build System](#10.2), [Testing](#10.3), [CI/CD Pipeline](#10.4), [Release Process](#10.5), and [Evaluation Suites](#10.6).

## Prerequisites

The DeepAgentsJS project requires the following tools:

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | 22.x or 24.x | Runtime environment |
| pnpm | 10.29.2 | Package manager |
| TypeScript | ^6.0.2 | Type system and compilation |

The Node.js version is managed via `.nvmrc` at the repository root [.github/workflows/ci.yml:36](). The pnpm version is specified in [package.json:58]() using the `packageManager` field.

## Development Workflow

```mermaid
graph TB
    ["Clone_Repository"] --> ["pnpm_install"]
    ["pnpm_install"] --> ["pnpm_build"]
    
    subgraph "Development_Loop"
        ["Edit_Code"] --> ["pnpm_format"]
        ["pnpm_format"] --> ["pnpm_lint"]
        ["pnpm_lint"] --> ["pnpm_typecheck"]
        ["pnpm_typecheck"] --> ["pnpm_test:unit"]
        ["pnpm_test:unit"] --> ["pnpm_test:int"]
    end
    
    ["pnpm_build"] --> ["Edit_Code"]
    ["pnpm_test:int"] --> ["Commit_Changes"]
    
    ["Commit_Changes"] --> ["CI_Pipeline_Runs"]
    ["CI_Pipeline_Runs"] --> ["Code_Review"]
    ["Code_Review"] --> ["Merge_to_main"]
```

**Sources:** [package.json:7-22](), [.github/workflows/ci.yml:1-169]()

### Initial Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/langchain-ai/deepagentsjs.git
    cd deepagentsjs
    ```

2.  **Install dependencies:**
    ```bash
    pnpm install
    ```
    This installs all dependencies across the monorepo workspace as defined in [pnpm-workspace.yaml:1-8]().

3.  **Build all packages:**
    ```bash
    pnpm build
    ```
    Builds all packages in `libs/*` and `libs/providers/*` directories [package.json:8]().

**Sources:** [package.json:8-9](), [pnpm-workspace.yaml:1-8]()

## Available Scripts

The root [package.json]() defines scripts for managing the entire monorepo:

### Build and Clean

| Script | Command | Description |
|--------|---------|-------------|
| `build` | `pnpm --filter "./libs/*" --filter "./libs/providers/*" build` | Build all library packages |
| `clean` | `pnpm --filter "./libs/*" clean` | Remove build artifacts |
| `typecheck` | `pnpm --filter "./libs/*" typecheck` | Run TypeScript type checking |

**Sources:** [package.json:8-10]()

### Code Quality

| Script | Command | Description |
|--------|---------|-------------|
| `lint` | `oxlint` | Fast linting using oxlint |
| `lint:fix` | `oxlint --fix` | Lint and auto-fix issues |
| `format` | `oxfmt` | Fast formatting using oxfmt |
| `format:check` | `oxfmt --check` | Check formatting |

**Sources:** [package.json:11-14]()

### Testing

| Script | Command | Description |
|--------|---------|-------------|
| `test` | `pnpm format:check && pnpm lint && pnpm --filter "./libs/*" test` | Run all checks and tests |
| `test:unit` | `pnpm --filter "./libs/*" test:unit` | Run unit tests only |
| `test:int` | `pnpm --filter "./libs/*" --filter "./libs/providers/*" test:int` | Run integration tests |
| `test:watch` | `pnpm --filter "./libs/*" test:watch` | Run tests in watch mode |
| `test:coverage` | `pnpm --filter "./libs/*" test:coverage` | Run tests with coverage |

**Sources:** [package.json:15-19]()

### Release Management

| Script | Command | Description |
|--------|---------|-------------|
| `changeset:version` | `changeset version` | Update package versions based on changesets |
| `release` | `pnpm build && changeset publish` | Build and publish packages to npm |

**Sources:** [package.json:20-21]()

## Tooling Configuration

```mermaid
graph LR
    subgraph "Code_Quality_Tools"
        ["oxlint@^1.57.0"]
        ["oxfmt@^0.42.0"]
        ["codespell_actions-codespell"]
        ["eslint-plugin-no-instanceof@^1.0.1"]
    end
    
    subgraph "Build_Tools"
        ["TypeScript_typescript@^6.0.2"]
        ["tsdown_@^0.21.4"]
        ["jiti_@^2.6.1"]
    end
    
    subgraph "Testing_Tools"
        ["Vitest_vitest@^4.0.18"]
    end
    
    subgraph "Release_Tools"
        ["@changesets/cli_@^2.29.8"]
        ["@changesets/changelog-github"]
    end
```

**Sources:** [package.json:41-53](), [libs/deepagents/package.json:50-66]()

### Linting and Formatting

The repository has migrated to high-performance Rust-based tooling. `oxlint` is used for linting and `oxfmt` is used for formatting [package.json:49-50](). Security checks for spelling are performed via `codespell` in CI [.github/workflows/ci.yml:65]().

### TypeScript Configuration

The project uses TypeScript 6.0.2 with the `@tsconfig/recommended` preset as a base configuration [package.json:44, 52]().

## Development Environment Tools

```mermaid
graph TB
    subgraph "Package_Management"
        ["pnpm@10.29.2_Workspace_Manager"]
        ["pnpm-workspace.yaml_libs/*,_providers/*,_internal/*,_evals/*"]
    end
    
    subgraph "Runtime_Tools"
        ["tsx@^4.21.0_TypeScript_Executor"]
        ["globals@^17.3.0_Global_Types"]
    end
    
    subgraph "Package_Overrides"
        ["minimatch@10.2.4"]
        ["fast-xml-parser@5.5.10"]
        ["rollup@4.59.0"]
        ["lodash@4.18.1"]
    end
```

**Sources:** [package.json:58-71](), [pnpm-workspace.yaml:1-8]()

### pnpm Workspace

The monorepo uses pnpm workspaces to manage multiple packages. Workspace packages are defined in [pnpm-workspace.yaml:1-8]():

*   `libs/*` - Core library packages (e.g., `deepagents`)
*   `libs/providers/*` - Sandbox provider packages (e.g., `deno`, `modal`)
*   `internal/*` - Internal tools and the `eval-harness`
*   `evals/*` - Behavioral evaluation suites
*   `examples` - Example applications and implementations

### Dependency Overrides

The root package defines security and compatibility overrides in [package.json:60-69]() for packages like `minimatch`, `fast-xml-parser`, `rollup`, and `lodash`.

## Continuous Integration

```mermaid
graph TB
    subgraph "Code_Quality_Gates"
        ["format:check_oxfmt_validation"]
        ["lint_oxlint_checks"]
        ["check-spelling_codespell"]
    end
    
    subgraph "Build_Stage"
        ["build_pnpm_build"]
        ["Upload_Artifacts_build-artifacts.tar.gz"]
    end
    
    subgraph "Test_Stage"
        ["Unit_Tests_Ubuntu_&_Windows_Node_22.x_&_24.x"]
        ["Integration_Tests_With_API_keys"]
    end
    
    ["format:check_oxfmt_validation"] --> ["build_pnpm_build"]
    ["lint_oxlint_checks"] --> ["build_pnpm_build"]
    ["check-spelling_codespell"] --> ["build_pnpm_build"]
    
    ["build_pnpm_build"] --> ["Upload_Artifacts_build-artifacts.tar.gz"]
    ["Upload_Artifacts_build-artifacts.tar.gz"] --> ["Unit_Tests_Ubuntu_&_Windows_Node_22.x_&_24.x"]
    ["Upload_Artifacts_build-artifacts.tar.gz"] --> ["Integration_Tests_With_API_keys"]
```

**Sources:** [.github/workflows/ci.yml:25-169]()

The CI pipeline runs on every push to `main` and on all pull requests. It enforces code quality through multiple gates before allowing tests to run. For detailed information, see [CI/CD Pipeline](#10.4).

## Test Configuration

The project uses Vitest for testing with separate configurations for unit and integration tests. In the `libs/providers/deno` package, for example, unit tests exclude `**/*.int.test.ts` and have a 60s timeout, while integration tests specifically include them with a 100s timeout [libs/providers/deno/vitest.config.ts:1-41]().

## Release Process

DeepAgentsJS uses `changesets` for versioning and publishing.

*   **Version Updates:** Handled by `changeset version`, which is triggered in the `release` workflow [.github/workflows/release.yml:44]().
*   **Publishing:** Handled by `pnpm release` which builds the project and runs `changeset publish` [package.json:21]().
*   **CLI Release:** A specialized workflow exists for the `deepagents-cli` package to build platform-specific binaries [.github/workflows/cli-release.yml:1-15]() and publish them to npm.

**Sources:** [.github/workflows/release.yml:1-50](), [.github/workflows/cli-release.yml:1-15](), [package.json:20-21]()

## Next Steps

For more detailed information about specific development topics:

*   **[Monorepo Structure](#10.1)** — Explanation of the pnpm workspace structure and package organization.
*   **[Build System](#10.2)** — Documentation of the build process and artifact generation using `tsdown`.
*   **[Testing](#10.3)** — Guide to the testing infrastructure and vitest configuration.
*   **[CI/CD Pipeline](#10.4)** — Documentation of the GitHub Actions workflows and quality gates.
*   **[Release Process](#10.5)** — Guide to versioning with changesets and publishing to npm.
*   **[Evaluation Suites](#10.6)** — Documentation of the behavioral evaluation system in `evals/`.

**Sources:** [package.json:1-72](), [.github/workflows/ci.yml:1-169](), [pnpm-workspace.yaml:1-8]()

---

