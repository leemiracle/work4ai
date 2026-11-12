<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/open-swe · page 12 Development · fetched 2026-10-26 -->

# Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.github/workflows/pr_lint.yml](.github/workflows/pr_lint.yml)
- [AGENTS.md](AGENTS.md)
- [CLAUDE.md](CLAUDE.md)
- [LICENSE](LICENSE)

</details>



This guide covers the development workflow for contributors and developers working on the Open SWE codebase. It includes local environment setup, testing procedures, CI/CD pipeline configuration, and monorepo structure. For deployment of Open SWE in production environments, see [Deployment](#11). For customization and extension of Open SWE components, see [Customization Guide](#9).

---

## Overview

Open SWE uses a modern development stack with separate toolchains for Python backend code and JavaScript frontend code. The Python components use `uv` for fast, reliable dependency management, while the JavaScript/TypeScript components are organized within a monorepo structure. A `Makefile` provides a unified interface for common development tasks like linting, formatting, and testing.

**Development Workflow:**

```mermaid
graph LR
    "Clone"["Clone repository"]
    "Setup"["Install dependencies<br/>(uv sync)"]
    "Code"["Write code"]
    "Lint"["Run linters<br/>(make lint)"]
    "Format"["Apply formatting<br/>(make format)"]
    "Test"["Run tests<br/>(make test)"]
    "Commit"["Commit changes"]
    "Push"["Push to GitHub"]
    "CI"["CI/CD pipeline<br/>(GitHub Actions)"]
    
    "Clone" --> "Setup"
    "Setup" --> "Code"
    "Code" --> "Lint"
    "Lint" --> "Format"
    "Format" --> "Test"
    "Test" --> "Commit"
    "Commit" --> "Push"
    "Push" --> "CI"
    "CI" --> "Code"
```

**Sources:** [AGENTS.md:15-24](), [.github/workflows/ci.yml:1-49]()

---

## 12.1. Local Development Setup

Setting up a local environment requires configuring the Python backend. The project relies on `uv` for Python dependency management. For details, see [Local Development Setup](#12.1).

### Prerequisites

| Tool | Purpose | Reference |
|------|---------|-----------|
| **UV** | Python package manager | [.github/workflows/ci.yml:22-22]() |
| **Make** | Task runner for dev commands | [AGENTS.md:15-24]() |
| **Ruff** | Linting and formatting | [AGENTS.md:13-13]() |

### Local Execution Modes
Developers can run the full LangGraph stack or just the FastAPI webapp.
- `make dev`: Runs `uv run langgraph dev`, serving all three graphs (`agent`, `reviewer`, `review_style_analyzer`) and the FastAPI app [AGENTS.md:17-17]().
- `make run`: Runs `uvicorn agent.webapp:app`, serving only the FastAPI webhooks and dashboard API [AGENTS.md:18-18]().

**Sources:** [AGENTS.md:1-44](), [.github/workflows/ci.yml:22-26]()

---

## 12.2. Testing

Open SWE includes a test suite that validates agent behavior, tool functionality, and middleware logic. The testing infrastructure is driven by `pytest` with `asyncio` support. For details, see [Testing](#12.2).

### Test Commands

| Command | Action |
|---------|--------|
| `make test` | Runs the full suite via `uv run pytest -vvv tests/` [AGENTS.md:19-19]() |
| `make test TEST_FILE=path/to/test.py` | Runs a specific test file [AGENTS.md:20-20]() |

The CI pipeline automatically runs `make test` on every pull request to ensure no regressions [.github/workflows/ci.yml:48-48]().

**Sources:** [AGENTS.md:13-21](), [.github/workflows/ci.yml:39-49]()

---

## 12.3. CI/CD Pipeline

The CI/CD pipeline is implemented using GitHub Actions. It enforces code quality through automated linting, semantic PR titles, and unit testing. For details, see [CI/CD Pipeline](#12.3).

### Workflow Jobs

```mermaid
graph TB
    subgraph "Agent CI [.github/workflows/ci.yml]"
        "Lint"["Agent lint"]
        "Format"["Agent format check"]
        "Tests"["Agent unit tests"]
    end

    subgraph "PR Quality [.github/workflows/pr_lint.yml]"
        "PRTitle"["Validate PR Title"]
    end
    
    "Lint" --> "L_Cmd"["make lint"]
    "Format" --> "F_Cmd"["make format-check"]
    "Tests" --> "T_Cmd"["make test"]
    "PRTitle" --> "S_Cmd"["Semantic PR Check"]
```

The pipeline uses `astral-sh/setup-uv` to manage the Python environment and `uv sync --locked --extra dev` to ensure a consistent environment across runs [.github/workflows/ci.yml:22-24]().

**Sources:** [.github/workflows/ci.yml:1-49](), [.github/workflows/pr_lint.yml:1-42]()

---

## 12.4. Monorepo Structure

Open SWE is organized as a monorepo containing the core agent logic, a dashboard frontend, and various integration packages. For details, see [Monorepo Structure](#12.4).

### Code Entity Space Mapping

```mermaid
graph TD
    "Root"["/"]
    
    subgraph "Core Agent Logic"
        "AgentDir"["agent/"]
        "Server"["agent/server.py"]
        "Reviewer"["agent/reviewer.py"]
        "Webapp"["agent/webapp.py"]
    end
    
    subgraph "Frontend & UI"
        "UIDir"["ui/"]
        "Dashboard"["agent/dashboard/"]
    end
    
    subgraph "Configuration"
        "LGJson"["langgraph.json"]
        "PyProject"["pyproject.toml"]
        "AgentsMD"["AGENTS.md"]
    end
    
    "Root" --> "AgentDir"
    "Root" --> "UIDir"
    "Root" --> "LGJson"
    "AgentDir" --> "Server"
    "AgentDir" --> "Reviewer"
    "AgentDir" --> "Webapp"
    "AgentDir" --> "Dashboard"
```

**Sources:** [AGENTS.md:26-44](), [.dockerignore:1-15]()

---

## 12.5. Operational Scripts

The codebase includes utility scripts in the `scripts/` directory for PR analytics and snapshot management. For details, see [Operational Scripts](#12.5).

### PR Analytics Utilities
- **`export_pr_urls.py`**: Extracts PR URLs from LangGraph threads for performance tracking.
- **`check_pr_merge_status.py`**: Performs bulk status checks via the GitHub API to verify if agent-produced PRs were successful.

These utilities are essential for evaluating the agent's real-world impact and identifying failure patterns in production.

---

## Development Best Practices

### Code Quality Checklist

Before committing changes, run the following checks locally:

```bash
# 1. Apply formatting and fix lint errors
make format

# 2. Verify linting (run by CI)
make lint

# 3. Run unit tests
make test
```

### Dependency Management

**Python:** Always use `uv sync --locked` to ensure your local environment matches the `uv.lock` file [.github/workflows/ci.yml:24-24]().

**Commits:** Follow semantic commit conventions (e.g., `feat:`, `fix:`, `docs:`) as enforced by the PR Title Lint workflow [.github/workflows/pr_lint.yml:19-31]().

**Sources:** [AGENTS.md:13-24](), [.github/workflows/ci.yml:1-49](), [.github/workflows/pr_lint.yml:1-42]()

---

