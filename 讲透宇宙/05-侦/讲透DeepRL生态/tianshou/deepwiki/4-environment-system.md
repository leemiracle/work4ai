> 来源: [https://deepwiki.com/thu-ml/tianshou/4-environment-system](https://deepwiki.com/thu-ml/tianshou/4-environment-system)
> DeepWiki thu-ml/tianshou | Last indexed: 19 April 2025 (90846f

# Environment System

  Relevant source files 
 - [test/base/test_env.py](https://github.com/thu-ml/tianshou/blob/90846f6b/test/base/test_env.py)
 - [tianshou/env/venv_wrappers.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/venv_wrappers.py)
 - [tianshou/env/venvs.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/venvs.py)
 - [tianshou/env/worker/base.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/worker/base.py)
 - [tianshou/env/worker/dummy.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/worker/dummy.py)
 - [tianshou/env/worker/ray.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/worker/ray.py)
 - [tianshou/env/worker/subproc.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/worker/subproc.py)
 
  The Environment System in Tianshou provides a comprehensive framework for handling reinforcement learning environments, with a focus on vectorized environments that enable parallel execution. This system serves as the interface between reinforcement learning agents and the environments they interact with, efficiently collecting experiences through various parallelization strategies.

 This document covers the architecture and components of the Environment System. For information about collecting experiences from environments, see [Collector](https://deepwiki.com/thu-ml/tianshou/2.3-collector). For details on policy interfaces that interact with environments, see [Policy Framework](https://deepwiki.com/thu-ml/tianshou/3-policy-framework).

 
## Core Architecture

 The Environment System is built around the concept of vectorized environments, which allow multiple environment instances to be executed simultaneously. This design significantly speeds up the data collection process for training reinforcement learning agents.

 
```

```

 Sources: [tianshou/env/venvs.py25-363](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/venvs.py#L25-L363) [tianshou/env/worker/base.py11-87](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/worker/base.py#L11-L87) [tianshou/env/venv_wrappers.py11-67](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/venv_wrappers.py#L11-L67)

 
### BaseVectorEnv

 At the core of the Environment System is the `BaseVectorEnv` class, which provides a unified interface for working with multiple environments simultaneously. It manages a collection of `EnvWorker` instances, each responsible for a single environment.

 Key features of `BaseVectorEnv` include:

 
 - Support for both synchronous and asynchronous environment execution
 - Unified reset and step operations across multiple environments
 - Environment attribute access and modification
 - Seeding and rendering capabilities
 
 The design allows for different implementations of vectorized environments with varying parallelization strategies, all adhering to the same interface.

 Sources: [tianshou/env/venvs.py25-363](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/venvs.py#L25-L363)

 
### Environment Workers

 Environment workers serve as intermediaries between the main process and individual environments. Each worker is responsible for executing commands (like step and reset) on its environment and returning the results.

 
```

```

 Different worker implementations enable different forms of parallelism:

 
 - `DummyEnvWorker` runs environments sequentially in the main process
 - `SubprocEnvWorker` runs environments in separate subprocesses
 - `RayEnvWorker` runs environments in distributed Ray workers
 
 Sources: [tianshou/env/worker/base.py11-87](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/worker/base.py#L11-L87) [tianshou/env/worker/dummy.py10-56](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/worker/dummy.py#L10-L56) [tianshou/env/worker/subproc.py141-275](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/worker/subproc.py#L141-L275) [tianshou/env/worker/ray.py26-80](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/worker/ray.py#L26-L80)

 
## Vectorized Environment Implementations

 Tianshou provides four implementations of vectorized environments, each with different parallelization strategies and performance characteristics.

 
### DummyVectorEnv

 `DummyVectorEnv` is the simplest implementation that runs environments sequentially in the main process. It uses `DummyEnvWorker` instances to manage the environments.

 
```

```

 This implementation is useful for debugging and simple use cases where parallelization is not needed.

 Sources: [tianshou/env/venvs.py365-386](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/venvs.py#L365-L386) [tianshou/env/worker/dummy.py10-56](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/worker/dummy.py#L10-L56)

 
### SubprocVectorEnv

 `SubprocVectorEnv` runs environments in separate subprocesses using Python's multiprocessing module. It uses `SubprocEnvWorker` instances to manage the environments.

 
```

```

 This implementation is more efficient than `DummyVectorEnv` when environments have computational overhead, as it can utilize multiple CPU cores.

 Sources: [tianshou/env/venvs.py389-425](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/venvs.py#L389-L425) [tianshou/env/worker/subproc.py141-275](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/worker/subproc.py#L141-L275)

 
### ShmemVectorEnv

 `ShmemVectorEnv` is an optimized version of `SubprocVectorEnv` that uses shared memory to efficiently transfer observations between processes. It's particularly beneficial when dealing with large observations like images.

 
```

```

 Under the hood, `ShmemVectorEnv` uses `SubprocEnvWorker` with the `share_memory=True` option.

 Sources: [tianshou/env/venvs.py427-447](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/venvs.py#L427-L447) [tianshou/env/worker/subproc.py141-275](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/worker/subproc.py#L141-L275)

 
### RayVectorEnv

 `RayVectorEnv` leverages the Ray framework for distributed execution across multiple machines. It uses `RayEnvWorker` instances to manage environments running in Ray workers.

 
```

```

 This implementation is suitable for large-scale training that requires distributing workloads across a cluster.

 Sources: [tianshou/env/venvs.py449-474](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/venvs.py#L449-L474) [tianshou/env/worker/ray.py26-80](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/worker/ray.py#L26-L80)

 
## Asynchronous vs. Synchronous Execution

 Tianshou's environment system supports both synchronous and asynchronous execution modes:

 
```

```

 Synchronous execution is simpler but can be inefficient when environments have variable execution times. Asynchronous execution allows processing to continue with environments that have finished their computation, without waiting for all environments to complete.

 Asynchronous execution is enabled by setting `wait_num` to less than the total number of environments or by specifying a `timeout`.

 Sources: [tianshou/env/venvs.py76-110](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/venvs.py#L76-L110) [tianshou/env/venvs.py237-322](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/venvs.py#L237-L322)

 
## Shared Memory for Optimization

 When using `ShmemVectorEnv` or `SubprocVectorEnv` with `share_memory=True`, the system uses shared memory to efficiently transfer observations between processes. This is particularly important for environments with large observation spaces, such as those with image observations.

 
```

```

 The `ShArray` class in the `subproc.py` file handles the shared memory arrays that store observations, which are passed between processes without copying the data.

 Sources: [tianshou/env/worker/subproc.py33-66](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/worker/subproc.py#L33-L66) [tianshou/env/worker/subproc.py147-162](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/worker/subproc.py#L147-L162)

 
## Environment Wrappers

 The Environment System includes wrappers that can modify the behavior of vectorized environments. The primary wrapper provided is `VectorEnvNormObs`, which normalizes observations.

 
### VectorEnvNormObs

 `VectorEnvNormObs` normalizes observations by maintaining running statistics (mean and standard deviation) of the observations and using them to normalize future observations.

 
```

```

 This wrapper is particularly useful for environments with observations of different scales, as normalization can improve learning stability.

 Sources: [tianshou/env/venv_wrappers.py69-121](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/venv_wrappers.py#L69-L121)

 
## Usage Patterns

 
### Basic Usage

 
```

```

 
### Handling Environment Attributes

 
```

```

 
### Handling Reset and Step

 
```

```

 Sources: [tianshou/env/venvs.py195-236](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/venvs.py#L195-L236) [tianshou/env/venvs.py237-322](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/venvs.py#L237-L322)

 
## Integration with Data Collection

 The Environment System is designed to work seamlessly with Tianshou's data collection system, particularly the `Collector` class.

 
```

```

 The `Collector` uses a vectorized environment to collect experiences by interacting with multiple environments simultaneously, which significantly speeds up the data collection process.

 Sources: [tianshou/env/venvs.py237-322](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/venvs.py#L237-L322)

 
## Performance Considerations

 When choosing a vectorized environment implementation, consider:

 
| Implementation | Use Case | Advantages | Limitations |
|---|---|---|---|
| DummyVectorEnv | Debugging, simple use cases | Simple, no multiprocessing overhead | Sequential execution |
| SubprocVectorEnv | General use | Parallel execution, works with most environments | IPC overhead |
| ShmemVectorEnv | Environments with large observations | Efficient observation transfer via shared memory | Only optimizes observation transfer |
| RayVectorEnv | Distributed training | Scales to multiple machines | Requires Ray setup |

 Asynchronous execution can provide additional performance benefits when environments have variable execution times, as it allows processing to continue with environments that have completed their computation.

 Sources: [tianshou/env/venvs.py365-474](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/env/venvs.py#L365-L474)

 
## Summary

 The Environment System in Tianshou provides a flexible and efficient framework for working with reinforcement learning environments. Its vectorized design enables parallel execution of multiple environments, which is crucial for efficiently training reinforcement learning agents. Various implementations cater to different use cases, from simple debugging to distributed training across multiple machines.
