<!-- source: DeepWiki mcp.deepwiki.com · repo yusufkaraaslan/Skill_Seekers · page 15 Testing & Quality Assurance · fetched 2026-10-26 -->

# Testing & Quality Assurance

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/FUNDING.yml](.github/FUNDING.yml)
- [.github/workflows/tests.yml](.github/workflows/tests.yml)
- [docs/FAQ.md](docs/FAQ.md)
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- [docs/features/HOW_TO_GUIDES.md](docs/features/HOW_TO_GUIDES.md)
- [src/skill_seekers/cli/arguments/enhance.py](src/skill_seekers/cli/arguments/enhance.py)
- [src/skill_seekers/cli/config_manager.py](src/skill_seekers/cli/config_manager.py)
- [src/skill_seekers/cli/execution_context.py](src/skill_seekers/cli/execution_context.py)
- [tests/conftest.py](tests/conftest.py)
- [tests/test_execution_context.py](tests/test_execution_context.py)
- [tests/test_mcp_fastmcp.py](tests/test_mcp_fastmcp.py)
- [tests/test_mcp_fetch_retry.py](tests/test_mcp_fetch_retry.py)

</details>



This page provides a high-level overview of the test suite, code quality enforcement, static analysis tools, and CI/CD pipelines in `skill-seekers`. 

This is a PARENT page. For detailed breakdowns of test files, fixtures, and functional coverage, see [Test Suite Organization](#15.1). For local execution instructions and coverage commands, see [Running Tests Locally](#15.2). For complete GitHub Actions definitions, see [CI/CD Workflows](#15.3).

---

## CI/CD Pipeline Overview

Automated testing and quality gates are orchestrated via GitHub Actions workflows defined in `.github/workflows/` [.github/workflows/tests.yml:1-10](). The primary continuous integration pipeline executes linting, parallel fast unit tests, serial integration tests, and specialized MCP server tests [/.github/workflows/tests.yml:9-160]().

### CI Job Structure

```mermaid
flowchart TD
    trigger[""Push/PR to main or development""]
    trigger --> lint[""lint job\n(Ruff & Mypy)""]
    trigger --> test_fast[""test-fast\n(Parallel Pytest)""]
    
    test_fast --> test_serial[""test-serial\n(Integration/E2E)""]
    test_fast --> test_mcp[""test-mcp\n(MCP Server Tests)""]
    
    lint --> complete[""tests-complete\n(Status Check Gate)""]
    test_serial --> complete
    test_mcp --> complete

    subgraph "Linting Phase"
    lint --> ruff_check[""ruff check src/ tests/""]
    lint --> ruff_format[""ruff format --check""]
    lint --> mypy[""mypy src/skill_seekers""]
    end

    subgraph "Testing Phase"
    test_fast --> xdist[""pytest -n auto\n(Unit Tests)""]
    test_serial --> e2e[""pytest -m integration\n(Slow/Network)""]
    test_mcp --> mcp_spec[""pytest -m mcp_only\n(FastMCP)""]
    xdist --> codecov[""Upload to Codecov""]
    end
```

Sources: [.github/workflows/tests.yml:9-156]()

For details on workflow triggers, matrix configurations, and deployment actions, see [CI/CD Workflows](#15.3).

---

## Test Suite Organization

The test suite is located in the `tests/` directory and covers all core modules, adaptors, CLI commands, and MCP tools. 

- **Test Fixtures**: Isolated environment fixtures, configuration isolation (`_isolate_user_config`), context resets (`_reset_execution_context`), and subprocess agent mocking (`_reject_unmocked_agent_processes`) are established in `tests/conftest.py` [tests/conftest.py:34-147]().
- **FastMCP Testing**: The FastMCP server implementation is thoroughly tested via `tests/test_mcp_fastmcp.py` [tests/test_mcp_fastmcp.py:1-170](), ensuring all registered tools conform to specs.
- **Resilience Testing**: Network retry logic and exponential backoff behavior are validated in `tests/test_mcp_fetch_retry.py` [tests/test_mcp_fetch_retry.py:1-79]().

For a complete architectural mapping of the `tests/` directory, naming conventions, and golden fixtures, see [Test Suite Organization](#15.1).

Sources: [tests/conftest.py:1-147](), [tests/test_mcp_fastmcp.py:1-170](), [tests/test_mcp_fetch_retry.py:1-79]()

---

## Static Analysis & Code Quality Enforcement

Code quality, formatting, and type safety are strictly enforced via Ruff and Mypy during both local development and CI execution [.github/workflows/tests.yml:35-59]().

| Tool | Command | Purpose | Fail CI? |
|------|---------|-------|----------|
| `ruff check` | `ruff check src/ tests/` | Linting & Logic errors | Yes [.github/workflows/tests.yml:50-50]() |
| `ruff format` | `ruff format --check` | Code style consistency | Yes [.github/workflows/tests.yml:52-52]() |
| `mypy` | `mypy src/skill_seekers` | Type safety checks | No (Warning only) [.github/workflows/tests.yml:53-55]() |

Sources: [.github/workflows/tests.yml:35-59]()

---

## Package Integrity & Structure

The repository maintains strict alignment between its physical filesystem structure and its installable Python package modules.

### Package Structure Mapping

```mermaid
graph художник
    subgraph "Filesystem Space"
    F1[""src/skill_seekers/__init__.py""]
    F2[""src/skill_seekers/mcp/server_fastmcp.py""]
    F3[""src/skill_seekers/_version.py""]
    F4[""pyproject.toml""]
    end

    subgraph "Code Entity Space"
    C1[""skill_seekers""]
    C2[""skill_seekers.mcp.server_fastmcp""]
    C3[""skill_seekers.__version__""]
    C4[""uv build""]
    end

    F1 -- "defines" --> C1
    F2 -- "implements" --> C2
    F3 -- "provides" --> C3
    F4 -- "metadata for" --> C4
```

Sources: [.github/workflows/tests.yml:1-156](), [src/skill_seekers/mcp/server_fastmcp.py:1-50]()

---

## Running Tests Locally & Coverage

Developers can run subsets of the test suite locally using `pytest` combined with custom safe execution runners or pytest markers [tests/conftest.py:1-147](). 

- **Fast Unit Tests**: Executed via parallel runners omitting slow network or integration tags.
- **Coverage Reports**: XML and terminal coverage are generated using `pytest-cov` and integrated with Codecov [.github/workflows/tests.yml:96-104]().

For detailed instructions on running specific test files, handling Docker integration suites, and managing test environments, see [Running Tests Locally](#15.2).

Sources: [.github/workflows/tests.yml:60-105](), [tests/conftest.py:1-147]()

---

