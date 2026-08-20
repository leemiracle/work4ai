# deepwiki cleanrl §9 testing-and-cicd
> 来源: https://deepwiki.com/vwxyzjn/cleanrl/9-testing-and-cicd

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

## Testing and CI/CD

Relevant source files

  - .github/workflows/pre-commit.yml

  - .github/workflows/tests.yaml

  - .github/workflows/utils_test.yaml

  - benchmark/ppg.sh

  - cleanrl_utils/evals/c51_eval.py

  - cleanrl_utils/evals/c51_jax_eval.py

  - cleanrl_utils/evals/ddpg_eval.py

  - cleanrl_utils/evals/ddpg_jax_eval.py

  - cleanrl_utils/evals/dqn_eval.py

  - cleanrl_utils/evals/dqn_jax_eval.py

  - cleanrl_utils/evals/ppo_eval.py

  - cleanrl_utils/evals/td3_eval.py

  - cleanrl_utils/evals/td3_jax_eval.py

  - tests/test_atari.py

  - tests/test_atari_gymnasium.py

  - tests/test_atari_jax_gymnasium.py

  - tests/test_classic_control.py

  - tests/test_classic_control_gymnasium.py

  - tests/test_envpool.py

  - tests/test_mujoco.py

This document covers the test suite organization, GitHub Actions CI/CD workflows, environment-specific testing, and test execution patterns in CleanRL. The testing infrastructure ensures that all algorithm implementations work correctly across different Python versions, environments, and dependencies.

For information about benchmarking and performance evaluation, see Benchmarking and Evaluation For details on dependency management and development workflows, see Development Guide

### Overview

CleanRL's testing infrastructure is designed to validate algorithm implementations across multiple dimensions:

  - Python version compatibility : Tests run on Python 3.8, 3.9, and 3.10 .github/workflows/tests.yaml 13

  - Environment family coverage : Separate test jobs for classic control, Atari, MuJoCo, EnvPool, PettingZoo, and Procgen .github/workflows/tests.yaml 9-180

  - Framework variants : Both PyTorch and JAX implementations are tested (JAX on Linux/macOS only) .github/workflows/tests.yaml 31-40

  - Fast feedback : Tests use minimal timesteps (16-256) to run in seconds rather than hours tests/test_atari.py 6

The test suite executes actual algorithm scripts via subprocess, ensuring integration-level validation rather than unit testing. This approach verifies that command-line interfaces, argument parsing, environment setup, and full training loops work end-to-end.

Sources: .github/workflows/tests.yaml1-202 tests/test_atari.py4-17

### Test Suite Structure

#### Test File Organization

```

```

Test Execution Pattern

All algorithm tests follow a consistent pattern using `subprocess.run()` to execute complete training scripts with minimal hyperparameters tests/test_atari.py5-9:

```

```

This pattern ensures:

  - Command-line argument parsing works correctly.

  - Environment setup completes successfully.

  - Training loop executes without errors.

  - No import or dependency issues exist.

Tests intentionally use small values for `--total-timesteps`, `--num-steps`, and `--buffer-size` to complete in seconds tests/test_atari_gymnasium.py6

Sources: tests/test_classic_control.py4-9 tests/test_atari.py4-17 tests/test_atari_gymnasium.py4-73

### CI/CD Workflows

#### Main Test Workflow Architecture

```

```

The main test workflow `.github/workflows/tests.yaml` defines seven parallel test jobs, each running on a matrix of three Python versions (3.8, 3.9, 3.10) on Ubuntu 22.04 .github/workflows/tests.yaml12-14 This creates 21 parallel test executions per pull request.

Sources: .github/workflows/tests.yaml8-202

#### Test Job: Core Environments

Purpose: Tests basic algorithms on classic control environments and JAX variants.

Steps:

  - Install core dependencies via uv pip install ".[pytest]" .github/workflows/tests.yaml 27

  - Run pytest tests/test_classic_control.py (PPO on CartPole) .github/workflows/tests.yaml 29

  - Conditionally install JAX on Linux/macOS: uv pip install ".[pytest, jax]" .github/workflows/tests.yaml 32

  - Run Gymnasium tests: pytest tests/test_classic_control_gymnasium.py .github/workflows/tests.yaml 34

  - Run JAX tests: pytest tests/test_classic_control_jax_gymnasium.py .github/workflows/tests.yaml 37

  - Run GAE computation tests: pytest tests/test_jax_compute_gae.py .github/workflows/tests.yaml 40

  - Install and test Optuna integration: pytest tests/test_tuner.py .github/workflows/tests.yaml 44

JAX Conditional Logic: JAX tests only run on Linux or macOS due to platform limitations. Windows is excluded via .github/workflows/tests.yaml31:

```

```

Sources: .github/workflows/tests.yaml9-44

#### Test Job: Atari Environments

Purpose: Tests value-based algorithms (DQN, C51, Rainbow, SAC) on Atari games.

Dependencies: Requires Atari-specific packages via `uv pip install ".[pytest, atari]"` .github/workflows/tests.yaml64
Additional migration dependencies are installed for Gymnasium support .github/workflows/tests.yaml71:

  - gymnasium[atari,accept-rom-license]==0.28.1

  - ale-py==0.8.1

Tested Algorithms:

  - ppo_atari.py , ppo_atari_lstm.py (from tests/test_atari.py ) tests/test_atari.py 4-17

  - dqn_atari.py , c51_atari.py , rainbow_atari.py , sac_atari.py tests/test_atari_gymnasium.py 4-73

  - qdagger_dqn_atari_impalacnn.py tests/test_atari_gymnasium.py 20

  - JAX variants: dqn_atari_jax.py , c51_atari_jax.py , qdagger_dqn_atari_jax_impalacnn.py tests/test_atari_jax_gymnasium.py 4-50

Model Persistence Testing: Several tests include `--save-model` flag to verify checkpoint saving tests/test_atari_gymnasium.py14:

```

```

Sources: .github/workflows/tests.yaml46-76 tests/test_atari_gymnasium.py4-73 tests/test_atari_jax_gymnasium.py4-50

#### Test Job: MuJoCo Environments

Purpose: Tests continuous control algorithms with physics simulation.

Special Requirements:

  - Virtual Display Setup (Xvfb for headless rendering) .github/workflows/tests.yaml 118-122 :

```

```

  - MuJoCo System Libraries .github/workflows/tests.yaml 129 :

```

```

  - Environment Variable : Tests run with DISPLAY=:99 to use the virtual framebuffer .github/workflows/tests.yaml 132-133

Dependencies: Includes both MuJoCo and dm_control extras .github/workflows/tests.yaml126:

```

```

Sources: .github/workflows/tests.yaml102-133 tests/test_mujoco.py1-78

#### Test Job: EnvPool Environments

Purpose: Tests high-performance vectorized environments with optional JAX interface.

Key Features:

  - Installs envpool and jax extras .github/workflows/tests.yaml 153

  - Tests both standard and XLA-accelerated variants (e.g., ppo_atari_envpool_xla_jax_scan.py ) tests/test_envpool.py 28-33

Installation:

```

```

Sources: .github/workflows/tests.yaml135-155 tests/test_envpool.py4-41

#### Test Job: PettingZoo Multi-Agent

Purpose: Tests multi-agent reinforcement learning implementations.

Unique Step - ROM Installation .github/workflows/tests.yaml199:

```

```

This step is required because PettingZoo's multi-agent Atari environments need ROM files that must be explicitly accepted due to licensing.

Dependencies:

```

```

Sources: .github/workflows/tests.yaml179-201

#### Test Job: Procgen Environments

Purpose: Tests Phasic Policy Gradient (PPG) algorithm on procedurally generated environments.

Special Requirement - Setuptools Downgrade .github/workflows/tests.yaml98:

```

```

This workaround is necessary for `procgen` package compatibility. The specific setuptools version 59.5.0 resolves installation issues with the Procgen environment library.

Sources: .github/workflows/tests.yaml78-100 tests/test_procgen.py1-100

#### Utils Test Workflow

```

```

This workflow tests utility functions in `cleanrl_utils/`, including benchmark utilities and AWS Batch helpers .github/workflows/utils_test.yaml32

Cloud Dependencies: The workflow installs cloud extras for AWS integration testing .github/workflows/utils_test.yaml28:

```

```

Sources: .github/workflows/utils_test.yaml1-32

#### Pre-commit Workflow

```

```

The pre-commit workflow enforces code quality standards before tests run .github/workflows/pre-commit.yml23-25 It uses the `pre-commit/action@v3.0.1` GitHub Action.

Sources: .github/workflows/pre-commit.yml1-25

### Evaluation Test Scripts

CleanRL provides evaluation modules in `cleanrl_utils/evals/` to verify trained models. These scripts follow a standardized `evaluate` function pattern.

#### Evaluation Implementation Details

```

```

PyTorch Evaluation (TD3 Example):
The `evaluate` function in `cleanrl_utils/evals/td3_eval.py` performs the following steps:

  - Initializes a SyncVectorEnv with make_env cleanrl_utils/evals/td3_eval.py 19

  - Loads model parameters using torch.load cleanrl_utils/evals/td3_eval.py 23

  - Sets the actor to evaluation mode with actor.eval() cleanrl_utils/evals/td3_eval.py 25

  - Runs episodes until eval_episodes is reached, collecting episodic_return from info["episode"]["r"] cleanrl_utils/evals/td3_eval.py 34-46

JAX Evaluation (TD3 Example):
The `evaluate` function in `cleanrl_utils/evals/td3_jax_eval.py` handles XLA-specific logic:

  - Loads parameters using flax.serialization.from_bytes cleanrl_utils/evals/td3_jax_eval.py 40

  - JIT-compiles the model apply function: actor.apply = jax.jit(actor.apply) cleanrl_utils/evals/td3_jax_eval.py 44

  - Clips actions based on envs.single_action_space bounds cleanrl_utils/evals/td3_jax_eval.py 55

Sources: cleanrl_utils/evals/td3_eval.py8-49 cleanrl_utils/evals/td3_jax_eval.py10-68

### Running Tests Locally

#### Complete Test Suite

Run all tests with uv:

```

```

#### Environment-Specific Testing

Atari:

```

```

MuJoCo:

```

```

JAX Variants (Linux/macOS only):

```

```

Sources: .github/workflows/tests.yaml27-29 .github/workflows/tests.yaml64-66 .github/workflows/tests.yaml126-131



#### On this page

  - Testing and CI/CD
  - Overview
  - Test Suite Structure
  - Test File Organization
  - CI/CD Workflows
  - Main Test Workflow Architecture
  - Test Job: Core Environments
  - Test Job: Atari Environments
  - Test Job: MuJoCo Environments
  - Test Job: EnvPool Environments
  - Test Job: PettingZoo Multi-Agent
  - Test Job: Procgen Environments
  - Utils Test Workflow
  - Pre-commit Workflow
  - Evaluation Test Scripts
  - Evaluation Implementation Details
  - Running Tests Locally
  - Complete Test Suite
  - Environment-Specific Testing

$!/$$/$
