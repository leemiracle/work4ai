<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/gym-hil · page 8 Development · fetched 2026-10-26 -->

# Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/quality.yml](.github/workflows/quality.yml)
- [.github/workflows/testing.yml](.github/workflows/testing.yml)
- [.gitignore](.gitignore)
- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [tests/test_env.py](tests/test_env.py)

</details>



This page covers the development setup, testing procedures, and contribution guidelines for developers working on gym-hil. It provides information about the tools, workflows, and standards used to maintain code quality and ensure reliable functionality.

For detailed information about the test suite and environment validation, see [Testing](#8.1). For documentation of the automated CI/CD pipeline and GitHub Actions workflows, see [CI/CD Pipeline](#8.2).

## Development Environment Setup

The gym-hil project uses Poetry for dependency management and virtual environment creation. The development setup includes code quality tools, testing frameworks, and pre-commit hooks to ensure consistent code standards.

### Development Tools and Dependencies

The project relies on several key development tools configured through Poetry and pre-commit hooks:

```mermaid
graph TB
    subgraph "Development Tools"
        POETRY["poetry<br/>Dependency Management"]
        RUFF["ruff<br/>Linting & Formatting"]
        PYTEST["pytest<br/>Testing Framework"]
        PRECOMMIT["pre-commit<br/>Git Hooks"]
    end
    
    subgraph "Code Quality Checks"
        RUFF_CHECK["ruff check<br/>Linting"]
        RUFF_FORMAT["ruff format<br/>Code Formatting"]
        PYUPGRADE["pyupgrade<br/>Python Syntax Updates"]
        BUILTIN_HOOKS["Built-in Hooks<br/>Basic Validation"]
    end
    
    subgraph "Testing Components"
        PYTEST_RUNNER["pytest Runner"]
        COVERAGE["Coverage Analysis"]
        ENV_CHECKER["gymnasium.utils.env_checker"]
    end
    
    POETRY --> RUFF
    POETRY --> PYTEST
    POETRY --> PRECOMMIT
    
    PRECOMMIT --> RUFF_CHECK
    PRECOMMIT --> RUFF_FORMAT
    PRECOMMIT --> PYUPGRADE
    PRECOMMIT --> BUILTIN_HOOKS
    
    PYTEST --> PYTEST_RUNNER
    PYTEST --> COVERAGE
    PYTEST --> ENV_CHECKER
```

**Development Tools Configuration**
- **Poetry**: Manages dependencies and virtual environments with `pyproject.toml` configuration
- **Ruff**: Provides fast linting and code formatting with version specified in `.pre-commit-config.yaml`
- **pytest**: Testing framework with coverage analysis support
- **Pre-commit**: Enforces code quality standards before commits

Sources: [.pre-commit-config.yaml:1-25](), [.github/workflows/quality.yml:1-56](), [.github/workflows/testing.yml:1-54]()

## Code Quality and Standards

The project enforces code quality through automated tools and pre-commit hooks. All code must pass linting, formatting, and basic validation checks before being committed.

### Pre-commit Hook Configuration

```mermaid
graph LR
    subgraph "Pre-commit Hooks Pipeline"
        COMMIT["Git Commit"]
        PRECOMMIT_HOOKS["Pre-commit Hooks"]
        
        subgraph "Validation Hooks"
            DEBUG_STMT["debug-statements"]
            MERGE_CONFLICT["check-merge-conflict"]
            CASE_CONFLICT["check-case-conflict"]
            YAML_CHECK["check-yaml"]
            TOML_CHECK["check-toml"]
            EOF_FIXER["end-of-file-fixer"]
            TRAILING_WS["trailing-whitespace"]
        end
        
        subgraph "Code Quality Hooks"
            PYUPGRADE_HOOK["pyupgrade"]
            RUFF_HOOK["ruff --fix"]
            RUFF_FORMAT_HOOK["ruff-format"]
        end
    end
    
    COMMIT --> PRECOMMIT_HOOKS
    PRECOMMIT_HOOKS --> DEBUG_STMT
    PRECOMMIT_HOOKS --> MERGE_CONFLICT
    PRECOMMIT_HOOKS --> CASE_CONFLICT
    PRECOMMIT_HOOKS --> YAML_CHECK
    PRECOMMIT_HOOKS --> TOML_CHECK
    PRECOMMIT_HOOKS --> EOF_FIXER
    PRECOMMIT_HOOKS --> TRAILING_WS
    PRECOMMIT_HOOKS --> PYUPGRADE_HOOK
    PRECOMMIT_HOOKS --> RUFF_HOOK
    PRECOMMIT_HOOKS --> RUFF_FORMAT_HOOK
```

**Code Quality Standards**
- **Python Version**: Requires Python 3.10 as specified in `default_language_version`
- **Linting**: Uses Ruff with automatic fixes enabled via `--fix` argument
- **Formatting**: Enforces consistent code formatting with `ruff-format`
- **Syntax Updates**: Automatically updates Python syntax using `pyupgrade`
- **Basic Validation**: Checks for debug statements, merge conflicts, and file format issues

Sources: [.pre-commit-config.yaml:1-25](), [.github/workflows/quality.yml:28-41]()

## Testing Overview

The project uses pytest for testing with Gymnasium's environment validation framework. Tests focus on verifying environment compliance and proper HIL functionality.

### Test Structure and Environment Validation

```mermaid
graph TB
    subgraph "Testing Framework"
        PYTEST_MAIN["pytest"]
        TEST_ENV["test_env.py"]
        PARAMETRIZE["@pytest.mark.parametrize"]
        
        subgraph "Test Functions"
            TEST_HIL["test_hil()"]
            GYM_MAKE["gym.make()"]
            CHECK_ENV["check_env()"]
        end
        
        subgraph "Environment Validation"
            ENV_CHECKER["gymnasium.utils.env_checker"]
            UNWRAPPED["env.unwrapped"]
            VALIDATION["Environment Compliance"]
        end
    end
    
    subgraph "Test Parameters"
        ENV_TASK["env_task"]
        IMAGE_OBS["image_obs"]
        PANDA_PICK["PandaPickCubeBase-v0"]
        BOOL_FLAGS["True/False"]
    end
    
    PYTEST_MAIN --> TEST_ENV
    TEST_ENV --> PARAMETRIZE
    PARAMETRIZE --> TEST_HIL
    TEST_HIL --> GYM_MAKE
    GYM_MAKE --> CHECK_ENV
    CHECK_ENV --> ENV_CHECKER
    ENV_CHECKER --> UNWRAPPED
    UNWRAPPED --> VALIDATION
    
    PARAMETRIZE --> ENV_TASK
    PARAMETRIZE --> IMAGE_OBS
    ENV_TASK --> PANDA_PICK
    IMAGE_OBS --> BOOL_FLAGS
```

**Test Configuration**
- **Parameterized Tests**: Uses `@pytest.mark.parametrize` to test multiple environment configurations
- **Environment Validation**: Leverages `gymnasium.utils.env_checker.check_env()` for compliance verification
- **Coverage Analysis**: Includes coverage reporting with `--cov=./gym_hil` flag
- **Test Environments**: Currently tests `PandaPickCubeBase-v0` with and without image observations

Sources: [tests/test_env.py:24-33](), [.github/workflows/testing.yml:51-53]()

## Contributing Guidelines

Development contributions should follow the established workflow patterns and pass all automated quality checks.

### Development Workflow Requirements

| Stage | Tool | Requirement |
|-------|------|-------------|
| **Pre-commit** | `pre-commit` | All hooks must pass |
| **Code Quality** | `ruff` | Linting and formatting compliance |
| **Testing** | `pytest` | All tests must pass with coverage |
| **Environment** | `poetry` | Dependency management via Poetry |

**Key Development Practices**
- **Environment Setup**: Use Poetry for dependency installation with `poetry install --all-extras`
- **Code Standards**: Follow Ruff linting and formatting rules
- **Testing**: Write parameterized tests for new environments using `pytest.mark.parametrize`
- **Git Workflow**: Ensure pre-commit hooks pass before committing changes
- **Platform Support**: Tests run on Ubuntu with EGL rendering support

Sources: [.github/workflows/testing.yml:36-49](), [.pre-commit-config.yaml:1-25](), [.github/workflows/quality.yml:44-55]()

## Development Environment Configuration

The project excludes specific files and directories from version control to maintain a clean development environment.

### Git Ignore Patterns

```mermaid
graph LR
    subgraph "Excluded Files and Directories"
        MISC["Miscellaneous<br/>.DS_Store, .vscode"]
        MEDIA["Media Files<br/>*.mp4"]
        PYTHON["Python Build<br/>__pycache__, *.pyc"]
        DIST["Distribution<br/>build/, dist/, *.egg-info"]
        TEST["Test Coverage<br/>htmlcov/, .coverage"]
        LOGS["Log Files<br/>*.log, MUJOCO_LOG.TXT"]
    end
    
    subgraph "Special Exclusions"
        MUJOCO_LOG["MUJOCO_LOG.TXT<br/>MuJoCo Default Log"]
        TEST_DATA["!tests/data<br/>Keep Test Data"]
        MP4_FILES["*.mp4<br/>Video Recordings"]
    end
```

**Notable Exclusions**
- **MuJoCo Logs**: Excludes `MUJOCO_LOG.TXT` which is MuJoCo's default log file
- **Media Files**: Excludes `.mp4` files, likely from environment recordings
- **Test Data**: Explicitly preserves `tests/data` directory with `!tests/data` pattern
- **Standard Python**: Follows typical Python `.gitignore` patterns for build artifacts and caches

Sources: [.gitignore:1-133]()

---

