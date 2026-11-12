<!-- source: DeepWiki mcp.deepwiki.com · repo cline/cline · page 14 Development and Release Engineering · fetched 2026-10-26 -->

# Development and Release Engineering

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.cline/skills/publish-extension/SKILL.md](.cline/skills/publish-extension/SKILL.md)
- [.github/ISSUE_TEMPLATE/bug_report.yml](.github/ISSUE_TEMPLATE/bug_report.yml)
- [.github/ISSUE_TEMPLATE/config.yml](.github/ISSUE_TEMPLATE/config.yml)
- [.github/pull_request_template.md](.github/pull_request_template.md)
- [.github/workflows/cli-publish.yml](.github/workflows/cli-publish.yml)
- [.github/workflows/ext-vscode-ab-package.yml](.github/workflows/ext-vscode-ab-package.yml)
- [.github/workflows/ext-vscode-publish-legacy.yml](.github/workflows/ext-vscode-publish-legacy.yml)
- [.github/workflows/ext-vscode-publish-nightly.yml](.github/workflows/ext-vscode-publish-nightly.yml)
- [.github/workflows/ext-vscode-publish-stable.yml](.github/workflows/ext-vscode-publish-stable.yml)
- [.github/workflows/ext-vscode-publish.yml](.github/workflows/ext-vscode-publish.yml)
- [.github/workflows/ext-vscode-test-e2e.yml](.github/workflows/ext-vscode-test-e2e.yml)
- [.github/workflows/ext-vscode-test.yml](.github/workflows/ext-vscode-test.yml)
- [.github/workflows/sdk-publish.yml](.github/workflows/sdk-publish.yml)
- [.husky/pre-commit](.husky/pre-commit)
- [CHANGELOG.md](CHANGELOG.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [apps/vscode-rollout/scripts/set-version.mjs](apps/vscode-rollout/scripts/set-version.mjs)
- [apps/vscode-rollout/scripts/set-version.test.mjs](apps/vscode-rollout/scripts/set-version.test.mjs)
- [apps/vscode/.vscode-test.mjs](apps/vscode/.vscode-test.mjs)
- [apps/vscode/.vscodeignore](apps/vscode/.vscodeignore)
- [apps/vscode/package.json](apps/vscode/package.json)
- [apps/vscode/scripts/interactive-playwright.ts](apps/vscode/scripts/interactive-playwright.ts)
- [apps/vscode/src/test/e2e/utils/build.mjs](apps/vscode/src/test/e2e/utils/build.mjs)
- [apps/vscode/src/test/e2e/utils/helpers.ts](apps/vscode/src/test/e2e/utils/helpers.ts)
- [package.json](package.json)

</details>



The Development and Release Engineering page provides a high-level overview of the build pipelines, testing suites, evaluations, publishing workflows, contributor guides, and documentation site across the Cline monorepo. Following the migration to the standalone SDK architecture, the release and build machinery coordinates multiple target platforms from a shared core.

For details, see the child pages below:
- [Build System and Protocol Buffers](#14.1) — Document esbuild/Vite builds for the extension and webview, `bun.mts` build scripts, proto compilation, and VS Code tasks/launch configs.
- [Testing Infrastructure](#14.2) — Describe Vitest/Mocha setups, stubs, e2e suites, biome linting, coverage checks, and CI test workflows.
- [Evals and Benchmarks](#14.3) — Document the `evals/` directory: smoke-test scenarios, e2e harness, tool-precision benchmarks, and analysis tooling.
- [Publishing and Release](#14.4) — Explain GitHub Actions publish workflows, changesets, sdk release scripts, and signing secrets.
- [Contributing and Agent Workflows](#14.5) — Guidance for contributors: dev setup, watch tasks, PR conventions, CODEOWNERS, and `.clinerules` workflows.
- [Documentation Site](#14.6) — Document the Mintlify docs site: navigation, tabs, redirects, and feature mapping.

---

## 14.1. Build System and Protocol Buffers

Cline uses [Bun](https://bun.sh) as its primary package manager and runtime, driving compilation tasks across the monorepo via custom scripts like `apps/cli/bun.mts` and task definitions in [.vscode/tasks.json:1-18](), [.vscode/tasks.json:36-51](). The build pipeline compiles shared SDK packages (`@cline/shared`, `@cline/llms`, `@cline/agents`, `@cline/core`), bundles applications using esbuild and Vite [apps/vscode/webview-ui/vite.config.ts:48-114](), and compiles Protocol Buffer definitions into gRPC-over-postMessage client stubs [.gitignore:41-43]().

### Build System and Configuration Code Mapping

```mermaid
graph TD
    subgraph "Natural_Language_Space"
        "CliBuildScript"["CLI Build Script"]
        "WebviewConfig"["Webview Bundler Config"]
        "VsCodeLaunchConfig"["Extension Launch Config"]
        "WorkspaceConfig"["Monorepo Workspaces"]
    end

    subgraph "Code_Entity_Space"
        "BunMts"["apps/cli/bun.mts"]
        "ViteConfig"["apps/vscode/webview-ui/vite.config.ts"]
        "LaunchJson"[".vscode/launch.json"]
        "TasksJson"[".vscode/tasks.json"]
        "RootPackageJson"["package.json"]
    end

    "CliBuildScript" --> "BunMts"
    "WebviewConfig" --> "ViteConfig"
    "VsCodeLaunchConfig" --> "LaunchJson"
    "VsCodeLaunchConfig" --> "TasksJson"
    "WorkspaceConfig" --> "RootPackageJson"
```

Sources: [package.json:4-14](), [apps/cli/bun.mts:1-12](), [.vscode/tasks.json:1-51](), [apps/vscode/webview-ui/vite.config.ts:48-114](), [.gitignore:41-43](), [.vscode/launch.json:1-32]()

For details, see [Build System and Protocol Buffers](#14.1).

---

## 14.2. Testing Infrastructure

The codebase employs a multi-tiered testing architecture combining unit tests, component tests via Vitest [apps/vscode/webview-ui/vite.config.ts:51-54](), integration tests, and Playwright-driven end-to-end suites. Static analysis and code formatting are enforced uniformly across packages using Biome as configured in [package.json:32-35]() and [.vscode/settings.json:23-44](). Continuous integration workflows automatically validate pull requests against these test beds before merge authorization, using test helpers defined in [apps/vscode/src/test/e2e/utils/helpers.ts:22-111]().

For details, see [Testing Infrastructure](#14.2).

Sources: [package.json:26-35](), [apps/vscode/webview-ui/vite.config.ts:51-54](), [.vscode/settings.json:23-44](), [apps/vscode/src/test/e2e/utils/helpers.ts:22-111]()

---

## 14.3. Evals and Benchmarks

Automated evaluation frameworks located in the `evals/` directory run regression checks, tool-precision benchmarks, and smoke-test scenarios against agent execution runs [.gitignore:55-56](). These benchmarks measure task completion rates, cost efficiency, and correct tool-calling behavior under controlled conditions, utilizing shared harness definitions across the core packages.

For details, see [Evals and Benchmarks](#14.3).

Sources: [.gitignore:55-56]()

---

## 14.4. Publishing and Release

GitHub Actions orchestrate automated publishing pipelines across the monorepo delivery surfaces. Stable extension releases and nightly builds are managed through workflow definitions such as [.github/workflows/ext-vscode-publish-nightly.yml:1-47]() and [.github/workflows/ext-vscode-ab-package.yml:1-38](), while agent skills guide manual operations[.cline/skills/publish-extension/SKILL.md:1-29](). Artifact signing, version validation, and marketplace publishing scripts enforce strict monotonicity constraints on package versions.

### Publishing Pipeline and Workflow Entity Mapping

```mermaid
graph TD
    subgraph "Natural_Language_Space"
        "StablePublishWorkflow"["Stable Extension Publisher"]
        "NightlyPublishWorkflow"["Nightly Extension Builder"]
        "AbPackageWorkflow"["Combined A/B VSIX Packager"]
        "PublishingSkill"["Extension Release Skill Guide"]
    end

    subgraph "Code_Entity_Space"
        "NightlyYml"[".github/workflows/ext-vscode-publish-nightly.yml"]
        "AbPackageYml"[".github/workflows/ext-vscode-ab-package.yml"]
        "PublishSkill"[".cline/skills/publish-extension/SKILL.md"]
        "RootPackageJson"["package.json"]
    end

    "NightlyPublishWorkflow" --> "NightlyYml"
    "AbPackageWorkflow" --> "AbPackageYml"
    "PublishingSkill" --> "PublishSkill"
    "StablePublishWorkflow" --> "RootPackageJson"
```

Sources: [.github/workflows/ext-vscode-publish-nightly.yml:1-47](), [.github/workflows/ext-vscode-ab-package.yml:1-38](), [.cline/skills/publish-extension/SKILL.md:1-29](), [package.json:37-38]()

For details, see [Publishing and Release](#14.4).

---

## 14.5. Contributing and Agent Workflows

Contributor workflows provide structured development setups, local debugging targets [.vscode/launch.json:1-32](), and background watch tasks [.vscode/tasks.json:36-51](). Pull requests must follow the guidelines outlined in [.github/pull_request_template.md:1-45]() and satisfy local linting checks described in [CONTRIBUTING.md:32-84](). Agents and automated tools rely on embedded skill definitions and `.clinerules` to execute repetitive operations, maintain release standards, and validate PR compliance.

For details, see [Contributing and Agent Workflows](#14.5).

Sources: [.vscode/launch.json:1-32](), [.vscode/tasks.json:36-51](), [.github/pull_request_template.md:1-45](), [CONTRIBUTING.md:32-84]()

---

## 14.6. Documentation Site

The public documentation site uses Mintlify to structure guides, references, and tutorials. Navigation trees, custom redirects, and UI assets are managed via configuration files, linking user-facing product features directly to the corresponding technical specifications in the repository.

For details, see [Documentation Site](#14.6).

Sources: [README.md:17]()

---

