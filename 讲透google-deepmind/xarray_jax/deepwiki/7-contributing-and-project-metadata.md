<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/xarray_jax · page 7 Contributing and Project Metadata · fetched 2026-10-26 -->

# Contributing and Project Metadata

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [LICENSE](LICENSE)
- [pyproject.toml](pyproject.toml)

</details>



This page provides an overview of the contribution processes, community standards, and technical metadata for the `xarray_jax` project. It serves as a high-level entry point for developers looking to participate in the project or understand its packaging structure.

## Contribution Overview

`xarray_jax` is an open-source project managed by Google DeepMind. We welcome external contributions that improve the integration between xarray and JAX. 

### Proposal and Review Process
For substantial changes or modifications that may affect backward compatibility, contributors are encouraged to open a GitHub issue to discuss the proposal before implementation [CONTRIBUTING.md:3-6](). All code submissions, including those from internal project members, must undergo a formal code review via GitHub Pull Requests [CONTRIBUTING.md:19-24]().

### Legal and Community Standards
*   **Contributor License Agreement (CLA):** All contributors must sign a Google CLA to grant permission for the redistribution of their work [CONTRIBUTING.md:7-13]().
*   **Community Guidelines:** This project adheres to [Google's Open Source Community Guidelines](https://opensource.google/conduct/) [CONTRIBUTING.md:26-29]().
*   **License:** The project is distributed under the **Apache-2.0** license [pyproject.toml:10-11](), [LICENSE:2-4]().

For a step-by-step guide on submitting code, see the [Contributing Guide](#7.1).

**Sources:** [CONTRIBUTING.md:1-30](), [pyproject.toml:10-11](), [LICENSE:1-132]()

---

## Project Metadata and Configuration

The project uses a modern Python packaging stack centered around `pyproject.toml`. It utilizes `setuptools` as the build backend and supports dynamic versioning tied to the package's internal `__version__` attribute.

### Dependency Profile
The project maintains strict minimum version requirements to ensure compatibility with the evolving JAX and xarray ecosystems:
*   **Python:** `>=3.13` [pyproject.toml:12-12]()
*   **JAX:** `>=0.4.30` [pyproject.toml:25-25]()
*   **xarray:** `>=2026.01.0` [pyproject.toml:27-27]()
*   **NumPy:** `>=1.24` [pyproject.toml:26-26]()

### Package Structure
The build system is configured to discover two primary packages: the core library `xarray_jax` and its associated test suite `xarray_jax.tests` [pyproject.toml:43-44](). Optional dependencies for testing include `absl-py` and `chex` [pyproject.toml:30-34]().

For detailed information on build hooks and versioning logic, see [Package Configuration and Versioning](#7.2).

**Sources:** [pyproject.toml:1-45]()

---

## Mapping Contributions to Code Entities

The following diagrams illustrate the relationship between the contribution process and the underlying project configuration.

### Contribution Workflow and Artifacts
This diagram maps the natural language "Contribution Process" to the specific files and external systems involved.

```mermaid
graph TD
    subgraph "External Systems"
        ["GitHub PR System"]
        ["Google CLA Portal"]
    end

    subgraph "Project Metadata Entities"
        [CONTRIBUTING.md]
        [LICENSE]
        [pyproject.toml]
    end

    "Contributor" -- "Signs" --> ["Google CLA Portal"]
    "Contributor" -- "Reads Guidelines" --> [CONTRIBUTING.md]
    "Contributor" -- "Submits Code" --> ["GitHub PR System"]
    ["GitHub PR System"] -- "Validates against" --> [pyproject.toml]
    [LICENSE] -- "Governs" --> "Contributor"
```
**Sources:** [CONTRIBUTING.md:1-30](), [pyproject.toml:1-45](), [LICENSE:1-132]()

### Package Metadata Association
This diagram bridges the project's conceptual metadata to the specific keys and attributes defined in the configuration files.

```mermaid
graph LR
    subgraph "pyproject.toml"
        ["project.name"]
        ["project.dependencies"]
        ["tool.setuptools.dynamic"]
    end

    subgraph "Codebase Symbols"
        ["xarray_jax.__version__"]
    end

    ["project.name"] -- "Defines" --> ["gdm-xarray-jax"]
    ["project.dependencies"] -- "Requires" --> ["jax >= 0.4.30"]
    ["project.dependencies"] -- "Requires" --> ["xarray >= 2026.01.0"]
    ["tool.setuptools.dynamic"] -- "Reads from" --> ["xarray_jax.__version__"]
```
**Sources:** [pyproject.toml:5-41]()

---

## Child Pages
*   **[Contributing Guide](#7.1)**: Detailed instructions on the CLA, PR workflow, and proposal process.
*   **[Package Configuration and Versioning](#7.2)**: Deep dive into `pyproject.toml`, build requirements, and dependency management.

---

