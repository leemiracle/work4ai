> 来源: [https://deepwiki.com/rlworkgroup/garage/2-core-architecture](https://deepwiki.com/rlworkgroup/garage/2-core-architecture)
> DeepWiki rlworkgroup/garage | Last indexed: 25 April 2025 (2d5948

# Core Architecture

  Relevant source files 
 - [.editorconfig](https://github.com/rlworkgroup/garage/blob/2d594803/.editorconfig)
 - [.github/workflows/ci-release-2021.03.yml](https://github.com/rlworkgroup/garage/blob/2d594803/.github/workflows/ci-release-2021.03.yml)
 - [.mdlrc](https://github.com/rlworkgroup/garage/blob/2d594803/.mdlrc)
 - [README.md](https://github.com/rlworkgroup/garage/blob/2d594803/README.md?plain=1)
 - [docs/index.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/index.md?plain=1)
 - [docs/user/algo_bc.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_bc.md?plain=1)
 - [docs/user/algo_cem.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_cem.md?plain=1)
 - [docs/user/algo_ddpg.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_ddpg.md?plain=1)
 - [docs/user/algo_dqn.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_dqn.md?plain=1)
 - [docs/user/algo_erwr.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_erwr.md?plain=1)
 - [docs/user/algo_maml.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_maml.md?plain=1)
 - [docs/user/algo_mtppo.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_mtppo.md?plain=1)
 - [docs/user/algo_mttrpo.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_mttrpo.md?plain=1)
 - [docs/user/algo_pearl.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_pearl.md?plain=1)
 - [docs/user/algo_ppo.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_ppo.md?plain=1)
 - [docs/user/algo_rl2.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_rl2.md?plain=1)
 - [docs/user/algo_sac.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_sac.md?plain=1)
 - [docs/user/algo_td3.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_td3.md?plain=1)
 - [docs/user/algo_trpo.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_trpo.md?plain=1)
 - [docs/user/algo_vpg.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_vpg.md?plain=1)
 - [docs/user/images/dqn_plots.png](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/images/dqn_plots.png)
 - [docs/user/images/numpy.png](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/images/numpy.png)
 - [docs/user/references.bib](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/references.bib)
 - [scripts/garage](https://github.com/rlworkgroup/garage/blob/2d594803/scripts/garage)
 - [src/garage/experiment/experiment.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/experiment/experiment.py)
 - [src/garage/trainer.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/trainer.py)
 - [tests/fixtures/envs/dummy/dummy_multitask_box_env.py](https://github.com/rlworkgroup/garage/blob/2d594803/tests/fixtures/envs/dummy/dummy_multitask_box_env.py)
 - [tests/garage/experiment/test_experiment.py](https://github.com/rlworkgroup/garage/blob/2d594803/tests/garage/experiment/test_experiment.py)
 - [tests/garage/experiment/test_task_sampler.py](https://github.com/rlworkgroup/garage/blob/2d594803/tests/garage/experiment/test_task_sampler.py)
 - [tests/integration_tests/test_sigint.py](https://github.com/rlworkgroup/garage/blob/2d594803/tests/integration_tests/test_sigint.py)
 
  The garage reinforcement learning framework is organized around a modular design that separates concerns like experiment management, algorithm implementation, environment interaction, and model training. This page provides an overview of the major components and their relationships in the garage framework. It explains how these components fit together to create a flexible and extensible system for reinforcement learning research.

 For information about specific data structures used throughout the framework, see [Data Structures](https://deepwiki.com/rlworkgroup/garage/2.1-data-structures). For details on the experiment system including the wrap_experiment decorator, see [Experiment System](https://deepwiki.com/rlworkgroup/garage/2.2-experiment-system). For information about the Trainer system, see [Trainer](https://deepwiki.com/rlworkgroup/garage/2.3-trainer). For details on how samplers collect experiences, see [Samplers](https://deepwiki.com/rlworkgroup/garage/2.4-samplers).

 
## System Overview

 At a high level, garage is organized around several key components that work together to implement and evaluate reinforcement learning algorithms:

 
```

```

 The framework provides a layered architecture where:

 
 - Experiments define the overall execution context
 - Trainers manage the training process
 - Algorithms implement specific RL techniques
 - Samplers collect experiences from environments
 - Data structures organize and store experiences
 
 Sources: [src/garage/experiment/experiment.py1-696](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/experiment/experiment.py#L1-L696) [src/garage/trainer.py1-666](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/trainer.py#L1-L666) [README.md1-176](https://github.com/rlworkgroup/garage/blob/2d594803/README.md?plain=1#L1-L176)

 
## Core Components

 
### Experiment System

 The experiment system provides a standardized way to configure, run, and log reinforcement learning experiments. The central component is the `wrap_experiment` decorator, which creates an experiment context that manages directories, logging, and snapshots.

 
```

```

 A typical experiment workflow:

 
 - User defines an experiment function and decorates it with `@wrap_experiment`
 - When called, the decorator creates an `ExperimentContext` which sets up logging and snapshotting
 - The experiment function receives this context as its first parameter (`ctxt`)
 - The context configures where logs and snapshots are stored
 
 Sources: [src/garage/experiment/experiment.py75-448](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/experiment/experiment.py#L75-L448) [docs/user/index.md15-38](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/index.md?plain=1#L15-L38)

 
### Trainer

 The Trainer class manages the training process for reinforcement learning algorithms. It provides a standardized interface for setting up algorithms and environments, running training loops, and handling logging and snapshots.

 
```

```

 Key aspects of the Trainer:

 
 - The `setup(algo, env)` method configures the algorithm and environment
 - The `train()` method starts the training process, delegating to the algorithm's `train` method
 - The `step_epochs()` generator manages the training loop, yielding each epoch
 - The `obtain_episodes()` method collects experiences from the environment using a sampler
 - The `save()` method snapshots the current state of training
 
 The `TFTrainer` extends the base `Trainer` with TensorFlow-specific functionality, such as session management.

 Sources: [src/garage/trainer.py60-529](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/trainer.py#L60-L529) [src/garage/trainer.py533-665](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/trainer.py#L533-L665)

 
### Algorithms

 Garage provides implementations of many reinforcement learning algorithms across different frameworks (TensorFlow, PyTorch, NumPy). Algorithms are organized into a hierarchy based on their characteristics (on-policy vs. off-policy, policy gradient vs. Q-learning, etc.).

 
```

```

 Each algorithm implements a common interface that includes methods like:

 
 - `train(trainer)`: The main training method called by the Trainer
 - `train_once(episodes)`: Performs a single update step using collected episodes
 - Policy handling methods for updating policy parameters
 
 The framework-specific implementations (TensorFlow, PyTorch, NumPy) provide optimized versions that leverage the specific capabilities of each framework.

 Sources: [README.md61-89](https://github.com/rlworkgroup/garage/blob/2d594803/README.md?plain=1#L61-L89) [docs/user/algo_trpo.md1-51](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_trpo.md?plain=1#L1-L51) [docs/user/algo_ppo.md1-61](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_ppo.md?plain=1#L1-L61) [docs/user/algo_sac.md1-65](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_sac.md?plain=1#L1-L65) [docs/user/algo_td3.md1-95](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_td3.md?plain=1#L1-L95)

 
### Samplers

 Samplers are responsible for collecting experiences from environments. They coordinate workers that interact with environments and collect the resulting transitions into standardized data structures like `EpisodeBatch`.

 
```

```

 Key aspects of the Sampler system:

 
 - Samplers coordinate workers to collect experiences
 - Workers interact with environments using policies
 - The `LocalSampler` runs workers in the local process
 - The `RaySampler` distributes workers across multiple processes using Ray
 - The collected experiences are organized into standardized data structures like `EpisodeBatch`
 
 Sources: [README.md13-26](https://github.com/rlworkgroup/garage/blob/2d594803/README.md?plain=1#L13-L26)

 
### Data Structures

 Garage uses several core data structures to represent and manage reinforcement learning experiences:

 
```

```

 These data structures provide a standardized way to represent and manipulate reinforcement learning experiences throughout the framework:

 
 - `TimeStep`: Represents a single transition (observation, action, reward, next observation, terminal)
 - `TimeStepBatch`: A batch of transitions
 - `Episode`: A sequence of transitions representing a complete episode
 - `EpisodeBatch`: A batch of episodes, often collected from multiple environments
 - `ReplayBuffer`: Stores experiences for off-policy learning algorithms
 - `PathBuffer`: A specialized replay buffer for storing trajectories
 
 Sources: [README.md13-26](https://github.com/rlworkgroup/garage/blob/2d594803/README.md?plain=1#L13-L26)

 
## Framework Implementations

 Garage provides implementations of its components across multiple frameworks to support different research needs and preferences.

 
```

```

 Each framework implementation provides:

 
 - Algorithm implementations optimized for that framework
 - Policy implementations (neural network models)
 - Value function and Q-function implementations
 - Framework-specific utilities and helpers
 
 Many algorithms are implemented across multiple frameworks, allowing users to choose the framework that best fits their needs or to compare implementations between frameworks.

 Sources: [README.md90-108](https://github.com/rlworkgroup/garage/blob/2d594803/README.md?plain=1#L90-L108)

 
## Experiment Workflow

 The following diagram illustrates the typical workflow of an experiment in garage, showing how the different components interact during the training process:

 
```

```

 A typical experiment in garage follows these steps:

 
 - User defines an experiment function decorated with `@wrap_experiment`
 - The experiment function sets up the algorithm and environment
 - The trainer is configured and training is started
 - During each epoch, the trainer: 
 - Collects experiences using the sampler
 - Passes experiences to the algorithm for updating
 - Logs metrics and saves snapshots
 - After training completes, the final model and metrics are available for evaluation
 
 Sources: [src/garage/trainer.py355-399](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/trainer.py#L355-L399) [src/garage/experiment/experiment.py317-373](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/experiment/experiment.py#L317-L373)

 
## Code Example

 Here's a simplified example of how these components work together in a garage experiment:

 
```

```

 This example demonstrates how the components fit together:

 
 - The experiment is wrapped with `@wrap_experiment` to set up logging and snapshotting
 - The environment, policy, and value function are created
 - A sampler is created to collect experiences
 - The algorithm is initialized with the policy, value function, and sampler
 - The trainer is set up with the algorithm and environment
 - Training is started, and the trainer manages the training loop
 
 Sources: [docs/user/algo_ppo.md32-48](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_ppo.md?plain=1#L32-L48)

 
## Conclusion

 The core architecture of garage provides a flexible and modular framework for reinforcement learning research. By separating concerns like experiment management, training, sampling, and algorithm implementation, garage enables researchers to focus on the components they want to modify while reusing the rest.

 The framework's support for multiple implementations (TensorFlow, PyTorch, NumPy) allows users to choose the tools that best fit their needs, and the standardized interfaces make it easy to compare different algorithms and approaches.
