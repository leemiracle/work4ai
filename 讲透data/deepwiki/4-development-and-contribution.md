<!-- source: DeepWiki mcp.deepwiki.com · repo pytorch/data · page 4 Development and Contribution · fetched 2026-10-21 -->

# Development and Contribution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/lint.yml](.github/workflows/lint.yml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [docs/Makefile](docs/Makefile)
- [docs/source/conf.py](docs/source/conf.py)
- [mypy.ini](mypy.ini)
- [pyproject.toml](pyproject.toml)

</details>



This page provides a comprehensive guide for developers interested in contributing to the TorchData repository. It covers the development environment setup, contribution workflow, code quality standards, testing procedures, and documentation system. For information about the build and release process, see [Build and Release Process](#4.1).

## Setting Up Development Environment

To begin contributing to TorchData, you need to set up a proper development environment.

### Installing Prerequisites

```bash
# Install PyTorch Nightly
conda install pytorch -c pytorch-nightly
# or with pip
pip install --pre torch --index-url https://download.pytorch.org/whl/nightly/cpu

# Clone and install TorchData in development mode
git clone https://github.com/pytorch/data.git
cd data
pip install -e .
pip install -r test/requirements.txt
```

Sources: [CONTRIBUTING.md:50-66]()

## Contribution Workflow

The following diagram illustrates the typical workflow for contributing to TorchData:

```mermaid
flowchart TD
    A["Fork Repository"] --> B["Clone Locally"]
    B --> C["Create Branch"]
    C --> D["Make Changes"]
    D --> E["Run Tests & Linting"]
    E --> F["Fix Issues"]
    F -->|All Passing| G["Submit PR"]
    F -->|Issues Remain| D
    G --> H["Code Review"]
    H --> I["Address Feedback"]
    I -->|Changes Needed| H
    I -->|Approved| J["PR Merged"]
    
    subgraph "One-Time Setup"
        K["Complete CLA"]
        L["Install pre-commit hooks"]
    end
    
    K -.-> G
    L -.-> D
```

Sources: [CONTRIBUTING.md:38-46](), [CONTRIBUTING.md:69-78]()

### Pull Request Guidelines

When submitting a pull request:

1. Fork the repo and create your branch from `main`
2. Add tests for any new functionality
3. Update documentation for API changes
4. Ensure all tests pass
5. Complete the Contributor License Agreement (CLA) if you haven't already

Contributors must sign the CLA to have their contributions accepted: https://code.facebook.com/cla

Sources: [CONTRIBUTING.md:38-46](), [CONTRIBUTING.md:141-146]()

## Code Quality Standards

TorchData maintains high code quality standards through automated tools and processes.

### Code Formatting

TorchData uses `pre-commit` hooks to enforce consistent code formatting:

```bash
# Install pre-commit
conda install -c conda-forge pre-commit
# or
pip install pre-commit

# Install the hooks
cd data
pre-commit install --install-hooks
```

Sources: [CONTRIBUTING.md:69-78]()

### Type Checking with MyPy

TorchData uses MyPy for static type checking:

```bash
# Run MyPy type checking
mypy --config-file=mypy.ini
```

The MyPy configuration defines strict type checking rules and handles third-party dependencies:

| Setting | Value | Purpose |
|---------|-------|---------|
| `check_untyped_defs` | True | Checks the body of functions without type annotations |
| `show_error_codes` | True | Shows error codes for easier debugging |
| `exclude` | examples, test, packaging | Excludes specific directories from checking |
| `python_version` | 3.9 | Sets Python version for type checking |

Sources: [CONTRIBUTING.md:82-86](), [mypy.ini:1-67]()

## Development Tools and Processes

The following diagram shows the relationship between various development tools used in TorchData:

```mermaid
graph TD
    subgraph "Code Quality"
        A["pre-commit hooks"] --> B["Black"]
        A --> C["usort"]
        A --> D["Other Linters"]
        E["MyPy"] --> F["Type Validation"]
    end
    
    subgraph "Testing"
        G["pytest"] --> H["Unit Tests"]
        H --> I["Node Tests"]
        I --> J["State Management Tests"]
    end
    
    subgraph "Documentation"
        K["Sphinx"] --> L["API Docs"]
        K --> M["Usage Examples"]
        N["Doc Completeness Check"] --> K
    end
    
    O["GitHub Actions"] --> A
    O --> E
    O --> G
    O --> N
```

Sources: [.github/workflows/lint.yml:1-89](), [mypy.ini:1-67](), [CONTRIBUTING.md:82-90]()

### Running Tests

To run unit tests locally:

```bash
pytest --durations=0 --no-header -v test/nodes/
```

Sources: [CONTRIBUTING.md:89-90]()

## Adding New Components

### Guidelines for Adding New Nodes

When adding a new Node to TorchData, follow this checklist:

1. **Functionality**: Ensure your Node subclasses `BaseNode` and implements required methods:
   - `.iterator(self, initial_state: Optional[Dict[str, Any]])` 
   - `.get_state(self) -> Dict[str, Any]`

2. **Type Hints**: Include type annotations for all public functions and methods

3. **Testing**: Add unit tests to verify functionality and state management
   - Use `test.nodes.utils.run_test_save_load_state` for basic state testing

4. **Documentation**: Include docstrings and usage examples

5. **Import**: Add the Node to the appropriate `__init__.py` file

Sources: [CONTRIBUTING.md:92-140]()

### Node Implementation Rules

The following diagram illustrates the state management pattern for TorchData Nodes:

```mermaid
sequenceDiagram
    participant C as "Client Code"
    participant N as "Node"
    participant P as "Parent Node"
    
    C->>N: create()
    C->>N: iterator(initial_state)
    N->>P: load_state_dict(initial_state["parent"])
    P-->>N: iterator prepared
    N-->>C: yield items
    
    C->>N: state_dict()
    N->>N: get_state()
    N->>P: state_dict()
    P-->>N: parent state
    N-->>C: combined state
```

Key state management assumptions:
- State is managed solely by the BaseNode, not through any iterators returned from them
- `state_dict()` returns the state of the most recently requested iterator
- `load_state_dict()` will set the state for the next iterator

Sources: [CONTRIBUTING.md:96-101](), [CONTRIBUTING.md:112-131]()

## Documentation System

TorchData uses Sphinx for documentation generation. The documentation build process is as follows:

```mermaid
flowchart TD
    A["Source Files (.py)"] --> B["Docstrings"]
    C["Documentation Source (.rst)"] --> D["Sphinx"]
    B --> D
    D --> E["HTML Documentation"]
    D --> F["Other Formats"]
    
    subgraph "CI Validation"
        G["Documentation Completeness Check"]
        H["Documentation Build Check"]
    end
    
    G --> D
    D --> H
```

Sources: [docs/source/conf.py:1-119](), [docs/Makefile:1-44](), [.github/workflows/lint.yml:77-88]()

### Building Documentation Locally

To build the documentation locally:

```bash
cd docs
make html       # Full build with examples
# or
make html-noplot  # Faster build without running examples
```

Sources: [docs/Makefile:26-29]()

### Documentation Completeness Check

TorchData CI includes a check that verifies all public APIs are properly documented. This check runs automatically on pull requests.

```bash
python ./.github/scripts/check_complete_doc.py
```

Sources: [.github/workflows/lint.yml:77-88]()

## CI/CD Workflows

The following diagram shows the Continuous Integration workflow for TorchData:

```mermaid
flowchart TD
    A["Pull Request or Push"] --> B["GitHub Actions"]
    
    B --> C["Lint Checks"]
    B --> D["MyPy Type Checking"]
    B --> E["Documentation Checks"]
    
    C --> C1["pre-commit"]
    C --> C2["Style Checks"]
    
    D --> D1["Type Validation"]
    
    E --> E1["Completeness Check"]
    
    subgraph "Validation Results"
        F["All Checks Pass"]
        G["Fixes Required"]
    end
    
    C --> F
    C --> G
    D --> F
    D --> G
    E --> F
    E --> G
    
    F --> H["Ready for Review"]
    G --> I["Fix Issues"]
    I --> B
```

Sources: [.github/workflows/lint.yml:1-89]()

## Common Issues and Solutions

Here are some common issues contributors might encounter and their solutions:

| Issue | Solution |
|-------|----------|
| Pre-commit hooks failing | Run `pre-commit run --all-files` to see the issues and fix them |
| MyPy errors | Check error codes and fix type annotations accordingly |
| Test failures | Run specific failing tests with more verbosity to debug |
| Documentation build errors | Check Sphinx warnings and fix documentation formatting |
| Missing CLA | Visit the CLA link and complete the agreement |

Sources: [CONTRIBUTING.md:69-86](), [.github/workflows/lint.yml:25-29]()

---

