> 来源: [https://deepwiki.com/thu-ml/tianshou/9-development-and-contribution](https://deepwiki.com/thu-ml/tianshou/9-development-and-contribution)
> DeepWiki thu-ml/tianshou | Last indexed: 19 April 2025 (90846f

# Development and Contribution

  Relevant source files 
 - [.github/workflows/extra_sys.yml](https://github.com/thu-ml/tianshou/blob/90846f6b/.github/workflows/extra_sys.yml)
 - [.github/workflows/gputest.yml](https://github.com/thu-ml/tianshou/blob/90846f6b/.github/workflows/gputest.yml)
 - [.github/workflows/lint_and_docs.yml](https://github.com/thu-ml/tianshou/blob/90846f6b/.github/workflows/lint_and_docs.yml)
 - [.github/workflows/pytest.yml](https://github.com/thu-ml/tianshou/blob/90846f6b/.github/workflows/pytest.yml)
 - [.readthedocs.yaml](https://github.com/thu-ml/tianshou/blob/90846f6b/.readthedocs.yaml)
 - [docs/_config.yml](https://github.com/thu-ml/tianshou/blob/90846f6b/docs/_config.yml)
 - [docs/create_toc.py](https://github.com/thu-ml/tianshou/blob/90846f6b/docs/create_toc.py)
 - [docs/nbstripout.py](https://github.com/thu-ml/tianshou/blob/90846f6b/docs/nbstripout.py)
 - [docs/spelling_wordlist.txt](https://github.com/thu-ml/tianshou/blob/90846f6b/docs/spelling_wordlist.txt)
 - [poetry.lock](https://github.com/thu-ml/tianshou/blob/90846f6b/poetry.lock)
 - [pyproject.toml](https://github.com/thu-ml/tianshou/blob/90846f6b/pyproject.toml)
 
  This page provides comprehensive guidance for developers who want to contribute to the Tianshou reinforcement learning library. It covers the development environment setup, build system, testing framework, CI/CD pipeline, documentation, and contribution guidelines.

 
## Development Environment Setup

 
### Prerequisites

 
 - Python 3.11 or higher
 - Poetry (dependency management tool)
 - Git
 
 
### Setting Up Local Development Environment

 
 - **Clone the repository**:

 
```

```
 - **Install Poetry** (if not already installed):

 
```

```
 - **Configure Poetry to use local virtual environments**:

 
```

```
 - **Install dependencies**:

 
```

```
 - **Install additional extras** (optional):

 
```

```
 
 Sources: [pyproject.toml1-240](https://github.com/thu-ml/tianshou/blob/90846f6b/pyproject.toml#L1-L240) [.github/workflows/pytest.yml35-52](https://github.com/thu-ml/tianshou/blob/90846f6b/.github/workflows/pytest.yml#L35-L52)

 
## Project Structure

 The Tianshou codebase is organized into several core modules:

 
```
tianshou/
├── tianshou/          # Main package
│   ├── data/          # Data handling (Batch, ReplayBuffer, Collector)
│   ├── env/           # Environment wrappers and vectorization
│   ├── exploration/   # Exploration strategies
│   ├── policy/        # RL algorithms implementations
│   │   ├── modelfree/ # Model-free algorithms
│   │   ├── modelbased/ # Model-based algorithms
│   │   ├── imitation/ # Imitation learning algorithms
│   │   └── multiagent/ # Multi-agent algorithms
│   ├── trainer/       # Training loops (on-policy, off-policy)
│   └── utils/         # Utility functions and network definitions
├── test/              # Test suite
├── examples/          # Example scripts and tutorials
├── docs/              # Documentation
└── .github/           # GitHub workflows and templates
```

 
### Component Relationships

 Tianshou Component Hierarchy

 
```

```

 
## Build System

 Tianshou uses Poetry for dependency management and build configuration.

 
### Managing Dependencies

 Dependencies are defined in `pyproject.toml` and locked in `poetry.lock`. The project organizes dependencies into:

 
 - **Core dependencies**: Required for basic functionality (`torch`, `gymnasium`, etc.)
 - **Optional dependencies**: Organized into extras like "atari", "box2d", "mujoco"
 - **Development dependencies**: In the "dev" group (testing, documentation, code quality)
 
 
### Development Tasks

 The project uses `poethepoet` (poe) to define common development tasks:

 
| Task Command | Description |
|---|---|
| poetry run poe test | Run tests with coverage |
| poetry run poe test-reduced | Run a subset of tests (faster) |
| poetry run poe format | Format code with black and ruff |
| poetry run poe lint | Check code style |
| poetry run poe type-check | Check type hints |
| poetry run poe doc-build | Build documentation |

 Sources: [pyproject.toml5-240](https://github.com/thu-ml/tianshou/blob/90846f6b/pyproject.toml#L5-L240) [poetry.lock1-597](https://github.com/thu-ml/tianshou/blob/90846f6b/poetry.lock#L1-L597)

 
## Testing Framework

 
### Test Organization

 Tests are structured to mirror the package organization:

 
 - `test/base/`: Basic functionality tests
 - `test/continuous/`: Tests for continuous control algorithms
 - `test/discrete/`: Tests for discrete control algorithms
 
 
### Running Tests

 
```

```

 
### Writing Tests

 New tests should:

 
 - Be placed in the appropriate directory based on functionality
 - Follow the naming convention `test_*.py`
 - Use pytest fixtures where appropriate
 - Include both unit tests and integration tests
 
 Example test structure:

 
```

```

 Sources: [pyproject.toml216-217](https://github.com/thu-ml/tianshou/blob/90846f6b/pyproject.toml#L216-L217) [.github/workflows/pytest.yml56-60](https://github.com/thu-ml/tianshou/blob/90846f6b/.github/workflows/pytest.yml#L56-L60)

 
## CI/CD Pipeline

 Tianshou uses GitHub Actions for continuous integration and deployment.

 
### CI Workflows

 Tianshou CI/CD Pipeline

 
```

```

 **Workflow Details**:

 
| Workflow | File | Purpose |
|---|---|---|
| Ubuntu Tests | pytest.yml | Runs full test suite on Ubuntu with Python 3.11 |
| Windows/MacOS Tests | extra_sys.yml | Runs reduced test suite for cross-platform compatibility |
| GPU Tests | gputest.yml | Runs tests on GPU using a self-hosted runner |
| Lint and Docs | lint_and_docs.yml | Checks code style, type annotations, and builds documentation |

 Sources: [.github/workflows/pytest.yml1-68](https://github.com/thu-ml/tianshou/blob/90846f6b/.github/workflows/pytest.yml#L1-L68) [.github/workflows/extra_sys.yml1-58](https://github.com/thu-ml/tianshou/blob/90846f6b/.github/workflows/extra_sys.yml#L1-L58) [.github/workflows/gputest.yml1-56](https://github.com/thu-ml/tianshou/blob/90846f6b/.github/workflows/gputest.yml#L1-L56) [.github/workflows/lint_and_docs.yml1-55](https://github.com/thu-ml/tianshou/blob/90846f6b/.github/workflows/lint_and_docs.yml#L1-L55)

 
## Documentation

 Tianshou's documentation is built with Sphinx and Jupyter Book.

 
### Documentation Structure

 
 - **API Reference**: Automatically generated from docstrings
 - **Tutorials**: Jupyter notebooks in `docs/02_notebooks/`
 - **Guides**: Markdown and reStructuredText files
 
 
### Building Documentation

 
```

```

 This process:

 
 - Generates API reference files (`docs/autogen_rst.py`)
 - Creates table of contents (`docs/create_toc.py`)
 - Configures Sphinx
 - Builds HTML documentation in `docs/_build`
 
 
### Documentation Standards

 
 - **Docstrings**: Use Google-style docstrings
 - **Notebooks**: Strip outputs before committing (`poetry run poe clean-nbs`)
 - **Spelling**: Add specialized terms to `docs/spelling_wordlist.txt`
 
 Sources: [.readthedocs.yaml1-24](https://github.com/thu-ml/tianshou/blob/90846f6b/.readthedocs.yaml#L1-L24) [docs/_config.yml1-151](https://github.com/thu-ml/tianshou/blob/90846f6b/docs/_config.yml#L1-L151) [docs/create_toc.py1-9](https://github.com/thu-ml/tianshou/blob/90846f6b/docs/create_toc.py#L1-L9) [docs/spelling_wordlist.txt1-295](https://github.com/thu-ml/tianshou/blob/90846f6b/docs/spelling_wordlist.txt#L1-L295)

 
## Contribution Process

 
### Contribution Workflow

 Tianshou Contribution Workflow

 
```

```

 
 - **Fork and clone** the repository
 - **Create a feature branch** from `master`
 - **Implement changes** and add tests
 - **Run tests, formatting, linting, and type checks**
 - **Submit a pull request** to the `master` branch
 
 
### Code Style

 Tianshou enforces code style through several tools:

 
| Tool | Purpose | Configuration |
|---|---|---|
| Black | Code formatting | Line length: 100 characters |
| Ruff | Linting | Multiple rule sets enabled |
| Mypy | Type checking | Strict type checking |

 All configured in `pyproject.toml`:

 
```

```

 
### Pull Request Guidelines

 
 - Focus PRs on a single issue or feature
 - Add tests for new functionality
 - Update documentation where relevant
 - Ensure CI passes before requesting review
 - Reference related issues
 
 Sources: [pyproject.toml127-205](https://github.com/thu-ml/tianshou/blob/90846f6b/pyproject.toml#L127-L205) [.github/workflows/lint_and_docs.yml49-54](https://github.com/thu-ml/tianshou/blob/90846f6b/.github/workflows/lint_and_docs.yml#L49-L54)

 
## Release Process

 Tianshou follows semantic versioning (MAJOR.MINOR.PATCH).

 
### Versioning

 
 - Current development version: `1.2.0-dev` in `pyproject.toml`
 - Version follows semantic versioning: 
 - **MAJOR**: Incompatible API changes
 - **MINOR**: Backwards-compatible features
 - **PATCH**: Backwards-compatible bug fixes
 
 
### Release Steps

 
 - Update version in `tianshou/__init__.py` and `pyproject.toml`
 - Update changelog with notable changes
 - Create a release PR for review
 - Merge to master and tag the release
 - Publish to PyPI
 
 Sources: [pyproject.toml6-7](https://github.com/thu-ml/tianshou/blob/90846f6b/pyproject.toml#L6-L7)
