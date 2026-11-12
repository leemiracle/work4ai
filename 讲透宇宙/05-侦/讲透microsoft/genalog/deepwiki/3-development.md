<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/genalog · page 3 Development · fetched 2026-10-26 -->

# Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [devops/nightly.yml](devops/nightly.yml)
- [devops/pr-gate.yml](devops/pr-gate.yml)
- [requirements-dev.txt](requirements-dev.txt)
- [tests/unit/text/test_alignment.py](tests/unit/text/test_alignment.py)
- [tox.ini](tox.ini)

</details>



This document covers the development infrastructure, testing framework, and continuous integration setup for the genalog project. It provides guidance for contributors on setting up development environments, running tests, and understanding the automated quality gates.

For information about the overall system architecture, see [System Architecture](#1.2). For details about building and releasing packages, see [Release Process](#3.3).

## Testing Framework

Genalog uses `tox` as the primary test orchestration tool, which manages multiple Python environments and test execution. The test suite is built on `pytest` with comprehensive coverage reporting and custom test markers for different test categories.

### Test Environment Configuration

The test environment is configured through `tox.ini` which defines multiple test environments and execution parameters:

```mermaid
graph TB
    subgraph "Test Execution Flow"
        A["tox.ini"] --> B["testenv"]
        A --> C["testenv:flake8"]
        
        B --> D["pytest"]
        D --> E["Unit Tests"]
        D --> F["Integration Tests"]
        D --> G["E2E Tests"]
        
        C --> H["flake8 ."]
        
        E --> I["Coverage Report"]
        F --> I
        G --> I
        
        I --> J["HTML Report"]
        I --> K["XML Report"]
        I --> L["Terminal Output"]
    end
    
    subgraph "Test Markers"
        M["@pytest.mark.slow"]
        N["@pytest.mark.azure"]
        O["@pytest.mark.io"]
    end
    
    E --> M
    F --> N
    G --> O
```

**Test Environment Setup and Execution**

*Sources: [tox.ini:1-63]()*

The testing framework supports multiple Python versions (3.6, 3.7, 3.8) and uses custom pytest markers to categorize tests:

| Marker | Purpose | Usage |
|--------|---------|-------|
| `slow` | Long-running tests | `pytest -m "not slow"` |
| `azure` | Azure service integration tests | `pytest -m "not azure"` |
| `io` | I/O operations (disk, network) | `pytest -m "not io"` |

Environment variables are passed through for Azure service testing, including `BLOB_KEY`, `COGNITIVE_SERVICE_KEY`, and `COMPUTER_VISION_SUBSCRIPTION_KEY`.

### Coverage Reporting

Test coverage is configured to generate multiple report formats with comprehensive tracking:

```mermaid
graph LR
    subgraph "Coverage Configuration"
        A["pytest execution"] --> B["--cov=genalog"]
        B --> C["--cov-report=html"]
        B --> D["--cov-report=xml"] 
        B --> E["--cov-report=term-missing"]
        B --> F["--junitxml=junit/test-results.xml"]
        
        C --> G["HTML Coverage Report"]
        D --> H["XML Coverage Report"]
        E --> I["Terminal Coverage"]
        F --> J["JUnit XML Results"]
    end
```

**Coverage Reporting Configuration**

*Sources: [tox.ini:47-50]()*

## Code Quality Tools

The project enforces code quality through automated linting and formatting tools integrated into the development workflow.

### Flake8 Configuration

Static code analysis is performed using `flake8` with import order checking:

```mermaid
graph TB
    subgraph "Code Quality Pipeline"
        A["Source Code"] --> B["flake8"]
        B --> C["Style Checking"]
        B --> D["Import Order Validation"]
        B --> E["Line Length Enforcement"]
        
        C --> F["PEP 8 Compliance"]
        D --> G["flake8-import-order"]
        E --> H["max-line-length = 140"]
        
        F --> I["Quality Gate"]
        G --> I
        H --> I
    end
```

**Flake8 Quality Enforcement**

*Sources: [tox.ini:53-63]()*

The flake8 configuration enforces:
- Maximum line length of 140 characters
- Import order style using `edited` format
- Application import names: `genalog`, `tests`
- Exclusion of build artifacts and virtual environments

## CI/CD Pipeline Architecture

The project uses Azure DevOps pipelines for continuous integration with separate configurations for pull request validation and nightly builds.

### Pipeline Structure

```mermaid
graph TB
    subgraph "PR Gate Pipeline"
        A["pr-gate.yml"] --> B["static_analysis"]
        B --> C["unit_tests"]
        B --> D["e2e_tests"]
        C --> E["collect_final_code_coverage"]
        D --> E
        
        B --> F["flake8_linux_py36"]
        F --> G["ComponentGovernanceComponentDetection"]
        
        C --> H["Python 3.6, 3.7, 3.8"]
        C --> I["ubuntu-18.04"]
        C --> J["unit + io tests"]
        
        D --> K["Python 3.6 only"]
        D --> L["e2e tests"]
    end
    
    subgraph "Nightly Pipeline"
        M["nightly.yml"] --> N["static_analysis"]
        N --> O["unit_tests"]
        N --> P["e2e_tests"]
        O --> Q["collect_final_code_coverage"]
        P --> Q
        Q --> R["publish_artifacts"]
        
        O --> S["Python 3.6, 3.7, 3.8"]
        P --> T["Python 3.6, 3.7, 3.8"]
        R --> U["build_wheel_n_sdist"]
        R --> V["PublishBuildArtifacts"]
    end
```

**CI/CD Pipeline Architecture**

*Sources: [devops/pr-gate.yml:1-52](), [devops/nightly.yml:1-66]()*

### Pipeline Stages

The CI/CD system implements a multi-stage approach with dependency management:

| Stage | PR Gate | Nightly | Purpose |
|-------|---------|---------|---------|
| `static_analysis` | ✓ | ✓ | Flake8 linting and component governance |
| `unit_tests` | ✓ | ✓ | Unit and I/O integration tests |
| `e2e_tests` | ✓ | ✓ | End-to-end Azure integration tests |
| `collect_final_code_coverage` | ✓ | ✓ | Merge coverage reports |
| `publish_artifacts` | ✗ | ✓ | Build and publish distribution packages |

### Azure Resource Integration

Both pipelines integrate with Azure services for testing:

```mermaid
graph LR
    subgraph "Azure Resources"
        A["azureResourceKeys"] --> B["BLOB_KEY"]
        A --> C["COGNITIVE_SERVICE_KEY"]
        A --> D["COMPUTER_VISION_SUBSCRIPTION_KEY"]
        A --> E["SEARCH_SERVICE_KEY"]
    end
    
    subgraph "Pipeline Variables"
        B --> F["E2E Tests"]
        C --> F
        D --> F
        E --> F
    end
    
    subgraph "Test Execution"
        F --> G["Azure OCR Integration"]
        F --> H["Blob Storage Tests"]
        F --> I["Cognitive Search Tests"]
    end
```

**Azure Service Integration for Testing**

*Sources: [devops/pr-gate.yml:13-14](), [devops/nightly.yml:12-14]()*

## Development Dependencies

The development environment requires specific packages for testing, linting, and development workflows:

```mermaid
graph TB
    subgraph "Development Dependencies"
        A["requirements-dev.txt"] --> B["Testing Framework"]
        A --> C["Code Quality"]
        A --> D["Build Tools"]
        
        B --> E["pytest"]
        B --> F["pytest-cov"]
        B --> G["pytest-mock"]
        B --> H["pytest-xdist[psutil]"]
        B --> I["pytest-lazy-fixture"]
        
        C --> J["flake8"]
        C --> K["flake8-import-order"]
        
        D --> L["tox"]
    end
```

**Development Dependency Structure**

*Sources: [requirements-dev.txt:1-9]()*

### Test Framework Components

The pytest ecosystem provides comprehensive testing capabilities:

| Package | Purpose |
|---------|---------|
| `pytest` | Core testing framework |
| `pytest-cov` | Coverage reporting integration |
| `pytest-mock` | Mocking utilities for unit tests |
| `pytest-xdist[psutil]` | Parallel test execution |
| `pytest-lazy-fixture` | Advanced fixture management |

## Development Workflow

### Local Development Setup

To set up a development environment:

1. Install development dependencies: `pip install -r requirements-dev.txt`
2. Install tox for environment management: `pip install tox`
3. Run the full test suite: `tox`
4. Run specific test categories: `tox -- -m "not azure and not slow"`

### Test Execution Patterns

```mermaid
graph TB
    subgraph "Local Development"
        A["Developer"] --> B["tox"]
        A --> C["tox -- -m 'not azure'"]
        A --> D["pytest tests/unit/"]
        
        B --> E["Full Test Suite"]
        C --> F["Fast Local Tests"]
        D --> G["Unit Tests Only"]
    end
    
    subgraph "CI Environment"
        H["PR Trigger"] --> I["pr-gate.yml"]
        J["Nightly Schedule"] --> K["nightly.yml"]
        
        I --> L["Quality Gates"]
        K --> M["Full Integration + Artifacts"]
    end
```

**Development and CI Test Execution Patterns**

*Sources: [tox.ini:16-23](), [devops/pr-gate.yml:10-12](), [devops/nightly.yml:8-10]()*

### Test Categories and Execution

The test suite supports selective execution based on markers:

- **Fast feedback loop**: `tox -- -m "not slow and not azure"` 
- **Integration testing**: `tox -- -m "azure"`
- **I/O testing**: `tox -- -m "io"`
- **Full suite**: `tox` (no arguments)

This structure allows developers to get rapid feedback during development while ensuring comprehensive testing in CI environments.

---

