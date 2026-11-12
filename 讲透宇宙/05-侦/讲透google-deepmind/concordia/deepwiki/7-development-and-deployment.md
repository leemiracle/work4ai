<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/concordia · page 7 Development and Deployment · fetched 2026-10-26 -->

# Development and Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/install/action.yml](.github/actions/install/action.yml)
- [.github/workflows/codeql-analysis.yml](.github/workflows/codeql-analysis.yml)
- [.github/workflows/pypi-publish.yml](.github/workflows/pypi-publish.yml)
- [.github/workflows/pypi-test.yml](.github/workflows/pypi-test.yml)
- [.github/workflows/scorecards-analysis.yml](.github/workflows/scorecards-analysis.yml)
- [.github/workflows/test-concordia.yml](.github/workflows/test-concordia.yml)
- [.github/workflows/test-examples.yml](.github/workflows/test-examples.yml)
- [bin/install.sh](bin/install.sh)
- [bin/test.sh](bin/test.sh)
- [bin/test_examples.sh](bin/test_examples.sh)
- [bin/update_requirements.sh](bin/update_requirements.sh)
- [pyproject.toml](pyproject.toml)
- [requirements.txt](requirements.txt)

</details>



This document covers the development infrastructure, continuous integration/continuous deployment (CI/CD) pipeline, testing framework, and package distribution system for the Concordia repository. It provides technical details for contributors and maintainers working on the codebase.

For information about configuring and launching simulations, see [Configuration and Launching](#4). For details about the core architecture and components, see [Core Architecture](#2).

## Development Environment

Concordia uses Python 3.11 as the primary development environment, with support for Python 3.11, 3.12, and 3.13 in production. The development environment is configured through several key files:

- **Python Version**: Specified in [.python-version:1]() as `3.11`
- **Dependencies**: Managed through [requirements.txt:1-1800]() with pinned versions and cryptographic hashes
- **Installation**: Automated via [bin/install.sh:1-32]()

### Development Environment Setup

```mermaid
graph TB
    subgraph "Local Development"
        PythonVersion[".python-version<br/>Python 3.11"]
        Requirements["requirements.txt<br/>Pinned Dependencies"]
        InstallScript["bin/install.sh<br/>Installation Script"]
    end
    
    subgraph "GitHub Actions Environment"
        SetupPython["actions/setup-python"]
        CacheSystem["actions/cache"]
        VenvCreation["venv Creation"]
    end
    
    subgraph "Installation Process"
        PipInstall["pip install --no-deps<br/>--require-hashes"]
        ConcordiaInstall["pip install --no-deps<br/>--editable ."]
    end
    
    PythonVersion -->|"specifies"| SetupPython
    Requirements -->|"defines"| PipInstall
    InstallScript -->|"orchestrates"| PipInstall
    InstallScript -->|"installs"| ConcordiaInstall
    
    SetupPython -->|"creates"| VenvCreation
    CacheSystem -->|"accelerates"| VenvCreation
    VenvCreation -->|"activates"| PipInstall
```

Sources: [.python-version:1](), [requirements.txt:1-1800](), [bin/install.sh:1-32](), [.github/actions/install/action.yml:1-84]()

## CI/CD Pipeline Overview

The CI/CD system consists of six GitHub Actions workflows that handle testing, security analysis, and package distribution:

### GitHub Actions Workflow Architecture

```mermaid
graph TB
    subgraph "GitHub Events"
        pushMain["push: branches: [main]"]
        pullRequest["pull_request: branches: [main]"]  
        releasePublished["release: types: [published]"]
        scheduleWeekly["schedule: cron: '17 10 * * 0'"]
        scheduleMonday["schedule: cron: '0 2 * * 1'"]
        workflowDispatch["workflow_dispatch"]
    end
    
    subgraph "Core Testing Workflows"
        testConcordia[".github/workflows/test-concordia.yml"]
        testExamples[".github/workflows/test-examples.yml"]
    end
    
    subgraph "Security Workflows"
        codeqlAnalysis[".github/workflows/codeql-analysis.yml"]
        scorecardsAnalysis[".github/workflows/scorecards-analysis.yml"]
    end
    
    subgraph "Distribution Workflows"
        pypiPublish[".github/workflows/pypi-publish.yml"]
        pypiTest[".github/workflows/pypi-test.yml"]
    end
    
    subgraph "Shared Action"
        installAction[".github/actions/install/action.yml"]
    end
    
    pushMain -->|"triggers"| testConcordia
    pushMain -->|"triggers"| testExamples
    pushMain -->|"triggers"| codeqlAnalysis
    
    pullRequest -->|"triggers"| testConcordia
    pullRequest -->|"triggers"| testExamples
    pullRequest -->|"triggers"| codeqlAnalysis
    
    releasePublished -->|"triggers"| pypiPublish
    workflowDispatch -->|"triggers"| pypiPublish
    
    scheduleWeekly -->|"triggers"| scorecardsAnalysis
    scheduleMonday -->|"triggers"| pypiTest
    
    pypiPublish -->|"workflow_run: completed"| pypiTest
    
    testConcordia -->|"uses"| installAction
    testExamples -->|"uses"| installAction
```

### Workflow Job Dependencies

```mermaid
graph TB
    subgraph "pypi-publish Workflow Jobs"
        buildJob["build"]
        testJob["test"]
        publishJob["publish"]
    end
    
    subgraph "Job Matrix Configuration"
        osMatrix["os: [macos-13, macos-14, ubuntu-22.04, ubuntu-24.04]"]
        pythonMatrix["python-version: ['3.11', '3.12', '3.13']"]
    end
    
    subgraph "Build Artifacts"
        sdist["python setup.py sdist"]
        bdistWheel["python setup.py bdist_wheel"]
        nameNormalization["gdm-concordia → gdm_concordia"]
    end
    
    subgraph "Publication Targets"
        testPyPI["TestPyPI: test.pypi.org"]
        pyPI["PyPI: pypi.org"]
    end
    
    buildJob -->|"needs: build"| testJob
    testJob -->|"needs: [build, test]"| publishJob
    
    buildJob -->|"produces"| sdist
    buildJob -->|"produces"| bdistWheel
    buildJob -->|"applies"| nameNormalization
    
    osMatrix -->|"configures"| testJob
    pythonMatrix -->|"configures"| testJob
    
    publishJob -->|"uploads to"| testPyPI
    publishJob -->|"uploads to"| pyPI
```

Sources: [.github/workflows/test-concordia.yml:1-56](), [.github/workflows/test-examples.yml:1-70](), [.github/workflows/pypi-publish.yml:1-114](), [.github/workflows/codeql-analysis.yml:1-63](), [.github/workflows/scorecards-analysis.yml:1-63](), [.github/workflows/pypi-test.yml:1-75]()

## Testing Framework

The testing system consists of two primary workflows with distinct validation phases:

### test-concordia Workflow Steps

```mermaid
graph TB
    subgraph "test-concordia Job Steps"
        checkoutStep["uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683"]
        installStep["uses: ./.github/actions/install"]
        pytestStep["run: pytest concordia"]
        pylintStep["run: pylint --errors-only concordia"]
        pytypeStep["run: pytype concordia"]
    end
    
    subgraph "install Action Components"
        setupPython["uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065"]
        cacheRestore["uses: actions/cache/restore@5a3ec84eff668545956fd18022155c47e93e2684"]
        venvCreate["python -m venv venv"]
        binInstall["./bin/install.sh"]
        cacheSave["uses: actions/cache/save@5a3ec84eff668545956fd18022155c47e93e2684"]
    end
    
    checkoutStep -->|"step 1"| installStep
    installStep -->|"step 2"| pytestStep
    pytestStep -->|"step 3"| pylintStep
    pylintStep -->|"step 4"| pytypeStep
    
    installStep -->|"executes"| setupPython
    setupPython -->|"then"| cacheRestore
    cacheRestore -->|"if cache miss"| venvCreate
    venvCreate -->|"then"| binInstall
    binInstall -->|"then"| cacheSave
```

### test-examples Workflow Steps

```mermaid
graph TB
    subgraph "test-examples Job Steps"
        checkoutExamples["uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683"]
        installExamples["uses: ./.github/actions/install"]
        pytestExamples["run: pytest examples"]
        pylintExamples["run: pylint --errors-only examples"]
        pytypeExamples["run: pytype examples"]
        convertNotebooks["run: ./bin/convert_notebooks.sh notebooks"]
        pylintNotebooks["run: pylint --errors-only notebooks"]
        pytypeNotebooks["run: pytype --pythonpath=. notebooks"]
    end
    
    subgraph "Notebook Processing"
        convertScript["./bin/convert_notebooks.sh"]
        notebookPath["notebooks/"]
        pytestXdist["pytest-xdist parallel execution"]
    end
    
    checkoutExamples -->|"step 1"| installExamples
    installExamples -->|"step 2"| pytestExamples
    pytestExamples -->|"step 3"| pylintExamples
    pylintExamples -->|"step 4"| pytypeExamples
    pytypeExamples -->|"step 5"| convertNotebooks
    convertNotebooks -->|"step 6"| pylintNotebooks
    pylintNotebooks -->|"step 7"| pytypeNotebooks
    
    convertNotebooks -->|"uses"| convertScript
    convertScript -->|"processes"| notebookPath
    pytestExamples -->|"uses"| pytestXdist
```

### Testing Tool Configuration

| Tool | Command | Target | Configuration |
|------|---------|--------|---------------|
| `pytest` | `pytest concordia` | Core library | Runs from [.github/workflows/test-concordia.yml:49]() |
| `pytest` | `pytest examples` | Examples directory | Runs from [.github/workflows/test-examples.yml:54]() |
| `pytest` | `pytest -n auto --pyargs concordia` | Installed package | Uses `pytest-xdist` from [.github/workflows/pypi-publish.yml:82]() |
| `pylint` | `pylint --errors-only` | Code quality | Error-only mode from [.github/workflows/test-concordia.yml:52]() |
| `pytype` | `pytype concordia` | Type checking | Static analysis from [.github/workflows/test-concordia.yml:55]() |
| `pytype` | `pytype --pythonpath=.` | Notebooks | Custom path from [.github/workflows/test-examples.yml:69]() |

Sources: [.github/workflows/test-concordia.yml:1-56](), [.github/workflows/test-examples.yml:1-70](), [.github/actions/install/action.yml:1-84]()

## Package Building and Distribution

The package distribution system is implemented through the `pypi-publish` workflow with three sequential jobs:

### pypi-publish Workflow Job Chain

```mermaid
graph TB
    subgraph "build Job"
        buildCondition["if: github.event_name == 'workflow_dispatch' || startsWith(github.ref, 'refs/tags/v')"]
        pythonSetup["Show Python setup: python --version, pip list"]
        buildDist["python setup.py sdist bdist_wheel"]
        nameWorkaround["for OLD in ./dist/gdm-concordia-*; mv $OLD $NEW"]
        uploadArtifact["uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02"]
    end
    
    subgraph "test Job"
        testNeeds["needs: build"]
        testMatrix["strategy: os: [macos-13, macos-14, ubuntu-22.04, ubuntu-24.04], python-version: ['3.11', '3.12', '3.13']"]
        downloadArtifact["uses: actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093"]
        installSdist["pip install dist/*.tar.gz"]
        testSdist["pytest -n auto --pyargs concordia"]
    end
    
    subgraph "publish Job"
        publishNeeds["needs: [build, test]"]
        publishCondition["if: always() && needs.build.result == 'success' && needs.test.result != 'failure'"]
        testPypiPublish["uses: pypa/gh-action-pypi-publish@76f52bc884231f62b9a034ebfe128415bbaabdfc, repository-url: https://test.pypi.org/legacy/"]
        pypiPublish["uses: pypa/gh-action-pypi-publish@76f52bc884231f62b9a034ebfe128415bbaabdfc"]
    end
    
    buildCondition -->|"gates"| pythonSetup
    pythonSetup -->|"then"| buildDist
    buildDist -->|"then"| nameWorkaround
    nameWorkaround -->|"then"| uploadArtifact
    
    testNeeds -->|"depends on"| uploadArtifact
    testMatrix -->|"configures"| downloadArtifact
    downloadArtifact -->|"then"| installSdist
    installSdist -->|"then"| testSdist
    
    publishNeeds -->|"depends on"| testSdist
    publishCondition -->|"gates"| testPypiPublish
    testPypiPublish -->|"then"| pypiPublish
```

### Package Name Normalization Process

```mermaid
graph LR
    subgraph "setup.py Build Output"
        originalSdist["gdm-concordia-*.tar.gz"]
        originalWheel["gdm-concordia-*.whl"]
    end
    
    subgraph "Normalization Script"
        bashLoop["for OLD in ./dist/gdm-concordia-*"]
        sedCommand["NEW=$(echo $OLD | sed s/gdm-concordia/gdm_concordia)"]
        mvCommand["mv $OLD $NEW"]
    end
    
    subgraph "Normalized Output"
        normalizedSdist["gdm_concordia-*.tar.gz"]
        normalizedWheel["gdm_concordia-*.whl"]
    end
    
    originalSdist -->|"processes"| bashLoop
    originalWheel -->|"processes"| bashLoop
    bashLoop -->|"generates"| sedCommand
    sedCommand -->|"executes"| mvCommand
    mvCommand -->|"produces"| normalizedSdist
    mvCommand -->|"produces"| normalizedWheel
```

### pypi-test Validation Workflow

The `pypi-test` workflow validates published packages independently:

| Trigger | Description | Configuration |
|---------|-------------|---------------|
| `schedule: cron: "0 2 * * 1"` | Weekly Monday 2am validation | [.github/workflows/pypi-test.yml:7]() |
| `workflow_run: workflows: [pypi-publish]` | Triggered after publication | [.github/workflows/pypi-test.yml:18-22]() |
| `workflow_dispatch: inputs.version` | Manual testing with version | [.github/workflows/pypi-test.yml:24-28]() |

The workflow installs via `pip install "gdm-concordia${VERSION:+==$VERSION}"` and validates with `pytest -n auto --pyargs concordia`.

Sources: [.github/workflows/pypi-publish.yml:1-114](), [.github/workflows/pypi-test.yml:1-75]()

## Security and Quality Assurance

The security framework consists of two dedicated workflows for vulnerability detection and supply chain analysis:

### codeql-analysis Workflow Steps

```mermaid
graph TB
    subgraph "CodeQL Security Scanning"
        codeqlTriggers["on: push: [main], pull_request: [main], schedule: cron: '36 13 * * 4'"]
        checkoutRepo["uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683"]
        initCodeQL["uses: github/codeql-action/init@28deaeda66b76a05916b6923827895f2b14ab387"]
        autobuild["uses: github/codeql-action/autobuild@28deaeda66b76a05916b6923827895f2b14ab387"]
        analyzeCodeQL["uses: github/codeql-action/analyze@28deaeda66b76a05916b6923827895f2b14ab387"]
    end
    
    subgraph "CodeQL Configuration"
        languageMatrix["strategy: matrix: language: ['python']"]
        permissionsConfig["permissions: actions: read, contents: read, security-events: write"]
        runnerConfig["runs-on: ubuntu-latest"]
    end
    
    codeqlTriggers -->|"triggers"| checkoutRepo
    checkoutRepo -->|"step 1"| initCodeQL
    initCodeQL -->|"step 2"| autobuild
    autobuild -->|"step 3"| analyzeCodeQL
    
    languageMatrix -->|"configures"| initCodeQL
    permissionsConfig -->|"enables"| analyzeCodeQL
    runnerConfig -->|"hosts"| checkoutRepo
```

### scorecards-analysis Workflow Steps

```mermaid
graph TB
    subgraph "OSSF Scorecard Analysis"
        scorecardTriggers["on: branch_protection_rule, schedule: cron: '17 10 * * 0', push: [main]"]
        checkoutCode["uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683"]
        runAnalysis["uses: ossf/scorecard-action@f49aabe0b5af0936a0987cfb85d86b75731b0186"]
        uploadArtifact["uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02"]
        uploadSarif["uses: github/codeql-action/upload-sarif@28deaeda66b76a05916b6923827895f2b14ab387"]
    end
    
    subgraph "Scorecard Configuration"
        resultsFile["results_file: results.sarif"]
        resultsFormat["results_format: sarif"]
        publishResults["publish_results: true"]
        retentionDays["retention-days: 5"]
    end
    
    scorecardTriggers -->|"triggers"| checkoutCode
    checkoutCode -->|"step 1"| runAnalysis
    runAnalysis -->|"step 2"| uploadArtifact
    uploadArtifact -->|"step 3"| uploadSarif
    
    resultsFile -->|"configures"| runAnalysis
    resultsFormat -->|"configures"| runAnalysis
    publishResults -->|"enables badges"| runAnalysis
    retentionDays -->|"configures"| uploadArtifact
```

### Security Analysis Permissions and Triggers

| Workflow | Permissions | Trigger Schedule | Output Format |
|----------|-------------|------------------|---------------|
| `codeql-analysis` | `security-events: write` | `cron: '36 13 * * 4'` (Thursday 1:36 PM) | SARIF uploaded to code-scanning |
| `scorecards-analysis` | `security-events: write, id-token: write` | `cron: '17 10 * * 0'` (Sunday 10:17 AM) | SARIF + artifacts with 5-day retention |

Both workflows use `permissions: read-all` as default with specific write permissions for security events.

Sources: [.github/workflows/codeql-analysis.yml:1-63](), [.github/workflows/scorecards-analysis.yml:1-63]()

## Development Tools and Scripts

The repository includes several utility scripts for development tasks:

### Development Script Architecture

```mermaid
graph TB
    subgraph "Installation Scripts"
        InstallSh["bin/install.sh<br/>Core Installation"]
        UpdateReqs["bin/update_requirements.sh<br/>Dependency Updates"]
    end
    
    subgraph "Testing Scripts"
        TestSh["bin/test.sh<br/>Core Testing"]
        TestExamplesSh["bin/test_examples.sh<br/>Examples Testing"]
        ConvertNotebooks["bin/convert_notebooks.sh<br/>Notebook Conversion"]
    end
    
    subgraph "GitHub Actions"
        InstallAction[".github/actions/install<br/>Reusable Installation"]
        CacheKey["Cache Key Generation<br/>OS + Python + Requirements Hash"]
        VenvManagement["Virtual Environment<br/>Creation and Caching"]
    end
    
    InstallSh -->|"pip install --no-deps<br/>--require-hashes"| UpdateReqs
    TestSh -->|"pytest + pylint + pytype"| TestExamplesSh
    TestExamplesSh -->|"includes"| ConvertNotebooks
    
    InstallAction -->|"uses"| InstallSh
    InstallAction -->|"manages"| CacheKey
    CacheKey -->|"enables"| VenvManagement
```

### Script Functions

Each development script serves specific purposes:

- **Installation**: [bin/install.sh:21-27]() handles dependency installation with hash verification
- **Testing**: [bin/test.sh:22-35]() runs the complete test suite with failure tracking
- **Requirements Update**: [bin/update_requirements.sh:21-22]() updates dependencies using `pip-compile`
- **GitHub Actions Cache**: [.github/actions/install/action.yml:24-37]() generates cache keys based on OS, Python version, and requirements hash

Sources: [bin/install.sh:1-32](), [bin/test.sh:1-42](), [bin/test_examples.sh:1-57](), [bin/update_requirements.sh:1-23](), [.github/actions/install/action.yml:1-84]()

---

