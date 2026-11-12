<!-- source: DeepWiki mcp.deepwiki.com · repo araffin/rl-baselines-zoo · page 6 Advanced Features · fetched 2026-10-30 -->

# Advanced Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [requirements.txt](requirements.txt)
- [trained_agents/dqn/BeamRiderNoFrameskip-v4.pkl](trained_agents/dqn/BeamRiderNoFrameskip-v4.pkl)
- [trained_agents/ppo2/BipedalWalkerHardcore-v2.pkl](trained_agents/ppo2/BipedalWalkerHardcore-v2.pkl)
- [trained_agents/ppo2/BipedalWalkerHardcore-v2/obs_rms.pkl](trained_agents/ppo2/BipedalWalkerHardcore-v2/obs_rms.pkl)
- [trained_agents/ppo2/BipedalWalkerHardcore-v2/ret_rms.pkl](trained_agents/ppo2/BipedalWalkerHardcore-v2/ret_rms.pkl)
- [utils/callbacks.py](utils/callbacks.py)
- [utils/import_envs.py](utils/import_envs.py)

</details>



This document covers advanced functionality in the RL Baselines Zoo that extends beyond basic training and evaluation workflows. It focuses on custom callbacks for training extensions, trained agent storage management, and advanced environment integration patterns.

For basic training and evaluation workflows, see [Getting Started](#2). For hyperparameter optimization, see [Hyperparameter Optimization](#2.3). For environment configuration basics, see [Environment Management](#3.2).

## Custom Callbacks and Training Extensions

The RL Baselines Zoo implements a sophisticated callback system that allows for custom training behavior, evaluation during training, and automated model management. The callback system is built on top of Stable Baselines' `BaseCallback` class and provides specialized implementations for different training scenarios.

### Training Callback Architecture

```mermaid
graph TB
    subgraph "BaseCallback System"
        BC["BaseCallback"]
        EC["EvalCallback"]
    end
    
    subgraph "Custom Callbacks"
        TEC["TrialEvalCallback"]
        SVNC["SaveVecNormalizeCallback"]
    end
    
    subgraph "Training Integration"
        TL["Training Loop"]
        HP["Hyperparameter Optimization"]
        MS["Model Saving"]
    end
    
    BC --> EC
    EC --> TEC
    BC --> SVNC
    
    TEC --> HP
    SVNC --> MS
    TL --> TEC
    TL --> SVNC
```

**Training Callback Integration Flow**

Sources: [utils/callbacks.py:1-68]()

### TrialEvalCallback Implementation

The `TrialEvalCallback` class extends the standard evaluation callback to support Optuna-based hyperparameter optimization trials. It provides automatic trial pruning based on performance metrics.

| Component | Function | Key Methods |
|-----------|----------|-------------|
| Trial Management | Integrates with Optuna trials | `__init__`, `_on_step` |
| Performance Reporting | Reports metrics to Optuna | `trial.report()` |
| Pruning Logic | Stops underperforming trials | `trial.should_prune()` |

```mermaid
flowchart TD
    TECInit["TrialEvalCallback.__init__()"] --> EvalFreqCheck["eval_freq check"]
    EvalFreqCheck -->|"n_calls % eval_freq == 0"| SuperEval["super()._on_step()"]
    SuperEval --> ReportMetrics["trial.report(-1 * last_mean_reward, eval_idx)"]
    ReportMetrics --> PruneCheck["trial.should_prune()"]
    PruneCheck -->|"True"| SetPruned["is_pruned = True"]
    PruneCheck -->|"False"| Continue["return True"]
    SetPruned --> StopTraining["return False"]
```

**TrialEvalCallback Decision Flow**

Sources: [utils/callbacks.py:8-35]()

### SaveVecNormalizeCallback Implementation

The `SaveVecNormalizeCallback` handles automatic saving of vectorized environment normalization statistics during training. This ensures that observation and reward normalization parameters are preserved for later use during evaluation.

```mermaid
graph LR
    subgraph "Callback Lifecycle"
        Init["_init_callback()"]
        Step["_on_step()"]
        Save["VecNormalize.save()"]
    end
    
    subgraph "File Management"
        CheckPath["os.makedirs(save_path)"]
        GenPath["Generate file path"]
        SaveFile["Save normalization stats"]
    end
    
    Init --> CheckPath
    Step --> GenPath
    GenPath --> SaveFile
    SaveFile --> Save
```

**SaveVecNormalizeCallback Process Flow**

The callback supports both timestamped saves and overwrite modes:

| Save Mode | Path Pattern | Use Case |
|-----------|-------------|----------|
| Timestamped | `{name_prefix}_{num_timesteps}_steps.pkl` | Training checkpoints |
| Overwrite | `vecnormalize.pkl` | Final model state |

Sources: [utils/callbacks.py:37-68]()

## Trained Agent Storage and Management

The RL Baselines Zoo implements a comprehensive storage system for trained agents that preserves all necessary information for model deployment and evaluation. The storage system maintains model artifacts, normalization statistics, and configuration metadata.

### Agent Storage Structure

```mermaid
graph TB
    subgraph "trained_agents/"
        subgraph "algorithm_name/"
            subgraph "environment_name/"
                Model["model.pkl"]
                Config["config.yml"]
                ObsNorm["obs_rms.pkl"]
                RetNorm["ret_rms.pkl"]
            end
        end
    end
    
    subgraph "Storage Components"
        ModelData["Model Parameters & Architecture"]
        NormStats["Normalization Statistics"]
        ConfigData["Training Configuration"]
    end
    
    Model --> ModelData
    ObsNorm --> NormStats
    RetNorm --> NormStats
    Config --> ConfigData
```

**Trained Agent Storage Architecture**

Sources: [trained_agents/ppo2/BipedalWalkerHardcore-v2.pkl:1-10](), [trained_agents/ppo2/BipedalWalkerHardcore-v2/obs_rms.pkl:1-12](), [trained_agents/ppo2/BipedalWalkerHardcore-v2/ret_rms.pkl:1-9]()

### Normalization Statistics Management

The system automatically manages observation and return normalization statistics through the `RunningMeanStd` class. These statistics are critical for maintaining consistent preprocessing between training and evaluation phases.

| Statistic Type | File | Content | Usage |
|---------------|------|---------|--------|
| Observation Normalization | `obs_rms.pkl` | Mean, variance, count for each observation dimension | Input preprocessing |
| Return Normalization | `ret_rms.pkl` | Mean, variance, count for episode returns | Reward scaling |

### Model Serialization Format

The trained models are stored using Python's pickle format with the following key components:

```mermaid
flowchart LR
    subgraph "Model Pickle Contents"
        HP["Hyperparameters"]
        Policy["Policy Network"]
        ObsSpace["Observation Space"]
        ActSpace["Action Space"]
        Weights["Network Weights"]
    end
    
    subgraph "Model Loading Process"
        Load["Load .pkl file"]
        Validate["Validate spaces"]
        Restore["Restore policy"]
    end
    
    HP --> Load
    Policy --> Load
    ObsSpace --> Validate
    ActSpace --> Validate
    Weights --> Restore
```

**Model Serialization Components**

The model files contain algorithm-specific hyperparameters, network architectures, and learned parameters. The observation and action spaces are preserved to ensure compatibility during loading.

Sources: [trained_agents/ppo2/BipedalWalkerHardcore-v2.pkl:1-50]()

## Environment Extensions and Import System

The RL Baselines Zoo supports a modular environment extension system that allows integration with external environment packages. The system uses conditional imports to maintain compatibility across different installation configurations.

### Environment Import Architecture

```mermaid
graph TB
    subgraph "Core Environment System"
        GymEnvs["Gym Environments"]
        CustomWrappers["Custom Wrappers"]
    end
    
    subgraph "Optional Extensions"
        PybulletEnvs["pybullet_envs"]
        HighwayEnv["highway_env"]
        MoccaEnvs["mocca_envs"]
    end
    
    subgraph "Import Management"
        TryImport["try/except import"]
        NoneHandler["Set to None if unavailable"]
        ConditionalUse["Conditional usage"]
    end
    
    TryImport --> PybulletEnvs
    TryImport --> HighwayEnv
    TryImport --> MoccaEnvs
    
    PybulletEnvs --> NoneHandler
    HighwayEnv --> NoneHandler
    MoccaEnvs --> NoneHandler
    
    NoneHandler --> ConditionalUse
```

**Environment Extension Import System**

### Conditional Environment Loading

The environment import system implements graceful degradation when optional dependencies are not available:

| Environment Package | Purpose | Fallback Behavior |
|---------------------|---------|-------------------|
| `pybullet_envs` | Physics simulation environments | Set to `None`, skip registration |
| `highway_env` | Autonomous driving scenarios | Set to `None`, skip registration |
| `mocca_envs` | Multi-object manipulation | Set to `None`, skip registration |

```python
# Pattern used for conditional imports
try:
    import pybullet_envs
except ImportError:
    pybullet_envs = None
```

This pattern ensures that the system remains functional even when specific environment packages are not installed, allowing for flexible deployment configurations.

Sources: [utils/import_envs.py:1-15]()

## Advanced Configuration Dependencies

The advanced features system integrates with several key dependencies that enable extended functionality:

### Required Dependencies for Advanced Features

| Package | Purpose | Advanced Features Enabled |
|---------|---------|---------------------------|
| `optuna` | Hyperparameter optimization | `TrialEvalCallback` trial management |
| `scikit-optimize` | Alternative optimization | Bayesian optimization support |
| `pyyaml>=5.1` | Configuration management | Advanced YAML parsing |
| `pytablewriter` | Report generation | Benchmark table formatting |
| `seaborn` | Visualization | Advanced plotting capabilities |

### Dependency Integration Flow

```mermaid
graph LR
    subgraph "Core Dependencies"
        SB["stable-baselines"]
        Gym["gym environments"]
    end
    
    subgraph "Advanced Dependencies"
        Optuna["optuna"]
        SKOpt["scikit-optimize"]
        YAML["pyyaml"]
    end
    
    subgraph "Advanced Features"
        HPOpt["Hyperparameter Optimization"]
        CustomCB["Custom Callbacks"]
        AdvConfig["Advanced Configuration"]
    end
    
    Optuna --> HPOpt
    SKOpt --> HPOpt
    YAML --> AdvConfig
    SB --> CustomCB
    
    HPOpt --> CustomCB
    AdvConfig --> CustomCB
```

**Advanced Feature Dependency Graph**

Sources: [requirements.txt:1-10]()

The advanced features system provides a robust foundation for extending the basic RL training capabilities with custom callbacks, sophisticated model management, and flexible environment integration. These features enable production-ready deployments and advanced research workflows while maintaining backward compatibility and graceful degradation.

---

