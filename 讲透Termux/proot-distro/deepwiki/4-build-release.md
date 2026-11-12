<!-- source: DeepWiki mcp.deepwiki.com · repo termux/proot-distro · page 4 Build & Release · fetched 2026-10-26 -->

# Build & Release

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/publish.yml](.github/workflows/publish.yml)
- [pyproject.toml](pyproject.toml)
- [screenshot.png](screenshot.png)

</details>



With the transition to v5.1, `proot-distro` has solidified its move from a shell-based distribution system to a modern Python packaging and release pipeline. The build system focuses on producing a Python package (Wheel and Source Distribution) and publishing it to PyPI using secure, automated workflows, while also managing shell completion assets.

## Overview

The `proot-distro` build and release architecture is centered around standard Python tooling and GitHub Actions. v5.1 leverages `setuptools` for packaging and OIDC-based "Trusted Publishing" for secure delivery to the Python Package Index (PyPI).

```mermaid
flowchart TD
    subgraph "Development & Packaging"
        PY["pyproject.toml"] --> |defines| MET["Metadata & Scripts"]
        MET --> |entry points| PD_CLI["proot-distro / pd"]
        MET --> |backend| ST["setuptools >= 77"]
        PY --> |data-files| COMP["Shell Completions"]
    end

    subgraph "CI/CD Pipeline (GitHub Actions)"
        TAG["Git Tag (v*)"] --> |triggers| GHA["publish.yml"]
        GHA --> |step 1| BUILD["Build Job"]
        BUILD --> |runs| P_BUILD["python -m build"]
        P_BUILD --> |outputs| DIST["dist/ (sdist & wheel)"]
        
        DIST --> |upload-artifact| ART["GitHub Artifacts (v7)"]
        ART --> |download-artifact| PUB["Publish Job (v8)"]
        
        PUB --> |OIDC Auth| PYPI[("PyPI Registry")]
    end

    PD_CLI --> |refers to| PROOT_CLI["proot_distro.cli:main"]
```

Sources: [pyproject.toml:1-32](), [.github/workflows/publish.yml:1-52]()

## Python Packaging

The core of the build system is the `pyproject.toml` file. It defines the project as a pure Python package with zero third-party dependencies, ensuring maximum compatibility within the Termux environment.

*   **Build Backend**: Uses `setuptools.build_meta` with a requirement for `setuptools>=77` [pyproject.toml:1-3]().
*   **Requirements**: Requires Python >= 3.9 [pyproject.toml:10-10]().
*   **Entry Points**: Defines two console scripts, `proot-distro` and the shorthand `pd`, both mapping to `proot_distro.cli:main` [pyproject.toml:19-21]().
*   **Asset Management**: Includes logic for installing shell completions for Bash, Zsh, and Fish into standard system paths [pyproject.toml:29-32]().

For details on version management via `importlib.metadata` and local installation from source, see [Python Packaging](#4.1).

Sources: [pyproject.toml:1-32]()

## Automated Release Pipeline

Release automation is handled by the `Publish to PyPI` workflow. This pipeline ensures that every tagged version (e.g., `v5.1.4`) is built in a clean environment and delivered securely to users.

### Release Workflow Logic

| Stage | Action | Entity/Tool |
|:---|:---|:---|
| **Trigger** | Push of a tag starting with `v*` | GitHub Actions [publish.yml:3-6]() |
| **Build** | Generate `.tar.gz` (sdist) and `.whl` (wheel) | `python -m build` [publish.yml:21-25]() |
| **Handover** | Transfer build files between jobs | `actions/upload-artifact@v7` and `download-artifact@v8` [publish.yml:28, 45]() |
| **Publish** | Upload to PyPI via OIDC | `pypa/gh-action-pypi-publish` [publish.yml:50-51]() |

### Security via OIDC
The workflow uses **Trusted Publishing**. Instead of storing sensitive API tokens in GitHub Secrets, the `publish` job requests a short-lived identity token from GitHub's OIDC provider by setting `permissions: id-token: write` [publish.yml:40-41](). This identity is verified by PyPI based on the repository and environment [publish.yml:37-39]().

For details on the CI/CD configuration and artifact lifecycle, see [GitHub Actions & PyPI Release](#4.2).

Sources: [.github/workflows/publish.yml:1-52]()

## Code-to-System Mapping

The following diagram maps the high-level release concepts to the specific files and configurations that implement them in the `proot-distro` repository.

```mermaid
graph LR
    subgraph "Code Entities"
        P_TOML["pyproject.toml"]
        PUB_YML[".github/workflows/publish.yml"]
        CLI_MAIN["proot_distro/cli.py"]
        COMP_DIR["proot_distro/completions/"]
    end

    subgraph "System Roles"
        SCRIPTS["Console Scripts (pd)"]
        CI_CD["Release Pipeline (OIDC)"]
        METADATA["Package Metadata (v5.1.4)"]
        SHELL["Shell Completion Provider"]
    end

    P_TOML -- "[project.scripts]" --> SCRIPTS
    P_TOML -- "[project]" --> METADATA
    P_TOML -- "[tool.setuptools.data-files]" --> SHELL
    COMP_DIR -- "contains" --> SHELL
    PUB_YML -- "jobs: publish" --> CI_CD
    SCRIPTS -- "points to" --> CLI_MAIN
```

Sources: [pyproject.toml:5-32](), [.github/workflows/publish.yml:33-52]()

---

