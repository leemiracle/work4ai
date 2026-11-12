<!-- source: DeepWiki mcp.deepwiki.com · repo chainer/chainerrl · page 2 Reinforcement Learning Agents · fetched 2026-10-30 -->

# Reinforcement Learning Agents

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [chainerrl/agents/a3c.py](chainerrl/agents/a3c.py)
- [chainerrl/agents/acer.py](chainerrl/agents/acer.py)
- [chainerrl/agents/ddpg.py](chainerrl/agents/ddpg.py)
- [chainerrl/agents/dqn.py](chainerrl/agents/dqn.py)
- [chainerrl/agents/nsq.py](chainerrl/agents/nsq.py)
- [chainerrl/agents/pcl.py](chainerrl/agents/pcl.py)
- [chainerrl/agents/pgt.py](chainerrl/agents/pgt.py)
- [chainerrl/misc/prioritized.py](chainerrl/misc/prioritized.py)
- [chainerrl/replay_buffer.py](chainerrl/replay_buffer.py)
- [tests/agents_tests/basetest_dqn_like.py](tests/agents_tests/basetest_dqn_like.py)
- [tests/agents_tests/test_dqn.py](tests/agents_tests/test_dqn.py)
- [tests/misc_tests/test_prioritized.py](tests/misc_tests/test_prioritized.py)
- [tests/test_replay_buffer.py](tests/test_replay_buffer.py)

</details>



This document provides an overview of the reinforcement learning agent implementations in ChainerRL, covering the various algorithms, their architectural patterns, and relationships between different agent types. The agents represent the core learning algorithms that interact with environments to solve reinforcement learning problems.

For information about the neural network components used by these agents, see [Core Components](#3). For details about training infrastructure and evaluation systems, see [Training and Evaluation Infrastructure](#4).

## Agent Architecture Overview

ChainerRL implements a diverse collection of RL algorithms organized around common interface patterns. All agents inherit from base classes that define standard methods for acting, training, and episode management.

```mermaid
graph TD
    subgraph "Base Agent Classes"
        Agent["Agent<br/>Basic interface"]
        BatchAgent["BatchAgent<br/>Batch environment support"]
        AsyncAgent["AsyncAgent<br/>Asynchronous training"]
        AttributeSavingMixin["AttributeSavingMixin<br/>Model persistence"]
    end
    
    subgraph "Value-Based Agents"
        DQN["DQN<br/>chainerrl.agents.dqn.DQN"]
        NSQ["NSQ<br/>chainerrl.agents.nsq.NSQ"]
    end
    
    subgraph "Actor-Critic Agents"
        ACER["ACER<br/>chainerrl.agents.acer.ACER"]
        DDPG["DDPG<br/>chainerrl.agents.ddpg.DDPG"]
        A3C["A3C<br/>chainerrl.agents.a3c.A3C"]
    end
    
    subgraph "Policy-Based Agents"
        PCL["PCL<br/>chainerrl.agents.pcl.PCL"]
        PGT["PGT<br/>chainerrl.agents.pgt.PGT"]
    end
    
    Agent --> BatchAgent
    Agent --> AsyncAgent
    
    DQN --> BatchAgent
    DQN --> AttributeSavingMixin
    NSQ --> AsyncAgent
    NSQ --> AttributeSavingMixin
    
    ACER --> AsyncAgent
    ACER --> AttributeSavingMixin
    DDPG --> BatchAgent
    DDPG --> AttributeSavingMixin
    A3C --> AsyncAgent
    A3C --> AttributeSavingMixin
    
    PCL --> AsyncAgent
    PCL --> AttributeSavingMixin
    PGT --> Agent
    PGT --> AttributeSavingMixin
```

The agent hierarchy reflects fundamental differences in training paradigms:
- `BatchAgent`: Supports vectorized environments and batch operations
- `AsyncAgent`: Designed for asynchronous multi-process training
- `AttributeSavingMixin`: Provides model saving/loading capabilities

Sources: [chainerrl/agents/dqn.py:98](), [chainerrl/agents/acer.py:223](), [chainerrl/agents/ddpg.py:35](), [chainerrl/agents/a3c.py:72]()

## Agent Training Lifecycle

All agents follow a common training lifecycle that involves environment interaction, experience collection, and model updates:

```mermaid
graph LR
    subgraph "Training Methods"
        ActAndTrain["act_and_train()<br/>Environment interaction"]
        StopEpisode["stop_episode_and_train()<br/>Episode termination"]
        Act["act()<br/>Evaluation only"]
    end
    
    subgraph "Core Components"
        Model["Neural Network Model<br/>Q-functions, Policies"]
        Optimizer["Chainer Optimizer<br/>Parameter updates"]
        ReplayBuffer["ReplayBuffer<br/>Experience storage"]
        Explorer["Explorer<br/>Action selection"]
    end
    
    subgraph "Update Mechanisms"
        Update["update()<br/>Model parameter updates"]
        SyncTarget["sync_target_network()<br/>Target network updates"]
    end
    
    ActAndTrain --> Model
    ActAndTrain --> Explorer
    ActAndTrain --> ReplayBuffer
    StopEpisode --> Update
    Update --> Optimizer
    Update --> SyncTarget
    Act --> Model
```

Sources: [chainerrl/agents/dqn.py:376-428](), [chainerrl/agents/ddpg.py:299-331]()

## Value-Based Agents

Value-based agents learn action-value functions (Q-functions) to make decisions. The DQN agent is the most prominent implementation and serves as the foundation for many variants.

### DQN (Deep Q-Networks)

The `DQN` class implements the Deep Q-Networks algorithm with experience replay and target networks:

```mermaid
graph TD
    subgraph "DQN Components"
        QFunction["q_function<br/>Main Q-network"]
        TargetQFunction["target_model<br/>Target Q-network"]
        ReplayBuffer["replay_buffer<br/>Experience storage"]
        Explorer["explorer<br/>Exploration strategy"]
    end
    
    subgraph "DQN Update Process"
        Experience["Experience<br/>(s, a, r, s', terminal)"]
        Batch["batch_experiences()<br/>Minibatch sampling"]
        Loss["compute_value_loss()<br/>TD error computation"]
        BackProp["Gradient computation<br/>and parameter update"]
    end
    
    subgraph "Target Network Updates"
        SyncInterval["target_update_interval"]
        SyncMethod["sync_target_network()<br/>Hard/soft updates"]
    end
    
    QFunction --> Experience
    Experience --> ReplayBuffer
    ReplayBuffer --> Batch
    Batch --> Loss
    Loss --> BackProp
    BackProp --> QFunction
    
    SyncInterval --> SyncMethod
    SyncMethod --> TargetQFunction
    TargetQFunction --> Loss
```

Key features of the DQN implementation:
- **Experience Replay**: Uses `ReplayBuffer` for storing and sampling transitions
- **Target Networks**: Maintains separate target network updated periodically
- **Loss Computation**: Supports both Huber loss and MSE with weighted variants
- **Recurrent Support**: Optional recurrent network support for partial observability

Sources: [chainerrl/agents/dqn.py:98-573](), [chainerrl/replay_buffer.py:135-176]()

The DQN agent supports both standard and recurrent variants:

| Configuration | Update Function | Replay Buffer Type | Use Case |
|---------------|-----------------|-------------------|----------|
| Standard DQN | `update()` | `ReplayBuffer` | Fully observable MDPs |
| Recurrent DQN | `update_from_episodes()` | `EpisodicReplayBuffer` | Partially observable MDPs |

Sources: [chainerrl/agents/dqn.py:173-176](), [chainerrl/agents/dqn.py:273-287]()

### NSQ (N-step Q-Learning)

The `NSQ` agent implements asynchronous n-step Q-learning for multi-process training:

```mermaid
graph TD
    subgraph "NSQ Architecture"
        SharedQ["shared_q_function<br/>Global Q-network"]
        LocalQ["q_function<br/>Process-local Q-network"]
        TargetQ["target_q_function<br/>Target network"]
    end
    
    subgraph "Asynchronous Updates"
        LocalSteps["Local n-step collection"]
        Gradients["Gradient computation"]
        GlobalUpdate["Global parameter update"]
        Sync["sync_parameters()"]
    end
    
    LocalQ --> LocalSteps
    LocalSteps --> Gradients
    Gradients --> SharedQ
    SharedQ --> GlobalUpdate
    GlobalUpdate --> Sync
    Sync --> LocalQ
```

Sources: [chainerrl/agents/nsq.py:18-193]()

## Actor-Critic Agents

Actor-critic agents combine policy optimization (actor) with value function learning (critic). These agents can handle both discrete and continuous action spaces.

### ACER (Actor-Critic with Experience Replay)

ACER combines on-policy actor-critic learning with off-policy experience replay:

```mermaid
graph TD
    subgraph "ACER Model Components"
        Model["model<br/>Combined policy-value network"]
        SharedModel["shared_model<br/>Global shared parameters"]
        AvgModel["shared_average_model<br/>Trust region computation"]
    end
    
    subgraph "ACER Training"
        OnPolicy["Online on-policy updates<br/>act_and_train()"]
        OffPolicy["Experience replay updates<br/>update_from_replay()"]
        TrustRegion["Trust region optimization<br/>compute_loss_with_kl_constraint()"]
    end
    
    subgraph "Loss Components"
        PolicyLoss["Policy gradient loss<br/>with importance sampling"]
        ValueLoss["Value function loss<br/>TD error"]
        EntropyReg["Entropy regularization"]
    end
    
    Model --> OnPolicy
    Model --> OffPolicy
    OnPolicy --> PolicyLoss
    OffPolicy --> PolicyLoss
    PolicyLoss --> TrustRegion
    PolicyLoss --> ValueLoss
    PolicyLoss --> EntropyReg
```

ACER's key innovations include:
- **Importance Sampling**: Corrects for off-policy bias in experience replay
- **Trust Region**: Uses efficient trust region optimization to stabilize training
- **Truncated Importance Weights**: Prevents exploding importance ratios

Sources: [chainerrl/agents/acer.py:223-710](), [chainerrl/agents/acer.py:184-221]()

### DDPG (Deep Deterministic Policy Gradients)

DDPG extends DQN to continuous action spaces using deterministic policies:

```mermaid
graph TD
    subgraph "DDPG Model"
        Policy["policy<br/>Deterministic policy network"]
        QFunction["q_function<br/>Critic network"]
        TargetPolicy["target_policy<br/>Target policy"]
        TargetQ["target_q_function<br/>Target critic"]
    end
    
    subgraph "DDPG Updates"
        CriticLoss["compute_critic_loss()<br/>Q-learning update"]
        ActorLoss["compute_actor_loss()<br/>Policy gradient"]
        TargetUpdates["Target network sync"]
    end
    
    subgraph "Training Process"
        ActorOpt["actor_optimizer"]
        CriticOpt["critic_optimizer"]
        Explorer["explorer<br/>Noise injection"]
    end
    
    Policy --> ActorLoss
    QFunction --> CriticLoss
    ActorLoss --> ActorOpt
    CriticLoss --> CriticOpt
    
    TargetPolicy --> CriticLoss
    TargetQ --> CriticLoss
    
    Policy --> Explorer
```

DDPG training alternates between critic and actor updates:
1. **Critic Update**: Standard Q-learning with target networks
2. **Actor Update**: Policy gradient to maximize Q-values
3. **Target Updates**: Soft updates to target networks

Sources: [chainerrl/agents/ddpg.py:35-470](), [chainerrl/agents/ddpg.py:161-212](), [chainerrl/agents/ddpg.py:214-251]()

### A3C (Asynchronous Advantage Actor-Critic)

A3C implements asynchronous actor-critic learning across multiple processes:

```mermaid
graph TD
    subgraph "A3C Model Types"
        SeparateModel["A3CSeparateModel<br/>Separate policy and value"]
        SharedModel["A3CSharedModel<br/>Shared parameters"]
    end
    
    subgraph "A3C Training"
        LocalSteps["Local t_max steps"]
        Advantage["Advantage computation<br/>R - V(s)"]
        PolicyGrad["Policy gradient<br/>log π(a|s) * A"]
        ValueLoss["Value function loss<br/>(R - V(s))²"]
    end
    
    subgraph "Asynchronous Updates"
        LocalModel["Process-local model"]
        SharedModel2["shared_model<br/>Global parameters"]
        GradCopy["copy_grad()"]
        ParamSync["sync_parameters()"]
    end
    
    LocalSteps --> Advantage
    Advantage --> PolicyGrad
    Advantage --> ValueLoss
    PolicyGrad --> GradCopy
    ValueLoss --> GradCopy
    GradCopy --> SharedModel2
    SharedModel2 --> ParamSync
    ParamSync --> LocalModel
```

Sources: [chainerrl/agents/a3c.py:72-304](), [chainerrl/agents/a3c.py:36-70]()

## Specialized Agents

### PCL (Path Consistency Learning)

PCL implements a novel approach that enforces consistency between different trajectory segments:

```mermaid
graph TD
    subgraph "PCL Components"
        Model["model<br/>Policy-value network"]
        ReplayBuf["replay_buffer<br/>Episode storage"]
        OnlineBatch["online_batch_losses<br/>Batch accumulation"]
    end
    
    subgraph "PCL Loss Computation"
        Rollout["rollout_len<br/>Path segments"]
        PathConsist["Path consistency<br/>constraint"]
        PolicyLoss["Policy loss component"]
        ValueLoss["Value loss component"]
    end
    
    Model --> Rollout
    Rollout --> PathConsist
    PathConsist --> PolicyLoss
    PathConsist --> ValueLoss
    PolicyLoss --> OnlineBatch
    ValueLoss --> OnlineBatch
```

Sources: [chainerrl/agents/pcl.py:30-490]()

### PGT (Policy Gradient Theorem)

PGT implements likelihood ratio policy gradients with Q-function baselines:

```mermaid
graph TD
    subgraph "PGT Architecture"
        Policy["policy<br/>Stochastic policy"]
        QFunc["q_function<br/>Action-value function"]
        TargetPolicy["target_policy"]
        TargetQ["target_q_function"]
    end
    
    subgraph "PGT Updates"
        LogProb["log_prob(a|s)"]
        Advantage["Q(s,a) - V(s)"]
        PolicyGrad["Policy gradient<br/>∇log π * A"]
        QUpdate["Q-function update"]
    end
    
    Policy --> LogProb
    QFunc --> Advantage
    LogProb --> PolicyGrad
    Advantage --> PolicyGrad
    QFunc --> QUpdate
```

Sources: [chainerrl/agents/pgt.py:18-284]()

## Agent Configuration Patterns

Most agents follow common configuration patterns for their key components:

| Component | Purpose | Common Types |
|-----------|---------|--------------|
| Model/Q-function | Neural network architecture | `StateQFunction`, `Policy`, `VFunction` |
| Optimizer | Parameter updates | `Adam`, `RMSprop` |
| Replay Buffer | Experience storage | `ReplayBuffer`, `EpisodicReplayBuffer`, `PrioritizedReplayBuffer` |
| Explorer | Action selection strategy | `EpsilonGreedy`, `AdditiveGaussian` |
| Target Update | Stabilization mechanism | Hard updates, soft updates with τ |

Sources: [chainerrl/agents/dqn.py:135-149](), [chainerrl/agents/ddpg.py:80-95](), [chainerrl/replay_buffer.py:230-281]()

---

