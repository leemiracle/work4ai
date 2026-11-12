<!-- source: DeepWiki mcp.deepwiki.com · repo stanfordnlp/dspy · page 7 Development & Contributing · fetched 2026-10-27 -->

# Development & Contributing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/.internal_dspyai/pyproject.toml](.github/.internal_dspyai/pyproject.toml)
- [.github/.tmp/.generated-actions/run-pypi-publish-in-docker-container/action.yml](.github/.tmp/.generated-actions/run-pypi-publish-in-docker-container/action.yml)
- [.github/workflows/build_and_release.yml](.github/workflows/build_and_release.yml)
- [.github/workflows/dependency-range.yml](.github/workflows/dependency-range.yml)
- [.github/workflows/docs-push.yml](.github/workflows/docs-push.yml)
- [.github/workflows/precommits_check.yml](.github/workflows/precommits_check.yml)
- [.github/workflows/run_tests.yml](.github/workflows/run_tests.yml)
- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [dspy/__metadata__.py](dspy/__metadata__.py)
- [pyproject.toml](pyproject.toml)
- [uv.lock](uv.lock)

</details>



This document provides technical information for contributors to the DSPy project. It covers the build system, testing infrastructure, documentation generation, and release workflows. For tutorials on building and optimizing DSPy programs, see [Building DSPy Programs](#3) and [Program Optimization](#4).

## Development Environment Setup

DSPy uses `uv` as its package manager and build tool, along with `ruff` for code formatting and linting. The development environment is configured through [pyproject.toml:1-193]().

The following diagram maps each `pyproject.toml` section to its role in the development system:

**pyproject.toml Section Roles**
```mermaid
graph LR
    subgraph "pyproject.toml"
        BS["[build-system]"]
        P["[project]"]
        OD["[project.optional-dependencies]"]
        PF["[tool.setuptools.packages.find]"]
        PT["[tool.pytest.ini_options]"]
        R["[tool.ruff]"]
        CV["[tool.coverage.run]"]
    end
    BS --> BLD["setuptools.build_meta"]
    P --> PKG["name, version, requires-python, dependencies"]
    OD --> EXT["dev / test_extras / anthropic / mcp / optuna / weaviate / langchain"]
    PF --> DISC["include: dspy, dspy.*"]
    PT --> PCT["filterwarnings (litellm pydantic warnings)"]
    R --> LINT["lint.select, format, per-file-ignores"]
    CV --> COV["omit patterns, branch=true"]
```

Sources: [pyproject.toml:1-193]()

### Package Manager: uv

The project recommends [uv](https://github.com/astral-sh/uv) for fast, reliable dependency management [CONTRIBUTING.md:105-109]().

**Key Configuration:**
- Minimum Python version: `>=3.10, <3.15` [pyproject.toml:16]()
- Build backend: `setuptools` [pyproject.toml:3]()
- Package discovery: Includes `dspy` and `dspy.*` subpackages [pyproject.toml:74-77]()

For details on dependency management and CI integration, see [Build System & CI/CD](#7.1).

### Code Quality Tools

**Ruff** is configured for linting and formatting [pyproject.toml:124-193](). DSPy follows the Google Python Style Guide [CONTRIBUTING.md:40]().

```mermaid
graph LR
    Developer["Developer"] --> PreCommit["pre-commit hooks"]
    PreCommit --> RuffCheck["ruff check --fix"]
    PreCommit --> RuffFormat["ruff format"]
    RuffCheck --> Rules["Enabled Rules:<br/>pycodestyle, pyflakes,<br/>isort, flake8"]
    RuffFormat --> Style["Code Style:<br/>120 char line length<br/>double quotes"]
```

**Configuration Highlights:**
- Line length: 120 characters [pyproject.toml:132]()
- Target version: Python 3.10 [pyproject.toml:134]()
- Enabled rule sets: E, W, F, I, C, B, UP, N, RUF, Q [pyproject.toml:137-148]()
- Automatic fixes available for all rules [pyproject.toml:165]()

### Pre-commit Hooks

Pre-commit hooks enforce code quality before commits. Install them with `pre-commit install` [CONTRIBUTING.md:45]().

The pre-commit configuration runs `ruff` and standard hooks like `check-yaml` and `check-added-large-files` [.pre-commit-config.yaml:1-25]().

Sources: [pyproject.toml:1-193](), [CONTRIBUTING.md:40-74](), [.pre-commit-config.yaml:1-25]()

## Continuous Integration Pipeline

The CI/CD pipeline runs on every push to `main` and on pull requests through GitHub Actions defined in [.github/workflows/run_tests.yml:1-135]().

### CI/CD Architecture

```mermaid
graph TB
    subgraph "Triggers"
        Push["Push to main"]
        PR["Pull Request"]
    end
    
    subgraph "Jobs"
        Fix["fix:<br/>Check Ruff Fix"]
        Test["test:<br/>Run Tests<br/>Python 3.10-3.14"]
        LLMTest["llm_call_test:<br/>Real LM Tests"]
        ExtraTest["extra_test:<br/>Run Extra and Deno Tests"]
    end
    
    subgraph "Fix Job Steps"
        UVInstall1["Install uv"]
        RuffCheckStep["ruff check --fix-only"]
    end
    
    subgraph "Test Job Steps"
        UVInstall2["Install uv + dependencies"]
        Pytest["pytest tests/ -m 'not extra and not deno'"]
    end
    
    subgraph "Extra Test Job Steps"
        UVInstall3["Install uv + test_extras"]
        DenoInstall["Install Deno"]
        ExtraPytest["pytest -m 'extra or deno'"]
    end
    
    subgraph "LLM Test Job Steps"
        OllamaCache["Cache Ollama models"]
        OllamaStart["Start Ollama Docker"]
        LLMPytest["pytest -m llm_call"]
    end
    
    Push --> Fix
    Push --> Test
    Push --> LLMTest
    Push --> ExtraTest
    PR --> Fix
    PR --> Test
    PR --> LLMTest
    PR --> ExtraTest
    
    Fix --> UVInstall1 --> RuffCheckStep
    Test --> UVInstall2 --> Pytest
    ExtraTest --> UVInstall3 --> DenoInstall --> ExtraPytest
    LLMTest --> OllamaCache --> OllamaStart --> LLMPytest
```

For a deep dive into the CI/CD stages and configuration, see [Build System & CI/CD](#7.1).

Sources: [.github/workflows/run_tests.yml:1-141](), [.github/workflows/dependency-range.yml:1-111]()

## Testing Framework

DSPy uses `pytest` with custom markers to manage different testing environments, such as local execution vs. remote LLM calls.

### Test Categories

- **Core Tests**: Standard unit tests run on every CI pass [.github/workflows/run_tests.yml:101]().
- **Extra Tests**: Tests requiring optional dependencies like `mcp` or `langchain_core`, triggered by the `extra` marker [.github/workflows/run_tests.yml:134]().
- **Deno Tests**: Tests requiring the Deno JavaScript runtime, used for sandboxed code execution [.github/workflows/run_tests.yml:132-134]().
- **LLM Call Tests**: Integration tests that communicate with real language models, typically using a local Ollama instance running `ollama/ollama:0.31.2` in CI [.github/workflows/run_tests.yml:148-192]().

For details on test structure and best practices, see [Testing Framework](#7.2).

Sources: [.github/workflows/run_tests.yml:101-192](), [pyproject.toml:116-122]()

## Documentation System

The documentation is built using MkDocs and hosted at [dspy.ai](https://dspy.ai). 

- **MkDocs**: The primary engine for rendering Markdown to HTML.
- **Update Workflow**: Documentation changes are validated on pull requests and pushed to a separate repository on main branch updates [.github/workflows/docs-push.yml:16-52]().

For details on contributing to documentation, see [Documentation System](#7.3).

Sources: [.github/workflows/docs-push.yml:1-52]()

## Package Metadata and Release Process

DSPy maintains versioning through a coordinated update of `pyproject.toml` and `dspy/__metadata__.py`.

### Release Workflow

1. **Tagging**: A release is triggered by pushing a git tag [.github/workflows/build_and_release.yml:3-6]().
2. **TestPyPI Validation**: The package is first built as `dspy-ai-test-isaac` and published to TestPyPI for verification [.github/workflows/build_and_release.yml:50-80]().
3. **PyPI Publication**: Upon successful validation, the workflow publishes the official `dspy` package and a compatibility alias `dspy-ai` [.github/workflows/build_and_release.yml:137-158]().

For the complete release checklist and version management details, see [Package Metadata & Release Process](#7.4).

Sources: [.github/workflows/build_and_release.yml:1-158](), [dspy/__metadata__.py:1-8](), [.github/.internal_dspyai/pyproject.toml:1-14]()

## Contributing Guidelines

### Finding an Issue
Contributors can look for issues labeled `good first issue` or `help wanted` on the GitHub repository [CONTRIBUTING.md:9-12]().

### AI-Generated Contributions
DSPy is pro-AI assisted coding but requires contributors to understand every line submitted [CONTRIBUTING.md:156-158]().
- Fully autonomous agent contributions are prohibited [CONTRIBUTING.md:159-160]().
- AI-assisted PRs must disclose the tool used and share prompts [CONTRIBUTING.md:167-168]().

### Pull Request Process
1. **Open an Issue**: Discuss major changes before implementation [CONTRIBUTING.md:23-26]().
2. **Fork & Setup**: Create a local dev environment using `uv` [CONTRIBUTING.md:105-122]().
3. **Lint & Format**: Ensure all pre-commit hooks pass [CONTRIBUTING.md:40-57]().
4. **Submit**: Open a PR to the `main` branch [CONTRIBUTING.md:75-78]().

Sources: [CONTRIBUTING.md:1-179]()

---

