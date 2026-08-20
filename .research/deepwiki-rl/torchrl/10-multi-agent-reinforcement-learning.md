# deepwiki torchrl §10 multi-agent-reinforcement-learning
> 来源: https://deepwiki.com/pytorch/rl/10-multi-agent-reinforcement-learning

$/$
$?

/$

DeepWiki

DeepWiki
pytorch/rl

$?

/$

Last indexed:  14 December 2025  (eaaa11)

  - Overview
  - Core Data Infrastructure
  - TensorDict System
  - TensorSpec System
  - Environments
  - EnvBase and Environment Specifications
  - Environment Transforms
  - Backend Integrations
  - Batched and Parallel Environments
  - Data Collection
  - Collector Architecture
  - Distributed Collection Strategies
  - Replay Buffers
  - ReplayBuffer Architecture
  - Advanced Replay Buffer Features
  - Modules and Models
  - TensorDictModule System
  - Actors, Critics, and Value Networks
  - Probability Distributions
  - Neural Network Architectures
  - Exploration Strategies
  - Learning Algorithms
  - Loss Module Architecture
  - On-Policy Algorithms
  - Off-Policy Algorithms
  - Value-Based Algorithms
  - Value Estimators
  - Training Infrastructure
  - Trainer System
  - Helper Utilities
  - LLM Integration
  - LLM Wrapper System
  - LLM Data Structures
  - LLM Training Objectives
  - LLM Environments and Tools
  - Multi-Agent Reinforcement Learning
  - Examples and Tutorials
  - Development and Deployment
  - Build System
  - Documentation System

Menu

## Multi-Agent Reinforcement Learning

Relevant source files

  - docs/source/reference/modules.rst

  - test/test_cost.py

  - test/test_exploration.py

  - test/test_modules.py

  - torchrl/modules/__init__.py

  - torchrl/modules/models/__init__.py

  - torchrl/modules/models/exploration.py

  - torchrl/modules/models/models.py

  - torchrl/modules/models/multiagent.py

  - torchrl/modules/models/utils.py

  - torchrl/modules/tensordict_module/__init__.py

  - torchrl/modules/tensordict_module/exploration.py

  - torchrl/objectives/a2c.py

  - torchrl/objectives/common.py

  - torchrl/objectives/cql.py

  - torchrl/objectives/ddpg.py

  - torchrl/objectives/deprecated.py

  - torchrl/objectives/dqn.py

  - torchrl/objectives/iql.py

  - torchrl/objectives/ppo.py

  - torchrl/objectives/redq.py

  - torchrl/objectives/reinforce.py

  - torchrl/objectives/sac.py

  - torchrl/objectives/td3.py

  - torchrl/objectives/utils.py

  - torchrl/objectives/value/advantages.py

### Purpose and Scope

This documentation covers multi-agent reinforcement learning (MARL) capabilities within TorchRL, including multi-agent environments, specialized network architectures, and MARL-specific loss modules. These components enable training multiple agents that interact in shared or competitive environments.

For single-agent RL algorithms, see Learning Algorithms (page 7). For general environment features, see Environments (page 3).

### Overview of MARL Components

TorchRL provides several components for multi-agent reinforcement learning:

  - Multi-Agent Environments : Integration with VMAS and PettingZoo libraries

  - Multi-Agent Network Architectures : Specialized networks for centralized/decentralized training

  - Value Mixing Networks : QMixer and VDN for credit assignment

  - MARL Loss Modules : QMixerLoss for training value decomposition networks

MARL System Architecture

```

```

Sources: torchrl/modules/models/multiagent.py21-265 test/test_cost.py231-302

### Multi-Agent Environments

TorchRL supports integration with multi-agent environment libraries through dedicated wrapper classes.

#### Environment Structure

Multi-agent environments in TorchRL use nested TensorDict structures to organize observations, actions, and rewards for multiple agents:

Multi-Agent TensorDict Structure

```

```

Sources: test/test_cost.py231-269

The key convention is that agent-specific data is nested under an `"agents"` key in the TensorDict, with an additional dimension for the number of agents. This allows the same data collection and training infrastructure to handle both single-agent and multi-agent scenarios.

#### VMAS Integration

VMAS (Vectorized Multi-Agent Simulator) provides fast, vectorized multi-agent environments. The `VmasEnv` wrapper integrates VMAS scenarios with TorchRL's environment interface.

#### PettingZoo Integration

PettingZoo is a library of multi-agent game environments. The `PettingZooEnv` wrapper enables using PettingZoo environments within TorchRL.

Sources: test/test_cost.py231-269

### Multi-Agent Network Architectures

TorchRL provides specialized network architectures for multi-agent reinforcement learning that support both centralized and decentralized training paradigms.

#### MultiAgentNetBase

`MultiAgentNetBase` is the abstract base class for all multi-agent networks, providing the common interface and utilities.

Multi-Agent Network Architecture

```

```

Sources: torchrl/modules/models/multiagent.py21-122

Key parameters:

  - n_agents : Number of agents in the environment

  - centralized : If True , all agents share the same network parameters (parameter sharing)

  - share_params : If True , agents share parameters; if False , each agent has its own parameters

  - agent_dim : The dimension along which agents are stacked (typically -2 )

#### MultiAgentMLP

`MultiAgentMLP` extends `MLP` to handle multi-agent scenarios with configurable parameter sharing.

MultiAgentMLP Architecture

```

```

Sources: torchrl/modules/models/multiagent.py124-177

Usage example:

```

```

#### MultiAgentConvNet

`MultiAgentConvNet` extends `ConvNet` to handle multi-agent scenarios with visual observations.

Sources: torchrl/modules/models/multiagent.py179-238

Key features:

  - Supports both centralized and decentralized architectures

  - Handles multi-agent visual observations

  - Can share convolutional layers across agents

  - Automatically flattens spatial dimensions for multi-agent batching

#### QMixer

`QMixer` implements the QMIX mixing network that combines individual agent Q-values into a joint Q-value while maintaining the Individual-Global-Max (IGM) principle.

QMixer Architecture

```

```

Sources: torchrl/modules/models/multiagent.py267-393

Key features:

  - Ensures monotonicity: increasing any agent's Q-value increases the total Q-value

  - Uses hypernetworks to generate mixing weights conditioned on global state

  - Enables centralized training with decentralized execution (CTDE)

  - Maintains the IGM principle for credit assignment

Usage example:

```

```

#### VDNMixer

`VDNMixer` implements Value Decomposition Networks (VDN), a simpler alternative to QMixer that additively combines agent Q-values.

VDN Architecture

```

```

Sources: torchrl/modules/models/multiagent.py396-431

Key features:

  - Simple additive value decomposition

  - Guarantees IGM principle

  - No additional parameters (just summation)

  - Faster and more stable than QMixer but less expressive

Usage example:

```

```

### MARL Loss Modules

#### QMixerLoss

`QMixerLoss` implements the QMIX algorithm, which trains a value decomposition network to perform credit assignment in cooperative multi-agent tasks.

QMixer Training Flow

```

```

Sources: test/test_cost.py231-302

Key features:

  - Implements QMIX algorithm for cooperative MARL

  - Supports both QMixer and VDNMixer networks

  - Handles multi-agent action spaces via nested TensorDict keys

  - Compatible with centralized training, decentralized execution (CTDE)

  - Uses target networks for stable training

The loss function computes the temporal difference error between the current total Q-value and the target:

```
L = (Q_tot(s, a) - (r + γ * max_a' Q_tot(s', a')))²
```

Where Q_tot is computed by the mixer network from individual agent Q-values.

Sources: test/test_cost.py231-302

### Composite Action Spaces for Multi-Agent

Multi-agent environments often require handling multiple actions simultaneously, potentially with different action types per agent. TorchRL uses `CompositeDistribution` for this purpose.

Composite Distribution for MARL

```

```

Sources: test/test_cost.py271-289

Example from test code showing composite distributions for MARL:

```

```

This shows how different action types can be specified for different agent action components using nested keys.

Sources: test/test_cost.py271-289

### Complete MARL Training Example

Here's a complete example showing how to set up and train a multi-agent system using QMIX:

```

```

This example demonstrates:

  - Setting up a multi-agent environment (VMAS)

  - Creating agent networks with parameter sharing

  - Using a QMixer for value decomposition

  - Training with experience replay

  - Handling multi-agent data through the standard TorchRL pipeline

Sources: torchrl/modules/models/multiagent.py21-431 test/test_cost.py231-302

### Summary of MARL Components

| Component | Purpose | Key Parameters | Use Case |
| MultiAgentMLP | MLP for multi-agent | n_agents , centralized , share_params | General multi-agent tasks |
| MultiAgentConvNet | ConvNet for multi-agent | n_agents , centralized , share_params | Visual multi-agent tasks |
| QMixer | Non-linear value mixing | state_shape , mixing_embed_dim , n_agents | QMIX algorithm (cooperative) |
| VDNMixer | Additive value mixing | None (just summation) | VDN algorithm (cooperative) |
| QMixerLoss | QMIX training loss | agent_network , mixer , delay_value | Training QMIX/VDN agents |
| VmasEnv | Vectorized multi-agent | scenario , num_envs , n_agents | Fast multi-agent simulation |
| PettingZooEnv | Multi-agent games | env_name , parallel | Game-based MARL |

#### Centralized vs Decentralized Training

| Mode | Description | When to Use |
| Centralized ( centralized=True ) | All agents processed by single network | Homogeneous agents, parameter efficiency |
| Decentralized ( centralized=False, share_params=True ) | Separate network per agent, shared weights | Heterogeneous agents with similar structure |
| Fully Independent ( centralized=False, share_params=False ) | Separate network per agent, separate weights | Heterogeneous agents with different roles |

### Conclusion

TorchRL provides a comprehensive set of tools for visual data processing in reinforcement learning. These tools enable efficient recording, transformation, and visualization of visual data, which is essential for modern RL applications involving visual observations such as robotics, game playing, and simulation environments.



#### On this page

  - Multi-Agent Reinforcement Learning
  - Purpose and Scope
  - Overview of MARL Components
  - Multi-Agent Environments
  - Environment Structure
  - VMAS Integration
  - PettingZoo Integration
  - Multi-Agent Network Architectures
  - MultiAgentNetBase
  - MultiAgentMLP
  - MultiAgentConvNet
  - QMixer
  - VDNMixer
  - MARL Loss Modules
  - QMixerLoss
  - Composite Action Spaces for Multi-Agent
  - Complete MARL Training Example
  - Summary of MARL Components
  - Centralized vs Decentralized Training
  - Conclusion

$!/$$/$
