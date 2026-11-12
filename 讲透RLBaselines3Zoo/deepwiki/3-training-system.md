<!-- source: DeepWiki mcp.deepwiki.com · repo DLR-RM/rl-baselines3-zoo · page 3 Training System · fetched 2026-10-14 -->

# Training System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [rl_zoo3/exp_manager.py](rl_zoo3/exp_manager.py)
- [rl_zoo3/train.py](rl_zoo3/train.py)
- [train.py](train.py)

</details>



The Training System in RL-Baselines3-Zoo is responsible for configuring and executing reinforcement learning experiments. It handles environment creation, algorithm initialization, hyperparameter management, training, evaluation, and model saving. This page explains the system architecture and workflow for training reinforcement learning agents.

For information about command-line options, see [Command Line Interface](#3.1). For details on experiment management, see [Experiment Management](#3.2). For callback system information, see [Callbacks System](#3.3).

## System Architecture

The training system is built around the ExperimentManager class, which orchestrates the entire training process. The following diagram shows the high-level architecture:

```mermaid
graph TD
    subgraph "Training System Components"
        TrainPy["train.py\nMain entry point"] --> ExpManager["ExperimentManager\nManages training process"]
        
        ExpManager --> Setup["setup_experiment()\nPrepares training environment"]
        ExpManager --> Learn["learn(model)\nExecutes training loop"]
        ExpManager --> Save["save_trained_model(model)\nSaves results"]
        
        Setup --> ReadParams["read_hyperparameters()\nLoads configuration"]
        Setup --> CreateEnv["create_envs()\nBuilds environments"]
        Setup --> CreateCallbacks["create_callbacks()\nSets up callbacks"]
        
        ReadParams --> HyperparamFiles["YAML/Python config files"]
        
        ExpManager --> HyperOpt["hyperparameters_optimization()\nOptuna integration"]
    end
    
    subgraph "External Components"
        SB3["Stable-Baselines3\nRL Algorithms"] 
        Gym["Gymnasium\nEnvironments"]
        Optuna["Optuna\nHyperparameter optimization"]
    end
    
    Setup --> SB3
    CreateEnv --> Gym
    HyperOpt --> Optuna
```

Sources: [rl_zoo3/exp_manager.py:56-193](), [rl_zoo3/train.py:20-266]()

## Training Workflow

The training workflow consists of several sequential steps, from parsing command-line arguments to saving the trained model:

```mermaid
flowchart TD
    Start([Start Training]) --> ParseArgs["Parse Command-Line Arguments\nAlgorithm, environment, hyperparameters"]
    ParseArgs --> InitManager["Initialize ExperimentManager\nConfigure experiment settings"]
    InitManager --> SetupExp["Setup Experiment\nRead hyperparams, create environment"]
    
    SetupExp --> CheckOpt{"--optimize flag\nspecified?"}
    
    CheckOpt -- Yes --> RunOptuna["Run Hyperparameter Optimization\nFind optimal parameters"]
    RunOptuna --> End([End Training])
    
    CheckOpt -- No --> CreateModel["Initialize RL Model\nCreate algorithm instance"]
    CreateModel --> SetupCallbacks["Setup Callbacks\nEvaluation, checkpoints, progress"]
    SetupCallbacks --> Train["Train Model\nExecute learning process"]
    Train --> SaveModel["Save Trained Model\nStore model and statistics"]
    SaveModel --> End
```

Sources: [rl_zoo3/train.py:20-286](), [rl_zoo3/exp_manager.py:193-232](), [rl_zoo3/exp_manager.py:233-270]()

## ExperimentManager Class

The `ExperimentManager` class serves as the central component of the training system:

```mermaid
classDiagram
    class ExperimentManager {
        +algo: str
        +env_name: EnvironmentName
        +n_timesteps: int
        +normalize: bool
        +save_path: str
        +tensorboard_log: str
        +setup_experiment()
        +learn(model)
        +save_trained_model(model)
        +create_envs(n_envs, eval_env, no_log)
        +read_hyperparameters()
        +create_callbacks()
        +hyperparameters_optimization()
        -_preprocess_hyperparams(hyperparams)
        -_preprocess_action_noise(hyperparams, saved_hyperparams, env)
        -_load_pretrained_agent(hyperparams, env)
    }
```

Sources: [rl_zoo3/exp_manager.py:56-193]()

### Key Methods

1. **setup_experiment()**: Prepares the training environment by reading hyperparameters, creating environments, and initializing the model.

2. **learn(model)**: Executes the training loop with the specified model and callbacks.

3. **save_trained_model(model)**: Saves the trained model, replay buffer (optional), and environment normalization statistics.

4. **create_envs()**: Creates vectorized environments for training or evaluation.

5. **read_hyperparameters()**: Loads hyperparameters from YAML or Python configuration files.

6. **create_callbacks()**: Sets up callbacks for evaluation, checkpointing, and progress tracking.

7. **hyperparameters_optimization()**: Runs hyperparameter optimization using Optuna.

Sources: [rl_zoo3/exp_manager.py:193-232](), [rl_zoo3/exp_manager.py:233-270](), [rl_zoo3/exp_manager.py:271-290](), [rl_zoo3/exp_manager.py:637-713](), [rl_zoo3/exp_manager.py:316-355](), [rl_zoo3/exp_manager.py:537-572](), [rl_zoo3/exp_manager.py:863-972]()

## Configuration and Hyperparameter Management

Hyperparameters are managed through a hierarchical system:

| Configuration Source | Priority | Description |
|----------------------|----------|-------------|
| Default YAML/Python files | Lowest | Base hyperparameters for each algorithm/environment combination |
| Optuna study results | Medium | Hyperparameters loaded from previous optimization trials |
| Command-line overrides | Highest | Parameters specified via `--hyperparams` option |

The hyperparameter loading process:

```mermaid
flowchart TD
    Start([Load Hyperparameters]) --> ConfigType{"Config file type?"}
    
    ConfigType -- YAML --> LoadYAML["Load from YAML file"]
    ConfigType -- Python --> LoadPython["Load from Python module"]
    
    LoadYAML --> EnvCheck{"Environment in config?"}
    LoadPython --> EnvCheck
    
    EnvCheck -- Yes --> UseEnvParams["Use environment-specific params"]
    EnvCheck -- No --> CheckAtari{"Is Atari environment?"}
    
    CheckAtari -- Yes --> UseAtariParams["Use Atari default params"]
    CheckAtari -- No --> Error["Error: Hyperparameters not found"]
    
    UseEnvParams --> CheckOptuna{"Load from Optuna study?"}
    UseAtariParams --> CheckOptuna
    
    CheckOptuna -- Yes --> LoadOptuna["Load optimal parameters\nfrom specified trial"]
    CheckOptuna -- No --> CheckCustom["Check for custom hyperparams"]
    
    LoadOptuna --> CheckCustom
    
    CheckCustom -- "Custom params\nspecified" --> ApplyCustom["Apply custom parameters"]
    CheckCustom -- "No custom\nparams" --> ReturnParams["Return hyperparameters"]
    
    ApplyCustom --> ReturnParams
    
    ReturnParams --> End([End])
    Error --> ErrorEnd([Raise Error])
```

Sources: [rl_zoo3/exp_manager.py:316-355](), [rl_zoo3/exp_manager.py:357-373]()

## Environment Creation

The training system creates environments through a sophisticated process that handles various environment types and wrappers:

```mermaid
flowchart TD
    Start([Create Environment]) --> VecEnv["Create VecEnv\nDummyVecEnv or SubprocVecEnv"]
    
    VecEnv --> CustomWrapper{"VecEnv wrapper\nspecified?"}
    CustomWrapper -- Yes --> ApplyVecWrapper["Apply VecEnv wrapper"]
    CustomWrapper -- No --> Normalize{"Normalize\nenabled?"}
    
    ApplyVecWrapper --> Normalize
    
    Normalize -- Yes --> ApplyNormalize["Apply VecNormalize\nfor obs/reward normalization"]
    Normalize -- No --> FrameStack{"Frame stack\nenabled?"}
    
    ApplyNormalize --> FrameStack
    
    FrameStack -- Yes --> ApplyFrameStack["Apply VecFrameStack"]
    FrameStack -- No --> ImageCheck{"Image\nobservation space?"}
    
    ApplyFrameStack --> ImageCheck
    
    ImageCheck -- Yes --> NeedsTranspose{"Channel-last\nformat?"}
    ImageCheck -- No --> Return["Return Environment"]
    
    NeedsTranspose -- Yes --> ApplyTranspose["Apply VecTransposeImage"]
    NeedsTranspose -- No --> Return
    
    ApplyTranspose --> Return
    
    Return --> End([End])
```

Sources: [rl_zoo3/exp_manager.py:637-713]()

## Training Execution

The `learn()` method handles the actual training execution:

```mermaid
flowchart TD
    Start([Start Training]) --> ConfigLogging["Configure logging interval"]
    ConfigLogging --> SetupCallbacks["Setup callbacks\nfor training control"]
    
    SetupCallbacks --> CheckARS{"Algorithm\nis ARS?"}
    
    CheckARS -- Yes --> SetupAsync["Setup AsyncEval\nfor parallel evaluation"]
    CheckARS -- No --> ExecuteTraining["Execute model.learn()\nwith callbacks"]
    
    SetupAsync --> ExecuteTraining
    
    ExecuteTraining --> HandleInterrupt{"Training\ninterrupted?"}
    
    HandleInterrupt -- Yes --> Cleanup["Cleanup and release resources"]
    HandleInterrupt -- No --> Cleanup
    
    Cleanup --> End([End Training])
```

Sources: [rl_zoo3/exp_manager.py:233-270]()

## Hyperparameter Optimization

When enabled, the training system performs hyperparameter optimization using Optuna:

```mermaid
flowchart TD
    Start([Start Optimization]) --> CreateSampler["Create sampler\n(TPE, Random, Auto)"]
    CreateSampler --> CreatePruner["Create pruner\n(Median, Halving, None)"]
    CreatePruner --> SetupStorage["Setup storage\n(Journal file or DB)"]
    
    SetupStorage --> CreateStudy["Create or load Optuna study"]
    CreateStudy --> RunTrials["Run optimization trials"]
    
    RunTrials --> ForEachTrial["For each trial:"]
    ForEachTrial --> SampleParams["Sample hyperparameters"]
    SampleParams --> CreateEnv["Create environment"]
    CreateEnv --> CreateModel["Create model with sampled params"]
    CreateModel --> TrainEval["Train and evaluate model"]
    TrainEval --> CheckPerformance["Check performance"]
    
    CheckPerformance --> PruneCheck{"Should prune?"}
    PruneCheck -- Yes --> PruneTrial["Prune trial"]
    PruneCheck -- No --> NextTrial["Continue to next trial"]
    
    PruneTrial --> NextTrial
    NextTrial --> CheckDone{"All trials\ncomplete?"}
    
    CheckDone -- No --> ForEachTrial
    CheckDone -- Yes --> ReportResults["Report best parameters"]
    
    ReportResults --> SaveResults["Save results and plots"]
    SaveResults --> End([End Optimization])
```

Sources: [rl_zoo3/exp_manager.py:863-972](), [rl_zoo3/exp_manager.py:772-861]()

## Environment Handling and Wrappers

The training system supports various environment types and wrappers:

| Environment Type | Detection Method | Special Handling |
|------------------|------------------|------------------|
| Atari            | Entry point check | Frame skipping, episodic life, etc. |
| MiniGrid         | Entry point check | Non-deterministic evaluation |
| PyBullet         | Entry point check | Specific wrappers |
| Robotics/GoalEnv | Entry point check | Success rate logging |
| Panda Gym        | Entry point check | Robotics interface |
| Generic          | Default          | Standard processing |

Sources: [rl_zoo3/exp_manager.py:574-598](), [rl_zoo3/exp_manager.py:637-713]()

## Integration with Stable-Baselines3

The training system integrates with Stable-Baselines3 algorithms through the `ALGOS` dictionary:

```mermaid
graph TD
    subgraph "Training System"
        ExpManager["ExperimentManager"]
        ModelCreation["Model Creation"]
    end
    
    subgraph "Stable-Baselines3 Algorithms"
        A2C["A2C"]
        PPO["PPO"]
        SAC["SAC"]
        TD3["TD3"]
        DDPG["DDPG"]
        DQN["DQN"]
    end
    
    subgraph "SB3-Contrib Algorithms"
        TQC["TQC"]
        TRPO["TRPO"]
        ARS["ARS"]
        RecurrentPPO["RecurrentPPO"]
        CrossQ["CrossQ"]
    end
    
    ExpManager --> ModelCreation
    ModelCreation --> ALGOS["ALGOS Dictionary\nMaps algorithm name to class"]
    
    ALGOS --> A2C
    ALGOS --> PPO
    ALGOS --> SAC
    ALGOS --> TD3
    ALGOS --> DDPG
    ALGOS --> DQN
    
    ALGOS --> TQC
    ALGOS --> TRPO
    ALGOS --> ARS
    ALGOS --> RecurrentPPO
    ALGOS --> CrossQ
```

Sources: [rl_zoo3/train.py:20-266](), [rl_zoo3/exp_manager.py:193-232]()

## Callback System

The training system uses a flexible callback system to monitor and control training:

| Callback | Purpose |
|----------|---------|
| `ProgressBarCallback` | Displays training progress (when `--progress` is specified) |
| `CheckpointCallback` | Saves model checkpoints at specified frequency |
| `EvalCallback` | Evaluates model performance during training |
| `SaveVecNormalizeCallback` | Saves normalization statistics when a new best model is found |
| `TrialEvalCallback` | Used during hyperparameter optimization to evaluate trials |

Sources: [rl_zoo3/exp_manager.py:537-572]()

## Data Flow

The following diagram illustrates the data flow through the training system:

```mermaid
flowchart LR
    subgraph "Configuration Phase"
        CLI["Command-Line Arguments"] --> ExpManager["ExperimentManager"]
        HyperFiles["Hyperparameter Files"] --> ExpManager
    end
    
    subgraph "Setup Phase"
        ExpManager --> Hyperparams["Processed Hyperparameters"]
        Hyperparams --> EnvConfig["Environment Configuration"]
        Hyperparams --> ModelConfig["Model Configuration"]
        Hyperparams --> CBConfig["Callback Configuration"]
    end
    
    subgraph "Training Phase"
        EnvConfig --> Env["Training Environment"]
        ModelConfig --> Model["RL Algorithm Model"]
        CBConfig --> Callbacks["Training Callbacks"]
        
        Env --> Observations["Environment Observations"]
        Observations --> Model
        Model --> Actions["Agent Actions"]
        Actions --> Env
        
        Env --> Rewards["Environment Rewards"]
        Rewards --> Model
        
        Model --> TrainingStats["Training Statistics"]
        TrainingStats --> Callbacks
    end
    
    subgraph "Output Phase"
        Model --> SavedModel["Saved Model (.zip)"]
        Model --> ReplayBuffer["Replay Buffer (optional)"]
        Env --> NormStats["Normalization Statistics"]
    end
```

Sources: [rl_zoo3/train.py:20-286](), [rl_zoo3/exp_manager.py:193-232](), [rl_zoo3/exp_manager.py:233-270](), [rl_zoo3/exp_manager.py:271-290]()

## Using the Training System

The training system can be used in two primary ways:

1. **Command-line interface**: Run `python train.py` with appropriate arguments to train an agent.

2. **Python API**: Import and use the `ExperimentManager` directly in your code.

Example command to train a PPO agent on CartPole:

```bash
python train.py --algo ppo --env CartPole-v1 -n 50000 --eval-freq 10000
```

Example command for hyperparameter optimization:

```bash
python train.py --algo ppo --env CartPole-v1 -n 50000 --optimize-hyperparameters --n-trials 100 
```

Sources: [rl_zoo3/train.py:20-286]()

## Conclusion

The Training System in RL-Baselines3-Zoo provides a flexible and powerful framework for training reinforcement learning agents. It handles the complexity of environment creation, model initialization, hyperparameter management, and training execution, allowing users to focus on experimenting with different algorithms and environments.

---

