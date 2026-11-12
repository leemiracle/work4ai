<!-- source: DeepWiki mcp.deepwiki.com · repo takuseno/d3rlpy · page 6 Data Management · fetched 2026-10-30 -->

# Data Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [d3rlpy/__init__.py](d3rlpy/__init__.py)
- [d3rlpy/cli.py](d3rlpy/cli.py)
- [d3rlpy/dataset/buffers.py](d3rlpy/dataset/buffers.py)
- [d3rlpy/dataset/components.py](d3rlpy/dataset/components.py)
- [d3rlpy/dataset/episode_generator.py](d3rlpy/dataset/episode_generator.py)
- [d3rlpy/dataset/io.py](d3rlpy/dataset/io.py)
- [d3rlpy/dataset/mini_batch.py](d3rlpy/dataset/mini_batch.py)
- [d3rlpy/dataset/replay_buffer.py](d3rlpy/dataset/replay_buffer.py)
- [d3rlpy/dataset/transition_pickers.py](d3rlpy/dataset/transition_pickers.py)
- [d3rlpy/dataset/utils.py](d3rlpy/dataset/utils.py)
- [d3rlpy/dataset/writers.py](d3rlpy/dataset/writers.py)
- [d3rlpy/datasets.py](d3rlpy/datasets.py)
- [d3rlpy/envs/wrappers.py](d3rlpy/envs/wrappers.py)
- [d3rlpy/ope/torch/fqe_impl.py](d3rlpy/ope/torch/fqe_impl.py)
- [d3rlpy/torch_utility.py](d3rlpy/torch_utility.py)
- [docs/cli.rst](docs/cli.rst)
- [examples/custom_algo.py](examples/custom_algo.py)
- [examples/deepmind_control.py](examples/deepmind_control.py)
- [mypy.ini](mypy.ini)
- [requirements.txt](requirements.txt)
- [setup.py](setup.py)
- [tests/algos/qlearning/algo_test.py](tests/algos/qlearning/algo_test.py)
- [tests/dataset/test_components.py](tests/dataset/test_components.py)
- [tests/dataset/test_mini_batch.py](tests/dataset/test_mini_batch.py)
- [tests/dataset/test_transition_pickers.py](tests/dataset/test_transition_pickers.py)
- [tests/test_datasets.py](tests/test_datasets.py)
- [tests/test_torch_utility.py](tests/test_torch_utility.py)
- [tests/testing_utils.py](tests/testing_utils.py)

</details>



This document covers d3rlpy's comprehensive data management system, which handles dataset acquisition, storage, sampling, and preprocessing for offline and online reinforcement learning. The system provides a unified interface for working with various data sources while supporting different algorithm requirements through configurable sampling strategies.

For information about data preprocessing and scaling, see [Data Preprocessing](#6.3). For details about specific dataset loading functions, see [Datasets and Loading](#6.1). For replay buffer implementations and data processing, see [Replay Buffers and Data Processing](#6.2).

## System Architecture Overview

The data management system follows a layered architecture that transforms raw data through several stages before reaching the training algorithms.

**Data Management System Architecture**
```mermaid
graph TB
    subgraph "Data Sources Layer"
        D4RL["D4RL Datasets"]
        ATARI["Atari Datasets"] 
        MINARI["Minari Datasets"]
        CUSTOM["Custom Data Files"]
        ENV["Online Environment"]
    end
    
    subgraph "Dataset Loading Layer"
        GET_D4RL["get_d4rl()"]
        GET_ATARI["get_atari()"]
        GET_MINARI["get_minari()"]
        GET_DATASET["get_dataset()"]
        LOAD_V1["load_v1()"]
    end
    
    subgraph "Episode Generation Layer"
        EPISODE_GEN["EpisodeGenerator"]
        EPISODES["Episode objects"]
    end
    
    subgraph "Buffer Management Layer"
        REPLAY_BUFFER["ReplayBuffer"]
        INFINITE_BUF["InfiniteBuffer"]
        FIFO_BUF["FIFOBuffer"]
        MIXED_BUF["MixedReplayBuffer"]
    end
    
    subgraph "Sampling Strategy Layer"
        BASIC_PICKER["BasicTransitionPicker"]
        FRAME_PICKER["FrameStackTransitionPicker"]
        MULTI_PICKER["MultiStepTransitionPicker"]
        BASIC_SLICER["BasicTrajectorySlicer"]
        FRAME_SLICER["FrameStackTrajectorySlicer"]
    end
    
    subgraph "Batch Processing Layer"
        TRANS_BATCH["TransitionMiniBatch"]
        TRAJ_BATCH["TrajectoryMiniBatch"]
        TORCH_BATCH["TorchMiniBatch"]
        TORCH_TRAJ["TorchTrajectoryMiniBatch"]
    end
    
    subgraph "Algorithm Integration"
        QL_ALGOS["Q-Learning Algorithms"]
        TRANS_ALGOS["Transformer Algorithms"]
    end
    
    %% Data flow connections
    D4RL --> GET_D4RL
    ATARI --> GET_ATARI
    MINARI --> GET_MINARI
    CUSTOM --> GET_DATASET
    CUSTOM --> LOAD_V1
    ENV --> REPLAY_BUFFER
    
    GET_D4RL --> EPISODE_GEN
    GET_ATARI --> EPISODE_GEN
    GET_MINARI --> EPISODE_GEN
    GET_DATASET --> EPISODE_GEN
    LOAD_V1 --> EPISODES
    
    EPISODE_GEN --> EPISODES
    EPISODES --> REPLAY_BUFFER
    
    REPLAY_BUFFER --> INFINITE_BUF
    REPLAY_BUFFER --> FIFO_BUF
    REPLAY_BUFFER --> MIXED_BUF
    
    INFINITE_BUF --> BASIC_PICKER
    FIFO_BUF --> BASIC_PICKER
    MIXED_BUF --> BASIC_PICKER
    
    BASIC_PICKER --> TRANS_BATCH
    FRAME_PICKER --> TRANS_BATCH
    MULTI_PICKER --> TRANS_BATCH
    BASIC_SLICER --> TRAJ_BATCH
    FRAME_SLICER --> TRAJ_BATCH
    
    TRANS_BATCH --> TORCH_BATCH
    TRAJ_BATCH --> TORCH_TRAJ
    
    TORCH_BATCH --> QL_ALGOS
    TORCH_TRAJ --> TRANS_ALGOS
```

Sources: [d3rlpy/datasets.py](), [d3rlpy/dataset/replay_buffer.py](), [d3rlpy/dataset/components.py](), [d3rlpy/torch_utility.py]()

## Core Data Structures

The system is built around several fundamental data structures that represent different aspects of reinforcement learning data.

**Core Data Structure Relationships**
```mermaid
graph TB
    subgraph "Raw Data Components"
        OBS["observations: ObservationSequence"]
        ACTIONS["actions: NDArray"]
        REWARDS["rewards: Float32NDArray"]
        TERMINALS["terminals: Float32NDArray"]
    end
    
    subgraph "Episode Level"
        EPISODE["Episode"]
        EPISODE_BASE["EpisodeBase Protocol"]
        SIGNATURE["Signature"]
        DATASET_INFO["DatasetInfo"]
    end
    
    subgraph "Transition Level" 
        TRANSITION["Transition"]
        PARTIAL_TRAJ["PartialTrajectory"]
    end
    
    subgraph "Batch Level"
        TRANS_MINI["TransitionMiniBatch"]
        TRAJ_MINI["TrajectoryMiniBatch"]
    end
    
    subgraph "PyTorch Integration"
        TORCH_MINI["TorchMiniBatch"]
        TORCH_TRAJ_MINI["TorchTrajectoryMiniBatch"]
    end
    
    %% Composition relationships
    OBS --> EPISODE
    ACTIONS --> EPISODE
    REWARDS --> EPISODE
    TERMINALS --> EPISODE
    
    EPISODE --> EPISODE_BASE
    SIGNATURE --> EPISODE
    DATASET_INFO --> EPISODE
    
    EPISODE --> TRANSITION
    EPISODE --> PARTIAL_TRAJ
    
    TRANSITION --> TRANS_MINI
    PARTIAL_TRAJ --> TRAJ_MINI
    
    TRANS_MINI --> TORCH_MINI
    TRAJ_MINI --> TORCH_TRAJ_MINI
```

The `Episode` class [d3rlpy/dataset/components.py:320-384]() serves as the fundamental container for trajectory data, implementing the `EpisodeBase` protocol. Each episode contains sequences of observations, actions, rewards, and a termination flag. The `Transition` class [d3rlpy/dataset/components.py:56-120]() represents individual timesteps extracted from episodes, while `PartialTrajectory` [d3rlpy/dataset/components.py:122-194]() represents subsequences used by transformer-based algorithms.

Sources: [d3rlpy/dataset/components.py:56-384](), [d3rlpy/dataset/mini_batch.py:19-231](), [d3rlpy/torch_utility.py:203-388]()

## Buffer Management System

The replay buffer system provides flexible storage and sampling mechanisms for both offline and online learning scenarios.

**Buffer Implementation Hierarchy**
```mermaid
graph TB
    subgraph "Buffer Protocols"
        BUFFER_PROTO["BufferProtocol"]
        REPLAY_BASE["ReplayBufferBase"]
    end
    
    subgraph "Buffer Implementations"
        INFINITE["InfiniteBuffer"]
        FIFO["FIFOBuffer"] 
        REPLAY_BUF["ReplayBuffer"]
        MIXED_BUF["MixedReplayBuffer"]
    end
    
    subgraph "Experience Writing"
        EXP_WRITER["ExperienceWriter"]
        WRITER_PREPROC["WriterPreprocessProtocol"]
        BASIC_PREPROC["BasicWriterPreprocess"]
        LAST_FRAME_PREPROC["LastFrameWriterPreprocess"]
    end
    
    subgraph "Sampling Components"
        TRANS_PICKER_PROTO["TransitionPickerProtocol"]
        TRAJ_SLICER_PROTO["TrajectorySlicerProtocol"]
    end
    
    %% Inheritance relationships
    BUFFER_PROTO --> INFINITE
    BUFFER_PROTO --> FIFO
    REPLAY_BASE --> REPLAY_BUF
    REPLAY_BASE --> MIXED_BUF
    
    %% Composition relationships
    INFINITE --> REPLAY_BUF
    FIFO --> REPLAY_BUF
    EXP_WRITER --> REPLAY_BUF
    TRANS_PICKER_PROTO --> REPLAY_BUF
    TRAJ_SLICER_PROTO --> REPLAY_BUF
    
    WRITER_PREPROC --> BASIC_PREPROC
    WRITER_PREPROC --> LAST_FRAME_PREPROC
    BASIC_PREPROC --> EXP_WRITER
    LAST_FRAME_PREPROC --> EXP_WRITER
```

The `ReplayBuffer` class [d3rlpy/dataset/replay_buffer.py:274-557]() serves as the main interface, wrapping either an `InfiniteBuffer` [d3rlpy/dataset/buffers.py:43-72]() for unlimited storage or a `FIFOBuffer` [d3rlpy/dataset/buffers.py:74-119]() for bounded capacity. The `MixedReplayBuffer` [d3rlpy/dataset/replay_buffer.py:559-707]() combines two buffers for mixing offline and online data.

For online learning, the `ExperienceWriter` [d3rlpy/dataset/writers.py:241-405]() handles incremental data collection with configurable preprocessing through the `WriterPreprocessProtocol` interface.

Sources: [d3rlpy/dataset/replay_buffer.py:43-707](), [d3rlpy/dataset/buffers.py:9-119](), [d3rlpy/dataset/writers.py:18-405]()

## Sampling Strategy System

Different reinforcement learning algorithms require different data sampling strategies, which are handled through pluggable picker and slicer components.

**Sampling Strategy Components**
```mermaid
graph TB
    subgraph "Transition Picking Strategies"
        BASIC_TRANS["BasicTransitionPicker"]
        FRAME_TRANS["FrameStackTransitionPicker"]
        MULTI_TRANS["MultiStepTransitionPicker"]
        SPARSE_TRANS["SparseRewardTransitionPicker"]
    end
    
    subgraph "Trajectory Slicing Strategies"
        BASIC_TRAJ["BasicTrajectorySlicer"]
        FRAME_TRAJ["FrameStackTrajectorySlicer"]
    end
    
    subgraph "Algorithm Types"
        Q_LEARNING["Q-Learning Algorithms"]
        TRANSFORMER["Transformer Algorithms"]
    end
    
    subgraph "Use Cases"
        STANDARD["Standard RL"]
        ATARI["Atari Games"]
        MULTI_STEP["Multi-step TD"]
        ANTMAZE["AntMaze Sparse Rewards"]
        SEQ_MODEL["Sequence Modeling"]
    end
    
    %% Strategy to algorithm mapping
    BASIC_TRANS --> Q_LEARNING
    FRAME_TRANS --> Q_LEARNING
    MULTI_TRANS --> Q_LEARNING
    SPARSE_TRANS --> Q_LEARNING
    
    BASIC_TRAJ --> TRANSFORMER
    FRAME_TRAJ --> TRANSFORMER
    
    %% Use case mapping
    STANDARD --> BASIC_TRANS
    STANDARD --> BASIC_TRAJ
    ATARI --> FRAME_TRANS
    ATARI --> FRAME_TRAJ
    MULTI_STEP --> MULTI_TRANS
    ANTMAZE --> SPARSE_TRANS
    SEQ_MODEL --> BASIC_TRAJ
```

The `BasicTransitionPicker` [d3rlpy/dataset/transition_pickers.py:43-73]() provides standard single-step sampling, while `FrameStackTransitionPicker` [d3rlpy/dataset/transition_pickers.py:109-165]() handles frame stacking for visual observations. The `MultiStepTransitionPicker` [d3rlpy/dataset/transition_pickers.py:168-226]() computes multi-step returns, and `SparseRewardTransitionPicker` [d3rlpy/dataset/transition_pickers.py:75-107]() handles special return calculations for sparse reward environments.

For transformer-based algorithms, trajectory slicers extract sequences from episodes. The `BasicTrajectorySlicer` provides standard sequential sampling, while `FrameStackTrajectorySlicer` handles frame stacking in the sequence dimension.

Sources: [d3rlpy/dataset/transition_pickers.py:27-226](), [d3rlpy/dataset/trajectory_slicers.py]()

## PyTorch Integration Pipeline

The final stage of the data pipeline converts numpy-based batches into PyTorch tensors with integrated preprocessing.

**PyTorch Data Conversion Pipeline**
```mermaid
graph LR
    subgraph "NumPy Domain"
        TRANS_BATCH["TransitionMiniBatch"]
        TRAJ_BATCH["TrajectoryMiniBatch"]
    end
    
    subgraph "Conversion Process"
        FROM_BATCH["TorchMiniBatch.from_batch()"]
        FROM_TRAJ["TorchTrajectoryMiniBatch.from_batch()"]
        CONVERT_TORCH["convert_to_torch_recursively()"]
        APPLY_SCALERS["Apply Scalers"]
    end
    
    subgraph "Preprocessing Components"
        OBS_SCALER["ObservationScaler"]
        ACT_SCALER["ActionScaler"] 
        REW_SCALER["RewardScaler"]
        COMPUTE_RTG["compute_returns_to_go"]
    end
    
    subgraph "PyTorch Domain"
        TORCH_BATCH["TorchMiniBatch"]
        TORCH_TRAJ["TorchTrajectoryMiniBatch"]
        TORCH_OBS["TorchObservation"]
        TORCH_TENSORS["torch.Tensor"]
    end
    
    %% Conversion flow
    TRANS_BATCH --> FROM_BATCH
    TRAJ_BATCH --> FROM_TRAJ
    
    FROM_BATCH --> CONVERT_TORCH
    FROM_TRAJ --> CONVERT_TORCH
    
    CONVERT_TORCH --> APPLY_SCALERS
    APPLY_SCALERS --> TORCH_BATCH
    APPLY_SCALERS --> TORCH_TRAJ
    
    %% Preprocessing integration
    OBS_SCALER --> APPLY_SCALERS
    ACT_SCALER --> APPLY_SCALERS
    REW_SCALER --> APPLY_SCALERS
    COMPUTE_RTG --> APPLY_SCALERS
    
    %% Output components
    TORCH_BATCH --> TORCH_OBS
    TORCH_BATCH --> TORCH_TENSORS
    TORCH_TRAJ --> TORCH_OBS
    TORCH_TRAJ --> TORCH_TENSORS
```

The `TorchMiniBatch.from_batch()` method [d3rlpy/torch_utility.py:216-276]() converts `TransitionMiniBatch` objects to PyTorch tensors, applying preprocessing and computing returns-to-go as needed. The `convert_to_torch_recursively()` function [d3rlpy/torch_utility.py:113-122]() handles the underlying tensor conversion, supporting both single arrays and nested sequences for tuple observations.

The conversion process integrates with the preprocessing system, automatically applying observation, action, and reward scalers when provided. For transformer algorithms, the `TorchTrajectoryMiniBatch` class [d3rlpy/torch_utility.py:290-388]() provides additional methods like `to_transition_batch()` for converting sequence data back to transition format when needed.

Sources: [d3rlpy/torch_utility.py:95-388](), [d3rlpy/dataset/mini_batch.py:62-106](), [d3rlpy/dataset/mini_batch.py:172-231]()

## Dataset Loading Interface

The top-level dataset loading functions provide a unified interface for acquiring data from various sources.

| Function | Purpose | Data Source | Return Type |
|----------|---------|-------------|-------------|
| `get_d4rl()` | Load D4RL datasets | D4RL package | `(ReplayBuffer, gym.Env)` |
| `get_atari()` | Load Atari datasets | d4rl-atari package | `(ReplayBuffer, gym.Env)` |
| `get_minari()` | Load Minari datasets | Minari package | `(ReplayBuffer, gymnasium.Env)` |
| `get_cartpole()` | Load cartpole datasets | Built-in datasets | `(ReplayBuffer, gym.Env)` |
| `get_pendulum()` | Load pendulum datasets | Built-in datasets | `(ReplayBuffer, gym.Env)` |
| `get_dataset()` | Auto-detect dataset type | Multiple sources | `(ReplayBuffer, gym.Env)` |

The `get_dataset()` function [d3rlpy/datasets.py:655-740]() provides automatic dataset type detection based on naming patterns, routing to the appropriate specialized loader. All functions return a tuple of a configured `ReplayBuffer` and the corresponding environment for evaluation.

For custom data, the `load_v1()` function [d3rlpy/dataset/io.py:84-117]() handles loading legacy dataset formats, while the `dump()` and `load()` functions [d3rlpy/dataset/io.py:15-81]() provide serialization for the current format.

Sources: [d3rlpy/datasets.py:58-740](), [d3rlpy/dataset/io.py:15-117]()

---

