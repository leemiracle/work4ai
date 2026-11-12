<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/agent-eval · page 5 Development · fetched 2026-10-26 -->

# Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Development.md](Development.md)
- [Makefile](Makefile)

</details>



This document provides a comprehensive guide for developers contributing to the agent-eval toolkit. It covers development environment setup, coding practices, testing procedures, schema management, and the release process. For information about using agent-eval as an end user, see [User Guide](#3). For information about the internal architecture, see [Architecture](#4).

## Development Environment

Setting up a development environment for agent-eval involves cloning the repository and installing development dependencies.

### Environment Setup

The development setup follows standard Python packaging practices with additional dependencies for code quality tools:

```bash
git clone https://github.com/allenai/agent-eval
cd agent-eval
pip install -e ".[dev]"
```

This installs the package in editable mode with development dependencies including testing frameworks, code formatters, and schema generation tools.

**Development Environment Components**
```mermaid
graph TB
    subgraph "Local Development"
        REPO["Git Repository"]
        VENV["Python Virtual Environment"]
        EDITABLE["Editable Install"]
    end
    
    subgraph "Development Dependencies"
        PYTEST["pytest"]
        BLACK["black formatter"]
        ISORT["isort import sorter"]
        PYDANTIC["pydantic"]
    end
    
    subgraph "Development Tools"
        MAKEFILE["Makefile"]
        SCRIPTS["scripts/ directory"]
        UPDATE_SCHEMA["update_schema.py"]
        PUBLISH["publish.sh"]
    end
    
    REPO --> VENV
    VENV --> EDITABLE
    EDITABLE --> PYTEST
    EDITABLE --> BLACK
    EDITABLE --> ISORT
    EDITABLE --> PYDANTIC
    
    MAKEFILE --> BLACK
    MAKEFILE --> ISORT
    MAKEFILE --> PYTEST
    SCRIPTS --> UPDATE_SCHEMA
    SCRIPTS --> PUBLISH
```

Sources: [Development.md:1-25](), [Makefile:1-25]()

## Code Quality and Formatting

The codebase maintains consistent code quality through automated formatting and linting tools integrated into the development workflow.

### Formatting Workflow

The project uses `black` for code formatting and `isort` for import organization:

| Tool | Purpose | Configuration |
|------|---------|---------------|
| `black` | Code formatting | Standard configuration |
| `isort` | Import sorting | Compatible with black |
| `pytest` | Unit testing | Test discovery and execution |

The formatting process is automated through the Makefile:

**Code Quality Pipeline**
```mermaid
graph LR
    subgraph "Development Process"
        CODE["Code Changes"]
        FORMAT["make format"]
        TEST["make test"]
        COMMIT["Git Commit"]
    end
    
    subgraph "Formatting Tools"
        ISORT_CMD["isort ."]
        BLACK_CMD["black ."]
    end
    
    subgraph "Testing"
        PYTEST_CMD["pytest"]
    end
    
    CODE --> FORMAT
    FORMAT --> ISORT_CMD
    FORMAT --> BLACK_CMD
    FORMAT --> TEST
    TEST --> PYTEST_CMD
    TEST --> COMMIT
```

Sources: [Makefile:3-7](), [Makefile:22-24]()

## Schema Management

The agent-eval system maintains strict schema compatibility with HuggingFace datasets through automated schema generation and validation.

### Schema Update Process

The schema management system ensures that Pydantic models remain synchronized with HuggingFace dataset schemas:

**Schema Generation Workflow**
```mermaid
graph TB
    subgraph "Source Models"
        PYDANTIC_MODELS["Pydantic Models"]
        TASK_RESULT["TaskResult"]
        EVAL_RESULT["EvalResult"]
    end
    
    subgraph "Schema Generation"
        UPDATE_SCRIPT["scripts/update_schema.py"]
        SCHEMA_GENERATOR["schema_generator.py"]
        DATASET_FEATURES["dataset_features.yml"]
    end
    
    subgraph "Validation"
        CI_CHECK["CI Schema Check"]
        HF_SCHEMA["HuggingFace Schema"]
    end
    
    PYDANTIC_MODELS --> UPDATE_SCRIPT
    TASK_RESULT --> SCHEMA_GENERATOR
    EVAL_RESULT --> SCHEMA_GENERATOR
    UPDATE_SCRIPT --> SCHEMA_GENERATOR
    SCHEMA_GENERATOR --> DATASET_FEATURES
    DATASET_FEATURES --> CI_CHECK
    CI_CHECK --> HF_SCHEMA
```

The schema update process is triggered when Pydantic models change:

1. Models are modified in the codebase
2. CI detects schema inconsistency
3. Developer runs schema update command
4. New schema is generated and committed

Sources: [Development.md:16-24](), [Makefile:17-20]()

## Testing Framework

The testing infrastructure ensures code quality and prevents regressions through comprehensive test coverage.

### Test Execution

Testing is managed through `pytest` with simple execution commands:

**Testing Architecture**
```mermaid
graph TB
    subgraph "Test Categories"
        UNIT_TESTS["Unit Tests"]
        INTEGRATION_TESTS["Integration Tests"]
        SCHEMA_TESTS["Schema Validation Tests"]
    end
    
    subgraph "Test Infrastructure"
        PYTEST_FRAMEWORK["pytest Framework"]
        TEST_FIXTURES["Test Fixtures"]
        MOCK_DATA["Mock Data"]
    end
    
    subgraph "CI Integration"
        GITHUB_ACTIONS["GitHub Actions"]
        AUTOMATED_TESTING["Automated Testing"]
        SCHEMA_VALIDATION["Schema Validation"]
    end
    
    UNIT_TESTS --> PYTEST_FRAMEWORK
    INTEGRATION_TESTS --> PYTEST_FRAMEWORK
    SCHEMA_TESTS --> PYTEST_FRAMEWORK
    
    PYTEST_FRAMEWORK --> TEST_FIXTURES
    PYTEST_FRAMEWORK --> MOCK_DATA
    
    PYTEST_FRAMEWORK --> GITHUB_ACTIONS
    GITHUB_ACTIONS --> AUTOMATED_TESTING
    GITHUB_ACTIONS --> SCHEMA_VALIDATION
```

Sources: [Makefile:22-24]()

## Publication and Release Process

The publication workflow handles versioning, packaging, and distribution to PyPI through automated scripts.

### Release Workflow

The release process involves version tagging and automated publishing:

**Publication Pipeline**
```mermaid
graph LR
    subgraph "Release Preparation"
        VERSION_TAG["Version Tagging"]
        TAG_SCRIPT["tag.sh"]
        BUILD_PACKAGE["Package Building"]
    end
    
    subgraph "Publication"
        PUBLISH_SCRIPT["scripts/publish.sh"]
        PYPI_TOKEN["PYPI_TOKEN"]
        PYPI_UPLOAD["PyPI Upload"]
    end
    
    subgraph "Automation"
        MAKE_TAG["make tag"]
        MAKE_PUBLISH["make publish"]
    end
    
    VERSION_TAG --> TAG_SCRIPT
    TAG_SCRIPT --> BUILD_PACKAGE
    BUILD_PACKAGE --> PUBLISH_SCRIPT
    PUBLISH_SCRIPT --> PYPI_TOKEN
    PYPI_TOKEN --> PYPI_UPLOAD
    
    MAKE_TAG --> TAG_SCRIPT
    MAKE_PUBLISH --> PUBLISH_SCRIPT
```

The publication process requires authentication through environment variables and follows these steps:

1. Set PYPI_TOKEN environment variable
2. Execute publication script
3. Package is built and uploaded to PyPI

Sources: [Development.md:8-14](), [Makefile:8-15]()

## Development Tasks

The Makefile provides convenient commands for common development tasks:

| Command | Purpose | Implementation |
|---------|---------|----------------|
| `make format` | Format code with black and isort | Runs formatting tools |
| `make test` | Execute test suite | Runs pytest |
| `make tag` | Create version tag | Executes tagging script |
| `make publish` | Publish to PyPI | Runs publication script |
| `make update-schema` | Update HF schema | Regenerates dataset schema |

This structured approach ensures consistent development practices and maintains code quality across contributions to the agent-eval toolkit.

Sources: [Makefile:1-25](), [Development.md:1-25]()

---

