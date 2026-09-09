> 来源: [https://deepwiki.com/hill-a/stable-baselines/2-getting-started](https://deepwiki.com/hill-a/stable-baselines/2-getting-started)
> DeepWiki hill-a/stable-baselines | Last indexed: 22 June 2025 (45beb2

# Getting Started

  Relevant source files 
 - [.travis.yml](https://github.com/hill-a/stable-baselines/blob/45beb246/.travis.yml)
 - [Dockerfile](https://github.com/hill-a/stable-baselines/blob/45beb246/Dockerfile)
 - [Makefile](https://github.com/hill-a/stable-baselines/blob/45beb246/Makefile)
 - [README.md](https://github.com/hill-a/stable-baselines/blob/45beb246/README.md?plain=1)
 - [docs/conf.py](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/conf.py)
 - [docs/guide/algos.rst](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/guide/algos.rst)
 - [docs/guide/examples.rst](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/guide/examples.rst)
 - [docs/guide/install.rst](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/guide/install.rst)
 - [docs/index.rst](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/index.rst)
 - [scripts/build_docker.sh](https://github.com/hill-a/stable-baselines/blob/45beb246/scripts/build_docker.sh)
 - [scripts/run_docker_cpu.sh](https://github.com/hill-a/stable-baselines/blob/45beb246/scripts/run_docker_cpu.sh)
 - [scripts/run_docker_gpu.sh](https://github.com/hill-a/stable-baselines/blob/45beb246/scripts/run_docker_gpu.sh)
 
  This document provides an overview of how to get started with Stable Baselines, covering the essential concepts, installation approaches, and basic workflow for training reinforcement learning agents. This page introduces the core system architecture and guides you through your first steps.

 For detailed installation instructions including platform-specific considerations and Docker setup, see [Installation](https://deepwiki.com/hill-a/stable-baselines/2.1-installation). For complete examples and advanced usage patterns, see [Basic Usage](https://deepwiki.com/hill-a/stable-baselines/2.2-basic-usage).

 
## What is Stable Baselines

 Stable Baselines is an improved implementation of reinforcement learning algorithms based on OpenAI Baselines. It provides a unified, sklearn-like interface for training RL agents with state-of-the-art algorithms including PPO2, A2C, DQN, DDPG, SAC, TD3, and specialized extensions like HER and GAIL.

 **Key Features:**

 
 - Unified structure across all algorithms via `BaseRLModel`
 - Comprehensive documentation and testing
 - Support for custom environments and policies
 - Vectorized environment processing
 - TensorBoard integration and monitoring tools
 - Docker containers for reproducible environments
 
 **Important Note:** This package is in maintenance mode. For active development, use [Stable-Baselines3](https://github.com/hill-a/stable-baselines/blob/45beb246/Stable-Baselines3)

 Sources: [README.md9-16](https://github.com/hill-a/stable-baselines/blob/45beb246/README.md?plain=1#L9-L16) [docs/index.rst9-33](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/index.rst#L9-L33)

 
## System Architecture Overview

 
```

```

 This architecture provides a clean separation between algorithms, policies, environments, and infrastructure components, enabling flexible composition and extensibility.

 Sources: [stable_baselines/__init__.py](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/__init__.py) [README.md159-183](https://github.com/hill-a/stable-baselines/blob/45beb246/README.md?plain=1#L159-L183) [docs/guide/algos.rst15-30](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/guide/algos.rst#L15-L30)

 
## Basic Workflow and Code Entities

 
```

```

 The workflow follows a standard pattern: environment setup → model configuration → training → evaluation/usage. Each step involves specific Stable Baselines classes and functions.

 Sources: [README.md109-142](https://github.com/hill-a/stable-baselines/blob/45beb246/README.md?plain=1#L109-L142) [docs/guide/examples.rst58-89](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/guide/examples.rst#L58-L89)

 
## Prerequisites Overview

 Stable Baselines requires specific system dependencies and Python packages:

 
| Component | Requirement | Purpose |
|---|---|---|
| Python | 3.5+ with dev headers | Core runtime |
| TensorFlow | 1.8.0 - 1.15.0 | Neural network backend |
| OpenMPI | System package | Multi-processing for DDPG, PPO1, TRPO, GAIL |
| CMake | System package | Building dependencies |
| zlib | System package | Compression support |

 **Platform-Specific Dependencies:**

 
 - **Ubuntu**: `cmake libopenmpi-dev python3-dev zlib1g-dev`
 - **macOS**: `cmake openmpi` (via Homebrew)
 - **Windows**: Anaconda recommended, MPI for Windows optional
 
 Sources: [README.md68-89](https://github.com/hill-a/stable-baselines/blob/45beb246/README.md?plain=1#L68-L89) [docs/guide/install.rst6-46](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/guide/install.rst#L6-L46)

 
## Installation Methods

 Stable Baselines offers multiple installation approaches:

 
### 1. PyPI Installation (Recommended for most users)

 
```

```

 
### 2. Docker Installation (Recommended for consistent environments)

 
```

```

 
### 3. Development Installation

 
```

```

 The MPI installation includes algorithms that use multi-processing: DDPG, GAIL, PPO1, and TRPO. The basic installation supports PPO2, A2C, DQN, SAC, TD3, ACER, ACKTR, and HER.

 Sources: [README.md91-102](https://github.com/hill-a/stable-baselines/blob/45beb246/README.md?plain=1#L91-L102) [docs/guide/install.rst56-100](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/guide/install.rst#L56-L100)

 
## Quick Start Example

 Here's the minimal code to train and use a PPO2 agent:

 
```

```

 This example demonstrates the core classes:

 
 - `MlpPolicy`: Multi-layer perceptron policy network
 - `PPO2`: Proximal Policy Optimization algorithm
 - `model.learn()`: Training method
 - `model.predict()`: Action prediction method
 
 Sources: [README.md109-132](https://github.com/hill-a/stable-baselines/blob/45beb246/README.md?plain=1#L109-L132)

 
## Available Algorithms and Capabilities

 
| Algorithm | Type | Continuous Actions | Discrete Actions | Recurrent | Multi-Processing |
|---|---|---|---|---|---|
| PPO2 | On-Policy | ✓ | ✓ | ✓ | ✓ |
| A2C | On-Policy | ✓ | ✓ | ✓ | ✓ |
| DQN | Off-Policy | ✗ | ✓ | ✗ | ✗ |
| DDPG | Off-Policy | ✓ | ✗ | ✗ | ✓ (MPI) |
| SAC | Off-Policy | ✓ | ✗ | ✗ | ✗ |
| TD3 | Off-Policy | ✓ | ✗ | ✗ | ✗ |
| HER | Extension | ✓ | ✓ | ✗ | ✗ |
| GAIL | Extension | ✓ | ✓ | ✗ | ✓ (MPI) |

 **Policy Types:**

 
 - `MlpPolicy`: Feed-forward networks for vector observations
 - `CnnPolicy`: Convolutional networks for image observations
 - `LstmPolicy`: Recurrent networks for sequence data
 - Custom policies: User-defined architectures
 
 Sources: [README.md161-180](https://github.com/hill-a/stable-baselines/blob/45beb246/README.md?plain=1#L161-L180) [docs/guide/algos.rst15-30](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/guide/algos.rst#L15-L30)

 
## Environment Integration

 Stable Baselines supports various environment configurations:

 
```

```

 Most algorithms automatically wrap single environments with `DummyVecEnv`. For multi-processing, use `SubprocVecEnv` or the `make_vec_env()` helper function.

 Sources: [docs/guide/examples.rst103-147](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/guide/examples.rst#L103-L147) [stable_baselines/common/vec_env/](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/common/vec_env/)

 
## Next Steps

 
 - **Installation**: Follow the detailed [Installation](https://deepwiki.com/hill-a/stable-baselines/2.1-installation) guide for your platform
 - **Basic Usage**: Explore comprehensive examples in [Basic Usage](https://deepwiki.com/hill-a/stable-baselines/2.2-basic-usage)
 - **Algorithm Selection**: Review [Core Algorithms](https://deepwiki.com/hill-a/stable-baselines/3-core-algorithms) for algorithm-specific guidance
 - **Environment Setup**: Learn about [Environment Management](https://deepwiki.com/hill-a/stable-baselines/5-environment-management) for custom environments
 - **Training Monitoring**: Set up [Training and Monitoring](https://deepwiki.com/hill-a/stable-baselines/6-training-and-monitoring) for tracking progress
 
 For immediate experimentation, try the [Google Colab notebooks](https://github.com/hill-a/stable-baselines/blob/45beb246/Google Colab notebooks) which provide ready-to-run examples in a browser environment.

 Sources: [README.md145-157](https://github.com/hill-a/stable-baselines/blob/45beb246/README.md?plain=1#L145-L157) [docs/guide/examples.rst6-31](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/guide/examples.rst#L6-L31)
