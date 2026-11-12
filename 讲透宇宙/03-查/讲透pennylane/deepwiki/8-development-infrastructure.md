<!-- source: DeepWiki mcp.deepwiki.com · repo PennyLaneAI/pennylane · page 8 Development Infrastructure · fetched 2026-10-21 -->

# Development Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/create-release.yml](.github/workflows/create-release.yml)
- [.github/workflows/docs.yml](.github/workflows/docs.yml)
- [.github/workflows/format.yml](.github/workflows/format.yml)
- [.github/workflows/interface-unit-tests.yml](.github/workflows/interface-unit-tests.yml)
- [.github/workflows/rc_sync.yml](.github/workflows/rc_sync.yml)
- [.github/workflows/rtd-check.yml](.github/workflows/rtd-check.yml)
- [.github/workflows/tests-gpu.yml](.github/workflows/tests-gpu.yml)
- [.github/workflows/tests.yml](.github/workflows/tests.yml)
- [.github/workflows/unit-test.yml](.github/workflows/unit-test.yml)
- [.github/workflows/upload-nightly-rc-release.yml](.github/workflows/upload-nightly-rc-release.yml)
- [.github/workflows/upload-nightly-release.yml](.github/workflows/upload-nightly-release.yml)
- [.github/workflows/upload.yml](.github/workflows/upload.yml)
- [.pylintrc](.pylintrc)
- [.readthedocs.yml](.readthedocs.yml)
- [doc/code/qml.rst](doc/code/qml.rst)
- [doc/development/guide/documentation.rst](doc/development/guide/documentation.rst)
- [doc/development/guide/installation.rst](doc/development/guide/installation.rst)
- [doc/introduction/compiling_workflows.rst](doc/introduction/compiling_workflows.rst)
- [doc/requirements.txt](doc/requirements.txt)
- [pennylane/compiler/__init__.py](pennylane/compiler/__init__.py)
- [pennylane/compiler/compiler.py](pennylane/compiler/compiler.py)
- [pennylane/numpy/random.py](pennylane/numpy/random.py)
- [pyproject.toml](pyproject.toml)
- [setup.py](setup.py)
- [tests/.pylintrc](tests/.pylintrc)

</details>



This page documents the development infrastructure that supports PennyLane's development workflow, including package organization, build configuration, testing frameworks, continuous integration, and release processes. This infrastructure enables developers to contribute effectively to PennyLane while maintaining code quality and ensuring compatibility across multiple interfaces and quantum computing backends.

## Package Structure and Build System

PennyLane uses a modern Python packaging approach with setuptools and multiple requirements files to manage dependencies for different use cases.

### Build Configuration

**Setup Configuration**
The build system is configured through `setup.py`, which provides a minimal setup call that delegates to configuration files.

```mermaid
graph TD
    setup_py["setup.py"] --> setup_call["setup()"]
    setup_call --> pyproject_toml["pyproject.toml"]
    setup_call --> setup_cfg["setup.cfg"]
    
    subgraph "Requirements Files"
        req_core["requirements.txt"]
        req_ci["requirements-ci.txt"] 
        req_dev["requirements-dev.txt"]
        req_doc["doc/requirements.txt"]
    end
    
    req_core --> core_deps["Core Dependencies"]
    req_ci --> ci_deps["CI Dependencies"]
    req_dev --> dev_deps["Development Tools"]
    req_doc --> doc_deps["Documentation Tools"]
```

**Requirements Management**
PennyLane maintains separate requirements files for different environments and use cases:

| File | Purpose | Key Dependencies |
|------|---------|------------------|
| `requirements.txt` | Core runtime dependencies | `numpy`, `scipy`, `autograd`, `autoray`, `rustworkx` |
| `requirements-ci.txt` | CI environment | Subset of core dependencies for testing |
| `requirements-dev.txt` | Development tools | `pytest`, `pylint`, `black`, `pre-commit` |
| `doc/requirements.txt` | Documentation building | `sphinx`, `jax`, `torch`, `tensorflow` |

### Core Dependencies

**Runtime Dependencies**
The core dependencies defined in `requirements.txt` include:

- **Mathematical Libraries**: `numpy~=1.23`, `scipy~=1.8`
- **Graph Libraries**: `networkx~=2.8`, `rustworkx~=0.15.1` 
- **Autodifferentiation**: `autograd~=1.4`, `autoray>=0.6.11`
- **Utilities**: `tomlkit~=0.13`, `appdirs~=1.4`, `cachetools~=5.3.0`
- **Visualization**: `matplotlib~=3.5`
- **Optimization**: `cvxpy~=1.2`, `cvxopt~=1.3.0`

**Interface Dependencies**
Optional interface dependencies are documented but not included in core requirements:

- **JAX Interface**: `jax==0.6.0`, `jaxlib==0.6.0`
- **PyTorch Interface**: `torch==2.5.1`
- **TensorFlow Interface**: `tensorflow==2.19`

### Development Installation

**Editable Installation**
For development work, install PennyLane in editable mode:

```bash
git clone https://github.com/PennyLaneAI/pennylane
cd pennylane
pip install -e .
```

**Development Dependencies**
Install development tools:

```bash
pip install -r requirements-dev.txt
```

This includes testing frameworks (`pytest`, `pytest-cov`), code quality tools (`black`, `pylint`, `isort`), and development utilities (`pre-commit`, `build`).

Sources:
[setup.py:1-4]()
[requirements.txt:1-19]()
[requirements-ci.txt:1-18]()
[requirements-dev.txt:1-18]()
[doc/requirements.txt:1-41]()
[doc/development/guide/installation.rst:56-86]()

## Testing and CI/CD

PennyLane maintains comprehensive testing infrastructure using `pytest` with specialized markers, fixtures, and continuous integration workflows to ensure code quality across multiple interfaces and quantum computing backends.

### Testing Framework

**Test Organization and Markers**
The testing system uses `pytest` markers to categorize and filter tests:

```mermaid
graph TD
    pytest["pytest"] --> core_tests["@pytest.mark.core"]
    pytest --> interface_tests["Interface Tests"]
    pytest --> specialty_tests["Specialty Tests"]
    
    interface_tests --> autograd["@pytest.mark.autograd"]
    interface_tests --> torch_tests["@pytest.mark.torch"] 
    interface_tests --> tf_tests["@pytest.mark.tf"]
    interface_tests --> jax_tests["@pytest.mark.jax"]
    interface_tests --> all_interfaces["@pytest.mark.all_interfaces"]
    
    specialty_tests --> qchem["@pytest.mark.qchem"]
    specialty_tests --> qcut["@pytest.mark.qcut"]
    specialty_tests --> slow["@pytest.mark.slow"]
    
    subgraph "Test Execution"
        test_cmd["python -m pytest"]
        marker_filter["python -m pytest -m torch"]
        exclude_slow["python -m pytest -m 'not slow'"]
    end
```

**Test Structure and Requirements**
Tests require specific dependencies based on their markers:

| Marker | Dependencies | Purpose |
|--------|-------------|---------|
| `core` | Core PennyLane only | Basic functionality |
| `autograd` | `autograd` | Autograd interface tests |
| `torch` | `torch` | PyTorch interface tests |
| `tf` | `tensorflow` | TensorFlow interface tests |
| `jax` | `jax`, `jaxlib` | JAX interface tests |
| `all_interfaces` | All interfaces | Cross-interface compatibility |

### Test Configuration

**pytest Configuration**
Tests are automatically marked based on imports through `conftest.py` configuration. Core tests (those not importing interfaces) are automatically marked as `@pytest.mark.core`.

**Specialized Testing Tools**
The testing framework includes several pytest extensions:

- `pytest-cov`: Test coverage measurement
- `pytest-mock`: Mock object support  
- `pytest-xdist`: Parallel test execution
- `pytest-benchmark`: Performance benchmarking
- `flaky`: Non-deterministic test handling
- `pytest-forked`: Process isolation
- `pytest-rng`: Random number generation control

### Linting and Code Quality

**pylint Configuration**
Code quality is enforced through `pylint` with separate configurations:

```mermaid
graph TD
    pylintrc[".pylintrc"] --> main_config["Main Codebase"]
    tests_pylintrc["tests/.pylintrc"] --> test_config["Test Code"]
    
    main_config --> main_rules["Production Code Rules"]
    test_config --> test_rules["Relaxed Test Rules"]
    
    subgraph "Ignored Modules"
        numpy_mods["numpy, scipy, autograd"]
        ml_mods["torch, tensorflow, jax"]  
        other_mods["networkx, rustworkx"]
    end
    
    main_config --> numpy_mods
    main_config --> ml_mods
    main_config --> other_mods
```

**Disabled Checks**
Both configurations disable certain checks:
- `line-too-long`: Handled by Black formatter
- `cyclic-import`: Temporarily disabled due to existing cycles
- `import-error`: Disabled for optional dependencies

### Continuous Integration

**Matrix Testing Strategy**
CI/CD employs matrix testing across Python versions and test categories:

```mermaid
flowchart TD
    pr_trigger["Pull Request"] --> workflow_dispatch["CI Workflow"]
    
    workflow_dispatch --> format_check["Code Formatting"]
    workflow_dispatch --> test_matrix["Test Matrix"]
    workflow_dispatch --> doc_build["Documentation Build"]
    
    format_check --> black_check["black --check"]
    format_check --> isort_check["isort --check"] 
    format_check --> pylint_check["pylint"]
    
    test_matrix --> python_versions["Python 3.10, 3.11, 3.12"]
    test_matrix --> test_types["Core, Interface, Device Tests"]
    
    subgraph "Test Execution"
        core_run["pytest core tests"]
        interface_run["pytest interface tests"]
        specialty_run["pytest qchem, qcut tests"]
    end
    
    test_types --> core_run
    test_types --> interface_run  
    test_types --> specialty_run
```

**Performance Optimizations**
CI pipeline includes several optimizations:
- **Test Splitting**: Uses `pytest-split` for balanced test distribution
- **Parallel Execution**: Leverages `pytest-xdist` for concurrent test runs
- **Dependency Caching**: Caches pip dependencies between runs
- **Selective Testing**: Runs only relevant tests based on changed files

Sources:
[doc/development/guide/tests.rst:1-254]()
[requirements-dev.txt:1-18]()
[.pylintrc:1-48]()
[tests/.pylintrc:1-64]()

## CI/CD Pipeline

PennyLane uses GitHub Actions for continuous integration and deployment, with a comprehensive set of workflows for testing, linting, documentation building, and releases.

### CI/CD Workflow

```mermaid
flowchart TD
    subgraph "Pull Request"
        A["PR Created/Updated"] --> B["Workflow Triggered"]
        B --> C1["Formatting Check"]
        B --> C2["Documentation Check"]
        B --> C3["Unit Tests"]
        B --> C4["GPU Tests (if labeled)"]
        
        C1 --> D1["Black"]
        C1 --> D2["Pylint"]
        C1 --> D3["isort"]
        
        C3 --> E1["Core Tests"]
        C3 --> E2["Interface Tests"]
        C3 --> E3["Device Tests"]
        C3 --> E4["Specialty Tests"]
        
        E1 & E2 & E3 & E4 --> F["Upload Coverage"]
    end
    
    subgraph "Merge to Master"
        G["Merge to Master"] --> H["Release Process"]
        H --> I["Update Version"]
        I --> J["Create Release"]
        J --> K["Upload to PyPI"]
    end
```

### Matrix Testing Strategy

PennyLane's CI pipeline uses a matrix strategy to run tests across different Python versions and interfaces:

```mermaid
graph TD
    A["Matrix Configuration"] --> B["Python Versions"]
    A --> C["Test Types"]
    
    B --> B1["Python 3.10"]
    B --> B2["Python 3.11"]
    B --> B3["Python 3.12"]
    
    C --> C1["Core Tests"]
    C --> C2["Interface Tests"]
    C --> C3["Device Tests"]
    
    C2 --> D1["Autograd"]
    C2 --> D2["PyTorch"]
    C2 --> D3["TensorFlow"]
    C2 --> D4["JAX"]
    C2 --> D5["All Interfaces"]
    
    subgraph "Optimization"
        E["Parallelization"]
        F["Test Splitting"]
        G["Duration-based Balancing"]
    end
    
    C1 & C2 & C3 --> E
    C1 & C3 --> F
    F --> G
```

The CI system uses cached dependencies and optimized test splitting to reduce test execution time.

### Workflow Implementation

The workflows are defined in YAML files in the `.github/workflows` directory:

- `tests.yml`: Main test workflow that calls `interface-unit-tests.yml`
- `interface-unit-tests.yml`: Reusable workflow with matrix testing for different interfaces
- `unit-test.yml`: Reusable workflow for running a specific test configuration
- `format.yml`: Code formatting and linting checks
- `docs.yml`: Documentation building and checks
- `tests-gpu.yml`: GPU-specific tests

The CI system also collects test results and coverage data, which are uploaded as artifacts and to Codecov.

Sources:
[.github/workflows/tests.yml:1-803]()
[.github/workflows/interface-unit-tests.yml:1-803]()
[.github/workflows/unit-test.yml:1-246]()
[.github/workflows/tests-gpu.yml:1-125]()
[.github/workflows/format.yml:1-59]()
[.github/workflows/docs.yml:1-87]()

## Release Management

PennyLane follows a structured release process for both regular releases and release candidates.

### Version Numbering

PennyLane uses semantic versioning (major.minor.patch) with optional development markers:

```
0.42.0-dev12  # Development release
0.42.0        # Stable release
```

Version numbers are maintained in `pennylane/_version.py`.

### Release Process

```mermaid
flowchart TD
    A["Development Phase"] --> B["Feature Freeze"]
    B --> C["Create Release Candidate"]
    C --> D["Testing and Bug Fixes"]
    D --> E["Final Release Preparation"]
    E --> F["Release to PyPI"]
    F --> G["Update Documentation"]
    G --> H["Start Next Development Cycle"]
    
    subgraph "RC Maintenance"
        I["Update RC Branch"]
        J["Sync Changes to Master"]
    end
    
    D --> I
    I --> D
    I --> J
    J --> A
```

### Release Synchronization

The `rc_sync.yml` workflow automatically synchronizes changes from release candidate branches to the master branch during feature freeze periods:

1. Checks for an RC branch matching the current development version
2. Creates a temporary branch based on the RC branch
3. Excludes version-specific files that need to remain different
4. Opens a pull request to merge changes back to master

### Release Notes

Release notes are maintained in Markdown files in the `doc/releases` directory:

- `changelog-dev.md`: Development version changelog
- `changelog-X.Y.Z.md`: Stable release changelogs

The release notes are assembled in `doc/development/release_notes.md`.

### Publishing Releases

When a release is published on GitHub, the `upload.yml` workflow is triggered, which:

1. Runs all tests to ensure the release is stable
2. Builds a distribution wheel
3. Uploads the package to PyPI

Sources:
[pennylane/_version.py:15-19]()
[.github/workflows/rc_sync.yml:1-75]()
[.github/workflows/upload.yml:1-49]()
[doc/development/release_notes.md:1-106]()
[doc/releases/changelog-0.40.0.md:1-82]()

## Code Quality Tools

PennyLane employs several tools to ensure code quality throughout the development process.

### Code Formatting

```mermaid
flowchart LR
    A["Code"] --> B["Code Quality Checks"]
    B --> C["Black"]
    B --> D["isort"]
    B --> E["Pylint"]
    
    C --> F["Python Format"]
    D --> G["Import Sorting"]
    E --> H["Linting"]
    
    F & G & H --> I["Formatted Code"]
```

The code quality tools are run automatically on pull requests:

- **Black**: Formats Python code with line length of 100 characters
- **isort**: Sorts imports with Black-compatible profile
- **Pylint**: Checks for coding standard violations and potential errors

Configuration for Pylint is defined in `.pylintrc` and `tests/.pylintrc`.

### Automated Checks

The `format.yml` workflow runs these tools automatically on pull requests:

```yaml
- name: Run Black
  run: |
    black -t py310 -t py311 -t py312 -l 100 pennylane/ --check
    black -t py310 -t py311 -t py312 -l 100 tests/ --check

- name: Run isort
  run: |
    isort --py 312 --profile black -l 100 -o autoray -p ./pennylane --skip __init__.py --filter-files ./pennylane --check
    isort --py 312 --profile black -l 100 -o autoray -p ./pennylane --skip __init__.py --filter-files ./tests --check

- name: Run Pylint
  run: pylint --rcfile .pylintrc $(find pennylane -name "*.py")
```

Sources:
[.github/workflows/format.yml:1-59]()
[.pylintrc:1-39]()
[tests/.pylintrc:1-18]()

## Documentation Infrastructure

PennyLane maintains comprehensive documentation built using Sphinx.

### Documentation Structure

```mermaid
graph TD
    A["Documentation"] --> B["API Reference"]
    A --> C["Guides"]
    A --> D["Development"]
    A --> E["Release Notes"]
    
    B --> F["Core Modules"]
    B --> G["Operations & Templates"]
    B --> H["Devices & Interfaces"]
    B --> I["Utilities"]
    
    D --> J["Contributing Guidelines"]
    D --> K["Installation Guide"]
    
    E --> L["Changelog Files"]
```

### Documentation Building

The documentation is built using Sphinx with several extensions:
- sphinx-automodapi for automatic API documentation
- sphinx-copybutton for copy buttons on code blocks
- sphinxcontrib-bibtex for bibliography support

The build process is defined in the `docs.yml` workflow:

```yaml
- uses: PennyLaneAI/sphinx-action@master
  with:
    docs-folder: "doc/"
    pre-build-command: >
        apt install -y graphviz
        && pip3 install -r doc/requirements.txt
        && pip3 install .
        && pip3 install openfermionpyscf
        && pip3 install aiohttp fsspec h5py
    build-command: "sphinx-build -b html . _build -W --keep-going"
```

### Release Notes Management

Release notes are organized by version in separate Markdown files and included in the documentation through `mdinclude` directives in `doc/development/release_notes.md`:

```
.. mdinclude:: ../releases/changelog-dev.md
.. mdinclude:: ../releases/changelog-0.41.0.md
...
```

Each changelog file follows a consistent format with sections for new features, improvements, breaking changes, and bug fixes.

Sources:
[.github/workflows/docs.yml:1-87]()
[doc/requirements.txt:1-41]()
[doc/development/release_notes.md:1-106]()
[doc/code/qml_wires.rst:1-14]()

---

