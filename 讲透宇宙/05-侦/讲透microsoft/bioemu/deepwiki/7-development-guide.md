<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/bioemu · page 7 Development Guide · fetched 2026-10-26 -->

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.github/workflows/codeql.yml](.github/workflows/codeql.yml)
- [pyproject.toml](pyproject.toml)

</details>



This guide provides information for developers who want to contribute to BioEmu. It covers development environment setup, coding standards, testing procedures, and the release workflow. For information about using BioEmu as an end-user, see [Core Functionality](#3).

## Development Environment Setup

Setting up a development environment for BioEmu requires a few steps to ensure all dependencies are properly installed and configured.

```mermaid
flowchart TD
    A["Clone Repository"] --> B["Set Up Python Environment"]
    B --> C["Install Dev Dependencies"]
    C --> D["Configure Pre-commit Hooks"]
    D --> E["Verify Installation"]

    subgraph "Environment Setup Steps"
        B
        C
        D
    end
```

### Prerequisites

- Python 3.10 or newer
- Git
- Conda or Mamba (recommended for environment management)

### Step 1: Clone the Repository

```bash
git clone https://github.com/microsoft/bioemu
cd bioemu
```

### Step 2: Set Up Python Environment

Using conda/mamba (recommended):

```bash
conda create -n bioemu python=3.10
conda activate bioemu
```

### Step 3: Install Development Dependencies

Install BioEmu with development dependencies:

```bash
pip install -e ".[dev,md]"
```

This installs BioEmu in development mode with all dev dependencies including:
- pytest and pytest-cov for testing
- pre-commit for code quality checks
- openmm and other MD-related packages

### Step 4: Set Up Pre-commit Hooks

Initialize pre-commit hooks to ensure code quality checks run automatically before each commit:

```bash
pre-commit install
```

Sources: [pyproject.toml:27-36](), [.github/workflows/ci.yml:32-46]()

## Code Structure

BioEmu's codebase is organized into several key modules that work together to generate protein structure ensembles.

```mermaid
graph TD
    subgraph "BioEmu Package Structure"
        bioemu["bioemu/"]
        sample["bioemu.sample"]
        get_embeds["bioemu.get_embeds"]
        diffusion["bioemu.diffusion"]
        sidechain["bioemu.sidechain_relax"]
        convert["bioemu.convert_chemgraph"]
        utils["bioemu.utils"]
    end

    bioemu --> sample
    bioemu --> get_embeds
    bioemu --> diffusion
    bioemu --> sidechain
    bioemu --> convert
    bioemu --> utils

    sample --> |"uses"| get_embeds
    sample --> |"uses"| diffusion
    diffusion --> |"outputs to"| convert
    convert --> |"inputs to"| sidechain
```

Sources: System architecture diagrams provided

## Coding Standards and Quality

BioEmu uses several tools to maintain code quality and consistency.

```mermaid
flowchart LR
    subgraph "Code Quality Tools"
        A["pre-commit"]
        B["Black"]
        C["isort"]
        D["Ruff"]
        E["mypy"]
    end

    A --> B
    A --> C
    A --> D
    A --> E
```

### Code Formatting

- **Black**: Automatically formats Python code to a consistent style
  - Line length is set to 100 characters
  - Configuration in `pyproject.toml`

- **isort**: Sorts imports automatically
  - Configured to be compatible with Black
  - Groups imports into first-party (bioemu) and third-party

### Linting and Type Checking

- **Ruff**: Fast Python linter that enforces style and catches common errors
  - Configured to enforce various rules including:
    - pycodestyle (E, W)
    - Pyflakes (F)
    - pyupgrade (UP)
    - pylint error rules (PLE)

- **mypy**: Optional static type checker
  - Various third-party modules are configured to ignore missing imports

### Using Pre-commit

Pre-commit runs all quality checks before allowing commits:

```bash
# Run on all files
pre-commit run --all-files

# Run automatically on staged files during commit
git commit -m "Your commit message"
```

Sources: [pyproject.toml:38-160]()

## Testing Framework

BioEmu uses pytest for testing. The test suite validates functionality and ensures changes don't break existing features.

```mermaid
flowchart TD
    A["Write Tests"] --> B["Run Tests Locally"]
    B -- "Tests Pass" --> C["Submit PR"]
    B -- "Tests Fail" --> A
    C --> D["CI Runs Tests"]
    D -- "CI Passes" --> E["Code Review"]
    D -- "CI Fails" --> A
```

### Running Tests

To run the test suite:

```bash
# Run all tests
pytest tests/

# Run with coverage
coverage run --source=bioemu -m pytest tests/
coverage report
```

### Coverage Reports

Generate coverage reports to identify untested code:

```bash
# Generate HTML report
coverage html

# Generate XML report
coverage xml
```

Sources: [.github/workflows/ci.yml:47-55]()

## Continuous Integration

BioEmu uses GitHub Actions for continuous integration to automatically test changes and enforce code quality.

```mermaid
flowchart TD
    A["Push to Branch"] --> B["GitHub Actions"]
    subgraph "CI Pipeline"
        B --> C["Set Up Environment"]
        C --> D["Install Dependencies"]
        D --> E["Run Pre-commit"]
        E --> F["Run Tests"]
        F --> G["Generate Coverage"]
    end
    G --> H["PR Comment with Coverage"]
```

### CI Workflow

The CI pipeline runs the following steps:
1. Sets up a Python 3.10 environment using conda
2. Installs BioEmu with development dependencies
3. Runs pre-commit checks on all files
4. Runs the test suite with coverage
5. Generates coverage reports
6. Posts coverage summary as a PR comment (for PRs from internal branches)

### CodeQL Analysis

A separate workflow runs CodeQL analysis to identify security vulnerabilities and code quality issues.

Sources: [.github/workflows/ci.yml:14-72](), [.github/workflows/codeql.yml:1-96]()

## Release Process

The release process for BioEmu involves several steps to ensure proper versioning and packaging.

```mermaid
flowchart LR
    A["Update Version"] --> B["Run Tests"]
    B --> C["Update Changelog"]
    C --> D["Create Tag"]
    D --> E["Build Package"]
    E --> F["Publish to PyPI"]
```

### Version Management

Version numbers are maintained in `pyproject.toml`. When preparing a release:

1. Update the version number following semantic versioning principles (MAJOR.MINOR.PATCH)
2. Ensure all tests pass with the updated version
3. Create a git tag matching the version number
4. Build the package using `python -m build`
5. Publish to PyPI (when applicable)

The current version scheme uses semver format as seen in `pyproject.toml`: 0.1.6

Sources: [pyproject.toml:6-7]()

## Contributing Guidelines

When contributing to BioEmu, follow these general guidelines:

1. **Create a branch**: Create a branch from `main` for your changes
2. **Make targeted changes**: Keep changes focused on a single feature or bug fix
3. **Write tests**: Add tests for new functionality
4. **Ensure code quality**: Run pre-commit checks before submitting
5. **Submit a PR**: Create a pull request with a clear description of changes
6. **Address feedback**: Be responsive to code review feedback

### Pull Request Process

```mermaid
flowchart TD
    A["Fork Repository"] --> B["Create Branch"]
    B --> C["Make Changes"]
    C --> D["Write Tests"]
    D --> E["Run Quality Checks"]
    E -- "Checks Pass" --> F["Submit PR"]
    E -- "Checks Fail" --> C
    F --> G["CI Runs"]
    G -- "CI Passes" --> H["Code Review"]
    G -- "CI Fails" --> C
    H -- "Changes Requested" --> C
    H -- "Approved" --> I["Merge to Main"]
```

## Advanced Development Tasks

### Adding Dependencies

To add new dependencies to BioEmu:

1. Add the dependency to the appropriate section in `pyproject.toml`:
   - Main dependencies in the `dependencies` list
   - Development dependencies in the `dev` optional group
   - MD-related dependencies in the `md` optional group

2. Update your local environment:
   ```bash
   pip install -e ".[dev,md]"
   ```

3. Update the CI configuration if needed

Sources: [pyproject.toml:12-36]()

### Environment Management

For development with conda/mamba, use the following commands for environment management:

```bash
# Create environment
conda create -n bioemu python=3.10

# Activate environment
conda activate bioemu

# Install package with dev dependencies
pip install -e ".[dev,md]"
```

This development setup matches the CI environment and ensures consistent behavior between local and CI testing.

Sources: [.github/workflows/ci.yml:32-40]()

---

