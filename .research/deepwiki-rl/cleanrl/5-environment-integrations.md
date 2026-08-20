# deepwiki cleanrl §5 environment-integrations
> 来源: https://deepwiki.com/vwxyzjn/cleanrl/5-environment-integrations

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

## Environment Integrations

Relevant source files

  - README.md

  - docs/get-started/installation.md

  - docs/index.md

  - docs/rl-algorithms/overview.md

  - docs/rl-algorithms/ppo.md

  - mkdocs.yml

### Purpose and Scope

This document provides an overview of how CleanRL integrates with different reinforcement learning environment libraries. CleanRL supports six major environment families, each requiring specific preprocessing pipelines, wrappers, and dependencies. For detailed implementation specifics of each environment type, see the child pages: Classic Control, Atari Games, MuJoCo and Continuous Control, Procgen and Generalization, Multi-agent Environments, and Isaac Gym Integration. For high-performance vectorized environments, see EnvPool Integration.

Sources: README.md1-29 mkdocs.yml31-63 docs/index.md1-40

### Supported Environment Types

CleanRL supports the following environment families, each with specific installation requirements and algorithm variants:

| Environment Type | Library | Action Space | Observation Space | Installation Extra | Primary Use Case |
| Classic Control | gymnasium | Discrete/Box | Box (low-dim) | Core dependency | Simple testing, debugging |
| Atari | gymnasium + ale-py | Discrete | Box (84×84×4) | [atari] | Discrete action, visual input |
| MuJoCo | gymnasium + mujoco | Box (continuous) | Box (low-dim) | [mujoco] | Continuous control |
| dm_control | shimmy + dm_control | Box (continuous) | Box (low-dim) | [dm_control] | Physics simulation |
| Procgen | procgen | Discrete | Box (64×64×3) | [procgen] | Generalization testing |
| PettingZoo | pettingzoo | Discrete | Box (84×84×4) | [pettingzoo] | Multi-agent scenarios |
| Isaac Gym | isaacgym | Box (continuous) | Box (low-dim) | Manual install | GPU-accelerated physics |
| EnvPool | envpool | Discrete | Box (84×84×4) | [envpool] | High-throughput training |

Sources: README.md99-126 docs/get-started/installation.md48-67 docs/rl-algorithms/overview.md5-33

### Installation Architecture

CleanRL uses optional dependency groups defined in `pyproject.toml` to manage environment-specific dependencies. Each environment type requires a separate installation extra:

```

```

Installation pattern:

```

```

Sources: README.md76-93 docs/get-started/installation.md48-67

### Algorithm Variant Naming Convention

CleanRL uses a systematic file naming convention to indicate environment-specific algorithm variants. The pattern follows: `{algorithm}_{environment_type}_{optional_modifiers}.py`

```

```

Naming components:

| Component | Purpose | Examples |
| Algorithm | Base RL algorithm | ppo , dqn , sac , ddpg , td3 |
| Environment Type | Target environment family | atari , continuous_action , procgen , pettingzoo_ma_atari |
| Modifiers | Additional features | lstm , envpool , multigpu , isaacgym , jax |

Sources: README.md135-167 docs/rl-algorithms/ppo.md24-35 docs/rl-algorithms/overview.md5-33

### Environment Wrapper Architecture

All CleanRL environment integrations follow a common pattern: environment creation through wrapper chains. Each environment type uses specific wrappers for preprocessing.

```

```

Sources: docs/rl-algorithms/ppo.md174-183 README.md111-116

### Environment-Specific make_env Functions

Each algorithm variant implements a `make_env` function that returns a thunk (zero-argument callable) for lazy environment creation. This pattern enables proper environment seeding and video capture.

#### Classic Control Pattern

The standard PPO implementation for classic control tasks uses a basic wrapper setup.

```

```

#### Atari Pattern

Atari implementations include a standard set of wrappers defined in the script to match the "Nature DQN" preprocessing.

```

```

Sources: docs/rl-algorithms/ppo.md174-183 README.md20-21

### Environment Integration Mapping

The following table maps CleanRL algorithm files to their supported environment types:

| Algorithm Files | Classic Control | Atari | MuJoCo | dm_control | Procgen | PettingZoo | Isaac Gym | EnvPool |
| ppo.py | ✓ |  |  |  |  |  |  |  |
| ppo_atari.py |  | ✓ |  |  |  |  |  |  |
| ppo_continuous_action.py |  |  | ✓ | ✓ |  |  |  |  |
| ppo_procgen.py |  |  |  |  | ✓ |  |  |  |
| ppo_pettingzoo_ma_atari.py |  |  |  |  |  | ✓ |  |  |
| ppo_continuous_action_isaacgym.py |  |  |  |  |  |  | ✓ |  |
| ppo_atari_envpool.py |  |  |  |  |  |  |  | ✓ |
| ppo_atari_lstm.py |  | ✓ |  |  |  |  |  |  |
| dqn.py | ✓ |  |  |  |  |  |  |  |
| dqn_atari.py |  | ✓ |  |  |  |  |  |  |
| sac_continuous_action.py |  |  | ✓ |  |  |  |  |  |
| sac_atari.py |  | ✓ |  |  |  |  |  |  |

Sources: docs/rl-algorithms/ppo.md24-35 docs/rl-algorithms/overview.md5-33 README.md135-167

### Action and Observation Space Handling

CleanRL algorithms automatically detect and handle different space types.

```

```

Sources: docs/rl-algorithms/ppo.md43-45 README.md21

### Environment-Specific Implementation Details

Each environment type requires specific preprocessing and implementation details:

#### Classic Control

  - Observation : Box space with low-dimensional features.

  - Action : Discrete or Box.

  - Preprocessing : Minimal ( RecordEpisodeStatistics only).

  - Network : Simple MLP.

  - See : Classic Control

#### Atari Games

  - Observation : Box (210, 160, 3) RGB images.

  - Action : Discrete.

  - Preprocessing : NoopReset , MaxAndSkip , EpisodicLife , FireReset , ClipReward , Resize , GrayScale , FrameStack .

  - Network : Nature CNN (3 conv layers).

  - See : Atari Games

#### MuJoCo and Continuous Control

  - Observation : Box space with proprioceptive state.

  - Action : Box (continuous).

  - Preprocessing : NormalizeObservation and NormalizeReward wrappers.

  - Network : Separate MLPs for actor/critic with Gaussian policy.

  - See : MuJoCo and Continuous Control

#### Procgen

  - Observation : Box (64, 64, 3) RGB images.

  - Action : Discrete.

  - Preprocessing : Handled internally by procgen .

  - Network : IMPALA-style residual network.

  - See : Procgen and Generalization

#### PettingZoo Multi-Agent

  - Observation : Per-agent observations.

  - Action : Per-agent discrete actions.

  - Preprocessing : SuperSuit wrappers for vectorization and Atari-like preprocessing.

  - See : Multi-agent Environments

#### Isaac Gym

  - Observation : GPU-resident observation tensors.

  - Action : Box (continuous).

  - Preprocessing : High-speed parallel environment vectorization on GPU.

  - See : Isaac Gym Integration

Sources: docs/rl-algorithms/ppo.md24-35 README.md104-126



#### On this page

  - Environment Integrations
  - Purpose and Scope
  - Supported Environment Types
  - Installation Architecture
  - Algorithm Variant Naming Convention
  - Environment Wrapper Architecture
  - Environment-Specific make_env Functions
  - Classic Control Pattern
  - Atari Pattern
  - Environment Integration Mapping
  - Action and Observation Space Handling
  - Environment-Specific Implementation Details
  - Classic Control
  - Atari Games
  - MuJoCo and Continuous Control
  - Procgen
  - PettingZoo Multi-Agent
  - Isaac Gym

$!/$$/$
