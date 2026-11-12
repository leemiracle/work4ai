> 来源: [https://deepwiki.com/opendilab/DI-engine/5-model-system](https://deepwiki.com/opendilab/DI-engine/5-model-system)
> DeepWiki opendilab/DI-engine | Last indexed: 20 April 2025 (c290a6

# Model System

  Relevant source files 
 - [ding/model/common/__init__.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/common/__init__.py)
 - [ding/model/common/encoder.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/common/encoder.py)
 - [ding/model/common/head.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/common/head.py)
 - [ding/model/common/utils.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/common/utils.py)
 - [ding/model/template/acer.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/template/acer.py)
 - [ding/model/template/maqac.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/template/maqac.py)
 - [ding/model/template/tests/test_maqac.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/template/tests/test_maqac.py)
 - [ding/model/template/vae.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/template/vae.py)
 - [ding/model/wrapper/model_wrappers.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/wrapper/model_wrappers.py)
 - [ding/model/wrapper/test_model_wrappers.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/wrapper/test_model_wrappers.py)
 - [ding/policy/r2d2_gtrxl.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/r2d2_gtrxl.py)
 - [ding/torch_utils/network/__init__.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/network/__init__.py)
 - [ding/torch_utils/network/gtrxl.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/network/gtrxl.py)
 - [ding/torch_utils/network/tests/test_gtrxl.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/network/tests/test_gtrxl.py)
 - [ding/torch_utils/network/tests/test_merge.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/network/tests/test_merge.py)
 - [dizoo/classic_control/cartpole/config/cartpole_ngu_config.py](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/classic_control/cartpole/config/cartpole_ngu_config.py)
 - [dizoo/classic_control/cartpole/config/cartpole_r2d2_gtrxl_config.py](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/classic_control/cartpole/config/cartpole_r2d2_gtrxl_config.py)
 - [dizoo/tabmwp/envs/tabmwp_env.py](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/tabmwp/envs/tabmwp_env.py)
 - [dizoo/tabmwp/envs/utils.py](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/tabmwp/envs/utils.py)
 
  The Model System in DI-engine provides the neural network architecture components and utilities for building, configuring, and extending reinforcement learning models. It serves as the foundation for defining the neural network structures used by policies to implement various reinforcement learning algorithms.

 This page covers the core components of the Model System, how they are structured, and how they can be combined to create models for different reinforcement learning tasks. For information about how to use these models in reinforcement learning algorithms, see the [Policy System](https://deepwiki.com/opendilab/DI-engine/4-policy-system).

 
## Core Architecture

 The Model System consists of four main components:

 
```

```

 
 - **Encoders**: Process raw observations (like images or state vectors) into meaningful embeddings
 - **Heads**: Transform embeddings into appropriate outputs (like Q-values or action probabilities)
 - **Model Wrappers**: Add functionality to models without modifying their core implementation
 - **Model Templates**: Pre-configured combinations of encoders and heads for common RL algorithms
 
 The typical flow for model construction and usage is:

 
```

```

 Sources:

 
 - [ding/model/common/__init__.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/common/__init__.py)
 - [ding/model/wrapper/model_wrappers.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/wrapper/model_wrappers.py)
 - [ding/model/common/utils.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/common/utils.py)
 
 
## Encoders

 Encoders transform raw observations (like states or images) into embedding vectors that can be further processed by other network components. The encoder type is chosen based on the observation structure.

 
### Encoder Types and Structure

 
```

```

 
 - **ConvEncoder**: Processes 2D image observations using convolutional neural networks

 
 - Used for: Image-based environments (like Atari games)
 - Key parameters: Observation shape, channel sizes, kernel sizes, strides
 - **FCEncoder**: Processes 1D vector observations using fully-connected networks

 
 - Used for: Low-dimensional state spaces (like classic control problems)
 - Key parameters: Observation shape, hidden sizes, whether to use residual blocks
 - **IMPALAConvEncoder**: A specialized CNN encoder used in the IMPALA algorithm

 
 - Used for: Complex visual environments requiring scalable distributed training
 - Key parameters: Observation shape, channels, number of residual blocks
 
 Sources:

 
 - [ding/model/common/encoder.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/common/encoder.py)
 
 
### Example Usage

 When creating a model configuration, you specify the encoder type and parameters based on your observation space:

 
```

```

 
## Heads

 Heads transform the embeddings from encoders into outputs appropriate for the RL algorithm, such as Q-values, policy logits, or value estimates. Different heads are optimized for different types of algorithms and action spaces.

 
### Head Types and Structure

 
```

```

 
 - **DiscreteHead**: Generates Q-values or action logits for discrete action spaces

 
 - Used for: DQN, PPO with discrete actions
 - Output: Action logits
 - **DistributionHead**: Generates a distribution over Q-values for distributional RL

 
 - Used for: C51 algorithm
 - Output: Value distribution represented by atoms
 - **RainbowHead**: Combines advantages of dueling architecture and distributional RL

 
 - Used for: Rainbow DQN
 - Output: Value distribution with dueling architecture
 - **QRDQNHead**: Implementation for Quantile Regression DQN

 
 - Used for: QR-DQN algorithm
 - Output: Quantile values representing the value distribution
 - **BranchingHead**: For high-dimensional discrete action spaces with independent dimensions

 
 - Used for: Branching DQN
 - Output: Value function for each action dimension
 
 Sources:

 
 - [ding/model/common/head.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/common/head.py)
 
 
### Head Selection

 The choice of head depends on:

 
 - The action space (discrete vs. continuous)
 - The reinforcement learning algorithm
 - Whether you need distributional properties
 
 
## Model Wrappers

 Model wrappers extend model functionality without modifying the core implementation. They "wrap" an existing model and intercept method calls, adding behavior before or after the model's methods execute.

 
### Wrapper Types and Hierarchy

 
```

```

 
 - **HiddenStateWrapper**: Maintains hidden state for RNN-based models

 
 - Used for: Recurrent policies (e.g., R2D2, DRQN)
 - Key feature: Manages hidden states across time steps
 - **Action Sampling Wrappers**: Implement different strategies for selecting actions

 
 - **ArgmaxSampleWrapper**: Selects the highest probability action (greedy)
 - **MultinomialSampleWrapper**: Samples actions based on their probabilities
 - **EpsGreedySampleWrapper**: Implements epsilon-greedy exploration
 - **ReparamSampleWrapper**: For continuous action spaces with reparameterization trick
 - **Transformer Wrappers**: Special wrappers for transformer architectures

 
 - **TransformerInputWrapper**: Manages input sequences for transformers
 - **TransformerSegmentWrapper**: Handles segmentation of long sequences
 - **TransformerMemoryWrapper**: Manages memory for transformer models
 - **ActionNoiseWrapper**: Adds noise to actions for exploration in continuous spaces

 
 - Used for: Algorithms like DDPG and TD3
 - Key feature: Supports different noise types (Gaussian, OU noise)
 
 Sources:

 
 - [ding/model/wrapper/model_wrappers.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/wrapper/model_wrappers.py)
 
 
### Common Wrapper Stacks

 Different policies require different wrapper stacks:

 
```

```

 Wrappers are applied using the `model_wrap` function:

 
```

```

 Sources:

 
 - [ding/policy/r2d2_gtrxl.py127-174](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/r2d2_gtrxl.py#L127-L174)
 
 
## Model Templates

 Model templates provide pre-configured combinations of encoders and heads for common RL algorithms. They abstract away the details of constructing neural networks for specific algorithms.

 
### Standard Model Structure

 
```

```

 
### Example Templates

 
 - **DQN Template**:

 
 - Encoder: ConvEncoder or FCEncoder based on observation shape
 - Head: DiscreteHead for Q-values
 - **Rainbow Template**:

 
 - Encoder: ConvEncoder or FCEncoder
 - Head: RainbowHead for distributional Q-values
 - **GTrXL Template** (for transformers):

 
 - Encoder: GTrXL network
 - Head: DiscreteHead for Q-values
 - **MAQAC Template** (Multi-Agent Q-Value Actor-Critic):

 
 - Encoder: Custom encoders for agent and global states
 - Heads: Separate heads for actor (DiscreteHead) and critic (DiscreteHead)
 
 Sources:

 
 - [ding/model/template/maqac.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/template/maqac.py)
 - [ding/model/template/vae.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/template/vae.py)
 
 
## Creating and Using Models

 The model system provides a flexible framework for creating and using models in reinforcement learning algorithms.

 
### Model Creation Process

 
```

```

 The `create_model` function in `ding/model/common/utils.py` is the primary entry point for creating models:

 
```

```

 The model can then be wrapped for different purposes (evaluation, collection) and used in a policy.

 
### Integration with Policy System

 The Model System integrates with the Policy System, providing the neural network components needed by policies to implement reinforcement learning algorithms:

 
```

```

 Source:

 
 - [ding/model/common/utils.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/common/utils.py)
 - [dizoo/classic_control/cartpole/config/cartpole_r2d2_gtrxl_config.py](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/classic_control/cartpole/config/cartpole_r2d2_gtrxl_config.py)
 
 
## Advanced Models

 The Model System also supports advanced neural network architectures for specialized reinforcement learning algorithms.

 
### Transformer-Based Models (GTrXL)

 For problems requiring long-term dependencies, DI-engine implements the Gated Transformer-XL (GTrXL) architecture:

 
```

```

 GTrXL models are used with special wrappers and configurations to effectively handle memory and sequence data.

 Sources:

 
 - [ding/torch_utils/network/gtrxl.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/network/gtrxl.py)
 - [dizoo/classic_control/cartpole/config/cartpole_r2d2_gtrxl_config.py](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/classic_control/cartpole/config/cartpole_r2d2_gtrxl_config.py)
 
 
### Multi-Agent Models

 For multi-agent reinforcement learning, DI-engine provides specialized model templates like MAQAC (Multi-Agent Q-Value Actor-Critic):

 
```

```

 Sources:

 
 - [ding/model/template/maqac.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/template/maqac.py)
 
 
## Conclusion

 The Model System in DI-engine provides a flexible and modular framework for creating neural network models for reinforcement learning. By combining encoders, heads, and model wrappers, users can easily configure and customize models for a wide range of reinforcement learning algorithms and environments.

 Key benefits of the Model System include:

 
 - Modular design that promotes code reuse and customization
 - Pre-configured templates for common RL algorithms
 - Support for advanced architectures like transformers
 - Integration with the Policy System for implementing RL algorithms
 
 For more information on how to use these models in reinforcement learning algorithms, see the [Policy System](https://deepwiki.com/opendilab/DI-engine/4-policy-system) documentation.
