<!-- source: DeepWiki mcp.deepwiki.com · repo PRIME-RL/SimpleVLA-RL · page 4 Benchmarks and Environments · fetched 2026-10-30 -->

# Benchmarks and Environments

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [verl/utils/dataset/rob_dataset.py](verl/utils/dataset/rob_dataset.py)
- [verl/workers/rollout/rob_rollout.py](verl/workers/rollout/rob_rollout.py)

</details>



This page documents the simulation benchmarks supported by SimpleVLA-RL and how they integrate with the training pipeline. SimpleVLA-RL currently supports two major robotic manipulation benchmarks: **LIBERO** and **RoboTwin** (versions 1.0 and 2.0). These benchmarks provide diverse task suites for training and evaluating Vision-Language-Action models using binary (0/1) outcome rewards.

For detailed information about specific benchmarks, see [LIBERO Benchmark](#4.1) and [RoboTwin Benchmark](#4.2). For information about how rollout workers interact with these environments, see [Rollout Workers](#4.3). For dataset construction and data loading, see [Dataset Classes](#5.1).

## Supported Benchmarks Overview

SimpleVLA-RL supports two primary benchmark families, each with distinct characteristics for robotic manipulation tasks:

### Benchmark Comparison

| Feature | LIBERO | RoboTwin 1.0 | RoboTwin 2.0 |
|---------|--------|--------------|--------------|
| **Task Suites** | libero-10, libero-90, libero-spatial, libero-object, libero-goal | 17 predefined tasks | 21 predefined tasks |
| **Seed Management** | Fixed seed (-1) per trial | Offset-based generation | Pre-collected feasible seeds |
| **Camera Views** | 2 (head, wrist) | 3 (head, left wrist, right wrist) | 3 (head, left wrist, right wrist) |
| **Action Dimensions** | 7D (xyz + quat + gripper) | 14D (dual-arm) | 7D per arm (dual-arm) |
| **Action Chunks** | 8 | Not specified | 5 |
| **Parallel Execution** | multiprocessing (Process-based) | Threading (ThreadPoolExecutor) | Threading (ThreadPoolExecutor) |
| **Max Episode Steps** | 512 | Task-dependent | 75-800 (task-dependent) |
| **Normalization Type** | bounds/bounds_q99 | bounds/bounds_q99 | bounds/bounds_q99 |

**Sources:** [verl/workers/rollout/rob_rollout.py:429-456](), [verl/utils/dataset/rob_dataset.py:65-219]()

## System Architecture

The benchmark environments integrate with the training system through a multi-layer architecture that separates data generation, environment management, and action execution:

```mermaid
graph TB
    subgraph "Dataset Layer"
        LiberoDS["LIBERO_Dataset<br/>(rob_dataset.py)"]
        TwinDS["Robotwin_Dataset<br/>(rob_dataset.py)"]
    end
    
    subgraph "Rollout Worker"
        RobRollout["RobHFRollout<br/>(rob_rollout.py)"]
        ProcessInput["process_input()<br/>Image/proprio preprocessing"]
        GenMinibatch["_generate_minibatch()<br/>Routes to env-specific impl"]
    end
    
    subgraph "Environment Management"
        LiberoProc["env_worker()<br/>Process-based<br/>multiprocessing.Process"]
        TwinWrapper["RobotwinEnvWrapper<br/>Thread-safe wrapper<br/>threading.Lock"]
    end
    
    subgraph "Simulation Environments"
        LiberoEnv["LIBERO Environments<br/>get_libero_env()"]
        Twin1Env["RoboTwin 1.0 Tasks"]
        Twin2Env["RoboTwin 2.0 Tasks<br/>get_robotwin2_task()"]
    end
    
    subgraph "Parallel Execution"
        MPQueue["Queue<br/>IPC for LIBERO"]
        ThreadPool["ThreadPoolExecutor<br/>max_workers=16"]
    end
    
    LiberoDS --> RobRollout
    TwinDS --> RobRollout
    
    RobRollout --> ProcessInput
    ProcessInput --> GenMinibatch
    
    GenMinibatch -->|"LIBERO"| LiberoProc
    GenMinibatch -->|"RoboTwin"| TwinWrapper
    
    LiberoProc --> MPQueue
    MPQueue --> LiberoEnv
    
    TwinWrapper --> ThreadPool
    ThreadPool --> Twin1Env
    ThreadPool --> Twin2Env
    
    LiberoEnv -->|"obs + reward"| LiberoProc
    Twin1Env -->|"obs + reward"| TwinWrapper
    Twin2Env -->|"obs + reward"| TwinWrapper
    
    LiberoProc -->|"trajectory data"| RobRollout
    TwinWrapper -->|"trajectory data"| RobRollout
```

**Sources:** [verl/workers/rollout/rob_rollout.py:424-502](), [verl/utils/dataset/rob_dataset.py:38-256]()

## Environment Lifecycle

Environments in SimpleVLA-RL follow different lifecycle patterns depending on the benchmark:

### LIBERO Environment Lifecycle

```mermaid
sequenceDiagram
    participant Rollout as RobHFRollout
    participant Worker as env_worker<br/>(Process)
    participant Env as LIBERO Environment
    participant Queue as input_queue/output_queue
    
    Rollout->>Worker: Start Process with task/trial params
    Worker->>Env: get_libero_env(task, config)
    Env-->>Worker: env instance + task_description
    Worker->>Env: reset() + set_init_state(initial_state)
    Env-->>Worker: initial observation
    Worker->>Queue: Put init data {obs, task_description}
    Queue-->>Rollout: Receive init data
    
    loop Until max_steps or done
        Rollout->>Rollout: process_input(obs) → batch
        Rollout->>Rollout: VLA forward pass → actions
        Rollout->>Queue: Put actions to input_queue
        Worker->>Queue: Get actions from input_queue
        
        loop For each action chunk
            Worker->>Env: step(action)
            Env-->>Worker: obs, reward, done
        end
        
        Worker->>Queue: Put step data {obs, active, complete}
        Queue-->>Rollout: Receive step data
    end
    
    Rollout->>Queue: Put None (terminate signal)
    Worker->>Env: close()
    Worker->>Queue: Put terminate confirmation
```

**Sources:** [verl/workers/rollout/rob_rollout.py:772-886](), [verl/workers/rollout/rob_rollout.py:334-420]()

### RoboTwin Environment Lifecycle

```mermaid
sequenceDiagram
    participant Rollout as RobHFRollout
    participant Wrapper as RobotwinEnvWrapper
    participant ThreadPool as ThreadPoolExecutor
    participant Env as RoboTwin Environment
    
    Rollout->>Wrapper: Create wrapper instance
    Rollout->>ThreadPool: Submit wrapper.initialize()
    ThreadPool->>Wrapper: Execute initialize()
    Wrapper->>Wrapper: Acquire _ENV_INIT_LOCK
    Wrapper->>Env: get_robotwin2_task(task_name)
    Env-->>Wrapper: env instance + args
    Wrapper->>Env: setup_demo(trial_id, seed)
    Env-->>Wrapper: episode initialized
    Wrapper->>Env: get_instruction()
    Env-->>Wrapper: instruction text
    Wrapper->>Wrapper: Release lock
    ThreadPool-->>Rollout: Initialization complete
    
    Rollout->>Wrapper: get_obs()
    Wrapper-->>Rollout: initial observation
    
    loop Until max_steps or done
        Rollout->>Rollout: process_input(obs) → batch
        Rollout->>Rollout: VLA forward pass → actions
        Rollout->>ThreadPool: Submit wrapper.step(actions)
        ThreadPool->>Wrapper: Execute step()
        Wrapper->>Wrapper: Acquire lock
        
        loop For each action chunk
            Wrapper->>Env: take_action(action)
            Env-->>Wrapper: Updates eval_success
        end
        
        Wrapper->>Env: get_obs()
        Env-->>Wrapper: new observation
        Wrapper->>Wrapper: Update active/complete status
        Wrapper->>Wrapper: Release lock
        ThreadPool-->>Rollout: Return obs, done
    end
    
    Rollout->>ThreadPool: Submit wrapper.close()
    ThreadPool->>Wrapper: Execute close()
    Wrapper->>Env: close_env(clear_cache=True)
```

**Sources:** [verl/workers/rollout/rob_rollout.py:604-770](), [verl/workers/rollout/rob_rollout.py:233-331]()

## Task Selection and Configuration

Benchmark tasks are selected and configured through the dataset classes, which generate training and validation samples:

### Task Suite Names

**LIBERO Suites:**
- `libero_10`: 10 diverse manipulation tasks
- `libero_90`: 90 tasks for comprehensive evaluation
- `libero_spatial`: Spatial reasoning tasks
- `libero_object`: Object manipulation tasks
- `libero_goal`: Goal-based tasks

**RoboTwin Tasks:**
RoboTwin 1.0 includes 17 tasks (e.g., `robotwin_block_hammer_beat`, `robotwin_dual_bottles_pick_easy`), while RoboTwin 2.0 includes 21 tasks (e.g., `robotwin2_click_bell`, `robotwin2_handover_mic`, `robotwin2_stack_blocks_two`).

**Sources:** [verl/utils/dataset/rob_dataset.py:83-133](), [README.md:52]()

### Dataset Construction Flow

```mermaid
graph LR
    subgraph "Configuration"
        TaskName["task_suite_name<br/>or task_name"]
        NumTrials["num_trials_per_task"]
        TrainVal["train_val<br/>('train' or 'valid')"]
    end
    
    subgraph "LIBERO Path"
        LiberoInit["LIBERO_Dataset.__init__()"]
        BenchmarkDict["benchmark.get_benchmark_dict()"]
        TaskSuite["task_suite.get_task()"]
        TrialLoop["Loop: task_id × trial_id"]
        LiberoData["Data: task_suite_name,<br/>task_id, trial_id,<br/>trial_seed=-1"]
    end
    
    subgraph "RoboTwin Path"
        TwinInit["Robotwin_Dataset.__init__()"]
        VersionDetect["Detect version<br/>1.0 or 2.0"]
        SeedManage["Seed Management<br/>IID vs OOD"]
        TwinData["Data: task_suite_name,<br/>trial_id, trial_seed,<br/>data_source"]
    end
    
    subgraph "Output"
        Dataloader["DataLoader +<br/>BufferedDataLoader"]
        Collate["collate_fn()<br/>Tensor stacking"]
    end
    
    TaskName --> LiberoInit
    TaskName --> TwinInit
    NumTrials --> LiberoInit
    NumTrials --> TwinInit
    TrainVal --> LiberoInit
    TrainVal --> TwinInit
    
    LiberoInit --> BenchmarkDict
    BenchmarkDict --> TaskSuite
    TaskSuite --> TrialLoop
    TrialLoop --> LiberoData
    
    TwinInit --> VersionDetect
    VersionDetect --> SeedManage
    SeedManage --> TwinData
    
    LiberoData --> Collate
    TwinData --> Collate
    Collate --> Dataloader
```

**Sources:** [verl/utils/dataset/rob_dataset.py:65-219]()

## Key Differences in Environment Interaction

### Parallel Execution Strategies

The choice of parallelization strategy reflects the characteristics of each benchmark:

**LIBERO (Process-based):**
- Uses `multiprocessing.Process` with `Queue` for inter-process communication
- Strong isolation between environment instances
- Suitable for environments that may have global state or C++ bindings
- Each worker process runs `env_worker()` function independently
- Communication via `input_queue` (for actions) and `output_queue` (for observations)

**RoboTwin (Thread-based):**
- Uses `ThreadPoolExecutor` with `threading.Lock` for synchronization
- Lightweight concurrency with shared memory
- `RobotwinEnvWrapper` ensures thread-safety with per-instance locks
- Global `_ENV_INIT_LOCK` prevents race conditions during initialization
- More efficient for environments with frequent small communications

**Sources:** [verl/workers/rollout/rob_rollout.py:64-70](), [verl/workers/rollout/rob_rollout.py:334-420](), [verl/workers/rollout/rob_rollout.py:233-331]()

### Observation Processing

Observations from both benchmarks are converted to a unified format by `_obs_to_input()`:

```mermaid
graph TB
    subgraph "LIBERO Observation"
        LibObs["env.step() returns obs dict"]
        LibState["State: eef_pos + quat→axisangle + gripper_qpos"]
        LibImg["Images: agentview_image, wrist_image"]
        LibConv["Convert to:<br/>{full_image, wrist_image, state}"]
    end
    
    subgraph "RoboTwin 1.0 Observation"
        Twin1Obs["env.get_obs() returns obs dict"]
        Twin1State["State: joint_action<br/>(scale gripper by 0.045)"]
        Twin1Img["Images: head_camera, left/right wrist"]
        Twin1Conv["Convert to:<br/>{full_image, left_wrist,<br/>right_wrist, state}"]
    end
    
    subgraph "RoboTwin 2.0 Observation"
        Twin2Obs["env.get_obs() returns obs dict"]
        Twin2State["State: joint_action.vector"]
        Twin2Img["Images: head_camera.rgb, left/right camera.rgb"]
        Twin2Conv["Convert to:<br/>{full_image, left_wrist,<br/>right_wrist, state}"]
    end
    
    subgraph "Unified Format"
        UnifiedDict["{full_image, state,<br/>optional wrist images}"]
        ProcessInput["process_input()<br/>Image crop/resize,<br/>Proprio normalization,<br/>Text tokenization"]
        BatchData["Batched tensors:<br/>input_ids, attention_mask,<br/>pixel_values, proprio"]
    end
    
    LibObs --> LibState
    LibObs --> LibImg
    LibState --> LibConv
    LibImg --> LibConv
    
    Twin1Obs --> Twin1State
    Twin1Obs --> Twin1Img
    Twin1State --> Twin1Conv
    Twin1Img --> Twin1Conv
    
    Twin2Obs --> Twin2State
    Twin2Obs --> Twin2Img
    Twin2State --> Twin2Conv
    Twin2Img --> Twin2Conv
    
    LibConv --> UnifiedDict
    Twin1Conv --> UnifiedDict
    Twin2Conv --> UnifiedDict
    
    UnifiedDict --> ProcessInput
    ProcessInput --> BatchData
```

**Sources:** [verl/workers/rollout/rob_rollout.py:1085-1126](), [verl/workers/rollout/rob_rollout.py:504-595]()

## Environment-Specific Utilities

### LIBERO Utilities

LIBERO-specific helper functions are located in `verl/utils/libero_utils.py` and include:
- `get_libero_env()`: Creates LIBERO environment instances with appropriate configuration
- `get_libero_image()`: Extracts and processes head camera images
- `get_libero_wrist_image()`: Extracts wrist camera images
- `get_libero_dummy_action()`: Generates no-op actions for environment warm-up
- `normalize_gripper_action()`: Normalizes gripper commands
- `invert_gripper_action()`: Inverts gripper action convention
- `quat2axisangle()`: Converts quaternion to axis-angle representation
- `save_rollout_video()`: Saves validation videos

**Sources:** [verl/workers/rollout/rob_rollout.py:32-41]()

### RoboTwin Utilities

RoboTwin-specific functionality includes:
- `get_robotwin2_task()`: Loads and configures RoboTwin 2.0 tasks with embodiment settings
- `normalize_proprio()`: Normalizes proprioception data using task-specific statistics
- `encode_obs()`: Post-processes observations (currently a pass-through)
- `RobotwinEnvWrapper`: Thread-safe wrapper providing `initialize()`, `get_obs()`, `get_instruction()`, `step()`, and `close()` methods

**Sources:** [verl/workers/rollout/rob_rollout.py:153-331]()

## Maximum Episode Steps Configuration

Each task has a predefined maximum number of steps, configured in `RobHFRollout.__init__()`:

```python
self.max_steps = {
    "libero_spatial": 512,
    "libero_object": 512,
    "libero_goal": 512,
    "libero_10": 512,
    "libero_90": 512,
    "robotwin2_click_bell": 200,
    "robotwin2_handover_mic": 200,
    "robotwin2_shake_bottle": 75,
    "robotwin2_put_bottles_dustbin": 800,
    # ... (21 RoboTwin 2.0 tasks total)
}
```

These limits prevent infinite loops and ensure consistent episode lengths across training runs. The actual episode may terminate earlier if the task is completed (`done=True`) or fails.

**Sources:** [verl/workers/rollout/rob_rollout.py:429-456]()

## Integration with Training Pipeline

The benchmark environments integrate into the PPO training loop through the following flow:

1. **Dataset Generation**: `LIBERO_Dataset` or `Robotwin_Dataset` creates training samples with task/trial metadata
2. **Batch Loading**: `BufferedDataLoader` fetches batches and manages excess samples from filtering
3. **Rollout Generation**: `RobHFRollout.generate_sequences()` creates environment instances, runs VLA inference, collects trajectories
4. **Reward Collection**: Binary rewards (0/1) are extracted from environment completion status
5. **Trajectory Return**: Complete episodes with observations, actions, and rewards are returned to the trainer

For details on the training loop, see [PPO Training Loop](#3.1). For data pipeline details, see [Data Pipeline](#5).

**Sources:** [verl/trainer/ppo/ray_trainer.py:68-82](), [verl/workers/rollout/rob_rollout.py:490-502]()

---

