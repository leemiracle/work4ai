> 来源: [https://deepwiki.com/takuseno/d3rlpy/6-data-management](https://deepwiki.com/takuseno/d3rlpy/6-data-management)
> DeepWiki takuseno/d3rlpy | Last indexed: 25 June 2025 (4f0956

# Data Management

  Relevant source files 
 - [d3rlpy/__init__.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/__init__.py)
 - [d3rlpy/cli.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/cli.py)
 - [d3rlpy/dataset/buffers.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/buffers.py)
 - [d3rlpy/dataset/components.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/components.py)
 - [d3rlpy/dataset/episode_generator.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/episode_generator.py)
 - [d3rlpy/dataset/io.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/io.py)
 - [d3rlpy/dataset/mini_batch.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/mini_batch.py)
 - [d3rlpy/dataset/replay_buffer.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/replay_buffer.py)
 - [d3rlpy/dataset/transition_pickers.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/transition_pickers.py)
 - [d3rlpy/dataset/utils.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/utils.py)
 - [d3rlpy/dataset/writers.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/writers.py)
 - [d3rlpy/datasets.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/datasets.py)
 - [d3rlpy/envs/wrappers.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/envs/wrappers.py)
 - [d3rlpy/ope/torch/fqe_impl.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/ope/torch/fqe_impl.py)
 - [d3rlpy/torch_utility.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/torch_utility.py)
 - [docs/cli.rst](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/cli.rst)
 - [examples/custom_algo.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/examples/custom_algo.py)
 - [examples/deepmind_control.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/examples/deepmind_control.py)
 - [mypy.ini](https://github.com/takuseno/d3rlpy/blob/4f0956ba/mypy.ini)
 - [requirements.txt](https://github.com/takuseno/d3rlpy/blob/4f0956ba/requirements.txt)
 - [setup.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/setup.py)
 - [tests/algos/qlearning/algo_test.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tests/algos/qlearning/algo_test.py)
 - [tests/dataset/test_components.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tests/dataset/test_components.py)
 - [tests/dataset/test_mini_batch.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tests/dataset/test_mini_batch.py)
 - [tests/dataset/test_transition_pickers.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tests/dataset/test_transition_pickers.py)
 - [tests/test_datasets.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tests/test_datasets.py)
 - [tests/test_torch_utility.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tests/test_torch_utility.py)
 - [tests/testing_utils.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tests/testing_utils.py)
 
  This document covers d3rlpy's comprehensive data management system, which handles dataset acquisition, storage, sampling, and preprocessing for offline and online reinforcement learning. The system provides a unified interface for working with various data sources while supporting different algorithm requirements through configurable sampling strategies.

 For information about data preprocessing and scaling, see [Data Preprocessing](https://deepwiki.com/takuseno/d3rlpy/6.3-data-preprocessing). For details about specific dataset loading functions, see [Datasets and Loading](https://deepwiki.com/takuseno/d3rlpy/6.1-datasets-and-loading). For replay buffer implementations and data processing, see [Replay Buffers and Data Processing](https://deepwiki.com/takuseno/d3rlpy/6.2-replay-buffers-and-data-processing).

 
## System Architecture Overview

 The data management system follows a layered architecture that transforms raw data through several stages before reaching the training algorithms.

 **Data Management System Architecture**

 
```

```

 Sources: [d3rlpy/datasets.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/datasets.py) [d3rlpy/dataset/replay_buffer.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/replay_buffer.py) [d3rlpy/dataset/components.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/components.py) [d3rlpy/torch_utility.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/torch_utility.py)

 
## Core Data Structures

 The system is built around several fundamental data structures that represent different aspects of reinforcement learning data.

 **Core Data Structure Relationships**

 
```

```

 The `Episode` class [d3rlpy/dataset/components.py320-384](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/components.py#L320-L384) serves as the fundamental container for trajectory data, implementing the `EpisodeBase` protocol. Each episode contains sequences of observations, actions, rewards, and a termination flag. The `Transition` class [d3rlpy/dataset/components.py56-120](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/components.py#L56-L120) represents individual timesteps extracted from episodes, while `PartialTrajectory` [d3rlpy/dataset/components.py122-194](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/components.py#L122-L194) represents subsequences used by transformer-based algorithms.

 Sources: [d3rlpy/dataset/components.py56-384](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/components.py#L56-L384) [d3rlpy/dataset/mini_batch.py19-231](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/mini_batch.py#L19-L231) [d3rlpy/torch_utility.py203-388](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/torch_utility.py#L203-L388)

 
## Buffer Management System

 The replay buffer system provides flexible storage and sampling mechanisms for both offline and online learning scenarios.

 **Buffer Implementation Hierarchy**

 
```

```

 The `ReplayBuffer` class [d3rlpy/dataset/replay_buffer.py274-557](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/replay_buffer.py#L274-L557) serves as the main interface, wrapping either an `InfiniteBuffer` [d3rlpy/dataset/buffers.py43-72](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/buffers.py#L43-L72) for unlimited storage or a `FIFOBuffer` [d3rlpy/dataset/buffers.py74-119](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/buffers.py#L74-L119) for bounded capacity. The `MixedReplayBuffer` [d3rlpy/dataset/replay_buffer.py559-707](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/replay_buffer.py#L559-L707) combines two buffers for mixing offline and online data.

 For online learning, the `ExperienceWriter` [d3rlpy/dataset/writers.py241-405](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/writers.py#L241-L405) handles incremental data collection with configurable preprocessing through the `WriterPreprocessProtocol` interface.

 Sources: [d3rlpy/dataset/replay_buffer.py43-707](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/replay_buffer.py#L43-L707) [d3rlpy/dataset/buffers.py9-119](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/buffers.py#L9-L119) [d3rlpy/dataset/writers.py18-405](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/writers.py#L18-L405)

 
## Sampling Strategy System

 Different reinforcement learning algorithms require different data sampling strategies, which are handled through pluggable picker and slicer components.

 **Sampling Strategy Components**

 
```

```

 The `BasicTransitionPicker` [d3rlpy/dataset/transition_pickers.py43-73](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/transition_pickers.py#L43-L73) provides standard single-step sampling, while `FrameStackTransitionPicker` [d3rlpy/dataset/transition_pickers.py109-165](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/transition_pickers.py#L109-L165) handles frame stacking for visual observations. The `MultiStepTransitionPicker` [d3rlpy/dataset/transition_pickers.py168-226](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/transition_pickers.py#L168-L226) computes multi-step returns, and `SparseRewardTransitionPicker` [d3rlpy/dataset/transition_pickers.py75-107](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/transition_pickers.py#L75-L107) handles special return calculations for sparse reward environments.

 For transformer-based algorithms, trajectory slicers extract sequences from episodes. The `BasicTrajectorySlicer` provides standard sequential sampling, while `FrameStackTrajectorySlicer` handles frame stacking in the sequence dimension.

 Sources: [d3rlpy/dataset/transition_pickers.py27-226](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/transition_pickers.py#L27-L226) [d3rlpy/dataset/trajectory_slicers.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/trajectory_slicers.py)

 
## PyTorch Integration Pipeline

 The final stage of the data pipeline converts numpy-based batches into PyTorch tensors with integrated preprocessing.

 **PyTorch Data Conversion Pipeline**

 
```

```

 The `TorchMiniBatch.from_batch()` method [d3rlpy/torch_utility.py216-276](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/torch_utility.py#L216-L276) converts `TransitionMiniBatch` objects to PyTorch tensors, applying preprocessing and computing returns-to-go as needed. The `convert_to_torch_recursively()` function [d3rlpy/torch_utility.py113-122](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/torch_utility.py#L113-L122) handles the underlying tensor conversion, supporting both single arrays and nested sequences for tuple observations.

 The conversion process integrates with the preprocessing system, automatically applying observation, action, and reward scalers when provided. For transformer algorithms, the `TorchTrajectoryMiniBatch` class [d3rlpy/torch_utility.py290-388](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/torch_utility.py#L290-L388) provides additional methods like `to_transition_batch()` for converting sequence data back to transition format when needed.

 Sources: [d3rlpy/torch_utility.py95-388](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/torch_utility.py#L95-L388) [d3rlpy/dataset/mini_batch.py62-106](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/mini_batch.py#L62-L106) [d3rlpy/dataset/mini_batch.py172-231](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/mini_batch.py#L172-L231)

 
## Dataset Loading Interface

 The top-level dataset loading functions provide a unified interface for acquiring data from various sources.

 
| Function | Purpose | Data Source | Return Type |
|---|---|---|---|
| get_d4rl() | Load D4RL datasets | D4RL package | (ReplayBuffer, gym.Env) |
| get_atari() | Load Atari datasets | d4rl-atari package | (ReplayBuffer, gym.Env) |
| get_minari() | Load Minari datasets | Minari package | (ReplayBuffer, gymnasium.Env) |
| get_cartpole() | Load cartpole datasets | Built-in datasets | (ReplayBuffer, gym.Env) |
| get_pendulum() | Load pendulum datasets | Built-in datasets | (ReplayBuffer, gym.Env) |
| get_dataset() | Auto-detect dataset type | Multiple sources | (ReplayBuffer, gym.Env) |

 The `get_dataset()` function [d3rlpy/datasets.py655-740](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/datasets.py#L655-L740) provides automatic dataset type detection based on naming patterns, routing to the appropriate specialized loader. All functions return a tuple of a configured `ReplayBuffer` and the corresponding environment for evaluation.

 For custom data, the `load_v1()` function [d3rlpy/dataset/io.py84-117](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/io.py#L84-L117) handles loading legacy dataset formats, while the `dump()` and `load()` functions [d3rlpy/dataset/io.py15-81](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/io.py#L15-L81) provide serialization for the current format.

 Sources: [d3rlpy/datasets.py58-740](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/datasets.py#L58-L740) [d3rlpy/dataset/io.py15-117](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/io.py#L15-L117)
