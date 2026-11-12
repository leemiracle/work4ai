> 来源: [https://deepwiki.com/hill-a/stable-baselines/1-overview](https://deepwiki.com/hill-a/stable-baselines/1-overview)
> DeepWiki hill-a/stable-baselines | Last indexed: 22 June 2025 (45beb2

# Overview

  Relevant source files 
 - [README.md](https://github.com/hill-a/stable-baselines/blob/45beb246/README.md?plain=1)
 - [docs/conf.py](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/conf.py)
 - [docs/guide/algos.rst](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/guide/algos.rst)
 - [docs/guide/examples.rst](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/guide/examples.rst)
 - [docs/index.rst](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/index.rst)
 - [docs/misc/changelog.rst](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/misc/changelog.rst)
 - [setup.py](https://github.com/hill-a/stable-baselines/blob/45beb246/setup.py)
 - [stable_baselines/__init__.py](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/__init__.py)
 
  
## Purpose and Scope

 Stable Baselines is a comprehensive reinforcement learning library that provides improved implementations of state-of-the-art RL algorithms based on OpenAI Baselines. This document covers the high-level architecture and core components of the stable-baselines codebase. For specific algorithm details, see [Core Algorithms](https://deepwiki.com/hill-a/stable-baselines/3-core-algorithms). For environment handling specifics, see [Environment Management](https://deepwiki.com/hill-a/stable-baselines/5-environment-management). For training workflows, see [Training and Monitoring](https://deepwiki.com/hill-a/stable-baselines/6-training-and-monitoring).

 The library serves as a production-ready toolkit for reinforcement learning research and applications, emphasizing code quality, documentation, and ease of use with a sklearn-like API interface.

 **Note**: This package is in maintenance mode. Users should migrate to Stable-Baselines3 for active development and support.

 Sources: [README.md1-239](https://github.com/hill-a/stable-baselines/blob/45beb246/README.md?plain=1#L1-L239) [stable_baselines/__init__.py32-34](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/__init__.py#L32-L34) [setup.py48-66](https://github.com/hill-a/stable-baselines/blob/45beb246/setup.py#L48-L66)

 
## High-Level Architecture

 The stable-baselines repository follows a modular architecture organized around three primary layers: algorithm implementations, common infrastructure, and development tooling.

 
```

```

 Sources: [stable_baselines/__init__.py1-35](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/__init__.py#L1-L35) [setup.py120-135](https://github.com/hill-a/stable-baselines/blob/45beb246/setup.py#L120-L135) [README.md159-184](https://github.com/hill-a/stable-baselines/blob/45beb246/README.md?plain=1#L159-L184)

 
## Core Algorithm Implementations

 Stable Baselines implements 12 reinforcement learning algorithms organized into distinct categories based on their learning paradigms and architectural requirements.

 
```

```

 
### Algorithm Import Structure

 The main package conditionally imports algorithms based on dependency availability:

 
| Algorithm Category | Import Condition | Code Location |
|---|---|---|
| Core Algorithms | Always available | stable_baselines/__init__.py4-11 |
| MPI Algorithms | mpi4py installed | stable_baselines/__init__.py19-23 |

 
### Action Space Support Matrix

 
| Algorithm | Box (Continuous) | Discrete | Multi-Processing |
|---|---|---|---|
| A2C | ✓ | ✓ | ✓ |
| DDPG | ✓ | ✗ | ✓ (MPI) |
| DQN | ✗ | ✓ | ✗ |
| PPO2 | ✓ | ✓ | ✓ |
| SAC | ✓ | ✗ | ✗ |
| TD3 | ✓ | ✗ | ✗ |

 Sources: [stable_baselines/__init__.py4-24](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/__init__.py#L4-L24) [README.md161-180](https://github.com/hill-a/stable-baselines/blob/45beb246/README.md?plain=1#L161-L180) [docs/guide/algos.rst15-30](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/guide/algos.rst#L15-L30)

 
## Common Infrastructure Components

 The infrastructure layer provides shared functionality across all algorithm implementations through the `stable_baselines.common` module structure.

 
```

```

 
### Key Infrastructure Classes

 
 - **`BaseRLModel`**: Abstract base class providing common interface for all algorithms
 - **`VecEnv`**: Vectorized environment abstraction enabling parallel environment execution
 - **`Monitor`**: Environment wrapper for episode statistics collection and logging
 - **`BaseCallback`**: Extensible callback system for training monitoring and control
 
 Sources: [README.md241-305](https://github.com/hill-a/stable-baselines/blob/45beb246/README.md?plain=1#L241-L305) [docs/guide/vec_envs.rst](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/guide/vec_envs.rst) [docs/guide/callbacks.rst](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/guide/callbacks.rst)

 
## Package Dependencies and Setup

 The stable-baselines package requires specific dependency management due to TensorFlow compatibility constraints and optional MPI functionality.

 
### Core Dependencies

 
```

```

 
### Installation Configuration

 The setup process includes automatic TensorFlow variant selection based on GPU availability:

 
 - **CPU Installation**: `tensorflow>=1.8.0,<2.0.0`
 - **GPU Installation**: `tensorflow-gpu>=1.8.0,<2.0.0` (when NVIDIA GPU detected)
 - **MPI Support**: Optional `mpi4py` dependency for distributed algorithms
 
 Sources: [setup.py16-45](https://github.com/hill-a/stable-baselines/blob/45beb246/setup.py#L16-L45) [setup.py126-152](https://github.com/hill-a/stable-baselines/blob/45beb246/setup.py#L126-L152) [README.md68-102](https://github.com/hill-a/stable-baselines/blob/45beb246/README.md?plain=1#L68-L102)
