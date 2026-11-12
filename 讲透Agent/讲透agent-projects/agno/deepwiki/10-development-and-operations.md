<!-- source: DeepWiki mcp.deepwiki.com · repo agno-agi/agno · page 10 Development and Operations · fetched 2026-11-09 -->

# Development and Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.cursorrules](.cursorrules)
- [.github/pull_request_template.md](.github/pull_request_template.md)
- [.github/workflows/claude.yml](.github/workflows/claude.yml)
- [.github/workflows/pr-triage.yml](.github/workflows/pr-triage.yml)
- [.gitignore](.gitignore)
- [AGENTS.md](AGENTS.md)
- [CLAUDE.md](CLAUDE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [cookbook/07_knowledge/02_building_blocks/README.md](cookbook/07_knowledge/02_building_blocks/README.md)
- [cookbook/07_knowledge/05_integrations/README.md](cookbook/07_knowledge/05_integrations/README.md)
- [cookbook/07_knowledge/05_integrations/vector_dbs/05_scylladb.py](cookbook/07_knowledge/05_integrations/vector_dbs/05_scylladb.py)
- [cookbook/README.md](cookbook/README.md)
- [libs/agno/agno/tools/reasoning.py](libs/agno/agno/tools/reasoning.py)
- [libs/agno_infra/agno/cli/infra_cli.py](libs/agno_infra/agno/cli/infra_cli.py)
- [libs/agno_infra/agno/infra/enums.py](libs/agno_infra/agno/infra/enums.py)
- [libs/agno_infra/agno/infra/operator.py](libs/agno_infra/agno/infra/operator.py)
- [scripts/demo_setup.sh](scripts/demo_setup.sh)
- [scripts/dev_setup.sh](scripts/dev_setup.sh)

</details>



This document covers the development setup, testing infrastructure, CI/CD pipelines, code quality tools, AI-assisted development, and infrastructure management for the Agno codebase. As a parent page, it provides a high-level overview of the development and operations lifecycle. For detailed instructions, refer to the respective child pages.

For information about deploying agents using the AgentOS runtime, see [AgentOS Runtime](#7). For infrastructure provisioning using the `agno infra` CLI, see [Infrastructure Management](#10.6).

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
        [PRLint]["pr-lint.yml<br/>Title format validation"]
        [CITest]["test.yml<br/>Validation Workflow"]
    end
    
    [Review]["Code Review<br/>(via @claude or Maintainers)"]
    [Merge]["Merge to main"]
    [Release]["GitHub Release"]
    
    subgraph "Release Pipeline"
        [BuildAgnoCtl]["Build agnoctl package"]
        [BuildAgno]["Build agno package"]
        [BuildInfra]["Build agno_infra package"]
        [PyPI]["Publish to PyPI"]
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

The Agno repository utilizes two distinct virtual environments to separate core framework development from cookbook example execution [CLAUDE.md:40-52](). Package management and virtual environment bootstrapping are handled via `uv` [scripts/dev_setup.sh:50-53]().

For details, see [Development Setup](#10.1).

- **`.venv/`**: Used for development tasks, running `pytest`, formatting, and validation [CLAUDE.md:46-49]().
- **`.venvs/demo/`**: Used for executing cookbook examples with full demo dependencies [CLAUDE.md:47-51]().

Sources: [.gitignore:40-51](), [CLAUDE.md:40-52](), [scripts/dev_setup.sh:50-53]()

---

## Testing and CI/CD

Testing spans unit tests, tool integrations, and CI workflows defined in GitHub Actions (`test.yml`, `claude.yml`) [.github/workflows/claude.yml:1-31](). Automated tests use pytest splitting across parallel job groups and integrate live service containers for database adapter validation [CONTRIBUTING.md:74-84]().

For details, see [Testing and CI/CD](#10.2).

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

Sources: [CLAUDE.md:162-170](), [CONTRIBUTING.md:74-84]()

---

## Code Quality and Validation

Agno enforces strict code quality standards using `Ruff` for formatting and linting, and `Mypy` for static type checking [CONTRIBUTING.md:61-73](). Both validation scripts must pass with zero errors prior to opening pull requests.

For details, see [Code Quality and Validation](#10.3).

Sources: [CLAUDE.md:182-198](), [CONTRIBUTING.md:61-73]()

---

## AI-Assisted Development

AI coding agents are integrated directly into the development workflow via the Claude Code GitHub Action workflow, which responds to `@claude` triggers in issues, pull requests, and code reviews [.github/workflows/claude.yml:1-31](). Guidelines for AI agents are specified in `CLAUDE.md` and `AGENTS.md` [CLAUDE.md:1-15](), [AGENTS.md:1-15]().

For details, see [AI-Assisted Development](#10.4).

Sources: [.github/workflows/claude.yml:1-74](), [CLAUDE.md:1-258](), [AGENTS.md:1-241]()

---

## Contributing Guidelines

Contributing to Agno follows a standardized fork-and-pull-request flow with strict commit message formatting, design doc checks, and an emphasis on creating comprehensive cookbook examples for new features [CONTRIBUTING.md:5-32]().

For details, see [Contributing Guidelines](#10.5).

Sources: [CONTRIBUTING.md:5-32](), [cookbook/README.md:119-121]()

---

## Infrastructure Management

Infrastructure provisioning and management are handled via the `agno-infra` package CLI (`ag infra`), which supports template-based project creation for Docker, AWS, and Railway deployment targets [libs/agno_infra/agno/cli/infra_cli.py:20-32](), [libs/agno_infra/agno/infra/operator.py:20-29]().

For details, see [Infrastructure Management](#10.6).

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

