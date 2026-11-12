<!-- source: DeepWiki mcp.deepwiki.com · repo WenjieDu/PyPOTS · page 6 Testing & CI/CD · fetched 2026-10-21 -->

# Testing & CI/CD

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/ISSUE_TEMPLATE/bug-report.yml](.github/ISSUE_TEMPLATE/bug-report.yml)
- [.github/ISSUE_TEMPLATE/config.yml](.github/ISSUE_TEMPLATE/config.yml)
- [.github/ISSUE_TEMPLATE/feature-request.yml](.github/ISSUE_TEMPLATE/feature-request.yml)
- [.github/ISSUE_TEMPLATE/model-addition.yml](.github/ISSUE_TEMPLATE/model-addition.yml)
- [.github/ISSUE_TEMPLATE/other-issues.yml](.github/ISSUE_TEMPLATE/other-issues.yml)
- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [.github/workflows/greetings.yml](.github/workflows/greetings.yml)
- [.github/workflows/linting.yml](.github/workflows/linting.yml)
- [.github/workflows/publish_to_PyPI.yml](.github/workflows/publish_to_PyPI.yml)
- [.github/workflows/stale.yml](.github/workflows/stale.yml)
- [.github/workflows/testing_ci.yml](.github/workflows/testing_ci.yml)
- [.github/workflows/testing_daily.yml](.github/workflows/testing_daily.yml)
- [pypots/data/__init__.py](pypots/data/__init__.py)
- [pypots/data/utils.py](pypots/data/utils.py)
- [pypots/imputation/mrnn/data.py](pypots/imputation/mrnn/data.py)
- [tests/anomaly_detection/__init__.py](tests/anomaly_detection/__init__.py)
- [tests/anomaly_detection/autoformer.py](tests/anomaly_detection/autoformer.py)
- [tests/anomaly_detection/saits.py](tests/anomaly_detection/saits.py)
- [tests/anomaly_detection/tefn.py](tests/anomaly_detection/tefn.py)
- [tests/global_test_config.py](tests/global_test_config.py)
- [tests/imputation/llms/__init__.py](tests/imputation/llms/__init__.py)
- [tests/imputation/llms/timellm.py](tests/imputation/llms/timellm.py)
- [tests/representation/ts2vec.py](tests/representation/ts2vec.py)

</details>



The PyPOTS project maintains a robust quality assurance infrastructure designed to ensure model reliability across diverse hardware and software environments. This infrastructure encompasses a comprehensive test suite, automated continuous integration (CI) pipelines for cross-platform validation, and a structured release process for distribution via PyPI and DockerHub.

## Overview of QA Infrastructure

The quality assurance system is built around three pillars: a standardized testing architecture using `pytest`, a GitHub Actions-based CI/CD pipeline, and an automated documentation build system.

### System Interaction Diagram
The following diagram illustrates how the testing infrastructure interacts with the codebase and external registries.

**QA & Release Workflow**
```mermaid
graph TD
    subgraph "Local_Development"
        "Developer" -- "pytest tests/" --> "test_suite[tests/]"
        "test_suite" -- "uses" --> "global_test_config[tests/global_test_config.py]"
    end

    subgraph "GitHub_Actions_CI"
        "push_event[Push/PR]" --> "CI_testing[.github/workflows/testing_ci.yml]"
        "schedule_event[Daily_Cron]" --> "Daily_testing[.github/workflows/testing_daily.yml]"
        "CI_testing" --> "linting[.github/workflows/linting.yml]"
        "CI_testing" -- "executes" --> "test_suite"
    end

    subgraph "Distribution"
        "release_event[Release]" --> "pypi_workflow[.github/workflows/publish_to_PyPI.yml]"
        "pypi_workflow" -- "uploads" --> "PyPI[PyPI_Registry]"
        "release_event" --> "rtd_build[ReadTheDocs]"
    end

    "global_test_config" -- "provides" --> "DATA/TRAIN_SET"
```
**Sources:** [.github/workflows/testing_ci.yml:1-12](), [.github/workflows/testing_daily.yml:1-10](), [.github/workflows/publish_to_PyPI.yml:1-20]()

---

## Test Architecture & Global Configuration

The PyPOTS test suite is organized under the `tests/` directory and relies on a centralized configuration to maintain consistency across different model tasks.

*   **Global Configuration**: The script `tests/global_test_config.py` is executed before testing to set up the environment and define shared constants such as `DATA`, `TRAIN_SET`, `DEVICE`, and `EPOCHS` [[tests/global_test_config.py:19-28]](). It utilizes `benchpots.datasets.preprocess_random_walk` to generate a unified synthetic dataset for all tests [[tests/global_test_config.py:58-65]]().
*   **Execution Strategy**: Tests utilize `pytest-xdist` for parallel execution. The CI pipeline uses `-n 1` with `--dist=loadgroup` to manage test distribution and coverage reporting via `.coveragerc` [[.github/workflows/testing_ci.yml:81]]().
*   **Source Synchronization**: A unique step in the CI pipeline involves explicitly copying the local `pypots` source code into the Python `site-packages` directory to ensure the tests run against the latest local changes rather than a stale installed version [[.github/workflows/testing_ci.yml:67-70]]().
*   **Lazy Loading Validation**: The infrastructure supports validating lazy-loading from HDF5 files. `global_test_config.py` provides utility functions like `save_dict_into_h5` to prepare test files [[tests/global_test_config.py:133-145]](), which are then used by individual model tests to verify data fetching from disk [[pypots/imputation/mrnn/data.py:133-188]]().

For details, see [Test Architecture & Global Configuration](#6.1).

---

## CI/CD Workflows & Release Process

PyPOTS uses GitHub Actions to automate testing, linting, and deployment across multiple environments.

*   **CI Testing**: Triggered on every push to `main` or `dev`. It installs a specific version of PyTorch (CPU) before installing complex dependencies like `torch-sparse` and `torch-scatter` to ensure compatibility [[.github/workflows/testing_ci.yml:41-49, 61-63]]().
*   **Daily Testing**: A scheduled workflow runs every 24 hours (0:00 AM UTC) across a matrix of Operating Systems (`ubuntu-latest`, `windows-latest`, `macOS-latest`) using Conda environments and `requirements/conda_dev_env.yml` [[.github/workflows/testing_daily.yml:4-6, 19-37]]().
*   **Linting**: Code style is enforced via `ruff` to maintain high code quality across the repository [[.github/workflows/linting.yml:14-32]]().
*   **Automated Release**: Upon a new release tag or push to `release` branches, the `publish_to_PyPI.yml` workflow builds the package using `python -m build` and uploads it to PyPI using the `pypa/gh-action-pypi-publish` action [[.github/workflows/publish_to_PyPI.yml:12-20, 46-55]]().
*   **Community Management**: Automated workflows handle greetings for new contributors [[.github/workflows/greetings.yml:1-44]]() and manage stale issues/PRs to keep the backlog healthy [[.github/workflows/stale.yml:1-33]](). The project also uses structured issue templates and PR templates to guide contributors [[.github/PULL_REQUEST_TEMPLATE.md:1-31]]() [[.github/ISSUE_TEMPLATE/config.yml:1-11]]().

For details, see [CI/CD Workflows & Release Process](#6.2).

---

## Documentation Build (ReadTheDocs & Sphinx)

The documentation pipeline is decoupled from the main testing suite but integrated into the release lifecycle.

*   **Sphinx & Furo**: The documentation is built using Sphinx with the Furo theme to provide a modern, searchable technical reference.
*   **ReadTheDocs Integration**: Configured via `.readthedocs.yaml`, the build process handles complex dependency management including academic citations via `sphinxcontrib-bibtex`.
*   **Automatic Updates**: Documentation is automatically rebuilt when changes are pushed to the `main` branch or when a new version is released, ensuring the "coffee universe" ecosystem remains well-documented.

For details, see [Documentation Build (ReadTheDocs & Sphinx)](#6.3).

### Test Environment Entity Mapping
The following diagram bridges the CI/CD configuration files to the specific environment actions they perform.

**Code Entity to CI Action Mapping**
```mermaid
graph LR
    subgraph "CI_Logic"
        "testing_ci.yml" -- "installs" --> "torch_cpu[torch==2.3.0+cpu]"
        "testing_ci.yml" -- "syncs" --> "site_packages[site-packages/pypots]"
        "testing_daily.yml" -- "manages" --> "conda_env[conda_dev_env.yml]"
        "linting.yml" -- "executes" --> "ruff_cmd[ruff check .]"
    end

    subgraph "Test_Suite_Entities"
        "global_test_config.py" -- "defines" --> "DATA_const[Global_Constants]"
        "tests_dir[tests/]" -- "contains" --> "unit_tests[Unit_Tests]"
    end

    "testing_ci.yml" -- "calls" --> "pytest_cmd[pytest -n 1 --cov=pypots]"
    "pytest_cmd" -- "runs" --> "tests_dir"
    "testing_ci.yml" -- "generates" --> "lcov[coverage.lcov]"
```
**Sources:** [.github/workflows/testing_ci.yml:48, 70, 80-85](), [.github/workflows/testing_daily.yml:35](), [.github/workflows/linting.yml:31](), [tests/global_test_config.py:19-28]()

---

