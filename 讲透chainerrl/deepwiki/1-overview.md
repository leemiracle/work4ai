<!-- source: DeepWiki mcp.deepwiki.com · repo chainer/chainerrl · page 1 Overview · fetched 2026-10-30 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/ChainerRL.png](assets/ChainerRL.png)
- [assets/breakout.gif](assets/breakout.gif)
- [assets/grasping.gif](assets/grasping.gif)
- [assets/humanoid.gif](assets/humanoid.gif)
- [chainerrl/links/mlp_bn.py](chainerrl/links/mlp_bn.py)
- [docs/install.rst](docs/install.rst)

</details>



## Purpose and Scope

ChainerRL is a deep reinforcement learning library that implements various state-of-the-art deep reinforcement learning algorithms in Python using the Chainer deep learning framework. This document provides an architectural overview of the ChainerRL codebase, covering its core components, algorithm implementations, and system organization.

For detailed information about specific RL algorithms, see [Reinforcement Learning Agents](#2). For implementation details of neural network components, see [Core Components](#3). For guidance on training agents and evaluation, see [Training and Evaluation Infrastructure](#4).

## Library Architecture

ChainerRL is organized into several key subsystems that work together to provide a comprehensive deep RL framework:

```mermaid
graph TB
    subgraph "chainerrl Package"
        AGENTS["chainerrl.agents<br/>DQN, PPO, A3C, etc."]
        POLICIES["chainerrl.policies<br/>Policy implementations"]
        QFUNCS["chainerrl.q_functions<br/>Q-function implementations"]
        LINKS["chainerrl.links<br/>Neural network components"]
        WRAPPERS["chainerrl.wrappers<br/>Environment preprocessing"]
        REPLAY["chainerrl.replay_buffer<br/>Experience storage"]
        TRAINING["chainerrl.training<br/>train_agent_*, evaluators"]
    end
    
    subgraph "External Dependencies"
        CHAINER["chainer<br/>Deep learning framework"]
        GYM["gym<br/>Environment interface"]
    end
    
    subgraph "Examples"
        EXAMPLES["examples/<br/>Training scripts"]
        REPRO["examples/*/reproduction/<br/>Paper reproductions"]
    end
    
    AGENTS --> POLICIES
    AGENTS --> QFUNCS
    AGENTS --> REPLAY
    POLICIES --> LINKS
    QFUNCS --> LINKS
    TRAINING --> AGENTS
    TRAINING --> WRAPPERS
    WRAPPERS --> GYM
    EXAMPLES --> TRAINING
    EXAMPLES --> AGENTS
    LINKS --> CHAINER
```

Sources: [README.md:1-134](), [chainerrl/links/mlp_bn.py:1-83]()

## Algorithm Portfolio

ChainerRL implements a comprehensive set of modern RL algorithms across different paradigms:

### Algorithm Support Matrix

| Algorithm | Discrete Actions | Continuous Actions | Recurrent Models | Batch Training | Async Training |
|-----------|:----------------:|:------------------:|:----------------:|:--------------:|:--------------:|
| `DQN` (including `DoubleDQN`) | ✓ | ✓ (NAF) | ✓ | ✓ | ✗ |
| `CategoricalDQN` | ✓ | ✗ | ✓ | ✓ | ✗ |
| `Rainbow` | ✓ | ✗ | ✓ | ✓ | ✗ |
| `IQN` | ✓ | ✗ | ✓ | ✓ | ✗ |
| `DDPG` | ✗ | ✓ | ✓ | ✓ | ✗ |
| `A3C` | ✓ | ✓ | ✓ | ✓ (A2C) | ✓ |
| `ACER` | ✓ | ✓ | ✓ | ✗ | ✓ |
| `NSQ` | ✓ | ✓ (NAF) | ✓ | ✗ | ✓ |
| `PCL` | ✓ | ✓ | ✓ | ✗ | ✓ |
| `PPO` | ✓ | ✓ | ✓ | ✓ | ✗ |
| `TRPO` | ✓ | ✓ | ✓ | ✓ | ✗ |
| `TD3` | ✗ | ✓ | ✗ | ✓ | ✗ |
| `SAC` | ✗ | ✓ | ✗ | ✓ | ✗ |

Sources: [README.md:40-54]()

### Algorithm Organization by Approach

```mermaid
graph LR
    subgraph "Value-Based Methods"
        DQN["chainerrl.agents.dqn.DQN"]
        CATDQN["chainerrl.agents.categorical_dqn.CategoricalDQN"]
        RAINBOW["chainerrl.agents.rainbow.Rainbow"]
        IQN["chainerrl.agents.iqn.IQN"]
    end
    
    subgraph "Policy-Based Methods"
        PPO["chainerrl.agents.ppo.PPO"]
        TRPO["chainerrl.agents.trpo.TRPO"]
        REINFORCE["chainerrl.agents.reinforce.REINFORCE"]
    end
    
    subgraph "Actor-Critic Methods"
        A3C["chainerrl.agents.a3c.A3C"]
        A2C["chainerrl.agents.a2c.A2C"]
        ACER["chainerrl.agents.acer.ACER"]
        DDPG["chainerrl.agents.ddpg.DDPG"]
        TD3["chainerrl.agents.td3.TD3"]
        SAC["chainerrl.agents.sac.SAC"]
    end
    
    subgraph "Specialized Methods"
        NSQ["chainerrl.agents.nsq.NSQ"]
        PCL["chainerrl.agents.pcl.PCL"]
    end
```

Sources: [README.md:56-86]()

## Core Neural Network Components

ChainerRL provides reusable neural network building blocks that agents compose for different tasks:

```mermaid
graph TB
    subgraph "chainerrl.links"
        MLP["MLP<br/>Basic multi-layer perceptron"]
        MLPBN["MLPBN<br/>MLP with batch normalization"]
        NOISY["NoisyLinear<br/>Noisy networks for exploration"]
    end
    
    subgraph "chainerrl.q_functions"
        STATEQ["StateQFunction<br/>State → Q-values"]
        SAQF["StateActionQFunction<br/>State,Action → Q-value"]
        DUELING["DuelingDQN<br/>Dueling architecture"]
        DISTQ["DistributionalQFunction<br/>Distributional Q-learning"]
    end
    
    subgraph "chainerrl.policies"
        GAUSSIAN["GaussianPolicy<br/>Continuous action policies"]
        SOFTMAX["SoftmaxPolicy<br/>Discrete action policies"]
        DETERMIN["DeterministicPolicy<br/>Deterministic policies"]
    end
    
    subgraph "chainerrl.v_functions"
        VFUNC["StateVFunction<br/>State value functions"]
    end
    
    MLP --> STATEQ
    MLP --> GAUSSIAN
    MLP --> VFUNC
    MLPBN --> STATEQ
    NOISY --> MLP
```

Sources: [chainerrl/links/mlp_bn.py:22-82](), [README.md:88-98]()

## Training Infrastructure

ChainerRL provides multiple training paradigms to accommodate different algorithm requirements:

```mermaid
graph LR
    subgraph "Training Functions"
        TRAIN_SYNC["chainerrl.training.train_agent<br/>Synchronous training"]
        TRAIN_BATCH["chainerrl.training.train_agent_batch<br/>Vectorized environments"]
        TRAIN_ASYNC["chainerrl.training.train_agent_async<br/>Asynchronous training"]
    end
    
    subgraph "Evaluation"
        EVALUATOR["chainerrl.evaluator.Evaluator<br/>Performance evaluation"]
        ASYNC_EVAL["chainerrl.evaluator.AsyncEvaluator<br/>Async evaluation"]
    end
    
    subgraph "Environment Processing"
        ATARI_WRAP["chainerrl.wrappers.atari_wrappers<br/>Atari preprocessing"]
        GENERAL_WRAP["chainerrl.wrappers<br/>General env wrappers"]
    end
    
    subgraph "Experience Management"
        REPLAY["chainerrl.replay_buffer<br/>Experience replay"]
        PRIORITIZED["PrioritizedReplayBuffer<br/>Prioritized experience replay"]
    end
    
    TRAIN_SYNC --> EVALUATOR
    TRAIN_BATCH --> EVALUATOR
    TRAIN_ASYNC --> ASYNC_EVAL
    TRAIN_SYNC --> GENERAL_WRAP
    TRAIN_BATCH --> ATARI_WRAP
```

Sources: [README.md:32-36]()

## Integration and Usage Patterns

ChainerRL integrates with standard RL environments and provides comprehensive examples:

```mermaid
graph TB
    subgraph "Environment Integration"
        GYM_ENV["gym.Env<br/>OpenAI Gym interface"]
        ATARI["Atari environments<br/>via gym[atari]"]
        MUJOCO["MuJoCo environments<br/>via gym[mujoco]"]
    end
    
    subgraph "Example Scripts"
        BASIC["examples/gym/<br/>Basic training examples"]
        ATARI_EX["examples/atari/<br/>Atari game training"]
        MUJOCO_EX["examples/mujoco/<br/>Continuous control"]
        REPRODUCTION["examples/*/reproduction/<br/>Paper reproductions"]
    end
    
    subgraph "Pretrained Models"
        DOWNLOAD["chainerrl.models<br/>Model download system"]
        PRETRAINED["Pretrained agent weights<br/>for immediate use"]
    end
    
    GYM_ENV --> BASIC
    ATARI --> ATARI_EX
    MUJOCO --> MUJOCO_EX
    BASIC --> REPRODUCTION
    DOWNLOAD --> PRETRAINED
```

Sources: [README.md:34-36](), [README.md:58-86]()

## Installation and Dependencies

ChainerRL requires Python 3.6+ and depends primarily on the Chainer deep learning framework. Installation is available via PyPI or from source:

```bash
pip install chainerrl
```

Or for development:
```bash
python setup.py install
```

Key dependencies include `chainer`, `numpy`, and `gym` for environment interfaces.

Sources: [README.md:16-30](), [docs/install.rst:1-26]()

---

