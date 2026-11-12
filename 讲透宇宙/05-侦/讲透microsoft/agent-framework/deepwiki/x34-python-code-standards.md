<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/agent-framework · extra page Python Code Standards · fetched 2026-10-26 -->

# Python Code Standards

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/scripts/check_python_api_compatibility.py](.github/scripts/check_python_api_compatibility.py)
- [.github/skills/pull-requests/SKILL.md](.github/skills/pull-requests/SKILL.md)
- [.github/tests/test_python_api_compatibility.py](.github/tests/test_python_api_compatibility.py)
- [.github/workflows/python-dependency-maintenance.yml](.github/workflows/python-dependency-maintenance.yml)
- [.gitignore](.gitignore)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [docs/assets/readme-banner.png](docs/assets/readme-banner.png)
- [dotnet/.github/skills/pull-requests/SKILL.md](dotnet/.github/skills/pull-requests/SKILL.md)
- [dotnet/.gitignore](dotnet/.gitignore)
- [dotnet/nuget/NUGET.md](dotnet/nuget/NUGET.md)
- [dotnet/nuget/icon.png](dotnet/nuget/icon.png)
- [python/.github/instructions/python.instructions.md](python/.github/instructions/python.instructions.md)
- [python/.github/skills/agent-framework-py-release/SKILL.md](python/.github/skills/agent-framework-py-release/SKILL.md)
- [python/.github/skills/pull-requests/SKILL.md](python/.github/skills/pull-requests/SKILL.md)
- [python/.github/skills/python-development/SKILL.md](python/.github/skills/python-development/SKILL.md)
- [python/.github/skills/python-package-management/SKILL.md](python/.github/skills/python-package-management/SKILL.md)
- [python/.pre-commit-config.yaml](python/.pre-commit-config.yaml)
- [python/AGENTS.md](python/AGENTS.md)
- [python/CODING_STANDARD.md](python/CODING_STANDARD.md)
- [python/DEV_SETUP.md](python/DEV_SETUP.md)
- [python/packages/devui/frontend/src/lib/utils.ts](python/packages/devui/frontend/src/lib/utils.ts)
- [python/packages/ollama/LICENSE](python/packages/ollama/LICENSE)
- [python/packages/ollama/README.md](python/packages/ollama/README.md)
- [python/packages/ollama/agent_framework_ollama/__init__.py](python/packages/ollama/agent_framework_ollama/__init__.py)
- [python/packages/ollama/agent_framework_ollama/py.typed](python/packages/ollama/agent_framework_ollama/py.typed)
- [python/scripts/dependencies/README.md](python/scripts/dependencies/README.md)
- [python/scripts/dependencies/_dependency_bounds_lower_impl.py](python/scripts/dependencies/_dependency_bounds_lower_impl.py)
- [python/scripts/dependencies/_dependency_bounds_release_impl.py](python/scripts/dependencies/_dependency_bounds_release_impl.py)
- [python/scripts/dependencies/_dependency_bounds_runtime.py](python/scripts/dependencies/_dependency_bounds_runtime.py)
- [python/scripts/dependencies/_dependency_bounds_upper_impl.py](python/scripts/dependencies/_dependency_bounds_upper_impl.py)
- [python/scripts/dependencies/tests/test_dependency_bounds_release.py](python/scripts/dependencies/tests/test_dependency_bounds_release.py)
- [python/scripts/dependencies/validate_dependency_bounds.py](python/scripts/dependencies/validate_dependency_bounds.py)

</details>



This document describes the code quality tools, standards, and enforcement mechanisms for Python code in the Microsoft Agent Framework. It covers linting, formatting, type checking, task orchestration, and code coverage requirements. For .NET code standards, see 9.3.1. For broader testing and CI/CD architecture, see 9.2.

## Purpose and Scope

The Python implementation enforces code quality through automated tooling integrated into both local development workflows and CI/CD pipelines. The framework uses modern Python tooling centered on **ruff** for linting and formatting, **pyright** and **mypy** for type checking, and **uv** for high-performance dependency management. All quality checks are orchestrated through **poe** (poethepoet) task automation defined in `pyproject.toml` and shared task configurations.

Sources: [python/CODING_STANDARD.md:1-30](), [python/pyproject.toml:31-31]()

## Code Quality Tool Stack

The Python codebase uses the following tools, managed through the `uv` package manager [python/pyproject.toml:31-31]() and executed via `poe` tasks [python/packages/core/pyproject.toml:133-135]().

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **ruff** | Linting and formatting | `pyproject.toml` [python/pyproject.toml:113-178]() |
| **pyright** | Static type checking (Source only) | `pyproject.toml` [python/pyproject.toml:199-210]() |
| **mypy** | Strict type checking (Source + Tests) | `pyproject.toml` [python/packages/core/pyproject.toml:114-128]() |
| **pytest** | Unit and integration testing | `pyproject.toml` [python/pyproject.toml:179-193]() |
| **bandit** | Security scanning | `pyproject.toml` [python/packages/core/pyproject.toml:129-132]() |
| **poe** | Task orchestration | `shared_tasks.toml` [python/packages/core/pyproject.toml:135-135]() |

Sources: [python/pyproject.toml:31-210](), [python/packages/core/pyproject.toml:114-148]()

### Code Quality Pipeline Architecture

The following diagram illustrates the flow from local development through the quality gates in the CI pipeline.

Title: Python Quality Gates Data Flow
```mermaid
graph TB
    subgraph LocalDevelopment["Local_Development_uv_poe"]
        [VSCode] -->|"on_save"| [Ruff_Fmt]
        [VSCode] -->|"editor_integration"| [Pyright_LSP]
        [PoeTasks] -->|"poe_lint"| [Ruff_Check]
        [PoeTasks] -->|"poe_mypy"| [Mypy_Strict]
        [PoeTasks] -->|"poe_test"| [Pytest_Cov]
    end
    
    subgraph CIWorkflow["CI_Quality_Gates"]
        [GitHub_Actions] -->|"python-code-quality.yml"| [Lint_Job]
        [GitHub_Actions] -->|"python-test-coverage.yml"| [Test_Job]
    end
    
    [Lint_Job] --> [Ruff_Check]
    [Lint_Job] --> [Pyright_Verify]
    [Lint_Job] --> [Mypy_Strict]
    [Test_Job] --> [Pytest_Cov]
    [Pytest_Cov] -->|"85_percent_threshold"| [Coverage_Report]
```

Sources: [python/pyproject.toml:113-210](), [python/packages/core/pyproject.toml:133-148]()

## Coding Standards and Conventions

The framework maintains specific Pythonic conventions to ensure consistency across the monorepo workspace [python/CODING_STANDARD.md:1-27]().

### Formatting and Linting
*   **Line Length**: Set to 120 characters [python/CODING_STANDARD.md:9-9]().
*   **Target Python Version**: Python 3.10+ [python/CODING_STANDARD.md:10-10]().
*   **Ruff Rules**: The framework enables a broad set of rules including `ASYNC`, `B` (Bugbear), `CPY` (Copyright), `D` (Docstrings), `E/W` (Pycodestyle), `F` (Pyflakes), `I` (Isort), `S` (Bandit), and `RUF` (Ruff-specific) [python/pyproject.toml:127-149]().
*   **Docstring Style**: Google-style docstrings are enforced for all public functions, classes, and modules [python/CODING_STANDARD.md:11-11]().
*   **Copyright Header**: Every file must include the Microsoft copyright notice [python/CODING_STANDARD.md:1-1]() (e.g., `# Copyright (c) Microsoft. All rights reserved.`).

Sources: [python/CODING_STANDARD.md:1-27](), [python/pyproject.toml:113-178]()

### Type Annotation Policy
Type annotations are used as a helper rather than an end in itself, focusing on public interfaces while allowing pragmatism internally [python/CODING_STANDARD.md:28-35]().
*   **Future Annotations**: Use `from __future__ import annotations` at the top of files to enable postponed evaluation of annotations and eliminate the need for string-based type hints for forward references [python/CODING_STANDARD.md:36-54]().
*   **TypeVar Naming Convention**: Use the suffix `T` for TypeVar names instead of a prefix (e.g., `ChatResponseT = TypeVar("ChatResponseT", bound=ChatResponse)`) [python/CODING_STANDARD.md:56-70]().
*   **Mapping Types**: Use `Mapping` instead of `MutableMapping` for input parameters when mutation is not required [python/CODING_STANDARD.md:72-86]().
*   **Typing Ignore and Cast Policy**: 
    *   Source code (`agent_framework*`) is checked by `pyright` in strict mode — use `# pyright: ignore[...]` there, never `# type: ignore` [python/CODING_STANDARD.md:97-98]().
    *   Tests and samples use a relaxed profile; keep test bodies readable [python/CODING_STANDARD.md:99-103]().
    *   When accessing private members across internal packages, use targeted `# pyright: ignore[reportPrivateUsage]` rather than making internal helpers public [python/CODING_STANDARD.md:107-110]().
    *   Avoid typing-only pass-through wrappers that add runtime overhead [python/CODING_STANDARD.md:111-113]().

Sources: [python/CODING_STANDARD.md:28-114]()

### Function Parameter Guidelines
*   **Positional Parameters**: Restricted to up to 3 expected parameters where appropriate [python/CODING_STANDARD.md:115-119]().
*   **Keyword-only Parameters**: Arguments after `*` in function signatures are keyword-only and preferred for optional parameters [python/CODING_STANDARD.md:120-120]().
*   **String-based Overrides**: Avoid requiring callers to import extra modules by providing string-based configuration overrides [python/CODING_STANDARD.md:121-127]().

Sources: [python/CODING_STANDARD.md:115-127]()

## Association: Type Entities

Title: Natural Language to Code Entity Space - Typing
```mermaid
graph TD
    subgraph NaturalLanguage["Natural_Language_Space"]
        "Source_Type_Integrity"
        "Test_Type_Validation"
        "Dependency_Resolution"
        "Task_Automation"
    end

    subgraph CodeSpace["Code_Entity_Space"]
        [pyright] -- "tool.pyright"
        [mypy] -- "tool.mypy"
        [uv] -- "tool.uv"
        [poe] -- "tool.poe"
    end

    "Source_Type_Integrity" --- [pyright]
    "Test_Type_Validation" --- [mypy]
    "Dependency_Resolution" --- [uv]
    "Task_Automation" --- [poe]

    [poe] -.triggers.-> [pyright]
    [poe] -.triggers.-> [mypy]
    [uv] -.manages.-> [pyright]
```

Sources: [python/pyproject.toml:29-51](), [python/packages/core/pyproject.toml:114-148]()

## Code Coverage Enforcement

The framework maintains a strict coverage policy to ensure reliability across all packages.

### Coverage Execution and Reporting
*   **Tooling**: `pytest-cov` is used to measure execution coverage during test runs [python/pyproject.toml:36-36]().
*   **Configuration**: Coverage reports omit `__init__.py` files to avoid misleading statistics [python/pyproject.toml:194-197]().
*   **Task Orchestration**: Coverage is typically run via the `test` task, which includes `--cov` arguments [python/packages/core/pyproject.toml:145-147]().
*   **Thresholds**: CI pipelines enforce a minimum coverage threshold (typically 85%) before allowing merges.

Sources: [python/pyproject.toml:194-198](), [python/packages/core/pyproject.toml:145-147]()

## Package Management and Build System

The framework uses a monorepo structure managed by `uv` workspaces [python/pyproject.toml:73-74]().

### Build and Distribution
*   **Build Backends**: Packages use modern build standards such as `flit_core.buildapi` [python/packages/core/pyproject.toml:152]() or `hatchling.build` [python/packages/ag-ui/pyproject.toml:52-52]().
*   **Dependency Groups**: Dependencies are split into `dev` (tooling) and `test` (integration requirements) groups [python/pyproject.toml:29-58]().
*   **Workspace Management**: Sub-packages are organized under `packages/` and managed via workspace inheritance.

Sources: [python/pyproject.toml:73-111](), [python/packages/core/pyproject.toml:152]()

### Association: Workspace Structure

Title: Natural Language to Code Entity Space - Workspace
```mermaid
graph TD
    subgraph NaturalLanguage["Natural_Language_Space"]
        "Monorepo_Root"
        "Core_Logic"
        "Experimental_Lab"
        "UI_Integration"
    end

    subgraph CodeSpace["Code_Entity_Space"]
        [python_pyproject] -- "python/pyproject.toml"
        [packages_core] -- "packages/core"
        [packages_lab] -- "packages/lab"
        [packages_ag_ui] -- "packages/ag-ui"
    end

    "Monorepo_Root" --- [python_pyproject]
    "Core_Logic" --- [packages_core]
    "Experimental_Lab" --- [packages_lab]
    "UI_Integration" --- [packages_ag_ui]

    [python_pyproject] -.defines_workspace.-> [packages_core]
    [python_pyproject] -.defines_workspace.-> [packages_lab]
    [python_pyproject] -.defines_workspace.-> [packages_ag_ui]
```

Sources: [python/pyproject.toml:73-111](), [python/packages/core/pyproject.toml:1-31]()

---

