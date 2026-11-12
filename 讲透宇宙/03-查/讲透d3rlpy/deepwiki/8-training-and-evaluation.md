<!-- source: DeepWiki mcp.deepwiki.com · repo takuseno/d3rlpy · page 8 Training and Evaluation · fetched 2026-10-30 -->

# Training and Evaluation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [d3rlpy/algos/transformer/inputs.py](d3rlpy/algos/transformer/inputs.py)
- [d3rlpy/logging/file_adapter.py](d3rlpy/logging/file_adapter.py)
- [d3rlpy/logging/logger.py](d3rlpy/logging/logger.py)
- [d3rlpy/logging/noop_adapter.py](d3rlpy/logging/noop_adapter.py)
- [d3rlpy/logging/tensorboard_adapter.py](d3rlpy/logging/tensorboard_adapter.py)
- [d3rlpy/logging/utils.py](d3rlpy/logging/utils.py)
- [d3rlpy/logging/wandb_adapter.py](d3rlpy/logging/wandb_adapter.py)
- [d3rlpy/metrics/evaluators.py](d3rlpy/metrics/evaluators.py)
- [d3rlpy/metrics/utility.py](d3rlpy/metrics/utility.py)
- [docs/references/metrics.rst](docs/references/metrics.rst)
- [tests/algos/transformer/test_inputs.py](tests/algos/transformer/test_inputs.py)
- [tests/dummy_env.py](tests/dummy_env.py)
- [tests/envs/test_wrappers.py](tests/envs/test_wrappers.py)
- [tests/logging/test_logger.py](tests/logging/test_logger.py)
- [tests/metrics/test_evaluators.py](tests/metrics/test_evaluators.py)
- [tests/metrics/test_utility.py](tests/metrics/test_utility.py)

</details>



This document covers d3rlpy's training and evaluation infrastructure, which provides comprehensive metrics, logging, and experiment tracking capabilities for reinforcement learning algorithms. The system supports both offline evaluation metrics and environment-based evaluation, along with flexible logging adapters for popular experiment tracking platforms.

For information about the core algorithm training loops, see [Algorithm System](#5). For data preprocessing and scaling during training, see [Data Preprocessing](#6.3).

## Overview

The training and evaluation system consists of two main components:

1. **Metrics and Evaluation**: A protocol-based system for computing various offline and online evaluation metrics
2. **Logging and Experiment Tracking**: An adapter-based logging system supporting multiple backends (WandB, TensorBoard, file-based)

These systems integrate seamlessly with d3rlpy's algorithm framework to provide comprehensive monitoring and evaluation during training.

## Metrics and Evaluation System

### Evaluation Protocol Architecture

The evaluation system is built around the `EvaluatorProtocol` which defines a standardized interface for all evaluation metrics.

```mermaid
graph TD
    subgraph "Evaluation Protocol"
        EP["EvaluatorProtocol"]
        EP --> |"__call__(algo, dataset)"| FLOAT["float"]
    end
    
    subgraph "Offline Metrics"
        TD["TDErrorEvaluator"]
        DSA["DiscountedSumOfAdvantageEvaluator"] 
        AVE["AverageValueEstimationEvaluator"]
        ISVE["InitialStateValueEstimationEvaluator"]
        SOPC["SoftOPCEvaluator"]
        CAD["ContinuousActionDiffEvaluator"]
        DAM["DiscreteActionMatchEvaluator"]
    end
    
    subgraph "Comparison Metrics"
        CCAD["CompareContinuousActionDiffEvaluator"]
        CDAM["CompareDiscreteActionMatchEvaluator"]
    end
    
    subgraph "Environment Evaluation"
        EE["EnvironmentEvaluator"]
        UTIL["evaluate_qlearning_with_environment()"]
        EE --> UTIL
    end
    
    EP -.-> TD
    EP -.-> DSA
    EP -.-> AVE
    EP -.-> ISVE
    EP -.-> SOPC
    EP -.-> CAD
    EP -.-> DAM
    EP -.-> CCAD
    EP -.-> CDAM
    EP -.-> EE
    
    subgraph "Data Processing"
        MB["make_batches()"]
        WS["WINDOW_SIZE=1024"]
        MB --> WS
    end
    
    TD --> MB
    DSA --> MB
    AVE --> MB
```

Sources: [d3rlpy/metrics/evaluators.py:34-50](), [d3rlpy/metrics/evaluators.py:52-68]()

### Core Evaluation Metrics

#### TD Error Evaluation
The `TDErrorEvaluator` measures temporal difference error to detect Q-function overfitting:

```mermaid
graph LR
    subgraph "TD Error Computation"
        OBS["observations"] --> PV["predict_value()"]
        ACT["actions"] --> PV
        PV --> VALUES["current_values"]
        
        N_OBS["next_observations"] --> PRED["predict()"]
        PRED --> N_ACT["next_actions"]
        N_OBS --> PV2["predict_value()"]
        N_ACT --> PV2
        PV2 --> N_VALUES["next_values"]
        
        REW["rewards"] --> TARGET["target = r + γ * next_values * mask"]
        N_VALUES --> TARGET
        GAMMA["gamma"] --> TARGET
        TERM["terminals"] --> MASK["mask = 1 - terminals"]
        MASK --> TARGET
        
        VALUES --> ERROR["td_error = (current_values - target)²"]
        TARGET --> ERROR
    end
    
    subgraph "Reward Scaling"
        REW_SCALER["reward_scaler"] -.-> |"transform_numpy()"| REW
    end
```

Sources: [d3rlpy/metrics/evaluators.py:71-121](), [d3rlpy/metrics/evaluators.py:114-119]()

#### Value Estimation Metrics
Several evaluators assess the quality and scale of value function estimates:

| Evaluator | Formula | Purpose |
|-----------|---------|---------|
| `AverageValueEstimationEvaluator` | `E[max_a Q(s,a)]` | Detect value overestimation |
| `InitialStateValueEstimationEvaluator` | `E[Q(s_0, π(s_0))]` | Expected return from initial states |
| `DiscountedSumOfAdvantageEvaluator` | `Σ γ^t A(s_t, a_t)` | Policy improvement over dataset |

Sources: [d3rlpy/metrics/evaluators.py:191-226](), [d3rlpy/metrics/evaluators.py:229-271](), [d3rlpy/metrics/evaluators.py:124-188]()

### Environment-Based Evaluation

The `EnvironmentEvaluator` provides online evaluation by running the trained policy in an environment:

```mermaid
graph TD
    subgraph "Environment Evaluation"
        ENV["GymEnv"] --> EE["EnvironmentEvaluator"]
        N_TRIALS["n_trials"] --> EE
        EPSILON["epsilon"] --> EE
        
        EE --> EVAL_FUNC["evaluate_qlearning_with_environment()"]
        
        subgraph "Episode Loop"
            RESET["env.reset()"] --> OBS["observation"]
            OBS --> PRED["algo.predict()"]
            PRED --> ACT["action"]
            ACT --> STEP["env.step()"]
            STEP --> REWARD["reward"]
            STEP --> DONE["done/truncated"]
            STEP --> OBS
            DONE --> |"if not done"| OBS
            DONE --> |"if done"| EPISODE_REWARD["episode_reward"]
        end
        
        EVAL_FUNC --> EPISODE_REWARD
        EPISODE_REWARD --> MEAN["np.mean(episode_rewards)"]
    end
    
    subgraph "Epsilon-Greedy Policy"
        RANDOM["np.random.random()"] --> CHECK["< epsilon?"]
        CHECK --> |"yes"| SAMPLE["env.action_space.sample()"]
        CHECK --> |"no"| PRED
    end
```

Sources: [d3rlpy/metrics/evaluators.py:506-548](), [d3rlpy/metrics/utility.py:12-71]()

## Logging and Experiment Tracking System

### Logger Architecture

The logging system uses an adapter pattern to support multiple experiment tracking backends:

```mermaid
graph TD
    subgraph "Core Logging"
        D3LOGGER["D3RLPyLogger"]
        ADAPTER_FACTORY["LoggerAdapterFactory"]
        ADAPTER["LoggerAdapter"]
        
        D3LOGGER --> ADAPTER_FACTORY
        ADAPTER_FACTORY --> |"create()"| ADAPTER
        D3LOGGER --> ADAPTER
    end
    
    subgraph "Adapter Implementations"
        FILE_ADAPTER["FileAdapter"]
        WANDB_ADAPTER["WanDBAdapter"] 
        TB_ADAPTER["TensorboardAdapter"]
        NOOP_ADAPTER["NoopAdapter"]
        COMBINE_ADAPTER["CombineAdapter"]
    end
    
    subgraph "Adapter Factories"
        FILE_FACTORY["FileAdapterFactory"]
        WANDB_FACTORY["WanDBAdapterFactory"]
        TB_FACTORY["TensorboardAdapterFactory"] 
        NOOP_FACTORY["NoopAdapterFactory"]
        COMBINE_FACTORY["CombineAdapterFactory"]
    end
    
    ADAPTER -.-> FILE_ADAPTER
    ADAPTER -.-> WANDB_ADAPTER
    ADAPTER -.-> TB_ADAPTER
    ADAPTER -.-> NOOP_ADAPTER
    ADAPTER -.-> COMBINE_ADAPTER
    
    ADAPTER_FACTORY -.-> FILE_FACTORY
    ADAPTER_FACTORY -.-> WANDB_FACTORY
    ADAPTER_FACTORY -.-> TB_FACTORY
    ADAPTER_FACTORY -.-> NOOP_FACTORY
    ADAPTER_FACTORY -.-> COMBINE_FACTORY
```

Sources: [d3rlpy/logging/logger.py:143-167](), [d3rlpy/logging/logger.py:123-140]()

### Logger Adapter Protocol

All logging adapters implement the `LoggerAdapter` protocol:

```mermaid
graph LR
    subgraph "LoggerAdapter Methods"
        WP["write_params()"]
        BWM["before_write_metric()"]
        WM["write_metric()"]
        AWM["after_write_metric()"]
        SM["save_model()"]
        WMD["watch_model()"]
        CLOSE["close()"]
    end
    
    subgraph "Data Flow"
        PARAMS["params: dict"] --> WP
        EPOCH["epoch: int"] --> BWM
        STEP["step: int"] --> BWM
        EPOCH --> WM
        STEP --> WM
        NAME["name: str"] --> WM
        VALUE["value: float"] --> WM
        EPOCH --> AWM
        STEP --> AWM
        EPOCH --> SM
        ALGO["algo: SaveProtocol"] --> SM
    end
```

Sources: [d3rlpy/logging/logger.py:61-121]()

### WandB Integration

The `WanDBAdapter` provides integration with Weights & Biases:

```mermaid
graph TD
    subgraph "WandB Setup"
        INIT["wandb.init()"] --> RUN["wandb.run"]
        PROJECT["project"] --> INIT
        EXP_NAME["experiment_name"] --> INIT
        
        RUN --> WATCH["run.watch()"]
        MODULES["algo.impl.modules"] --> WATCH
        WATCH --> GRADIENTS["log='gradients'"]
        N_STEPS["n_steps_per_epoch"] --> WATCH
    end
    
    subgraph "Logging Operations"
        CONFIG["run.config.update()"] --> PARAMS["hyperparameters"]
        LOG["run.log()"] --> METRICS["metrics + epoch"]
        FINISH["run.finish()"] --> CLOSE["adapter.close()"]
    end
    
    WATCH -.-> LOG
```

Sources: [d3rlpy/logging/wandb_adapter.py:25-43](), [d3rlpy/logging/wandb_adapter.py:52-70]()

### File-Based Logging

The `FileAdapter` saves metrics as CSV files and models as `.d3` files:

```mermaid
graph TD
    subgraph "File Structure"
        LOGDIR["logdir/"] --> PARAMS_JSON["params.json"]
        LOGDIR --> METRIC_CSV["metric_name.csv"]
        LOGDIR --> MODEL_D3["model_epoch.d3"]
        LOGDIR --> GRAD_CSV["module_name_grad.csv"]
    end
    
    subgraph "File Operations"
        JSON_DUMP["json.dumps()"] --> PARAMS_JSON
        CSV_WRITE["print(epoch,step,value)"] --> METRIC_CSV
        SAVE["algo.save()"] --> MODEL_D3
        GRAD_STATS["min,max,mean,std"] --> GRAD_CSV
    end
    
    subgraph "Gradient Tracking"
        GET_GRADS["modules.get_gradients()"] --> GRAD_STATS
        FIRST_CALL["_is_model_watched"] --> HEADER["epoch,step,min,max,mean,std"]
        HEADER --> GRAD_CSV
    end
```

Sources: [d3rlpy/logging/file_adapter.py:47-82](), [d3rlpy/logging/file_adapter.py:90-121]()

## Training Integration

### Metric Collection and Reporting

The `D3RLPyLogger` manages the collection and reporting of metrics during training:

```mermaid
graph TD
    subgraph "Training Loop Integration"
        ALGO["Algorithm"] --> LOGGER["D3RLPyLogger"]
        EVALUATORS["evaluators: dict"] --> METRICS["metric_values"]
        
        subgraph "Metric Buffering"
            ADD_METRIC["add_metric()"] --> BUFFER["_metrics_buffer"]
            MEASURE_TIME["measure_time()"] --> ADD_METRIC
            BUFFER --> COMMIT["commit()"]
        end
        
        subgraph "Logging Cycle"
            COMMIT --> BEFORE["adapter.before_write_metric()"]
            BEFORE --> WRITE["adapter.write_metric()"]
            WRITE --> AFTER["adapter.after_write_metric()"]
            AFTER --> WATCH["adapter.watch_model()"]
            WATCH --> CLEAR["_metrics_buffer.clear()"]
        end
    end
    
    subgraph "Experiment Setup"
        FACTORY["adapter_factory"] --> CREATE["create()"]
        EXP_NAME["experiment_name"] --> CREATE
        TIMESTAMP["with_timestamp"] --> DATE["datetime.now()"]
        DATE --> EXP_NAME
        CREATE --> ADAPTER["adapter"]
        ADAPTER --> LOGGER
    end
```

Sources: [d3rlpy/logging/logger.py:149-166](), [d3rlpy/logging/logger.py:175-198](), [d3rlpy/logging/logger.py:206-213]()

### Protocol Definitions

The logging system defines several protocols for type safety:

| Protocol | Purpose | Key Methods |
|----------|---------|-------------|
| `SaveProtocol` | Models that can be saved | `save(fname: str)` |
| `ModuleProtocol` | Neural network modules | `get_torch_modules()`, `get_gradients()` |
| `ImplProtocol` | Algorithm implementations | `modules: ModuleProtocol` |
| `AlgProtocol` | Algorithm interface | `impl: Optional[ImplProtocol]` |

Sources: [d3rlpy/logging/logger.py:40-59]()

The training and evaluation system provides comprehensive monitoring capabilities for d3rlpy algorithms, supporting both research and production use cases through its flexible adapter architecture and extensive metric collection.

---

