<!-- source: DeepWiki mcp.deepwiki.com · repo fetchai/uAgents · page 7 Development · fetched 2026-10-26 -->

# Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/CODEOWNERS](.github/CODEOWNERS)
- [.github/ISSUE_TEMPLATE/bug-report.yml](.github/ISSUE_TEMPLATE/bug-report.yml)
- [.github/ISSUE_TEMPLATE/feature-request.yml](.github/ISSUE_TEMPLATE/feature-request.yml)
- [.github/pull_request_template.md](.github/pull_request_template.md)
- [.github/workflows/pr-title-linting.yml](.github/workflows/pr-title-linting.yml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [DEVELOPING.md](DEVELOPING.md)
- [LICENSE](LICENSE)
- [README.md](README.md)
- [python/uagents-core/uagents_core/__init__.py](python/uagents-core/uagents_core/__init__.py)

</details>



This document provides comprehensive guidance for developers contributing to the uAgents project. It covers development environment setup, contribution workflows, code quality standards, testing procedures, and release processes.

For detailed guidelines, see the following child pages:
- [Contributing Guide](#7.1) — Detailed instructions on commit conventions, PR requirements, and code standards.
- [Release Process](#7.2) — Documentation of the automated release pipeline and versioning strategy.
- [Deployment](#7.3) — Guides for containerization and cloud deployment.

## Development Environment Setup

Setting up a development environment for uAgents requires Python 3.10-3.13 and [uv](https://docs.astral.sh/uv) for dependency management. The project follows a structured approach with pre-commit hooks for code quality enforcement.

### Environment Configuration

```mermaid
flowchart TD
    Fork["Fork Repository"] --> Clone["Clone Fork"]
    Clone["git clone"] --> SetupUpstream["git remote add upstream"]
    SetupUpstream --> InstallUV["Install uv"]
    InstallUV --> UVSync["uv sync"]
    UVSync --> PreCommit["uv run pre-commit install"]
    PreCommit --> DevReady["Development Ready"]
    
    subgraph "Workspace"
        UVSync --> Venv["python/.venv"]
    end
```

The development setup process is centered in the `python` directory. Running `uv sync` prepares the virtual environment, and `pre-commit install` ensures that linting and formatting are checked during `git commit`.

**Sources:** [DEVELOPING.md:13-35](), [DEVELOPING.md:39-40]()

### Code Quality Standards

The project enforces strict code quality standards using [Ruff](https://github.com/astral-sh/ruff) for linting and formatting.

```mermaid
flowchart LR
    Developer["Developer"] --> CodeChanges["Make Code Changes"]
    CodeChanges --> ManualCheck["uv run ruff check --fix"]
    ManualCheck --> ManualFormat["uv run ruff format"]
    ManualFormat --> CommitStage["git commit"]
    CommitStage --> PreCommitHook["Pre-commit Hooks"]
    PreCommitHook --> CIChecks["CI Quality Checks"]
```

Consistency is maintained through automated formatting. Developers are encouraged to add `ruff` to their IDE to speed up development.

**Sources:** [DEVELOPING.md:41-49](), [CONTRIBUTING.md:126]()

## Testing Infrastructure

The project uses `pytest` for unit and integration testing. All new features and bug fixes must include tests to ensure correctness and prevent regressions.

### Test Execution Workflow

```mermaid
flowchart TD
    LocalDev["Local Development"] --> RunTests["uv run pytest"]
    RunTests --> TestResults["Test Results"]
    TestResults --> PassLocal["Tests Pass Locally"]
    
    PRCreate["Create PR"] --> CITrigger["CI Tests Triggered"]
    CITrigger --> CITests["ci-tests.yml"]
    CITests --> Success["PR Ready for Review"]
    
    PassLocal --> PRCreate
```

Testing is a prerequisite for any PR submission. Local execution via `uv run pytest` saves CI hours and ensures only clean code is committed.

**Sources:** [DEVELOPING.md:52-56](), [CONTRIBUTING.md:129-133]()

## Contribution Workflow

The contribution process follows GitHub Flow. Major features require an initial proposal issue, while small features and bug fixes can be submitted directly as Pull Requests.

### PR Submission Process

```mermaid
flowchart TD
    IssueCheck["Search Issue Tracker"] --> CreateIssue["Create Issue (Bug/Feature)"]
    CreateIssue --> ForkRepo["Fork & Create Branch"]
    ForkRepo --> MakeChanges["Implement Changes"]
    MakeChanges --> AddTests["Add Tests & Docs"]
    AddTests --> CommitChanges["Commit (Conventional Commits)"]
    CommitChanges --> CreatePR["Create PR against fetchai:main"]
    CreatePR --> PRReview["Code Owner Review"]
    PRReview --> SquashMerge["Squash and Merge"]
```

The project uses `Conventional Commits` to determine versioning and generate release notes. PR titles are automatically linted to ensure they follow types like `feat`, `fix`, `docs`, etc.

**Sources:** [CONTRIBUTING.md:60-95](), [.github/workflows/pr-title-linting.yml:19-29](), [.github/pull_request_template.md:1-30]()

## Release and Deployment

The release process is automated via GitHub Actions and the `do_release.py` script. It supports multiple packages within the monorepo: `uagents`, `uagents-core`, and `uagents-ai-engine`.

### Release Automation

```mermaid
flowchart TD
    subgraph "Trigger"
        Merge["Merge Release PR to main"]
    end
    
    subgraph "Action: release.yml"
        Check["Check Version vs Tags"]
        Build["poetry build"]
        Publish["Upload to PyPI"]
        Tag["Create & Push Git Tag"]
        GHRelease["Create GitHub Release"]
    end
    
    Merge --> Check
    Check --> Build --> Publish --> Tag --> GHRelease
```

For deployment, uAgents can be containerized using Docker or deployed at scale using Kubernetes. Reference implementations like `hello-agent` provide templates for these configurations.

For details, see [Release Process](#7.2) and [Deployment](#7.3).

**Sources:** [README.md:104-106](), [CONTRIBUTING.md:135](), [.github/CODEOWNERS:1-3]()

---

