> 来源: [https://deepwiki.com/AgileRL/AgileRL/5-neural-network-architecture](https://deepwiki.com/AgileRL/AgileRL/5-neural-network-architecture)
> DeepWiki AgileRL/AgileRL | Last indexed: 25 June 2025 (03307c

# Neural Network Architecture

  Relevant source files 
 - [agilerl/modules/base.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/modules/base.py)
 - [agilerl/modules/cnn.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/modules/cnn.py)
 - [agilerl/modules/mlp.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/modules/mlp.py)
 - [agilerl/modules/multi_input.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/modules/multi_input.py)
 - [agilerl/networks/actors.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/networks/actors.py)
 - [agilerl/networks/base.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/networks/base.py)
 - [agilerl/networks/q_networks.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/networks/q_networks.py)
 - [agilerl/utils/evolvable_networks.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/utils/evolvable_networks.py)
 
  AgileRL's neural network architecture system provides evolvable neural networks that can automatically adapt their structure and parameters during training through evolutionary hyperparameter optimization. This system forms the foundation for all reinforcement learning algorithms in AgileRL, enabling networks to grow, shrink, and modify their architectures based on performance feedback.

 For detailed information about specific network implementations, see [Evolvable Networks](https://deepwiki.com/AgileRL/AgileRL/5.1-evolvable-networks), [Q-Networks and Value Functions](https://deepwiki.com/AgileRL/AgileRL/5.2-q-networks-and-value-functions), [Actor Networks](https://deepwiki.com/AgileRL/AgileRL/5.3-actor-networks), and [Custom Networks and MakeEvolvable](https://deepwiki.com/AgileRL/AgileRL/5.4-custom-networks-and-makeevolvable).

 
## System Overview

 The neural network architecture is built on a hierarchical foundation with `EvolvableModule` as the base class for all evolvable components, and `EvolvableNetwork` as the specialized base for complete neural networks used in RL algorithms.

 
### Core Architecture Hierarchy

 
```

```

 Sources: [agilerl/modules/base.py258-689](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/modules/base.py#L258-L689) [agilerl/networks/base.py125-535](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/networks/base.py#L125-L535) [agilerl/networks/q_networks.py16-423](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/networks/q_networks.py#L16-L423) [agilerl/networks/actors.py13-389](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/networks/actors.py#L13-L389)

 
### Network Component Structure

 Each `EvolvableNetwork` follows a consistent encoder-head architecture pattern where observations are processed through an encoder to produce latent features, which are then processed by specialized heads for different tasks.

 
```

```

 Sources: [agilerl/networks/base.py302-314](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/networks/base.py#L302-L314) [agilerl/networks/base.py470-535](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/networks/base.py#L470-L535) [agilerl/networks/q_networks.py95-107](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/networks/q_networks.py#L95-L107)

 
## Evolvability System

 The core innovation of AgileRL's architecture is the mutation system that allows networks to evolve their structure during training. This is implemented through the `@mutation` decorator and specialized mutation methods.

 
### Mutation Types and Methods

 
| Mutation Type | Purpose | Example Methods |
|---|---|---|
| MutationType.LAYER | Add/remove entire layers | add_layer(), remove_layer() |
| MutationType.NODE | Modify layer sizes | add_node(), remove_node(), add_latent_node() |
| MutationType.ACTIVATION | Change activation functions | change_activation() |

 The mutation system automatically tracks which methods were applied and recreates networks with preserved parameters using `EvolvableModule.preserve_parameters()`.

 Sources: [agilerl/modules/base.py49-73](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/modules/base.py#L49-L73) [agilerl/modules/base.py420-456](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/modules/base.py#L420-L456) [agilerl/modules/base.py423-453](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/modules/base.py#L423-L453)

 
## Network Type Categories

 
### Value-Based Networks

 Used for algorithms like DQN, Rainbow DQN, and TD3 critics:

 
 - **`QNetwork`**: Basic Q-value estimation for discrete action spaces
 - **`RainbowQNetwork`**: Distributional Q-learning with dueling architecture and noisy networks
 - **`ContinuousQNetwork`**: Q-value estimation for continuous action spaces (state-action pairs)
 
 
### Policy Networks

 Used for actor-critic and policy gradient algorithms:

 
 - **`DeterministicActor`**: Outputs deterministic actions (DDPG, TD3)
 - **`StochasticActor`**: Outputs action distributions with sampling capabilities (PPO, SAC)
 
 
### Encoder Modules

 Automatically selected based on observation space:

 
 - **`EvolvableMLP`**: For vector observations
 - **`EvolvableCNN`**: For image observations
 - **`EvolvableMultiInput`**: For dict/tuple observation spaces
 - **`EvolvableLSTM`**: For sequential/recurrent processing
 
 Sources: [agilerl/networks/q_networks.py16-133](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/networks/q_networks.py#L16-L133) [agilerl/networks/actors.py13-195](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/networks/actors.py#L13-L195) [agilerl/modules/mlp.py11-289](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/modules/mlp.py#L11-L289) [agilerl/modules/cnn.py168-608](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/modules/cnn.py#L168-L608)

 
## Configuration and Initialization

 Networks are configured through standardized config objects and automatically adapt to environment observation and action spaces:

 
```

```

 The system automatically:

 
 - Selects appropriate encoder architecture based on `observation_space`
 - Configures output dimensions based on `action_space`
 - Sets up mutation methods for evolutionary optimization
 - Handles parameter preservation during network recreation
 
 Sources: [agilerl/networks/base.py177-263](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/networks/base.py#L177-L263) [agilerl/utils/evolvable_networks.py52-79](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/utils/evolvable_networks.py#L52-L79) [agilerl/modules/configs.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/modules/configs.py)

 
## Integration with RL Algorithms

 The evolvable networks integrate seamlessly with AgileRL's algorithm implementations through the `EvolvableAlgorithm` base class. Each algorithm maintains multiple networks (e.g., actor, critic, target networks) that can all evolve independently or together during training.

 The mutation and recreation system ensures that:

 
 - Network architectures can change during training
 - Parameters are preserved across structural changes
 - Multiple networks in an algorithm can share architectural mutations
 - Evolution is guided by performance feedback from the training process
 
 Sources: [agilerl/networks/base.py102-123](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/networks/base.py#L102-L123) [agilerl/modules/base.py75-165](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/modules/base.py#L75-L165)
