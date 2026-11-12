<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/gym-aloha · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [pyproject.toml](pyproject.toml)

</details>



This document provides a comprehensive introduction to the gym-aloha repository, explaining its purpose as a Gymnasium environment for ALOHA bimanual robotics simulation, key architectural components, and available features. For detailed installation instructions, see [Installation and Setup](#1.1). For hands-on usage examples, see [Quick Start Guide](#1.2).

## Purpose and Scope

The `gym-aloha` repository implements a Gymnasium-compatible reinforcement learning environment for simulating ALOHA bimanual robot manipulation tasks. This environment enables researchers and developers to train and evaluate robotic policies on complex bimanual manipulation scenarios using MuJoCo physics simulation.

**Sources:** [README.md:1-3](), [pyproject.toml:2-4]()

## System Overview

gym-aloha is designed as a modular robotics simulation environment that integrates multiple open-source components to provide a comprehensive bimanual manipulation platform. The system serves as a bridge between high-level reinforcement learning frameworks and detailed physics simulation.

### Primary Components

The system consists of several key components:

- **Environment Interface**: Gymnasium-compatible API for reinforcement learning integration
- **Physics Simulation**: MuJoCo-based realistic physics and rendering
- **Robot Models**: Detailed ViperX 300S bimanual robot configurations  
- **Task Definitions**: Structured manipulation tasks with reward systems
- **Asset Management**: 3D models, textures, and scene configurations

**Sources:** [README.md:48-66](), [pyproject.toml:24-29]()

## High-Level Architecture

The following diagram illustrates the system's main architectural components and their relationships:

### System Architecture Overview

```mermaid
graph TB
    subgraph "RL Interface Layer"
        GYMNASIUM["gymnasium.make()"]
        ENV_REGISTRY["Environment Registration"]
        ALOHA_INSERTION["gym_aloha/AlohaInsertion-v0"]
        ALOHA_TRANSFER["gym_aloha/AlohaTransferCube-v0"]
    end
    
    subgraph "Core Environment"
        ALOHA_ENV["AlohaEnv Class"]
        OBS_SPACE["observation_space"]
        ACTION_SPACE["action_space"]
        RESET_METHOD["reset()"]
        STEP_METHOD["step()"]
        RENDER_METHOD["render()"]
    end
    
    subgraph "Physics Backend"
        DM_CONTROL["dm_control.Environment"]
        MUJOCO_ENGINE["MuJoCo Physics Engine"]
        XML_MODELS["XML Scene Models"]
        STL_ASSETS["STL Mesh Assets"]
    end
    
    subgraph "Task Implementation"
        INSERTION_TASK["InsertionTask Logic"]
        TRANSFER_TASK["TransferCubeTask Logic"]
        REWARD_CALC["Reward Calculation"]
        STATE_MANAGEMENT["State Management"]
    end
    
    GYMNASIUM --> ENV_REGISTRY
    ENV_REGISTRY --> ALOHA_INSERTION
    ENV_REGISTRY --> ALOHA_TRANSFER
    ALOHA_INSERTION --> ALOHA_ENV
    ALOHA_TRANSFER --> ALOHA_ENV
    
    ALOHA_ENV --> OBS_SPACE
    ALOHA_ENV --> ACTION_SPACE
    ALOHA_ENV --> RESET_METHOD
    ALOHA_ENV --> STEP_METHOD
    ALOHA_ENV --> RENDER_METHOD
    
    ALOHA_ENV --> DM_CONTROL
    DM_CONTROL --> MUJOCO_ENGINE
    MUJOCO_ENGINE --> XML_MODELS
    XML_MODELS --> STL_ASSETS
    
    ALOHA_ENV --> INSERTION_TASK
    ALOHA_ENV --> TRANSFER_TASK
    INSERTION_TASK --> REWARD_CALC
    TRANSFER_TASK --> REWARD_CALC
    REWARD_CALC --> STATE_MANAGEMENT
```

**Sources:** [README.md:23-45](), [pyproject.toml:24-29]()

### Core Implementation Structure

The following diagram shows the specific code entities and their relationships within the implementation:

```mermaid
graph TB
    subgraph "Package Structure"
        INIT_PY["gym_aloha/__init__.py"]
        ENV_PY["gym_aloha/env.py"]
        PYPROJECT["pyproject.toml"]
    end
    
    subgraph "Environment Registration"
        REGISTER_FUNC["gymnasium.register()"]
        ENTRY_POINT["entry_point: AlohaEnv"]
        MAX_STEPS["max_episode_steps: 300"]
        NONDETERMINISTIC["nondeterministic: True"]
    end
    
    subgraph "AlohaEnv Implementation"
        ALOHA_ENV_CLASS["class AlohaEnv(gymnasium.Env)"]
        INIT_METHOD["__init__(task, obs_type, render_mode)"]
        OBSERVATION_SPACE["Box observation_space"]
        ACTION_SPACE["Box action_space (14-dim)"]
        RESET_IMPL["reset() -> observation, info"]
        STEP_IMPL["step(action) -> obs, reward, term, trunc, info"]
        RENDER_IMPL["render() -> rgb_array"]
    end
    
    subgraph "Dependencies"
        MUJOCO_DEP["mujoco ^2.3.7"]
        GYMNASIUM_DEP["gymnasium >=0.29.1"]
        DMCONTROL_DEP["dm-control >=1.0.14"]
        IMAGEIO_DEP["imageio >=2.34.0"]
    end
    
    INIT_PY --> REGISTER_FUNC
    REGISTER_FUNC --> ENTRY_POINT
    REGISTER_FUNC --> MAX_STEPS
    REGISTER_FUNC --> NONDETERMINISTIC
    
    ENTRY_POINT --> ALOHA_ENV_CLASS
    ENV_PY --> ALOHA_ENV_CLASS
    
    ALOHA_ENV_CLASS --> INIT_METHOD
    ALOHA_ENV_CLASS --> OBSERVATION_SPACE
    ALOHA_ENV_CLASS --> ACTION_SPACE
    ALOHA_ENV_CLASS --> RESET_IMPL
    ALOHA_ENV_CLASS --> STEP_IMPL
    ALOHA_ENV_CLASS --> RENDER_IMPL
    
    PYPROJECT --> MUJOCO_DEP
    PYPROJECT --> GYMNASIUM_DEP
    PYPROJECT --> DMCONTROL_DEP
    PYPROJECT --> IMAGEIO_DEP
    
    ALOHA_ENV_CLASS --> DMCONTROL_DEP
    ALOHA_ENV_CLASS --> MUJOCO_DEP
```

**Sources:** [pyproject.toml:21-38](), [README.md:87-93]()

## Available Tasks

The environment provides two primary bimanual manipulation tasks:

| Task Name | Environment ID | Description | Max Reward |
|-----------|---------------|-------------|------------|
| **Insertion Task** | `gym_aloha/AlohaInsertion-v0` | Insert peg into socket using coordinated bimanual manipulation | 4 points |
| **Transfer Cube Task** | `gym_aloha/AlohaTransferCube-v0` | Transfer cube from right gripper to left gripper | 4 points |

### Task Characteristics

Both tasks feature:
- **Randomized initial states** for arms and objects
- **Progressive reward structure** encouraging proper manipulation sequences  
- **Success criteria** based on achieving maximum reward
- **300-step episode limit** with early termination on success

For detailed task mechanics and reward structures, see [Tasks and Simulations](#3).

**Sources:** [README.md:51-84]()

## Key Features

The gym-aloha environment provides several important capabilities:

### Observation Modes
- **`pixels`**: RGB camera observations from multiple viewpoints
- **`pixels_agent_pos`**: Combined visual and proprioceptive observations
- **Configurable resolution**: Customizable observation and visualization dimensions

### Action Interface  
- **14-dimensional continuous action space**: 12 joint positions + 2 gripper controls
- **Absolute joint positioning**: Direct joint angle control for precise manipulation
- **Normalized gripper control**: 0 (closed) to 1 (open) gripper positions

### Rendering Capabilities
- **RGB array output**: Compatible with video recording and visualization
- **Multiple camera angles**: Various viewpoints for comprehensive observation
- **GPU acceleration support**: EGL-based GPU rendering for performance

**Sources:** [README.md:55-66](), [README.md:87-106]()

## Technical Dependencies

The system is built on a foundation of established robotics and machine learning libraries:

### Core Dependencies
- **Python 3.10+**: Modern Python features and performance
- **MuJoCo 2.3.7+**: Physics simulation and rendering engine  
- **Gymnasium 0.29.1+**: Standard RL environment interface
- **dm-control 1.0.14+**: DeepMind's control suite utilities
- **ImageIO 2.34.0+**: Video recording and image processing

### Development Infrastructure
- **Poetry**: Dependency management and packaging
- **Ruff**: Code formatting and linting  
- **Pre-commit hooks**: Automated code quality checks
- **pytest**: Testing framework with coverage reporting

**Sources:** [pyproject.toml:24-33](), [pyproject.toml:41-77]()

## Next Steps

- For installation instructions and environment setup, see [Installation and Setup](#1.1)
- For basic usage examples and API introduction, see [Quick Start Guide](#1.2)  
- For detailed environment implementation, see [Core Environment Implementation](#2)
- For task-specific information, see [Tasks and Simulations](#3)
- For contributing guidelines, see [Development Workflow](#5)

---

