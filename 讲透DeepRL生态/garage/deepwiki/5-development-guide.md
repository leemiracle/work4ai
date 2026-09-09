> 来源: [https://deepwiki.com/rlworkgroup/garage/5-development-guide](https://deepwiki.com/rlworkgroup/garage/5-development-guide)
> DeepWiki rlworkgroup/garage | Last indexed: 25 April 2025 (2d5948

# Development Guide

  Relevant source files 
 - [.pre-commit-config.yaml](https://github.com/rlworkgroup/garage/blob/2d594803/.pre-commit-config.yaml)
 - [.pylintrc](https://github.com/rlworkgroup/garage/blob/2d594803/.pylintrc)
 - [CONTRIBUTING.md](https://github.com/rlworkgroup/garage/blob/2d594803/CONTRIBUTING.md?plain=1)
 - [Makefile](https://github.com/rlworkgroup/garage/blob/2d594803/Makefile)
 - [docker/Dockerfile](https://github.com/rlworkgroup/garage/blob/2d594803/docker/Dockerfile)
 - [docker/hooks/build](https://github.com/rlworkgroup/garage/blob/2d594803/docker/hooks/build)
 - [docs/bibtex.json](https://github.com/rlworkgroup/garage/blob/2d594803/docs/bibtex.json)
 - [docs/requirements.txt](https://github.com/rlworkgroup/garage/blob/2d594803/docs/requirements.txt)
 - [docs/user/docker.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/docker.md?plain=1)
 - [docs/user/docker_dev.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/docker_dev.md?plain=1)
 - [scripts/check_commit_message](https://github.com/rlworkgroup/garage/blob/2d594803/scripts/check_commit_message)
 - [setup.cfg](https://github.com/rlworkgroup/garage/blob/2d594803/setup.cfg)
 - [setup.py](https://github.com/rlworkgroup/garage/blob/2d594803/setup.py)
 - [tests/garage/.pylintrc](https://github.com/rlworkgroup/garage/blob/2d594803/tests/garage/.pylintrc)
 - [tests/garage/torch/algos/test_sac.py](https://github.com/rlworkgroup/garage/blob/2d594803/tests/garage/torch/algos/test_sac.py)
 
  The Development Guide provides comprehensive instructions for contributors looking to develop and extend the garage reinforcement learning framework. This document covers setting up a development environment, code style guidelines, development workflow, testing, and continuous integration. For information on using garage as an end-user, see [Overview](https://deepwiki.com/rlworkgroup/garage/1-overview) and [Quick Start Guide](https://deepwiki.com/rlworkgroup/garage/1.2-quick-start-guide).

 
## Setting Up a Development Environment

 This section explains how to set up a development environment for contributing to garage. You can either set up a local development environment or use Docker.

 
### Local Development Setup

 To set up a local development environment:

 
 - Clone the repository:

 
```

```
 - Install the development dependencies:

 
```

```
 - Install pre-commit hooks:

 
```

```
 
 The development dependencies include:

 
 - Testing tools (pytest, pytest-cov, etc.)
 - Linting tools (flake8, pylint, etc.)
 - Documentation tools (sphinx, etc.)
 - Pre-commit hooks for code style enforcement
 
 Sources: [setup.py77-100](https://github.com/rlworkgroup/garage/blob/2d594803/setup.py#L77-L100) [CONTRIBUTING.md21-35](https://github.com/rlworkgroup/garage/blob/2d594803/CONTRIBUTING.md?plain=1#L21-L35)

 
### Docker-based Development

 For a containerized development environment, garage provides Docker configurations:

 
 - **Basic development environment**: Use `make run-dev` to build and run a Docker container with your local garage code mounted.
 - **NVIDIA GPU support**: Use `make run-dev-nvidia` for development with GPU support.
 - **Headless NVIDIA support**: Use `make run-dev-nvidia-headless` for servers without displays.
 
 Example usage:

 
```

```

 You can specify additional options:

 
 - `CONTAINER_NAME="my-container"` to name your container
 - `MJKEY_PATH="/path/to/mjkey.txt"` for MuJoCo
 - `GPUS="device=0,2"` to specify which GPUs to use (for NVIDIA images)
 
 Sources: [Makefile47-120](https://github.com/rlworkgroup/garage/blob/2d594803/Makefile#L47-L120) [docker/Dockerfile147-214](https://github.com/rlworkgroup/garage/blob/2d594803/docker/Dockerfile#L147-L214) [docs/user/docker_dev.md1-141](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/docker_dev.md?plain=1#L1-L141)

 
## Development Workflow Diagram

 
```

```

 Sources: [CONTRIBUTING.md251-316](https://github.com/rlworkgroup/garage/blob/2d594803/CONTRIBUTING.md?plain=1#L251-L316) [.pre-commit-config.yaml1-89](https://github.com/rlworkgroup/garage/blob/2d594803/.pre-commit-config.yaml#L1-L89) [Makefile28-40](https://github.com/rlworkgroup/garage/blob/2d594803/Makefile#L28-L40)

 
## Code Style Guidelines

 Garage enforces a consistent code style through various linting tools and pre-commit hooks.

 
### Python Style Guidelines

 
 - Follow [PEP8](https://www.python.org/dev/peps/pep-0008/) for Python code
 - Import sorting: Use isort with custom configuration in [setup.cfg24-62](https://github.com/rlworkgroup/garage/blob/2d594803/setup.cfg#L24-L62)
 - Code formatting: Use yapf with configuration in [setup.cfg77-80](https://github.com/rlworkgroup/garage/blob/2d594803/setup.cfg#L77-L80)
 - Linting: Use flake8 and pylint with configurations in [.pylintrc1-54](https://github.com/rlworkgroup/garage/blob/2d594803/.pylintrc#L1-L54) and [setup.cfg1-19](https://github.com/rlworkgroup/garage/blob/2d594803/setup.cfg#L1-L19)
 
 
### Garage-specific Style Rules

 
 - **Imports**:

 
 - Sort imports alphabetically within PEP8 groupings
 - Use absolute imports within the same package
 - Only import whole modules from external dependencies
 - **String formatting**:

 
 - Prefer single-quoted strings (`'foo'`) over double-quoted strings
 - Use f-strings for string interpolation
 - **Class design**:

 
 - Use `abc` package for abstract classes
 - Abstract methods should use `pass`, not `raise NotImplementedError`
 - **Documentation**:

 
 - Follow Google docstring format
 - Document types for all arguments, returns, exceptions
 - Include detailed shape information for tensor arguments
 
 Sources: [CONTRIBUTING.md36-196](https://github.com/rlworkgroup/garage/blob/2d594803/CONTRIBUTING.md?plain=1#L36-L196) [setup.cfg1-62](https://github.com/rlworkgroup/garage/blob/2d594803/setup.cfg#L1-L62) [.pylintrc1-54](https://github.com/rlworkgroup/garage/blob/2d594803/.pylintrc#L1-L54)

 
## Documentation Guidelines

 All public methods should include docstrings following the Google format. Example:

 
```

```

 Special conventions for tensor shapes:

 
 - Use `:math:` directive for shapes
 - `N` - Batch dimension
 - `T` - Time dimension
 - `[.]` - Variable-length dimensions
 - `\bullet` - Flattening operator
 
 Sources: [CONTRIBUTING.md186-227](https://github.com/rlworkgroup/garage/blob/2d594803/CONTRIBUTING.md?plain=1#L186-L227) [docs/requirements.txt1-21](https://github.com/rlworkgroup/garage/blob/2d594803/docs/requirements.txt#L1-L21)

 
## Development Tools Diagram

 
```

```

 Sources: [.pre-commit-config.yaml1-89](https://github.com/rlworkgroup/garage/blob/2d594803/.pre-commit-config.yaml#L1-L89) [setup.cfg64-76](https://github.com/rlworkgroup/garage/blob/2d594803/setup.cfg#L64-L76) [docs/requirements.txt1-21](https://github.com/rlworkgroup/garage/blob/2d594803/docs/requirements.txt#L1-L21)

 
## Git Workflow

 Garage uses a linear commit history with rebase-only merging. This means:

 
 - No merge commits in the project history
 - All pull requests are squashed to a single atomic commit when merged
 
 
### Git Best Practices

 
 - **Do**:

 
 - Fetch upstream frequently and keep your `master` branch up-to-date
 - Rebase your feature branch on `master` frequently
 - Keep only one or a few commits in your feature branch
 - Use `git commit --amend` to update changes
 - **Don't**:

 
 - Use GitHub's "Update branch" button
 - Use `git merge` or `git pull` (unless your branch can be fast-forwarded)
 - Make commits directly to the `master` branch
 
 
### Commit Message Format

 Commit messages must follow these guidelines:

 
 - Informative subject line of 50 characters or less
 - Capitalized subject line that doesn't end with a period
 - Blank line between subject and body
 - Body wrapped to 72 characters
 
 Example valid commit message:

 
```
Add logging system for training metrics

This adds a structured logging system that captures training
metrics in JSON format and writes them to disk. The metrics
can be loaded later for visualization or analysis.
```

 Sources: [CONTRIBUTING.md250-316](https://github.com/rlworkgroup/garage/blob/2d594803/CONTRIBUTING.md?plain=1#L250-L316) [scripts/check_commit_message1-71](https://github.com/rlworkgroup/garage/blob/2d594803/scripts/check_commit_message#L1-L71)

 
## Testing System

 Garage uses pytest for testing. The test configuration is in [setup.cfg64-76](https://github.com/rlworkgroup/garage/blob/2d594803/setup.cfg#L64-L76)

 
### Running Tests

 To run the test suite:

 
```

```

 To run specific test types using markers:

 
```

```

 
### Writing Tests

 When adding new functionality:

 
 - Add a test file in `tests/garage/` directory
 - Name the file with a `test_` prefix
 - Use appropriate markers for special tests
 
 Test markers available:

 
 - `@pytest.mark.nightly` - Long-running tests for nightly builds
 - `@pytest.mark.huge` - Very resource-intensive tests
 - `@pytest.mark.flaky` - Tests that occasionally fail
 - `@pytest.mark.gpu` - Tests requiring GPU
 - `@pytest.mark.mujoco` - Tests requiring MuJoCo
 
 Sources: [setup.cfg64-76](https://github.com/rlworkgroup/garage/blob/2d594803/setup.cfg#L64-L76) [tests/garage/torch/algos/test_sac.py1-343](https://github.com/rlworkgroup/garage/blob/2d594803/tests/garage/torch/algos/test_sac.py#L1-L343) [tests/garage/.pylintrc1-57](https://github.com/rlworkgroup/garage/blob/2d594803/tests/garage/.pylintrc#L1-L57)

 
## Docker Environment Structure

 
```

```

 Sources: [docker/Dockerfile1-219](https://github.com/rlworkgroup/garage/blob/2d594803/docker/Dockerfile#L1-L219) [docker/hooks/build1-30](https://github.com/rlworkgroup/garage/blob/2d594803/docker/hooks/build#L1-L30) [Makefile47-120](https://github.com/rlworkgroup/garage/blob/2d594803/Makefile#L47-L120)

 
## Continuous Integration

 Garage uses Travis CI for continuous integration. The CI pipeline runs the following checks:

 
 - **Code style checks**:

 
 - Flake8: Checks for PEP8 compliance and docstrings
 - Pylint: Checks for code quality and potential bugs
 - isort: Checks for proper import ordering
 - **Tests**:

 
 - Unit tests: Run with pytest
 - Integration tests: Run with appropriate markers
 - Test coverage: Generated with pytest-cov
 - **Documentation**:

 
 - Builds documentation with Sphinx
 - Checks for broken links
 - Validates docstring completeness
 
 
### Docker in CI

 The CI pipeline uses Docker to ensure consistent test environments. The `garage-test` image is built and used to run the test suite:

 
```

```

 This will run the default command in the test image:

 
```
nice -n 11 pytest -v -n auto -m 'not huge and not flaky' --durations=20
```

 Sources: [docker/Dockerfile216-219](https://github.com/rlworkgroup/garage/blob/2d594803/docker/Dockerfile#L216-L219) [Makefile28-40](https://github.com/rlworkgroup/garage/blob/2d594803/Makefile#L28-L40) [.pre-commit-config.yaml1-89](https://github.com/rlworkgroup/garage/blob/2d594803/.pre-commit-config.yaml#L1-L89)

 
## Project Structure and Dependencies

 The garage project is organized with the following key dependencies:

 
| Dependency Type | Packages |
|---|---|
| Core | akro, cloudpickle, numpy, torch, dowel |
| Algorithms | cma |
| Visualization | scikit-image |
| Environment | gym, mujoco-py, dm_control, pybullet |
| Distributed | ray, psutil, setproctitle |
| Development | flake8, pylint, pytest, sphinx |
| Optional | tensorflow, tensorflow-probability |

 The main code structure follows a modular design with frameworks for TensorFlow, PyTorch, and NumPy implementations.

 Sources: [setup.py10-100](https://github.com/rlworkgroup/garage/blob/2d594803/setup.py#L10-L100) [setup.cfg1-62](https://github.com/rlworkgroup/garage/blob/2d594803/setup.cfg#L1-L62)

 
## Release Process

 When preparing a release:

 
 - Update [CHANGELOG.md](https://github.com/rlworkgroup/garage/blob/2d594803/CHANGELOG.md?plain=1) with the most relevant changes since the last release
 - Follow the format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
 - Adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
 
 The version number is maintained in the `VERSION` file at the repository root and is automatically used during the build process.

 Sources: [CONTRIBUTING.md318-322](https://github.com/rlworkgroup/garage/blob/2d594803/CONTRIBUTING.md?plain=1#L318-L322) [setup.py105-108](https://github.com/rlworkgroup/garage/blob/2d594803/setup.py#L105-L108)

 
## Common Development Tasks

 
### Building Documentation

 To build and view the HTML documentation:

 
```

```

 This will build the documentation using Sphinx and open it in your default web browser.

 Sources: [Makefile42-45](https://github.com/rlworkgroup/garage/blob/2d594803/Makefile#L42-L45) [docs/requirements.txt1-21](https://github.com/rlworkgroup/garage/blob/2d594803/docs/requirements.txt#L1-L21)

 
### Running Examples

 Example usage of garage algorithms can be found in the `examples/` directory. These provide working demonstrations of different algorithms and can serve as templates for your own experiments.

 To run an example inside the development Docker container:

 
```

```

 Sources: [docs/user/docker.md26-36](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/docker.md?plain=1#L26-L36) [Makefile73-84](https://github.com/rlworkgroup/garage/blob/2d594803/Makefile#L73-L84)
