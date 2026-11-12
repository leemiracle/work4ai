<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/physicsnemo · page 10 Development Guide · fetched 2026-10-21 -->

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/ISSUE_TEMPLATE/bug_report.yml](.github/ISSUE_TEMPLATE/bug_report.yml)
- [.github/ISSUE_TEMPLATE/config.yml](.github/ISSUE_TEMPLATE/config.yml)
- [.github/ISSUE_TEMPLATE/documentation_request.yml](.github/ISSUE_TEMPLATE/documentation_request.yml)
- [.github/ISSUE_TEMPLATE/feature_request.yml](.github/ISSUE_TEMPLATE/feature_request.yml)
- [.github/ISSUE_TEMPLATE/research_paper.yml](.github/ISSUE_TEMPLATE/research_paper.yml)
- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [.github/actions/replace-cache/action.yml](.github/actions/replace-cache/action.yml)
- [.github/workflows/blossom-ci.yml](.github/workflows/blossom-ci.yml)
- [.github/workflows/codeowners-info.yml](.github/workflows/codeowners-info.yml)
- [.gitlab/issue_templates/bug.md](.gitlab/issue_templates/bug.md)
- [.gitlab/issue_templates/documentation.md](.gitlab/issue_templates/documentation.md)
- [.gitlab/issue_templates/feature_request.md](.gitlab/issue_templates/feature_request.md)
- [.gitlab/issue_templates/security.md](.gitlab/issue_templates/security.md)
- [.gitlab/merge_request_templates/Default.md](.gitlab/merge_request_templates/Default.md)
- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [codecov.yml](codecov.yml)
- [docs/conf.py](docs/conf.py)
- [docs/img/Modulus-850x720.svg](docs/img/Modulus-850x720.svg)
- [docs/research.md](docs/research.md)
- [greptile.json](greptile.json)

</details>



This page provides a high-level overview of the development workflow, testing infrastructure, CI/CD pipelines, and code quality standards for the PhysicsNeMo codebase. It serves as a central hub for contributors to understand how to move from a local feature branch to a merged Pull Request.

As a parent page, this guide introduces key sub-topics and links to detailed child pages:
- **[Contributing Guidelines](#10.1)** — Document PR workflow, DCO sign-off, CHANGELOG updates, CODEOWNERS review map, GitHub/GitLab issue templates, release process, and greptile.json.
- **[Testing Framework](#10.2)** — Document pytest usage, test organization, golden-file testing, multi-GPU setup, coverage/codecov components, and numerical checks.
- **[CI/CD Pipeline](#10.3)** — Document Blossom-CI workflows, GitHub Actions, caching contracts, and container builds.
- **[Code Quality Standards](#10.4)** — Document pre-commit hooks, ruff, interrogate docstring coverage with baseline, license headers, import-linter contracts, and coding standards.
- **[AI Agent Skills and Editor Rules](#10.5)** — Document AI assistant skill cards and editor rules used to guide development.

---

## Contributing Workflow

PhysicsNeMo follows a standard GitHub fork-and-pull model [CONTRIBUTING.md:98-118](). Developers are required to fork the upstream repository and submit Pull Requests (PRs) from their feature branches. Every PR must correspond to an open issue and include updates to `CHANGELOG.md` [CONTRIBUTING.md:112-118]().

### PR Lifecycle and Automation
The review process is augmented by both human maintainers and automated AI/CI tools:
* **Authorization**: CI jobs on hybrid infrastructure (`Blossom-CI`) require authorization from specific project maintainers [.github/workflows/blossom-ci.yml:41-69]().
* **CODEOWNERS Mapping**: Automated workflows like `codeowners-info.yml` parse `.github/CODEOWNERS` to track file-level review coverage and team sign-offs [.github/workflows/codeowners-info.yml:43-121]().
* **AI Assistance**: PR templates guide contributors through checklists and prompt interaction with code review assistants [.github/PULL_REQUEST_TEMPLATE.md:9-17]().

For detailed procedures, see **[Contributing Guidelines](#10.1)**.

Sources: [CONTRIBUTING.md:98-131](), [.github/workflows/blossom-ci.yml:18-124](), [.github/workflows/codeowners-info.yml:1-121](), [.github/PULL_REQUEST_TEMPLATE.md:1-34]()

---

## Testing Framework

The testing suite relies on `pytest` and handles both standalone unit tests and multi-GPU distributed environments.

### Test Organization and Execution
Tests are organized under the `test/` directory [CONTRIBUTING.md:77-79](). Test coverage and validation components interact closely with Codecov configuration (`codecov.yml`) to track core components (models, distributed, datapipes, mesh, nn, diffusion) [codecov.yml:41-77]().

For details on writing and running tests, see **[Testing Framework](#10.2)**.

Sources: [CONTRIBUTING.md:77-79](), [codecov.yml:1-80]()

---

## CI/CD Pipeline

PhysicsNeMo employs a robust CI/CD pipeline spanning GitHub Actions and NVIDIA's internal infrastructure [.github/workflows/blossom-ci.yml:17-32]().

### Pipeline Stages
1. **Vulnerability Scanning**: Automatically checks codebases and dependencies [.github/workflows/blossom-ci.yml:78-112]().
2. **Pre-commit Hooks**: Enforces code style, licensing, and documentation standards [.pre-commit-config.yaml:17-65]().
3. **Code Quality Gates**: Integrates linting, import linting, and docstring coverage checks [.pre-commit-config.yaml:26-65]().

For details on the pipeline architecture, see **[CI/CD Pipeline](#10.3)**.

Sources: [.github/workflows/blossom-ci.yml:17-135](), [.pre-commit-config.yaml:1-65]()

---

## Code Quality Standards

Code quality is strictly enforced through `pre-commit` configurations and linting tools.

### Quality Enforcement Tools
| Tool | Purpose | Source File |
| :--- | :--- | :--- |
| **Ruff** | Unified linting and formatting (`ruff-check`, `ruff-format`) | [.pre-commit-config.yaml:18-25]() |
| **Interrogate** | Enforces docstring coverage against baseline | [.pre-commit-config.yaml:26-35]() |
| **License Header Checker** | Ensures Apache 2.0 copyright headers on source files | [.pre-commit-config.yaml:42-51]() |
| **Import Linter** | Prevents architectural violations and circular imports | [.pre-commit-config.yaml:58-65]() |

For the full list of standards, see **[Code Quality Standards](#10.4)**.

Sources: [.pre-commit-config.yaml:17-65]()

---

## AI Agent Skills and Editor Rules

PhysicsNeMo incorporates structured guidelines and skill definitions to assist AI-driven development.

### Development Assistance Infrastructure
* **Editor Rules**: `.cursor/rules` files and editor configurations direct AI behavior regarding code style, typing, and architecture.
* **Skill Cards**: The `skills/` directory contains specialized task definitions (such as `physicsnemo-discover` and tensor sharding tools) referenced by AI agents.

For details, see **[AI Agent Skills and Editor Rules](#10.5)**.

Sources: [CONTRIBUTING.md:1-131](), [.github/PULL_REQUEST_TEMPLATE.md:1-34]()

---

## System Maps

### Workflow to Code Entity Mapping
This diagram maps natural language contribution stages to the specific code entities and configuration files that implement them.

```mermaid
graph TD
    subgraph "Contribution Lifecycle"
        "ForkAndPR"["Pull Request & Issue Templates"]
        "LocalCommit"["DCO Sign-off & CHANGELOG"]
    end

    subgraph "Validation Configs"
        "PreCommit"[".pre-commit-config.yaml"]
        "CodeCov"["codecov.yml"]
        "CodeOwners"["CODEOWNERS info Workflow"]
    end

    subgraph "CI Automation"
        "BlossomCI"[".github/workflows/blossom-ci.yml"]
        "PRTemplate"[".github/PULL_REQUEST_TEMPLATE.md"]
    end

    "ForkAndPR" --> "PRTemplate"
    "LocalCommit" --> "PreCommit"
    "PreCommit" --> "BlossomCI"
    "CodeOwners" --> "BlossomCI"
    "CodeCov" --> "BlossomCI"
```
Sources: [CONTRIBUTING.md:98-131](), [.github/workflows/blossom-ci.yml:17-135](), [.pre-commit-config.yaml:1-65](), [codecov.yml:1-80]()

### CI/CD Stage Mapping
This diagram bridges the conceptual CI/CD stages to the underlying GitHub Actions and local validation scripts.

```mermaid
graph LR
    subgraph "Trigger Layer"
        "IssueComment"["issue_comment / workflow_dispatch"]
    end

    subgraph "GitHub Actions"
        "BlossomWorkflow"["Blossom-CI Job"]
        "CodeownersWorkflow"["codeowners-info.yml"]
    end

    subgraph "Verification Scripts"
        "HeaderCheck"["test/ci_tests/header_check.py"]
        "DocstringCheck"["test/ci_tests/check_docstring_coverage.py"]
    end

    "IssueComment" --> "BlossomWorkflow"
    "BlossomWorkflow" --> "HeaderCheck"
    "BlossomWorkflow" --> "DocstringCheck"
    "CodeownersWorkflow" --> "BlossomWorkflow"
```
Sources: [.github/workflows/blossom-ci.yml:17-135](), [.github/workflows/codeowners-info.yml:1-50](), [.pre-commit-config.yaml:26-51]()

---

