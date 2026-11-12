<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/dataset-viewer · page 8 Development · fetched 2026-10-26 -->

# Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/_e2e_tests.yml](.github/workflows/_e2e_tests.yml)
- [.github/workflows/_quality-python.yml](.github/workflows/_quality-python.yml)
- [.github/workflows/_unit-tests-python.yml](.github/workflows/_unit-tests-python.yml)
- [.github/workflows/openapi-spec.yml](.github/workflows/openapi-spec.yml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [e2e/Makefile](e2e/Makefile)
- [tools/Python.mk](tools/Python.mk)

</details>



This page provides information for developers working on the dataset-viewer system. It covers development environment setup, code quality standards, testing approaches, and the contribution workflow. For deployment and operational procedures, see [Deployment and Operations](#7). For specific setup instructions, see [Development Setup](#8.1).

## Development Environment Overview

The dataset-viewer system uses a modern Python development stack with Poetry for dependency management and Docker Compose for local service orchestration. The development environment supports both individual component development and full system integration testing.

```mermaid
graph TB
    subgraph "Development Tools"
        Poetry["poetry<br/>Dependency Management"]
        Docker["docker-compose<br/>Service Orchestration"]
        Make["Makefiles<br/>Task Automation"]
    end
    
    subgraph "Code Quality Tools"
        Ruff["ruff<br/>Linting & Formatting"]
        Mypy["mypy<br/>Type Checking"]
        Bandit["bandit<br/>Security Analysis"]
    end
    
    subgraph "Testing Framework"
        Pytest["pytest<br/>Test Runner"]
        UnitTests["Unit Tests<br/>Component Testing"]
        E2ETests["E2E Tests<br/>Integration Testing"]
    end
    
    subgraph "Development Services"
        MongoDB["MongoDB<br/>Local Database"]
        S3Mock["S3 Mock<br/>Local Storage"]
        HubCI["hub-ci.huggingface.co<br/>Test Hub Instance"]
    end
    
    Poetry --> Ruff
    Poetry --> Mypy
    Poetry --> Bandit
    Poetry --> Pytest
    
    Docker --> MongoDB
    Docker --> S3Mock
    
    E2ETests --> HubCI
    E2ETests --> MongoDB
    E2ETests --> S3Mock
```

Sources: [tools/Python.mk:1-50](), [e2e/Makefile:1-59](), [.github/workflows/_quality-python.yml:1-60]()

## Code Quality Standards

The project enforces strict code quality standards through automated tooling integrated into the CI/CD pipeline and development workflow.

### Quality Tools Configuration

| Tool | Purpose | Configuration |
|------|---------|---------------|
| `ruff` | Linting and formatting | Checks `src/` and `tests/` directories |
| `mypy` | Static type checking | Type safety validation |
| `bandit` | Security analysis | Vulnerability scanning |
| `poetry` | Dependency management | Lock file consistency |

### Quality Check Process

```mermaid
graph LR
    subgraph "Code Quality Pipeline"
        LockCheck["poetry lock --check<br/>Dependency Consistency"]
        RuffLint["ruff check<br/>Code Linting"]
        RuffFormat["ruff format --check<br/>Code Formatting"]
        MypyCheck["mypy<br/>Type Checking"]
        BanditScan["bandit -r src<br/>Security Scan"]
    end
    
    subgraph "Development Commands"
        QualityCmd["make quality<br/>Run All Checks"]
        StyleCmd["make style<br/>Auto-format Code"]
    end
    
    LockCheck --> RuffLint
    RuffLint --> RuffFormat
    RuffFormat --> MypyCheck
    MypyCheck --> BanditScan
    
    QualityCmd --> LockCheck
    StyleCmd --> RuffLint
```

Sources: [.github/workflows/_quality-python.yml:36-56](), [tools/Python.mk:22-46]()

## Testing Strategy

The system implements a comprehensive testing strategy with multiple levels of testing to ensure reliability and correctness.

### Test Architecture

```mermaid
graph TB
    subgraph "Testing Levels"
        UnitTests["Unit Tests<br/>pytest -m 'not real_dataset and not integration'"]
        IntegrationTests["Integration Tests<br/>Real MongoDB & S3"]
        E2ETests["End-to-End Tests<br/>Full System Testing"]
    end
    
    subgraph "Test Dependencies"
        MongoDB["MongoDB Container<br/>docker-compose-mongo.yml"]
        TestServices["Test Services<br/>docker-compose-dataset-viewer.yml"]
        HubCI["hub-ci.huggingface.co<br/>Test Hub Instance"]
    end
    
    subgraph "Test Environment Variables"
        CacheMongo["CACHE_MONGO_URL"]
        QueueMongo["QUEUE_MONGO_URL"]
        HFToken["COMMON_HF_TOKEN"]
        S3Config["S3_ACCESS_KEY_ID<br/>S3_SECRET_ACCESS_KEY"]
    end
    
    UnitTests --> MongoDB
    IntegrationTests --> MongoDB
    IntegrationTests --> TestServices
    E2ETests --> TestServices
    E2ETests --> HubCI
    
    MongoDB --> CacheMongo
    MongoDB --> QueueMongo
    TestServices --> HFToken
    TestServices --> S3Config
```

Sources: [.github/workflows/_unit-tests-python.yml:50-62](), [.github/workflows/_e2e_tests.yml:70-117]()

### Test Execution Environment

The testing framework uses specific environment configurations to ensure consistent and isolated test execution:

**Unit Test Configuration:**
- MongoDB URL: `mongodb://localhost:27017`
- Asset storage: `/tmp/assets` and `/tmp/cached-assets`
- Excludes real dataset tests and integration tests

**E2E Test Configuration:**
- Uses `hub-ci.huggingface.co` as test Hub instance
- Hardcoded test tokens for CI environment
- Full service stack with reverse proxy on port 8000
- S3 integration with test buckets

Sources: [.github/workflows/_unit-tests-python.yml:50-62](), [.github/workflows/_e2e_tests.yml:25-70]()

## CI/CD Pipeline

The continuous integration and deployment pipeline automates code quality checks, testing, and deployment processes across all components.

### Workflow Architecture

```mermaid
graph TD
    subgraph "Trigger Events"
        PRTrigger["Pull Request"]
        PushTrigger["Push to main"]
        WorkflowDispatch["Manual Trigger"]
    end
    
    subgraph "Reusable Workflows"
        QualityCheck["_quality-python.yml<br/>Code Quality Checks"]
        UnitTestWorkflow["_unit-tests-python.yml<br/>Unit Testing"]
        E2EWorkflow["_e2e_tests.yml<br/>Integration Testing"]
    end
    
    subgraph "Quality Gates"
        RuffChecks["ruff check/format"]
        MypyValidation["mypy type checking"]
        BanditSecurity["bandit security scan"]
        PytestExecution["pytest test execution"]
    end
    
    subgraph "Environment Setup"
        PythonSetup["Python 3.9.18<br/>Poetry Cache"]
        DependencyInstall["poetry install<br/>System packages"]
        ServiceStart["Docker Compose<br/>Service Startup"]
    end
    
    PRTrigger --> QualityCheck
    PRTrigger --> UnitTestWorkflow
    PRTrigger --> E2EWorkflow
    
    QualityCheck --> RuffChecks
    QualityCheck --> MypyValidation  
    QualityCheck --> BanditSecurity
    
    UnitTestWorkflow --> PytestExecution
    E2EWorkflow --> PytestExecution
    
    QualityCheck --> PythonSetup
    UnitTestWorkflow --> PythonSetup
    E2EWorkflow --> PythonSetup
    
    PythonSetup --> DependencyInstall
    UnitTestWorkflow --> ServiceStart
    E2EWorkflow --> ServiceStart
```

Sources: [.github/workflows/_quality-python.yml:4-60](), [.github/workflows/_unit-tests-python.yml:4-63](), [.github/workflows/_e2e_tests.yml:4-118]()

## Development Workflow

The standard development workflow follows established patterns for code quality, testing, and contribution management.

### Development Commands

The project provides standardized Make targets for common development tasks:

| Command | Purpose | Implementation |
|---------|---------|----------------|
| `make install` | Install dependencies | `poetry install` |
| `make quality` | Run all quality checks | Ruff, mypy, bandit |
| `make style` | Auto-format code | `ruff check --fix`, `ruff format` |
| `make test` | Run tests | `pytest` execution |
| `make lock` | Update dependencies | `poetry lock` and install |

### Service Development

```mermaid
graph LR
    subgraph "Service Components"
        APIService["services/api<br/>FastAPI Application"]
        RowsService["services/rows<br/>Data Access Service"]  
        SearchService["services/search<br/>Search & Filter Service"]
        WorkerService["services/worker<br/>Background Processing"]
        AdminService["services/admin<br/>Management Interface"]
    end
    
    subgraph "Shared Libraries"
        LibCommon["libs/libcommon<br/>Core Utilities"]
        LibAPI["libs/libapi<br/>API Utilities"]
    end
    
    subgraph "Development Tools"
        UvicornDev["uvicorn --reload<br/>Development Server"]
        PytestWatch["pytest --watch<br/>Test Watching"]
        DockerCompose["docker-compose up<br/>Local Stack"]
    end
    
    APIService --> LibCommon
    RowsService --> LibCommon
    SearchService --> LibCommon
    WorkerService --> LibCommon
    AdminService --> LibCommon
    
    APIService --> LibAPI
    RowsService --> LibAPI
    SearchService --> LibAPI
    
    APIService --> UvicornDev
    RowsService --> UvicornDev
    SearchService --> UvicornDev
    
    LibCommon --> PytestWatch
    LibAPI --> PytestWatch
    
    UvicornDev --> DockerCompose
```

Sources: [tools/Python.mk:5-46](), [e2e/Makefile:30-54]()

## Contributing Process

The project follows a structured contribution process with clear guidelines for code quality, testing, and review procedures.

### Contribution Workflow

```mermaid
graph TD
    subgraph "Issue Management"
        IssueList["GitHub Issues<br/>Open Issues List"]
        SelfAssign["#take or #self-assign<br/>Claim Issue"]
        WorkIssue["Work on Issue<br/>Local Development"]
    end
    
    subgraph "Development Process"
        ForkRepo["Fork Repository<br/>GitHub Fork"]
        CloneFork["git clone<br/>Local Clone"]
        CreateBranch["git checkout -b<br/>Feature Branch"]
        DevWork["Development Work<br/>Code Changes"]
    end
    
    subgraph "Quality Assurance"
        RunStyle["make style<br/>Format Code"]
        RunQuality["make quality<br/>Quality Checks"]
        RunTests["pytest<br/>Test Execution"]
        CommitChanges["git commit<br/>Record Changes"]
    end
    
    subgraph "Submission"
        PushBranch["git push<br/>Push to Fork"]
        CreatePR["Create Pull Request<br/>GitHub PR"]
        ReviewProcess["Code Review<br/>Maintainer Review"]
    end
    
    IssueList --> SelfAssign
    SelfAssign --> WorkIssue
    WorkIssue --> ForkRepo
    
    ForkRepo --> CloneFork
    CloneFork --> CreateBranch
    CreateBranch --> DevWork
    
    DevWork --> RunStyle
    RunStyle --> RunQuality
    RunQuality --> RunTests
    RunTests --> CommitChanges
    
    CommitChanges --> PushBranch
    PushBranch --> CreatePR
    CreatePR --> ReviewProcess
```

Sources: [CONTRIBUTING.md:15-82]()

The contribution process emphasizes code quality through automated tooling and follows HuggingFace docstring guidelines. All contributions must pass the CI/CD pipeline quality gates including linting, type checking, security analysis, and comprehensive testing before merge approval.

Sources: [CONTRIBUTING.md:84-92]()

---

