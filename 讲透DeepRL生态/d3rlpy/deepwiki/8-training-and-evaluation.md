> 来源: [https://deepwiki.com/takuseno/d3rlpy/8-training-and-evaluation](https://deepwiki.com/takuseno/d3rlpy/8-training-and-evaluation)
> DeepWiki takuseno/d3rlpy | Last indexed: 25 June 2025 (4f0956

# Training and Evaluation

  Relevant source files 
 - [d3rlpy/algos/transformer/inputs.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/algos/transformer/inputs.py)
 - [d3rlpy/logging/file_adapter.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/logging/file_adapter.py)
 - [d3rlpy/logging/logger.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/logging/logger.py)
 - [d3rlpy/logging/noop_adapter.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/logging/noop_adapter.py)
 - [d3rlpy/logging/tensorboard_adapter.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/logging/tensorboard_adapter.py)
 - [d3rlpy/logging/utils.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/logging/utils.py)
 - [d3rlpy/logging/wandb_adapter.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/logging/wandb_adapter.py)
 - [d3rlpy/metrics/evaluators.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/metrics/evaluators.py)
 - [d3rlpy/metrics/utility.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/metrics/utility.py)
 - [docs/references/metrics.rst](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/metrics.rst)
 - [tests/algos/transformer/test_inputs.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tests/algos/transformer/test_inputs.py)
 - [tests/dummy_env.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tests/dummy_env.py)
 - [tests/envs/test_wrappers.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tests/envs/test_wrappers.py)
 - [tests/logging/test_logger.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tests/logging/test_logger.py)
 - [tests/metrics/test_evaluators.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tests/metrics/test_evaluators.py)
 - [tests/metrics/test_utility.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tests/metrics/test_utility.py)
 
  This document covers d3rlpy's training and evaluation infrastructure, which provides comprehensive metrics, logging, and experiment tracking capabilities for reinforcement learning algorithms. The system supports both offline evaluation metrics and environment-based evaluation, along with flexible logging adapters for popular experiment tracking platforms.

 For information about the core algorithm training loops, see [Algorithm System](https://deepwiki.com/takuseno/d3rlpy/5-algorithm-system). For data preprocessing and scaling during training, see [Data Preprocessing](https://deepwiki.com/takuseno/d3rlpy/6.3-data-preprocessing).

 
## Overview

 The training and evaluation system consists of two main components:

 
 - **Metrics and Evaluation**: A protocol-based system for computing various offline and online evaluation metrics
 - **Logging and Experiment Tracking**: An adapter-based logging system supporting multiple backends (WandB, TensorBoard, file-based)
 
 These systems integrate seamlessly with d3rlpy's algorithm framework to provide comprehensive monitoring and evaluation during training.

 
## Metrics and Evaluation System

 
### Evaluation Protocol Architecture

 The evaluation system is built around the `EvaluatorProtocol` which defines a standardized interface for all evaluation metrics.

 
```

```

 Sources: [d3rlpy/metrics/evaluators.py34-50](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/metrics/evaluators.py#L34-L50) [d3rlpy/metrics/evaluators.py52-68](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/metrics/evaluators.py#L52-L68)

 
### Core Evaluation Metrics

 
#### TD Error Evaluation

 The `TDErrorEvaluator` measures temporal difference error to detect Q-function overfitting:

 
```

```

 Sources: [d3rlpy/metrics/evaluators.py71-121](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/metrics/evaluators.py#L71-L121) [d3rlpy/metrics/evaluators.py114-119](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/metrics/evaluators.py#L114-L119)

 
#### Value Estimation Metrics

 Several evaluators assess the quality and scale of value function estimates:

 
| Evaluator | Formula | Purpose |
|---|---|---|
| AverageValueEstimationEvaluator | E[max_a Q(s,a)] | Detect value overestimation |
| InitialStateValueEstimationEvaluator | E[Q(s_0, π(s_0))] | Expected return from initial states |
| DiscountedSumOfAdvantageEvaluator | Σ γ^t A(s_t, a_t) | Policy improvement over dataset |

 Sources: [d3rlpy/metrics/evaluators.py191-226](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/metrics/evaluators.py#L191-L226) [d3rlpy/metrics/evaluators.py229-271](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/metrics/evaluators.py#L229-L271) [d3rlpy/metrics/evaluators.py124-188](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/metrics/evaluators.py#L124-L188)

 
### Environment-Based Evaluation

 The `EnvironmentEvaluator` provides online evaluation by running the trained policy in an environment:

 
```

```

 Sources: [d3rlpy/metrics/evaluators.py506-548](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/metrics/evaluators.py#L506-L548) [d3rlpy/metrics/utility.py12-71](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/metrics/utility.py#L12-L71)

 
## Logging and Experiment Tracking System

 
### Logger Architecture

 The logging system uses an adapter pattern to support multiple experiment tracking backends:

 
```

```

 Sources: [d3rlpy/logging/logger.py143-167](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/logging/logger.py#L143-L167) [d3rlpy/logging/logger.py123-140](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/logging/logger.py#L123-L140)

 
### Logger Adapter Protocol

 All logging adapters implement the `LoggerAdapter` protocol:

 
```

```

 Sources: [d3rlpy/logging/logger.py61-121](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/logging/logger.py#L61-L121)

 
### WandB Integration

 The `WanDBAdapter` provides integration with Weights & Biases:

 
```

```

 Sources: [d3rlpy/logging/wandb_adapter.py25-43](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/logging/wandb_adapter.py#L25-L43) [d3rlpy/logging/wandb_adapter.py52-70](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/logging/wandb_adapter.py#L52-L70)

 
### File-Based Logging

 The `FileAdapter` saves metrics as CSV files and models as `.d3` files:

 
```

```

 Sources: [d3rlpy/logging/file_adapter.py47-82](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/logging/file_adapter.py#L47-L82) [d3rlpy/logging/file_adapter.py90-121](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/logging/file_adapter.py#L90-L121)

 
## Training Integration

 
### Metric Collection and Reporting

 The `D3RLPyLogger` manages the collection and reporting of metrics during training:

 
```

```

 Sources: [d3rlpy/logging/logger.py149-166](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/logging/logger.py#L149-L166) [d3rlpy/logging/logger.py175-198](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/logging/logger.py#L175-L198) [d3rlpy/logging/logger.py206-213](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/logging/logger.py#L206-L213)

 
### Protocol Definitions

 The logging system defines several protocols for type safety:

 
| Protocol | Purpose | Key Methods |
|---|---|---|
| SaveProtocol | Models that can be saved | save(fname: str) |
| ModuleProtocol | Neural network modules | get_torch_modules(), get_gradients() |
| ImplProtocol | Algorithm implementations | modules: ModuleProtocol |
| AlgProtocol | Algorithm interface | impl: Optional[ImplProtocol] |

 Sources: [d3rlpy/logging/logger.py40-59](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/logging/logger.py#L40-L59)

 The training and evaluation system provides comprehensive monitoring capabilities for d3rlpy algorithms, supporting both research and production use cases through its flexible adapter architecture and extensive metric collection.
