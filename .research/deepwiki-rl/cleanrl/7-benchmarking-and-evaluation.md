# deepwiki cleanrl §7 benchmarking-and-evaluation
> 来源: https://deepwiki.com/vwxyzjn/cleanrl/7-benchmarking-and-evaluation

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

## Benchmarking and Evaluation

Relevant source files

  - .github/issue_template.md

  - .github/pull_request_template.md

  - .github/workflows/pre-commit.yml

  - .github/workflows/tests.yaml

  - .github/workflows/utils_test.yaml

  - benchmark/ppg.sh

  - cleanrl_utils/benchmark.py

  - docs/get-started/benchmark-utility.md

This page describes CleanRL's infrastructure for benchmarking algorithms, tracking experiments, and evaluating performance. It covers the benchmark orchestration system, experiment tracking integrations, and how results are published to public dashboards.

For information about running individual training scripts, see Basic Usage. For hyperparameter optimization with Optuna, see Hyperparameter Tuning with Optuna. For model evaluation using pre-trained weights, see Model Zoo and HuggingFace Integration.

### Benchmarking Philosophy

CleanRL's benchmarking system is designed around reproducibility, transparency, and statistical rigor. All benchmarks:

  - Run with multiple random seeds (typically 3-10) to capture variance.

  - Log to public tracking services (Weights & Biases) for full transparency.

  - Use standardized hyperparameters specified in benchmark scripts.

  - Support distributed execution via SLURM or AWS Batch for scaling.

  - Integrate with OpenRL Benchmark (benchmark.cleanrl.dev) for comparison.

The system separates concerns into three layers:

  - Algorithm implementations : Single-file scripts (e.g., cleanrl/ppo.py ).

  - Benchmark orchestration : Shell scripts in benchmark/*.sh and the cleanrl_utils.benchmark module.

  - Results aggregation : OpenRL Benchmark dashboards and W&B reports.

Sources: .github/pull_request_template.md22-32 cleanrl_utils/benchmark.py13-37 docs/get-started/benchmark-utility.md1-5

### Benchmark Orchestration System

#### System Architecture

```

```

Diagram: Benchmark Orchestration Flow

The benchmark system uses a three-tier architecture where shell scripts define parameters, the `cleanrl_utils.benchmark` module expands these into individual commands, and the `ThreadPoolExecutor` or SLURM backend handles execution.

Sources: cleanrl_utils/benchmark.py110-116 cleanrl_utils/benchmark.py150-152 docs/get-started/benchmark-utility.md62-74

#### Benchmark Script Structure

Benchmark scripts in the `benchmark/` directory follow a consistent pattern:

| Script Component | Purpose | Example |
| Dependency Installation | Install optional extras | uv pip install ".[procgen]" |
| Environment IDs | List of test environments | --env-ids starpilot bossfight |
| Command Template | Algorithm script with flags | uv run python cleanrl/ppo.py --track |
| Seed Count | Number of random seeds | --num-seeds 3 |
| Parallelism | Concurrent worker count | --workers 1 |
| SLURM Config | Cluster resource requests | --slurm-gpus-per-task 1 |

Sources: benchmark/ppg.sh3-8 docs/get-started/benchmark-utility.md55-60

### Experiment Tracking Integration

#### Dual Tracking System

CleanRL supports both local and cloud-based experiment tracking. The standard implementation uses a `SummaryWriter` for TensorBoard and optionally initializes `wandb` when `--track` is provided.

| Tracking System | Trigger | Storage Location | Use Case |
| TensorBoard | Always enabled | runs/{run_name}/ | Local visualization, debugging |
| Weights & Biases | --track flag | W&B cloud servers | Collaboration, public benchmarks |
| Video Capture | --capture-video flag | videos/{run_name}/ | Gameplay visualization |

Sources: docs/get-started/benchmark-utility.md79-82 .github/pull_request_template.md25

#### Standard Metrics Logged

All CleanRL algorithms log a consistent set of metrics to ensure comparability across different experiments.

| Metric Category | Metric Name | Description |
| Performance | charts/episodic_return | Total reward per episode |
| Throughput | charts/SPS | Steps per second |
| Diagnostic | losses/explained_variance | Value function fit quality |
|  | losses/approx_kl | KL divergence approximation |

Sources: .github/pull_request_template.md19 docs/get-started/benchmark-utility.md90

### Distributed Execution

#### SLURM Cluster Integration

The `cleanrl_utils.benchmark` module automates job submission to SLURM clusters by populating a template file (e.g., `benchmark/cleanrl_1gpu.slurm_template`).

```

```

Diagram: SLURM Job Generation

Sources: cleanrl_utils/benchmark.py121-148 docs/get-started/benchmark-utility.md103-122

### Reproducibility and Validation

#### Seeding and Auto-tagging

To ensure results can be traced back to specific code versions, the benchmark utility includes an `autotag()` function.

  - Git Integration : It automatically retrieves the current git tag or commit hash using git describe or git rev-parse .

  - PR Tracking : It attempts to query the GitHub API to associate the run with a specific Pull Request number.

  - W&B Tags : These identifiers are injected into the WANDB_TAGS environment variable.

Sources: cleanrl_utils/benchmark.py54-87 cleanrl_utils/benchmark.py92-99

#### CI/CD Testing

The project maintains a rigorous testing suite via GitHub Actions to prevent regressions.

  - Environment Matrix : Tests are run across Python 3.8, 3.9, and 3.10.

  - Scope : Includes tests for classic_control , atari , procgen , mujoco , envpool , and pettingzoo .

  - Utility Tests : Specifically validates the tuner and core utilities.

Sources: .github/workflows/tests.yaml9-13 .github/workflows/tests.yaml41-44 .github/workflows/utils_test.yaml1-33

### Child Pages

For detailed instructions on specific evaluation topics, refer to the following pages:

  - Running Benchmarks : How to use benchmark/*.sh and the benchmark module for multi-seed runs.

  - Experiment Tracking : Detailed setup for TensorBoard, W&B, and the SummaryWriter pattern.

  - Hyperparameter Tuning with Optuna : Using the Tuner class for automated hyperparameter search.

Sources: cleanrl_utils/tuner.py docs/get-started/benchmark-utility.md1-100



#### On this page

  - Benchmarking and Evaluation
  - Benchmarking Philosophy
  - Benchmark Orchestration System
  - System Architecture
  - Benchmark Script Structure
  - Experiment Tracking Integration
  - Dual Tracking System
  - Standard Metrics Logged
  - Distributed Execution
  - SLURM Cluster Integration
  - Reproducibility and Validation
  - Seeding and Auto-tagging
  - CI/CD Testing
  - Child Pages

$!/$$/$
