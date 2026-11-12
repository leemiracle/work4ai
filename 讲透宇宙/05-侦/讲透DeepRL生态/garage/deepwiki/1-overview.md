> 来源: [https://deepwiki.com/rlworkgroup/garage/1-overview](https://deepwiki.com/rlworkgroup/garage/1-overview)
> DeepWiki rlworkgroup/garage | Last indexed: 25 April 2025 (2d5948

# Overview

  Relevant source files 
 - [.editorconfig](https://github.com/rlworkgroup/garage/blob/2d594803/.editorconfig)
 - [.github/workflows/ci-release-2021.03.yml](https://github.com/rlworkgroup/garage/blob/2d594803/.github/workflows/ci-release-2021.03.yml)
 - [.mdlrc](https://github.com/rlworkgroup/garage/blob/2d594803/.mdlrc)
 - [README.md](https://github.com/rlworkgroup/garage/blob/2d594803/README.md?plain=1)
 - [docs/index.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/index.md?plain=1)
 - [docs/user/algo_bc.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_bc.md?plain=1)
 - [docs/user/algo_cem.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_cem.md?plain=1)
 - [docs/user/algo_ddpg.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_ddpg.md?plain=1)
 - [docs/user/algo_dqn.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_dqn.md?plain=1)
 - [docs/user/algo_erwr.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_erwr.md?plain=1)
 - [docs/user/algo_maml.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_maml.md?plain=1)
 - [docs/user/algo_mtppo.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_mtppo.md?plain=1)
 - [docs/user/algo_mttrpo.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_mttrpo.md?plain=1)
 - [docs/user/algo_pearl.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_pearl.md?plain=1)
 - [docs/user/algo_ppo.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_ppo.md?plain=1)
 - [docs/user/algo_rl2.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_rl2.md?plain=1)
 - [docs/user/algo_sac.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_sac.md?plain=1)
 - [docs/user/algo_td3.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_td3.md?plain=1)
 - [docs/user/algo_trpo.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_trpo.md?plain=1)
 - [docs/user/algo_vpg.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_vpg.md?plain=1)
 - [docs/user/images/dqn_plots.png](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/images/dqn_plots.png)
 - [docs/user/images/numpy.png](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/images/numpy.png)
 - [docs/user/references.bib](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/references.bib)
 
  Garage is a toolkit for developing and evaluating reinforcement learning algorithms, accompanied by a comprehensive library of state-of-the-art implementations built using that toolkit. It provides a modular, flexible framework for RL research with support for multiple deep learning frameworks and a wide range of algorithms.

 This document provides a high-level overview of the garage framework, its architecture, components, and capabilities. For installation instructions, see [Installation](https://deepwiki.com/rlworkgroup/garage/1.1-installation). For getting started with experiments, see [Quick Start Guide](https://deepwiki.com/rlworkgroup/garage/1.2-quick-start-guide).

 
## Key Features

 Garage offers a variety of features that make it a powerful tool for RL research:

 
 - Modular design for composable neural network models, policies, and value functions
 - High-performance samplers for efficient data collection
 - Support for multiple frameworks (PyTorch, TensorFlow, and NumPy)
 - Comprehensive experiment management with logging and reproducibility tools
 - Extensive algorithm library covering various RL paradigms
 - Built-in support for popular environment suites (OpenAI Gym, MuJoCo, etc.)
 - Reproducible experiment snapshots and resuming
 
 Sources: [README.md9-26](https://github.com/rlworkgroup/garage/blob/2d594803/README.md?plain=1#L9-L26) [docs/index.md3-8](https://github.com/rlworkgroup/garage/blob/2d594803/docs/index.md?plain=1#L3-L8)

 
## System Architecture

 Garage is designed with modularity and extensibility in mind. Here's a high-level view of the system architecture:

 
```

```

 Sources: [README.md13-26](https://github.com/rlworkgroup/garage/blob/2d594803/README.md?plain=1#L13-L26)

 The core architecture consists of several key systems:

 
 - **Experiment System**: Manages experiment execution, logging, and reproducibility
 - **Trainer**: Coordinates the training process between algorithms and samplers
 - **Samplers**: Collect experience from environments
 - **Algorithms**: Implement RL methods using experiences to update policies
 - **Environments**: Interface with reinforcement learning environments
 - **Policies & Value Functions**: Represent agent behaviors and value estimations
 
 For more details about specific components, see [Core Architecture](https://deepwiki.com/rlworkgroup/garage/2-core-architecture).

 
## Framework Support

 Garage supports multiple frameworks for implementing RL algorithms:

 
```

```

 Sources: [README.md90-108](https://github.com/rlworkgroup/garage/blob/2d594803/README.md?plain=1#L90-L108)

 
 - **PyTorch** (`garage.torch`): Modern implementation supporting most algorithms
 - **TensorFlow** (`garage.tf`): Implementation of various algorithms
 - **NumPy** (`garage.np`): Framework-independent algorithms that don't require deep learning
 
 
## Supported Algorithms

 Garage implements a wide range of reinforcement learning algorithms across different categories:

 
| Category | Algorithms | Frameworks |
|---|---|---|
| On-Policy | REINFORCE (VPG), TRPO, PPO, TNPG, NPO, REPS | PyTorch, TensorFlow |
| Off-Policy | DQN, DDPG, TD3, SAC | PyTorch, TensorFlow |
| Meta-RL | MAML, RL², PEARL | PyTorch, TensorFlow |
| Multi-Task | MT-PPO, MT-TRPO, MT-SAC | PyTorch, TensorFlow |
| Evolutionary | CEM, CMA-ES | NumPy |
| Imitation Learning | Behavioral Cloning | PyTorch |

 Sources: [README.md61-88](https://github.com/rlworkgroup/garage/blob/2d594803/README.md?plain=1#L61-L88)

 
## Algorithm Hierarchy

 Algorithms in garage are organized in a hierarchical structure:

 
```

```

 Sources: [README.md61-88](https://github.com/rlworkgroup/garage/blob/2d594803/README.md?plain=1#L61-L88) [docs/user/algo_ppo.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_ppo.md?plain=1) [docs/user/algo_trpo.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_trpo.md?plain=1) [docs/user/algo_vpg.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_vpg.md?plain=1) [docs/user/algo_sac.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_sac.md?plain=1)

 
## Experiment Workflow

 A typical garage experiment follows this workflow:

 
```

```

 Sources: [README.md37-48](https://github.com/rlworkgroup/garage/blob/2d594803/README.md?plain=1#L37-L48)

 The framework simplifies the experiment workflow through:

 
 - **Experiment definition**: Using the `@wrap_experiment` decorator to set up the experiment environment
 - **Trainer setup**: Configuring the trainer with an algorithm and environment
 - **Training execution**: Running the training loop, which handles: 
 - Sample collection from environments
 - Policy/value function updates via the algorithm
 - Logging and metrics tracking
 - Periodic snapshots for experiment resumption
 
 
## Core Components

 
### Trainers

 Trainers manage the main training loop, coordinating between algorithms, samplers, and logging:

 
 - `Trainer`: Base trainer class for PyTorch algorithms
 - `TFTrainer`: Trainer for TensorFlow algorithms
 
 These handle the orchestration of training iterations, evaluation, and experiment state management.

 
### Samplers

 Samplers are responsible for collecting experiences from environments:

 
 - `LocalSampler`: Collects samples serially on a single process
 - `RaySampler`: Distributes sampling across multiple processes using Ray
 - `MultiprocessingSampler`: Parallel sampling using Python's multiprocessing
 
 
### Algorithms

 Algorithms implement specific RL methods that update policies based on collected experiences:

 
 - **Policy Gradient**: VPG, TRPO, PPO
 - **Q-Learning**: DQN, DDQN
 - **Actor-Critic**: DDPG, TD3, SAC
 - **Meta-Learning**: MAML, RL², PEARL
 - **Evolutionary**: CEM, CMA-ES
 
 
### Policies

 Policies represent the agent's decision-making mechanism:

 
 - `Policy`: Base class for all policies
 - `StochasticPolicy`: Policies that output probability distributions
 - `DeterministicPolicy`: Policies that output deterministic actions
 - Various specialized policies for different frameworks and algorithms
 
 
### Value Functions

 Value functions estimate expected returns or advantages:

 
 - `ValueFunction`: Base class for value functions
 - `QFunction`: Estimates action-value (Q-value)
 - Various implementations for different algorithms and frameworks
 
 
## Reproducibility

 Garage emphasizes reproducible research through:

 
 - Global random seed management
 - Comprehensive experiment logging
 - Environment state snapshotting
 - Experiment resumption capabilities
 - Standardized benchmarking tools
 
 For details on ensuring experiment reproducibility, see [Ensure Your Experiments Are Reproducible](https://github.com/rlworkgroup/garage/blob/2d594803/Ensure Your Experiments Are Reproducible)

 Sources: [README.md116-134](https://github.com/rlworkgroup/garage/blob/2d594803/README.md?plain=1#L116-L134)

 
## Getting Started

 To install garage:

 
```
pip install --user garage
```

 You can run the included examples to get familiar with the framework:

 
```
garage examples
```

 For more detailed instructions, see the [Installation](https://deepwiki.com/rlworkgroup/garage/1.1-installation) and [Quick Start Guide](https://deepwiki.com/rlworkgroup/garage/1.2-quick-start-guide) pages.

 Sources: [README.md31-48](https://github.com/rlworkgroup/garage/blob/2d594803/README.md?plain=1#L31-L48)
