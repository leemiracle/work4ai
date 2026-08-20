# deepwiki cleanrl §11 contributing
> 来源: https://deepwiki.com/vwxyzjn/cleanrl/11-contributing

$/$
$?

/$

DeepWiki

DeepWiki
vwxyzjn/cleanrl

$?

/$

Last indexed:  27 July 2026  (fe8d8a)

  - Overview
  - Getting Started
  - Installation
  - Basic Usage
  - Model Zoo and HuggingFace Integration
  - Core Algorithms
  - PPO (Proximal Policy Optimization)
  - DQN (Deep Q-Network)
  - SAC (Soft Actor-Critic)
  - DDPG and TD3
  - Advanced Algorithms
  - JAX Implementations
  - JAX Algorithm Implementations
  - EnvPool XLA Integration
  - Environment Integrations
  - Classic Control
  - Atari Games
  - MuJoCo and Continuous Control
  - Procgen and Generalization
  - Multi-agent Environments
  - Isaac Gym Integration
  - EnvPool Integration
  - Benchmarking and Evaluation
  - Running Benchmarks
  - Experiment Tracking
  - Hyperparameter Tuning with Optuna
  - Cloud Deployment
  - AWS Batch Setup
  - Docker Containers
  - Testing and CI/CD
  - Development Guide
  - Contributing
  - Glossary

Menu

## Contributing

Relevant source files

  - .github/issue_template.md

  - .github/pull_request_template.md

  - .gitignore

  - CONTRIBUTING.md

  - LICENSE

  - cleanrl_utils/benchmark.py

  - cleanrl_utils/tuner.py

  - docs/advanced/optuna-dashboard-1.png

  - docs/advanced/optuna-dashboard-2.png

  - docs/advanced/optuna-results.png

  - docs/blog/.authors.yml

  - docs/blog/.meta.yml

  - docs/blog/index.md

  - docs/cleanrl-supported-papers-projects.md

  - docs/contribution.md

  - docs/get-started/benchmark-utility.md

  - docs/static/pre-commit.png

This guide explains how to contribute to CleanRL, a library focused on high-quality single-file implementations of reinforcement learning algorithms. It covers the development environment setup, contribution workflow, code standards, testing, benchmarking, and documentation processes required to successfully contribute to the project.

### Development Environment Setup

Before contributing to CleanRL, you'll need to set up your development environment properly.

#### Prerequisites

  - Python >=3.8,<3.11 (as specified in pyproject.toml )

  - uv - Fast Python package installer

  - Git for version control

Sources:

  - CONTRIBUTING.md 1

  - docs/contribution.md 9-13

#### Installation Steps

  - Clone the repository:

```

```

  - Install uv (if not already installed).

  - Create a virtual environment and install dependencies:

```

```

  - For specific environment support, install optional dependencies:

```

```

  - Set up pre-commit hooks for code quality:

```

```

Sources:

  - docs/contribution.md 9-13

  - docs/contribution.md 41

  - .github/issue_template.md 5

#### Pre-commit Hooks

CleanRL uses pre-commit hooks to ensure code quality. The hooks run automatically on `git commit`, but you can also run them manually.

The pre-commit checks include:

  - pyupgrade : Upgrades syntax for newer versions of the language.

  - isort : Sorts imported dependencies.

  - black : Enforces uniform code style.

  - codespell : Avoids common incorrect spelling.

Sources:

  - docs/contribution.md 31-42

  - .github/pull_request_template.md 15

### Contribution Workflow

The following diagram illustrates the contribution workflow for CleanRL:

```

```

Sources:

  - docs/contribution.md 3-5

  - docs/contribution.md 50-68

  - .github/pull_request_template.md 1-21

#### Types of Contributions

CleanRL categorizes contributions into two main types:

  - Non-performance-impacting changes : Changes that don't affect the algorithm's performance, such as: Documentation fixes. Variable renaming. Removing unused code.

  - Performance-impacting changes : Changes that influence the algorithm's performance, such as: Modification to hyperparameters (e.g., gamma in PPO). Bug fixes in the training logic. New algorithm implementations.

Sources:

  - docs/contribution.md 60-66

  - .github/pull_request_template.md 5-9

#### Opening Issues

Before making significant contributions, start by opening an issue using the `issue_template.md` to discuss your proposed changes. This ensures alignment with the project's goals.

Sources:

  - docs/contribution.md 53-56

  - .github/issue_template.md 1-25

### RLops Process for Performance-Impacting Changes

For contributions that impact algorithm performance, CleanRL uses the "RLops" process to ensure quality and prevent regressions.

```

```

Sources:

  - docs/contribution.md 69-72

  - cleanrl_utils/benchmark.py 13-37

#### Running Benchmarks

To run benchmark experiments, use the `cleanrl_utils.benchmark` utility. This script automatically invokes an `--autotag` feature to tag experiments with git information and PR numbers.

```

```

Sources:

  - docs/contribution.md 76-90

  - cleanrl_utils/benchmark.py 54-87

  - docs/get-started/benchmark-utility.md 9-48

#### Regression Check

Verify performance using the `openrlbenchmark.rlops` CLI:

```

```

Sources:

  - docs/contribution.md 93-104

  - .github/pull_request_template.md 26-32

### Testing System

CleanRL uses `pytest` for unit and integration testing.

#### Running Tests Locally

To run the tests locally, ensure you have all extras installed:

```

```

Sources:

  - docs/contribution.md 22-27

### Hyperparameter Tuning

CleanRL provides a `Tuner` class in `cleanrl_utils/tuner.py` for automated hyperparameter search using Optuna.

| Feature | Description |
| Storage | Defaults to sqlite:///cleanrl_hpopt.db cleanrl_utils/tuner.py 36 |
| Aggregation | Supports average , median , max , min cleanrl_utils/tuner.py 52-61 |
| Pruning | Integrated with Optuna's trial.should_prune() cleanrl_utils/tuner.py 119 |
| Logging | Integrates with W&B for study tracking cleanrl_utils/tuner.py 75-83 |

Sources:

  - cleanrl_utils/tuner.py 24-69

  - cleanrl_utils/tuner.py 72-128

### Documentation

CleanRL uses `mkdocs` for documentation.

#### Building Documentation

To build and serve the documentation locally:

```

```

Sources:

  - docs/contribution.md 9-19

### Pull Request Checklist

When submitting a PR, follow the checklist in the `pull_request_template.md`:

  - General : Summary of changes and type of change (Bug fix, New feature, etc.).

  - Quality : Ensure pre-commit run --all-files passes.

  - Documentation : Update mkdocs and explain note-worthy implementation details.

  - Performance : If applicable, include W&B learning curves and regression tables.

Sources:

  - .github/pull_request_template.md 1-34

  - docs/contribution.md 14-19

### License and Attribution

Contributions are licensed under the MIT License. If you adapt code from other repositories (e.g., `sfujim/TD3` or `haarnoja/sac`), you must include the appropriate copyright notices in the code and `LICENSE` file.

Sources:

  - LICENSE 1-21

  - LICENSE 26-74



#### On this page

  - Contributing
  - Development Environment Setup
  - Prerequisites
  - Installation Steps
  - Pre-commit Hooks
  - Contribution Workflow
  - Types of Contributions
  - Opening Issues
  - RLops Process for Performance-Impacting Changes
  - Running Benchmarks
  - Regression Check
  - Testing System
  - Running Tests Locally
  - Hyperparameter Tuning
  - Documentation
  - Building Documentation
  - Pull Request Checklist
  - License and Attribution

$!/$$/$
