<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/mona · page 6 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/BUILD.bazel](src/BUILD.bazel)
- [src/main.py](src/main.py)
- [src/matrix_constructor.py](src/matrix_constructor.py)

</details>



This document provides a technical overview of the internal architecture and key components of the MONA research system. It covers the modular design, component dependencies, data flow patterns, and build system organization.

For information about running experiments and using the system, see [Getting Started](#2). For details about the experimental approaches themselves, see [Experimental Approaches](#3). For information about data formats and organization, see [Data and Results](#5).

## Overall System Design

The MONA system follows a layered architecture with clear separation between the core environment, experimental methods, data persistence, and analysis components. The design supports both tabular value iteration and neural network-based approaches to test the MONA framework.

### High-Level Component Organization

```mermaid
graph TB
    subgraph "Entry Points"
        MainBinary["main (py_binary)"]
        PPONotebook["PPO Jupyter Notebook"]
    end
    
    subgraph "Experiment Orchestration"
        Runner["Runner"]
        RolloutHandler["RolloutHandler"]
    end
    
    subgraph "Core Environment"
        BlockPushEnv["BlockPushEnv"]
        BlockPushGymEnv["BlockPushGymEnv"]
        State["State"]
        Data["Data"]
    end
    
    subgraph "MONA Framework"
        Train["Train"]
        PolicyConstructor["PolicyConstructor"]
        MatrixConstructor["MatrixConstructor"]
    end
    
    subgraph "Data Persistence"
        FileHandler["FileHandler"]
        FileSystem["FileSystem"]
        ProtoBuf["rollout.proto"]
    end
    
    MainBinary --> Runner
    MainBinary --> MatrixConstructor
    PPONotebook --> BlockPushGymEnv
    
    Runner --> Train
    Runner --> MatrixConstructor
    Runner --> PolicyConstructor
    Runner --> RolloutHandler
    Runner --> FileHandler
    
    Train --> MatrixConstructor
    Train --> PolicyConstructor
    Train --> State
    
    MatrixConstructor --> BlockPushEnv
    MatrixConstructor --> State
    BlockPushGymEnv --> BlockPushEnv
    
    BlockPushEnv --> State
    BlockPushEnv --> Data
    State --> Data
    
    FileHandler --> FileSystem
    FileHandler --> ProtoBuf
    RolloutHandler --> ProtoBuf
    
    PolicyConstructor --> Data
```

**Sources:** [src/BUILD.bazel:1-201](), [src/main.py:1-365](), [src/matrix_constructor.py:1-313]()

## Core Components

The system is built around several key components that handle different aspects of the MONA research workflow.

### Environment and State Management

```mermaid
graph TD
    subgraph "State System"
        StateClass["State class"]
        DataModule["data.py module"]
        Constants["AGENT_CHR, BOX_CHR, EMPTY_CHR"]
    end
    
    subgraph "Environment Implementation"
        BlockPushEnvCore["BlockPushEnv._env"]
        BlockPushGymWrapper["BlockPushGymEnv"]
        EnvMethods["step(), get_true_reward(), get_false_reward()"]
    end
    
    subgraph "Matrix Construction"
        MatrixConstructorClass["MatrixConstructor"]
        StateEnumeration["_iterate_objects_layers()"]
        TransitionMatrix["transition_matrix property"]
        RewardMatrices["construct_good/bad_reward_matrix()"]
        InitialStates["initial_states(), get_random_initial_state()"]
    end
    
    DataModule --> StateClass
    Constants --> StateClass
    
    StateClass --> BlockPushEnvCore
    DataModule --> BlockPushEnvCore
    
    BlockPushEnvCore --> BlockPushGymWrapper
    BlockPushEnvCore --> MatrixConstructorClass
    
    StateClass --> MatrixConstructorClass
    DataModule --> MatrixConstructorClass
    
    MatrixConstructorClass --> StateEnumeration
    MatrixConstructorClass --> TransitionMatrix
    MatrixConstructorClass --> RewardMatrices
    MatrixConstructorClass --> InitialStates
    
    EnvMethods --> TransitionMatrix
    EnvMethods --> RewardMatrices
```

**Sources:** [src/BUILD.bazel:90-96](), [src/BUILD.bazel:42-50](), [src/matrix_constructor.py:37-313]()

| Component | File | Primary Responsibilities |
|-----------|------|-------------------------|
| `State` | `src/state.py` | Represents gridworld states with agent and box positions |
| `data` | `src/data.py` | Defines constants, actions, and data structures |
| `BlockPushEnv` | `src/block_push_env.py` | Core environment logic for agent movement, box pushing, rewards |
| `BlockPushGymEnv` | `src/block_push_gym_env.py` | Gymnasium-compatible wrapper for RL libraries |
| `MatrixConstructor` | `src/matrix_constructor.py` | Generates state space, transition matrices, reward matrices |

### Experiment Orchestration Pipeline

The system uses a `Runner` class to orchestrate experiments, handling parameter configuration, policy training, and result storage.

```mermaid
graph LR
    subgraph "Experiment Configuration"
        RunParams["RunParams dataclass"]
        Flags["Command-line flags"]
        RunResult["RunResult dataclass"]
    end
    
    subgraph "Runner Operations"
        RunnerInit["Runner.__init__()"]
        RunMethod["Runner.run()"]
        GetFullDir["get_full_dir_for_run()"]
        LoadRunResult["load_run_result()"]
    end
    
    subgraph "Training Pipeline"
        TrainModule["train.py"]
        ValueIteration["Value iteration algorithm"]
        PolicyGeneration["Policy construction"]
    end
    
    subgraph "Data Operations"
        FileHandlerOps["FileHandler save/load"]
        RolloutGeneration["RolloutHandler.get_rollout()"]
        DataPersistence["Protocol buffer serialization"]
    end
    
    Flags --> RunParams
    RunParams --> RunMethod
    
    RunnerInit --> MatrixConstructorClass
    RunMethod --> TrainModule
    RunMethod --> GetFullDir
    RunMethod --> FileHandlerOps
    
    TrainModule --> ValueIteration
    ValueIteration --> PolicyGeneration
    
    PolicyGeneration --> RolloutGeneration
    RolloutGeneration --> DataPersistence
    DataPersistence --> RunResult
```

**Sources:** [src/BUILD.bazel:69-78](), [src/main.py:287-330]()

## Data Flow Architecture

The system implements a comprehensive data pipeline from experiment execution through persistent storage and analysis.

### File Organization and Storage

```mermaid
graph TB
    subgraph "Parameter-Based Directory Structure"
        ParamDir["data/R=bad-V_init=good-noise_init=0.5-step_penalty=0.01-shape=4_4-boxes=2/"]
        TrialDirs["trial_1/, trial_2/, ..."]
    end
    
    subgraph "Data File Types"
        RolloutProto["rollouts.textproto"]
        ValueMatrix["value_matrix.npy"]
        PolicyArrays["Policy data arrays"]
    end
    
    subgraph "File Handler System"
        FileHandlerClass["FileHandler class"]
        FileSystemClass["FileSystem class"]
        EncodingEnum["Encoding.TEXTPROTO/BINARY"]
    end
    
    subgraph "Protocol Buffer Definitions"
        RolloutProto_["proto/rollout.proto"]
        ExperimentData["ExperimentData message"]
        RolloutData["RolloutData message"]
    end
    
    ParamDir --> TrialDirs
    TrialDirs --> RolloutProto
    TrialDirs --> ValueMatrix
    TrialDirs --> PolicyArrays
    
    FileHandlerClass --> FileSystemClass
    FileHandlerClass --> EncodingEnum
    FileHandlerClass --> RolloutProto
    FileHandlerClass --> ValueMatrix
    
    RolloutProto_ --> ExperimentData
    RolloutProto_ --> RolloutData
    ExperimentData --> RolloutProto
    RolloutData --> RolloutProto
```

**Sources:** [src/BUILD.bazel:120-127](), [src/BUILD.bazel:148-150](), [src/main.py:30-53]()

### Matrix and State Space Generation

The `MatrixConstructor` handles the computationally intensive task of generating the complete state space and transition matrices for the tabular value iteration approach.

| Method | Purpose | Return Type |
|--------|---------|-------------|
| `_iterate_objects_layers()` | Generate all possible board configurations | `Iterator[NDArray]` |
| `_initialize_states()` | Create state objects and index mapping | `None` |
| `transition_matrix` | Lazy computation of state transitions | `NDArray[np.int32]` |
| `construct_good_reward_matrix()` | Generate reward matrix for true objective | `NDArray[np.float64]` |
| `construct_bad_reward_matrix()` | Generate reward matrix for exploitable objective | `NDArray[np.float64]` |
| `initial_states()` | Find valid starting states for experiments | `set[int]` |

**Sources:** [src/matrix_constructor.py:40-51](), [src/matrix_constructor.py:238-250](), [src/matrix_constructor.py:252-256]()

## Build and Dependency System

The system uses Bazel for build management with a clear dependency hierarchy and external package management.

### Build Target Organization

```mermaid
graph TD
    subgraph "Binary Targets"
        MainBinary["py_binary: main"]
    end
    
    subgraph "Library Targets"
        CoreLibs["block_push_env, state, data"]
        OrchestrationLibs["runner, train, matrix_constructor"]
        DataLibs["file_handler, file_system, rollout_handler"]
        PolicyLibs["policy_constructor"]
        GymLib["block_push_gym_env"]
    end
    
    subgraph "Test Targets"
        UnitTests["*_test py_test targets"]
    end
    
    subgraph "External Dependencies"
        Requirements["@mona_deps//:requirements.bzl"]
        AbseilPy["@abseil-py//absl"]
        ProtoBuf["//proto:rollout_py_pb2"]
    end
    
    MainBinary --> OrchestrationLibs
    MainBinary --> DataLibs
    MainBinary --> AbseilPy
    
    OrchestrationLibs --> CoreLibs
    OrchestrationLibs --> PolicyLibs
    DataLibs --> ProtoBuf
    GymLib --> CoreLibs
    
    UnitTests --> CoreLibs
    UnitTests --> OrchestrationLibs
    UnitTests --> Requirements
```

**Sources:** [src/BUILD.bazel:1-201]()

### Dependency Management

| Package Category | Examples | Purpose |
|------------------|----------|---------|
| Numerical Computing | `numpy`, `sympy` | Matrix operations, state enumeration |
| Data Structures | `frozendict` | Immutable mappings for state caching |
| RL Interface | `gymnasium` | Standard RL environment API |
| Command Line | `@abseil-py//absl` | Flag parsing and application framework |
| Data Serialization | `//proto:rollout_py_pb2` | Structured experiment result storage |
| Testing | `pytest` | Unit test framework |

The build system enforces clean separation between components through explicit dependency declarations, ensuring that core environment logic remains independent of specific experimental approaches or data persistence mechanisms.

**Sources:** [src/BUILD.bazel:1-4](), [src/BUILD.bazel:38](), [src/BUILD.bazel:189]()

---

