# deepwiki torchrl §3 environments
> 来源: https://deepwiki.com/pytorch/rl/3-environments

$/$
$?

/$

DeepWiki

DeepWiki
pytorch/rl

$?

/$

Last indexed:  14 December 2025  (eaaa11)

  - Overview
  - Core Data Infrastructure
  - TensorDict System
  - TensorSpec System
  - Environments
  - EnvBase and Environment Specifications
  - Environment Transforms
  - Backend Integrations
  - Batched and Parallel Environments
  - Data Collection
  - Collector Architecture
  - Distributed Collection Strategies
  - Replay Buffers
  - ReplayBuffer Architecture
  - Advanced Replay Buffer Features
  - Modules and Models
  - TensorDictModule System
  - Actors, Critics, and Value Networks
  - Probability Distributions
  - Neural Network Architectures
  - Exploration Strategies
  - Learning Algorithms
  - Loss Module Architecture
  - On-Policy Algorithms
  - Off-Policy Algorithms
  - Value-Based Algorithms
  - Value Estimators
  - Training Infrastructure
  - Trainer System
  - Helper Utilities
  - LLM Integration
  - LLM Wrapper System
  - LLM Data Structures
  - LLM Training Objectives
  - LLM Environments and Tools
  - Multi-Agent Reinforcement Learning
  - Examples and Tutorials
  - Development and Deployment
  - Build System
  - Documentation System

Menu

## Environments

Relevant source files

  - docs/source/reference/envs.rst

  - test/_utils_internal.py

  - test/mocking_classes.py

  - test/test_collector.py

  - test/test_env.py

  - test/test_libs.py

  - test/test_specs.py

  - test/test_transforms.py

  - torchrl/collectors/collectors.py

  - torchrl/data/tensor_specs.py

  - torchrl/envs/__init__.py

  - torchrl/envs/batched_envs.py

  - torchrl/envs/common.py

  - torchrl/envs/env_creator.py

  - torchrl/envs/gym_like.py

  - torchrl/envs/libs/gym.py

  - torchrl/envs/transforms/__init__.py

  - torchrl/envs/transforms/transforms.py

  - torchrl/envs/utils.py

### Purpose and Scope

This page provides an overview of TorchRL's environment abstraction layer, which enables uniform interaction with reinforcement learning environments from different backends (Gym, DMControl, Brax, etc.). The environment system is built around three core concepts: the `EnvBase` abstract class, the `TensorSpec` specification system, and the `Transform` pipeline architecture.

Related pages:

  - For detailed information about EnvBase and the spec system, see EnvBase and Environment Specifications

  - For transform implementations and the TransformedEnv wrapper, see Environment Transforms

  - For backend-specific integrations (Gym, DMControl, etc.), see Backend Integrations

  - For parallel and batched environment execution, see Batched and Parallel Environments

### Overview

TorchRL's environment system provides a unified API for interacting with RL environments regardless of their underlying implementation. All environments inherit from `EnvBase` and communicate using `TensorDict` objects, which serve as the universal data container throughout the library. This design allows environments to handle arbitrary numbers of inputs and outputs, nested data structures, and batched execution without changing the interface.

The environment system consists of four layers:

  - Base Layer : EnvBase defines the core interface ( reset() , step() , rollout() ) and manages environment specifications

  - Transform Layer : Transform objects modify environment behavior by preprocessing observations, shaping rewards, or altering actions

  - Backend Layer : Wrapper classes ( GymEnv , DMControlEnv , etc.) adapt external environment libraries to the TorchRL interface

  - Batching Layer : ParallelEnv and SerialEnv enable vectorized execution of multiple environment instances

Sources: torchrl/envs/common.py314-475 torchrl/envs/transforms/transforms.py189-237

### EnvBase: The Foundation Class

```

```

EnvBase Class Hierarchy and Key Methods

`EnvBase` is the abstract base class that all TorchRL environments inherit from. It defines the contract that environments must implement while providing common functionality for state management, specification handling, and execution control.

Core Methods:

  - reset(tensordict=None) : Resets the environment and returns initial observations. Accepts an optional TensorDict for partial resets in batched environments.

  - step(tensordict) : Executes one step given actions in tensordict , returns next observations, rewards, and done flags.

  - rollout(policy, max_steps, ...) : Executes a complete trajectory using the provided policy, returning a batched TensorDict of transitions.

  - _set_seed(seed) : Abstract method for setting the random seed (must be implemented by subclasses).

Spec System:

Every environment maintains specifications that define the shape, dtype, and valid ranges of its inputs and outputs:

  - input_spec : Contains full_action_spec and full_state_spec

  - output_spec : Contains full_observation_spec , full_reward_spec , and full_done_spec

  - Leaf specs (e.g., action_spec , observation_spec ) provide direct access to the main action/observation tensor specs

The spec system enables automatic validation, random data generation for testing, and correct batching behavior.

Sources: torchrl/envs/common.py314-475 torchrl/envs/common.py481-543

### Environment Specifications (TensorSpec)

```

```

TensorSpec System

The `TensorSpec` class hierarchy provides typed specifications for tensor data throughout TorchRL. Each spec defines:

  - Shape : The expected tensor dimensions (including batch dimensions)

  - Dtype : The PyTorch data type

  - Device : The device where tensors should be allocated

  - Domain : Valid value ranges or constraints (e.g., bounded continuous, discrete categorical)

Common Spec Types:

| Spec Class | Use Case | Key Attributes |
| Bounded | Continuous actions/observations with min/max | low , high , shape , dtype |
| Unbounded | Continuous values without constraints | shape , dtype |
| Categorical | Discrete actions (integer indices) | n (number of categories) |
| OneHot | Discrete actions (one-hot encoded) | n (number of categories) |
| Binary | Binary values | n (number of binary variables) |
| Composite | Nested/structured data | Dictionary of child specs |

Spec Operations:

Specs support several operations that simplify environment interaction:

  - rand() : Generate random samples satisfying the spec constraints

  - zero() : Generate zero-initialized tensors of the correct shape/dtype

  - is_in(value) : Check if a value satisfies the spec constraints

  - project(value) : Project an out-of-bounds value to the valid range

  - encode(value) : Convert external data (e.g., numpy arrays) to the spec's format

Sources: torchrl/data/tensor_specs.py589-704 torchrl/envs/common.py349-378

### Environment Data Flow

```

```

TensorDict-Based Communication

All data exchange between the user, the environment, and other TorchRL components happens through `TensorDict` objects. This provides several advantages:

  - Unified Interface : The same data structure works for single environments, batched environments, and nested data

  - Flexible Schema : Environments can have arbitrary numbers of observations, rewards, or auxiliary outputs

  - Efficient Batching : TensorDict handles batching automatically without copying data

  - Spec Validation : Input and output specs ensure data consistency

Standard Key Convention:

  - Root level : Contains current observations, states, and actions (e.g., "observation" , "action" )

  - "next" subtree : Contains next-step data (e.g., ("next", "observation") , ("next", "reward") )

  - Done signals : ("next", "done") , ("next", "terminated") , ("next", "truncated")

step_mdp Utility:

The `step_mdp()` function (torchrl/envs/utils.py79-266) converts step outputs to rollout format by promoting `"next"` entries to the root level. This is used internally by `rollout()` to build trajectory tensordicts.

Sources: torchrl/envs/common.py544-732 torchrl/envs/utils.py79-266

### Transform System

```

```

Transform Architecture

Transforms modify environment behavior by intercepting and transforming data between the environment and the user. The `Transform` base class provides a flexible framework for building transformation pipelines.

Key/Output Specification:

  - in_keys : List of keys to read from the input tensordict

  - out_keys : List of keys to write to the output tensordict

  - in_keys_inv : Keys for inverse transformation (actions before step)

  - out_keys_inv : Output keys for inverse transformation

Transform Execution Points:

| Method | When Called | Use Case |
| _call(next_tensordict) | After step() and reset() | Modify observations, rewards, done flags |
| _step(tensordict, next_tensordict) | During step() only | Access both current and next state |
| _inv_call(tensordict) | Before step() | Transform actions before environment execution |
| forward(tensordict) | Offline (replay buffers, modules) | Standalone transformation |

TransformedEnv:

`TransformedEnv` (torchrl/envs/transforms/transforms.py865-1139) wraps a base environment with a transform or a `Compose` of transforms. It intercepts `reset()` and `step()` calls to apply transformations automatically:

```
env = GymEnv("Pendulum-v1")
transformed_env = TransformedEnv(
    env,
    Compose(
        ObservationNorm(in_keys=["observation"]),
        RewardSum(),
        StepCounter(max_steps=200)
    )
)
```

Compose:

`Compose` (torchrl/envs/transforms/transforms.py8686-9308) chains multiple transforms together, executing them sequentially. It handles spec transformations, parent environment tracking, and proper cleanup.

Sources: torchrl/envs/transforms/transforms.py189-856 torchrl/envs/transforms/transforms.py865-1139 torchrl/envs/transforms/transforms.py8686-9308

### Transform Categories

#### Observation Transforms

Observation transforms modify the observations returned by the environment:

| Transform | Purpose | Key Parameters |
| ObservationNorm | Normalize observations using running statistics | in_keys , standard_normal |
| ToTensorImage | Convert observations to image format (C×H×W) | in_keys , unsqueeze |
| CatFrames | Stack multiple frames along a dimension | N (number of frames), dim |
| Resize | Resize image observations | w (width), h (height) |
| GrayScale | Convert RGB images to grayscale | in_keys |
| CenterCrop | Center crop images | w , h |
| FlattenObservation | Flatten nested observations | first_dim , last_dim |

Sources: torchrl/envs/transforms/transforms.py1800-2800

#### Action Transforms

Action transforms modify actions before they are passed to the environment:

| Transform | Purpose | Key Parameters |
| ClipTransform | Clip actions to valid range | low , high , in_keys_inv |
| ActionMask | Apply action masking for discrete actions | Reads "action_mask" from tensordict |

Sources: torchrl/envs/transforms/transforms.py3500-3700

#### Reward Transforms

Reward transforms shape or aggregate rewards:

| Transform | Purpose | Key Parameters |
| RewardSum | Accumulate rewards over episode | in_keys , reset_keys |
| RewardClipping | Clip rewards to range | clamp_min , clamp_max |
| RewardScaling | Scale rewards by a factor | loc , scale |
| BinarizeReward | Convert rewards to binary (0/1) | in_keys |

Sources: torchrl/envs/transforms/transforms.py3700-4200

#### State Management Transforms

State management transforms track episode state or initialize data:

| Transform | Purpose | Key Parameters |
| StepCounter | Count steps per episode | max_steps |
| InitTracker | Track environment resets | Adds "is_init" key |
| TensorDictPrimer | Initialize keys with default values | primers (dict of specs) |
| FrameSkipTransform | Repeat actions for multiple steps | frame_skip |

Sources: torchrl/envs/transforms/transforms.py4200-5000

### Environment Backends

```

```

Backend Integration Pattern

TorchRL provides wrapper classes that adapt external environment libraries to the TorchRL interface. These wrappers handle:

  - Spec Conversion : Converting library-specific space definitions to TorchRL TensorSpec objects

  - Data Format : Converting between native formats (numpy arrays, JAX arrays) and PyTorch tensors

  - API Mapping : Mapping library-specific methods to the EnvBase interface

  - Metadata Handling : Processing info dictionaries and auxiliary outputs

GymLikeEnv Base Class:

`GymLikeEnv` (torchrl/envs/gym_like.py107-439) is a common base for Gym-like environments (Gym, Gymnasium, DMControl). It provides:

  - Automatic spec inference from environment spaces

  - Info dictionary reading via BaseInfoDictReader

  - Shared reset/step implementation

Backend Wrappers:

| Wrapper | Backend | Key Features |
| GymEnv | OpenAI Gym / Gymnasium | Auto-detects backend, handles pixels/vectors |
| DMControlEnv | DeepMind Control Suite | Task/domain specification, pixel rendering |
| BraxEnv | Brax (JAX) | JAX→PyTorch conversion, hardware acceleration |
| JumanjiEnv | Jumanji (JAX) | JAX-based environments, action masking |
| VmasEnv | VMAS | Vectorized multi-agent simulation |
| PettingZooEnv | PettingZoo | Multi-agent RL, parallel/AEC APIs |

Sources: torchrl/envs/gym_like.py107-439 torchrl/envs/libs/gym.py344-700

### Batched Environments

```

```

Vectorized Environment Execution

TorchRL provides two mechanisms for executing multiple environment instances in batch: `SerialEnv` and `ParallelEnv`. Both inherit from `BatchedEnvBase` and present a unified interface with `batch_size=[num_workers]`.

SerialEnv:

`SerialEnv` (torchrl/envs/batched_envs.py1403-1632) executes environments sequentially in a single process:

  - Use case : Debugging, environments with low step time, avoiding multiprocessing overhead

  - Execution : Iterates through environments one by one

  - Data : Returns a stacked TensorDict or LazyStackedTensorDict

  - Overhead : Minimal, no process spawning or IPC

ParallelEnv:

`ParallelEnv` (torchrl/envs/batched_envs.py646-1401) executes environments in separate worker processes:

  - Use case : CPU-bound environments, maximizing throughput

  - Execution : Each worker runs in an independent process

  - Communication : Uses multiprocessing pipes to send/receive data

  - Shared Memory : Optional shared memory for efficient data transfer

  - Start Methods : Supports "spawn", "fork", "forkserver"

Key Configuration Parameters:

| Parameter | Description | Default |
| num_workers | Number of parallel environments | Required |
| create_env_fn | Callable or list of callables to create environments | Required |
| create_env_kwargs | Dict or list of dicts with environment kwargs | None |
| share_individual_td | Create separate TensorDicts per worker | False |
| shared_memory | Use shared memory for data transfer | True |
| use_buffers | Use circular buffers for communication | True |
| mp_start_method | Multiprocessing start method | "spawn" |

EnvCreator:

`EnvCreator` (torchrl/envs/env_creator.py19-130) is a helper class for creating environments with shared state (e.g., for `ObservationNorm`). It handles passing shared memory references to worker processes.

Sources: torchrl/envs/batched_envs.py140-645 torchrl/envs/batched_envs.py646-1401 torchrl/envs/batched_envs.py1403-1632 torchrl/envs/env_creator.py19-130

### Environment Lifecycle

```

```

Environment State Management

TorchRL environments follow a defined lifecycle:

  - Creation : Instantiate with __init__() , specs are defined, is_closed=True

  - Opening : First call to reset() , step() , or rollout() opens the environment (workers started for batched envs)

  - Running : Environment executes step() calls, maintains internal state

  - Reset : Call reset() to return to initial state (partial resets supported for batched envs)

  - Closing : Call close() to release resources (automatic on garbage collection)

Automatic State Management:

TorchRL environments automatically handle state transitions:

  - Calling reset() or step() on a closed environment automatically reopens it

  - Batched environments ( ParallelEnv ) start worker processes lazily on first use

  - The @_check_start decorator ( torchrl/envs/batched_envs.py 64-74 ) handles reopening

Reset Behavior:

  - Full reset : reset() with no arguments resets all environments

  - Partial reset : reset(tensordict) with a tensordict containing "_reset" entries only resets specified environments

  - Auto-reset : Environments can be wrapped with AutoResetTransform to reset automatically when done

Sources: torchrl/envs/common.py544-618 torchrl/envs/batched_envs.py64-74

### Utility Functions

#### check_env_specs

`check_env_specs(env)` (torchrl/envs/utils.py300-500) validates that an environment's outputs match its declared specs. This is essential for:

  - Debugging environment implementations

  - Ensuring compatibility with TorchRL components

  - Verifying transform correctness

The function executes a `reset()` and several `step()` calls, checking that all outputs satisfy their corresponding specs.

#### step_mdp

`step_mdp(tensordict, next_tensordict)` (torchrl/envs/utils.py79-266) converts step outputs to MDP format by moving `"next"` entries to the root level. This is used internally by `rollout()` to build trajectory tensordicts.

#### make_composite_from_td

`make_composite_from_td(tensordict)` (torchrl/envs/utils.py500-600) creates a `Composite` spec from an example tensordict. Useful for automatically inferring specs from environment outputs.

Sources: torchrl/envs/utils.py56-600

### Summary

The TorchRL environment system provides a powerful and flexible abstraction for RL environments:

  - EnvBase : Unified interface with reset() , step() , rollout()

  - TensorSpec : Type-safe specifications for inputs and outputs

  - Transform : Modular transformation pipeline

  - Backends : Seamless integration with Gym, DMControl, Brax, and more

  - Batching : Efficient vectorization via SerialEnv and ParallelEnv

  - TensorDict : Universal data container enabling composability

This architecture enables writing environment-agnostic RL code that works across different backends, supports parallel execution, and composes naturally with the rest of TorchRL's components (collectors, replay buffers, loss modules).

For implementation details, see:

  - EnvBase and Environment Specifications for EnvBase internals and spec system

  - Environment Transforms for transform implementations

  - Backend Integrations for specific environment wrappers

  - Batched and Parallel Environments for vectorization details



#### On this page

  - Environments
  - Purpose and Scope
  - Overview
  - EnvBase: The Foundation Class
  - Environment Specifications (TensorSpec)
  - Environment Data Flow
  - Transform System
  - Transform Categories
  - Observation Transforms
  - Action Transforms
  - Reward Transforms
  - State Management Transforms
  - Environment Backends
  - Batched Environments
  - Environment Lifecycle
  - Utility Functions
  - check_env_specs
  - step_mdp
  - make_composite_from_td
  - Summary

$!/$$/$
