> 来源: [https://deepwiki.com/tensorflow/agents/6-policy-system](https://deepwiki.com/tensorflow/agents/6-policy-system)
> DeepWiki tensorflow/agents | Last indexed: 24 April 2025 (2a236d

# Policy System

  Relevant source files 
 - [tf_agents/policies/boltzmann_policy.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/boltzmann_policy.py)
 - [tf_agents/policies/epsilon_greedy_policy.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/epsilon_greedy_policy.py)
 - [tf_agents/policies/epsilon_greedy_policy_test.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/epsilon_greedy_policy_test.py)
 - [tf_agents/policies/greedy_policy.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/greedy_policy.py)
 - [tf_agents/policies/policy_saver.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/policy_saver.py)
 - [tf_agents/policies/policy_saver_test.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/policy_saver_test.py)
 - [tf_agents/policies/py_epsilon_greedy_policy.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/py_epsilon_greedy_policy.py)
 - [tf_agents/policies/py_tf_eager_policy.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/py_tf_eager_policy.py)
 - [tf_agents/policies/py_tf_eager_policy_test.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/py_tf_eager_policy_test.py)
 - [tf_agents/policies/random_tf_policy.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/random_tf_policy.py)
 - [tf_agents/policies/random_tf_policy_test.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/random_tf_policy_test.py)
 - [tf_agents/policies/scripted_py_policy.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/scripted_py_policy.py)
 - [tf_agents/policies/tf_py_policy.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/tf_py_policy.py)
 - [tf_agents/policies/tf_py_policy_test.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/tf_py_policy_test.py)
 
  The Policy System in TF-Agents provides the core mechanisms for agent decision-making. A policy defines how an agent selects actions based on observations of the environment. This document covers the policy architecture, key policy types, policy conversion between TensorFlow and Python, and policy saving/loading mechanisms. For information about specific agent implementations that use these policies, see [Reinforcement Learning Agents](https://deepwiki.com/tensorflow/agents/3-reinforcement-learning-agents).

 
## Policy Architecture

 The TF-Agents policy system is built around two primary base classes: `TFPolicy` for TensorFlow-based policies and `PyPolicy` for Python-based policies. These provide interfaces for selecting actions based on environment observations.

 
```

```

 Sources:

 
 - [tf_agents/policies/tf_py_policy.py37-188](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/tf_py_policy.py#L37-L188)
 - [tf_agents/policies/py_tf_eager_policy.py39-145](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/py_tf_eager_policy.py#L39-L145)
 - [tf_agents/policies/epsilon_greedy_policy.py42-216](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/epsilon_greedy_policy.py#L42-L216)
 - [tf_agents/policies/greedy_policy.py42-90](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/greedy_policy.py#L42-L90)
 - [tf_agents/policies/random_tf_policy.py68-256](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/random_tf_policy.py#L68-L256)
 - [tf_agents/policies/boltzmann_policy.py31-91](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/boltzmann_policy.py#L31-L91)
 
 
## Policy Components and Data Flow

 Policies transform observations into actions through a well-defined flow. The diagram below shows how policies interact with other components in the TF-Agents framework:

 
```

```

 Sources:

 
 - [tf_agents/policies/py_tf_eager_policy.py39-145](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/py_tf_eager_policy.py#L39-L145)
 - [tf_agents/policies/tf_py_policy.py37-188](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/tf_py_policy.py#L37-L188)
 
 
## Core Policy Classes

 
### TFPolicy

 `TFPolicy` is the base class for all TensorFlow-based policies. It defines the core interface with these methods:

 
 - `action(time_step, policy_state, seed=None)`: Returns a PolicyStep containing the action to take, the next policy state, and any extra info.
 - `distribution(time_step, policy_state)`: Returns distributions over possible actions.
 - `get_initial_state(batch_size)`: Provides the initial policy state.
 
 Specific implementations override the protected methods `_action()` and `_distribution()` to define custom policy behavior.

 
### PyPolicy

 `PyPolicy` is the base class for Python-based policies, with a similar interface to `TFPolicy` but implemented in Python:

 
 - `action(time_step, policy_state, seed=None)`: Returns a PolicyStep.
 - `get_initial_state(batch_size)`: Provides the initial policy state.
 
 Implementations override the protected method `_action()`.

 Sources:

 
 - [tf_agents/policies/py_tf_eager_policy.py39-145](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/py_tf_eager_policy.py#L39-L145)
 - [tf_agents/policies/tf_py_policy.py37-188](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/tf_py_policy.py#L37-L188)
 
 
## Policy Types

 TF-Agents provides several standard policy implementations:

 
### Greedy Policy

 `GreedyPolicy` always selects the action with the highest expected value. It wraps another policy and transforms that policy's action distribution by selecting the mode of the distribution.

 
```

```

 
### Epsilon-Greedy Policy

 `EpsilonGreedyPolicy` balances exploration and exploitation by selecting random actions with probability epsilon, and greedy actions otherwise.

 
```

```

 
### Random Policy

 `RandomTFPolicy` selects actions randomly according to the action spec, useful for pure exploration or as a baseline.

 
```

```

 
### Boltzmann Policy

 `BoltzmannPolicy` applies a temperature parameter to the action distribution, controlling the randomness of action selection.

 
```

```

 Sources:

 
 - [tf_agents/policies/greedy_policy.py42-90](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/greedy_policy.py#L42-L90)
 - [tf_agents/policies/epsilon_greedy_policy.py42-216](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/epsilon_greedy_policy.py#L42-L216)
 - [tf_agents/policies/random_tf_policy.py68-256](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/random_tf_policy.py#L68-L256)
 - [tf_agents/policies/boltzmann_policy.py31-91](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/boltzmann_policy.py#L31-L91)
 
 
## Policy Conversion

 TF-Agents provides mechanisms to convert between TensorFlow and Python policies:

 
```

```

 
### TFPyPolicy

 `TFPyPolicy` wraps a Python policy so it can be used where a TensorFlow policy is expected:

 
```

```

 
### PyTFEagerPolicy

 `PyTFEagerPolicy` wraps a TensorFlow policy for use in Python environments:

 
```

```

 Sources:

 
 - [tf_agents/policies/tf_py_policy.py37-188](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/tf_py_policy.py#L37-L188)
 - [tf_agents/policies/py_tf_eager_policy.py39-145](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/py_tf_eager_policy.py#L39-L145)
 
 
## Policy Saving and Loading

 TF-Agents allows policies to be saved and loaded across different contexts:

 
```

```

 
### PolicySaver

 `PolicySaver` saves TensorFlow policies to disk in a format that can be loaded and executed later:

 
```

```

 The saved policy includes these signatures:

 
 - `action`: Takes a time step and policy state, returns a policy step
 - `get_initial_state`: Returns the initial policy state
 - `get_train_step`: Returns the saved training step
 - `get_metadata`: Returns policy metadata
 
 
### SavedModelPyTFEagerPolicy

 `SavedModelPyTFEagerPolicy` loads a saved policy for use in Python:

 
```

```

 Alternatively, you can load the specs from the saved policy:

 
```

```

 Sources:

 
 - [tf_agents/policies/policy_saver.py103-720](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/policy_saver.py#L103-L720)
 - [tf_agents/policies/py_tf_eager_policy.py150-293](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/py_tf_eager_policy.py#L150-L293)
 
 
## Policy Usage Examples

 
### Creating and Using a Basic Policy

 
```

```

 
### Policy With Exploration

 
```

```

 
### Saving and Loading a Policy

 
```

```

 Sources:

 
 - [tf_agents/policies/policy_saver_test.py143-147](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/policy_saver_test.py#L143-L147)
 - [tf_agents/policies/py_tf_eager_policy_test.py130-143](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/py_tf_eager_policy_test.py#L130-L143)
 - [tf_agents/policies/epsilon_greedy_policy_test.py102-128](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/epsilon_greedy_policy_test.py#L102-L128)
 
 
## Summary

 The Policy System in TF-Agents provides a flexible framework for implementing decision-making strategies for reinforcement learning agents. It supports both TensorFlow and Python implementations, various exploration strategies, and seamless saving and loading for deployment. This modularity allows users to easily experiment with different policies while maintaining a consistent interface.

 Sources:

 
 - [tf_agents/policies/policy_saver.py103-720](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/policy_saver.py#L103-L720)
 - [tf_agents/policies/py_tf_eager_policy.py39-293](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/py_tf_eager_policy.py#L39-L293)
 - [tf_agents/policies/tf_py_policy.py37-188](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/policies/tf_py_policy.py#L37-L188)
