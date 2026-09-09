> 来源: [https://deepwiki.com/catalyst-team/catalyst/2-runner-system](https://deepwiki.com/catalyst-team/catalyst/2-runner-system)
> DeepWiki catalyst-team/catalyst | Last indexed: 21 April 2025 (e99f90

# Runner System

  Relevant source files 
 - [catalyst/callbacks/__init__.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/__init__.py)
 - [catalyst/callbacks/checkpoint.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/checkpoint.py)
 - [catalyst/callbacks/profiler.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/profiler.py)
 - [catalyst/core/__init__.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/__init__.py)
 - [catalyst/core/callback.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/callback.py)
 - [catalyst/core/runner.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/runner.py)
 - [catalyst/dl/__init__.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/dl/__init__.py)
 - [catalyst/runners/runner.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/runners/runner.py)
 - [catalyst/runners/supervised.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/runners/supervised.py)
 - [docs/api/core.rst](https://github.com/catalyst-team/catalyst/blob/e99f9065/docs/api/core.rst)
 
  The Runner System is the central orchestration component in Catalyst that manages the entire machine learning experiment flow. It coordinates the training loops, handles data movement between components, and drives the event-based callback system. This page describes the Runner architecture, its core interfaces, and how it orchestrates the training process.

 For details about specific Runner implementations, see [Supervised and Custom Runners](https://deepwiki.com/catalyst-team/catalyst/2.2-supervised-and-custom-runners).

 
## Core Concepts

 The Runner system is built around the concept of events that occur during a training process. These events form a hierarchical structure:

 
```

```

 At each of these events, the Runner executes callbacks that can modify the training behavior, log metrics, save checkpoints, or perform other operations.

 Sources: [catalyst/core/runner.py11-44](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/runner.py#L11-L44) [catalyst/core/callback.py8-46](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/callback.py#L8-L46)

 
## IRunner Interface

 The `IRunner` interface defines the common API that all Runners must implement. It serves as both a backbone of the training process and an event dispatcher for the callback system.

 
```

```

 Key properties of `IRunner`:

 
 - Inherits from both `ICallback` and `ILogger`
 - Manages core training components (model, criterion, optimizer, scheduler)
 - Maintains state information (batch step, epoch step, metrics)
 - Defines abstract methods that concrete implementations must provide
 
 Sources: [catalyst/core/runner.py40-426](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/runner.py#L40-L426) [catalyst/core/callback.py8-46](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/callback.py#L8-L46)

 
## Training Execution Flow

 The Runner system orchestrates the entire training process through a nested execution flow. Here's how the execution proceeds:

 
```

```

 The execution process includes error handling through the `on_exception` event, which is triggered if any uncaught exception occurs during training.

 Sources: [catalyst/core/runner.py359-423](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/runner.py#L359-L423)

 
## State Management

 The Runner maintains several levels of state information:

 
| State Level | Description | Example Properties |
|---|---|---|
| Experiment | Global experiment settings | seed, hparams, num_epochs |
| Epoch | Per-epoch state | epoch_step, epoch_metrics |
| Loader | Per-loader state | loader_key, is_train_loader, loader_metrics |
| Batch | Per-batch state | batch, batch_size, batch_metrics |

 This hierarchical state management allows callbacks to access and modify state at the appropriate level of granularity.

 Sources: [catalyst/core/runner.py69-110](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/runner.py#L69-L110)

 
## Core Execution Methods

 The Runner implements several core methods that drive the training process:

 
```

```

 These methods form the backbone of the execution flow and trigger the appropriate callbacks at each step.

 Sources: [catalyst/core/runner.py377-423](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/runner.py#L377-L423)

 
## Runner and Component Setup

 Before starting the training process, the Runner sets up all necessary components:

 
```

```

 This setup process ensures that all components are properly initialized, prepared for the appropriate hardware, and ready for the training process.

 Sources: [catalyst/core/runner.py260-280](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/runner.py#L260-L280)

 
## Hardware Abstraction through Engine

 The Runner system works with the Engine system to abstract hardware details. This allows the same Runner code to operate efficiently on different hardware configurations:

 
```

```

 This abstraction allows the Runner to focus on orchestrating the training flow without being concerned with the specific hardware details.

 Sources: [catalyst/core/runner.py173-174](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/runner.py#L173-L174) [catalyst/core/runner.py239-256](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/runner.py#L239-L256)

 
## Concrete Runner Implementations

 The base `Runner` class provides a concrete implementation of `IRunner` with additional user-friendly features:

 
```

```

 The `Runner` class adds convenience methods like `train()`, `predict_batch()`, and `evaluate_loader()`, while `SupervisedRunner` specializes in supervised learning with input/output mappings.

 Sources: [catalyst/runners/runner.py34-501](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/runners/runner.py#L34-L501) [catalyst/runners/supervised.py24-257](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/runners/supervised.py#L24-L257)

 
## Metrics Collection and Logging

 The Runner is responsible for collecting and organizing metrics at different levels:

 
```

```

 These metrics are made available to callbacks and are logged using the configured loggers.

 Sources: [catalyst/core/runner.py26-31](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/runner.py#L26-L31) [catalyst/core/runner.py141-169](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/runner.py#L141-L169)

 
## Integration with Callback System

 The Runner system and Callback system are tightly integrated. The Runner itself implements the `ICallback` interface and triggers callback events for all registered callbacks:

 
```

```

 This design allows callbacks to inject behavior at various points in the training loop.

 Sources: [catalyst/core/runner.py359-365](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/runner.py#L359-L365) [catalyst/core/callback.py91-134](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/callback.py#L91-L134)

 
## Relationship to Other Systems

 The Runner system interacts with several other core systems in the Catalyst framework:

 
```

```

 This web of interactions makes the Runner the central coordination point of the Catalyst framework.

 Sources: [catalyst/core/runner.py40-426](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/runner.py#L40-L426)

 
## Usage Example

 The `Runner` and `SupervisedRunner` classes provide high-level interfaces for common training scenarios:

 
```

```

 The `SupervisedRunner` automatically sets up the necessary callbacks for criterion, backward, optimizer, and scheduler steps, while custom runners provide more flexibility at the cost of additional implementation.

 Sources: [catalyst/runners/runner.py65-138](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/runners/runner.py#L65-L138) [catalyst/runners/supervised.py174-258](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/runners/supervised.py#L174-L258)
