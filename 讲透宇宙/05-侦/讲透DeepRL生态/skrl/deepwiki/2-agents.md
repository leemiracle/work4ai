> 来源: [https://deepwiki.com/Toni-SM/skrl/2-agents](https://deepwiki.com/Toni-SM/skrl/2-agents)
> DeepWiki Toni-SM/skrl | Last indexed: 17 August 2026 (3cdc7f

# Agents

  Relevant source files 
 - [skrl/agents/jax/base.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/jax/base.py)
 - [skrl/agents/torch/a2c/a2c.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/torch/a2c/a2c.py)
 - [skrl/agents/torch/amp/amp.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/torch/amp/amp.py)
 - [skrl/agents/torch/base.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/torch/base.py)
 - [skrl/agents/torch/cem/cem.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/torch/cem/cem.py)
 - [skrl/agents/torch/ddpg/ddpg.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/torch/ddpg/ddpg.py)
 - [skrl/agents/torch/dqn/dqn.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/torch/dqn/dqn.py)
 - [skrl/agents/torch/ppo/ppo.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/torch/ppo/ppo.py)
 - [skrl/agents/torch/q_learning/q_learning.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/torch/q_learning/q_learning.py)
 - [skrl/agents/torch/sac/sac.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/torch/sac/sac.py)
 - [skrl/agents/torch/sarsa/sarsa.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/torch/sarsa/sarsa.py)
 - [skrl/agents/torch/td3/td3.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/torch/td3/td3.py)
 - [skrl/agents/torch/trpo/trpo.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/torch/trpo/trpo.py)
 - [skrl/agents/warp/base.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/warp/base.py)
 - [skrl/multi_agents/jax/base.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/multi_agents/jax/base.py)
 - [skrl/multi_agents/torch/base.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/multi_agents/torch/base.py)
 
  Agents are the core decision-making components in **skrl** that implement reinforcement learning algorithms. They encapsulate the policy learning logic, interact with environments, and manage the training process. Each agent implements a specific RL algorithm and provides a unified interface for training and evaluation across multiple backends.

 For information about the models that agents use, see [Models](https://deepwiki.com/Toni-SM/skrl/3-models). For details about memory systems that store agent experiences, see [Memories](https://deepwiki.com/Toni-SM/skrl/6-memories). For training orchestration, see [Trainers](https://deepwiki.com/Toni-SM/skrl/5-trainers).

 
## Agent Architecture

 The agent system in **skrl** follows a modular design with support for **PyTorch**, **JAX**, and **Warp** backends. All agents inherit from a base class that defines the training lifecycle.

 
### Core Agent Lifecycle

 
```

```

 Sources: [skrl/agents/torch/base.py83-264](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/torch/base.py#L83-L264) [skrl/agents/torch/ppo/ppo.py67-165](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/torch/ppo/ppo.py#L67-L165) [skrl/agents/torch/sac/sac.py23-155](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/torch/sac/sac.py#L23-L155)

 
### Agent Hierarchy and Backends

 The codebase organizes agents by backend and algorithm family.

 
```

```

 Sources: [skrl/agents/torch/base.py83](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/torch/base.py#L83-L83) [skrl/agents/jax/base.py1](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/jax/base.py#L1-L1) [skrl/agents/warp/base.py1](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/warp/base.py#L1-L1)

 
## Common Agent Interface

 All agents implement a standardized interface that enables consistent interaction with trainers and environments.

 
### Core Methods

 
| Method | Purpose | Implementation Detail |
|---|---|---|
| init() | Initializes memory tensors and experiment directories. | skrl/agents/torch/base.py187-228 |
| act() | Processes observations to produce actions. | skrl/agents/torch/ppo/ppo.py254-278 |
| record_transition() | Stores transitions in the Memory buffer. | skrl/agents/torch/base.py245-264 |
| update() | Triggers the optimization step (loss calculation and backprop). | skrl/agents/torch/ppo/ppo.py353-370 |
| post_interaction() | Handles logging to TensorBoard/WandB and checkpointing. | skrl/agents/torch/base.py297-332 |

 
### Action Generation Process

 The `act()` method typically handles state preprocessing and exploration noise. For value-based agents like `DQN`, it also manages the epsilon-greedy schedule [skrl/agents/torch/dqn/dqn.py144-184](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/torch/dqn/dqn.py#L144-L184) For actor-critic agents like `TD3`, it applies exploration noise to deterministic actions [skrl/agents/torch/td3/td3.py248-262](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/torch/td3/td3.py#L248-L262)

 
## Configuration and Experiment Tracking

 Each agent is configured using a specialized dataclass (e.g., `PPO_CFG`, `SAC_CFG`) which inherits from `AgentCfg`.

 
### Experiment Configuration

 The `ExperimentCfg` class within the base agent defines how data is saved and logged:

 
 - `directory`: Root path for experiment runs [skrl/agents/torch/base.py27](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/torch/base.py#L27-L27)
 - `write_interval`: Frequency of logging to TensorBoard [skrl/agents/torch/base.py36](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/torch/base.py#L36-L36)
 - `checkpoint_interval`: Frequency of saving model weights [skrl/agents/torch/base.py43](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/torch/base.py#L43-L43)
 - `wandb`: Toggle for Weights & Biases integration [skrl/agents/torch/base.py57](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/torch/base.py#L57-L57)
 
 Sources: [skrl/agents/torch/base.py23-65](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/torch/base.py#L23-L65) [skrl/agents/torch/ppo/ppo_cfg.py1-20](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/torch/ppo/ppo_cfg.py#L1-L20)

 
## Multi-Agent Systems

 **skrl** supports Multi-Agent Reinforcement Learning (MARL) through the `MultiAgent` base class. Unlike single agents, multi-agents manage dictionaries of models and memories keyed by agent identifiers (`uid`).

 
 - **IPPO / MAPPO**: Independent and Multi-Agent PPO implementations.
 - **Shared Parameters**: Support for shared or independent networks across agents.
 - **GAE for MARL**: Specialized advantage estimation for multi-agent trajectories.
 
 For details, see [Multi-Agent Systems](https://deepwiki.com/Toni-SM/skrl/7-multi-agent-systems).

 Sources: [skrl/multi_agents/torch/base.py95-135](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/multi_agents/torch/base.py#L95-L135)

 
## Backend-Specific Details

 
### PyTorch Agents

 PyTorch agents implement standard optimization loops using `torch.optim`. They feature support for **Automatic Mixed Precision (AMP)** using `torch.amp.GradScaler` [skrl/agents/torch/ppo/ppo.py122-125](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/torch/ppo/ppo.py#L122-L125) and **Distributed Data Parallel** synchronization via `broadcast_parameters()` [skrl/agents/torch/ppo/ppo.py113-119](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/torch/ppo/ppo.py#L113-L119)

 For details, see [PyTorch Agents](https://deepwiki.com/Toni-SM/skrl/2.1-pytorch-agents).

 
### JAX Agents

 JAX agents utilize functional programming patterns and JIT compilation. They often rely on the `optax` library for optimization and handle state management through Flax-like state dictionaries.

 For details, see [JAX Agents](https://deepwiki.com/Toni-SM/skrl/2.2-jax-agents).

 
### Warp Agents

 Specialized agents optimized for NVIDIA Warp, allowing for high-performance simulations where the RL update step can be tightly integrated with the simulation kernels.

 Sources: [skrl/agents/jax/base.py1](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/jax/base.py#L1-L1) [skrl/agents/warp/base.py1](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/agents/warp/base.py#L1-L1)
