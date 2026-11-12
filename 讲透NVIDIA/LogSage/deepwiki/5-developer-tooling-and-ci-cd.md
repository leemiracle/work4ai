<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/LogSage · page 5 Developer Tooling and CI/CD · fetched 2026-10-26 -->

# Developer Tooling and CI/CD

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitlab-ci.yml](.gitlab-ci.yml)
- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [Makefile](Makefile)

</details>



This section provides an overview of the infrastructure supporting the LogSage development lifecycle. The project employs a standardized toolchain to ensure code quality, type safety, and automated delivery. The workflow is centered around a containerized development environment, a comprehensive suite of pre-commit hooks for local validation, and a multi-stage GitLab CI/CD pipeline for testing and distribution.

## Development Environment Setup

LogSage is designed to be developed within a consistent environment to eliminate "works on my machine" issues. The primary entry point for developers is the `Makefile`, which orchestrates the setup of a [Poetry](https://python-poetry.org/) virtual environment and local configuration [Makefile:72-82]().

Key components of the setup include:
*   **VS Code Dev Containers**: A pre-configured environment using a `Dockerfile` and `devcontainer.json` to provide all system dependencies, including `zsh` and `powerlevel10k`.
*   **Poetry Management**: Dependency resolution and virtual environment isolation are handled by Poetry [Makefile:75-79]().
*   **Automated Configuration**: The `make install` target automatically updates `pyproject.toml` based on the local Python version and configures private NVIDIA PyPI repositories [Makefile:52-67, 164-171]().

For detailed instructions on environment variables and container setup, see [Development Environment Setup](#5.1).

**Sources:** [Makefile:1-171]()

## Linting, Formatting, and Pre-commit Hooks

The project enforces strict code quality standards through an automated toolchain integrated into the Git workflow via `pre-commit`.

| Tool | Purpose | Configuration |
| :--- | :--- | :--- |
| **Ruff** | Replaces Black, isort, and Pylint for high-speed linting and formatting. | [.pre-commit-config.yaml:16-23]() |
| **MyPy** | Static type checking to ensure type safety across Pydantic models. | [.pre-commit-config.yaml:25-29]() |
| **detect-secrets** | Scans for accidentally committed credentials or API keys. | [.pre-commit-config.yaml:41-45]() |
| **Prettier** | Formats non-Python files like YAML and Markdown. | [.pre-commit-config.yaml:32-38]() |
| **licensecheck** | Validates 3rd-party licenses against `LICENSE-3rd-party.txt`. | [Makefile:118-119]() |

Developers can trigger these checks manually using `make lint`, `make format`, or `make hooks` [Makefile:91-113]().

For details on specific rule configurations and hook stages, see [Linting, Formatting, and Pre-commit Hooks](#5.2).

**Sources:** [.pre-commit-config.yaml:1-54](), [Makefile:91-119]()

## CI/CD Pipeline

The LogSage CI/CD pipeline is defined in `.gitlab-ci.yml` and utilizes a modular structure located in the `.gitlab/` directory [`.gitlab-ci.yml:1-9`](). The pipeline ensures that every contribution meets the project's quality bar before it can be merged or released.

### Pipeline Architecture: Code to Artifact

The following diagram illustrates how code moves from a developer's machine through the automated validation and release stages.

**LogSage CI/CD Flow**
```mermaid
graph TD
    subgraph "Local_Dev_Space"
        A["git commit"] --> B["pre-commit hooks"]
        B -- "ruff/mypy/secrets" --> C["git push"]
    end

    subgraph "GitLab_CI_Pipeline"
        C --> D["Stage: test"]
        D --> D1["job: pytest (test-coverage)"]
        D1 --> E{ "Branch/Tag?" }
        
        E -- "Main Branch" --> F["Merge Ready"]
        E -- "Version Tag (v*)" --> G["Stage: deploy"]
        
        G --> G1["job: build_wheel (poetry build)"]
        G1 --> G2["job: publish (twine/poetry)"]
    end

    subgraph "Artifact_Registry"
        G2 --> H["GitLab Package Registry"]
        G2 --> I["NVIDIA Private PyPI"]
    end

    style D1 stroke-width:2px
    style G1 stroke-width:2px
```
**Sources:** [.gitlab-ci.yml:1-9](), [Makefile:129-136, 160-162]()

### Release Automation
Version management is handled via `bump2version`, which synchronizes version strings across the codebase and creates Git tags [Makefile:142-158](). When a tag is pushed, the pipeline triggers the `deploy` stage to build the wheel package and publish it to the configured registries [Makefile:160-162]().

For a deep dive into pipeline job definitions and registry authentication, see [CI/CD Pipeline](#5.3).

**Sources:** [Makefile:142-162](), [.gitlab-ci.yml:1-3]()

## Developer Tooling Summary

The following table maps common developer tasks to their corresponding `Makefile` targets:

| Task | Command | Code Reference |
| :--- | :--- | :--- |
| **Full Setup** | `make install` | [Makefile:72-82]() |
| **Run Tests** | `make test-coverage` | [Makefile:129-136]() |
| **Lint/Format** | `make lint && make format` | [Makefile:94-108]() |
| **Check Secrets** | `make secrets` | [Makefile:114-117]() |
| **Version Bump** | `make bump-patch` | [Makefile:142-147]() |
| **Build Package** | `make build` | [Makefile:160-163]() |

**Sources:** [Makefile:1-163]()

---

