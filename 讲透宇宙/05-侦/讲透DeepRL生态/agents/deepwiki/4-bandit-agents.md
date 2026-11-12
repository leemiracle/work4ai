> 来源: [https://deepwiki.com/tensorflow/agents/4-bandit-agents](https://deepwiki.com/tensorflow/agents/4-bandit-agents)
> DeepWiki tensorflow/agents | Last indexed: 24 April 2025 (2a236d

# Bandit Agents

  Relevant source files 
 - [tf_agents/bandits/agents/dropout_thompson_sampling_agent.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/agents/dropout_thompson_sampling_agent.py)
 - [tf_agents/bandits/agents/dropout_thompson_sampling_agent_test.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/agents/dropout_thompson_sampling_agent_test.py)
 - [tf_agents/bandits/agents/greedy_reward_prediction_agent.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/agents/greedy_reward_prediction_agent.py)
 - [tf_agents/bandits/agents/greedy_reward_prediction_agent_test.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/agents/greedy_reward_prediction_agent_test.py)
 - [tf_agents/bandits/agents/neural_epsilon_greedy_agent.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/agents/neural_epsilon_greedy_agent.py)
 - [tf_agents/bandits/agents/neural_epsilon_greedy_agent_test.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/agents/neural_epsilon_greedy_agent_test.py)
 - [tf_agents/bandits/agents/neural_linucb_agent.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/agents/neural_linucb_agent.py)
 - [tf_agents/bandits/agents/neural_linucb_agent_test.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/agents/neural_linucb_agent_test.py)
 - [tf_agents/bandits/agents/utils.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/agents/utils.py)
 - [tf_agents/bandits/agents/utils_test.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/agents/utils_test.py)
 - [tf_agents/bandits/policies/greedy_reward_prediction_policy.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/policies/greedy_reward_prediction_policy.py)
 - [tf_agents/bandits/policies/greedy_reward_prediction_policy_test.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/policies/greedy_reward_prediction_policy_test.py)
 - [tf_agents/bandits/policies/neural_linucb_policy.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/policies/neural_linucb_policy.py)
 - [tf_agents/bandits/policies/neural_linucb_policy_test.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/policies/neural_linucb_policy_test.py)
 
  This document explains the Bandit Agents system in TF-Agents, a collection of specialized agents for solving contextual multi-armed bandit problems. Bandit agents are designed to balance exploration and exploitation in decision-making scenarios where an agent must choose from multiple actions based on contextual information, receiving feedback only for the chosen action.

 For information about reinforcement learning agents that work with sequential decision-making problems, see [Reinforcement Learning Agents](https://deepwiki.com/tensorflow/agents/3-reinforcement-learning-agents).

 
## Overview

 Bandit agents in TF-Agents implement various algorithms for contextual multi-armed bandit problems. These agents share a common architecture but differ in their exploration strategies and underlying algorithms. They typically use neural networks to predict rewards for different actions and employ various strategies to balance exploration and exploitation.

 
```

```

 Sources:

 
 - [tf_agents/bandits/agents/greedy_reward_prediction_agent.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/agents/greedy_reward_prediction_agent.py)
 - [tf_agents/bandits/agents/neural_linucb_agent.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/agents/neural_linucb_agent.py)
 - [tf_agents/bandits/agents/neural_epsilon_greedy_agent.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/agents/neural_epsilon_greedy_agent.py)
 - [tf_agents/bandits/agents/dropout_thompson_sampling_agent.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/agents/dropout_thompson_sampling_agent.py)
 
 
## Agent Types

 TF-Agents provides several bandit agent implementations, each with different exploration strategies:

 
### Greedy Reward Prediction Agent

 The `GreedyRewardPredictionAgent` is the base implementation that uses a neural network to predict rewards and takes greedy actions based on those predictions.

 
```

```

 Key features:

 
 - Uses a neural network to predict rewards for each action
 - Takes the action with the highest predicted reward
 - Supports action masking through observation splitting
 - Can incorporate constraints on actions
 - Supports Laplacian smoothing for actions with graph structure
 - Handles per-arm features for personalized recommendations
 
 Training flow:

 
 - Process experience data (observations, actions, rewards)
 - Compute reward predictions from the network
 - Calculate loss based on the difference between predicted and actual rewards
 - Apply optional Laplacian smoothing if actions have a graph structure
 - Update the network using gradient descent
 
 Sources:

 
 - [tf_agents/bandits/agents/greedy_reward_prediction_agent.py41-447](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/agents/greedy_reward_prediction_agent.py#L41-L447)
 - [tf_agents/bandits/policies/greedy_reward_prediction_policy.py24-61](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/policies/greedy_reward_prediction_policy.py#L24-L61)
 
 
### Neural LinUCB Agent

 The `NeuralLinUCBAgent` combines deep learning with the Linear Upper Confidence Bound (LinUCB) algorithm to balance exploration and exploitation.

 
```

```

 Key features:

 
 - Uses an encoding network to extract features from observations
 - Initially trains using direct reward prediction (epsilon-greedy exploration)
 - After a set number of training steps, switches to LinUCB for more efficient exploration
 - Maintains covariance matrices and data vectors for LinUCB calculations
 - Computes confidence bounds for exploration
 - Supports both global-only and per-arm observation models
 
 Training flow:

 
 - Process experience data
 - If still in initial training phase: 
 - Train the encoding network to predict rewards directly
 - If in LinUCB phase: 
 - Update covariance matrices and data vectors for LinUCB
 - Use LinUCB algorithm for action selection with confidence bounds
 
 Sources:

 
 - [tf_agents/bandits/agents/neural_linucb_agent.py100-687](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/agents/neural_linucb_agent.py#L100-L687)
 - [tf_agents/bandits/policies/neural_linucb_policy.py39-420](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/policies/neural_linucb_policy.py#L39-L420)
 
 
### Neural Epsilon Greedy Agent

 The `NeuralEpsilonGreedyAgent` extends the greedy agent by adding epsilon-greedy exploration.

 Key features:

 
 - With probability ε, selects a random action
 - With probability 1-ε, selects the greedy action
 - Inherits all functionality from `GreedyRewardPredictionAgent`
 - Simple but effective exploration strategy
 
 Sources:

 
 - [tf_agents/bandits/agents/neural_epsilon_greedy_agent.py37-164](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/agents/neural_epsilon_greedy_agent.py#L37-L164)
 
 
### Dropout Thompson Sampling Agent

 The `DropoutThompsonSamplingAgent` implements Thompson sampling through dropout in neural networks.

 Key features:

 
 - Uses dropout in neural networks to approximate Bayesian posterior sampling
 - Can apply dropout to all layers or just the top layer
 - Supports heteroscedastic modeling (estimating both mean and variance)
 - Balances exploration and exploitation through Bayesian uncertainty
 - Inherits core functionality from `GreedyRewardPredictionAgent`
 
 Sources:

 
 - [tf_agents/bandits/agents/dropout_thompson_sampling_agent.py40-194](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/agents/dropout_thompson_sampling_agent.py#L40-L194)
 
 
## Core Components and Workflow

 The bandit agents share common core components and a similar workflow:

 
```

```

 
### Agent-Policy-Network Relationship

 Bandit agents follow a structure where:

 
 - The agent contains the training logic and orchestrates the overall workflow
 - The policy determines action selection based on reward predictions
 - The network processes observations and predicts rewards
 
 This separation allows for reusing network architectures and policies across different agent implementations.

 
| Component | Responsibility | Example Classes |
|---|---|---|
| Agent | Training, exploration strategy, overall control | GreedyRewardPredictionAgent, NeuralLinUCBAgent |
| Policy | Action selection, handling action constraints | GreedyRewardPredictionPolicy, NeuralLinUCBPolicy |
| Network | Feature extraction, reward prediction | Any TF-Agents Network (custom or provided) |

 Sources:

 
 - [tf_agents/bandits/agents/greedy_reward_prediction_agent.py41-447](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/agents/greedy_reward_prediction_agent.py#L41-L447)
 - [tf_agents/bandits/policies/greedy_reward_prediction_policy.py24-61](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/policies/greedy_reward_prediction_policy.py#L24-L61)
 - [tf_agents/bandits/policies/neural_linucb_policy.py39-420](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/policies/neural_linucb_policy.py#L39-L420)
 
 
## Advanced Features

 
### Per-Arm Features

 Bandit agents can handle two types of observation models:

 
 - **Global-only features**: Each action is evaluated using the same observation
 - **Per-arm features**: Each action has its own feature vector, allowing for personalized recommendations
 
 When using per-arm features:

 
 - The reward network must process each arm's features individually
 - The agent keeps track of selected arm features for more efficient training
 - Only one sample count is maintained instead of one per action
 
 Sources:

 
 - [tf_agents/bandits/agents/greedy_reward_prediction_agent.py157-173](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/agents/greedy_reward_prediction_agent.py#L157-L173)
 - [tf_agents/bandits/agents/utils.py158-206](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/agents/utils.py#L158-L206)
 
 
### Action Masking

 Agents support action masking through the `observation_and_action_constraint_splitter` parameter, which:

 
 - Takes a full observation
 - Returns a tuple of (actual observation, action mask)
 - The action mask is a boolean tensor indicating which actions are valid
 - Only valid actions can be selected during inference
 
 Sources:

 
 - [tf_agents/bandits/agents/greedy_reward_prediction_agent.py54-56](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/agents/greedy_reward_prediction_agent.py#L54-L56)
 - [tf_agents/bandits/policies/greedy_reward_prediction_policy.py33-36](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/policies/greedy_reward_prediction_policy.py#L33-L36)
 
 
### Laplacian Smoothing

 For problems where actions have a graph structure (e.g., related actions should have similar rewards), the agents support Laplacian smoothing:

 
 - A Laplacian matrix represents the action graph structure
 - The smoothing regularizes the reward function to be smooth over the graph
 - This encourages similar rewards for related actions
 - The weight parameter controls the strength of the regularization
 
 Sources:

 
 - [tf_agents/bandits/agents/greedy_reward_prediction_agent.py69-91](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/agents/greedy_reward_prediction_agent.py#L69-L91)
 - [tf_agents/bandits/agents/utils.py58-154](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/agents/utils.py#L58-L154)
 
 
### Constraints

 Bandit agents can incorporate constraints on actions through the `constraints` parameter:

 
 - Constraints are implemented as neural networks
 - They can represent business rules, safety constraints, or other limitations
 - They are trained alongside the reward network
 - During inference, they filter out actions that violate constraints
 
 Sources:

 
 - [tf_agents/bandits/agents/greedy_reward_prediction_agent.py58-110](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/bandits/agents/greedy_reward_prediction_agent.py#L58-L110)
 
 
## Usage Examples

 
### Basic Usage of GreedyRewardPredictionAgent

 
```

```

 
### Using NeuralLinUCBAgent

 
```

```

 
## Conclusion

 The bandit agents in TF-Agents provide a flexible framework for solving contextual multi-armed bandit problems. By choosing the appropriate agent and configuring its exploration strategy, developers can effectively balance exploration and exploitation in a wide range of decision-making scenarios.

 For more detailed information about specific bandit agent implementations, see:

 
 - [Greedy Reward Prediction](https://deepwiki.com/tensorflow/agents/4.1-greedy-reward-prediction)
 - [Neural LinUCB](https://deepwiki.com/tensorflow/agents/4.2-neural-linucb)
 - [Neural Epsilon Greedy and Thompson Sampling](https://deepwiki.com/tensorflow/agents/4.3-neural-epsilon-greedy-and-thompson-sampling)
