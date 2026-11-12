> 来源: [https://deepwiki.com/thu-ml/tianshou/7-neural-network-components](https://deepwiki.com/thu-ml/tianshou/7-neural-network-components)
> DeepWiki thu-ml/tianshou | Last indexed: 19 April 2025 (90846f

# Neural Network Components

  Relevant source files 
 - [tianshou/utils/net/common.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/net/common.py)
 - [tianshou/utils/net/continuous.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/net/continuous.py)
 - [tianshou/utils/net/discrete.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/net/discrete.py)
 
  This document describes the neural network components available in Tianshou, a reinforcement learning library. These components provide the foundation for building and implementing various reinforcement learning algorithms. For information about using these networks with policies, see [Policy Framework](https://deepwiki.com/thu-ml/tianshou/3-policy-framework).

 
## Purpose and Structure

 Tianshou's neural network components are organized into three main modules:

 
 - Common networks - Base classes and general-purpose architectures
 - Discrete action space networks - Networks specialized for discrete action spaces
 - Continuous action space networks - Networks specialized for continuous action spaces
 
 These components provide ready-to-use implementations for various network architectures commonly used in reinforcement learning algorithms while maintaining flexibility for customization.

 Sources: [tianshou/utils/net/common.py1-725](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/net/common.py#L1-L725) [tianshou/utils/net/discrete.py1-436](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/net/discrete.py#L1-L436) [tianshou/utils/net/continuous.py1-530](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/net/continuous.py#L1-L530)

 
## Component Hierarchy

 The following diagram illustrates the hierarchical organization of Tianshou's neural network components:

 
```

```

 Sources: [tianshou/utils/net/common.py148-175](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/net/common.py#L148-L175) [tianshou/utils/net/common.py616-634](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/net/common.py#L616-L634) [tianshou/utils/net/continuous.py89-99](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/net/continuous.py#L89-L99)

 
## Core Network Components

 
### MLP (Multi-Layer Perceptron)

 The `MLP` class is the fundamental building block of most network architectures in Tianshou:

 
```

```

 Key features of the `MLP` class:

 
 - Configurable hidden layer sizes
 - Optional normalization layers (e.g., BatchNorm, LayerNorm)
 - Customizable activation functions
 - Support for custom linear layers
 - Optional input flattening
 
 Sources: [tianshou/utils/net/common.py49-142](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/net/common.py#L49-L142) [tianshou/utils/net/common.py21-46](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/net/common.py#L21-L46)

 
### Net Class

 The `Net` class wraps the `MLP` class to provide additional features for reinforcement learning:

 
```

```

 Key features of the `Net` class:

 
 - Support for dueling network architecture (used in Dueling DQN)
 - Optional softmax output for action probabilities
 - Support for distributional RL via `num_atoms` parameter
 
 Sources: [tianshou/utils/net/common.py161-289](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/net/common.py#L161-L289)

 
### Recurrent Networks

 The `Recurrent` class implements recurrent neural networks for handling sequential or partially observable environments:

 
```

```

 Sources: [tianshou/utils/net/common.py292-374](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/net/common.py#L292-L374)

 
## Actor Networks

 Tianshou provides actor networks for both discrete and continuous action spaces:

 
### Discrete Action Space Actor

 
```

```

 Sources: [tianshou/utils/net/discrete.py13-82](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/net/discrete.py#L13-L82)

 
### Continuous Action Space Actor

 
```

```

 Sources: [tianshou/utils/net/continuous.py24-86](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/net/continuous.py#L24-L86)

 
### Probabilistic Actor (ActorProb)

 
```

```

 Sources: [tianshou/utils/net/continuous.py181-261](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/net/continuous.py#L181-L261)

 
## Critic Networks

 Tianshou provides critic networks for estimating state values or state-action values:

 
### Discrete Action Space Critic

 
```

```

 Sources: [tianshou/utils/net/discrete.py85-121](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/net/discrete.py#L85-L121)

 
### Continuous Action Space Critic

 
```

```

 Sources: [tianshou/utils/net/continuous.py100-178](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/net/continuous.py#L100-L178)

 
## Advanced Network Components

 Tianshou offers several specialized network components for implementing advanced RL algorithms:

 
### Distributional RL Networks

 For distributional reinforcement learning algorithms (C51, QR-DQN, IQN, FQF):

 
 - `ImplicitQuantileNetwork`: Network for implementing the Implicit Quantile Network (IQN) algorithm
 - `CosineEmbeddingNetwork`: Embeds quantile fractions using cosine functions for IQN
 - `FractionProposalNetwork`: Network for learning to propose fractions for FQF
 - `FullQuantileFunction`: Implementation of the Fully parameterized Quantile Function for FQF
 
 Sources: [tianshou/utils/net/discrete.py124-319](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/net/discrete.py#L124-L319)

 
### Noisy Networks and Curiosity

 
 - `NoisyLinear`: Implementation of noisy networks for exploration
 - `IntrinsicCuriosityModule`: Implementation of intrinsic curiosity module for exploration
 
 Sources: [tianshou/utils/net/discrete.py321-435](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/net/discrete.py#L321-L435)

 
### Offline RL Networks

 
 - `Perturbation`: Perturbation network for BCQ algorithm
 - `VAE`: Variational Autoencoder for modeling action distributions in BCQ
 
 Sources: [tianshou/utils/net/continuous.py410-530](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/net/continuous.py#L410-L530)

 
## Integration with Other Components

 The neural network components in Tianshou are designed to work seamlessly with the rest of the framework:

 
```

```

 Sources: [tianshou/utils/net/common.py377-390](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/net/common.py#L377-L390)

 
## Feature Support Matrix

 The following table shows which features are supported by different network components:

 
| Component | Discrete Actions | Continuous Actions | Recurrent | Distributional | Dueling |
|---|---|---|---|---|---|
| Net | ✓ | ✓ |  | ✓ | ✓ |
| Recurrent | ✓ | ✓ | ✓ |  |  |
| discrete.Actor | ✓ |  |  |  |  |
| discrete.Critic | ✓ |  |  |  |  |
| continuous.Actor |  | ✓ |  |  |  |
| continuous.Critic |  | ✓ |  |  |  |
| continuous.ActorProb |  | ✓ |  |  |  |
| ImplicitQuantileNetwork | ✓ |  |  | ✓ |  |
| BranchingNet | ✓ |  |  |  | ✓ |
| RecurrentActorProb |  | ✓ | ✓ |  |  |
| RecurrentCritic |  | ✓ | ✓ |  |  |

 Sources: [tianshou/utils/net/common.py49-374](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/net/common.py#L49-L374) [tianshou/utils/net/discrete.py13-435](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/net/discrete.py#L13-L435) [tianshou/utils/net/continuous.py24-407](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/net/continuous.py#L24-L407)

 
## Related Components

 For more detailed information about specific neural network components, refer to:

 
 - [Common Networks](https://deepwiki.com/thu-ml/tianshou/7.1-common-networks) - Documentation on general-purpose network architectures
 - [Actor-Critic Networks](https://deepwiki.com/thu-ml/tianshou/7.2-actor-critic-networks) - Explanation of actor-critic network architectures and their use in algorithms
 - [Distributional RL Networks](https://deepwiki.com/thu-ml/tianshou/7.3-distributional-rl-networks) - Details about network architectures for distributional reinforcement learning
