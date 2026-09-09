> 来源: [https://deepwiki.com/thu-ml/tianshou/6-high-level-api](https://deepwiki.com/thu-ml/tianshou/6-high-level-api)
> DeepWiki thu-ml/tianshou | Last indexed: 19 April 2025 (90846f

# High-Level API

  Relevant source files 
 - [examples/atari/atari_wrapper.py](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/atari/atari_wrapper.py)
 - [examples/mujoco/mujoco_env.py](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/mujoco/mujoco_env.py)
 - [tianshou/highlevel/agent.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/highlevel/agent.py)
 - [tianshou/highlevel/config.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/highlevel/config.py)
 - [tianshou/highlevel/env.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/highlevel/env.py)
 - [tianshou/highlevel/experiment.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/highlevel/experiment.py)
 - [tianshou/highlevel/logger.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/highlevel/logger.py)
 - [tianshou/highlevel/module/actor.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/highlevel/module/actor.py)
 - [tianshou/highlevel/module/critic.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/highlevel/module/critic.py)
 - [tianshou/highlevel/module/module_opt.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/highlevel/module/module_opt.py)
 - [tianshou/highlevel/optim.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/highlevel/optim.py)
 - [tianshou/highlevel/params/policy_params.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/highlevel/params/policy_params.py)
 
  The High-Level API in Tianshou provides a simplified interface for setting up and running reinforcement learning experiments. It abstracts away much of the boilerplate code required when using the lower-level components directly, making it easier to experiment with different algorithms and configurations while maintaining flexibility. For more detailed information about the specific implementation of RL algorithms, see [Policy Framework](https://deepwiki.com/thu-ml/tianshou/3-policy-framework).

 
## Architecture

 The High-Level API is built as a layer on top of Tianshou's core components, providing a more user-friendly interface through an experiment-oriented approach.

 
### High-Level API Overview

 
```

```

 Sources: [tianshou/highlevel/experiment.py1-687](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/highlevel/experiment.py#L1-L687)

 
### Workflow

 The typical workflow for using the High-Level API involves configuring an experiment via a builder, creating the experiment, and then running it.

 
```

```

 Sources: [tianshou/highlevel/experiment.py351-454](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/highlevel/experiment.py#L351-L454)

 
## Key Components

 
### ExperimentConfig

 `ExperimentConfig` is a dataclass that contains configuration parameters common to all reinforcement learning experiments:

 
```

```

 Sources: [tianshou/highlevel/experiment.py120-147](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/highlevel/experiment.py#L120-L147)

 
### SamplingConfig

 `SamplingConfig` controls the data collection, batch sizes, buffer configurations, and training loop parameters:

 
```

```

 Sources: [tianshou/highlevel/config.py10-192](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/highlevel/config.py#L10-L192)

 
### Experiment

 The `Experiment` class represents a complete reinforcement learning experiment, combining configuration, environment, agent, and training setup:

 
```

```

 Sources: [tianshou/highlevel/experiment.py165-470](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/highlevel/experiment.py#L165-L470)

 
### World

 The `World` class serves as a container for all the essential components needed in an RL experiment:

 
 - Environment instances for training, testing, and visualization
 - Policy (agent) instance
 - Collectors for gathering experience
 - Trainer for optimization
 - Logger for metrics collection
 - Persistence mechanisms for saving/loading
 
 Sources: [tianshou/highlevel/experiment.py347-370](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/highlevel/experiment.py#L347-L370)

 
### ExperimentBuilder

 `ExperimentBuilder` follows the builder pattern to simplify experiment configuration:

 
```

```

 Algorithm-specific builders (like `PPOExperimentBuilder`, `DQNExperimentBuilder`, etc.) inherit from `ExperimentBuilder` and provide additional configuration options specific to each algorithm.

 Sources: [tianshou/highlevel/experiment.py490-685](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/highlevel/experiment.py#L490-L685)

 
## Agent and Environment Factories

 The High-Level API uses factories to create agent (policy) and environment instances, promoting clean separation of concerns.

 
### AgentFactory

 `AgentFactory` is responsible for creating policies, collectors, and trainers:

 
```

```

 Sources: [tianshou/highlevel/agent.py85-627](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/highlevel/agent.py#L85-L627)

 
### EnvFactory

 `EnvFactory` is responsible for creating environments:

 
```

```

 Sources: [tianshou/highlevel/env.py364-501](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/highlevel/env.py#L364-L501) [examples/mujoco/mujoco_env.py40-117](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/mujoco/mujoco_env.py#L40-L117) [examples/atari/atari_wrapper.py391-469](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/atari/atari_wrapper.py#L391-L469)

 
## Builder Pattern Usage

 The High-Level API extensively uses the builder pattern to simplify experiment configuration:

 
```

```

 The builder pattern makes it easy to customize various aspects of the experiment while keeping the code clean and readable. Each `with_*` method returns the builder itself, allowing method calls to be chained.

 Sources: [tianshou/highlevel/experiment.py545-633](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/highlevel/experiment.py#L545-L633)

 
## Multiple Experiments

 For statistical evaluation, it's common to run experiments with multiple random seeds. The `ExperimentCollection` class makes this easy:

 
```

```

 The `build_seeded_collection` method automatically creates multiple experiments with different seeds:

 
```

```

 Sources: [tianshou/highlevel/experiment.py473-487](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/highlevel/experiment.py#L473-L487) [tianshou/highlevel/experiment.py665-685](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/highlevel/experiment.py#L665-L685)

 
## Neural Network Factories

 The High-Level API includes factories for creating neural network components such as actors and critics:

 
```

```

 These factories make it easy to create neural network components with customizable architectures.

 Sources: [tianshou/highlevel/module/actor.py50-299](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/highlevel/module/actor.py#L50-L299) [tianshou/highlevel/module/critic.py17-304](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/highlevel/module/critic.py#L17-L304)

 
## Optimizer Factories

 The High-Level API includes factories for creating optimizers:

 
```

```

 The default optimizer is Adam, but you can customize it or use a different optimizer like RMSprop.

 Sources: [tianshou/highlevel/optim.py17-93](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/highlevel/optim.py#L17-L93)

 
## Logger Factory

 The High-Level API includes a factory for creating loggers:

 
```

```

 The default logger uses TensorBoard, but you can also use Weights & Biases (wandb) for more advanced experiment tracking.

 Sources: [tianshou/highlevel/logger.py13-106](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/highlevel/logger.py#L13-L106)

 
## Example Usage

 Here's a complete example showing how to use the High-Level API:

 
```

```

 
## Persistence and Resumption

 The High-Level API supports saving and resuming experiments:

 
```

```

 The experiment saves not only the configuration but also the policy (neural network parameters), allowing you to resume training or evaluate a trained policy later.

 Sources: [tianshou/highlevel/experiment.py202-214](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/highlevel/experiment.py#L202-L214) [tianshou/highlevel/experiment.py239-246](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/highlevel/experiment.py#L239-L246)

 
## Summary

 The High-Level API provides a simplified interface for setting up and running reinforcement learning experiments in Tianshou. It offers:

 
 - A declarative approach to defining experiments
 - Support for a wide range of RL algorithms
 - Customizable neural network architectures and optimization settings
 - Experiment persistence and resumption
 - Tools for running multiple experiments with different seeds
 - Integration with logging and visualization tools
 
 By abstracting away many of the implementation details, the High-Level API makes it easier to iterate on experiments while maintaining the flexibility to customize all aspects of the reinforcement learning setup when needed.
