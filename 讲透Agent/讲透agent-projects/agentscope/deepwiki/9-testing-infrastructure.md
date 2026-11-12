<!-- source: DeepWiki mcp.deepwiki.com · repo agentscope-ai/agentscope · page 9 Testing Infrastructure · fetched 2026-10-30 -->

# Testing Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/pre-commit.yml](.github/workflows/pre-commit.yml)
- [.github/workflows/publish-pypi.yml](.github/workflows/publish-pypi.yml)
- [.github/workflows/stale.yml](.github/workflows/stale.yml)
- [.github/workflows/unittest.yml](.github/workflows/unittest.yml)
- [examples/workspace/apple-container-workspace.md](examples/workspace/apple-container-workspace.md)
- [src/agentscope/app/workspace_manager/_applecontainer_workspace_manager.py](src/agentscope/app/workspace_manager/_applecontainer_workspace_manager.py)
- [src/agentscope/workspace/_applecontainer/__init__.py](src/agentscope/workspace/_applecontainer/__init__.py)
- [src/agentscope/workspace/_applecontainer/_applecontainer_backend.py](src/agentscope/workspace/_applecontainer/_applecontainer_backend.py)
- [src/agentscope/workspace/_applecontainer/_applecontainer_workspace.py](src/agentscope/workspace/_applecontainer/_applecontainer_workspace.py)
- [src/agentscope/workspace/_applecontainer/_constants.py](src/agentscope/workspace/_applecontainer/_constants.py)
- [tests/backend_applecontainer_test.py](tests/backend_applecontainer_test.py)
- [tests/workspace_applecontainer_test.py](tests/workspace_applecontainer_test.py)

</details>



AgentScope employs a multi-tiered testing strategy to ensure the reliability of its SDK, model adapters, and execution environments. The infrastructure spans from local unit tests with mocked models to integration tests running in sandboxed containers and automated CI/CD pipelines.

### Testing Architecture Overview

The testing suite is designed to validate both the logic of the SDK and the connectivity of the model layer. It utilizes `pytest` for unit testing and specialized scripts for verifying LLM provider integrations.

#### Test Execution Flow
The following diagram illustrates how tests interact with different layers of the AgentScope ecosystem, mapping high-level test types to specific code entities.

**AgentScope Testing Data Flow**
```mermaid
graph TD
    subgraph "Local_Environment"
        [pytest] --> [Unit_Tests]
        [Unit_Tests] --> ["MockModel"]
        ["MockModel"] -.-> [Agent_Logic]
    end

    subgraph "Sandboxed_Environments"
        [Integration_Tests] --> ["AppleContainerBackend"]
        ["AppleContainerBackend"] --> ["container_CLI"]
        ["AppleContainerWorkspace"] --> ["SandboxedWorkspaceBase"]
    end

    subgraph "External_Providers"
        ["run_tests.py"] --> ["Provider_Scripts"]
        ["Provider_Scripts"] --> [Remote_LLM_APIs]
    end

    [CI_CD_Pipeline] --> [pytest]
    [CI_CD_Pipeline] --> [Integration_Tests]

    style "MockModel" stroke-dasharray: 5 5
    style "AppleContainerBackend" stroke-dasharray: 5 5
```
**Sources:** [.github/workflows/unittest.yml:30-34](), [src/agentscope/workspace/_applecontainer/_applecontainer_backend.py:23-25](), [src/agentscope/workspace/_applecontainer/_applecontainer_workspace.py:75-85]()

---

### Unit & Integration Tests

The core of the test suite resides in the `tests/` directory. It covers every major component, including agents, middleware, formatters, and storage backends. To avoid high API costs and latency during development, AgentScope provides a comprehensive mocking utility.

*   **Mocking Framework**: The `MockModel` class allows developers to simulate complex LLM behaviors, including streaming responses, structured JSON outputs, and API exceptions, without making actual network calls.
*   **Workspace Testing**: Specialized tests for sandboxed environments, such as `tests/backend_applecontainer_test.py`, verify that shell commands and file I/O operate correctly within isolated containers via `AppleContainerBackend` [tests/backend_applecontainer_test.py:39-46]().
*   **Utility Helpers**: The suite uses specific patterns to verify asynchronous behavior and CLI command construction [tests/backend_applecontainer_test.py:57-75]().

For a detailed breakdown of test categories and mocking patterns, see **[Unit & Integration Tests](#9.1)**.

**Sources:** [tests/backend_applecontainer_test.py:1-118](), [tests/workspace_applecontainer_test.py:1-73]()

---

### Model Example Scripts

Located in `scripts/model_examples/`, these scripts serve a dual purpose: they act as executable documentation for users and as a functional test suite for LLM provider adapters.

*   **Unified Runner**: The `run_tests.py` script provides a single entry point to detect available API keys and run provider-specific tests.
*   **Provider Coverage**: Individual scripts exercise specific features like reasoning blocks and tool calling. These scripts are essential for validating the `ChatModelBase` implementations across different providers.

For details on setting up environment variables and running these scripts, see **[Model Example Scripts](#9.2)**.

---

### Sandboxed Workspace Tests

AgentScope includes robust testing for its sandboxed execution layers, ensuring that tools (like Bash or File I/O) behave consistently across different backends.

*   **Apple Container Testing**: The `AppleContainerWorkspaceManager` manages container lifecycles with TTL-based caching and background sweeping [src/agentscope/app/workspace_manager/_applecontainer_workspace_manager.py:37-48](). Tests verify that `AppleContainerWorkspace` correctly pulls images and bootstraps the gateway [src/agentscope/workspace/_applecontainer/_applecontainer_workspace.py:157-191]().
*   **Backend Primitives**: `AppleContainerBackend` implements `exec_shell`, `read_file`, and `write_file` using the `container` CLI [src/agentscope/workspace/_applecontainer/_applecontainer_backend.py:23-52](). Unit tests mock `asyncio.create_subprocess_exec` to verify command construction and error handling [tests/backend_applecontainer_test.py:57-75]().

**Sources:** [src/agentscope/workspace/_applecontainer/_applecontainer_backend.py:1-140](), [src/agentscope/app/workspace_manager/_applecontainer_workspace_manager.py:37-114](), [src/agentscope/workspace/_applecontainer/_applecontainer_workspace.py:75-154]()

---

### CI/CD Pipeline

The project uses GitHub Actions to automate testing across multiple operating systems and Python versions.

| Component | Description |
| :--- | :--- |
| **Workflow** | `unittest.yml` triggers on every push and pull request [.github/workflows/unittest.yml:1-3]() |
| **Matrix** | Runs on `ubuntu-latest`, `windows-latest`, and `macos-26` [.github/workflows/unittest.yml:8-11]() |
| **Dependencies** | Uses `uv` for fast dependency installation and `bubblewrap` for Linux sandboxing tests [.github/workflows/unittest.yml:17-25]() |
| **Coverage** | Generates a coverage report using `pytest` and `coverage` [.github/workflows/unittest.yml:30-37]() |
| **Publishing** | `publish-pypi.yml` automates package builds and uploads to PyPI upon release [.github/workflows/publish-pypi.yml:9-43]() |

**CI/CD Entity Mapping**
```mermaid
graph LR
    subgraph "GitHub_Actions"
        ["unittest.yml"] --> ["setup-uv@v5"]
        ["setup-uv@v5"] --> ["uv_pip_install"]
        ["uv_pip_install"] --> ["pytest_tests"]
        ["pytest_tests"] --> ["coverage_report"]
        ["publish-pypi.yml"] --> ["pypa/gh-action-pypi-publish"]
    end
```
**Sources:** [.github/workflows/unittest.yml:1-37](), [.github/workflows/publish-pypi.yml:1-43](), [.github/workflows/pre-commit.yml:1-29]()

---

