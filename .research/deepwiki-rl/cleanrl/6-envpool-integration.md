# deepwiki cleanrl §6 envpool-integration
> 来源: https://deepwiki.com/vwxyzjn/cleanrl/6-envpool-integration

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

## EnvPool Integration

Relevant source files

  - cleanrl/ppo_atari_envpool.py

  - cleanrl/ppo_atari_envpool_xla_jax_scan.py

  - cleanrl/ppo_continuous_action_isaacgym/ppo_continuous_action_isaacgym.py

  - cleanrl/ppo_pettingzoo_ma_atari.py

  - cleanrl/ppo_rnd_envpool.py

  - cleanrl_utils/evals/dqn_eval.py

  - cleanrl_utils/evals/dqn_jax_eval.py

  - docs/rl-algorithms/ppo/ppo_atari_envpool_xla_jax_scan/compare-time.png

  - docs/rl-algorithms/ppo/ppo_atari_envpool_xla_jax_scan/compare.png

  - tests/test_envpool.py

  - tests/test_jax_compute_gae.py

### Purpose and Scope

This document provides technical details on CleanRL's integration with EnvPool, a high-performance environment execution engine. EnvPool dramatically accelerates reinforcement learning training by implementing environments in C++ and providing efficient vectorization. This page covers creating and using EnvPool environments, performance benefits, and specifics on both PyTorch and JAX implementations.

For information about other environment types supported by CleanRL, see Environment Integrations.

### Overview of EnvPool

EnvPool is a high-throughput, concurrent reinforcement learning environment execution engine developed by Garena AI Lab. It implements popular environments like Atari in C++ with optimized parallelism and a unified Python interface, allowing for significantly faster sampling compared to traditional Python-based environments.

#### System Architecture

The following diagram bridges the high-level EnvPool architecture with specific CleanRL code entities.

Diagram: EnvPool to Code Entity Mapping

```

```

Sources: cleanrl/ppo_atari_envpool.py185-196 cleanrl/ppo_atari_envpool_xla_jax_scan.py99-115 cleanrl/ppo_atari_envpool_xla_jax_scan.py235-252

EnvPool provides significant performance advantages over standard Gym environments and even other vectorized implementations:

| Environment | Standard Gym | gym.vector | EnvPool | Speedup |
| Atari | 50-100 SPS | 200-400 SPS | 2000-5000 SPS | 10-20x |
| Classic Control | 1000 SPS | 3000 SPS | 20000+ SPS | 7-10x |

### Implementation Details

#### Creating EnvPool Environments

The core function for creating EnvPool environments in CleanRL is the `make_env` function (or direct `envpool.make` calls in PyTorch scripts).

Diagram: Environment Data Flow

```

```

Sources: cleanrl/ppo_atari_envpool.py185-197 cleanrl/ppo_atari_envpool_xla_jax_scan.py99-115

EnvPool is initialized with parameters specific to the environment type:

  - env_type : Set to "gym" for Gym-compatible interface cleanrl/ppo_atari_envpool.py 187

  - num_envs : Number of parallel environments cleanrl/ppo_atari_envpool.py 188

  - episodic_life : Set to True for Atari to treat each life as an episode cleanrl/ppo_atari_envpool.py 189

  - reward_clip : Set to True to clip rewards to [-1, 1] cleanrl/ppo_atari_envpool.py 190

#### JAX-specific Integration

CleanRL's JAX implementations utilize EnvPool's XLA interface for even faster environment stepping by eliminating Python call overhead. The integration uses `jax.lax.scan` to fold the environment stepping into the compiled XLA graph.

Data Structures for XLA Integration:

  - AgentParams : A dataclass holding network_params , actor_params , and critic_params cleanrl/ppo_atari_envpool_xla_jax_scan.py 171-174

  - Storage : A JAX-compatible dataclass for rollouts including obs , actions , logprobs , dones , values , advantages , returns , and rewards cleanrl/ppo_atari_envpool_xla_jax_scan.py 178-186

  - EpisodeStatistics : Tracks episode_returns and episode_lengths across steps within the XLA scan cleanrl/ppo_atari_envpool_xla_jax_scan.py 190-194

Sources: cleanrl/ppo_atari_envpool_xla_jax_scan.py170-196

### Advanced Features

#### JAX Scan Optimization

The `ppo_atari_envpool_xla_jax_scan.py` implementation uses JAX's scan operation to optimize the training loop. This allows the entire rollout loop to be JIT-compiled as a single operation.

GAE Computation via Scan:
CleanRL implements GAE using `jax.lax.scan` in reverse to compute advantages efficiently.

```

```

Sources: tests/test_jax_compute_gae.py20-27 cleanrl/ppo_atari_envpool_xla_jax_scan.py330-352

#### Performance Considerations

When running EnvPool-based algorithms, specific configurations are required to handle memory and determinism:

  - Memory Management : To prevent JAX from pre-allocating all GPU memory, CleanRL sets XLA_PYTHON_CLIENT_MEM_FRACTION cleanrl/ppo_atari_envpool_xla_jax_scan.py 23

  - Determinism : Specific XLA flags are set for deterministic reductions cleanrl/ppo_atari_envpool_xla_jax_scan.py 25-26

  - Speedups : ppo_atari_envpool.py (PyTorch) provides a baseline speedup via C++ vectorization. ppo_atari_envpool_xla_jax_scan.py (JAX) provides maximum throughput by running the environment and policy updates inside the same XLA device context.

Sources: cleanrl/ppo_atari_envpool_xla_jax_scan.py22-26 tests/test_envpool.py4-41

### Testing

CleanRL includes automated tests to verify EnvPool integrations:

  - test_ppo_atari_envpool : Verifies the PyTorch Atari implementation tests/test_envpool.py 4-9

  - test_ppo_rnd_envpool : Verifies Random Network Distillation with EnvPool tests/test_envpool.py 12-17

  - test_ppo_atari_envpool_xla_jax_scan : Verifies the high-performance JAX implementation tests/test_envpool.py 28-33

Sources: tests/test_envpool.py1-42



#### On this page

  - EnvPool Integration
  - Purpose and Scope
  - Overview of EnvPool
  - System Architecture
  - Implementation Details
  - Creating EnvPool Environments
  - JAX-specific Integration
  - Advanced Features
  - JAX Scan Optimization
  - Performance Considerations
  - Testing

$!/$$/$
