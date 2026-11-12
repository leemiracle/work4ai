<!-- source: DeepWiki mcp.deepwiki.com · repo agno-agi/agno · page 9 Development and Operations · fetched 2026-10-26 -->

# Development and Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.cursorrules](.cursorrules)
- [.github/workflows/claude.yml](.github/workflows/claude.yml)
- [.github/workflows/test.yml](.github/workflows/test.yml)
- [.gitignore](.gitignore)
- [AGENTS.md](AGENTS.md)
- [CLAUDE.md](CLAUDE.md)
- [cookbook/05_agent_os/27_public_pages/implementation.md](cookbook/05_agent_os/27_public_pages/implementation.md)
- [cookbook/05_agent_os/27_public_pages/public_control_plane.py](cookbook/05_agent_os/27_public_pages/public_control_plane.py)
- [cookbook/05_agent_os/27_public_pages/public_pages.py](cookbook/05_agent_os/27_public_pages/public_pages.py)
- [cookbook/README.md](cookbook/README.md)
- [libs/agno/agno/db/postgres/_bounded.py](libs/agno/agno/db/postgres/_bounded.py)
- [libs/agno/agno/knowledge/page/_source.py](libs/agno/agno/knowledge/page/_source.py)
- [libs/agno/agno/os/public/__init__.py](libs/agno/agno/os/public/__init__.py)
- [libs/agno/agno/os/public/_limits.py](libs/agno/agno/os/public/_limits.py)
- [libs/agno/agno/os/public/_middleware.py](libs/agno/agno/os/public/_middleware.py)
- [libs/agno/agno/os/public/_policy.py](libs/agno/agno/os/public/_policy.py)
- [libs/agno/tests/unit/os/test_public_mcp_config.py](libs/agno/tests/unit/os/test_public_mcp_config.py)
- [libs/agno_infra/agno/cli/infra_cli.py](libs/agno_infra/agno/cli/infra_cli.py)
- [libs/agno_infra/agno/infra/enums.py](libs/agno_infra/agno/infra/enums.py)
- [libs/agno_infra/agno/infra/operator.py](libs/agno_infra/agno/infra/operator.py)

</details>



This document covers the development setup, testing infrastructure, CI/CD pipelines, code quality tools, AI-assisted development, and infrastructure management for the Agno codebase. As a parent page, it provides a high-level overview of the development and operations lifecycle. For detailed instructions, refer to the respective child pages.

For information about deploying agents using the AgentOS runtime, see [AgentOS Runtime](#7). For infrastructure provisioning using the `agno infra` CLI, see [Infrastructure Management](#9.6).

---

## Development Workflow Overview

The Agno development workflow follows a fork-and-pull-request model with automated quality gates. The pipeline ensures that all contributions meet code quality standards before merging.

Title: Development to Release Pipeline
```mermaid
graph TB
    [Fork]["Fork Repository"]
    [Clone]["Clone Fork Locally"]
    [DevSetup]["Run dev_setup.sh/bat<br/>Creates .venv, installs dependencies"]
    [Feature]["Create Feature Branch"]
    [Code]["Write Code"]
    [Format]["Run format.sh/bat<br/>Ruff formatter"]
    [Validate]["Run validate.sh/bat<br/>Mypy type checker"]
    [Test]["Run pytest suite"]
    [Commit]["Commit Changes"]
    [Push]["Push to Fork"]
    [PR]["Create Pull Request"]
    
    subgraph "Automated PR Checks"
        [PRLint]"pr-lint.yml<br/>Title format validation"
        [CITest]"test.yml<br/>Validation Workflow"
    end
    
    [Review]"Code Review<br/>(via @claude or Maintainers)"
    [Merge]"Merge to main"
    [Release]"GitHub Release"
    
    subgraph "Release Pipeline"
        [BuildAgnoCtl]"Build agnoctl package"
        [BuildAgno]"Build agno package"
        [BuildInfra]"Build agno_infra package"
        [PyPI]"Publish to PyPI"
    end
    
    [Fork] --> [Clone]
    [Clone] --> [DevSetup]
    [DevSetup] --> [Feature]
    [Feature] --> [Code]
    [Code] --> [Format]
    [Format] --> [Validate]
    [Validate] --> [Test]
    [Test] --> [Commit]
    [Commit] --> [Push]
    [Push] --> [PR]
    
    [PR] --> [PRLint]
    [PR] --> [CITest]
    [PRLint] --> [Review]
    [CITest] --> [Review]
    [Review] --> [Merge]
    [Merge] --> [Release]
    
    [Release] --> [BuildAgnoCtl]
    [BuildAgnoCtl] --> [BuildAgno]
    [BuildAgno] --> [BuildInfra]
    [BuildInfra] --> [PyPI]
```

Sources: [CLAUDE.md:182-198](), [.github/workflows/claude.yml:1-12]()

---

## Development Setup

The Agno repository utilizes two distinct virtual environments to separate core framework development from cookbook example execution [CLAUDE.md:40-52](). Package management and virtual environment bootstrapping are handled via `uv`.

For details, see [Development Setup](#9.1).

- **`.venv/`**: Used for development tasks, running `pytest`, formatting, and validation [CLAUDE.md:46-49]().
- **`.venvs/demo/`**: Used for executing cookbook examples with full demo dependencies [CLAUDE.md:47-51]().

Sources: [.gitignore:40-51](), [CLAUDE.md:40-52]()

---

## Testing and CI/CD

Testing spans unit tests, tool integrations, and CI workflows defined in GitHub Actions (`test.yml`, `claude.yml`) [.github/workflows/test.yml:1-23](). Automated tests use pytest splitting across parallel job groups and integrate live service containers like pgvector for database adapter validation [.github/workflows/test.yml:158-187]().

For details, see [Testing and CI/CD](#9.2).

Title: Test Execution and Validation
```mermaid
graph TB
    subgraph "Test Suites"
        [UnitTests]["pytest libs/agno/tests/unit"]
        [ToolTests]["test_firecrawl.py<br/>test_pubmed.py"]
        [RegressionTests]["test_run_regressions.py"]
    end
    
    subgraph "CI Gates"
        [ValidateScript]["./scripts/validate.sh<br/>(Ruff & Mypy)"]
        [FormatScript]["./scripts/format.sh<br/>(Ruff format)"]
    end
    
    [ValidateScript] --> [UnitTests]
    [FormatScript] --> [UnitTests]
    [UnitTests] --> [ToolTests]
    [UnitTests] --> [RegressionTests]
```

Sources: [CLAUDE.md:162-170](), [.github/workflows/test.yml:1-213]()

---

## Code Quality and Validation

Agno enforces strict code quality standards using `Ruff` for formatting and linting, and `Mypy` for static type checking [CLAUDE.md:184-198](). Both validation scripts must pass with zero errors prior to opening pull requests.

For details, see [Code Quality and Validation](#9.3).

Sources: [CLAUDE.md:182-198](), [.github/workflows/test.yml:44-157]()

---

## AI-Assisted Development

AI coding agents are integrated directly into the development workflow via the Claude Code GitHub Action workflow, which responds to `@claude` triggers in issues, pull requests, and code reviews [.github/workflows/claude.yml:1-31](). Guidelines for AI agents are specified in `CLAUDE.md` and `AGENTS.md` [CLAUDE.md:1-15](), [AGENTS.md:1-15]().

For details, see [AI-Assisted Development](#9.4).

Sources: [.github/workflows/claude.yml:1-74](), [CLAUDE.md:1-258](), [AGENTS.md:1-241]()

---

## Contributing Guidelines

Contributing to Agno follows a standardized fork-and-pull-request flow with strict commit message formatting, design doc checks, and an emphasis on creating comprehensive cookbook examples for new features [CLAUDE.md:173-216]().

For details, see [Contributing Guidelines](#9.5).

Sources: [CLAUDE.md:173-216](), [cookbook/README.md:119-121]()

---

## Infrastructure Management

Infrastructure provisioning and management are handled via the `agno-infra` package CLI (`ag infra`), which supports template-based project creation for Docker, AWS, and Railway deployment targets [libs/agno_infra/agno/cli/infra_cli.py:20-32](), [libs/agno_infra/agno/infra/operator.py:20-29]().

For details, see [Infrastructure Management](#9.6).

Title: Infrastructure CLI and Operator Architecture
```mermaid
graph LR
    subgraph "CLI Entrypoint [libs/agno_infra/agno/cli/infra_cli.py]"
        [InfraCLI]["infra_cli Typer App"]
        [UpCmd]["up command"]
        [CreateCmd]["create command"]
    end
    
    subgraph "Operators [libs/agno_infra/agno/infra/operator.py]"
        [InfraOp]["create_infra_from_template"]
        [SetupInfra]["setup_infra_config_from_dir"]
    end
    
    subgraph "Starter Templates [libs/agno_infra/agno/infra/enums.py]"
        [Docker]["agentos_docker"]
        [AWS]["agentos_aws"]
        [Railway]["agentos_railway"]
    end
    
    [InfraCLI] --> [CreateCmd]
    [InfraCLI] --> [UpCmd]
    [CreateCmd] --> [InfraOp]
    [UpCmd] --> [SetupInfra]
    [InfraOp] --> [Docker]
    [InfraOp] --> [AWS]
    [InfraOp] --> [Railway]
```

Sources: [libs/agno_infra/agno/cli/infra_cli.py:20-130](), [libs/agno_infra/agno/infra/operator.py:20-171](), [libs/agno_infra/agno/infra/enums.py:1-7]()

---

