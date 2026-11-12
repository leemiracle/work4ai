> 来源: [https://deepwiki.com/astooke/rlpyt/7-models](https://deepwiki.com/astooke/rlpyt/7-models)
> DeepWiki astooke/rlpyt | Last indexed: 25 April 2025 (f04f23

# Models

  Relevant source files 
 - [rlpyt/agents/dqn/r2d1_agent.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/agents/dqn/r2d1_agent.py)
 - [rlpyt/agents/pg/atari.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/agents/pg/atari.py)
 - [rlpyt/agents/pg/categorical.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/agents/pg/categorical.py)
 - [rlpyt/agents/pg/gaussian.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/agents/pg/gaussian.py)
 - [rlpyt/distributions/gaussian.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/distributions/gaussian.py)
 - [rlpyt/experiments/scripts/mujoco/pg/launch/pabti/launch_mujoco_ppo_serial.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/experiments/scripts/mujoco/pg/launch/pabti/launch_mujoco_ppo_serial.py)
 - [rlpyt/models/dqn/atari_catdqn_model.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/models/dqn/atari_catdqn_model.py)
 - [rlpyt/models/dqn/atari_dqn_model.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/models/dqn/atari_dqn_model.py)
 - [rlpyt/models/dqn/atari_r2d1_model.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/models/dqn/atari_r2d1_model.py)
 - [rlpyt/models/dqn/dueling.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/models/dqn/dueling.py)
 - [rlpyt/models/pg/atari_ff_model.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/models/pg/atari_ff_model.py)
 - [rlpyt/models/pg/atari_lstm_model.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/models/pg/atari_lstm_model.py)
 - [rlpyt/models/qpg/mlp.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/models/qpg/mlp.py)
 - [rlpyt/samplers/parallel/gpu/alternating_sampler.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/samplers/parallel/gpu/alternating_sampler.py)
 
  The Models component in rlpyt provides the neural network architectures that power various reinforcement learning algorithms. These models are responsible for processing environment observations and producing outputs that agents use to select actions, estimate values, or both. This page documents the different model types, their structure, and how they integrate with other components of the rlpyt framework.

 
## Overview of Models in rlpyt

 Models in rlpyt are implemented as PyTorch modules that follow a consistent interface to integrate with agents and algorithms. They serve as the brain of learning agents, transforming observations into action probabilities, state values, or Q-values depending on the algorithm being used.

 Model relationships with other system components:

 
```

```

 Sources: [rlpyt/agents/pg/categorical.py20-25](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/agents/pg/categorical.py#L20-L25) [rlpyt/agents/pg/gaussian.py20-24](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/agents/pg/gaussian.py#L20-L24)

 
## Model Architecture Types

 The rlpyt framework implements several model architecture types for different algorithms and environment domains:

 
```

```

 Sources: [rlpyt/models/dqn/atari_dqn_model.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/models/dqn/atari_dqn_model.py) [rlpyt/models/pg/atari_ff_model.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/models/pg/atari_ff_model.py) [rlpyt/models/qpg/mlp.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/models/qpg/mlp.py)

 
## Common Model Structure

 All models in rlpyt share a similar structure and interface pattern:

 
 - They extend PyTorch's `nn.Module`
 - They have an initialization method that sets up the neural network layers
 - They implement a `forward()` method that processes observations and returns outputs
 - They handle batch and time dimensions using utility functions
 
 Here's a visualization of the data flow through models:

 
```

```

 Sources: [rlpyt/models/dqn/atari_dqn_model.py47-68](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/models/dqn/atari_dqn_model.py#L47-L68) [rlpyt/models/pg/atari_ff_model.py40-63](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/models/pg/atari_ff_model.py#L40-L63)

 
## DQN Models

 DQN (Deep Q-Network) models are used in value-based reinforcement learning algorithms. They estimate the Q-value (expected future rewards) for each possible action in a given state.

 
### AtariDqnModel

 The `AtariDqnModel` is a standard convolutional network for DQN that processes multiple video frames per observation:

 
```

```

 Key features:

 
 - Convolutional layers for processing image observations
 - Optional dueling architecture for better performance
 - Configurable hyperparameters (channels, kernel sizes, strides, etc.)
 
 Sources: [rlpyt/models/dqn/atari_dqn_model.py10-68](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/models/dqn/atari_dqn_model.py#L10-L68)

 
### AtariR2d1Model

 The `AtariR2d1Model` extends the DQN architecture with recurrent layers:

 
```

```

 Key features:

 
 - Convolutional layers for processing image observations
 - LSTM layer for maintaining a memory of past observations
 - Handles recurrent state across forward passes
 
 Sources: [rlpyt/models/dqn/atari_r2d1_model.py14-77](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/models/dqn/atari_r2d1_model.py#L14-L77)

 
### Dueling Architecture

 Dueling networks separate the estimation of state value and action advantages:

 
```

```

 The `DuelingHeadModel` implements this architecture:

 
```

```

 Sources: [rlpyt/models/dqn/dueling.py8-46](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/models/dqn/dueling.py#L8-L46)

 
## Policy Gradient Models

 Policy gradient models are used in algorithms that directly optimize a policy function.

 
### AtariFfModel

 The `AtariFfModel` is a feedforward model for Atari agents:

 
```

```

 Key features:

 
 - Convolutional network for processing image observations
 - Outputs both action probabilities and state-value estimate
 - Used in algorithms like A2C and PPO for Atari environments
 
 Sources: [rlpyt/models/pg/atari_ff_model.py9-63](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/models/pg/atari_ff_model.py#L9-L63)

 
### AtariLstmModel

 The `AtariLstmModel` adds recurrent capability to the policy gradient model:

 
```

```

 Key features:

 
 - Convolutional layers followed by an LSTM
 - Maintains and updates recurrent state across time steps
 - Outputs action probabilities and value estimates
 
 Sources: [rlpyt/models/pg/atari_lstm_model.py13-78](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/models/pg/atari_lstm_model.py#L13-L78)

 
## QPG Models

 QPG (Q-Policy Gradient) models are used in algorithms that combine aspects of Q-learning and policy gradients, such as DDPG, TD3, and SAC.

 
### MuMlpModel

 The `MuMlpModel` is an MLP that outputs the deterministic action mean:

 
```

```

 Sources: [rlpyt/models/qpg/mlp.py9-32](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/models/qpg/mlp.py#L9-L32)

 
### PiMlpModel

 The `PiMlpModel` outputs parameters for a Gaussian action distribution:

 
```

```

 Sources: [rlpyt/models/qpg/mlp.py35-59](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/models/qpg/mlp.py#L35-L59)

 
### QofMuMlpModel

 The `QofMuMlpModel` estimates Q-values for state-action pairs:

 
```

```

 Sources: [rlpyt/models/qpg/mlp.py62-87](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/models/qpg/mlp.py#L62-L87)

 
## Model Integration with Agents

 Models in rlpyt are instantiated by agents and used to process observations and select actions. The flow of data between agents and models depends on the agent type.

 
### Data Flow for DQN Agents

 
```

```

 Sources: [rlpyt/agents/dqn/r2d1_agent.py25-42](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/agents/dqn/r2d1_agent.py#L25-L42)

 
### Data Flow for Policy Gradient Agents

 
```

```

 Sources: [rlpyt/agents/pg/categorical.py33-43](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/agents/pg/categorical.py#L33-L43) [rlpyt/agents/pg/atari.py15-25](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/agents/pg/atari.py#L15-L25)

 
## Handling Recurrent State

 Recurrent models in rlpyt use a consistent pattern for managing recurrent state across time steps:

 
```

```

 The recurrent state is managed by the following pattern:

 
```

```

 Sources: [rlpyt/models/dqn/atari_r2d1_model.py11](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/models/dqn/atari_r2d1_model.py#L11-L11) [rlpyt/models/pg/atari_lstm_model.py10](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/models/pg/atari_lstm_model.py#L10-L10)

 
## Observation Processing

 Most models in rlpyt use a common pattern for processing image observations:

 
```

```

 Additionally, they handle batch and time dimensions using utility functions:

 
```

```

 Sources: [rlpyt/models/dqn/atari_dqn_model.py57-67](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/models/dqn/atari_dqn_model.py#L57-L67) [rlpyt/models/pg/atari_ff_model.py50-61](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/models/pg/atari_ff_model.py#L50-L61)

 
## Distributional RL Models

 For distributional reinforcement learning algorithms like Categorical DQN, special model architectures are provided:

 
```

```

 The `AtariCatDqnModel` implements this approach, where instead of outputting a single Q-value per action, it outputs a probability distribution over possible Q-values.

 Sources: [rlpyt/models/dqn/atari_catdqn_model.py24-77](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/models/dqn/atari_catdqn_model.py#L24-L77)

 
## Model-Distribution Interaction

 For stochastic policies, models output parameters that are passed to distribution classes for action sampling:

 
```

```

 For example, Gaussian distributions for continuous actions:

 
```

```

 Sources: [rlpyt/distributions/gaussian.py15-246](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/distributions/gaussian.py#L15-L246)

 
## Summary

 The Models component in rlpyt provides a flexible set of neural network architectures tailored for different reinforcement learning algorithms and environments. These models follow consistent patterns and interfaces, making them easy to use and extend. By understanding the different model types and their integration with agents and distributions, you can effectively use existing models or create custom ones for your specific needs.

 Sources: All referenced files
