> 来源: [https://deepwiki.com/astooke/rlpyt/2-core-architecture](https://deepwiki.com/astooke/rlpyt/2-core-architecture)
> DeepWiki astooke/rlpyt | Last indexed: 25 April 2025 (f04f23

# Core Architecture

  Relevant source files 
 - [docs/source/conf.py](https://github.com/astooke/rlpyt/blob/f04f23db/docs/source/conf.py)
 - [docs/source/index.rst](https://github.com/astooke/rlpyt/blob/f04f23db/docs/source/index.rst)
 - [docs/source/pages/base.rst](https://github.com/astooke/rlpyt/blob/f04f23db/docs/source/pages/base.rst)
 - [docs/source/pages/qpg.rst](https://github.com/astooke/rlpyt/blob/f04f23db/docs/source/pages/qpg.rst)
 - [docs/source/pages/runner.rst](https://github.com/astooke/rlpyt/blob/f04f23db/docs/source/pages/runner.rst)
 - [docs/source/pages/sampler.rst](https://github.com/astooke/rlpyt/blob/f04f23db/docs/source/pages/sampler.rst)
 - [rlpyt/agents/base.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/agents/base.py)
 - [rlpyt/algos/base.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/base.py)
 - [rlpyt/envs/base.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/envs/base.py)
 - [rlpyt/runners/base.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/runners/base.py)
 
  This document provides a technical overview of the rlpyt framework's core architecture, explaining the fundamental building blocks and how they interact to implement reinforcement learning algorithms. For specific algorithm implementations, see [Algorithms](https://deepwiki.com/astooke/rlpyt/3-algorithms), and for detailed information about samplers, see [Samplers](https://deepwiki.com/astooke/rlpyt/6-samplers).

 
## Core Components and Relationships

 The rlpyt framework is built around several key components that work together to implement reinforcement learning algorithms:

 **Core Components Diagram**

 
```

```

 Sources:

 
 - [rlpyt/runners/base.py1-16](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/runners/base.py#L1-L16)
 - [rlpyt/algos/base.py1-69](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/base.py#L1-L69)
 - [rlpyt/agents/base.py17-246](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/agents/base.py#L17-L246)
 - [rlpyt/envs/base.py11-66](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/envs/base.py#L11-L66)
 
 
### Runner

 The Runner (implemented as `BaseRunner` in [rlpyt/runners/base.py1-16](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/runners/base.py#L1-L16)) orchestrates the entire training process. It connects the sampling system with the optimization system and manages the training loop, evaluation, and checkpointing. The `train()` method serves as the entry point for running an RL experiment.

 
### Algorithm

 The Algorithm (implemented as `RlAlgorithm` in [rlpyt/algos/base.py1-69](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/base.py#L1-L69)) is responsible for updating the agent's parameters based on collected experience data. It handles the reinforcement learning logic, such as computing TD-errors and performing gradient descent on the agent's model parameters. Key methods include `initialize()` to set up optimization and `optimize_agent()` to perform parameter updates.

 
### Agent

 The Agent (implemented as `BaseAgent` in [rlpyt/agents/base.py17-246](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/agents/base.py#L17-L246)) serves as the interface between the algorithm and environment. It contains the policy model (neural network) and handles action selection during sampling and training. The agent manages model device placement, recurrent state (if applicable), and parameter communication between processes.

 
### Sampler

 The Sampler collects experience by coordinating agent-environment interactions. It manages worker processes that run environments in parallel to collect training data. Different sampler implementations support various parallelization strategies for CPU or GPU computation.

 
### Environment

 The Environment (interface defined in [rlpyt/envs/base.py11-66](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/envs/base.py#L11-L66) as `Env`) provides the interface to the reinforcement learning task, with defined observation and action spaces. It follows a standard interface similar to OpenAI Gym with `step()` and `reset()` methods.

 
## Training Process Flow

 The following diagram illustrates how components interact during the training process:

 **Training Flow Diagram**

 
```

```

 Sources:

 
 - [rlpyt/runners/base.py1-16](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/runners/base.py#L1-L16)
 - [rlpyt/agents/base.py59-170](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/agents/base.py#L59-L170)
 - [rlpyt/algos/base.py42-54](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/base.py#L42-L54)
 - [rlpyt/envs/base.py17-32](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/envs/base.py#L17-L32)
 
 The typical data flow in rlpyt follows these steps:

 
 - The Runner initializes all components (agent, algorithm, sampler) and starts the training loop
 - The Runner calls `sampler.obtain_samples(itr)` to collect experiences
 - The Sampler coordinates: 
 - Getting actions from the Agent via `agent.step(observation, prev_action, prev_reward)`
 - Executing actions in Environments via `env.step(action)`
 - Collecting the resulting observations, rewards, and done flags
 - The collected experiences are returned to the Runner
 - For off-policy algorithms, experiences may be stored in a replay buffer
 - The Algorithm processes experiences and updates the Agent's parameters via `algorithm.optimize_agent(itr, samples)`
 - This cycle repeats until training completes
 
 
## Parallelism Patterns

 rlpyt provides flexible parallelism options to efficiently utilize available hardware:

 **Parallelism Options Diagram**

 
```

```

 Sources:

 
 - [docs/source/pages/runner.rst1-60](https://github.com/astooke/rlpyt/blob/f04f23db/docs/source/pages/runner.rst#L1-L60)
 - [docs/source/pages/sampler.rst1-71](https://github.com/astooke/rlpyt/blob/f04f23db/docs/source/pages/sampler.rst#L1-L71)
 
 
### Single-Process Execution (MinibatchRl)

 A simple execution pattern with minimal overhead, suitable for debugging or small-scale experiments. The `MinibatchRl` runner implements this pattern with sequential sampling and optimization.

 
### Multi-GPU Data Parallel (SyncRl)

 Distributes neural network computation across multiple GPUs for faster training. The `SyncRl` runner implements this pattern using PyTorch's DistributedDataParallel for data-parallel training.

 
### Asynchronous Execution (AsyncRl)

 Separates sampling and optimization into different processes, allowing them to run concurrently. The `AsyncRl` runner implements this pattern for better resource utilization.

 
## Agent Architecture

 The agent is a crucial component that bridges between the algorithm and environment. It encapsulates neural networks and manages model state:

 **Agent Structure Diagram**

 
```

```

 Sources:

 
 - [rlpyt/agents/base.py17-246](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/agents/base.py#L17-L246)
 - [rlpyt/agents/base.py252-372](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/agents/base.py#L252-L372)
 
 The `BaseAgent` class in [rlpyt/agents/base.py17-246](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/agents/base.py#L17-L246) defines the interface for all agents. Key methods include:

 
 - `initialize(env_spaces, ...)`: Sets up the agent's model based on environment specifications
 - `step(observation, prev_action, prev_reward)`: Selects actions during sampling
 - `to_device(cuda_idx)`: Moves the model to a specified GPU device
 - `data_parallel()`: Wraps the model with PyTorch's DistributedDataParallel
 - `train_mode()`, `sample_mode()`, `eval_mode()`: Toggle between different operation modes
 
 For recurrent agents, additional functionality is provided by `RecurrentAgentMixin` [rlpyt/agents/base.py252-304](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/agents/base.py#L252-L304) which manages recurrent state during sampling. For alternating samplers, `AlternatingRecurrentAgentMixin` [rlpyt/agents/base.py307-372](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/agents/base.py#L307-L372) provides specialized state management.

 
## Data Structures

 rlpyt uses structured named tuples for passing data between components:

 
| Data Structure | Fields | Purpose |
|---|---|---|
| AgentInputs | observation, prev_action, prev_reward | Input to agent's step function |
| AgentStep | action, agent_info | Output from agent's step function |
| EnvStep | observation, reward, done, env_info | Output from environment's step function |
| AgentInputsRnn | observation, prev_action, prev_reward, init_rnn_state | Input for recurrent agents (training) |

 Sources:

 
 - [rlpyt/agents/base.py12-14](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/agents/base.py#L12-L14)
 - [rlpyt/agents/base.py248-249](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/agents/base.py#L248-L249)
 - [rlpyt/envs/base.py5-8](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/envs/base.py#L5-L8)
 
 These data structures ensure consistent interfaces and memory layout between components.

 
## Environment Interface

 Environments in rlpyt follow a standard interface similar to OpenAI Gym:

 
```

```

 The environment interface is defined in the `Env` class in [rlpyt/envs/base.py11-66](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/envs/base.py#L11-L66) Each environment must provide:

 
 - `step(action)`: Execute action and return next observation, reward, done flag, and info
 - `reset()`: Reset the environment and return initial observation
 - `action_space` and `observation_space`: Define the shape and type of actions and observations
 
 
## Extending the Framework

 To implement new algorithms or agents in rlpyt, you typically:

 
 - Subclass the appropriate base class (`RlAlgorithm`, `BaseAgent`, etc.)
 - Implement the required methods for that component
 - Define any custom models needed
 
 For example, to create a new agent:

 
```

```

 
## Conclusion

 The core architecture of rlpyt provides a flexible, modular framework for implementing reinforcement learning algorithms. Its components are designed to be interchangeable, allowing researchers to easily experiment with different algorithms, agents, and parallelization strategies. The clean separation of concerns between sampling, agent behavior, and optimization makes it straightforward to extend the framework with new methods.
