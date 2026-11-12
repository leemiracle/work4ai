<!-- source: DeepWiki mcp.deepwiki.com · repo feast-dev/feast · page 5 Testing and Quality Assurance · fetched 2026-10-21 -->

# Testing and Quality Assurance

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/fork_workflows/fork_pr_integration_tests_aws.yml](.github/fork_workflows/fork_pr_integration_tests_aws.yml)
- [.github/fork_workflows/fork_pr_integration_tests_gcp.yml](.github/fork_workflows/fork_pr_integration_tests_gcp.yml)
- [.github/fork_workflows/fork_pr_integration_tests_snowflake.yml](.github/fork_workflows/fork_pr_integration_tests_snowflake.yml)
- [.github/workflows/build_wheels.yml](.github/workflows/build_wheels.yml)
- [.github/workflows/linter.yml](.github/workflows/linter.yml)
- [.github/workflows/master_only.yml](.github/workflows/master_only.yml)
- [.github/workflows/nightly-ci.yml](.github/workflows/nightly-ci.yml)
- [.github/workflows/pr_integration_tests.yml](.github/workflows/pr_integration_tests.yml)
- [.github/workflows/pr_local_integration_tests.yml](.github/workflows/pr_local_integration_tests.yml)
- [.github/workflows/publish.yml](.github/workflows/publish.yml)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [.github/workflows/unit_tests.yml](.github/workflows/unit_tests.yml)
- [.releaserc.js](.releaserc.js)
- [Makefile](Makefile)
- [docs/how-to-guides/adding-or-reusing-tests.md](docs/how-to-guides/adding-or-reusing-tests.md)
- [infra/scripts/redis-cluster.sh](infra/scripts/redis-cluster.sh)
- [sdk/python/feast/infra/offline_stores/contrib/__init__.py](sdk/python/feast/infra/offline_stores/contrib/__init__.py)
- [sdk/python/tests/README.md](sdk/python/tests/README.md)

</details>



This document describes Feast's comprehensive testing infrastructure that ensures reliability and correctness across a complex, multi-backend ML feature store ecosystem. It covers the universal testing framework which parametrizes tests to run across various storage backends, the organizing principles and reusable patterns for test code, and the continuous integration and delivery (CI/CD) pipelines that automate quality validation.

For details, see the child pages:  
- [Universal Testing Framework](#5.1) — the parametrized test architecture running tests across multiple online/offline store combinations.  
- [Test Infrastructure and Patterns](#5.2) — pytest configuration, fixtures, environment setup, and validation patterns.  
- [CI/CD Workflows](#5.3) — GitHub Actions workflows for unit, integration, linting, and release pipelines.  

---

## Overview

Feast employs a layered testing strategy addressing its architecture's diversity and external dependencies. The main test categories include:

- **Unit tests**: Fast, isolated tests verifying core logic and SDK components without external dependencies, triggered by commands like `make test-python-unit` [Makefile:51-51]().
- **Integration tests**: Validate end-to-end behavior requiring external cloud or local services (e.g., BigQuery, Snowflake, Redis, PostgreSQL). Redis Cluster and other infrastructure are set up within the CI pipelines to ensure robust coverage [`.github/workflows/pr_integration_tests.yml:83-86`]().
- **Universal tests**: Parametrized tests dynamically run across combinations of offline and online stores using the `Environment` abstraction and `DataSourceCreator`, thus comprehensively testing store interoperability [sdk/python/tests/utils/cli_repo_creator.py:166-172]().
- **Benchmark tests**: Measure performance of critical feature store operations such as online retrieval and materialization, run optionally with `pytest --benchmark` [`.github/workflows/master_only.yml:82-82`]().

**Sources:** [Makefile:51-51](), [`.github/workflows/pr_integration_tests.yml:83-86`](), [sdk/python/tests/utils/cli_repo_creator.py:166-172](), [`.github/workflows/master_only.yml:82-82`]()

---

## Universal Testing Framework

The universal testing framework ensures feature parity and consistent behavior across multiple storage backends. It leverages pytest's parametrization to generate test matrices covering combinations of offline stores, online stores, and providers.

### Universal Testing Architecture

```mermaid
graph TD
    subgraph "Natural Language Space"
        TestReq [""Test online retrieval consistency across storage backends""]
    end

    subgraph "Code Entity Space"
        TestFunc ["test_connection_pool_online_stores"]
        Marker ["@pytest.mark.universal_online_stores"]
        EnvFixture ["Environment"]
        
        Config1 ["SqliteOnlineStoreConfig"]
        Config2 ["RedisOnlineStoreConfig"]
        
        DSC ["DataSourceCreator"]
        OnlineDB1 ["SqliteOnlineStore"]
        OnlineDB2 ["RedisOnlineStore"]
    end

    TestReq --> TestFunc
    TestFunc --> Marker
    Marker --> Config1
    Marker --> Config2
    
    Config1 --> EnvFixture
    Config2 --> EnvFixture
    
    EnvFixture --> DSC
    DSC -->|writes_to| OnlineDB1
    DSC -->|writes_to| OnlineDB2
```

*Title: Universal Testing Framework Data Flow*

At the core, test cases (e.g., `test_connection_pool_online_stores`) are annotated with pytest markers identifying applicable backend combinations. The `Environment` fixture encapsulates the runtime context, selecting specific backend configurations like `SqliteOnlineStoreConfig` or `RedisOnlineStoreConfig`. The `DataSourceCreator` handles provisioning and writing test data to the corresponding online store instances. This approach maximizes test reuse and broad coverage without duplication.

**Sources:** [sdk/python/tests/utils/cli_repo_creator.py:166-172]()

For details, see [Universal Testing Framework](#5.1).

---

## Test Infrastructure and Patterns

Feast's test infrastructure is built on `pytest` with centralized configuration and fixtures defined mainly in `sdk/python/tests/conftest.py`. These fixtures abstract environment setup, dependency initialization, and backend resource provisioning to facilitate reusable, modular tests with consistent state management.

The `CliRunner` utility wraps execution of Feast CLI commands via subprocesses, isolating side effects and enabling ephemeral use of temporary repositories defined by `feature_store.yaml` files.

### Test Environment Lifecycle

```mermaid
graph LR
    subgraph "Natural Language Space"
        SetupReq [""Initialize test environment and dependencies""]
    end

    subgraph "Code Entity Space"
        Setup ["make install-python-dependencies-ci"]
        CliRunner ["CliRunner"]
        FeastCLI ["feast.cli.cli"]
        SubprocessRun ["subprocess.run"]
        SubprocessPopen ["subprocess.Popen"]
        TempDir ["tempfile.TemporaryDirectory"]
        RepoConfig ["feature_store.yaml"]
    end

    SetupReq --> Setup
    Setup --> CliRunner
    CliRunner --> SubprocessRun
    CliRunner --> SubprocessPopen
    CliRunner -->|manages| TempDir
    TempDir --> RepoConfig
    SubprocessRun -->|executes| FeastCLI
    SubprocessPopen -->|executes| FeastCLI
```

*Title: Test Environment Lifecycle*

The lifecycle begins with installing dependencies robustly via `make install-python-dependencies-ci` which utilizes `uv` to install and sync packages in isolated virtual environments [Makefile:106-117](). The `CliRunner` component orchestrates subprocess execution of Feast CLI commands (`feast.cli.cli`) for test runs, managing temporary directories for feature repository configuration files (`feature_store.yaml`). This allows tests to run in fully isolated environments, avoiding state leakage.

Fixtures also enable parametrization of test inputs across offline and online store configurations, facilitating the universal test suite's dynamic test generation.

**Sources:** [Makefile:106-117](), [sdk/python/tests/utils/cli_repo_creator.py:50-138](), [sdk/python/tests/utils/cli_repo_creator.py:156-172]()

For details, see [Test Infrastructure and Patterns](#5.2).

---

## CI/CD Workflows

Feast automates testing and quality assurance through GitHub Actions workflows covering linting, unit and integration testing, Docker image builds, and release automation. These pipelines are designed for security, efficiency, and multi-platform, multi-language support.

### CI/CD Architecture Overview

```mermaid
graph TD
    subgraph "Natural Language Space"
        PR ["Pull Request"]
        PushMaster ["Push to master branch"]
        Nightly ["Nightly scheduled runs"]
    end

    subgraph "Code Entity Space"
        UnitTestPy ["unit-test-python job"]
        UnitTestGo ["unit-test-go job"]
        UnitTestUI ["unit-test-ui job"]
        IntegrationTest ["pr-integration-tests and pr-local-integration-tests jobs"]
        Linter ["linter job"]
        NightlyCI ["nightly-ci job"]
        DockerBuilds ["build-all-docker-images job"]
        Release ["release job"]
        Publish ["publish job"]
    end

    PR --> Linter
    PR --> UnitTestPy
    PR --> UnitTestGo
    PR --> UnitTestUI
    PR --> IntegrationTest
    PushMaster --> UnitTestPy
    PushMaster --> IntegrationTest
    PushMaster --> DockerBuilds
    Nightly --> NightlyCI
    Release --> Publish
```

*Title: CI/CD Workflow Overview*

Key workflow elements:

- **Unit Tests**  
  Multi-OS and Python version matrix runs for Python unit tests [`.github/workflows/unit_tests.yml:22-170`](), alongside Go and UI (React) unit tests [`.github/workflows/unit_tests.yml:94-140`](), [`.github/workflows/unit_tests.yml:144-171`]().

- **Integration Tests**  
  Gated by PR approval labels (`ok-to-test`, `approved`, `lgtm`) to safely access cloud credentials [`.github/workflows/pr_integration_tests.yml:20-23`](). Local integration tests with containerized backend stubs provide faster feedback [`.github/workflows/pr_local_integration_tests.yml:16-20`]().

- **Nightly CI**  
  Periodic full integration tests including cleanup for flaky cloud resources such as DynamoDB and Bigtable [`.github/workflows/nightly-ci.yml:1-153`]().

- **Linting**  
  Comprehensive lint checks including ruff, mypy, and pre-commit to enforce code style and typing correctness [`.github/workflows/linter.yml:49-50`]().  

- **Docker Builds**  
  Automated multi-architecture build and push to Quay.io for core components like `feature-server-dev`, `feature-transformation-server`, and `feast-operator` [`.github/workflows/master_only.yml:89-145`]().  

- **Release Pipelines**  
  Version bumping, changelog generation, semantic-release integration, and artifact publishing (Python wheels, Docker images, Helm charts, UI packages) are orchestrated [`.github/workflows/release.yml:1-190`](), [`.github/workflows/publish.yml:1-74`](), with semantic-release config ensuring consistent versioning and git tagging [.releaserc.js:1-95]().

Security gating ensures that untrusted code from forks cannot access cloud secrets or run privileged jobs by requiring specific reviewer labels handled by `pull_request_target` event [`.github/workflows/pr_integration_tests.yml:4-23`]().  

**Sources:**  
[`.github/workflows/unit_tests.yml:22-170`](), [`.github/workflows/unit_tests.yml:94-140`](), [`.github/workflows/unit_tests.yml:144-171`](),  
[`.github/workflows/pr_integration_tests.yml:20-23`](), [`.github/workflows/pr_local_integration_tests.yml:16-20`](),  
[`.github/workflows/nightly-ci.yml:1-153`](), [`.github/workflows/linter.yml:49-50`](),  
[`.github/workflows/master_only.yml:89-145`](), [`.github/workflows/release.yml:1-190`](), [`.github/workflows/publish.yml:1-74`]()

For details, see [CI/CD Workflows](#5.3).

---

## Summary of Commands

| Command                      | Purpose                                                                   |
|------------------------------|---------------------------------------------------------------------------|
| `make test-python-unit`       | Run Python SDK unit tests rapidly                                        |
| `make test-python-integration`| Run full Python integration tests with cloud backends                   |
| `make lint-python`            | Run Python linting and type checking                                    |
| `make precommit-check`        | Run formatting and lint checks before committing                        |
| `make install-python-dependencies-ci` | Install Python dependencies for CI environments using `uv`        |
| `make build-docker`           | Build Docker images for various Feast components                        |

**Sources:** [Makefile:51-51](), [`.github/workflows/master_only.yml:73-73`](), [Makefile:61-64](), [Makefile:67-68](), [Makefile:106-117](), [Makefile:55-55]()

---

For in-depth technical details, explore the child pages:  
- [Universal Testing Framework](#5.1)  
- [Test Infrastructure and Patterns](#5.2)  
- [CI/CD Workflows](#5.3)

---

