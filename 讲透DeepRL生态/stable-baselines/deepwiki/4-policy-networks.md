> 来源: [https://deepwiki.com/hill-a/stable-baselines/4-policy-networks](https://deepwiki.com/hill-a/stable-baselines/4-policy-networks)
> DeepWiki hill-a/stable-baselines | Last indexed: 22 June 2025 (45beb2

# Policy Networks

  Relevant source files 
 - [docs/guide/custom_policy.rst](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/guide/custom_policy.rst)
 - [docs/modules/ddpg.rst](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/modules/ddpg.rst)
 - [docs/modules/dqn.rst](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/modules/dqn.rst)
 - [docs/modules/sac.rst](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/modules/sac.rst)
 - [stable_baselines/common/policies.py](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/common/policies.py)
 - [stable_baselines/common/tf_util.py](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/common/tf_util.py)
 - [stable_baselines/ddpg/policies.py](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/ddpg/policies.py)
 - [stable_baselines/deepq/build_graph.py](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/deepq/build_graph.py)
 - [stable_baselines/deepq/policies.py](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/deepq/policies.py)
 - [tests/test_custom_policy.py](https://github.com/hill-a/stable-baselines/blob/45beb246/tests/test_custom_policy.py)
 
  Policy networks are the neural network architectures that map observations to actions in reinforcement learning algorithms. This document covers the policy network implementations in stable-baselines, including the class hierarchy, built-in architectures, and customization mechanisms.

 For information about the algorithms that use these policies, see [On-Policy Algorithms](https://deepwiki.com/hill-a/stable-baselines/3.1-on-policy-algorithms) and [Off-Policy Algorithms](https://deepwiki.com/hill-a/stable-baselines/3.2-off-policy-algorithms). For details on creating custom policies, see [Custom Policy Creation](https://deepwiki.com/hill-a/stable-baselines/4.2-custom-policy-creation).

 
## Policy Architecture Overview

 The policy system in stable-baselines follows a hierarchical design where different algorithms share common policy interfaces while implementing algorithm-specific behaviors.

 
```

```

 Sources: [stable_baselines/common/policies.py92-753](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/common/policies.py#L92-L753) [stable_baselines/ddpg/policies.py7-262](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/ddpg/policies.py#L7-L262) [stable_baselines/deepq/policies.py9-254](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/deepq/policies.py#L9-L254)

 
## Base Policy Classes

 
### BasePolicy

 The `BasePolicy` class provides the fundamental interface for all policy networks, handling observation processing and action selection.

 
| Property | Description | Type |
|---|---|---|
| obs_ph | Observation placeholder | tf.Tensor |
| processed_obs | Processed observation tensor | tf.Tensor |
| action_ph | Action placeholder (optional) | tf.Tensor |
| is_discrete | Whether action space is discrete | bool |
| initial_state | Initial state for recurrent policies | np.ndarray |

 Key methods:

 
 - `step(obs, state, mask)` - Returns actions for given observations
 - `proba_step(obs, state, mask)` - Returns action probabilities
 
 Sources: [stable_baselines/common/policies.py92-204](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/common/policies.py#L92-L204)

 
### ActorCriticPolicy

 The `ActorCriticPolicy` extends `BasePolicy` for algorithms that use separate actor and critic networks, such as PPO2, A2C, and TRPO.

 
```

```

 Sources: [stable_baselines/common/policies.py206-319](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/common/policies.py#L206-L319)

 
## Neural Network Architectures

 
### Multi-Layer Perceptron (MLP) Extractor

 The `mlp_extractor` function creates flexible MLP architectures with shared and separate layers for policy and value networks.

 Network architecture specification uses the `net_arch` parameter:

 
 - `[64, 64]` - Two shared layers of 64 units each
 - `[128, dict(vf=[256, 256], pi=[128])]` - Shared 128-unit layer, then separate value (256x2) and policy (128) layers
 
 Sources: [stable_baselines/common/policies.py32-89](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/common/policies.py#L32-L89)

 
### Convolutional Neural Network (CNN) Extractor

 The `nature_cnn` function implements the CNN architecture from the Nature DQN paper for processing image observations.

 Architecture:

 
 - Conv2D: 32 filters, 8x8 kernel, stride 4, ReLU activation
 - Conv2D: 64 filters, 4x4 kernel, stride 2, ReLU activation
 - Conv2D: 64 filters, 3x3 kernel, stride 1, ReLU activation
 - Fully Connected: 512 units, ReLU activation
 
 Sources: [stable_baselines/common/policies.py16-29](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/common/policies.py#L16-L29)

 
### LSTM Networks

 The `LstmPolicy` class supports recurrent policies using LSTM layers for environments requiring memory of past observations.

 
```

```

 Sources: [stable_baselines/common/policies.py376-515](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/common/policies.py#L376-L515)

 
## Built-in Policy Types

 
### Feed-Forward Policies

 
| Policy Class | Feature Extraction | Architecture |
|---|---|---|
| MlpPolicy | MLP | 2 layers of 64 units (default) |
| CnnPolicy | CNN | Nature CNN + fully connected |
| CnnLstmPolicy | CNN + LSTM | Nature CNN → LSTM → outputs |
| MlpLstmPolicy | MLP + LSTM | MLP → LSTM → outputs |
| CnnLnLstmPolicy | CNN + Layer-Norm LSTM | With layer normalization |
| MlpLnLstmPolicy | MLP + Layer-Norm LSTM | With layer normalization |

 Sources: [stable_baselines/common/policies.py517-702](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/common/policies.py#L517-L702)

 
### Algorithm-Specific Policies

 Different algorithms require specialized policy interfaces:

 **DDPG Policies** - Implement deterministic actor-critic for continuous control:

 
 - `make_actor()` - Creates deterministic policy network
 - `make_critic()` - Creates Q-value network that takes state-action pairs
 
 **DQN Policies** - Implement Q-networks for discrete action spaces:

 
 - Support dueling architecture (separate value and advantage streams)
 - Output Q-values for each discrete action
 
 Sources: [stable_baselines/ddpg/policies.py7-262](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/ddpg/policies.py#L7-L262) [stable_baselines/deepq/policies.py9-254](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/deepq/policies.py#L9-L254)

 
## Policy Registration System

 The policy registration system allows dynamic policy lookup and custom policy registration.

 
```

```

 Key functions:

 
 - `get_policy_from_name(base_policy_type, name)` - Retrieves registered policy by string name
 - `register_policy(name, policy)` - Registers new policy class with string identifier
 
 Sources: [stable_baselines/common/policies.py704-753](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/common/policies.py#L704-L753)

 
## Policy Integration with Algorithms

 Policies integrate with RL algorithms through a standardized interface:

 
```

```

 The policy's `step()` method is called during both training and inference to:

 
 - Process observations through the neural network
 - Sample actions from the policy distribution
 - Return additional information needed by the algorithm
 
 Sources: [stable_baselines/common/policies.py182-204](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/common/policies.py#L182-L204) [stable_baselines/common/policies.py295-318](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/common/policies.py#L295-L318)
