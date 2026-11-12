<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-node · page 7 Development and Testing · fetched 2026-10-26 -->

# Development and Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.github/workflows/create-releases.yml](.github/workflows/create-releases.yml)
- [.github/workflows/detect-breaking-changes.yml](.github/workflows/detect-breaking-changes.yml)
- [.github/workflows/publish-jsr.yml](.github/workflows/publish-jsr.yml)
- [.github/workflows/publish-npm.yml](.github/workflows/publish-npm.yml)
- [Brewfile](Brewfile)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [bin/publish-npm](bin/publish-npm)
- [examples/logprobs.ts](examples/logprobs.ts)
- [scripts/bootstrap](scripts/bootstrap)
- [scripts/mock](scripts/mock)
- [scripts/test](scripts/test)
- [scripts/utils/upload-artifact.sh](scripts/utils/upload-artifact.sh)

</details>



This document provides a high-level overview of the development infrastructure, testing strategies, and release workflows for the OpenAI Node.js SDK. It covers environment setup, continuous integration, and the multi-runtime testing strategy.

## Development Environment Setup

The SDK uses `yarn@v1` as its primary package manager [CONTRIBUTING.md:3-4](). Setting up the repository involves installing dependencies and building the project to generate the `dist/` directory [CONTRIBUTING.md:6-13]().

### Core Development Commands

| Command | Purpose |
|---------|---------|
| `yarn` | Installs dependencies for the core library [CONTRIBUTING.md:9]() |
| `./scripts/bootstrap` | Installs dependencies for both the core library and examples [scripts/bootstrap:22-30]() |
| `./scripts/build` | Compiles TypeScript into dual-mode CJS/ESM output [scripts/build:1-5]() |
| `yarn lint` | Runs ESLint and type checks via `./scripts/lint` [.github/workflows/ci.yml:35]() |
| `yarn fix` | Automatically formats code using Prettier and fixes lint issues [CONTRIBUTING.md:92]() |

Sources: [CONTRIBUTING.md:1-94](), [scripts/bootstrap:1-30](), [.github/workflows/ci.yml:18-36]()

## Build System

The SDK is built to support multiple environments, including Node.js (CommonJS and ESM), Deno, and browsers. For details, see [Build System](#7.1).

The build process is managed via `./scripts/build` [scripts/build:1-5](). Most of the SDK is generated code; however, modifications to `src/lib/` and `examples/` are persisted as they are ignored by the generator [CONTRIBUTING.md:17-20]().

Sources: [CONTRIBUTING.md:15-20](), [.github/workflows/ci.yml:37-58]()

## Testing Practices

The SDK employs a multi-layered testing strategy including unit tests, integration tests with mock servers, and regression testing for dependent SDKs. For details, see [Testing Practices](#7.5).

### Mock Server Integration

Most tests require a mock server running against the OpenAI OpenAPI spec. The SDK uses `steady` (via `@stdy/cli`) to provide this mock environment [scripts/mock:25-27]().

#### Diagram: Test Orchestration Flow

```mermaid
graph TD
    "Developer" -- "runs ./scripts/test" --> "CheckEnv[is_overriding_api_base_url]"
    "CheckEnv[is_overriding_api_base_url]" -- "No" --> "SteadyCheck[steady_is_running]"
    "SteadyCheck[steady_is_running]" -- "No" --> "StartMock[./scripts/mock --daemon]"
    "StartMock[./scripts/mock --daemon]" --> "WaitHealth[Wait for /_x-steady/health]"
    "WaitHealth[Wait for /_x-steady/health]" --> "RunJest[./node_modules/.bin/jest]"
    "SteadyCheck[steady_is_running]" -- "Yes" --> "RunJest[./node_modules/.bin/jest]"
    "CheckEnv[is_overriding_api_base_url]" -- "Yes" --> "RunJest[./node_modules/.bin/jest]"
    "RunJest[./node_modules/.bin/jest]" -- "Finally" --> "KillMock[kill_server_on_port 4010]"
```

Sources: [scripts/test:12-57](), [scripts/mock:1-52](), [CONTRIBUTING.md:66-77]()

## Ecosystem Tests

The SDK verifies compatibility across a wide range of runtimes including Node.js, Deno, and Bun. For details, see [Ecosystem Tests](#7.3).

Ecosystem tests are executed using a specialized CLI located at `ecosystem-tests/cli.ts` [.github/workflows/ci.yml:146](). This ensures that changes do not break support for non-Node environments or different module resolution strategies.

Sources: [.github/workflows/ci.yml:118-150]()

## CI/CD Pipeline

The CI/CD pipeline is hosted on GitHub Actions and handles linting, building, testing, and artifact generation. For details, see [CI/CD Pipeline](#7.2).

### Workflow Jobs

*   **lint**: Validates code style and TypeScript types [.github/workflows/ci.yml:18-36]().
*   **build**: Compiles the project and uploads a tarball artifact to Stainless storage for previewing [.github/workflows/ci.yml:37-76]().
*   **test**: Executes the standard Jest test suite [.github/workflows/ci.yml:77-95]().
*   **detect_breaking_changes**: Compares the current PR against the base branch to identify breaking API changes [.github/workflows/detect-breaking-changes.yml:9-36]().
*   **agents_sdk**: A regression test that links the current SDK build to `openai-agents-js` to ensure compatibility with the Agents SDK [.github/workflows/detect-breaking-changes.yml:37-97]().

Sources: [.github/workflows/ci.yml:1-150](), [.github/workflows/detect-breaking-changes.yml:1-97]()

## Release Process

Releases are automated via "Release Please" and scheduled workflows. For details, see [Release Process](#7.4).

#### Diagram: Release and Distribution Flow

```mermaid
flowchart TD
    "MainBranch[Push to main]" --> "ReleasePlease[stainless-api/trigger-release-please]"
    "Schedule[Cron Schedule]" --> "ReleasePlease[stainless-api/trigger-release-please]"
    "ReleasePlease[stainless-api/trigger-release-please]" -- "If Release Created" --> "Build[yarn build]"
    "Build[yarn build]" --> "Dist[cd dist]"
    "Dist[cd dist]" --> "NPM[bin/publish-npm]"
    "Dist[cd dist]" --> "JSR[bin/publish-jsr]"
    "NPM[bin/publish-npm]" -- "Uses" --> "OIDCToken[GitHub OIDC Token]"
```

The `bin/publish-npm` script handles version detection, determining if a release is a pre-release (alpha/beta), and publishing with the appropriate NPM tags [bin/publish-npm:15-63]().

Sources: [.github/workflows/create-releases.yml:1-48](), [bin/publish-npm:1-71](), [.github/workflows/publish-npm.yml:1-31]()

---

