> 来源: [https://deepwiki.com/Toni-SM/skrl/1-overview](https://deepwiki.com/Toni-SM/skrl/1-overview)
> DeepWiki Toni-SM/skrl | Last indexed: 17 August 2026 (3cdc7f

# Overview

  Relevant source files 
 - [.github/ISSUE_TEMPLATE/bug_report.yaml](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/.github/ISSUE_TEMPLATE/bug_report.yaml)
 - [.pre-commit-config.yaml](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/.pre-commit-config.yaml)
 - [CHANGELOG.md](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/CHANGELOG.md?plain=1)
 - [README.md](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/README.md?plain=1)
 - [docs/source/_static/imgs/data_tensorboard.jpg](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/_static/imgs/data_tensorboard.jpg)
 - [docs/source/_static/imgs/example_parallel.jpg](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/_static/imgs/example_parallel.jpg)
 - [docs/source/api/config/frameworks.rst](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/api/config/frameworks.rst)
 - [docs/source/conf.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/conf.py)
 - [docs/source/index.rst](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/index.rst)
 - [docs/source/intro/data.rst](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/intro/data.rst)
 - [docs/source/intro/examples.rst](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/intro/examples.rst)
 - [docs/source/intro/getting_started.rst](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/intro/getting_started.rst)
 - [docs/source/intro/installation.rst](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/intro/installation.rst)
 - [docs/source/snippets/data.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/snippets/data.py)
 - [pyproject.toml](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/pyproject.toml)
 - [skrl/__init__.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/__init__.py)
 - [skrl/envs/wrappers/jax/gym_envs.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/envs/wrappers/jax/gym_envs.py)
 - [skrl/envs/wrappers/jax/gymnasium_envs.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/envs/wrappers/jax/gymnasium_envs.py)
 - [skrl/envs/wrappers/jax/pettingzoo_envs.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/envs/wrappers/jax/pettingzoo_envs.py)
 - [skrl/envs/wrappers/torch/gym_envs.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/envs/wrappers/torch/gym_envs.py)
 - [skrl/envs/wrappers/torch/gymnasium_envs.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/envs/wrappers/torch/gymnasium_envs.py)
 - [skrl/envs/wrappers/torch/pettingzoo_envs.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/envs/wrappers/torch/pettingzoo_envs.py)
 - [skrl/envs/wrappers/warp/gymnasium_envs.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/envs/wrappers/warp/gymnasium_envs.py)
 - [skrl/utils/__init__.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/utils/__init__.py)
 
  This document provides an overview of the **skrl** reinforcement learning library architecture, core components, and design principles. It covers the high-level system structure, multi-backend support (PyTorch, JAX, and NVIDIA Warp), and how the major components interact to enable modular RL algorithm implementation.

 For specific implementation details of individual components, see their respective documentation pages: [Installation and Setup](https://deepwiki.com/Toni-SM/skrl/1.1-installation-and-setup), [Quick Start](https://deepwiki.com/Toni-SM/skrl/1.2-quick-start), Agents, Models, Environments, Trainers, Memories, and Multi-Agent Systems.

 
## Library Purpose and Design Philosophy

 **skrl** is an open-source modular library for Reinforcement Learning written in Python and implemented in **PyTorch**, **JAX**, and **NVIDIA Warp**. It is designed with a focus on modularity, readability, simplicity, and transparency of algorithm implementation. The library provides a unified interface for various RL algorithms while supporting multiple ML frameworks and environment interfaces, including NVIDIA Isaac Lab and MuJoCo Playground.

 **Core Design Principles:**

 
 - **Modularity**: Components (Agents, Models, Memories, Trainers) can be mixed and matched independently [docs/source/intro/getting_started.rst96-98](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/intro/getting_started.rst#L96-L98)
 - **Multi-Backend Support**: Full implementations in PyTorch, JAX, and Warp with consistent APIs [docs/source/index.rst37-39](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/index.rst#L37-L39)
 - **Environment Agnostic**: Unified wrappers for diverse simulation platforms like Gymnasium, ManiSkill, and Isaac Lab [docs/source/index.rst40-48](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/index.rst#L40-L48)
 - **Algorithm Transparency**: Clean, readable implementations that avoid "hidden" templates [docs/source/intro/getting_started.rst126-130](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/intro/getting_started.rst#L126-L130)
 
 Sources: [docs/source/index.rst37-58](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/index.rst#L37-L58) [README.md24-35](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/README.md?plain=1#L24-L35) [pyproject.toml4](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/pyproject.toml#L4-L4) [skrl/__init__.py47-50](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/__init__.py#L47-L50)

 
## High-Level System Architecture

 The library follows a layered architecture with clear separation between core components, environment integration, and backend implementations.

 
```

```

 Sources: [docs/source/index.rst101-211](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/index.rst#L101-L211) [docs/source/intro/getting_started.rst44-124](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/intro/getting_started.rst#L44-L124) [pyproject.toml30-52](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/pyproject.toml#L30-L52)

 
## Core Component Abstractions

 The library is built around four primary abstractions that interact to form the RL loop.

 
### 1. Agents

 The `Agent` is the central component implementing the RL algorithm (e.g., PPO, SAC). It handles the optimization loop, action selection, and data tracking. All agents inherit from a base class that defines a uniform interface: `act()`, `record_transition()`, and `update()`.

 
 - **Source:** [docs/source/index.rst117-124](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/index.rst#L117-L124)
 
 
### 2. Models

 Models represent the neural networks (policies and value functions). `skrl` uses a **Mixin** pattern (e.g., `GaussianMixin`, `CategoricalMixin`) to add specific probability distribution logic to user-defined network architectures.

 
 - **Source:** [docs/source/intro/getting_started.rst120-132](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/intro/getting_started.rst#L120-L132)
 
 
### 3. Memories

 Memories are storage components (rollout or replay buffers). The library provides `RandomMemory` which is backend-agnostic in its interface but optimized for the specific ML framework in its implementation.

 
 - **Source:** [docs/source/intro/getting_started.rst102-116](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/intro/getting_started.rst#L102-L116)
 
 
### 4. Trainers

 Trainers orchestrate the interaction between the Agent and the Environment.

 
 - `SequentialTrainer`: Standard single-process training.
 - `ParallelTrainer`: Multi-process training for vectorized environments.
 - `StepTrainer`: Manual control over the training steps.
 - **Source:** [docs/source/index.rst196-202](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/index.rst#L196-L202)
 
 
## Multi-Backend Support

 `skrl` differentiates itself by providing deep integration with three major backends. Configuration is managed globally via `skrl.config`.

 
| Feature | PyTorch | JAX | NVIDIA Warp |
|---|---|---|---|
| Backend Path | skrl.agents.torch | skrl.agents.jax | skrl.agents.warp |
| Optimization | Native Autograd | JIT Compilation (@jax.jit) | Kernel-based (Warp JIT) |
| Distributed | torch.distributed | jax.distributed | Supported via Runner |
| Config Object | skrl.config.torch | skrl.config.jax | skrl.config.warp |

 Sources: [skrl/__init__.py51-183](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/__init__.py#L51-L183) [pyproject.toml30-52](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/pyproject.toml#L30-L52) [CHANGELOG.md19-24](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/CHANGELOG.md?plain=1#L19-L24)

 
## System Entity Mapping

 The following diagram maps high-level library concepts to their specific code entities and file locations.

 
```

```

 Sources: [docs/source/index.rst108-211](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/index.rst#L108-L211) [docs/source/intro/getting_started.rst102-163](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/intro/getting_started.rst#L102-L163)

 
## Installation and Quick Start

 For detailed instructions on setting up the library and running your first experiment, please refer to the child pages:

 
 - **[Installation and Setup](https://deepwiki.com/Toni-SM/skrl/1.1-installation-and-setup)**: Detailed guide on installing backend-specific dependencies (PyTorch, JAX, Warp) and configuring distributed training.
 - **[Quick Start](https://deepwiki.com/Toni-SM/skrl/1.2-quick-start)**: Minimal examples using Gymnasium and MuJoCo Playground to get a training loop running in minutes.
 
 Sources: [docs/source/intro/installation.rst1-45](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/intro/installation.rst#L1-L45) [docs/source/intro/getting_started.rst1-8](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/intro/getting_started.rst#L1-L8)

 
## Key Features Summary

 
 - **Multi-Agent RL**: Support for IPPO and MAPPO [docs/source/index.rst139-149](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/index.rst#L139-L149)
 - **Environment Support**: Wrappers for Gymnasium, ManiSkill, MuJoCo Playground, and Isaac Lab [docs/source/index.rst55-57](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/index.rst#L55-L57)
 - **Logging & Checkpointing**: Integrated TensorBoard and Weights & Biases support [docs/source/intro/data.rst9-105](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/intro/data.rst#L9-L105)
 - **Model Instantiators**: Utilities to programmatically create models from configuration [CHANGELOG.md89-98](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/CHANGELOG.md?plain=1#L89-L98)
 - **Mixed Precision**: Support for Automatic Mixed Precision (AMP) in PyTorch [CHANGELOG.md93](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/CHANGELOG.md?plain=1#L93-L93)
 
 Sources: [CHANGELOG.md16-34](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/CHANGELOG.md?plain=1#L16-L34) [pyproject.toml1-29](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/pyproject.toml#L1-L29)
