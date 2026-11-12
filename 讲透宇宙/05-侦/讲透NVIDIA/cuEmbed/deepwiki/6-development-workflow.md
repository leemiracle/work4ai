<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuEmbed · page 6 Development Workflow · fetched 2026-10-26 -->

# Development Workflow

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitlab-ci.yml](.gitlab-ci.yml)
- [CONTRIBUTING.md](CONTRIBUTING.md)

</details>



## Purpose and Scope

This document covers the development workflow, processes, and tooling used in the cuEmbed project. It provides an overview of the continuous integration pipeline, code quality enforcement, and contribution guidelines that ensure consistent development practices.

For detailed CI/CD pipeline configuration, see [CI/CD Pipeline](#6.1). For specific code formatting and quality tools, see [Code Quality](#6.2). For comprehensive contribution requirements, see [Contributing](#6.3).

## Development Process Overview

The cuEmbed project follows a structured development workflow that emphasizes code quality, comprehensive testing, and performance validation. The process integrates multiple quality gates and automated checks to maintain the library's reliability and performance standards.

### Development Workflow Architecture

```mermaid
graph TD
    DEV["Developer"] --> FEATURE["Feature Branch"]
    FEATURE --> PRECOMMIT["pre-commit hooks"]
    PRECOMMIT --> QUALITY_PASS{"Quality Checks Pass?"}
    QUALITY_PASS -->|No| FEATURE
    QUALITY_PASS -->|Yes| PR["Pull Request to main"]
    
    PR --> CI_TRIGGER["CI Pipeline Trigger"]
    CI_TRIGGER --> CI_CONFIG[".gitlab-ci.yml"]
    CI_CONFIG --> CI_BRANCH["ci-config branch"]
    CI_BRANCH --> BUILD_MATRIX["Build Matrix"]
    
    BUILD_MATRIX --> UNIT_TESTS["Unit Tests"]
    BUILD_MATRIX --> CORRECTNESS_TESTS["Correctness Tests"]
    BUILD_MATRIX --> INTEGRATION_TESTS["Integration Tests"]
    BUILD_MATRIX --> SANITIZER["Compute Sanitizer"]
    
    UNIT_TESTS --> TEST_RESULTS["Test Results"]
    CORRECTNESS_TESTS --> TEST_RESULTS
    INTEGRATION_TESTS --> TEST_RESULTS
    SANITIZER --> TEST_RESULTS
    
    TEST_RESULTS --> PERF_CHECK{"Performance Impact?"}
    PERF_CHECK -->|Yes| BENCHMARK["Run Benchmarks"]
    PERF_CHECK -->|No| CODE_REVIEW["Code Review"]
    BENCHMARK --> PERF_ANALYSIS["Performance Analysis"]
    PERF_ANALYSIS --> CODE_REVIEW
    
    CODE_REVIEW --> REVIEW_PASS{"Review Approved?"}
    REVIEW_PASS -->|No| FEATURE
    REVIEW_PASS -->|Yes| MERGE["Merge to main"]
```

Sources: [CONTRIBUTING.md:1-22](), [.gitlab-ci.yml:1-5]()

## CI/CD System Architecture

The cuEmbed project uses GitLab CI with a centralized configuration approach where the main CI logic is maintained in a separate `ci-config` branch, promoting reusability and maintainability across different branches.

### CI/CD Pipeline Structure

```mermaid
graph LR
    subgraph "Repository Branches"
        MAIN["main branch"]
        FEATURE["feature/* branches"]
        CI_CONFIG["ci-config branch"]
    end
    
    subgraph "CI Configuration"
        GITLAB_CI[".gitlab-ci.yml"]
        CI_INCLUDE["include: ci-config/.gitlab-ci.yml"]
        CI_LOGIC["Centralized CI Logic"]
    end
    
    subgraph "Build Targets"
        CMAKE_ROOT["CMakeLists.txt BUILD_TESTS=ON"]
        TEST_BUILD["tests/ executables"]
        BENCH_BUILD["benchmarks/ executables"]
        PYT_BUILD["examples/pytorch/ extension"]
    end
    
    subgraph "Quality Gates"
        CLANG_FORMAT["clang-format"]
        CPPLINT["cpplint"]
        COMPUTE_SANITIZER["NVIDIA Compute Sanitizer"]
    end
    
    subgraph "Test Execution"
        UNIT_EXEC["Unit Test Execution"]
        CORRECTNESS_EXEC["GPU vs CPU Validation"]
        PERFORMANCE_EXEC["Benchmark Execution"]
    end
    
    MAIN --> GITLAB_CI
    FEATURE --> GITLAB_CI
    GITLAB_CI --> CI_INCLUDE
    CI_INCLUDE --> CI_CONFIG
    CI_CONFIG --> CI_LOGIC
    
    CI_LOGIC --> CMAKE_ROOT
    CMAKE_ROOT --> TEST_BUILD
    CMAKE_ROOT --> BENCH_BUILD
    CMAKE_ROOT --> PYT_BUILD
    
    CI_LOGIC --> CLANG_FORMAT
    CI_LOGIC --> CPPLINT
    CI_LOGIC --> COMPUTE_SANITIZER
    
    TEST_BUILD --> UNIT_EXEC
    TEST_BUILD --> CORRECTNESS_EXEC
    BENCH_BUILD --> PERFORMANCE_EXEC
```

Sources: [.gitlab-ci.yml:1-5]()

## Code Quality Requirements

The project enforces strict code quality standards through automated tools and manual review processes. All contributions must pass these quality gates before acceptance.

### Code Quality Enforcement Pipeline

| Stage | Tool | Purpose | Failure Action |
|-------|------|---------|----------------|
| Pre-commit | `clang-format` | Code formatting consistency | Block commit |
| Pre-commit | `cpplint` | C++ style compliance | Block commit |
| CI Build | `NVIDIA Compute Sanitizer` | Memory safety validation | Fail CI |
| Manual Review | Code Review | Logic and design validation | Block merge |

The pre-commit hooks are installed via:
```bash
pip install pre-commit && pre-commit install
```

Quality verification can be run manually:
```bash
pre-commit run --files all
```

Sources: [CONTRIBUTING.md:15-16]()

## Testing Requirements

All contributions must include appropriate test coverage and pass existing test suites. The testing strategy encompasses multiple levels of validation.

### Test Coverage Requirements

```mermaid
graph TD
    CONTRIBUTION["New Contribution"] --> TEST_ANALYSIS["Test Impact Analysis"]
    TEST_ANALYSIS --> UNIT_REQ["Unit Tests Required?"]
    TEST_ANALYSIS --> CORRECTNESS_REQ["Correctness Tests Required?"]
    TEST_ANALYSIS --> INTEGRATION_REQ["Integration Tests Required?"]
    
    UNIT_REQ -->|Yes| UNIT_ADD["Add/Modify Unit Tests"]
    CORRECTNESS_REQ -->|Yes| CORRECTNESS_ADD["Add/Modify Correctness Tests"]
    INTEGRATION_REQ -->|Yes| INTEGRATION_ADD["Add/Modify Integration Tests"]
    
    UNIT_ADD --> TEST_EXECUTION["Execute Test Suite"]
    CORRECTNESS_ADD --> TEST_EXECUTION
    INTEGRATION_ADD --> TEST_EXECUTION
    UNIT_REQ -->|No| TEST_EXECUTION
    CORRECTNESS_REQ -->|No| TEST_EXECUTION
    INTEGRATION_REQ -->|No| TEST_EXECUTION
    
    TEST_EXECUTION --> ALL_PASS{"All Tests Pass?"}
    ALL_PASS -->|No| CONTRIBUTION
    ALL_PASS -->|Yes| SANITIZER_CHECK["Compute Sanitizer Check"]
    
    SANITIZER_CHECK --> SANITIZER_PASS{"Sanitizer Clean?"}
    SANITIZER_PASS -->|No| CONTRIBUTION
    SANITIZER_PASS -->|Yes| READY_REVIEW["Ready for Review"]
```

Test execution is performed through the CMake build system with `BUILD_TESTS=ON` option. The tests are located in the `tests/` directory and must validate functionality across different configurations and parameter combinations.

Sources: [CONTRIBUTING.md:9-12]()

## Performance Validation Process

Changes that may impact performance require benchmark validation to prevent performance regressions. This process ensures that optimizations are genuine improvements and that feature additions don't negatively affect existing performance characteristics.

### Performance Testing Workflow

The performance validation process uses the benchmarking infrastructure to measure impact:

```bash
cd benchmarks
./sweep_parameters.sh
```

This generates comprehensive performance data in CSV format for analysis. Performance comparisons should be conducted both before and after changes to identify any regressions or improvements.

Performance impact assessment criteria:
- **Significant Impact**: Changes to core kernel implementations, memory access patterns, or algorithmic approaches
- **Moderate Impact**: Changes to host API, indexing logic, or data structure layouts  
- **Minimal Impact**: Documentation, test additions, or build system modifications

Sources: [CONTRIBUTING.md:17-18]()

## Commit and Review Process

The project follows a structured commit and review process that emphasizes clear communication, comprehensive testing, and collaborative improvement of code quality.

### Commit Requirements

All commits must be signed using the `--signoff` flag to certify compliance with the Developer Certificate of Origin:

```bash
git commit -s
# or
git commit --signoff
```

This certification indicates that the contributor has the right to submit the work under the project's open source license and understands the public nature of the contribution.

### Pull Request Guidelines

Pull requests should adhere to specific scope and quality standards:

- **Scope**: Limited, focused changes that address a single concern or feature
- **Target**: All pull requests target the `main` branch
- **Commit Messages**: Clear, descriptive messages that facilitate code review
- **Documentation**: Updated inline documentation and relevant README files
- **Test Coverage**: Appropriate test additions or modifications

The review process involves both automated checks and human review to ensure code quality, correctness, and maintainability.

Sources: [CONTRIBUTING.md:4-8](), [CONTRIBUTING.md:19-20](), [CONTRIBUTING.md:23-62]()

---

