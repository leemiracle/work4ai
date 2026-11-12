> 来源: [https://deepwiki.com/astooke/rlpyt/5-runners](https://deepwiki.com/astooke/rlpyt/5-runners)
> DeepWiki astooke/rlpyt | Last indexed: 25 April 2025 (f04f23

# Runners

  Relevant source files 
 - [rlpyt/runners/async_rl.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/runners/async_rl.py)
 - [rlpyt/runners/minibatch_rl.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/runners/minibatch_rl.py)
 - [rlpyt/utils/logging/logger.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/utils/logging/logger.py)
 
  Runners in rlpyt are core orchestration components responsible for coordinating the entire reinforcement learning training process. They manage the interaction between samplers (which collect experience data) and algorithms (which update agent parameters), handle logging, checkpointing, and evaluation.

 For specific types of runners, see [Synchronous Runners](https://deepwiki.com/astooke/rlpyt/5.1-synchronous-runners) and [Asynchronous Runners](https://deepwiki.com/astooke/rlpyt/5.2-asynchronous-runners).

 
## Runner Overview

 Runners serve as the main entry point for rlpyt reinforcement learning experiments. They provide a standardized interface for training agents, encapsulating the common patterns of:

 
 - Initializing the sampler, agent, and algorithm
 - Coordinating the main training loop
 - Managing hardware resource allocation
 - Handling logging and checkpointing
 - Coordinating evaluation (when applicable)
 
 Runner classes in rlpyt are organized in a hierarchical structure, with specialized implementations for different parallelism patterns.

 
```

```

 Sources: [rlpyt/runners/minibatch_rl.py15-350](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/runners/minibatch_rl.py#L15-L350) [rlpyt/runners/async_rl.py21-456](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/runners/async_rl.py#L21-L456)

 
## Runner Types

 Rlpyt provides two main types of runners with different performance characteristics:

 
### 1. Synchronous Runners

 Synchronous runners (`MinibatchRl` and `MinibatchRlEval`) implement a sequential workflow where sampling and optimization strictly alternate. These runners provide simplicity and are suitable for single or multi-GPU data-parallel training.

 
### 2. Asynchronous Runners

 Asynchronous runners (`AsyncRl` and `AsyncRlEval`) decouple sampling and optimization by running them in separate processes. This allows parallel execution and can improve hardware utilization (e.g., CPUs running environment simulation concurrently with GPU optimization).

 Each type also comes in two variants:

 
 - **Standard**: Tracks agent performance using statistics from training trajectories
 - **Eval**: Performs periodic dedicated evaluation runs to measure agent performance
 
 
## Training Workflow

 The training workflow differs significantly between synchronous and asynchronous runners.

 
### Synchronous Training Workflow

 
```

```

 Sources: [rlpyt/runners/minibatch_rl.py232-284](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/runners/minibatch_rl.py#L232-L284)

 
### Asynchronous Training Workflow

 
```

```

 Sources: [rlpyt/runners/async_rl.py80-132](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/runners/async_rl.py#L80-L132) [rlpyt/runners/async_rl.py189-195](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/runners/async_rl.py#L189-L195) [rlpyt/runners/async_rl.py515-608](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/runners/async_rl.py#L515-L608)

 
## Core Runner Methods

 All runners implement several key methods that define the training process:

 
| Method | Purpose |
|---|---|
| startup() | Initializes hardware affinity, samplers, agents, algorithms, logging |
| train() | Executes the main training loop |
| store_diagnostics() | Collects and stores performance metrics during training |
| log_diagnostics() | Writes diagnostics to csv and console at logging intervals |
| save_itr_snapshot() | Saves checkpoints of agent and algorithm state |
| shutdown() | Cleans up processes and resources |

 Sources: [rlpyt/runners/minibatch_rl.py49-133](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/runners/minibatch_rl.py#L49-L133) [rlpyt/runners/async_rl.py134-178](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/runners/async_rl.py#L134-L178)

 
## Hardware Affinity Management

 Runners handle hardware resource allocation through an affinity configuration that specifies:

 
 - CPU core assignments
 - CUDA device selection
 - PyTorch thread settings
 
 This enables efficient parallel execution across multiple processes and devices.

 
```

```

 Sources: [rlpyt/runners/minibatch_rl.py55-68](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/runners/minibatch_rl.py#L55-L68) [rlpyt/runners/async_rl.py169-178](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/runners/async_rl.py#L169-L178)

 
## Logging and Monitoring

 Runners are responsible for tracking and reporting training progress. They:

 
 - Collect trajectory statistics from completed episodes
 - Store optimization metrics from algorithm updates
 - Calculate performance metrics (e.g., samples/second, updates/second)
 - Log everything to csv files and console output
 - Save model checkpoints at specified intervals
 
 
```

```

 Sources: [rlpyt/runners/minibatch_rl.py157-229](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/runners/minibatch_rl.py#L157-L229) [rlpyt/utils/logging/logger.py191-472](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/utils/logging/logger.py#L191-L472)

 
## Evaluation Mechanisms

 Rlpyt runners support two evaluation approaches:

 
 - **Online evaluation**: Tracks performance using trajectories collected during training

 
 - Used by `MinibatchRl` and `AsyncRl`
 - Lightweight but potentially biased by exploration
 - **Offline evaluation**: Performs dedicated evaluation runs at specific intervals

 
 - Used by `MinibatchRlEval` and `AsyncRlEval`
 - More accurate but requires additional computation time
 
 For offline evaluation, runners pause the training process, switch the agent to evaluation mode, collect dedicated evaluation trajectories, and log the results separately.

 Sources: [rlpyt/runners/minibatch_rl.py286-350](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/runners/minibatch_rl.py#L286-L350) [rlpyt/runners/async_rl.py434-456](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/runners/async_rl.py#L434-L456)

 
## Initialization Process

 The initialization sequence in runners is responsible for setting up all components before training begins:

 
```

```

 Sources: [rlpyt/runners/minibatch_rl.py49-99](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/runners/minibatch_rl.py#L49-L99) [rlpyt/runners/async_rl.py134-178](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/runners/async_rl.py#L134-L178)

 
## Usage Example

 To use a runner, you typically instantiate and configure the sampler, agent, and algorithm, then pass them to the appropriate runner:

 
```

```

 Sources: [rlpyt/runners/minibatch_rl.py232-284](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/runners/minibatch_rl.py#L232-L284)

 
## Conclusion

 Runners are a fundamental component of the rlpyt framework that handle the orchestration of the reinforcement learning training process. They provide a standardized interface for coordinating samplers, agents, and algorithms, while managing hardware resources, logging, and checkpointing.

 The choice between synchronous and asynchronous runners depends on hardware configuration and training requirements:

 
 - Synchronous runners offer simplicity and predictable behavior
 - Asynchronous runners can provide better hardware utilization through parallel execution
