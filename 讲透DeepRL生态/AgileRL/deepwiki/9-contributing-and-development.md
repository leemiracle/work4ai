> 来源: [https://deepwiki.com/AgileRL/AgileRL/9-contributing-and-development](https://deepwiki.com/AgileRL/AgileRL/9-contributing-and-development)
> DeepWiki AgileRL/AgileRL | Last indexed: 25 June 2025 (03307c

# Contributing and Development

  Relevant source files 
 - [.coveragerc](https://github.com/AgileRL/AgileRL/blob/03307c7b/.coveragerc)
 - [.github/workflows/python-app.yml](https://github.com/AgileRL/AgileRL/blob/03307c7b/.github/workflows/python-app.yml)
 - [.pre-commit-config.yaml](https://github.com/AgileRL/AgileRL/blob/03307c7b/.pre-commit-config.yaml)
 - [agilerl/utils/minari_utils.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/utils/minari_utils.py)
 
  This document covers the development workflow, code quality standards, testing infrastructure, and contribution guidelines for AgileRL. It provides technical guidance for developers who want to contribute to the codebase or understand the development processes.

 For information about AgileRL's core architecture and algorithms, see [Core Architecture](https://deepwiki.com/AgileRL/AgileRL/1.1-core-architecture). For details about specific training frameworks, see [Training Framework](https://deepwiki.com/AgileRL/AgileRL/3-training-framework).

 
## Development Environment Setup

 AgileRL uses a standardized development environment with specific Python version requirements and dependency management.

 
### Requirements

 
 - Python 3.8 or higher (enforced by pyupgrade configuration)
 - CUDA 12.8 support for GPU acceleration
 - Ray framework for distributed computing capabilities
 
 
### Installation Process

 
```

```

 The editable installation allows for real-time code changes during development without requiring reinstallation.

 **Sources:** [.github/workflows/python-app.yml26-31](https://github.com/AgileRL/AgileRL/blob/03307c7b/.github/workflows/python-app.yml#L26-L31)

 
## Code Quality Standards

 AgileRL enforces strict code quality standards through automated tools and pre-commit hooks. The quality pipeline ensures consistent code formatting, linting, and validation across all contributions.

 
### Code Quality Pipeline

 
```

```

 
### Quality Tool Configuration

 
| Tool | Purpose | Configuration |
|---|---|---|
| black | Code formatting | Default settings |
| ruff | Fast Python linter | Ignores E501 (line length), auto-fix enabled |
| isort | Import sorting | Black profile compatibility |
| codespell | Spell checking | Skips web assets, ignores domain-specific terms |
| pyupgrade | Python syntax modernization | Python 3.8+ features |
| yamlfmt | YAML formatting | Standard formatting rules |

 **Sources:** [.pre-commit-config.yaml1-59](https://github.com/AgileRL/AgileRL/blob/03307c7b/.pre-commit-config.yaml#L1-L59) [.github/workflows/python-app.yml32-46](https://github.com/AgileRL/AgileRL/blob/03307c7b/.github/workflows/python-app.yml#L32-L46)

 
## Testing Framework

 AgileRL uses pytest as the primary testing framework with comprehensive coverage reporting and distributed testing capabilities.

 
### Testing Infrastructure

 
```

```

 
### Coverage Configuration

 The testing framework includes advanced coverage tracking capabilities:

 
 - **Multiprocessing Support**: Tracks coverage across multiple processes
 - **Parallel Execution**: Enables concurrent test execution
 - **Signal Handling**: Proper SIGTERM handling for clean test termination
 
 **Sources:** [.github/workflows/python-app.yml47-53](https://github.com/AgileRL/AgileRL/blob/03307c7b/.github/workflows/python-app.yml#L47-L53) [.coveragerc1-5](https://github.com/AgileRL/AgileRL/blob/03307c7b/.coveragerc#L1-L5)

 
## CI/CD Pipeline

 AgileRL uses GitHub Actions for continuous integration with a custom Docker-based environment optimized for machine learning workloads.

 
### CI Environment Specification

 
```

```

 
### Environment Characteristics

 
 - **Custom Ray Container**: Pre-configured with Python 3.10, CUDA 12.8, and Ray framework
 - **Self-hosted Runners**: Uses `gha-runner-scale-set` for scalable execution
 - **Root Access**: Container runs with root privileges for full system access
 - **AWS ECR Integration**: Container images hosted on Amazon Elastic Container Registry
 
 **Sources:** [.github/workflows/python-app.yml14-18](https://github.com/AgileRL/AgileRL/blob/03307c7b/.github/workflows/python-app.yml#L14-L18)

 
## Development Utilities

 AgileRL provides specialized utilities for common development tasks, particularly for dataset handling and testing scenarios.

 
### Dataset Integration Utilities

 The `minari_utils.py` module demonstrates the codebase's approach to utility functions with comprehensive error handling and distributed training support:

 
```

```

 Key utility functions include:

 
 - `load_minari_dataset()`: Handles both local and remote dataset loading with distributed training support
 - `minari_to_agile_buffer()`: Converts Minari episodes to AgileRL `ReplayBuffer` format
 - `minari_to_agile_dataset()`: Creates HDF5-formatted datasets compatible with offline training
 
 **Sources:** [agilerl/utils/minari_utils.py16-136](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/utils/minari_utils.py#L16-L136)

 
## Contribution Workflow

 
### Pre-commit Hook Setup

 Enable automatic code quality checks by installing pre-commit hooks:

 
```

```

 
### Development Process

 
 - **Environment Setup**: Install development dependencies and enable pre-commit hooks
 - **Feature Development**: Implement changes following code quality standards
 - **Local Testing**: Run `pytest` locally to verify functionality
 - **Commit Process**: Pre-commit hooks automatically validate code quality
 - **CI Validation**: GitHub Actions pipeline performs comprehensive testing
 - **Coverage Review**: Monitor test coverage through Codecov integration
 
 
### Code Quality Requirements

 All contributions must pass:

 
 - Black code formatting
 - Ruff linting (excluding E501 line length)
 - Import sorting with isort
 - Spell checking with codespell
 - Python 3.8+ syntax compatibility
 - Comprehensive test coverage
 
 **Sources:** [.pre-commit-config.yaml1-59](https://github.com/AgileRL/AgileRL/blob/03307c7b/.pre-commit-config.yaml#L1-L59) [.github/workflows/python-app.yml1-54](https://github.com/AgileRL/AgileRL/blob/03307c7b/.github/workflows/python-app.yml#L1-L54)
