# deepwiki cleanrl §3 core-algorithms
> 来源: https://deepwiki.com/vwxyzjn/cleanrl/3-core-algorithms

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

## Core Algorithms

Relevant source files

  - cleanrl/dqn.py

  - cleanrl/dqn_atari.py

  - cleanrl/ppo.py

  - cleanrl/ppo_continuous_action.py

  - docs/rl-algorithms/overview.md

  - docs/rl-algorithms/ppo.md

  - mkdocs.yml

This page provides a technical overview of the main reinforcement learning algorithms implemented in CleanRL. CleanRL distinguishes itself by providing high-quality, single-file implementations of popular RL algorithms that are easy to understand while maintaining research-grade performance. This document covers the core algorithms, their implementation structure, and key architecture components.

### Algorithm Implementation Philosophy

CleanRL implements all algorithms following a consistent, single-file approach. Each implementation includes all the necessary components to understand and run the algorithm, without requiring additional imports from other parts of the codebase (except for environment wrappers and utilities).

Title: Single-File Algorithm Component Mapping

```

```

Sources: cleanrl/ppo.py18-78 cleanrl/dqn.py18-71 cleanrl/ppo_continuous_action.py18-85

### Common Architecture Across Algorithms

Despite implementing different algorithms, CleanRL maintains a consistent structure across files, making it easy to understand and compare implementations.

Title: Bridge: Natural Language Space to Code Entity Space

```

```

Sources: cleanrl/ppo.py100-126 cleanrl/dqn.py91-103 cleanrl/ppo_continuous_action.py112-142

### Major Algorithm Families

CleanRL implements several popular RL algorithm families, each with variants for different environment types.

#### Proximal Policy Optimization (PPO)

PPO is an on-policy algorithm that uses a clipped surrogate objective to prevent large policy updates. It is widely used due to its sample efficiency and stability. For details, see PPO (Proximal Policy Optimization).

Key components:

  - Actor-Critic Architecture : Separate networks for policy ( actor ) and value function ( critic ) cleanrl/ppo.py 103-116

  - Generalized Advantage Estimation (GAE) : For computing advantages with controlled bias/variance.

  - Implementation Details : Includes orthogonal initialization via layer_init cleanrl/ppo.py 94-97 and learning rate annealing cleanrl/ppo.py 187-190

Sources: cleanrl/ppo.py100-126 cleanrl/ppo.py185-293

#### Deep Q-Network (DQN)

DQN is a value-based algorithm that uses a neural network to approximate the Q-function, with experience replay and target networks to stabilize training. For details, see DQN (Deep Q-Network).

Key components:

  - Q-Network : Neural network approximating action-values cleanrl/dqn.py 91-100

  - Target Network : Periodically updated copy of Q-network for stable TD targets cleanrl/dqn.py 149-150

  - Experience Replay : Uses ReplayBuffer for storing transitions cleanrl/dqn.py 152-158

  - Exploration : Employs linear_schedule for epsilon-greedy exploration cleanrl/dqn.py 106-108

Sources: cleanrl/dqn.py90-102 cleanrl/dqn.py171-226

#### Soft Actor-Critic (SAC)

SAC is an off-policy actor-critic algorithm that maximizes both expected return and entropy, making it effective for exploration while being sample-efficient. For details, see SAC (Soft Actor-Critic).

Key components:

  - Entropy Regularization : Automatic tuning of the temperature parameter alpha .

  - Reparameterization Trick : Used in the stochastic policy to allow gradients to flow through samples.

  - Dual Q-Networks : Mitigates overestimation bias in value estimation.

Sources: docs/rl-algorithms/overview.md24-25 mkdocs.yml46

#### DDPG and TD3

Deep Deterministic Policy Gradient (DDPG) and Twin Delayed Deep Deterministic Policy Gradient (TD3) are off-policy algorithms designed for continuous action spaces. TD3 addresses issues in DDPG with several improvements. For details, see DDPG and TD3.

Key components:

  - Deterministic Policy : Maps states directly to specific actions.

  - TD3 Improvements : Clipped double Q-learning, delayed policy updates, and target policy smoothing.

Sources: docs/rl-algorithms/overview.md26-29 mkdocs.yml45-47

#### Advanced Algorithms

CleanRL includes several advanced and specialized algorithms. For details, see Advanced Algorithms.

  - Phasic Policy Gradient (PPG) : Separates training into policy and auxiliary phases docs/rl-algorithms/overview.md 30

  - Categorical DQN (C51) : Learns a distribution over possible returns docs/rl-algorithms/overview.md 20

  - Rainbow : Combines multiple DQN improvements docs/rl-algorithms/overview.md 34

  - Qdagger : A distillation-based approach docs/rl-algorithms/overview.md 32

  - RND : Random Network Distillation for exploration docs/rl-algorithms/overview.md 31

### Common Implementation Features

#### Args Dataclass Structure

All algorithms use a dataclass for hyperparameters, providing self-documentation via `tyro`.
Sources: cleanrl/ppo.py17-78 cleanrl/dqn.py18-71 cleanrl/dqn_atari.py26-80

#### Environment Wrappers

CleanRL uses standard `gymnasium` wrappers and custom wrappers for specific needs like Atari preprocessing.

  - Atari : Includes NoopResetEnv , MaxAndSkipEnv , and FrameStack cleanrl/dqn_atari.py 91-99

  - Continuous : Includes NormalizeObservation and NormalizeReward cleanrl/ppo_continuous_action.py 97-99

#### Logging and Metrics

Consistent logging is performed using `torch.utils.tensorboard.SummaryWriter`.

  - Standard Metrics : charts/episodic_return , charts/episodic_length , and charts/SPS (Steps Per Second).
Sources: cleanrl/dqn.py 176-181 cleanrl/ppo.py 147

### Conclusion

CleanRL's core algorithms provide clear, standalone implementations of major reinforcement learning algorithms. Each implementation contains all necessary components in a single file, making it easy to understand, modify, and extend. The consistent structure across different algorithms allows for easy comparison and learning.



#### On this page

  - Core Algorithms
  - Algorithm Implementation Philosophy
  - Common Architecture Across Algorithms
  - Major Algorithm Families
  - Proximal Policy Optimization (PPO)
  - Deep Q-Network (DQN)
  - Soft Actor-Critic (SAC)
  - DDPG and TD3
  - Advanced Algorithms
  - Common Implementation Features
  - Args Dataclass Structure
  - Environment Wrappers
  - Logging and Metrics
  - Conclusion

$!/$$/$
