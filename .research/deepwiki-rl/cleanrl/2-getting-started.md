# deepwiki cleanrl §2 getting-started
> 来源: https://deepwiki.com/vwxyzjn/cleanrl/2-getting-started

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

## Getting Started

Relevant source files

  - README.md

  - docs/get-started/installation.md

  - docs/index.md

  - pyproject.toml

  - requirements/requirements-cloud.txt

CleanRL provides high-quality single-file implementations of deep reinforcement learning algorithms. This section guides you through installation, basic usage, and accessing pre-trained models. Each algorithm is self-contained in a single Python file, making it easy to understand, modify, and experiment with.

### Quick Start

The fastest way to get started with CleanRL is:

```

```

This will train a PPO agent on the CartPole environment. Training metrics are automatically logged to TensorBoard in the `runs/` directory.

Sources: README.md48-63 docs/get-started/installation.md8-13

### Getting Started Workflow

The typical workflow for using CleanRL follows these stages:

```

```

Sources: README.md42-74 pyproject.toml14-26

### File-to-Environment Mapping

CleanRL's single-file implementations are organized by algorithm and environment type. Each file contains the complete logic for that specific variant.

```

```

Sources: README.md135-166 pyproject.toml28-51

### Package Manager: uv

CleanRL uses `uv` as its primary package manager for fast, reliable dependency installation. The project requires Python `3.8` to `3.10`.

Dependency Installation Pattern:

```

```

For details, see Installation.

Sources: README.md45-46 docs/get-started/installation.md5-6 pyproject.toml6-75

### Command-Line Interface Pattern

All CleanRL algorithm files follow a consistent CLI pattern using the `tyro` library to parse a central `Args` dataclass.

```

```

For details, see Basic Usage.

Sources: pyproject.toml25 README.md56-73

### Model Zoo and Monitoring

CleanRL integrates with `huggingface-hub` for model sharing and `Weights & Biases` for experiment tracking.

  - Experiment Tracking : Use the --track flag to log metrics to WandB.

  - Model Zoo : Download and evaluate pre-trained models using cleanrl_utils.enjoy .

  - HuggingFace : Upload trained agents using the push_to_hub functionality.

For details, see Model Zoo and HuggingFace Integration.

Sources: README.md11-26 pyproject.toml16-22

### Next Steps

  - Installation — Detailed guide for setting up environments and optional dependencies.

  - Basic Usage — Learn how to run experiments and configure hyperparameters via CLI.

  - Model Zoo and HuggingFace Integration — Instructions for using pre-trained models and sharing your own.

Sources: README.md42-126



#### On this page

  - Getting Started
  - Quick Start
  - Getting Started Workflow
  - File-to-Environment Mapping
  - Package Manager: uv
  - Command-Line Interface Pattern
  - Model Zoo and Monitoring
  - Next Steps

$!/$$/$
