# deepwiki cleanrl §4 jax-implementations
> 来源: https://deepwiki.com/vwxyzjn/cleanrl/4-jax-implementations

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

## JAX Implementations

Relevant source files

  - benchmark/ddpg.sh

  - benchmark/dqn.sh

  - benchmark/td3.sh

  - cleanrl/ddpg_continuous_action_jax.py

  - cleanrl/dqn_atari_jax.py

  - cleanrl/dqn_jax.py

  - cleanrl/ppo_atari_envpool_xla_jax_scan.py

  - cleanrl/td3_continuous_action_jax.py

  - docs/rl-algorithms/ddpg.md

  - docs/rl-algorithms/dqn.md

  - docs/rl-algorithms/ppo/ppo_atari_envpool_xla_jax_scan/compare-time.png

  - docs/rl-algorithms/ppo/ppo_atari_envpool_xla_jax_scan/compare.png

  - docs/rl-algorithms/td3.md

  - tests/test_jax_compute_gae.py

This page documents the JAX-based reinforcement learning algorithm implementations in CleanRL. JAX implementations provide significant performance improvements over PyTorch equivalents while maintaining the clean, single-file design philosophy of CleanRL. For information on PyTorch-based implementations, refer to the appropriate algorithm-specific documentation in the Core Algorithms section.

### Introduction to JAX in CleanRL

JAX is a high-performance numerical computing library developed by Google that combines NumPy's familiar API with the benefits of hardware acceleration and just-in-time (JIT) compilation. CleanRL provides JAX implementations for several key reinforcement learning algorithms, offering 2.5-4x speedups compared to equivalent PyTorch implementations.

#### JAX Ecosystem Overview

The JAX stack in CleanRL relies on Flax for neural network definitions and Optax for gradient transformation and optimization.

```

```

Sources: cleanrl/dqn_jax.py7-18 cleanrl/ddpg_continuous_action_jax.py7-15 cleanrl/ppo_atari_envpool_xla_jax_scan.py10-19

### Performance Benefits

JAX implementations offer substantial performance improvements over their PyTorch counterparts, typically ranging from 2x to 4x speedups depending on the hardware and environment complexity.

| Algorithm | Environment | JAX Speedup | Key Optimization |
| DQN | CartPole | ~2.5x | jax.jit updates |
| DQN | Atari | ~3x | XLA Fusion |
| DDPG/TD3 | MuJoCo | ~3x | Functional gradients |
| PPO | Atari | ~4x | jax.lax.scan + EnvPool |

Sources: cleanrl/dqn_jax.py154-180 cleanrl/ppo_atari_envpool_xla_jax_scan.py22-26 benchmark/ddpg.sh12-22

### Core Architecture Patterns

The JAX implementations in CleanRL follow a consistent architecture pattern while leveraging JAX-specific optimizations:

#### TrainState Pattern

Unlike PyTorch where models and optimizers are stateful objects, JAX is functional. CleanRL uses the `TrainState` pattern to bundle parameters, the optimizer state, and target parameters into a single immutable container.

```

```

Sources: cleanrl/dqn_jax.py102-103 cleanrl/ddpg_continuous_action_jax.py109-110 cleanrl/td3_continuous_action_jax.py113-114

#### JIT Compilation and XLA

Performance is largely driven by `jax.jit`, which compiles Python/JAX functions into XLA (Accelerated Linear Algebra) kernels. CleanRL typically JIT-compiles the entire update step to minimize Python overhead.

```

```

Sources: cleanrl/dqn_jax.py166-179 cleanrl/ddpg_continuous_action_jax.py178-200

#### XLA Memory Management

To prevent OOM (Out of Memory) issues common with JAX's default memory pre-allocation, CleanRL scripts often configure the XLA client memory fraction.

```

```

Sources: cleanrl/dqn_atari_jax.py8 cleanrl/ppo_atari_envpool_xla_jax_scan.py23

### Child Pages

#### JAX Algorithm Implementations

Details the JAX versions of DQN, DDPG, TD3, and C51. It explains the functional update steps, the use of `jax.value_and_grad`, and how `optax` is used for gradient updates.
For details, see JAX Algorithm Implementations.

#### EnvPool XLA Integration

Explains the highly optimized PPO implementation that uses EnvPool's XLA interface. This section covers the `jax.lax.scan` pattern for environment rollouts and the `EpisodeStatistics` dataclass used for tracking metrics within the JIT-compiled loop.
For details, see EnvPool XLA Integration.

### Comparison: JAX vs PyTorch

| Feature | PyTorch Versions | JAX Versions |
| State | Stateful objects ( nn.Module ) | Functional/Immutable ( TrainState ) |
| Optimization | optimizer.step() | state.apply_gradients(grads) |
| Speed | Standard | High (JIT/XLA) |
| Randomness | torch.manual_seed | Explicit jax.random.PRNGKey |
| Vectorization | SyncVectorEnv | jax.vmap or jax.lax.scan |

Sources: cleanrl/dqn_jax.py163-164 cleanrl/ppo_atari_envpool_xla_jax_scan.py320-330 docs/rl-algorithms/ddpg.md83-119



#### On this page

  - JAX Implementations
  - Introduction to JAX in CleanRL
  - JAX Ecosystem Overview
  - Performance Benefits
  - Core Architecture Patterns
  - TrainState Pattern
  - JIT Compilation and XLA
  - XLA Memory Management
  - Child Pages
  - [JAX Algorithm Implementations](#4.1)
  - [EnvPool XLA Integration](#4.2)
  - Comparison: JAX vs PyTorch

$!/$$/$
