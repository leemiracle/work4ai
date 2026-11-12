<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/optimum-intel · page 7 Development and Contributing · fetched 2026-10-26 -->

# Development and Contributing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/build_documentation.yml](.github/workflows/build_documentation.yml)
- [.github/workflows/build_pr_documentation.yml](.github/workflows/build_pr_documentation.yml)
- [.github/workflows/test_openvino.yml](.github/workflows/test_openvino.yml)
- [.github/workflows/test_openvino_slow.yml](.github/workflows/test_openvino_slow.yml)
- [Makefile](Makefile)

</details>



This page provides guidance for developers who want to contribute to the `optimum-intel` codebase. It covers setting up a development environment, code quality standards, running tests, building documentation, and the contribution workflow. 

For detailed information on specific topics, see:
- Package organization and module hierarchy: [Package Structure](#7.1)
- Test infrastructure and CI workflows: [Testing Infrastructure](#7.2)
- Documentation versioning and release management: [Documentation and Release Management](#7.3)

**Scope**: This page focuses on the development workflow, tooling, and contribution process. It provides an overview of testing and documentation systems, with links to detailed coverage in child pages.

---

## Development Environment Setup

To contribute to `optimum-intel`, you need to set up a development environment with the appropriate dependencies.

### Prerequisites

1. **Python 3.9+**: The project supports modern Python versions.
2. **Git**: For cloning the repository and managing changes.
3. **Virtual environment** (recommended): Use `venv`, `conda`, or `uv`.

### Installation for Development

The project uses `uv` for fast dependency management in CI workflows [.github/workflows/test_openvino.yml:56-57]().

```bash
# Clone the repository
git clone https://github.com/huggingface/optimum-intel.git
cd optimum-intel

# Install in editable mode with quality tools
pip install -e .[quality]

# Install backend-specific dependencies (optional)
pip install -e .[openvino,nncf]  # For OpenVINO and Quantization development
pip install -e .[ipex]           # For IPEX development
```

### Development Dependencies

The `[quality]` extra installs code quality tools:
- **black**: Code formatter [Makefile:24-28]()
- **ruff**: Fast Python linter [Makefile:25-29]()
- **pytest**: Testing framework [Makefile:33]()

For documentation development, install additional dependencies:
```bash
pip install git+https://github.com/huggingface/doc-builder
pip install .[quality] diffusers accelerate datasets
```

**Sources**: [Makefile:1-67](), [.github/workflows/test_openvino.yml:56-57](), [.github/workflows/build_pr_documentation.yml:38-42]()

---

## Code Quality and Style

The project uses automated tools to maintain code quality and consistent style across the codebase.

### Diagram: Code Quality Workflow

```mermaid
flowchart LR
    subgraph "Developer_Workflow"
        ["Edit_Code"] --> ["make_style_check"]
        ["make_style_check"] --> ["make_style"]
        ["make_style"] --> ["Git_Commit"]
    end
    
    subgraph "Style_Tools"
        ["black_--check_."]
        ["ruff_check_."]
        ["black_."]
        ["ruff_check_.--fix"]
    end
    
    subgraph "CI_Validation"
        ["Pull_Request"] --> ["Quality_Checks_Workflow"]
        ["Quality_Checks_Workflow"] --> ["Merge"]
    end
    
    ["make_style_check"] -.-> ["black_--check_."]
    ["make_style_check"] -.-> ["ruff_check_."]
    ["make_style"] -.-> ["black_."]
    ["make_style"] -.-> ["ruff_check_.--fix"]
```

### Style Commands

The [Makefile:1-67]() defines two primary style-related targets:

#### Check Style (Non-Destructive)
```bash
make style_check
```
This runs:
- `black --check .` [Makefile:24]()
- `ruff check .` [Makefile:25]()

#### Fix Style (Automatic Formatting)
```bash
make style
```
This runs:
- `black .` [Makefile:28]()
- `ruff check . --fix` [Makefile:29]()

**Sources**: [Makefile:22-30]()

---

## Running Tests

The project includes comprehensive test suites for each backend. Run tests locally before submitting pull requests.

### Basic Test Command

```bash
make test
```

This executes [Makefile:32-33](), which runs:
```bash
python -m pytest tests
```

### Test Organization and CI Triggers

Tests are organized by backend and functionality. CI workflows use matrix strategies to test across different `transformers` versions and test patterns [.github/workflows/test_openvino.yml:28-41]().

| Directory | Backend | CI Workflow |
|-----------|---------|-------------|
| `tests/openvino/` | OpenVINO | `OpenVINO - Test` [.github/workflows/test_openvino.yml:1]() |
| `tests/ipex/` | IPEX | `IPEX - Test` |
| `tests/openvino/` (slow) | OpenVINO | `OpenVINO - Slow Test` [.github/workflows/test_openvino_slow.yml:1]() |

### CI Matrix Testing

The OpenVINO CI runs a matrix of test patterns including:
- `*genai*` [.github/workflows/test_openvino.yml:33]()
- `*export*` [.github/workflows/test_openvino.yml:34]()
- `*decoder*` [.github/workflows/test_openvino.yml:35]()
- `*quantization*` [.github/workflows/test_openvino.yml:39]()

For details on test categorization and markers (like `run_slow`), see [Testing Infrastructure](#7.2).

**Sources**: [Makefile:31-33](), [.github/workflows/test_openvino.yml:28-41](), [.github/workflows/test_openvino_slow.yml:92-94]()

---

## Building Documentation

The project uses [doc-builder](https://github.com/huggingface/doc-builder) to generate documentation.

### Diagram: Documentation Build System

```mermaid
flowchart TB
    subgraph "Source_Files"
        ["docs/source/*.md"]
        ["optimum/intel/**/*.py"]
        ["optimum/intel/version.py"]
    end
    
    subgraph "Build_Commands"
        ["make_doc"]
        ["doc-builder_build"]
    end
    
    subgraph "Version_Logic"
        ["grep_VERSION"]
        ["VERSION=main"]
        ["VERSION=vX.Y.Z"]
    end
    
    subgraph "Deployment"
        ["doc-build-artifact"]
        ["hf-doc-build/doc-build"]
    end
    
    ["optimum/intel/version.py"] --> ["grep_VERSION"]
    ["grep_VERSION"] --> ["VERSION=main"]
    ["grep_VERSION"] --> ["VERSION=vX.Y.Z"]
    
    ["docs/source/*.md"] --> ["make_doc"]
    ["optimum/intel/**/*.py"] --> ["make_doc"]
    ["VERSION=main"] --> ["make_doc"]
    ["VERSION=vX.Y.Z"] --> ["make_doc"]
    
    ["make_doc"] --> ["doc-builder_build"]
    ["doc-builder_build"] --> ["doc-build-artifact"]
    ["doc-builder_build"] --> ["hf-doc-build/doc-build"]
```

### Local Documentation Build

To build documentation locally:

```bash
make doc BUILD_DIR=./doc-build VERSION=local
```

This command [Makefile:48-57]() uses `doc-builder` to process markdown files from `docs/source/` and docstrings from the `optimum.intel` package.

### CI Documentation Workflows

- **PR Preview**: `Build PR documentation` generates a preview for every pull request [.github/workflows/build_pr_documentation.yml:1-56]().
- **Official Build**: `Build documentation` pushes to the official Hugging Face doc repository [.github/workflows/build_documentation.yml:63-67]().

See [Documentation and Release Management](#7.3) for details on how versions are calculated from `optimum/intel/version.py` [.github/workflows/build_documentation.yml:36-46]().

**Sources**: [Makefile:48-58](), [.github/workflows/build_pr_documentation.yml:1-56](), [.github/workflows/build_documentation.yml:1-67]()

---

## Contribution Workflow

### Diagram: Pull Request Lifecycle

```mermaid
flowchart TD
    ["Create_Branch"] --> ["Write_Code_&_Tests"]
    ["Write_Code_&_Tests"] --> ["make_style"]
    ["make_style"] --> ["pytest_tests/openvino/..."]
    ["pytest_tests/openvino/..."] --> ["Push_to_GitHub"]
    ["Push_to_GitHub"] --> ["Open_Pull_Request"]
    
    subgraph "GitHub_Actions_CI"
        ["Quality_Checks"]
        ["OpenVINO_-_Test"]
        ["Build_PR_documentation"]
    end
    
    ["Open_Pull_Request"] --> ["Quality_Checks"]
    ["Open_Pull_Request"] --> ["OpenVINO_-_Test"]
    ["Open_Pull_Request"] --> ["Build_PR_documentation"]
    
    ["Quality_Checks"] & ["OpenVINO_-_Test"] & ["Build_PR_documentation"] --> ["Maintainer_Review"]
    ["Maintainer_Review"] --> ["Merge_to_main"]
```

1. **Fork and Clone**: Fork the repository and clone it locally.
2. **Branch**: Create a feature branch from `main`.
3. **Develop**: Implement changes and add tests.
4. **Validate**: Run `make style` [Makefile:27]() and `pytest` [Makefile:33]().
5. **Submit**: Push your branch and open a Pull Request.

**Sources**: [Makefile:20-33](), [.github/workflows/test_openvino.yml:9-11]()

---

## Release Process

The release process involves building distribution packages and uploading them to PyPI.

### Build and Upload

The [Makefile:36-46]() provides targets for release management:
- `make build_dist`: Cleans previous builds and runs `python -m build` [Makefile:40-43]().
- `make pypi_upload`: Uploads the generated artifacts to PyPI using `twine` [Makefile:45-46]().

### Clean Artifacts

Use `make clean` [Makefile:59-67]() to remove:
- `build/` and `dist/` directories.
- `.pytest_cache`, `.ruff_cache`, and `.mypy_cache`.
- `__pycache__` files.

**Sources**: [Makefile:36-67]()

---

