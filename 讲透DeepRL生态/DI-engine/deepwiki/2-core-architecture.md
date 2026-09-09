> 来源: [https://deepwiki.com/opendilab/DI-engine/2-core-architecture](https://deepwiki.com/opendilab/DI-engine/2-core-architecture)
> DeepWiki opendilab/DI-engine | Last indexed: 20 April 2025 (c290a6

# Core Architecture

  Relevant source files 
 - [CHANGELOG](https://github.com/opendilab/DI-engine/blob/c290a673/CHANGELOG)
 - [README.md](https://github.com/opendilab/DI-engine/blob/c290a673/README.md?plain=1)
 - [conda/meta.yaml](https://github.com/opendilab/DI-engine/blob/c290a673/conda/meta.yaml)
 - [ding/__init__.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/__init__.py)
 - [ding/entry/serial_entry_offline.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/entry/serial_entry_offline.py)
 - [ding/example/dqn_nstep.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/example/dqn_nstep.py)
 - [ding/framework/__init__.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/framework/__init__.py)
 - [ding/framework/context.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/framework/context.py)
 - [ding/framework/middleware/functional/ctx_helper.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/framework/middleware/functional/ctx_helper.py)
 - [ding/framework/parallel.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/framework/parallel.py)
 - [ding/framework/task.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/framework/task.py)
 - [ding/framework/tests/context_fake_data.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/framework/tests/context_fake_data.py)
 - [ding/framework/tests/test_context.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/framework/tests/test_context.py)
 - [ding/framework/tests/test_parallel.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/framework/tests/test_parallel.py)
 - [ding/framework/tests/test_task.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/framework/tests/test_task.py)
 - [ding/framework/tests/test_wrapper.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/framework/tests/test_wrapper.py)
 - [ding/model/template/vac.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/template/vac.py)
 - [ding/policy/base_policy.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/base_policy.py)
 - [ding/utils/__init__.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/utils/__init__.py)
 - [ding/utils/log_helper.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/utils/log_helper.py)
 - [ding/utils/log_writer_helper.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/utils/log_writer_helper.py)
 - [ding/utils/memory_helper.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/utils/memory_helper.py)
 - [ding/utils/pytorch_ddp_dist_helper.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/utils/pytorch_ddp_dist_helper.py)
 - [ding/utils/tests/test_k8s_launcher.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/utils/tests/test_k8s_launcher.py)
 - [ding/utils/tests/test_log_helper.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/utils/tests/test_log_helper.py)
 - [ding/utils/tests/test_log_writer_helper.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/utils/tests/test_log_writer_helper.py)
 - [ding/utils/tests/test_memory_helper.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/utils/tests/test_memory_helper.py)
 - [ding/worker/learner/base_learner.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/worker/learner/base_learner.py)
 - [ding/worker/learner/learner_hook.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/worker/learner/learner_hook.py)
 - [setup.py](https://github.com/opendilab/DI-engine/blob/c290a673/setup.py)
 
  
## Purpose and Scope

 This document provides a comprehensive overview of the core architecture of DI-engine, a generalized decision intelligence engine for PyTorch. It explains the foundational components, their interactions, and the overall system design that powers the various reinforcement learning algorithms in the framework. This page focuses on the internal architecture rather than the usage patterns - for information about how to use DI-engine to implement specific algorithms, see the respective algorithm pages or the [Getting Started](https://deepwiki.com/opendilab/DI-engine/1.2-getting-started) guide.

 DI-engine's architecture is designed to be modular, extensible, and focused on reinforcement learning workflows. It provides a python-first, asynchronous-native framework built around a task middleware model that coordinates the essential components of reinforcement learning systems: environments, policies, and models.

 
## High-Level Architecture Overview

 
```

```

 Sources:

 
 - [README.md47-63](https://github.com/opendilab/DI-engine/blob/c290a673/README.md?plain=1#L47-L63)
 - [setup.py38-52](https://github.com/opendilab/DI-engine/blob/c290a673/setup.py#L38-L52)
 - [ding/utils/__init__.py1-44](https://github.com/opendilab/DI-engine/blob/c290a673/ding/utils/__init__.py#L1-L44)
 
 
## Framework Core Components

 The foundation of DI-engine is built on several key abstractions that structure and orchestrate the workflow of reinforcement learning algorithms. These core components provide the framework within which the rest of the system operates.

 
### Task and Context

 At the heart of DI-engine's architecture is the Task and Context system that orchestrates the workflow of RL algorithms.

 
```

```

 
 - **Task**: Manages the execution flow of the middleware pipeline. It handles execution order, provides async capability, and facilitates communication between components.
 - **Context**: Acts as a data container that passes information between middleware. Different context types (OnlineRLContext, OfflineRLContext) store different types of training state.
 
 The Task system provides:

 
 - **Sequential and asynchronous execution modes**: Tasks can run middleware sequentially or in parallel
 - **Event-based communication**: Components can emit and listen for events
 - **Generator-based control flow**: Middleware can yield to pause execution at strategic points
 
 Sources:

 
 - [ding/framework/task.py69-553](https://github.com/opendilab/DI-engine/blob/c290a673/ding/framework/task.py#L69-L553)
 - [ding/framework/context.py7-104](https://github.com/opendilab/DI-engine/blob/c290a673/ding/framework/context.py#L7-L104)
 - [ding/framework/tests/test_task.py10-383](https://github.com/opendilab/DI-engine/blob/c290a673/ding/framework/tests/test_task.py#L10-L383)
 - [ding/framework/tests/context_fake_data.py1-69](https://github.com/opendilab/DI-engine/blob/c290a673/ding/framework/tests/context_fake_data.py#L1-L69)
 
 
### Middleware System

 The middleware system provides a flexible way to define and compose processing steps in the RL pipeline.

 
```

```

 
 - **Middleware**: Functions that process the context data and implement steps of the RL workflow
 - **Pipeline composition**: Middleware can be composed sequentially or in parallel
 - **Yield mechanism**: Middleware can yield control flow to implement before/after patterns
 
 Middleware follows a simple pattern - they are functions that receive a context object, process it, and optionally yield to implement pre/post processing:

 
```

```

 Sources:

 
 - [ding/framework/task.py16-54](https://github.com/opendilab/DI-engine/blob/c290a673/ding/framework/task.py#L16-L54)
 - [ding/framework/middleware/functional/ctx_helper.py1-29](https://github.com/opendilab/DI-engine/blob/c290a673/ding/framework/middleware/functional/ctx_helper.py#L1-L29)
 - [ding/example/dqn_nstep.py1-64](https://github.com/opendilab/DI-engine/blob/c290a673/ding/example/dqn_nstep.py#L1-L64)
 
 
### Parallel Execution

 DI-engine supports distributed execution through its Parallel system, enabling multi-process and multi-node training.

 
```

```

 Key features of the parallel system:

 
 - **Process-based parallelism**: Spawns multiple processes for parallel execution
 - **Message-passing communication**: Uses message queues for inter-process communication
 - **Event-based API**: Provides emit/on methods for publishing and subscribing to events
 - **Network topologies**: Supports different connection patterns (mesh, star, etc.)
 - **Auto-recovery**: Can automatically recover from crashes in worker processes
 
 Sources:

 
 - [ding/framework/parallel.py1-413](https://github.com/opendilab/DI-engine/blob/c290a673/ding/framework/parallel.py#L1-L413)
 - [ding/framework/tests/test_parallel.py1-157](https://github.com/opendilab/DI-engine/blob/c290a673/ding/framework/tests/test_parallel.py#L1-L157)
 - [ding/utils/pytorch_ddp_dist_helper.py1-251](https://github.com/opendilab/DI-engine/blob/c290a673/ding/utils/pytorch_ddp_dist_helper.py#L1-L251)
 
 
## Policy System

 The Policy system is the core component for implementing reinforcement learning algorithms. It defines how agents interact with environments, learn from data, and make decisions.

 
```

```

 The Policy system has several key design features:

 
 - **Three operational modes**:

 
 - **Learn mode**: For updating the policy from collected data
 - **Collect mode**: For interacting with environments to gather experiences
 - **Eval mode**: For evaluating policy performance
 - **Command Mode Architecture**: All specific algorithm policies inherit from a CommandModePolicy, which provides common pre/post-processing operations.
 - **Configuration System**: Policies use a recursive configuration system, where derived policies inherit and extend base configurations.
 - **Model Integration**: Policies are responsible for creating and using neural network models that implement the algorithm's decision-making and learning capabilities.
 
 Sources:

 
 - [ding/policy/base_policy.py14-630](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/base_policy.py#L14-L630)
 - [README.md194-247](https://github.com/opendilab/DI-engine/blob/c290a673/README.md?plain=1#L194-L247)
 
 
## Model System

 The Model system defines the neural network architectures that implement the various reinforcement learning algorithms. It provides a modular approach to building and combining model components.

 
```

```

 Key components of the Model system:

 
 - **Registry Pattern**: Models are registered with MODEL_REGISTRY and can be created by name.
 - **Model Templates**: Pre-defined architectures like VAC (Value Actor-Critic), DQN, etc., that implement specific algorithms.
 - **Component Composition**:

 
 - **Encoders**: Transform observations into feature representations (FCEncoder, ConvEncoder, etc.)
 - **Heads**: Output action distributions or value estimates (DiscreteHead, ReparameterizationHead, etc.)
 - **Wrappers**: Add functionality to models (TargetNetwork, HiddenState, etc.)
 - **Forward Mode Selection**: Models can have different forward methods for different purposes (e.g., `compute_actor`, `compute_critic`).
 
 Example of a model template (VAC - Value Actor-Critic):

 The VAC model shows how components are combined into a complete architecture:

 
 - Observation input → Encoder → Actor and Critic Heads → Action logits and state values
 - Supports discrete, continuous, and hybrid action spaces
 - Configurable sharing of encoder between actor and critic
 
 Sources:

 
 - [ding/model/template/vac.py1-384](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/template/vac.py#L1-L384)
 - [ding/utils/__init__.py20-24](https://github.com/opendilab/DI-engine/blob/c290a673/ding/utils/__init__.py#L20-L24)
 
 
## Environment System

 The Environment system provides a standardized interface for interacting with a variety of reinforcement learning environments. It handles the communication between the agent and the environment.

 
```

```

 Key components of the Environment system:

 
 - **BaseEnv Interface**: Defines the standard methods for environment interaction (reset, step, close, seed).
 - **DingEnvWrapper**: Adapts various environments (Gym, Gymnasium, etc.) to the BaseEnv interface.
 - **Environment Managers**: Coordinate multiple environments for parallel data collection.

 
 - **AsyncSubprocessEnvManager**: Runs environments in separate processes asynchronously.
 - **SyncSubprocessEnvManager**: Runs environments in separate processes synchronously.
 - **GymVectorEnvManager**: Uses Gym's vectorized environment implementation.
 - **Vectorized Execution**: Enables efficient interaction with multiple environments in parallel.
 
 The environment system supports:

 
 - Various action spaces (discrete, continuous, hybrid)
 - Dynamic and fixed seeding for reproducibility
 - Environment state serialization for checkpointing
 - Automatic retry mechanisms for robustness
 
 Sources:

 
 - [README.md122-174](https://github.com/opendilab/DI-engine/blob/c290a673/README.md?plain=1#L122-L174)
 
 
## Pipeline System

 The Pipeline system orchestrates the training process by connecting the various components of the reinforcement learning workflow.

 
```

```

 Key components of the Pipeline system:

 
 - **Serial Pipeline**: Orchestrates the training loop by coordinating the other components.
 - **Collector**: Gathers experiences by having the agent interact with the environment.

 
 - Manages the exploration-exploitation tradeoff
 - Collects transitions (state, action, reward, next state)
 - Handles episode boundaries and terminal states
 - **Buffer**: Stores collected experiences for training.

 
 - Supports various sampling strategies (uniform, prioritized, etc.)
 - May implement additional processing (n-step returns, etc.)
 - **Learner**: Updates the policy based on collected experiences.

 
 - Implements the optimization step of RL algorithms
 - Tracks training statistics and learning progress
 - Manages model checkpoints and logging
 - **Evaluator**: Assesses the performance of the current policy.

 
 - Runs the policy without exploration
 - Computes performance metrics (episode returns, success rate, etc.)
 - May visualize agent behavior
 
 The BaseLearner class handles the learning process with features like:

 
 - Hook system for extensibility (save checkpoints, log metrics, etc.)
 - Monitoring training metrics
 - Automatic logging to console and tensorboard
 - Distributed training support
 
 Sources:

 
 - [ding/worker/learner/base_learner.py16-634](https://github.com/opendilab/DI-engine/blob/c290a673/ding/worker/learner/base_learner.py#L16-L634)
 - [ding/worker/learner/learner_hook.py1-344](https://github.com/opendilab/DI-engine/blob/c290a673/ding/worker/learner/learner_hook.py#L1-L344)
 - [ding/utils/log_helper.py1-174](https://github.com/opendilab/DI-engine/blob/c290a673/ding/utils/log_helper.py#L1-L174)
 - [ding/utils/log_writer_helper.py1-135](https://github.com/opendilab/DI-engine/blob/c290a673/ding/utils/log_writer_helper.py#L1-L135)
 
 
## Integration and Data Flow

 Here we illustrate how all the components interact in a complete training pipeline:

 
```

```

 Key integration points:

 
 - **Configuration Flow**: Configuration parameters flow from the entry point through the pipeline to each component.
 - **Data Flow**:

 
 - Environment generates observations and rewards
 - Policy generates actions based on observations
 - Collector mediates the interaction and stores transitions
 - Buffer provides data batches to the learner
 - Learner updates the policy
 - Evaluator assesses policy performance
 - **Control Flow**: The task system manages the execution order, ensuring that steps happen in the correct sequence:

 
 - Collection happens before learning
 - Learning happens before evaluation
 - State is maintained across iterations
 - **Event System**: Components can communicate through the event system:

 
 - Learner can emit training statistics
 - Evaluator can emit performance metrics
 - Pipeline can emit control events (stop, pause, resume)
 
 Sources:

 
 - [ding/entry/serial_entry_offline.py18-113](https://github.com/opendilab/DI-engine/blob/c290a673/ding/entry/serial_entry_offline.py#L18-L113)
 - [ding/framework/__init__.py1-12](https://github.com/opendilab/DI-engine/blob/c290a673/ding/framework/__init__.py#L1-L12)
 
 
## Advanced Features

 DI-engine includes several advanced features that enhance its capabilities:

 
### Memory Profiling and Optimization

 DI-engine provides tools for monitoring and optimizing memory usage:

 
```

```

 
 - **Memory Profiler**: Tracks memory usage of model parameters, gradients, and activations
 - **Memory Tracking**: Hierarchical view of memory usage by model component
 - **Visualization**: Generates visualizations of memory usage patterns
 
 Sources:

 
 - [ding/utils/memory_helper.py1-376](https://github.com/opendilab/DI-engine/blob/c290a673/ding/utils/memory_helper.py#L1-L376)
 - [ding/utils/tests/test_memory_helper.py1-40](https://github.com/opendilab/DI-engine/blob/c290a673/ding/utils/tests/test_memory_helper.py#L1-L40)
 
 
### Deployment and Distribution

 DI-engine supports deployment on various platforms:

 
```

```

 
 - **Docker Integration**: Ready-to-use Docker images for different environments
 - **Kubernetes Support**: Orchestration for large-scale training
 - **Multi-GPU Training**: Distributed data parallel training on multiple GPUs
 
 Sources:

 
 - [ding/utils/tests/test_k8s_launcher.py1-77](https://github.com/opendilab/DI-engine/blob/c290a673/ding/utils/tests/test_k8s_launcher.py#L1-L77)
 
 
## Summary

 DI-engine's core architecture is built on a flexible framework of Task and Middleware that coordinate the key components of reinforcement learning systems:

 
 - **Policy System**: Implements RL algorithms with learn, collect, and eval modes
 - **Model System**: Provides modular neural network components for implementing policies
 - **Environment System**: Standardizes interaction with various simulation environments
 - **Pipeline System**: Orchestrates the training process connecting all components
 
 This architecture enables:

 
 - **Modularity**: Components can be developed and tested independently
 - **Flexibility**: Different algorithms can be implemented by combining components
 - **Scalability**: Distributed training across multiple processes and machines
 - **Extensibility**: New features can be added through the middleware system
 
 The middleware-based approach also makes it easy to implement common RL practices like:

 
 - Checkpointing and restoration
 - Logging and visualization
 - Custom data processing
 - Complex training schedules
 
 Sources:

 
 - [README.md47-126](https://github.com/opendilab/DI-engine/blob/c290a673/README.md?plain=1#L47-L126)
 - [CHANGELOG1-554](https://github.com/opendilab/DI-engine/blob/c290a673/CHANGELOG#L1-L554)
