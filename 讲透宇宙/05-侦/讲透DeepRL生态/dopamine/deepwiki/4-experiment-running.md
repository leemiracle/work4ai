> 来源: [https://deepwiki.com/google/dopamine/4-experiment-running](https://deepwiki.com/google/dopamine/4-experiment-running)
> DeepWiki google/dopamine | Last indexed: 18 April 2025 (bec5f4

# Experiment Running

  Relevant source files 
 - [dopamine/discrete_domains/logger.py](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/logger.py)
 - [dopamine/discrete_domains/run_experiment.py](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/run_experiment.py)
 - [tests/dopamine/atari_init_test.py](https://github.com/google/dopamine/blob/bec5f4e1/tests/dopamine/atari_init_test.py)
 - [tests/dopamine/discrete_domains/run_experiment_test.py](https://github.com/google/dopamine/blob/bec5f4e1/tests/dopamine/discrete_domains/run_experiment_test.py)
 - [tests/dopamine/tests/gin_config_test.py](https://github.com/google/dopamine/blob/bec5f4e1/tests/dopamine/tests/gin_config_test.py)
 - [tests/dopamine/tests/integration_test.py](https://github.com/google/dopamine/blob/bec5f4e1/tests/dopamine/tests/integration_test.py)
 
  This page documents the experiment running system in Dopamine, which provides a framework for setting up, executing, and tracking reinforcement learning experiments. This system handles the lifecycle of experiments, including initialization, training/evaluation loops, checkpointing, and metrics collection.

 For information about specific runner implementations, see [Runner System](https://deepwiki.com/google/dopamine/4.1-runner-system). For details on how to configure experiments, see [Configuration with Gin](https://deepwiki.com/google/dopamine/4.2-configuration-with-gin).

 
## Overview

 The experiment running system in Dopamine provides a standardized way to train and evaluate reinforcement learning agents across various environments. It manages the interaction between agents and environments, collects performance metrics, and handles experiment resumption through checkpointing.

 
```

```

 Sources:

 
 - [dopamine/discrete_domains/run_experiment.py714-739](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/run_experiment.py#L714-L739)
 - [dopamine/discrete_domains/run_experiment.py572-620](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/run_experiment.py#L572-L620)
 - [dopamine/discrete_domains/run_experiment.py515-570](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/run_experiment.py#L515-L570)
 
 
## Key Components

 
### Runner

 The `Runner` class is the central component for conducting experiments. It orchestrates the interaction between the agent and environment, manages training and evaluation phases, and handles checkpointing and logging.

 
```

```

 Sources:

 
 - [dopamine/discrete_domains/run_experiment.py162-741](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/run_experiment.py#L162-L741)
 - [dopamine/discrete_domains/run_experiment.py742-846](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/run_experiment.py#L742-L846)
 
 
#### Initialization

 The `Runner` initializes all necessary components for an experiment:

 
 - Environment for agent interaction
 - Agent with specific algorithm implementation
 - Checkpointer for saving/loading experiment state
 - Logger for recording metrics
 - TensorBoard summary writer for visualization
 - Collector dispatcher for metrics collection
 
 
```

```

 Sources:

 
 - [dopamine/discrete_domains/run_experiment.py181-269](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/run_experiment.py#L181-L269)
 
 
### Running an Experiment

 The main method for executing an experiment is `run_experiment()`, which runs the experiment for the specified number of iterations.

 
```

```

 Sources:

 
 - [dopamine/discrete_domains/run_experiment.py714-739](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/run_experiment.py#L714-L739)
 - [dopamine/discrete_domains/run_experiment.py515-546](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/run_experiment.py#L515-L546)
 - [dopamine/discrete_domains/run_experiment.py548-570](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/run_experiment.py#L548-L570)
 - [dopamine/discrete_domains/run_experiment.py390-429](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/run_experiment.py#L390-L429)
 
 
### Training and Evaluation

 The experiment alternates between training and evaluation phases:

 
 - **Training Phase**: The agent interacts with the environment and learns from experience.

 
 - The agent's `eval_mode` is set to `False`
 - Runs for `training_steps` steps across multiple episodes
 - Updates the neural network based on experiences
 - **Evaluation Phase**: The agent's performance is evaluated without learning.

 
 - The agent's `eval_mode` is set to `True`
 - Runs for `evaluation_steps` steps across multiple episodes
 - No network updates during this phase
 
 Sources:

 
 - [dopamine/discrete_domains/run_experiment.py515-546](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/run_experiment.py#L515-L546)
 - [dopamine/discrete_domains/run_experiment.py548-570](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/run_experiment.py#L548-L570)
 
 
### Episode Handling

 Episodes are managed through two key methods:

 
 - `_run_one_episode()`: Runs a single episode from start to finish, with a maximum number of steps defined by `max_steps_per_episode`.
 - `_run_continued_episode()`: Allows for episodes to continue across iterations, which is useful for very long episodes or when training with a fixed number of steps rather than episodes.
 
 
```

```

 Sources:

 
 - [dopamine/discrete_domains/run_experiment.py390-429](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/run_experiment.py#L390-L429)
 - [dopamine/discrete_domains/run_experiment.py430-468](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/run_experiment.py#L430-L468)
 
 
### Checkpointing and Logging

 The experiment runner includes systems for checkpointing and logging:

 
 - **Checkpointing**: Saves the state of the experiment (including agent parameters) to disk, allowing experiments to be resumed.

 
 - Implemented in the `_checkpoint_experiment()` method
 - Uses the `Checkpointer` class to manage checkpoint files
 - **Logging**: Records metrics and statistics about the experiment.

 
 - Traditional logging with the `Logger` class (being deprecated)
 - Modern metrics collection with the `CollectorDispatcher`
 - TensorBoard integration for visualization
 
 Sources:

 
 - [dopamine/discrete_domains/run_experiment.py699-713](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/run_experiment.py#L699-L713)
 - [dopamine/discrete_domains/run_experiment.py685-698](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/run_experiment.py#L685-L698)
 - [dopamine/discrete_domains/run_experiment.py622-684](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/run_experiment.py#L622-L684)
 
 
### TrainRunner

 The `TrainRunner` is a specialized version of `Runner` that only performs the training phase without evaluation. This is useful for cases where evaluation is not needed or is performed separately.

 The key differences from the base `Runner` class:

 
 - Only runs the training phase in `_run_one_iteration()`
 - Simplified TensorBoard summary generation (only training metrics)
 
 Sources:

 
 - [dopamine/discrete_domains/run_experiment.py742-846](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/run_experiment.py#L742-L846)
 
 
## Configuration with Gin

 Dopamine uses the Gin configuration framework for flexible parameter injection. This allows for modifying experiment parameters without changing the code.

 
### Loading Configurations

 Configurations are loaded using the `load_gin_configs()` function, which accepts:

 
 - `gin_files`: List of paths to Gin configuration files
 - `gin_bindings`: List of parameter bindings to override values in the config files
 
 
```

```

 Sources:

 
 - [dopamine/discrete_domains/run_experiment.py47-58](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/run_experiment.py#L47-L58)
 - [tests/dopamine/tests/gin_config_test.py73-84](https://github.com/google/dopamine/blob/bec5f4e1/tests/dopamine/tests/gin_config_test.py#L73-L84)
 
 
### Configurable Components

 Many components in the experiment running system are Gin-configurable:

 
 - **Runner** - Controls experiment execution parameters

 
 - `training_steps` - Number of steps per training phase
 - `evaluation_steps` - Number of steps per evaluation phase
 - `num_iterations` - Total number of iterations
 - `max_steps_per_episode` - Maximum steps per episode
 - **Agent creation** - Configures which agent to use and its parameters

 
 - `agent_name` - Name of the agent type to create
 - Agent-specific parameters (e.g., `epsilon_decay_period`, `update_horizon`)
 - **Environment creation** - Configures the environment

 
 - Environment-specific parameters (e.g., `game_name`, `sticky_actions`)
 
 Sources:

 
 - [dopamine/discrete_domains/run_experiment.py136-158](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/run_experiment.py#L136-L158)
 - [dopamine/discrete_domains/run_experiment.py61-132](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/run_experiment.py#L61-L132)
 - [tests/dopamine/tests/gin_config_test.py49-58](https://github.com/google/dopamine/blob/bec5f4e1/tests/dopamine/tests/gin_config_test.py#L49-L58)
 
 
## Example: Running an Experiment

 Here's a simple workflow for running an experiment in Dopamine:

 
 - **Setup Configuration**: Create or modify Gin configuration files
 - **Initialize Runner**: Create a runner with appropriate parameters
 - **Run Experiment**: Call `run_experiment()` on the runner
 - **Analyze Results**: Examine logs, checkpoints, and TensorBoard summaries
 
 
```

```

 Sources:

 
 - [tests/dopamine/tests/integration_test.py47-58](https://github.com/google/dopamine/blob/bec5f4e1/tests/dopamine/tests/integration_test.py#L47-L58)
 - [tests/dopamine/tests/integration_test.py88-95](https://github.com/google/dopamine/blob/bec5f4e1/tests/dopamine/tests/integration_test.py#L88-L95)
 
 
## Integration with Other Systems

 The experiment running system integrates with several other components in Dopamine:

 
 - **Agents**: Through the `create_agent_fn` parameter, which creates a specific agent type
 - **Environments**: Through the `create_environment_fn` parameter, which creates the environment
 - **Checkpointing**: Through the `Checkpointer` class for saving and loading experiment state
 - **Logging**: Through the `Logger` and `CollectorDispatcher` for recording metrics
 - **TensorBoard**: For visualizing experiment progress and results
 
 Sources:

 
 - [dopamine/discrete_domains/run_experiment.py265-277](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/run_experiment.py#L265-L277)
 - [dopamine/discrete_domains/run_experiment.py307-354](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/run_experiment.py#L307-L354)
 
 
## Summary

 The experiment running system in Dopamine provides a flexible and powerful framework for conducting reinforcement learning experiments. It handles the complexities of agent-environment interaction, training and evaluation loops, metrics collection, and experiment resumption, allowing researchers to focus on algorithm development rather than experimental infrastructure.

 The system is highly configurable through Gin, making it easy to modify experiment parameters without changing the code. This facilitates rapid iteration and experimentation, which is essential for reinforcement learning research.
