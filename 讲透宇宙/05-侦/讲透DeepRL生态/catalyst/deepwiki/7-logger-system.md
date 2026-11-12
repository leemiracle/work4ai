> 来源: [https://deepwiki.com/catalyst-team/catalyst/7-logger-system](https://deepwiki.com/catalyst-team/catalyst/7-logger-system)
> DeepWiki catalyst-team/catalyst | Last indexed: 21 April 2025 (e99f90

# Logger System

  Relevant source files 
 - [catalyst/callbacks/__init__.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/__init__.py)
 - [catalyst/callbacks/checkpoint.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/checkpoint.py)
 - [catalyst/callbacks/profiler.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/profiler.py)
 - [catalyst/core/__init__.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/__init__.py)
 - [catalyst/core/callback.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/callback.py)
 - [catalyst/core/logger.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/logger.py)
 - [catalyst/core/runner.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/runner.py)
 - [catalyst/loggers/comet.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/loggers/comet.py)
 - [catalyst/loggers/console.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/loggers/console.py)
 - [catalyst/loggers/csv.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/loggers/csv.py)
 - [catalyst/loggers/mlflow.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/loggers/mlflow.py)
 - [catalyst/loggers/neptune.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/loggers/neptune.py)
 - [catalyst/loggers/tensorboard.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/loggers/tensorboard.py)
 - [catalyst/loggers/wandb.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/loggers/wandb.py)
 - [catalyst/runners/runner.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/runners/runner.py)
 - [catalyst/runners/supervised.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/runners/supervised.py)
 - [docs/api/core.rst](https://github.com/catalyst-team/catalyst/blob/e99f9065/docs/api/core.rst)
 
  The Logger System in Catalyst provides a flexible and extensible framework for tracking experiments, logging metrics, visualizing results, and managing artifacts during model training. This document describes the architecture of the logging system, the available loggers, and how to use them effectively.

 For information about the metrics computation system that produces values to be logged, see [Metrics System](https://deepwiki.com/catalyst-team/catalyst/6-metrics-system).

 
## Architecture Overview

 The Logger System is built around the `ILogger` interface and integrates with the Runner to provide comprehensive experiment tracking capabilities.

 
```

```

 Sources: [catalyst/core/logger.py9-98](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/logger.py#L9-L98) [catalyst/core/runner.py40-179](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/runner.py#L40-L179)

 
### Core Components

 The Logger System consists of these key components:

 
 - **ILogger Interface**: Defines the contract that all loggers must implement
 - **Concrete Logger Implementations**: Various loggers that output to different platforms
 - **Runner Integration**: Mechanism to connect loggers to the training process
 
 
### Metric Flow Through the System

 
```

```

 Sources: [catalyst/core/runner.py330-347](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/runner.py#L330-L347)

 
## ILogger Interface

 The `ILogger` interface defines the contract that all loggers must implement:

 
```

```

 Sources: [catalyst/core/logger.py9-98](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/logger.py#L9-L98)

 
## Integration with Runner

 The Runner class integrates with loggers through the following mechanisms:

 
 - **Loggers storage**: `self.loggers: Dict[str, ILogger]`
 - **Logger configuration**: `get_loggers()` method
 - **Logging methods**: 
 - `log_artifact()`
 - `log_image()`
 - `log_hparams()`
 - `log_metrics()`
 - `flush_log()`
 - `close_log()`
 
 The event handlers in the Runner (`on_batch_end`, `on_loader_end`, `on_epoch_end`) call the appropriate logging methods at each stage of the training process.

 Sources: [catalyst/core/runner.py40-179](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/runner.py#L40-L179) [catalyst/core/runner.py330-352](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/runner.py#L330-L352)

 
## Built-in Loggers

 Catalyst provides several logger implementations for different backends:

 
### Console Logger

 The most basic logger that prints metrics to the console.

 
```

```

 Sources: [catalyst/loggers/console.py13-51](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/loggers/console.py#L13-L51)

 
### CSV Logger

 Logs metrics to CSV files for later analysis.

 
```

```

 Sources: [catalyst/loggers/csv.py13-116](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/loggers/csv.py#L13-L116)

 
### TensorBoard Logger

 Logs metrics, images, and other data to TensorBoard.

 Sources: [catalyst/loggers/tensorboard.py32-173](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/loggers/tensorboard.py#L32-L173)

 
### MLflow Logger

 Integrates with MLflow for experiment tracking.

 Sources: [catalyst/loggers/mlflow.py73-221](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/loggers/mlflow.py#L73-L221)

 
### Neptune Logger

 Logs experiment data to Neptune.ai.

 Sources: [catalyst/loggers/neptune.py32-276](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/loggers/neptune.py#L32-L276)

 
### Weights & Biases Logger

 Integrates with Weights & Biases (wandb) for experiment tracking.

 Sources: [catalyst/loggers/wandb.py17-201](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/loggers/wandb.py#L17-L201)

 
### Comet Logger

 Logs experiment data to Comet ML.

 Sources: [catalyst/loggers/comet.py32-211](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/loggers/comet.py#L32-L211)

 
## Logging Lifecycle

 The logging system follows a specific lifecycle during training:

 
```

```

 Sources: [catalyst/core/runner.py259-352](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/runner.py#L259-L352)

 
## Using Loggers

 There are two main ways to set up loggers in Catalyst:

 
### 1. Through the Runner's train method

 
```

```

 
### 2. By overriding the get_loggers method in a custom Runner

 
```

```

 
## Advanced Features

 
### Controlling Metric Logging Granularity

 Each logger can be configured to log metrics at different granularities:

 
```

```

 
### Logging Images

 The logging system supports visualization of images:

 
```

```

 
### Logging Custom Artifacts

 You can log arbitrary files and objects:

 
```

```

 
## Creating Custom Loggers

 To create a custom logger, implement the `ILogger` interface:

 
```

```

 
## Best Practices

 
 - **Choose the right granularity**: Log batch metrics only when necessary as it can slow down training.
 - **Use appropriate loggers for your needs**: 
 - For simple experiments, ConsoleLogger and TensorboardLogger are sufficient
 - For team collaboration or experiment tracking, consider MLflow, Neptune, WandB, or Comet
 - **Log important hyperparameters**: Make sure to log hyperparameters for experiment reproducibility
 - **Visualize model outputs**: Use image logging to understand what your model is learning
 
 
## Summary

 The Logger System in Catalyst provides a flexible and extensible framework for tracking experiments and visualizing results. It supports various backends through a unified interface and integrates seamlessly with the Runner class to provide comprehensive logging at different stages of the training process.
