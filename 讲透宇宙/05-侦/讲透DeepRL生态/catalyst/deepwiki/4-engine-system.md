> 来源: [https://deepwiki.com/catalyst-team/catalyst/4-engine-system](https://deepwiki.com/catalyst-team/catalyst/4-engine-system)
> DeepWiki catalyst-team/catalyst | Last indexed: 21 April 2025 (e99f90

# Engine System

  Relevant source files 
 - [catalyst/callbacks/__init__.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/__init__.py)
 - [catalyst/callbacks/checkpoint.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/checkpoint.py)
 - [catalyst/callbacks/profiler.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/profiler.py)
 - [catalyst/core/__init__.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/__init__.py)
 - [catalyst/core/callback.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/callback.py)
 - [catalyst/core/engine.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/engine.py)
 - [catalyst/core/runner.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/runner.py)
 - [catalyst/engines/torch.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/engines/torch.py)
 - [catalyst/runners/runner.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/runners/runner.py)
 - [catalyst/runners/supervised.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/runners/supervised.py)
 - [docs/api/core.rst](https://github.com/catalyst-team/catalyst/blob/e99f9065/docs/api/core.rst)
 - [examples/engines/README.md](https://github.com/catalyst-team/catalyst/blob/e99f9065/examples/engines/README.md?plain=1)
 - [examples/engines/src.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/examples/engines/src.py)
 - [examples/engines/train_albert.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/examples/engines/train_albert.py)
 - [examples/engines/train_resnet.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/examples/engines/train_resnet.py)
 - [tests/catalyst/callbacks/test_profiler.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/tests/catalyst/callbacks/test_profiler.py)
 
  The Engine System is a core component of the Catalyst framework that provides hardware abstraction for deep learning experiments. It enables seamless execution of training code across various hardware configurations (CPU, GPU, multi-GPU, TPU) and supports optimization techniques like mixed precision training and distributed training. This page documents the Engine architecture, available implementations, and integration with the Runner system.

 For information about the overall training process orchestration, see [Runner System](https://deepwiki.com/catalyst-team/catalyst/2-runner-system).

 
## Engine Architecture

 The Engine system serves as a bridge between the high-level training logic in Catalyst and the specific hardware capabilities of the underlying infrastructure. It abstracts away the complexities of device management, distributed communication, and hardware-specific optimizations.

 
```

```

 Sources: [catalyst/core/engine.py18-96](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/engine.py#L18-L96) [catalyst/engines/torch.py20-215](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/engines/torch.py#L20-L215)

 The `Engine` base class extends PyTorch's Accelerator and provides methods for distributed setup, process spawning, and metric synchronization. Specific implementations handle different hardware configurations and optimization techniques.

 
## Engine and Runner Integration

 The Engine system is tightly integrated with the Runner system in Catalyst. The Runner manages the training loop while delegating hardware-specific operations to the Engine.

 
```

```

 Sources: [catalyst/core/runner.py394-423](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/runner.py#L394-L423) [catalyst/runners/runner.py429-448](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/runners/runner.py#L429-L448)

 The Runner obtains an Engine instance through its `get_engine()` method, then uses it to prepare the model, data loaders, and handle device-specific operations like backward passes and metric synchronization.

 
## Available Engine Implementations

 Catalyst provides several Engine implementations to support different hardware configurations and optimization techniques:

 
| Engine Type | Implementation | Hardware | Description |
|---|---|---|---|
| CPU | CPUEngine | CPU | Basic CPU-based training |
| GPU | GPUEngine | Single GPU | Uses a single GPU for training |
| DataParallel | DataParallelEngine | Multiple GPUs (single node) | Uses PyTorch's DataParallel for multi-GPU training |
| DistributedDataParallel | DistributedDataParallelEngine | Multiple GPUs (single/multi-node) | Uses PyTorch's DistributedDataParallel for efficient multi-GPU training |
| XLA | DistributedXLAEngine | TPUs | Uses PyTorch XLA for TPU training |

 Each Engine type can also be combined with Automatic Mixed Precision (AMP) for improved performance on compatible hardware.

 Sources: [catalyst/engines/torch.py20-205](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/engines/torch.py#L20-L205) [examples/engines/src.py7-19](https://github.com/catalyst-team/catalyst/blob/e99f9065/examples/engines/src.py#L7-L19)

 
## Engine Selection

 The engine can be specified when initializing the Runner or during the `train()` method call. Catalyst provides a convenient mapping from string identifiers to Engine implementations:

 
```

```

 Sources: [examples/engines/src.py7-19](https://github.com/catalyst-team/catalyst/blob/e99f9065/examples/engines/src.py#L7-L19) [examples/engines/README.md1-142](https://github.com/catalyst-team/catalyst/blob/e99f9065/examples/engines/README.md?plain=1#L1-L142)

 
## Key Engine Features

 
### Model Preparation

 Engines handle model preparation for the target hardware:

 
```

```

 Sources: [catalyst/engines/torch.py43-47](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/engines/torch.py#L43-L47) [catalyst/core/runner.py240-245](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/runner.py#L240-L245)

 
### Distributed Training

 The `DistributedDataParallelEngine` implements distributed training capabilities:

 
 - Process spawning for multi-GPU training
 - Initialization of distributed process groups
 - Rank and world size management
 - Metric synchronization across processes
 
 Sources: [catalyst/engines/torch.py50-158](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/engines/torch.py#L50-L158)

 
### XLA Support

 The `DistributedXLAEngine` enables training on TPUs using PyTorch XLA:

 
 - Process spawning for TPU cores
 - XLA-specific metric reduction
 - Integration with PyTorch XLA's API
 
 Sources: [catalyst/engines/torch.py161-205](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/engines/torch.py#L161-L205)

 
## Usage Examples

 
### Basic Usage

 The engine can be specified when training a model:

 
```

```

 Sources: [examples/engines/README.md19-83](https://github.com/catalyst-team/catalyst/blob/e99f9065/examples/engines/README.md?plain=1#L19-L83) [catalyst/runners/runner.py259-377](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/runners/runner.py#L259-L377)

 
### Custom Runner with Engine Selection

 For more control, you can implement a custom runner that selects the engine:

 
```

```

 Sources: [examples/engines/train_resnet.py45-54](https://github.com/catalyst-team/catalyst/blob/e99f9065/examples/engines/train_resnet.py#L45-L54) [examples/engines/train_albert.py18-26](https://github.com/catalyst-team/catalyst/blob/e99f9065/examples/engines/train_albert.py#L18-L26)

 
### Distributed Training

 For distributed training, additional parameters can be specified:

 
```

```

 Sources: [examples/engines/README.md24-32](https://github.com/catalyst-team/catalyst/blob/e99f9065/examples/engines/README.md?plain=1#L24-L32) [examples/engines/src.py36-105](https://github.com/catalyst-team/catalyst/blob/e99f9065/examples/engines/src.py#L36-L105)

 
## Engine System and Callbacks

 The Engine system works closely with callbacks, especially those that handle training operations:

 
 - `BackwardCallback` - Uses the engine to compute gradients
 - `OptimizerCallback` - Updates weights after backward pass
 - `CheckpointCallback` - Saves and loads model state through the engine
 - `ProfilerCallback` - Profiles code execution with engine-aware profiling
 
 Sources: [catalyst/callbacks/checkpoint.py83-119](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/checkpoint.py#L83-L119) [catalyst/callbacks/profiler.py91-198](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/profiler.py#L91-L198)

 
## Advanced Engine Features

 
### Batch Handling in Distributed Mode

 When using distributed engines, the Runner adjusts batch handling to account for multiple processes:

 
```

```

 Sources: [catalyst/core/runner.py323-327](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/runner.py#L323-L327)

 
### Distributed Samplers

 When using distributed engines, dataset samplers need to be adjusted:

 
```

```

 Sources: [examples/engines/train_resnet.py74-88](https://github.com/catalyst-team/catalyst/blob/e99f9065/examples/engines/train_resnet.py#L74-L88) [examples/engines/train_albert.py61-75](https://github.com/catalyst-team/catalyst/blob/e99f9065/examples/engines/train_albert.py#L61-L75)

 
## Customizing Engines

 The Engine system is designed to be extensible. To create a custom engine:

 
 - Inherit from the base `Engine` class
 - Implement required methods: `spawn`, `setup`, `cleanup`
 - Add hardware-specific optimizations or features
 
 For example, the `DataParallelEngine` customizes model preparation:

 
```

```

 Sources: [catalyst/engines/torch.py36-47](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/engines/torch.py#L36-L47)

 
## Summary

 The Engine system is a fundamental component of Catalyst that abstracts hardware-specific details from the training process. It allows the same code to run efficiently on different hardware setups, from a single CPU to a multi-node, multi-GPU cluster, or even TPUs. By selecting the appropriate engine, you can leverage hardware acceleration and optimization techniques without changing your training code.
