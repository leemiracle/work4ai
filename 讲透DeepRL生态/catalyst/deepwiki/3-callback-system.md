> 来源: [https://deepwiki.com/catalyst-team/catalyst/3-callback-system](https://deepwiki.com/catalyst-team/catalyst/3-callback-system)
> DeepWiki catalyst-team/catalyst | Last indexed: 21 April 2025 (e99f90

# Callback System

  Relevant source files 
 - [catalyst/callbacks/__init__.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/__init__.py)
 - [catalyst/callbacks/checkpoint.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/checkpoint.py)
 - [catalyst/callbacks/metrics/__init__.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/metrics/__init__.py)
 - [catalyst/callbacks/profiler.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/profiler.py)
 - [catalyst/core/__init__.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/__init__.py)
 - [catalyst/core/callback.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/callback.py)
 - [catalyst/core/runner.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/runner.py)
 - [catalyst/dl/__init__.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/dl/__init__.py)
 - [catalyst/metrics/__init__.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/metrics/__init__.py)
 - [catalyst/metrics/_functional_metric.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/metrics/_functional_metric.py)
 - [catalyst/metrics/_r2_squared.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/metrics/_r2_squared.py)
 - [catalyst/metrics/functional/__init__.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/metrics/functional/__init__.py)
 - [catalyst/metrics/functional/_r2_squared.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/metrics/functional/_r2_squared.py)
 - [catalyst/runners/runner.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/runners/runner.py)
 - [catalyst/runners/supervised.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/runners/supervised.py)
 - [docs/api/callbacks.rst](https://github.com/catalyst-team/catalyst/blob/e99f9065/docs/api/callbacks.rst)
 - [docs/api/core.rst](https://github.com/catalyst-team/catalyst/blob/e99f9065/docs/api/core.rst)
 - [docs/api/metrics.rst](https://github.com/catalyst-team/catalyst/blob/e99f9065/docs/api/metrics.rst)
 - [tests/catalyst/metrics/functional/test_r2_squared.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/tests/catalyst/metrics/functional/test_r2_squared.py)
 - [tests/catalyst/metrics/test_r2squared.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/tests/catalyst/metrics/test_r2squared.py)
 
  The Callback System is a central component of Catalyst that enables customizable, event-driven training workflows. Callbacks allow users to inject custom logic at specific points in the training process without modifying the core training loop. This makes the framework highly extensible and allows for easy implementation of complex training patterns.

 
## Callback Architecture and Lifecycle

 Callbacks in Catalyst follow a specific lifecycle that aligns with the training process. Each callback can implement methods that are triggered at different stages of the training process.

 
```

```

 
### Event Flow

 
 - **Experiment Level**: `on_experiment_start()` and `on_experiment_end()`
 - **Epoch Level**: `on_epoch_start()` and `on_epoch_end()`
 - **Loader Level**: `on_loader_start()` and `on_loader_end()`
 - **Batch Level**: `on_batch_start()` and `on_batch_end()`
 - **Exception Handling**: `on_exception()`
 
 The Runner executes these methods on all registered callbacks at appropriate points in the training loop.

 Sources: [catalyst/core/callback.py8-46](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/callback.py#L8-L46) [catalyst/core/runner.py357-365](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/runner.py#L357-L365)

 
## Callback Hierarchy

 Callbacks in Catalyst are organized in a hierarchical structure to promote reusability and specialization.

 
```

```

 
### Key Components:

 
 - **ICallback**: Base interface defining the callback lifecycle methods.
 - **Callback**: Implementation adding the `order` property for execution sequencing.
 - **Specialized Interfaces**: (`IMetricCallback`, `ICriterionCallback`, etc.) provide specialized behavior for specific tasks.
 - **CallbackWrapper**: Utility to enable/disable callbacks dynamically.
 
 Sources: [catalyst/core/callback.py8-257](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/callback.py#L8-L257) [catalyst/callbacks/__init__.py7-18](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/__init__.py#L7-L18)

 
## Callback Execution Order

 Callbacks are executed in a specific order determined by the `CallbackOrder` enum. This ensures that interdependent operations happen in the correct sequence.

 
```

```

 
### Predefined Orders:

 
| Order Value | Name | Purpose |
|---|---|---|
| 0 | Internal | For Catalyst internal use (e.g., PhaseCallbacks) |
| 10 | Metric | For metrics and loss computation |
| 20 | MetricAggregation | For aggregating different metrics |
| 30 | Backward | For backward pass operations |
| 40 | Optimizer | For optimizer steps (requires computed metrics) |
| 50 | Scheduler/Checkpoint | For scheduler steps (may require validation metrics) |
| 100 | External | For additional custom logic |

 Callbacks with lower order values are executed **before** callbacks with higher order values.

 Sources: [catalyst/core/callback.py48-89](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/callback.py#L48-L89)

 
## Built-in Callbacks

 Catalyst provides a rich set of built-in callbacks for common tasks:

 
### Core Callbacks

 
| Callback | Purpose | Order |
|---|---|---|
| CriterionCallback | Computes loss using criterion | Metric |
| BackwardCallback | Performs backward pass | Backward |
| OptimizerCallback | Updates model parameters | Optimizer |
| SchedulerCallback | Adjusts learning rate | Scheduler |
| CheckpointCallback | Saves and loads model state | Checkpoint |
| TqdmCallback | Displays progress bar | External |
| TimerCallback | Measures execution time | External |
| BatchOverfitCallback | Helps with model overfitting | External |
| ProfilerCallback | Profiles code execution | Internal |

 
### Metric Callbacks

 Metric callbacks integrate with the Metrics system to compute and log performance metrics.

 
| Callback | Metric |
|---|---|
| AccuracyCallback | Classification accuracy |
| AUCCallback | Area under ROC curve |
| PrecisionRecallF1SupportCallback | Precision, recall, F1 |
| R2SquaredCallback | R² for regression |
| IOUCallback | Intersection over Union |
| DiceCallback | Dice coefficient |

 Sources: [catalyst/callbacks/__init__.py21-76](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/__init__.py#L21-L76) [catalyst/callbacks/metrics/__init__.py3-42](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/metrics/__init__.py#L3-L42) [docs/api/callbacks.rst18-306](https://github.com/catalyst-team/catalyst/blob/e99f9065/docs/api/callbacks.rst#L18-L306)

 
## Integration with Runner System

 The Runner system orchestrates callback execution at specific points in the training process:

 
```

```

 The `_run_event` method in the Runner class is responsible for executing all registered callbacks for a specific event. The method maintains proper execution order and handles both start and end events correctly.

 Sources: [catalyst/core/runner.py359-365](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/runner.py#L359-L365) [catalyst/core/runner.py394-406](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/runner.py#L394-L406)

 
## Creating Custom Callbacks

 To create a custom callback, you need to inherit from the `Callback` class or one of its specialized subclasses and implement the required methods.

 
### Example: Custom Metric Callback

 
```

```

 
### Registering Callbacks with Runner

 Callbacks need to be registered with the Runner to be executed during training:

 
```

```

 Sources: [catalyst/core/callback.py91-134](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/callback.py#L91-L134) [catalyst/runners/supervised.py229-257](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/runners/supervised.py#L229-L257)

 
## Integration with Metrics System

 Catalyst integrates callbacks with metrics through specialized interfaces:

 
```

```

 
### Types of Metric Callbacks:

 
 - **BatchMetricCallback**: Computes metrics on each batch (e.g., loss).
 - **LoaderMetricCallback**: Computes metrics over entire loader (e.g., AUC).
 - **FunctionalMetricCallback**: Uses arbitrary functions as metrics.
 
 Sources: [catalyst/metrics/__init__.py9-21](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/metrics/__init__.py#L9-L21) [catalyst/metrics/_functional_metric.py13-233](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/metrics/_functional_metric.py#L13-L233) [catalyst/callbacks/metrics/__init__.py3-42](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/metrics/__init__.py#L3-L42)

 
## Example Usage

 
### Basic Callback Usage with Runner

 
```

```

 
### Advanced: Custom Training Loop with Profiling

 
```

```

 Sources: [catalyst/runners/runner.py66-139](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/runners/runner.py#L66-L139) [catalyst/callbacks/profiler.py41-86](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/profiler.py#L41-L86)

 
## Conclusion

 The Callback System is one of the core architectural components of Catalyst, providing a flexible and extensible way to customize the training process. By understanding the callback lifecycle, execution order, and available built-in callbacks, users can leverage the full power of Catalyst for a wide range of deep learning tasks.

 For detailed information about built-in callbacks, see [Built-in Callbacks](https://deepwiki.com/catalyst-team/catalyst/3.1-built-in-callbacks). For guidance on creating custom callbacks, see [Creating Custom Callbacks](https://deepwiki.com/catalyst-team/catalyst/3.2-creating-custom-callbacks).
