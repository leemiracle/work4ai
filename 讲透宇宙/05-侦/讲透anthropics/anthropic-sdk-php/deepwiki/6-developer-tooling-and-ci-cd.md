<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/anthropic-sdk-php · page 6 Developer Tooling and CI/CD · fetched 2026-10-26 -->

# Developer Tooling and CI/CD

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitattributes](.gitattributes)
- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.github/workflows/create-releases.yml](.github/workflows/create-releases.yml)
- [.github/workflows/publish-packagist.yml](.github/workflows/publish-packagist.yml)
- [.github/workflows/release-doctor.yml](.github/workflows/release-doctor.yml)
- [.gitignore](.gitignore)
- [.php-cs-fixer.dist.php](.php-cs-fixer.dist.php)
- [bin/check-release-environment](bin/check-release-environment)
- [scripts/mock](scripts/mock)
- [scripts/test](scripts/test)

</details>



This page provides a high-level overview of the development workflow for the Anthropic PHP SDK. It covers the local development environment, automated testing pipelines, and the release management process. The repository utilizes a set of standardized scripts and GitHub Actions to ensure code quality and consistent delivery.

## Local Development Workflow

The development environment is centered around a set of bash scripts located in the `scripts/` directory. These scripts wrap common tasks such as dependency installation, linting, and running the test suite.

*   **Bootstrapping**: The `./scripts/bootstrap` script handles the initial environment setup, typically by installing Composer dependencies. It is used in CI environments to ensure a clean state [[.github/workflows/ci.yml:33-33]]().
*   **Code Quality**: Static analysis and formatting are enforced via `./scripts/lint` and `./scripts/format`. The SDK uses **PHP CS Fixer** for styling, governed by the configuration in `.php-cs-fixer.dist.php` [[.php-cs-fixer.dist.php:9-19]](), and **PHPStan** for type checking.
*   **Testing**: The `./scripts/test` script executes the test suite using the **Pest** framework [[scripts/test:55-55]]().

For details on available scripts and their configurations, see [Code Quality Scripts](#6.3).

### Development Tooling Relationship

The following diagram illustrates how local scripts interact with the codebase and external tools.

**Local Tooling Architecture**
```mermaid
graph TD
    subgraph "Local Environment"
        "scripts/bootstrap" --> "vendor/ (Composer)"
        "scripts/format" --> "PHP CS Fixer"
        "scripts/lint" --> "PHPStan"
        "scripts/test" --> "Pest"
        "scripts/mock" --> "Steady Mock Server"
    end

    subgraph "Code Entity Space"
        "PHP CS Fixer" -.-> ".php-cs-fixer.dist.php"
        "PHPStan" -.-> "phpstan.dist.neon"
        "Pest" -.-> "tests/"
        "Steady Mock Server" -.-> ".stats.yml"
    end
```
Sources: [[.github/workflows/ci.yml:33-36]](), [[scripts/test:55-55]](), [[scripts/mock:11-11]](), [[.php-cs-fixer.dist.php:1-19]]()

## Testing Infrastructure

The SDK employs a robust testing strategy that combines unit tests with integration tests validated against a mock API server.

*   **Mock Server**: The SDK uses the **Steady** (or Prism) mock server to simulate the Anthropic API. The `./scripts/mock` script starts this server using the OpenAPI specification URL found in `.stats.yml` [[scripts/mock:11-12]]().
*   **Validation**: The mock server ensures that outgoing requests from the SDK conform to the official API contract [[scripts/mock:51-51]]().
*   **Environment Overrides**: Developers can bypass the local mock server by setting the `TEST_API_BASE_URL` environment variable to point to a different endpoint [[scripts/test:24-26]]().

For details on the testing framework and mock server setup, see [Testing Infrastructure](#6.1).

## CI/CD and Release Pipeline

The project uses GitHub Actions to automate the integration and delivery process.

*   **Continuous Integration**: Every push and pull request triggers the `CI` workflow, which runs lints and tests across supported environments [[.github/workflows/ci.yml:1-55]]().
*   **Automated Releases**: The SDK uses **Stainless** and **release-please** to automate versioning and changelog generation [[.github/workflows/create-releases.yml:19-23]]().
*   **Distribution**: Once a release is tagged, it is automatically published to **Packagist** via a webhook-style `curl` request to the Packagist API [[.github/workflows/create-releases.yml:25-31]]().
*   **Health Checks**: The `Release Doctor` workflow verifies that all necessary secrets (like `STAINLESS_API_KEY` and `PACKAGIST_SAFE_KEY`) are present before attempting a release [[.github/workflows/release-doctor.yml:1-25]](), [[bin/check-release-environment:5-15]]().

For details on the automation workflows and release process, see [CI/CD and Release Pipeline](#6.2).

### Release Pipeline Flow

The diagram below maps the release process from code push to package distribution.

**CI/CD Pipeline Mapping**
```mermaid
graph LR
    subgraph "GitHub Actions"
        "ci.yml" --> "create-releases.yml"
        "create-releases.yml" --> "release-doctor.yml"
    end

    subgraph "Code & External Services"
        "create-releases.yml" -- "Triggers" --> "release-please"
        "release-please" -- "Updates" --> "CHANGELOG.md"
        "release-please" -- "Updates" --> "VERSION"
        "create-releases.yml" -- "POST" --> "packagist.org/api"
        "release-doctor.yml" -- "Runs" --> "bin/check-release-environment"
    end
```
Sources: [[.github/workflows/ci.yml:1-3]](), [[.github/workflows/create-releases.yml:1-31]](), [[.github/workflows/release-doctor.yml:1-25]](), [[bin/check-release-environment:1-29]]()

## Child Pages
*   [Testing Infrastructure](#6.1)
*   [CI/CD and Release Pipeline](#6.2)
*   [Code Quality Scripts](#6.3)

---

