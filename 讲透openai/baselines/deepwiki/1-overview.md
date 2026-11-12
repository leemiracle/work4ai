<!-- source: DeepWiki mcp.deepwiki.com · repo openai/baselines · page 1 Overview · fetched 2026-10-30 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [README.md](README.md)

</details>



OpenAI Baselines is a set of high-quality implementations of reinforcement learning algorithms designed to serve as benchmarks for the research community. This document introduces the key components and architecture of the Baselines library, providing a high-level understanding of how the different parts of the system work together.

## Purpose and Scope

Baselines provides standardized implementations of popular reinforcement learning algorithms with these core objectives:

- Facilitate reproducibility of reinforcement learning research
- Provide reliable benchmark implementations for new algorithm development
- Create a foundation that researchers can build upon and extend
- Offer common tools for environment handling, neural network model creation, and experiment logging

For specific information about installing and using Baselines, see [Getting Started](#2). For details on running experiments, see [Running Experiments](#2.1).

## Repository Structure

```mermaid
graph TD
    subgraph "Main Components"
        Algs["RL Algorithms"]
        Env["Environment Handling"]
        Core["Core Infrastructure"]
        Run["Experiment Runner"]
    end
    
    subgraph "RL Algorithms"
        PPO["baselines.ppo2"]
        DQN["baselines.deepq"]
        A2C["baselines.a2c"]
        TRPO["baselines.trpo_mpi"]
        DDPG["baselines.ddpg"]
        HER["baselines.her"]
        ACKTR["baselines.acktr"]
        ACER["baselines.acer"]
        GAIL["baselines.gail"]
    end
    
    subgraph "Environment Handling"
        VecEnv["baselines.common.vec_env"]
        EnvMakers["Environment Creators"]
        Wrappers["Environment Wrappers"]
    end
    
    subgraph "Core Infrastructure"
        Models["baselines.common.models"]
        Policies["baselines.common.policies"]
        TFUtil["baselines.common.tf_util"]
        Distributions["baselines.common.distributions"]
        Utils["Other Utilities"]
    end
    
    Run -- "imports" --> Algs
    Run -- "creates" --> Env
    Algs -- "uses" --> Core
    Algs -- "interacts with" --> Env
    Env -- "uses" --> Core
```

Sources: [README.md:5-9](), [README.md:132-142]()

## Key Components

### Reinforcement Learning Algorithms

Baselines implements several state-of-the-art reinforcement learning algorithms:

| Algorithm | Package | Description |
|-----------|---------|-------------|
| PPO2 | `baselines.ppo2` | Proximal Policy Optimization (improved version) |
| DQN | `baselines.deepq` | Deep Q-Networks for value-based learning |
| A2C | `baselines.a2c` | Advantage Actor-Critic method |
| DDPG | `baselines.ddpg` | Deep Deterministic Policy Gradient for continuous control |
| ACKTR | `baselines.acktr` | Actor-Critic with Kronecker-Factored Trust Region |
| ACER | `baselines.acer` | Actor-Critic with Experience Replay |
| TRPO | `baselines.trpo_mpi` | Trust Region Policy Optimization |
| GAIL | `baselines.gail` | Generative Adversarial Imitation Learning |
| HER | `baselines.her` | Hindsight Experience Replay for sample-efficient learning |

Sources: [README.md:132-142]()

### Environment Handling

The environment handling system provides a standardized interface to interact with reinforcement learning environments, with particular focus on:

- **Vectorized Environments**: Run multiple environment instances in parallel for efficient data collection
- **Environment Wrappers**: Modify environment behavior for preprocessing observations, framing stacking, etc.
- **Monitoring**: Track and log performance metrics during training

Sources: [README.md:117-129]()

### Core Infrastructure

The core infrastructure provides shared functionality used by the various algorithms:

- **Neural Network Models**: Standard architectures for policy and value functions
- **Policies**: Classes that handle action selection and state processing
- **TensorFlow Utilities**: Helpers for building and training neural networks
- **Probability Distributions**: Components for stochastic policy representation
- **Logging and Visualization**: Tools for tracking experiment progress

Sources: [README.md:94-95]()

## System Architecture

The Baselines system integrates the components described above into a cohesive framework. Below are diagrams showing the high-level architecture and execution flow.

### High-Level Architecture

```mermaid
graph TD
    CLI["Command Line Interface"] --> Run["baselines.run"]
    Run --> AlgFactory["Algorithm Factory"]
    Run --> EnvFactory["Environment Factory"]
    
    AlgFactory --> |"creates"| Algorithm["RL Algorithm Instance"]
    EnvFactory --> |"creates"| VecEnv["Vectorized Environment"]
    
    Algorithm --> |"trains"| Policy["Neural Network Policy"]
    Algorithm --> |"interacts with"| VecEnv
    VecEnv --> |"provides obs"| Algorithm
    Algorithm --> |"takes actions"| VecEnv
    
    VecEnv --> |"wraps"| EnvWrappers["Environment Wrappers"]
    EnvWrappers --> |"modify"| Environments["Gym Environments"]
    
    Algorithm --> |"logs to"| Logger["Training Logger"]
```

Sources: [README.md:78-81]()

### Experiment Execution Flow

```mermaid
flowchart TD
    Start([Start]) --> ParseArgs["Parse Command Line Arguments"]
    ParseArgs --> GetAlg["Get Algorithm (--alg)"]
    GetAlg --> GetEnv["Create Environment (--env)"]
    GetEnv --> SetupNetwork["Setup Network Architecture (--network)"]
    SetupNetwork --> ConfigureHyperparams["Configure Hyperparameters"]
    ConfigureHyperparams --> Train["Train for num_timesteps"]
    Train --> SaveModel{Save Model?}
    SaveModel -- "Yes (--save_path)" --> Save["Save to Disk"]
    SaveModel -- "No" --> Play{Play Mode?}
    Save --> Play
    Play -- "Yes (--play)" --> Visualize["Visualize Agent"]
    Play -- "No" --> End([End])
    Visualize --> End
```

Sources: [README.md:78-101](), [README.md:103-115]()

## Core Module Structure

Below is a diagram showing the key modules and classes that form the core of Baselines:

```mermaid
graph TD
    subgraph "Algorithm Implementation"
        learn["algorithm.learn()"] --> Runner["Algorithm Runner"]
        Runner --> step["step() / run()"]
        step --> |"collect experience"| Buffer["Experience Buffer"]
        Buffer --> |"sample data"| Update["Policy Update"]
        Update --> Policy["Neural Network Policy"]
    end
    
    subgraph "Policy Structure"
        Policy --> Models["baselines.common.models"]
        Policy --> Distributions["baselines.common.distributions"]
        Models --> |"builds"| TFLayers["TensorFlow Layers"]
        Distributions --> |"produces"| Actions["Action Sampling"]
    end
    
    subgraph "Environment Interface"
        VecEnv["VecEnv (base class)"] --> SPVE["SubprocVecEnv"]
        VecEnv --> DVE["DummyVecEnv"]
        VecEnv --> SHVE["ShmemVecEnv"]
        SPVE --> |"runs multiple"| Envs["Environments"]
        DVE --> |"runs sequentially"| Envs
        SHVE --> |"shared memory"| Envs
    end
    
    Runner --> |"interacts with"| VecEnv
    VecEnv --> |"observations"| Runner
    Runner --> |"actions"| VecEnv
```

Sources: [README.md:94-95]()

## Integration with Environments

Baselines is designed to work with various types of environments, with special support for popular benchmarks:

```mermaid
graph TD
    subgraph "Environment Types"
        Atari["Atari Games"]
        Mujoco["MuJoCo Physics"]
        Gym["OpenAI Gym"]
        Custom["Custom Environments"]
    end
    
    subgraph "Environment Creation"
        make_vec_env["make_vec_env()"]
        make_env["make_env()"]
        make_atari["make_atari()"]
        make_mujoco["make_mujoco_env()"]
    end
    
    subgraph "Environment Processing"
        Wrappers["Environment Wrappers"]
        Monitor["Monitor Wrapper"]
        AtariWrappers["Atari Preprocessing"]
        VecNormalize["VecNormalize"]
    end
    
    Atari --> make_atari
    Mujoco --> make_mujoco
    Gym --> make_env
    Custom --> make_env
    
    make_atari --> make_env
    make_mujoco --> make_env
    make_env --> make_vec_env
    
    make_vec_env --> VecEnv["VecEnv Instances"]
    
    VecEnv --> VecNormalize
    VecEnv --> Monitor
    make_atari --> AtariWrappers
```

Sources: [README.md:67-70](), [README.md:82-92](), [README.md:117]()

## Reinforcement Learning Algorithm Structure

The reinforcement learning algorithms in Baselines follow similar organizational patterns, typically providing a `learn()` function as the main entry point:

```mermaid
graph TD
    subgraph "Common Algorithm Structure"
        learn["algorithm.learn()"] --> setup["Setup Networks/Environment"]
        setup --> Runner["Create Runner"]
        Runner --> train_loop["Training Loop"]
        train_loop --> collect["Collect Experience"]
        collect --> update["Update Policy"]
        update --> log["Log Progress"]
        log --> check["Check Termination"]
        check --> |"continue"| train_loop
        check --> |"done"| cleanup["Cleanup"]
    end
    
    subgraph "Algorithm-Specific Components"
        PPO["PPO Runner"]
        DQN["Replay Buffer"]
        DDPG["Action Noise"]
        HER["Goal Relabeling"]
    end
    
    Runner --> PPO
    Runner --> DQN
    Runner --> DDPG
    collect --> HER
```

Sources: [README.md:94-95]()

## Usage Flow

The typical usage flow for Baselines is as follows:

1. **Installation**: Install the package and dependencies
2. **Environment Setup**: Configure the desired environment
3. **Algorithm Selection**: Choose a reinforcement learning algorithm
4. **Training**: Run the training process with specified hyperparameters
5. **Saving/Loading**: Save trained models and load them later for evaluation
6. **Visualization**: Visualize agent performance

For detailed information on these steps, please refer to [Getting Started](#2) and [Running Experiments](#2.1).

Sources: [README.md:45-65](), [README.md:78-101](), [README.md:103-115]()

---

